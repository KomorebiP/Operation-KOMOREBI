"""Focused checks for RRCT v0.47 distributed shared workspace."""
from __future__ import annotations

from dataclasses import asdict, replace

import numpy as np

from rrct.distributed_shared_workspace import (
    make_pair_message_receipt,
    validate_distributed_workspace_chain,
    validate_joint_planning_receipt,
)
from rrct.distributed_shared_workspace_experiment import (
    _discovery_metrics,
    _evaluate_case,
    _feedback_challenge,
    _interaction_states,
    _partner_swap_probe,
    _patch_probe,
    _provenance_probe,
    _train_dyad,
    run_distributed_shared_workspace_benchmark,
)
from rrct.transformational_self_continuity import _digest


def test_shared_manifold_is_recovered_without_private_leakage() -> None:
    trained = _train_dyad(47011)
    metrics = _discovery_metrics(trained)
    assert metrics["shared_rank"] == trained.world.config.expected_shared_rank
    assert metrics["minimum_canonical_correlation"] > 0.99
    assert metrics["cross_agent_alignment_r2"] > 0.99
    assert metrics["projector_overlap_a"] > 0.99
    assert metrics["projector_overlap_b"] > 0.99
    assert metrics["private_leakage_accuracy_a"] <= 0.30
    assert metrics["private_leakage_accuracy_b"] <= 0.30
    assert metrics["all_packet_certificates_valid"]


def test_full_shared_workspace_solves_joint_task_that_agents_cannot_solve_alone() -> None:
    trained = _train_dyad(47011)
    controller = trained.controller()
    rows = [
        _evaluate_case(trained, controller, trial=trial, mode="full_shared")
        for trial in range(18)
    ]
    assert np.mean([row["task_correct"] for row in rows]) == 1.0
    assert np.mean([row["individual_a_correct"] for row in rows]) <= 0.45
    assert np.mean([row["individual_b_correct"] for row in rows]) <= 0.45
    assert np.mean([row["functional_shared_closure"] for row in rows]) == 1.0


def test_message_success_is_not_counted_as_distributed_closure() -> None:
    trained = _train_dyad(47011)
    controller = trained.controller()
    rows = [
        _evaluate_case(trained, controller, trial=trial, mode="message_only")
        for trial in range(18)
    ]
    assert np.mean([row["task_correct"] for row in rows]) == 1.0
    assert np.mean([row["message_only_route"] for row in rows]) == 1.0
    assert np.mean([row["memory_write"] for row in rows]) == 0.0
    assert np.mean([row["bidirectional"] for row in rows]) == 0.0
    assert np.mean([row["functional_shared_closure"] for row in rows]) == 0.0


def test_shared_packet_ablation_spares_private_routines() -> None:
    trained = _train_dyad(47012)
    controller = trained.controller()
    rows = [
        _evaluate_case(trained, controller, trial=trial, mode="workspace_cut")
        for trial in range(18)
    ]
    assert np.mean([row["task_correct"] for row in rows]) == 0.0
    assert np.mean([row["routine_a_correct"] for row in rows]) == 1.0
    assert np.mean([row["routine_b_correct"] for row in rows]) == 1.0


def test_joint_patch_redirects_plan_and_is_bidirectionally_causal() -> None:
    trained = _train_dyad(47013)
    rows = [_patch_probe(trained, trial) for trial in range(12)]
    assert np.mean([row["joint_patch_success"] for row in rows]) == 1.0
    assert np.mean([row["agent_a_private_preserved"] for row in rows]) == 1.0
    assert np.mean([row["agent_b_private_preserved"] for row in rows]) == 1.0
    assert np.mean([row["a_to_b_causal_effect_ratio"] for row in rows]) > 0.45
    assert np.mean([row["b_to_a_causal_effect_ratio"] for row in rows]) > 0.45


def test_wrong_pair_memory_is_quarantined_and_provenance_cut_accepts_it() -> None:
    trained = _train_dyad(47014)
    row = _provenance_probe(trained, 900)
    assert row["full_quarantined"] == 1.0
    assert row["full_false_write"] == 0.0
    assert row["full_planner_bound"] == 0.0
    assert row["provenance_cut_false_write"] == 1.0
    assert row["provenance_cut_planner_bound"] == 1.0


