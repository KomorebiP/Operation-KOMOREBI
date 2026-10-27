"""Finite support games used by the written control-transport results.

States are integer addresses. A catalogue contains successor sets for the
common action addresses; None means disabled. Empty admitted successor sets
are rejected. These algorithms are reference implementations, not Lean proofs.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

Row = tuple[Optional[frozenset[int]], ...]

@dataclass(frozen=True)
class Game:
    n: int
    safe: frozenset[int]
    goal: frozenset[int]
    running: tuple[Row, ...]
    ending: tuple[Row, ...]

    def __post_init__(self) -> None:
        if type(self.n) is not int or self.n < 1:
            raise ValueError("n must be a positive integer")
        states = frozenset(range(self.n))
        if not self.goal <= self.safe <= states:
            raise ValueError("goal must be contained in safe, and safe in the state space")
        for cat in (self.running, self.ending):
            if len(cat) != self.n or len({len(row) for row in cat}) != 1:
                raise ValueError("catalogue shape does not match the state/action spaces")
            for row in cat:
                for post in row:
                    if post is not None and (not post or not post <= states):
                        raise ValueError("enabled successor sets must be nonempty and in range")

def pre(cat: tuple[Row, ...], target: frozenset[int]) -> frozenset[int]:
    return frozenset(x for x, row in enumerate(cat)
                     if any(post is not None and post <= target for post in row))

def regions(g: Game) -> tuple[list[frozenset[int]], list[frozenset[int]], dict[int, int]]:
    t = [g.goal]
    while True:
        nxt = t[-1] | (g.safe & pre(g.ending, t[-1]))
        if nxt == t[-1]:
            break
        t.append(nxt)
    rank = {x: next(k for k, level in enumerate(t) if x in level) for x in t[-1]}
    l = [t[-1]]
    while True:
        nxt = l[-1] & pre(g.running, l[-1])
        if nxt == l[-1]:
            break
        l.append(nxt)
    if len(t) > g.n + 1 or len(l) > g.n + 1:
        raise AssertionError("a finite monotone sequence exceeded its cardinality bound")
    return t, l, rank

def pull(pi: tuple[int, ...], subset: frozenset[int]) -> frozenset[int]:
    return frozenset(x for x, z in enumerate(pi) if z in subset)

def image(pi: tuple[int, ...], subset: frozenset[int]) -> frozenset[int]:
    return frozenset(pi[x] for x in subset)

def all_subsets(n: int):
    for mask in range(1 << n):
        yield frozenset(i for i in range(n) if mask & (1 << i))

def exact_quotient(g: Game, pi: tuple[int, ...]) -> Game | None:
    if len(pi) != g.n or any(type(i) is not int or i < 0 for i in pi):
        raise ValueError("invalid quotient map")
    m = 1 + max(pi)
    if set(pi) != set(range(m)):
        raise ValueError("quotient addresses must be surjective and contiguous")
    representatives = [pi.index(z) for z in range(m)]
    for subset in (g.safe, g.goal):
        if pull(pi, image(pi, subset)) != subset:
            return None
    cats = []
    for cat in (g.running, g.ending):
        mapped = tuple(tuple(None if p is None else image(pi, p) for p in row) for row in cat)
        if any(mapped[x] != mapped[representatives[pi[x]]] for x in range(g.n)):
            return None
        cats.append(tuple(mapped[x] for x in representatives))
    return Game(m, image(pi, g.safe), image(pi, g.goal), cats[0], cats[1])
