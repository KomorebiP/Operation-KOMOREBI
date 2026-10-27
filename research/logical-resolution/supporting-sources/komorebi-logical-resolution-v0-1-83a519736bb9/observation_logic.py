"""Finite reference semantics for the Lean observational first-order fragment.

The semantics quantifies over STATES and compares observation VALUES only.
No state-equality atom is available. Code is independently tested, not extracted
from Lean. State variables are de Bruijn indices: a quantifier prepends its witness.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Any, Iterable

@dataclass(frozen=True)
class System:
    n: int
    values: int
    steps: tuple[tuple[int, ...], ...]
    observations: tuple[tuple[int, ...], ...]
    name: str = "system"

    def __post_init__(self) -> None:
        if self.n < 0 or self.values < 1:
            raise ValueError("Nonnegative state count and positive value count required")
        for row in self.steps:
            if len(row) != self.n or any(not 0 <= x < self.n for x in row):
                raise ValueError("Invalid total transition table")
        for row in self.observations:
            if len(row) != self.n or any(not 0 <= x < self.values for x in row):
                raise ValueError("Invalid observation table")

    def behavior(self, state: int, word: tuple[int, ...], observation: int) -> int:
        if not 0 <= state < self.n or not 0 <= observation < len(self.observations):
            raise ValueError("Invalid state or observation")
        for action in word:
            if not 0 <= action < len(self.steps):
                raise ValueError("Invalid operation")
            state = self.steps[action][state]
        return self.observations[observation][state]

@dataclass(frozen=True)
class Term:
    kind: str
    args: tuple[Any, ...]

    @staticmethod
    def literal(value: int) -> Term:
        return Term("literal", (value,))

    @staticmethod
    def probe(variable: int, word: Iterable[int], observation: int) -> Term:
        return Term("probe", (variable, tuple(word), observation))

    def validate(self, system: System, arity: int) -> None:
        if self.kind == "literal":
            if len(self.args) != 1 or not 0 <= self.args[0] < system.values:
                raise ValueError("Unknown value literal")
        elif self.kind == "probe":
            i, word, j = self.args
            if not 0 <= i < arity or not 0 <= j < len(system.observations):
                raise ValueError("Out-of-scope variable or observation")
            if any(not 0 <= a < len(system.steps) for a in word):
                raise ValueError("Unknown operation")
        else:
            raise ValueError("Unknown value term")

    def eval(self, system: System, env: tuple[int, ...]) -> int:
        if self.kind == "literal":
            return self.args[0]
        i, word, j = self.args
        return system.behavior(env[i], word, j)

    @property
    def depth(self) -> int:
        return 0 if self.kind == "literal" else len(self.args[1])

@dataclass(frozen=True)
class Formula:
    kind: str
    args: tuple[Any, ...] = ()

    @staticmethod
    def equal(t: Term, u: Term) -> Formula:
        return Formula("equal", (t, u))

    @staticmethod
    def neg(f: Formula) -> Formula:
        return Formula("not", (f,))

    @staticmethod
    def conj(f: Formula, g: Formula) -> Formula:
        return Formula("and", (f, g))

    @staticmethod
    def exists(f: Formula) -> Formula:
        return Formula("exists", (f,))

    def validate(self, system: System, arity: int) -> None:
        if arity < 0:
            raise ValueError("Negative arity")
        expected = {"false": 0, "equal": 2, "not": 1, "and": 2, "exists": 1}
        if self.kind not in expected or len(self.args) != expected[self.kind]:
            raise ValueError("Malformed formula constructor")
        if self.kind == "false":
            if self.args: raise ValueError("Falsum has no arguments")
        elif self.kind == "equal":
            for t in self.args: t.validate(system, arity)
        elif self.kind in ("not", "and"):
            for f in self.args: f.validate(system, arity)
        elif self.kind == "exists":
            self.args[0].validate(system, arity + 1)
        else:
            raise ValueError("Unknown formula, including forbidden state-equality")

    @property
    def depth(self) -> int:
        if self.kind == "false": return 0
        if self.kind == "equal": return max(t.depth for t in self.args)
        return max(f.depth for f in self.args)

    @property
    def qrank(self) -> int:
        if self.kind in ("false", "equal"): return 0
        if self.kind == "exists": return 1 + self.args[0].qrank
        return max(f.qrank for f in self.args)

@lru_cache(maxsize=250000)
def holds(system: System, f: Formula, env: tuple[int, ...]) -> bool:
    """Evaluate already validated syntax; no approximation or horizon cutoff."""
    if f.kind == "false": return False
    if f.kind == "equal": return f.args[0].eval(system, env) == f.args[1].eval(system, env)
    if f.kind == "not": return not holds(system, f.args[0], env)
    if f.kind == "and": return holds(system, f.args[0], env) and holds(system, f.args[1], env)
    if f.kind == "exists":
        return any(holds(system, f.args[0], (x,) + env) for x in range(system.n))
    raise ValueError("Unknown formula")

def evaluate(system: System, f: Formula, env: tuple[int, ...]) -> bool:
    f.validate(system, len(env))
    if any(not 0 <= x < system.n for x in env):
        raise ValueError("Invalid environment")
    return holds(system, f, env)

def check_transport(source: System, target: System, encoding: tuple[int, ...], *, onto: bool) -> None:
    if (source.values, len(source.steps), len(source.observations)) != (
            target.values, len(target.steps), len(target.observations)):
        raise ValueError("Signatures/value domains differ")
    if len(encoding) != source.n or any(not 0 <= y < target.n for y in encoding):
        raise ValueError("Invalid encoding")
    if onto and set(encoding) != set(range(target.n)):
        raise ValueError("Quantified transport requires surjectivity")
    for a in range(len(source.steps)):
        for x, y in enumerate(encoding):
            if encoding[source.steps[a][x]] != target.steps[a][y]:
                raise ValueError("Transition square does not commute")
    for j in range(len(source.observations)):
        for x, y in enumerate(encoding):
            if source.observations[j][x] != target.observations[j][y]:
                raise ValueError("Observation is not preserved")

def behavioral_quotient(system: System) -> tuple[System, tuple[int, ...]]:
    """Exact finite partition refinement, with an explicit complete state interface."""
    def colors(signatures: list[Any]) -> tuple[int, ...]:
        table: dict[Any, int] = {}
        return tuple(table.setdefault(s, len(table)) for s in signatures)
    labels = colors([tuple(o[x] for o in system.observations) for x in range(system.n)])
    while True:
        updated = colors([(labels[x], tuple(labels[row[x]] for row in system.steps))
                          for x in range(system.n)])
        if updated == labels: break
        labels = updated
    n = len(set(labels))
    representatives = [labels.index(i) for i in range(n)]
    target = System(n, system.values,
                    tuple(tuple(labels[row[x]] for x in representatives) for row in system.steps),
                    tuple(tuple(row[x] for x in representatives) for row in system.observations),
                    system.name + "_quotient")
    check_transport(system, target, labels, onto=True)
    return target, labels

def distinguishing_word(system: System, x: int, y: int) -> tuple[tuple[int, ...], int] | None:
    queue = deque([(x, y, ())]); visited = {(x, y)}
    while queue:
        a, b, word = queue.popleft()
        for j, row in enumerate(system.observations):
            if row[a] != row[b]: return word, j
        for d, row in enumerate(system.steps):
            pair = row[a], row[b]
            if pair not in visited:
                visited.add(pair); queue.append((*pair, word + (d,)))
    return None

def compile_test_equality(tests: Iterable[tuple[tuple[int, ...], int]]) -> Formula:
    f = Formula.neg(Formula("false"))
    for word, j in reversed(tuple(tests)):
        f = Formula.conj(Formula.equal(Term.probe(0, word, j), Term.probe(1, word, j)), f)
    return f

def discover_defining_formula(system: System) -> tuple[Formula, tuple[tuple[tuple[int, ...], int], ...]]:
    """Finite witness search, not a learned policy and not minimum-formula search."""
    tests = []
    for x in range(system.n):
        for y in range(x):
            if any(system.behavior(x, w, j) != system.behavior(y, w, j) for w, j in tests):
                continue
            witness = distinguishing_word(system, x, y)
            if witness is not None: tests.append(witness)
    return compile_test_equality(tests), tuple(tests)
