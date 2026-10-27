#!/usr/bin/env python3
"""Stdlib-only integrity verifier for Flat Packet Connection v0.5.0.

Verification authenticates bytes, frozen design receipts, scientific banks,
checkpoint seals, and cross-artifact status consistency.  A scientifically
negative result is a valid retained result: scientific ``FAIL`` never turns an
otherwise valid package into a verifier failure.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence
import zipfile


VERSION = "0.5.0"
AUTHOR = "Komorebi P."
MANIFEST_SCHEMA = "komorebi.neuralese.package_manifest.v5"
VERIFICATION_SCHEMA = "komorebi.flat_packet_connection.verification.v1"
PREREGISTRATION_SCHEMA = "komorebi.flat_packet_connection.preregistration.v2"
CONTRACT_SCHEMA = "komorebi.flat_packet_connection.contract.v1"
RESULT_SCHEMA = "komorebi.flat_packet_connection.result.v1"
STARTED_SCHEMA = "komorebi.flat_packet_connection.run_started.v1"
COMPLETION_SCHEMA = "komorebi.flat_packet_connection.run_complete.v1"
EVAL_BANK_SCHEMA = "komorebi.flat_packet_connection.eval_bank.v1"
CHECKPOINT_SEAL_SCHEMA = "komorebi.flat_packet_connection.checkpoint_seal.v1"

MANIFEST_NAME = "MANIFEST.json"
SUMS_NAME = "SHA256SUMS.txt"
PREREGISTRATION_NAME = "FLAT_CONNECTION_PREREGISTRATION.json"
CONTRACT_NAME = "FLAT_CONNECTION_CONTRACT.json"
SELF_EXCLUDED = frozenset({MANIFEST_NAME, SUMS_NAME})
SOURCE_SUFFIXES = frozenset({".py", ".md", ".json", ".toml", ".ps1", ".txt"})
FORBIDDEN_DIRECTORY_NAMES = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        ".git",
    }
)
HEX_256 = re.compile(r"[0-9a-f]{64}\Z")
REGISTERED_DESIGN_FIELDS = (
    "profile_name",
    "arms",
    "pilot_profile",
    "thresholds",
    "numerical_contract",
    "preregistration_sha256",
)


class VerificationError(RuntimeError):
    """Raised when package integrity or receipt consistency fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path, label: str | None = None) -> Any:
    display = label or path.as_posix()
    require(path.exists(), f"missing required artifact: {display}")
    require(not path.is_symlink(), f"symbolic links are forbidden: {display}")
    require(path.is_file(), f"artifact is not a regular file: {display}")
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
            object_pairs_hook=_strict_json_object,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise VerificationError(f"invalid strict JSON in {display}: {error}") from error


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def require_sha256(value: Any, label: str) -> str:
    require(
        isinstance(value, str) and HEX_256.fullmatch(value) is not None,
        f"{label} must be a lowercase SHA-256 digest",
    )
    return value


def validate_relative_path(relative: str) -> None:
    parsed = PurePosixPath(relative)
    if (
        not relative
        or parsed.is_absolute()
        or relative != parsed.as_posix()
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or "\\" in relative
        or "\x00" in relative
    ):
        raise VerificationError(f"unsafe package path: {relative!r}")


def _is_cache_path(relative: str) -> bool:
    path = PurePosixPath(relative)
    return (
        any(part in FORBIDDEN_DIRECTORY_NAMES for part in path.parts)
        or path.suffix.lower() in {".pyc", ".pyo"}
    )


def iter_package_files(root: Path) -> Iterable[tuple[str, Path]]:
    """Enumerate every package file except the two self-excluding indexes."""

    root = root.resolve(strict=True)
    require(root.is_dir(), f"package root is not a directory: {root}")
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        validate_relative_path(relative)
        require(not path.is_symlink(), f"symbolic links are forbidden: {relative}")
        require(not _is_cache_path(relative), f"cache/bytecode artifact is forbidden: {relative}")
        if path.is_dir():
            continue
        require(path.is_file(), f"non-regular package entry is forbidden: {relative}")
        if relative not in SELF_EXCLUDED:
            yield relative, path


def package_inventory(root: Path) -> dict[str, Path]:
    return dict(iter_package_files(root))


def _atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def write_v5_manifest(root: Path) -> Mapping[str, Any]:
    """Write the v0.5 self-excluding manifest and canonical checksum list."""

    root = root.resolve(strict=True)
    records = [
        {
            "path": relative,
            "size": path.stat().st_size,
            "sha256": file_sha256(path),
        }
        for relative, path in iter_package_files(root)
    ]
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "file_count": len(records),
        "files": records,
    }
    sums = "".join(
        f"{record['sha256']}  {record['path']}\n" for record in records
    )
    rendered = json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
    _atomic_text(root / SUMS_NAME, sums)
    _atomic_text(root / MANIFEST_NAME, rendered)
    return manifest


