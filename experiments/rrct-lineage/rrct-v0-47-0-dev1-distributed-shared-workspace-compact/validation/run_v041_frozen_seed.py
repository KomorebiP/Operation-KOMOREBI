"""Run one freeze-bound arm of the RRCT v0.41.1 paired pilot matrix.

This module deliberately has no top-level RRCT imports.  It verifies the
pre-outcome freeze and its unopened seed registry, and it durably consumes the
seed/condition claim, before importing or constructing the experimental
runtime.  A completed arm is always labelled exploratory pilot evidence, never
confirmatory evidence.  Scientific endpoint misses are retained as completed
results; only execution or integrity failures raise.
"""

from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import tempfile
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.41.1.dev2"
FREEZE_NAME = "V0_41_1_PREOUTCOME_FREEZE.json"
FREEZE_SCHEMA = "rrct.v0411.preoutcome_freeze.v1"
REGISTRY_NAME = "V0_41_1_SEED_REGISTRY.json"
REGISTRY_SCHEMA = "rrct.v0411.seed_registry.v1"
SELECTION_RECEIPT_NAME = "V0_41_1_SEED_SELECTION_RECEIPT.json"
SELECTION_RECEIPT_SCHEMA = "rrct.v0411.seed_selection_receipt.v1"
SELECTION_SCAN_MANIFEST_NAME = "V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
SELECTION_SCAN_MANIFEST_SCHEMA = "rrct.v0411.seed_selection_scan_manifest.v1"
EXTERNAL_COMMITMENT_NAME = "V0_41_1_PREOUTCOME_EXTERNAL_COMMITMENT.json"
EXTERNAL_COMMITMENT_SCHEMA = "rrct.v0411.preoutcome_external_commitment.v1"
CAMPAIGN_DIRECTORY_NAME = "v0.41.1_frozen_exploratory_pilot_campaign"
CAMPAIGN_LOCK_NAME = ".v0.41.1_frozen_exploratory_pilot_campaign.lock"

START_NAME = "start_receipt.json"
ROWS_NAME = "sealed_rows.jsonl"
SUMMARY_NAME = "summary.json"
FINISH_NAME = "finish_receipt.json"
FAILURE_NAME = "failure_receipt.json"
ARTIFACT_NAME = "artifact_sha256.json"

START_SCHEMA = "rrct.v0411.frozen_pilot_condition.start.v1"
FINISH_SCHEMA = "rrct.v0411.frozen_pilot_condition.finish.v1"
FAILURE_SCHEMA = "rrct.v0411.frozen_pilot_condition.failure.v1"
CLAIM_SCHEMA = "rrct.v0411.frozen_pilot_condition.claim.v1"
SEED_CLAIM_SCHEMA = "rrct.v0411.frozen_pilot_seed.claim.v1"
CAMPAIGN_SCHEMA = "rrct.v0411.frozen_pilot_campaign.v1"

SCIENTIFIC_STATUS = "frozen_exploratory_pilot_not_confirmatory"
FREEZE_SCIENTIFIC_STATUS = "fresh_pilot_temporal_identity_preoutcome_freeze"
ATTEMPT_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,80}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

MANDATORY_FROZEN_SOURCE_PATHS = (
    "src/rrct/post_change_closure_experiment.py",
    "src/rrct/temporal_self_identity.py",
    "src/rrct/temporal_self_identity_experiment.py",
    "validation/run_v041_frozen_seed.py",
)

CONDITIONS: dict[str, dict[str, Any]] = {
    "K_RPLUS": {
        "history_policy": "keyed",
        "historical_prior_enabled": True,
        "world_variant": "true_recurrence",
    },
    "N_RPLUS": {
        "history_policy": "withheld",
        "historical_prior_enabled": False,
        "world_variant": "true_recurrence",
    },
    "G_RPLUS": {
        "history_policy": "generic",
        "historical_prior_enabled": True,
        "world_variant": "true_recurrence",
    },
    "K_RMINUS": {
        "history_policy": "keyed",
        "historical_prior_enabled": True,
        "world_variant": "same_key_null_lure",
    },
    "N_RMINUS": {
        "history_policy": "withheld",
        "historical_prior_enabled": False,
        "world_variant": "same_key_null_lure",
    },
    "G_RMINUS": {
        "history_policy": "generic",
        "historical_prior_enabled": True,
        "world_variant": "same_key_null_lure",
    },
}

PHASE_STEPS: tuple[tuple[str, int], ...] = (
    ("identity_a_initial", 1_440),
    ("world_shock_a", 480),
    ("identity_b_first", 1_440),
    ("disconnect_one", 1_440),
    ("identity_a_return_one", 1_440),
    ("identity_b_return", 1_440),
    ("disconnect_two", 1_440),
    ("identity_a_return_two", 1_440),
)
EXPECTED_TRANSITION_COUNT = sum(count for _phase, count in PHASE_STEPS)

REQUIRED_ENVIRONMENT = {
    "PYTHONHASHSEED": "0",
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}
REQUIRED_PYTHON_FLAGS = {
    "safe_path": True,
    "no_user_site": True,
    "dont_write_bytecode": True,
}
REQUIRED_PREEXECUTION_CHECKS = (
    "development_science_audit_pass",
    "development_integrity_yoking_audit_pass",
    "focused_v041_tests_pass",
    "frozen_runner_adversarial_tests_pass",
    "campaign_auditor_present",
    "seed_selection_receipt_valid",
    "seed_scan_manifest_valid",
    "seed_registry_exactly_four_unopened",
    "scientific_source_inputs_present",
    "production_hashes_match_development_evidence",
    "no_fresh_rows_or_outcomes_opened",
    "environment_contract_declared",
)
SELECTION_DRAW_EXPRESSION = "secrets.randbelow(800_000_000) + 100_000_000"
SELECTION_SCAN_RULE = "standalone_decimal_occurrences_not_adjacent_to_ascii_digits"