def test_feedback_reopens_interaction_and_improves_next_decision() -> None:
    trained = _train_dyad(47011)
    row = _feedback_challenge(trained, 950)
    assert row["full_shared_reopened"] == 1.0
    assert row["recurrence_cut_reopened"] == 0.0
    assert row["full_shared_second_rounds"] == 3
    assert row["recurrence_cut_second_rounds"] == 1
    assert row["full_shared_second_correct"] == 1.0
    assert row["recurrence_cut_second_correct"] == 0.0


def test_pair_specific_code_fails_partner_swap_but_new_shared_map_recovers() -> None:
    first = _train_dyad(47011)
    second = _train_dyad(47012)
    result = _partner_swap_probe(first, second, trials=36)
    assert result["pair_private_message_swap_accuracy"] <= 0.45
    assert result["unadapted_atlas_swap_accuracy"] <= 0.50
    assert result["remapped_shared_atlas_accuracy"] == 1.0
    assert result["remapped_alignment_r2"] > 0.99


def test_rehashed_but_misbound_plan_fails_complete_chain() -> None:
    trained = _train_dyad(47013)
    controller = trained.controller()
    episode = _interaction_states(
        trained, trial=7, rounds=1, mode="full_shared"
    )
    episode_id = "chain-tamper"
    message_a = make_pair_message_receipt(
        time=1,
        episode_id=episode_id,
        round_index=0,
        sender_lineage_digest=trained.world.agent_a.lineage_digest,
        receiver_lineage_digest=trained.world.agent_b.lineage_digest,
        pair_lineage_digest=controller.pair_lineage_digest,
        message=episode["message_a"],
        communication_enabled=True,
        shuffled=False,
    )
    message_b = make_pair_message_receipt(
        time=1,
        episode_id=episode_id,
        round_index=0,
        sender_lineage_digest=trained.world.agent_b.lineage_digest,
        receiver_lineage_digest=trained.world.agent_a.lineage_digest,
        pair_lineage_digest=controller.pair_lineage_digest,
        message=episode["message_b"],
        communication_enabled=True,
        shuffled=False,
    )
    workspace, _, _, _ = controller.integrate(
        time=2,
        episode_id=episode_id,
        mode="full_shared",
        state_a=episode["state_a"],
        state_b=episode["state_b"],
        message_a=episode["message_a"],
        message_b=episode["message_b"],
        message_a_receipt=message_a,
        message_b_receipt=message_b,
        origin_pair_lineage_digest=controller.pair_lineage_digest,
    )
    plan = controller.plan(time=3, workspace=workspace)
    outcome = controller.observe(
        time=4, plan=plan, actual_action=episode["actual_action"]
    )
    assert validate_distributed_workspace_chain(
        trained.atlas.discovery_receipt,
        message_a,
        message_b,
        workspace,
        plan,
        outcome,
    )
    tampered = replace(plan, joint_workspace_digest="0" * 64, digest="")
    payload = asdict(tampered)
    payload.pop("digest")
    tampered = replace(tampered, digest=_digest(payload))
    assert validate_joint_planning_receipt(tampered)
    assert not validate_distributed_workspace_chain(
        trained.atlas.discovery_receipt,
        message_a,
        message_b,
        workspace,
        tampered,
        outcome,
    )


def test_small_matched_benchmark_meets_declared_endpoints() -> None:
    result = run_distributed_shared_workspace_benchmark(
        (47011, 47012), trials_per_mode=12
    )
    assert result["all_endpoints_met"]
    assert all(result["endpoints"].values())
    assert result["mode_summaries"]["full_shared"]["task_accuracy"] == 1.0
    assert result["mode_summaries"]["message_only"]["task_accuracy"] == 1.0
    assert (
        result["mode_summaries"]["message_only"][
            "functional_shared_closure_score"
        ]
        == 0.0
    )
