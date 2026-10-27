#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


def det(matrix: Sequence[Sequence[int]]) -> int:
    n = len(matrix)
    if n == 0:
        return 1
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    total = 0
    for j, value in enumerate(matrix[0]):
        minor = [list(row[:j]) + list(row[j + 1 :]) for row in matrix[1:]]
        total += (-1) ** j * value * det(minor)
    return total


def rank_rational(columns: Sequence[Sequence[int]]) -> int:
    if not columns:
        return 0
    rows = len(columns[0])
    matrix = [[Fraction(columns[j][i]) for j in range(len(columns))] for i in range(rows)]
    rank = 0
    for col in range(len(columns)):
        pivot = next((r for r in range(rank, rows) if matrix[r][col] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        matrix[rank] = [x / pivot_value for x in matrix[rank]]
        for r in range(rows):
            if r != rank and matrix[r][col] != 0:
                factor = matrix[r][col]
                matrix[r] = [x - factor * y for x, y in zip(matrix[r], matrix[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def all_square_minors(matrix: Sequence[Sequence[int]]) -> dict[int, list[int]]:
    row_count = len(matrix)
    col_count = len(matrix[0])
    values: dict[int, list[int]] = {}
    for size in range(1, min(row_count, col_count) + 1):
        vals: list[int] = []
        for rows in itertools.combinations(range(row_count), size):
            for cols in itertools.combinations(range(col_count), size):
                square = [[matrix[i][j] for j in cols] for i in rows]
                vals.append(det(square))
        values[size] = vals
    return values


def connected_parameters(n: int) -> tuple[int, int]:
    if n < 7:
        raise ValueError("connected family starts at dimension seven")
    v = (n - 1) // 2
    u = n - v - 2
    if not (1 <= v <= u + 1):
        raise AssertionError((n, u, v))
    return u, v


def main() -> None:
    # Columns are x, p, q, x+p, p+q, x+p+q.
    b = [
        [1, 0, 0, 1, 0, 1],
        [0, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 1],
    ]
    minors = all_square_minors(b)
    assert all(value in (-1, 0, 1) for vals in minors.values() for value in vals)

    columns = [tuple(b[i][j] for i in range(3)) for j in range(6)]
    dependent_triples = []
    for triple in itertools.combinations(range(6), 3):
        selected = [columns[j] for j in triple]
        if rank_rational(selected) < 3:
            dependent_triples.append(triple)
    expected_cycles = [(0, 1, 3), (0, 4, 5), (1, 2, 4), (2, 3, 5)]
    assert dependent_triples == expected_cycles

    # Edge labels p,x,x+p,p+q,q,x+p+q -> 12,13,23,14,24,34.
    state_to_edge = ["13", "12", "24", "23", "14", "34"]
    cycle_edges = [tuple(sorted(state_to_edge[i] for i in triple)) for triple in dependent_triples]
    assert sorted(cycle_edges) == sorted(
        [
            ("12", "13", "23"),
            ("12", "14", "24"),
            ("13", "14", "34"),
            ("23", "24", "34"),
        ]
    )

    connected_rows = []
    for n in range(7, 101):
        u, v = connected_parameters(n)
        restricted = u + 2 * v
        two_upper = u + v + 2
        gap = restricted - two_upper
        assert two_upper == n
        assert gap == (n - 5) // 2
        connected_rows.append(
            {
                "dimension": n,
                "u": u,
                "v": v,
                "restricted_exact": restricted,
                "two_upper_upper_bound": two_upper,
                "certified_gap": gap,
            }
        )

    weighted_checks = []
    for lambda_value in (Fraction(1), Fraction(3), Fraction(5), Fraction(15, 2)):
        for n in (7, 12, 21, 40, 100):
            u, v = connected_parameters(n)
            weighted_upper = Fraction(u + v) + 2 * lambda_value
            restricted = Fraction(u + 2 * v)
            advantage = restricted - weighted_upper
            assert advantage == Fraction(v) - 2 * lambda_value
            weighted_checks.append(
                {
                    "lambda": str(lambda_value),
                    "dimension": n,
                    "advantage_lower_bound": str(advantage),
                }
            )

    summary = {
        "matrix": b,
        "minor_value_sets": {str(k): sorted(set(v)) for k, v in minors.items()},
        "minor_counts": {str(k): len(v) for k, v in minors.items()},
        "dependent_triples_zero_based": [list(t) for t in dependent_triples],
        "k4_triangle_edge_sets": [list(t) for t in sorted(cycle_edges)],
        "connected_family_first": connected_rows[0],
        "connected_family_last": connected_rows[-1],
        "weighted_checks": weighted_checks,
    }

    Path("resource_generalization_results.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )

    print("regular_matroid_total_unimodularity PASS")
    print("minor_value_sets", {k: sorted(set(v)) for k, v in minors.items()})
    print("dependent_triples", dependent_triples)
    print("k4_triangle_edge_sets", sorted(cycle_edges))
    print("two_upper_family_dimensions 7..100 PASS")
    print("weighted_penalty_identities PASS")
    print("wrote resource_generalization_results.json")


if __name__ == "__main__":
    main()
