from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from rrct.unified_causal_loop import _digest
from rrct.whole_loop_causal_closure import (
    WholeLoopActionCandidate,
    WholeLoopClosureConfig,
    make_causal_preview_receipt,
    validate_whole_loop_planning_receipt,
    validate_whole_loop_receipt_chain,
)
from rrct.whole_loop_causal_closure import _planning_payload
from rrct.whole_loop_causal_closure_experiment import (
    V043_COARSE_PAIRS,
    V043_REFINED_PAIRS,
    _candidate_material,
    _verify_holdout_freeze,
    _identity_pair,
    _learned_baseline,
    _new_controller,
    _preview_receipts,
    _public_certificate,
    run_feedback_reopening_challenge,
    run_whole_loop_closure_cohort,
    run_whole_loop_closure_seed,
)

TEST_IDENTITIES = (6101, 6107)


def _decision(mode: str, *, scenario: str = "copy_trap", trial: int = 0):
    config = WholeLoopClosureConfig()
    controller = _new_controller(TEST_IDENTITIES, config)
    seed = TEST_IDENTITIES[0]
    candidates, raw_candidates, effects = _candidate_material(seed, scenario, trial)
    baseline = _learned_baseline(seed)
    signature = (_identity_pair(seed), int(baseline.discovery.rank), 1)
    coarse, refined = _preview_receipts(
        seed=seed,
        scenario=scenario,
        trial=trial,
        time=100_000,
        target_signature=signature,
        candidates=candidates,
        effects=effects,
    )
    state = controller.begin_decision(
        time=100_000,
        target_signature=signature,
        candidates=candidates,
        coarse_preview=coarse,
        intervention_mode=mode,
    )
    return controller, state, coarse, refined, raw_candidates, effects


def test_intact_chain_binds_identity_boundary_plan_and_outcome() -> None:
    controller, state, _, refined, _, _ = _decision("intact")
    plan = controller.commit_decision(
        state,
        refined_preview=refined if state.refinement_requested else None,
    )
    outcome = controller.observe_outcome(
        state,
        plan,
        plan.predicted_selected_return + 0.10,
        reveal_time=100_001,
    )

    assert state.memory_source_key_matches_target
    assert state.boundary_attribution_available
    assert state.metacognition_available
    assert state.planner_binding_available
    assert plan.self_model_authorized
    assert plan.boundary_memory_digest == state.memory_digest
    assert plan.boundary_certificate_digest == state.boundary_certificate_digest
    assert outcome.outcome_update_applied
    assert outcome.provenance_safe_update
    assert outcome.memory_after_digest != outcome.memory_before_digest
    assert validate_whole_loop_receipt_chain(state, plan, outcome)


def test_rehashed_boundary_memory_substitution_fails_cross_receipt_chain() -> None:
    controller, state, _, refined, _, _ = _decision("intact")
    plan = controller.commit_decision(
        state,
        refined_preview=refined if state.refinement_requested else None,
    )
    substituted = replace(
        plan,
        boundary_memory_digest=_digest(
            {"schema": "rrct.v043.test.substituted_boundary_memory.v1"}
        ),
        digest="0" * 64,
    )
    substituted = replace(
        substituted,
        digest=_digest(_planning_payload(substituted)),
    )

    assert validate_whole_loop_planning_receipt(substituted)
    assert not validate_whole_loop_receipt_chain(state, substituted)


def test_memory_cut_requires_correct_fresh_boundary_and_preserves_temporal_binding() -> None:
    controller, state, _, refined, _, _ = _decision("memory_cut")
    assert not state.memory_available
    assert state.identity_id is not None
    assert state.temporal_commit_digest is not None
    assert state.temporal_authorization_digest is not None
    assert state.refinement_requested

    with pytest.raises(RuntimeError, match="fresh boundary rediscovery"):
        controller.commit_decision(state, refined_preview=refined)

    wrong = _public_certificate(6107, epoch=1, time=100_000)
    with pytest.raises(ValueError, match="different identity"):
        controller.commit_decision(
            state,
            refined_preview=refined,
            fresh_boundary_certificate=wrong,
        )

    correct = _public_certificate(6101, epoch=1, time=100_000)
    plan = controller.commit_decision(
        state,
        refined_preview=refined,
        fresh_boundary_certificate=correct,
    )
    assert plan.self_model_authorized
    assert plan.temporal_authorization_digest == state.temporal_authorization_digest
    assert plan.boundary_memory_digest is not None
    assert plan.boundary_certificate_digest == correct.digest
    assert validate_whole_loop_receipt_chain(state, plan)


