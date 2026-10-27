"""A finite reference for the Lean/Mathlib guarded compilation contract.

The target evaluator uses only first-order primitives: falsum, equality, a state
predicate, implication, and universal quantification. Bound variables use levels
(new binders append), unlike the source fragment (newest variable is index zero).
This program is tested, not extracted from or executable-verified by Lean.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from observational_logic import FiniteSystem, Formula, normalize, code_formula

Term = tuple[Any, ...]
Target = tuple[Any, ...]
Tagged = tuple[str, int]
BOT: Target = ('false',)
TOP: Target = ('imp', BOT, BOT)


def neg(f: Target) -> Target:
    return ('imp', f, BOT)


def conj(f: Target, g: Target) -> Target:
    return neg(('imp', f, neg(g)))


def exists(f: Target) -> Target:
    return neg(('all', neg(f)))


@dataclass(frozen=True)
class TaggedModel:
    transitions: tuple[tuple[int, ...], ...]
    observations: tuple[tuple[int, ...], ...]
    state_size: int
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.state_size < 0 or len(set(self.values)) != len(self.values):
            raise ValueError('Invalid state size or repeated value tags.')
        if any(len(row) != self.state_size for row in self.transitions + self.observations):
            raise ValueError('All rows must cover the state sort exactly.')
        if any(not 0 <= x < self.state_size for row in self.transitions for x in row):
            raise ValueError('Invalid state transition.')
        if any(x not in self.values for row in self.observations for x in row):
            raise ValueError('Observed value absent from the specified value sort.')

    @classmethod
    def from_system(cls, s: FiniteSystem, values: tuple[int, ...]) -> TaggedModel:
        return cls(s.transitions, s.observations, s.size, values)

    def universe(self) -> tuple[Tagged, ...]:
        return tuple(('state', x) for x in range(self.state_size)) + tuple(('value', c) for c in self.values)


def observed_term(t: tuple[int, tuple[int, ...]], j: int, mapping: tuple[Term, ...]) -> Term:
    if not isinstance(t, tuple) or len(t) != 2 or not isinstance(t[0], int) or not 0 <= t[0] < len(mapping):
        raise ValueError('Unbound or malformed source state term.')
    if not isinstance(t[1], tuple) or any(not isinstance(a, int) or a < 0 for a in t[1]):
        raise ValueError('Operation word must be a tuple of nonnegative symbol indices.')
    if not isinstance(j, int) or j < 0:
        raise ValueError('Invalid observation symbol.')
    out = mapping[t[0]]
    for a in t[1]:
        out = ('action', a, out)
    return ('observe', j, out)


def translate_aux(f: Formula, mapping: tuple[Term, ...], depth: int) -> Target:
    match f:
        case ('true',):
            return TOP
        case ('test', t, j, c):
            return ('eq', observed_term(t, j, mapping), ('constant', c))
        case ('compare', t, j, s, k):
            return ('eq', observed_term(t, j, mapping), observed_term(s, k, mapping))
        case ('not', g):
            return neg(translate_aux(g, mapping, depth))
        case ('and', g, h):
            return conj(translate_aux(g, mapping, depth), translate_aux(h, mapping, depth))
        case ('exists', g):
            new = ('bound', depth)
            return exists(conj(('state', new), translate_aux(g, (new,) + mapping, depth + 1)))
        case _:
            raise ValueError('Formula is outside the specified observational source grammar.')


def translate(f: Formula, free_variables: int) -> Target:
    if not isinstance(free_variables, int) or free_variables < 0:
        raise ValueError('Expected a nonnegative free-variable count.')
    return translate_aux(f, tuple(('free', i) for i in range(free_variables)), 0)


def path_to_fo(f: Formula) -> Formula:
    match f:
        case ('true',): return f
        case ('atom', word, j, c): return ('test', (0, word), j, c)
        case ('not', g): return ('not', path_to_fo(g))
        case ('and', g, h): return ('and', path_to_fo(g), path_to_fo(h))
        case _: raise ValueError('Invalid path-normal source.')


def compile_source(f: Formula) -> Target:
    return translate(path_to_fo(normalize(f)), 1)


def guarded_code(tests: list[tuple[tuple[int, ...], int]]) -> Target:
    return conj(conj(('state', ('free', 0)), ('state', ('free', 1))), translate(code_formula(tests), 2))


def eval_term(m: TaggedModel, t: Term, free: tuple[Tagged, ...], bound: tuple[Tagged, ...]) -> Tagged:
    match t:
        case ('free', i):
            if not isinstance(i, int) or not 0 <= i < len(free): raise ValueError('Unbound free variable.')
            return free[i]
        case ('bound', i):
            if not isinstance(i, int) or not 0 <= i < len(bound): raise ValueError('Unbound bound level.')
            return bound[i]
        case ('constant', c):
            if c not in m.values: raise ValueError('Value name absent from signature.')
            return ('value', c)
        case ('action', a, s):
            if not isinstance(a, int) or not 0 <= a < len(m.transitions): raise ValueError('Unknown action.')
            tag, x = eval_term(m, s, free, bound)
            return ('state', m.transitions[a][x]) if tag == 'state' else (tag, x)
        case ('observe', j, s):
            if not isinstance(j, int) or not 0 <= j < len(m.observations): raise ValueError('Unknown observation.')
            tag, x = eval_term(m, s, free, bound)
            return ('value', m.observations[j][x]) if tag == 'state' else (tag, x)
        case _: raise ValueError('Invalid target term.')


def eval_formula(m: TaggedModel, f: Target, free: tuple[Tagged, ...],
                 bound: tuple[Tagged, ...] = ()) -> bool:
    match f:
        case ('false',): return False
        case ('eq', t, s): return eval_term(m, t, free, bound) == eval_term(m, s, free, bound)
        case ('state', t): return eval_term(m, t, free, bound)[0] == 'state'
        case ('imp', g, h): return not eval_formula(m, g, free, bound) or eval_formula(m, h, free, bound)
        case ('all', g): return all(eval_formula(m, g, free, bound + (x,)) for x in m.universe())
        case _: raise ValueError('Invalid primitive target formula.')


def target_rank(f: Target) -> int:
    match f:
        case ('false',) | ('eq', _, _) | ('state', _): return 0
        case ('imp', g, h): return max(target_rank(g), target_rank(h))
        case ('all', g): return target_rank(g) + 1
        case _: raise ValueError('Invalid target formula.')
