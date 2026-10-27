"""Focused checks for the unrun v0.36 unified causal-loop harness."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import rrct.unified_causal_loop_experiment as experiment
from rrct.unified_causal_loop import (
    ActionCandidate,
    PublicBoundaryCertificate,
    UnifiedCausalLoop,
)


@pytest.fixture(scope="module")
def short_trace() -> tuple[list[dict[str, object]], dict[str, object]]:
    config = experiment.V036ExperimentConfig(
        stable_steps=2,
        world_shock_steps=2,
        remap_steps=2,
        disconnect_steps=2,
        restore_steps=2,
    )
    return experiment._run_trace(
        experiment.V036_FIRST_PILOT_SEED,
        experiment_config=config,
        boundary_config=experiment._boundary_config(
            experiment.V036_FIRST_PILOT_SEED
        ),
        runtime_config=experiment._runtime_config(
            experiment.V036_FIRST_PILOT_SEED
        ),
    )


def test_d0_schedule_world_rank_and_stronger_passive_decoy() -> None:
    config = experiment.V036_D0_CONFIG
    assert config.total_steps == 4_800
    assert config.phase_steps == (
        ("stable", 1_440),
        ("world_shock", 480),
        ("remap", 960),
        ("disconnect", 960),
        ("restore", 960),
    )
    assert experiment.V036_FIRST_PILOT_SEED == 6451

    world = experiment._hidden_world(6451, config)
    assert world.stable_pair != world.remap_pair
    assert world.exogenous_source not in {
        world.stable_pair[1],
        world.remap_pair[1],
    }
    assert np.linalg.matrix_rank(world.stable_effect) == 2
    assert np.linalg.matrix_rank(world.remap_effect) == 2
    assert np.linalg.matrix_rank(world.exogenous_effect) == 2
    route_singular = np.linalg.svd(world.stable_effect, compute_uv=False)
    decoy_singular = np.linalg.svd(world.exogenous_effect, compute_uv=False)
    assert decoy_singular[1] > route_singular[0]


def test_run_specific_internal_rng_streams_and_blind_bank_replay() -> None:
    first = experiment.V036_FIRST_PILOT_SEED
    second = experiment.V036_PILOT_SEEDS[1]
    assert experiment._boundary_config(first).seed != experiment._boundary_config(
        second
    ).seed
    assert experiment._runtime_config(first).seed != experiment._runtime_config(
        second
    ).seed

    signature = inspect.signature(experiment._equal_energy_process_bank)
    assert set(signature.parameters) == {"rng", "energy"}
    assert {"phase", "pair", "handle", "truth"}.isdisjoint(signature.parameters)
    rng = np.random.default_rng(19)
    bank, receipt = experiment._draw_process_bank_with_replay_receipt(
        rng, energy=np.sqrt(experiment.V036_PROCESS_DIM), sequence_id=0
    )
    np.testing.assert_allclose(
        np.linalg.norm(bank, axis=1),
        np.sqrt(experiment.V036_PROCESS_DIM),
        rtol=0.0,
        atol=1e-12,
    )
    assert receipt.replay_valid
    assert receipt.process_bank_sha256 == receipt.replay_process_bank_sha256
    assert receipt.draw_arguments == ("rng", "energy")


def test_harness_order_and_imports_exclude_legacy_truth_paths() -> None:
    source = inspect.getsource(experiment._run_trace)
    draw_at = source.index("_draw_process_bank_with_replay_receipt")
    hash_at = source.index("_array_sha256(bank)")
    precommit_at = source.index("runtime.precommit_process_bank(bank)")
    advance_at = source.index("runtime.advance(")
    consequence_at = source.index("_world_transition(")
    assert draw_at < hash_at < precommit_at < advance_at < consequence_at

    module_path = Path(experiment.__file__)
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any("experiment" in imported for imported in imports)


def test_action_candidates_are_fixed_public_and_have_no_preview() -> None:
    candidates = experiment._action_candidates()
    assert len(candidates) == 5
    assert tuple(candidate.key for candidate in candidates) == (
        "hold",
        "east",
        "west",
        "north",
        "south",
    )
    np.testing.assert_array_equal(
        np.stack([candidate.action for candidate in candidates]),
        experiment.V036_ACTIONS,
    )
    assert all(candidate.preview_effect_operator is None for candidate in candidates)


def test_world_action_consequence_is_gated_by_exact_public_pair() -> None:
    config = experiment.V036ExperimentConfig(
        stable_steps=1,
        world_shock_steps=1,
        remap_steps=1,
        disconnect_steps=1,
        restore_steps=1,
        observation_noise=0.0,
        return_noise=0.0,
    )
    world = experiment._hidden_world(6451, config)
    phase = experiment._phase_truth(config, world, 0)
    observation = np.zeros(experiment.V036_OBSERVATION_DIM)
    bank = experiment._equal_energy_process_bank(
        np.random.default_rng(71), energy=config.process_energy
    )
    handles = np.zeros(experiment.V036_HANDLE_COUNT)
    context = np.asarray([1.0, 0.0])
    hold = experiment.V036_ACTIONS[0]
    east = experiment.V036_ACTIONS[1]
    wrong_pair = (world.stable_pair[0], (world.stable_pair[1] + 1) % 6)

    matching_hold = experiment._world_transition(
        np.random.default_rng(3),
        config,
        world,
        phase,
        observation,
        bank,
        handles,
        hold,
        context,
        world.stable_pair,
    )
    matching_east = experiment._world_transition(
        np.random.default_rng(3),
        config,
        world,
        phase,
        observation,
        bank,
        handles,
        east,
        context,
        world.stable_pair,
    )
    wrong_hold = experiment._world_transition(
        np.random.default_rng(3),
        config,
        world,
        phase,
        observation,
        bank,
        handles,
        hold,
        context,
        wrong_pair,
    )
    wrong_east = experiment._world_transition(
        np.random.default_rng(3),
        config,
        world,
        phase,
        observation,
        bank,
        handles,
        east,
        context,
        wrong_pair,
    )

    np.testing.assert_allclose(
        matching_east[0] - matching_hold[0], world.action_effect[0]
    )
    assert matching_east[1] > matching_hold[1]
    assert matching_east[4] and matching_hold[4]
    np.testing.assert_array_equal(wrong_east[0], wrong_hold[0])
    assert wrong_east[1] == wrong_hold[1] == 0.0
    assert not wrong_east[4] and not wrong_hold[4]


def test_sealed_design_encodes_public_pair_and_action_interactions() -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    boundary = experiment._boundary_config(seed)
    runtime = UnifiedCausalLoop(
        experiment._agent(boundary, seed), experiment._runtime_config(seed)
    )
    certificate = PublicBoundaryCertificate(
        time=0,
        pair=(2, 4),
        rank=2,
        internal_projector=np.eye(experiment.V036_PROCESS_DIM),
        sensory_projector=np.eye(experiment.V036_OBSERVATION_DIM),
        effect_operator=np.zeros(
            (experiment.V036_PROCESS_DIM, experiment.V036_OBSERVATION_DIM)
        ),
        confidence=0.8,
        uncertainty=0.2,
        change_alarm=0.0,
        epoch=1,
        model_digest="a" * 64,
        workspace_access_digest="b" * 64,
        digest="c" * 64,
    )
    selection = runtime._select_action(
        time=0,
        observation=np.zeros(experiment.V036_OBSERVATION_DIM),
        context=np.asarray([0.4, -0.7]),
        candidates=experiment._action_candidates(),
        certificate=certificate,
    )
    telemetry = experiment._public_design_telemetry(selection, certificate)
    expected = np.zeros(1 + experiment.V036_HANDLE_COUNT + experiment.V036_SOURCE_COUNT)
    expected[0] = 1.0
    expected[1 + 2] = 1.0
    expected[1 + experiment.V036_HANDLE_COUNT + 4] = 1.0
    np.testing.assert_array_equal(telemetry["expected_public_identity"], expected)
    assert telemetry["public_identity_encoding_valid"]
    assert telemetry["public_action_identity_interactions_valid"]
    assert telemetry["action_certificate_reference_valid"]
    np.testing.assert_array_equal(selection.route_strengths, np.zeros(5))


def test_short_trace_is_one_closed_prequential_loop(
    short_trace: tuple[list[dict[str, object]], dict[str, object]],
) -> None:
    rows, summary = short_trace
    assert len(rows) == 10
    assert [row["transition_index"] for row in rows] == list(range(10))
    assert len({row["runtime_instance_digest"] for row in rows}) == 1
    assert all(row["prequential_chain_valid"] for row in rows)
    assert all(row["process_bank_replay_valid"] for row in rows)
    assert all(np.allclose(row["route_strengths"], 0.0) for row in rows)
    assert all(
        np.all(np.isfinite(row["predicted_next_observations"])) for row in rows
    )
    assert all(row["candidate_preview_all_null"] for row in rows)
    assert all(row["public_identity_encoding_valid"] for row in rows)
    assert all(
        row["public_action_identity_interactions_valid"] for row in rows
    )
    assert all(summary["integrity"].values())
    assert summary["phase_model_update_counts"] == {
        "stable": {"transition": 2, "return": 2},
        "world_shock": {"transition": 4, "return": 4},
        "remap": {"transition": 6, "return": 6},
        "disconnect": {"transition": 8, "return": 8},
        "restore": {"transition": 10, "return": 10},
    }
    terminal = summary["terminal_flush"]
    assert terminal["closed"]
    assert terminal["causal_transition_digest"] == rows[-1][
        "bound_transition_digest"
    ]


def test_jsonl_summary_and_hash_manifest_are_replayable(
    tmp_path: Path,
    short_trace: tuple[list[dict[str, object]], dict[str, object]],
) -> None:
    rows, summary = short_trace
    hashes = experiment._write_evidence_artifacts(rows, summary, tmp_path)
    rows_path = tmp_path / "v036_unified_causal_loop_rows.jsonl"
    summary_path = tmp_path / "v036_unified_causal_loop_summary.json"
    manifest_path = tmp_path / "artifact_sha256.json"
    parsed_rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    assert len(parsed_rows) == len(rows)
    assert json.loads(summary_path.read_text())["seed"] == 6451
    assert json.loads(manifest_path.read_text()) == hashes
    assert hashes[rows_path.name] == hashlib.sha256(rows_path.read_bytes()).hexdigest()
    assert hashes[summary_path.name] == hashlib.sha256(
        summary_path.read_bytes()
    ).hexdigest()
    with pytest.raises(FileExistsError):
        experiment._write_evidence_artifacts(rows, summary, tmp_path)


def test_campaign_requires_explicit_valid_attempt_and_fixed_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "campaign"
    output = root / "runs" / "attempt"
    monkeypatch.setattr(experiment, "V036_CAMPAIGN_ROOT", root)
    with pytest.raises(ValueError, match="attempt_id is required"):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            output,
        )
    with pytest.raises(ValueError, match="inside the fixed campaign_root"):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            tmp_path / "outside" / "attempt",
            attempt_id="P-TEST-001",
        )


def test_start_receipt_and_claims_precede_rng_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "campaign"
    output = root / "runs" / "P-TEST-START"
    monkeypatch.setattr(experiment, "V036_CAMPAIGN_ROOT", root)

    def stop_at_first_seed_sequence(*_: object, **__: object) -> None:
        receipt = output / experiment.V036_RUN_START_RECEIPT
        assert receipt.is_file()
        assert json.loads(receipt.read_text(encoding="utf-8"))["status"] == (
            "started_before_rng_construction"
        )
        raise RuntimeError("first RNG construction reached")

    monkeypatch.setattr(experiment.np.random, "SeedSequence", stop_at_first_seed_sequence)
    with pytest.raises(RuntimeError, match="first RNG construction reached"):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            output,
            attempt_id="P-TEST-START",
        )

    assert (root / "claims" / "attempts" / "P-TEST-START.json").is_file()
    assert (
        root
        / "claims"
        / "seeds"
        / f"pilot-seed-{experiment.V036_FIRST_PILOT_SEED}.json"
    ).is_file()
    assert (output / "v036_run_failure_receipt.json").is_file()


def test_campaign_seed_claim_blocks_a_second_output_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "campaign"
    monkeypatch.setattr(experiment, "V036_CAMPAIGN_ROOT", root)

    def fail_trace(*_: object, **__: object) -> None:
        raise RuntimeError("injected campaign stop")

    monkeypatch.setattr(experiment, "_run_trace", fail_trace)
    with pytest.raises(RuntimeError, match="injected campaign stop"):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            root / "runs" / "first",
            attempt_id="P-TEST-FIRST",
        )
    with pytest.raises(FileExistsError):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            root / "runs" / "second",
            attempt_id="P-TEST-SECOND",
        )
    assert not (
        root / "claims" / "attempts" / "P-TEST-SECOND.json"
    ).exists()
    assert not (
        root / "runs" / "second" / experiment.V036_RUN_START_RECEIPT
    ).exists()


def test_failed_campaign_preserves_each_complete_streamed_row(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "campaign"
    output = root / "runs" / "partial"
    monkeypatch.setattr(experiment, "V036_CAMPAIGN_ROOT", root)
    partial_rows = (
        {"seed": experiment.V036_FIRST_PILOT_SEED, "transition_index": 0},
        {"seed": experiment.V036_FIRST_PILOT_SEED, "transition_index": 1},
    )

    def fail_after_rows(
        *_: object,
        sealed_row_sink: object,
        **__: object,
    ) -> None:
        assert callable(sealed_row_sink)
        for row in partial_rows:
            sealed_row_sink(row)
        raise RuntimeError("injected failure after durable rows")

    monkeypatch.setattr(experiment, "_run_trace", fail_after_rows)
    with pytest.raises(RuntimeError, match="injected failure after durable rows"):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            output,
            attempt_id="P-TEST-PARTIAL",
        )

    rows_path = output / experiment.V036_ROWS_ARTIFACT
    recovered = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    assert recovered == list(partial_rows)
    failure = json.loads(
        (output / "v036_run_failure_receipt.json").read_text(encoding="utf-8")
    )
    assert failure["status"] == "INTEGRITY_FAIL"
    assert failure["scientific_classification"] == "INTEGRITY_FAIL"
    assert failure["operational_status"] == "interrupted_or_failed"
    assert not failure["typed_hard_integrity_failure"]
    assert failure["durably_streamed_rows"] == 2
    assert failure["partial_rows_sha256"] == hashlib.sha256(
        rows_path.read_bytes()
    ).hexdigest()


def test_typed_hard_failure_receipt_is_classified_integrity_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "campaign"
    output = root / "runs" / "typed-hard-failure"
    monkeypatch.setattr(experiment, "V036_CAMPAIGN_ROOT", root)

    def fail_hard(*_: object, **__: object) -> None:
        raise experiment.HardIntegrityError("injected typed integrity failure")

    monkeypatch.setattr(experiment, "_run_trace", fail_hard)
    with pytest.raises(
        experiment.HardIntegrityError,
        match="injected typed integrity failure",
    ):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_FIRST_PILOT_SEED,
            output,
            attempt_id="P-TEST-TYPED-HARD",
        )

    failure = json.loads(
        (output / "v036_run_failure_receipt.json").read_text(encoding="utf-8")
    )
    assert failure["status"] == "INTEGRITY_FAIL"
    assert failure["scientific_classification"] == "INTEGRITY_FAIL"
    assert failure["typed_hard_integrity_failure"]


def test_hard_integrity_failure_is_streamed_before_immediate_stop(
    short_trace: tuple[list[dict[str, object]], dict[str, object]],
) -> None:
    row = dict(short_trace[0][0])
    row["runtime_identity_ok"] = False
    streamed: list[dict[str, object]] = []

    with pytest.raises(
        experiment.HardIntegrityError,
        match="hard-integrity failure after sealing",
    ):
        experiment._seal_row_or_stop(row, lambda value: streamed.append(dict(value)))

    assert len(streamed) == 1
    assert not streamed[0]["hard_integrity_valid"]
    assert not streamed[0]["hard_integrity_checks"]["runtime_identity"]


def test_hard_integrity_stop_precedes_the_next_world_consequence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    config = experiment.V036ExperimentConfig(
        stable_steps=1,
        world_shock_steps=1,
        remap_steps=1,
        disconnect_steps=1,
        restore_steps=1,
    )
    real_world_transition = experiment._world_transition
    real_reveal_row = experiment._reveal_row
    world_calls = 0
    streamed: list[dict[str, object]] = []

    def counted_world_transition(*args: object, **kwargs: object) -> object:
        nonlocal world_calls
        world_calls += 1
        return real_world_transition(*args, **kwargs)

    def corrupt_first_revealed_row(*args: object, **kwargs: object) -> dict[str, object]:
        row = real_reveal_row(*args, **kwargs)
        row["runtime_identity_ok"] = False
        return row

    monkeypatch.setattr(experiment, "_world_transition", counted_world_transition)
    monkeypatch.setattr(experiment, "_reveal_row", corrupt_first_revealed_row)

    with pytest.raises(
        experiment.HardIntegrityError,
        match="hard-integrity failure after sealing",
    ):
        experiment._run_trace(
            seed,
            experiment_config=config,
            boundary_config=experiment._boundary_config(seed),
            runtime_config=experiment._runtime_config(seed),
            sealed_row_sink=lambda row: streamed.append(dict(row)),
        )

    assert world_calls == 1
    assert len(streamed) == 1
    assert streamed[0]["transition_index"] == 0


def test_nonfinite_hard_failure_row_is_durably_tagged(
    tmp_path: Path,
    short_trace: tuple[list[dict[str, object]], dict[str, object]],
) -> None:
    row = dict(short_trace[0][0])
    row["realized_external_return"] = float("nan")
    stream = experiment._DurableRowStream(tmp_path / experiment.V036_ROWS_ARTIFACT)

    try:
        with pytest.raises(
            experiment.HardIntegrityError,
            match="hard-integrity failure after sealing",
        ):
            experiment._seal_row_or_stop(row, stream.append)
    finally:
        stream.close()

    assert stream.row_count == 1
    sealed = json.loads(stream.path.read_text(encoding="utf-8"))
    assert sealed["failure_row_schema"] == (
        "rrct.v036.hard_integrity_failure_row.v1"
    )
    assert not sealed["hard_integrity_valid"]
    assert not sealed["hard_integrity_checks"]["finite_numeric_payload"]
    assert sealed["realized_external_return"] == {
        "schema": "rrct.v036.tagged_nonfinite.v1",
        "value": "NaN",
    }


def test_development_freeze_verifies_every_frozen_source_checksum(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    validation = project / "validation"
    source = project / "src" / "frozen.py"
    validation.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    source.write_bytes(b"frozen source\n")
    manifest = validation / "V0_36_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_36_PREOUTCOME_FREEZE.json.sha256"
    payload = {
        "schema": "rrct.v036.preoutcome_freeze.v1",
        "status": "sealed_before_development_outcomes",
        "development_seeds": list(experiment.V036_DEVELOPMENT_SEEDS),
        "files": {
            "src/frozen.py": {
                "size": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        },
    }
    manifest.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    manifest_digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    checksum.write_text(
        f"{manifest_digest}  {manifest.name}\n", encoding="ascii"
    )
    monkeypatch.setattr(experiment, "V036_PROJECT_ROOT", project)
    monkeypatch.setattr(experiment, "V036_DEVELOPMENT_FREEZE_MANIFEST", manifest)
    monkeypatch.setattr(experiment, "V036_DEVELOPMENT_FREEZE_CHECKSUM", checksum)
    monkeypatch.setattr(
        experiment,
        "V036_REQUIRED_DEVELOPMENT_FREEZE_FILES",
        ("src/frozen.py",),
    )

    assert experiment._verify_development_freeze() == manifest_digest
    source.write_bytes(b"tampered\n")
    with pytest.raises(RuntimeError, match="frozen source checksum mismatch"):
        experiment._verify_development_freeze()


def test_development_freeze_cannot_omit_a_required_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    validation = project / "validation"
    source = project / "src" / "frozen.py"
    validation.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    source.write_bytes(b"frozen source\n")
    manifest = validation / "V0_36_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_36_PREOUTCOME_FREEZE.json.sha256"
    payload = {
        "schema": "rrct.v036.preoutcome_freeze.v1",
        "status": "sealed_before_development_outcomes",
        "development_seeds": list(experiment.V036_DEVELOPMENT_SEEDS),
        "files": {
            "src/frozen.py": {
                "size": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        },
    }
    manifest.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    checksum.write_text(
        f"{hashlib.sha256(manifest.read_bytes()).hexdigest()}  {manifest.name}\n",
        encoding="ascii",
    )
    monkeypatch.setattr(experiment, "V036_PROJECT_ROOT", project)
    monkeypatch.setattr(experiment, "V036_DEVELOPMENT_FREEZE_MANIFEST", manifest)
    monkeypatch.setattr(experiment, "V036_DEVELOPMENT_FREEZE_CHECKSUM", checksum)
    monkeypatch.setattr(
        experiment,
        "V036_REQUIRED_DEVELOPMENT_FREEZE_FILES",
        ("src/frozen.py", "tests/test_required.py"),
    )

    with pytest.raises(RuntimeError, match="omits required files"):
        experiment._verify_development_freeze()


def test_allow_development_stops_before_claim_without_a_freeze(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "campaign"
    monkeypatch.setattr(experiment, "V036_CAMPAIGN_ROOT", root)
    monkeypatch.setattr(
        experiment,
        "V036_DEVELOPMENT_FREEZE_MANIFEST",
        tmp_path / "missing-freeze.json",
    )
    monkeypatch.setattr(
        experiment,
        "V036_DEVELOPMENT_FREEZE_CHECKSUM",
        tmp_path / "missing-freeze.json.sha256",
    )

    with pytest.raises(RuntimeError, match="requires a frozen"):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_DEVELOPMENT_SEEDS[0],
            root / "runs" / "development",
            cohort="development",
            allow_development=True,
            attempt_id="D-TEST-NOFREEZE",
        )
    assert not (root / "claims").exists()


def test_campaign_status_never_turns_a_pilot_into_a_development_claim() -> None:
    endpoints = {f"E{index:02d}": True for index in range(1, 9)}
    endpoints["E01_integrity"] = True
    assert experiment._campaign_status(
        experiment.V036_FIRST_PILOT_SEED, endpoints
    ) == "PILOT_ENDPOINTS_MET"
    assert experiment._campaign_status(
        experiment.V036_DEVELOPMENT_SEEDS[0], endpoints
    ) == "DEVELOPMENT_SEED_ENDPOINTS_MET"
    endpoints["E08"] = False
    assert experiment._campaign_status(
        experiment.V036_FIRST_PILOT_SEED, endpoints
    ) == "PILOT_ENDPOINTS_NOT_MET"


def test_development_seed_guard_fires_before_execution(tmp_path: Path) -> None:
    with pytest.raises(PermissionError):
        experiment.run_unified_causal_loop_seed(
            experiment.V036_DEVELOPMENT_SEEDS[0],
            tmp_path,
            cohort="development",
        )


def test_public_design_audit_rejects_a_tampered_identity_column() -> None:
    identity_dim = 1 + experiment.V036_HANDLE_COUNT + experiment.V036_SOURCE_COUNT
    total_design_dim = (
        1
        + experiment.V036_OBSERVATION_DIM
        + experiment.V036_CONTEXT_DIM
        + experiment.V036_ACTION_DIM
        + 7
        + identity_dim
        + experiment.V036_ACTION_DIM * experiment.V036_CONTEXT_DIM
        + experiment.V036_ACTION_DIM * experiment.V036_OBSERVATION_DIM
        + experiment.V036_ACTION_DIM
        + experiment.V036_ACTION_DIM * 5
        + experiment.V036_ACTION_DIM * experiment.V036_CONTEXT_DIM
        + experiment.V036_ACTION_DIM * identity_dim
    )
    selection = SimpleNamespace(
        candidate_designs=np.zeros((5, total_design_dim)),
        candidate_actions=experiment.V036_ACTIONS,
        candidate_keys=experiment.V036_ACTION_KEYS,
        public_certificate_digest=None,
    )
    selection.candidate_designs[0, -1] = 1.0
    telemetry = experiment._public_design_telemetry(selection, None)
    assert telemetry["public_identity_encoding_valid"]
    assert not telemetry["public_action_identity_interactions_valid"]


def test_candidate_overflow_is_rejected_before_agent_mutation() -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    agent = experiment._agent(experiment._boundary_config(seed), seed)
    runtime = UnifiedCausalLoop(agent, experiment._runtime_config(seed))
    bank = experiment._equal_energy_process_bank(
        np.random.default_rng(17), energy=np.sqrt(experiment.V036_PROCESS_DIM)
    )
    runtime.precommit_process_bank(bank)
    unsafe = (
        ActionCandidate("overflow", np.zeros(2), 1e308, 1e308),
        ActionCandidate("finite", np.ones(2)),
    )

    with pytest.raises(ValueError, match="candidate_value_bound"):
        runtime.advance(
            np.zeros(experiment.V036_OBSERVATION_DIM),
            unsafe,
            observable_context=np.zeros(experiment.V036_CONTEXT_DIM),
        )

    assert agent.time == 0
    assert agent.causal_boundary is not None
    assert not agent.causal_boundary.has_pending
    assert not runtime.closed
    assert not runtime.awaiting_process_bank


def test_drift_capacity_must_hold_identifiable_design() -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    agent = experiment._agent(experiment._boundary_config(seed), seed)
    required = (
        1
        + experiment.V036_OBSERVATION_DIM
        + experiment.V036_SOURCE_COUNT * experiment.V036_PROCESS_DIM
        + experiment.V036_HANDLE_COUNT
        + experiment.V036_PROCESS_DIM
        + 1
    )
    invalid = replace(
        experiment._runtime_config(seed),
        drift_capacity=required - 1,
        drift_baseline_samples=required - 1,
        drift_recent_samples=required - 1,
    )

    with pytest.raises(ValueError, match="identifiable drift design"):
        UnifiedCausalLoop(agent, invalid)


def test_terminal_flush_preserves_last_executed_action() -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    agent = experiment._agent(experiment._boundary_config(seed), seed)
    runtime = UnifiedCausalLoop(agent, experiment._runtime_config(seed))
    bank = experiment._equal_energy_process_bank(
        np.random.default_rng(19), energy=np.sqrt(experiment.V036_PROCESS_DIM)
    )
    runtime.precommit_process_bank(bank)
    step = runtime.advance(
        np.zeros(experiment.V036_OBSERVATION_DIM),
        experiment._action_candidates(),
        observable_context=np.asarray([1.0, 0.0]),
    )
    before = agent.choose_action().copy()
    np.testing.assert_array_equal(before, step.action)

    terminal = runtime.flush(
        0.1 * np.ones(experiment.V036_OBSERVATION_DIM),
        realized_external_return=0.2,
    )

    np.testing.assert_array_equal(agent.choose_action(), before)
    assert runtime.closed
    assert not runtime.awaiting_outcome
    assert agent.causal_boundary is not None
    assert not agent.causal_boundary.has_pending
    assert terminal.randomized_row_count == 1
    assert runtime._transition_model.observation_count == 1


def test_replaced_private_transition_is_detected_before_model_update() -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    agents = [
        experiment._agent(experiment._boundary_config(seed), seed) for _ in range(2)
    ]
    runtimes = [
        UnifiedCausalLoop(agent, experiment._runtime_config(seed))
        for agent in agents
    ]
    rng = np.random.default_rng(23)
    for runtime in runtimes:
        bank = experiment._equal_energy_process_bank(
            rng, energy=np.sqrt(experiment.V036_PROCESS_DIM)
        )
        runtime.precommit_process_bank(bank)
        runtime.advance(
            np.zeros(experiment.V036_OBSERVATION_DIM),
            experiment._action_candidates(),
            observable_context=np.asarray([1.0, 0.0]),
        )

    assert agents[0].causal_boundary is not None
    assert agents[1].causal_boundary is not None
    agents[0].causal_boundary.load_snapshot(agents[1].causal_boundary.snapshot())
    bank = experiment._equal_energy_process_bank(
        rng, energy=np.sqrt(experiment.V036_PROCESS_DIM)
    )
    runtimes[0].precommit_process_bank(bank)

    with pytest.raises(RuntimeError, match="does not match"):
        runtimes[0].advance(
            0.1 * np.ones(experiment.V036_OBSERVATION_DIM),
            experiment._action_candidates(),
            observable_context=np.asarray([0.0, 1.0]),
            realized_external_return=0.2,
        )

    assert runtimes[0].closed
    assert runtimes[0]._transition_model.observation_count == 0
    assert runtimes[0].randomized_row_count == 0


def test_post_step_failure_permanently_closes_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    agent = experiment._agent(experiment._boundary_config(seed), seed)
    runtime = UnifiedCausalLoop(agent, experiment._runtime_config(seed))
    bank = experiment._equal_energy_process_bank(
        np.random.default_rng(29), energy=np.sqrt(experiment.V036_PROCESS_DIM)
    )
    runtime.precommit_process_bank(bank)

    def fail_selection(**_: object) -> None:
        raise RuntimeError("injected post-step failure")

    monkeypatch.setattr(runtime, "_select_action", fail_selection)
    with pytest.raises(RuntimeError, match="injected post-step failure"):
        runtime.advance(
            np.zeros(experiment.V036_OBSERVATION_DIM),
            experiment._action_candidates(),
            observable_context=np.zeros(experiment.V036_CONTEXT_DIM),
        )

    assert agent.time == 1
    assert runtime.closed


def test_missing_post_step_commitment_fails_closed() -> None:
    seed = experiment.V036_FIRST_PILOT_SEED
    agent = experiment._agent(experiment._boundary_config(seed), seed)
    runtime = UnifiedCausalLoop(agent, experiment._runtime_config(seed))
    bank = experiment._equal_energy_process_bank(
        np.random.default_rng(31), energy=np.sqrt(experiment.V036_PROCESS_DIM)
    )
    runtime.precommit_process_bank(bank)
    agent.causal_boundary = None

    with pytest.raises(RuntimeError, match="emitted no handle commitment"):
        runtime.advance(
            np.zeros(experiment.V036_OBSERVATION_DIM),
            experiment._action_candidates(),
            observable_context=np.zeros(experiment.V036_CONTEXT_DIM),
        )

    assert agent.time == 1
    assert runtime.closed
    assert not runtime.awaiting_outcome
