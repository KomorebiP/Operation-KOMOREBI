"""Regression checks for the v0.41 temporal-identity action path."""
from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

from rrct.autonomous_self_diagnosis import ConsequenceGroundingConfig
from rrct.autonomous_self_diagnosis_experiment import _agent_v039
from rrct.robust_reflexive_diagnosis import RobustReflexiveDiagnosticController
from rrct.temporal_self_identity import (
    TemporalPriorConsequenceGroundedAccessController,
    TemporalSelfIdentityController,
    TemporalSelfIdentityUnifiedCausalLoop,
)
from rrct.unified_causal_loop_experiment import _boundary_config, _runtime_config
from tests.test_v039_autonomous_self_diagnosis import (
    _certificate,
    _outcome,
    _result,
    _selection,
)
from tests.test_v041_temporal_self_identity import _grounding, _observe


def _runtime(seed: int = 41_041) -> TemporalSelfIdentityUnifiedCausalLoop:
    agent = _agent_v039(_boundary_config(seed), seed)
    return TemporalSelfIdentityUnifiedCausalLoop(
        agent,
        replace(
            _runtime_config(seed),
            quarantine_public_certificate_on_drift=True,
        ),
    )


def test_same_signature_accepts_new_per_row_certificate_digest() -> None:
    """Workspace/time receipts may change without changing the active epoch."""

    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    grounded = _observe(
        temporal,
        robust,
        _grounding(
            0,
            digest_char="a",
            events=("initial_boundary_certified",),
        ),
    )
    signature = grounded.raw_signature
    assert signature is not None

    authorization_b = temporal.ordinary_action_authorization_digest(
        signature,
        "b" * 64,
    )
    authorization_c = temporal.ordinary_action_authorization_digest(
        signature,
        "c" * 64,
    )

    assert authorization_b is not None
    assert authorization_c is not None
    assert authorization_b != authorization_c


def test_retired_epoch_reuse_is_detected_with_new_full_certificate_digest() -> None:
    """Retirement follows the stable epoch binding, not one row's receipt hash."""

    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(
            0,
            digest_char="a",
            events=("initial_boundary_certified",),
        ),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            1,
            digest_char="b",
            status_after="revoked",
            events=("certificate_revoked_by_consequence",),
            diagnosis="boundary_effect_failed",
        ),
    )

    reused = _observe(
        temporal,
        robust,
        _grounding(
            2,
            digest_char="c",
            mode="ordinary_use",
            status_before="certified",
            status_after="certified",
        ),
    )

    assert reused.raw_certificate_digest == "c" * 64
    assert reused.stale_certificate_reuse_detected
    assert reused.diagnosis == "stale_identity_reuse_detected"


def test_grounder_minima_cannot_undercut_temporal_freshness() -> None:
    """Prevent certify/deny/reset oscillation from incompatible thresholds."""

    seed = 41_042
    agent = _agent_v039(_boundary_config(seed), seed)
    grounding = ConsequenceGroundingConfig(
        minimum_on_samples=1,
        minimum_off_samples=1,
    )

    with pytest.raises(ValueError, match="grounder ON minimum"):
        TemporalSelfIdentityUnifiedCausalLoop(
            agent,
            _runtime_config(seed),
            grounding_config=grounding,
        )


def test_final_public_gate_clears_temporal_action_authorization() -> None:
    """A temporal grant is not a final authorization after a drift veto."""

    runtime = _runtime()
    certificate = _certificate()
    plan = runtime.grounding.plan(
        time=1,
        raw_certificate=certificate,
        result=_result(),
    )
    runtime._current_grounding_plan = plan
    runtime._current_temporal_action_authorization_digest = "f" * 64
    drift = SimpleNamespace(
        reopen_requested=True,
        digest="d" * 64,
        pair=certificate.pair,
        rank=certificate.rank,
    )

    effective, receipt = runtime._gate_public_certificate(
        time=1,
        raw_certificate=certificate,
        drift=drift,
    )

    assert effective is None
    assert receipt.event == "entered"
    assert plan.actual_certificate_on is False
    assert runtime._current_temporal_action_authorization_digest is None


def test_snapshot_digest_commits_future_causal_evidence_state() -> None:
    temporal = TemporalSelfIdentityController()
    signature = ((1, 2), 2, 1)
    before = temporal.snapshot()["digest"]
    temporal._fresh_evidence[signature] = {
        "on": [(1, 1.0)],
        "off": [(2, 0.0)],
    }
    after = temporal.snapshot()["digest"]
    assert after != before


def test_duplicate_grounding_for_active_epoch_does_not_open_second_episode() -> None:
    temporal = TemporalSelfIdentityController()
    robust = RobustReflexiveDiagnosticController()
    first = _observe(
        temporal,
        robust,
        _grounding(0, events=("initial_boundary_certified",)),
    )
    duplicate = _observe(
        temporal,
        robust,
        _grounding(1, events=("boundary_recertified",)),
    )
    assert "duplicate_active_epoch_grounding_ignored" in duplicate.events
    assert duplicate.active_episode_after == first.active_episode_after
    assert len(temporal.snapshot()["episodes"]) == 1


def test_true_private_absence_is_not_relabelled_as_visibility_restoration() -> None:
    grounder = TemporalPriorConsequenceGroundedAccessController()
    certificate = _certificate()
    ledger = grounder._ledger(certificate.structural_signature, 0)
    ledger.status = "certified"
    ledger.certified_time = 0
    ledger.next_sentinel_time = 100
    grounder._ever_certified = True
    grounder._last_certified_signature = certificate.structural_signature

    missing = grounder.plan(
        time=1,
        raw_certificate=None,
        result=_result(active=False, public=False),
    )
    grounder.finalize_gate(missing, None)
    grounder.bind_selection(missing, _selection(1))
    grounder.observe(missing, _outcome(1, 0.0))

    returned = grounder.plan(
        time=2,
        raw_certificate=certificate,
        result=_result(),
    )
    assert "boundary_candidate_visibility_restored" not in returned.plan_events
