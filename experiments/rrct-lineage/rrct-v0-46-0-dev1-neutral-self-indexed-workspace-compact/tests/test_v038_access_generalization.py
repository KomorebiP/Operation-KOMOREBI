"""Focused checks for the v0.38 bounded access-memory successor."""

from __future__ import annotations

import copy

import numpy as np

from rrct.causal_boundary import OnlineCausalAccessMemoryReadout
from rrct.access_generalization_experiment import (
    V038_ACCESS_MEMORY_CAPACITY,
    V038_ACCESS_MODE,
    V038_ACCESS_NEIGHBORS,
    _agent_v038,
    _wrap_v038_row,
    run_access_generalization_trace,
)
from rrct.post_change_closure_experiment import V037ExperimentConfig
from rrct.unified_causal_loop_experiment import _boundary_config


V038_EXPOSED_DEVELOPMENT_SEED = 7351


def test_fifo_memory_predicts_before_update_and_remains_bounded() -> None:
    readout = OnlineCausalAccessMemoryReadout(
        4,
        2,
        3,
        memory_capacity=3,
        neighbors=1,
        strategy="fifo",
    )
    feature = np.asarray([0.8, -0.2, 0.1, 0.4])
    assert readout.predict(feature).pair is None
    readout.update(feature, (1, 2))
    assert readout.predict(feature).pair is None
    readout.update(feature, (1, 2))
    assert readout.predict(feature).pair == (1, 2)
    for offset in range(8):
        readout.update(feature + 0.01 * offset, (1, 2))
    snapshot = readout.snapshot()
    class_index = 1 * 3 + 2
    assert len(snapshot["memories"][class_index]) == 3
    assert max(len(memory) for memory in snapshot["memories"]) <= 3


def test_access_memory_snapshot_roundtrip_and_deepcopy() -> None:
    readout = OnlineCausalAccessMemoryReadout(
        3,
        2,
        2,
        memory_capacity=4,
        neighbors=1,
        strategy="prototype",
    )
    for _ in range(7):
        readout.update([0.9, 0.1, -0.2], (0, 1))
    restored = OnlineCausalAccessMemoryReadout(
        3,
        2,
        2,
        memory_capacity=4,
        neighbors=1,
        strategy="prototype",
    )
    restored.load_snapshot(readout.snapshot())
    clone = copy.deepcopy(readout)
    assert restored.snapshot()["digest"] == readout.snapshot()["digest"]
    assert clone.snapshot()["digest"] == readout.snapshot()["digest"]
    assert restored.predict([0.9, 0.1, -0.2]).pair == (0, 1)


def test_v038_agent_replaces_only_the_startup_access_readout() -> None:
    seed = V038_EXPOSED_DEVELOPMENT_SEED
    agent = _agent_v038(_boundary_config(seed), seed)
    assert agent.time == 0
    assert agent.last_result is None
    assert agent.causal_access_readout_mode == V038_ACCESS_MODE
    assert agent.causal_access_memory_capacity == V038_ACCESS_MEMORY_CAPACITY
    assert agent.causal_access_neighbors == V038_ACCESS_NEIGHBORS
    snapshot = agent.causal_boundary_snapshot()
    assert snapshot["access_readout"]["strategy"] == "fifo"
    assert snapshot["access_readout"]["memory_capacity"] == 64


def test_v038_wrapper_binds_the_checked_engine_row() -> None:
    source = {
        "schema": "rrct.v037.post_change_closure.row.v1",
        "hard_integrity_valid": True,
        "transition_index": 7,
    }
    wrapped = _wrap_v038_row(source)
    assert wrapped["schema"] == "rrct.v038.access_generalization.row.v1"
    assert wrapped["v037_engine_schema"] == source["schema"]
    assert wrapped["v038_wrapper_integrity"]
    assert wrapped["causal_access_updated"] is False
    assert wrapped["causal_access_updates"] == 0
    assert wrapped["access_decoder"]["prediction_before_current_label"]
    assert not wrapped["access_decoder"]["evaluator_truth_visible"]