class FrozenPilotError(RuntimeError):
    """A fail-closed v0.41.1 freeze, claim, or evidence violation."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise FrozenPilotError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> None:
    raise FrozenPilotError(f"nonfinite JSON token: {token}")


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"required frozen-pilot file is missing: {path}")
    try:
        return json.loads(
            path.read_bytes(),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except FrozenPilotError:
        raise
    except Exception as error:
        raise FrozenPilotError(f"invalid JSON in {path}: {error}") from error


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(
        os.fspath(directory),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, payload: bytes) -> None:
    remaining = memoryview(payload)
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("frozen-pilot write made no progress")
        remaining = remaining[written:]


def _atomic_no_replace_json(path: Path, payload: Mapping[str, Any]) -> str:
    """Publish a complete receipt atomically without replacing an existing one."""

    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        _write_all(descriptor, encoded)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    try:
        os.link(temporary, path, follow_symlinks=False)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
            _fsync_directory(path.parent)
        except FileNotFoundError:
            pass
    return hashlib.sha256(encoded).hexdigest()


# Kept as the local publication primitive name used throughout this runner.
_exclusive_json = _atomic_no_replace_json


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise FrozenPilotError(f"{label} is not a lowercase SHA-256 digest")
    return value


def _validate_seed(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("seed must be a positive integer below 2**63")
    seed = int(value)
    if not 1 <= seed < 2**63:
        raise ValueError("seed must be a positive integer below 2**63")
    return seed


def _canonical_project_root(project_root: Path) -> Path:
    supplied = Path(os.path.abspath(os.fspath(project_root)))
    resolved = supplied.resolve(strict=True)
    if supplied != resolved:
        raise FrozenPilotError(
            "project root must be an already-resolved nonsymlink path"
        )
    if not resolved.is_dir() or resolved.is_symlink():
        raise FrozenPilotError("project root must be a nonsymlink directory")
    validation = resolved / "validation"
    if not validation.is_dir() or validation.is_symlink():
        raise FrozenPilotError("validation must be a nonsymlink project directory")
    return resolved


def _project_file(project_root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise FrozenPilotError(f"{label} must be a nonempty relative path")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise FrozenPilotError(f"{label} must stay inside the project root")
    unresolved = project_root / candidate
    path = unresolved.resolve(strict=True)
    try:
        path.relative_to(project_root)
    except (TypeError, ValueError) as error:
        raise FrozenPilotError(f"{label} escapes the project root") from error
    if not path.is_file():
        raise FrozenPilotError(f"{label} is not a regular file")
    if unresolved.absolute() != path or unresolved.is_symlink():
        raise FrozenPilotError(f"{label} must not traverse a symlink")
    return path


def _verify_checksum_companion(freeze_path: Path) -> str:
    checksum_path = freeze_path.with_name(f"{freeze_path.name}.sha256")
    if not checksum_path.is_file():
        raise FileNotFoundError("v0.41.1 freeze checksum companion is missing")
    observed = _sha256_file(freeze_path)
    parts = checksum_path.read_text(encoding="utf-8").strip().split()
    if (
        len(parts) != 2
        or parts[0] != observed
        or Path(parts[1]).name != freeze_path.name
    ):
        raise FrozenPilotError("v0.41.1 freeze checksum companion mismatch")
    return observed


def _validate_selection_artifacts(
    project_root: Path,
    freeze: Mapping[str, Any],
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    scan_binding = freeze.get("seed_selection_scan_manifest")
    if not isinstance(scan_binding, Mapping):
        raise FrozenPilotError("seed-selection scan-manifest binding is missing")
    if (
        scan_binding.get("relative_path")
        != f"validation/{SELECTION_SCAN_MANIFEST_NAME}"
    ):
        raise FrozenPilotError("seed-selection scan-manifest path mismatch")
    if scan_binding.get("schema") != SELECTION_SCAN_MANIFEST_SCHEMA:
        raise FrozenPilotError("seed-selection scan-manifest schema mismatch")
    scan_path = _project_file(
        project_root,
        scan_binding.get("relative_path"),
        "seed-selection scan manifest",
    )
    scan_sha256 = _require_sha256(
        scan_binding.get("sha256"),
        "seed_selection_scan_manifest.sha256",
    )
    if freeze.get("seed_selection_scan_manifest_sha256") != scan_sha256:
        raise FrozenPilotError("top-level scan-manifest digest mismatch")
    if _sha256_file(scan_path) != scan_sha256:
        raise FrozenPilotError("seed-selection scan-manifest digest mismatch")
    scan = _load_json(scan_path)
    if not isinstance(scan, Mapping):
        raise FrozenPilotError("seed-selection scan manifest must be an object")
    if scan.get("schema") != SELECTION_SCAN_MANIFEST_SCHEMA:
        raise FrozenPilotError("seed-selection scan schema mismatch")
    if scan.get("version") != VERSION:
        raise FrozenPilotError("seed-selection scan version mismatch")
    if scan.get("scientific_status") != "pre_registry_complete_project_evidence_scan":
        raise FrozenPilotError("seed-selection scan scientific status mismatch")
    if scan.get("scan_rule") != SELECTION_SCAN_RULE:
        raise FrozenPilotError("seed-selection scan rule mismatch")
    files = scan.get("files")
    if not isinstance(files, list) or not files:
        raise FrozenPilotError("seed-selection scan file list is empty")
    if scan.get("file_count") != len(files):
        raise FrozenPilotError("seed-selection scan file count mismatch")
    paths: list[str] = []
    for index, record in enumerate(files):
        if not isinstance(record, Mapping):
            raise FrozenPilotError(f"scan file record {index} is not an object")
        relative = record.get("relative_path")
        if not isinstance(relative, str) or not relative:
            raise FrozenPilotError(f"scan file record {index} path is invalid")
        _require_sha256(record.get("sha256"), f"scan file record {index} sha256")
        size = record.get("size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise FrozenPilotError(f"scan file record {index} size is invalid")
        paths.append(relative)
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise FrozenPilotError("seed-selection scan paths are not sorted and unique")
    scan_surface_sha256 = _require_sha256(
        scan.get("scan_surface_sha256"),
        "seed-selection scan surface digest",
    )
    if _canonical_sha256(files) != scan_surface_sha256:
        raise FrozenPilotError("seed-selection scan surface digest mismatch")

    receipt_binding = freeze.get("seed_selection_receipt")
    if not isinstance(receipt_binding, Mapping):
        raise FrozenPilotError("seed-selection receipt binding is missing")
    if receipt_binding.get("relative_path") != f"validation/{SELECTION_RECEIPT_NAME}":
        raise FrozenPilotError("seed-selection receipt path mismatch")
    if receipt_binding.get("schema") != SELECTION_RECEIPT_SCHEMA:
        raise FrozenPilotError("seed-selection receipt schema mismatch")
    if receipt_binding.get("selection_state_at_freeze") != "unopened":
        raise FrozenPilotError("seed-selection receipt was not unopened at freeze")
    receipt_path = _project_file(
        project_root,
        receipt_binding.get("relative_path"),
        "seed-selection receipt",
    )
    receipt_sha256 = _require_sha256(
        receipt_binding.get("sha256"),
        "seed_selection_receipt.sha256",
    )
    if freeze.get("seed_selection_receipt_sha256") != receipt_sha256:
        raise FrozenPilotError("top-level selection-receipt digest mismatch")
    if _sha256_file(receipt_path) != receipt_sha256:
        raise FrozenPilotError("seed-selection receipt digest mismatch")
    receipt = _load_json(receipt_path)
    if not isinstance(receipt, Mapping):
        raise FrozenPilotError("seed-selection receipt must be an object")
    exact_receipt = {
        "schema": SELECTION_RECEIPT_SCHEMA,
        "version": VERSION,
        "scientific_status": "preoutcome_seed_selection_complete_unopened",
        "selection_method": "single_nonrepeated_secrets_randbelow_draw_loop",
        "draw_expression": SELECTION_DRAW_EXPRESSION,
        "candidate_count": 12,
        "scan_rule": SELECTION_SCAN_RULE,
        "selection_rule": (
            "first_four_candidates_in_generation_order_with_zero_occurrences"
        ),
        "selection_state": "unopened",
        "registry_state_at_selection": "unopened",
        "cohort_opened": False,
        "opened_seed_condition_pairs": [],
        "rows_or_outcomes_opened": 0,
        "no_redraw_after_scan": True,
        "wall_clock_time_in_record": False,
    }
    for key, value in exact_receipt.items():
        if receipt.get(key) != value:
            raise FrozenPilotError(f"seed-selection receipt mismatch: {key}")
    candidates = receipt.get("candidate_generation_order")
    if not isinstance(candidates, list) or len(candidates) != 12:
        raise FrozenPilotError("seed-selection receipt must contain 12 candidates")
    try:
        normalized_candidates = [_validate_seed(value) for value in candidates]
    except (TypeError, ValueError) as error:
        raise FrozenPilotError(str(error)) from error
    if len(set(normalized_candidates)) != 12 or not all(
        100_000_000 <= value <= 899_999_999 for value in normalized_candidates
    ):
        raise FrozenPilotError(
            "seed-selection candidates are not unique nine-digit values"
        )
    calls = receipt.get("randbelow_call_count")
    duplicates = receipt.get("duplicate_draw_count")
    if (
        isinstance(calls, bool)
        or not isinstance(calls, int)
        or calls < 12
        or isinstance(duplicates, bool)
        or not isinstance(duplicates, int)
        or duplicates != calls - 12
    ):
        raise FrozenPilotError("seed-selection draw accounting is invalid")
    records = receipt.get("candidate_scan_records")
    if not isinstance(records, list) or len(records) != 12:
        raise FrozenPilotError("seed-selection scan records are incomplete")
    zero_candidates: list[int] = []
    for index, (candidate, record) in enumerate(zip(normalized_candidates, records)):
        if not isinstance(record, Mapping):
            raise FrozenPilotError(f"candidate scan record {index} is not an object")
        count = record.get("standalone_decimal_occurrence_count")
        occurrence_paths = record.get("occurrence_paths")
        if (
            record.get("generation_index") != index
            or record.get("candidate") != candidate
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count < 0
            or not isinstance(occurrence_paths, list)
            or any(not isinstance(path, str) for path in occurrence_paths)
            or len(occurrence_paths) != count
            or record.get("zero_occurrence") is not (count == 0)
        ):
            raise FrozenPilotError(f"candidate scan record {index} is invalid")
        if count == 0:
            zero_candidates.append(candidate)
    selected = receipt.get("selected_fresh_pilot_seeds")
    if selected != zero_candidates[:4] or len(selected) != 4:
        raise FrozenPilotError(
            "seed selection is not the first four zero-occurrence candidates"
        )
    manifest_receipt = receipt.get("scan_manifest")
    if not isinstance(manifest_receipt, Mapping) or manifest_receipt != {
        "relative_path": f"validation/{SELECTION_SCAN_MANIFEST_NAME}",
        "schema": SELECTION_SCAN_MANIFEST_SCHEMA,
        "sha256": scan_sha256,
        "file_count": len(files),
        "scan_surface_sha256": scan_surface_sha256,
    }:
        raise FrozenPilotError("selection receipt scan-manifest binding mismatch")
    selector = receipt.get("selector")
    selector_relative = "validation/select_v0411_seeds.py"
    if (
        not isinstance(selector, Mapping)
        or selector.get("relative_path") != selector_relative
    ):
        raise FrozenPilotError("selection receipt selector binding mismatch")
    selector_sha256 = _require_sha256(selector.get("sha256"), "selector sha256")
    if source_hashes.get(selector_relative) != selector_sha256:
        raise FrozenPilotError(
            "frozen selector source does not match selection receipt"
        )
    return {
        "selection_scan_manifest": dict(scan),
        "selection_scan_manifest_path": scan_path,
        "selection_scan_manifest_sha256": scan_sha256,
        "selection_receipt": dict(receipt),
        "selection_receipt_path": receipt_path,
        "selection_receipt_sha256": receipt_sha256,
        "selected_fresh_pilot_seeds": tuple(selected),
    }


def _validate_preexecution_binding(
    project_root: Path,
    freeze: Mapping[str, Any],
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    expected_environment = {
        "environment": REQUIRED_ENVIRONMENT,
        "python_flags": REQUIRED_PYTHON_FLAGS,
    }
    if freeze.get("required_environment") != expected_environment:
        raise FrozenPilotError("freeze execution-environment contract mismatch")
    binding = freeze.get("preexecution_validation")
    if not isinstance(binding, Mapping):
        raise FrozenPilotError("freeze preexecution binding is missing")
    expected_binding = {
        "relative_path": "validation/V0_41_1_PREEXECUTION_VALIDATION.json",
        "schema": "rrct.v0411.preexecution_validation.v1",
        "scientific_status": "preoutcome_all_checks_pass",
        "all_checks_pass": True,
    }
    for key, value in expected_binding.items():
        if binding.get(key) != value:
            raise FrozenPilotError(f"freeze preexecution binding mismatch: {key}")
    digest = _require_sha256(binding.get("sha256"), "preexecution sha256")
    if freeze.get("preexecution_validation_sha256") != digest:
        raise FrozenPilotError("top-level preexecution digest mismatch")
    path = _project_file(
        project_root,
        binding.get("relative_path"),
        "preexecution validation",
    )
    if _sha256_file(path) != digest:
        raise FrozenPilotError("preexecution validation digest mismatch")
    record = _load_json(path)
    if not isinstance(record, Mapping):
        raise FrozenPilotError("preexecution validation must be an object")
    exact = {
        "schema": "rrct.v0411.preexecution_validation.v1",
        "version": VERSION,
        "scientific_status": "preoutcome_all_checks_pass",
        "all_checks_pass": True,
        "cohort_opened": False,
        "fresh_seed_state": "unopened",
        "errors": [],
        "failures": [],
        "failed_checks": [],
        "required_environment": expected_environment,
    }
    for key, value in exact.items():
        if record.get(key) != value:
            raise FrozenPilotError(f"preexecution validation mismatch: {key}")
    checks = record.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != set(
        REQUIRED_PREEXECUTION_CHECKS
    ):
        raise FrozenPilotError("preexecution validation exact checklist mismatch")
    if any(checks[key] is not True for key in REQUIRED_PREEXECUTION_CHECKS):
        raise FrozenPilotError("preexecution checklist contains a non-pass")
    if (
        not isinstance(record.get("test_command"), str)
        or not record["test_command"].strip()
    ):
        raise FrozenPilotError("preexecution test command is missing")
    count = record.get("passed_test_count")
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise FrozenPilotError("preexecution passed-test count is invalid")
    lock_digest = source_hashes.get("uv.lock")
    if record.get("dependency_lock_sha256") != lock_digest:
        raise FrozenPilotError("preexecution dependency-lock digest mismatch")
    production_paths = MANDATORY_FROZEN_SOURCE_PATHS[:3]
    production = {path: source_hashes[path] for path in production_paths}
    if record.get("production_source_sha256") != production:
        raise FrozenPilotError("preexecution production-source manifest mismatch")
    if record.get("production_source_set_sha256") != _canonical_sha256(production):
        raise FrozenPilotError("preexecution production source-set digest mismatch")
    return dict(record)


def verify_v0411_preoutcome_freeze(project_root: Path) -> dict[str, Any]:
    """Verify the future pre-outcome freeze and unopened seed registry."""

    project_root = _canonical_project_root(project_root)
    freeze_path = project_root / "validation" / FREEZE_NAME
    freeze_sha256 = _verify_checksum_companion(freeze_path)
    freeze = _load_json(freeze_path)
    if not isinstance(freeze, Mapping):
        raise FrozenPilotError("v0.41.1 freeze must be a JSON object")
    if freeze.get("schema") != FREEZE_SCHEMA:
        raise FrozenPilotError("v0.41.1 freeze schema mismatch")
    if freeze.get("version") != VERSION:
        raise FrozenPilotError("v0.41.1 freeze version mismatch")
    if freeze.get("scientific_status") != FREEZE_SCIENTIFIC_STATUS:
        raise FrozenPilotError("v0.41.1 freeze scientific status mismatch")
    if freeze.get("campaign_stage") != "fresh_pilot":
        raise FrozenPilotError("v0.41.1 freeze campaign stage mismatch")
    if freeze.get("confirmatory") is not False:
        raise FrozenPilotError("v0.41.1 pilot freeze cannot be confirmatory")
    if freeze.get("fresh_seed_state_at_freeze") != "unopened":
        raise FrozenPilotError("v0.41.1 freeze does not record unopened seeds")
    if freeze.get("cohort_opened_at_freeze") is not False:
        raise FrozenPilotError("v0.41.1 cohort was already open at freeze")
    if freeze.get("seed_selection_performed_by_freeze") is not False:
        raise FrozenPilotError("v0.41.1 freeze performed seed selection")
    if freeze.get("seed_claims_written_by_freeze") != 0:
        raise FrozenPilotError("v0.41.1 freeze records seed claims")
    if freeze.get("rows_or_outcomes_opened_by_freeze") != 0:
        raise FrozenPilotError("v0.41.1 freeze records opened rows or outcomes")

    if freeze.get("condition_matrix") != CONDITIONS:
        raise FrozenPilotError("v0.41.1 freeze condition matrix mismatch")
    if freeze.get("condition_names") != sorted(CONDITIONS):
        raise FrozenPilotError("v0.41.1 freeze condition-name set mismatch")

    source_hashes = freeze.get("scientific_source_sha256")
    if not isinstance(source_hashes, Mapping) or not source_hashes:
        raise FrozenPilotError("v0.41.1 freeze source manifest is missing")
    if not set(MANDATORY_FROZEN_SOURCE_PATHS).issubset(source_hashes):
        missing = sorted(set(MANDATORY_FROZEN_SOURCE_PATHS) - set(source_hashes))
        raise FrozenPilotError(f"mandatory frozen source is unbound: {missing}")
    normalized_source_hashes: dict[str, str] = {}
    for relative, expected_value in source_hashes.items():
        if not isinstance(relative, str):
            raise FrozenPilotError("frozen source path is not a string")
        expected = _require_sha256(
            expected_value,
            f"scientific_source_sha256[{relative!r}]",
        )
        path = _project_file(project_root, relative, f"frozen source {relative}")
        if _sha256_file(path) != expected:
            raise FrozenPilotError(f"frozen source mismatch: {relative}")
        normalized_source_hashes[relative] = expected
    source_set_sha256 = _require_sha256(
        freeze.get("scientific_source_set_sha256"),
        "scientific_source_set_sha256",
    )
    if _canonical_sha256(normalized_source_hashes) != source_set_sha256:
        raise FrozenPilotError("v0.41.1 frozen source-set digest mismatch")

    preexecution = _validate_preexecution_binding(
        project_root,
        freeze,
        normalized_source_hashes,
    )

    archive = freeze.get("source_archive")
    if not isinstance(archive, Mapping):
        raise FrozenPilotError("v0.41.1 source archive binding is missing")
    archive_path = _project_file(
        project_root,
        archive.get("relative_path"),
        "frozen source archive",
    )
    archive_sha256 = _require_sha256(
        archive.get("sha256"),
        "source_archive.sha256",
    )
    if _sha256_file(archive_path) != archive_sha256:
        raise FrozenPilotError("v0.41.1 frozen source archive mismatch")
    member_count = archive.get("member_count")
    if isinstance(member_count, bool) or not isinstance(member_count, int):
        raise FrozenPilotError("source_archive.member_count must be positive")
    if member_count <= 0:
        raise FrozenPilotError("source_archive.member_count must be positive")

    selection = _validate_selection_artifacts(
        project_root,
        freeze,
        normalized_source_hashes,
    )

    registry_binding = freeze.get("seed_registry")
    if not isinstance(registry_binding, Mapping):
        raise FrozenPilotError("v0.41.1 seed-registry binding is missing")
    if registry_binding.get("relative_path") != f"validation/{REGISTRY_NAME}":
        raise FrozenPilotError("v0.41.1 seed-registry path mismatch")
    if registry_binding.get("schema") != REGISTRY_SCHEMA:
        raise FrozenPilotError("v0.41.1 bound seed-registry schema mismatch")
    if registry_binding.get("registry_state_at_freeze") != "unopened":
        raise FrozenPilotError("v0.41.1 bound seed registry was not unopened")
    registry_path = _project_file(
        project_root,
        registry_binding.get("relative_path"),
        "seed registry",
    )
    registry_sha256 = _require_sha256(
        registry_binding.get("sha256"),
        "seed_registry.sha256",
    )
    if freeze.get("seed_registry_sha256") != registry_sha256:
        raise FrozenPilotError("top-level seed-registry digest mismatch")
    if _sha256_file(registry_path) != registry_sha256:
        raise FrozenPilotError("bound v0.41.1 seed-registry digest mismatch")

    registry = _load_json(registry_path)
    if not isinstance(registry, Mapping):
        raise FrozenPilotError("v0.41.1 seed registry must be a JSON object")
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise FrozenPilotError("v0.41.1 seed-registry schema mismatch")
    if registry.get("version") != VERSION:
        raise FrozenPilotError("v0.41.1 seed-registry version mismatch")
    if (
        registry.get("scientific_status")
        != "fresh_pilot_seed_registry_selected_unopened"
    ):
        raise FrozenPilotError("v0.41.1 seed-registry scientific status mismatch")
    if registry.get("registry_state") != "unopened":
        raise FrozenPilotError("v0.41.1 seed registry is not unopened")
    if registry.get("cohort_opened") is not False:
        raise FrozenPilotError("v0.41.1 seed-registry cohort is already open")
    if registry.get("conditions") != CONDITIONS:
        raise FrozenPilotError("v0.41.1 seed-registry condition matrix mismatch")
    if registry.get("opened_seed_condition_pairs") != []:
        raise FrozenPilotError("v0.41.1 seed registry records opened pairs")
    seed_values = registry.get("fresh_pilot_seeds")
    if not isinstance(seed_values, list) or len(seed_values) != 4:
        raise FrozenPilotError("v0.41.1 seed registry must contain exactly four seeds")
    try:
        seeds = tuple(_validate_seed(value) for value in seed_values)
    except ValueError as error:
        raise FrozenPilotError(str(error)) from error
    if len(seeds) != len(set(seeds)):
        raise FrozenPilotError("v0.41.1 fresh pilot seeds are not unique")
    if seeds != selection["selected_fresh_pilot_seeds"]:
        raise FrozenPilotError("seed registry disagrees with selection receipt")
    if (
        registry.get("seed_selection_receipt_relative_path")
        != f"validation/{SELECTION_RECEIPT_NAME}"
    ):
        raise FrozenPilotError("seed registry selection-receipt path mismatch")
    if (
        registry.get("seed_selection_scan_manifest_relative_path")
        != f"validation/{SELECTION_SCAN_MANIFEST_NAME}"
        or registry.get("seed_selection_scan_manifest_sha256")
        != selection["selection_scan_manifest_sha256"]
    ):
        raise FrozenPilotError("seed registry scan-manifest binding mismatch")
    receipt_registry = selection["selection_receipt"].get("seed_registry")
    if not isinstance(receipt_registry, Mapping) or receipt_registry != {
        "relative_path": f"validation/{REGISTRY_NAME}",
        "schema": REGISTRY_SCHEMA,
        "sha256": registry_sha256,
        "registry_state": "unopened",
    }:
        raise FrozenPilotError("selection receipt seed-registry binding mismatch")

    return {
        "project_root": project_root,
        "freeze": dict(freeze),
        "freeze_path": freeze_path,
        "freeze_sha256": freeze_sha256,
        "source_sha256": normalized_source_hashes,
        "source_set_sha256": source_set_sha256,
        "source_archive_path": archive_path,
        "source_archive_sha256": archive_sha256,
        "registry": dict(registry),
        "registry_path": registry_path,
        "registry_sha256": registry_sha256,
        "fresh_pilot_seeds": seeds,
        "preexecution_validation": preexecution,
        **selection,
    }


def verify_v0411_external_commitment(
    project_root: Path,
    verified_freeze: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify the post-freeze external pre-outcome commitment record."""

    project_root = _canonical_project_root(project_root)
    path = project_root / "validation" / EXTERNAL_COMMITMENT_NAME
    checksum_path = path.with_name(f"{path.name}.sha256")
    if not path.is_file() or path.is_symlink() or not checksum_path.is_file():
        raise FileNotFoundError(
            "v0.41.1 external commitment and checksum are required before execution"
        )
    digest = _sha256_file(path)
    parts = checksum_path.read_text(encoding="utf-8").strip().split()
    if len(parts) != 2 or parts[0] != digest or Path(parts[1]).name != path.name:
        raise FrozenPilotError("external commitment checksum mismatch")
    payload = _load_json(path)
    if not isinstance(payload, Mapping):
        raise FrozenPilotError("external commitment must be a JSON object")
    required = {
        "schema": EXTERNAL_COMMITMENT_SCHEMA,
        "version": VERSION,
        "scientific_status": "external_preoutcome_commitment_complete",
        "confirmatory": False,
        "freeze_sha256": verified_freeze["freeze_sha256"],
        "scientific_source_set_sha256": verified_freeze["source_set_sha256"],
        "source_archive_sha256": verified_freeze["source_archive_sha256"],
        "seed_registry_sha256": verified_freeze["registry_sha256"],
        "seed_selection_receipt_sha256": verified_freeze["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified_freeze[
            "selection_scan_manifest_sha256"
        ],
        "outcomes_opened_before_commitment": False,
        "rows_opened_before_commitment": 0,
        "seed_condition_claims_before_commitment": 0,
    }
    for key, value in required.items():
        if payload.get(key) != value:
            raise FrozenPilotError(f"external commitment mismatch: {key}")
    persistent = payload.get("external_persistent_file")
    if not isinstance(persistent, Mapping):
        raise FrozenPilotError("external persistent-file binding is missing")
    for key in ("provider", "file_id", "version"):
        value = persistent.get(key)
        if not isinstance(value, str) or not value.strip():
            raise FrozenPilotError(f"external persistent-file {key} is missing")
    if persistent.get("immutable_or_append_only") is not True:
        raise FrozenPilotError("external commitment is not immutable/append-only")
    timestamp = persistent.get("committed_at_utc")
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise FrozenPilotError("external commitment UTC timestamp is invalid")
    try:
        datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError as error:
        raise FrozenPilotError(
            "external commitment UTC timestamp is invalid"
        ) from error
    return {
        "external_commitment": dict(payload),
        "external_commitment_path": path,
        "external_commitment_sha256": digest,
        "external_persistent_file": dict(persistent),
    }


