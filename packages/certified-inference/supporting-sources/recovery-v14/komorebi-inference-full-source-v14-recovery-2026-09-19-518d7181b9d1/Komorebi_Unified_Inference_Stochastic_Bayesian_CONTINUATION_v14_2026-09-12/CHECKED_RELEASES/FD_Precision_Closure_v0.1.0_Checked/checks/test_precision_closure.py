#!/usr/bin/env python3
"""Independent exact diagnostics of the finite precision graph and hybrid producer.

SymPy constructs the exact matrices independently of the Fraction arithmetic
used by the producers. Finite diagnostics are not substitutes for Lean proofs.
"""
from __future__ import annotations
import hashlib,json,math,platform,time
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sympy as sp
from exact_certificate import Model,eye,zero,packet_valid,matrix,rational
from rounded_certificate import produce,rsum
from precision_certificate import graph,score_coefficient,precision_for,sufficient_precision,total,Budget
from hybrid_solver import hybrid,export_lean

ROOT=Path(__file__).resolve().parents[1]
count=0;negative=0

def check(condition:bool,label:str)->None:
    global count
    count+=1
    if not condition:raise AssertionError(label)

def reject(fn,label:str)->None:
    global negative
    try:fn()
    except (ValueError,TypeError,ArithmeticError):negative+=1;return
    raise AssertionError('Expected rejection: '+label)

def q(x)->Q:return Q(int(sp.numer(x)),int(sp.denom(x)))
def mat(a)->sp.Matrix:return sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in a])
def tuplemat(a)->tuple:return tuple(tuple(q(a[i,j]) for j in range(a.cols)) for i in range(a.rows))

def packets(n:int)->tuple:
    v=sp.Matrix([i+1 for i in range(n)])
    U=sp.eye(n)-2*v*v.T/(v.T*v)[0]
    return tuple(tuplemat(U[:,i]*U[:,i].T) for i in range(n))

def rational_matrix(n:int,k:int,seed:int)->tuple:
    return tuple(tuple(Q(((seed+3*i+2*j)%7)-3,((seed+i+j)%4)+1) for j in range(k)) for i in range(n))

def exact_graph(m:Model,gain)->dict[str,sp.Matrix]:
    H,L,N,B=map(mat,[m.H,m.L,m.N,gain]);s=sp.Rational(m.sigma.numerator,m.sigma.denominator)
    P=L*L.T;R=N*N.T+s*sp.eye(H.rows);S=H*P*H.T+R;F=P*H.T-B*S
    v=sp.Matrix(m.observation)-H*sp.Matrix(m.mean)
    result={'prior':P,'noise':R,'innovation':S,'residual':F,'innovation_vector':v}
    for i,pa in enumerate(m.outputs):
        for j,pb in enumerate(m.inputs):result[f'packet_{i}_{j}']=mat(pa)*F*mat(pb)
    return result

