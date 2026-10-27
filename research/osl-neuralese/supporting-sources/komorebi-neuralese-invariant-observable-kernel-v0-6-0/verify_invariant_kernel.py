#!/usr/bin/env python3
"""Independent structural verifier for the v0.6 invariant-kernel block.

The verifier deliberately distinguishes *artifact integrity* from scientific
success.  A completed developmental screen may retain a negative scientific
decision and still verify.  Missing, ambiguous, duplicated, non-finite, or
unsealed evidence always fails closed.

The default verification is structural and does not execute the experiment
runner.  ``--replay`` additionally asks the manifested runner for its optional
deterministic replay hook.  Checkpoints are always loaded with
``weights_only=True`` and every tensor is checked independently.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable, Mapping, Sequence
import zipfile


VERSION = "0.6.0"
AUTHOR = "Komorebi P."
PLAN_VERSION = "v0.6-invariant-observable-kernel-dev2"
PREREGISTRATION_NAME = "INVARIANT_KERNEL_PREREGISTRATION.json"
RUNNER_NAME = "run_invariant_kernel.py"

PREREGISTRATION_SCHEMA = "komorebi.invariant_observable_kernel.preregistration.v1"
CHECKPOINT_SCHEMA = "komorebi.neuralese.invariant_kernel.checkpoint.v1"
CHECKPOINT_SEAL_SCHEMA = "komorebi.neuralese.invariant_kernel.checkpoint_seal.v1"
EVAL_BANK_SCHEMA = "komorebi.neuralese.invariant_kernel.eval_bank.v1"
RECORD_SCHEMA = "komorebi.neuralese.invariant_kernel.arm_record.v1"
RESULT_SCHEMA = "komorebi.neuralese.invariant_kernel.result.v1"
GATES_SCHEMA = "komorebi.neuralese.invariant_kernel.gates.v1"
STARTED_SCHEMA = "komorebi.neuralese.invariant_kernel.run_started.v1"
COMPLETION_SCHEMA = "komorebi.neuralese.invariant_kernel.run_complete.v1"
VERIFICATION_SCHEMA = "komorebi.neuralese.invariant_kernel.verification.v1"

RESULT_KEYS = frozenset(
    {
        "schema",
        "version",
        "profile",
        "run_mode",
        "config",
        "source_digest",
        "source_files",
        "preregistration_sha256",
        "training_contract",
        "checkpoint_seal",
        "evaluation_bank_fingerprint",
        "record_index",
        "records",
        "training",
        "controls",
        "aggregate",
        "aggregate_sha256",
        "gates",
        "runtime",
        "phase_seconds",
        "chart",
    }
)
GATES_KEYS = frozenset(
    {
        "schema",
        "version",
        "profile",
        "run_mode",
        "source_digest",
        "preregistration_sha256",
        "status",
    }
)
COMPLETION_KEYS = frozenset(
    {
        "schema",
        "version",
        "profile",
        "run_mode",
        "source_digest",
        "preregistration_sha256",
        "checkpoint_seal_sha256",
        "evaluation_bank_fingerprint",
        "record_hashes",
        "aggregate_sha256",
        "execution_integrity",
        "assay_validity",
        "scientific_status",
        "pilot_promotion",
        "results_sha256",
        "gates_sha256",
        "controls_sha256",
        "report_sha256",
        "chart_sha256",
    }
)

PRIMARY_ARMS = (
    "polar_supervised",
    "polar_cr",
    "polar_exact",
    "learned_intertwiner",
    "hard_kernel_supervised",
    "hard_kernel_semantic_flat",
)
EXPECTED_MODEL_CLASSES = {
    "polar_supervised": "LinearPolarTableOperatorRNN",
    "polar_cr": "LinearPolarTableOperatorRNN",
    "polar_exact": "LinearPolarTableOperatorRNN",
    "learned_intertwiner": "LearnedIntertwinerPolarRNN",
    "hard_kernel_supervised": "LearnedFrameBlockIsometricOperatorRNN",
    "hard_kernel_semantic_flat": "LearnedFrameBlockIsometricOperatorRNN",
}

HEX_256 = re.compile(r"[0-9a-f]{64}\Z")
SOURCE_SUFFIXES = frozenset({".py", ".md", ".json", ".toml", ".ps1", ".txt"})
SOURCE_EXCLUDED_NAMES = frozenset(
    {
        "MANIFEST.json",
        "SHA256SUMS.txt",
    }
)
FORBIDDEN_DIRECTORY_NAMES = frozenset(
    {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", ".git"}
)
CHECKPOINT_LIKE_SUFFIXES = frozenset({".pt", ".pth", ".ckpt", ".bin", ".safetensors"})

CHECKPOINT_PAYLOAD_KEYS = frozenset(
    {
        "schema",
        "version",
        "arm",
        "seed",
        "config",
        "model_class",
        "state_dict",
        "initial_state_digest",
        "final_state_digest",
        "training_metadata",
        "source_digest",
        "preregistration_sha256",
    }
)
TRAINING_METADATA_KEYS = frozenset(
    {
        "plan_version",
        "arm",
        "config",
        "model_class",
        "parameter_count",
        "trainable_parameter_count",
        "initial_state_digest",
        "core_initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
        "terminal_counts",
        "construction",
        "ambient_encoder",
        "hard_anchor_contract",
        "auxiliary_schedule",
        "relation_exposure",
        "claim_boundary",
    }
)
TRAIN_CONFIG_KEYS = frozenset(
    {
        "seed",
        "steps",
        "batch_size",
        "train_max_length",
        "hidden_dim",
        "learning_rate",
        "weight_decay",
        "grad_clip",
        "warmup_steps",
        "auxiliary_delay_steps",
        "auxiliary_ramp_end_step",
        "auxiliary_contexts",
        "construction_words_per_step",
        "relation_cells_per_step",
        "episode_seed_base",
        "gauge_seed_base",
        "ambient_seed_base",
        "checkpoints",
        "device",
        "base_weights",
        "weights",
    }
)
BASE_WEIGHT_KEYS = frozenset(
    {
        "construction_ce",
        "anchor",
        "composition",
        "margin",
        "conformal",
        "switched_gain",
        "delayed_return",
    }
)
AUXILIARY_WEIGHT_KEYS = frozenset(
    {
        "exact_flatness",
        "observer_anchor_geometry",
        "observer_centered_readout",
        "observer_intertwining",
        "observer_semantic_relation",
        "hard_semantic_flatness",
    }
)
ARM_METADATA = {
    "polar_supervised": {
        "name": "polar_supervised",
        "architecture": "polar",
        "legacy_cr": False,
        "exact_flatness": False,
        "learned_intertwiner": False,
        "semantic_flatness": False,
    },
    "polar_cr": {
        "name": "polar_cr",
        "architecture": "polar",
        "legacy_cr": True,
        "exact_flatness": False,
        "learned_intertwiner": False,
        "semantic_flatness": False,
    },
    "polar_exact": {
        "name": "polar_exact",
        "architecture": "polar",
        "legacy_cr": False,
        "exact_flatness": True,
        "learned_intertwiner": False,
        "semantic_flatness": False,
    },
    "learned_intertwiner": {
        "name": "learned_intertwiner",
        "architecture": "polar",
        "legacy_cr": False,
        "exact_flatness": False,
        "learned_intertwiner": True,
        "semantic_flatness": False,
    },
    "hard_kernel_supervised": {
        "name": "hard_kernel_supervised",
        "architecture": "hard_kernel",
        "legacy_cr": False,
        "exact_flatness": False,
        "learned_intertwiner": False,
        "semantic_flatness": False,
    },
    "hard_kernel_semantic_flat": {
        "name": "hard_kernel_semantic_flat",
        "architecture": "hard_kernel",
        "legacy_cr": False,
        "exact_flatness": False,
        "learned_intertwiner": False,
        "semantic_flatness": True,
    },
}
TRAJECTORY_ROW_KEYS = frozenset(
    {
        "step",
        "length",
        "loss",
        "terminal_loss",
        "construction_ce_loss",
        "legacy_composition_loss",
        "legacy_delayed_return_loss",
        "exact_flatness_loss",
        "observer_anchor_geometry_loss",
        "observer_centered_readout_loss",
        "observer_intertwining_loss",
        "observer_semantic_relation_loss",
        "observer_orthogonality_residual",
        "hard_semantic_flatness_loss",
        "terminal_accuracy",
        "construction_accuracy",
        "gradient_norm_before_clip",
        "base_warmup",
        "auxiliary_multiplier",
        "auxiliary_delay_steps",
        "auxiliary_ramp_end_step",
        "relation_context_indices",
        "relation_cell_indices",
        "relation_cells_per_context",
        "relation_cells_total",
    }
)
TRAINING_ROW_KEYS = frozenset(
    {
        "config",
        "trajectory",
        "elapsed_seconds",
        "final_loss",
        "parameter_count",
        "trainable_parameter_count",
        "initial_state_digest",
        "core_initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
        "terminal_proposal_count",
        "terminal_candidates_accepted",
        "terminal_candidates_rejected",
        "terminal_identity_rejections",
        "terminal_r2_rejections",
        "construction_digest",
        "ambient_initial_digest",
        "ambient_final_digest",
    }
)


class VerificationError(RuntimeError):
    """Raised when a retained run cannot be authenticated."""


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


def canonical_object_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json_tree(value: Any, label: str) -> None:
    """Reject both named constants and finite-literal overflow such as ``1e999``."""

    if isinstance(value, float):
        require(math.isfinite(value), f"non-finite JSON number in {label}")
    elif isinstance(value, list):
        for item in value:
            _reject_nonfinite_json_tree(item, label)
    elif isinstance(value, dict):
        for item in value.values():
            _reject_nonfinite_json_tree(item, label)


def load_json(path: Path, label: str | None = None) -> Any:
    display = label or path.as_posix()
    require(path.exists(), f"missing required artifact: {display}")
    require(not path.is_symlink(), f"symbolic links are forbidden: {display}")
    require(path.is_file(), f"artifact is not a regular file: {display}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
            object_pairs_hook=_strict_json_object,
        )
        _reject_nonfinite_json_tree(value, display)
        return value
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


def _require_exact_keys(value: Mapping[str, Any], keys: Iterable[str], label: str) -> None:
    expected = set(keys)
    observed = set(value)
    require(
        observed == expected,
        f"{label} schema mismatch; extra={sorted(observed - expected)}, "
        f"missing={sorted(expected - observed)}",
    )


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
        raise VerificationError(f"unsafe relative path: {relative!r}")


def _is_cache_path(relative: str) -> bool:
    parsed = PurePosixPath(relative)
    return (
        any(part in FORBIDDEN_DIRECTORY_NAMES for part in parsed.parts)
        or parsed.suffix.lower() in {".pyc", ".pyo"}
    )


def scan_run_tree(directory: Path) -> dict[str, Path]:
    """Inventory a run and reject links, caches, bytecode, and non-files."""

    directory = directory.resolve(strict=True)
    require(directory.is_dir(), f"result path is not a directory: {directory}")
    inventory: dict[str, Path] = {}
    for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(directory).as_posix()
        validate_relative_path(relative)
        require(not path.is_symlink(), f"symbolic links are forbidden: {relative}")
        require(not _is_cache_path(relative), f"cache/bytecode artifact is forbidden: {relative}")
        if path.is_dir():
            continue
        require(path.is_file(), f"non-regular run artifact is forbidden: {relative}")
        inventory[relative] = path
        if path.suffix.lower() == ".json":
            load_json(path, relative)
    return inventory


def scan_package_safety(root: Path) -> None:
    """Reject links, caches, bytecode, and special files anywhere in a package."""

    root = root.resolve(strict=True)
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        validate_relative_path(relative)
        require(not path.is_symlink(), f"symbolic links are forbidden in package: {relative}")
        require(not _is_cache_path(relative), f"cache/bytecode artifact is forbidden: {relative}")
        require(path.is_dir() or path.is_file(), f"non-regular package entry is forbidden: {relative}")


def _source_inventory(root: Path) -> dict[str, Path]:
    root = root.resolve(strict=True)
    require(root.is_dir(), f"package root is not a directory: {root}")
    result: dict[str, Path] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        validate_relative_path(relative)
        require(not path.is_symlink(), f"symbolic links are forbidden in source tree: {relative}")
        if path.is_dir():
            continue
        if (
            path.suffix.lower() in SOURCE_SUFFIXES
            and "results" not in PurePosixPath(relative).parts
            and path.name not in SOURCE_EXCLUDED_NAMES
            and not _is_cache_path(relative)
        ):
            result[relative] = path
    return result


def source_digest(root: Path) -> tuple[str, list[str]]:
    """Digest the non-result source tree using the runner's stable convention."""

    files = _source_inventory(root)
    digest = hashlib.sha256()
    for relative in sorted(files):
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(files[relative].read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), sorted(files)


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