def test_short_v038_trace_preserves_row_order_and_wrapper_integrity() -> None:
    config = V037ExperimentConfig(
        stable_steps=2,
        world_shock_steps=2,
        remap_steps=2,
        disconnect_steps=2,
        restore_steps=2,
        recovery_tail_steps=1,
        confirmation_budget_steps=1,
    )
    rows, summary = run_access_generalization_trace(
        V038_EXPOSED_DEVELOPMENT_SEED, experiment_config=config
    )
    assert len(rows) == config.total_steps == 10
    assert [row["transition_index"] for row in rows] == list(range(10))
    assert all(row["v038_wrapper_integrity"] for row in rows)
    previous_updates = (
        rows[0]["causal_access_updates"]
        - int(rows[0]["causal_access_updated"])
    )
    assert previous_updates in (0, 1)
    for row in rows:
        assert row["causal_access_updates"] == (
            previous_updates + int(row["causal_access_updated"])
        )
        previous_updates = row["causal_access_updates"]
    assert summary["access_update_trace"]["stepwise_consistent"]
    assert summary["access_update_trace"]["terminal_update_count"] == (
        previous_updates
    )
    assert summary["schema"] == "rrct.v038.access_generalization.summary.v1"
    assert summary["seed"] == V038_EXPOSED_DEVELOPMENT_SEED


def test_claimed_pilot_writes_complete_durable_evidence(
    tmp_path, monkeypatch
) -> None:
    import hashlib
    import json
    from types import SimpleNamespace

    import rrct.access_generalization_experiment as experiment

    source_archive = tmp_path / "frozen-source.tar.gz"
    source_archive.write_bytes(b"immutable-v038-source")
    archive_sha = hashlib.sha256(source_archive.read_bytes()).hexdigest()
    monkeypatch.setattr(
        experiment,
        "verify_v038_preoutcome_freeze",
        lambda: {
            "freeze": {"source_archive": {"sha256": archive_sha}},
            "freeze_sha256": "f" * 64,
            "source_archive_path": source_archive,
        },
    )
    monkeypatch.setattr(
        experiment,
        "V038_PILOT_SEEDS",
        (V038_EXPOSED_DEVELOPMENT_SEED,),
    )
    monkeypatch.setattr(
        experiment,
        "V038_FIRST_PILOT_SEED",
        V038_EXPOSED_DEVELOPMENT_SEED,
    )
    monkeypatch.setattr(
        experiment,
        "V037_D1_CONFIG",
        SimpleNamespace(total_steps=3),
    )
    from types import SimpleNamespace

    monkeypatch.setattr(
        experiment,
        "V037_D1_CONFIG",
        SimpleNamespace(total_steps=3),
    )

    fake_rows = [
        {
            "schema": experiment.V038_ROW_SCHEMA,
            "transition_index": index,
            "phase": "stable",
            "phase_offset": index,
            "structural_event": "none",
            "action_gate_open_evaluator_only": False,
            "hard_integrity_valid": True,
        }
        for index in range(3)
    ]
    fake_summary = {
        "status": "V038_PILOT_ENDPOINTS_MET",
        "all_endpoints_met": True,
        "endpoints": {"G01_integrity": True},
    }

    def fake_trace(seed, *, sealed_row_sink=None, **kwargs):
        assert seed == experiment.V038_FIRST_PILOT_SEED
        assert sealed_row_sink is not None
        for row in fake_rows:
            sealed_row_sink(row)
        return fake_rows, fake_summary

    monkeypatch.setattr(
        experiment, "run_access_generalization_trace", fake_trace
    )
    output, summary = experiment.run_claimed_v038_pilot(
        V038_EXPOSED_DEVELOPMENT_SEED,
        "G1-P-9001",
        campaign_root=tmp_path / "campaign",
        progress_every=2,
    )
    assert summary["campaign"]["rows_count"] == 3
    manifest = json.loads(
        (output / "artifact_sha256.json").read_text(encoding="utf-8")
    )
    for name, expected in manifest.items():
        observed = hashlib.sha256((output / name).read_bytes()).hexdigest()
        assert observed == expected
    assert (output / "finish_receipt.json").is_file()
    assert (output / source_archive.name).read_bytes() == source_archive.read_bytes()
    finish = json.loads(
        (output / "finish_receipt.json").read_text(encoding="utf-8")
    )
    assert finish["rows_sha256"] == manifest[experiment.V038_ROWS_ARTIFACT]
    assert finish["summary_sha256"] == manifest[
        experiment.V038_SUMMARY_ARTIFACT
    ]
    assert finish["start_receipt_sha256"] == manifest["start_receipt.json"]
    start = json.loads(
        (output / "start_receipt.json").read_text(encoding="utf-8")
    )
    for kind in ("attempt", "seed"):
        claim = tmp_path / "campaign" / start[f"{kind}_claim"]
        assert claim.is_file()
        assert hashlib.sha256(claim.read_bytes()).hexdigest() == start[
            f"{kind}_claim_sha256"
        ]


