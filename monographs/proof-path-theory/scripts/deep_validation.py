from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path
import random

import numpy as np

from proof_path_theory import (
    __version__, BridgeGraph,
    Certificate,
    ClaimNode,
    Justification,
    NodeKind,
    ProofField,
    certificate_cost,
    effective_reviewer_count,
    equicorrelated_covariance,
    equicorrelated_effective_count,
    exact_cardinality_retention,
    greedy_cardinality_retention,
    minimum_certificate,
    retention_join,
    retention_meet,
    retention_projection,
    validate_certificate,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "deep_validation.json"


def _certificate_field() -> ProofField:
    node_ids = ("A", "X", "Y", "Z", "U", "V", "T1", "T2")
    nodes = [
        ClaimNode(
            node_id,
            node_id,
            NodeKind.PREMISE if node_id == "A" else NodeKind.CLAIM,
        )
        for node_id in node_ids
    ]
    justifications = [
        Justification("jx", ("A",), "X", "rule"),
        Justification("jy", ("A",), "Y", "rule"),
        Justification("jz-x", ("X",), "Z", "rule"),
        Justification("jz-y", ("Y",), "Z", "rule"),
        Justification("ju-x", ("X",), "U", "rule"),
        Justification("ju-z", ("Z",), "U", "rule"),
        Justification("jv-y", ("Y",), "V", "rule"),
        Justification("jv-z", ("Z",), "V", "rule"),
        Justification("jt1-u", ("U",), "T1", "rule"),
        Justification("jt1-z", ("Z",), "T1", "rule"),
        Justification("jt2-v", ("V",), "T2", "rule"),
        Justification("jt2-z", ("Z",), "T2", "rule"),
    ]
    return ProofField(
        nodes,
        justifications,
        premises=("A",),
        targets=("T1", "T2"),
    )


def _brute_minimum_cost(
    field: ProofField,
    node_cost: dict[str, float],
    justification_cost: dict[str, float],
) -> float:
    justification_ids = tuple(sorted(field.justifications))
    best = float("inf")
    for size in range(len(justification_ids) + 1):
        for choice in combinations(justification_ids, size):
            nodes = set(field.premises) | set(field.targets)
            for justification_id in choice:
                justification = field.justifications[justification_id]
                nodes.add(justification.conclusion)
                nodes.update(justification.premises)
            certificate = Certificate(
                frozenset(nodes),
                frozenset(choice),
                field.targets,
            )
            if validate_certificate(field, certificate).valid:
                best = min(
                    best,
                    certificate_cost(
                        field,
                        certificate,
                        node_cost=node_cost,
                        justification_cost=justification_cost,
                    ),
                )
    if not np.isfinite(best):
        raise RuntimeError("brute-force field unexpectedly has no certificate")
    return float(best)


def validate_minimum_certificate(rng: random.Random, trials: int = 18) -> int:
    field = _certificate_field()
    for _ in range(trials):
        node_cost = {
            node_id: rng.choice((0.0, 0.25, 0.5, 1.0, 2.0, 3.0))
            for node_id in field.nodes
        }
        justification_cost = {
            justification_id: rng.choice((0.0, 0.125, 0.25, 0.5))
            for justification_id in field.justifications
        }
        exact = minimum_certificate(
            field,
            node_cost=node_cost,
            justification_cost=justification_cost,
        )
        exact_cost = certificate_cost(
            field,
            exact,
            node_cost=node_cost,
            justification_cost=justification_cost,
        )
        brute_cost = _brute_minimum_cost(field, node_cost, justification_cost)
        if not np.isclose(exact_cost, brute_cost, atol=1e-12, rtol=0.0):
            raise AssertionError(
                f"minimum-certificate mismatch: exact={exact_cost}, brute={brute_cost}"
            )
    return trials


def validate_greedy_bound(rng: random.Random, trials: int = 100) -> int:
    candidates = tuple(f"c{index}" for index in range(7))
    targets = tuple(f"t{index}" for index in range(9))
    base = "base"
    nodes = {base, *candidates, *targets}
    k = 3
    guarantee = 1.0 - (1.0 - 1.0 / k) ** k
    for _ in range(trials):
        edges: set[tuple[str, str]] = set()
        for candidate in candidates:
            for target in targets:
                if rng.random() < 0.34:
                    edges.add((candidate, target))
        for target in targets:
            if rng.random() < 0.10:
                edges.add((base, target))
        graph = BridgeGraph(nodes, edges)
        weights = {target: rng.choice((0.25, 0.5, 1.0, 2.0, 4.0)) for target in targets}
        greedy = greedy_cardinality_retention(
            graph,
            candidates,
            weights,
            budget=k,
            mandatory=(base,),
        )
        exact = exact_cardinality_retention(
            graph,
            candidates,
            weights,
            budget=k,
            mandatory=(base,),
        )
        baseline = graph.target_utility((base,), weights)
        greedy_gain = greedy.utility - baseline
        exact_gain = exact.utility - baseline
        if greedy_gain + 1e-12 < guarantee * exact_gain:
            raise AssertionError(
                f"greedy bound failed: {greedy_gain} < {guarantee} * {exact_gain}"
            )
    return trials


def validate_retention_algebra() -> int:
    universe = frozenset(f"v{index}" for index in range(5))
    masks = [
        frozenset(choice)
        for size in range(len(universe) + 1)
        for choice in combinations(sorted(universe), size)
    ]
    checks = 0
    for left in masks:
        if retention_projection(retention_projection(universe, left), left) != left:
            raise AssertionError("retention idempotence failed")
        for right in masks:
            composed = retention_projection(
                retention_projection(universe, left), right
            )
            reversed_composed = retention_projection(
                retention_projection(universe, right), left
            )
            if composed != reversed_composed or composed != retention_meet(left, right):
                raise AssertionError("retention composition failed")
            if retention_join(left, right) != left.union(right):
                raise AssertionError("retention join failed")
            checks += 1
    return checks


def validate_review_formula() -> int:
    checks = 0
    for reviewers in range(2, 21):
        lower = -1.0 / (reviewers - 1)
        for correlation in (max(lower + 0.01, -0.2), 0.0, 0.1, 0.35, 0.8, 1.0):
            covariance = equicorrelated_covariance(
                reviewers,
                variance=1.7,
                correlation=correlation,
            )
            direct = effective_reviewer_count(
                covariance,
                reference_variance=1.7,
            )
            formula = equicorrelated_effective_count(reviewers, correlation)
            if not np.isclose(direct, formula, atol=1e-10, rtol=1e-10):
                raise AssertionError("effective reviewer formula mismatch")
            checks += 1
    return checks


def main() -> int:
    rng = random.Random(1729)
    report = {
        "version": __version__,
        "seed": 1729,
        "minimum_certificate_bruteforce_trials": validate_minimum_certificate(rng),
        "greedy_bound_trials": validate_greedy_bound(rng),
        "retention_algebra_checks": validate_retention_algebra(),
        "review_formula_checks": validate_review_formula(),
        "status": "passed",
    }
    OUTPUT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
