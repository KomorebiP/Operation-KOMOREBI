"""Bounded exact reference code for the accountability chapter.

No live agents, external systems, or real credentials are controlled here.
The caller supplies mathematical laws and implemented-action assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Sequence

from finite_contract import KnowledgeGame, check_certificate

Q = Fraction


def rational(value: int | Fraction, name: str) -> Fraction:
    """Reject floats so exact inputs cannot silently become binary fractions."""
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError(f'{name} must be an integer or fractions.Fraction.')
    return Q(value)


def privacy_envelope(factor: int | Fraction, cap: int | Fraction) -> Fraction:
    k, a = rational(factor, 'factor'), rational(cap, 'cap')
    if k < 1 or not 0 <= a <= 1:
        raise ValueError('Require factor >= 1 and 0 <= cap <= 1.')
    return min((k - 1) * a, (k - 1) / (k + 1))


def privacy_attainment(factor: int | Fraction, cap: int | Fraction
                       ) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...], tuple[Fraction, ...]]:
    privacy_envelope(factor, cap)  # Validate the whole input contract.
    k, a = Q(factor), Q(cap)
    return ((k / (k + 1), 1 / (k + 1)),
            (1 / (k + 1), k / (k + 1)),
            (Q(0), min((k + 1) * a, Q(1))))


def inspection_equilibrium(gain: int | Fraction, penalty: int | Fraction,
                          cost: int | Fraction, reward: int | Fraction
                          ) -> tuple[Fraction, Fraction]:
    g, f = rational(gain, 'gain'), rational(penalty, 'penalty')
    c, b = rational(cost, 'cost'), rational(reward, 'reward')
    if not 0 < g < f or not 0 < c < b:
        raise ValueError('This routine implements only 0 < gain < penalty and 0 < cost < reward.')
    return c / b, g / f


def _validate_appeals(windows: Sequence[tuple[int, int]], capacity: Sequence[int]) -> None:
    if any(type(c) is not int or c < 0 for c in capacity):
        raise ValueError('Capacity entries must be nonnegative integers.')
    t = len(capacity)
    for window in windows:
        if len(window) != 2 or any(type(x) is not int for x in window):
            raise ValueError('Every window must contain two integer endpoints.')
        r, d = window
        if not 1 <= r <= d <= t:
            raise ValueError('Each evidence-ready window must lie in epochs 1 through T.')


def appeal_obstruction(windows: Sequence[tuple[int, int]], capacity: Sequence[int]
                      ) -> tuple[int, int, int, int] | None:
    """Return a deficient interval (start, end, demand, capacity), or None."""
    _validate_appeals(windows, capacity)
    for a in range(1, len(capacity) + 1):
        supply = 0
        for b in range(a, len(capacity) + 1):
            supply += capacity[b - 1]
            demand = sum(r >= a and d <= b for r, d in windows)
            if demand > supply:
                return a, b, demand, supply
    return None


def assign_appeals(windows: Sequence[tuple[int, int]], capacity: Sequence[int]
                  ) -> dict[int, tuple[int, int]] | None:
    """Construct a matching, independently of the interval inequality routine.

    Keys are zero-indexed appeal IDs. Values are (one-indexed epoch, slot ID).
    Empty workloads return {}, while infeasible workloads return None.
    """
    _validate_appeals(windows, capacity)
    slots = [(t + 1, k) for t, count in enumerate(capacity) for k in range(count)]
    edges = [[s for s, (t, _) in enumerate(slots) if r <= t <= d] for r, d in windows]
    occupied: dict[int, int] = {}

    def augment(j: int, visited: set[int]) -> bool:
        for s in edges[j]:
            if s in visited:
                continue
            visited.add(s)
            if s not in occupied or augment(occupied[s], visited):
                occupied[s] = j
                return True
        return False

    for j in range(len(windows)):
        if not augment(j, set()):
            return None
    return {j: slots[s] for s, j in occupied.items()}


@dataclass(frozen=True)
class StoppingResult:
    ending_ranks: Mapping[int, int]
    ending_policy: Mapping[int, int]
    running_kernel: frozenset[int]
    running_policy: Mapping[int, int]


def restrict_actions(game: KnowledgeGame, allowed: Mapping[int, frozenset[int]]) -> KnowledgeGame:
    if set(allowed) != set(game.beliefs):
        raise ValueError('The restriction must specify every public possibility set.')
    for b, actions in allowed.items():
        if not actions <= game.actions[b]:
            raise ValueError(f'{b}: restricted profile is not jointly admissible.')
    return KnowledgeGame(game.model, game.beliefs, dict(allowed),
                         {(b, a): game.successors[b, a] for b in game.beliefs for a in allowed[b]})


def stoppable_kernel(game: KnowledgeGame, running: Mapping[int, frozenset[int]],
                     ending: Mapping[int, frozenset[int]], goal: int) -> StoppingResult:
    """Compute the ending attractor, then preserve it during continued operation.

    Ending commands must be authenticated and observable before profile choice.
    This code checks no real command source. All successors are sure possibilities.
    """
    rg, eg = restrict_actions(game, running), restrict_actions(game, ending)
    if type(goal) is not int or goal < 0 or goal & ~game.model.safe:
        raise ValueError('The ending target must be a valid subset of the safe states.')
    safe = frozenset(b for b in game.beliefs if not b & ~game.model.safe)
    targets = frozenset(b for b in safe if not b & ~goal)
    ranks = {b: 0 for b in targets}
    ep: dict[int, int] = {}
    for b in targets:
        hold = [a for a in eg.actions[b] if eg.successors[b, a] <= targets]
        if not hold:
            raise ValueError('Every certified target must have an ending-mode safe hold.')
        ep[b] = min(hold)
    k = 0
    while True:
        prior = frozenset(ranks)
        added = {b: min(opts) for b in safe - prior
                 if (opts := [a for a in eg.actions[b] if eg.successors[b, a] <= prior])}
        if not added:
            break
        k += 1
        for b, a in added.items():
            ranks[b], ep[b] = k, a
    current = frozenset(ranks)
    while True:
        nxt = frozenset(b for b in current if any(
            rg.successors[b, a] <= current for a in rg.actions[b]))
        if nxt == current:
            break
        current = nxt
    rp = {b: min(a for a in rg.actions[b] if rg.successors[b, a] <= current) for b in current}
    return StoppingResult(ranks, ep, current, rp)


def check_stopping_certificate(game: KnowledgeGame, running: Mapping[int, frozenset[int]],
                               ending: Mapping[int, frozenset[int]], initial: int,
                               run_policy: Mapping[int, int], end_policy: Mapping[int, int],
                               end_ranks: Mapping[int, int], goal: int
                               ) -> tuple[bool, tuple[str, ...]]:
    rg, eg = restrict_actions(game, running), restrict_actions(game, ending)
    okay_run, erun = check_certificate(rg, initial, run_policy)
    okay_end, eend = check_certificate(eg, initial, end_policy, end_ranks, goal)
    errors = list(erun + eend)
    if not set(run_policy) <= set(end_policy):
        errors.append('A running state has no certified ending policy.')
    return okay_run and okay_end and not errors, tuple(errors)
