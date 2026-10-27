"""Finite exact instances and negative controls for Foundations 0.4.0.

All general claims are proved in the accompanying manuscript. This suite never
labels a finite word enumeration as proof of an infinite-horizon statement.
"""
from __future__ import annotations
import json
import itertools
import platform
from pathlib import Path
import sys
from collections import Counter
import sympy as sp
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'examples'))
from certified_probability_example import load_observable_model
from cone_reference import verify_certificate, search_interval, probability, minimum_mixture_repair

RESULTS = []


def check(name, proposition, condition, scope='finite exact example'):
    row = {'name': name, 'proposition': proposition, 'arithmetic': 'exact rational',
           'scope': scope, 'passed': bool(condition)}
    RESULTS.append(row)
    if not row['passed']:
        raise AssertionError(name)


def rejects(name, call):
    try:
        call()
    except ValueError:
        check(name, 39, True, 'expected input rejection')
    else:
        check(name, 39, False, 'expected input rejection')


def norm1(v):
    return sum(abs(x) for x in v)


def tree(ops, initial, mass, depth, adaptive=True):
    states = {(): initial}
    for t in range(depth):
        nxt = {}
        for h, z in states.items():
            a = (t+sum(h)) % 2 if adaptive else t % 2
            for o in [0, 1]:
                nxt[h+(o,)] = ops[(a,o)] * z
        states = nxt
    return {h: (mass*z)[0] for h,z in states.items()}


def rotation_model(alpha=sp.Rational(1)):
    R = sp.Matrix([[sp.Rational(3,5),-sp.Rational(4,5)],
                   [sp.Rational(4,5),sp.Rational(3,5)]])
    z = sp.Matrix([1,1,0]); lam = sp.Matrix([[1,0,0]])
    T = sp.diag(1, alpha*R)
    ops = {(0,0):T, (0,1):sp.zeros(3),
           (1,0):z*sp.Matrix([[sp.Rational(1,2),sp.Rational(1,2),0]]),
           (1,1):z*sp.Matrix([[sp.Rational(1,2),-sp.Rational(1,2),0]])}
    return ops,z,lam,R


def diamond_coefficients(u):
    t,x,y = u
    if t < abs(x)+abs(y):
        raise ValueError('Outside diamond cone.')
    residual = (t-abs(x)-abs(y))/4
    return sp.Matrix([max(x,0)+residual,max(y,0)+residual,
                      max(-x,0)+residual,max(-y,0)+residual])