def _verify_execution_environment(project_root: Path) -> dict[str, Any]:
    """Require the frozen single-process execution envelope before claims."""

    mismatches = {
        name: {"expected": expected, "observed": os.environ.get(name)}
        for name, expected in REQUIRED_ENVIRONMENT.items()
        if os.environ.get(name) != expected
    }
    if mismatches:
        raise FrozenPilotError(f"frozen execution environment mismatch: {mismatches}")
    flags = {
        "safe_path": bool(sys.flags.safe_path),
        "no_user_site": bool(sys.flags.no_user_site),
        "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
    }
    if not all(flags.values()) or not sys.dont_write_bytecode:
        raise FrozenPilotError(
            "runner requires python -s -P -B and disabled bytecode writes"
        )
    lock_path = project_root / "uv.lock"
    if not lock_path.is_file() or lock_path.is_symlink():
        raise FrozenPilotError("the frozen uv.lock is missing or symlinked")
    payload = {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": Path(sys.executable).resolve(strict=True).as_posix(),
        "platform": platform.platform(),
        "numpy_distribution_version": importlib.metadata.version("numpy"),
        "uv_lock_sha256": _sha256_file(lock_path),
        "environment": dict(REQUIRED_ENVIRONMENT),
        "sys_flags": flags,
        "sys_dont_write_bytecode": bool(sys.dont_write_bytecode),
    }
    payload["sha256"] = _canonical_sha256(payload)
    return payload