def verify_manifest(root: Path) -> tuple[Mapping[str, Any], dict[str, Path]]:
    root = root.resolve(strict=True)
    manifest_path = root / MANIFEST_NAME
    sums_path = root / SUMS_NAME
    require(manifest_path.exists(), f"missing required artifact: {MANIFEST_NAME}")
    require(sums_path.exists(), f"missing required artifact: {SUMS_NAME}")
    # Inventory first so a cache cannot hide behind manifest exclusion rules.
    actual = package_inventory(root)
    manifest = require_mapping(load_json(manifest_path, MANIFEST_NAME), MANIFEST_NAME)
    require(
        set(manifest) == {"schema", "version", "author", "file_count", "files"},
        "manifest top-level schema mismatch",
    )
    require(manifest.get("schema") == MANIFEST_SCHEMA, "manifest schema mismatch")
    require(manifest.get("version") == VERSION, "manifest version mismatch")
    require(manifest.get("author") == AUTHOR, "manifest author mismatch")
    records = manifest.get("files")
    require(isinstance(records, list), "manifest files must be a list")
    require(
        type(manifest.get("file_count")) is int
        and manifest["file_count"] >= 0
        and manifest["file_count"] == len(records),
        "manifest file_count mismatch",
    )

    expected: dict[str, tuple[int, str]] = {}
    order: list[str] = []
    for index, raw in enumerate(records):
        row = require_mapping(raw, f"manifest record {index}")
        require(
            set(row) == {"path", "size", "sha256"},
            f"manifest record {index} schema mismatch",
        )
        relative = row.get("path")
        require(isinstance(relative, str), f"manifest record {index} path is invalid")
        validate_relative_path(relative)
        require(relative not in SELF_EXCLUDED, f"self-excluded path was manifested: {relative}")
        require(not _is_cache_path(relative), f"cache path was manifested: {relative}")
        require(relative not in expected, f"duplicate manifest path: {relative}")
        size = row.get("size")
        require(type(size) is int and size >= 0, f"invalid manifest size: {relative}")
        digest = require_sha256(row.get("sha256"), f"manifest digest for {relative}")
        expected[relative] = (size, digest)
        order.append(relative)
    require(order == sorted(order), "manifest paths are not sorted")
    require(
        set(actual) == set(expected),
        "manifest coverage mismatch; "
        f"unmanifested={sorted(set(actual) - set(expected))}, "
        f"missing={sorted(set(expected) - set(actual))}",
    )
    for relative, path in actual.items():
        expected_size, expected_digest = expected[relative]
        require(path.stat().st_size == expected_size, f"manifest size mismatch: {relative}")
        require(file_sha256(path) == expected_digest, f"manifest hash mismatch: {relative}")
        if path.suffix.lower() == ".json":
            load_json(path, relative)

    expected_sums = "".join(
        f"{expected[relative][1]}  {relative}\n" for relative in order
    )
    try:
        observed_sums = sums_path.read_text(encoding="utf-8")
    except UnicodeError as error:
        raise VerificationError(f"invalid {SUMS_NAME} encoding: {error}") from error
    require(observed_sums == expected_sums, f"{SUMS_NAME} is not canonical")
    return manifest, actual


def source_digest(root: Path, inventory: Mapping[str, Path] | None = None) -> tuple[str, list[str]]:
    """Reproduce the runner's non-self-referential source-tree digest."""

    root = root.resolve(strict=True)
    files = inventory if inventory is not None else package_inventory(root)
    names = sorted(
        relative
        for relative in files
        if PurePosixPath(relative).suffix.lower() in SOURCE_SUFFIXES
        and "results" not in PurePosixPath(relative).parts
        and PurePosixPath(relative).name
        not in {MANIFEST_NAME, SUMS_NAME, CONTRACT_NAME}
        and not any(
            part in {"__pycache__", ".pytest_cache", ".venv", ".git"}
            for part in PurePosixPath(relative).parts
        )
    )
    digest = hashlib.sha256()
    for relative in names:
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(files[relative].read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), names


