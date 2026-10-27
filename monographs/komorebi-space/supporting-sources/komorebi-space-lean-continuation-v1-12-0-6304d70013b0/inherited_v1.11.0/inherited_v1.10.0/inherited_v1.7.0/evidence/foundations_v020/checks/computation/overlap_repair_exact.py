#!/usr/bin/env python3
"""Independent exact audit of anchored isometric overlap reconstruction.

Uses rational arithmetic and signed permutation frames. Finite tests audit the
implementation and assumptions; arbitrary-size/normed-space results are Lean
proofs, not extrapolations from this run. No network or third-party packages.
"""
from __future__ import annotations
import argparse
from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import time
from datetime import datetime, timezone

Vec = tuple[Q, ...]
Edge = tuple[int, int]
CHECKS: Counter[str] = Counter()
CASES: Counter[str] = Counter()


def check(condition: bool, label: str) -> None:
    CHECKS[label] += 1
    if not condition:
        raise AssertionError(label)


def add(x: Vec, y: Vec) -> Vec:
    return tuple(a+b for a, b in zip(x, y, strict=True))


def sub(x: Vec, y: Vec) -> Vec:
    return tuple(a-b for a, b in zip(x, y, strict=True))


def neg(x: Vec) -> Vec:
    return tuple(-a for a in x)


def vn(x: Vec) -> Q:
    return max(map(abs, x), default=Q(0))


def fn(xs: list[Vec] | dict[Edge, Vec]) -> Q:
    vals = xs.values() if isinstance(xs, dict) else xs
    return max((vn(x) for x in vals), default=Q(0))


@dataclass(frozen=True)
class Frame:
    permutation: tuple[int, ...]
    signs: tuple[int, ...]

    def __post_init__(self) -> None:
        if sorted(self.permutation) != list(range(len(self.permutation))):
            raise ValueError('Not a permutation')
        if len(self.signs) != len(self.permutation) or any(s not in (-1, 1) for s in self.signs):
            raise ValueError('Invalid signs')

    def apply(self, x: Vec) -> Vec:
        return tuple(Q(self.signs[i])*x[j] for i, j in enumerate(self.permutation))

    def inverse(self, x: Vec) -> Vec:
        result = [Q(0)]*len(x)
        for i, j in enumerate(self.permutation):
            result[j] = Q(self.signs[i])*x[i]
        return tuple(result)

    def after(self, other: Frame) -> Frame:
        # self after other, verified independently by vector action below.
        return Frame(tuple(other.permutation[j] for j in self.permutation),
                     tuple(self.signs[i]*other.signs[j] for i, j in enumerate(self.permutation)))


def edges_for(kind: str, n: int) -> list[Edge]:
    if kind == 'path':
        pairs = {(i, i+1) for i in range(n-1)}
    elif kind == 'star':
        pairs = {(0, i) for i in range(1, n)}
    elif kind == 'cycle':
        pairs = {(i, i+1) for i in range(n-1)} | ({(0,n-1)} if n > 2 else set())
    elif kind == 'complete':
        pairs = {(i,j) for i in range(n) for j in range(i+1,n)}
    else:
        raise ValueError(kind)
    return sorted(pairs | {(j,i) for i,j in pairs})


def routes(n: int, edges: list[Edge], root: int, reverse: bool = False) -> list[list[Edge]]:
    adj = {i: sorted([j for a,j in edges if a == i], reverse=reverse) for i in range(n)}
    paths: dict[int,list[Edge]] = {root: []}
    queue = deque([root])
    while queue:
        i = queue.popleft()
        for j in adj[i]:
            if j not in paths:
                paths[j] = paths[i]+[(i,j)]
                queue.append(j)
    if len(paths) != n:
        raise ValueError('Disconnected measured graph')
    return [paths[i] for i in range(n)]


def differential(frames: list[Frame], edges: list[Edge], x: list[Vec]) -> dict[Edge,Vec]:
    # Literal source-frame overlap equation, not a sum of precomputed normalized values.
    return {(i,j): sub(frames[i].apply(frames[j].inverse(x[j])), x[i]) for i,j in edges}


def integrate(frames: list[Frame], paths: list[list[Edge]], r: dict[Edge,Vec]) -> list[Vec]:
    dim = len(frames[0].signs)
    out: list[Vec] = []
    for i, path in enumerate(paths):
        total = tuple(Q(0) for _ in range(dim))
        for a,b in path:
            total = add(total, frames[a].inverse(r[(a,b)]))
        out.append(frames[i].apply(total))
    return out


def repair(frames: list[Frame], root: int, x: list[Vec]) -> list[Vec]:
    seed = frames[root].inverse(x[root])
    return [f.apply(seed) for f in frames]


