#!/usr/bin/env python3
"""Verify the complete Komorebi Neuralese packet-closure package."""

from __future__ import annotations

import sys


if not (sys.flags.ignore_environment and sys.flags.safe_path):
    raise SystemExit("Run verification with: python -E -P -B verify_package.py")
sys.dont_write_bytecode = True

# Only isolated standard-library imports are permitted until every packaged
# byte has been enumerated and matched to the self-excluding manifest.
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
VERSION = "0.4.0"
AUTHOR = "Komorebi P."
MANIFEST_SCHEMA = "komorebi.neuralese.package_manifest.v4"
SELF_EXCLUDED = frozenset({"MANIFEST.json", "SHA256SUMS.txt"})
HEX_256 = re.compile(r"[0-9a-f]{64}\Z")


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_relative_path(relative: str) -> None:
    parsed = PurePosixPath(relative)
    if (
        not relative
        or parsed.is_absolute()
        or relative != parsed.as_posix()
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or "\\" in relative
    ):
        raise ValueError(f"unsafe package path: {relative!r}")


def is_excluded(relative: str, path: Path) -> bool:
    return (
        path.name in SELF_EXCLUDED
        or relative == "prof.out"
        or "__pycache__" in path.parts
        or ".pytest_cache" in path.parts
        or relative.startswith("results/local/")
        or relative.startswith("results/local_")
    )


