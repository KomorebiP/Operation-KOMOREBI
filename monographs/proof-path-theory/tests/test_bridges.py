from __future__ import annotations

from itertools import combinations

from proof_path_theory import (
    BridgeGraph,
    exact_cardinality_retention,
    greedy_cardinality_retention,
    greedy_cost_retention,
    is_monotone_submodular_coverage,
)


def graph() -> BridgeGraph:
    return BridgeGraph(
        nodes=("A", "x", "y", "z", "t1", "t2", "t3"),
        edges=(
            ("A", "x"),
            ("A", "y"),
            ("x", "t1"),
            ("x", "t2"),
            ("y", "t2"),
            ("z", "t3"),
        ),
    )


def test_bridge_criticality_is_weighted_dominator_loss() -> None:
    g = graph()
    weights = {"t1": 2.0, "t2": 1.0, "t3": 5.0}
    assert g.bridge_criticality(("x",), "x", weights) == 3.0
    assert g.dominated_targets(("x",), "x", weights) == frozenset({"x", "t1", "t2"}).intersection(weights)


def test_coverage_utility_is_monotone_submodular() -> None:
    g = graph()
    assert is_monotone_submodular_coverage(
        g,
        ("x", "y", "z"),
        {"t1": 2.0, "t2": 1.0, "t3": 5.0},
    )


def test_greedy_cardinality_matches_exact_on_example() -> None:
    g = graph()
    weights = {"t1": 2.0, "t2": 1.0, "t3": 5.0}
    greedy = greedy_cardinality_retention(g, ("x", "y", "z"), weights, budget=2)
    exact = exact_cardinality_retention(g, ("x", "y", "z"), weights, budget=2)
    assert greedy.utility == exact.utility == 8.0
    assert "z" in greedy.retained


def test_greedy_cost_respects_budget() -> None:
    g = graph()
    result = greedy_cost_retention(
        g,
        ("x", "y", "z"),
        {"t1": 2.0, "t2": 1.0, "t3": 5.0},
        {"x": 2.0, "y": 1.0, "z": 4.0},
        budget=4.0,
    )
    assert result.spent <= 4.0
    assert result.utility >= 3.0


def test_reachability_with_blocked_node() -> None:
    g = graph()
    assert "t1" in g.reachable(("x",))
    assert "t1" not in g.reachable(("x",), blocked=("x",))