def _registered_design(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {field: contract[field] for field in REGISTERED_DESIGN_FIELDS}


def _pilot_profile_matches_preregistration(
    pilot_profile: Mapping[str, Any],
    preregistered: Mapping[str, Any],
) -> bool:
    if pilot_profile == preregistered:
        return True
    projection = {
        "seeds": pilot_profile.get("seeds"),
        "steps": pilot_profile.get("steps"),
        "batch_size": pilot_profile.get("batch_size"),
        "causal_examples_per_seed": pilot_profile.get("causal_examples"),
        "deep_examples_per_depth_per_seed": pilot_profile.get("deep_examples"),
        "diamond_examples_per_length": pilot_profile.get("diamonds_per_length"),
        "loop_examples_per_repeat_suffix_stratum": pilot_profile.get(
            "loops_per_stratum"
        ),
    }
    return projection == preregistered


def verify_preregistration(root: Path) -> tuple[Mapping[str, Any], str]:
    path = root / PREREGISTRATION_NAME
    prereg = require_mapping(load_json(path, PREREGISTRATION_NAME), PREREGISTRATION_NAME)
    require(prereg.get("schema") == PREREGISTRATION_SCHEMA, "preregistration schema mismatch")
    require(prereg.get("version") == VERSION, "preregistration version mismatch")
    require(prereg.get("author") == AUTHOR, "preregistration author mismatch")
    require(isinstance(prereg.get("arms"), list), "preregistration arms are missing")
    require_mapping(prereg.get("pilot"), "preregistration pilot profile")
    require_mapping(prereg.get("thresholds"), "preregistration thresholds")
    require_mapping(prereg.get("numerical_contract"), "preregistration numerical contract")
    return prereg, file_sha256(path)


def verify_contract(
    root: Path,
    preregistration: Mapping[str, Any],
    preregistration_sha256: str,
    current_source_digest: str,
) -> tuple[Mapping[str, Any] | None, str | None]:
    path = root / CONTRACT_NAME
    if not path.exists():
        return None, None
    contract = require_mapping(load_json(path, CONTRACT_NAME), CONTRACT_NAME)
    required = {
        "schema",
        "version",
        "author",
        "source_digest",
        *REGISTERED_DESIGN_FIELDS,
        "registered_design_sha256",
    }
    allowed_surfaces = (required, required | {"primary_arm"})
    require(
        any(set(contract) == surface for surface in allowed_surfaces),
        "contract top-level schema mismatch",
    )
    require(contract.get("schema") == CONTRACT_SCHEMA, "contract schema mismatch")
    require(contract.get("version") == VERSION, "contract version mismatch")
    require(contract.get("author") == AUTHOR, "contract author mismatch")
    require(contract.get("profile_name") == "pilot", "contract profile_name must be pilot")
    require(
        require_sha256(contract.get("source_digest"), "contract source_digest")
        == current_source_digest,
        "contract source_digest does not match the packaged source tree",
    )
    require(
        require_sha256(
            contract.get("preregistration_sha256"),
            "contract preregistration_sha256",
        )
        == preregistration_sha256,
        "contract preregistration digest mismatch",
    )
    arms = contract.get("arms")
    require(
        isinstance(arms, list)
        and arms
        and all(isinstance(value, str) and value for value in arms)
        and len(set(arms)) == len(arms),
        "contract arms must be a nonempty unique string list",
    )
    require(arms == preregistration.get("arms"), "contract/preregistration arms mismatch")
    if "primary_arm" in contract:
        require(
            contract.get("primary_arm") == preregistration.get("primary_arm"),
            "contract primary arm mismatch",
        )
    pilot_profile = require_mapping(contract.get("pilot_profile"), "contract pilot_profile")
    require(
        _pilot_profile_matches_preregistration(
            pilot_profile,
            require_mapping(preregistration.get("pilot"), "preregistration pilot"),
        ),
        "contract pilot profile does not match the preregistration",
    )
    thresholds = require_mapping(contract.get("thresholds"), "contract thresholds")
    numerical = require_mapping(
        contract.get("numerical_contract"), "contract numerical_contract"
    )
    require(thresholds == preregistration.get("thresholds"), "contract threshold mismatch")
    require(
        numerical == preregistration.get("numerical_contract"),
        "contract numerical contract mismatch",
    )
    expected_registered_digest = hashlib.sha256(
        canonical_json_bytes(_registered_design(contract))
    ).hexdigest()
    require(
        require_sha256(
            contract.get("registered_design_sha256"),
            "contract registered_design_sha256",
        )
        == expected_registered_digest,
        "contract registered-design seal mismatch",
    )
    return contract, file_sha256(path)


def _safe_member(base: Path, relative: Any, label: str) -> Path:
    require(isinstance(relative, str), f"{label} path must be a string")
    validate_relative_path(relative)
    candidate = base.joinpath(*PurePosixPath(relative).parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(base.resolve(strict=True))
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        raise VerificationError(f"{label} path escapes or is missing: {relative}") from error
    require(not candidate.is_symlink(), f"{label} may not be a symbolic link: {relative}")
    require(candidate.is_file(), f"{label} is not a regular file: {relative}")
    return candidate


def _verify_torch_checkpoint_container(path: Path, label: str) -> None:
    require(zipfile.is_zipfile(path), f"{label} is not a torch ZIP checkpoint")
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), f"{label} ZIP contains duplicate members")
            for name in names:
                parsed = PurePosixPath(name)
                require(
                    not parsed.is_absolute()
                    and all(part not in {"", ".", ".."} for part in parsed.parts),
                    f"{label} ZIP contains an unsafe member",
                )
            require(
                any(name.endswith("/data.pkl") for name in names)
                and any(name.endswith("/version") for name in names)
                and any(name.endswith("/byteorder") for name in names),
                f"{label} lacks required torch checkpoint members",
            )
    except (OSError, zipfile.BadZipFile) as error:
        raise VerificationError(f"invalid {label} ZIP: {error}") from error


def _verify_self_seal(value: Mapping[str, Any], key: str, label: str) -> str:
    observed = require_sha256(value.get(key), f"{label} {key}")
    unsigned = dict(value)
    del unsigned[key]
    expected = hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest()
    require(observed == expected, f"{label} self-seal mismatch")
    return observed


def verify_checkpoint_seal(
    directory: Path,
    seal: Mapping[str, Any],
    current_source_digest: str,
    *,
    expected_arms: Sequence[str],
    expected_seeds: Sequence[int],
) -> Mapping[tuple[int, str], Mapping[str, Any]]:
    require(
        set(seal)
        == {
            "schema",
            "version",
            "source_digest",
            "count",
            "checkpoints",
            "seal_sha256",
        },
        "checkpoint-seal top-level schema mismatch",
    )
    require(seal.get("schema") == CHECKPOINT_SEAL_SCHEMA, "checkpoint-seal schema mismatch")
    require(seal.get("version") == VERSION, "checkpoint-seal version mismatch")
    require(seal.get("source_digest") == current_source_digest, "checkpoint source mismatch")
    _verify_self_seal(seal, "seal_sha256", "checkpoint seal")
    rows = seal.get("checkpoints")
    require(isinstance(rows, list), "checkpoint-seal records must be a list")
    require(
        type(seal.get("count")) is int and seal["count"] == len(rows),
        "checkpoint-seal count mismatch",
    )
    observed_paths: set[str] = set()
    observed_keys: set[tuple[int, str]] = set()
    order: list[tuple[int, str]] = []
    for index, raw in enumerate(rows):
        row = require_mapping(raw, f"checkpoint record {index}")
        require(
            set(row) == {"path", "sha256", "arm", "seed", "state_digest"},
            f"checkpoint record {index} schema mismatch",
        )
        relative = row.get("path")
        require(
            isinstance(relative, str)
            and relative.startswith("checkpoints/")
            and relative.endswith(".pt"),
            f"checkpoint record {index} path is invalid",
        )
        require(relative not in observed_paths, f"duplicate checkpoint path: {relative}")
        observed_paths.add(relative)
        arm = row.get("arm")
        seed = row.get("seed")
        require(isinstance(arm, str) and arm, f"checkpoint record {index} arm is invalid")
        require(type(seed) is int, f"checkpoint record {index} seed is invalid")
        require(
            relative == f"checkpoints/{arm}_seed{seed}.pt",
            f"checkpoint record {index} path does not match arm/seed",
        )
        key = (seed, arm)
        require(key not in observed_keys, f"duplicate checkpoint arm/seed: {key}")
        observed_keys.add(key)
        order.append(key)
        path = _safe_member(directory, relative, f"checkpoint {index}")
        _verify_torch_checkpoint_container(path, f"checkpoint {index}")
        require(
            file_sha256(path)
            == require_sha256(row.get("sha256"), f"checkpoint {index} sha256"),
            f"checkpoint file hash mismatch: {relative}",
        )
        require_sha256(row.get("state_digest"), f"checkpoint {index} state_digest")
    require(order == sorted(order), "checkpoint records are not sorted by seed and arm")
    expected_grid = {
        (int(seed), str(arm))
        for seed in expected_seeds
        for arm in expected_arms
    }
    require(observed_keys == expected_grid, "checkpoint seal does not cover the exact seed/arm grid")
    expected_files = {
        f"checkpoints/{arm}_seed{int(seed)}.pt"
        for seed in expected_seeds
        for arm in expected_arms
    }
    checkpoint_dir = directory / "checkpoints"
    actual_files = {
        path.relative_to(directory).as_posix()
        for path in checkpoint_dir.glob("*.pt")
        if path.is_file()
    }
    require(actual_files == expected_files, "checkpoint directory differs from the seal")
    return {
        (int(row["seed"]), str(row["arm"])): row
        for row in rows
    }


