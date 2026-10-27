"""Focused checks for v0.39 oracle-free active self-diagnosis."""
from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from rrct.agent import RRCTAgent
from rrct.autonomous_self_diagnosis import (
    AutonomousDiagnosticUnifiedCausalLoop,
    ConsequenceGroundedAccessController,
    ConsequenceGroundingConfig,
    validate_grounding_outcome_receipt,
)
from rrct.causal_boundary import DirectCausalAccessReadout
from rrct.post_change_closure_experiment import (
    V037ExperimentConfig,
    run_post_change_closure_trace,
)
from rrct.unified_causal_loop import (
    ActionOutcomeReceipt,
    PublicBoundaryCertificate,
)
from rrct.unified_causal_loop_experiment import (
    V036_OBSERVATION_DIM,
    V036_PROCESS_DIM,
    _agent,
    _boundary_config,
    _runtime_config,
)


def _certificate(epoch: int = 1) -> PublicBoundaryCertificate:
    return PublicBoundaryCertificate(
        time=0,
        pair=(1, 2),
        rank=2,
        internal_projector=np.eye(V036_PROCESS_DIM),
        sensory_projector=np.eye(V036_OBSERVATION_DIM),
        effect_operator=np.zeros((V036_PROCESS_DIM, V036_OBSERVATION_DIM)),
        confidence=0.95,
        uncertainty=0.05,
        change_alarm=0.0,
        epoch=epoch,
        model_digest="a" * 64,
        workspace_access_digest="b" * 64,
        digest=("c" if epoch == 1 else "d") * 64,
    )


def _result(*, active: bool = True, public: bool = True) -> SimpleNamespace:
    state = SimpleNamespace(active=active)
    return SimpleNamespace(
        causal_boundary_state=state,
        causal_boundary_proposal_selected=active,
        selected_specialists=("causal_boundary",) if active else (),
        causal_boundary_workspace_drive=(
            np.ones(4, dtype=np.float64) if active else np.zeros(4)
        ),
        ablations=(),
        causal_access_update_count=0,
        causal_public_pair=(1, 2) if public else None,
    )


def _selection(time: int) -> SimpleNamespace:
    return SimpleNamespace(
        selected_key="east",
        selected_action=np.asarray([1.0, 0.0], dtype=np.float64),
        observable_context=np.asarray([1.0, 0.0], dtype=np.float64),
    )


def _outcome(time: int, value: float, transition_error: float = 0.05) -> ActionOutcomeReceipt:
    return ActionOutcomeReceipt(
        selection_digest="e" * 64,
        reveal_time=time + 1,
        realized_external_return=value,
        predicted_external_return=0.0,
        return_prediction_error=value,
        transition_prediction_error=transition_error,
        inverse_propensity_weight=1.0,
        transition_model_updated=True,
        return_model_updated=True,
        digest="f" * 64,
    )


def _complete(
    controller: ConsequenceGroundedAccessController,
    time: int,
    certificate: PublicBoundaryCertificate,
    value: float,
):
    plan = controller.plan(
        time=time,
        raw_certificate=certificate,
        result=_result(),
    )
    controller.finalize_gate(
        plan, certificate if plan.requested_certificate_on else None
    )
    controller.bind_selection(plan, _selection(time))
    return controller.observe(plan, _outcome(time, value))


def test_direct_access_readout_is_label_free_and_snapshot_safe() -> None:
    readout = DirectCausalAccessReadout(5, 4, 6)
    prediction = readout.predict(np.zeros(5))
    assert prediction.pair is None
    assert readout.update_count == 0
    with pytest.raises(RuntimeError, match="label-free"):
        readout.update(np.zeros(5), (1, 2))
    snapshot = readout.snapshot()
    assert snapshot["strategy"] == "direct_workspace_candidate"
    assert snapshot["uses_class_labels"] is False
    restored = DirectCausalAccessReadout(5, 4, 6)
    restored.load_snapshot(snapshot)
    assert restored.snapshot()["digest"] == snapshot["digest"]


def test_controller_selects_on_off_probes_and_certifies_from_consequences() -> None:
    controller = ConsequenceGroundedAccessController()
    certificate = _certificate()
    receipts = []
    for time in range(6):
        # Correct candidate yields a strong return only when certificate is on.
        plan = controller.plan(
            time=time,
            raw_certificate=certificate,
            result=_result(),
        )
        value = 0.96 if plan.requested_certificate_on else 0.0
        controller.finalize_gate(
            plan, certificate if plan.requested_certificate_on else None
        )
        controller.bind_selection(plan, _selection(time))
        receipts.append(controller.observe(plan, _outcome(time, value)))
        if receipts[-1].status_after == "certified":
            break
    assert receipts[-1].status_after == "certified"
    assert "initial_boundary_certified" in receipts[-1].events
    assert receipts[-1].lower_bound is not None
    assert receipts[-1].lower_bound >= 0.45
    assert controller.authorization_count == 1
    assert controller.informative_probe_count >= 4
    assert all(not receipt.uses_evaluator_labels for receipt in receipts)


