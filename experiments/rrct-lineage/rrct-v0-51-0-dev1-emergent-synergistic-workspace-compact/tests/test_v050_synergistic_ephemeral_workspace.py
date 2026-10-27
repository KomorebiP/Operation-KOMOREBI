"""Focused tests for RRCT v0.50 synergistic ephemeral workspace."""
from __future__ import annotations

import pytest

from rrct.synergistic_ephemeral_workspace import (
    analyze_synergistic_seed,
    all_sequence_rows,
    state_dict_sha256,
    synergy_receipt,
    train_operator_agent,
)


@pytest.fixture(scope="module")
def development_analysis() -> dict:
    return analyze_synergistic_seed(50001)


def test_agents_are_separately_trained_on_complementary_operators() -> None:
    agent_a, receipt_a = train_operator_agent("A", 100003)
    agent_b, receipt_b = train_operator_agent("B", 100004)
    assert receipt_a.transition_accuracy == 1.0
    assert receipt_b.transition_accuracy == 1.0
    assert receipt_a.private_accuracy == 1.0
    assert receipt_b.private_accuracy == 1.0
    assert state_dict_sha256(agent_a) != state_dict_sha256(agent_b)


def test_training_is_seed_deterministic() -> None:
    first, first_receipt = train_operator_agent("A", 50017)
    second, second_receipt = train_operator_agent("A", 50017)
    assert first_receipt.steps == second_receipt.steps
    assert state_dict_sha256(first) == state_dict_sha256(second)


def test_task_has_exact_four_bit_synergy() -> None:
    receipt = synergy_receipt(all_sequence_rows())
    assert receipt.target_entropy_bits == 4.0
    assert receipt.information_from_a_history_bits == 0.0
    assert receipt.information_from_b_history_bits == 0.0
    assert receipt.information_from_joint_history_bits == 4.0
    assert receipt.synergy_lower_bound_bits == 4.0
    assert receipt.bayes_accuracy_a_history == 1.0 / 16.0
    assert receipt.bayes_accuracy_b_history == 1.0 / 16.0
    assert receipt.bayes_accuracy_joint_history == 1.0


def test_persistent_joint_state_is_necessary_under_frozen_controls(
    development_analysis: dict,
) -> None:
    modes = development_analysis["modes"]
    assert modes["full_workspace"]["task_accuracy"] == 1.0
    assert modes["recurrent_message_workspace"]["task_accuracy"] == 1.0
    assert development_analysis["max_nonpersistent_control_accuracy"] <= 0.18
    assert modes["reset_each_update"]["task_accuracy"] == 1.0 / 16.0
    assert modes["reset_each_round"]["task_accuracy"] == 1.0 / 16.0
    assert modes["one_way_a"]["task_accuracy"] == 1.0 / 16.0
    assert modes["one_way_b"]["task_accuracy"] == 1.0 / 16.0


def test_workspace_and_message_state_are_functionally_equivalent(
    development_analysis: dict,
) -> None:
    modes = development_analysis["modes"]
    assert modes["full_workspace"]["task_accuracy"] == modes[
        "recurrent_message_workspace"
    ]["task_accuracy"]
    assert modes["full_workspace"]["physically_centralized"] is True
    assert modes["recurrent_message_workspace"]["physically_centralized"] is False
    assert modes["recurrent_message_workspace"]["persistent_joint_state"] is True
    assert modes["message_log_oracle"]["task_accuracy"] == 1.0


def test_workspace_is_causally_writable_and_bilateral(
    development_analysis: dict,
) -> None:
    patch = development_analysis["causal_patch"]
    assert patch == {
        "patch_target_accuracy": 1.0,
        "patch_changes_final_plan_rate": 1.0,
        "agent_a_report_accuracy": 1.0,
        "agent_b_report_accuracy": 1.0,
    }
    assert development_analysis["active_workspace_reports"] == {
        "agent_a_accuracy": 1.0,
        "agent_b_accuracy": 1.0,
    }


def test_workspace_dissolves_without_copying_answer_to_private_memory(
    development_analysis: dict,
) -> None:
    post = development_analysis["post_dissolution"]
    assert post["workspace_state_retained"] is False
    assert post["pair_memory_retained"] is False
    assert post["agent_a_post_erase_accuracy"] == 1.0 / 16.0
    assert post["agent_b_post_erase_accuracy"] == 1.0 / 16.0
    assert development_analysis["private_routine_accuracy"] == {
        "agent_a": 1.0,
        "agent_b": 1.0,
    }


def test_development_seed_meets_all_frozen_endpoints(
    development_analysis: dict,
) -> None:
    assert development_analysis["all_endpoints_met"]
    assert len(development_analysis["endpoints"]) == 23
    assert all(development_analysis["endpoints"].values())
    assert development_analysis["valence_model_present"] is False
    assert development_analysis["survival_reward"] == 0.0
    assert development_analysis["identity_reward"] == 0.0