def verify_training_grid(
    training: Any,
    seal_rows: Mapping[tuple[int, str], Mapping[str, Any]],
    *,
    expected_arms: Sequence[str],
    expected_seeds: Sequence[int],
) -> None:
    training = require_mapping(training, "RESULTS training")
    expected_seed_keys = {str(int(seed)) for seed in expected_seeds}
    require(set(training) == expected_seed_keys, "training receipt seed grid mismatch")
    required_fields = {
        "config",
        "trajectory",
        "elapsed_seconds",
        "final_loss",
        "parameter_count",
        "initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_proposal_count",
        "terminal_candidates_accepted",
        "terminal_candidates_rejected",
    }
    for seed in expected_seeds:
        arms = require_mapping(training[str(int(seed))], f"training seed {seed}")
        require(set(arms) == set(expected_arms), f"training arm grid mismatch for seed {seed}")
        for arm in expected_arms:
            row = require_mapping(arms[arm], f"training {seed}/{arm}")
            require(set(row) == required_fields, f"training receipt schema mismatch: {seed}/{arm}")
            config = require_mapping(row.get("config"), f"training config {seed}/{arm}")
            require(config.get("seed") == int(seed), f"training config seed mismatch: {seed}/{arm}")
            for digest_name in (
                "initial_state_digest",
                "final_state_digest",
                "episode_stream_digest",
                "terminal_proposal_stream_digest",
                "relation_schedule_digest",
            ):
                require_sha256(row.get(digest_name), f"training {seed}/{arm} {digest_name}")
            require(
                row.get("final_state_digest") == seal_rows[(int(seed), str(arm))].get("state_digest"),
                f"training/seal state digest mismatch: {seed}/{arm}",
            )
            for numeric_name in ("elapsed_seconds", "final_loss"):
                value = row.get(numeric_name)
                require(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(float(value))
                    and float(value) >= 0.0,
                    f"training {seed}/{arm} {numeric_name} is invalid",
                )
            require(
                type(row.get("parameter_count")) is int and row["parameter_count"] > 0,
                f"training {seed}/{arm} parameter_count is invalid",
            )
            counts = tuple(
                row.get(name)
                for name in (
                    "terminal_proposal_count",
                    "terminal_candidates_accepted",
                    "terminal_candidates_rejected",
                )
            )
            require(
                all(type(value) is int and value >= 0 for value in counts)
                and counts[0] == counts[1] + counts[2],
                f"training proposal arithmetic mismatch: {seed}/{arm}",
            )
            trajectory = row.get("trajectory")
            require(
                isinstance(trajectory, list) and trajectory,
                f"training trajectory is missing: {seed}/{arm}",
            )
            final_step = require_mapping(trajectory[-1], f"training final step {seed}/{arm}")
            require(
                final_step.get("loss") == row.get("final_loss"),
                f"training final loss/trajectory mismatch: {seed}/{arm}",
            )


def verify_evaluation_bank(bank: Mapping[str, Any]) -> str:
    require(
        set(bank) == {"schema", "audit_bank", "causal_banks", "deep_banks", "fingerprint"},
        "evaluation-bank top-level schema mismatch",
    )
    require(bank.get("schema") == EVAL_BANK_SCHEMA, "evaluation-bank schema mismatch")
    return _verify_self_seal(bank, "fingerprint", "evaluation bank")


def _require_status(value: Any, allowed: set[str], label: str) -> str:
    require(isinstance(value, str) and value in allowed, f"invalid {label}: {value!r}")
    return value


