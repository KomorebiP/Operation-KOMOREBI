"""Finite reference semantics and a locally-nameless first-order translator.

This is an audited reference implementation, not code extracted from Lean.
Source binders prepend; target bound variables are levels and binders append.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Any

Expr = tuple[Any, ...]

@dataclass(frozen=True)
class Model:
    n: int
    values: int
    actions: tuple[tuple[int, ...], ...]
    observations: tuple[tuple[int, ...], ...]
    relations: tuple[tuple[tuple[bool, ...], ...], ...]

    def __post_init__(self) -> None:
        if self.n < 0 or self.values < 0:
            raise ValueError('negative domain size')
        for row in self.actions:
            if len(row) != self.n or any(type(x) is not int or not 0 <= x < self.n for x in row):
                raise ValueError('invalid action')
        for row in self.observations:
            if len(row) != self.n or any(type(x) is not int or not 0 <= x < self.values for x in row):
                raise ValueError('invalid observation')
        for matrix in self.relations:
            if len(matrix) != self.n or any(len(row) != self.n or any(type(v) is not bool for v in row) for row in matrix):
                raise ValueError('invalid relation')

    def run(self, x: int, word: tuple[int, ...]) -> int:
        for a in word:
            x = self.actions[a][x]
        return x


def validate(f: Expr, model: Model, arity: int) -> None:
    def state(t: Expr) -> None:
        if len(t) != 2 or type(t[0]) is not int or not 0 <= t[0] < arity:
            raise ValueError('out-of-scope state variable')
        if not isinstance(t[1], tuple) or any(type(a) is not int or not 0 <= a < len(model.actions) for a in t[1]):
            raise ValueError('invalid operation word')
    def value(t: Expr) -> None:
        if t[0] == 'lit' and len(t) == 2:
            if type(t[1]) is not int or not 0 <= t[1] < model.values:
                raise ValueError('invalid value literal')
        elif t[0] == 'probe' and len(t) == 4:
            state((t[1], t[2]))
            if type(t[3]) is not int or not 0 <= t[3] < len(model.observations):
                raise ValueError('invalid observation index')
        else:
            raise ValueError('invalid value term')
    if not isinstance(f, tuple) or not f:
        raise ValueError('invalid formula')
    tag = f[0]
    if tag == 'false' and len(f) == 1:
        return
    if tag == 'eq' and len(f) == 3:
        value(f[1]); value(f[2]); return
    if tag == 'rel' and len(f) == 4:
        if type(f[1]) is not int or not 0 <= f[1] < len(model.relations):
            raise ValueError('invalid relation name')
        state(f[2]); state(f[3]); return
    if tag == 'not' and len(f) == 2:
        validate(f[1], model, arity); return
    if tag == 'and' and len(f) == 3:
        validate(f[1], model, arity); validate(f[2], model, arity); return
    if tag == 'exists' and len(f) == 2:
        validate(f[1], model, arity+1); return
    raise ValueError('unsupported formula or malformed arity')


def evaluate(model: Model, f: Expr, env: tuple[int, ...]) -> bool:
    validate(f, model, len(env))
    if any(type(x) is not int or not 0 <= x < model.n for x in env):
        raise ValueError('invalid state assignment')
    return source_eval(model, f, env)


def source_eval(m: Model, f: Expr, env: tuple[int, ...]) -> bool:
    def val(t: Expr) -> int:
        return t[1] if t[0] == 'lit' else m.observations[t[3]][m.run(env[t[1]], t[2])]
    tag = f[0]
    if tag == 'false': return False
    if tag == 'eq': return val(f[1]) == val(f[2])
    if tag == 'rel': return m.relations[f[1]][m.run(env[f[2][0]], f[2][1])][m.run(env[f[3][0]], f[3][1])]
    if tag == 'not': return not source_eval(m, f[1], env)
    if tag == 'and': return source_eval(m, f[1], env) and source_eval(m, f[2], env)
    if tag == 'exists': return any(source_eval(m, f[1], (x,)+env) for x in range(m.n))
    raise ValueError('unknown formula')


def translate(f: Expr, arity: int) -> Expr:
    """Translate a validated formula to rel/imp/all and unary function terms."""
    def convert(f: Expr, sigma: tuple[Expr, ...], bound_count: int) -> Expr:
        def term(st: Expr) -> Expr:
            t = sigma[st[0]]
            for a in st[1]: t = ('func', a, t)
            return t
        def equal(a: Expr, b: Expr) -> Expr:
            if a[0] == 'lit' and b[0] == 'lit':
                return ('relation', ('literals', a[1], b[1]), ())
            if a[0] == 'lit': a,b = b,a
            if b[0] == 'lit':
                return ('relation', ('valueIs', a[3], b[1]), (term((a[1], a[2])),))
            return ('relation', ('agree', a[3], b[3]), (term((a[1],a[2])), term((b[1],b[2]))))
        tag = f[0]
        if tag == 'false': return ('false',)
        if tag == 'eq': return equal(f[1],f[2])
        if tag == 'rel': return ('relation', ('link',f[1]), (term(f[2]),term(f[3])))
        if tag == 'not': return ('imp',convert(f[1],sigma,bound_count),('false',))
        if tag == 'and':
            return ('imp', ('imp',convert(f[1],sigma,bound_count),
                            ('imp',convert(f[2],sigma,bound_count),('false',))), ('false',))
        if tag == 'exists':
            body=convert(f[1],(('bound',bound_count),)+sigma,bound_count+1)
            return ('imp',('all',('imp',body,('false',))),('false',))
        raise ValueError('unsupported source formula')
    return convert(f,tuple(('free',i) for i in range(arity)),0)


def target_eval(m: Model, f: Expr, free: tuple[int, ...], bound: tuple[int, ...] = ()) -> bool:
    """Separate standard-style evaluator. It has no source-expression evaluator call."""
    def term(t: Expr) -> int:
        if t[0] == 'free': return free[t[1]]
        if t[0] == 'bound': return bound[t[1]]
        if t[0] == 'func': return m.actions[t[1]][term(t[2])]
        raise ValueError('invalid target term')
    tag=f[0]
    if tag == 'false': return False
    if tag == 'imp': return not target_eval(m,f[1],free,bound) or target_eval(m,f[2],free,bound)
    if tag == 'all': return all(target_eval(m,f[1],free,bound+(x,)) for x in range(m.n))
    if tag == 'equality': return term(f[1]) == term(f[2])
    if tag == 'relation':
        sym=f[1]; args=tuple(term(t) for t in f[2])
        if sym[0] == 'literals': return sym[1] == sym[2]
        if sym[0] == 'valueIs': return m.observations[sym[1]][args[0]] == sym[2]
        if sym[0] == 'agree': return m.observations[sym[1]][args[0]] == m.observations[sym[2]][args[1]]
        if sym[0] == 'link': return m.relations[sym[1]][args[0]][args[1]]
    raise ValueError('invalid target formula')


def source_rank(f: Expr) -> int:
    if f[0] in ('false','eq','rel'): return 0
    if f[0]=='not': return source_rank(f[1])
    if f[0]=='and': return max(source_rank(f[1]),source_rank(f[2]))
    if f[0]=='exists': return source_rank(f[1])+1
    raise ValueError('invalid source')


def target_rank(f: Expr) -> int:
    if f[0] in ('false','relation','equality'): return 0
    if f[0]=='imp': return max(target_rank(f[1]),target_rank(f[2]))
    if f[0]=='all': return target_rank(f[1])+1
    raise ValueError('invalid target')


def certify_transport(s: Model,t: Model,q: tuple[int,...], *, quantified: bool=True) -> None:
    if len(q)!=s.n or any(not 0<=x<t.n for x in q): raise ValueError('invalid encoder')
    if s.values!=t.values or len(s.actions)!=len(t.actions) or len(s.observations)!=len(t.observations) or len(s.relations)!=len(t.relations):
        raise ValueError('signature mismatch')
    if quantified and set(q)!=set(range(t.n)): raise ValueError('not surjective')
    for a in range(len(s.actions)):
        for x in range(s.n):
            if q[s.actions[a][x]] != t.actions[a][q[x]]: raise ValueError('action mismatch')
    for j in range(len(s.observations)):
        for x in range(s.n):
            if s.observations[j][x]!=t.observations[j][q[x]]: raise ValueError('observation mismatch')
    for k in range(len(s.relations)):
        for x,y in product(range(s.n),repeat=2):
            if s.relations[k][x][y]!=t.relations[k][q[x]][q[y]]:
                raise ValueError('relation does not reflect on fibers')


def identity_atomic(m: Model, env: tuple[int,...]) -> tuple:
    """Exact atomic diagram of our fragment when all operations are identity."""
    if any(row!=tuple(range(m.n)) for row in m.actions):
        raise ValueError('this finite back-and-forth audit requires identity dynamics')
    return (tuple(row[x] for row in m.observations for x in env),
            tuple(matrix[x][y] for matrix in m.relations for x in env for y in env))


@lru_cache(maxsize=None)
def identity_backforth(s: Model,t: Model,q: int,env: tuple[int,...],tau: tuple[int,...]) -> bool:
    if identity_atomic(s,env)!=identity_atomic(t,tau): return False
    if q==0:return True
    return (all(any(identity_backforth(s,t,q-1,(x,)+env,(y,)+tau) for y in range(t.n)) for x in range(s.n))
        and all(any(identity_backforth(s,t,q-1,(x,)+env,(y,)+tau) for x in range(s.n)) for y in range(t.n)))
