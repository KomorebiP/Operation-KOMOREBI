"""Focused fail-closed tests for the v0.41.1 frozen pilot runner."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import multiprocessing
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = PROJECT_ROOT / "validation/run_v041_frozen_seed.py"


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "test_run_v041_frozen_seed",
        RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load v0.41.1 frozen runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUNNER = _load_runner()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _frozen_fixture_root(tmp_path: Path, seeds: list[int]) -> Path:
    if len(seeds) != 4 or len(set(seeds)) != 4:
        raise ValueError("fixture requires exactly four unique seeds")
    root = tmp_path / "project"
    copied_paths = (
        *RUNNER.MANDATORY_FROZEN_SOURCE_PATHS,
        "validation/select_v0411_seeds.py",
        "uv.lock",
    )
    for relative in copied_paths:
        source = PROJECT_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    production_hashes = {
        relative: _sha256(root / relative)
        for relative in RUNNER.MANDATORY_FROZEN_SOURCE_PATHS[:3]
    }
    preexecution_path = root / "validation/V0_41_1_PREEXECUTION_VALIDATION.json"
    preexecution = {
        "schema": "rrct.v0411.preexecution_validation.v1",
        "version": RUNNER.VERSION,
        "scientific_status": "preoutcome_all_checks_pass",
        "all_checks_pass": True,
        "cohort_opened": False,
        "fresh_seed_state": "unopened",
        "errors": [],
        "failures": [],
        "failed_checks": [],
        "checks": {key: True for key in RUNNER.REQUIRED_PREEXECUTION_CHECKS},
        "test_command": "test-only prospective runner fixture",
        "passed_test_count": 1,
        "dependency_lock_sha256": _sha256(root / "uv.lock"),
        "production_source_sha256": production_hashes,
        "production_source_set_sha256": RUNNER._canonical_sha256(production_hashes),
        "required_environment": {
            "environment": RUNNER.REQUIRED_ENVIRONMENT,
            "python_flags": RUNNER.REQUIRED_PYTHON_FLAGS,
        },
    }
    _write_json(preexecution_path, preexecution)

    scan_path = root / "validation" / RUNNER.SELECTION_SCAN_MANIFEST_NAME
    selector_relative = "validation/select_v0411_seeds.py"
    scan_files = [
        {
            "relative_path": selector_relative,
            "size_bytes": (root / selector_relative).stat().st_size,
            "sha256": _sha256(root / selector_relative),
        }
    ]
    scan_manifest = {
        "schema": RUNNER.SELECTION_SCAN_MANIFEST_SCHEMA,
        "version": RUNNER.VERSION,
        "scientific_status": "pre_registry_complete_project_evidence_scan",
        "scan_rule": RUNNER.SELECTION_SCAN_RULE,
        "file_count": len(scan_files),
        "files": scan_files,
        "scan_surface_sha256": RUNNER._canonical_sha256(scan_files),
        "project_surface_policy": {},
        "excluded_entries": [],
    }
    _write_json(scan_path, scan_manifest)
    scan_sha256 = _sha256(scan_path)

    registry_path = root / "validation" / RUNNER.REGISTRY_NAME
    registry = {
        "schema": RUNNER.REGISTRY_SCHEMA,
        "version": RUNNER.VERSION,
        "scientific_status": "fresh_pilot_seed_registry_selected_unopened",
        "registry_state": "unopened",
        "cohort_opened": False,
        "fresh_pilot_seeds": seeds,
        "conditions": RUNNER.CONDITIONS,
        "opened_seed_condition_pairs": [],
        "seed_selection_receipt_relative_path": (
            f"validation/{RUNNER.SELECTION_RECEIPT_NAME}"
        ),
        "seed_selection_scan_manifest_relative_path": (
            f"validation/{RUNNER.SELECTION_SCAN_MANIFEST_NAME}"
        ),
        "seed_selection_scan_manifest_sha256": scan_sha256,
    }
    _write_json(registry_path, registry)
    registry_sha256 = _sha256(registry_path)

    candidates = [
        *seeds,
        800_000_001,
        800_000_002,
        800_000_003,
        800_000_004,
        800_000_005,
        800_000_006,
        800_000_007,
        800_000_008,
    ]
    candidate_records = [
        {
            "generation_index": index,
            "candidate": candidate,
            "standalone_decimal_occurrence_count": 0 if index < 4 else 1,
            "occurrence_paths": [] if index < 4 else ["historical.txt"],
            "zero_occurrence": index < 4,
        }
        for index, candidate in enumerate(candidates)
    ]
    receipt_path = root / "validation" / RUNNER.SELECTION_RECEIPT_NAME
    receipt = {
        "schema": RUNNER.SELECTION_RECEIPT_SCHEMA,
        "version": RUNNER.VERSION,
        "scientific_status": "preoutcome_seed_selection_complete_unopened",
        "selection_method": "single_nonrepeated_secrets_randbelow_draw_loop",
        "draw_expression": RUNNER.SELECTION_DRAW_EXPRESSION,
        "candidate_count": 12,
        "candidate_generation_order": candidates,
        "randbelow_call_count": 12,
        "duplicate_draw_count": 0,
        "scan_rule": RUNNER.SELECTION_SCAN_RULE,
        "candidate_scan_records": candidate_records,
        "selection_rule": (
            "first_four_candidates_in_generation_order_with_zero_occurrences"
        ),
        "selected_fresh_pilot_seeds": seeds,
        "selection_state": "unopened",
        "registry_state_at_selection": "unopened",
        "cohort_opened": False,
        "opened_seed_condition_pairs": [],
        "rows_or_outcomes_opened": 0,
        "no_redraw_after_scan": True,
        "wall_clock_time_in_record": False,
        "scan_manifest": {
            "relative_path": f"validation/{RUNNER.SELECTION_SCAN_MANIFEST_NAME}",
            "schema": RUNNER.SELECTION_SCAN_MANIFEST_SCHEMA,
            "sha256": scan_sha256,
            "file_count": len(scan_files),
            "scan_surface_sha256": scan_manifest["scan_surface_sha256"],
        },
        "selector": {
            "relative_path": selector_relative,
            "sha256": _sha256(root / selector_relative),
        },
        "seed_registry": {
            "relative_path": f"validation/{RUNNER.REGISTRY_NAME}",
            "schema": RUNNER.REGISTRY_SCHEMA,
            "sha256": registry_sha256,
            "registry_state": "unopened",
        },
    }
    _write_json(receipt_path, receipt)
    receipt_sha256 = _sha256(receipt_path)

    archive_path = root / "validation" / "fixture-frozen-source.tar.gz"
    archive_path.write_bytes(b"test-only frozen source archive\n")
    source_hashes = {
        relative: _sha256(root / relative)
        for relative in (*copied_paths, preexecution_path.relative_to(root).as_posix())
    }
    freeze = {
        "schema": RUNNER.FREEZE_SCHEMA,
        "version": RUNNER.VERSION,
        "scientific_status": RUNNER.FREEZE_SCIENTIFIC_STATUS,
        "campaign_stage": "fresh_pilot",
        "confirmatory": False,
        "scientific_source_sha256": source_hashes,
        "scientific_source_set_sha256": RUNNER._canonical_sha256(source_hashes),
        "source_archive": {
            "relative_path": archive_path.relative_to(root).as_posix(),
            "sha256": _sha256(archive_path),
            "member_count": len(source_hashes),
        },
        "seed_registry": {
            "relative_path": registry_path.relative_to(root).as_posix(),
            "sha256": registry_sha256,
            "schema": RUNNER.REGISTRY_SCHEMA,
            "registry_state_at_freeze": "unopened",
        },
        "seed_registry_sha256": registry_sha256,
        "seed_selection_scan_manifest": {
            "relative_path": scan_path.relative_to(root).as_posix(),
            "sha256": scan_sha256,
            "schema": RUNNER.SELECTION_SCAN_MANIFEST_SCHEMA,
        },
        "seed_selection_scan_manifest_sha256": scan_sha256,
        "seed_selection_receipt": {
            "relative_path": receipt_path.relative_to(root).as_posix(),
            "sha256": receipt_sha256,
            "schema": RUNNER.SELECTION_RECEIPT_SCHEMA,
            "selection_state_at_freeze": "unopened",
        },
        "seed_selection_receipt_sha256": receipt_sha256,
        "preexecution_validation": {
            "relative_path": preexecution_path.relative_to(root).as_posix(),
            "schema": "rrct.v0411.preexecution_validation.v1",
            "sha256": _sha256(preexecution_path),
            "scientific_status": "preoutcome_all_checks_pass",
            "all_checks_pass": True,
        },
        "preexecution_validation_sha256": _sha256(preexecution_path),
        "required_environment": {
            "environment": RUNNER.REQUIRED_ENVIRONMENT,
            "python_flags": RUNNER.REQUIRED_PYTHON_FLAGS,
        },
        "fresh_seed_state_at_freeze": "unopened",
        "cohort_opened_at_freeze": False,
        "seed_selection_performed_by_freeze": False,
        "seed_claims_written_by_freeze": 0,
        "rows_or_outcomes_opened_by_freeze": 0,
        "condition_matrix": RUNNER.CONDITIONS,
        "condition_names": sorted(RUNNER.CONDITIONS),
    }
    freeze_path = root / "validation" / RUNNER.FREEZE_NAME
    _write_json(freeze_path, freeze)
    checksum = _sha256(freeze_path)
    freeze_path.with_name(f"{freeze_path.name}.sha256").write_text(
        f"{checksum}  {freeze_path.name}\n",
        encoding="utf-8",
    )

    commitment_path = root / "validation" / RUNNER.EXTERNAL_COMMITMENT_NAME
    commitment = {
        "schema": RUNNER.EXTERNAL_COMMITMENT_SCHEMA,
        "version": RUNNER.VERSION,
        "scientific_status": "external_preoutcome_commitment_complete",
        "confirmatory": False,
        "freeze_sha256": checksum,
        "scientific_source_set_sha256": freeze["scientific_source_set_sha256"],
        "source_archive_sha256": _sha256(archive_path),
        "seed_registry_sha256": registry_sha256,
        "seed_selection_receipt_sha256": receipt_sha256,
        "seed_selection_scan_manifest_sha256": scan_sha256,
        "outcomes_opened_before_commitment": False,
        "rows_opened_before_commitment": 0,
        "seed_condition_claims_before_commitment": 0,
        "external_persistent_file": {
            "provider": "test-only",
            "file_id": "fixture-commitment-id",
            "version": "1",
            "committed_at_utc": "2026-08-23T00:00:00Z",
            "immutable_or_append_only": True,
        },
    }
    _write_json(commitment_path, commitment)
    commitment_path.with_name(f"{commitment_path.name}.sha256").write_text(
        f"{_sha256(commitment_path)}  {commitment_path.name}\n",
        encoding="utf-8",
    )
    return root


def _verified_for_claims(root: Path) -> dict[str, Any]:
    verified = RUNNER.verify_v0411_preoutcome_freeze(root)
    verified.update(RUNNER.verify_v0411_external_commitment(root, verified))
    verified["runtime_environment_fingerprint"] = {
        "sha256": "e" * 64,
    }
    return verified


def _race_claim_worker(
    project_root: str,
    verified: dict[str, Any],
    seed: int,
    attempt_id: str,
    barrier: Any,
    result_queue: Any,
) -> None:
    barrier.wait()
    try:
        result = RUNNER._claim_condition(
            project_root=Path(project_root),
            verified=verified,
            seed=seed,
            condition_id="K_RPLUS",
            attempt_id=attempt_id,
        )
        result_queue.put(("ok", result["condition_claim_sha256"]))
    except (RUNNER.FrozenPilotError, OSError, TypeError, ValueError) as error:
        result_queue.put(("error", type(error).__name__, str(error)))


def _fake_row(
    *,
    seed: int,
    index: int,
    condition_id: str,
    row_schema: str,
) -> dict[str, Any]:
    phase, offset = RUNNER._expected_phase(index)
    condition = RUNNER.CONDITIONS[condition_id]
    return {
        "schema": row_schema,
        "seed": seed,
        "transition_index": index,
        "phase": phase,
        "phase_offset": offset,
        "history_policy": condition["history_policy"],
        "world_variant_evaluator_only": condition["world_variant"],
        "task_return_multiplier_evaluator_only": RUNNER._expected_multiplier(
            phase,
            condition["world_variant"],
        ),
        "hard_integrity_valid": True,
        "v039_wrapper_integrity": True,
        "v040_wrapper_integrity": True,
        "v041_wrapper_integrity": True,
        "temporal_action_gate_binding_valid": True,
        "runtime_identity_ok": True,
        "reset_count": 0,
        "evaluator_truth_leak": False,
    }


def _fake_summary(
    *,
    seed: int,
    condition_id: str,
    summary_schema: str,
    all_endpoints_met: bool,
) -> dict[str, Any]:
    condition = RUNNER.CONDITIONS[condition_id]
    return {
        "schema": summary_schema,
        "version": RUNNER.VERSION,
        "seed": seed,
        "condition": {
            "history_policy": condition["history_policy"],
            "world_variant": condition["world_variant"],
        },
        "schedule": list(RUNNER.PHASE_STEPS),
        "integrity": {"test_integrity": True},
        "engine_summary": {"integrity": {"test_engine_integrity": True}},
        "temporal_identity": {
            "historical_prior_enabled": condition["historical_prior_enabled"]
        },
        "all_endpoints_met": all_endpoints_met,
        "status": (
            "TEST_ENGINE_ENDPOINTS_MET"
            if all_endpoints_met
            else "TEST_ENGINE_ENDPOINTS_NOT_MET"
        ),
    }


def test_freeze_rejects_bound_runner_hash_mismatch_before_claim(
    tmp_path: Path,
) -> None:
    root = _frozen_fixture_root(
        tmp_path,
        [100_000_101, 100_000_103, 100_000_105, 100_000_107],
    )
    copied_runner = root / "validation/run_v041_frozen_seed.py"
    copied_runner.write_bytes(
        copied_runner.read_bytes() + b"\n# changed after freeze\n"
    )

    with pytest.raises(RUNNER.FrozenPilotError, match="frozen source mismatch"):
        RUNNER.verify_v0411_preoutcome_freeze(root)

    assert not (root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME).exists()


def test_paired_seed_allows_distinct_arms_but_condition_reuse_fails_closed(
    tmp_path: Path,
) -> None:
    seeds = [100_000_103, 100_000_113, 100_000_123, 100_000_133]
    root = _frozen_fixture_root(tmp_path, seeds)
    verified = _verified_for_claims(root)
    campaign = root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME

    first = RUNNER._claim_condition(
        project_root=root,
        verified=verified,
        seed=seeds[0],
        condition_id="K_RPLUS",
        attempt_id="V041-P-TEST-001",
    )
    second = RUNNER._claim_condition(
        project_root=root,
        verified=verified,
        seed=seeds[0],
        condition_id="N_RPLUS",
        attempt_id="V041-P-TEST-002",
    )

    assert first["seed_claim_created"] is True
    assert second["seed_claim_created"] is False
    assert first["output_dir"].is_dir()
    assert second["output_dir"].is_dir()

    with pytest.raises(RUNNER.FrozenPilotError, match="already consumed"):
        RUNNER._claim_condition(
            project_root=root,
            verified=verified,
            seed=seeds[0],
            condition_id="K_RPLUS",
            attempt_id="V041-P-TEST-003",
        )

    assert (campaign / "_attempt_claims/V041-P-TEST-003.json").is_file()
    condition_claims = list((campaign / "_condition_claims").glob("*.json"))
    assert len(condition_claims) == 2


def test_unregistered_seed_is_rejected_before_campaign_creation(
    tmp_path: Path,
) -> None:
    root = _frozen_fixture_root(
        tmp_path,
        [100_000_105, 100_000_115, 100_000_125, 100_000_135],
    )
    verified = _verified_for_claims(root)
    campaign = root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME

    with pytest.raises(ValueError, match="not in the frozen"):
        RUNNER._claim_condition(
            project_root=root,
            verified=verified,
            seed=999,
            condition_id="K_RPLUS",
            attempt_id="V041-P-TEST-004",
        )

    assert not campaign.exists()


def test_runner_has_one_canonical_campaign_and_rejects_symlink_root(
    tmp_path: Path,
) -> None:
    seeds = [100_000_201, 100_000_211, 100_000_221, 100_000_231]
    root = _frozen_fixture_root(tmp_path, seeds)
    assert (
        "campaign_root" not in inspect.signature(RUNNER.run_frozen_condition).parameters
    )
    link = tmp_path / "project-link"
    link.symlink_to(root, target_is_directory=True)
    with pytest.raises(RUNNER.FrozenPilotError, match="nonsymlink"):
        RUNNER.verify_v0411_preoutcome_freeze(link)


def test_atomic_campaign_and_same_condition_claim_survive_multiprocess_race(
    tmp_path: Path,
) -> None:
    seeds = [100_000_301, 100_000_311, 100_000_321, 100_000_331]
    root = _frozen_fixture_root(tmp_path, seeds)
    verified = _verified_for_claims(root)
    context = multiprocessing.get_context("fork")
    barrier = context.Barrier(6)
    result_queue = context.Queue()
    processes = [
        context.Process(
            target=_race_claim_worker,
            args=(
                root.as_posix(),
                verified,
                seeds[0],
                f"V041-P-RACE-{index:03d}",
                barrier,
                result_queue,
            ),
        )
        for index in range(6)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=30)
        assert process.exitcode == 0
    results = [result_queue.get(timeout=5) for _process in processes]
    assert [result[0] for result in results].count("ok") == 1
    errors = [result for result in results if result[0] == "error"]
    assert len(errors) == 5
    assert all("already consumed" in result[2] for result in errors)

    campaign = root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME
    assert json.loads((campaign / "campaign_receipt.json").read_text(encoding="utf-8"))[
        "canonical_campaign_root"
    ] == (f"validation/{RUNNER.CAMPAIGN_DIRECTORY_NAME}")
    attempts = sorted((campaign / "_attempt_claims").glob("*.json"))
    assert len(attempts) == 6
    for attempt in attempts:
        assert json.loads(attempt.read_text(encoding="utf-8"))["schema"] == (
            RUNNER.CLAIM_SCHEMA
        )
    assert len(list((campaign / "_seed_claims").glob("*.json"))) == 1
    assert len(list((campaign / "_condition_claims").glob("*.json"))) == 1


def test_preloaded_or_out_of_tree_rrct_module_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_path = tmp_path / "installed/rrct/fake.py"
    fake_path.parent.mkdir(parents=True)
    fake_path.write_text("# installed package bypass\n", encoding="utf-8")
    injected = ModuleType("rrct.adversarial_installed_package")
    injected.__file__ = fake_path.as_posix()
    monkeypatch.setitem(sys.modules, injected.__name__, injected)

    with pytest.raises(RUNNER.FrozenPilotError, match="preloaded"):
        RUNNER._reject_preloaded_rrct_modules()

    source_hashes = {
        "src/rrct/fake.py": "f" * 64,
        **{relative: "e" * 64 for relative in RUNNER.MANDATORY_FROZEN_SOURCE_PATHS[:3]},
    }
    with pytest.raises(
        RUNNER.FrozenPilotError,
        match="not frozen|escaped verified",
    ):
        RUNNER._verify_loaded_rrct_modules(tmp_path.resolve(), source_hashes)


def test_preloaded_monkeypatched_experiment_cannot_reach_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rrct.temporal_self_identity_experiment as experiment

    seeds = [100_000_351, 100_000_361, 100_000_371, 100_000_381]
    root = _frozen_fixture_root(tmp_path, seeds)
    monkeypatch.setattr(
        experiment,
        "run_temporal_self_identity_trace",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("ambient monkeypatch executed")
        ),
    )
    monkeypatch.setattr(
        RUNNER,
        "_verify_execution_environment",
        lambda _root: {"sha256": "e" * 64},
    )

    with pytest.raises(RUNNER.FrozenPilotError, match="preloaded"):
        RUNNER.run_frozen_condition(
            project_root=root,
            seed=seeds[0],
            condition_id="K_RPLUS",
            attempt_id="V041-P-MONKEYPATCH-001",
        )
    assert not (root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME).exists()


def test_external_commitment_hash_mismatch_fails_before_claim(
    tmp_path: Path,
) -> None:
    seeds = [100_000_401, 100_000_411, 100_000_421, 100_000_431]
    root = _frozen_fixture_root(tmp_path, seeds)
    verified = RUNNER.verify_v0411_preoutcome_freeze(root)
    commitment = root / "validation" / RUNNER.EXTERNAL_COMMITMENT_NAME
    commitment.write_bytes(commitment.read_bytes() + b" ")

    with pytest.raises(RUNNER.FrozenPilotError, match="checksum mismatch"):
        RUNNER.verify_v0411_external_commitment(root, verified)
    assert not (root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME).exists()


def test_completed_endpoint_miss_is_preserved_as_nonconfirmatory_pilot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rrct.temporal_self_identity_experiment as experiment

    seed = 100_000_107
    condition_id = "K_RPLUS"
    root = _frozen_fixture_root(
        tmp_path,
        [seed, 100_000_117, 100_000_127, 100_000_137],
    )
    monkeypatch.setattr(
        RUNNER,
        "_verify_execution_environment",
        lambda _root: {"sha256": "e" * 64},
    )
    monkeypatch.setattr(RUNNER, "_reject_preloaded_rrct_modules", lambda: None)
    monkeypatch.setattr(
        RUNNER,
        "_activate_verified_source",
        lambda project_root: project_root / "src",
    )
    monkeypatch.setattr(
        RUNNER,
        "_verify_loaded_rrct_modules",
        lambda *_args, **_kwargs: {
            "rrct.temporal_self_identity": ("src/rrct/temporal_self_identity.py")
        },
    )
    monkeypatch.setattr(RUNNER, "_rehash_source_manifest", lambda *_a, **_k: None)

    def fake_trace(
        observed_seed: int,
        *,
        temporal_identity_config: Any,
        world_variant: str,
        sealed_row_sink: Any,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        assert observed_seed == seed
        assert temporal_identity_config.history_policy == "keyed"
        assert world_variant == "true_recurrence"
        rows = [
            _fake_row(
                seed=seed,
                index=index,
                condition_id=condition_id,
                row_schema=experiment.V041_ROW_SCHEMA,
            )
            for index in range(RUNNER.EXPECTED_TRANSITION_COUNT)
        ]
        for row in rows:
            sealed_row_sink(row)
        return rows, _fake_summary(
            seed=seed,
            condition_id=condition_id,
            summary_schema=experiment.V041_SUMMARY_SCHEMA,
            all_endpoints_met=False,
        )

    monkeypatch.setattr(experiment, "run_temporal_self_identity_trace", fake_trace)
    output, summary = RUNNER.run_frozen_condition(
        project_root=root,
        seed=seed,
        condition_id=condition_id,
        attempt_id="V041-P-TEST-005",
        progress_every=RUNNER.EXPECTED_TRANSITION_COUNT,
    )

    assert summary["all_endpoints_met"] is False
    assert summary["scientific_status"] == RUNNER.SCIENTIFIC_STATUS
    assert summary["confirmatory"] is False
    assert summary["frozen_pilot"]["scientific_failure_preserved"] is True
    assert summary["status"].endswith("ENDPOINTS_NOT_MET")

    finish = json.loads((output / RUNNER.FINISH_NAME).read_text(encoding="utf-8"))
    assert finish["integrity_complete"] is True
    assert finish["scientific_all_endpoints_met"] is False
    assert finish["scientific_failure_preserved"] is True
    assert finish["confirmatory"] is False
    assert finish["rows_count"] == RUNNER.EXPECTED_TRANSITION_COUNT
    assert not (output / RUNNER.FAILURE_NAME).exists()

    manifest = json.loads((output / RUNNER.ARTIFACT_NAME).read_text(encoding="utf-8"))
    for name, expected in manifest.items():
        assert _sha256(output / name) == expected


def test_execution_failure_retains_partial_durable_rows_and_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rrct.temporal_self_identity_experiment as experiment

    seed = 100_000_109
    condition_id = "N_RMINUS"
    root = _frozen_fixture_root(
        tmp_path,
        [seed, 100_000_119, 100_000_129, 100_000_139],
    )
    monkeypatch.setattr(
        RUNNER,
        "_verify_execution_environment",
        lambda _root: {"sha256": "e" * 64},
    )
    monkeypatch.setattr(RUNNER, "_reject_preloaded_rrct_modules", lambda: None)
    monkeypatch.setattr(
        RUNNER,
        "_activate_verified_source",
        lambda project_root: project_root / "src",
    )
    monkeypatch.setattr(
        RUNNER,
        "_verify_loaded_rrct_modules",
        lambda *_args, **_kwargs: {
            "rrct.temporal_self_identity": ("src/rrct/temporal_self_identity.py")
        },
    )
    monkeypatch.setattr(RUNNER, "_rehash_source_manifest", lambda *_a, **_k: None)

    def failing_trace(
        observed_seed: int,
        *,
        temporal_identity_config: Any,
        world_variant: str,
        sealed_row_sink: Any,
    ) -> Any:
        assert observed_seed == seed
        sealed_row_sink(
            _fake_row(
                seed=seed,
                index=0,
                condition_id=condition_id,
                row_schema=experiment.V041_ROW_SCHEMA,
            )
        )
        raise RuntimeError("injected post-row failure")

    monkeypatch.setattr(experiment, "run_temporal_self_identity_trace", failing_trace)
    campaign = root / "validation" / RUNNER.CAMPAIGN_DIRECTORY_NAME
    with pytest.raises(RuntimeError, match="injected post-row failure"):
        RUNNER.run_frozen_condition(
            project_root=root,
            seed=seed,
            condition_id=condition_id,
            attempt_id="V041-P-TEST-006",
        )

    output = campaign / "pairs" / f"seed-{seed}" / condition_id
    failure = json.loads((output / RUNNER.FAILURE_NAME).read_text(encoding="utf-8"))
    assert failure["rows_count"] == 1
    assert failure["partial_rows_preserved"] is True
    assert failure["scientific_status"] == RUNNER.SCIENTIFIC_STATUS
    assert failure["confirmatory"] is False
    assert failure["status"].endswith("EXECUTION_FAILED")
    assert (
        len((output / RUNNER.ROWS_NAME).read_text(encoding="utf-8").splitlines()) == 1
    )