def verify_scientific_status(
    profile: str,
    gates: Mapping[str, Any],
    completion: Mapping[str, Any],
) -> str:
    require(
        set(gates)
        == {
            "execution_integrity",
            "assay_validity",
            "scientific_flatness",
            "scientific_connection",
            "ambient_necessity",
            "control_gates",
            "integrity_checks",
            "scientific_checks",
            "all_primary_checks_pass",
        },
        "GATES.json top-level schema mismatch",
    )
    execution = _require_status(
        gates.get("execution_integrity"), {"PASS", "FAIL"}, "execution integrity"
    )
    assay = _require_status(gates.get("assay_validity"), {"PASS", "FAIL"}, "assay validity")
    controls = require_mapping(gates.get("control_gates"), "control gates")
    require(controls, "control gates may not be empty")
    require(all(type(value) is bool for value in controls.values()), "control gates must be booleans")
    require(
        (assay == "PASS") == all(controls.values()),
        "assay validity is inconsistent with control gates",
    )
    integrity_checks = require_mapping(gates.get("integrity_checks"), "integrity checks")
    require(integrity_checks, "integrity checks may not be empty")
    require(
        all(type(value) is bool for value in integrity_checks.values()),
        "integrity checks must be booleans",
    )
    require(
        (execution == "PASS") == all(integrity_checks.values()),
        "execution integrity is inconsistent with integrity checks",
    )
    checks = require_mapping(gates.get("scientific_checks"), "scientific checks")
    require(checks, "scientific checks may not be empty")
    decisions: dict[str, bool] = {}
    for name, raw in checks.items():
        require(isinstance(name, str) and name, "scientific check name is invalid")
        check = require_mapping(raw, f"scientific check {name}")
        require(type(check.get("pass")) is bool, f"scientific check {name} lacks a boolean pass")
        decisions[name] = check["pass"]
    primary = [
        decision
        for name, decision in decisions.items()
        if name != "exact_arm_full_flatness_secondary"
    ]
    require(primary, "no primary scientific checks were recorded")
    expected_all_primary = all(primary)
    require(
        type(gates.get("all_primary_checks_pass")) is bool
        and gates["all_primary_checks_pass"] == expected_all_primary,
        "all_primary_checks_pass is inconsistent with scientific checks",
    )
    scientific = _require_status(
        gates.get("scientific_flatness"),
        {"PASS", "FAIL", "NOT_EVALUATED", "DEVELOPMENTAL_NOT_ADJUDICATED"},
        "scientific flatness",
    )
    if profile == "pilot":
        expected_scientific = (
            "NOT_EVALUATED"
            if execution != "PASS" or assay != "PASS"
            else ("PASS" if expected_all_primary else "FAIL")
        )
    else:
        expected_scientific = "DEVELOPMENTAL_NOT_ADJUDICATED"
    require(scientific == expected_scientific, "scientific-flatness status is inconsistent")
    require(
        gates.get("scientific_connection") == "NOT_EVALUATED",
        "scientific connection must remain NOT_EVALUATED",
    )
    require(
        gates.get("ambient_necessity") == "SEPARATE_CALIBRATION_ONLY",
        "ambient-necessity status mismatch",
    )
    for key in ("execution_integrity", "assay_validity", "scientific_flatness"):
        require(completion.get(key) == gates.get(key), f"completion/GATES mismatch for {key}")
    require(execution == "PASS", "canonical pilot execution integrity did not pass")
    require(assay == "PASS", "canonical pilot assay validity did not pass")
    require(scientific in {"PASS", "FAIL"}, "canonical pilot science was not adjudicated")
    return scientific


