#!/usr/bin/env python3
"""Deterministic finite tests. The universal soundness result is the Lean theorem."""
from pathlib import Path
from fractions import Fraction as Q
import dataclasses, hashlib, json, platform, sys, time
import sympy as sp
from exact_certificate import *

ROOT=Path(__file__).resolve().parents[1]

def sm(a:Matrix):return sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in a])

def rank_packets(n:int)->tuple[Matrix,...]:
    u=tuple(Q(i+1) for i in range(n));d=sum((x*x for x in u),Q(0))
    h=tuple(tuple(Q(int(i==j))-2*u[i]*u[j]/d for j in range(n)) for i in range(n))
    return tuple(tuple(tuple(h[i][a]*h[j][a] for j in range(n)) for i in range(n)) for a in range(n))

def case(n:int,k:int)->Model:
    r=max(1,n-1)
    H=tuple(tuple(Q(((i+1)*(j+2))%5-2,3) for j in range(n)) for i in range(k))
    L=tuple(tuple(Q(((i+2)*(j+1))%5-2,2) for j in range(r)) for i in range(n))
    N=tuple((Q(i+1,5),) for i in range(k))
    return Model(H,L,N,Q(1,4),tuple(Q(i-1,3) for i in range(n)),tuple(Q(i+1,2) for i in range(k)),rank_packets(n),rank_packets(k))

def run()->dict:
    start=time.monotonic();cases=[];assertions=0;rejected=0
    for n in range(1,5):
      for k in range(1,4):
        m=case(n,k);B=tuple(tuple(Q((i-j)%3-1,8) for j in range(k)) for i in range(n))
        c=m.exact(B);assert c.valid(m);assertions+=1
        # Independent matrix implementation and a different energy expression (trace of a Gram).
        P=sm(m.L)*sm(m.L).T;R=sm(m.N)*sm(m.N).T+sp.Rational(1,4)*sp.eye(k)
        S=sm(m.H)*P*sm(m.H).T+R;F=P*sm(m.H).T-sm(B)*S
        assert P==sm(m.P) and R==sm(m.R) and S==sm(m.S) and F==sm(m.residual(B));assertions+=4
        assert (F.T*F).trace()==sp.Rational(c.total().numerator,c.total().denominator);assertions+=1
        for i,p in enumerate(m.outputs):
          for j,q in enumerate(m.inputs):
            b=sm(p)*F*sm(q)
            assert (b.T*b).trace()==sp.Rational(c.upper[i][j].numerator,c.upper[i][j].denominator);assertions+=1
        padded=m.exact(B,Q(1,1000));assert padded.valid(m);assertions+=1
        forged=dataclasses.replace(c,upper=tuple(tuple(x-Q(1) if i==j==0 else x for j,x in enumerate(row)) for i,row in enumerate(c.upper)))
        assert not forged.valid(m);rejected+=1
        iv=dataclasses.replace(c,innovation_upper=c.innovation_upper-Q(1));assert not iv.valid(m);rejected+=1
        nofloor=dataclasses.replace(m,sigma=Q(0));assert not c.valid(nofloor);rejected+=1
        incomplete=dataclasses.replace(m,outputs=tuple(zero(n,n) for _ in m.outputs));assert not c.valid(incomplete);rejected+=1
        # Three deterministic untrusted Richardson proposals. No convergence theorem is inferred.
        step=1/max(sum(abs(x) for x in row) for row in m.S)
        inc=m.exact(zero(n,k));proposals=[forged]
        b=zero(n,k)
        for _ in range(3):
          b=add(b,scale(step,m.residual(b)));proposals.append(m.exact(b))
        selected,decisions=select(m,inc,proposals)
        assert selected.valid(m) and selected.score(m)<=inc.score(m);assertions+=2
        cases.append(dict(state=n,observation=k,prior_rank=int(P.rank()),
             proposed_score=str(c.score(m)),selected_score=str(selected.score(m)),
             initial_score=str(inc.score(m)),proposal_accepts=[d['accepted'] for d in decisions]))
    for bad in [0.1,float('inf'),float('nan'),True,'1/0','nan']:
        try:rational(bad)
        except ValueError:rejected+=1
        else:raise AssertionError(f'Unsupported numeric input accepted: {bad!r}')
    for malformed in [[[1],[1,2]],[],[[1.5]]]:
        try:matrix(malformed,'test')
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid matrix accepted')
    d=json.loads((ROOT/'examples/GeneratedExactScalar.json').read_text());m=Model.parse(d['model']);cs=[Candidate.parse(c,m) for c in d['candidates']]
    selected,dec=select(m,cs[0],cs[1:]);assert selected.score(m)==Q(1,1250) and selected.tolerance(m,Q(1,20));assertions+=2
    d=json.loads((ROOT/'examples/GeneratedExactRotated.json').read_text());m=Model.parse(d['model']);cs=[Candidate.parse(c,m) for c in d['candidates']]
    selected,dec=select(m,cs[0],cs[1:]);assert selected.score(m)==Q(15,256) and selected.tolerance(m,Q(1,4));assertions+=2
    assert [x['accepted'] for x in dec]==[True,False,False];assertions+=1
    return dict(status='PASS',range_cases=len(cases),independent_assertions=assertions,negative_checks=rejected,
                coefficient_domain='exact rational',randomness='none',python=sys.version,sympy=sp.__version__,platform=platform.platform(),
                elapsed_seconds=round(time.monotonic()-start,4),cases=cases,
                non_claims=['Finite diagnostics do not prove universal soundness','No floating point certification','No solver convergence or termination theorem'])

if __name__=='__main__':
    result=run();(ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/exact_tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
