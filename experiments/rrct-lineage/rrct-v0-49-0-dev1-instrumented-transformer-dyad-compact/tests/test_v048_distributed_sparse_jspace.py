"""Focused tests for RRCT v0.48 distributed sparse J-space."""
from __future__ import annotations

from dataclasses import asdict, replace

import numpy as np

from rrct.distributed_shared_workspace import make_pair_message_receipt
from rrct.distributed_sparse_jspace import (
    validate_distributed_jspace_access_receipt,
    validate_distributed_jspace_chain,
)
from rrct.distributed_sparse_jspace_experiment import (
    _ablation_probe,
    _capacity_probe,
    _feedback_challenge,
    _interaction_states,
    _partner_swap_probe,
    _provenance_probe,
    _swap_probe,
    _train_dyad,
    run_distributed_sparse_jspace_benchmark,
)
from rrct.transformational_self_continuity import _digest


def test_two_local_jacobian_workspaces_form_one_sparse_shared_frame() -> None:
    trained = _train_dyad(48011)
    receipt = trained.jspace.discovery_receipt
    assert receipt.local_workspace_rank_a == 4
    assert receipt.local_workspace_rank_b == 4
    assert receipt.shared_rank == 4
    assert receipt.shared_frame_count == 8
    assert receipt.support_capacity == 4
    assert receipt.minimum_canonical_correlation > 0.99
    assert receipt.cross_agent_alignment_r2 > 0.99
    assert receipt.minimum_frame_alignment_cosine > 0.99
    assert receipt.support_exact_agreement_rate == 1.0
    assert receipt.dynamic_support_count == 16
    assert receipt.packet_certificates_valid


def test_full_shared_jspace_reports_reuses_and_controls_planning() -> None:
    trained = _train_dyad(48011)
    controller = trained.controller()
    rows = [
        __import__(
            "rrct.distributed_sparse_jspace_experiment",
            fromlist=["_evaluate_case"],
        )._evaluate_case(trained, controller, trial=trial, mode="full_shared")
        for trial in range(24)
    ]
    assert np.mean([row["task_correct"] for row in rows]) == 1.0
    assert np.mean([row["report_a_correct"] for row in rows]) == 1.0
    assert np.mean([row["report_b_correct"] for row in rows]) == 1.0
    assert np.mean([row["shared_support_correct"] for row in rows]) == 1.0
    assert np.mean([row["flexible_reuse_correct"] for row in rows]) == 1.0
    assert np.mean([row["distributed_jspace_closure"] for row in rows]) == 1.0


def test_message_only_cooperation_is_not_distributed_jspace() -> None:
    trained = _train_dyad(48011)
    controller = trained.controller()
    evaluate = __import__(
        "rrct.distributed_sparse_jspace_experiment",
        fromlist=["_evaluate_case"],
    )._evaluate_case
    rows = [
        evaluate(trained, controller, trial=trial, mode="message_only")
        for trial in range(20)
    ]
    assert np.mean([row["task_correct"] for row in rows]) == 1.0
    assert np.mean([row["bidirectional"] for row in rows]) == 0.0
    assert np.mean([row["joint_memory_write"] for row in rows]) == 0.0
    assert np.mean([row["distributed_jspace_closure"] for row in rows]) == 0.0


def test_shared_concept_swap_changes_both_reports_reasoning_and_plan() -> None:
    trained = _train_dyad(48012)
    rows = [_swap_probe(trained, trial) for trial in range(20)]
    assert np.mean([row["report_swap_a"] for row in rows]) == 1.0
    assert np.mean([row["report_swap_b"] for row in rows]) == 1.0
    assert np.mean([row["joint_plan_swap"] for row in rows]) == 1.0
    assert np.mean([row["flexible_reuse_swap"] for row in rows]) == 1.0
    assert np.mean([row["private_a_preserved"] for row in rows]) == 1.0
    assert np.mean([row["private_b_preserved"] for row in rows]) == 1.0


def test_jspace_ablation_is_selective_and_capacity_is_limited() -> None:
    trained = _train_dyad(48013)
    ablations = [_ablation_probe(trained, trial) for trial in range(24)]
    assert np.mean([row["intact_task"] for row in ablations]) == 1.0
    assert (
        np.mean([row["intact_task"] for row in ablations])
        - np.mean([row["ablated_task"] for row in ablations])
        >= 0.60
    )
    assert np.mean([row["private_a_preserved"] for row in ablations]) == 1.0
    assert np.mean([row["private_b_preserved"] for row in ablations]) == 1.0
    capacities = [_capacity_probe(trained, trial) for trial in range(24)]
    assert np.mean([row["capacity_respected"] for row in capacities]) == 1.0
    assert np.mean([row["selected_support_size"] for row in capacities]) == 4.0
    assert np.mean([row["union_support_size"] for row in capacities]) == 8.0
    assert np.mean([row["dual_union_recall"] for row in capacities]) == 0.5


def test_foreign_pair_content_is_quarantined_without_provenance_cut() -> None:
    trained = _train_dyad(48014)
    row = _provenance_probe(trained, 900)
    assert row["full_quarantined"] == 1.0
    assert row["full_false_write"] == 0.0
    assert row["full_planner_bound"] == 0.0
    assert row["provenance_cut_false_write"] == 1.0
    assert row["provenance_cut_planner_bound"] == 1.0


