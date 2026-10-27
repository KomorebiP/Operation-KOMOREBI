#!/usr/bin/env python3
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

Matrix = list[list[int]]


def eye(n: int) -> Matrix:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def add_row(a: Matrix, source: int, target: int, coeff: int, modulus: int) -> None:
    a[target] = [
        (x + coeff * y) % modulus for x, y in zip(a[target], a[source])
    ]


def canonical_target(modulus: int) -> Matrix:
    a = eye(6)
    a[1][0] = 1
    a[3][1] = a[3][2] = 1
    a[4][0] = a[4][1] = a[4][2] = 1
    a[5][0] = a[5][1] = a[5][2] = 1
    return [[x % modulus for x in row] for row in a]


def canonical_ambient(modulus: int) -> Matrix:
    a = eye(6)
    for source, target, coeff in [
        (2, 1, 1),
        (1, 3, 1),
        (0, 1, 1),
        (1, 4, 1),
        (1, 5, 1),
        (2, 1, -1),
    ]:
        add_row(a, source, target, coeff, modulus)
    return a


def canonical_lower(modulus: int) -> Matrix:
    a = eye(6)
    for source, target, coeff in [
        (0, 1, 1),
        (1, 2, 1),
        (0, 3, -1),
        (2, 3, 1),
        (2, 4, 1),
        (2, 5, 1),
        (1, 2, -1),
    ]:
        add_row(a, source, target, coeff, modulus)
    return a


def rank_mod_prime(a: Matrix, prime: int) -> int:
    if not a or not a[0]:
        return 0
    m = [[x % prime for x in row] for row in a]
    rows, cols = len(m), len(m[0])
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if m[r][col] != 0), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        inv = pow(m[rank][col], -1, prime)
        m[rank] = [(inv * x) % prime for x in m[rank]]
        for r in range(rows):
            if r == rank or m[r][col] == 0:
                continue
            factor = m[r][col]
            m[r] = [
                (x - factor * y) % prime for x, y in zip(m[r], m[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def strict_upper(a: Matrix) -> Matrix:
    n = len(a)
    return [[a[i][j] if i < j else 0 for j in range(n)] for i in range(n)]


def upper_bandwidth(a: Matrix) -> int:
    n = len(a)
    values = [j - i for i in range(n) for j in range(i + 1, n) if a[i][j] != 0]
    return max(values, default=0)


def connected_parameters(n: int) -> tuple[int, int, tuple[int, ...]]:
    if n < 7:
        raise ValueError("connected family starts at dimension seven")
    v = (n - 1) // 2
    u = n - v - 2
    phases = tuple(range(v))
    assert 1 <= v <= u + 1
    assert phases[-1] <= u
    return u, v, phases


def snapshot_path(u: int, phases: Sequence[int], prime: int) -> list[Matrix]:
    phases = tuple(phases)
    v = len(phases)
    n = u + v + 2
    p, q, first_t = u, u + 1, u + 2
    by_phase = {phase: j for j, phase in enumerate(phases)}
    state = eye(n)
    path = [[row[:] for row in state]]

    add_row(state, q, p, 1, prime)
    path.append([row[:] for row in state])
    if 0 in by_phase:
        add_row(state, p, first_t + by_phase[0], 1, prime)
        path.append([row[:] for row in state])
    for i in range(u):
        add_row(state, i, p, 1, prime)
        path.append([row[:] for row in state])
        phase = i + 1
        if phase in by_phase:
            add_row(state, p, first_t + by_phase[phase], 1, prime)
            path.append([row[:] for row in state])
    add_row(state, q, p, -1, prime)
    path.append([row[:] for row in state])
    assert len(path) - 1 == u + v + 2
    return path


def finite_field_bound(n: int, q: int, d: int) -> Fraction:
    N = n * (n - 1) // 2
    M = n * (n - 1)
    return min(Fraction(1), Fraction(M ** (N - d), q**d))


def tensor_lift_length(m: int, one_copy_length: int, power: int) -> int:
    return power * (m ** (power - 1)) * one_copy_length


def main() -> None:
    ring_rows = []
    for modulus in (4, 6, 8):
        target = canonical_target(modulus)
        assert canonical_ambient(modulus) == target
        assert canonical_lower(modulus) == target
        ring_rows.append(
            {
                "modulus": modulus,
                "ambient_word_length": 6,
                "lower_word_length": 7,
                "target_verified": True,
            }
        )

    microscopic_rows = []
    for prime in (2, 3, 5):
        for n in (7, 8, 9, 21, 40):
            u, v, phases = connected_parameters(n)
            path = snapshot_path(u, phases, prime)
            ranks = [rank_mod_prime(strict_upper(a), prime) for a in path]
            bandwidths = [upper_bandwidth(a) for a in path]
            assert max(ranks) == 1
            assert max(bandwidths) == 1
            assert ranks[0] == ranks[-1] == 0
            assert bandwidths[0] == bandwidths[-1] == 0
            microscopic_rows.append(
                {
                    "field": prime,
                    "dimension": n,
                    "path_length": len(path) - 1,
                    "max_strict_upper_rank": max(ranks),
                    "max_upper_bandwidth": max(bandwidths),
                    "upper_gate_count": 2,
                }
            )

    density_rows = []
    for n in (3, 4, 6, 8):
        N = n * (n - 1) // 2
        for q in (5, 11):
            for d in (1, min(2, N), min(3, N)):
                value = finite_field_bound(n, q, d)
                assert value >= 0
                assert value <= 1
                density_rows.append(
                    {
                        "n": n,
                        "q": q,
                        "d": d,
                        "bound": str(value),
                    }
                )

    tensor_rows = []
    for m, lower_seed, ambient_seed in ((7, 8, 7), (21, 29, 21)):
        for r in range(1, 5):
            for s in range(1, 5):
                lower_rs = tensor_lift_length(m, lower_seed, r + s)
                lower_split = (
                    (m**s) * tensor_lift_length(m, lower_seed, r)
                    + (m**r) * tensor_lift_length(m, lower_seed, s)
                )
                ambient_rs = tensor_lift_length(m, ambient_seed, r + s)
                ambient_split = (
                    (m**s) * tensor_lift_length(m, ambient_seed, r)
                    + (m**r) * tensor_lift_length(m, ambient_seed, s)
                )
                assert lower_rs == lower_split
                assert ambient_rs == ambient_split
                b_r = Fraction(tensor_lift_length(m, ambient_seed, r), m ** (r - 1))
                b_s = Fraction(tensor_lift_length(m, ambient_seed, s), m ** (s - 1))
                b_rs = Fraction(
                    tensor_lift_length(m, ambient_seed, r + s),
                    m ** (r + s - 1),
                )
                assert b_rs == b_r + b_s
                tensor_rows.append(
                    {
                        "dimension_seed": m,
                        "r": r,
                        "s": s,
                        "normalized_additivity": str(b_rs),
                    }
                )

    result = {
        "ring_circuit_audits": ring_rows,
        "microscopic_escape_audits": microscopic_rows,
        "finite_field_density_samples": density_rows,
        "tensor_normalization_checks": tensor_rows,
    }
    Path("further_generalization_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("composite_ring_circuit_identities Z/4,Z/6,Z/8 PASS")
    print("microscopic_rank_one_bandwidth_one_paths PASS")
    print("finite_field_density_bound_samples PASS")
    print("stable_tensor_normalization_identities PASS")
    print("wrote further_generalization_results.json")


if __name__ == "__main__":
    main()