def main():
    out=ROOT/'verification';out.mkdir(exist_ok=True)
    model=load_observable_model();bs=dict(model.operators);z=model.initial;lam=model.mass
    found=search_interval(bs,z,denominator_bound=8)
    check('bounded observable-only search returns certificate',45,found is not None)
    v=found.generators;vi=v.inv();aa=dict(found.lifts);alpha=found.weights
    check('interval endpoints',45,(found.lower,found.upper)==(sp.Rational(2,5),sp.Rational(3,5)))
    check('first successful ordered candidate',45,found.tested_candidates==10 and found.candidate_count==132)
    check('initial weights',39,alpha==sp.Matrix([sp.Rational(7,24),sp.Rational(17,24)]))
    check('positive robustness slack',40,min(x for a in aa.values() for x in a)==sp.Rational(1,64))
    check('verifier internal validity',39,verify_certificate(bs,lam,z,v,aa,alpha)['all_word_probability_validity'])
    for s in bs:
        check(f'intertwining {s}',39,bs[s]*v==v*aa[s])
        check(f'nonnegative lift {s}',39,all(x>=0 for x in aa[s]))
        for j in range(2):
            check(f'dual generator facets {s} {j}',39,all(x>=0 for x in vi*bs[s]*v[:,j]))
    for a in (0,1):
        check(f'exact positive lift conservation action {a}',39,
              sp.ones(1,2)*(aa[(a,0)]+aa[(a,1)])==sp.ones(1,2))
    # Exact bounded-word comparisons are grouped by length, not inflated as proof counts.
    total=0;keys=tuple(sorted(bs))
    for n in range(7):
        valid=True
        for word in itertools.product(keys,repeat=n):
            p=probability(bs,lam,z,word)
            q=probability(aa,sp.ones(1,2),alpha,word)
            valid=valid and p==q and 0<=p<=1
            total+=1
        check(f'positive lift word equivalence through exact length {n}',39,valid,
              f'exhaustive finite comparison of {4**n} words')
    # Complete invariance supports arbitrary rational mixtures, checked at examples.
    d=sp.Rational(1,128);e=sp.ones(2)*d
    vertices=[]
    for sign0,sign1 in itertools.product((-1,1),repeat=2):
        pert={s:sp.Matrix(a) for s,a in aa.items()}
        for action,sign in [(0,sign0),(1,sign1)]:
            pert[(action,0)]+=sign*e;pert[(action,1)]-=sign*e
        bpert={s:v*a*vi for s,a in pert.items()}
        report=verify_certificate(bpert,lam,z,v,pert,alpha)
        check(f'robust joint vertex {sign0} {sign1}',40,report['all_word_probability_validity'])
        vertices.append((pert,bpert))
    for k in range(9):
        w=sp.Rational(k,8)
        pert={s:w*vertices[0][0][s]+(1-w)*vertices[-1][0][s] for s in bs}
        bpert={s:v*a*vi for s,a in pert.items()}
        check(f'robust convex family {w}',40,verify_certificate(bpert,lam,z,v,pert,alpha)['all_word_probability_validity'])
    aa2,bs2=vertices[-1]
    epsilon=max(sum(norm1((aa[s]-aa2[s])[:,j]) for s in keys if s[0]==a)
                for a in [0,1] for j in [0,1])
    check('summed base-norm perturbation',42,epsilon==sp.Rational(1,32))
    for coeff in ([1,-1],[2,-3],[0,1],[-2,-1],[sp.Rational(1,7),-sp.Rational(2,9)]):
        x=sp.Matrix(coeff)
        for action in [0,1]:
            check(f'base contraction {coeff} action {action}',42,
                  sum(norm1(aa[(action,o)]*x) for o in [0,1])<=norm1(x))
    law=[]
    for adaptive in [False,True]:
        for horizon in range(9):
            pp=tree(bs,z,lam,horizon,adaptive);qq=tree(bs2,z,lam,horizon,adaptive)
            tv=sum(abs(pp[h]-qq[h]) for h in pp)/2
            bound=min(sp.Rational(1),horizon*epsilon/2)
            check(f'observation law TV horizon {horizon} adaptive {adaptive}',43,
                  sum(pp.values())==1 and sum(qq.values())==1 and all(p>=0 for p in [*pp.values(),*qq.values()]) and tv<=bound)
            if adaptive:law.append({'horizon':horizon,'tv':str(tv),'bound':str(bound)})
    # Perturbed initialization contributes its own half base norm.
    altalpha=sp.Matrix([sp.Rational(1,2),sp.Rational(1,2)]);altz=v*altalpha
    initialerror=norm1(alpha-altalpha)
    for t in [0,1,3,6]:
        pp=tree(bs,z,lam,t);qq=tree(bs2,altz,lam,t)
        tv=sum(abs(pp[h]-qq[h]) for h in pp)/2
        check(f'law bound with initial error {t}',43,tv<=(initialerror+t*epsilon)/2)
    # Conditional-law amplification: equality cases, including an absent Q event.
    rare=[]
    for p in [sp.Rational(1,2),sp.Rational(1,10),sp.Rational(1,100)]:
        delta=p/10;P=sp.Matrix([p,0,1-p]);Q=sp.Matrix([p-delta,delta,1-p])
        tv=norm1(P-Q)/2;conditional=norm1(P[:2,0]/p-Q[:2,0]/p)/2
        check(f'conditioning sharpness p={p}',44,tv==delta and conditional==delta/p)
        rare.append({'p':str(p),'unconditional_tv':str(tv),'conditional_tv':str(conditional)})
    # A raw invalid lift repaired by a declared positive reference mixture.
    raw={s:sp.Matrix(a) for s,a in aa.items()}
    key,min_i=min(((s,i) for s in keys for i in range(4)),key=lambda si:raw[si[0]][si[1]])
    i,j=divmod(min_i,2);amount=raw[key][i,j]+sp.Rational(1,100)
    raw[key][i,j]-=amount
    partner=(key[0],1-key[1]);raw[partner][i,j]+=amount
    reference={s:sp.ones(2)/4 for s in keys}
    eta,repaired=minimum_mixture_repair(raw,reference)
    check('explicit repair weight',41,eta==sp.Rational(1,26))
    check('corrected lift nonnegative',41,all(x>=0 for a in repaired.values() for x in a))
    bfix={s:v*a*vi for s,a in repaired.items()}
    check('corrected all-word validity',41,verify_certificate(bfix,lam,z,v,repaired,alpha)['all_word_probability_validity'])
    below=eta/2
    check('smaller mixture fails positivity',41,any(x<0 for s in keys for x in (1-below)*raw[s]+below*reference[s]),'negative control')
    # Rational curved-domain process and finite-test witness.
    rot,zr,lr,R=rotation_model()
    T=rot[(0,0)]
    check('rotation exact isometry',46,R.T*R==sp.eye(2) and R.det()==1)
    check('reachable rank three',46,sp.Matrix.hstack(zr,T*zr,T*T*zr).det()!=0)
    check('observable rank three',46,sp.Matrix.vstack(lr,lr*rot[(1,0)],lr*rot[(1,0)]*T).det()!=0)
    check('nonintegral rational twice cosine',46,2*R[0,0]==sp.Rational(6,5) and not (2*R[0,0]).is_Integer,
          'exact algebraic premise of the written irrational-rotation proof')
    orbit=[];state=zr
    for k in range(21):
        check(f'rational orbit on Lorentz boundary {k}',46,state[0]==1 and state[1]**2+state[2]**2==1)
        orbit.append([str(x) for x in state]);state=T*state
    witness=sp.Matrix([1,0,sp.Rational(6,5)])
    validshort=all(probability(rot,lr,witness,w)>=0 for n in range(3) for w in itertools.product(keys,repeat=n))
    negword=((0,0),(0,0),(1,0));neg=probability(rot,lr,witness,negword)
    check('outer two-step tests admit an invalid state',38,validshort and neg==sp.Rational(-19,250),'explicit length-three negative witness')
    # An exact rational four-generator certificate for an explicitly damped model.
    damp,zd,ld,_=rotation_model(sp.Rational(2,3))
    vd=sp.Matrix([[1,1,1,1],[1,0,-1,0],[0,1,0,-1]])
    ad={s:sp.Matrix.hstack(*(diamond_coefficients(b*vd[:,j]) for j in range(4))) for s,b in damp.items()}
    alphad=sp.Matrix([1,0,0,0])
    check('rational diamond certificate',47,verify_certificate(damp,ld,zd,vd,ad,alphad)['all_word_probability_validity'])
    for s in damp:
        check(f'diamond intertwining {s}',47,damp[s]*vd==vd*ad[s])
    check('undamped diamond fails',46,abs((T*vd[:,0])[1])+abs((T*vd[:,0])[2])>1,'negative control')
    contraction=sp.Rational(2,3)*sp.Rational(7,5)
    check('strict diamond contraction margin',47,contraction==sp.Rational(14,15))
    damp_law=[]
    for t in range(9):
        pp=tree(rot,zr,lr,t);qq=tree(damp,zd,ld,t)
        tv=sum(abs(pp[h]-qq[h]) for h in pp)/2;bound=min(sp.Rational(1),sp.Rational(t,6))
        check(f'damped law certificate {t}',47,sum(pp.values())==1 and sum(qq.values())==1 and tv<=bound)
        damp_law.append({'horizon':t,'tv':str(tv),'bound':str(bound)})
    # Coordinate transport preserves the same finite witness.
    chart=sp.Matrix([[1,1],[1,-1]]);ci=chart.inv()
    transported={s:chart*b*ci for s,b in bs.items()}
    check('complete coordinate certificate transport',49,
          verify_certificate(transported,lam*ci,chart*z,chart*v,aa,alpha)['all_word_probability_validity'])
    # Confidence accounting itself is symbolic arithmetic, not empirical coverage.
    delta=sp.Rational(1,100)
    for n in [1,2,5,10]:
        spent=sum(delta/2**j for j in range(1,n+1));tail=delta/2**n
        check(f'confidence budget exact partial sum {n}',48,spent+tail==delta)
    # Validation failures must not be silently accepted as certificates.
    rejects('float generator rejected',lambda:verify_certificate(bs,lam,z,[[1.,1.],[.4,.6]],aa,alpha))
    rejects('rank-deficient generators rejected',lambda:verify_certificate(bs,lam,z,sp.Matrix([[1,1],[sp.Rational(1,2),sp.Rational(1,2)]]),aa,alpha))
    rejects('unnormalized generators rejected',lambda:verify_certificate(bs,lam,z,2*v,aa,alpha))
    rejects('inconsistent initial weights rejected',lambda:verify_certificate(bs,lam,z,v,aa,sp.Matrix([1,0])))
    bad={s:sp.Matrix(a) for s,a in aa.items()};bad[key][0,0]=-1
    rejects('negative lift rejected',lambda:verify_certificate(bs,lam,z,v,bad,alpha))
    bad={s:sp.Matrix(a) for s,a in aa.items()};bad[key][0,0]+=1
    rejects('false intertwining rejected',lambda:verify_certificate(bs,lam,z,v,bad,alpha))
    missing={s:a for s,a in aa.items() if s!=key}
    rejects('missing lift branch rejected',lambda:verify_certificate(bs,lam,z,v,missing,alpha))
    rawb={s:v*a*vi for s,a in raw.items()}
    rejects('invalid raw model rejected',lambda:verify_certificate(rawb,lam,z,v,raw,alpha))
    badB=dict(bs);badB[key]=badB[key]+sp.eye(2)
    rejects('mass failure in search rejected',lambda:search_interval(badB,z))
    rejects('invalid grid limit rejected',lambda:search_interval(bs,z,denominator_bound=0))
    rejects('partial alphabet rejected',lambda:search_interval({s:b for s,b in bs.items() if s!=key},z))
    rejects('unknown word symbol rejected',lambda:probability(bs,lam,z,((9,9),)))
    badref={s:sp.zeros(2) for s in keys}
    rejects('nonpositive reference rejected',lambda:minimum_mixture_repair(raw,badref))
    # Bounded search with no candidate must explicitly withhold a result.
    check('coarse grid can withhold a certificate',45,search_interval(bs,z,denominator_bound=1) is None,'expected no-certificate result')
    report={'version':'0.4.0','status':'PASS','check_records':len(RESULTS),
            'arithmetic_counts':dict(Counter(r['arithmetic'] for r in RESULTS)),
            'exhaustive_word_comparisons':total,'maximum_word_length':6,
            'python':platform.python_version(),'sympy':sp.__version__,
            'proof_kernel_run':False,'production_runtime_modified':False,'checks':RESULTS}
    (out/'certified_domain_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'learned_cone_certificate.json').write_text(json.dumps(found.report,indent=2)+'\n')
    data={'scope':'exact finite examples, not empirical model performance',
          'interval':[str(found.lower),str(found.upper)],'minimum_lift_entry':'1/64',
          'robust_entry_radius':'1/128','law':law,'rare':rare,'repair_weight':str(eta),
          'negative_test_value':str(neg),'rotation_orbit':orbit,'damped_law':damp_law}
    (out/'domain_figure_data.json').write_text(json.dumps(data,indent=2)+'\n')
    print(f'PASS: {len(RESULTS)} exact rational check records; {total} grouped word comparisons.')
    print('Written proofs, not trajectory counts, establish the general results. No Lean run.')


if __name__=='__main__':
    try:
        main()
    except Exception:
        (ROOT/'verification').mkdir(exist_ok=True)
        (ROOT/'verification'/'certified_domain_failed_attempt.json').write_text(json.dumps(RESULTS,indent=2)+'\n')
        raise