def _reject_preloaded_rrct_modules() -> None:
    preloaded = sorted(
        name for name in sys.modules if name == "rrct" or name.startswith("rrct.")
    )
    if preloaded:
        raise FrozenPilotError(
            "RRCT modules were preloaded before frozen source verification: "
            + ", ".join(preloaded)
        )


def _activate_verified_source(project_root: Path) -> Path:
    source_root = project_root / "src"
    resolved = source_root.resolve(strict=True)
    if source_root.absolute() != resolved or source_root.is_symlink():
        raise FrozenPilotError("verified project src must be a nonsymlink directory")
    bytecode = sorted(
        path.relative_to(project_root).as_posix()
        for path in resolved.rglob("*")
        if path.is_file() and path.suffix in {".pyc", ".pyo"}
    )
    if bytecode:
        raise FrozenPilotError(
            "verified project src contains executable bytecode artifacts: "
            + ", ".join(bytecode[:8])
        )
    filtered: list[str] = []
    for entry in sys.path:
        if not entry:
            continue
        try:
            if Path(entry).resolve(strict=False) == resolved:
                continue
        except (OSError, RuntimeError):
            pass
        filtered.append(entry)
    sys.path[:] = [resolved.as_posix(), *filtered]
    sys.path_importer_cache.clear()
    return resolved


