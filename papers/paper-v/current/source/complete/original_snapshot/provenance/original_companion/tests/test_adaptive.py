from __future__ import annotations

import numpy as np

from projector_signal.adaptive import (
    all_haar_packet_nodes,
    best_pruning,
    enumerate_prunings,
    is_complete_pruning,
    optimum_gap,
    packet_tree_costs,
    perturbation_envelope,
    pruning_cost,
    stable_by_gap,
    synthesize_pruning,
)


def test_pruning_counts() -> None:
    assert [len(enumerate_prunings(depth)) for depth in range(5)] == [1, 2, 5, 26, 677]


def test_every_enumerated_pruning_is_complete() -> None:
    for pruning in enumerate_prunings(4):
        assert is_complete_pruning(pruning, 4)


def test_mixed_depth_pruning_synthesizes_exactly() -> None:
    rng = np.random.default_rng(20260729)
    x = rng.normal(size=64)
    nodes = all_haar_packet_nodes(x, 4)
    pruning = ("00", "01", "1")
    assert is_complete_pruning(pruning, 4)
    rebuilt = synthesize_pruning(nodes, pruning, 4)
    assert np.max(np.abs(rebuilt - x)) < 2e-14


def test_dynamic_programming_matches_brute_force() -> None:
    rng = np.random.default_rng(8)
    depth = 4
    costs = {}
    for level in range(depth + 1):
        for number in range(2**level):
            path = format(number, f"0{level}b") if level else ""
            costs[path] = float(rng.uniform(0.05, 2.0))
    result = best_pruning(costs, depth)
    brute = min(enumerate_prunings(depth), key=lambda pruning: pruning_cost(pruning, costs))
    assert abs(result.cost - pruning_cost(brute, costs)) < 1e-14
    assert abs(result.cost - min(pruning_cost(p, costs) for p in enumerate_prunings(depth))) < 1e-14


def test_gap_stability_certificate() -> None:
    depth = 3
    costs = {}
    for level in range(depth + 1):
        for number in range(2**level):
            path = format(number, f"0{level}b") if level else ""
            costs[path] = 10.0 if level < depth else 0.1 + 0.01 * number
    base = best_pruning(costs, depth)
    gap = optimum_gap(costs, depth)
    local_bound = {path: 0.01 for path in costs}
    envelope = perturbation_envelope(local_bound, depth)
    assert stable_by_gap(gap, envelope)

    rng = np.random.default_rng(9)
    perturbed = {path: value + rng.uniform(-0.01, 0.01) for path, value in costs.items()}
    after = best_pruning(perturbed, depth)
    assert after.nodes == base.nodes


def test_signal_derived_costs_return_exact_basis() -> None:
    t = np.linspace(0.0, 1.0, 128, endpoint=False)
    x = np.sin(2 * np.pi * 5 * t) + 0.8 * ((t > 0.37) & (t < 0.62))
    nodes = all_haar_packet_nodes(x, 5)
    costs = packet_tree_costs(nodes, 5, complexity_per_node=0.015)
    result = best_pruning(costs, 5)
    assert is_complete_pruning(result.nodes, 5)
    rebuilt = synthesize_pruning(nodes, result.nodes, 5)
    assert np.max(np.abs(rebuilt - x)) < 4e-14
