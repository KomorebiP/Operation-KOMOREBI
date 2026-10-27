"""Exact reference implementation for the normalized observational fragment.

Source syntax: ('true',), ('test', observation, value), ('not', f),
('and', f, g), ('after', action, f).
Path-normal syntax replaces tests and after-nodes with ('atom', word, j, value).
FO syntax adds ('compare', term, j, term, k) and ('exists', body); a term is
(variable_index, operation_word). It deliberately omits state equality.

This Python module is tested against the formal contract. It is not extracted
from Lean and is not itself a formally verified executable.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable

Formula = tuple[Any, ...]
Word = tuple[int, ...]
Test = tuple[Word, int]

@dataclass(frozen=True)
class FiniteSystem:
    transitions: tuple[tuple[int, ...], ...]
    observations: tuple[tuple[int, ...], ...]
    size: int

    def __post_init__(self) -> None:
        if not isinstance(self.size, int) or self.size < 1:
            raise ValueError('The executable requires a nonempty finite state set.')
        if any(len(row) != self.size for row in self.transitions + self.observations):
            raise ValueError('Every table row must cover exactly the source state set.')
        if any(not isinstance(y,int) or not 0 <= y < self.size
               for row in self.transitions for y in row):
            raise ValueError('Transition target outside the state set.')
        if any(not isinstance(v,int) for row in self.observations for v in row):
            raise ValueError('Reference executable observation values must be integers.')

    def run(self, x: int, word: Word) -> int:
        if not 0 <= x < self.size:
            raise ValueError('Invalid initial state.')
        for a in word:
            if not isinstance(a,int) or not 0 <= a < len(self.transitions):
                raise ValueError('Unknown action symbol.')
            x = self.transitions[a][x]
        return x

    def observe(self, x: int, word: Word, j: int) -> int:
        if not isinstance(j,int) or not 0 <= j < len(self.observations):
            raise ValueError('Unknown observation symbol.')
        return self.observations[j][self.run(x, word)]


def prefix(word: Word, f: Formula) -> Formula:
    match f:
        case ('true',): return f
        case ('atom', w, j, c): return ('atom', word + w, j, c)
        case ('not', g): return ('not', prefix(word,g))
        case ('and', g, h): return ('and', prefix(word,g), prefix(word,h))
        case _: raise ValueError('Invalid path-normal formula.')


def normalize(f: Formula) -> Formula:
    match f:
        case ('true',): return f
        case ('test', j, c): return ('atom', (), j, c)
        case ('not', g): return ('not', normalize(g))
        case ('and', g, h): return ('and', normalize(g), normalize(h))
        case ('after', a, g): return prefix((a,), normalize(g))
        case _: raise ValueError('Invalid source observation formula.')


def embed(f: Formula) -> Formula:
    match f:
        case ('true',): return f
        case ('atom', w, j, c):
            out = ('test', j, c)
            for a in reversed(w): out = ('after', a, out)
            return out
        case ('not', g): return ('not', embed(g))
        case ('and', g, h): return ('and', embed(g), embed(h))
        case _: raise ValueError('Invalid path-normal formula.')


def source_sat(s: FiniteSystem, f: Formula, x: int) -> bool:
    match f:
        case ('true',): return True
        case ('test', j, c): return s.observe(x, (), j) == c
        case ('not', g): return not source_sat(s,g,x)
        case ('and', g, h): return source_sat(s,g,x) and source_sat(s,h,x)
        case ('after', a, g): return source_sat(s,g,s.run(x,(a,)))
        case _: raise ValueError('Invalid source formula.')


def path_sat(s: FiniteSystem, f: Formula, x: int) -> bool:
    match f:
        case ('true',): return True
        case ('atom', w, j, c): return s.observe(x,w,j) == c
        case ('not', g): return not path_sat(s,g,x)
        case ('and', g, h): return path_sat(s,g,x) and path_sat(s,h,x)
        case _: raise ValueError('Invalid path-normal formula.')


def horizon(f: Formula) -> int:
    match f:
        case ('true',): return 0
        case ('atom', w, _, _): return len(w)
        case ('not', g): return horizon(g)
        case ('and', g, h): return max(horizon(g),horizon(h))
        case _: raise ValueError('Invalid path-normal formula.')


def fo_sat(s: FiniteSystem, f: Formula, env: tuple[int, ...]) -> bool:
    def obs(t: tuple[int, Word], j: int) -> int:
        if not 0 <= t[0] < len(env): raise ValueError('Unbound state variable.')
        return s.observe(env[t[0]], t[1], j)
    match f:
        case ('true',): return True
        case ('test', t, j, c): return obs(t,j) == c
        case ('compare', t, j, u, k): return obs(t,j) == obs(u,k)
        case ('not', g): return not fo_sat(s,g,env)
        case ('and', g, h): return fo_sat(s,g,env) and fo_sat(s,h,env)
        case ('exists', g): return any(fo_sat(s,g,(x,)+env) for x in range(s.size))
        case _: raise ValueError('Not in the specified observational first-order fragment.')


def fo_quantifier_rank(f: Formula) -> int:
    match f:
        case ('true',) | ('test', _, _, _) | ('compare', _, _, _, _): return 0
        case ('not', g): return fo_quantifier_rank(g)
        case ('and', g, h): return max(fo_quantifier_rank(g),fo_quantifier_rank(h))
        case ('exists', g): return fo_quantifier_rank(g)+1
        case _: raise ValueError('Invalid FO formula.')


def fo_term_horizon(f: Formula) -> int:
    match f:
        case ('true',): return 0
        case ('test', t, _, _): return len(t[1])
        case ('compare', t, _, u, _): return max(len(t[1]),len(u[1]))
        case ('not', g) | ('exists', g): return fo_term_horizon(g)
        case ('and', g, h): return max(fo_term_horizon(g),fo_term_horizon(h))
        case _: raise ValueError('Invalid FO formula.')


def relabel(keys: Iterable[Any]) -> tuple[int,...]:
    ids: dict[Any,int] = {}
    return tuple(ids.setdefault(k,len(ids)) for k in keys)


def behavioral_quotient(s: FiniteSystem) -> tuple[FiniteSystem, tuple[int,...], int]:
    """Complete finite partition refinement; returns quotient, encoding, horizon."""
    classes = relabel(tuple(row[x] for row in s.observations) for x in range(s.size))
    h=0
    while True:
        new = relabel((classes[x],tuple(classes[row[x]] for row in s.transitions))
                      for x in range(s.size))
        if new == classes: break
        classes=new;h+=1
        if h >= s.size: raise AssertionError('Finite refinement exceeded its bound.')
    count=max(classes)+1
    reps=[classes.index(i) for i in range(count)]
    q=FiniteSystem(tuple(tuple(classes[row[x]] for x in reps) for row in s.transitions),
                   tuple(tuple(row[x] for x in reps) for row in s.observations),count)
    return q,classes,h


def words_through(alphabet: int, h: int, cap: int = 100_000) -> list[Word]:
    if alphabet < 0 or h < 0: raise ValueError('Negative word bounds.')
    total=sum(alphabet**i for i in range(h+1))
    if total>cap: raise RuntimeError('Word family exceeds resource cap; unresolved.')
    return [tuple(w) for i in range(h+1) for w in product(range(alphabet),repeat=i)]


def code_formula(tests: list[Test]) -> Formula:
    out=('true',)
    for w,j in reversed(tests):
        out=('and',('compare',(0,w),j,(1,w),j),out)
    return out


def check_finite_code(s: FiniteSystem, tests: list[Test]) -> bool:
    """Checks precisely the local outputs/steps contract, not a sampled horizon."""
    codes=[tuple(s.observe(x,w,j) for w,j in tests) for x in range(s.size)]
    for x,y in product(range(s.size),repeat=2):
        if codes[x] != codes[y]: continue
        if any(row[x] != row[y] for row in s.observations): return False
        if any(codes[row[x]] != codes[row[y]] for row in s.transitions): return False
    return True