def consistent(rows: list[list[Q]], values: list[Q], variables: int) -> bool:
    """Independent exact row elimination, not path integration."""
    matrix = [[Q(a) for a in row]+[Q(rhs)] for row,rhs in zip(rows,values,strict=True)]
    pivot = 0
    for col in range(variables):
        found = next((i for i in range(pivot,len(matrix)) if matrix[i][col]), None)
        if found is None:
            continue
        matrix[pivot], matrix[found] = matrix[found], matrix[pivot]
        scale = matrix[pivot][col]
        matrix[pivot] = [a/scale for a in matrix[pivot]]
        for i in range(len(matrix)):
            if i != pivot and matrix[i][col]:
                scale = matrix[i][col]
                matrix[i] = [a-scale*b for a,b in zip(matrix[i],matrix[pivot],strict=True)]
        pivot += 1
    return all(any(row[:-1]) or row[-1] == 0 for row in matrix)


def residual_integrable(frames: list[Frame], edges: list[Edge], r: dict[Edge,Vec], root: int) -> bool:
    n, dim = len(frames), len(frames[0].signs)
    rows: list[list[Q]] = []
    for i,j in edges:
        row=[Q(0)]*n; row[i]=-1; row[j]=1; rows.append(row)
    boundary=[Q(0)]*n; boundary[root]=1; rows.append(boundary)
    return all(consistent(rows,[frames[i].inverse(r[(i,j)])[k] for i,j in edges]+[Q(0)],n)
               for k in range(dim))


def fixture_frames(n: int, dim: int, pattern: int) -> list[Frame]:
    return [Frame(tuple((j+i+pattern)%dim for j in range(dim)),
                  tuple(-1 if (i+2*j+pattern)%3 == 0 else 1 for j in range(dim)))
            for i in range(n)]


def audit_case(n: int, dim: int, kind: str, root: int, pattern: int, seed: int) -> None:
    edges=edges_for(kind,n); paths=routes(n,edges,root); radius=max(map(len,paths),default=0)
    frames=fixture_frames(n,dim,pattern)
    x=[tuple(Q(((i+1)*(k+2)+seed*(i-k))%13-6, seed+1) for k in range(dim)) for i in range(n)]
    for i in range(n):
        check(frames[i].inverse(frames[i].apply(x[i])) == x[i], 'frame_inverse')
        check(vn(frames[i].apply(x[i])) == vn(x[i]), 'frame_isometry')
    r=differential(frames,edges,x); correction=integrate(frames,paths,r); p=repair(frames,root,x)
    check(fn(r) <= 2*fn(x), 'differential_bound')
    check([sub(a,b) for a,b in zip(x,correction,strict=True)] == p, 'path_vs_direct_repair')
    check(differential(frames,edges,p) == {edge:tuple(Q(0) for _ in range(dim)) for edge in edges}, 'exact_repair')
    check(p[root] == x[root], 'protected_anchor')
    check(repair(frames,root,p) == p, 'idempotent_repair')
    check(fn(p) <= fn(x), 'repair_contractive')
    check(fn(correction) <= radius*fn(r), 'derived_error_bound')
    check(differential(frames,edges,correction) == r, 'dAd_equals_d')
    check(integrate(frames,routes(n,edges,root,True),r) == correction, 'routing_independence_on_image')
    check(residual_integrable(frames,edges,r,root), 'actual_residual_gaussian_consistency')
    for i in range(n):
        same=frames[i].inverse(x[i]) == frames[root].inverse(x[root])
        check((p[i] == x[i]) == same, 'prescribed_value_criterion')
    changes=fixture_frames(n,dim,pattern+2)
    newframes=[changes[i].after(frames[i]) for i in range(n)]
    newx=[changes[i].apply(x[i]) for i in range(n)]
    newp=repair(newframes,root,newx); newr=differential(newframes,edges,newx)
    check(newp == [changes[i].apply(p[i]) for i in range(n)], 'isometric_reframe_repair')
    check(newr == {(i,j):changes[i].apply(r[(i,j)]) for i,j in edges}, 'isometric_reframe_defect')
    check(fn(newr) == fn(r), 'isometric_reframe_norm')
    # Independent residual assignments, not necessarily in the image.
    for typ in ('antisymmetric','unrestricted'):
        q={}
        for i,j in edges:
            lo,hi=min(i,j),max(i,j)
            z=tuple(Q((lo+2)*(hi+3)+(k+seed)**2, k+1) for k in range(dim))
            if typ == 'antisymmetric' and i>j: z=neg(z)
            q[(i,j)]=frames[i].apply(z)
        a=integrate(frames,paths,q); dq=differential(frames,edges,a)
        obstruction={edge:sub(q[edge],dq[edge]) for edge in edges}
        check(fn(a) <= radius*fn(q), 'arbitrary_integral_bound')
        check(fn(obstruction) <= (1+2*radius)*fn(q), 'integrability_obstruction_bound')
        check(fn(obstruction) == 0 if residual_integrable(frames,edges,q,root) else fn(obstruction)>0,
              'image_criterion_vs_independent_elimination')
        check(differential(frames,edges,integrate(frames,paths,dq)) == dq, 'residual_projection_idempotent')
        check(fn(integrate(frames,paths,obstruction)) == 0, 'integration_annihilates_obstruction')
        if typ == 'antisymmetric':
            check(all(frames[i].inverse(q[(i,j)]) == neg(frames[j].inverse(q[(j,i)])) for i,j in edges),
                  'normalized_antisymmetry')
        CASES['independent_residuals'] += 1
    CASES['graph_frame_candidate_configurations'] += 1


