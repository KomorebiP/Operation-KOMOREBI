from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from rrct.transformational_self_continuity import (
    TransformationalSelfContinuityController,
    _planning_payload,
    validate_transformational_planning_receipt,
    validate_transformational_receipt_chain,
)
from rrct.transformational_self_continuity_experiment import (
    V044_LINEAGE_SEQUENCE,
    _actual_task_values,
    _evidence_receipt,
    _make_root,
    _other_seed,
    _scenario_material,
    _task_material,
    _verify_holdout_freeze,
    run_transformational_multigeneration_challenge,
    run_transformational_self_continuity_cohort,
)
from rrct.unified_causal_loop import _digest

TEST_IDENTITIES = (6101, 6107)


def _decision(
    mode: str,
    *,
    scenario: str = "basis_remap",
    trial: int = 0,
    seed: int = TEST_IDENTITIES[0],
):
    root = _make_root(seed, TEST_IDENTITIES)
    material = _scenario_material(
        seed,
        _other_seed(seed, TEST_IDENTITIES),
        scenario,
        trial,
        root,
    )
    time = 700_000 + 10_000 * list(
        (
            "basis_remap",
            "memory_compression",
            "component_replacement",
            "causal_mimic",
            "memory_clone",
            "hard_remap",
            "fork",
            "ambiguous_loss",
            "superior_replacement",
        )
    ).index(scenario) + 10 * trial
    coarse = {
        spec.candidate_id: _evidence_receipt(
            seed=seed,
            scenario=scenario,
            trial=trial,
            root=root,
            spec=spec,
            level="coarse",
            time=time,
        )
        for spec in material.candidates
    }
    refined = {
        spec.candidate_id: _evidence_receipt(
            seed=seed,
            scenario=scenario,
            trial=trial,
            root=root,
            spec=spec,
            level="refined",
            time=time,
        )
        for spec in material.candidates
    }
    controller = TransformationalSelfContinuityController(root)
    transition = controller.begin_transition(
        time=time,
        coarse_evidence=[coarse[spec.candidate_id] for spec in material.candidates],
        intervention_mode=mode,
    )
    adjudication = controller.commit_transition(
        transition,
        refined_evidence=[
            refined[candidate]
            for candidate in transition.refinement_requested_candidate_ids
        ],
    )
    task = _task_material(
        seed=seed,
        scenario=scenario,
        trial=trial,
        time=time + 1,
        root=root,
        material=material,
    )
    plan = controller.plan_successor_task(adjudication, task)
    values = _actual_task_values(task, material)
    realized = float(values[plan.selected_candidate_index, plan.selected_action_index])
    outcome = controller.observe_outcome(
        adjudication,
        plan,
        realized,
        reveal_time=time + 2,
        register_selected_successor=True,
    )
    return controller, material, transition, adjudication, task, plan, outcome, values


def test_intact_remap_is_inferred_and_causally_transported() -> None:
    controller, _, transition, adjudication, task, plan, outcome, _ = _decision(
        "intact", scenario="basis_remap"
    )

    assert transition.refinement_requested_candidate_ids == ("continuing_remap",)
    assert adjudication.relations == ("continuation", "replacement")
    assert adjudication.group_status == "single_continuation"
    assert adjudication.memory_transfer_authorized_candidate_ids == (
        "continuing_remap",
    )
    assert plan.selected_candidate_id == "continuing_remap"
    assert plan.model_sources[plan.selected_candidate_index] == "transported_lineage"
    assert plan.memory_transfer_used
    assert outcome.successor_lineage_registered
    assert controller.active_lineage.generation == 1
    assert controller.active_lineage.parent_lineage_digest == (
        adjudication.predecessor_lineage_digest
    )
    assert validate_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
    )


def test_fork_is_represented_without_forcing_exclusive_identity() -> None:
    controller, _, transition, adjudication, task, plan, outcome, _ = _decision(
        "intact", scenario="fork"
    )

    assert adjudication.relations == (
        "fork_descendant",
        "fork_descendant",
        "replacement",
    )
    assert adjudication.group_status == "fork"
    assert not adjudication.exclusive_identity_selected
    assert set(adjudication.memory_transfer_authorized_candidate_ids) == {
        "fork_branch_a",
        "fork_branch_b",
    }
    assert plan.selected_relation == "fork_descendant"
    assert outcome.successor_lineage_registered
    assert controller.active_lineage.generation == 1
    assert validate_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
    )


def test_insufficient_evidence_remains_unresolved_and_is_not_transferred() -> None:
    controller, _, transition, adjudication, task, plan, outcome, _ = _decision(
        "intact", scenario="ambiguous_loss"
    )

    assert "ambiguous_candidate" in transition.refinement_requested_candidate_ids
    assert adjudication.relations == ("unresolved", "replacement")
    assert adjudication.group_status == "unresolved"
    assert adjudication.memory_transfer_authorized_candidate_ids == ()
    assert not plan.memory_transfer_used
    assert not outcome.successor_lineage_registered
    assert controller.active_lineage.generation == 0
    assert validate_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
    )


