"""Create the exclusive, deterministic RRCT v0.41.1 pre-outcome freeze.

This program deliberately does not choose, claim, or open a fresh seed.  It
only validates and binds an already-created *unopened* seed registry together
with the complete scientific source surface needed by the v0.41.1 fresh-pilot
campaign.  Missing inputs and any evidence that the registry was opened are
hard failures that occur before an archive or freeze record is written.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import tarfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

VERSION = "0.41.1.dev2"
FREEZE_SCHEMA = "rrct.v0411.preoutcome_freeze.v1"
REGISTRY_SCHEMA = "rrct.v0411.seed_registry.v1"
SCAN_SCHEMA = "rrct.v0411.seed_selection_scan_manifest.v1"
RECEIPT_SCHEMA = "rrct.v0411.seed_selection_receipt.v1"
PREEXECUTION_SCHEMA = "rrct.v0411.preexecution_validation.v1"
FREEZE_NAME = "V0_41_1_PREOUTCOME_FREEZE.json"
FREEZE_CHECKSUM_NAME = f"{FREEZE_NAME}.sha256"
ARCHIVE_PREFIX = "V0_41_1_EXECUTED_SOURCE_"
TEMP_ARCHIVE_NAME = f".{ARCHIVE_PREFIX}tmp.tar.gz"

EXPECTED_CONDITIONS = (
    "G_RMINUS",
    "G_RPLUS",
    "K_RMINUS",
    "K_RPLUS",
    "N_RMINUS",
    "N_RPLUS",
)

PRODUCTION_SOURCE_PATHS = (
    "src/rrct/post_change_closure_experiment.py",
    "src/rrct/temporal_self_identity.py",
    "src/rrct/temporal_self_identity_experiment.py",
)

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

REQUIRED_ENVIRONMENT = {
    "environment": {
        "PYTHONHASHSEED": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
    },
    "python_flags": {
        "safe_path": True,
        "no_user_site": True,
        "dont_write_bytecode": True,
    },
}

# Exact non-discoverable campaign inputs.  src/rrct and tests are added below
# by discovery so that newly added Python modules/tests cannot silently escape
# the freeze.
REQUIRED_RELATIVE_PATHS = (
    "pyproject.toml",
    "uv.lock",
    "MANIFEST.in",
    "validation/V0_41_1_CRITICAL_PATH_MATRIX_PROTOCOL.md",
    "validation/V0_41_1_FRESH_PILOT_PROTOCOL.md",
    "validation/V0_41_1_DEVELOPMENT_CONDITIONS.json",
    "validation/V0_41_1_PRIOR_HANDSHAKE_INCIDENT.md",
    "validation/V0_41_1_SEED_REGISTRY.json",
    "validation/V0_41_1_PREEXECUTION_VALIDATION.json",
    "validation/V0_41_1_DEVELOPMENT_AUDIT.json",
    "validation/V0_41_1_DEVELOPMENT_REPORT.md",
    "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json",
    "validation/V0_41_1_SEED_SELECTION_RECEIPT.json",
    "validation/audit_v041_development_integrity.py",
    "validation/audit_v041_development_matrix.py",
    "validation/audit_v041_campaign.py",
    "validation/run_v041_development_condition.py",
    "validation/run_v041_frozen_seed.py",
    "validation/select_v0411_seeds.py",
    "validation/summarize_v041_sealed_rows.py",
    "validation/freeze_v0411_source.py",
    "tests/test_v041_temporal_self_identity.py",
    "tests/test_v041_critical_path.py",
    "tests/test_v041_frozen_seed_runner.py",
    "tests/test_v041_freeze_source.py",
    "tests/test_v0411_seed_selector.py",
    "tests/test_v041_campaign_auditor.py",
    "validation/v0.41.1_development_matrix_seed_41011/integrity_yoking_audit.json",
    "validation/v0.41.1_development_matrix_seed_41011/independent_science_audit.json",
    "validation/v0.41.1_development_matrix_seed_41011/G_RMINUS/summary.json",
    "validation/v0.41.1_development_matrix_seed_41011/G_RPLUS/summary.json",
    "validation/v0.41.1_development_matrix_seed_41011/K_RMINUS/summary.json",
    "validation/v0.41.1_development_matrix_seed_41011/K_RPLUS/summary.json",
    "validation/v0.41.1_development_matrix_seed_41011/N_RMINUS/summary.json",
    "validation/v0.41.1_development_matrix_seed_41011/N_RPLUS/summary.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label} JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be a JSON object: {path}")
    return value


def _condition_matrix(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "validation/V0_41_1_DEVELOPMENT_CONDITIONS.json"
    registry = _read_json_object(path, "development condition registry")
    if registry.get("schema") != "rrct.v0411.development_condition_registry.v1":
        raise ValueError("unexpected development condition registry schema")
    if registry.get("version") != VERSION:
        raise ValueError(
            "development condition registry version must be "
            f"{VERSION!r}, got {registry.get('version')!r}"
        )
    if registry.get("scientific_status") != "exposed_development_only_not_frozen":
        raise ValueError("unexpected development condition registry scientific_status")
    if registry.get("development_seed") != 41011:
        raise ValueError("development condition registry seed must be 41011")
    conditions = registry.get("conditions")
    if not isinstance(conditions, dict):
        raise TypeError("development condition registry conditions must be an object")
    if tuple(sorted(conditions)) != EXPECTED_CONDITIONS:
        raise ValueError(
            "development condition registry must contain exactly "
            f"{list(EXPECTED_CONDITIONS)!r}, got {sorted(conditions)!r}"
        )
    for name, specification in conditions.items():
        if not isinstance(specification, dict):
            raise TypeError(f"condition {name!r} must be an object")
    # Round-trip through JSON so no caller can mutate the parsed registry.
    return json.loads(json.dumps(conditions, allow_nan=False, sort_keys=True))


def _validate_unopened_seed_registry(
    root: Path, condition_matrix: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    path = root / "validation/V0_41_1_SEED_REGISTRY.json"
    registry = _read_json_object(path, "seed registry")
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise ValueError(
            f"seed registry schema must be {REGISTRY_SCHEMA!r}, "
            f"got {registry.get('schema')!r}"
        )
    if registry.get("version") != VERSION:
        raise ValueError(
            f"seed registry version must be {VERSION!r}, "
            f"got {registry.get('version')!r}"
        )
    if registry.get("registry_state") != "unopened":
        raise ValueError("seed registry must have registry_state='unopened'")
    if registry.get("cohort_opened") is not False:
        raise ValueError("seed registry must have cohort_opened=false")
    opened_pairs = registry.get("opened_seed_condition_pairs")
    if opened_pairs != []:
        raise ValueError("opened_seed_condition_pairs must be an empty list")

    seeds = registry.get("fresh_pilot_seeds")
    if not isinstance(seeds, list) or len(seeds) != 4:
        raise ValueError("fresh_pilot_seeds must contain exactly four values")
    if any(
        isinstance(seed, bool) or not isinstance(seed, int) or seed <= 0
        for seed in seeds
    ):
        raise ValueError("fresh_pilot_seeds must contain only positive integers")
    if len(seeds) != len(set(seeds)):
        raise ValueError("fresh_pilot_seeds must be unique")

    registry_conditions = registry.get("conditions")
    if registry_conditions != dict(condition_matrix):
        raise ValueError(
            "seed registry conditions must exactly equal the frozen development "
            "condition matrix"
        )
    return registry


def _validate_seed_selection_artifacts(
    root: Path,
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    scan_path = root / "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
    receipt_path = root / "validation/V0_41_1_SEED_SELECTION_RECEIPT.json"
    selector_path = root / "validation/select_v0411_seeds.py"
    scan = _read_json_object(scan_path, "seed-selection scan manifest")
    receipt = _read_json_object(receipt_path, "seed-selection receipt")
    if scan.get("schema") != SCAN_SCHEMA or scan.get("version") != VERSION:
        raise ValueError("unexpected seed-selection scan manifest schema/version")
    if scan.get("scientific_status") != "pre_registry_complete_project_evidence_scan":
        raise ValueError("unexpected seed-selection scan scientific_status")
    files = scan.get("files")
    if not isinstance(files, list) or not files or scan.get("file_count") != len(files):
        raise ValueError("seed-selection scan file inventory is invalid")
    if scan.get("scan_surface_sha256") != _canonical_sha256(files):
        raise ValueError("seed-selection scan-surface digest mismatch")

    exact_receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "scientific_status": "preoutcome_seed_selection_complete_unopened",
        "selection_method": "single_nonrepeated_secrets_randbelow_draw_loop",
        "draw_expression": "secrets.randbelow(800_000_000) + 100_000_000",
        "candidate_count": 12,
        "scan_rule": "standalone_decimal_occurrences_not_adjacent_to_ascii_digits",
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
            raise ValueError(f"seed-selection receipt mismatch: {key}")
    candidates = receipt.get("candidate_generation_order")
    records = receipt.get("candidate_scan_records")
    if (
        not isinstance(candidates, list)
        or len(candidates) != 12
        or len(set(candidates)) != 12
        or any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 100_000_000 <= value <= 899_999_999
            for value in candidates
        )
        or not isinstance(records, list)
        or len(records) != 12
    ):
        raise ValueError("seed-selection candidate inventory is invalid")
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
        raise ValueError("seed-selection draw accounting is invalid")
    zero_candidates: list[int] = []
    for index, (candidate, record) in enumerate(zip(candidates, records)):
        if not isinstance(record, dict):
            raise TypeError("seed-selection candidate record is not an object")
        count = record.get("standalone_decimal_occurrence_count")
        paths = record.get("occurrence_paths")
        if (
            record.get("generation_index") != index
            or record.get("candidate") != candidate
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count < 0
            or not isinstance(paths, list)
            or any(not isinstance(path, str) for path in paths)
            or len(paths) != count
            or record.get("zero_occurrence") is not (count == 0)
        ):
            raise ValueError("seed-selection candidate record is invalid")
        if count == 0:
            zero_candidates.append(candidate)
    selected = receipt.get("selected_fresh_pilot_seeds")
    if selected != zero_candidates[:4] or selected != registry["fresh_pilot_seeds"]:
        raise ValueError("seed-selection first-four derivation disagrees with registry")

    scan_sha256 = _sha256(scan_path)
    registry_sha256 = _sha256(root / "validation/V0_41_1_SEED_REGISTRY.json")
    if receipt.get("scan_manifest") != {
        "relative_path": "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json",
        "schema": SCAN_SCHEMA,
        "sha256": scan_sha256,
        "file_count": len(files),
        "scan_surface_sha256": scan["scan_surface_sha256"],
    }:
        raise ValueError("seed-selection receipt scan-manifest binding mismatch")
    if receipt.get("seed_registry") != {
        "relative_path": "validation/V0_41_1_SEED_REGISTRY.json",
        "schema": REGISTRY_SCHEMA,
        "sha256": registry_sha256,
        "registry_state": "unopened",
    }:
        raise ValueError("seed-selection receipt registry binding mismatch")
    selector = receipt.get("selector")
    if selector != {
        "relative_path": "validation/select_v0411_seeds.py",
        "sha256": _sha256(selector_path),
    }:
        raise ValueError("seed-selection receipt selector binding mismatch")
    if (
        registry.get("seed_selection_receipt_relative_path")
        != "validation/V0_41_1_SEED_SELECTION_RECEIPT.json"
        or registry.get("seed_selection_scan_manifest_relative_path")
        != "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
        or registry.get("seed_selection_scan_manifest_sha256") != scan_sha256
    ):
        raise ValueError("seed registry selection-artifact binding mismatch")
    return {
        "scan_path": scan_path,
        "scan_sha256": scan_sha256,
        "receipt_path": receipt_path,
        "receipt_sha256": _sha256(receipt_path),
    }


def _validate_development_audits(root: Path) -> None:
    canonical_path = root / "validation/V0_41_1_DEVELOPMENT_AUDIT.json"
    independent_path = (
        root
        / "validation/v0.41.1_development_matrix_seed_41011/independent_science_audit.json"
    )
    canonical = _read_json_object(canonical_path, "canonical development audit")
    independent = _read_json_object(independent_path, "independent science audit")
    if canonical_path.read_bytes() != independent_path.read_bytes():
        raise ValueError(
            "V0_41_1_DEVELOPMENT_AUDIT.json must be an exact byte copy of "
            "the independent science audit"
        )
    expected_schema = "rrct.v041.development_matrix.independent_audit.v1"
    for label, audit in (("canonical", canonical), ("independent", independent)):
        if audit.get("schema") != expected_schema:
            raise ValueError(
                f"{label} development audit schema must be {expected_schema!r}"
            )
        if audit.get("all_criteria_met") is not True:
            raise ValueError(
                f"{label} development audit must have all_criteria_met=true"
            )
        if audit.get("development_only") is not True:
            raise ValueError(
                f"{label} development audit must have development_only=true"
            )
        if audit.get("seed") != 41011:
            raise ValueError(f"{label} development audit seed must be 41011")

    integrity_path = (
        root
        / "validation/v0.41.1_development_matrix_seed_41011/integrity_yoking_audit.json"
    )
    integrity = _read_json_object(integrity_path, "development integrity audit")
    if integrity.get("schema") != "rrct.v041.development_integrity_yoking_audit.v1":
        raise ValueError("unexpected development integrity audit schema")
    if integrity.get("all_checks_pass") is not True:
        raise ValueError("development integrity audit must have all_checks_pass=true")
    if integrity.get("development_only") is not True:
        raise ValueError("development integrity audit must have development_only=true")
    if integrity.get("seed") != 41011:
        raise ValueError("development integrity audit seed must be 41011")


def _validate_preexecution_record(root: Path) -> dict[str, Any]:
    path = root / "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
    record = _read_json_object(path, "preexecution validation")
    exact = {
        "schema": PREEXECUTION_SCHEMA,
        "version": VERSION,
        "scientific_status": "preoutcome_all_checks_pass",
        "all_checks_pass": True,
        "cohort_opened": False,
        "fresh_seed_state": "unopened",
        "errors": [],
        "failures": [],
        "failed_checks": [],
        "required_environment": REQUIRED_ENVIRONMENT,
    }
    for key, value in exact.items():
        if record.get(key) != value:
            raise ValueError(f"preexecution validation mismatch: {key}")
    checks = record.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(REQUIRED_PREEXECUTION_CHECKS):
        raise ValueError("preexecution validation has the wrong exact checklist")
    if any(checks[key] is not True for key in REQUIRED_PREEXECUTION_CHECKS):
        raise ValueError("every preexecution checklist item must be literal true")
    command = record.get("test_command")
    if not isinstance(command, str) or not command.strip():
        raise ValueError("preexecution validation test_command is missing")
    passed = record.get("passed_test_count")
    if isinstance(passed, bool) or not isinstance(passed, int) or passed <= 0:
        raise ValueError("preexecution validation passed_test_count must be positive")
    dependency_digest = record.get("dependency_lock_sha256")
    if dependency_digest != _sha256(root / "uv.lock"):
        raise ValueError("preexecution dependency-lock digest mismatch")
    production_hashes = record.get("production_source_sha256")
    expected_hashes = {
        relative: _sha256(root / relative) for relative in PRODUCTION_SOURCE_PATHS
    }
    if production_hashes != expected_hashes:
        raise ValueError("preexecution production-source hashes mismatch")
    if record.get("production_source_set_sha256") != _canonical_sha256(expected_hashes):
        raise ValueError("preexecution production source-set digest mismatch")
    return record


def _source_paths(root: Path) -> tuple[Path, ...]:
    required = tuple(root / relative for relative in REQUIRED_RELATIVE_PATHS)
    missing = [path for path in required if not path.is_file()]
    if missing:
        names = ", ".join(path.relative_to(root).as_posix() for path in missing)
        raise FileNotFoundError(f"missing v0.41.1 freeze inputs: {names}")

    source_root = root / "src/rrct"
    tests_root = root / "tests"
    executable_bytecode = sorted(
        path.relative_to(root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file() and path.suffix in {".pyc", ".pyo"}
    )
    if executable_bytecode:
        raise ValueError(
            "src/rrct contains executable bytecode artifacts that must be removed "
            "before freeze: " + ", ".join(executable_bytecode[:8])
        )
    discovered = [
        *sorted(source_root.rglob("*.py")),
        *sorted(tests_root.rglob("*.py")),
        *sorted((tests_root / "fixtures").rglob("*")),
    ]
    source_python = [
        path
        for path in discovered
        if path.is_file()
        and path.suffix == ".py"
        and "__pycache__" not in path.parts
        and source_root in path.parents
    ]
    if not source_python:
        raise FileNotFoundError("src/rrct must contain at least one Python source file")

    paths = {
        path.resolve()
        for path in (*required, *discovered)
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    }
    return tuple(sorted(paths, key=lambda path: path.relative_to(root).as_posix()))


def _write_deterministic_archive(
    root: Path, paths: tuple[Path, ...], destination: Path
) -> None:
    with (
        destination.open("xb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped,
        tarfile.open(fileobj=zipped, mode="w", format=tarfile.USTAR_FORMAT) as archive,
    ):
        for path in paths:
            data = path.read_bytes()
            info = tarfile.TarInfo(path.relative_to(root).as_posix())
            info.size = len(data)
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            info.type = tarfile.REGTYPE
            archive.addfile(info, io.BytesIO(data))
        raw.flush()
        os.fsync(raw.fileno())


def _archived_source_hashes(path: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    with tarfile.open(path, mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                raise RuntimeError(f"non-file source archive member: {member.name}")
            if member.name in hashes:
                raise RuntimeError(f"duplicate source archive member: {member.name}")
            extracted = archive.extractfile(member)
            if extracted is None:
                raise RuntimeError(f"unreadable source archive member: {member.name}")
            digest = hashlib.sha256()
            for chunk in iter(lambda handle=extracted: handle.read(1 << 20), b""):
                digest.update(chunk)
            hashes[member.name] = digest.hexdigest()
    return hashes


def _write_exclusive_text(path: Path, value: str) -> None:
    descriptor = os.open(os.fspath(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        remaining = memoryview(value.encode("utf-8"))
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise OSError(f"exclusive write made no progress: {path}")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(os.fspath(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _assert_output_space_is_unused(validation: Path) -> None:
    freeze = validation / FREEZE_NAME
    checksum = validation / FREEZE_CHECKSUM_NAME
    temporary = validation / TEMP_ARCHIVE_NAME
    existing_archives = sorted(validation.glob(f"{ARCHIVE_PREFIX}*.tar.gz"))
    conflicts = [path for path in (freeze, checksum, temporary) if path.exists()]
    conflicts.extend(existing_archives)
    if conflicts:
        names = ", ".join(path.name for path in conflicts)
        raise FileExistsError(
            f"v0.41.1 pre-outcome freeze output already exists: {names}"
        )


def create_freeze(project_root: Path) -> dict[str, Any]:
    """Validate all inputs and create one immutable pre-outcome freeze."""

    root = project_root.resolve()
    validation = root / "validation"
    if not validation.is_dir():
        raise FileNotFoundError(f"validation directory does not exist: {validation}")

    _assert_output_space_is_unused(validation)
    paths = _source_paths(root)
    conditions = _condition_matrix(root)
    registry = _validate_unopened_seed_registry(root, conditions)
    selection = _validate_seed_selection_artifacts(root, registry)
    _validate_development_audits(root)
    preexecution = _validate_preexecution_record(root)

    # All semantically meaningful failures above occur before the first write.
    source_hashes = {path.relative_to(root).as_posix(): _sha256(path) for path in paths}
    temporary_archive = validation / TEMP_ARCHIVE_NAME
    _write_deterministic_archive(root, paths, temporary_archive)
    if _archived_source_hashes(temporary_archive) != source_hashes:
        raise RuntimeError(
            "source changed while the deterministic archive was being written; "
            "temporary archive preserved as a fail-closed incident"
        )
    archive_sha256 = _sha256(temporary_archive)
    archive = validation / f"{ARCHIVE_PREFIX}{archive_sha256[:16]}.tar.gz"
    # A hard link is an atomic no-replace publication within validation/.
    # A failed publication preserves the temporary archive as a visible,
    # fail-closed incident.
    os.link(temporary_archive, archive)
    temporary_archive.unlink()
    _fsync_directory(validation)

    seed_registry_path = validation / "V0_41_1_SEED_REGISTRY.json"
    payload: dict[str, Any] = {
        "schema": FREEZE_SCHEMA,
        "version": VERSION,
        "scientific_status": "fresh_pilot_temporal_identity_preoutcome_freeze",
        "campaign_stage": "fresh_pilot",
        "confirmatory": False,
        "scientific_source_sha256": source_hashes,
        "scientific_source_set_sha256": _canonical_sha256(source_hashes),
        "source_archive": {
            "relative_path": archive.relative_to(root).as_posix(),
            "sha256": archive_sha256,
            "member_count": len(paths),
            "format": "ustar+gzip",
            "member_mtime": 0,
            "gzip_mtime": 0,
        },
        "seed_registry": {
            "relative_path": seed_registry_path.relative_to(root).as_posix(),
            "sha256": _sha256(seed_registry_path),
            "schema": REGISTRY_SCHEMA,
            "registry_state_at_freeze": "unopened",
        },
        "seed_registry_sha256": _sha256(seed_registry_path),
        "seed_selection_scan_manifest": {
            "relative_path": selection["scan_path"].relative_to(root).as_posix(),
            "sha256": selection["scan_sha256"],
            "schema": SCAN_SCHEMA,
        },
        "seed_selection_scan_manifest_sha256": selection["scan_sha256"],
        "seed_selection_receipt": {
            "relative_path": selection["receipt_path"].relative_to(root).as_posix(),
            "sha256": selection["receipt_sha256"],
            "schema": RECEIPT_SCHEMA,
            "selection_state_at_freeze": "unopened",
        },
        "seed_selection_receipt_sha256": selection["receipt_sha256"],
        "fresh_seed_state_at_freeze": "unopened",
        "cohort_opened_at_freeze": False,
        "condition_matrix": conditions,
        "condition_names": list(EXPECTED_CONDITIONS),
        "development_protocol_sha256": _sha256(
            validation / "V0_41_1_CRITICAL_PATH_MATRIX_PROTOCOL.md"
        ),
        "fresh_pilot_protocol_sha256": _sha256(
            validation / "V0_41_1_FRESH_PILOT_PROTOCOL.md"
        ),
        "protocol_sha256": _sha256(validation / "V0_41_1_FRESH_PILOT_PROTOCOL.md"),
        "development_conditions_sha256": _sha256(
            validation / "V0_41_1_DEVELOPMENT_CONDITIONS.json"
        ),
        "preexecution_validation_sha256": _sha256(
            validation / "V0_41_1_PREEXECUTION_VALIDATION.json"
        ),
        "preexecution_validation": {
            "relative_path": "validation/V0_41_1_PREEXECUTION_VALIDATION.json",
            "schema": PREEXECUTION_SCHEMA,
            "sha256": _sha256(validation / "V0_41_1_PREEXECUTION_VALIDATION.json"),
            "scientific_status": preexecution["scientific_status"],
            "all_checks_pass": True,
        },
        "required_environment": REQUIRED_ENVIRONMENT,
        "development_audit_sha256": _sha256(
            validation / "V0_41_1_DEVELOPMENT_AUDIT.json"
        ),
        "development_report_sha256": _sha256(
            validation / "V0_41_1_DEVELOPMENT_REPORT.md"
        ),
        "development_integrity_anchor_sha256": _sha256(
            validation
            / "v0.41.1_development_matrix_seed_41011/integrity_yoking_audit.json"
        ),
        "seed_selection_performed_by_freeze": False,
        "seed_claims_written_by_freeze": 0,
        "rows_or_outcomes_opened_by_freeze": 0,
        "deterministic_record": True,
        "wall_clock_time_in_record": False,
    }
    freeze_text = (
        json.dumps(
            payload, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n"
    )
    freeze_path = validation / FREEZE_NAME
    checksum_path = validation / FREEZE_CHECKSUM_NAME
    _write_exclusive_text(freeze_path, freeze_text)
    freeze_sha256 = hashlib.sha256(freeze_text.encode("utf-8")).hexdigest()
    _write_exclusive_text(checksum_path, f"{freeze_sha256}  {FREEZE_NAME}\n")
    _fsync_directory(validation)

    return {
        "freeze_path": str(freeze_path),
        "freeze_sha256": freeze_sha256,
        "source_archive": str(archive),
        "source_archive_sha256": archive_sha256,
        "source_file_count": len(paths),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the RRCT v0.41.1 exclusive pre-outcome source freeze."
    )
    parser.add_argument("--project-root", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(create_freeze(arguments.project_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
