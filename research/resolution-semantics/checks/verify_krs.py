#!/usr/bin/env python3
"""Exact checks for Komorebi Resolution Semantics v0.1.0.

No external dependencies. Polynomial certificates are checked in the free
Boolean ring. Finite graph/partition checks have explicit bounds and do not
claim to simulate a model of ZFC. Run from the release root:
    python checks/verify_krs.py
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations, product, permutations
from pathlib import Path
from time import perf_counter
import hashlib
import json
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class ANF:
    """Squarefree monomials represented by bit masks, coefficients in F_2."""
    terms: frozenset[int]
    def __add__(self, other: 'ANF') -> 'ANF':
        return ANF(self.terms ^ other.terms)
    def __mul__(self, other: 'ANF') -> 'ANF':
        out: set[int] = set()
        for a in self.terms:
            for b in other.terms:
                m = a | b
                if m in out:
                    out.remove(m)
                else:
                    out.add(m)
        return ANF(frozenset(out))
    def evaluate(self, assignment: int) -> int:
        out = 0
        for mask in self.terms:
            out ^= int((assignment & mask) == mask)
        return out

ZERO = ANF(frozenset())
ONE = ANF(frozenset({0}))
def x(i: int) -> ANF:
    return ANF(frozenset({1 << i}))
def mul(xs: list[ANF]) -> ANF:
    out = ONE
    for a in xs:
        out = out * a
    return out

def polynomial_checks() -> dict:
    records = []
    # Independent Boolean evaluation verifies multiplication on every monomial
    # pair in four variables. Bilinearity extends this primitive check.
    for m1,m2,bits in product(range(16), repeat=3):
        p1=ANF(frozenset({m1})); p2=ANF(frozenset({m2}))
        assert (p1*p2).evaluate(bits) == (int((bits&m1)==m1) & int((bits&m2)==m2))
    def check(name: str, lhs: ANF, rhs: ANF, n: int) -> None:
        normal = lhs + rhs
        assert normal == ZERO, (name, normal)
        for bits in range(1 << n):
            assert lhs.evaluate(bits) == rhs.evaluate(bits), (name, bits)
        records.append({'identity': name, 'variables': n,
                        'normal_form': sorted(normal.terms),
                        'truth_assignments_cross_checked': 1 << n})
    a,b,c,d = [x(i) for i in range(4)]
    check('defect_additivity', (a+b)+(c+d), (a+c)+(b+d), 4)
    check('twisted_Leibniz', a*b+c*d, (a+c)*b+c*(b+d), 4)
    check('composition_cancellation', a+c, (a+b)+(b+c), 3)
    check('negation_invariance', (ONE+a)+(ONE+b), a+b, 2)
    check('reconstruction', a+(a+b), b, 2)
    check('three_cycle_telescope', (a+b)+(b+c)+(c+a), ZERO, 3)
    for n in range(1,7):
        u = [x(i) for i in range(n)]
        v = [x(n+i) for i in range(n)]
        rhs = ZERO
        for k in range(n):
            rhs = rhs + mul(v[:k])*(u[k]+v[k])*mul(u[k+1:])
        check(f'product_telescope_{n}', mul(u)+mul(v), rhs, 2*n)
    return {'status':'PASS', 'identities':records,
            'scope':'Exact free-Boolean-ring normal forms for the listed polynomial identities. '
                    'The arbitrary-length product identity also has an induction proof in the note.'}

def graph_components(n: int, edges: list[tuple[int,int]]) -> list[list[int]]:
    adj = [[] for _ in range(n)]
    for u,v in edges:
        adj[u].append(v); adj[v].append(u)
    seen = set(); out = []
    for root in range(n):
        if root in seen: continue
        seen.add(root); q=deque([root]); comp=[]
        while q:
            u=q.popleft(); comp.append(u)
            for v in adj[u]:
                if v not in seen: seen.add(v); q.append(v)
        out.append(comp)
    return out

def gradient(a: int, edges: list[tuple[int,int]]) -> int:
    return sum(( ((a>>u)&1)^((a>>v)&1) ) << j for j,(u,v) in enumerate(edges))

def integrate(n: int, edges: list[tuple[int,int]], r: int) -> tuple[bool,int]:
    adj = [[] for _ in range(n)]
    for j,(u,v) in enumerate(edges):
        adj[u].append((v,j)); adj[v].append((u,j))
    values = [-1]*n
    for root in range(n):
        if values[root] != -1: continue
        values[root]=0; q=deque([root])
        while q:
            u=q.popleft()
            for v,j in adj[u]:
                want=values[u]^((r>>j)&1)
                if values[v] == -1:
                    values[v]=want; q.append(v)
                elif values[v] != want:
                    return False,0
    return True,sum(b<<i for i,b in enumerate(values))

def rank_f2(columns: list[int]) -> int:
    basis: dict[int,int] = {}
    for c in columns:
        while c:
            pivot=c.bit_length()-1
            if pivot in basis: c ^= basis[pivot]
            else: basis[pivot]=c; break
    return len(basis)

def graph_checks() -> dict:
    count=labelings=residuals=0
    by_n=[]
    for n in range(1,6):
        possible=list(combinations(range(n),2)); nc=nr=nl=0
        for gm in range(1<<len(possible)):
            edges=[e for j,e in enumerate(possible) if (gm>>j)&1]
            comps=graph_components(n,edges); c=len(comps)
            fibers: dict[int,int]={}
            for a in range(1<<n):
                d=gradient(a,edges); fibers[d]=fibers.get(d,0)+1
                for comp in comps:
                    mixed = len({(a>>v)&1 for v in comp})>1
                    boundary = any(((d>>j)&1) for j,(u,v) in enumerate(edges) if u in comp)
                    assert mixed == boundary
                nl+=1
            assert len(fibers)==1<<(n-c)
            assert set(fibers.values())=={1<<c}
            columns=[gradient(1<<v,edges) for v in range(n)]
            assert rank_f2(columns)==n-c
            for r in range(1<<len(edges)):
                ok,a=integrate(n,edges,r)
                assert ok == (r in fibers)
                if ok: assert gradient(a,edges)==r
                nr+=1
            nc+=1
        count+=nc; residuals+=nr; labelings+=nl
        by_n.append({'vertices':n,'graphs':nc,'labelings':nl,'edge_assignments':nr})
    return {'status':'PASS','range':'All labelled simple undirected graphs on 1 through 5 vertices',
            'graphs':count,'world_labelings':labelings,'edge_assignments':residuals,'by_n':by_n,
            'verified':['kernel dimension equals connected component count',
                        'incidence rank n-c by independent Gaussian elimination',
                        'integrability and reconstruction by propagation',
                        'all gradient fibers have 2^c elements',
                        'ambiguity equals component saturation of nonzero derivative'],
            'non_claim':'No assertion that these finite graphs realize specified forcing diagrams.'}

def partitions(n: int):
    def rec(i: int, blocks: list[list[int]]):
        if i==n:
            yield tuple(tuple(b) for b in blocks); return
        for j in range(len(blocks)):
            blocks[j].append(i); yield from rec(i+1,blocks); blocks[j].pop()
        blocks.append([i]); yield from rec(i+1,blocks); blocks.pop()
    yield from rec(0,[])

def partition_checks() -> dict:
    pc=inputs=selector_evaluations=hom_candidates=0
    for n in range(1,6):
        for blocks in partitions(n):
            pc+=1
            selectors=list(product(*blocks))
            count_expected=1
            for C in blocks: count_expected*=len(C)
            assert len(selectors)==count_expected
            invariant_values = {sum(int((bm>>j)&1)<<v for j,C in enumerate(blocks) for v in C)
                                for bm in range(1<<len(blocks))}
            for a in range(1<<n):
                lo=hi=0
                for C in blocks:
                    mask=sum(1<<v for v in C)
                    vals=[(a>>v)&1 for v in C]
                    if all(vals): lo|=mask
                    if any(vals): hi|=mask
                possible={sum(((a>>s)&1)<<v for C,s in zip(blocks,sel) for v in C)
                          for sel in selectors}
                interval={b for b in invariant_values if (lo & b)==lo and (b & hi)==b}
                assert possible==interval
                assert all((lo&b)==lo and (b&hi)==b for b in possible)
                selector_evaluations+=len(selectors); inputs+=1
            # Independent enumeration of all coordinate maps, each representing a
            # unital Boolean homomorphism P( n ) -> P( n ), for n <= 4.
            if n<=4:
                inv_masks=list(invariant_values)
                good=[]
                for f in product(range(n), repeat=n):
                    hom_candidates+=1
                    def apply(a): return sum(((a>>f[v])&1)<<v for v in range(n))
                    if (all(apply(a) in invariant_values for a in range(1<<n))
                        and all(apply(a)==a for a in inv_masks)):
                        good.append(f)
                generated=[]
                for sel in selectors:
                    f=[0]*n
                    for C,s in zip(blocks,sel):
                        for v in C: f[v]=s
                    generated.append(tuple(f))
                assert set(good)==set(generated)
    # All functions Bool^2 -> Bool are enumerated. A Boolean retraction onto
    # constants must preserve 0, 1, XOR, and conjunction.
    retractions=[]; equivariant=[]
    for table in product(range(2),repeat=4):
        ok=table[0]==0 and table[3]==1
        for a,b in product(range(4),repeat=2):
            ok = ok and table[a^b]==(table[a]^table[b]) and table[a&b]==(table[a]&table[b])
        if ok:
            retractions.append(list(table))
            if table[1]==table[2]: equivariant.append(list(table))
    assert len(retractions)==2 and equivariant==[]
    return {'status':'PASS','partitions':pc,'observable_inputs':inputs,
            'selector_evaluations':selector_evaluations,
            'independent_coordinate_homomorphisms_examined':hom_candidates,
            'range':'All partitions on 1 through 5 labelled points; independent homomorphism enumeration through 4 points',
            'two_world_boolean_retractions':retractions,
            'swap_equivariant_boolean_retractions':equivariant,
            'verified':['selector classification','exact lower/upper envelope of all Boolean retractions',
                        'no symmetry-preserving Boolean retraction in the two-world example']}

def stability_checks() -> dict:
    # All directed graphs through 3 vertices, including loops. An independent
    # cycle enumeration checks the SCC criterion used in the note.
    systems=0
    for n in range(1,4):
        edges_all=list(product(range(n),repeat=2))
        for gm in range(1<<len(edges_all)):
            edges=[e for j,e in enumerate(edges_all) if (gm>>j)&1]
            reach=[[i==j for j in range(n)] for i in range(n)]
            for i,j in edges: reach[i][j]=True
            for k in range(n):
                for i in range(n):
                    for j in range(n): reach[i][j] |= reach[i][k] and reach[k][j]
            for a in range(1<<n):
                mixed_scc=any(reach[i][j] and reach[j][i] and ((a>>i)&1)!=((a>>j)&1)
                              for i in range(n) for j in range(n))
                # A truth-changing edge belongs to a directed cycle precisely
                # when its target can reach its source.
                changing_cycle=any(((a>>i)&1)!=((a>>j)&1) and reach[j][i] for i,j in edges)
                assert mixed_scc==changing_cycle
                systems+=1
    return {'status':'PASS','labelled_directed_systems':systems,
            'range':'All directed graphs with loops on 1 through 3 vertices, all binary vertex labellings',
            'verified':'Mixed SCC iff some truth-changing edge lies on a directed cycle',
            'non_claim':'Infinite-path equivalence uses the proof in the note, not finite simulation of infinite paths.'}

def main() -> None:
    if not __debug__:
        raise RuntimeError('Assertions must be enabled. Do not run this checker with python -O.')
    started=datetime.now(timezone.utc).isoformat(); t=perf_counter()
    result={
        'release':'Komorebi Resolution Semantics 0.1.0',
        'run_started_utc':started,
        'python_version':sys.version,
        'platform':platform.platform(),
        'arithmetic':'Exact integers, bit masks, and F_2 squarefree polynomial normal forms',
        'randomness':'None',
        'polynomial':polynomial_checks(),
        'graphs':graph_checks(),
        'partitions':partition_checks(),
        'stability':stability_checks(),
        'lean_status':'NOT_RUN: no Lean executable located; pinned release download failed because runtime could not resolve github.com and the external download route was restricted.',
        'proof_boundary':'The note provides ordinary mathematical proofs. Exact certificates and bounded enumeration are not a Lean verification of the entire framework or of forcing semantics.'
    }
    result['elapsed_seconds']=round(perf_counter()-t,6)
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['status']='PASS'
    out=ROOT/'results'/'VERIFICATION.json'; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        # Do not leave a stale PASS file after a failed reproduction.
        out=ROOT/'results'/'VERIFICATION.json'
        out.parent.mkdir(parents=True,exist_ok=True)
        failure={'status':'FAIL','error_type':type(exc).__name__,
                 'error':str(exc),'run_utc':datetime.now(timezone.utc).isoformat(),
                 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        out.write_text(json.dumps(failure,indent=2)+'\n')
        raise

