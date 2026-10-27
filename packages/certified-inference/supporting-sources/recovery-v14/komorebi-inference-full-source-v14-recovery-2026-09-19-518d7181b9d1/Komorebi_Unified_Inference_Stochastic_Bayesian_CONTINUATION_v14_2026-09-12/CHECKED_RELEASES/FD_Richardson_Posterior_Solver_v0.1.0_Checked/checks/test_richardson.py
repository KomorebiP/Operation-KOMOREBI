#!/usr/bin/env python3
"""Independent deterministic exact-rational diagnostics, not a universal proof."""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib, json, platform, sys, time
import sympy as sp
from exact_certificate import Model, Candidate, matrix, rational, zero, eye, add, sub, mul, trans, scale, energy
from solve_richardson import solve, export_lean

ROOT=Path(__file__).resolve().parents[1]

def sm(a):
    return sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in a])

def fm(a):
    return tuple(tuple(Q(int(a[i,j].p),int(a[i,j].q)) for j in range(a.cols)) for i in range(a.rows))

def rotated_packets(n):
    u=[Q(i+1) for i in range(n)];d=sum((x*x for x in u),Q(0))
    h=tuple(tuple(Q(i==j)-2*u[i]*u[j]/d for j in range(n)) for i in range(n))
    return tuple(tuple(tuple(h[i][a]*h[j][a] for j in range(n)) for i in range(n)) for a in range(n))

def case(n,k):
    H=tuple(tuple(Q((2*i+3*j+1)%5-2,5) for j in range(n)) for i in range(k))
    L=tuple(tuple(Q((3*i+2*j+1)%7-3,5) for j in range(max(1,n-1))) for i in range(n))
    N=tuple((Q(i+1,7),) for i in range(k))
    return Model(H,L,N,Q(1),tuple(Q(i-1,4) for i in range(n)),
                 tuple(Q(i+1,5) for i in range(k)),rotated_packets(n),rotated_packets(k))

def run():
    start=time.monotonic();checks=0;negative=0;records=[]
    def check(value):
        nonlocal checks
        assert value
        checks+=1
    for n in range(1,5):
      for k in range(1,4):
        m=case(n,k);B=tuple(tuple(Q((i-j)%3-1,9) for j in range(k)) for i in range(n))
        P=sm(m.L)*sm(m.L).T;R=sm(m.N)*sm(m.N).T+sp.eye(k)
        S=sm(m.H)*P*sm(m.H).T+R;A=P*sm(m.H).T
        cap=1+sp.trace(S);tau=1/cap;rho=1-1/cap;rate=rho**2;T=sp.eye(k)-tau*S
        check(sm(m.S)==S);check(S==S.T);check(0<=rho<1)
        # A separate exact positivity check, independent of the source's spectral proof.
        for J in range(1,k+1):
            for js in combinations(range(k),J):
                check((S-sp.eye(k)).extract(js,js).det()>=0)
                check((cap*sp.eye(k)-S).extract(js,js).det()>=0)
        initialF=A-sm(B)*S;Bq=B
        for it in range(6):
            Fq=m.residual(Bq);F=A-sm(Bq)*S
            check(sm(Fq)==F)
            check(F==initialF*T**it)
            check(sp.trace(F.T*F)==sp.Rational(energy(Fq).numerator,energy(Fq).denominator))
            c=m.exact(Bq);check(c.valid(m));check(c.total()==energy(Fq))
            nextB=add(Bq,scale(Q(tau),Fq));nextF=m.residual(nextB)
            check(sm(nextF)==F*T)
            check(energy(nextF)<=Q(rate)*energy(Fq))
            check(m.exact(nextB).score(m)<=Q(rate)*c.score(m))
            Bq=nextB
        result=solve(m,B,Q(1,4),max_steps=1000,max_bits=32768)
        check(result['status']=='PASS_EXACT_DIAGNOSTIC')
        check(result['iterations']<=result['conservative_fuel'])
        final=Candidate.parse(result['final_candidate'],m)
        check(final.valid(m));check(final.tolerance(m,Q(1,4)))
        check(sm(m.residual(final.gain))==initialF*T**result['iterations'])
        # Exact solver reference is used only by this independent diagnostic.
        K=A*S.inv();exact=solve(m,fm(K),Q(1,1000),max_steps=0)
        check(exact['iterations']==0 and Q(exact['final_score'])==0)
        records.append(dict(state=n,observation=k,prior_rank=int(P.rank()),
            steps=result['iterations'],fuel=result['conservative_fuel'],final_score=result['final_score']))
    m=case(2,2);B=zero(2,2)
    for badm,badeps,badgain in [(replace(m,sigma=Q(0)),Q(1,4),B),
        (m,Q(0),B),(m,Q(-1),B),
        (replace(m,outputs=(zero(2,2),)),Q(1,4),B),(m,Q(1,4),zero(1,2))]:
        try:solve(badm,badgain,badeps)
        except ValueError:negative+=1
        else:raise AssertionError('An invalid solver input was accepted')
    for value in [0.1,float('inf'),float('nan'),True,'1/0']:
        try:rational(value)
        except ValueError:negative+=1
        else:raise AssertionError('Unsupported scalar input accepted')
    capped=solve(m,B,Q(1,1000000),max_steps=0)
    check(capped['status']=='RESOURCE_LIMIT' and not capped['posterior_tolerance_certified'])
    try:export_lean(m,B,Q(1,1000000),capped,'InvalidCappedExport')
    except ValueError:negative+=1
    else:raise AssertionError('Capped result exported as success')
    # Preserved kernel-checked instances and exporter fidelity to their exact data.
    examples=[]
    for stem,ns,steps in [('scalar','GeneratedRichardsonScalar',4),('rotated','GeneratedRichardsonRotated',3)]:
        d=json.loads((ROOT/f'examples/solver_{stem}.json').read_text());m=Model.parse(d['model'])
        B=matrix(d['initial_gain'],'initial');eps=rational(d['epsilon'])
        r=solve(m,B,eps);check(r['iterations']==steps)
        text=export_lean(m,B,eps,r,ns)
        check(text==(ROOT/f'Komorebi/{ns}.lean').read_text())
        examples.append(dict(name=stem,steps=steps,fuel=r['conservative_fuel'],score=r['final_score'],
            source_sha256=hashlib.sha256(text.encode()).hexdigest()))
    return dict(status='PASS',arithmetic='exact rational; independent SymPy matrices and principal minors',
        cases=len(records),steps_per_recurrence_case=6,assertions=checks,negative_checks=negative,
        scope='12 constructed (state 1..4, observation 1..3) cases plus two exported instances and capped/invalid input controls',
        deterministic=True,random_seed=None,records=records,examples=examples,
        environment=dict(python=sys.version,sympy=sp.__version__,platform=platform.platform()),
        runtime_seconds=round(time.monotonic()-start,6),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        solver_sha256=hashlib.sha256((ROOT/'checks/solve_richardson.py').read_bytes()).hexdigest(),
        non_claims=['Finite diagnostics are not a universal proof','No floating-point enclosure',
        'No empirical performance comparison','Python parser/exporter are not formally verified'])

if __name__=='__main__':
    result=run();(ROOT/'results/exact_tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'records','environment'}},indent=2))