def test_grounding_receipt_digest_rejects_posthoc_tampering() -> None:
    controller = ConsequenceGroundedAccessController()
    certificate = _certificate()
    receipt = _complete(controller, 0, certificate, 0.96)
    assert validate_grounding_outcome_receipt(receipt)
    assert not validate_grounding_outcome_receipt(
        replace(receipt, recommended_response="tampered")
    )


def test_two_failed_sentinels_revoke_a_previously_certified_candidate() -> None:
    config = ConsequenceGroundingConfig(sentinel_interval=1)
    controller = ConsequenceGroundedAccessController(config)
    certificate = _certificate()
    for time in range(8):
        receipt = _complete(
            controller,
            time,
            certificate,
            0.96 if time % 2 == 0 else 0.0,
        )
        if receipt.status_after == "certified":
            start = time + 1
            break
    else:
        raise AssertionError("candidate never certified")
    ordinary = _complete(controller, start, certificate, 0.96)
    assert ordinary.mode == "ordinary_use"
    first = _complete(controller, start + 1, certificate, 0.0)
    second = _complete(controller, start + 2, certificate, 0.0)
    assert first.mode == "sentinel"
    assert "sentinel_failure" in first.events
    assert second.status_after == "revoked"
    assert "certificate_revoked_by_consequence" in second.events
    assert controller.revocation_count == 1


def test_internal_access_failure_is_distinguished_from_private_boundary_absence() -> None:
    controller = ConsequenceGroundedAccessController(
        ConsequenceGroundingConfig(access_fault_confirmations=2)
    )
    first = controller.plan(
        time=10,
        raw_certificate=None,
        result=_result(active=True, public=False),
    )
    second = controller.plan(
        time=11,
        raw_certificate=None,
        result=_result(active=True, public=False),
    )
    assert first.mode == "access_fault"
    assert second.mode == "access_fault"
    assert controller.access_fault_count == 1
    assert any(
        event["event"] == "access_path_failure"
        for event in controller.event_log
    )


def test_runtime_factory_supports_autonomous_loop_without_breaking_short_trace() -> None:
    seed = 12345
    config = V037ExperimentConfig(
        stable_steps=2,
        world_shock_steps=2,
        remap_steps=2,
        disconnect_steps=2,
        restore_steps=2,
        recovery_tail_steps=1,
        confirmation_budget_steps=1,
    )
    holder: list[AutonomousDiagnosticUnifiedCausalLoop] = []

    def agent_factory(boundary, run_seed):
        base = _agent(boundary, run_seed)
        return RRCTAgent(
            observation_dim=base.observation_dim,
            action_dim=base.action_dim,
            n_levels=base.n_levels,
            projector_ranks=base.projectors.ranks,
            n_specialists=base.n_specialists,
            specialist_dim=base.specialist_dim,
            workspace_dim=base.workspace_dim,
            workspace_capacity=base.workspace_capacity,
            self_dim=base.self_dim,
            memory_capacity=base.memory_capacity,
            memory_top_k=base.memory_top_k,
            seed=run_seed,
            recurrent_gain=base.recurrent_gain,
            closure_gain=base.closure_gain,
            self_feedback_gain=base.self_feedback_gain,
            action_feedback_gain=base.action_feedback_gain,
            self_model_mode=base.self_model_mode,
            self_model_learning_rate=base.self_model_learning_rate,
            observation_forecaster_learning_rate=(
                base.observation_forecaster_learning_rate
            ),
            feedback_mode=base.feedback_mode,
            feedback_minimum_gain=base.feedback_minimum_gain,
            feedback_maximum_gain=base.feedback_maximum_gain,
            feedback_adaptation_rate=base.feedback_adaptation_rate,
            feedback_maximum_step=base.feedback_maximum_step,
            feedback_deadband=base.feedback_deadband,
            causal_boundary_config=boundary,
            causal_boundary_broadcast_gain=base.causal_boundary_broadcast_gain,
            causal_access_readout_mode="direct_candidate",
            ablations=base.ablations,
        )

    def runtime_factory(agent, runtime_config):
        runtime = AutonomousDiagnosticUnifiedCausalLoop(
            agent,
            runtime_config,
        )
        holder.append(runtime)
        return runtime

    rows, _ = run_post_change_closure_trace(
        seed,
        experiment_config=config,
        runtime_factory=runtime_factory,
        agent_factory=agent_factory,
    )
    assert len(rows) == config.total_steps
    assert len(holder) == 1
    snapshot = holder[0].grounding_snapshot
    assert snapshot["uses_evaluator_labels"] is False
    assert snapshot["probe_count"] == 0
    assert holder[0]._agent.causal_boundary_snapshot()["access_readout"]["update_count"] == 0