def _rehash_source_manifest(
    project_root: Path,
    expected: Mapping[str, str],
    *,
    stage: str,
) -> None:
    for relative, digest in expected.items():
        path = _project_file(project_root, relative, f"{stage} source {relative}")
        if _sha256_file(path) != digest:
            raise FrozenPilotError(f"{stage} frozen source mismatch: {relative}")


def _verify_loaded_rrct_modules(
    project_root: Path,
    source_hashes: Mapping[str, str],
) -> dict[str, str]:
    loaded: dict[str, str] = {}
    for name, module in sorted(sys.modules.items()):
        if name != "rrct" and not name.startswith("rrct."):
            continue
        module_file = getattr(module, "__file__", None)
        if not isinstance(module_file, str) or not module_file.endswith(".py"):
            raise FrozenPilotError(
                f"loaded RRCT module has no verified .py file: {name}"
            )
        path = Path(module_file).resolve(strict=True)
        try:
            relative = path.relative_to(project_root).as_posix()
        except ValueError as error:
            raise FrozenPilotError(
                f"loaded RRCT module escaped verified project source: {name}"
            ) from error
        expected = source_hashes.get(relative)
        if expected is None:
            raise FrozenPilotError(f"loaded RRCT module is not frozen: {name}")
        if _sha256_file(path) != expected:
            raise FrozenPilotError(f"loaded RRCT module hash mismatch: {name}")
        loaded[name] = relative
    required = {
        "rrct.post_change_closure_experiment",
        "rrct.temporal_self_identity",
        "rrct.temporal_self_identity_experiment",
        "rrct.unified_causal_loop_experiment",
    }
    if not required.issubset(loaded):
        raise FrozenPilotError(
            f"required verified RRCT imports are missing: {sorted(required - set(loaded))}"
        )
    return loaded


def _canonical_campaign_root(project_root: Path) -> Path:
    project_root = _canonical_project_root(project_root)
    return project_root / "validation" / CAMPAIGN_DIRECTORY_NAME


@contextmanager
def _campaign_initialization_lock(project_root: Path) -> Any:
    lock_path = project_root / "validation" / CAMPAIGN_LOCK_NAME
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(os.fspath(lock_path), flags, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _ensure_campaign(
    project_root: Path,
    verified: Mapping[str, Any],
) -> tuple[Path, dict[str, Any]]:
    """Initialize or verify the one canonical campaign under an OS lock."""

    project_root = _canonical_project_root(project_root)
    campaign_root = _canonical_campaign_root(project_root)
    invariant = {
        "schema": CAMPAIGN_SCHEMA,
        "version": VERSION,
        "scientific_status": SCIENTIFIC_STATUS,
        "confirmatory": False,
        "canonical_campaign_root": campaign_root.relative_to(project_root).as_posix(),
        "freeze_sha256": verified["freeze_sha256"],
        "source_set_sha256": verified["source_set_sha256"],
        "source_archive_sha256": verified["source_archive_sha256"],
        "seed_registry_sha256": verified["registry_sha256"],
        "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified[
            "selection_scan_manifest_sha256"
        ],
        "external_commitment_sha256": verified["external_commitment_sha256"],
        "external_persistent_file": verified["external_persistent_file"],
        "environment_fingerprint_sha256": verified["runtime_environment_fingerprint"][
            "sha256"
        ],
        "conditions": CONDITIONS,
    }
    with _campaign_initialization_lock(project_root):
        if campaign_root.exists():
            if campaign_root.is_symlink() or not campaign_root.is_dir():
                raise FrozenPilotError(
                    "canonical campaign root exists but is not a nonsymlink directory"
                )
        else:
            campaign_root.mkdir(exist_ok=False)
            _fsync_directory(campaign_root.parent)

        receipt_path = campaign_root / "campaign_receipt.json"
        if receipt_path.exists():
            if receipt_path.is_symlink():
                raise FrozenPilotError("campaign receipt must not be a symlink")
            receipt = _load_json(receipt_path)
            if not isinstance(receipt, Mapping):
                raise FrozenPilotError("campaign receipt is not a JSON object")
            for key, value in invariant.items():
                if receipt.get(key) != value:
                    raise FrozenPilotError(f"campaign receipt mismatch: {key}")
        else:
            receipt = dict(invariant)
            receipt["created_at_utc"] = datetime.now(timezone.utc).isoformat()
            _exclusive_json(receipt_path, receipt)

        for name in ("_attempt_claims", "_seed_claims", "_condition_claims", "pairs"):
            path = campaign_root / name
            if path.exists():
                if path.is_symlink() or not path.is_dir():
                    raise FrozenPilotError(
                        f"campaign member is not a nonsymlink directory: {name}"
                    )
            else:
                path.mkdir(exist_ok=False)
                _fsync_directory(campaign_root)
    if campaign_root.resolve(strict=True) != campaign_root:
        raise FrozenPilotError("canonical campaign root resolved unexpectedly")
    return campaign_root, dict(receipt)


