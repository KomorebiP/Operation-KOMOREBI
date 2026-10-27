"""Rational reference solver for the finite common-monitor linear program.

The vertex enumerator is for small, inspectable instances, not large-scale LPs.
It rejects an excessive enumeration before starting. All arithmetic is exact.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from typing import Sequence


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q(0))


def solve_square(rows, rhs):
    n = len(rhs)
    if len(rows) != n or any(len(row) != n for row in rows):
        raise ValueError('Square system required.')
    a = [[Q(x) for x in row] + [Q(b)] for row, b in zip(rows, rhs)]
    for col in range(n):
        piv = next((i for i in range(col, n) if a[i][col]), None)
        if piv is None:
            return None
        a[col], a[piv] = a[piv], a[col]
        scale = a[col][col]
        a[col] = [v/scale for v in a[col]]
        for i in range(n):
            if i != col and a[i][col]:
                c = a[i][col]
                a[i] = [v-c*w for v, w in zip(a[i], a[col])]
    return tuple(a[i][-1] for i in range(n))


def vertices(inequalities, dimension: int, max_combinations: int = 200_000):
    """Vertices of {x: a.x<=b}; callers supply a nonempty bounded polytope."""
    if comb(len(inequalities), dimension) > max_combinations:
        raise ValueError('Declared exact vertex-enumeration limit exceeded.')
    found = set()
    for selected in combinations(inequalities, dimension):
        point = solve_square([a for a, b in selected], [b for a, b in selected])
        if point is not None and all(dot(a, point) <= b for a, b in inequalities):
            found.add(point)
    return tuple(sorted(found))


def validate(pc, laws, gains, penalty, alpha):
    n = len(pc)
    if not n or not laws or len(laws) != len(gains):
        raise ValueError('Nonempty observations/deviations with one gain each required.')
    if any(len(p) != n or any(x < 0 for x in p) or sum(p) != 1 for p in (pc, *laws)):
        raise ValueError('Invalid rational probability law.')
    if penalty <= 0 or not 0 <= alpha <= 1 or any(g < 0 for g in gains):
        raise ValueError('Penalty, gain, or false-positive cap outside the model.')


def monitor_vertices(pc, alpha):
    n = len(pc)
    constraints = []
    for i in range(n):
        row = tuple(Q(i == j) for j in range(n))
        constraints += [(row, Q(1)), (tuple(-v for v in row), Q(0))]
    constraints.append((tuple(pc), Q(alpha)))
    return vertices(constraints, n)


def common_monitor(pc, laws, gains, penalty=Q(1), alpha=Q(1)):
    pc = tuple(map(Q, pc)); laws = tuple(tuple(map(Q, p)) for p in laws)
    gains = tuple(map(Q, gains)); penalty = Q(penalty); alpha = Q(alpha)
    validate(pc, laws, gains, penalty, alpha)
    n = len(pc)
    constraints = []
    for i in range(n):
        row = tuple(Q(i == j) for j in range(n)) + (Q(0),)
        constraints += [(row, Q(1)), (tuple(-v for v in row), Q(0))]
    constraints.append((pc + (Q(0),), alpha))
    for law, g in zip(laws, gains):
        # t <= F(P_j-P_C).s - g_j
        constraints.append((tuple(-penalty*(p-c) for p, c in zip(law, pc)) + (Q(1),), -g))
    # s=0 gives margin -max(gains), so this lower truncation cannot remove an optimum.
    constraints.append(((Q(0),)*n + (Q(-1),), max(gains)+1))
    pts = vertices(constraints, n+1)
    if not pts:
        raise RuntimeError('No LP vertex found in an always-feasible bounded surrogate.')
    optimum = max(v[-1] for v in pts)
    point = min(v for v in pts if v[-1] == optimum)
    return optimum, point[:-1]


def two_deviation_dual(pc, laws, gains, penalty=Q(1), alpha=Q(1)):
    """Independent 1-D upper-envelope minimization of the two-deviation dual."""
    pc = tuple(map(Q, pc)); laws = tuple(tuple(map(Q, p)) for p in laws)
    gains = tuple(map(Q, gains)); penalty = Q(penalty); alpha = Q(alpha)
    validate(pc, laws, gains, penalty, alpha)
    if len(laws) != 2:
        raise ValueError('This orthogonal dual checker is restricted to two deviations.')
    lines = []
    for s in monitor_vertices(pc, alpha):
        d = [penalty*dot(tuple(p-c for p,c in zip(law,pc)), s)-g
             for law,g in zip(laws,gains)]
        lines.append((d[0]-d[1], d[1]))
    candidates = {Q(0), Q(1)}
    for (a,b), (c,d) in combinations(lines, 2):
        if a != c:
            x = (d-b)/(a-c)
            if 0 <= x <= 1:
                candidates.add(x)
    scored = [(max(a*x+b for a,b in lines), x) for x in candidates]
    value, weight = min(scored)
    return value, (weight, 1-weight)