def test_claimed_pilot_rejects_invalid_progress_interval(tmp_path) -> None:
    import pytest

    from rrct.access_generalization_experiment import run_claimed_v038_pilot

    with pytest.raises(ValueError, match="positive integer"):
        run_claimed_v038_pilot(
            V038_EXPOSED_DEVELOPMENT_SEED,
            "G1-P-9002",
            campaign_root=tmp_path,
            progress_every=0,
        )


def test_disconnect_endpoint_rewards_null_specificity_not_open_gate() -> None:
    import rrct.access_generalization_experiment as experiment

    readout = OnlineCausalAccessMemoryReadout(
        28,
        4,
        6,
        memory_capacity=64,
        neighbors=1,
        strategy="fifo",
    )
    readout.update(np.zeros(28), None)
    valid_row = {
        "v038_wrapper_integrity": True,
        "hard_integrity_valid": True,
    }
    active_tail = {
        "correct_gated_actions": 480,
        "rows": 480,
        "action_public_exact_fraction": 1.0,
        "action_gate_open_fraction": 1.0,
        "action_public_null_fraction": 0.0,
    }
    disconnect_tail = {
        "correct_gated_actions": 480,
        "rows": 480,
        "action_public_exact_fraction": 1.0,
        "action_gate_open_fraction": 0.0,
        "action_public_null_fraction": 1.0,
    }
    v037_summary = {
        "post_change": {
            "remap": {"tail": active_tail},
            "restore": {"tail": active_tail},
            "disconnect": {"tail": disconnect_tail},
        },
        "stable_tail": active_tail,
        "world_shock_tail": active_tail,
        "endpoints": {"F01_integrity": True},
        "status": "V037_PILOT_ENDPOINTS_MET",
        "control_return_margins": {},
        "rollout_audit": {},
    }
    summary = experiment._build_v038_summary(
        V038_EXPOSED_DEVELOPMENT_SEED,
        [valid_row] * experiment.V037_D1_CONFIG.total_steps,
        v037_summary,
        readout.snapshot(),
    )
    assert summary["endpoints"]["G06_disconnect_null_specificity"]