def _claim_condition(
    *,
    project_root: Path,
    verified: Mapping[str, Any],
    seed: int,
    condition_id: str,
    attempt_id: str,
) -> dict[str, Any]:
    """Consume one seed/condition arm before any RRCT import or RNG creation."""

    seed = _validate_seed(seed)
    if seed not in verified["fresh_pilot_seeds"]:
        raise ValueError(f"seed {seed} is not in the frozen v0.41.1 registry")
    if condition_id not in CONDITIONS:
        raise ValueError(f"unknown condition_id {condition_id!r}")
    if not isinstance(attempt_id, str) or ATTEMPT_PATTERN.fullmatch(attempt_id) is None:
        raise ValueError("attempt_id contains unsupported characters")

    campaign_root, _campaign_receipt = _ensure_campaign(project_root, verified)
    claimed_at = datetime.now(timezone.utc).isoformat()
    common = {
        "version": VERSION,
        "scientific_status": SCIENTIFIC_STATUS,
        "confirmatory": False,
        "seed": seed,
        "freeze_sha256": verified["freeze_sha256"],
        "source_set_sha256": verified["source_set_sha256"],
        "seed_registry_sha256": verified["registry_sha256"],
        "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified[
            "selection_scan_manifest_sha256"
        ],
        "external_commitment_sha256": verified["external_commitment_sha256"],
        "external_persistent_file": verified["external_persistent_file"],
        "environment_fingerprint_sha256": verified["runtime_environment_fingerprint"][
            "sha256"
        ],
    }

    attempt_path = campaign_root / "_attempt_claims" / f"{attempt_id}.json"
    attempt_claim = {
        **common,
        "schema": CLAIM_SCHEMA,
        "attempt_id": attempt_id,
        "condition_id": condition_id,
        "claimed_at_utc": claimed_at,
        "state": "consumed_before_rng_construction",
    }
    attempt_sha256 = _exclusive_json(attempt_path, attempt_claim)

    seed_path = campaign_root / "_seed_claims" / f"seed-{seed}.json"
    seed_claim_created = False
    seed_claim = {
        **common,
        "schema": SEED_CLAIM_SCHEMA,
        "first_attempt_id": attempt_id,
        "first_condition_id": condition_id,
        "claimed_at_utc": claimed_at,
        "reserved_paired_conditions": sorted(CONDITIONS),
        "state": "paired_seed_consumed_before_first_rng_construction",
    }
    try:
        seed_sha256 = _exclusive_json(seed_path, seed_claim)
        seed_claim_created = True
    except FileExistsError:
        existing = _load_json(seed_path)
        if not isinstance(existing, Mapping):
            raise FrozenPilotError("paired seed claim is not a JSON object")
        seed_invariants = {
            "schema": SEED_CLAIM_SCHEMA,
            "version": VERSION,
            "scientific_status": SCIENTIFIC_STATUS,
            "confirmatory": False,
            "seed": seed,
            "freeze_sha256": verified["freeze_sha256"],
            "source_set_sha256": verified["source_set_sha256"],
            "seed_registry_sha256": verified["registry_sha256"],
            "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
            "seed_selection_scan_manifest_sha256": verified[
                "selection_scan_manifest_sha256"
            ],
            "external_commitment_sha256": verified["external_commitment_sha256"],
            "external_persistent_file": verified["external_persistent_file"],
            "environment_fingerprint_sha256": verified[
                "runtime_environment_fingerprint"
            ]["sha256"],
            "reserved_paired_conditions": sorted(CONDITIONS),
            "state": "paired_seed_consumed_before_first_rng_construction",
        }
        for key, value in seed_invariants.items():
            if existing.get(key) != value:
                raise FrozenPilotError(f"paired seed claim mismatch: {key}")
        seed_sha256 = _sha256_file(seed_path)

    condition_claim_path = (
        campaign_root / "_condition_claims" / f"seed-{seed}--{condition_id}.json"
    )
    condition_claim = {
        **common,
        "schema": CLAIM_SCHEMA,
        "attempt_id": attempt_id,
        "condition_id": condition_id,
        "history_policy": CONDITIONS[condition_id]["history_policy"],
        "world_variant": CONDITIONS[condition_id]["world_variant"],
        "claimed_at_utc": claimed_at,
        "state": "seed_condition_consumed_before_rng_construction",
    }
    try:
        condition_claim_sha256 = _exclusive_json(
            condition_claim_path,
            condition_claim,
        )
    except FileExistsError as error:
        raise FrozenPilotError(
            f"seed {seed} condition {condition_id} was already consumed; "
            "the new attempt claim remains recorded"
        ) from error

    pair_root = campaign_root / "pairs" / f"seed-{seed}"
    try:
        pair_root.mkdir(exist_ok=False)
    except FileExistsError:
        if pair_root.is_symlink() or not pair_root.is_dir():
            raise FrozenPilotError(
                "paired seed output root is not a nonsymlink directory"
            )
    _fsync_directory(pair_root.parent)
    output_dir = pair_root / condition_id
    try:
        output_dir.mkdir(exist_ok=False)
    except FileExistsError as error:
        raise FrozenPilotError(
            "exclusive seed-condition output directory already exists; claims remain"
        ) from error
    _fsync_directory(pair_root)

    return {
        "output_dir": output_dir,
        "attempt_claim_path": attempt_path,
        "attempt_claim_sha256": attempt_sha256,
        "seed_claim_path": seed_path,
        "seed_claim_sha256": seed_sha256,
        "seed_claim_created": seed_claim_created,
        "condition_claim_path": condition_claim_path,
        "condition_claim_sha256": condition_claim_sha256,
    }


def _expected_phase(index: int) -> tuple[str, int]:
    start = 0
    for phase, count in PHASE_STEPS:
        stop = start + count
        if start <= index < stop:
            return phase, index - start
        start = stop
    raise IndexError(f"transition index {index} lies outside the frozen schedule")


def _expected_multiplier(phase: str, world_variant: str) -> float:
    if phase in {"identity_b_first", "identity_b_return"}:
        return 0.65
    if world_variant == "same_key_null_lure" and phase == "identity_a_return_two":
        return 0.0
    return 1.40