def test_pair_outcome_reopens_shared_jspace_on_next_interaction() -> None:
    trained = _train_dyad(48011)
    row = _feedback_challenge(trained, 950)
    assert row["full_shared_reopened"] == 1.0
    assert row["recurrence_cut_reopened"] == 0.0
    assert row["full_shared_second_rounds"] == 3
    assert row["recurrence_cut_second_rounds"] == 1
    assert row["full_shared_second_correct"] == 1.0
    assert row["recurrence_cut_second_correct"] == 0.0


def test_new_partner_needs_new_code_and_shared_frame_alignment() -> None:
    first = _train_dyad(48011)
    second = _train_dyad(48012)
    result = _partner_swap_probe(first, second, trials=48)
    assert result["unadapted_partner_accuracy"] <= 0.50
    assert result["remapped_partner_accuracy"] == 1.0
    assert result["remapped_alignment_r2"] > 0.99
    assert result["remapped_frame_cosine"] > 0.99
    assert result["remapped_support_agreement"] == 1.0


def test_rehashed_but_misbound_distributed_access_fails_chain() -> None:
    trained = _train_dyad(48013)
    world = trained.world
    controller = trained.controller()
    interaction = _interaction_states(
        trained, trial=7, rounds=1, mode="full_shared"
    )
    episode_id = "v048-chain-tamper"
    pair_lineage = controller.pair_lineage_digest
    message_a = make_pair_message_receipt(
        time=1,
        episode_id=episode_id,
        round_index=1,
        sender_lineage_digest=world.lineage_a_digest,
        receiver_lineage_digest=world.lineage_b_digest,
        pair_lineage_digest=pair_lineage,
        message=interaction["message_a"],
        communication_enabled=True,
        shuffled=False,
    )
    message_b = make_pair_message_receipt(
        time=1,
        episode_id=episode_id,
        round_index=1,
        sender_lineage_digest=world.lineage_b_digest,
        receiver_lineage_digest=world.lineage_a_digest,
        pair_lineage_digest=pair_lineage,
        message=interaction["message_b"],
        communication_enabled=True,
        shuffled=False,
    )
    joint, _, written_a, written_b = controller.integrate(
        time=2,
        episode_id=episode_id,
        mode="full_shared",
        state_a=interaction["state_a"],
        state_b=interaction["state_b"],
        message_a=interaction["message_a"],
        message_b=interaction["message_b"],
        message_a_receipt=message_a,
        message_b_receipt=message_b,
        origin_pair_lineage_digest=pair_lineage,
    )
    access_a = trained.workspace_a.access(
        time=3,
        case_id=episode_id + ":a",
        hidden=written_a,
        mode="full_closure",
    )
    access_b = trained.workspace_b.access(
        time=3,
        case_id=episode_id + ":b",
        hidden=written_b,
        mode="full_closure",
    )
    distributed = trained.jspace.access(
        time=3,
        episode_id=episode_id,
        pair_lineage_digest=pair_lineage,
        state_a=written_a,
        state_b=written_b,
        local_access_a=access_a,
        local_access_b=access_b,
        joint_workspace=joint,
    )
    plan = controller.plan(time=4, workspace=joint)
    outcome = controller.observe(
        time=5,
        plan=plan,
        actual_action=world.action_from_bits(interaction["bits"]),
    )
    assert validate_distributed_jspace_chain(
        discovery=trained.jspace.discovery_receipt,
        atlas_receipt=trained.jspace.atlas.discovery_receipt,
        local_access_a=access_a,
        local_access_b=access_b,
        message_a=message_a,
        message_b=message_b,
        joint_workspace=joint,
        distributed_access=distributed,
        plan=plan,
        outcome=outcome,
    )
    tampered = replace(distributed, joint_workspace_digest="0" * 64, digest="")
    payload = asdict(tampered)
    payload.pop("digest")
    tampered = replace(tampered, digest=_digest(payload))
    assert validate_distributed_jspace_access_receipt(tampered)
    assert not validate_distributed_jspace_chain(
        discovery=trained.jspace.discovery_receipt,
        atlas_receipt=trained.jspace.atlas.discovery_receipt,
        local_access_a=access_a,
        local_access_b=access_b,
        message_a=message_a,
        message_b=message_b,
        joint_workspace=joint,
        distributed_access=tampered,
        plan=plan,
        outcome=outcome,
    )


def test_small_matched_benchmark_meets_all_declared_endpoints() -> None:
    result = run_distributed_sparse_jspace_benchmark(
        (48011, 48017), trials_per_seed=16
    )
    assert result["all_endpoints_met"]
    assert all(result["endpoints"].values())
    assert result["mode_summaries"]["full_shared"]["task_accuracy"] == 1.0
    assert (
        result["mode_summaries"]["full_shared"][
            "distributed_jspace_closure_score"
        ]
        == 1.0
    )
    assert result["mode_summaries"]["message_only"]["task_accuracy"] == 1.0
    assert (
        result["mode_summaries"]["message_only"][
            "distributed_jspace_closure_score"
        ]
        == 0.0
    )