def test_freeze_builder_is_one_time_and_self_verifying(tmp_path) -> None:
    import hashlib
    import importlib.util
    import json
    from pathlib import Path

    import pytest

    test_seeds = (6451, 7301, 7351, 7601)
    script_path = (
        Path(__file__).resolve().parents[1]
        / "validation"
        / "freeze_v038_source.py"
    )
    spec = importlib.util.spec_from_file_location("freeze_v038_source", script_path)
    assert spec is not None and spec.loader is not None
    freeze_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freeze_module)

    root = tmp_path / "project"
    (root / "src" / "rrct").mkdir(parents=True)
    (root / "tests" / "fixtures").mkdir(parents=True)
    (root / "validation").mkdir(parents=True)
    for relative, content in {
        "pyproject.toml": "[project]\nname='rrct-freeze-test'\n",
        "MANIFEST.in": "include README.md\n",
        "uv.lock": "version = 1\n",
        "README.md": "test\n",
        "RELEASE_NOTES.md": "test\n",
        "ETHICS.md": "test\n",
        "Verify_V038_Evidence.ps1": "Write-Host test\n",
        "src/rrct/a.py": "VALUE = 1\n",
        "tests/test_a.py": "def test_a(): assert True\n",
        "tests/fixtures/example.json": "{}\n",
        "validation/V0_38_ACCESS_GENERALIZATION_PROTOCOL.md": "protocol\n",
        "validation/V0_38_SEED_REGISTRY.json": json.dumps(
            {"fresh_pilot_seeds": list(test_seeds)}
        )
        + "\n",
        "validation/V0_38_SEED_SELECTION_RECEIPT.json": json.dumps(
            {
                "selected_fresh_pilot_seeds": list(test_seeds),
                "retired_preoutcome_seeds": [7601, 7607, 7613, 7619],
            }
        )
        + "\n",
        "validation/V0_38_DEVELOPMENT_NOTES.md": "notes\n",
        "validation/V0_38_DECODER_SCREEN_ON_V037_TRACE.json": "{}\n",
        "validation/V0_38_IMPLEMENTATION_REPLAY_ON_V037_7301.json": "{}\n",
        "validation/freeze_v038_source.py": script_path.read_text(
            encoding="utf-8"
        ),
    }.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    result = freeze_module.create_freeze(root)
    freeze_path = Path(result["freeze_path"])
    payload = json.loads(freeze_path.read_text(encoding="utf-8"))
    archive = Path(result["source_archive_path"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == payload[
        "source_archive"
    ]["sha256"]
    assert freeze_module._canonical_sha256(
        payload["scientific_source_sha256"]
    ) == payload["scientific_source_set_sha256"]

    import rrct.access_generalization_experiment as experiment

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(experiment, "V038_PROJECT_ROOT", root)
    monkeypatch.setattr(experiment, "V038_VALIDATION_ROOT", root / "validation")
    monkeypatch.setattr(experiment, "V038_PILOT_SEEDS", test_seeds)
    monkeypatch.setattr(experiment, "V038_FIRST_PILOT_SEED", test_seeds[0])
    monkeypatch.setattr(
        experiment,
        "V038_FREEZE_PATH",
        root / "validation" / "V0_38_PREOUTCOME_FREEZE.json",
    )
    monkeypatch.setattr(
        experiment,
        "V038_FREEZE_SHA256_PATH",
        root / "validation" / "V0_38_PREOUTCOME_FREEZE.json.sha256",
    )
    try:
        verified = experiment.verify_v038_preoutcome_freeze()
    finally:
        monkeypatch.undo()
    assert verified["freeze_sha256"] == result["freeze_sha256"]
    assert Path(verified["source_archive_path"]) == archive
    with pytest.raises(FileExistsError, match="already exists"):
        freeze_module.create_freeze(root)


def test_frozen_cohort_rule_requires_three_of_four_and_median_440(
    monkeypatch,
) -> None:
    import copy

    import rrct.access_generalization_experiment as experiment

    test_seeds = (6451, 7301, 7351, 7601)
    monkeypatch.setattr(experiment, "V038_PILOT_SEEDS", test_seeds)

    def seed_summary(seed: int, remap: int, restore: int, passed: bool):
        return {
            "seed": seed,
            "status": (
                "V038_PILOT_ENDPOINTS_MET"
                if passed
                else "V038_PILOT_ENDPOINTS_NOT_MET"
            ),
            "all_endpoints_met": passed,
            "endpoints": {"G01_integrity": True},
            "post_change": {
                "remap": {"tail": {"correct_gated_actions": remap}},
                "restore": {"tail": {"correct_gated_actions": restore}},
            },
            "exact_public_action_counts": {
                "remap": remap,
                "restore": restore,
            },
            "campaign": {"attempt_id": f"G1-P-{seed}"},
        }

    seeds = experiment.V038_PILOT_SEEDS
    passing = {
        seeds[0]: seed_summary(seeds[0], 450, 470, True),
        seeds[1]: seed_summary(seeds[1], 442, 460, True),
        seeds[2]: seed_summary(seeds[2], 438, 450, False),
        seeds[3]: seed_summary(seeds[3], 446, 440, True),
    }
    cohort = experiment._build_v038_cohort_summary(passing)
    assert cohort["cohort_target_met"]
    assert cohort["all_endpoint_pass_count"] == 3
    assert cohort["median_remap_correct_actions"] == 444.0

    failing = copy.deepcopy(passing)
    failing[seeds[3]]["all_endpoints_met"] = False
    cohort = experiment._build_v038_cohort_summary(failing)
    assert not cohort["cohort_target_met"]
    assert cohort["status"] == "V038_COHORT_TARGET_NOT_MET"


def test_campaign_aggregator_verifies_hashes_and_rows(tmp_path, monkeypatch) -> None:
    import hashlib
    import json

    import rrct.access_generalization_experiment as experiment

    test_seeds = (6451, 7301, 7351, 7601)
    monkeypatch.setattr(experiment, "V038_PILOT_SEEDS", test_seeds)
    monkeypatch.setattr(experiment, "V038_FIRST_PILOT_SEED", test_seeds[0])
    archive_name = "V0_38_EXECUTED_SOURCE_test.tar.gz"
    archive_payload = b"frozen"
    archive_sha = hashlib.sha256(archive_payload).hexdigest()
    monkeypatch.setattr(experiment, "V038_PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        experiment,
        "verify_v038_preoutcome_freeze",
        lambda: {
            "freeze": {"source_archive": {"sha256": archive_sha}},
            "freeze_sha256": "a" * 64,
            "source_archive_path": tmp_path / "validation" / archive_name,
        },
    )
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    claims = campaign / "claims"
    claims.mkdir()
    for index, seed in enumerate(experiment.V038_PILOT_SEEDS, start=1):
        attempt_id = f"G1-P-{index:04d}"
        directory = campaign / f"G1-P-{index:04d}-seed-{seed}"
        directory.mkdir()
        rows_path = directory / experiment.V038_ROWS_ARTIFACT
        phase_specs = (
            ("stable", experiment.V037_D1_CONFIG.stable_steps, 450),
            (
                "world_shock",
                experiment.V037_D1_CONFIG.world_shock_steps,
                450,
            ),
            ("remap", experiment.V037_D1_CONFIG.remap_steps, 450),
            (
                "disconnect",
                experiment.V037_D1_CONFIG.disconnect_steps,
                480,
            ),
            ("restore", experiment.V037_D1_CONFIG.restore_steps, 470),
        )
        transition_index = 0
        with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
            for phase, phase_rows, exact_tail_count in phase_specs:
                tail_start = int(phase_rows) - int(
                    experiment.V037_D1_CONFIG.recovery_tail_steps
                )
                for phase_offset in range(int(phase_rows)):
                    tail_offset = phase_offset - tail_start
                    exact = bool(0 <= tail_offset < exact_tail_count)
                    engine_row = {
                        "schema": "rrct.v037.post_change_closure.row.v1",
                        "transition_index": transition_index,
                        "phase": phase,
                        "hard_integrity_valid": True,
                        "action_public_exact_evaluator_only": exact,
                        "action_public_pair": (
                            None
                            if phase == "disconnect"
                            else ([0, 0] if exact else [1, 1])
                        ),
                        "action_gate_open_evaluator_only": bool(
                            phase != "disconnect" and exact
                        ),
                    }
                    row = experiment._wrap_v038_row(
                        engine_row,
                        causal_access_updated=(transition_index == 0),
                        causal_access_updates=1,
                    )
                    handle.write(
                        json.dumps(
                            row,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )
                    transition_index += 1
        rows_sha = hashlib.sha256(rows_path.read_bytes()).hexdigest()
        endpoints = {
            "G01_integrity": True,
            "G02_all_v037_closure_endpoints": True,
            "G03_remap_access_generalization": True,
            "G04_restoration_access_generalization": True,
            "G05_no_stable_or_shock_regression": True,
            "G06_disconnect_null_specificity": True,
        }
        summary = {
            "seed": seed,
            "status": "V038_PILOT_ENDPOINTS_MET",
            "all_endpoints_met": True,
            "endpoints": endpoints,
            "post_change": {
                "remap": {"tail": {"correct_gated_actions": 450}},
                "restore": {"tail": {"correct_gated_actions": 470}},
            },
            "exact_public_action_counts": {
                "stable": 450,
                "world_shock": 450,
                "remap": 450,
                "disconnect": 480,
                "restore": 470,
            },
            "access_memory_terminal": {
                "schema": "rrct.online_causal_access_memory.v1",
                "strategy": "fifo",
                "memory_capacity": 64,
                "neighbors": 1,
                "class_count": 25,
                "class_memory_sizes": [1] + [0] * 24,
                "maximum_class_memory_size": 1,
                "nonempty_classes": 1,
                "class_updates": [1] + [0] * 24,
                "update_count": 1,
                "snapshot_digest": "test",
            },
            "access_update_trace": {
                "rows": experiment.V037_D1_CONFIG.total_steps,
                "initial_update_count": 0,
                "first_update_count": 1,
                "terminal_update_count": 1,
                "updated_rows": 1,
                "stepwise_consistent": True,
            },
            "integrity": {
                "row_count_exact": True,
                "all_wrappers_valid": True,
                "all_inherited_hard_integrity": True,
                "decoder_schema_exact": True,
                "decoder_strategy_exact": True,
                "decoder_capacity_exact": True,
                "decoder_neighbors_exact": True,
                "decoder_memory_bounded": True,
                "decoder_class_count_exact": True,
                "decoder_class_updates_nonnegative": True,
                "decoder_memory_sizes_match_updates": True,
                "decoder_updates_internally_consistent": True,
                "decoder_update_trace_fields_present": True,
                "decoder_update_trace_stepwise_consistent": True,
                "decoder_update_trace_terminal_matches_snapshot": True,
            },
            "campaign": {
                "attempt_id": attempt_id,
                "freeze_sha256": "a" * 64,
                "source_archive_sha256": archive_sha,
                "rows_count": experiment.V037_D1_CONFIG.total_steps,
                "rows_sha256": rows_sha,
            },
        }
        summary_path = directory / experiment.V038_SUMMARY_ARTIFACT
        summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary_sha = hashlib.sha256(summary_path.read_bytes()).hexdigest()
        (directory / archive_name).write_bytes(archive_payload)
        claim_payload = {
            "schema": "rrct.v038.campaign_claim.v1",
            "version": experiment.V038_VERSION,
            "attempt_id": attempt_id,
            "seed": seed,
            "freeze_sha256": "a" * 64,
            "state": "consumed_before_rng_construction",
        }
        attempt_claim = claims / f"attempt-{attempt_id}.json"
        seed_claim = claims / f"seed-{seed}.json"
        for claim_path in (attempt_claim, seed_claim):
            claim_path.write_text(
                json.dumps(claim_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        start = {
            "schema": "rrct.v038.start_receipt.v1",
            "version": experiment.V038_VERSION,
            "attempt_id": attempt_id,
            "seed": seed,
            "freeze_sha256": "a" * 64,
            "source_archive": archive_name,
            "source_archive_sha256": archive_sha,
            "expected_transition_count": experiment.V037_D1_CONFIG.total_steps,
            "attempt_claim": attempt_claim.relative_to(campaign).as_posix(),
            "attempt_claim_sha256": hashlib.sha256(
                attempt_claim.read_bytes()
            ).hexdigest(),
            "seed_claim": seed_claim.relative_to(campaign).as_posix(),
            "seed_claim_sha256": hashlib.sha256(
                seed_claim.read_bytes()
            ).hexdigest(),
            "row_fsync": True,
            "seed_claimed_before_rng_construction": True,
        }
        start_path = directory / "start_receipt.json"
        start_path.write_text(
            json.dumps(start, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        start_sha = hashlib.sha256(start_path.read_bytes()).hexdigest()
        finish = {
            "schema": "rrct.v038.finish_receipt.v1",
            "version": experiment.V038_VERSION,
            "attempt_id": attempt_id,
            "seed": seed,
            "freeze_sha256": "a" * 64,
            "source_archive_sha256": archive_sha,
            "rows_count": experiment.V037_D1_CONFIG.total_steps,
            "rows_sha256": rows_sha,
            "summary_sha256": summary_sha,
            "start_receipt_sha256": start_sha,
            "endpoints_sha256": experiment._json_sha256(endpoints),
            "status": "V038_PILOT_ENDPOINTS_MET",
            "all_endpoints_met": True,
        }
        (directory / "finish_receipt.json").write_text(
            json.dumps(finish, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        names = (
            experiment.V038_ROWS_ARTIFACT,
            experiment.V038_SUMMARY_ARTIFACT,
            archive_name,
            "start_receipt.json",
            "finish_receipt.json",
        )
        manifest = {
            name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in names
        }
        (directory / "artifact_sha256.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

    cohort = experiment.aggregate_v038_campaign(campaign)
    assert cohort["cohort_target_met"]
    assert cohort["all_endpoint_pass_count"] == 4
    assert set(cohort["evidence_audit"]) == {
        str(seed) for seed in experiment.V038_PILOT_SEEDS
    }


def test_integrity_uses_terminal_memory_internal_consistency() -> None:
    import rrct.access_generalization_experiment as experiment

    terminal = experiment.V037_D1_CONFIG.total_steps // 2
    rows = []
    update_count = 0
    for index in range(experiment.V037_D1_CONFIG.total_steps):
        updated = index < terminal
        update_count += int(updated)
        rows.append(
            {
                "v038_wrapper_integrity": True,
                "hard_integrity_valid": True,
                "causal_access_updated": updated,
                "causal_access_updates": update_count,
            }
        )
    active_tail = {
        "correct_gated_actions": 480,
        "rows": 480,
        "action_public_exact_fraction": 1.0,
        "action_gate_open_fraction": 1.0,
        "action_public_null_fraction": 0.0,
    }
    disconnect_tail = {
        "correct_gated_actions": 480,
        "rows": 480,
        "action_public_exact_fraction": 1.0,
        "action_gate_open_fraction": 0.0,
        "action_public_null_fraction": 1.0,
    }
    v037_summary = {
        "post_change": {
            "remap": {"tail": active_tail},
            "restore": {"tail": active_tail},
            "disconnect": {"tail": disconnect_tail},
        },
        "stable_tail": active_tail,
        "world_shock_tail": active_tail,
        "endpoints": {"F01_integrity": True},
        "status": "V037_PILOT_ENDPOINTS_MET",
        "control_return_margins": {},
        "rollout_audit": {},
    }
    snapshot = {
        "schema": "rrct.online_causal_access_memory.v1",
        "strategy": "fifo",
        "memory_capacity": 64,
        "neighbors": 1,
        "memories": [np.zeros((64, 28))]
        + [np.zeros((0, 28)) for _ in range(24)],
        "class_updates": [terminal] + [0] * 24,
        "update_count": terminal,
        "digest": "test",
    }
    summary = experiment._build_v038_summary(
        V038_EXPOSED_DEVELOPMENT_SEED, rows, v037_summary, snapshot
    )
    assert summary["integrity"]["decoder_updates_internally_consistent"]
    assert summary["integrity"]["decoder_update_trace_stepwise_consistent"]
    assert summary["integrity"][
        "decoder_update_trace_terminal_matches_snapshot"
    ]
    assert summary["endpoints"]["G01_integrity"]

    broken_rows = copy.deepcopy(rows)
    broken_rows[terminal]["causal_access_updates"] += 1
    broken = experiment._build_v038_summary(
        V038_EXPOSED_DEVELOPMENT_SEED,
        broken_rows,
        v037_summary,
        snapshot,
    )
    assert not broken["integrity"][
        "decoder_update_trace_stepwise_consistent"
    ]
    assert not broken["endpoints"]["G01_integrity"]

    shifted_snapshot = copy.deepcopy(snapshot)
    shifted_snapshot["update_count"] += 1
    shifted = experiment._build_v038_summary(
        V038_EXPOSED_DEVELOPMENT_SEED,
        rows,
        v037_summary,
        shifted_snapshot,
    )
    assert not shifted["integrity"][
        "decoder_updates_internally_consistent"
    ]
    assert not shifted["endpoints"]["G01_integrity"]
