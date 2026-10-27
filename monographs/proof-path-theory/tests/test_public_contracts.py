from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from proof_path_theory import (
    BridgeGraph,
    Certificate,
    Representation,
    TaskRequirement,
    append_only_derivability_preserved,
    audit_priority,
    certificate_cost,
    compression_debt,
    compression_report,
    constant_rate_regime,
    equicorrelated_covariance,
    generalized_least_squares_weights,
    greedy_cardinality_retention,
    greedy_cost_retention,
    load_proof_field,
    minimum_certificate,
    optimal_depth,
    stopping_depth,
    unique_and_dag_certificate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_empty_cost_mapping_is_honored() -> None:
    field = load_proof_field(ROOT / "examples" / "alternative_proofs.json")
    certificate = minimum_certificate(field, node_cost={})
    assert certificate_cost(field, certificate, node_cost={}) == 0.0


def test_nonfinite_certificate_cost_is_rejected() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    certificate = unique_and_dag_certificate(field)
    with pytest.raises(ValueError, match="finite and nonnegative"):
        certificate_cost(field, certificate, node_cost={"A": float("nan")})
    with pytest.raises(ValueError, match="finite and nonnegative"):
        minimum_certificate(field, node_cost={"A": float("inf")})


def test_task_probabilities_must_form_distribution_for_debt() -> None:
    tasks = (
        TaskRequirement("a", frozenset({"x"}), probability=0.4),
        TaskRequirement("b", frozenset({"y"}), probability=0.4),
    )
    with pytest.raises(ValueError, match="sum to 1"):
        compression_debt(set(), tasks, {"x": 1.0, "y": 1.0})


def test_empty_recovery_cost_mapping_is_honored() -> None:
    tasks = (TaskRequirement("a", frozenset({"x"}), probability=1.0),)
    assert compression_debt(set(), tasks, {}) == 0.0


def test_duplicate_task_ids_are_rejected_in_debt_model() -> None:
    tasks = (
        TaskRequirement("same", frozenset({"x"}), probability=0.5),
        TaskRequirement("same", frozenset({"y"}), probability=0.5),
    )
    with pytest.raises(ValueError, match="identifiers must be unique"):
        compression_debt(set(), tasks, {"x": 1.0, "y": 1.0})


def test_compression_report_rejects_unknown_task_nodes() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    certificate = unique_and_dag_certificate(field)
    representation = Representation(
        "certificate", certificate.node_ids, certificate=certificate
    )
    tasks = (TaskRequirement("unknown", frozenset({"not-a-node"})),)
    with pytest.raises(KeyError):
        compression_report(field, representation, tasks=tasks)


def test_bridge_selection_validates_candidates_even_with_zero_budget() -> None:
    graph = BridgeGraph({"a", "t"}, {("a", "t")})
    with pytest.raises(KeyError):
        greedy_cardinality_retention(
            graph, ["missing"], {"t": 1.0}, budget=0
        )


def test_bridge_candidate_and_mandatory_sets_must_be_disjoint() -> None:
    graph = BridgeGraph({"a", "t"}, {("a", "t")})
    with pytest.raises(ValueError, match="disjoint"):
        greedy_cardinality_retention(
            graph, ["a"], {"t": 1.0}, budget=1, mandatory={"a"}
        )


def test_bridge_budget_and_costs_must_be_finite() -> None:
    graph = BridgeGraph({"a", "t"}, {("a", "t")})
    with pytest.raises(ValueError, match="budget must be finite"):
        greedy_cost_retention(
            graph, ["a"], {"t": 1.0}, {"a": 1.0}, budget=float("nan")
        )
    with pytest.raises(ValueError, match="costs must be finite"):
        greedy_cost_retention(
            graph, ["a"], {"t": 1.0}, {"a": float("inf")}, budget=1.0
        )


def test_review_contract_rejects_nonfinite_inputs() -> None:
    with pytest.raises(ValueError, match="correlation must be finite"):
        equicorrelated_covariance(3, correlation=float("nan"))
    with pytest.raises(ValueError, match="covariance must be nonempty"):
        generalized_least_squares_weights(np.empty((0, 0)))


def test_audit_contract_rejects_nonfinite_inputs() -> None:
    with pytest.raises(ValueError, match="rates must be finite"):
        constant_rate_regime(float("nan"), 1.0)
    with pytest.raises(ValueError, match="priority inputs must be finite"):
        audit_priority(
            error_probability=0.2,
            consequence=float("inf"),
            dependency_reach=1.0,
            audit_cost=1.0,
        )


def test_refinement_contract_requires_nested_monotone_sequences() -> None:
    with pytest.raises(ValueError, match="residuals must be nonincreasing"):
        optimal_depth(
            [1.0, 1.2], [0.0, 1.0], residual_weight=1.0, cost_weight=1.0
        )
    with pytest.raises(ValueError, match="costs must be nondecreasing"):
        stopping_depth(
            [1.0, 0.5],
            [1.0, 0.0],
            residual_tolerance=0.1,
            marginal_gain_floor=0.01,
        )


def test_append_only_check_rejects_unknown_requested_target() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    with pytest.raises(KeyError):
        append_only_derivability_preserved(field, field, targets={"missing"})


def test_public_schema_identifiers_are_stable_urns() -> None:
    from proof_path_theory import bundled_schema

    assert bundled_schema("proof-field")["$id"] == (
        "urn:komorebi:proof-path-theory:schema:proof-field:1.0"
    )
    assert bundled_schema("certificate")["$id"] == (
        "urn:komorebi:proof-path-theory:schema:certificate:1.0"
    )
