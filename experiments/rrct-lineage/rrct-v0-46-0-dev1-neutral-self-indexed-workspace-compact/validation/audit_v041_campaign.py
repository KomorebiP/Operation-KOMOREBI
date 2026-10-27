"""Independent audit of the frozen RRCT v0.41.1 four-seed pilot campaign.

Only the Python standard library is used.  The experimental package is never
imported.  Primitive sealed-row replay is delegated to the sibling independent
development auditor, which is itself standard-library-only and is frozen as
part of the scientific source surface.

The campaign decision is deliberately conjunctive: all four registered seeds
must have all six conditions, all integrity/claim/freeze chains must replay,
and every seed must meet every primary R+/R- endpoint.  Descriptive reward and
regret windows are always reported but never enter the pass rule.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tarfile
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

VERSION = "0.41.1.dev2"
FREEZE_NAME = "V0_41_1_PREOUTCOME_FREEZE.json"
REGISTRY_NAME = "V0_41_1_SEED_REGISTRY.json"
SELECTION_RECEIPT_NAME = "V0_41_1_SEED_SELECTION_RECEIPT.json"
SELECTION_SCAN_MANIFEST_NAME = "V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
EXTERNAL_COMMITMENT_NAME = "V0_41_1_PREOUTCOME_EXTERNAL_COMMITMENT.json"
DEFAULT_CAMPAIGN_NAME = "v0.41.1_frozen_exploratory_pilot_campaign"

FREEZE_SCHEMA = "rrct.v0411.preoutcome_freeze.v1"
REGISTRY_SCHEMA = "rrct.v0411.seed_registry.v1"
SELECTION_RECEIPT_SCHEMA = "rrct.v0411.seed_selection_receipt.v1"
SELECTION_SCAN_MANIFEST_SCHEMA = "rrct.v0411.seed_selection_scan_manifest.v1"
EXTERNAL_COMMITMENT_SCHEMA = "rrct.v0411.preoutcome_external_commitment.v1"
CAMPAIGN_SCHEMA = "rrct.v0411.frozen_pilot_campaign.v1"
START_SCHEMA = "rrct.v0411.frozen_pilot_condition.start.v1"
FINISH_SCHEMA = "rrct.v0411.frozen_pilot_condition.finish.v1"
CLAIM_SCHEMA = "rrct.v0411.frozen_pilot_condition.claim.v1"
SEED_CLAIM_SCHEMA = "rrct.v0411.frozen_pilot_seed.claim.v1"

FREEZE_STATUS = "fresh_pilot_temporal_identity_preoutcome_freeze"
PILOT_STATUS = "frozen_exploratory_pilot_not_confirmatory"

START_NAME = "start_receipt.json"
ROWS_NAME = "sealed_rows.jsonl"
SUMMARY_NAME = "summary.json"
FINISH_NAME = "finish_receipt.json"
ARTIFACT_NAME = "artifact_sha256.json"
CONDITION_FILES = {
    START_NAME,
    ROWS_NAME,
    SUMMARY_NAME,
    FINISH_NAME,
    ARTIFACT_NAME,
}

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
CONDITION_NAMES = tuple(CONDITIONS)

MANDATORY_FROZEN_SOURCE_PATHS = {
    "src/rrct/post_change_closure_experiment.py",
    "src/rrct/temporal_self_identity.py",
    "src/rrct/temporal_self_identity_experiment.py",
    "validation/run_v041_frozen_seed.py",
    "validation/audit_v041_development_matrix.py",
    "validation/audit_v041_campaign.py",
    "validation/select_v0411_seeds.py",
    "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json",
    "validation/V0_41_1_SEED_SELECTION_RECEIPT.json",
    "validation/V0_41_1_PREEXECUTION_VALIDATION.json",
    "validation/V0_41_1_FRESH_PILOT_PROTOCOL.md",
    "tests/test_v041_campaign_auditor.py",
}

BOUND_PREOUTCOME_INPUTS = {
    "development_protocol_sha256": (
        "validation/V0_41_1_CRITICAL_PATH_MATRIX_PROTOCOL.md"
    ),
    "fresh_pilot_protocol_sha256": ("validation/V0_41_1_FRESH_PILOT_PROTOCOL.md"),
    "protocol_sha256": "validation/V0_41_1_FRESH_PILOT_PROTOCOL.md",
    "development_conditions_sha256": ("validation/V0_41_1_DEVELOPMENT_CONDITIONS.json"),
    "preexecution_validation_sha256": (
        "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
    ),
    "development_audit_sha256": ("validation/V0_41_1_DEVELOPMENT_AUDIT.json"),
    "development_report_sha256": ("validation/V0_41_1_DEVELOPMENT_REPORT.md"),
    "development_integrity_anchor_sha256": (
        "validation/v0.41.1_development_matrix_seed_41011/integrity_yoking_audit.json"
    ),
}

PREEXECUTION_TRUE_CHECKS = (
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
    "PYTHONHASHSEED": "0",
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}

SELECTOR_RELATIVE_PATH = "validation/select_v0411_seeds.py"
SELECTION_SCAN_RULE = "standalone_decimal_occurrences_not_adjacent_to_ascii_digits"
SELECTION_CACHE_DIRECTORIES = {
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
}

CORE_PRODUCTION_PATHS = (
    "src/rrct/post_change_closure_experiment.py",
    "src/rrct/temporal_self_identity.py",
    "src/rrct/temporal_self_identity_experiment.py",
)


class CampaignAuditError(RuntimeError):
    """One fail-closed campaign-audit violation."""


def _load_replay_module() -> ModuleType:
    path = Path(__file__).with_name("audit_v041_development_matrix.py")
    name = "_rrct_v041_independent_row_replay"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CampaignAuditError("cannot load independent row replay module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REPLAY = _load_replay_module()


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CampaignAuditError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise CampaignAuditError(f"nonfinite JSON token {token!r}")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CampaignAuditError(f"required file is missing: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except CampaignAuditError:
        raise
    except Exception as exc:
        raise CampaignAuditError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CampaignAuditError(f"JSON object required: {path}")
    return value


def _canonical_sha256(value: Any) -> str:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CampaignAuditError(f"noncanonical JSON value: {exc}") from exc
    return hashlib.sha256(encoded).hexdigest()


def _canonical_pretty_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CampaignAuditError(f"noncanonical pretty JSON value: {exc}") from exc


def _runner_pretty_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CampaignAuditError(f"noncanonical runner JSON value: {exc}") from exc


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError as exc:
        raise CampaignAuditError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CampaignAuditError(message)


def _is_sha256(value: Any) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _parse_utc(value: Any, label: str) -> datetime:
    _require(isinstance(value, str) and bool(value), f"{label}: UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CampaignAuditError(f"{label}: malformed UTC timestamp") from exc
    _require(
        parsed.tzinfo is not None
        and parsed.utcoffset() == timezone.utc.utcoffset(parsed),
        f"{label}: timestamp is not UTC",
    )
    return parsed


def _safe_project_file(project_root: Path, relative: Any, label: str) -> Path:
    _require(isinstance(relative, str) and bool(relative), f"{label}: relative path")
    candidate = Path(relative)
    _require(
        not candidate.is_absolute() and ".." not in candidate.parts,
        f"{label}: path escape",
    )
    unresolved = project_root / candidate
    try:
        path = unresolved.resolve(strict=True)
        path.relative_to(project_root)
    except (OSError, ValueError) as exc:
        raise CampaignAuditError(f"{label}: path is outside project") from exc
    _require(path.is_file(), f"{label}: not a regular file")
    _require(
        unresolved.absolute() == path and not unresolved.is_symlink(),
        f"{label}: symlink traversal is forbidden",
    )
    return path


def _safe_campaign_file(campaign_root: Path, relative: Any, label: str) -> Path:
    _require(isinstance(relative, str) and bool(relative), f"{label}: relative path")
    candidate = Path(relative)
    _require(
        not candidate.is_absolute() and ".." not in candidate.parts,
        f"{label}: path escape",
    )
    unresolved = campaign_root / candidate
    try:
        path = unresolved.resolve(strict=True)
        path.relative_to(campaign_root)
    except (OSError, ValueError) as exc:
        raise CampaignAuditError(f"{label}: path is outside campaign") from exc
    _require(path.is_file(), f"{label}: not a regular file")
    _require(
        unresolved.absolute() == path and not unresolved.is_symlink(),
        f"{label}: symlink traversal is forbidden",
    )
    return path


def _verify_archive_members(
    archive_path: Path, source_hashes: Mapping[str, str]
) -> None:
    observed: dict[str, str] = {}
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            for member in archive.getmembers():
                _require(
                    member.isfile(), f"archive contains non-file member {member.name!r}"
                )
                _require(
                    member.name not in observed,
                    f"duplicate archive member {member.name!r}",
                )
                _require(
                    not Path(member.name).is_absolute()
                    and ".." not in Path(member.name).parts,
                    f"unsafe archive member {member.name!r}",
                )
                extracted = archive.extractfile(member)
                _require(
                    extracted is not None, f"unreadable archive member {member.name!r}"
                )
                digest = hashlib.sha256()
                for block in iter(lambda handle=extracted: handle.read(1 << 20), b""):
                    digest.update(block)
                observed[member.name] = digest.hexdigest()
    except (OSError, tarfile.TarError) as exc:
        raise CampaignAuditError(f"cannot verify source archive: {exc}") from exc
    _require(
        observed == dict(source_hashes),
        "source archive members differ from frozen manifest",
    )


def verify_freeze(project_root: Path) -> dict[str, Any]:
    """Recompute the freeze, registry, source, and source-archive chain."""

    supplied_root = Path(os.path.abspath(os.fspath(project_root)))
    project_root = supplied_root.resolve(strict=True)
    _require(
        supplied_root == project_root
        and project_root.is_dir()
        and not project_root.is_symlink(),
        "project root must be an already-resolved nonsymlink directory",
    )
    validation_root = project_root / "validation"
    _require(
        validation_root.is_dir() and not validation_root.is_symlink(),
        "validation root must be a nonsymlink directory",
    )
    freeze_path = project_root / "validation" / FREEZE_NAME
    checksum_path = freeze_path.with_name(f"{freeze_path.name}.sha256")
    _require(
        freeze_path.is_file()
        and checksum_path.is_file()
        and not freeze_path.is_symlink()
        and not checksum_path.is_symlink(),
        "freeze/checksum missing or symlinked",
    )
    freeze_sha256 = _sha256_file(freeze_path)
    parts = checksum_path.read_text(encoding="utf-8").strip().split()
    _require(
        len(parts) == 2
        and parts[0] == freeze_sha256
        and Path(parts[1]).name == FREEZE_NAME,
        "freeze checksum companion mismatch",
    )
    freeze = _load_json(freeze_path)
    _require(freeze.get("schema") == FREEZE_SCHEMA, "freeze schema mismatch")
    _require(freeze.get("version") == VERSION, "freeze version mismatch")
    _require(freeze.get("scientific_status") == FREEZE_STATUS, "freeze status mismatch")
    _require(freeze.get("campaign_stage") == "fresh_pilot", "freeze campaign stage")
    _require(freeze.get("confirmatory") is False, "pilot freeze marked confirmatory")
    _require(
        freeze.get("fresh_seed_state_at_freeze") == "unopened",
        "seeds not unopened at freeze",
    )
    _require(freeze.get("cohort_opened_at_freeze") is False, "cohort open at freeze")
    _require(
        freeze.get("seed_selection_performed_by_freeze") is False,
        "freeze selected seeds",
    )
    _require(
        freeze.get("seed_claims_written_by_freeze") == 0, "freeze wrote seed claims"
    )
    _require(
        freeze.get("rows_or_outcomes_opened_by_freeze") == 0, "freeze opened outcomes"
    )
    _require(
        freeze.get("deterministic_record") is True
        and freeze.get("wall_clock_time_in_record") is False,
        "freeze deterministic-record metadata",
    )
    _require(freeze.get("condition_matrix") == CONDITIONS, "freeze condition matrix")
    _require(
        freeze.get("condition_names") == sorted(CONDITIONS), "freeze condition names"
    )
    for field, relative in BOUND_PREOUTCOME_INPUTS.items():
        path = _safe_project_file(project_root, relative, field)
        _require(
            freeze.get(field) == _sha256_file(path),
            f"freeze pre-outcome binding mismatch: {field}",
        )
    preexecution = _load_json(
        project_root / "validation" / "V0_41_1_PREEXECUTION_VALIDATION.json"
    )
    _require(
        preexecution.get("schema") == "rrct.v0411.preexecution_validation.v1",
        "preexecution schema",
    )
    _require(preexecution.get("version") == VERSION, "preexecution version")
    _require(
        preexecution.get("scientific_status") == "preoutcome_all_checks_pass",
        "preexecution status",
    )
    _require(preexecution.get("all_checks_pass") is True, "preexecution all-pass")
    _require(preexecution.get("cohort_opened") is False, "preexecution cohort opened")
    _require(
        preexecution.get("fresh_seed_state") == "unopened",
        "preexecution fresh-seed state",
    )
    checks = preexecution.get("checks")
    _require(
        isinstance(checks, dict)
        and set(checks) == set(PREEXECUTION_TRUE_CHECKS)
        and all(checks.get(key) is True for key in PREEXECUTION_TRUE_CHECKS),
        "preexecution checklist failed/incomplete",
    )
    _require(
        isinstance(preexecution.get("test_command"), str)
        and bool(preexecution["test_command"].strip()),
        "preexecution test command",
    )
    passed_test_count = preexecution.get("passed_test_count")
    _require(
        isinstance(passed_test_count, int)
        and not isinstance(passed_test_count, bool)
        and passed_test_count > 0,
        "preexecution passed-test count",
    )
    dependency_lock = project_root / "uv.lock"
    _require(
        preexecution.get("dependency_lock_sha256") == _sha256_file(dependency_lock),
        "preexecution dependency-lock digest",
    )
    production_source = preexecution.get("production_source_sha256")
    _require(
        isinstance(production_source, dict)
        and set(production_source) == set(CORE_PRODUCTION_PATHS),
        "preexecution production-source map",
    )
    for relative in CORE_PRODUCTION_PATHS:
        _require(
            production_source.get(relative) == _sha256_file(project_root / relative),
            f"preexecution production-source digest: {relative}",
        )
    _require(
        preexecution.get("production_source_set_sha256")
        == _canonical_sha256(production_source),
        "preexecution production-source-set digest",
    )
    _require(
        preexecution.get("required_environment")
        == {
            "environment": REQUIRED_ENVIRONMENT,
            "python_flags": {
                "safe_path": True,
                "no_user_site": True,
                "dont_write_bytecode": True,
            },
        },
        "preexecution environment contract",
    )
    _require(
        freeze.get("required_environment") == preexecution["required_environment"],
        "freeze/preexecution environment contract",
    )
    _require(
        freeze.get("preexecution_validation")
        == {
            "relative_path": ("validation/V0_41_1_PREEXECUTION_VALIDATION.json"),
            "schema": "rrct.v0411.preexecution_validation.v1",
            "sha256": freeze["preexecution_validation_sha256"],
            "scientific_status": "preoutcome_all_checks_pass",
            "all_checks_pass": True,
        },
        "freeze/preexecution record binding",
    )
    for field in ("errors", "failures", "failed_checks"):
        if field in preexecution:
            _require(preexecution[field] == [], f"preexecution {field} is nonempty")
    if "cohort_opened" in preexecution:
        _require(preexecution["cohort_opened"] is False, "preexecution cohort opened")
    if "fresh_seed_state" in preexecution:
        _require(
            preexecution["fresh_seed_state"] == "unopened",
            "preexecution seed state",
        )

    source_hashes = freeze.get("scientific_source_sha256")
    _require(
        isinstance(source_hashes, dict) and bool(source_hashes),
        "freeze source manifest missing",
    )
    _require(
        MANDATORY_FROZEN_SOURCE_PATHS.issubset(source_hashes),
        "mandatory source missing from freeze",
    )
    for relative, expected in source_hashes.items():
        _require(_is_sha256(expected), f"malformed source digest: {relative}")
        path = _safe_project_file(project_root, relative, f"frozen source {relative}")
        _require(_sha256_file(path) == expected, f"frozen source changed: {relative}")
    source_set_sha256 = freeze.get("scientific_source_set_sha256")
    _require(
        _is_sha256(source_set_sha256)
        and source_set_sha256 == _canonical_sha256(source_hashes),
        "frozen source-set digest mismatch",
    )

    archive = freeze.get("source_archive")
    _require(isinstance(archive, dict), "source archive binding missing")
    _require(
        archive.get("format") == "ustar+gzip"
        and archive.get("member_mtime") == 0
        and archive.get("gzip_mtime") == 0,
        "source archive reproducibility metadata",
    )
    archive_path = _safe_project_file(
        project_root, archive.get("relative_path"), "source archive"
    )
    archive_sha256 = archive.get("sha256")
    _require(
        _is_sha256(archive_sha256) and _sha256_file(archive_path) == archive_sha256,
        "source archive digest mismatch",
    )
    _require(
        archive_path.name == f"V0_41_1_EXECUTED_SOURCE_{archive_sha256[:16]}.tar.gz",
        "source archive name/digest binding",
    )
    validation_archive_paths = list(
        (project_root / "validation").glob("V0_41_1_EXECUTED_SOURCE_*.tar.gz")
    )
    _require(
        all(not path.is_symlink() for path in validation_archive_paths),
        "symlinked executed-source archive",
    )
    validation_archives = {
        path.resolve(strict=True) for path in validation_archive_paths
    }
    _require(
        validation_archives == {archive_path},
        "extra/missing executed-source archive",
    )
    _require(
        not any(
            (project_root / "validation").glob(".V0_41_1_EXECUTED_SOURCE_*.tar.gz")
        ),
        "temporary/failure source archive remains",
    )
    _require(
        archive.get("member_count") == len(source_hashes),
        "source archive member count mismatch",
    )
    _verify_archive_members(archive_path, source_hashes)

    registry_binding = freeze.get("seed_registry")
    _require(isinstance(registry_binding, dict), "seed registry binding missing")
    _require(
        registry_binding.get("relative_path") == f"validation/{REGISTRY_NAME}",
        "seed registry path mismatch",
    )
    registry_path = _safe_project_file(
        project_root, registry_binding.get("relative_path"), "seed registry"
    )
    registry_sha256 = registry_binding.get("sha256")
    _require(
        _is_sha256(registry_sha256)
        and registry_sha256 == freeze.get("seed_registry_sha256")
        and _sha256_file(registry_path) == registry_sha256,
        "seed registry digest mismatch",
    )
    registry = _load_json(registry_path)
    _require(registry.get("schema") == REGISTRY_SCHEMA, "registry schema")
    _require(registry.get("version") == VERSION, "registry version")
    _require(
        registry.get("registry_state") == "unopened", "registry was not frozen unopened"
    )
    _require(registry.get("cohort_opened") is False, "registry cohort-open flag")
    _require(
        registry.get("opened_seed_condition_pairs") == [],
        "registry recorded opened pairs before freeze",
    )
    _require(registry.get("conditions") == CONDITIONS, "registry conditions")
    seeds = registry.get("fresh_pilot_seeds")
    _require(
        isinstance(seeds, list)
        and len(seeds) == 4
        and len(set(seeds)) == 4
        and all(
            isinstance(seed, int) and not isinstance(seed, bool) and 1 <= seed < 2**63
            for seed in seeds
        ),
        "registry must contain exactly four unique positive seeds",
    )
    return {
        "project_root": project_root,
        "freeze": freeze,
        "freeze_sha256": freeze_sha256,
        "source_sha256": source_hashes,
        "source_set_sha256": source_set_sha256,
        "source_archive_path": archive_path,
        "source_archive_sha256": archive_sha256,
        "registry": registry,
        "registry_sha256": registry_sha256,
        "seeds": tuple(int(seed) for seed in seeds),
    }


def verify_seed_selection(
    project_root: Path, verified: Mapping[str, Any]
) -> dict[str, Any]:
    """Recompute the sealed twelve-candidate scan and first-four derivation."""

    validation = project_root / "validation"
    scan_path = validation / SELECTION_SCAN_MANIFEST_NAME
    receipt_path = validation / SELECTION_RECEIPT_NAME
    for label, path in (
        ("scan manifest", scan_path),
        ("selection receipt", receipt_path),
    ):
        _require(
            path.is_file() and not path.is_symlink(),
            f"seed-selection {label} missing/symlinked",
        )
    _require(
        not (validation / ".V0_41_1_SEED_SELECTION_TRANSACTION").exists(),
        "seed-selection transaction directory remains",
    )
    scan = _load_json(scan_path)
    receipt = _load_json(receipt_path)
    candidates = receipt.get("candidate_generation_order")
    _require(
        isinstance(candidates, list)
        and len(candidates) == 12
        and len(set(candidates)) == 12
        and all(
            isinstance(candidate, int)
            and not isinstance(candidate, bool)
            and 100_000_000 <= candidate < 900_000_000
            for candidate in candidates
        ),
        "selection receipt candidate generation order",
    )
    patterns = {
        candidate: re.compile(
            rb"(?<![0-9])" + str(candidate).encode("ascii") + rb"(?![0-9])"
        )
        for candidate in candidates
    }
    reconstructed_occurrences: dict[int, list[str]] = {
        candidate: [] for candidate in candidates
    }
    registry = verified["registry"]
    registry_path = project_root / "validation" / REGISTRY_NAME
    _require(
        scan_path.read_bytes() == _canonical_pretty_bytes(scan),
        "scan manifest is not canonical selector JSON",
    )
    _require(
        receipt_path.read_bytes() == _canonical_pretty_bytes(receipt),
        "selection receipt is not canonical selector JSON",
    )
    _require(
        registry_path.read_bytes() == _canonical_pretty_bytes(registry),
        "seed registry is not canonical selector JSON",
    )
    scan_sha256 = _sha256_file(scan_path)
    receipt_sha256 = _sha256_file(receipt_path)
    freeze = verified["freeze"]
    _require(
        freeze.get("seed_selection_scan_manifest")
        == {
            "relative_path": f"validation/{SELECTION_SCAN_MANIFEST_NAME}",
            "sha256": scan_sha256,
            "schema": SELECTION_SCAN_MANIFEST_SCHEMA,
        }
        and freeze.get("seed_selection_scan_manifest_sha256") == scan_sha256,
        "freeze/selection scan-manifest binding",
    )
    _require(
        freeze.get("seed_selection_receipt")
        == {
            "relative_path": f"validation/{SELECTION_RECEIPT_NAME}",
            "sha256": receipt_sha256,
            "schema": SELECTION_RECEIPT_SCHEMA,
            "selection_state_at_freeze": "unopened",
        }
        and freeze.get("seed_selection_receipt_sha256") == receipt_sha256,
        "freeze/selection receipt binding",
    )

    _require(scan.get("schema") == SELECTION_SCAN_MANIFEST_SCHEMA, "scan schema")
    _require(scan.get("version") == VERSION, "scan version")
    _require(
        scan.get("scientific_status") == "pre_registry_complete_project_evidence_scan",
        "scan scientific status",
    )
    _require(scan.get("scan_rule") == SELECTION_SCAN_RULE, "scan rule")
    expected_surface_policy = {
        "root": ".",
        "follow_symlinks": False,
        "regular_files_only": True,
        "excluded_directory_names": sorted(SELECTION_CACHE_DIRECTORIES),
        "excluded_future_output_names": sorted(
            {SELECTION_SCAN_MANIFEST_NAME, SELECTION_RECEIPT_NAME, REGISTRY_NAME}
        ),
        "excluded_campaign_directory": f"validation/{DEFAULT_CAMPAIGN_NAME}",
        "excluded_freeze_output_patterns": [
            "validation/V0_41_1_PREOUTCOME_FREEZE.json*",
            "validation/V0_41_1_EXECUTED_SOURCE_*.tar.gz",
            "validation/.V0_41_1_EXECUTED_SOURCE_*.tar.gz",
        ],
    }
    _require(
        scan.get("project_surface_policy") == expected_surface_policy,
        "scan surface policy",
    )
    file_records = scan.get("files")
    _require(isinstance(file_records, list) and bool(file_records), "scan files")
    observed_file_paths: list[str] = []
    for index, record in enumerate(file_records):
        _require(
            isinstance(record, dict)
            and set(record) == {"relative_path", "size_bytes", "sha256"},
            f"scan file record {index}",
        )
        relative = record.get("relative_path")
        size = record.get("size_bytes")
        digest = record.get("sha256")
        _require(
            isinstance(relative, str)
            and bool(relative)
            and isinstance(size, int)
            and not isinstance(size, bool)
            and size >= 0
            and _is_sha256(digest),
            f"scan file record {index} fields",
        )
        path = _safe_project_file(project_root, relative, f"scan file {relative}")
        data = path.read_bytes()
        _require(
            len(data) == size and hashlib.sha256(data).hexdigest() == digest,
            f"scan file changed: {relative}",
        )
        observed_file_paths.append(relative)
        for candidate, pattern in patterns.items():
            count = len(pattern.findall(data))
            reconstructed_occurrences[candidate].extend([relative] * count)
    _require(
        observed_file_paths == sorted(observed_file_paths)
        and len(observed_file_paths) == len(set(observed_file_paths)),
        "scan file records are not sorted/unique",
    )
    reconstructed_surface: list[str] = []

    def walk_error(error: OSError) -> None:
        raise CampaignAuditError(f"selection-surface walk failed: {error}")

    for directory, directory_names, file_names in os.walk(
        project_root, followlinks=False, onerror=walk_error
    ):
        directory_path = Path(directory)
        retained_directories: list[str] = []
        for name in sorted(directory_names):
            path = directory_path / name
            relative = path.relative_to(project_root)
            if name in SELECTION_CACHE_DIRECTORIES:
                continue
            if relative.as_posix() == f"validation/{DEFAULT_CAMPAIGN_NAME}":
                continue
            _require(
                not path.is_symlink(),
                f"symlink in reconstructed selection surface: {relative}",
            )
            retained_directories.append(name)
        directory_names[:] = retained_directories
        for name in sorted(file_names):
            path = directory_path / name
            relative = path.relative_to(project_root).as_posix()
            allowed_postselection = bool(
                relative
                in {
                    f"validation/{SELECTION_SCAN_MANIFEST_NAME}",
                    f"validation/{SELECTION_RECEIPT_NAME}",
                    f"validation/{REGISTRY_NAME}",
                    f"validation/{FREEZE_NAME}",
                    f"validation/{FREEZE_NAME}.sha256",
                    f"validation/{EXTERNAL_COMMITMENT_NAME}",
                    f"validation/{EXTERNAL_COMMITMENT_NAME}.sha256",
                    ("validation/.v0.41.1_frozen_exploratory_pilot_campaign.lock"),
                }
                or re.fullmatch(
                    r"validation/\.?V0_41_1_EXECUTED_SOURCE_.*\.tar\.gz",
                    relative,
                )
                is not None
            )
            if allowed_postselection:
                continue
            _require(
                path.is_file() and not path.is_symlink(),
                f"nonregular entry in reconstructed selection surface: {relative}",
            )
            reconstructed_surface.append(relative)
    reconstructed_surface.sort()
    _require(
        reconstructed_surface == observed_file_paths,
        "scan manifest omits/adds files relative to the reconstructable surface",
    )
    _require(
        scan.get("file_count") == len(file_records)
        and scan.get("scan_surface_sha256") == _canonical_sha256(file_records),
        "scan surface count/digest",
    )
    _require(
        SELECTOR_RELATIVE_PATH in observed_file_paths,
        "selector missing from pre-registry scan surface",
    )
    excluded = scan.get("excluded_entries")
    _require(isinstance(excluded, list), "scan excluded entries")
    allowed_exclusion_reasons = {
        "venv_or_cache_directory",
        "future_campaign_output",
        "future_seed_selection_output",
        "future_freeze_output",
    }
    normalized_excluded: list[tuple[str, str]] = []
    for index, record in enumerate(excluded):
        _require(
            isinstance(record, dict)
            and set(record) == {"relative_path", "reason"}
            and isinstance(record.get("relative_path"), str)
            and bool(record["relative_path"])
            and record.get("reason") in allowed_exclusion_reasons,
            f"scan exclusion record {index}",
        )
        relative_path = Path(record["relative_path"])
        _require(
            not relative_path.is_absolute() and ".." not in relative_path.parts,
            f"unsafe scan exclusion record {index}",
        )
        reason = record["reason"]
        reason_matches_path = bool(
            (
                reason == "venv_or_cache_directory"
                and any(
                    part in SELECTION_CACHE_DIRECTORIES for part in relative_path.parts
                )
            )
            or (
                reason == "future_campaign_output"
                and relative_path.parts[:2] == ("validation", DEFAULT_CAMPAIGN_NAME)
            )
            or (
                reason == "future_seed_selection_output"
                and len(relative_path.parts) == 2
                and relative_path.parts[0] == "validation"
                and relative_path.name
                in {
                    SELECTION_SCAN_MANIFEST_NAME,
                    SELECTION_RECEIPT_NAME,
                    REGISTRY_NAME,
                    ".V0_41_1_SEED_SELECTION_TRANSACTION",
                }
            )
            or (
                reason == "future_freeze_output"
                and len(relative_path.parts) == 2
                and relative_path.parts[0] == "validation"
                and (
                    relative_path.name in {FREEZE_NAME, f"{FREEZE_NAME}.sha256"}
                    or re.fullmatch(
                        r"\.?V0_41_1_EXECUTED_SOURCE_.*\.tar\.gz",
                        relative_path.name,
                    )
                    is not None
                )
            )
        )
        _require(reason_matches_path, f"scan exclusion {index} reason/path")
        normalized_excluded.append((record["relative_path"], record["reason"]))
    _require(
        normalized_excluded == sorted(normalized_excluded)
        and len(normalized_excluded) == len(set(normalized_excluded)),
        "scan exclusions are not sorted/unique",
    )

    receipt_invariants = {
        "schema": SELECTION_RECEIPT_SCHEMA,
        "version": VERSION,
        "scientific_status": "preoutcome_seed_selection_complete_unopened",
        "selection_method": "single_nonrepeated_secrets_randbelow_draw_loop",
        "draw_expression": "secrets.randbelow(800_000_000) + 100_000_000",
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
    for field, expected in receipt_invariants.items():
        _require(receipt.get(field) == expected, f"selection receipt: {field}")
    randbelow_calls = receipt.get("randbelow_call_count")
    _require(
        isinstance(randbelow_calls, int)
        and not isinstance(randbelow_calls, bool)
        and randbelow_calls >= 12
        and receipt.get("duplicate_draw_count") == randbelow_calls - 12,
        "selection draw accounting",
    )
    candidate_records = receipt.get("candidate_scan_records")
    _require(
        isinstance(candidate_records, list) and len(candidate_records) == 12,
        "selection candidate scan records",
    )
    for index, (candidate, record) in enumerate(
        zip(candidates, candidate_records, strict=True)
    ):
        paths = reconstructed_occurrences[candidate]
        _require(
            isinstance(record, dict)
            and set(record)
            == {
                "generation_index",
                "candidate",
                "standalone_decimal_occurrence_count",
                "occurrence_paths",
                "zero_occurrence",
            }
            and record.get("generation_index") == index
            and record.get("candidate") == candidate
            and record.get("standalone_decimal_occurrence_count") == len(paths)
            and record.get("occurrence_paths") == paths
            and record.get("zero_occurrence") is (not paths),
            f"selection candidate scan record {index}",
        )
    selected = [
        candidate
        for candidate, record in zip(candidates, candidate_records, strict=True)
        if record["zero_occurrence"]
    ][:4]
    _require(len(selected) == 4, "selection has fewer than four clean candidates")
    _require(
        receipt.get("selected_fresh_pilot_seeds") == selected
        and list(verified["seeds"]) == selected,
        "selected seeds are not the first four zero-occurrence candidates",
    )

    scan_binding = receipt.get("scan_manifest")
    _require(
        scan_binding
        == {
            "relative_path": f"validation/{SELECTION_SCAN_MANIFEST_NAME}",
            "schema": SELECTION_SCAN_MANIFEST_SCHEMA,
            "sha256": scan_sha256,
            "file_count": len(file_records),
            "scan_surface_sha256": scan["scan_surface_sha256"],
        },
        "selection receipt/scan binding",
    )
    selector_binding = receipt.get("selector")
    selector_index = observed_file_paths.index(SELECTOR_RELATIVE_PATH)
    selector_sha256 = file_records[selector_index]["sha256"]
    _require(
        selector_binding
        == {
            "relative_path": SELECTOR_RELATIVE_PATH,
            "sha256": selector_sha256,
        },
        "selection receipt/selector binding",
    )
    _require(
        verified["source_sha256"].get(SELECTOR_RELATIVE_PATH) == selector_sha256,
        "frozen selector source differs from selection receipt",
    )
    _require(
        receipt.get("seed_registry")
        == {
            "relative_path": f"validation/{REGISTRY_NAME}",
            "schema": REGISTRY_SCHEMA,
            "sha256": verified["registry_sha256"],
            "registry_state": "unopened",
        },
        "selection receipt/registry binding",
    )
    _require(
        registry.get("scientific_status")
        == "fresh_pilot_seed_registry_selected_unopened"
        and registry.get("seed_selection_receipt_relative_path")
        == f"validation/{SELECTION_RECEIPT_NAME}"
        and registry.get("seed_selection_scan_manifest_relative_path")
        == f"validation/{SELECTION_SCAN_MANIFEST_NAME}"
        and registry.get("seed_selection_scan_manifest_sha256") == scan_sha256,
        "registry/selection provenance binding",
    )
    return {
        "selection_receipt": receipt,
        "selection_receipt_sha256": receipt_sha256,
        "selection_scan_manifest": scan,
        "selection_scan_manifest_sha256": scan_sha256,
        "selector_sha256": selector_sha256,
        "selection_surface_file_count": len(file_records),
    }


def verify_external_commitment(
    project_root: Path, verified: Mapping[str, Any]
) -> dict[str, Any]:
    """Rehash the post-freeze, externally persisted pre-outcome commitment."""

    path = project_root / "validation" / EXTERNAL_COMMITMENT_NAME
    checksum_path = path.with_name(f"{path.name}.sha256")
    _require(
        path.is_file()
        and not path.is_symlink()
        and checksum_path.is_file()
        and not checksum_path.is_symlink(),
        "external commitment/checksum missing or symlinked",
    )
    digest = _sha256_file(path)
    parts = checksum_path.read_text(encoding="utf-8").strip().split()
    _require(
        len(parts) == 2
        and parts[0] == digest
        and Path(parts[1]).name == EXTERNAL_COMMITMENT_NAME,
        "external commitment checksum mismatch",
    )
    payload = _load_json(path)
    required = {
        "schema": EXTERNAL_COMMITMENT_SCHEMA,
        "version": VERSION,
        "scientific_status": "external_preoutcome_commitment_complete",
        "confirmatory": False,
        "freeze_sha256": verified["freeze_sha256"],
        "scientific_source_set_sha256": verified["source_set_sha256"],
        "source_archive_sha256": verified["source_archive_sha256"],
        "seed_registry_sha256": verified["registry_sha256"],
        "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified[
            "selection_scan_manifest_sha256"
        ],
        "outcomes_opened_before_commitment": False,
        "rows_opened_before_commitment": 0,
        "seed_condition_claims_before_commitment": 0,
    }
    for key, value in required.items():
        _require(payload.get(key) == value, f"external commitment: {key}")
    persistent = payload.get("external_persistent_file")
    _require(isinstance(persistent, dict), "external persistent-file binding")
    for key in ("provider", "file_id", "version"):
        _require(
            isinstance(persistent.get(key), str) and bool(persistent[key].strip()),
            f"external persistent file: {key}",
        )
    _require(
        persistent.get("immutable_or_append_only") is True,
        "external persistent file is not immutable/append-only",
    )
    timestamp = persistent.get("committed_at_utc")
    _require(
        isinstance(timestamp, str) and timestamp.endswith("Z"),
        "external commitment timestamp format",
    )
    _parse_utc(timestamp, "external commitment")
    return {
        "external_commitment": payload,
        "external_commitment_sha256": digest,
        "external_persistent_file": persistent,
    }


def expected_topology(seeds: Sequence[int]) -> dict[str, set[str]]:
    """Return the exact directory/claim basenames permitted by the protocol."""

    return {
        "pair_seed_directories": {f"seed-{seed}" for seed in seeds},
        "seed_claim_files": {f"seed-{seed}.json" for seed in seeds},
        "condition_claim_files": {
            f"seed-{seed}--{condition}.json"
            for seed in seeds
            for condition in CONDITIONS
        },
    }


def _entry_names(directory: Path) -> set[str]:
    _require(
        directory.is_dir() and not directory.is_symlink(),
        f"required nonsymlink directory missing: {directory}",
    )
    return {entry.name for entry in directory.iterdir()}


def verify_topology(campaign_root: Path, seeds: Sequence[int]) -> dict[str, Any]:
    expected = expected_topology(seeds)
    pairs_root = campaign_root / "pairs"
    seed_claims = campaign_root / "_seed_claims"
    condition_claims = campaign_root / "_condition_claims"
    attempt_claims = campaign_root / "_attempt_claims"
    _require(
        _entry_names(pairs_root) == expected["pair_seed_directories"],
        "extra/missing paired seed directory",
    )
    _require(
        _entry_names(seed_claims) == expected["seed_claim_files"],
        "extra/missing seed claim",
    )
    _require(
        _entry_names(condition_claims) == expected["condition_claim_files"],
        "extra/missing condition claim",
    )
    attempt_names = _entry_names(attempt_claims)
    _require(
        len(attempt_names) == len(seeds) * len(CONDITIONS),
        "attempt claim count is not exactly 24",
    )
    _require(
        all(name.endswith(".json") for name in attempt_names),
        "non-JSON attempt claim entry",
    )
    for seed in seeds:
        seed_root = pairs_root / f"seed-{seed}"
        _require(
            _entry_names(seed_root) == set(CONDITIONS),
            f"seed {seed}: extra/missing condition arm",
        )
        for condition in CONDITIONS:
            condition_root = seed_root / condition
            _require(
                _entry_names(condition_root) == CONDITION_FILES,
                f"seed {seed} {condition}: extra/missing artifact",
            )
            _require(
                all(
                    (condition_root / name).is_file()
                    and not (condition_root / name).is_symlink()
                    for name in CONDITION_FILES
                ),
                f"seed {seed} {condition}: non-file/symlink artifact",
            )
    return {
        "pair_seed_directories": sorted(expected["pair_seed_directories"]),
        "seed_claim_files": sorted(expected["seed_claim_files"]),
        "condition_claim_files": sorted(expected["condition_claim_files"]),
        "attempt_claim_count": len(attempt_names),
    }


def _claim_common_valid(
    claim: Mapping[str, Any],
    *,
    seed: int,
    verified: Mapping[str, Any],
) -> bool:
    return bool(
        claim.get("version") == VERSION
        and claim.get("scientific_status") == PILOT_STATUS
        and claim.get("confirmatory") is False
        and claim.get("seed") == seed
        and claim.get("freeze_sha256") == verified["freeze_sha256"]
        and claim.get("source_set_sha256") == verified["source_set_sha256"]
        and claim.get("seed_registry_sha256") == verified["registry_sha256"]
        and claim.get("seed_selection_receipt_sha256")
        == verified["selection_receipt_sha256"]
        and claim.get("seed_selection_scan_manifest_sha256")
        == verified["selection_scan_manifest_sha256"]
        and claim.get("external_commitment_sha256")
        == verified["external_commitment_sha256"]
        and claim.get("external_persistent_file")
        == verified["external_persistent_file"]
    )


def verify_arm_chain(
    campaign_root: Path,
    condition_root: Path,
    *,
    seed: int,
    condition: str,
    verified: Mapping[str, Any],
) -> dict[str, Any]:
    start = _load_json(condition_root / START_NAME)
    finish = _load_json(condition_root / FINISH_NAME)
    summary = _load_json(condition_root / SUMMARY_NAME)
    artifact_manifest = _load_json(condition_root / ARTIFACT_NAME)
    for filename, value in (
        (START_NAME, start),
        (FINISH_NAME, finish),
        (SUMMARY_NAME, summary),
        (ARTIFACT_NAME, artifact_manifest),
    ):
        _require(
            (condition_root / filename).read_bytes() == _runner_pretty_bytes(value),
            f"seed {seed} {condition}: noncanonical {filename}",
        )
    specification = CONDITIONS[condition]
    _require(
        start.get("schema") == START_SCHEMA, f"seed {seed} {condition}: start schema"
    )
    _require(
        finish.get("schema") == FINISH_SCHEMA, f"seed {seed} {condition}: finish schema"
    )
    for label, receipt in (("start", start), ("finish", finish)):
        _require(
            receipt.get("version") == VERSION,
            f"seed {seed} {condition}: {label} version",
        )
        _require(
            receipt.get("scientific_status") == PILOT_STATUS,
            f"seed {seed} {condition}: {label} status",
        )
        _require(
            receipt.get("confirmatory") is False,
            f"seed {seed} {condition}: {label} confirmatory",
        )
        _require(
            receipt.get("freeze_bound") is True,
            f"seed {seed} {condition}: {label} freeze binding",
        )
        _require(
            receipt.get("seed") == seed and receipt.get("condition_id") == condition,
            f"seed {seed} {condition}: {label} identity",
        )
        _require(
            receipt.get("history_policy") == specification["history_policy"],
            f"seed {seed} {condition}: {label} policy",
        )
        _require(
            receipt.get("world_variant") == specification["world_variant"],
            f"seed {seed} {condition}: {label} world",
        )
        _require(
            receipt.get("freeze_sha256") == verified["freeze_sha256"],
            f"seed {seed} {condition}: {label}/freeze",
        )
        _require(
            receipt.get("source_set_sha256") == verified["source_set_sha256"],
            f"seed {seed} {condition}: {label}/source",
        )
        _require(
            receipt.get("seed_registry_sha256") == verified["registry_sha256"],
            f"seed {seed} {condition}: {label}/registry",
        )
    attempt_id = start.get("attempt_id")
    _require(
        isinstance(attempt_id, str)
        and re.fullmatch(r"[A-Z0-9][A-Z0-9._-]{2,80}", attempt_id) is not None,
        f"seed {seed} {condition}: attempt ID",
    )
    _require(
        finish.get("attempt_id") == attempt_id,
        f"seed {seed} {condition}: finish attempt",
    )
    environment = start.get("environment_fingerprint")
    _require(
        isinstance(environment, dict),
        f"seed {seed} {condition}: environment fingerprint",
    )
    environment_digest = environment.get("sha256")
    environment_payload = dict(environment)
    environment_payload.pop("sha256", None)
    _require(
        _is_sha256(environment_digest)
        and _canonical_sha256(environment_payload) == environment_digest,
        f"seed {seed} {condition}: environment fingerprint digest",
    )
    _require(
        set(environment)
        == {
            "python",
            "python_implementation",
            "python_executable",
            "platform",
            "numpy_distribution_version",
            "uv_lock_sha256",
            "environment",
            "sys_flags",
            "sys_dont_write_bytecode",
            "sha256",
        }
        and all(
            isinstance(environment.get(field), str) and bool(environment[field])
            for field in (
                "python",
                "python_implementation",
                "python_executable",
                "platform",
                "numpy_distribution_version",
            )
        )
        and environment.get("uv_lock_sha256")
        == _sha256_file(verified["project_root"] / "uv.lock")
        and environment.get("environment") == REQUIRED_ENVIRONMENT
        and environment.get("sys_flags")
        == {
            "safe_path": True,
            "no_user_site": True,
            "dont_write_bytecode": True,
        }
        and environment.get("sys_dont_write_bytecode") is True,
        f"seed {seed} {condition}: execution environment contract",
    )
    required_modules = {
        "rrct.post_change_closure_experiment": (
            "src/rrct/post_change_closure_experiment.py"
        ),
        "rrct.temporal_self_identity": "src/rrct/temporal_self_identity.py",
        "rrct.temporal_self_identity_experiment": (
            "src/rrct/temporal_self_identity_experiment.py"
        ),
        "rrct.unified_causal_loop_experiment": (
            "src/rrct/unified_causal_loop_experiment.py"
        ),
    }
    verified_modules = start.get("verified_rrct_module_paths")
    _require(
        isinstance(verified_modules, dict)
        and all(
            verified_modules.get(module) == relative
            for module, relative in required_modules.items()
        ),
        f"seed {seed} {condition}: verified RRCT module set",
    )
    _require(
        all(
            isinstance(relative, str) and relative in verified["source_sha256"]
            for relative in verified_modules.values()
        ),
        f"seed {seed} {condition}: RRCT module escaped frozen source",
    )
    _require(
        start.get("post_import_source_manifest_reverified") is True
        and start.get("post_import_loaded_rrct_modules_reverified") is True,
        f"seed {seed} {condition}: post-import source verification receipt",
    )
    receipt_binding_fields = {
        "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified[
            "selection_scan_manifest_sha256"
        ],
        "external_commitment_sha256": verified["external_commitment_sha256"],
    }
    for field, expected in receipt_binding_fields.items():
        _require(
            start.get(field) == expected,
            f"seed {seed} {condition}: start/{field}",
        )
        _require(
            finish.get(field) == expected,
            f"seed {seed} {condition}: finish/{field}",
        )
    _require(
        finish.get("environment_fingerprint_sha256") == environment_digest,
        f"seed {seed} {condition}: finish/environment fingerprint",
    )

    claims = start.get("claims")
    _require(isinstance(claims, dict), f"seed {seed} {condition}: claims receipt")
    claim_specs = (
        ("attempt", CLAIM_SCHEMA, attempt_id),
        ("seed", SEED_CLAIM_SCHEMA, None),
        ("condition", CLAIM_SCHEMA, attempt_id),
    )
    loaded_claims: dict[str, dict[str, Any]] = {}
    for label, schema, expected_attempt in claim_specs:
        relative = claims.get(f"{label}_relative_path")
        path = _safe_campaign_file(
            campaign_root, relative, f"{seed} {condition} {label} claim"
        )
        expected_sha = claims.get(f"{label}_sha256")
        _require(
            _is_sha256(expected_sha) and _sha256_file(path) == expected_sha,
            f"seed {seed} {condition}: {label} claim hash",
        )
        claim = _load_json(path)
        _require(
            path.read_bytes() == _runner_pretty_bytes(claim),
            f"seed {seed} {condition}: noncanonical {label} claim",
        )
        _require(
            claim.get("schema") == schema,
            f"seed {seed} {condition}: {label} claim schema",
        )
        _require(
            _claim_common_valid(claim, seed=seed, verified=verified),
            f"seed {seed} {condition}: {label} claim chain",
        )
        if expected_attempt is not None:
            _require(
                claim.get("attempt_id") == expected_attempt,
                f"seed {seed} {condition}: {label} attempt",
            )
        _require(
            claim.get("environment_fingerprint_sha256") == environment_digest,
            f"seed {seed} {condition}: {label} claim/environment",
        )
        loaded_claims[label] = claim
    attempt_claim = loaded_claims["attempt"]
    condition_claim = loaded_claims["condition"]
    seed_claim = loaded_claims["seed"]
    _require(
        claims.get("attempt_relative_path") == f"_attempt_claims/{attempt_id}.json",
        f"seed {seed} {condition}: attempt claim path",
    )
    _require(
        claims.get("seed_relative_path") == f"_seed_claims/seed-{seed}.json",
        f"seed {seed} {condition}: seed claim path",
    )
    _require(
        claims.get("condition_relative_path")
        == f"_condition_claims/seed-{seed}--{condition}.json",
        f"seed {seed} {condition}: condition claim path",
    )
    _require(
        attempt_claim.get("condition_id") == condition,
        f"seed {seed} {condition}: attempt condition",
    )
    _require(
        condition_claim.get("condition_id") == condition,
        f"seed {seed} {condition}: condition claim identity",
    )
    _require(
        condition_claim.get("history_policy") == specification["history_policy"],
        f"seed {seed} {condition}: condition claim policy",
    )
    _require(
        condition_claim.get("world_variant") == specification["world_variant"],
        f"seed {seed} {condition}: condition claim world",
    )
    _require(
        seed_claim.get("reserved_paired_conditions") == sorted(CONDITIONS),
        f"seed {seed}: seed claim reservation",
    )
    _require(
        seed_claim.get("state") == "paired_seed_consumed_before_first_rng_construction",
        f"seed {seed}: seed claim state",
    )
    _require(
        attempt_claim.get("state") == "consumed_before_rng_construction",
        f"seed {seed} {condition}: attempt claim state",
    )
    _require(
        condition_claim.get("state")
        == "seed_condition_consumed_before_rng_construction",
        f"seed {seed} {condition}: condition claim state",
    )
    _require(
        claims.get("all_claims_precede_rng_construction") is True,
        f"seed {seed} {condition}: claim timing",
    )
    _require(
        isinstance(claims.get("seed_claim_created_by_this_arm"), bool),
        f"seed {seed} {condition}: seed-creator flag type",
    )
    started_at = _parse_utc(
        start.get("started_at_utc"), f"seed {seed} {condition} start"
    )
    commitment_at = _parse_utc(
        verified["external_persistent_file"]["committed_at_utc"],
        "external commitment",
    )
    _require(
        started_at >= commitment_at,
        f"seed {seed} {condition}: start predates external commitment",
    )
    completed_at = _parse_utc(
        finish.get("completed_at_utc"), f"seed {seed} {condition} finish"
    )
    _require(
        completed_at >= started_at,
        f"seed {seed} {condition}: finish precedes start",
    )
    for label, claim in loaded_claims.items():
        claimed_at = _parse_utc(
            claim.get("claimed_at_utc"),
            f"seed {seed} {condition} {label} claim",
        )
        _require(
            commitment_at <= claimed_at <= started_at,
            f"seed {seed} {condition}: {label} claim chronology",
        )
    _require(
        start.get("source_archive_relative_path")
        == verified["freeze"]["source_archive"]["relative_path"]
        and start.get("source_archive_sha256") == verified["source_archive_sha256"],
        f"seed {seed} {condition}: source archive binding",
    )
    frozen_summary = summary.get("frozen_pilot")
    _require(
        isinstance(frozen_summary, dict), f"seed {seed} {condition}: frozen summary"
    )
    _require(
        frozen_summary.get("attempt_id") == attempt_id,
        f"seed {seed} {condition}: summary attempt",
    )
    _require(
        frozen_summary.get("condition_id") == condition,
        f"seed {seed} {condition}: summary condition",
    )
    _require(
        frozen_summary.get("rows_count") == finish.get("rows_count")
        and frozen_summary.get("rows_sha256") == finish.get("rows_sha256"),
        f"seed {seed} {condition}: summary/row binding",
    )
    _require(
        started_at
        <= _parse_utc(
            frozen_summary.get("completed_at_utc"),
            f"seed {seed} {condition} summary completion",
        )
        <= completed_at,
        f"seed {seed} {condition}: summary completion chronology",
    )
    summary_binding_fields = {
        **receipt_binding_fields,
        "environment_fingerprint_sha256": environment_digest,
    }
    for field, expected in summary_binding_fields.items():
        _require(
            frozen_summary.get(field) == expected,
            f"seed {seed} {condition}: summary/{field}",
        )
    for label, receipt in (("summary", frozen_summary), ("finish", finish)):
        _require(
            receipt.get("external_persistent_file")
            == verified["external_persistent_file"],
            f"seed {seed} {condition}: {label}/persistent external metadata",
        )
        _require(
            receipt.get("post_run_source_manifest_reverified") is True
            and receipt.get("post_run_loaded_rrct_modules_reverified") is True
            and receipt.get("post_run_source_set_sha256")
            == verified["source_set_sha256"],
            f"seed {seed} {condition}: {label}/post-run source receipt",
        )
    _require(
        start.get("external_persistent_file") == verified["external_persistent_file"],
        f"seed {seed} {condition}: persistent external commitment binding",
    )
    return {
        "attempt_id": attempt_id,
        "attempt_claim_relative_path": claims["attempt_relative_path"],
        "condition_claim_relative_path": claims["condition_relative_path"],
        "seed_claim_relative_path": claims["seed_relative_path"],
        "seed_claim_created_by_this_arm": claims["seed_claim_created_by_this_arm"],
        "seed_claim_first_attempt_id": seed_claim.get("first_attempt_id"),
        "seed_claim_first_condition_id": seed_claim.get("first_condition_id"),
        "environment": environment,
    }


def _vector_equal(cells: Mapping[str, Any], attribute: str) -> bool:
    values = [getattr(cells[name], attribute) for name in CONDITION_NAMES]
    return all(value == values[0] for value in values[1:])


def _latency(start: int | None, stop: int | None) -> int | None:
    if start is None or stop is None:
        return None
    return stop - start


def evaluate_seed(seed: int, cells: Mapping[str, Any]) -> dict[str, Any]:
    """Apply every predeclared per-seed scientific and safety endpoint."""

    _require(set(cells) == set(CONDITIONS), f"seed {seed}: six-cell mapping incomplete")
    kp, np, gp = cells["K_RPLUS"], cells["N_RPLUS"], cells["G_RPLUS"]
    km, nm, gm = cells["K_RMINUS"], cells["N_RMINUS"], cells["G_RMINUS"]

    universal = all(
        all(cell.integrity_checks.values())
        and cell.global_premature_count == 0
        and cell.global_stale_count == 0
        and cell.commit_after_quarantined_prior_count == 0
        for cell in cells.values()
    )
    rplus_grounding = bool(
        kp.target_fresh_on_before_commit == 1
        and kp.target_fresh_off_before_commit == 1
        and np.target_fresh_on_before_commit is not None
        and np.target_fresh_off_before_commit is not None
        and np.target_fresh_on_before_commit >= 2
        and np.target_fresh_off_before_commit >= 2
        and gp.target_fresh_on_before_commit is not None
        and gp.target_fresh_off_before_commit is not None
        and gp.target_fresh_on_before_commit >= 2
        and gp.target_fresh_off_before_commit >= 2
        and kp.target_episode_commits
        == np.target_episode_commits
        == gp.target_episode_commits
        == 1
    )
    rplus_prior_specificity = bool(
        kp.target_prior_digest is not None
        and kp.target_compatible
        and not kp.target_quarantine
        and kp.target_prior_source_key == kp.target_key
        and np.target_prior_digest is None
        and gp.target_prior_digest is not None
        and gp.target_quarantine
        and not gp.target_compatible
        and gp.target_prior_source_key != gp.target_key
    )
    rplus_comparison_values_present = all(
        value is not None
        for value in (
            kp.target_fresh_probes_before_commit,
            np.target_fresh_probes_before_commit,
            gp.target_fresh_probes_before_commit,
            kp.target_candidate_time,
            np.target_candidate_time,
            gp.target_candidate_time,
            kp.target_commit_time,
            np.target_commit_time,
            gp.target_commit_time,
            kp.target_authorization_time,
            np.target_authorization_time,
            gp.target_authorization_time,
        )
    )
    rplus_keyed_efficiency = bool(
        rplus_comparison_values_present
        and kp.target_fresh_probes_before_commit < np.target_fresh_probes_before_commit
        and kp.target_fresh_probes_before_commit < gp.target_fresh_probes_before_commit
        and kp.target_commit_time < np.target_commit_time
        and kp.target_commit_time < gp.target_commit_time
        and kp.target_authorization_time < np.target_authorization_time
        and kp.target_authorization_time < gp.target_authorization_time
    )
    rminus_fail_closed = all(
        cell.target_episode_commits == 0
        and cell.target_ordinary_authorization_count == 0
        and cell.target_authorization_time is None
        and cell.target_episode_count_after == cell.target_episode_count_before
        for cell in (km, nm, gm)
    )
    rminus_diagnosis = bool(
        km.target_quarantine
        and gm.target_quarantine
        and nm.target_prior_digest is None
        and nm.target_rejection_count >= 1
        and all(
            cell.target_candidate_rows > 0
            and cell.target_private_visible_rows == cell.target_candidate_rows
            for cell in (km, nm, gm)
        )
    )
    exogenous_yoking = _vector_equal(cells, "exogenous_sha256")
    variant_blind_pretarget = all(
        cells[f"{policy}_RPLUS"].pretarget_v040_sha256
        == cells[f"{policy}_RMINUS"].pretarget_v040_sha256
        for policy in ("K", "N", "G")
    )
    prequential_priors = bool(
        kp.target_prior_digest == km.target_prior_digest
        and gp.target_prior_digest == gm.target_prior_digest
    )
    same_target_key = len({cell.target_key for cell in cells.values()}) == 1
    criteria = {
        "S01_all_six_cell_integrity_and_universal_safety": universal,
        "S02_cross_policy_exogenous_yoking": exogenous_yoking,
        "S03_within_policy_world_variant_blind_before_target": (
            variant_blind_pretarget
        ),
        "S04_same_target_structural_key_all_cells": same_target_key,
        "S05_prequential_prior_receipts_match_across_rplus_rminus": (
            prequential_priors
        ),
        "S06_rplus_exact_fresh_grounding_pattern": rplus_grounding,
        "S07_rplus_prior_specificity_pattern": rplus_prior_specificity,
        "S08_rplus_keyed_faster_than_withheld_and_generic": (rplus_keyed_efficiency),
        "S09_rminus_zero_authorization_and_episode_commit": rminus_fail_closed,
        "S10_rminus_quarantine_rejection_and_private_visibility": (rminus_diagnosis),
    }
    return {
        "seed": seed,
        "criteria": criteria,
        "all_primary_endpoints_met": all(criteria.values()),
        "status": (
            "V0411_FROZEN_PILOT_SEED_PASS"
            if all(criteria.values())
            else "V0411_FROZEN_PILOT_SEED_FAIL"
        ),
        "conditions": {name: cells[name].public() for name in CONDITION_NAMES},
        "primary_contrasts": {
            "fresh_probes_before_commit": {
                name: cells[name].target_fresh_probes_before_commit
                for name in ("K_RPLUS", "N_RPLUS", "G_RPLUS")
            },
            "candidate_to_commit_latency": {
                name: _latency(
                    cells[name].target_candidate_time,
                    cells[name].target_commit_time,
                )
                for name in ("K_RPLUS", "N_RPLUS", "G_RPLUS")
            },
            "candidate_to_first_authorization_latency": {
                name: _latency(
                    cells[name].target_candidate_time,
                    cells[name].target_authorization_time,
                )
                for name in ("K_RPLUS", "N_RPLUS", "G_RPLUS")
            },
            "rminus_authorizations": {
                name: cells[name].target_ordinary_authorization_count
                for name in ("K_RMINUS", "N_RMINUS", "G_RMINUS")
            },
            "rminus_episode_commits": {
                name: cells[name].target_episode_commits
                for name in ("K_RMINUS", "N_RMINUS", "G_RMINUS")
            },
        },
        "descriptive_windows_noncriterion": {
            "phase_start_first_128": {
                name: {
                    "task_opportunity_regret_sum": cells[
                        name
                    ].target_first_128_task_opportunity_regret_sum,
                    "realized_return_sum": cells[
                        name
                    ].target_first_128_realized_return_sum,
                }
                for name in CONDITION_NAMES
            },
            "exploratory_candidate_aligned_first_128": {
                "exploratory_noncriterion": True,
                "conditions": {
                    name: {
                        "transition_range": [
                            cells[name].target_candidate_time,
                            cells[name].target_candidate_time + 127,
                        ],
                        "task_opportunity_regret_sum": cells[
                            name
                        ].target_candidate_128_task_opportunity_regret_sum,
                        "realized_return_sum": cells[
                            name
                        ].target_candidate_128_realized_return_sum,
                    }
                    for name in CONDITION_NAMES
                },
            },
        },
    }


def cohort_decision(
    seed_audits: Sequence[Mapping[str, Any]],
    expected_seeds: Sequence[int],
    *,
    topology_valid: bool,
    campaign_claim_chain_valid: bool,
) -> dict[str, bool]:
    """Return the all-four rule; useful independently in focused tests."""

    observed = [audit.get("seed") for audit in seed_audits]
    return {
        "C01_exact_four_registered_seeds": (
            len(seed_audits) == 4
            and len(expected_seeds) == 4
            and sorted(observed) == sorted(expected_seeds)
        ),
        "C02_exact_24_arm_topology": bool(topology_valid),
        "C03_campaign_freeze_claim_artifact_chains": bool(campaign_claim_chain_valid),
        "C04_all_four_seeds_meet_every_primary_endpoint": bool(
            len(seed_audits) == 4
            and all(
                audit.get("all_primary_endpoints_met") is True for audit in seed_audits
            )
        ),
    }


def audit_campaign(
    project_root: Path, campaign_root: Path | None = None
) -> dict[str, Any]:
    verified = verify_freeze(project_root)
    project_root = verified["project_root"]
    verified.update(verify_seed_selection(project_root, verified))
    verified.update(verify_external_commitment(project_root, verified))
    if campaign_root is None:
        campaign_root = project_root / "validation" / DEFAULT_CAMPAIGN_NAME
    supplied_campaign_root = Path(os.path.abspath(os.fspath(campaign_root)))
    campaign_root = supplied_campaign_root.resolve(strict=True)
    _require(
        supplied_campaign_root == campaign_root
        and campaign_root.is_dir()
        and not campaign_root.is_symlink()
        and campaign_root
        == (project_root / "validation" / DEFAULT_CAMPAIGN_NAME).resolve(strict=False),
        "campaign root is not the canonical in-project campaign directory",
    )
    campaign_receipt_path = campaign_root / "campaign_receipt.json"
    _require(
        campaign_receipt_path.is_file() and not campaign_receipt_path.is_symlink(),
        "canonical campaign receipt missing/symlinked",
    )
    top_level_entries = {path.name for path in campaign_root.iterdir()}
    required_entries = {
        "campaign_receipt.json",
        "_attempt_claims",
        "_seed_claims",
        "_condition_claims",
        "pairs",
    }
    allowed_audit_outputs = {
        "independent_campaign_audit.json",
        "independent_campaign_audit.json.sha256",
    }
    _require(
        required_entries.issubset(top_level_entries)
        and top_level_entries <= required_entries | allowed_audit_outputs,
        "canonical campaign has extra/missing top-level entries",
    )
    campaign_receipt = _load_json(campaign_receipt_path)
    _require(
        campaign_receipt_path.read_bytes() == _runner_pretty_bytes(campaign_receipt),
        "campaign receipt is not canonical JSON",
    )
    campaign_invariants = {
        "schema": CAMPAIGN_SCHEMA,
        "version": VERSION,
        "scientific_status": PILOT_STATUS,
        "confirmatory": False,
        "canonical_campaign_root": (f"validation/{DEFAULT_CAMPAIGN_NAME}"),
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
        "conditions": CONDITIONS,
    }
    for key, value in campaign_invariants.items():
        _require(
            campaign_receipt.get(key) == value, f"campaign receipt mismatch: {key}"
        )
    _require(
        _parse_utc(campaign_receipt.get("created_at_utc"), "campaign creation")
        >= _parse_utc(
            verified["external_persistent_file"]["committed_at_utc"],
            "external commitment",
        ),
        "campaign predates external commitment",
    )
    campaign_environment_sha256 = campaign_receipt.get("environment_fingerprint_sha256")
    _require(
        _is_sha256(campaign_environment_sha256),
        "campaign environment fingerprint digest",
    )
    topology = verify_topology(campaign_root, verified["seeds"])

    frozen_context = {
        "freeze_sha256": verified["freeze_sha256"],
        "source_sha256": verified["source_sha256"],
        "source_set_sha256": verified["source_set_sha256"],
        "source_archive_sha256": verified["source_archive_sha256"],
        "registry_sha256": verified["registry_sha256"],
    }
    seed_audits: list[dict[str, Any]] = []
    attempt_claim_paths: set[str] = set()
    condition_claim_paths: set[str] = set()
    seed_claim_paths: set[str] = set()
    configuration_by_condition: dict[str, set[str]] = {
        condition: set() for condition in CONDITIONS
    }
    environment_digests: set[str] = set()
    for seed in verified["seeds"]:
        cells: dict[str, Any] = {}
        arm_chains: dict[str, dict[str, Any]] = {}
        seed_creator_arms: list[str] = []
        for condition in CONDITION_NAMES:
            root = campaign_root / "pairs" / f"seed-{seed}" / condition
            chain = verify_arm_chain(
                campaign_root,
                root,
                seed=seed,
                condition=condition,
                verified=verified,
            )
            arm_chains[condition] = chain
            attempt_claim_paths.add(chain["attempt_claim_relative_path"])
            condition_claim_paths.add(chain["condition_claim_relative_path"])
            seed_claim_paths.add(chain["seed_claim_relative_path"])
            if chain["seed_claim_created_by_this_arm"]:
                seed_creator_arms.append(condition)
            _require(
                isinstance(chain["environment"], dict) and bool(chain["environment"]),
                f"seed {seed} {condition}: missing execution environment",
            )
            environment_digests.add(_canonical_sha256(chain["environment"]))
            cell = REPLAY._audit_cell(
                root,
                condition,
                frozen_context=frozen_context,
            )
            _require(cell.seed == seed, f"seed {seed} {condition}: replay seed")
            configuration_by_condition[condition].add(cell.condition_config_sha256)
            cells[condition] = cell
        _require(
            len(seed_creator_arms) == 1,
            f"seed {seed}: exactly one arm must create seed claim",
        )
        creator = seed_creator_arms[0]
        _require(
            arm_chains[creator]["seed_claim_first_attempt_id"]
            == arm_chains[creator]["attempt_id"]
            and arm_chains[creator]["seed_claim_first_condition_id"] == creator,
            f"seed {seed}: seed-claim creator/first arm mismatch",
        )
        seed_result = evaluate_seed(seed, cells)
        seed_result["claim_chains"] = arm_chains
        seed_audits.append(seed_result)

    expected_attempt_paths = {
        f"_attempt_claims/{name}"
        for name in _entry_names(campaign_root / "_attempt_claims")
    }
    expected_condition_paths = {
        f"_condition_claims/{name}"
        for name in _entry_names(campaign_root / "_condition_claims")
    }
    expected_seed_paths = {
        f"_seed_claims/{name}" for name in _entry_names(campaign_root / "_seed_claims")
    }
    claim_paths_exact = bool(
        attempt_claim_paths == expected_attempt_paths
        and condition_claim_paths == expected_condition_paths
        and seed_claim_paths == expected_seed_paths
    )
    configuration_stable = all(
        len(values) == 1 for values in configuration_by_condition.values()
    )
    environment_consistent = len(environment_digests) == 1
    _require(
        environment_digests == {campaign_environment_sha256},
        "arm environments do not match campaign environment binding",
    )
    for relative, expected_sha256 in verified["source_sha256"].items():
        path = _safe_project_file(
            project_root, relative, f"post-replay frozen source {relative}"
        )
        _require(
            _sha256_file(path) == expected_sha256,
            f"frozen source changed during/before completed audit: {relative}",
        )
    post_replay_source_recheck = True
    decisions = cohort_decision(
        seed_audits,
        verified["seeds"],
        topology_valid=True,
        campaign_claim_chain_valid=(
            claim_paths_exact
            and configuration_stable
            and environment_consistent
            and post_replay_source_recheck
        ),
    )
    all_met = all(decisions.values())
    return {
        "schema": "rrct.v0411.frozen_pilot_campaign.independent_audit.v1",
        "version": VERSION,
        "scientific_status": PILOT_STATUS,
        "confirmatory": False,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": project_root.as_posix(),
        "campaign_root": campaign_root.as_posix(),
        "freeze_sha256": verified["freeze_sha256"],
        "source_set_sha256": verified["source_set_sha256"],
        "source_archive_sha256": verified["source_archive_sha256"],
        "seed_registry_sha256": verified["registry_sha256"],
        "seed_selection_receipt_sha256": verified["selection_receipt_sha256"],
        "seed_selection_scan_manifest_sha256": verified[
            "selection_scan_manifest_sha256"
        ],
        "selection_surface_file_count": verified["selection_surface_file_count"],
        "external_commitment_sha256": verified["external_commitment_sha256"],
        "external_persistent_file": verified["external_persistent_file"],
        "registered_seeds": list(verified["seeds"]),
        "topology": topology,
        "claim_paths_exact": claim_paths_exact,
        "condition_configuration_stable_across_seeds": configuration_stable,
        "execution_environment_consistent_across_24_arms": (environment_consistent),
        "post_replay_current_source_matches_freeze": (post_replay_source_recheck),
        "seed_audits": seed_audits,
        "total_sealed_rows": sum(
            condition["row_count"]
            for seed_audit in seed_audits
            for condition in seed_audit["conditions"].values()
        ),
        "cohort_criteria": decisions,
        "all_four_cohort_rule_met": all_met,
        "status": (
            "V0411_FROZEN_EXPLORATORY_PILOT_COHORT_PASS"
            if all_met
            else "V0411_FROZEN_EXPLORATORY_PILOT_COHORT_FAIL"
        ),
        "interpretation_boundary": (
            "Independent standard-library replay of the prospectively frozen "
            "four-seed, six-arm exploratory pilot. A pass supports replication "
            "of the bounded temporal-identity memory mechanism in this simulator. "
            "It is not confirmatory evidence, external replication, a matched-"
            "controller necessity result, or evidence of subjective awareness."
        ),
    }


def _write_report(path: Path, report: Mapping[str, Any]) -> str:
    encoded = (
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the frozen RRCT v0.41.1 four-seed pilot campaign."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = audit_campaign(args.project_root, args.campaign_root)
        output_sha256 = None
        if args.output is not None:
            output_sha256 = _write_report(args.output.resolve(), report)
        display = {
            "status": report["status"],
            "all_four_cohort_rule_met": report["all_four_cohort_rule_met"],
            "registered_seeds": report["registered_seeds"],
            "total_sealed_rows": report["total_sealed_rows"],
            "cohort_criteria": report["cohort_criteria"],
            "output": (
                None if args.output is None else args.output.resolve().as_posix()
            ),
            "output_sha256": output_sha256,
        }
        print(json.dumps(display, indent=2, sort_keys=True), flush=True)
        return 0 if report["all_four_cohort_rule_met"] else 1
    except Exception as exc:  # noqa: BLE001 - CLI must emit a fail-closed receipt.
        failure = {
            "schema": "rrct.v0411.frozen_pilot_campaign.independent_audit_failure.v1",
            "version": VERSION,
            "scientific_status": PILOT_STATUS,
            "confirmatory": False,
            "audited_at_utc": datetime.now(timezone.utc).isoformat(),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "status": "V0411_FROZEN_PILOT_CAMPAIGN_AUDIT_ERROR",
        }
        if args.output is not None:
            failure["output_sha256"] = _write_report(args.output.resolve(), failure)
        print(
            json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr, flush=True
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