def iter_package_files(root: Path = ROOT) -> Iterable[tuple[str, Path]]:
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError(f"symbolic links are forbidden in the package: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        validate_relative_path(relative)
        if not is_excluded(relative, path):
            yield relative, path


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json_path(path: Path) -> Any:
    if not path.exists():
        fail(f"Missing required artifact: {path.relative_to(ROOT).as_posix()}")
    if path.is_symlink():
        fail(f"Symbolic links are forbidden: {path.relative_to(ROOT).as_posix()}")
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
            object_pairs_hook=_strict_json_object,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        fail(f"Invalid strict JSON: {path.relative_to(ROOT).as_posix()}: {error}")


def load_json(relative: str) -> Any:
    validate_relative_path(relative)
    return load_json_path(ROOT / PurePosixPath(relative))


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def require_sha256(value: Any, label: str) -> str:
    require(
        isinstance(value, str) and HEX_256.fullmatch(value) is not None,
        f"{label} is not a lowercase SHA-256 digest",
    )
    return value


def verify_manifest() -> Mapping[str, Any]:
    for self_file in (ROOT / "MANIFEST.json", ROOT / "SHA256SUMS.txt"):
        require(self_file.exists(), f"Missing required artifact: {self_file.name}")
        require(not self_file.is_symlink(), f"Symbolic links are forbidden: {self_file.name}")

    manifest_path = ROOT / "MANIFEST.json"
    manifest = require_mapping(load_json_path(manifest_path), "MANIFEST.json")
    require(
        set(manifest) == {"schema", "version", "author", "file_count", "files"},
        "Manifest top-level schema mismatch",
    )
    require(manifest.get("schema") == MANIFEST_SCHEMA, "Manifest schema mismatch")
    require(manifest.get("version") == VERSION, "Manifest version mismatch")
    require(manifest.get("author") == AUTHOR, "Manifest author mismatch")
    records = manifest.get("files")
    require(isinstance(records, list), "Manifest files must be a list")
    require(
        type(manifest.get("file_count")) is int
        and manifest["file_count"] >= 0
        and manifest["file_count"] == len(records),
        "Manifest file count mismatch",
    )

    expected_records: dict[str, tuple[int, str]] = {}
    observed_order: list[str] = []
    for index, raw_record in enumerate(records):
        record = require_mapping(raw_record, f"manifest record {index}")
        require(
            set(record) == {"path", "size", "sha256"},
            f"Manifest record {index} has an unexpected schema",
        )
        relative = record.get("path")
        require(isinstance(relative, str), f"Manifest record {index} path is invalid")
        try:
            validate_relative_path(relative)
        except ValueError as error:
            fail(str(error))
        require(relative not in expected_records, f"Duplicate manifest path: {relative}")
        size = record.get("size")
        require(
            type(size) is int and size >= 0,
            f"Invalid manifest size: {relative}",
        )
        digest = require_sha256(record.get("sha256"), f"Manifest digest {relative}")
        expected_records[relative] = (size, digest)
        observed_order.append(relative)
    require(observed_order == sorted(observed_order), "Manifest paths are not sorted")

    expected_sums = "".join(
        f"{expected_records[path][1]}  {path}\n" for path in observed_order
    )
    try:
        actual_sums = (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8")
    except UnicodeError as error:
        fail(f"Invalid SHA256SUMS encoding: {error}")
    require(actual_sums == expected_sums, "SHA256SUMS is not the canonical manifest rendering")

    try:
        actual = dict(iter_package_files(ROOT))
    except ValueError as error:
        fail(str(error))
    require(set(actual) == set(expected_records), (
        "Manifest path-set mismatch; "
        f"missing={sorted(set(actual) - set(expected_records))}, "
        f"extra={sorted(set(expected_records) - set(actual))}"
    ))
    for relative, path in actual.items():
        size, expected_digest = expected_records[relative]
        require(path.stat().st_size == size, f"Manifest size mismatch: {relative}")
        require(file_sha256(path) == expected_digest, f"Checksum mismatch: {relative}")
        if path.suffix.lower() == ".json":
            load_json_path(path)
    return manifest


_unsafe_preimport_paths = [
    path
    for path in ROOT.rglob("*")
    if path.is_symlink()
    or path.name == "__pycache__"
    or path.suffix.lower() in {".pyc", ".pyo"}
]
if _unsafe_preimport_paths:
    raise SystemExit(
        "symlinks and local bytecode/cache artifacts are forbidden before verification: "
        + ", ".join(
            path.relative_to(ROOT).as_posix()
            for path in _unsafe_preimport_paths[:8]
        )
    )

_BOOTSTRAP_MANIFEST = verify_manifest()

import copy
import math
import os
import subprocess
import tempfile
from dataclasses import asdict
from datetime import datetime

# Import the external numeric runtime before adding package-controlled paths.
import torch

for module_name in tuple(sys.modules):
    if (
        module_name in {"run_packet_closure", "build_manifest"}
        or module_name == "komorebi_neuralese"
        or module_name.startswith("komorebi_neuralese.")
    ):
        fail(f"Package module was loaded before manifest verification: {module_name}")

# Manifest-verified local modules now take priority over installed copies.
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

import run_packet_closure as closure
from komorebi_neuralese.algebra import canonical_maps
from komorebi_neuralese.ambient_eval import (
    episode_bank_receipts,
    episode_contract,
    make_episode_bank,
)
from komorebi_neuralese.packet_closure_eval import (
    freeze_heldout_bank,
    sample_switch_words,
)
from komorebi_neuralese.packet_closure_train import (
    build_packet_closure_model,
    construction_checkpoint_metadata,
    d4_terminal_reserved_mask,
    get_packet_closure_arm,
    make_v04_construction_bank,
    make_v04_suffix_plan,
    shared_initialization_digest,
    state_dict_digest,
    terminal_firewall_policy_digest,
)
from komorebi_neuralese.reporting import source_files, tree_digest


V01_SOURCE_DIGEST = (
    "a5f2db2864b664837cf9bde4e44b9ef36efe296026af952f0b097c6c6b80c9ac"
)
V02_SOURCE_DIGEST = (
    "cb5d6b1eccb7b9e05cbbe16637dac90cc1334a469fb9add6472238affa61210e"
)
V03_SOURCE_DIGEST = (
    "b9a85f36687610a84d813130e910a97048bee324b5ea6e9a3b98bda5118a418f"
)
V03_CONTRACT_SHA256 = (
    "eab8e8ffc6d58611e0de1de8e3e2e9f029e2667f2fd3ca6ab485dbb2e56de5c7"
)


def numerically_close_structure(
    actual: Any,
    expected: Any,
    *,
    relative_tolerance: float = 1e-6,
    absolute_tolerance: float = 1e-8,
) -> bool:
    """Compare replay output with exact topology and cross-build float tolerance."""

    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            numerically_close_structure(
                actual[key],
                expected[key],
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
            )
            for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            numerically_close_structure(
                left,
                right,
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
            )
            for left, right in zip(actual, expected)
        )
    if isinstance(expected, float):
        return math.isfinite(actual) and math.isfinite(expected) and math.isclose(
            actual,
            expected,
            rel_tol=relative_tolerance,
            abs_tol=absolute_tolerance,
        )
    return bool(actual == expected)


def require_fraction(value: Any, label: str, *, allow_none: bool = False) -> float | None:
    if value is None and allow_none:
        return None
    require(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and 0.0 <= float(value) <= 1.0,
        f"{label} is not a finite unit-interval fraction",
    )
    return float(value)


def safe_artifact_path(base: Path, relative: Any, label: str) -> Path:
    require(isinstance(relative, str), f"{label} path must be a string")
    try:
        validate_relative_path(relative)
    except ValueError as error:
        fail(f"{label}: {error}")
    candidate = base.joinpath(*PurePosixPath(relative).parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(base.resolve(strict=True))
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        fail(f"{label} path escapes or is missing: {relative}: {error}")
    require(not candidate.is_symlink(), f"{label} cannot be a symbolic link: {relative}")
    require(candidate.is_file(), f"{label} is not a regular file: {relative}")
    return candidate


def parse_time(value: Any, label: str) -> datetime:
    require(isinstance(value, str), f"{label} timestamp is missing")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as error:
        fail(f"Invalid {label} timestamp: {error}")
    require(result.tzinfo is not None, f"{label} timestamp is not timezone-aware")
    return result


def verify_legacy_lineage() -> None:
    legacy = require_mapping(
        load_json("results/pilot/RUN_COMPLETE.json"), "legacy completion"
    )
    require(
        legacy.get("schema") == "komorebi.neuralese.run_complete.v1"
        and legacy.get("profile") == "pilot"
        and legacy.get("all_development_gates_passed") is True,
        "Legacy v0.1.1 parent pilot is incomplete",
    )


def verify_v02_parent(directory: str, completion_schema: str, result_schema: str) -> None:
    completion = require_mapping(
        load_json(f"{directory}/RUN_COMPLETE.json"), f"{directory} completion"
    )
    result = require_mapping(load_json(f"{directory}/RESULTS.json"), f"{directory} result")
    require(completion.get("schema") == completion_schema, f"Parent schema mismatch: {directory}")
    require(completion.get("profile") == "pilot", f"Parent profile mismatch: {directory}")
    require(completion.get("all_gates_passed") is True, f"Parent gates failed: {directory}")
    require(
        completion.get("evaluation_source_digest") == V02_SOURCE_DIGEST,
        f"Parent completion source mismatch: {directory}",
    )
    require(result.get("schema") == result_schema, f"Parent result schema mismatch: {directory}")
    require(result.get("version") == "0.2.0", f"Parent result version mismatch: {directory}")
    require(result.get("profile") == "pilot", f"Parent result profile mismatch: {directory}")
    require(
        result.get("source_digest") == V02_SOURCE_DIGEST
        and result.get("evaluation_source_digest") == V02_SOURCE_DIGEST,
        f"Parent result source mismatch: {directory}",
    )
    for key, filename in (("results_sha256", "RESULTS.json"), ("report_sha256", "REPORT.md")):
        require(
            completion.get(key) == file_sha256(ROOT / directory / filename),
            f"Parent completion hash mismatch: {directory}/{filename}",
        )


def verify_v03_ambient() -> Mapping[str, Any]:
    directory = "results/ambient_pilot"
    completion = require_mapping(
        load_json(f"{directory}/RUN_COMPLETE.json"), "ambient completion"
    )
    expected = {
        "schema": "komorebi.neuralese.ambient_diagnostics.completion.v1",
        "version": "0.3.0",
        "profile": "pilot",
        "execution_status": "PASS",
        "assay_status": "PASS",
        "full_developmental_claim": "NOT_CLAIMED_POSTHOC",
        "evaluation_source_digest": V03_SOURCE_DIGEST,
    }
    for key, value in expected.items():
        require(completion.get(key) == value, f"Ambient completion mismatch for {key}")
    for key in ("mechanism_reference_status", "capability_reference_status"):
        require(completion.get(key) in {"PASS", "FAIL"}, f"Ambient {key} is not evaluable")
    for key, filename in (
        ("results_sha256", "RESULTS.json"),
        ("gates_sha256", "GATES.json"),
        ("report_sha256", "REPORT.md"),
        ("environment_sha256", "ENVIRONMENT.json"),
    ):
        require(
            completion.get(key) == file_sha256(ROOT / directory / filename),
            f"Ambient completion hash mismatch: {filename}",
        )

    result = require_mapping(load_json(f"{directory}/RESULTS.json"), "ambient result")
    gates = require_mapping(load_json(f"{directory}/GATES.json"), "ambient gates")
    environment = require_mapping(
        load_json(f"{directory}/ENVIRONMENT.json"), "ambient environment"
    )
    contract = require_mapping(load_json("AMBIENT_PREREGISTRATION.json"), "ambient contract")
    require(file_sha256(ROOT / "AMBIENT_PREREGISTRATION.json") == V03_CONTRACT_SHA256,
            "Archived v0.3 contract hash mismatch")
    require(environment.get("schema") == "komorebi.neuralese.ambient_diagnostics.environment.v1",
            "Ambient environment schema mismatch")
    require(environment.get("device") == "cpu" and environment.get("deterministic_algorithms") is True,
            "Ambient run was not deterministic CPU execution")
    require(result.get("schema") == "komorebi.neuralese.ambient_diagnostics.result.v1",
            "Ambient result schema mismatch")
    require(result.get("version") == "0.3.0" and result.get("profile") == "pilot",
            "Ambient result version/profile mismatch")
    require(result.get("source_digest") == V03_SOURCE_DIGEST,
            "Archived v0.3 result source mismatch")
    expected_study = "developmental_posthoc_frozen_checkpoint_diagnostics"
    require(result.get("study_status") == expected_study, "Ambient study status mismatch")
    require(result.get("contract_sha256") == V03_CONTRACT_SHA256,
            "Ambient result contract hash mismatch")
    for key, value in (
        ("contract_schema", contract.get("schema")),
        ("contract_version", contract.get("version")),
        ("contract_status", contract.get("status")),
        ("contract_sha256", V03_CONTRACT_SHA256),
    ):
        require(result.get(key) == value, f"Ambient result contract mismatch for {key}")
        require(completion.get(key) == value, f"Ambient completion contract mismatch for {key}")
    require(result.get("implementation_contract") == contract.get("profiles", {}).get("pilot"),
            "Ambient result does not match its frozen contract")
    require(result.get("adjudication") == gates, "Ambient RESULTS/GATES mismatch")
    require(gates.get("study_status") == expected_study, "Ambient gates study mismatch")
    require(gates.get("execution_status") == "PASS" and gates.get("assay_status") == "PASS",
            "Ambient execution or assay failed")
    require(gates.get("assay_valid") is True, "Ambient assay validity missing")
    for emitted, contract_key in (
        ("assay_gates", "assay_gates"),
        ("mechanism_reference_gates", "learned_mechanism_reference_gates"),
        ("capability_reference_gates", "capability_reference_gates"),
    ):
        criteria = {name: gate["criterion"] for name, gate in gates[emitted].items()}
        require(criteria == contract.get(contract_key), f"Ambient gate criteria mismatch: {emitted}")
    for key in (
        "execution_status",
        "assay_status",
        "mechanism_reference_status",
        "capability_reference_status",
        "full_developmental_claim",
    ):
        require(completion.get(key) == gates.get(key), f"Ambient status mismatch: {key}")

    parent = require_mapping(
        load_json("results/projective_pilot/RESULTS.json"), "projective parent result"
    )
    for seed in contract["profiles"]["pilot"]["model_seeds"]:
        receipt = result.get("checkpoint_receipts", {}).get(str(seed))
        parent_record = parent.get("records", {}).get(str(seed), {}).get("projective", {})
        parent_checkpoint = parent_record.get("checkpoint", {})
        parent_config = parent_record.get("training", {}).get("config")
        require(isinstance(receipt, dict) and isinstance(parent_config, dict),
                f"Missing archived checkpoint provenance for seed {seed}")
        for key in ("path", "sha256", "schema"):
            require(receipt.get(key) == parent_checkpoint.get(key),
                    f"Archived checkpoint {key} mismatch for seed {seed}")
        require(receipt.get("seed") == seed, f"Archived checkpoint seed mismatch: {seed}")
        require(receipt.get("config") == parent_config,
                f"Archived checkpoint config mismatch for seed {seed}")
        require(receipt.get("training_source_digest") == V01_SOURCE_DIGEST,
                f"Archived checkpoint training source mismatch for seed {seed}")
        checkpoint = safe_artifact_path(ROOT, receipt.get("path"), f"v0.3 checkpoint {seed}")
        require(file_sha256(checkpoint) == receipt.get("sha256"),
                f"Archived checkpoint file hash mismatch for seed {seed}")

    profile = contract["profiles"]["pilot"]
    for family in profile["families"]:
        bank = make_episode_bank(
            contexts=profile["contexts_per_family"],
            length=max(profile["prefixes"]),
            family=family,
            seed=profile["bank_seed"],
        )
        require(result.get("bank_receipts", {}).get(family) == episode_bank_receipts(bank),
                f"Archived deterministic bank mismatch: {family}")
        require(result.get("bank_contracts", {}).get(family) == episode_contract(bank),
                f"Archived deterministic contract mismatch: {family}")
    return completion


def verify_tensor_state_dict(
    state: Any,
    reference: Mapping[str, torch.Tensor],
    label: str,
) -> None:
    require(isinstance(state, dict), f"{label} state_dict is not a mapping")
    require(set(state) == set(reference), f"{label} state_dict key mismatch")
    for name, expected in reference.items():
        value = state[name]
        require(isinstance(value, torch.Tensor), f"{label}/{name} is not a tensor")
        require(value.dtype == expected.dtype, f"{label}/{name} dtype mismatch")
        require(tuple(value.shape) == tuple(expected.shape), f"{label}/{name} shape mismatch")
        require(bool(torch.isfinite(value).all()), f"{label}/{name} is nonfinite")


def verify_checkpoint_panel(
    directory: Path,
    result: Mapping[str, Any],
    seal: Mapping[str, Any],
    config: Mapping[str, Any],
    source_digest: str,
    contract_sha256: str,
    evaluation_bank_sha256: str,
) -> None:
    expected_pairs = [
        (int(seed), arm)
        for seed in config["seeds"]
        for arm in closure.ARM_NAMES
    ]
    receipts = seal.get("checkpoints")
    require(isinstance(receipts, list), "Checkpoint seal receipts are not a list")
    observed_pairs = [(item.get("seed"), item.get("arm")) for item in receipts if isinstance(item, dict)]
    require(observed_pairs == expected_pairs, "Checkpoint receipt coverage/order mismatch")
    require(len({item.get("path") for item in receipts}) == len(expected_pairs),
            "Checkpoint receipt paths are not unique")

    checkpoint_dir = directory / "checkpoints"
    require(checkpoint_dir.is_dir() and not checkpoint_dir.is_symlink(),
            "Pilot checkpoint directory is missing or unsafe")
    expected_paths = {f"checkpoints/{arm}_seed{seed}.pt" for seed, arm in expected_pairs}
    actual_paths = {
        path.relative_to(directory).as_posix()
        for path in checkpoint_dir.rglob("*")
        if path.is_file()
    }
    require(actual_paths == expected_paths,
            f"Checkpoint directory mismatch: expected={sorted(expected_paths)}, actual={sorted(actual_paths)}")

    plan = make_v04_construction_bank(int(config["training"]["auxiliary_max_depth"]))
    expected_construction = construction_checkpoint_metadata(plan)
    require(len(plan.construction) == 20, "Construction bank does not contain exactly 20 words")
    require(
        closure.strict_json_equal(seal.get("construction"), expected_construction)
        and type(seal.get("construction_word_count")) is int
        and seal.get("construction_word_count") == len(plan.construction),
        "Checkpoint seal does not bind the exact canonical construction bank",
    )
    for word in plan.construction:
        encoded = torch.tensor([word], dtype=torch.long)
        require(not bool(d4_terminal_reserved_mask(encoded).any()),
                f"Construction word crosses the terminal firewall: {word}")
    policy_digest = terminal_firewall_policy_digest()
    by_seed_initial: dict[int, set[str]] = {}
    by_seed_shared: dict[int, set[str]] = {}
    by_seed_episode: dict[int, set[str]] = {}
    by_seed_proposals: dict[int, set[str]] = {}
    by_seed_counts: dict[int, set[tuple[int, ...]]] = {}
    seal_time = parse_time(seal.get("sealed_at"), "checkpoint seal")

    for receipt in receipts:
        require(isinstance(receipt, dict), "Malformed checkpoint receipt")
        require(set(receipt) == {
            "arm", "seed", "path", "sha256", "state_dict_digest",
            "construction_digest", "terminal_firewall_policy_digest",
            "terminal_proposal_stream_digest", "sealed_at",
        }, "Checkpoint receipt schema mismatch")
        require(type(receipt.get("seed")) is int, "Checkpoint receipt seed is not an integer")
        require(type(receipt.get("arm")) is str, "Checkpoint receipt arm is not a string")
        seed = receipt["seed"]
        arm = receipt["arm"]
        require(parse_time(receipt.get("sealed_at"), f"checkpoint {seed}/{arm}") <= seal_time,
                f"Checkpoint receipt was sealed after its enclosing seal: {seed}/{arm}")
        expected_relative = f"checkpoints/{arm}_seed{seed}.pt"
        require(receipt.get("path") == expected_relative,
                f"Unexpected checkpoint path for seed={seed}, arm={arm}")
        checkpoint_path = safe_artifact_path(directory, expected_relative, "v0.4 checkpoint")
        digest = file_sha256(checkpoint_path)
        require_sha256(receipt.get("sha256"), f"checkpoint receipt {seed}/{arm}")
        require(digest == receipt.get("sha256"), f"Checkpoint hash mismatch: {expected_relative}")

        record = result.get("records", {}).get(str(seed), {}).get(arm)
        require(isinstance(record, dict), f"Missing result record: seed={seed}, arm={arm}")
        require(closure.strict_json_equal(record.get("checkpoint"), receipt),
                f"Result/seal receipt mismatch: {seed}/{arm}")
        require(record.get("training", {}).get("status") == "COMPLETED",
                f"Training did not complete: {seed}/{arm}")
        require(record.get("evaluation_status") == "COMPLETED",
                f"Evaluation did not complete: {seed}/{arm}")
        require(record.get("checkpoint_reload_verified") is True,
                f"Checkpoint reload was not verified: {seed}/{arm}")
        expected_evaluation_provenance = {
            "checkpoint_sha256": digest,
            "evaluation_bank_sha256": evaluation_bank_sha256,
            "source_digest": source_digest,
            "contract_sha256": contract_sha256,
        }
        require(closure.strict_json_equal(
                    record.get("evaluation_provenance"), expected_evaluation_provenance
                ),
                f"Evaluation provenance mismatch: {seed}/{arm}")
        require(closure.strict_json_equal(
                    record.get("evaluation", {}).get("evaluation_seed"), seed
                ),
                f"Evaluation seed mismatch: {seed}/{arm}")

        try:
            payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        except Exception as error:
            fail(f"Cannot safely load checkpoint {expected_relative}: {error}")
        require(isinstance(payload, dict), f"Checkpoint payload is not a mapping: {expected_relative}")
        require(set(payload) == {
            "schema", "version", "arm", "arm_spec", "train_config",
            "source_digest", "contract_sha256", "state_dict", "construction",
            "terminal_firewall", "provenance",
        }, f"Checkpoint payload schema mismatch: {expected_relative}")
        require(payload.get("schema") == f"{closure.SCHEMA_PREFIX}.checkpoint.v1",
                f"Checkpoint schema mismatch: {expected_relative}")
        require(payload.get("version") == VERSION and payload.get("arm") == arm,
                f"Checkpoint identity mismatch: {expected_relative}")
        require(payload.get("source_digest") == source_digest,
                f"Checkpoint source mismatch: {expected_relative}")
        require(payload.get("contract_sha256") == contract_sha256,
                f"Checkpoint contract mismatch: {expected_relative}")
        require(closure.strict_json_equal(
                    payload.get("arm_spec"), asdict(get_packet_closure_arm(arm))
                ),
                f"Checkpoint arm spec mismatch: {expected_relative}")

        train_config = closure.training_config_for(config, seed=seed, device=torch.device("cpu"))
        require(closure.strict_json_equal(
                    payload.get("train_config"), closure.config_payload(train_config)
                ),
                f"Checkpoint training config mismatch: {expected_relative}")
        require(closure.strict_json_equal(payload.get("construction"), expected_construction),
                f"Checkpoint construction metadata mismatch: {expected_relative}")
        require(not closure.checkpoint_has_forbidden_audit_content(payload),
                f"Checkpoint contains audit-side keys: {expected_relative}")

        fresh = build_packet_closure_model(train_config, arm)
        reference_state = fresh.state_dict()
        verify_tensor_state_dict(payload.get("state_dict"), reference_state, expected_relative)
        fresh_initial = state_dict_digest(fresh)
        fresh_shared = shared_initialization_digest(fresh)
        provenance = payload.get("provenance")
        firewall = payload.get("terminal_firewall")
        require(isinstance(provenance, dict) and isinstance(firewall, dict),
                f"Checkpoint provenance/firewall malformed: {expected_relative}")
        require(set(provenance) == {
            "initial_state_digest", "shared_initialization_digest",
            "final_state_digest", "episode_stream_digest",
        }, f"Checkpoint provenance schema mismatch: {expected_relative}")
        require(set(firewall) == {
            "policy_digest", "proposal_stream_digest", "proposal_count",
            "accepted_count", "rejected_count", "identity_rejections",
            "r2_rejections",
        }, f"Checkpoint firewall schema mismatch: {expected_relative}")
        for field in (
            "initial_state_digest", "shared_initialization_digest",
            "final_state_digest", "episode_stream_digest",
        ):
            require_sha256(provenance.get(field), f"checkpoint {seed}/{arm} {field}")
        require_sha256(
            firewall.get("proposal_stream_digest"),
            f"checkpoint {seed}/{arm} terminal proposal stream",
        )
        require(provenance.get("initial_state_digest") == fresh_initial,
                f"Initial-state digest mismatch: {expected_relative}")
        require(provenance.get("shared_initialization_digest") == fresh_shared,
                f"Shared-initialization digest mismatch: {expected_relative}")
        fresh.load_state_dict(payload["state_dict"], strict=True)
        final_digest = state_dict_digest(fresh)
        require(final_digest == provenance.get("final_state_digest")
                == receipt.get("state_dict_digest"),
                f"Final-state digest mismatch: {expected_relative}")
        require(receipt.get("construction_digest") == expected_construction["construction_digest"],
                f"Construction digest receipt mismatch: {expected_relative}")

        training = record["training"]
        for field in (
            "initial_state_digest", "shared_initialization_digest", "final_state_digest",
            "episode_stream_digest",
        ):
            require(training.get(field) == provenance.get(field),
                    f"Training/payload provenance mismatch for {field}: {seed}/{arm}")
        require(training.get("construction_digest") == expected_construction["construction_digest"]
                and type(training.get("construction_word_count")) is int
                and training.get("construction_word_count") == 20,
                f"Training construction receipt mismatch: {seed}/{arm}")

        require(firewall.get("policy_digest") == policy_digest
                == receipt.get("terminal_firewall_policy_digest")
                == training.get("terminal_firewall_policy_digest"),
                f"Terminal firewall policy mismatch: {seed}/{arm}")
        require(firewall.get("proposal_stream_digest")
                == receipt.get("terminal_proposal_stream_digest")
                == training.get("terminal_proposal_stream_digest"),
                f"Terminal proposal digest mismatch: {seed}/{arm}")
        firewall_count_fields = (
            "proposal_count",
            "accepted_count",
            "rejected_count",
            "identity_rejections",
            "r2_rejections",
        )
        require(
            all(type(firewall.get(field)) is int for field in firewall_count_fields),
            f"Terminal firewall counts are not strict integers: {seed}/{arm}",
        )
        proposed = firewall["proposal_count"]
        accepted = firewall["accepted_count"]
        rejected = firewall["rejected_count"]
        identity_rejections = firewall["identity_rejections"]
        r2_rejections = firewall["r2_rejections"]
        require(
            all(
                value >= 0
                for value in (
                    proposed,
                    accepted,
                    rejected,
                    identity_rejections,
                    r2_rejections,
                )
            )
            and proposed >= accepted,
            f"Terminal firewall counts are negative or ordered incorrectly: {seed}/{arm}",
        )
        require(accepted == int(config["training"]["steps"]) * int(config["training"]["batch_size"]),
                f"Terminal accepted-count mismatch: {seed}/{arm}")
        require(proposed == accepted + rejected
                and rejected == identity_rejections + r2_rejections,
                f"Terminal firewall counts do not close: {seed}/{arm}")
        count_fields = {
            "terminal_proposal_count": proposed,
            "terminal_candidates_accepted": accepted,
            "terminal_candidates_rejected": rejected,
            "terminal_identity_rejections": identity_rejections,
            "terminal_r2_rejections": r2_rejections,
        }
        for field, value in count_fields.items():
            require(type(training.get(field)) is int and training.get(field) == value,
                    f"Terminal count record mismatch for {field}: {seed}/{arm}")

        by_seed_initial.setdefault(seed, set()).add(fresh_initial)
        by_seed_shared.setdefault(seed, set()).add(fresh_shared)
        by_seed_episode.setdefault(seed, set()).add(str(provenance.get("episode_stream_digest")))
        by_seed_proposals.setdefault(seed, set()).add(str(firewall.get("proposal_stream_digest")))
        by_seed_counts.setdefault(seed, set()).add(
            (proposed, accepted, rejected, identity_rejections, r2_rejections)
        )

    for seed in config["seeds"]:
        integer_seed = int(seed)
        require(len(by_seed_initial[integer_seed]) == 1,
                f"Paired full initialization differs within seed {seed}")
        require(len(by_seed_shared[integer_seed]) == 1,
                f"Paired shared initialization differs within seed {seed}")
        require(len(by_seed_episode[integer_seed]) == 1,
                f"Paired episode stream differs within seed {seed}")
        require(len(by_seed_proposals[integer_seed]) == 1,
                f"Paired terminal proposal stream differs within seed {seed}")
        require(len(by_seed_counts[integer_seed]) == 1,
                f"Paired terminal firewall counts differ within seed {seed}")


def verify_evaluation_bank(
    bank: Mapping[str, Any],
    config: Mapping[str, Any],
    source_digest: str,
    contract_sha256: str,
    checkpoint_seal_sha256: str,
) -> None:
    require(bank.get("schema") == f"{closure.SCHEMA_PREFIX}.evaluation_bank.v1",
            "Evaluation-bank schema mismatch")
    require(bank.get("version") == VERSION and bank.get("profile") == "pilot",
            "Evaluation-bank version/profile mismatch")
    require(bank.get("source_digest") == source_digest,
            "Evaluation-bank source mismatch")
    require(bank.get("contract_sha256") == contract_sha256,
            "Evaluation-bank contract mismatch")
    require(bank.get("checkpoint_seal_sha256") == checkpoint_seal_sha256,
            "Evaluation-bank checkpoint-seal link mismatch")
    parse_time(bank.get("materialized_at"), "evaluation-bank materialization")

    expected_banks, expected_receipts = closure.make_eval_banks(config)
    require(closure.strict_json_equal(bank.get("episode_receipts"), expected_receipts),
            "Evaluation episode receipts/contracts are not reproducible")
    expected_cross_context = closure.independent_cross_context_bank_contract(
        expected_banks["intervention"],
        expected_banks["intervention_operator_control"],
        operator_step=int(config["intervention_operator_step_zero_indexed"]),
    )
    require(
        closure.strict_json_equal(
            bank.get("cross_context_operator_control"), expected_cross_context
        ),
        "Cross-context operator-control contract is not reproducible",
    )
    require(
        closure.validate_cross_context_control_contract(
            expected_cross_context, config
        ),
        "Cross-context operator-control bank violates its zero-collision contract",
    )

    audit_plan = make_v04_suffix_plan(max_depth=8)
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    frozen = freeze_heldout_bank(audit_plan, transitions, max_suffixes=None)
    require(closure.strict_json_equal(bank.get("heldout_bank"), frozen.to_dict()),
            "Held-out bank metadata mismatch")
    require(closure.strict_json_equal(
                bank.get("heldout_words"), [list(word) for word in frozen.words]
            ),
            "Held-out word bank mismatch")
    require(closure.strict_json_equal(
                bank.get("heldout_relation_signatures"),
                [list(value) for value in frozen.relation_signatures],
            ),
            "Held-out relation signatures mismatch")
    require(len(frozen.words) == 171 and frozen.words[0] == (),
            "Pilot held-out bank must contain the empty word plus 170 reserved words")
    require(sum(word == () for word in frozen.words) == 1,
            "The empty held-out continuation must appear exactly once")
    identity_signature = tuple(range(8))
    canonical = canonical_maps("d4")
    r2_signature = tuple(int(value) for value in canonical[0][canonical[0]])
    signature_counts = {
        signature: frozen.relation_signatures.count(signature)
        for signature in set(frozen.relation_signatures)
    }
    require(signature_counts == {identity_signature: 86, r2_signature: 85},
            f"Held-out relation-group cardinalities mismatch: {signature_counts}")

    switched_words = sample_switch_words(
        num_actions=2,
        word_length=int(config["switched_word_length"]),
        count=int(config["switched_word_count"]),
        seed=closure.derive_seed(int(config["eval_seed_base"]), "switch_words"),
        include_constant_words=True,
    )
    expected_switch = {
        "word_length": int(config["switched_word_length"]),
        "word_count": len(switched_words),
        "contexts": int(config["switched_contexts"]),
        "exhaustive": len(switched_words) == 2 ** int(config["switched_word_length"]),
        "words": [list(word) for word in switched_words],
    }
    require(closure.strict_json_equal(bank.get("switch_bank"), expected_switch),
            "Switched-word bank mismatch")
    require(
        closure.validate_switch_bank("pilot", config, bank.get("switch_bank", {})),
        "Switched-word bank violates the strict registered schema",
    )
    require(expected_switch["word_length"] == 8
            and expected_switch["word_count"] == 256
            and expected_switch["exhaustive"] is True,
            "Pilot switch bank is not exhaustive at length eight")


def verify_null_closure_semantics(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    seed: int,
    arm: str,
) -> None:
    """Validate baseline, conditional-retention, and post-loop quantities."""

    label = f"seed={seed}, arm={arm}"
    null = evaluation.get("null_loop_retention")
    require(isinstance(null, dict), f"Null-loop result missing: {label}")
    expected_repeats = [int(value) for value in config["null_repeats"]]
    require(null.get("repeats") == expected_repeats,
            f"Null-loop repeat schedule mismatch: {label}")
    expected_bank = freeze_heldout_bank(
        make_v04_suffix_plan(max_depth=8),
        torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long),
        max_suffixes=None,
    ).to_dict()
    require(null.get("bank") == expected_bank, f"Null-loop bank mismatch: {label}")

    baseline = null.get("baseline")
    require(isinstance(baseline, dict), f"Null-loop baseline missing: {label}")
    require(baseline.get("bank") == expected_bank,
            f"Null-loop baseline bank mismatch: {label}")
    require(baseline.get("examples") == int(config["null_examples"]),
            f"Null-loop baseline example count mismatch: {label}")
    baseline_membership = require_fraction(
        baseline.get("strict_membership_fraction"),
        f"Null-loop baseline membership ({label})",
    )
    baseline_word_membership = require_fraction(
        baseline.get("word_weighted_membership_fraction"),
        f"Null-loop baseline word membership ({label})",
    )
    require(baseline_membership is not None and baseline_word_membership is not None,
            f"Null-loop baseline fractions missing: {label}")

    relations = null.get("relations")
    require(isinstance(relations, dict)
            and set(relations) == set(closure.D4_RELATIONS),
            f"Null-loop relation coverage mismatch: {label}")
    for relation_name, expected_word in closure.D4_RELATIONS.items():
        relation = relations[relation_name]
        require(isinstance(relation, dict)
                and relation.get("word") == list(expected_word),
                f"Null-loop relation word mismatch: {label}/{relation_name}")
        by_repeat = relation.get("by_repeat")
        expected_repeat_keys = {str(value) for value in expected_repeats}
        require(isinstance(by_repeat, dict) and set(by_repeat) == expected_repeat_keys,
                f"Null-loop repeat grid mismatch: {label}/{relation_name}")
        for repeat in expected_repeats:
            row = by_repeat[str(repeat)]
            require(isinstance(row, dict),
                    f"Null-loop cell malformed: {label}/{relation_name}/{repeat}")
            require_fraction(
                row.get("strict_membership_fraction"),
                f"post-loop membership ({label}/{relation_name}/{repeat})",
            )
            conditional = require_fraction(
                row.get("conditional_retention_fraction"),
                f"conditional retention ({label}/{relation_name}/{repeat})",
                allow_none=True,
            )
            conditional_word = require_fraction(
                row.get("conditional_word_retention_fraction"),
                f"conditional word retention ({label}/{relation_name}/{repeat})",
                allow_none=True,
            )
            require(
                (conditional is None) == (baseline_membership == 0.0),
                f"Conditional retention definedness disagrees with baseline: "
                f"{label}/{relation_name}/{repeat}",
            )
            require(
                (conditional_word is None) == (baseline_word_membership == 0.0),
                f"Conditional word-retention definedness disagrees with baseline: "
                f"{label}/{relation_name}/{repeat}",
            )
            require_fraction(
                row.get("current_label_accuracy"),
                f"null-loop current-label accuracy ({label}/{relation_name}/{repeat})",
            )
            require_fraction(
                row.get("finite_logit_fraction"),
                f"null-loop finite-logit fraction ({label}/{relation_name}/{repeat})",
            )
        crossing = relation.get("first_sampled_crossing")
        require(isinstance(crossing, dict) and isinstance(crossing.get("observed"), list),
                f"Null-loop crossing record missing: {label}/{relation_name}")
        never = require_fraction(
            crossing.get("never_fraction_among_baseline_members"),
            f"null-loop never-crossed fraction ({label}/{relation_name})",
            allow_none=True,
        )
        require((never is None) == (baseline_membership == 0.0),
                f"Null-loop crossing definedness disagrees with baseline: {label}/{relation_name}")


def verify_primary_grid_and_control_gates(
    result: Mapping[str, Any],
    bank: Mapping[str, Any],
    gates: Mapping[str, Any],
    config: Mapping[str, Any],
) -> None:
    coverage_rows: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        for arm in closure.ARM_NAMES:
            evaluation = result["records"][str(seed)][arm]["evaluation"]
            coverage = closure.validate_primary_closure_grid(evaluation, config)
            require(coverage.get("valid") is True,
                    f"Incomplete primary closure grid: seed={seed}, arm={arm}: {coverage}")
            coverage_rows.append({"seed": int(seed), "arm": arm, **coverage})
            verify_null_closure_semantics(
                evaluation,
                config,
                seed=int(seed),
                arm=arm,
            )

    assay = gates.get("assay_gates", {})
    a13 = assay.get("A13_complete_primary_closure_grid", {})
    require(a13.get("status") == "PASS"
            and closure.strict_json_equal(a13.get("observed"), coverage_rows),
            "A13 primary-grid receipt mismatch")
    a14 = assay.get("A14_cross_context_operator_control_bank", {})
    require(
        a14.get("status") == "PASS"
        and closure.strict_json_equal(
            a14.get("observed"), bank.get("cross_context_operator_control")
        ),
        "A14 cross-context control receipt mismatch",
    )


def verify_evaluation_replay(
    directory: Path,
    result: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Recompute every evaluation from sealed checkpoints and frozen bank recipes."""

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    banks, _ = closure.make_eval_banks(config)
    audit_plan = make_v04_suffix_plan(max_depth=8)
    switched_words = sample_switch_words(
        num_actions=2,
        word_length=int(config["switched_word_length"]),
        count=int(config["switched_word_count"]),
        seed=closure.derive_seed(int(config["eval_seed_base"]), "switch_words"),
        include_constant_words=True,
    )
    replayed_records = copy.deepcopy(result.get("records", {}))
    for seed in config["seeds"]:
        for arm in closure.ARM_NAMES:
            label = f"seed={seed}, arm={arm}"
            record = result.get("records", {}).get(str(seed), {}).get(arm)
            require(isinstance(record, dict), f"Missing evaluation record: {label}")
            checkpoint = safe_artifact_path(
                directory,
                f"checkpoints/{arm}_seed{seed}.pt",
                f"evaluation replay checkpoint {label}",
            )
            try:
                payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
            except Exception as error:
                fail(f"Cannot load evaluation replay checkpoint {label}: {error}")
            train_config = closure.training_config_for(
                config, seed=int(seed), device=torch.device("cpu")
            )
            model = build_packet_closure_model(train_config, arm)
            model.load_state_dict(payload["state_dict"], strict=True)
            model.to(torch.device("cpu")).eval()
            recomputed = closure.json_ready(
                closure.evaluate_model(
                    model,
                    config,
                    banks,
                    audit_plan,
                    switched_words,
                    arm=arm,
                    seed=int(seed),
                    device=torch.device("cpu"),
                )
            )
            require(
                numerically_close_structure(record.get("evaluation"), recomputed),
                f"Stored evaluation differs from deterministic checkpoint replay: {label}",
            )
            replayed_records[str(seed)][arm]["evaluation"] = recomputed
    return replayed_records


def verify_rendered_outputs(
    directory: Path,
    result: Mapping[str, Any],
    completion: Mapping[str, Any],
) -> None:
    """Bind the human-readable report and plots to the verified result object."""

    try:
        from PIL import Image
    except ImportError as error:
        fail(f"Pillow is required to verify decoded chart pixels: {error}")

    expected_report = closure.render_report(result)
    require(
        (directory / "REPORT.md").read_text(encoding="utf-8") == expected_report,
        "Retained REPORT.md differs from the deterministic verified rendering",
    )
    chart_names = completion.get("charts")
    require(isinstance(chart_names, list), "Completion chart list is malformed")
    with tempfile.TemporaryDirectory(prefix="komorebi-v04-chart-verify-") as temporary:
        regenerated = closure.render_chart(Path(temporary), result["aggregate"])
        require(
            closure.strict_json_equal(regenerated, chart_names),
            "Retained chart list differs from regeneration",
        )
        for chart in chart_names:
            retained = safe_artifact_path(directory, chart, "pilot chart")
            expected = Path(temporary) / chart
            require(expected.is_file(), f"Regenerated chart is missing: {chart}")
            try:
                with Image.open(retained) as retained_image, Image.open(expected) as expected_image:
                    retained_image.verify()
                    expected_image.verify()
                with Image.open(retained) as retained_image, Image.open(expected) as expected_image:
                    retained_pixels = retained_image.convert("RGBA")
                    expected_pixels = expected_image.convert("RGBA")
                    same_pixels = (
                        retained_pixels.size == expected_pixels.size
                        and retained_pixels.tobytes() == expected_pixels.tobytes()
                    )
            except (OSError, ValueError) as error:
                fail(f"Cannot decode retained or regenerated chart {chart}: {error}")
            require(
                same_pixels,
                f"Retained chart pixels differ from deterministic regeneration: {chart}",
            )


def verify_v04_pilot(current_source_digest: str) -> Mapping[str, Any]:
    directory = ROOT / "results" / "packet_closure_pilot"
    relative_directory = "results/packet_closure_pilot"
    contract = require_mapping(
        load_json(closure.CONTRACT_FILENAME), "packet-closure contract"
    )
    contract_sha256 = require_sha256(
        file_sha256(ROOT / closure.CONTRACT_FILENAME), "v0.4 contract"
    )
    contract_source_digest = closure.contract_source_digest(ROOT)
    validation = closure.validate_contract(
        contract,
        "pilot",
        closure.PROFILES["pilot"],
        contract_source_digest,
    )
    require(validation.get("valid") is True and all(validation.values()),
            f"Packet-closure contract does not match live implementation: {validation}")
    require(contract.get("author") == AUTHOR, "Packet-closure contract author mismatch")

    run_contract = require_mapping(
        load_json(f"{relative_directory}/PREREGISTRATION.json"), "pilot contract copy"
    )
    require(run_contract == contract, "Pilot contract copy differs from root contract")
    canonical_contract_copy = json.dumps(
        contract, indent=2, sort_keys=True, allow_nan=False
    ) + "\n"
    require(
        (directory / "PREREGISTRATION.json").read_text(encoding="utf-8")
        == canonical_contract_copy,
        "Pilot contract copy is not the canonical serialization of the root contract",
    )

    completion = require_mapping(
        load_json(f"{relative_directory}/RUN_COMPLETE.json"), "v0.4 completion"
    )
    result = require_mapping(
        load_json(f"{relative_directory}/RESULTS.json"), "v0.4 result"
    )
    gates = require_mapping(
        load_json(f"{relative_directory}/GATES.json"), "v0.4 gates"
    )
    environment = require_mapping(
        load_json(f"{relative_directory}/ENVIRONMENT.json"), "v0.4 environment"
    )
    seal = require_mapping(
        load_json(f"{relative_directory}/CHECKPOINT_SEAL.json"), "v0.4 checkpoint seal"
    )
    bank = require_mapping(
        load_json(f"{relative_directory}/EVAL_BANK.json"), "v0.4 evaluation bank"
    )

    artifacts = {
        "results_sha256": "RESULTS.json",
        "gates_sha256": "GATES.json",
        "report_sha256": "REPORT.md",
        "environment_sha256": "ENVIRONMENT.json",
        "checkpoint_seal_sha256": "CHECKPOINT_SEAL.json",
        "evaluation_bank_sha256": "EVAL_BANK.json",
    }
    for key, filename in artifacts.items():
        require(completion.get(key) == file_sha256(directory / filename),
                f"v0.4 completion hash mismatch: {filename}")
    checkpoint_seal_sha256 = require_sha256(
        completion.get("checkpoint_seal_sha256"), "checkpoint-seal completion receipt"
    )
    evaluation_bank_sha256 = require_sha256(
        completion.get("evaluation_bank_sha256"), "evaluation-bank completion receipt"
    )

    common = {
        "version": VERSION,
        "profile": "pilot",
        "source_digest": current_source_digest,
        "contract_sha256": contract_sha256,
    }
    schemas = {
        "completion": (completion, f"{closure.SCHEMA_PREFIX}.completion.v1"),
        "result": (result, f"{closure.SCHEMA_PREFIX}.result.v1"),
        "environment": (environment, f"{closure.SCHEMA_PREFIX}.environment.v1"),
        "seal": (seal, f"{closure.SCHEMA_PREFIX}.checkpoint_seal.v1"),
        "bank": (bank, f"{closure.SCHEMA_PREFIX}.evaluation_bank.v1"),
    }
    for label, (artifact, schema) in schemas.items():
        require(artifact.get("schema") == schema, f"v0.4 {label} schema mismatch")
        for key, value in common.items():
            require(artifact.get(key) == value, f"v0.4 {label} {key} mismatch")

    for label, artifact in (
        ("completion", completion),
        ("result", result),
        ("gates", gates),
        ("environment", environment),
    ):
        require(artifact.get("run_mode") == "official",
                f"Canonical pilot {label} is not an official run")
    require(
        gates.get("study_status")
        == "prospective_developmental_fresh_seed_paired_2x2",
        "Canonical pilot has a replay or development study status",
    )

    canonical_runtime = closure.CANONICAL_PILOT_RUNTIME
    require(closure.strict_json_equal(result.get("runtime"), {
                "live": canonical_runtime,
                "canonical_pilot": canonical_runtime,
                "canonical_match": True,
            }), "RESULTS canonical-runtime receipt mismatch")
    require(closure.strict_json_equal(
                environment.get("runtime_receipt"), canonical_runtime
            )
            and closure.strict_json_equal(
                environment.get("canonical_pilot_runtime"), canonical_runtime
            )
            and environment.get("canonical_runtime_match") is True,
            "Environment canonical-runtime receipt mismatch")
    require(completion.get("canonical_runtime_match") is True,
            "Completion does not certify the frozen canonical runtime")

    expected_source_integrity_at_seal = {
        "startup_source_digest": current_source_digest,
        "preseal_source_digest": current_source_digest,
        "startup_contract_sha256": contract_sha256,
        "preseal_contract_sha256": contract_sha256,
        "valid": True,
    }
    expected_source_integrity = {
        **expected_source_integrity_at_seal,
        "final_source_digest": current_source_digest,
        "final_contract_sha256": contract_sha256,
        "valid": True,
    }
    require(closure.strict_json_equal(
                seal.get("source_integrity_at_seal"), expected_source_integrity_at_seal
            ),
            "Checkpoint-seal source-integrity receipt mismatch")
    require(closure.strict_json_equal(
                result.get("source_integrity"), expected_source_integrity
            ),
            "RESULTS source-integrity receipt mismatch")
    require(environment.get("source_integrity_valid") is True
            and completion.get("source_integrity_valid") is True,
            "Environment/completion source-integrity status failed")

    require(result.get("checkpoint_seal_sha256") == checkpoint_seal_sha256,
            "RESULTS checkpoint-seal hash mismatch")
    require(result.get("evaluation_bank_sha256") == evaluation_bank_sha256,
            "RESULTS evaluation-bank hash mismatch")
    require(environment.get("evaluation_bank_sha256") == evaluation_bank_sha256,
            "Environment evaluation-bank hash mismatch")
    require(bank.get("checkpoint_seal_sha256") == checkpoint_seal_sha256,
            "Evaluation bank does not bind the checkpoint seal")
    require(closure.strict_json_equal(result.get("checkpoint_seal"), seal),
            "RESULTS/seal mismatch")
    require(seal.get("strict_checkpoint_firewall") is True,
            "Checkpoint seal does not assert the strict audit firewall")
    require(closure.strict_json_equal(seal.get("construction_word_count"), 20),
            "Checkpoint seal construction-word count mismatch")
    expected_bank_summary = {
        "path": "EVAL_BANK.json",
        "heldout_bank": bank.get("heldout_bank"),
        "switch_bank": {
            key: value for key, value in bank.get("switch_bank", {}).items()
            if key != "words"
        },
    }
    require(closure.strict_json_equal(result.get("evaluation_bank"), expected_bank_summary),
            "RESULTS evaluation-bank summary mismatch")

    config = result.get("config")
    require(closure.strict_json_equal(config, closure.PROFILES["pilot"])
            and closure.strict_json_equal(
                config, contract.get("profiles", {}).get("pilot")
            ),
            "Pilot configuration does not match the live frozen profile")
    require(result.get("developmental") is True, "Pilot developmental status missing")
    require(closure.strict_json_equal(result.get("pilot_seed_policy"), {
                "seeds": [101, 211, 307],
                "status": "consumed_by_this_run",
            }), "Pilot seed policy mismatch")
    require(environment.get("device") == "cpu"
            and closure.strict_json_equal(environment.get("torch_threads"), 1)
            and environment.get("deterministic_algorithms") is True,
            "Pilot was not deterministic single-thread CPU execution")

    require(completion.get("completed") is True, "v0.4 pilot did not complete")
    require(completion.get("execution_status") == "PASS", "v0.4 execution failed")
    require(completion.get("assay_status") == "PASS", "v0.4 assay failed")
    require(closure.strict_json_equal(result.get("gates"), gates),
            "RESULTS/GATES mismatch")
    require(gates.get("scientific_failures_are_retained") is True,
            "Scientific-failure retention policy missing")
    status_fields = (
        "execution_status", "assay_status", "mechanism_status", "capability_status",
        "attribution_status", "secondary_transfer_status", "ambient_attribution_status",
        "objective_effect_status", "full_developmental_claim",
    )
    for key in status_fields:
        require(completion.get(key) == gates.get(key), f"Completion/gates mismatch: {key}")
    for key in (
        "mechanism_status", "capability_status", "attribution_status",
        "secondary_transfer_status", "ambient_attribution_status", "objective_effect_status",
    ):
        require(gates.get(key) in {"PASS", "FAIL"}, f"Pilot status is not evaluable: {key}")
    require(gates.get("full_developmental_claim") in {"PASS", "FAIL"},
            "Pilot full claim is not evaluable")
    expected_failure_retained = any(
        gates[key] == "FAIL"
        for key in (
            "mechanism_status", "capability_status", "attribution_status",
            "secondary_transfer_status", "ambient_attribution_status", "objective_effect_status",
        )
    )
    require(completion.get("scientific_gate_failure_retained") == expected_failure_retained,
            "Scientific-failure completion flag mismatch")
    require(closure.strict_json_equal(
                completion.get("elapsed_seconds"), result.get("elapsed_seconds")
            ),
            "Completion/result elapsed time mismatch")
    e06 = gates.get("execution_gates", {}).get(
        "E06_source_and_contract_immutable", {}
    )
    require(
        e06.get("status") == "PASS"
        and closure.strict_json_equal(e06.get("observed"), expected_source_integrity),
        "E06 source/contract immutability receipt mismatch",
    )

    phase = result.get("phase_times")
    require(isinstance(phase, dict), "Pilot phase timestamps are missing")
    ordered_times = [
        parse_time(phase.get(key), key)
        for key in (
            "started", "training_finished", "checkpoint_sealed",
            "evaluation_bank_materialized", "evaluation_finished",
        )
    ]
    require(ordered_times == sorted(ordered_times), "Pilot phase timestamps are out of order")
    seal_time = parse_time(seal.get("sealed_at"), "checkpoint seal")
    bank_time = parse_time(bank.get("materialized_at"), "evaluation bank")
    require(seal_time <= ordered_times[2],
            "Checkpoint seal timestamp is inconsistent")
    require(bank_time <= ordered_times[3],
            "Evaluation-bank timestamp is inconsistent")
    require(seal_time < bank_time,
            "Evaluation bank was not materialized after the checkpoint seal")

    verify_evaluation_bank(
        bank,
        config,
        current_source_digest,
        contract_sha256,
        checkpoint_seal_sha256,
    )
    verify_checkpoint_panel(
        directory,
        result,
        seal,
        config,
        current_source_digest,
        contract_sha256,
        evaluation_bank_sha256,
    )
    verify_primary_grid_and_control_gates(result, bank, gates, config)
    replayed_records = verify_evaluation_replay(directory, result, config)

    expected_aggregate = closure.aggregate_records(result["records"], config)
    require(closure.strict_json_equal(result.get("aggregate"), expected_aggregate),
            "Aggregate metrics mismatch")
    expected_paired = closure.paired_2x2_analysis(result["records"], config)
    require(closure.strict_json_equal(result.get("paired_2x2_analysis"), expected_paired),
            "Paired 2x2 analysis mismatch")
    contract_status = {
        "available": True,
        "path": closure.CONTRACT_FILENAME,
        "sha256": contract_sha256,
        **validation,
    }
    expected_gates = closure.adjudicate(
        "pilot",
        config,
        contract_status,
        result["records"],
        expected_aggregate,
        expected_paired,
        seal,
        bank,
        phase,
        run_mode="official",
        source_integrity=expected_source_integrity,
    )
    require(closure.strict_json_equal(gates, expected_gates),
            "Stored gates do not match independent adjudication")
    replayed_aggregate = closure.aggregate_records(replayed_records, config)
    replayed_paired = closure.paired_2x2_analysis(replayed_records, config)
    require(
        numerically_close_structure(result.get("aggregate"), replayed_aggregate),
        "Stored aggregate differs from checkpoint-replayed evaluation",
    )
    require(
        numerically_close_structure(result.get("paired_2x2_analysis"), replayed_paired),
        "Stored paired analysis differs from checkpoint-replayed evaluation",
    )
    replayed_gates = closure.adjudicate(
        "pilot",
        config,
        contract_status,
        replayed_records,
        replayed_aggregate,
        replayed_paired,
        seal,
        bank,
        phase,
        run_mode="official",
        source_integrity=expected_source_integrity,
    )
    require(
        numerically_close_structure(gates, replayed_gates),
        "Stored scientific decisions differ from checkpoint-replayed adjudication",
    )
    verify_rendered_outputs(directory, result, completion)
    return completion


def main() -> int:
    manifest = _BOOTSTRAP_MANIFEST
    subprocess.run(
        [
            sys.executable,
            "-E",
            "-P",
            "-B",
            "-m",
            "pytest",
            "--assert=plain",
            "-p",
            "no:cacheprovider",
            "-q",
            str(ROOT / "tests"),
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=True,
    )
    post_test_bytecode = [
        path
        for path in ROOT.rglob("*")
        if path.name == "__pycache__"
        or path.suffix.lower() in {".pyc", ".pyo"}
    ]
    require(
        not post_test_bytecode,
        "Verification tests created forbidden local bytecode/cache artifacts",
    )
    verify_manifest()

    verify_legacy_lineage()
    verify_v02_parent(
        "results/stability_pilot",
        "komorebi.neuralese.stable_quotient.completion.v1",
        "komorebi.neuralese.stable_quotient.result.v1",
    )
    verify_v02_parent(
        "results/projective_pilot",
        "komorebi.neuralese.projective_training.completion.v1",
        "komorebi.neuralese.projective_training.result.v1",
    )
    ambient = verify_v03_ambient()
    current_source_digest = tree_digest(ROOT, source_files(ROOT))
    pilot = verify_v04_pilot(current_source_digest)

    print(
        json.dumps(
            {
                "status": "PACKAGE_VERIFY_PASS",
                "author": AUTHOR,
                "version": VERSION,
                "manifest_files": manifest["file_count"],
                "tests": "passed",
                "parent_lineage": "verified",
                "ambient_assay": ambient["assay_status"],
                "packet_closure_assay": pilot["assay_status"],
                "packet_closure_mechanism": pilot["mechanism_status"],
                "packet_closure_capability": pilot["capability_status"],
                "packet_closure_attribution": pilot["attribution_status"],
                "packet_closure_secondary_transfer": pilot["secondary_transfer_status"],
                "packet_closure_ambient_attribution": pilot["ambient_attribution_status"],
                "packet_closure_objective_effect": pilot["objective_effect_status"],
                "packet_closure_full_claim": pilot["full_developmental_claim"],
                "source_digest": current_source_digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