def verify_result_directory(
    root: Path,
    directory: Path,
    *,
    preregistration_sha256: str,
    current_source_digest: str,
    current_source_files: Sequence[str],
    contract: Mapping[str, Any] | None,
    contract_sha256: str | None,
) -> Mapping[str, Any]:
    relative_directory = directory.relative_to(root).as_posix()
    for name in ("RUN_STARTED.json", "RESULTS.json", "GATES.json", "RUN_COMPLETE.json", "REPORT.md"):
        require((directory / name).is_file(), f"incomplete result directory {relative_directory}: {name}")
    started = require_mapping(load_json(directory / "RUN_STARTED.json"), "RUN_STARTED.json")
    result = require_mapping(load_json(directory / "RESULTS.json"), "RESULTS.json")
    gates = require_mapping(load_json(directory / "GATES.json"), "GATES.json")
    completion = require_mapping(load_json(directory / "RUN_COMPLETE.json"), "RUN_COMPLETE.json")
    require(started.get("schema") == STARTED_SCHEMA, "RUN_STARTED schema mismatch")
    require(result.get("schema") == RESULT_SCHEMA, "RESULTS schema mismatch")
    require(completion.get("schema") == COMPLETION_SCHEMA, "RUN_COMPLETE schema mismatch")
    for label, artifact in (
        ("RUN_STARTED", started),
        ("RESULTS", result),
        ("RUN_COMPLETE", completion),
    ):
        require(artifact.get("version") == VERSION, f"{label} version mismatch")
    profile = result.get("profile")
    require(profile in {"smoke", "screen", "pilot"}, "RESULTS profile is invalid")
    run_mode = result.get("run_mode")
    allowed_modes = {
        "smoke": {"developmental"},
        "screen": {"developmental"},
        "pilot": {"fresh_pilot", "non_evidentiary_pilot_replay"},
    }
    require(run_mode in allowed_modes[profile], "RESULTS run_mode/profile mismatch")
    for label, artifact in (("RUN_STARTED", started), ("RUN_COMPLETE", completion)):
        require(artifact.get("profile") == profile, f"{label}/RESULTS profile mismatch")
        require(artifact.get("run_mode") == run_mode, f"{label}/RESULTS run_mode mismatch")
    if run_mode == "fresh_pilot":
        require(directory.name == "flat_connection_pilot", "fresh pilot is not in its canonical directory")
    require(
        started.get("source_digest")
        == result.get("source_digest")
        == current_source_digest,
        "run source digest does not match the packaged source tree",
    )
    require(
        started.get("preregistration_sha256")
        == result.get("preregistration_sha256")
        == preregistration_sha256,
        "run preregistration digest mismatch",
    )
    require(
        result.get("source_files") == list(current_source_files),
        "RESULTS source-file inventory mismatch",
    )
    if profile == "pilot":
        require(contract is not None, "pilot result requires FLAT_CONNECTION_CONTRACT.json")
        require(result.get("config") == contract.get("pilot_profile"), "pilot config/contract mismatch")
        require(result.get("thresholds") == contract.get("thresholds"), "pilot thresholds/contract mismatch")
    for label, artifact in (("RUN_STARTED", started), ("RESULTS", result), ("RUN_COMPLETE", completion)):
        require(
            artifact.get("contract_sha256") == contract_sha256,
            f"{label} contract hash mismatch",
        )

    require(result.get("status") == gates, "RESULTS status differs from GATES.json")
    scientific = verify_scientific_status(profile, gates, completion)

    seal_path = directory / "CHECKPOINT_SEAL.json"
    embedded_seal = result.get("checkpoint_seal")
    require(seal_path.is_file(), "canonical pilot is missing CHECKPOINT_SEAL.json")
    require(isinstance(embedded_seal, dict), "RESULTS is missing its embedded checkpoint seal")
    seal = require_mapping(load_json(seal_path), "CHECKPOINT_SEAL.json")
    config = require_mapping(result.get("config"), "RESULTS config")
    seeds = config.get("seeds")
    require(
        isinstance(seeds, list) and all(type(seed) is int for seed in seeds),
        "RESULTS config seeds are invalid",
    )
    expected_arms = contract.get("arms") if contract is not None else None
    require(
        isinstance(expected_arms, list)
        and all(isinstance(arm, str) for arm in expected_arms),
        "registered arm list is invalid",
    )
    seal_rows = verify_checkpoint_seal(
        directory,
        seal,
        current_source_digest,
        expected_arms=expected_arms,
        expected_seeds=seeds,
    )
    verify_training_grid(
        result.get("training"),
        seal_rows,
        expected_arms=expected_arms,
        expected_seeds=seeds,
    )
    require(embedded_seal == seal, "RESULTS checkpoint seal differs from CHECKPOINT_SEAL.json")

    bank_path = directory / "EVAL_BANK.json"
    bank_fingerprint = result.get("evaluation_bank_fingerprint")
    require(bank_path.is_file(), "canonical pilot is missing EVAL_BANK.json")
    require_sha256(bank_fingerprint, "RESULTS evaluation-bank fingerprint")
    bank = require_mapping(load_json(bank_path), "EVAL_BANK.json")
    observed_fingerprint = verify_evaluation_bank(bank)
    require(
        bank_fingerprint == observed_fingerprint,
        "RESULTS evaluation-bank fingerprint mismatch",
    )

    chart = require_mapping(result.get("chart"), "RESULTS chart")
    chart_path = _safe_member(directory, chart.get("path"), "result chart")
    chart_sha = require_sha256(chart.get("sha256"), "RESULTS chart sha256")
    require(file_sha256(chart_path) == chart_sha, "chart hash mismatch")
    for key, name in (
        ("results_sha256", "RESULTS.json"),
        ("report_sha256", "REPORT.md"),
    ):
        require(
            completion.get(key) == file_sha256(directory / name),
            f"RUN_COMPLETE hash mismatch for {name}",
        )
    require(completion.get("chart_sha256") == chart_sha, "RUN_COMPLETE chart hash mismatch")
    return {
        "path": relative_directory,
        "profile": profile,
        "run_mode": run_mode,
        "execution_integrity": gates["execution_integrity"],
        "assay_validity": gates["assay_validity"],
        "scientific_flatness": scientific,
    }


def discover_result_directories(root: Path) -> list[Path]:
    """Return only the canonical evidentiary pilot.

    Historical smoke, screen, and replay directories remain manifest-covered,
    but their deliberately older source seals cannot satisfy the live v2 pilot
    contract and they cannot stand in for the official result.
    """

    results = root / "results"
    require(results.is_dir() and not results.is_symlink(), "results must be a real directory")
    canonical = results / "flat_connection_pilot"
    require(canonical.is_dir() and not canonical.is_symlink(), "canonical pilot directory is missing")
    return [canonical]


def _load_verified_runner(root: Path) -> Any:
    """Import the manifest-verified runner only after the byte trust boundary."""

    runner_path = root / "run_flat_connection.py"
    require(runner_path.is_file(), "manifested run_flat_connection.py is missing")
    module_name = "_komorebi_verified_flat_connection_runner"
    spec = importlib.util.spec_from_file_location(module_name, runner_path)
    require(spec is not None and spec.loader is not None, "cannot load verified runner")
    source = str(root / "src")
    additions = [str(root), source]
    previous_path = list(sys.path)
    try:
        for value in reversed(additions):
            if value not in sys.path:
                sys.path.insert(0, value)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as error:
        sys.modules.pop(module_name, None)
        raise VerificationError(f"verified runner import failed: {error}") from error
    finally:
        sys.path[:] = previous_path
    return module


