"""Derive and cross-check the exact polynomial system for five-node class 142.

The tree/forest calculation is compared symbolically with direct determinant
expansion. This encodes one topology; it neither solves nor excludes it.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import zipfile

import sympy as S

BASE=Path(__file__).resolve().parents[1]
ARCHIVE_SHA='39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
SOURCE='Smith_Chart_Research_2026-11-11/reproduction/six_state/q6_canonical_fits_75_168.json'
SOURCE_SHA='4892891c9afd5e5888ee2c207a4e83e20c0417daf213ca2bb14086256559c901'


def determinant(matrix):
    total=0
    for p in itertools.permutations(range(matrix.rows)):
        inversions=sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))
        total+=(-1)**inversions*S.prod(matrix[i,p[i]] for i in range(len(p)))
    return S.expand(total)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    archive=(BASE/'SmithChart_Complete.zip').read_bytes()
    assert hashlib.sha256(archive).hexdigest()==ARCHIVE_SHA
    with zipfile.ZipFile(BASE/'SmithChart_Complete.zip') as z:raw=z.read(SOURCE)
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    saved=[r for r in json.loads(raw)['cases'] if r['id']==142]
    assert len(saved)==1
    reactives=tuple(map(tuple,saved[0]['reactives']))
    assert reactives==(('L',1),('L',7),('L',9),('C',2),('C',4),('C',6))
    s=S.Symbol('s');g=S.symbols('g0:10');h=S.symbols('h0:6')
    edges=tuple(itertools.combinations(range(5),2))
    def components(selection):
        parent=list(range(5))
        def find(x):
            while parent[x]!=x:x=parent[x]
            return x
        for k in selection:
            u,v=edges[k];a,b=find(u),find(v)
            if a==b:return None
            parent[a]=b
        return len({find(x) for x in range(5)}),find(0)!=find(1)
    trees=[c for c in itertools.combinations(range(10),4) if components(c) is not None and components(c)[0]==1]
    forests=[c for c in itertools.combinations(range(10),3) if components(c)==(2,True)]
    assert len(trees)==125 and len(forests)==50
    admittances=list(g)
    for value,(kind,edge) in zip(h,reactives):admittances[edge]+=value/s if kind=='L' else value*s
    N=S.expand(s**3*sum(S.prod(admittances[e] for e in selection) for selection in forests))
    D=S.expand(s**3*sum(S.prod(admittances[e] for e in selection) for selection in trees))
    Y=S.zeros(4)
    for (u,v),ad in zip(edges,admittances):
        if u:Y[u-1,u-1]+=ad
        if v:Y[v-1,v-1]+=ad
        if u and v:Y[u-1,v-1]-=ad;Y[v-1,u-1]-=ad
    A=Y.applyfunc(lambda entry:S.expand(s*entry))
    assert S.expand(determinant(A)-s*D)==0
    assert S.expand(determinant(A.minor_submatrix(0,0))-N)==0
    Np,Dp=S.Poly(N,s),S.Poly(D,s)
    assert Np.degree()==Dp.degree()==6
    targetP=S.Poly(450*s**6+1385*s**5+2477*s**4+2200*s**3+1142*s**2+335*s+75,s)
    targetD=S.Poly(150*s**6+795*s**5+1375*s**4+1720*s**3+1250*s**2+445*s+25,s)
    cross=S.Poly(S.expand(N*targetD.as_expr()-D*targetP.as_expr()),s)
    equations=[S.expand(cross.nth(k)) for k in range(13)]
    assert cross.degree()==12 and all(S.Poly(e,*g,*h).total_degree()<=4 for e in equations)
    # Every tree coefficient is a sum of nonnegative monomials. The reactive
    # edge union is connected, so h_i>0 already gives a nonsingular Y(s) at s>0.
    assert components((1,7,9,4)) is not None and components((1,7,9,4))[0]==1
    assert all(c>=0 for polynomial in (Np,Dp) for c in S.Poly(polynomial.as_expr(),s,*g,*h).coeffs())
    record={'status':'PASS','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python':platform.python_version(),'sympy':S.__version__,
            'source_archive_sha256':ARCHIVE_SHA,'candidate_source':SOURCE,'candidate_source_sha256':SOURCE_SHA,
            'candidate_id':142,'nodes':5,'terminals':[0,1],'edges':edges,'reactives':reactives,
            'variables':list(map(str,g+h)),
            'constraints':'g0,...,g9 >= 0; h0,...,h5 > 0; all 13 coefficient equations equal zero. For inductors h=1/L; for capacitors h=C.',
            'trees':len(trees),'separating_two_forests':len(forests),
            'clearing_factor':'s^3','numerator_coefficients_ascending':list(map(str,[Np.nth(k) for k in range(7)])),
            'denominator_coefficients_ascending':list(map(str,[Dp.nth(k) for k in range(7)])),
            'identity_equations_ascending':list(map(str,equations)),
            'maximum_equation_total_degree':4,
            'determinant_comparison':'Both tree/forest polynomials equal direct symbolic nodal determinant expansions.',
            'scope':'Exact formulation for one five-node reactive placement. Existence of a positive solution and global six-reactive feasibility remain open.'}
    with args.output.open('x',encoding='utf-8',newline='\n') as out:json.dump(record,out,indent=2);out.write('\n')
    print('PASS: class 142; 125 trees, 50 separating forests; 13 equations of degree at most four; direct determinants agree.')


if __name__=='__main__':main()
