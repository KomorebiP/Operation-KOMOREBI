#!/usr/bin/env python3
"""Bounded independent exact-rational audit; not a substitute for the Lean proof."""
from __future__ import annotations
import datetime as dt,hashlib,json,platform,sys,time
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sympy as sp
from exact_certificate import Model,zero,eye,matrix,rational,encode
from rounded_gain_solver import parameters,rounded_update,solve,export_lean,ResourceLimit
from rounded_certificate import produce

ROOT=Path(__file__).resolve().parents[1]
checks=0
negative=0

def check(p,msg):
    global checks
    checks+=1
    if not p:raise AssertionError(msg)

def srat(x):return sp.Rational(x.numerator,x.denominator)
def smat(a):return sp.Matrix([[srat(x) for x in row] for row in a])
def sen(a):return sp.expand(sum(x*x for x in a))
def frac(x):return Q(int(sp.numer(x)),int(sp.denom(x)))
def coords(n):return tuple(tuple(tuple(Q(int(i==j==k)) for j in range(n)) for i in range(n)) for k in range(n))
def packets(n):
    if n!=2:return coords(n)
    return (((Q(1,2),Q(1,2)),(Q(1,2),Q(1,2))),
            ((Q(1,2),Q(-1,2)),(Q(-1,2),Q(1,2))))

def expect_error(fn,name):
    global negative
    try:fn()
    except (ValueError,ResourceLimit):negative+=1
    else:raise AssertionError('Invalid case accepted: '+name)

def main():
    start=dt.datetime.now(dt.timezone.utc).isoformat();t0=time.monotonic();cases=[]
    for n in range(1,5):
      for k in range(1,4):
        cid=(n-1)*3+k
        u=1 if cid%2 else min(n,2)
        H=tuple(tuple(Q((-1)**(i+j)*(1+(i+2*j+cid)%3),3) for j in range(n)) for i in range(k))
        L=tuple(tuple(Q(1+(i+j)%2,2) for j in range(u)) for i in range(n))
        N=tuple((Q((-1)**i,5),) for i in range(k))
        m=Model.parse(encode(dict(H=H,L=L,N=N,sigma=Q(2+cid%3,2),
            mean=tuple(Q(i-1,7) for i in range(n)),observation=tuple(Q((-1)**i,3) for i in range(k)),
            output_packets=packets(n),input_packets=packets(k))))
        initial=tuple(tuple(Q((i-j)%3-1,10) for j in range(k)) for i in range(n))
        eps=Q(1,3);p=parameters(m,initial,eps);acc=p['update_accuracy'];h=Q(1,1<<acc)
        SH,SL,SN=smat(H),smat(L),smat(N)
        P=SL*SL.T;R=SN*SN.T+srat(m.sigma)*sp.eye(k);S=SH*P*SH.T+R
        C=P*SH.T;tau=srat(p['step']);T=sp.eye(k)-tau*S
        check(S==smat(m.S),'independent innovation')
        check(0<=p['rate']<1,'rate')
        check(p['coefficient']*h*h<=eps*eps/8,'selected floor')
        B=smat(initial);ideal=B;gain=initial
        A0=sen(C-B*S);q=srat(p['rate']);weight=srat(p['weight']);floor=6*n*k*srat(h*h)/(1-q)**2
        bit_trace=[]
        for it in range(6):
            Bnext,meta,balls=rounded_update(m,gain,acc)
            nextS=smat(Bnext);exactStep=B+tau*(C-B*S);E=nextS-exactStep
            for i in range(n):
              for j in range(k):
                b=balls[i][j]
                check(b.encloses(frac(exactStep[i,j])),'update enclosure')
                check(abs(E[i,j])<=srat(h),'whole-update error')
                check(b.radius<=h,'radius policy')
            check(sen(E)<=n*k*srat(h*h),'local energy')
            check(C-nextS*S==(C-B*S)*T-E*S,'forced residual identity')
            ideal=ideal+tau*(C-ideal*S)
            check(sen(nextS-ideal)<=floor,'uniform tracking tube')
            exactScore=sen(C-nextS*S)*weight
            upper=2*q**(it+1)*A0*weight+srat(p['coefficient']*h*h)
            check(exactScore<=upper,'geometric plus floor')
            # Check a different certificate precision than update precision.
            candidate,_=produce(m,Bnext,24)
            check(candidate.valid(m),'rounded certificate bounds exact energies')
            check(srat(candidate.score(m))>=exactScore,'outward score bounds exact score')
            bit_trace.append(meta['precision']);gain=Bnext;B=nextS
        cases.append(dict(n=n,k=k,steps=6,local_accuracy=acc,update_precisions=bit_trace,
                          prior_rank=int(P.rank()),final_score=str(exactScore)))
    formal=[]
    for name in ['scalar','rotated']:
        raw=json.loads((ROOT/'examples'/f'solver_{name}.json').read_text())
        m=Model.parse(raw['model']);B=matrix(raw['initial_gain'],'B');eps=rational(raw['epsilon'])
        r=solve(m,B,eps,[4,12]);saved=json.loads((ROOT/'results'/f'rounded_{name}.json').read_text())
        check(r['status']=='PASS_ROUNDED_SOLVER_PROVISIONAL','actual solver succeeds')
        check(r['final_candidate']==saved['final_candidate'],'saved candidate reproduced')
        check(r['iterations']==saved['iterations'],'saved update count reproduced')
        check(r['chosen_precision']==12,'probe precision')
        formal.append(dict(example=name,iterations=r['iterations'],verification_precision=12))
    # Producer and export guards are checked separately from theorem soundness.
    raw=json.loads((ROOT/'examples/solver_scalar.json').read_text());m=Model.parse(raw['model']);B=zero(1,1)
    expect_error(lambda:solve(m,B,Q(0)),'zero tolerance')
    expect_error(lambda:solve(m,B,Q(-1)),'negative tolerance')
    expect_error(lambda:solve(replace(m,sigma=Q(0)),B,Q(1,20)),'zero floor')
    expect_error(lambda:solve(m,zero(2,1),Q(1,20)),'gain shape')
    expect_error(lambda:rational(0.5),'raw float')
    expect_error(lambda:solve(m,B,Q(1,20),[True]),'Boolean precision')
    expect_error(lambda:solve(m,B,Q(1,20),[513]),'oversized probe')
    capped=solve(m,B,Q(1,20),[],max_steps=0)
    check(capped['status']=='RESOURCE_LIMIT','resource cap reports failure')
    expect_error(lambda:export_lean(m,B,Q(1,20),capped,'ForbiddenExport'),'no capped success export')
    report=dict(status='PASS',started_at_utc=start,elapsed_seconds=round(time.monotonic()-t0,3),
        arithmetic='exact fractions; independent SymPy rational matrices',
        environment=dict(python=sys.version,sympy=sp.__version__,platform=platform.platform()),
        case_count=len(cases),steps_per_case=6,assertions=checks,expected_rejections=negative,cases=cases,
        reproduced_executions=formal,randomness='none',
        non_claims=['Finite constructed tests, not universal proof or performance benchmarks.',
                    'No Gaussian sampling or floating tolerance was used.',
                    'Source/API semantics require the separate Lean proof.'])
    (ROOT/'results/ROUNDOFF_DIAGNOSTICS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','case_count','assertions','expected_rejections','elapsed_seconds']},indent=2))

if __name__=='__main__':main()
