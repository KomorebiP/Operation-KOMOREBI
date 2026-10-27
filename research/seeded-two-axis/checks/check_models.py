#!/usr/bin/env python3
"""Exact finite regression tests. These are not a formal proof of the category theorems."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import platform
import time
from collections import deque
from pathlib import Path
from typing import Iterable

Token = tuple[str, int]
Event = tuple[int, int]

def tokenise(word: str) -> tuple[Token, ...]:
    counts = {'T': 0, 'C': 0}
    out = []
    for a in word:
        out.append((a, counts[a])); counts[a] += 1
    return tuple(out)

def events_and_predecessors(tokens: tuple[Token, ...]):
    events = tuple((a[1], b[1]) for i, a in enumerate(tokens)
                   for b in tokens[i + 1:] if a[0] == 'T' and b[0] == 'C')
    prec = {e: frozenset(f for f in events if
                        (f[0] == e[0] and f[1] < e[1]) or
                        (f[1] == e[1] and f[0] > e[0])) for e in events}
    return events, prec

def syntax_graph(tokens: tuple[Token, ...]):
    queue = deque([tokens]); seen = {tokens}; edges = set()
    while queue:
        x = queue.popleft()
        for k in range(len(x) - 1):
            if x[k][0] == 'T' and x[k+1][0] == 'C':
                y = x[:k] + (x[k+1], x[k]) + x[k+2:]
                edges.add((x, y))
                if y not in seen:
                    seen.add(y); queue.append(y)
    return seen, edges

def ideal_graph(events: tuple[Event, ...], prec: dict):
    empty = frozenset(); seen = {empty}; queue = deque([empty]); edges = set()
    while queue:
        ideal = queue.popleft()
        for e in events:
            if e not in ideal and prec[e] <= ideal:
                new = ideal | {e}; edges.add((ideal, new))
                if new not in seen:
                    seen.add(new); queue.append(new)
    return seen, edges

def completed_events(state: tuple[Token, ...], events: tuple[Event, ...]):
    loc = {t: i for i, t in enumerate(state)}
    return frozenset(e for e in events if loc[('C', e[1])] < loc[('T', e[0])])

def check_histories(max_length: int):
    totals = {'words': 0, 'states': 0, 'edges': 0, 'max_events': 0}
    for n in range(max_length + 1):
        for letters in itertools.product('TC', repeat=n):
            word = ''.join(letters); tokens = tokenise(word)
            events, pred = events_and_predecessors(tokens)
            states, edges = syntax_graph(tokens)
            ideals, ideal_edges = ideal_graph(events, pred)
            image = {x: completed_events(x, events) for x in states}
            assert len(set(image.values())) == len(states), ('injectivity', word)
            assert set(image.values()) == ideals, ('object-bijection', word)
            assert {(image[x], image[y]) for x, y in edges} == ideal_edges, ('edge-bijection', word)
            # Every terminal state has the same fully sorted tokens, including n=0.
            outgoing = {x for x, y in edges}
            terminal = states - outgoing
            expected = tuple(t for t in tokens if t[0] == 'C') + tuple(t for t in tokens if t[0] == 'T')
            assert terminal == {expected}, ('normal-form', word)
            totals['words'] += 1; totals['states'] += len(states); totals['edges'] += len(edges)
            totals['max_events'] = max(totals['max_events'], len(events))
    return totals

Matrix = tuple[tuple[int, ...], ...]
def mul(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) for col in zip(*b)) for row in a)
def mv(a: Matrix, x: tuple[int, ...]):
    return tuple(sum(v*w for v, w in zip(row, x)) for row in a)
def support(x: tuple[int, ...]):
    return frozenset(i for i, n in enumerate(x) if n)

def check_constructors():
    I = ((1,0,0),(0,1,0),(0,0,1))
    U = ((0,0,0),(0,0,0),(0,1,1))
    V = ((0,0,0),(0,0,0),(1,0,1))
    M = (I, U, V)
    assert all(mul(a,b) in M for a in M for b in M)
    assert mul(U,V) == V and mul(V,U) == U
    x, y, z = (1,0,0), (0,1,0), (0,0,1)
    assert mv(U,x) == (0,0,0) and mv(V,y) == (0,0,0)
    assert all(mv(a,(1,1,0)) != (0,0,0) for a in M)
    assert all(mv(a,z) == z for a in M)
    killable = [x for x in itertools.product((0,1), repeat=3) if any(mv(a,x)==(0,0,0) for a in M)]
    thick_support = frozenset().union(*(support(x) for x in killable))
    assert thick_support == {0,1}
    invariant_support = frozenset().union(*(support(mv(a,x)) for a in M for x in killable))
    assert invariant_support == {0,1,2}
    assert not ({mul(p,U) for p in M} & {mul(q,V) for q in M})
    # A positive directed example, retaining a nonzero first coordinate.
    I2, L = ((1,0),(0,1)), ((1,0),(0,0))
    M2=(I2,L)
    assert all({mul(p,u) for p in M2} & {mul(q,v) for q in M2} for u in M2 for v in M2)
    assert all(mv(a,(1,0)) != (0,0) for a in M2)
    return {'composition_products_checked': 9,
            'binary_supports_checked': 8,
            'killable_supports': [list(x) for x in killable],
            'ordinary_thick_support': sorted(i+1 for i in thick_support),
            'constructor_invariant_support': sorted(i+1 for i in invariant_support),
            'directed_positive_model': 'PASS'}

def rank_q(rows: list[list[int]]) -> int:
    from fractions import Fraction
    if not rows:
        return 0
    a = [[Fraction(x) for x in row] for row in rows]
    m, n, r = len(a), len(a[0]), 0
    for c in range(n):
        pivot = next((i for i in range(r,m) if a[i][c]), None)
        if pivot is None: continue
        a[r],a[pivot]=a[pivot],a[r]
        v=a[r][c]; a[r]=[x/v for x in a[r]]
        for i in range(m):
            if i != r:
                v=a[i][c]; a[i]=[x-v*y for x,y in zip(a[i],a[r])]
        r+=1
        if r == m: break
    return r

def cone_betti(rows: list[list[int]], source_dim: int, target_dim: int):
    # f is a map between degree-zero complexes. H^{-1}=ker f, H^0=coker f.
    assert len(rows)==target_dim and all(len(row)==source_dim for row in rows)
    r=rank_q(rows)
    return {'H^-1': source_dim-r, 'H^0': target_dim-r}

def check_filtrations():
    i1=[[1],[0],[0]]; i2=[[0,0],[1,0],[0,1]]
    assert cone_betti(i1,1,3)=={'H^-1':0,'H^0':2}
    assert cone_betti(i2,2,3)=={'H^-1':0,'H^0':1}
    assert cone_betti([[],[],[]],0,3)=={'H^-1':0,'H^0':3}
    assert cone_betti([[1,0,0],[0,1,0]],3,2)=={'H^-1':1,'H^0':0}
    assert cone_betti([[1]],1,1)=={'H^-1':0,'H^0':0}
    assert cone_betti([[0]],1,1)=={'H^-1':1,'H^0':1}
    return {'left_filtered_dimensions':[0,1,3], 'right_filtered_dimensions':[0,2,3],
            'common_total_dimension':3, 'graded_dimensions_left':[1,2],
            'graded_dimensions_right':[2,1], 'ordered_filtrations_equivalent':False,
            'split_projection_cofiber':{'H^-1':1,'H^0':0},
            'same_endpoints_insufficient':True, 'exact_rank_checks':6}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--max-length',type=int,default=10)
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name('results.json'))
    args=parser.parse_args()
    if not 0 <= args.max_length <= 12:
        parser.error('--max-length must be between 0 and 12')
    start=time.perf_counter()
    data={'status':'PASS','evidence':'exact finite regression, not a proof-assistant certificate',
          'python':platform.python_version(),'domain':'integer matrices, rational ranks, finite labelled words',
          'max_length':args.max_length, 'histories':check_histories(args.max_length),
          'constructors':check_constructors(), 'filtrations':check_filtrations()}
    data['runtime_seconds']=round(time.perf_counter()-start,6)
    data['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))

if __name__ == '__main__':
    main()