def _verify_checkpoint_payloads(
    runner: Any,
    directory: Path,
    profile: Mapping[str, Any],
    seal_rows: Mapping[tuple[int, str], Mapping[str, Any]],
    training: Mapping[str, Any],
    source_sha256: str,
) -> int:
    expected_payload_keys = {
        "schema",
        "version",
        "arm",
        "config",
        "model_class",
        "state_dict",
        "initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "source_digest",
    }
    count = 0
    for seed in profile["seeds"]:
        for arm in runner.PRIMARY_FLATNESS_ARMS:
            seed = int(seed)
            path = directory / "checkpoints" / f"{arm}_seed{seed}.pt"
            try:
                payload = runner.torch.load(
                    path,
                    map_location="cpu",
                    weights_only=True,
                )
            except Exception as error:
                raise VerificationError(
                    f"safe checkpoint load failed for {arm}/seed{seed}: {error}"
                ) from error
            require(isinstance(payload, dict), f"checkpoint payload is not a mapping: {arm}/{seed}")
            require(set(payload) == expected_payload_keys, f"checkpoint payload schema mismatch: {arm}/{seed}")
            require(
                payload.get("schema") == "komorebi.flat_packet_connection.checkpoint.v1"
                and payload.get("version") == VERSION
                and payload.get("arm") == arm
                and payload.get("source_digest") == source_sha256,
                f"checkpoint identity mismatch: {arm}/{seed}",
            )
            config = runner.train_config(profile, seed, "cpu")
            require(
                runner.strict_json_equal(payload.get("config"), runner.asdict(config)),
                f"checkpoint config mismatch: {arm}/{seed}",
            )
            model = runner.build_flatness_model(config, arm).to("cpu")
            require(
                payload.get("model_class") == type(model).__name__,
                f"checkpoint model class mismatch: {arm}/{seed}",
            )
            require(
                runner.state_dict_digest(model) == payload.get("initial_state_digest"),
                f"checkpoint initial-state digest mismatch: {arm}/{seed}",
            )
            state = payload.get("state_dict")
            require(isinstance(state, dict), f"checkpoint state_dict is invalid: {arm}/{seed}")
            for name, tensor in state.items():
                require(isinstance(name, str), f"checkpoint tensor name is invalid: {arm}/{seed}")
                require(
                    isinstance(tensor, runner.torch.Tensor)
                    and bool(runner.torch.isfinite(tensor).all()),
                    f"checkpoint tensor is nonfinite or invalid: {arm}/{seed}/{name}",
                )
            try:
                model.load_state_dict(state, strict=True)
            except Exception as error:
                raise VerificationError(
                    f"checkpoint tensor key/shape mismatch: {arm}/{seed}: {error}"
                ) from error
            final_digest = runner.state_dict_digest(model)
            require(
                final_digest == payload.get("final_state_digest"),
                f"checkpoint final-state digest mismatch: {arm}/{seed}",
            )
            seal_row = seal_rows[(seed, arm)]
            require(
                seal_row.get("state_digest") == final_digest
                and seal_row.get("sha256") == file_sha256(path),
                f"checkpoint/seal mismatch: {arm}/{seed}",
            )
            training_row = training[str(seed)][arm]
            for key in (
                "config",
                "initial_state_digest",
                "final_state_digest",
                "episode_stream_digest",
                "terminal_proposal_stream_digest",
                "relation_schedule_digest",
            ):
                require(
                    runner.strict_json_equal(training_row.get(key), payload.get(key)),
                    f"training/checkpoint metadata mismatch for {key}: {arm}/{seed}",
                )
            del model, payload
            count += 1
    return count


def _verify_runtime_evidence(
    root: Path,
    directory: Path,
    preregistration: Mapping[str, Any],
    preregistration_sha256: str,
    contract: Mapping[str, Any],
    current_source_digest: str,
) -> Mapping[str, Any]:
    """Replay deterministic structural checks using the manifested runner."""

    runner = _load_verified_runner(root)
    try:
        require(runner.VERSION == VERSION, "verified runner version mismatch")
        runner.torch.set_num_threads(1)
        runner.torch.use_deterministic_algorithms(True)
        try:
            runner.torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
        live_preregistration = runner.validate_preregistration()
        require(
            runner.strict_json_equal(live_preregistration, preregistration),
            "runner/preregistration validation mismatch",
        )
        live_source_digest, live_source_files = runner.source_digest()
        require(live_source_digest == current_source_digest, "runner/verifier source digest mismatch")
        runner.validate_pilot_contract(
            contract,
            source_sha256=current_source_digest,
            preregistration_sha256=preregistration_sha256,
            preregistration=preregistration,
        )
        profile = dict(runner.PROFILE_CONFIG["pilot"])
        expected_profile = {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in profile.items()
        }
        require(
            runner.strict_json_equal(contract.get("pilot_profile"), expected_profile),
            "contract does not match the executable pilot profile",
        )
        require(
            list(runner.PRIMARY_FLATNESS_ARMS) == contract.get("arms"),
            "contract does not match executable arm order",
        )
        require(
            runner.strict_json_equal(contract.get("thresholds"), dict(runner.FROZEN_THRESHOLDS)),
            "contract does not match executable thresholds",
        )

        result = require_mapping(load_json(directory / "RESULTS.json"), "RESULTS.json")
        gates = require_mapping(load_json(directory / "GATES.json"), "GATES.json")
        started = require_mapping(load_json(directory / "RUN_STARTED.json"), "RUN_STARTED.json")
        seal = require_mapping(load_json(directory / "CHECKPOINT_SEAL.json"), "CHECKPOINT_SEAL.json")
        bank = require_mapping(load_json(directory / "EVAL_BANK.json"), "EVAL_BANK.json")
        require(
            runner.strict_json_equal(result.get("config"), expected_profile),
            "RESULTS config differs from executable pilot profile",
        )
        require(result.get("source_files") == live_source_files, "runner source-file list mismatch")
        live_runtime = runner.runtime_receipt()
        require(
            runner.strict_json_equal(started.get("runtime"), result.get("runtime"))
            and runner.strict_json_equal(result.get("runtime"), live_runtime),
            "pilot runtime receipt does not match the verification runtime",
        )

        seal_rows = runner.validate_checkpoint_seal(
            directory,
            seal,
            profile,
            expected_source_digest=current_source_digest,
        )
        training = require_mapping(result.get("training"), "RESULTS training")
        checkpoint_count = _verify_checkpoint_payloads(
            runner,
            directory,
            profile,
            seal_rows,
            training,
            current_source_digest,
        )
        require(checkpoint_count == 30, "canonical pilot does not contain exactly 30 checkpoints")

        with tempfile.TemporaryDirectory(prefix="komorebi-v05-bank-") as temporary:
            temporary_path = Path(temporary)
            audit_bank, causal_banks, rebuilt_bank = runner.build_postseal_banks(
                temporary_path,
                profile,
            )
            runner.validate_eval_bank_receipt(
                temporary_path,
                audit_bank,
                causal_banks,
                rebuilt_bank,
                profile,
            )
            require(
                runner.strict_json_equal(bank, rebuilt_bank),
                "stored evaluation bank differs from deterministic reconstruction",
            )

            expected_controls = runner.evaluate_control_suite(
                audit_bank,
                deep_examples=min(256, int(profile["deep_examples"])),
                device="cpu",
            )
            controls = require_mapping(result.get("controls"), "RESULTS controls")
            require(
                runner.strict_json_equal(controls, expected_controls),
                "stored deterministic controls differ from reconstruction",
            )

            records = require_mapping(result.get("records"), "RESULTS records")
            aggregate = require_mapping(result.get("aggregate"), "RESULTS aggregate")
            integrity = runner.validate_execution_integrity(
                records,
                aggregate,
                controls,
                profile,
            )
            require(
                integrity.get("valid") is True and all(integrity.get("checks", {}).values()),
                f"registered result grid is incomplete: {integrity}",
            )
            require(
                runner.strict_json_equal(gates.get("integrity_checks"), integrity["checks"]),
                "stored integrity checks differ from independent validation",
            )
            rebuilt_aggregate = runner.aggregate_records(records, profile)
            require(
                runner.strict_json_equal(aggregate, rebuilt_aggregate),
                "stored aggregate differs from recomputation",
            )
            rebuilt_gates = runner.adjudicate(
                records,
                rebuilt_aggregate,
                controls,
                "pilot",
                profile,
            )
            require(
                runner.strict_json_equal(gates, rebuilt_gates),
                "stored scientific adjudication differs from recomputation",
            )
            expected_report = runner.render_report(result)
            require(
                (directory / "REPORT.md").read_text(encoding="utf-8") == expected_report,
                "REPORT.md differs from deterministic rendering",
            )
            chart_name = runner.render_chart(temporary_path, rebuilt_aggregate, profile)
            require(
                file_sha256(temporary_path / chart_name)
                == file_sha256(directory / chart_name),
                "retained chart differs from deterministic regeneration",
            )

        from komorebi_neuralese.ambient_delay import deterministic_self_check

        anc4 = deterministic_self_check()
        require(anc4.get("status") == "PASS", "ANC-4 deterministic self-check failed")
    except VerificationError:
        raise
    except Exception as error:
        raise VerificationError(f"runtime evidence verification failed: {error}") from error
    return {
        "checkpoint_payloads_verified": checkpoint_count,
        "evaluation_bank_reconstructed": True,
        "controls_reconstructed": True,
        "aggregate_recomputed": True,
        "adjudication_recomputed": True,
        "report_regenerated": True,
        "chart_regenerated": True,
        "anc4_self_check": "PASS",
    }


