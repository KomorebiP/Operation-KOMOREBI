"""A bounded improvement of the diagnostic compiler, not an autonomous agent.

Supplied candidate rules can propose a tree before exhaustive synthesis. A
separate checker and a checked information lower bound authorize early return.
The model table is supplied. Table reads count compiler work in one declared
unit; they are not a count of CPU instructions or physical experiments.
No network, exec, eval, subprocess generation, or learned model is used here.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Iterable
from repair_calculus import (Problem, Experiment, Repair, Tree, Witness,
                             compile_frontier, check_tree)

class ReadBudgetExceeded(RuntimeError):
    """The declared table-read budget ended before a certificate was returned."""

@dataclass
class Meter:
    limit: int | None = None
    phase: str = 'setup'

    def __post_init__(self) -> None:
        if self.limit is not None and (type(self.limit) is not int or self.limit < 0):
            raise ValueError('The read limit must be a nonnegative integer.')
        self.reads: Counter[str] = Counter()

    def read(self) -> None:
        if self.limit is not None and self.total >= self.limit:
            raise ReadBudgetExceeded('The input-table read budget was exhausted.')
        self.reads[self.phase] += 1

    @property
    def total(self) -> int:
        return sum(self.reads.values())

class CountedRows(tuple):
    """Count consumed transition/report records, including domain checks."""
    def __new__(cls, values: Iterable, meter: Meter):
        obj = tuple.__new__(cls, values)
        obj.meter = meter
        return obj

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[i] for i in range(*index.indices(len(self))))
        self.meter.read()
        return tuple.__getitem__(self, index)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

def metered_problem(problem: Problem, meter: Meter) -> Problem:
    # Input-shape validation is shared setup, accounted separately from the
    # measured compiler calls. Disable the compiler allowance during setup.
    limit = meter.limit
    meter.limit = None
    copied = Problem(problem.n,
        tuple(Experiment(e.name, e.cost, CountedRows(e.transitions, meter))
              for e in problem.experiments), problem.repairs)
    meter.setup_reads = meter.total
    meter.reads.clear()
    meter.limit = limit
    return copied

def immutable_binary_guard(problem: Problem, meter: Meter) -> dict[int, int] | None:
    """Check unit-cost binary immutable cases and singleton repair effects."""
    meter.phase = 'guard'
    leaf_for: dict[int, int] = {}
    for i, r in enumerate(problem.repairs):
        if r.cost != 1 or len(r.good) != 1:
            return None
        x = next(iter(r.good))
        leaf_for.setdefault(x, i)
    if set(leaf_for) != set(range(problem.n)):
        return None
    for e in problem.experiments:
        if e.cost != 1:
            return None
        for x in range(problem.n):
            entry = e.transitions[x]
            if entry is None or entry[0] != x or entry[1] not in (0, 1):
                return None
    return leaf_for

def propose_tree(problem: Problem, support: tuple[int, ...], horizon: int,
                 leaves: dict[int, int], rule: str, meter: Meter,
                 stats: dict[str, int]) -> Tree | None:
    """Use only public model rows, never the next episode's hidden case."""
    if rule not in ('first', 'balanced'):
        raise ValueError('Only the two declared proposal rules are supported.')
    meter.phase = 'proposal'
    def solve(states: tuple[int, ...], depth: int) -> Tree | None:
        stats['proposal_supports'] = stats.get('proposal_supports', 0) + 1
        if len(states) == 1:
            return Tree('repair', leaves[states[0]])
        if depth == 0:
            return None
        chosen = None
        best = None
        for ei, e in enumerate(problem.experiments):
            groups = {0: [], 1: []}
            for x in states:
                item = e.transitions[x]
                if item is None:
                    raise ValueError('Guarded total experiment became partial.')
                groups[item[1]].append(x)
            if not groups[0] or not groups[1]:
                continue
            key = (max(map(len, groups.values())), ei)
            if best is None or key < best:
                best = key
                chosen = (ei, tuple(groups[0]), tuple(groups[1]))
            if rule == 'first':
                break
        if chosen is None:
            return None
        ei, left, right = chosen
        # This is a sound impossibility test for the proposed first action,
        # not a claim that no alternative action works.
        if max(len(left), len(right)) > 2 ** (depth-1):
            return None
        a = solve(left, depth-1)
        if a is None:
            return None
        b = solve(right, depth-1)
        if b is None:
            return None
        return Tree('query', ei, ((0, a), (1, b)))
    return solve(support, horizon)

