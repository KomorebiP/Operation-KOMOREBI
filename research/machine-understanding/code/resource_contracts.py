#!/usr/bin/env python3
"""Finite resource contracts for fixed-recipient acquisition and explanation.

The state space, experiments, costs, and bounded-decoder outcomes are supplied.
This module does not discover them. Costs are nonnegative integer vectors in
explicitly declared units. A controller is an explicit tree, not a shared DAG.
Only the Python standard library is used.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import combinations, product
from typing import Any, Iterable

Cost = tuple[int, ...]
Policy = dict[str, Any]


def natural(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer, not a boolean.')
    return value


def leq(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    if len(a) != len(b):
        raise ValueError('Incompatible vector dimensions.')
    return all(x <= y for x, y in zip(a, b))


def max_vectors(rows: Iterable[Cost]) -> Cost:
    rows = tuple(rows)
    if not rows:
        raise ValueError('A componentwise maximum needs a nonempty family.')
    if len({len(r) for r in rows}) != 1:
        raise ValueError('Incompatible vector dimensions.')
    return tuple(max(r[j] for r in rows) for j in range(len(rows[0])))


def common_codebook(allowed: Iterable[Iterable[int]], message_count: int) -> tuple[int, ...] | None:
    """Smallest common codebook meeting every nonempty sender-fibre requirement.

    ``None`` is a genuine finite-catalogue impossibility. An empty family needs
    no messages. Each member is the intersection of allowable messages across
    all cases in that sender fibre, not a union of casewise choices.
    """
    natural(message_count, 'message_count')
    requirements = tuple(frozenset(r) for r in allowed)
    if any(type(x) is not int or not 0 <= x < message_count
           for r in requirements for x in r):
        raise ValueError('Message id outside the finite alphabet.')
    for k in range(message_count + 1):
        for chosen in combinations(range(message_count), k):
            if all(set(chosen) & r for r in requirements):
                return chosen
    return None


@dataclass(frozen=True)
class Experiment:
    name: str
    transition: tuple[int, ...]
    observation: tuple[int, ...]
    admissible: frozenset[int]
    cost: Cost


@dataclass(frozen=True)
class Model:
    state_count: int
    message_count: int
    units: tuple[str, ...]
    experiments: tuple[Experiment, ...]
    # terminal_costs[x][m] is None for a false answer, timeout, or rejection.
    terminal_costs: tuple[tuple[Cost | None, ...], ...]

    def __post_init__(self) -> None:
        natural(self.state_count, 'state_count')
        natural(self.message_count, 'message_count')
        if not self.state_count or not self.message_count or not self.units:
            raise ValueError('States, messages, and cost dimensions must be nonempty.')
        if len(set(self.units)) != len(self.units) or any(not u for u in self.units):
            raise ValueError('Cost units must be nonempty and distinct.')
        n, k, d = self.state_count, self.message_count, len(self.units)
        def valid_cost(c: Cost) -> None:
            if len(c) != d:
                raise ValueError('Incorrect cost dimension.')
            for x in c:
                natural(x, 'cost')
        if len(self.terminal_costs) != n or any(len(r) != k for r in self.terminal_costs):
            raise ValueError('Incorrect terminal table shape.')
        for row in self.terminal_costs:
            for c in row:
                if c is not None:
                    valid_cost(c)
        if len({e.name for e in self.experiments}) != len(self.experiments):
            raise ValueError('Experiment names must be unique.')
        for e in self.experiments:
            if not e.name or len(e.transition) != n or len(e.observation) != n:
                raise ValueError('Malformed experiment table.')
            if any(type(x) is not int or not 0 <= x < n for x in e.transition):
                raise ValueError('Transition leaves the declared state space.')
            if any(type(o) is not int or o < 0 for o in e.observation):
                raise ValueError('Observation ids must be nonnegative integers.')
            if any(type(x) is not int or not 0 <= x < n for x in e.admissible):
                raise ValueError('Invalid admissibility set.')
            valid_cost(e.cost)


def checked_support(model: Model, support: Iterable[int]) -> tuple[int, ...]:
    v = tuple(sorted(set(support)))
    if not v or any(type(x) is not int or not 0 <= x < model.state_count for x in v):
        raise ValueError('Support must be a nonempty subset of the state space.')
    return v


def branches(model: Model, support: tuple[int, ...], experiment: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    e = model.experiments[experiment]
    if not set(support) <= e.admissible:
        raise ValueError('Experiment is not uniformly admissible.')
    outcomes = sorted({e.observation[x] for x in support})
    return tuple((o, tuple(sorted({e.transition[x] for x in support if e.observation[x] == o})))
                 for o in outcomes)


@dataclass(frozen=True)
class Profile:
    cost: Cost
    records: int
    policy: Policy = field(compare=False, hash=False)

    @property
    def key(self) -> tuple[int, ...]:
        return self.cost + (self.records,)


def nondominated(profiles: Iterable[Profile]) -> tuple[Profile, ...]:
    unique: dict[tuple[int, ...], Profile] = {}
    for p in profiles:
        unique.setdefault(p.key, p)
    keys = sorted(unique)
    return tuple(unique[k] for k in keys if not any(j != k and leq(j, k) for j in keys))


def resource_frontier(model: Model, support: Iterable[int], horizon: int) -> tuple[Profile, ...]:
    """Return the exact Pareto frontier of attainable tree costs with witnesses.

    Stop costs include all charged recipient execution costs. Experiment costs
    include the charged source-side interface work. Planning work is offline and
    separately reported. The number of records counts the entire explicit tree,
    including mutually exclusive branches, rather than the longest run alone.
    """
    natural(horizon, 'horizon')
    initial = checked_support(model, support)
    @lru_cache(None)
    def solve(v: tuple[int, ...], h: int) -> tuple[Profile, ...]:
        candidates: list[Profile] = []
        for message in range(model.message_count):
            costs = [model.terminal_costs[x][message] for x in v]
            if all(c is not None for c in costs):
                candidates.append(Profile(max_vectors(costs), 1, {'kind': 'stop', 'message': message}))
        if h:
            for j, e in enumerate(model.experiments):
                if not set(v) <= e.admissible:
                    continue
                children = branches(model, v, j)
                fronts = [solve(w, h - 1) for _, w in children]
                if any(not front for front in fronts):
                    continue
                for combo in product(*fronts):
                    tail = max_vectors(p.cost for p in combo)
                    candidates.append(Profile(
                        tuple(a + b for a, b in zip(e.cost, tail)),
                        1 + sum(p.records for p in combo),
                        {'kind': 'experiment', 'experiment': j,
                         'branches': {str(o): p.policy for (o, _), p in zip(children, combo)}}))
        return nondominated(candidates)
    return solve(initial, horizon)


def verify_policy(model: Model, support: Iterable[int], horizon: int, policy: Policy) -> Profile:
    """Verify a supplied tree without invoking resource_frontier.

    Structure/admissibility is checked on every reachable support. Actual costs
    are independently accumulated by simulating every possible initial state.
    Extraneous branches, unavailable experiments, invalid messages, and horizon
    overruns are rejected rather than silently ignored.
    """
    natural(horizon, 'horizon')
    initial = checked_support(model, support)
    def structure(node: Policy, v: tuple[int, ...], remaining: int) -> int:
        if not isinstance(node, dict):
            raise ValueError('Policy node must be a dictionary.')
        if node.get('kind') == 'stop':
            if set(node) != {'kind', 'message'}:
                raise ValueError('Unexpected stop fields.')
            m = node['message']
            if type(m) is not int or not 0 <= m < model.message_count:
                raise ValueError('Invalid message.')
            if any(model.terminal_costs[x][m] is None for x in v):
                raise ValueError('Message fails a recipient or resource contract.')
            return 1
        if node.get('kind') != 'experiment' or set(node) != {'kind', 'experiment', 'branches'} or not remaining:
            raise ValueError('Malformed experiment node or exhausted horizon.')
        j = node['experiment']
        if type(j) is not int or not 0 <= j < len(model.experiments):
            raise ValueError('Experiment outside the catalogue.')
        children = branches(model, v, j)
        if not isinstance(node['branches'], dict) or set(node['branches']) != {str(o) for o, _ in children}:
            raise ValueError('Branch set is not exactly the possible observation set.')
        return 1 + sum(structure(node['branches'][str(o)], w, remaining - 1) for o, w in children)
    records = structure(policy, initial, horizon)
    accumulated = []
    for x0 in initial:
        x, node, total = x0, policy, [0] * len(model.units)
        while node['kind'] != 'stop':
            e = model.experiments[node['experiment']]
            total = [a + b for a, b in zip(total, e.cost)]
            o, x = e.observation[x], e.transition[x]
            node = node['branches'][str(o)]
        gamma = model.terminal_costs[x][node['message']]
        if gamma is None:
            raise ValueError('Invalid leaf.')
        accumulated.append(tuple(a + b for a, b in zip(total, gamma)))
    return Profile(max_vectors(accumulated), records, policy)
