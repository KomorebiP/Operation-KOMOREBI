#!/usr/bin/env python3
"""Finite reference constructions for Machine Understanding, v0.5.0.

These routines operate on explicitly supplied mathematical models. They do not
infer a neural mechanism, authenticate observations, or establish comprehension.
Probabilities and costs use Fraction. None means that a finite acquisition
contract is infeasible, not that a timeout or an implementation error occurred.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Hashable, Sequence

F = Fraction
Distribution = tuple[Fraction, ...]
Matrix = tuple[Distribution, ...]


def distribution(values: Sequence[Fraction | int]) -> Distribution:
    p = tuple(F(v) for v in values)
    if not p or any(v < 0 for v in p) or sum(p) != 1:
        raise ValueError('Expected a nonempty nonnegative distribution of mass one.')
    return p


def channel(rows: Sequence[Sequence[Fraction | int]]) -> Matrix:
    ans = tuple(distribution(row) for row in rows)
    if not ans or len({len(row) for row in ans}) != 1:
        raise ValueError('A channel needs a nonempty rectangular set of rows.')
    return ans


def tv(p: Sequence[Fraction], q: Sequence[Fraction]) -> Fraction:
    if len(p) != len(q):
        raise ValueError('Distributions must use the same finite alphabet.')
    return sum((abs(a-b) for a, b in zip(p, q)), F(0)) / 2


def compose(left: Matrix, right: Matrix) -> Matrix:
    left, right = channel(left), channel(right)
    if len(left[0]) != len(right):
        raise ValueError('Channel dimensions do not match.')
    return tuple(tuple(sum((left[m][o]*right[o][z]
                            for o in range(len(right))), F(0))
                       for z in range(len(right[0]))) for m in range(len(left)))


def posterior(prior: Sequence[Fraction], likelihood: Sequence[Fraction]) -> Distribution | None:
    p = distribution(prior)
    if len(p) != len(likelihood) or any(v < 0 for v in likelihood):
        raise ValueError('Likelihood dimension or sign is invalid.')
    u = tuple(a*F(b) for a, b in zip(p, likelihood))
    mass = sum(u)
    return None if mass == 0 else tuple(v/mass for v in u)


def reconstruct_channel(likelihood: Matrix, report: Matrix) -> Matrix | None:
    """Find rho[z][o] with L[m,o] B[o,z] = (LB)[m,z] rho[z,o].

    This is conditional reconstruction in the actual joint experiment. Merely
    simulating L from LB through some other channel is a different property.
    Columns z impossible under every model get an arbitrary point-mass row.
    """
    likelihood, report = channel(likelihood), channel(report)
    coarse = compose(likelihood, report)
    n_o, n_z = len(likelihood[0]), len(report[0])
    result = []
    for z in range(n_z):
        m0 = next((m for m in range(len(likelihood)) if coarse[m][z] > 0), None)
        if m0 is None:
            rho = tuple(F(int(o == 0)) for o in range(n_o))
        else:
            rho = tuple(likelihood[m0][o]*report[o][z]/coarse[m0][z]
                        for o in range(n_o))
        if any(likelihood[m][o]*report[o][z] != coarse[m][z]*rho[o]
               for m in range(len(likelihood)) for o in range(n_o)):
            return None
        result.append(rho)
    return tuple(result)


def explanation_graph(sender: Sequence[Hashable], backgrounds: Sequence[Sequence[Hashable]],
                      demands: Sequence[Sequence[Hashable]]) -> tuple[tuple[Hashable, ...], frozenset[tuple[int, int]]]:
    """Confusability graph on sender-access values, including obstruction loops."""
    if not sender or len(backgrounds) != len(demands):
        raise ValueError('Nonempty cases and matched recipient arrays are required.')
    if any(len(row) != len(sender) for row in [*backgrounds, *demands]):
        raise ValueError('Every recipient row must cover all source cases.')
    vertices = tuple(dict.fromkeys(sender))
    index = {v: j for j, v in enumerate(vertices)}
    edges = set()
    for m, n in combinations(range(len(sender)), 2):
        if any(b[m] == b[n] and d[m] != d[n] for b, d in zip(backgrounds, demands)):
            i, j = sorted((index[sender[m]], index[sender[n]]))
            edges.add((i, j))
    return vertices, frozenset(edges)


def color_graph(n: int, edges: frozenset[tuple[int, int]], k: int) -> tuple[int, ...] | None:
    """Exact bounded coloring, with loops interpreted as infeasibility."""
    if n < 1 or k < 1 or any(i < 0 or j >= n or i > j for i, j in edges):
        raise ValueError('Invalid graph or color bound.')
    if any(i == j for i, j in edges):
        return None
    neighbors = [set() for _ in range(n)]
    for i, j in edges:
        neighbors[i].add(j); neighbors[j].add(i)
    order = sorted(range(n), key=lambda i: (-len(neighbors[i]), i))
    colors = [-1]*n
    def visit(pos: int) -> bool:
        if pos == n:
            return True
        v = order[pos]
        used = {colors[u] for u in neighbors[v] if colors[u] >= 0}
        for c in range(k):
            if c not in used:
                colors[v] = c
                if visit(pos+1): return True
        colors[v] = -1
        return False
    return tuple(colors) if visit(0) else None


def chromatic_number(n: int, edges: frozenset[tuple[int, int]]) -> int | None:
    if any(i == j for i, j in edges): return None
    for k in range(1, n+1):
        if color_graph(n, edges, k) is not None: return k
    raise RuntimeError('A finite loop-free graph must admit an n-coloring.')


@dataclass(frozen=True)
class Experiment:
    name: str
    next_state: tuple[int, ...]
    outcome: tuple[Hashable, ...]
    cost: Fraction = F(1)
    allowed: tuple[bool, ...] | None = None

    def validate(self, n: int) -> None:
        if len(self.next_state) != n or len(self.outcome) != n:
            raise ValueError('Experiment tables do not match the state space.')
        if any(y < 0 or y >= n for y in self.next_state):
            raise ValueError('A transition leaves the state space.')
        if self.cost < 0:
            raise ValueError('Experiment costs must be nonnegative.')
        if self.allowed is not None and len(self.allowed) != n:
            raise ValueError('Admissibility table does not match the state space.')
        for o in self.outcome: hash(o)


def successors(belief: frozenset[int], e: Experiment) -> dict[Hashable, frozenset[int]]:
    result: dict[Hashable, set[int]] = {}
    for x in sorted(belief):
        result.setdefault(e.outcome[x], set()).add(e.next_state[x])
    return {o: frozenset(xs) for o, xs in result.items()}


def acquisition(target: Sequence[Hashable], experiments: Sequence[Experiment],
                initial: frozenset[int], horizon: int) -> tuple[Fraction | None, dict]:
    """Minimum worst-case cost to know the CURRENT target within a finite horizon.

    Available actions must be admissible at every currently possible state.
    Historical recovery requires explicit origin tags in the state and target.
    Costs may be zero because the declared horizon bounds the search.
    """
    n = len(target)
    if not n or not initial or horizon < 0 or any(x < 0 or x >= n for x in initial):
        raise ValueError('Invalid acquisition contract.')
    for e in experiments: e.validate(n)
    @lru_cache(None)
    def value(b: frozenset[int], h: int) -> tuple[Fraction | None, dict]:
        if len({target[x] for x in b}) == 1:
            return F(0), {'stop': True, 'belief': sorted(b), 'target': target[min(b)]}
        if h == 0:
            return None, {'infeasible': True, 'belief': sorted(b), 'horizon': 0}
        best: Fraction | None = None
        witness: dict = {'infeasible': True, 'belief': sorted(b), 'horizon': h}
        for j, e in enumerate(experiments):
            if e.allowed is not None and any(not e.allowed[x] for x in b): continue
            branches = successors(b, e)
            solved = {o: value(next_b, h-1) for o, next_b in branches.items()}
            if any(cost is None for cost, _ in solved.values()): continue
            cost = e.cost + max(v[0] for v in solved.values() if v[0] is not None)
            if best is None or cost < best:
                best = cost
                witness = {'experiment': j, 'name': e.name, 'belief': sorted(b),
                           'children': {o: result[1] for o, result in solved.items()}}
        return best, witness
    return value(initial, horizon)


def policy_trace(initial_state: int, witness: dict,
                 experiments: Sequence[Experiment]) -> tuple[int, Fraction, int]:
    """Execute a supplied witness on one state, rejecting malformed certificates."""
    x, cost, depth = initial_state, F(0), 0
    node = witness
    while not node.get('stop', False):
        if node.get('infeasible', False): raise ValueError('An infeasibility record is not a policy.')
        j = node['experiment']; e = experiments[j]
        if e.allowed is not None and not e.allowed[x]: raise ValueError('Inadmissible experiment.')
        o = e.outcome[x]
        x = e.next_state[x]; cost += e.cost; depth += 1
        node = node['children'][o]
    return x, cost, depth
