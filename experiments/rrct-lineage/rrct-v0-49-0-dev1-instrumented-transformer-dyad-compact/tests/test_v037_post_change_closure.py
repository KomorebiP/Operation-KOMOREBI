"""Focused v0.37 public-boundary quarantine and schedule checks."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import rrct.unified_causal_loop_experiment as v036
import rrct.post_change_closure_experiment as v037
from rrct.post_change_closure_experiment import (
    V037_D1_CONFIG,
    V037ExperimentConfig,
    run_post_change_closure_trace,
)
from rrct.unified_causal_loop import (
    DriftAssessment,
    PublicBoundaryCertificate,
    UnifiedCausalLoop,
)


def _certificate(*, pair: tuple[int, int], epoch: int, digest_char: str) -> PublicBoundaryCertificate:
    return PublicBoundaryCertificate(
        time=0,
        pair=pair,
        rank=2,
        internal_projector=np.eye(v036.V036_PROCESS_DIM),
        sensory_projector=np.eye(v036.V036_OBSERVATION_DIM),
        effect_operator=np.zeros(
            (v036.V036_PROCESS_DIM, v036.V036_OBSERVATION_DIM),
            dtype=np.float64,
        ),
        confidence=0.9,
        uncertainty=0.1,
        change_alarm=0.0,
        epoch=epoch,
        model_digest=digest_char * 64,
        workspace_access_digest=digest_char.upper() * 64,
        digest=("f" if digest_char == "a" else "e") * 64,
    )


def _drift(pair: tuple[int, int], *, digest_char: str = "d") -> DriftAssessment:
    return DriftAssessment(
        time=1,
        pair=pair,
        rank=2,
        baseline_samples=240,
        recent_samples=240,
        relative_drift=0.8,
        baseline_norm=1.0,
        recent_norm=0.2,
        reopen_requested=True,
        reason="interface_drift",
        digest=digest_char * 64,
    )


def _runtime(seed: int = 7403) -> UnifiedCausalLoop:
    boundary = v036._boundary_config(seed)
    config = replace(
        v036._runtime_config(seed),
        quarantine_public_certificate_on_drift=True,
    )
    return UnifiedCausalLoop(v036._agent(boundary, seed), config)


def test_drift_alarm_quarantines_before_the_next_action_and_new_signature_releases() -> None:
    runtime = _runtime()
    old = _certificate(pair=(0, 1), epoch=1, digest_char="a")
    new = _certificate(pair=(3, 2), epoch=2, digest_char="b")

    effective, receipt = runtime._gate_public_certificate(
        time=10,
        raw_certificate=old,
        drift=None,
    )
    assert effective is not None and effective.digest == old.digest
    assert receipt.event == "pass"
    runtime._public_boundary = effective

    effective, receipt = runtime._gate_public_certificate(
        time=11,
        raw_certificate=old,
        drift=_drift(old.pair),
    )
    assert effective is None
    assert receipt.event == "entered"
    assert receipt.quarantine_active
    assert receipt.quarantine_signature == old.structural_signature
    runtime._public_boundary = effective

    effective, receipt = runtime._gate_public_certificate(
        time=12,
        raw_certificate=old,
        drift=None,
    )
    assert effective is None
    assert receipt.event == "held"
    assert receipt.quarantine_active

    effective, receipt = runtime._gate_public_certificate(
        time=13,
        raw_certificate=new,
        drift=None,
    )
    assert effective is not None and effective.digest == new.digest
    assert receipt.event == "released"
    assert not receipt.quarantine_active
    assert receipt.quarantine_signature is None


def test_quarantine_is_disabled_by_default_for_v036_compatibility() -> None:
    seed = 7403
    runtime = UnifiedCausalLoop(
        v036._agent(v036._boundary_config(seed), seed),
        v036._runtime_config(seed),
    )
    old = _certificate(pair=(0, 1), epoch=1, digest_char="a")
    effective, receipt = runtime._gate_public_certificate(
        time=1,
        raw_certificate=old,
        drift=_drift(old.pair),
    )
    assert effective is not None and effective.digest == old.digest
    assert receipt.event == "disabled"
    assert not receipt.quarantine_active


def test_d1_schedule_reserves_a_fixed_post_change_action_tail() -> None:
    assert V037_D1_CONFIG.total_steps == 6_240
    assert V037_D1_CONFIG.recovery_tail_steps == 480
    for phase in ("remap_steps", "disconnect_steps", "restore_steps"):
        assert getattr(V037_D1_CONFIG, phase) >= (
            V037_D1_CONFIG.confirmation_budget_steps
            + V037_D1_CONFIG.recovery_tail_steps
        )


def test_short_d1_trace_seals_rollout_controls_and_gate_receipts() -> None:
    config = V037ExperimentConfig(
        stable_steps=4,
        world_shock_steps=2,
        remap_steps=4,
        disconnect_steps=4,
        restore_steps=4,
        recovery_tail_steps=2,
        confirmation_budget_steps=2,
    )
    rows, summary = run_post_change_closure_trace(
        123,
        experiment_config=config,
    )

    assert len(rows) == config.total_steps == 18
    assert all(row["hard_integrity_valid"] for row in rows)
    assert all("action_public_gate_receipt" in row for row in rows)
    assert all("public_gate_after_reveal" in row for row in rows)
    assert all(
        set(row["controls"])
        == {"no_certificate", "phase_stale", "shuffled_certificate"}
        for row in rows
    )
    assert all(
        row["transition_rollout"]["policy_score_reconstruction_valid"]
        for row in rows
    )
    assert all(
        row["hard_integrity_checks"]["action_gate_certificate_binding"]
        and row["hard_integrity_checks"]["reveal_gate_certificate_binding"]
        and row["hard_integrity_checks"]["public_gate_quarantine_enabled"]
        for row in rows
    )
    assert any(
        row["transition_rollout"]["rollout_propensity_l1_shift"] > 1e-12
        for row in rows
    )
    assert summary["integrity"]["v037_hard_integrity_all"]
    assert summary["unified_runtime_config"][
        "quarantine_public_certificate_on_drift"
    ]
    assert summary["unified_runtime_config"]["transition_rollout_weight"] > 0.0
    assert "F10_world_shock_specificity" in summary["endpoints"]



def test_change_summary_anchors_stale_certificate_to_the_alarm_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(v037, "_tail_summary", lambda rows, tail_steps: {})

    def row(
        offset: int,
        digest: str | None,
        *,
        alarm: bool = False,
        gate_event: str = "pass",
        structural_event: str = "none",
        gate_open: bool = False,
    ) -> dict[str, object]:
        return {
            "phase_offset": offset,
            "reopen_requested": alarm,
            "public_gate_event_after_reveal": gate_event,
            "structural_event": structural_event,
            "action_public_certificate_digest": digest,
            "action_gate_open_evaluator_only": gate_open,
            "action_public_pair": None if digest is None else [0, 1],
        }

    rows = [
        row(0, "phase-entry"),
        row(1, "phase-entry"),
        row(2, "alarm-time", alarm=True, gate_event="entered"),
        row(3, None),
        row(4, "alarm-time", structural_event="pair_revision"),
        row(5, "new", gate_open=True),
    ]
    summary = v037._change_summary(rows, "remap", tail_steps=2)

    assert summary["alarm_latency"] == 3
    assert summary["quarantine_entry_latency"] == 3
    assert summary["stale_action_retirement_latency"] == 4
    assert summary["stale_action_retirement_delay"] == 1
    assert summary["stale_action_reuse_after_retirement_count"] == 1
    assert summary["private_change_latency"] == 5
    assert summary["first_correct_action_latency"] == 6
    assert summary["public_release_delay"] == 1


def test_campaign_ledger_claims_each_attempt_and_seed_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    campaign = (tmp_path / "campaign").resolve()
    monkeypatch.setattr(v037, "V037_CAMPAIGN_ROOT", campaign)
    output = campaign / "D1-P-TEST-0001"
    root, destination, start_digest = v037._prepare_v037_campaign_attempt(
        seed=v037.V037_FIRST_PILOT_SEED,
        attempt_id="D1-P-TEST-0001",
        output=output,
        freeze_sha256="a" * 64,
    )

    assert root == campaign
    assert destination == output
    assert len(start_digest) == 64
    assert (output / v037.V037_RUN_START_RECEIPT).is_file()
    assert (
        campaign
        / "claims"
        / "attempts"
        / "D1-P-TEST-0001.json"
    ).is_file()
    assert (
        campaign
        / "claims"
        / "seeds"
        / f"pilot-seed-{v037.V037_FIRST_PILOT_SEED}.json"
    ).is_file()

    with pytest.raises(FileExistsError, match="pilot seed"):
        v037._prepare_v037_campaign_attempt(
            seed=v037.V037_FIRST_PILOT_SEED,
            attempt_id="D1-P-TEST-0002",
            output=campaign / "D1-P-TEST-0002",
            freeze_sha256="a" * 64,
        )


@pytest.mark.parametrize(
    "attempt_id",
    [None, "", "bad attempt", "/absolute", "x" * 65],
)
def test_campaign_attempt_identifier_is_fail_closed(attempt_id: str | None) -> None:
    with pytest.raises(ValueError):
        v037._validate_v037_attempt_id(attempt_id)


def test_default_zero_rollout_reproduces_the_v036_policy_score() -> None:
    seed = 7411
    runtime = UnifiedCausalLoop(
        v036._agent(v036._boundary_config(seed), seed),
        v036._runtime_config(seed),
    )
    candidates = v036._action_candidates()
    selection = runtime._select_action(
        time=0,
        observation=np.linspace(-0.4, 0.4, v036.V036_OBSERVATION_DIM),
        context=np.asarray([0.6, -0.2]),
        candidates=candidates,
        certificate=None,
    )
    expected = np.asarray(
        [
            candidate.immediate_external_value
            + max(
                float(selection.predicted_external_returns[index]),
                candidate.alternative_competence,
            )
            for index, candidate in enumerate(candidates)
        ],
        dtype=np.float64,
    )
    assert selection.transition_rollout_weight == 0.0
    np.testing.assert_array_equal(selection.one_step_rollout_values, np.zeros(5))
    np.testing.assert_allclose(selection.policy_scores, expected, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        selection.counterfactual_no_certificate_returns,
        selection.predicted_external_returns,
        rtol=0.0,
        atol=0.0,
    )
    assert selection.public_boundary_value_advantage == 0.0


def test_positive_rollout_uses_predicted_next_state_in_policy_scores(
    monkeypatch,
) -> None:
    seed = 7417
    config = replace(
        v036._runtime_config(seed),
        transition_rollout_weight=0.35,
    )
    runtime = UnifiedCausalLoop(
        v036._agent(v036._boundary_config(seed), seed),
        config,
    )
    candidates = v036._action_candidates()
    probe = runtime._design(
        np.zeros(v036.V036_OBSERVATION_DIM),
        np.zeros(v036.V036_CONTEXT_DIM),
        candidates[0],
        0.0,
        None,
    )
    design_dim = len(probe)
    transition_coefficients = np.zeros(
        (design_dim, v036.V036_OBSERVATION_DIM), dtype=np.float64
    )
    return_coefficients = np.zeros((design_dim, 1), dtype=np.float64)

    observation_start = 1
    action_start = 1 + v036.V036_OBSERVATION_DIM + v036.V036_CONTEXT_DIM
    transition_coefficients[action_start, 0] = 1.0
    return_coefficients[observation_start, 0] = 1.0
    monkeypatch.setattr(
        runtime._transition_model,
        "coefficients",
        lambda: transition_coefficients.copy(),
    )
    monkeypatch.setattr(
        runtime._return_model,
        "coefficients",
        lambda: return_coefficients.copy(),
    )

    selection = runtime._select_action(
        time=0,
        observation=np.zeros(v036.V036_OBSERVATION_DIM),
        context=np.zeros(v036.V036_CONTEXT_DIM),
        candidates=candidates,
        certificate=None,
    )
    east = v036.V036_ACTION_KEYS.index("east")
    hold = v036.V036_ACTION_KEYS.index("hold")
    west = v036.V036_ACTION_KEYS.index("west")
    assert selection.one_step_rollout_values[east] > 0.0
    assert selection.one_step_rollout_values[west] == 0.0
    assert int(np.argmax(selection.policy_scores)) == east
    assert int(np.argmax(selection.predicted_external_returns)) == hold
    np.testing.assert_allclose(
        selection.policy_scores,
        config.transition_rollout_weight * selection.one_step_rollout_values,
        rtol=0.0,
        atol=1e-12,
    )


def test_short_v037_trace_has_paired_controls_and_closed_integrity() -> None:
    from rrct.post_change_closure_experiment import (
        V037_CONTROL_NAMES,
        V037_SCHEMA,
        V037ExperimentConfig,
        run_post_change_closure_trace,
    )

    config = V037ExperimentConfig(
        stable_steps=12,
        world_shock_steps=4,
        remap_steps=8,
        disconnect_steps=8,
        restore_steps=8,
        recovery_tail_steps=2,
        confirmation_budget_steps=6,
    )
    rows, summary = run_post_change_closure_trace(7499, experiment_config=config)
    assert len(rows) == config.total_steps
    assert summary["endpoints"]["F01_integrity"]
    assert summary["integrity"]["v037_shared_noise_all"]
    assert summary["integrity"]["v037_hard_integrity_all"]
    assert all(row["schema"] == V037_SCHEMA for row in rows)
    assert all(set(row["controls"]) == set(V037_CONTROL_NAMES) for row in rows)
    assert all(
        row["transition_rollout"]["policy_score_reconstruction_valid"]
        for row in rows
    )
    assert all(
        arm["observation_noise_sha256"] == row["observation_noise_sha256"]
        and arm["return_noise"] == row["return_noise"]
        for row in rows
        for arm in row["controls"].values()
    )
