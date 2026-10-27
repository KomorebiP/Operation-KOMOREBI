#!/usr/bin/env python3
"""Exact finite regression of the v0.14 research protocol.

This is a separately implemented toy-model regression, NOT Lean extraction and
NOT a simulation of measured LLM success. All task propositions in the model
are True. A receipt is valid exactly when its Boolean observation is 1.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import hashlib, json, platform, time

@dataclass(frozen=True)
class State:
    belief: F
    completed: frozenset[int]
    pending: frozenset[int]
    budget: int
    spent: int = 0
    halted: bool = False

Action = tuple[str, int]
STOP: Action = ('stop', -1)

def subsets(values):
    values = sorted(values)
    return [frozenset(values[j] for j in range(len(values)) if mask >> j & 1)
            for mask in range(1 << len(values))]

def closure(n, edges):
    rows = [set() for _ in range(n)]
    for u, v in edges:
        rows[v].add(u)
    for k in range(n):
        for v in range(n):
            if k in rows[v]:
                rows[v] |= rows[k]
    return tuple(frozenset(x) for x in rows)

class Model:
    def __init__(self, prereqs: tuple[frozenset[int], ...], congestion: F):
        self.prereqs = prereqs
        self.tasks = frozenset(range(len(prereqs)))
        self.congestion = congestion

    def ready(self, s: State):
        return {x for x in self.tasks - s.completed if self.prereqs[x] <= s.completed}

    def safe(self, s: State):
        return (F(0) <= s.belief <= F(1) and s.completed <= self.tasks
                and all(self.prereqs[x] <= s.completed for x in s.completed)
                and s.pending <= self.ready(s) and s.budget >= 0 and s.spent >= 0)

    def actions(self, s: State):
        if s.halted or s.budget < 1:
            return (STOP,)
        ready = self.ready(s)
        return (STOP,) + tuple(('attempt', x) for x in sorted(ready - s.pending)) + \
            tuple(('verify', x) for x in sorted(ready & s.pending))

    def prob(self, s: State, o: int):
        return s.belief if o else 1 - s.belief

    def step(self, s: State, a: Action, o: int):
        if a not in self.actions(s):
            raise ValueError('Inadmissible action: ' + repr(a))
        if o not in (0, 1):
            raise ValueError('Invalid observation')
        kind, x = a
        if kind == 'stop':
            return replace(s, halted=True)
        posterior = F(o) if self.prob(s, o) > 0 else s.belief
        if kind == 'attempt':
            return replace(s, belief=posterior, pending=s.pending | {x},
                           budget=s.budget - 1, spent=s.spent + 1)
        return replace(s, belief=posterior, pending=s.pending - {x},
                       completed=s.completed | ({x} if o else set()),
                       budget=s.budget - 1, spent=s.spent + 1)

    def reward(self, s: State, a: Action):
        if a == STOP or s.halted:
            return F(0)
        return -1 - self.congestion * len(s.pending) ** 2 + (6 * s.belief if a[0] == 'verify' else 0)

    @lru_cache(None)
    def bellman(self, n: int, s: State):
        if n == 0:
            return F(0)
        return max(self.reward(s, a) + sum(self.prob(s, o) * self.bellman(n - 1, self.step(s, a, o))
                                          for o in (0, 1)) for a in self.actions(s))

    @lru_cache(None)
    def all_tree_values(self, n: int, s: State):
        """Explicit adaptive-tree enumeration, independent of max/Bellman recursion."""
        if n == 0:
            return (F(0),)
        values = []
        for a in self.actions(s):
            branches = [self.all_tree_values(n - 1, self.step(s, a, o)) for o in (0, 1)]
            for v0, v1 in product(*branches):
                values.append(self.reward(s, a) + self.prob(s, 0) * v0 + self.prob(s, 1) * v1)
        return tuple(values)

def main():
    t = time.monotonic()
    counters = dict(orders=0, model_configs=0, states=0, transition_checks=0,
                    oracle_comparisons=0, enumerated_policy_trees=0)
    for n in range(4):
        edges = list(combinations(range(n), 2)); seen = set()
        for bits in range(1 << len(edges)):
            rel = closure(n, [edge for j, edge in enumerate(edges) if bits >> j & 1])
            if rel in seen:
                continue
            seen.add(rel); counters['orders'] += 1
            for congestion in (F(0), F(1, 4)):
                model = Model(rel, congestion); counters['model_configs'] += 1
                for completed in subsets(range(n)):
                    if not all(rel[x] <= completed for x in completed):
                        continue
                    ready = model.ready(State(F(1, 2), completed, frozenset(), 3))
                    for pending, budget, b, halted in product(subsets(ready), range(4), (F(0), F(1, 2), F(1)), (False, True)):
                        s = State(b, completed, pending, budget, 3 - budget, halted)
                        assert model.safe(s); counters['states'] += 1
                        for a, o in product(model.actions(s), (0, 1)):
                            z = model.step(s, a, o); counters['transition_checks'] += 1
                            assert model.safe(z) and z.budget + z.spent == 3
                            assert z.budget <= s.budget and z.completed >= s.completed
                            if a[0] != 'verify' or o == 0:
                                assert z.completed == s.completed
                            for x in z.completed - s.completed:
                                assert a == ('verify', x) and x in s.pending and rel[x] <= s.completed
                        vals = model.all_tree_values(2, s)
                        assert max(vals) == model.bellman(2, s)
                        assert min(model.bellman(2, s) - v for v in vals) >= 0
                        counters['oracle_comparisons'] += 1
                        counters['enumerated_policy_trees'] += len(vals)
    demo = Model((frozenset(),), F(0))
    initial = State(F(1, 2), frozenset(), frozenset(), 2)
    assert demo.bellman(1, initial) == 0
    assert demo.bellman(2, initial) == F(3, 2)
    positive = demo.step(initial, ('attempt', 0), 1)
    assert positive.belief == 1 and not positive.completed
    accepted = demo.step(positive, ('verify', 0), 1)
    assert accepted.completed == {0} and accepted.spent == 2 and accepted.budget == 0
    failures = 0
    for bad_state, bad_action in ((initial, ('verify', 0)),
                                  (replace(initial, budget=0), ('attempt', 0)),
                                  (replace(initial, halted=True), ('attempt', 0))):
        try:
            demo.step(bad_state, bad_action, 1)
        except ValueError:
            failures += 1
        else:
            raise AssertionError('Guard bypass accepted')
    report = dict(status='PASS', model='finite static Boolean tool-availability world; all claims True',
                  arithmetic='fractions.Fraction; exact rational',
                  bounds=dict(task_vertices=[0, 3], forward_edge_DAGs=True, horizons=[2],
                              priors=['0', '1/2', '1'], remaining_budgets=[0, 3],
                              congestion_coefficients=['0', '1/4'], observations=[0, 1]),
                  counters=counters, invalid_actions_rejected=failures,
                  example=dict(one_step='0', two_step='3/2', successful_spend=2),
                  python=platform.python_version(), elapsed_seconds=round(time.monotonic()-t, 3),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  nonclaims=['not Lean-extracted', 'not empirical LLM validation',
                             'no universal theorem inferred from bounded tests'])
    out = Path(__file__).resolve().parents[1] / 'results/v0.14.0/controller_regression.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