def verify_package(root: Path) -> Mapping[str, Any]:
    root = root.resolve(strict=True)
    manifest, inventory = verify_manifest(root)
    current_source_digest, current_source_files = source_digest(root, inventory)
    prereg, prereg_sha = verify_preregistration(root)
    contract, contract_sha = verify_contract(
        root,
        prereg,
        prereg_sha,
        current_source_digest,
    )
    require(contract is not None, "canonical package requires FLAT_CONNECTION_CONTRACT.json")
    runs = [
        verify_result_directory(
            root,
            directory,
            preregistration_sha256=prereg_sha,
            current_source_digest=current_source_digest,
            current_source_files=current_source_files,
            contract=contract,
            contract_sha256=contract_sha,
        )
        for directory in discover_result_directories(root)
    ]
    fresh_pilots = [run for run in runs if run["run_mode"] == "fresh_pilot"]
    require(len(runs) == 1 and len(fresh_pilots) == 1, "exactly one fresh canonical pilot is required")
    runtime_verification = _verify_runtime_evidence(
        root,
        root / "results" / "flat_connection_pilot",
        prereg,
        prereg_sha,
        contract,
        current_source_digest,
    )
    receipt = {
        "schema": VERIFICATION_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "status": "PASS",
        "manifest_file_count": manifest["file_count"],
        "manifest_sha256": file_sha256(root / MANIFEST_NAME),
        "source_digest": current_source_digest,
        "source_file_count": len(current_source_files),
        "preregistration_sha256": prereg_sha,
        "contract_sha256": contract_sha,
        "runs": runs,
        "runtime_verification": runtime_verification,
        "scientific_failures_retained": sum(
            run["scientific_flatness"] == "FAIL" for run in runs
        ),
    }
    # Re-scan at the end so verification itself cannot leave hidden bytecode.
    package_inventory(root)
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="write the v5 manifest and SHA256SUMS, then exit",
    )
    args = parser.parse_args(argv)
    if not (sys.flags.ignore_environment and sys.flags.safe_path and sys.dont_write_bytecode):
        print("Run with: python -E -P -B verify_flat_connection.py", file=sys.stderr)
        return 2
    try:
        if args.write_manifest:
            result = write_v5_manifest(args.root)
            print(json.dumps({key: result[key] for key in ("schema", "version", "file_count")}, sort_keys=True))
        else:
            print(json.dumps(verify_package(args.root), indent=2, sort_keys=True, allow_nan=False))
    except (OSError, VerificationError, ValueError) as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AUTHOR",
    "CONTRACT_SCHEMA",
    "MANIFEST_SCHEMA",
    "REGISTERED_DESIGN_FIELDS",
    "VERSION",
    "VerificationError",
    "canonical_json_bytes",
    "file_sha256",
    "source_digest",
    "verify_package",
    "write_v5_manifest",
]
