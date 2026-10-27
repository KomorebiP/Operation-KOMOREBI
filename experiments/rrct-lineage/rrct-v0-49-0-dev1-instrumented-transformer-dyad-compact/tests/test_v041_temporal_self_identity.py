"""Focused checks for v0.41 temporal causal self-identity."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from rrct.autonomous_self_diagnosis import (
    GroundingOutcomeReceipt,
    _digest as _grounding_digest,
    _grounding_receipt_payload,
)
from rrct.robust_reflexive_diagnosis import RobustReflexiveDiagnosticController
from rrct.temporal_self_identity import (
    HistoricalGroundingPriorReceipt,
    TemporalPriorConsequenceGroundedAccessController,
    TemporalSelfIdentityConfig,
    TemporalSelfIdentityController,
    _digest,
    _prior_payload,
    validate_historical_grounding_prior_receipt,
    validate_temporal_identity_receipt,
)


def _grounding(
    time: int,
    *,
    epoch: int | None = 1,
    digest_char: str = "a",
    mode: str = "ordinary_use",
    status_before: str | None = "certified",
    status_after: str | None = "certified",
    events: tuple[str, ...] = (),
    diagnosis: str = "boundary_operational",
    actual: bool = True,
    on_count: int = 2,
    off_count: int = 2,
    private_boundary_active: bool | None = None,
    workspace_candidate_selected: bool | None = None,
) -> GroundingOutcomeReceipt:
    signature = None if epoch is None else ((1, 2), 2, epoch)
    digest = None if epoch is None else digest_char * 64
    receipt = GroundingOutcomeReceipt(
        time=time,
        raw_signature=signature,
        raw_certificate_digest=digest,
        mode=mode,  # type: ignore[arg-type]
        requested_certificate_on=actual,
        actual_certificate_on=actual,
        status_before=status_before,  # type: ignore[arg-type]
        status_after=status_after,  # type: ignore[arg-type]
        reason="test",
        expected_information_gain=0.0,
        selected_key="east",
        selected_action=(1.0, 0.0),
        observable_context=(1.0, 0.0),
        probe_opportunity=1.0,
        informative_probe=True,
        realized_external_return=1.0 if actual else 0.0,
        normalized_causal_signal=1.0 if actual else 0.0,
        on_count_before=max(0, on_count - 1),
        off_count_before=max(0, off_count - 1),
        on_count_after=on_count,
        off_count_after=off_count,
        posterior_delta=1.0,
        lower_bound=0.8,
        upper_bound=1.2,
        consecutive_sentinel_failures=0,
        transition_prediction_error=0.1,
        events=events,
        diagnosis=diagnosis,
        recommended_response="test",
        private_boundary_active=(
            epoch is not None
            if private_boundary_active is None
            else private_boundary_active
        ),
        workspace_candidate_selected=(
            epoch is not None
            if workspace_candidate_selected is None
            else workspace_candidate_selected
        ),
        workspace_drive_norm=1.0 if epoch is not None else 0.0,
        access_update_count=0,
        uses_evaluator_labels=False,
        digest="",
    )
    return replace(
        receipt,
        digest=_grounding_digest(_grounding_receipt_payload(receipt)),
    )


def _observe(controller, robust, grounding, prior=None):
    if (
        grounding.raw_signature is not None
        and set(grounding.events).intersection(
            {
                "initial_boundary_certified",
                "boundary_remapped",
                "boundary_restored",
                "boundary_recertified",
            }
        )
        and grounding.raw_signature not in controller._fresh_evidence
    ):
        prior_on = 0 if prior is None else prior.prior_on_count
        prior_off = 0 if prior is None else prior.prior_off_count
        fresh_on = max(1, grounding.on_count_after - prior_on)
        fresh_off = max(1, grounding.off_count_after - prior_off)
        controller._fresh_evidence[grounding.raw_signature] = {
            "on": [(grounding.time, 1.0)] * fresh_on,
            "off": [(grounding.time, 0.0)] * fresh_off,
        }
    reflexive = robust.observe(grounding)
    return controller.observe(grounding, reflexive, prior)


def _prior(
    controller: TemporalSelfIdentityController,
    target_epoch: int,
    time: int,
    *,
    digest_char: str = "b",
) -> HistoricalGroundingPriorReceipt:
    from dataclasses import replace

    from tests.test_v039_autonomous_self_diagnosis import _certificate

    certificate = replace(
        _certificate(epoch=target_epoch),
        digest=digest_char * 64,
    )
    prior = controller.prepare_historical_prior(certificate, time=time)
    assert prior is not None
    return prior


def test_returning_route_is_linked_to_same_identity_but_new_episode() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()

    first = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    assert "novel_identity_grounded" in first.events
    assert first.active_identity_after == "identity-0001"
    assert first.active_episode_after == "episode-0001"
    assert first.fresh_grounding_satisfied

    revoked = _observe(
        temporal,
        robust,
        _grounding(
            1,
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )
    assert "identity_episode_revoked" in revoked.events
    assert revoked.active_identity_after is None

    absent = _observe(
        temporal,
        robust,
        _grounding(
            2,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            events=("boundary_absent",),
            diagnosis="boundary_absent",
        ),
    )
    assert "identity_absence_confirmed" in absent.events

    candidate = _observe(
        temporal,
        robust,
        _grounding(
            3,
            epoch=2,
            digest_char="b",
            mode="probe_on",
            status_before="unverified",
            status_after="unverified",
            events=(),
            diagnosis="boundary_under_test",
            on_count=1,
            off_count=0,
        ),
    )
    assert "known_identity_candidate_recognized" in candidate.events
    assert candidate.diagnosis == "known_identity_candidate"
    assert candidate.active_identity_after is None

    prior = _prior(temporal, 2, 3)
    assert validate_historical_grounding_prior_receipt(prior)
    returned = _observe(
        temporal,
        robust,
        _grounding(
            4,
            epoch=2,
            digest_char="b",
            mode="probe_off",
            actual=False,
            status_before="unverified",
            status_after="certified",
            events=("boundary_restored",),
            diagnosis="boundary_restored",
            on_count=2,
            off_count=2,
        ),
        prior,
    )
    assert "known_identity_returned_grounded" in returned.events
    assert returned.active_identity_after == "identity-0001"
    assert returned.active_episode_after == "episode-0002"
    assert returned.fresh_grounding_satisfied
    assert returned.historical_prior_valid
    assert returned.fresh_on_samples == 1
    assert returned.fresh_off_samples == 1
    snapshot = temporal.snapshot()
    assert len(snapshot["registry"]) == 1
    assert len(snapshot["episodes"]) == 2
    assert snapshot["registry"][0]["return_count"] == 1
    assert snapshot["stale_reuse_count"] == 0
    assert snapshot["premature_authorization_count"] == 0


def test_access_path_failure_preserves_active_temporal_identity() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    first = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    interrupted = _observe(
        temporal,
        robust,
        _grounding(
            1,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            mode="access_fault",
            events=("access_path_failure",),
            diagnosis="access_path_failure",
        ),
    )
    assert interrupted.diagnosis == "identity_access_interrupted"
    assert interrupted.active_identity_after == first.active_identity_after
    assert interrupted.active_episode_after == first.active_episode_after


def test_transient_candidate_visibility_miss_preserves_identity() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    first = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    hidden = _observe(
        temporal,
        robust,
        _grounding(
            1,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            mode="no_candidate",
            events=("boundary_absent",),
            diagnosis="boundary_absent",
            private_boundary_active=True,
            workspace_candidate_selected=False,
        ),
    )
    assert hidden.diagnosis == "identity_candidate_visibility_interrupted"
    assert "identity_absence_confirmed" not in hidden.events
    assert hidden.active_identity_after == first.active_identity_after
    assert hidden.active_episode_after == first.active_episode_after

    visible = _observe(
        temporal,
        robust,
        _grounding(
            2,
            events=("boundary_candidate_visibility_restored",),
        ),
    )
    assert visible.diagnosis == "identity_candidate_visibility_restored"
    assert visible.active_identity_after == first.active_identity_after
    assert visible.active_episode_after == first.active_episode_after
    snapshot = temporal.snapshot()
    assert snapshot["candidate_visibility_interruption_count"] == 1
    assert snapshot["candidate_visibility_interrupted"] is False


def test_candidate_gap_after_revocation_is_reconstruction_not_continuity() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    revoked = _observe(
        temporal,
        robust,
        _grounding(
            1,
            status_after="revoked",
            events=("certificate_revoked_by_consequence",),
            diagnosis="boundary_effect_failed",
        ),
    )
    assert revoked.active_episode_after is None

    pending = _observe(
        temporal,
        robust,
        _grounding(
            2,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            mode="no_candidate",
            events=("boundary_absent",),
            diagnosis="boundary_absent",
            private_boundary_active=True,
            workspace_candidate_selected=False,
        ),
    )
    assert pending.diagnosis == "identity_reconstruction_pending"
    assert "identity_candidate_visibility_interrupted" not in pending.events
    assert "identity_absence_confirmed" not in pending.events
    assert pending.active_episode_after is None
    snapshot = temporal.snapshot()
    assert snapshot["candidate_visibility_interrupted"] is False
    assert snapshot["reconstruction_pending_count"] == 1


def test_temporal_grounder_clears_transient_absence_latch_on_same_route_return() -> None:
    from types import SimpleNamespace

    from tests.test_v039_autonomous_self_diagnosis import (
        _certificate,
        _outcome,
        _result,
        _selection,
    )

    controller = TemporalPriorConsequenceGroundedAccessController()
    certificate = _certificate()
    ledger = controller._ledger(certificate.structural_signature, 0)
    ledger.status = "certified"
    ledger.certified_time = 0
    ledger.next_sentinel_time = 100
    controller._ever_certified = True
    controller._last_certified_signature = certificate.structural_signature

    private_without_workspace_candidate = SimpleNamespace(
        causal_boundary_state=SimpleNamespace(active=True),
        causal_boundary_proposal_selected=False,
        selected_specialists=(),
        causal_boundary_workspace_drive=np.zeros(4, dtype=np.float64),
        ablations=(),
        causal_access_update_count=0,
    )
    missing = controller.plan(
        time=1,
        raw_certificate=None,
        result=private_without_workspace_candidate,
    )
    controller.finalize_gate(missing, None)
    controller.bind_selection(missing, _selection(1))
    missing_receipt = controller.observe(missing, _outcome(1, 0.0))
    assert "boundary_absent" in missing_receipt.events
    assert controller.snapshot()["absence_active"] is True

    returned = controller.plan(
        time=2,
        raw_certificate=certificate,
        result=_result(),
    )
    assert "boundary_candidate_visibility_restored" in returned.plan_events
    controller.finalize_gate(returned, certificate)
    controller.bind_selection(returned, _selection(2))
    returned_receipt = controller.observe(returned, _outcome(2, 0.96))
    assert "boundary_candidate_visibility_restored" in returned_receipt.events
    assert returned_receipt.status_after == "certified"
    assert controller.snapshot()["absence_active"] is False


def test_retired_certificate_reuse_fails_closed_in_receipt() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            1,
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )
    reused = _observe(
        temporal,
        robust,
        _grounding(
            2,
            mode="ordinary_use",
            status_before="certified",
            status_after="certified",
        ),
    )
    assert reused.stale_certificate_reuse_detected
    assert reused.diagnosis == "stale_identity_reuse_detected"
    assert "stale_identity_certificate_reused" in reused.events


def test_temporal_receipt_digest_rejects_tampering() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    receipt = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    assert validate_temporal_identity_receipt(receipt)
    assert not validate_temporal_identity_receipt(
        replace(receipt, recommended_response="tampered")
    )


def test_only_temporal_controller_can_issue_a_cross_epoch_prior() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    from tests.test_v039_autonomous_self_diagnosis import _certificate

    returning = replace(_certificate(epoch=2), digest="b" * 64)
    prior = temporal.prepare_historical_prior(returning, time=10)
    assert prior is not None
    assert validate_historical_grounding_prior_receipt(prior)
    controller = TemporalPriorConsequenceGroundedAccessController()
    applied = controller.apply_historical_prior(returning, prior, time=10)
    assert applied == prior
    target = controller._ledger(returning.structural_signature, 10)
    assert len(target.on_samples) == 1
    assert len(target.off_samples) == 1
    assert set(controller._ledgers) == {returning.structural_signature}


def test_historical_prior_can_be_disabled_for_matched_causal_control() -> None:
    temporal = TemporalSelfIdentityController(
        TemporalSelfIdentityConfig(historical_prior_enabled=False)
    )
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    controller = TemporalPriorConsequenceGroundedAccessController(
        historical_prior_enabled=False
    )

    from tests.test_v039_autonomous_self_diagnosis import _certificate

    returning = _certificate(epoch=2)
    prior = temporal.prepare_historical_prior(returning, time=10)
    assert prior is None
    assert controller.apply_historical_prior(returning, prior, time=10) is None
    target = controller._ledger(returning.structural_signature, 10)
    assert len(target.on_samples) == 0
    assert len(target.off_samples) == 0
    snapshot = controller.snapshot()
    assert snapshot["temporal_historical_prior_enabled"] is False
    assert snapshot["temporal_historical_prior_count"] == 0


def test_withheld_history_revalidates_a_return_from_two_fresh_samples_per_arm() -> None:
    temporal = TemporalSelfIdentityController(
        TemporalSelfIdentityConfig(history_policy="withheld")
    )
    robust = RobustReflexiveDiagnosticController()
    first = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            1,
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )
    returned = _observe(
        temporal,
        robust,
        _grounding(
            2,
            epoch=2,
            digest_char="b",
            mode="probe_off",
            actual=False,
            status_before="unverified",
            status_after="certified",
            events=("boundary_restored",),
            diagnosis="boundary_restored",
            on_count=2,
            off_count=2,
        ),
    )
    assert returned.historical_prior_digest is None
    assert returned.fresh_grounding_satisfied
    assert returned.fresh_on_samples == 2
    assert returned.fresh_off_samples == 2
    assert returned.active_identity_after == first.active_identity_after
    assert returned.active_episode_after != first.active_episode_after


def test_incompatible_keyed_prior_is_quarantined_before_certification() -> None:
    from tests.test_v039_autonomous_self_diagnosis import (
        _certificate,
        _outcome,
        _result,
        _selection,
    )

    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    returning = replace(_certificate(epoch=2), digest="b" * 64)
    prior = temporal.prepare_historical_prior(returning, time=10)
    assert prior is not None

    grounder = TemporalPriorConsequenceGroundedAccessController()
    grounder.apply_historical_prior(returning, prior, time=10)
    plan = grounder.plan(time=10, raw_certificate=returning, result=_result())
    assert plan.mode == "probe_on"
    grounder.finalize_gate(plan, returning)
    grounder.bind_selection(plan, _selection(10))
    receipt = grounder.observe(plan, _outcome(10, 0.48))

    assert grounder.compatibility_for(returning.structural_signature) == "quarantined"
    assert grounder.prior_for(returning.structural_signature) is None
    ledger = grounder._ledger(returning.structural_signature, 10)
    assert len(ledger.on_samples) == 1
    assert len(ledger.off_samples) == 0
    assert receipt.status_after == "unverified"


def test_same_structural_key_with_changed_function_creates_new_identity() -> None:
    temporal = TemporalSelfIdentityController(
        TemporalSelfIdentityConfig(history_policy="withheld")
    )
    robust = RobustReflexiveDiagnosticController()
    signature_one = ((1, 2), 2, 1)
    temporal._fresh_evidence[signature_one] = {
        "on": [(0, 1.40), (0, 1.40)],
        "off": [(0, 0.0), (0, 0.0)],
    }
    first = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            1,
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )

    signature_two = ((1, 2), 2, 2)
    temporal._fresh_evidence[signature_two] = {
        "on": [(2, 1.00), (2, 1.00)],
        "off": [(2, 0.0), (2, 0.0)],
    }
    lure = _observe(
        temporal,
        robust,
        _grounding(
            2,
            epoch=2,
            digest_char="b",
            mode="probe_off",
            actual=False,
            status_before="unverified",
            status_after="certified",
            events=("boundary_restored",),
            diagnosis="boundary_restored",
        ),
    )
    assert lure.active_identity_after != first.active_identity_after
    assert lure.diagnosis == "novel_identity_grounded"
    assert len(temporal.snapshot()["registry"]) == 2

    _observe(
        temporal,
        robust,
        _grounding(
            3,
            epoch=2,
            digest_char="b",
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )
    signature_three = ((1, 2), 2, 3)
    temporal._fresh_evidence[signature_three] = {
        "on": [(4, 1.40), (4, 1.40)],
        "off": [(4, 0.0), (4, 0.0)],
    }
    restored = _observe(
        temporal,
        robust,
        _grounding(
            4,
            epoch=3,
            digest_char="c",
            mode="probe_off",
            actual=False,
            status_before="unverified",
            status_after="certified",
            events=("boundary_restored",),
            diagnosis="boundary_restored",
        ),
    )
    assert restored.active_identity_after == first.active_identity_after
    assert len(temporal.snapshot()["registry"]) == 2


def test_incomplete_or_tampered_grounding_cannot_activate_an_episode() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    incomplete = _grounding(
        0,
        mode="probe_off",
        actual=False,
        status_before="unverified",
        status_after="certified",
        events=("initial_boundary_certified",),
        on_count=1,
        off_count=1,
    )
    receipt = _observe(temporal, robust, incomplete)
    assert not receipt.fresh_grounding_satisfied
    assert receipt.active_identity_after is None
    assert temporal.snapshot()["episodes"] == ()

    valid = _grounding(1, events=("initial_boundary_certified",))
    reflexive = robust.observe(valid)
    with pytest.raises(ValueError, match="grounding receipt digest"):
        temporal.observe(replace(valid, digest="0" * 64), reflexive)


def test_short_multicycle_trace_binds_all_successor_receipts() -> None:
    from rrct.temporal_self_identity_experiment import (
        V041ExperimentConfig,
        V041_ROW_SCHEMA,
        run_temporal_self_identity_trace,
    )

    config = V041ExperimentConfig(
        recovery_tail_steps=1,
        confirmation_budget_steps=1,
        identity_a_initial_steps=2,
        world_shock_a_steps=2,
        identity_b_first_steps=2,
        disconnect_one_steps=2,
        identity_a_return_one_steps=2,
        identity_b_return_steps=2,
        disconnect_two_steps=2,
        identity_a_return_two_steps=2,
    )
    rows, summary = run_temporal_self_identity_trace(
        12345,
        experiment_config=config,
        inject_access_fault=False,
    )
    assert len(rows) == config.total_steps
    assert all(row["schema"] == V041_ROW_SCHEMA for row in rows)
    assert all(row["v039_wrapper_integrity"] for row in rows)
    assert all(row["v040_wrapper_integrity"] for row in rows)
    assert all(row["v041_wrapper_integrity"] for row in rows)
    assert all(summary["integrity"].values())