def _verify_self_seal(value: Mapping[str, Any], key: str, label: str) -> str:
    observed = require_sha256(value.get(key), f"{label} {key}")
    unsigned = dict(value)
    del unsigned[key]
    require(observed == canonical_object_sha256(unsigned), f"{label} self-seal mismatch")
    return observed


def _verify_torch_checkpoint_container(path: Path, label: str) -> None:
    require(zipfile.is_zipfile(path), f"{label} is not a torch ZIP checkpoint")
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(names and len(names) == len(set(names)), f"{label} ZIP has duplicate members")
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


def _state_dict_digest(state: Mapping[str, Any], torch: Any) -> str:
    digest = hashlib.sha256()
    require(state, "checkpoint state_dict may not be empty")
    for name, tensor in sorted(state.items()):
        require(isinstance(name, str) and name, "checkpoint tensor name is invalid")
        require(isinstance(tensor, torch.Tensor), f"checkpoint value is not a tensor: {name}")
        require(bool(torch.isfinite(tensor).all()), f"checkpoint tensor is non-finite: {name}")
        local = tensor.detach().to(device="cpu").contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(local.dtype).encode("ascii"))
        digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
        digest.update(local.numpy().tobytes())
    return digest.hexdigest()


def verify_preregistration(root: Path) -> tuple[Mapping[str, Any], str]:
    preregistration = require_mapping(
        load_json(root / PREREGISTRATION_NAME, PREREGISTRATION_NAME),
        PREREGISTRATION_NAME,
    )
    require(
        preregistration.get("schema") == PREREGISTRATION_SCHEMA,
        "preregistration schema mismatch",
    )
    require(preregistration.get("version") == VERSION, "preregistration version mismatch")
    require(preregistration.get("author") == AUTHOR, "preregistration author mismatch")
    require(
        preregistration.get("training_plan_version") == PLAN_VERSION,
        "preregistration training-plan version mismatch",
    )
    arms = preregistration.get("arms")
    require(isinstance(arms, list), "preregistration arms are missing")
    arm_names = tuple(
        require_mapping(row, f"preregistration arm {index}").get("name")
        for index, row in enumerate(arms)
    )
    require(arm_names == PRIMARY_ARMS, "preregistration arm panel mismatch")
    profiles = require_mapping(preregistration.get("profiles"), "preregistration profiles")
    require(set(profiles) == {"smoke", "screen", "pilot"}, "preregistration profiles mismatch")
    for profile_name, raw in profiles.items():
        profile = require_mapping(raw, f"preregistration profile {profile_name}")
        seeds = profile.get("seeds")
        require(
            isinstance(seeds, list)
            and seeds
            and all(type(seed) is int for seed in seeds)
            and len(set(seeds)) == len(seeds),
            f"preregistration {profile_name} seeds are invalid",
        )
        require(
            type(profile.get("auxiliary_contexts")) is int
            and profile.get("auxiliary_contexts") == 8,
            f"preregistration {profile_name} auxiliary-context count is invalid",
        )
    return preregistration, file_sha256(root / PREREGISTRATION_NAME)


