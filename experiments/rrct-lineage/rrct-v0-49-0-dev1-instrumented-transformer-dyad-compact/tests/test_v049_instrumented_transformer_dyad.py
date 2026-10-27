"""Focused tests for the RRCT v0.49 trained-transformer pilot."""
from __future__ import annotations

import pytest

from rrct.instrumented_transformer_dyad import (
    TransformerDyadConfig,
    analyze_transformer_seed,
    evaluate_frozen_endpoints,
    output_accuracies,
    state_dict_sha256,
    train_transformer_dyad,
)


@pytest.fixture(scope="module")
def development_analysis() -> dict:
    return analyze_transformer_seed(49001)


def test_two_separately_parameterized_transformers_learn_all_tasks() -> None:
    model, _ = train_transformer_dyad(49001)
    accuracies = output_accuracies(model)
    assert min(accuracies.values()) == 1.0
    assert not any(
        left.data_ptr() == right.data_ptr()
        for left, right in zip(model.agent_a.parameters(), model.agent_b.parameters())
    )


def test_training_is_seed_deterministic() -> None:
    first, first_step = train_transformer_dyad(49013)
    second, second_step = train_transformer_dyad(49013)
    assert first_step == second_step
    assert state_dict_sha256(first) == state_dict_sha256(second)


def test_early_average_jacobian_is_ranked_but_not_a_workspace(
    development_analysis: dict,
) -> None:
    early = development_analysis["stage_metrics"]["h1"]
    assert early["rank_a"] == early["rank_b"] == 4
    assert early["alignment_r2"] <= 0.35
    assert early["ablation_shared_mean"] >= 0.90


def test_late_shared_access_state_is_aligned_causal_and_private_selective(
    development_analysis: dict,
) -> None:
    late_stage = development_analysis["stage_metrics"]["h3"]
    late = development_analysis["late_workspace"]
    assert late_stage["alignment_r2"] >= 0.95
    assert late_stage["jscore_a"] == {"factor_a": 1.0, "factor_b": 1.0}
    assert late_stage["jscore_b"] == {"factor_a": 1.0, "factor_b": 1.0}
    assert late["direct_ablation_shared_mean"] <= 0.45
    assert late["direct_ablation_private_mean"] >= 0.95
    assert min(late["patch_both_a"].values()) >= 0.95
    assert min(late["patch_both_b"].values()) >= 0.95


def test_late_state_transmits_between_agents_but_is_corrected_on_return(
    development_analysis: dict,
) -> None:
    late = development_analysis["late_workspace"]
    assert late["a_only_to_b_round1"]["a"] >= 0.75
    assert late["a_only_to_b_round1"]["joint"] >= 0.75
    assert late["b_only_to_a_round1"]["b"] >= 0.75
    assert late["b_only_to_a_round1"]["joint"] >= 0.75
    assert late["a_only_back_to_a_round2"]["a"] <= 0.25
    assert late["b_only_back_to_b_round2"]["b"] <= 0.25


def test_jacobian_specificity_is_not_established(
    development_analysis: dict,
) -> None:
    late = development_analysis["late_workspace"]
    for agent in ("a", "b"):
        j_probe = late[f"j_probes_{agent}"]
        pca_probe = late[f"pca_probes_{agent}"]
        assert min(j_probe[key] for key in ("a", "b", "joint", "f1", "f2")) >= 0.95
        assert min(pca_probe[key] for key in ("a", "b", "joint", "f1", "f2")) >= 0.95
    assert late["random_probes_a"]["private"] >= 0.65
    assert late["random_probes_b"]["private"] >= 0.65


def test_development_seed_meets_all_frozen_pilot_endpoints(
    development_analysis: dict,
) -> None:
    endpoints = evaluate_frozen_endpoints(development_analysis)
    assert len(endpoints) == 23
    assert all(endpoints.values())
    assert development_analysis["valence_model_present"] is False
    assert development_analysis["survival_reward"] == 0.0
    assert development_analysis["identity_reward"] == 0.0