def run_frozen_condition(
    *,
    project_root: Path,
    seed: int,
    condition_id: str,
    attempt_id: str,
    progress_every: int = 480,
) -> tuple[Path, dict[str, Any]]:
    """Run one condition after verifying and consuming its frozen claim."""

    if isinstance(progress_every, bool) or not isinstance(progress_every, int):
        raise TypeError("progress_every must be a positive integer")
    if progress_every <= 0:
        raise ValueError("progress_every must be a positive integer")
    project_root = _canonical_project_root(project_root)
    runtime_environment = _verify_execution_environment(project_root)
    _reject_preloaded_rrct_modules()
    verified = verify_v0411_preoutcome_freeze(project_root)
    verified.update(verify_v0411_external_commitment(project_root, verified))
    verified["runtime_environment_fingerprint"] = runtime_environment
    campaign_root = _canonical_campaign_root(project_root)

    # This claim is intentionally complete before importing any RRCT module.
    claim = _claim_condition(
        project_root=project_root,
        verified=verified,
        seed=seed,
        condition_id=condition_id,
        attempt_id=attempt_id,
    )
    output_dir: Path = claim["output_dir"]

    _activate_verified_source(project_root)
    from rrct.temporal_self_identity import TemporalSelfIdentityConfig
    from rrct.temporal_self_identity_experiment import (
        V041_D1_CONFIG,
        V041_ROW_SCHEMA,
        V041_SUMMARY_SCHEMA,
        V041_VERSION,
        run_temporal_self_identity_trace,
    )
    from rrct.unified_causal_loop_experiment import (
        _DurableRowStream,
        _jsonl_row_bytes,
    )

    loaded_rrct_modules = _verify_loaded_rrct_modules(
        project_root,
        verified["source_sha256"],
    )
    _rehash_source_manifest(
        project_root,
        verified["source_sha256"],
        stage="post_import",
    )

    if V041_VERSION != VERSION:
        raise FrozenPilotError("executed v0.41.1 version disagrees with freeze")
    imported_phase_steps = tuple(
        (str(name), int(count)) for name, count in V041_D1_CONFIG.phase_steps
    )
    if imported_phase_steps != PHASE_STEPS:
        raise FrozenPilotError("executed v0.41.1 phase schedule disagrees with freeze")
    if int(V041_D1_CONFIG.total_steps) != EXPECTED_TRANSITION_COUNT:
        raise FrozenPilotError("executed v0.41.1 row count disagrees with freeze")

    condition = CONDITIONS[condition_id]
    temporal_config = TemporalSelfIdentityConfig(
        historical_prior_enabled=bool(condition["historical_prior_enabled"]),
        history_policy=condition["history_policy"],
    )
    if asdict(temporal_config)["history_policy"] != condition["history_policy"]:
        raise FrozenPilotError("executed history policy disagrees with freeze")
    if (
        temporal_config.historical_prior_enabled
        is not condition["historical_prior_enabled"]
    ):
        raise FrozenPilotError("executed prior switch disagrees with freeze")

    condition_payload = {
        "condition_id": condition_id,
        "temporal_identity_config": asdict(temporal_config),
        "world_variant": condition["world_variant"],
        "experiment_config": asdict(V041_D1_CONFIG),
        "phase_steps": PHASE_STEPS,
    }
    start_receipt = {
        "schema": START_SCHEMA,
        "version": VERSION,
        "scientific_status": SCIENTIFIC_STATUS,
        "confirmatory": False,
        "freeze_bound": True,
        "seed": seed,
        "condition_id": condition_id,
        "attempt_id": attempt_id,
        "history_policy": condition["history_policy"],
        "historical_prior_enabled": condition["historical_prior_enabled"],
        "world_variant": condition["world_variant"],
        "expected_transition_count": EXPECTED_TRANSITION_COUNT,
        "expected_phase_counts": dict(PHASE_STEPS),
        "condition_config_sha256": _canonical_sha256(condition_payload),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "freeze_sha256": verified["freeze_sha256"],
        "source_sha256": verified["source_sha256"],
        "source_set_sha256": verified["source_set_sha256"],
        "source_archive_relative_path": verified["freeze"]["source_archive"][
            "relative_path"
        ],
        "source_archive_sha256": verified["source_archive_sha256"],
        "seed_registry_sha256": verified["registry_sha256"],
        "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified[
            "selection_scan_manifest_sha256"
        ],
        "external_commitment_sha256": verified["external_commitment_sha256"],
        "external_persistent_file": verified["external_persistent_file"],
        "verified_rrct_module_paths": loaded_rrct_modules,
        "post_import_source_manifest_reverified": True,
        "post_import_loaded_rrct_modules_reverified": True,
        "claims": {
            "attempt_relative_path": claim["attempt_claim_path"]
            .relative_to(campaign_root)
            .as_posix(),
            "attempt_sha256": claim["attempt_claim_sha256"],
            "seed_relative_path": claim["seed_claim_path"]
            .relative_to(campaign_root)
            .as_posix(),
            "seed_sha256": claim["seed_claim_sha256"],
            "seed_claim_created_by_this_arm": claim["seed_claim_created"],
            "condition_relative_path": claim["condition_claim_path"]
            .relative_to(campaign_root)
            .as_posix(),
            "condition_sha256": claim["condition_claim_sha256"],
            "all_claims_precede_rng_construction": True,
        },
        "environment_fingerprint": runtime_environment,
        "row_serialization": {
            "json_sort_keys": True,
            "json_separators": [",", ":"],
            "allow_nan": False,
            "line_ending": "LF",
            "fsync_each_row": True,
        },
        "success_semantics": ("integrity_complete_independent_of_scientific_endpoints"),
    }
    start_sha256 = _exclusive_json(output_dir / START_NAME, start_receipt)

    stream = _DurableRowStream(output_dir / ROWS_NAME)
    phase_counts = {name: 0 for name, _count in PHASE_STEPS}
    try:

        def sink(row: Mapping[str, Any]) -> None:
            index = stream.row_count
            if row.get("schema") != V041_ROW_SCHEMA:
                raise FrozenPilotError(f"row {index} has the wrong v0.41 schema")
            if int(row.get("seed", -1)) != seed:
                raise FrozenPilotError(f"row {index} has the wrong seed")
            if int(row.get("transition_index", -1)) != index:
                raise FrozenPilotError(f"row {index} breaks transition order")
            expected_phase, expected_offset = _expected_phase(index)
            if row.get("phase") != expected_phase:
                raise FrozenPilotError(f"row {index} has the wrong phase")
            if int(row.get("phase_offset", -1)) != expected_offset:
                raise FrozenPilotError(f"row {index} has the wrong phase offset")
            if row.get("history_policy") != condition["history_policy"]:
                raise FrozenPilotError(f"row {index} has the wrong history policy")
            if row.get("world_variant_evaluator_only") != condition["world_variant"]:
                raise FrozenPilotError(f"row {index} has the wrong world variant")
            multiplier = float(
                row.get("task_return_multiplier_evaluator_only", float("nan"))
            )
            if multiplier != _expected_multiplier(
                expected_phase,
                condition["world_variant"],
            ):
                raise FrozenPilotError(
                    f"row {index} has the wrong task-return multiplier"
                )
            mandatory_integrity = (
                "hard_integrity_valid",
                "v039_wrapper_integrity",
                "v040_wrapper_integrity",
                "v041_wrapper_integrity",
                "temporal_action_gate_binding_valid",
                "runtime_identity_ok",
            )
            if not all(bool(row.get(name)) for name in mandatory_integrity):
                raise FrozenPilotError(
                    f"row {index} failed a mandatory integrity check"
                )
            if int(row.get("reset_count", -1)) != 0:
                raise FrozenPilotError(f"row {index} records a runtime reset")
            if bool(row.get("evaluator_truth_leak")):
                raise FrozenPilotError(f"row {index} records evaluator-truth leakage")
            phase_counts[expected_phase] += 1
            stream.append(row)
            if stream.row_count % progress_every == 0:
                print(
                    f"condition={condition_id} seed={seed} "
                    f"rows={stream.row_count}/{EXPECTED_TRANSITION_COUNT} "
                    f"phase={expected_phase} offset={expected_offset}",
                    flush=True,
                )

        completed_rows, engine_summary = run_temporal_self_identity_trace(
            seed,
            temporal_identity_config=temporal_config,
            world_variant=condition["world_variant"],
            sealed_row_sink=sink,
        )
        stream.close()

        if stream.row_count != EXPECTED_TRANSITION_COUNT:
            raise FrozenPilotError("durable row stream has the wrong row count")
        if len(completed_rows) != EXPECTED_TRANSITION_COUNT:
            raise FrozenPilotError("returned trace has the wrong row count")
        if phase_counts != dict(PHASE_STEPS):
            raise FrozenPilotError("durable row stream has the wrong phase counts")
        returned_digest = hashlib.sha256()
        for row in completed_rows:
            returned_digest.update(_jsonl_row_bytes(row))
        if returned_digest.hexdigest() != stream.sha256:
            raise FrozenPilotError("returned rows disagree with durable rows")
        if _sha256_file(output_dir / ROWS_NAME) != stream.sha256:
            raise FrozenPilotError("durable row file hash changed")

        if engine_summary.get("schema") != V041_SUMMARY_SCHEMA:
            raise FrozenPilotError("run summary has the wrong schema")
        if engine_summary.get("version") != VERSION:
            raise FrozenPilotError("run summary has the wrong version")
        if int(engine_summary.get("seed", -1)) != seed:
            raise FrozenPilotError("run summary has the wrong seed")
        summary_condition = engine_summary.get("condition")
        if not isinstance(summary_condition, Mapping):
            raise FrozenPilotError("run summary has no condition mapping")
        if summary_condition.get("history_policy") != condition["history_policy"]:
            raise FrozenPilotError("run summary has the wrong history policy")
        if summary_condition.get("world_variant") != condition["world_variant"]:
            raise FrozenPilotError("run summary has the wrong world variant")
        summary_schedule = [
            [str(name), int(count)]
            for name, count in engine_summary.get("schedule", ())
        ]
        if summary_schedule != [[name, count] for name, count in PHASE_STEPS]:
            raise FrozenPilotError("run summary has the wrong schedule")
        for label, integrity in (
            ("summary", engine_summary.get("integrity")),
            (
                "engine summary",
                engine_summary.get("engine_summary", {}).get("integrity"),
            ),
        ):
            if not isinstance(integrity, Mapping) or not integrity:
                raise FrozenPilotError(f"{label} has no integrity section")
            if not all(bool(value) for value in integrity.values()):
                raise FrozenPilotError(f"{label} reports an integrity failure")
        if bool(
            engine_summary.get("temporal_identity", {}).get("historical_prior_enabled")
        ) != bool(condition["historical_prior_enabled"]):
            raise FrozenPilotError("run summary has the wrong prior switch")

        _rehash_source_manifest(
            project_root,
            verified["source_sha256"],
            stage="post_run",
        )
        _verify_loaded_rrct_modules(project_root, verified["source_sha256"])

        scientific_all_endpoints_met = bool(engine_summary.get("all_endpoints_met"))
        summary = copy.deepcopy(engine_summary)
        summary["development_summary_status"] = engine_summary.get("status")
        summary["scientific_status"] = SCIENTIFIC_STATUS
        summary["confirmatory"] = False
        summary["status"] = (
            "V0411_FROZEN_EXPLORATORY_PILOT_CONDITION_ENDPOINTS_MET"
            if scientific_all_endpoints_met
            else "V0411_FROZEN_EXPLORATORY_PILOT_CONDITION_ENDPOINTS_NOT_MET"
        )
        summary["frozen_pilot"] = {
            "attempt_id": attempt_id,
            "condition_id": condition_id,
            "freeze_sha256": verified["freeze_sha256"],
            "source_set_sha256": verified["source_set_sha256"],
            "source_archive_sha256": verified["source_archive_sha256"],
            "seed_registry_sha256": verified["registry_sha256"],
            "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
            "seed_selection_scan_manifest_sha256": verified[
                "selection_scan_manifest_sha256"
            ],
            "external_commitment_sha256": verified["external_commitment_sha256"],
            "external_persistent_file": verified["external_persistent_file"],
            "environment_fingerprint_sha256": runtime_environment["sha256"],
            "post_run_source_manifest_reverified": True,
            "post_run_loaded_rrct_modules_reverified": True,
            "post_run_source_set_sha256": verified["source_set_sha256"],
            "rows_count": stream.row_count,
            "rows_sha256": stream.sha256,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "scientific_failure_preserved": not scientific_all_endpoints_met,
        }
        summary_sha256 = _exclusive_json(output_dir / SUMMARY_NAME, summary)

        finish_receipt = {
            "schema": FINISH_SCHEMA,
            "version": VERSION,
            "scientific_status": SCIENTIFIC_STATUS,
            "confirmatory": False,
            "freeze_bound": True,
            "seed": seed,
            "condition_id": condition_id,
            "attempt_id": attempt_id,
            "history_policy": condition["history_policy"],
            "world_variant": condition["world_variant"],
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "freeze_sha256": verified["freeze_sha256"],
            "source_set_sha256": verified["source_set_sha256"],
            "seed_registry_sha256": verified["registry_sha256"],
            "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
            "seed_selection_scan_manifest_sha256": verified[
                "selection_scan_manifest_sha256"
            ],
            "external_commitment_sha256": verified["external_commitment_sha256"],
            "external_persistent_file": verified["external_persistent_file"],
            "environment_fingerprint_sha256": runtime_environment["sha256"],
            "post_run_source_manifest_reverified": True,
            "post_run_loaded_rrct_modules_reverified": True,
            "post_run_source_set_sha256": verified["source_set_sha256"],
            "start_receipt_sha256": start_sha256,
            "rows_count": stream.row_count,
            "rows_sha256": stream.sha256,
            "summary_sha256": summary_sha256,
            "integrity_complete": True,
            "scientific_all_endpoints_met": scientific_all_endpoints_met,
            "scientific_failure_preserved": not scientific_all_endpoints_met,
            "status": "V0411_FROZEN_PILOT_CONDITION_INTEGRITY_COMPLETE",
        }
        finish_sha256 = _exclusive_json(
            output_dir / FINISH_NAME,
            finish_receipt,
        )
        artifact_hashes = {
            START_NAME: _sha256_file(output_dir / START_NAME),
            ROWS_NAME: _sha256_file(output_dir / ROWS_NAME),
            SUMMARY_NAME: _sha256_file(output_dir / SUMMARY_NAME),
            FINISH_NAME: _sha256_file(output_dir / FINISH_NAME),
        }
        expected_hashes = {
            START_NAME: start_sha256,
            ROWS_NAME: stream.sha256,
            SUMMARY_NAME: summary_sha256,
            FINISH_NAME: finish_sha256,
        }
        if artifact_hashes != expected_hashes:
            raise FrozenPilotError("artifact hashes changed before manifest creation")
        _exclusive_json(output_dir / ARTIFACT_NAME, artifact_hashes)
        return output_dir, summary
    except BaseException as error:
        stream_close_error: dict[str, str] | None = None
        try:
            stream.close()
        except (OSError, RuntimeError) as close_error:
            stream_close_error = {
                "exception_type": type(close_error).__name__,
                "exception_message": str(close_error),
            }
        failure_receipt = {
            "schema": FAILURE_SCHEMA,
            "version": VERSION,
            "scientific_status": SCIENTIFIC_STATUS,
            "confirmatory": False,
            "seed": seed,
            "condition_id": condition_id,
            "attempt_id": attempt_id,
            "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            "freeze_sha256": verified["freeze_sha256"],
            "source_set_sha256": verified["source_set_sha256"],
            "seed_registry_sha256": verified["registry_sha256"],
            "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
            "seed_selection_scan_manifest_sha256": verified[
                "selection_scan_manifest_sha256"
            ],
            "external_commitment_sha256": verified["external_commitment_sha256"],
            "external_persistent_file": verified["external_persistent_file"],
            "environment_fingerprint_sha256": runtime_environment["sha256"],
            "exception_type": type(error).__name__,
            "exception_message": str(error),
            "rows_count": stream.row_count,
            "rows_sha256": stream.sha256,
            "partial_rows_preserved": (output_dir / ROWS_NAME).is_file(),
            "stream_close_error": stream_close_error,
            "status": "V0411_FROZEN_PILOT_CONDITION_EXECUTION_FAILED",
        }
        try:
            _exclusive_json(output_dir / FAILURE_NAME, failure_receipt)
        except (OSError, TypeError, ValueError) as receipt_error:
            error.add_note(
                "failure receipt publication also failed: "
                f"{type(receipt_error).__name__}: {receipt_error}"
            )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run one freeze-bound condition of the v0.41.1 paired "
            "exploratory pilot matrix."
        )
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition-id", choices=tuple(CONDITIONS), required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--progress-every", type=int, default=480)
    args = parser.parse_args()
    output, summary = run_frozen_condition(
        project_root=args.project_root,
        seed=args.seed,
        condition_id=args.condition_id,
        attempt_id=args.attempt_id,
        progress_every=args.progress_every,
    )
    print(
        json.dumps(
            {
                "output": output.as_posix(),
                "seed": summary["seed"],
                "condition_id": args.condition_id,
                "status": summary["status"],
                "scientific_status": summary["scientific_status"],
                "confirmatory": summary["confirmatory"],
                "all_endpoints_met": summary["all_endpoints_met"],
            },
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