def _profile_matches_preregistration(
    observed: Mapping[str, Any], registered: Mapping[str, Any]
) -> bool:
    """Accept either the public prereg surface or the runner's internal aliases."""

    if dict(observed) == dict(registered):
        return True
    projection = {
        "seeds": observed.get("seeds"),
        "steps": observed.get("steps"),
        "batch_size": observed.get("batch_size"),
        "geometry_contexts": observed.get("geometry_contexts"),
        "auxiliary_contexts": observed.get("auxiliary_contexts"),
        "diamonds_per_length": observed.get("diamonds_per_length"),
        "diamond_lengths": observed.get("diamond_lengths"),
        "diamond_suffix_lengths": observed.get("diamond_suffix_lengths"),
        "loops_per_repeat_suffix_stratum": observed.get("loops_per_stratum"),
        "loop_repeats": observed.get("loop_repeats"),
        "loop_suffix_lengths": observed.get("loop_suffix_lengths"),
        "deep_depths": observed.get("deep_depths"),
        "deep_examples_per_depth": observed.get("deep_examples"),
        "causal_examples": observed.get("causal_examples"),
    }
    return projection == dict(registered)


def _expected_relation_exposure(config: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the frozen eight-context relation estimator receipt."""

    contexts = config.get("auxiliary_contexts")
    cells = config.get("relation_cells_per_step")
    require(
        type(contexts) is int and contexts == 8,
        "checkpoint auxiliary-context count is invalid",
    )
    require(
        type(cells) is int and cells == 9,
        "checkpoint relation-cell schedule is invalid",
    )
    return {
        "selection": "first_n_accepted_rows_without_replacement",
        "contexts_per_step": contexts,
        "cells_per_context": cells,
        "cells_per_step_total": contexts * cells,
        "aggregation": "mean_over_contexts_and_cells_not_sum",
        "shared_across_arms": True,
    }


def _verify_relation_exposure(
    value: Any,
    config: Mapping[str, Any],
    label: str,
) -> None:
    exposure = require_mapping(value, label)
    expected = _expected_relation_exposure(config)
    _require_exact_keys(exposure, set(expected), label)
    try:
        exact = canonical_json_bytes(dict(exposure)) == canonical_json_bytes(expected)
    except (TypeError, ValueError):
        exact = False
    require(exact, f"{label} differs from frozen eight-context policy")


def _verify_identity(
    artifact: Mapping[str, Any],
    label: str,
    *,
    source_sha256: str,
    preregistration_sha256: str,
) -> None:
    require(artifact.get("version") == VERSION, f"{label} version mismatch")
    require(
        artifact.get("source_digest") == source_sha256,
        f"{label} source digest mismatch",
    )
    require(
        artifact.get("preregistration_sha256") == preregistration_sha256,
        f"{label} preregistration digest mismatch",
    )


def verify_checkpoint_seal(
    directory: Path,
    seal: Mapping[str, Any],
    inventory: Mapping[str, Path],
    *,
    expected_arms: Sequence[str],
    expected_seeds: Sequence[int],
    source_sha256: str,
    preregistration_sha256: str,
) -> dict[tuple[int, str], Mapping[str, Any]]:
    _require_exact_keys(
        seal,
        {
            "schema",
            "version",
            "source_digest",
            "preregistration_sha256",
            "count",
            "checkpoints",
            "seal_sha256",
        },
        "checkpoint seal",
    )
    require(seal.get("schema") == CHECKPOINT_SEAL_SCHEMA, "checkpoint-seal schema mismatch")
    _verify_identity(
        seal,
        "checkpoint seal",
        source_sha256=source_sha256,
        preregistration_sha256=preregistration_sha256,
    )
    _verify_self_seal(seal, "seal_sha256", "checkpoint seal")
    rows = seal.get("checkpoints")
    require(isinstance(rows, list), "checkpoint-seal checkpoints must be a list")
    require(type(seal.get("count")) is int and seal["count"] == len(rows), "checkpoint count mismatch")
    expected_grid = {
        (int(seed), str(arm)) for seed in expected_seeds for arm in expected_arms
    }
    observed: dict[tuple[int, str], Mapping[str, Any]] = {}
    order: list[tuple[int, str]] = []
    for index, raw in enumerate(rows):
        row = require_mapping(raw, f"checkpoint row {index}")
        _require_exact_keys(row, {"path", "sha256", "arm", "seed", "state_digest"}, f"checkpoint row {index}")
        arm, seed = row.get("arm"), row.get("seed")
        require(isinstance(arm, str) and type(seed) is int, f"checkpoint row {index} identity is invalid")
        key = (seed, arm)
        require(key not in observed, f"duplicate checkpoint arm/seed: {key}")
        expected_path = f"checkpoints/{arm}_seed{seed}.pt"
        require(row.get("path") == expected_path, f"checkpoint path does not match arm/seed: {key}")
        path = _safe_member(directory, row.get("path"), f"checkpoint {index}")
        _verify_torch_checkpoint_container(path, f"checkpoint {arm}/seed{seed}")
        require(file_sha256(path) == require_sha256(row.get("sha256"), f"checkpoint {key} hash"), f"checkpoint file hash mismatch: {expected_path}")
        require_sha256(row.get("state_digest"), f"checkpoint {key} state digest")
        observed[key] = row
        order.append(key)
    require(order == sorted(order), "checkpoint rows are not sorted by seed and arm")
    require(set(observed) == expected_grid, "checkpoint seal does not cover the exact seed/arm grid")
    actual_checkpoint_files = {
        relative for relative in inventory if PurePosixPath(relative).parts[:1] == ("checkpoints",)
    }
    expected_checkpoint_files = {str(row["path"]) for row in observed.values()}
    require(
        actual_checkpoint_files == expected_checkpoint_files,
        "checkpoint directory contains missing or extra artifacts",
    )
    checkpoint_like_files = {
        relative
        for relative in inventory
        if PurePosixPath(relative).suffix.lower() in CHECKPOINT_LIKE_SUFFIXES
    }
    require(
        checkpoint_like_files == expected_checkpoint_files,
        "run contains an unsealed checkpoint outside the checkpoint directory",
    )
    return observed


def _verify_training_metadata(
    metadata: Mapping[str, Any],
    *,
    arm: str,
    seed: int,
    model_class: str,
) -> str:
    _require_exact_keys(metadata, TRAINING_METADATA_KEYS, f"training metadata {arm}/seed{seed}")
    arm_spec = require_mapping(metadata.get("arm"), f"training metadata arm {arm}/seed{seed}")
    config = require_mapping(metadata.get("config"), f"training metadata config {arm}/seed{seed}")
    require(
        dict(arm_spec) == ARM_METADATA[arm],
        f"training metadata arm contract mismatch: {arm}/seed{seed}",
    )
    require(config.get("seed") == seed, f"training metadata seed mismatch: {arm}/seed{seed}")
    require(
        metadata.get("plan_version") == PLAN_VERSION,
        f"training metadata plan version mismatch: {arm}/seed{seed}",
    )
    require(metadata.get("model_class") == model_class, f"training metadata model mismatch: {arm}/seed{seed}")
    require(
        model_class == EXPECTED_MODEL_CLASSES[arm],
        f"checkpoint model class is not registered for arm: {arm}/seed{seed}",
    )
    for key in (
        "initial_state_digest",
        "core_initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
    ):
        require_sha256(metadata.get(key), f"training metadata {arm}/seed{seed} {key}")
    for key in ("parameter_count", "trainable_parameter_count"):
        require(type(metadata.get(key)) is int and metadata[key] > 0, f"training metadata {key} is invalid: {arm}/seed{seed}")
    counts = require_mapping(metadata.get("terminal_counts"), f"terminal counts {arm}/seed{seed}")
    _require_exact_keys(
        counts,
        {"proposals", "accepted", "rejected", "identity_rejections", "r2_rejections"},
        f"terminal counts {arm}/seed{seed}",
    )
    require(
        all(type(value) is int and value >= 0 for value in counts.values())
        and counts["proposals"] == counts["accepted"] + counts["rejected"],
        f"terminal count arithmetic mismatch: {arm}/seed{seed}",
    )
    construction = require_mapping(metadata.get("construction"), f"construction metadata {arm}/seed{seed}")
    _require_exact_keys(construction, {"digest", "words"}, f"construction metadata {arm}/seed{seed}")
    require_sha256(construction.get("digest"), f"construction digest {arm}/seed{seed}")
    require(isinstance(construction.get("words"), list), f"construction words are invalid: {arm}/seed{seed}")
    ambient = require_mapping(metadata.get("ambient_encoder"), f"ambient metadata {arm}/seed{seed}")
    _require_exact_keys(ambient, {"frozen_random_dormant", "initial_digest", "final_digest"}, f"ambient metadata {arm}/seed{seed}")
    for key in ("initial_digest", "final_digest"):
        value = ambient.get(key)
        require(value is None or (isinstance(value, str) and HEX_256.fullmatch(value)), f"ambient {key} is invalid: {arm}/seed{seed}")
    hard_arm = arm.startswith("hard_kernel")
    require(
        ambient.get("frozen_random_dormant") is hard_arm,
        f"ambient freeze policy disagrees with arm: {arm}/seed{seed}",
    )
    if hard_arm:
        require(
            ambient.get("initial_digest") == ambient.get("final_digest"),
            f"frozen ambient encoder changed: {arm}/seed{seed}",
        )
    else:
        require(
            ambient.get("initial_digest") is None and ambient.get("final_digest") is None,
            f"unregistered ambient metadata present: {arm}/seed{seed}",
        )
    expected_anchor_contract = (
        "orthogonal_anchor_completion_via_common_logit_gauge" if hard_arm else None
    )
    require(
        metadata.get("hard_anchor_contract") == expected_anchor_contract,
        f"hard-anchor contract disagrees with arm: {arm}/seed{seed}",
    )
    schedule = require_mapping(
        metadata.get("auxiliary_schedule"),
        f"auxiliary schedule {arm}/seed{seed}",
    )
    _require_exact_keys(
        schedule,
        {
            "delay_steps",
            "ramp_end_step",
            "base_warmup_steps",
            "base_warmup_is_independent",
        },
        f"auxiliary schedule {arm}/seed{seed}",
    )
    require(
        schedule.get("delay_steps") == config.get("auxiliary_delay_steps")
        and schedule.get("ramp_end_step") == config.get("auxiliary_ramp_end_step")
        and schedule.get("base_warmup_steps") == config.get("warmup_steps")
        and schedule.get("base_warmup_is_independent") is True,
        f"auxiliary schedule/config mismatch: {arm}/seed{seed}",
    )
    _verify_relation_exposure(
        metadata.get("relation_exposure"),
        config,
        f"relation exposure {arm}/seed{seed}",
    )
    claims = require_mapping(metadata.get("claim_boundary"), f"claim boundary {arm}/seed{seed}")
    _require_exact_keys(
        claims,
        {
            "explicit_pressure_only",
            "spontaneous_emergence",
            "anchor_geometry_is_supervised",
            "observer_constructs_recurrence",
            "learned_intertwiner_projective_normalization",
            "ambient_fiber_is_useful_memory",
        },
        f"claim boundary {arm}/seed{seed}",
    )
    require(
        claims.get("explicit_pressure_only") is True
        and claims.get("spontaneous_emergence") is False
        and claims.get("observer_constructs_recurrence") is False
        and claims.get("learned_intertwiner_projective_normalization") is False
        and claims.get("ambient_fiber_is_useful_memory") is False,
        f"checkpoint exceeds registered claim boundary: {arm}/seed{seed}",
    )
    require(
        claims.get("anchor_geometry_is_supervised") is (arm == "learned_intertwiner"),
        f"anchor-supervision claim disagrees with arm: {arm}/seed{seed}",
    )
    return str(metadata["final_state_digest"])


def _verify_registered_training_config(
    config: Mapping[str, Any],
    *,
    seed: int,
    profile: Mapping[str, Any],
    preregistration: Mapping[str, Any],
) -> None:
    _require_exact_keys(config, TRAIN_CONFIG_KEYS, f"checkpoint config seed {seed}")
    _reject_nonfinite_json_tree(config, f"checkpoint config seed {seed}")
    for config_key, profile_key in (
        ("steps", "steps"),
        ("batch_size", "batch_size"),
        ("auxiliary_delay_steps", "auxiliary_delay_steps"),
        ("auxiliary_ramp_end_step", "auxiliary_ramp_end_step"),
        ("auxiliary_contexts", "auxiliary_contexts"),
    ):
        require(
            config.get(config_key) == profile.get(profile_key),
            f"checkpoint config differs from preregistered {profile_key}: seed {seed}",
        )
    require(config.get("seed") == seed, f"checkpoint config seed mismatch: seed {seed}")
    loss_contract = require_mapping(
        preregistration.get("loss_contract"), "preregistration loss contract"
    )
    learned = require_mapping(
        loss_contract.get("learned_intertwiner"),
        "preregistration learned-intertwiner loss contract",
    )
    expected_weights = {
        "exact_flatness": loss_contract.get("full_space_relation_weight"),
        "observer_anchor_geometry": learned.get("simplex_gram_weight"),
        "observer_centered_readout": learned.get("centered_readout_weight"),
        "observer_intertwining": learned.get("intertwining_weight"),
        "observer_semantic_relation": learned.get("semantic_relation_weight"),
        "hard_semantic_flatness": loss_contract.get("hard_semantic_relation_weight"),
    }
    weights = require_mapping(config.get("weights"), f"checkpoint auxiliary weights seed {seed}")
    _require_exact_keys(weights, AUXILIARY_WEIGHT_KEYS, f"checkpoint auxiliary weights seed {seed}")
    require(
        dict(weights) == expected_weights,
        f"checkpoint loss weights differ from preregistration: seed {seed}",
    )
    base_weights = require_mapping(config.get("base_weights"), f"checkpoint base weights seed {seed}")
    _require_exact_keys(base_weights, BASE_WEIGHT_KEYS, f"checkpoint base weights seed {seed}")
    require(
        all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
            and float(value) >= 0.0
            for value in base_weights.values()
        ),
        f"checkpoint base weights are invalid: seed {seed}",
    )
    require(
        config.get("warmup_steps") == loss_contract.get("warmup_steps"),
        f"checkpoint warmup differs from preregistration: seed {seed}",
    )
    decomposition = require_mapping(
        preregistration.get("decomposition_contract"),
        "preregistration decomposition contract",
    )
    require(
        config.get("hidden_dim") == decomposition.get("hidden_dimension"),
        f"checkpoint hidden dimension differs from preregistration: seed {seed}",
    )
    require(
        type(config.get("relation_cells_per_step")) is int
        and config.get("relation_cells_per_step") == 9,
        f"checkpoint relation-cell schedule is invalid: seed {seed}",
    )
    _verify_relation_exposure(
        loss_contract.get("relation_exposure"),
        config,
        "preregistration relation exposure",
    )


def verify_checkpoint_payloads(
    directory: Path,
    rows: Mapping[tuple[int, str], Mapping[str, Any]],
    *,
    source_sha256: str,
    preregistration_sha256: str,
    registered_profile: Mapping[str, Any],
    preregistration: Mapping[str, Any],
) -> tuple[int, dict[tuple[int, str], Mapping[str, Any]]]:
    try:
        import torch
    except Exception as error:  # pragma: no cover - packaging environment failure
        raise VerificationError(f"PyTorch is required for safe checkpoint verification: {error}") from error
    count = 0
    stream_rows: dict[int, list[Mapping[str, Any]]] = {}
    metadata_index: dict[tuple[int, str], Mapping[str, Any]] = {}
    for (seed, arm), row in sorted(rows.items()):
        path = _safe_member(directory, row["path"], f"checkpoint {arm}/seed{seed}")
        try:
            payload = torch.load(path, map_location="cpu", weights_only=True)
        except Exception as error:
            raise VerificationError(f"safe weights-only load failed for {arm}/seed{seed}: {error}") from error
        payload = require_mapping(payload, f"checkpoint payload {arm}/seed{seed}")
        _require_exact_keys(payload, CHECKPOINT_PAYLOAD_KEYS, f"checkpoint payload {arm}/seed{seed}")
        require(payload.get("schema") == CHECKPOINT_SCHEMA, f"checkpoint schema mismatch: {arm}/seed{seed}")
        _verify_identity(
            payload,
            f"checkpoint {arm}/seed{seed}",
            source_sha256=source_sha256,
            preregistration_sha256=preregistration_sha256,
        )
        require(payload.get("arm") == arm, f"checkpoint arm mismatch: {arm}/seed{seed}")
        require(payload.get("seed") == seed, f"checkpoint seed mismatch: {arm}/seed{seed}")
        config = require_mapping(payload.get("config"), f"checkpoint config {arm}/seed{seed}")
        require(config.get("seed") == seed, f"checkpoint seed mismatch: {arm}/seed{seed}")
        _verify_registered_training_config(
            config,
            seed=seed,
            profile=registered_profile,
            preregistration=preregistration,
        )
        model_class = payload.get("model_class")
        require(isinstance(model_class, str) and model_class, f"checkpoint model class is invalid: {arm}/seed{seed}")
        metadata = require_mapping(payload.get("training_metadata"), f"training metadata {arm}/seed{seed}")
        metadata_digest = _verify_training_metadata(metadata, arm=arm, seed=seed, model_class=model_class)
        require(dict(config) == metadata.get("config"), f"checkpoint config/metadata mismatch: {arm}/seed{seed}")
        require(
            payload.get("initial_state_digest") == metadata.get("initial_state_digest"),
            f"checkpoint initial digest/metadata mismatch: {arm}/seed{seed}",
        )
        require(
            payload.get("final_state_digest") == metadata_digest,
            f"checkpoint final digest/metadata mismatch: {arm}/seed{seed}",
        )
        state = require_mapping(payload.get("state_dict"), f"checkpoint state_dict {arm}/seed{seed}")
        state_digest = _state_dict_digest(state, torch)
        require(state_digest == metadata_digest, f"checkpoint tensor digest mismatch: {arm}/seed{seed}")
        require(state_digest == row.get("state_digest"), f"checkpoint/seal state digest mismatch: {arm}/seed{seed}")
        stream_rows.setdefault(seed, []).append(metadata)
        metadata_index[(seed, arm)] = metadata
        count += 1
    paired_fields = (
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
    )
    for seed, metadata_rows in stream_rows.items():
        for field in paired_fields:
            require(
                len({str(row[field]) for row in metadata_rows}) == 1,
                f"paired checkpoint streams disagree for seed {seed}: {field}",
            )
        constructions = [require_mapping(row["construction"], "construction") for row in metadata_rows]
        require(
            len({str(row["digest"]) for row in constructions}) == 1,
            f"paired checkpoint constructions disagree for seed {seed}",
        )
    return count, metadata_index


def verify_training_grid(
    training: Any,
    metadata_index: Mapping[tuple[int, str], Mapping[str, Any]],
    *,
    expected_arms: Sequence[str],
    expected_seeds: Sequence[int],
) -> None:
    training = require_mapping(training, "RESULTS training")
    require(
        set(training) == {str(int(seed)) for seed in expected_seeds},
        "training receipt seed grid mismatch",
    )
    metadata_fields = (
        "config",
        "parameter_count",
        "trainable_parameter_count",
        "initial_state_digest",
        "core_initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
    )
    for seed in expected_seeds:
        seed_rows = require_mapping(training[str(int(seed))], f"training seed {seed}")
        require(set(seed_rows) == set(expected_arms), f"training arm grid mismatch: seed {seed}")
        for arm in expected_arms:
            row = require_mapping(seed_rows[arm], f"training {arm}/seed{seed}")
            _require_exact_keys(row, TRAINING_ROW_KEYS, f"training {arm}/seed{seed}")
            metadata = metadata_index[(int(seed), str(arm))]
            for field in metadata_fields:
                require(
                    row.get(field) == metadata.get(field),
                    f"training/checkpoint metadata mismatch for {field}: {arm}/seed{seed}",
                )
            counts = require_mapping(metadata.get("terminal_counts"), "checkpoint terminal counts")
            count_mapping = {
                "terminal_proposal_count": "proposals",
                "terminal_candidates_accepted": "accepted",
                "terminal_candidates_rejected": "rejected",
                "terminal_identity_rejections": "identity_rejections",
                "terminal_r2_rejections": "r2_rejections",
            }
            for result_name, metadata_name in count_mapping.items():
                require(
                    row.get(result_name) == counts.get(metadata_name),
                    f"training/checkpoint count mismatch for {result_name}: {arm}/seed{seed}",
                )
            construction = require_mapping(metadata.get("construction"), "checkpoint construction")
            ambient = require_mapping(metadata.get("ambient_encoder"), "checkpoint ambient encoder")
            require(
                row.get("construction_digest") == construction.get("digest")
                and row.get("ambient_initial_digest") == ambient.get("initial_digest")
                and row.get("ambient_final_digest") == ambient.get("final_digest"),
                f"training/checkpoint construction or ambient mismatch: {arm}/seed{seed}",
            )
            for field in ("elapsed_seconds", "final_loss"):
                value = row.get(field)
                require(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(float(value))
                    and float(value) >= 0.0,
                    f"training {field} is invalid: {arm}/seed{seed}",
                )
            trajectory = row.get("trajectory")
            require(
                isinstance(trajectory, list) and trajectory,
                f"training trajectory is missing: {arm}/seed{seed}",
            )
            config = require_mapping(row.get("config"), f"training config {arm}/seed{seed}")
            previous_step = 0
            numeric_fields = TRAJECTORY_ROW_KEYS - {
                "step",
                "length",
                "auxiliary_delay_steps",
                "auxiliary_ramp_end_step",
                "relation_context_indices",
                "relation_cell_indices",
                "relation_cells_per_context",
                "relation_cells_total",
            }
            for index, raw_trajectory_row in enumerate(trajectory):
                trajectory_row = require_mapping(
                    raw_trajectory_row,
                    f"trajectory row {index} {arm}/seed{seed}",
                )
                _require_exact_keys(
                    trajectory_row,
                    TRAJECTORY_ROW_KEYS,
                    f"trajectory row {index} {arm}/seed{seed}",
                )
                step = trajectory_row.get("step")
                length = trajectory_row.get("length")
                require(
                    type(step) is int
                    and previous_step < step <= config.get("steps"),
                    f"training trajectory step sequence is invalid: {arm}/seed{seed}",
                )
                require(
                    type(length) is int
                    and 1 <= length <= config.get("train_max_length"),
                    f"training trajectory length is invalid: {arm}/seed{seed}",
                )
                previous_step = step
                for field in numeric_fields:
                    value = trajectory_row.get(field)
                    require(
                        isinstance(value, (int, float))
                        and not isinstance(value, bool)
                        and math.isfinite(float(value))
                        and float(value) >= 0.0,
                        f"training trajectory {field} is invalid: {arm}/seed{seed}",
                    )
                require(
                    0.0 <= float(trajectory_row["terminal_accuracy"]) <= 1.0
                    and 0.0 <= float(trajectory_row["construction_accuracy"]) <= 1.0,
                    f"training trajectory accuracy is invalid: {arm}/seed{seed}",
                )
                delay = config.get("auxiliary_delay_steps")
                ramp_end = config.get("auxiliary_ramp_end_step")
                warmup_steps = config.get("warmup_steps")
                require(
                    trajectory_row.get("auxiliary_delay_steps") == delay
                    and trajectory_row.get("auxiliary_ramp_end_step") == ramp_end,
                    f"training trajectory auxiliary schedule mismatch: {arm}/seed{seed}",
                )
                expected_auxiliary = (
                    0.0
                    if step <= delay
                    else 1.0
                    if step >= ramp_end
                    else (step - delay) / (ramp_end - delay)
                )
                expected_base = 1.0 if warmup_steps == 0 else min(1.0, step / warmup_steps)
                require(
                    math.isclose(
                        float(trajectory_row["auxiliary_multiplier"]),
                        expected_auxiliary,
                        rel_tol=1e-15,
                        abs_tol=0.0,
                    )
                    and math.isclose(
                        float(trajectory_row["base_warmup"]),
                        expected_base,
                        rel_tol=1e-15,
                        abs_tol=0.0,
                    ),
                    f"training trajectory staged multiplier mismatch: {arm}/seed{seed}",
                )
                require(
                    isinstance(trajectory_row.get("relation_context_indices"), list)
                    and all(
                        type(value) is int
                        for value in trajectory_row["relation_context_indices"]
                    )
                    and trajectory_row["relation_context_indices"]
                    == list(range(config.get("auxiliary_contexts")))
                    and isinstance(trajectory_row.get("relation_cell_indices"), list)
                    and all(
                        type(value) is int
                        for value in trajectory_row["relation_cell_indices"]
                    )
                    and trajectory_row["relation_cell_indices"]
                    == list(range(config.get("relation_cells_per_step")))
                    and type(trajectory_row.get("relation_cells_per_context")) is int
                    and trajectory_row["relation_cells_per_context"]
                    == config.get("relation_cells_per_step")
                    and type(trajectory_row.get("relation_cells_total")) is int
                    and trajectory_row["relation_cells_total"]
                    == config.get("auxiliary_contexts")
                    * config.get("relation_cells_per_step"),
                    f"training trajectory relation-cell schedule mismatch: {arm}/seed{seed}",
                )
            last = require_mapping(trajectory[-1], f"final trajectory row {arm}/seed{seed}")
            require(
                trajectory[0].get("step") == 1,
                f"training trajectory does not begin at step one: {arm}/seed{seed}",
            )
            require(
                last.get("step") == config.get("steps"),
                f"training trajectory does not end at configured step: {arm}/seed{seed}",
            )
            require(
                last.get("loss") == row.get("final_loss"),
                f"training final loss differs from trajectory: {arm}/seed{seed}",
            )


def verify_training_contract(
    value: Any,
    metadata_index: Mapping[tuple[int, str], Mapping[str, Any]],
    *,
    first_seed: int,
) -> None:
    contract = require_mapping(value, "RESULTS training contract")
    _require_exact_keys(
        contract,
        {
            "plan_version",
            "arms",
            "config",
            "stream_lineage",
            "auxiliary_schedule",
            "relation_exposure",
            "learned_intertwiner",
            "hard_kernel",
            "claim_boundary",
        },
        "RESULTS training contract",
    )
    reference = metadata_index[(first_seed, PRIMARY_ARMS[0])]
    require(
        contract.get("plan_version") == reference.get("plan_version"),
        "RESULTS training-contract plan version mismatch",
    )
    require(
        contract.get("plan_version") == PLAN_VERSION,
        "RESULTS training-contract plan version mismatch",
    )
    require(
        contract.get("arms") == [ARM_METADATA[arm] for arm in PRIMARY_ARMS],
        "RESULTS training-contract arm panel mismatch",
    )
    require(
        contract.get("config") == reference.get("config"),
        "RESULTS training-contract config mismatch",
    )
    schedule = require_mapping(
        contract.get("auxiliary_schedule"),
        "RESULTS training-contract auxiliary schedule",
    )
    _require_exact_keys(
        schedule,
        {
            "delay_steps",
            "ramp_end_step",
            "rule",
            "base_warmup_steps",
            "base_warmup_is_independent",
        },
        "RESULTS training-contract auxiliary schedule",
    )
    config = require_mapping(reference.get("config"), "reference checkpoint config")
    require(
        schedule.get("delay_steps") == config.get("auxiliary_delay_steps")
        and schedule.get("ramp_end_step") == config.get("auxiliary_ramp_end_step")
        and schedule.get("base_warmup_steps") == config.get("warmup_steps")
        and schedule.get("base_warmup_is_independent") is True
        and schedule.get("rule")
        == (
            "zero through completed delay_steps; linear ramp thereafter; "
            "one at completed ramp_end_step"
        ),
        "RESULTS training-contract schedule mismatch",
    )
    _verify_relation_exposure(
        contract.get("relation_exposure"),
        config,
        "RESULTS training-contract relation exposure",
    )
    require(
        contract.get("relation_exposure") == reference.get("relation_exposure"),
        "RESULTS training-contract relation exposure/checkpoint mismatch",
    )


def verify_evaluation_bank(
    bank: Mapping[str, Any],
    *,
    source_sha256: str,
    preregistration_sha256: str,
) -> str:
    require(bank.get("schema") == EVAL_BANK_SCHEMA, "evaluation-bank schema mismatch")
    _verify_identity(
        bank,
        "evaluation bank",
        source_sha256=source_sha256,
        preregistration_sha256=preregistration_sha256,
    )
    return _verify_self_seal(bank, "fingerprint", "evaluation bank")


def _verify_record_index(
    directory: Path,
    inventory: Mapping[str, Path],
    result: Mapping[str, Any],
    *,
    expected_arms: Sequence[str],
    expected_seeds: Sequence[int],
    checkpoint_rows: Mapping[tuple[int, str], Mapping[str, Any]],
    source_sha256: str,
    preregistration_sha256: str,
) -> tuple[list[Mapping[str, Any]], dict[str, dict[str, Mapping[str, Any]]]]:
    raw_index = result.get("record_index")
    require(isinstance(raw_index, list), "RESULTS record_index is missing")
    expected_grid = {
        (int(seed), str(arm)) for seed in expected_seeds for arm in expected_arms
    }
    observed: dict[tuple[int, str], Mapping[str, Any]] = {}
    record_tree: dict[str, dict[str, Mapping[str, Any]]] = {
        str(int(seed)): {} for seed in expected_seeds
    }
    order: list[tuple[int, str]] = []
    for index, raw in enumerate(raw_index):
        row = require_mapping(raw, f"record index row {index}")
        _require_exact_keys(row, {"path", "sha256", "arm", "seed"}, f"record index row {index}")
        arm, seed = row.get("arm"), row.get("seed")
        require(isinstance(arm, str) and type(seed) is int, f"record index identity is invalid: {index}")
        key = (seed, arm)
        require(key not in observed, f"duplicate record arm/seed: {key}")
        expected_path = f"records/{arm}_seed{seed}.json"
        require(row.get("path") == expected_path, f"record path does not match arm/seed: {key}")
        path = _safe_member(directory, row.get("path"), f"record {arm}/seed{seed}")
        require(file_sha256(path) == require_sha256(row.get("sha256"), f"record hash {key}"), f"record file hash mismatch: {expected_path}")
        record = require_mapping(load_json(path, expected_path), expected_path)
        _require_exact_keys(
            record,
            {
                "schema",
                "version",
                "seed",
                "arm",
                "source_digest",
                "preregistration_sha256",
                "checkpoint_sha256",
                "checkpoint_state_digest",
                "behavior",
                "geometry",
                "null_perturbation",
            },
            f"record {arm}/seed{seed}",
        )
        require(record.get("schema") == RECORD_SCHEMA, f"record schema mismatch: {key}")
        _verify_identity(
            record,
            f"record {arm}/seed{seed}",
            source_sha256=source_sha256,
            preregistration_sha256=preregistration_sha256,
        )
        require(record.get("arm") == arm and record.get("seed") == seed, f"record identity mismatch: {key}")
        checkpoint_row = checkpoint_rows[key]
        require(
            record.get("checkpoint_sha256") == checkpoint_row.get("sha256")
            and record.get("checkpoint_state_digest") == checkpoint_row.get("state_digest"),
            f"record/checkpoint binding mismatch: {key}",
        )
        observed[key] = row
        record_tree[str(seed)][arm] = record
        order.append(key)
    require(order == sorted(order), "record index is not sorted by seed and arm")
    require(set(observed) == expected_grid, "record index does not cover the exact seed/arm grid")
    actual_record_files = {
        relative for relative in inventory if PurePosixPath(relative).parts[:1] == ("records",)
    }
    expected_record_files = {str(row["path"]) for row in observed.values()}
    require(actual_record_files == expected_record_files, "records directory contains missing or extra artifacts")
    normalized = [dict(row) for row in raw_index]
    return normalized, record_tree


def _hash_from_completion(
    completion: Mapping[str, Any], key: str, expected: str, label: str
) -> None:
    require(
        require_sha256(completion.get(key), f"RUN_COMPLETE {key}") == expected,
        f"RUN_COMPLETE hash mismatch for {label}",
    )


def verify_result_directory(
    root: Path,
    directory: Path,
    *,
    replay: bool = False,
) -> Mapping[str, Any]:
    """Verify one complete v0.6 smoke, screen, or pilot directory."""

    root = root.resolve(strict=True)
    directory = directory.resolve(strict=True)
    try:
        directory.relative_to(root)
    except ValueError as error:
        raise VerificationError("result directory must be contained by package root") from error
    inventory = scan_run_tree(directory)
    preregistration, preregistration_sha256 = verify_preregistration(root)
    current_source_digest, current_source_files = source_digest(root)

    required = {
        "RUN_STARTED.json",
        "CHECKPOINT_SEAL.json",
        "EVAL_BANK.json",
        "CONTROLS.json",
        "RESULTS.json",
        "GATES.json",
        "REPORT.md",
        "RUN_COMPLETE.json",
    }
    require(required <= set(inventory), f"run is incomplete; missing={sorted(required - set(inventory))}")
    started = require_mapping(load_json(directory / "RUN_STARTED.json"), "RUN_STARTED.json")
    seal = require_mapping(load_json(directory / "CHECKPOINT_SEAL.json"), "CHECKPOINT_SEAL.json")
    bank = require_mapping(load_json(directory / "EVAL_BANK.json"), "EVAL_BANK.json")
    controls_file = require_mapping(load_json(directory / "CONTROLS.json"), "CONTROLS.json")
    result = require_mapping(load_json(directory / "RESULTS.json"), "RESULTS.json")
    gates = require_mapping(load_json(directory / "GATES.json"), "GATES.json")
    completion = require_mapping(load_json(directory / "RUN_COMPLETE.json"), "RUN_COMPLETE.json")

    schemas = (
        (started, STARTED_SCHEMA, "RUN_STARTED"),
        (result, RESULT_SCHEMA, "RESULTS"),
        (gates, GATES_SCHEMA, "GATES"),
        (completion, COMPLETION_SCHEMA, "RUN_COMPLETE"),
    )
    for artifact, schema, label in schemas:
        require(artifact.get("schema") == schema, f"{label} schema mismatch")
        _verify_identity(
            artifact,
            label,
            source_sha256=current_source_digest,
            preregistration_sha256=preregistration_sha256,
        )
    _require_exact_keys(result, RESULT_KEYS, "RESULTS")
    _require_exact_keys(gates, GATES_KEYS, "GATES")
    _require_exact_keys(completion, COMPLETION_KEYS, "RUN_COMPLETE")
    _require_exact_keys(
        started,
        {
            "schema",
            "version",
            "profile",
            "run_mode",
            "source_digest",
            "preregistration_sha256",
            "runtime",
        },
        "RUN_STARTED",
    )

    profile = result.get("profile")
    require(profile in {"smoke", "screen", "pilot"}, "RESULTS profile is invalid")
    run_mode = result.get("run_mode")
    allowed_modes = {
        "smoke": {"developmental"},
        "screen": {"developmental"},
        "pilot": {"fresh_pilot", "non_evidentiary_pilot_replay"},
    }
    require(run_mode in allowed_modes[profile], "RESULTS run_mode/profile mismatch")
    for artifact, label in ((started, "RUN_STARTED"), (gates, "GATES"), (completion, "RUN_COMPLETE")):
        require(artifact.get("profile") == profile, f"{label}/RESULTS profile mismatch")
        require(artifact.get("run_mode") == run_mode, f"{label}/RESULTS run-mode mismatch")

    profile_config = require_mapping(
        require_mapping(preregistration.get("profiles"), "preregistration profiles").get(profile),
        f"preregistered {profile} profile",
    )
    config = require_mapping(result.get("config"), "RESULTS config")
    require(
        _profile_matches_preregistration(config, profile_config),
        "RESULTS config differs from preregistration",
    )
    require(
        result.get("source_files") == current_source_files,
        "RESULTS source-file inventory mismatch",
    )
    seeds = profile_config.get("seeds")
    assert isinstance(seeds, list)

    seal_rows = verify_checkpoint_seal(
        directory,
        seal,
        inventory,
        expected_arms=PRIMARY_ARMS,
        expected_seeds=seeds,
        source_sha256=current_source_digest,
        preregistration_sha256=preregistration_sha256,
    )
    embedded_seal = result.get("checkpoint_seal")
    require(embedded_seal == seal, "RESULTS checkpoint seal differs from CHECKPOINT_SEAL.json")
    checkpoint_count, checkpoint_metadata = verify_checkpoint_payloads(
        directory,
        seal_rows,
        source_sha256=current_source_digest,
        preregistration_sha256=preregistration_sha256,
        registered_profile=profile_config,
        preregistration=preregistration,
    )
    verify_training_contract(
        result.get("training_contract"),
        checkpoint_metadata,
        first_seed=int(seeds[0]),
    )
    verify_training_grid(
        result.get("training"),
        checkpoint_metadata,
        expected_arms=PRIMARY_ARMS,
        expected_seeds=seeds,
    )

    bank_fingerprint = verify_evaluation_bank(
        bank,
        source_sha256=current_source_digest,
        preregistration_sha256=preregistration_sha256,
    )
    require(
        result.get("evaluation_bank_fingerprint") == bank_fingerprint,
        "RESULTS evaluation-bank fingerprint mismatch",
    )

    record_index, record_tree = _verify_record_index(
        directory,
        inventory,
        result,
        expected_arms=PRIMARY_ARMS,
        expected_seeds=seeds,
        checkpoint_rows=seal_rows,
        source_sha256=current_source_digest,
        preregistration_sha256=preregistration_sha256,
    )
    require(result.get("records") == record_tree, "RESULTS records differ from sealed record files")
    aggregate = require_mapping(result.get("aggregate"), "RESULTS aggregate")
    require(set(aggregate) == set(PRIMARY_ARMS), "RESULTS aggregate arm grid mismatch")
    aggregate_digest = canonical_object_sha256(aggregate)
    require(
        result.get("aggregate_sha256") == aggregate_digest,
        "RESULTS aggregate hash mismatch",
    )
    require(result.get("gates") == gates, "RESULTS gates differ from GATES.json")
    require(result.get("controls") == controls_file, "RESULTS controls differ from CONTROLS.json")
    _require_exact_keys(
        controls_file,
        {"schema", "kernel", "behavioral", "assay_valid"},
        "CONTROLS",
    )
    require(
        controls_file.get("schema")
        == "komorebi.neuralese.invariant_kernel.controls.v1",
        "CONTROLS schema mismatch",
    )
    require(
        isinstance(controls_file.get("kernel"), dict)
        and isinstance(controls_file.get("behavioral"), dict)
        and controls_file.get("assay_valid") is True,
        "CONTROLS assay receipt is invalid",
    )
    gate_status = require_mapping(gates.get("status"), "GATES status")
    require(gate_status.get("execution_integrity") == "PASS", "execution integrity did not pass")
    require(gate_status.get("assay_validity") == "PASS", "assay validity did not pass")

    chart = require_mapping(result.get("chart"), "RESULTS chart")
    _require_exact_keys(chart, {"path", "sha256"}, "RESULTS chart")
    chart_path = _safe_member(directory, chart.get("path"), "summary chart")
    chart_sha = require_sha256(chart.get("sha256"), "RESULTS chart sha256")
    require(file_sha256(chart_path) == chart_sha, "chart hash mismatch")

    _hash_from_completion(completion, "results_sha256", file_sha256(directory / "RESULTS.json"), "RESULTS.json")
    _hash_from_completion(completion, "gates_sha256", file_sha256(directory / "GATES.json"), "GATES.json")
    _hash_from_completion(completion, "report_sha256", file_sha256(directory / "REPORT.md"), "REPORT.md")
    _hash_from_completion(completion, "chart_sha256", chart_sha, str(chart["path"]))
    _hash_from_completion(
        completion,
        "checkpoint_seal_sha256",
        file_sha256(directory / "CHECKPOINT_SEAL.json"),
        "CHECKPOINT_SEAL.json",
    )
    require(
        completion.get("evaluation_bank_fingerprint") == bank_fingerprint,
        "RUN_COMPLETE evaluation-bank fingerprint mismatch",
    )
    require(completion.get("record_hashes") == record_index, "RUN_COMPLETE record hashes differ from RESULTS index")
    _hash_from_completion(completion, "aggregate_sha256", aggregate_digest, "aggregate")
    _hash_from_completion(
        completion,
        "controls_sha256",
        file_sha256(directory / "CONTROLS.json"),
        "CONTROLS.json",
    )
    require(completion.get("execution_integrity") == gate_status.get("execution_integrity"), "RUN_COMPLETE execution status mismatch")
    require(completion.get("assay_validity") == gate_status.get("assay_validity"), "RUN_COMPLETE assay status mismatch")
    require(completion.get("scientific_status") == gate_status.get("scientific_status"), "RUN_COMPLETE scientific status mismatch")
    require(completion.get("pilot_promotion") == gate_status.get("pilot_promotion"), "RUN_COMPLETE promotion status mismatch")

    replay_receipt: Mapping[str, Any] | None = None
    if replay:
        replay_receipt = _runtime_replay(root, directory)
    # Re-scan to ensure imports/replay did not leave bytecode inside the run.
    scan_run_tree(directory)
    return {
        "path": directory.relative_to(root).as_posix(),
        "profile": profile,
        "run_mode": run_mode,
        "status": "PASS",
        "checkpoint_payloads_verified": checkpoint_count,
        "record_files_verified": len(record_index),
        "source_digest": current_source_digest,
        "preregistration_sha256": preregistration_sha256,
        "scientific_status": gate_status.get("scientific_status", "NOT_EVALUATED"),
        "runtime_replay": replay_receipt,
    }


def discover_result_directories(root: Path) -> list[Path]:
    results = root / "results"
    require(results.is_dir() and not results.is_symlink(), "results directory is missing")
    discovered = [
        path.parent
        for path in sorted(results.glob("*/RESULTS.json"), key=lambda item: item.as_posix())
        if path.parent.is_dir() and not path.parent.is_symlink()
    ]
    v06: list[Path] = []
    for directory in discovered:
        result = require_mapping(load_json(directory / "RESULTS.json"), f"{directory.name}/RESULTS.json")
        if result.get("schema") == RESULT_SCHEMA:
            v06.append(directory)
    require(v06, "no completed v0.6 result directory was found")
    return v06


def _runtime_replay(root: Path, directory: Path) -> Mapping[str, Any]:
    runner_path = root / RUNNER_NAME
    require(runner_path.is_file() and not runner_path.is_symlink(), f"{RUNNER_NAME} is missing")
    module_name = "_komorebi_verified_invariant_kernel_runner"
    spec = importlib.util.spec_from_file_location(module_name, runner_path)
    require(spec is not None and spec.loader is not None, "cannot import verified invariant-kernel runner")
    previous_path = list(sys.path)
    try:
        for value in reversed((str(root), str(root / "src"))):
            if value not in sys.path:
                sys.path.insert(0, value)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        hook = getattr(module, "verify_retained_run", None)
        require(callable(hook), "runner exposes no verify_retained_run replay hook")
        receipt = hook(directory, structural_only=False)
        require(isinstance(receipt, dict) and receipt.get("status") == "PASS", "runner replay did not pass")
        return receipt
    except VerificationError:
        raise
    except Exception as error:
        raise VerificationError(f"runtime replay failed: {error}") from error
    finally:
        sys.modules.pop(module_name, None)
        sys.path[:] = previous_path


def verify_package(
    root: Path,
    *,
    result_directory: Path | None = None,
    replay: bool = False,
) -> Mapping[str, Any]:
    require(not root.is_symlink(), "package root may not be a symbolic link")
    if result_directory is not None:
        require(
            not result_directory.is_symlink(),
            "result directory may not be a symbolic link",
        )
    root = root.resolve(strict=True)
    scan_package_safety(root)
    directories = (
        [result_directory.resolve(strict=True)]
        if result_directory is not None
        else discover_result_directories(root)
    )
    runs = [verify_result_directory(root, directory, replay=replay) for directory in directories]
    scan_package_safety(root)
    return {
        "schema": VERIFICATION_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "status": "PASS",
        "runs": runs,
        "developmental_runs": sum(run["profile"] in {"smoke", "screen"} for run in runs),
        "fresh_pilots": sum(run["run_mode"] == "fresh_pilot" for run in runs),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--result-dir", type=Path)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args(argv)
    if not (sys.flags.ignore_environment and sys.flags.safe_path and sys.dont_write_bytecode):
        print("Run with: python -E -P -B verify_invariant_kernel.py", file=sys.stderr)
        return 2
    try:
        receipt = verify_package(
            args.root,
            result_directory=args.result_dir,
            replay=args.replay,
        )
        print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    except (OSError, VerificationError, ValueError) as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AUTHOR",
    "CHECKPOINT_PAYLOAD_KEYS",
    "PRIMARY_ARMS",
    "VERSION",
    "VerificationError",
    "canonical_json_bytes",
    "canonical_object_sha256",
    "file_sha256",
    "load_json",
    "source_digest",
    "verify_package",
    "verify_result_directory",
]