def _checked_frontier(problem: Problem, support: tuple[int, ...], horizon: int,
                      meter: Meter, stats: dict) -> tuple[Witness, ...]:
    meter.phase = 'exact_search'
    front = compile_frontier(problem, support, horizon, stats)
    meter.phase = 'verification'
    for w in front:
        if check_tree(problem, support, w.tree, horizon) != (w.work, w.storage):
            raise ValueError('The baseline returned an inconsistent witness.')
    return front

def compile_measured(problem: Problem, horizon: int, rule: str | None = None,
                     support: Iterable[int] | None = None,
                     read_limit: int | None = None) -> tuple[tuple[Witness, ...], dict]:
    """Compile from fresh caches. None is the unchanged exhaustive predecessor.

    The sequential fast path may add work before fallback. No universal speedup
    or two-worker racing guarantee is claimed for this implementation.
    """
    states = tuple(sorted(set(range(problem.n) if support is None else support)))
    if not states or not set(states) <= set(range(problem.n)) or type(horizon) is not int or horizon < 0:
        raise ValueError('Invalid support or horizon.')
    meter = Meter(read_limit)
    p = metered_problem(problem, meter)
    stats: dict = {}
    mode = 'baseline'
    try:
        front = None
        if rule is not None:
            if rule not in ('first', 'balanced'):
                raise ValueError('Unknown proposal rule.')
            leaves = immutable_binary_guard(p, meter)
            if leaves is not None:
                candidate = propose_tree(p, states, horizon, leaves, rule, meter, stats)
                if candidate is not None:
                    meter.phase = 'verification'
                    w, m = check_tree(p, states, candidate, horizon)
                    lower = ((len(states)-1).bit_length()+1, 2*len(states)-1)
                    if (w, m) == lower:
                        front = (Witness(w, m, candidate),)
                        mode = 'certified_shortcut'
            if front is None:
                mode = 'fallback'
        if front is None:
            front = _checked_frontier(p, states, horizon, meter, stats)
        status = 'complete'
    except ReadBudgetExceeded:
        front = ()
        mode = 'read_budget_exhausted'
        status = 'incomplete'
    report = {'status': status, 'mode': mode, 'rule': rule,
              'table_reads': meter.total, 'phase_reads': dict(meter.reads),
              'shared_input_validation_reads': meter.setup_reads,
              'algorithm_counters': stats,
              'frontier': [[str(w.work), w.storage] for w in front],
              'read_limit': read_limit,
              'non_claim': 'Table reads are not complete CPU work; no cache crosses calls.'}
    return front, report

def tagged_problem(models: tuple[Problem, ...]) -> Problem:
    """Exact reduction for a fixed unknown member of a finite model family."""
    if not models:
        raise ValueError('A nonempty model family is required.')
    base = models[0]
    for p in models:
        if (p.n != base.n or
            [(e.name, e.cost) for e in p.experiments] != [(e.name, e.cost) for e in base.experiments] or
            [(r.name, r.cost) for r in p.repairs] != [(r.name, r.cost) for r in base.repairs]):
            raise ValueError('Models must share state names, action names, and costs.')
    experiments = []
    for ei, e in enumerate(base.experiments):
        rows = []
        for theta, p in enumerate(models):
            for item in p.experiments[ei].transitions:
                rows.append(None if item is None else (theta*base.n+item[0], item[1]))
        experiments.append(Experiment(e.name, e.cost, tuple(rows)))
    repairs = []
    for ri, r in enumerate(base.repairs):
        good = frozenset(theta*base.n+x for theta,p in enumerate(models)
                         for x in p.repairs[ri].good)
        repairs.append(Repair(r.name,r.cost,good))
    return Problem(base.n*len(models),tuple(experiments),tuple(repairs))

def orientation_family(calibration: bool) -> tuple[Problem, ...]:
    out=[]
    for theta in (0,1):
        exps=[Experiment('sense',Q(1),tuple((x,x^theta) for x in (0,1)))]
        if calibration:
            exps.append(Experiment('reference',Q(2),tuple((x,theta) for x in (0,1))))
        reps=tuple(Repair(f'repair_{x}',Q(1),frozenset((x,))) for x in (0,1))
        out.append(Problem(2,tuple(exps),reps))
    return tuple(out)

def evidence_step(capital: Q, score: Q, bet: Q, gamma: Q = Q(0)) -> Q:
    """One exact e-process update; caller must establish predictability/freshness."""
    if not (capital >= 0 and -1 <= score <= 1 and 0 <= gamma < 1 and 0 <= bet <= 1/(1+gamma)):
        raise ValueError('Invalid capital, score, target margin, or predictable bet.')
    return capital * (1 + bet*(score-gamma))