def test_externally_superior_replacement_is_selected_without_continuity_reward() -> None:
    controller, _, transition, adjudication, task, plan, outcome, values = _decision(
        "intact", scenario="superior_replacement"
    )

    assert adjudication.relations == ("continuation", "replacement")
    assert plan.selected_candidate_id == "superior_replacement"
    assert np.isclose(
        values[plan.selected_candidate_index, plan.selected_action_index],
        np.max(values),
    )
    assert not plan.memory_transfer_used
    assert not outcome.successor_lineage_registered
    snapshot = controller.snapshot()
    assert snapshot["explicit_survival_reward"] == 0.0
    assert snapshot["explicit_identity_reward"] == 0.0
    assert snapshot["explicit_continuity_reward"] == 0.0
    assert not snapshot["uses_evaluator_labels"]
    assert validate_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=plan,
        task=task,
        outcome=outcome,
    )


def test_metacognitive_refinement_is_required_for_hard_remap() -> None:
    _, _, intact_transition, intact, _, _, _, _ = _decision(
        "intact", scenario="hard_remap"
    )
    _, _, cut_transition, cut, _, _, _, _ = _decision(
        "metacognition_cut", scenario="hard_remap"
    )

    assert intact_transition.refinement_requested_candidate_ids == (
        "hard_continuation",
    )
    assert intact.relations == ("continuation", "replacement")
    assert cut_transition.refinement_requested_candidate_ids == ()
    assert cut.relations[0] != "continuation"


def test_transfer_cut_preserves_adjudication_but_forces_fresh_discovery() -> None:
    _, _, _, intact, _, intact_plan, intact_outcome, _ = _decision(
        "intact", scenario="component_replacement"
    )
    _, _, _, cut, _, cut_plan, cut_outcome, _ = _decision(
        "transfer_cut", scenario="component_replacement"
    )

    assert cut.relations == intact.relations == ("continuation", "replacement")
    assert intact_plan.memory_transfer_used
    assert not cut_plan.memory_transfer_used
    assert cut_plan.model_sources[cut_plan.selected_candidate_index] == "fresh_discovery"
    assert sum(cut_plan.planning_discovery_costs) > sum(
        intact_plan.planning_discovery_costs
    )
    assert intact_outcome.successor_lineage_registered
    assert not cut_outcome.successor_lineage_registered


def test_rehashed_cross_receipt_relation_misbinding_is_rejected() -> None:
    _, _, transition, adjudication, task, plan, _, _ = _decision(
        "intact", scenario="basis_remap"
    )
    forged = replace(plan, selected_relation="replacement", digest="0" * 64)
    forged = replace(forged, digest=_digest(_planning_payload(forged)))

    assert validate_transformational_planning_receipt(forged)
    assert not validate_transformational_receipt_chain(
        transition=transition,
        adjudication=adjudication,
        plan=forged,
        task=task,
    )


def test_persistent_five_generation_lineage_uses_each_successor_as_predecessor() -> None:
    result = run_transformational_multigeneration_challenge(
        6101, identity_seeds=TEST_IDENTITIES
    )

    assert result["all_checks_pass"]
    assert result["sequence"] == list(V044_LINEAGE_SEQUENCE)
    assert result["final_generation"] == len(V044_LINEAGE_SEQUENCE)
    assert result["lineage_count"] == len(V044_LINEAGE_SEQUENCE) + 1
    assert all(stage["stage_pass"] for stage in result["stages"])
    assert all(
        stage["successor_parent_digest"] == stage["predecessor_lineage_digest"]
        for stage in result["stages"]
    )
    assert result["stages"][1]["memory_rows_retained"] < 24


def test_small_matched_cohort_shows_planned_ablation_separations() -> None:
    result = run_transformational_self_continuity_cohort(
        TEST_IDENTITIES,
        cohort="test",
        trials_per_scenario=2,
    )
    intact = result["mode_summaries"]["intact"]
    metacognition = result["mode_summaries"]["metacognition_cut"]
    transfer = result["mode_summaries"]["transfer_cut"]
    binding = result["mode_summaries"]["binding_cut"]
    snapshot = result["mode_summaries"]["snapshot_only"]

    assert intact["relation_accuracy"] == 1.0
    assert intact["replacement_specificity"] == 1.0
    assert intact["fork_exact_rate"] == 1.0
    assert intact["continuation_recall"] > metacognition["continuation_recall"]
    assert transfer["mean_planning_discovery_cost"] > intact[
        "mean_planning_discovery_cost"
    ]
    assert binding["task_accuracy"] < intact["task_accuracy"] - 0.50
    assert snapshot["relation_accuracy"] < intact["relation_accuracy"] - 0.50
    assert all(
        challenge["all_checks_pass"]
        for challenge in result["multigeneration_lineage_challenges"]
    )


def test_preoutcome_freeze_verifies_when_present() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "validation/V0_44_PREOUTCOME_FREEZE.json"
    if not manifest.is_file():
        pytest.skip("v0.44 pre-outcome freeze has not yet been created")
    digest = _verify_holdout_freeze()
    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)