def run()->dict:
    start=time.perf_counter();cases=[]
    for n in range(1,4):
        for k in range(1,4):
            seed=10*n+k;u=max(1,n-1);w=2
            m=Model(rational_matrix(k,n,seed),rational_matrix(n,u,seed+1),
                rational_matrix(k,w,seed+2),Q(1+(seed%3),2),
                tuple(Q(i-1,3) for i in range(n)),tuple(Q(2-j,5) for j in range(k)),
                packets(n),packets(k))
            gain=rational_matrix(n,k,seed+4)
            check(packet_valid(m.outputs,n) and packet_valid(m.inputs,k),'packet construction')
            exact=exact_graph(m,gain);c,parts,nodes=score_coefficient(m,gain)
            F=exact['residual'];v=exact['innovation_vector'];s=sp.Rational(m.sigma.numerator,m.sigma.denominator)
            exact_score=q(sp.trace(F*F.T)*(s+(v.T*v)[0])/(s*s))
            check(exact_score==m.exact(gain).score(m),'independent exact score')
            ceiling=max(0,-((-exact_score.numerator)//exact_score.denominator))
            eps=Q(math.isqrt(ceiling)+1)
            slack=min(Q(1),(eps*eps-exact_score)/2)
            p=precision_for(c,slack)
            check(p<=512,'diagnostic precision cap')
            for bits in sorted(set([0,3,8,16,p,p+1])):
                candidate,trace=produce(m,gain,bits);mesh=Q(1,1<<bits)
                for name,budget in nodes.items():
                    x=exact[name];balls=trace[name]
                    check((len(budget),len(budget[0]))==(x.rows,x.cols),'node shape')
                    for i in range(x.rows):
                        for j in range(x.cols):
                            value=q(x[i,j]);b=balls[i][j];z=budget[i][j]
                            check(abs(value)<=z.mag,'exact magnitude')
                            check(b.encloses(value),'outward enclosure')
                            check(b.radius<=z.coeff*mesh,'quantified radius')
                            check(value*value<=b.upper()<=value*value+z.energy_coeff*mesh,'energy inflation')
                score=candidate.score(m)
                check(exact_score<=score<=exact_score+c*mesh,'full score sandwich')
                if bits>=p:
                    check(c*mesh<=slack,'chosen precision bounds inflation')
                    check(candidate.tolerance(m,eps),'strict-margin precision sufficiency')
            cases.append(dict(state=n,observation=k,prior_rank=int(exact['prior'].rank()),
                predicted_bits=p,coefficient=str(c),exact_score=str(exact_score),tolerance=str(eps)))
    # Empty sums are part of the universal scalar contracts.
    check(total([])==Budget(Q(0),Q(2)),'empty budget sum')
    for p in [0,1,9]:
        b=rsum(p,[]);check(b.encloses(Q(0)) and b.radius<=Q(2,1<<p),'empty rounded sum')
    for C in [Q(0),Q(1,3),Q(1),Q(10**20,7)]:
        for d in [Q(1),Q(1,1024),Q(1,10**15)]:
            p=precision_for(C,d)
            check(C/Q(1<<p)<=d,'bit budget endpoints')
    scalar=json.loads((ROOT/'examples/solver_scalar.json').read_text())
    m=Model.parse(scalar['model']);initial=matrix(scalar['initial_gain'],'gain');eps=rational(scalar['epsilon'])
    low=hybrid(m,initial,eps,max_steps=0)
    check(low['status']=='RESOURCE_LIMIT' and not low['posterior_tolerance_certified'],'iteration resource cap')
    prec=hybrid(m,initial,eps,max_precision=1)
    check(prec['status']=='RESOURCE_LIMIT' and not prec['posterior_tolerance_certified'],'precision resource cap')
    reject(lambda:export_lean(m,initial,eps,prec,'NoProof'),'no capped success export')
    scheduled=hybrid(m,initial,eps,probes=[4,12])
    check(scheduled['chosen_precision']==12 and scheduled['guaranteed_precision']==61,'early precision with guaranteed fallback')
    check([a['passed'] for a in scheduled['precision_attempts']]==[False,True],'precision schedule follows actual checks')
    fallback=hybrid(m,initial,eps,probes=[0,1])
    check(fallback['chosen_precision']==fallback['guaranteed_precision'],'fallback reached after failed probes')
    reject(lambda:hybrid(m,initial,eps,probes=[True]),'Boolean probe rejected')
    reject(lambda:hybrid(m,initial,eps,probes=[-1]),'negative probe rejected')

    for e in [Q(0),Q(-1)]:reject(lambda e=e:hybrid(m,initial,e),'nonpositive tolerance')
    reject(lambda:precision_for(Q(1),Q(0)),'zero slack')
    reject(lambda:precision_for(Q(1),Q(-1)),'negative slack')
    reject(lambda:hybrid(replace(m,sigma=Q(0)),initial,eps),'zero floor')
    reject(lambda:hybrid(replace(m,sigma=Q(-1)),initial,eps),'negative floor')
    reject(lambda:hybrid(replace(m,outputs=(zero(1,1),)),initial,eps),'incomplete packets')
    reject(lambda:sufficient_precision(m,((Q(1),Q(2)),),Q(1)),'bad gain shape')
    reject(lambda:rational(0.1),'binary float rejected')
    reject(lambda:rational(True),'Boolean rejected')
    reject(lambda:hybrid(m,initial,eps,max_precision=True),'Boolean precision rejected')
    # Equal exact-score boundary does not by itself make tested rounded precisions pass.
    boundary=replace(m,observation=(Q(0),));B=((Q(1,3),),)
    check(boundary.exact(B).score(boundary)==Q(1,9),'exact score equals squared tolerance')
    for p in [4,16]:
        cand,_=produce(boundary,B,p)
        check(not cand.tolerance(boundary,Q(1,3)),'boundary equality may reject')
    return dict(status='PASS',cases=cases,case_count=len(cases),precisions_per_case=6,
        assertions=count,negative_rejections=negative,arithmetic='exact rational; independent SymPy matrices',
        random_seed=None,randomness_used=False,python=platform.python_version(),sympy=sp.__version__,
        seconds=round(time.perf_counter()-start,3),
        non_claims=['Finite diagnostics do not establish universal theorems.',
                    'No numerical performance or optimal-precision claim.'])

if __name__=='__main__':
    report=run();target=ROOT/'results/PRECISION_DIAGNOSTICS.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
