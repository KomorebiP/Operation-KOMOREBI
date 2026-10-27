from __future__ import annotations

from pathlib import Path

from proof_path_theory import (
    GoalWeights,
    Representation,
    RepresentationProfile,
    TaskRequirement,
    compression_debt,
    compression_report,
    load_proof_field,
    pareto_front,
    recoverability_equivalent,
    recoverability_preorder,
    representation_utility,
    select_representation,
    task_signature,
    unique_and_dag_certificate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_task_recoverability_preorder_and_equivalence() -> None:
    tasks = (
        TaskRequirement("verify", frozenset({"A", "B"})),
        TaskRequirement("teach", frozenset({"E"})),
        TaskRequirement("discover", frozenset({"F"})),
    )
    short = Representation("short", frozenset({"A", "B"}))
    rich = Representation("rich", frozenset({"A", "B", "E", "F"}))
    duplicate = Representation("duplicate", frozenset({"A", "B"}))
    assert recoverability_preorder(short, rich, tasks)
    assert not recoverability_preorder(rich, short, tasks)
    assert recoverability_equivalent(short, duplicate, tasks)
    assert task_signature(rich, tasks) == frozenset({"verify", "teach", "discover"})


def test_compression_report_separates_losses() -> None:
    field = load_proof_field(ROOT / "examples" / "and_dag.json")
    certificate = unique_and_dag_certificate(field)
    representation = Representation(
        "certificate",
        certificate.node_ids,
        certificate=certificate,
    )
    tasks = (
        TaskRequirement("verify", certificate.node_ids, probability=0.5),
        TaskRequirement("teach", frozenset({"E"}), probability=0.2),
        TaskRequirement("extend", frozenset({"F", "C"}), probability=0.3),
    )
    report = compression_report(field, representation, tasks=tasks)
    assert report.verification_complete
    assert report.loss_values.discovery > 0
    assert report.loss_values.bridge > 0
    assert report.expected_recovery_debt > 0
    assert report.sufficient_tasks == frozenset({"verify"})


def test_compression_debt_is_monotone_under_retention() -> None:
    tasks = (
        TaskRequirement("t1", frozenset({"x"}), probability=0.4),
        TaskRequirement("t2", frozenset({"y", "z"}), probability=0.6),
    )
    costs = {"x": 1.0, "y": 2.0, "z": 3.0}
    sparse = compression_debt(set(), tasks, costs)
    richer = compression_debt({"x", "y"}, tasks, costs)
    assert richer < sparse


def test_goal_dependent_selection() -> None:
    formal = RepresentationProfile("formal", 1.0, 0.2, 0.3, 1.0, 0.2, 0.05, 0.3)
    archive = RepresentationProfile("archive", 0.7, 1.0, 0.8, 0.5, 1.0, 0.3, 1.0)
    certificate_goal = GoalWeights(verification=0.7, auditability=0.3, cost=0.2)
    discovery_goal = GoalWeights(discovery=0.5, bridge=0.5, cost=0.05)
    assert select_representation((formal, archive), certificate_goal).name == "formal"
    assert select_representation((formal, archive), discovery_goal).name == "archive"
    assert representation_utility(formal, certificate_goal) > representation_utility(archive, certificate_goal)


def test_pareto_front_removes_dominated_profile() -> None:
    strong = RepresentationProfile("strong", 0.9, 0.9, 0.9, 0.9, 0.9, 0.1, 0.5)
    weak = RepresentationProfile("weak", 0.7, 0.7, 0.7, 0.7, 0.7, 0.2, 0.7)
    cheap = RepresentationProfile("cheap", 0.6, 0.6, 0.6, 0.6, 0.6, 0.05, 0.2)
    assert {profile.name for profile in pareto_front((strong, weak, cheap))} == {"strong", "cheap"}


def test_pure_retention_projections_form_intersection_algebra() -> None:
    from proof_path_theory import retention_join, retention_meet, retention_projection

    universe = {"A", "B", "C", "D"}
    left = {"A", "B", "C"}
    right = {"B", "C", "D"}
    once = retention_projection(universe, left)
    twice = retention_projection(once, left)
    composed = retention_projection(retention_projection(universe, left), right)
    reversed_composed = retention_projection(
        retention_projection(universe, right), left
    )
    assert once == twice
    assert composed == reversed_composed == retention_meet(left, right)
    assert retention_join(left, right) == frozenset(universe)