def test_unrequested_refined_evidence_is_rejected() -> None:
    config = WholeLoopClosureConfig()
    controller = _new_controller(TEST_IDENTITIES, config)
    seed = TEST_IDENTITIES[0]
    baseline = _learned_baseline(seed)
    signature = (_identity_pair(seed), int(baseline.discovery.rank), 91_001)
    candidates = (
        WholeLoopActionCandidate("stable_route", 0.0, 0.0, 0.20),
        WholeLoopActionCandidate("decoy", 0.0, 0.0, 0.95),
    )
    effects = np.asarray(
        [
            np.asarray(baseline.sensory_map, dtype=np.float64),
            np.zeros_like(np.asarray(baseline.sensory_map, dtype=np.float64)),
        ]
    )
    coarse = make_causal_preview_receipt(
        time=910_000,
        target_signature=signature,
        candidate_keys=[candidate.key for candidate in candidates],
        effect_operators=effects,
        sample_count=V043_COARSE_PAIRS,
        refinement_level="coarse",
    )
    refined = make_causal_preview_receipt(
        time=910_000,
        target_signature=signature,
        candidate_keys=[candidate.key for candidate in candidates],
        effect_operators=effects,
        sample_count=V043_REFINED_PAIRS,
        refinement_level="refined",
    )
    state = controller.begin_decision(
        time=910_000,
        target_signature=signature,
        candidates=candidates,
        coarse_preview=coarse,
        intervention_mode="intact",
    )
    assert not state.refinement_requested
    with pytest.raises(ValueError, match="unrequested future evidence"):
        controller.commit_decision(state, refined_preview=refined)


def test_feedback_write_causally_reopens_next_information_request() -> None:
    result = run_feedback_reopening_challenge(
        6101,
        identity_seeds=TEST_IDENTITIES,
    )
    assert result["all_checks_pass"]
    assert result["second_decision"]["intact"]["refinement_requested"]
    assert not result["second_decision"]["feedback_cut"][
        "refinement_requested"
    ]
    assert (
        result["second_decision"]["intact"]["samples_per_candidate"]
        == V043_REFINED_PAIRS
    )
    assert (
        result["second_decision"]["feedback_cut"]["samples_per_candidate"]
        == V043_COARSE_PAIRS
    )


def test_provenance_cut_cannot_relabel_wrong_source_update() -> None:
    result = run_whole_loop_closure_seed(
        6101,
        identity_seeds=TEST_IDENTITIES,
        modes=("provenance_cut",),
        trials_per_scenario=1,
    )
    rows = result["rows"]
    assert rows
    assert all(not row["memory_source_key_matches_target"] for row in rows)
    assert all(row["outcome_update_applied"] for row in rows)
    assert all(not row["provenance_safe_update"] for row in rows)
    assert all(row["receipt_chain_valid"] for row in rows)


def test_joint_cut_is_not_mislabeled_as_self_model_authorized() -> None:
    result = run_whole_loop_closure_seed(
        6101,
        identity_seeds=TEST_IDENTITIES,
        modes=("joint_cut",),
        trials_per_scenario=1,
    )
    rows = result["rows"]
    assert rows
    assert all(row["planner_mode"] == "snapshot_control" for row in rows)
    assert all(not row["self_model_authorized"] for row in rows)
    assert all(row["boundary_memory_digest"] is None for row in rows)
    assert all(row["boundary_certificate_digest"] is None for row in rows)
    assert all(not row["outcome_update_applied"] for row in rows)


def test_small_matched_cohort_meets_frozen_functional_endpoints() -> None:
    result = run_whole_loop_closure_cohort(
        TEST_IDENTITIES,
        cohort="test",
        trials_per_scenario=2,
    )
    assert result["all_frozen_endpoints_met"]
    assert result["mode_summaries"]["intact"]["accuracy"] == 1.0
    assert result["mode_summaries"]["memory_cut"]["accuracy"] == 1.0
    assert (
        result["mode_summaries"]["intact"]["mean_samples_per_candidate"]
        < result["mode_summaries"]["memory_cut"][
            "mean_samples_per_candidate"
        ]
    )
    assert (
        result["mode_summaries"]["intact"]["accuracy"]
        > result["mode_summaries"]["joint_cut"]["accuracy"]
    )


def test_preoutcome_freeze_verifies_when_present() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    manifest = root / "validation/V0_43_PREOUTCOME_FREEZE.json"
    if not manifest.is_file():
        pytest.skip("pre-outcome freeze has not yet been created")
    digest = _verify_holdout_freeze()
    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)
