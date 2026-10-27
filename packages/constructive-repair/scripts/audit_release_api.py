#!/usr/bin/env python3
"""Exact randomized coordinate-invariance checks with independent SymPy ranks."""
from pathlib import Path
import sys,json,random,hashlib,time
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import sympy as S
import komorebi_repair as K
from repair_certificates import Mat,canonical


def main():
    rng=random.Random(2026101906);start=time.monotonic()
    records=[];comparisons=0
    def matrix(m,n):
        return Mat.of([[F(rng.randint(-4,4),rng.randint(1,5)) for _ in range(n)] for _ in range(m)],n)
    def rank(a):
        return S.Matrix(a.rows,a.cols,[S.Rational(x.numerator,x.denominator) for r in a.data for x in r]).rank()
    def oracle(D,E,R,w,table):
        nonlocal comparisons
        feasible=[]
        for mask in range(1<<E.cols):
            B=D.join(E.columns([j for j in range(E.cols) if mask&(1<<j)]))
            ok=rank(B)==rank(B.join(R));comparisons+=1
            if ok and (table is None or mask in table):
                feasible.append((sum(w[j] for j in range(E.cols) if mask&(1<<j)),mask))
        return min(feasible)[0] if feasible else None
    for i in range(128):
        m,n,q,s=(rng.randrange(z) for z in (6,5,6,4))
        D,E,R=matrix(m,n),matrix(m,q),matrix(m,s)
        weights=[rng.randrange(6) for _ in range(q)]
        table=None if i%3 else sorted(rng.sample(list(range(1<<q)),rng.randrange((1<<q)+1)))
        T=Mat.of([[F(1) if j==k else F(rng.randint(-2,2)) if j<k else F(0)
                   for j in range(m)] for k in range(m)],m)
        expected=oracle(D,E,R,weights,table)
        residual_rank=rank(D.join(R))-rank(D)
        for name,A,B,C in [('original',D,E,R),('invertible_coordinate_change',T@D,T@E,T@R)]:
            p=K.menu_problem(A,B,C,weights,table);out=K.solve(p)
            assert out.status=='PYTHON_CERTIFICATE_VALID',(i,name,out.error)
            assert (out.certificate.get('cost') if out.certificate['kind']=='optimal_menu' else None)==expected
            assert K.verify(p,out.certificate).status=='PYTHON_CERTIFICATE_VALID'
            fp=K.free_problem(A,C);fo=K.solve(fp)
            assert fo.status=='PYTHON_CERTIFICATE_VALID' and fo.certificate['t']==residual_rank
            assert K.verify(fp,fo.certificate).status=='PYTHON_CERTIFICATE_VALID'
            records.append({'seed':2026101906,'case':i,'realization':name,'problem':p,
                            'certificate':out.certificate,'free_problem':fp,'free_certificate':fo.certificate,
                            'independent_menu_cost':expected,'independent_obstruction_rank':residual_rank})
    path=ROOT/'evidence/release_coordinate_cases.jsonl'
    path.write_bytes(b''.join(canonical(r) for r in records))
    result={'status':'PASS','seed':2026101906,'original_problems':128,
            'coordinate_invariance_pairs':128,'menu_certificate_checks':256,
            'free_certificate_checks':256,'independent_subset_rank_comparisons':comparisons,
            'independent_obstruction_rank_comparisons':128,'records':len(records),
            'seconds':round(time.monotonic()-start,3),'case_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'scope':'New exact computations, not new general Lean theorems'}
    (ROOT/'evidence/release_coordinate_audit.json').write_bytes(canonical(result))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
