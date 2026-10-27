from __future__ import annotations

import hashlib
import importlib.util
import json
import tarfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FREEZE_MODULE_PATH = PROJECT_ROOT / "validation/freeze_v0411_source.py"
SPEC = importlib.util.spec_from_file_location("freeze_v0411_source", FREEZE_MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
freeze = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freeze)


CONDITIONS = {
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


def _write_fixture_file(root: Path, relative: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if relative == "validation/V0_41_1_DEVELOPMENT_CONDITIONS.json":
        value = {
            "schema": "rrct.v0411.development_condition_registry.v1",
            "version": freeze.VERSION,
            "scientific_status": "exposed_development_only_not_frozen",
            "development_seed": 41011,
            "conditions": CONDITIONS,
        }
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    elif relative == "validation/V0_41_1_SEED_REGISTRY.json":
        value = {
            "schema": freeze.REGISTRY_SCHEMA,
            "version": freeze.VERSION,
            "scientific_status": "fresh_pilot_seed_registry_selected_unopened",
            "registry_state": "unopened",
            "cohort_opened": False,
            "fresh_pilot_seeds": [100_041_101, 100_041_102, 100_041_103, 100_041_104],
            "conditions": CONDITIONS,
            "opened_seed_condition_pairs": [],
            "seed_selection_receipt_relative_path": (
                "validation/V0_41_1_SEED_SELECTION_RECEIPT.json"
            ),
            "seed_selection_scan_manifest_relative_path": (
                "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
            ),
            "seed_selection_scan_manifest_sha256": "0" * 64,
        }
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    elif relative in {
        "validation/V0_41_1_DEVELOPMENT_AUDIT.json",
        "validation/v0.41.1_development_matrix_seed_41011/independent_science_audit.json",
    }:
        value = {
            "schema": "rrct.v041.development_matrix.independent_audit.v1",
            "seed": 41011,
            "development_only": True,
            "all_criteria_met": True,
        }
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    elif relative == (
        "validation/v0.41.1_development_matrix_seed_41011/integrity_yoking_audit.json"
    ):
        value = {
            "schema": "rrct.v041.development_integrity_yoking_audit.v1",
            "seed": 41011,
            "development_only": True,
            "all_checks_pass": True,
        }
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    elif (
        relative == "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
        or path.suffix == ".json"
    ):
        path.write_text("{}\n", encoding="utf-8")
    elif path.suffix == ".py":
        path.write_text('"""freeze fixture"""\n', encoding="utf-8")
    else:
        path.write_text(f"fixture for {relative}\n", encoding="utf-8")


def _write_selection_bundle(root: Path) -> None:
    scan_path = root / "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json"
    receipt_path = root / "validation/V0_41_1_SEED_SELECTION_RECEIPT.json"
    registry_path = root / "validation/V0_41_1_SEED_REGISTRY.json"
    selector_path = root / "validation/select_v0411_seeds.py"
    files = [
        {
            "relative_path": "validation/select_v0411_seeds.py",
            "size_bytes": selector_path.stat().st_size,
            "sha256": hashlib.sha256(selector_path.read_bytes()).hexdigest(),
        }
    ]
    scan = {
        "schema": freeze.SCAN_SCHEMA,
        "version": freeze.VERSION,
        "scientific_status": "pre_registry_complete_project_evidence_scan",
        "scan_rule": "standalone_decimal_occurrences_not_adjacent_to_ascii_digits",
        "file_count": 1,
        "files": files,
        "scan_surface_sha256": freeze._canonical_sha256(files),
    }
    scan_path.write_text(json.dumps(scan, sort_keys=True) + "\n", encoding="utf-8")
    scan_sha = hashlib.sha256(scan_path.read_bytes()).hexdigest()
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["seed_selection_scan_manifest_sha256"] = scan_sha
    registry_path.write_text(
        json.dumps(registry, sort_keys=True) + "\n", encoding="utf-8"
    )
    registry_sha = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    candidates = [
        *registry["fresh_pilot_seeds"],
        800_041_101,
        800_041_102,
        800_041_103,
        800_041_104,
        800_041_105,
        800_041_106,
        800_041_107,
        800_041_108,
    ]
    records = [
        {
            "generation_index": index,
            "candidate": candidate,
            "standalone_decimal_occurrence_count": 0 if index < 4 else 1,
            "occurrence_paths": [] if index < 4 else ["historical.txt"],
            "zero_occurrence": index < 4,
        }
        for index, candidate in enumerate(candidates)
    ]
    receipt = {
        "schema": freeze.RECEIPT_SCHEMA,
        "version": freeze.VERSION,
        "scientific_status": "preoutcome_seed_selection_complete_unopened",
        "selection_method": "single_nonrepeated_secrets_randbelow_draw_loop",
        "draw_expression": "secrets.randbelow(800_000_000) + 100_000_000",
        "candidate_count": 12,
        "candidate_generation_order": candidates,
        "randbelow_call_count": 12,
        "duplicate_draw_count": 0,
        "scan_rule": "standalone_decimal_occurrences_not_adjacent_to_ascii_digits",
        "candidate_scan_records": records,
        "selection_rule": (
            "first_four_candidates_in_generation_order_with_zero_occurrences"
        ),
        "selected_fresh_pilot_seeds": registry["fresh_pilot_seeds"],
        "selection_state": "unopened",
        "registry_state_at_selection": "unopened",
        "cohort_opened": False,
        "opened_seed_condition_pairs": [],
        "rows_or_outcomes_opened": 0,
        "no_redraw_after_scan": True,
        "wall_clock_time_in_record": False,
        "scan_manifest": {
            "relative_path": "validation/V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json",
            "schema": freeze.SCAN_SCHEMA,
            "sha256": scan_sha,
            "file_count": 1,
            "scan_surface_sha256": scan["scan_surface_sha256"],
        },
        "selector": {
            "relative_path": "validation/select_v0411_seeds.py",
            "sha256": hashlib.sha256(selector_path.read_bytes()).hexdigest(),
        },
        "seed_registry": {
            "relative_path": "validation/V0_41_1_SEED_REGISTRY.json",
            "schema": freeze.REGISTRY_SCHEMA,
            "sha256": registry_sha,
            "registry_state": "unopened",
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_preexecution(root: Path) -> None:
    production = {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in freeze.PRODUCTION_SOURCE_PATHS
    }
    value = {
        "schema": freeze.PREEXECUTION_SCHEMA,
        "version": freeze.VERSION,
        "scientific_status": "preoutcome_all_checks_pass",
        "all_checks_pass": True,
        "cohort_opened": False,
        "fresh_seed_state": "unopened",
        "errors": [],
        "failures": [],
        "failed_checks": [],
        "checks": {key: True for key in freeze.REQUIRED_PREEXECUTION_CHECKS},
        "test_command": "test-only freeze fixture",
        "passed_test_count": 1,
        "dependency_lock_sha256": hashlib.sha256(
            (root / "uv.lock").read_bytes()
        ).hexdigest(),
        "production_source_sha256": production,
        "production_source_set_sha256": freeze._canonical_sha256(production),
        "required_environment": freeze.REQUIRED_ENVIRONMENT,
    }
    path = root / "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _populate_project(root: Path) -> None:
    for relative in freeze.REQUIRED_RELATIVE_PATHS:
        _write_fixture_file(root, relative)
    for relative in freeze.PRODUCTION_SOURCE_PATHS:
        _write_fixture_file(root, relative)
    # Exercise discovery beyond the exact required list.
    _write_fixture_file(root, "src/rrct/__init__.py")
    _write_fixture_file(root, "src/rrct/additional_scientific_module.py")
    _write_fixture_file(root, "tests/test_additional_scientific_surface.py")
    (root / "tests/__pycache__").mkdir(parents=True, exist_ok=True)
    (root / "tests/__pycache__/ignored.py").write_text(
        "ignored = True\n", encoding="utf-8"
    )
    _write_selection_bundle(root)
    _write_preexecution(root)


def _assert_no_outputs(root: Path) -> None:
    validation = root / "validation"
    assert not (validation / freeze.FREEZE_NAME).exists()
    assert not (validation / freeze.FREEZE_CHECKSUM_NAME).exists()
    assert not (validation / freeze.TEMP_ARCHIVE_NAME).exists()
    assert not list(validation.glob(f"{freeze.ARCHIVE_PREFIX}*.tar.gz"))


def test_missing_required_input_fails_before_any_output(tmp_path: Path) -> None:
    _populate_project(tmp_path)
    missing = tmp_path / "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
    missing.unlink()

    with pytest.raises(FileNotFoundError, match="PREEXECUTION_VALIDATION"):
        freeze.create_freeze(tmp_path)

    _assert_no_outputs(tmp_path)


def test_identical_inputs_make_identical_content_addressed_freezes(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _populate_project(first)
    _populate_project(second)

    first_result = freeze.create_freeze(first)
    second_result = freeze.create_freeze(second)

    first_archive = Path(first_result["source_archive"])
    second_archive = Path(second_result["source_archive"])
    assert first_archive.name == second_archive.name
    assert first_archive.read_bytes() == second_archive.read_bytes()
    assert (
        first_result["source_archive_sha256"]
        == hashlib.sha256(first_archive.read_bytes()).hexdigest()
    )

    first_manifest = first / "validation" / freeze.FREEZE_NAME
    second_manifest = second / "validation" / freeze.FREEZE_NAME
    assert first_manifest.read_bytes() == second_manifest.read_bytes()
    assert (first / "validation" / freeze.FREEZE_CHECKSUM_NAME).read_bytes() == (
        second / "validation" / freeze.FREEZE_CHECKSUM_NAME
    ).read_bytes()

    payload = json.loads(first_manifest.read_text(encoding="utf-8"))
    assert payload["scientific_source_sha256"][
        "src/rrct/additional_scientific_module.py"
    ]
    assert payload["scientific_source_sha256"][
        "tests/test_additional_scientific_surface.py"
    ]
    assert not any(
        "__pycache__" in name for name in payload["scientific_source_sha256"]
    )

    with tarfile.open(first_archive, mode="r:gz") as archive:
        members = archive.getmembers()
    names = [member.name for member in members]
    assert names == sorted(names)
    assert all(member.isfile() for member in members)
    assert all(member.mtime == 0 for member in members)
    assert all(member.uid == 0 and member.gid == 0 for member in members)
    assert all(member.mode == 0o644 for member in members)
    assert not any(name.endswith("sealed_rows.jsonl") for name in names)


def test_freeze_is_exclusive_and_does_not_claim_or_open_seeds(
    tmp_path: Path,
) -> None:
    _populate_project(tmp_path)
    registry_path = tmp_path / "validation/V0_41_1_SEED_REGISTRY.json"
    registry_before = registry_path.read_bytes()

    result = freeze.create_freeze(tmp_path)
    freeze_path = Path(result["freeze_path"])
    archive_path = Path(result["source_archive"])
    freeze_before = freeze_path.read_bytes()
    archive_before = archive_path.read_bytes()

    with pytest.raises(FileExistsError, match="already exists"):
        freeze.create_freeze(tmp_path)

    assert freeze_path.read_bytes() == freeze_before
    assert archive_path.read_bytes() == archive_before
    assert registry_path.read_bytes() == registry_before
    payload = json.loads(freeze_before)
    assert payload["confirmatory"] is False
    assert payload["fresh_seed_state_at_freeze"] == "unopened"
    assert payload["cohort_opened_at_freeze"] is False
    assert payload["seed_selection_performed_by_freeze"] is False
    assert payload["seed_claims_written_by_freeze"] == 0
    assert payload["rows_or_outcomes_opened_by_freeze"] == 0
    assert payload["condition_matrix"] == CONDITIONS
    assert payload["condition_names"] == sorted(CONDITIONS)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"registry_state": "opened"}, "registry_state"),
        ({"cohort_opened": True}, "cohort_opened"),
        (
            {"opened_seed_condition_pairs": [[100_041_101, "K_RPLUS"]]},
            "opened_seed_condition_pairs",
        ),
        (
            {
                "fresh_pilot_seeds": [
                    100_041_101,
                    100_041_101,
                    100_041_103,
                    100_041_104,
                ]
            },
            "must be unique",
        ),
    ],
)
def test_registry_must_be_explicitly_unopened(
    tmp_path: Path, mutation: dict[str, object], message: str
) -> None:
    _populate_project(tmp_path)
    registry_path = tmp_path / "validation/V0_41_1_SEED_REGISTRY.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry.update(mutation)
    registry_path.write_text(json.dumps(registry) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        freeze.create_freeze(tmp_path)

    _assert_no_outputs(tmp_path)


def test_registry_conditions_must_exactly_match_development_matrix(
    tmp_path: Path,
) -> None:
    _populate_project(tmp_path)
    registry_path = tmp_path / "validation/V0_41_1_SEED_REGISTRY.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["conditions"]["K_RPLUS"]["history_policy"] = "generic"
    registry_path.write_text(json.dumps(registry) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="exactly equal"):
        freeze.create_freeze(tmp_path)

    _assert_no_outputs(tmp_path)


def test_development_audit_must_be_passing_exact_independent_copy(
    tmp_path: Path,
) -> None:
    _populate_project(tmp_path)
    canonical_path = tmp_path / "validation/V0_41_1_DEVELOPMENT_AUDIT.json"
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    canonical["all_criteria_met"] = False
    canonical_path.write_text(json.dumps(canonical) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="exact byte copy"):
        freeze.create_freeze(tmp_path)

    _assert_no_outputs(tmp_path)


def test_preexecution_validation_must_be_all_pass(tmp_path: Path) -> None:
    _populate_project(tmp_path)
    preexecution = tmp_path / "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
    value = json.loads(preexecution.read_text(encoding="utf-8"))
    value["all_checks_pass"] = False
    preexecution.write_text(json.dumps(value) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="mismatch: all_checks_pass"):
        freeze.create_freeze(tmp_path)

    _assert_no_outputs(tmp_path)