def run() -> list[dict[str,object]]:
    for n in range(1,9):
        for dim in (1,2,3):
            for kind in ('path','star','cycle','complete'):
                for root in sorted({0,n-1}):
                    for pattern in (0,1):
                        for seed in (0,1,2):
                            audit_case(n,dim,kind,root,pattern,seed)
    for length in range(1,41):
        n=length+1; frames=[Frame((0,),(1,))]*n
        x=[(Q(i),) for i in range(n)]
        r=differential(frames,edges_for('path',n),x)
        err=fn([sub(a,b) for a,b in zip(x,repair(frames,0,x),strict=True)])
        check(fn(r)==1 and err==length,'chain_sharpness')
        CASES['chain_lengths']+=1
    # Five explicit false-claim controls. A pass means the false claim was rejected.
    negative=[]
    def reject(label: str, false_claim: bool) -> None:
        check(not false_claim,'negative_'+label)
        negative.append({'claim':label,'rejected':not false_claim})
    reject('one_error_constant_for_all_chain_lengths', err <= fn(r))
    frames=[Frame((0,),(1,))]*3; edges=edges_for('complete',3)
    q={edge:(Q(1 if edge in ((0,1),(1,2)) else -1 if edge in ((1,0),(2,1)) else 0),) for edge in edges}
    reject('every_antisymmetric_triangle_residual_has_a_primitive',residual_integrable(frames,edges,q,0))
    x=[(Q(7),),(Q(9),)]; frames2=frames[:2]; edges2=edges_for('path',2)
    a=integrate(frames2,routes(2,edges2,0),differential(frames2,edges2,x))
    wrong=[add(u,v) for u,v in zip(x,a,strict=True)]
    reject('reverse_correction_sign_repairs',fn(differential(frames2,edges2,wrong))==0)
    ident=Frame((0,1),(1,1)); quarter=Frame((1,0),(-1,1)); z=(Q(2),Q(3))
    coherent=[ident.apply(z),quarter.apply(z)]
    wrong_def=sub(ident.apply(quarter.apply(coherent[1])),coherent[0])
    reject('omit_inverse_of_local_chart',vn(wrong_def)==0)
    reject('all_incompatible_prescribed_values_can_be_preserved',
           consistent([[Q(-1),Q(1)],[Q(1),Q(0)],[Q(0),Q(1)]],[Q(0),Q(7),Q(9)],2))
    return negative


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic(); stamp=datetime.now(timezone.utc).isoformat()
    negatives=run()
    result={'status':'PASS','started_at_utc':stamp,'runtime_seconds':time.monotonic()-start,
            'python_version':platform.python_version(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'coefficient_domain':'exact fractions.Fraction rationals and signed permutation frames',
            'conventions':'directed edge i->j has tau_ij*x_j-x_i; integration uses inverse source frame; sup norms',
            'bounds':{'vertices':[1,8],'dimensions':[1,2,3],
                      'graph_families':['path','star','cycle','complete'],'roots':'first and last (deduplicated)',
                      'frame_patterns':[0,1],'candidate_seeds':[0,1,2],'sharp_chain_lengths':[1,40]},
            'randomness':{'used':False},'cases':dict(CASES),'assertions':sum(CHECKS.values()),
            'checks_by_kind':dict(CHECKS),'negative_controls':negatives,
            'non_claims':['Not all finite graphs or all isometries are enumerated.',
                          'Finite tests do not establish arbitrary graph or normed-space theorems.',
                          'No nonlinear, nonflat, or general stack repair is claimed.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','cases','assertions','runtime_seconds')},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
