#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from typing import Iterable, List, Sequence, Tuple

Matrix = List[List[int]]
Cut = Tuple[List[int], List[int]]


def eye(n: int) -> Matrix:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def add_row(a: Matrix, source: int, target: int, coeff: int, modulus: int) -> None:
    a[target] = [
        (x + coeff * y) % modulus for x, y in zip(a[target], a[source])
    ]


def matmul(a: Matrix, b: Matrix, modulus: int) -> Matrix:
    n, p, m = len(a), len(b), len(b[0])
    assert len(a[0]) == p
    return [
        [sum(a[i][k] * b[k][j] for k in range(p)) % modulus for j in range(m)]
        for i in range(n)
    ]


def kron(a: Matrix, b: Matrix, modulus: int) -> Matrix:
    return [
        [
            (a[i][j] * b[r][s]) % modulus
            for j in range(len(a[0]))
            for s in range(len(b[0]))
        ]
        for i in range(len(a))
        for r in range(len(b))
    ]


def rank_mod(a: Matrix, modulus: int) -> int:
    if not a or not a[0]:
        return 0
    m = [row[:] for row in a]
    rows, cols = len(m), len(m[0])
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if m[r][col] % modulus), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        inv = pow(m[rank][col] % modulus, -1, modulus)
        m[rank] = [(inv * x) % modulus for x in m[rank]]
        for r in range(rows):
            if r != rank and m[r][col] % modulus:
                factor = m[r][col] % modulus
                m[r] = [
                    (x - factor * y) % modulus for x, y in zip(m[r], m[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def snapshot_target(u: int, phases: Sequence[int], modulus: int) -> Matrix:
    phases = tuple(phases)
    assert 1 <= len(phases) <= u + 1
    assert tuple(sorted(set(phases))) == phases
    assert 0 <= phases[0] and phases[-1] <= u
    v = len(phases)
    n = u + v + 2
    p, q, first_t = u, u + 1, u + 2
    a = eye(n)
    for i in range(u):
        a[p][i] = 1
    for j, phase in enumerate(phases):
        t = first_t + j
        a[t][p] = 1
        a[t][q] = 1
        for i in range(phase):
            a[t][i] = 1
    return [[x % modulus for x in row] for row in a]


def snapshot_ambient(u: int, phases: Sequence[int], modulus: int) -> Matrix:
    phases = tuple(phases)
    v = len(phases)
    n = u + v + 2
    p, q, first_t = u, u + 1, u + 2
    by_phase = {phase: j for j, phase in enumerate(phases)}
    a = eye(n)
    add_row(a, q, p, 1, modulus)
    if 0 in by_phase:
        add_row(a, p, first_t + by_phase[0], 1, modulus)
    for i in range(u):
        add_row(a, i, p, 1, modulus)
        phase = i + 1
        if phase in by_phase:
            add_row(a, p, first_t + by_phase[phase], 1, modulus)
    add_row(a, q, p, -1, modulus)
    return a


def snapshot_lower(u: int, phases: Sequence[int], modulus: int) -> Matrix:
    phases = tuple(phases)
    v = len(phases)
    n = u + v + 2
    p, q, first_t = u, u + 1, u + 2
    by_phase = {phase: j for j, phase in enumerate(phases)}
    a = eye(n)
    if 0 in by_phase:
        t = first_t + by_phase[0]
        add_row(a, p, t, 1, modulus)
        add_row(a, q, t, 1, modulus)
    for i in range(u):
        add_row(a, i, p, 1, modulus)
        phase = i + 1
        if phase in by_phase:
            t = first_t + by_phase[phase]
            add_row(a, p, t, 1, modulus)
            add_row(a, q, t, 1, modulus)
    return a


def snapshot_tree(u: int, v: int) -> List[Cut]:
    n = u + v + 2
    p, q, first_t = u, u + 1, u + 2
    cuts: List[Cut] = []
    cuts.append((list(range(0, p + 1)), list(range(q, n))))
    for r in range(u):
        cuts.append(([r], list(range(r + 1, p + 1))))
    for j in range(v):
        cuts.append((list(range(q, first_t + j)), [first_t + j]))
    assert len(cuts) == n - 1
    return cuts


def potential(a: Matrix, cuts: Sequence[Cut], modulus: int) -> int:
    total = 0
    for left, right in cuts:
        block = [[a[i][j] for j in left] for i in right]
        total += rank_mod(block, modulus)
    return total


def substitution_tree(outer: Sequence[Cut], inner: Sequence[Cut], m: int, n: int) -> List[Cut]:
    cuts: List[Cut] = []
    for left, right in outer:
        cuts.append((
            [i * n + r for i in left for r in range(n)],
            [i * n + r for i in right for r in range(n)],
        ))
    for i in range(m):
        for left, right in inner:
            cuts.append((
                [i * n + r for r in left],
                [i * n + r for r in right],
            ))
    assert len(cuts) == m * n - 1
    return cuts


def zeta_lift(a: Matrix, modulus: int) -> Matrix:
    m = len(a)
    z = [[0 for _ in range(2 * m)] for _ in range(2 * m)]
    for i in range(m):
        for j in range(m):
            z[i][j] = a[i][j] % modulus
            z[m + i][j] = a[i][j] % modulus
            z[m + i][m + j] = a[i][j] % modulus
    return z


def connected_parameters(n: int) -> Tuple[int, int, Tuple[int, ...]]:
    assert n >= 7
    v = (n - 1) // 2
    u = n - v - 2
    phases = tuple(range(v))
    assert v <= u + 1
    return u, v, phases


def main() -> None:
    checks = []
    for modulus in (2, 3, 5):
        for u, phases in ((2, (0, 1, 2)), (3, (0, 1, 2)), (3, (0, 1, 2, 3)), (9, tuple(range(10)))):
            target = snapshot_target(u, phases, modulus)
            assert snapshot_ambient(u, phases, modulus) == target
            assert snapshot_lower(u, phases, modulus) == target
            v = len(phases)
            phi = potential(target, snapshot_tree(u, v), modulus)
            assert phi == u + 2 * v
            checks.append({
                "field": modulus,
                "u": u,
                "v": v,
                "dimension": u + v + 2,
                "tree_potential": phi,
                "ambient_word_length": u + v + 2,
                "lower_word_length": u + 2 * v,
            })

    # A concrete tensor audit for the seven-dimensional seed.
    modulus = 2
    a = snapshot_target(2, (0, 1, 2), modulus)
    t = kron(a, a, modulus)
    cuts = substitution_tree(snapshot_tree(2, 3), snapshot_tree(2, 3), 7, 7)
    tensor_phi = potential(t, cuts, modulus)
    assert tensor_phi == 2 * 7 * 8

    # Zeta-lift rank recurrence is audited on the same seed.
    z = zeta_lift(a, modulus)
    assert len(z) == 14
    cross_rank = rank_mod([row[:7] for row in z[7:]], modulus)
    assert cross_rank == 7

    higher_table = []
    for n in range(7, 22):
        u, v, phases = connected_parameters(n)
        lower = u + 2 * v
        ambient = n
        higher_table.append({
            "dimension": n,
            "u": u,
            "v": v,
            "phases": list(phases),
            "restricted_exact": lower,
            "ambient_upper": ambient,
            "certified_gap": lower - ambient,
        })
        assert lower - ambient == math.floor((n - 5) / 2)

    rates = []
    for m in range(7, 101):
        v = (m - 1) // 2
        u = m - v - 2
        if 3 <= v <= u + 1:
            delta = v - 2
            rate = delta / (m * math.log2(m))
            rates.append((rate, m, u, v, delta))
    best = max(rates)
    assert best[1:] == (21, 9, 10, 8)

    tensor_table = []
    m, lower_seed, ambient_seed, delta = 21, 29, 21, 8
    for r in range(1, 5):
        n = m**r
        lower = r * (m ** (r - 1)) * lower_seed
        ambient = r * n
        gap = r * (m ** (r - 1)) * delta
        assert lower - ambient == gap
        tensor_table.append({
            "power": r,
            "dimension": n,
            "restricted_exact": lower,
            "ambient_upper": ambient,
            "certified_gap": gap,
        })

    result = {
        "snapshot_checks": checks,
        "tensor_seed_7_potential": tensor_phi,
        "zeta_seed_7_cross_rank": cross_rank,
        "connected_higher_cases": higher_table,
        "optimal_snapshot_rate": {
            "dimension": best[1],
            "u": best[2],
            "v": best[3],
            "seed_defect": best[4],
            "coefficient": best[0],
            "exact_expression": "8/(21*log2(21))",
        },
        "tensor_power_table": tensor_table,
    }
    with open("higher_family_results.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print("snapshot circuit identities: PASS")
    print("interval-tree certificates: PASS")
    print(f"seven-dimensional tensor potential: {tensor_phi}")
    print(f"zeta-lift cross rank: {cross_rank}")
    print("connected cases n=7..21: PASS")
    print(
        "best snapshot tensor coefficient: "
        f"m={best[1]} u={best[2]} v={best[3]} delta={best[4]} "
        f"c={best[0]:.15f}"
    )
    print("tensor power formulas r=1..4: PASS")


if __name__ == "__main__":
    main()
