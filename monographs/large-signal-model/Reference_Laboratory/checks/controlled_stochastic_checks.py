"""Finite exact checks and labeled numerical tests for Propositions 26--37.

All model-wide claims remain conditional on the hypotheses in the written proofs.
This is a theory verification suite, not a benchmark or formal proof-kernel run.
"""
from __future__ import annotations
from collections import Counter
from itertools import product
from pathlib import Path
import json
import math
import platform
import numpy as np
import sympy as sp
from stochastic_reference import fit_core, finite_subspace_report, noisy_core_bound
from stochastic_generator import (SYMBOLS, T, INSTRUMENTS, INITIAL, MASS, R, TESTS,
    HISTORIES, population_tables, required_words, word_probability, reset_success_count)

ROOT = Path(__file__).resolve().parents[1]
Q = sp.Rational
RESULTS = []


def check(name, proposition, condition, *, arithmetic='exact', scope='finite example', details=None):
    record = dict(name=name, proposition=str(proposition), passed=bool(condition),
                  arithmetic=arithmetic, scope=scope)
    if details is not None:
        record['details'] = details
    RESULTS.append(record)
    if not condition:
        raise AssertionError(f'{name} failed')


def rejects(name, function, message):
    try:
        function()
    except ValueError as exc:
        check(name, 'reference API', message in str(exc), scope='expected input rejection')
    else:
        check(name, 'reference API', False, scope='expected input rejection')


def strings(matrix):
    return [[str(value) for value in row] for row in sp.Matrix(matrix).tolist()]


def main():
    out = ROOT / 'verification'
    out.mkdir(exist_ok=True)
    h, gs, b0 = population_tables()
    model = fit_core(h, gs, b0, rank_upper_bound=2)
    check('instrument mass conservation',26,
          all(MASS*sum((INSTRUMENTS[a,o] for o in range(2)),sp.zeros(2)) == MASS for a in range(2)))
    check('noncommuting action transitions',26,T[0]*T[1] != T[1]*T[0],scope='genuinely controlled example')
    check('minimal invariant observable row space',26,R.rank()==2)
    check('all four instrument intertwining identities',26,
          all(model.operators[s]*R == R*INSTRUMENTS[s] for s in SYMBOLS))
    check('core determinant is 11/576',28,h.det()==Q(11,576))
    check('initial core probability is 13/24',28,b0 == sp.Matrix([1,Q(13,24)]))
    check('four shifted table identities',28,all(model.operators[s]*h==gs[s] for s in SYMBOLS))
    total_words=0
    for length in range(6):
        words=list(product(SYMBOLS, repeat=length))
        valid=all(model.probability(w)==word_probability(w) for w in words)
        check(f'all word probabilities at length {length}',27,valid,
              scope='exhaustive finite comparison against separate hidden generator',
              details={'words_compared':len(words)})
        total_words+=len(words)
    expected_ops={
        (0,0):sp.Matrix([[1,-1],[Q(11,32),-Q(1,4)]]),
        (0,1):sp.Matrix([[0,1],[-Q(3,32),Q(3,4)]]),
        (1,0):sp.Matrix([[Q(5,48),Q(5,6)],[Q(23,192),Q(5,24)]]),
        (1,1):sp.Matrix([[Q(43,48),-Q(5,6)],[Q(37,64),-Q(5,8)]])}
    check('all published learned matrices',28,all(model.operators[s]==expected_ops[s] for s in SYMBOLS))
    z=b0; p=INITIAL; path=[]
    sequence=((0,1),(1,0),(1,1),(0,0),(0,1),(1,1))
    joint=sp.Integer(1)
    for i,s in enumerate(sequence):
        probability,z=model.update(z,s)
        un=INSTRUMENTS[s]*p; trueprob=(MASS*un)[0];p=un/trueprob
        check(f'conditional filter step {i+1}',29,z==R*p and probability==trueprob,
              details={'symbol':list(s),'probability':str(probability),'q':str(z[1])})
        joint*=probability
        check(f'conditional product step {i+1}',27,joint==word_probability(sequence[:i+1]))
        path.append(dict(index=i+1,symbol=list(s),probability=str(probability),q=str(z[1]),joint=str(joint)))
    check('published first posterior',28,path[0]['q']=='15/26')
    check('published second posterior',28,path[1]['q']=='599/1460')
    check('published second likelihood',28,path[1]['probability']=='365/624')
    check('published two-step probability',28,path[1]['joint']=='365/1152')
    check('negative learned entries are present',29,any(v<0 for B in model.operators.values() for v in B),
          scope='negative coordinate entries do not imply negative represented probabilities')
    check('known cone extreme-ray invariance',29,
          all(all(v>=0 for v in R.inv()*model.operators[s]*R) for s in SYMBOLS),
          scope='certificate uses known generator, not learned solely from table')
    for s in SYMBOLS:
        ok=True
        for numerator in range(11):
            p=sp.Matrix([Q(numerator,10),1-Q(numerator,10)])
            probability,z=model.update(R*p,s)
            ok &= (0<probability<=1 and Q(3,8)<=z[1]<=Q(5,8))
        check(f'probability base grid {s}',29,ok,details={'beliefs':11})
    bad=sp.Matrix([1,Q(1,10)])
    check('one-step valid state can fail at two steps',29,
          all(0<=(model.mass*model.operators[s]*bad)[0]<=1 for s in SYMBOLS)
          and (model.mass*model.operators[0,1]**2*bad)[0]<0,
          scope='negative control to finite-horizon positivity extrapolation')
    P=sp.Matrix([[Q(1,2),-Q(1,2)],[-Q(1,2),Q(1,2)]])
    packet=P*sp.Matrix([Q(3,4),Q(1,4)])
    check('Haar detail is signed and zero mass',30,
          packet==sp.Matrix([Q(1,4),-Q(1,4)]) and (MASS*packet)[0]==0 and packet!=sp.zeros(2,1))
    check('signed Haar packets reconstruct exactly',30,
          P*P==P and (sp.eye(2)-P)*P==sp.zeros(2) and P+(sp.eye(2)-P)==sp.eye(2))
    coordinate_packets=[sp.diag(1,0),sp.diag(0,1)]
    check('positive coordinate packets are genuine mixture components',30,
          all(all(x>=0 for x in p) and p*p==p for p in coordinate_packets))
    passive_common={(0,0):[[Q(1,2)]],(0,1):[[Q(1,2)]]}
    passive_a=fit_core([[1]],{**passive_common,(1,0):[[1]],(1,1):[[0]]},[1],rank_upper_bound=1)
    passive_b=fit_core([[1]],{**passive_common,(1,0):[[0]],(1,1):[[1]]},[1],rank_upper_bound=1)
    for length in range(5):
        words=list(product(((0,0),(0,1)),repeat=length))
        check(f'missing action indistinguishability length {length}',31,
              all(passive_a.probability(w)==passive_b.probability(w)==Q(1,2)**length for w in words),
              scope='two instantiated one-state models, identical fair-coin action only',
              details={'passive_words_compared':len(words)})
    check('unobserved action models disagree',31,
          passive_a.probability(((1,0),))==1 and passive_b.probability(((1,0),))==0,
          scope='same passive process; other action emits opposite deterministic observations')
    # Exact normalized defect with a coarse two-block partition of three states.
    rr=sp.Matrix([[1,1,0],[0,0,1]])
    mm=sp.diag(Q(1,4),Q(3,4),Q(1,2))
    bb=sp.diag(Q(1,2),Q(1,2)); prior=sp.Matrix([Q(1,2),Q(1,4),Q(1,4)])
    zz=rr*prior; lam=sp.ones(1,2); defect=(rr*mm-bb*rr)*prior
    aa=(sp.ones(1,3)*mm*prior)[0];b=(lam*bb*zz)[0];posthat=bb*zz/b
    lhs=rr*(mm*prior/aa)-posthat
    rhs=(sp.eye(2)-posthat*lam)*defect/aa
    check('exact vector filtering defect',36,lhs==rhs)
    check('exact scalar branch likelihood defect',36,aa-b==(lam*defect)[0])
    check('posterior may agree while likelihood differs',36,
          Q(1,4)/Q(1,4)==Q(3,4)/Q(3,4) and Q(1,4)!=Q(3,4),
          scope='one-state counterexample')
    # Likelihood sensitivity at decreasing event mass: exact rational.
    rare=[]
    for denominator in [10,100,1000,10000]:
        eta=Q(1,denominator);u=sp.Matrix([eta,0]);v=sp.Matrix([eta,eta])
        postu=u/sum(u);postv=v/sum(v)
        check(f'rare branch amplification denominator {denominator}',34,
              sum(abs(x) for x in postu-postv)==1 and sum(abs(x) for x in u-v)==eta,
              scope='vanishing raw error with nonvanishing posterior error')
        rare.append({'eta':float(eta),'raw_error':float(eta),'posterior_error':1.0})
    # Invertible recoding must carry operators and mass functional together.
    gauge=sp.Matrix([[2,1],[-1,1]])
    for length in range(4):
        okay=True
        for w in product(SYMBOLS,repeat=length):
            state=gauge*b0
            for s in w:state=gauge*model.operators[s]*gauge.inv()*state
            okay &= (model.mass*gauge.inv()*state)[0]==model.probability(w)
        check(f'atlas invariance through word length {length}',37,okay)
    rejects('singular core rejection',lambda:fit_core([[1,1],[1,1]],gs,b0),'invertible')
    rejects('float in exact fitter rejection',lambda:fit_core([[1.,.5],[.5,.3]],gs,b0),'exact rational')
    rejects('too-small rank bound rejection',lambda:fit_core(h,gs,b0,rank_upper_bound=1),'smaller')
    rejects('insufficient rank bound rejection',lambda:fit_core(h,gs,b0,rank_upper_bound=3),'larger')
    rejects('initial mass rejection',lambda:fit_core(h,gs,[Q(1,2),Q(1,2)]),'first entry one')
    rejects('missing branch rejection',lambda:fit_core(h,{(0,1):gs[0,1]},b0),'conservation')
    rejects('unknown symbol rejection',lambda:model.probability(((4,3),)),'Unknown')
    rejects('wrong state shape rejection',lambda:model.update([1,2,3],(0,0)),'wrong shape')
    rejects('unnormalized state rejection',lambda:model.update([2,1],(0,0)),'mass must')
    zero_model=fit_core([[1]],{(0,0):[[0]],(0,1):[[1]]},[1],rank_upper_bound=1)
    rejects('zero-probability conditioning rejection',lambda:zero_model.update([1],(0,0)),'(0, 1]')
    check('fitter does not claim global positivity',28,not model.certificate()['global_cone_invariance_certified_by_fitter'])
    # Finite noisy subspace cases. Projector bounds are numerical, not symbolic.
    rng=np.random.default_rng(20261009)
    subspace=[]
    for m,n,r in [(5,6,2),(6,5,3),(4,4,1),(4,4,4)]:
        U=np.linalg.qr(rng.normal(size=(m,r)))[0]
        V=np.linalg.qr(rng.normal(size=(n,r)))[0]
        singular=np.linspace(2.,.5,r) if r>1 else np.array([.5])
        x=(U*singular)@V.T;s=singular[-1]
        for frac in [.01,.1,.24,.49]:
            e=rng.normal(size=(m,n));e*=frac*s/np.linalg.norm(e,2)
            budget=float(np.linalg.norm(e,2));y=x+e
            Uhat=np.linalg.svd(y,full_matrices=False)[0][:,:r]
            measured=float(np.linalg.norm(U@U.T-Uhat@Uhat.T,2));bound=2*budget/s
            alignment=float(np.linalg.svd(Uhat.T@U,compute_uv=False)[-1])
            check(f'subspace m={m}, n={n}, r={r}, fraction={frac}',32,
                  measured<=bound+1e-12 and alignment>=math.sqrt(1-bound**2)-1e-12,
                  arithmetic='float64',scope='deterministic numerical perturbation, tolerance 1e-12')
            subspace.append(dict(m=m,n=n,r=r,fraction=frac,error=measured,bound=bound))
    rejects('invalid numerical rank rejection',lambda:finite_subspace_report(np.eye(2),3,.01),'Rank')
    rejects('nonfinite numerical table rejection',lambda:finite_subspace_report([[float('nan')]],1,.01),'finite')
    hh=np.asarray(h,float)
    noisy=[]
    for scale in [1e-6,1e-5,1e-4,1e-3]:
        e=rng.normal(size=(2,2));e*=scale/np.linalg.norm(e,2)
        for symbol in SYMBOLS:
            ff=rng.normal(size=(2,2));ff*=scale/np.linalg.norm(ff,2)
            result=noisy_core_bound(hh+e,np.asarray(gs[symbol],float)+ff,h_error=scale,g_error=scale)
            actual=float(np.linalg.norm(result['operator']-np.asarray(model.operators[symbol],float),2))
            check(f'noisy core {symbol}, scale={scale}',33,actual<=result['bound']+1e-11,
                  arithmetic='float64',scope='deterministic finite-core sensitivity, tolerance 1e-11')
            noisy.append(dict(symbol=list(symbol),scale=scale,error=actual,bound=result['bound']))
    rejects('insufficient noisy core gap rejection',lambda:noisy_core_bound(hh,np.asarray(gs[0,1],float),h_error=1.,g_error=0.),'gap')
    # Reset trials generate observations. Sample tables are not declared exactly coherent.
    words=required_words();delta=.01;sampling=[]
    for n in [2000,200000]:
        means={};rows=[]
        for w in words:
            successes=reset_success_count(w,n,rng)
            means[w]=successes/n
            rows.append({'word':[list(s) for s in w], 'trials':n,'successes':successes,
                         'estimate':successes/n,'population':float(word_probability(w))})
        eps=math.sqrt(math.log(2*len(words)/delta)/(2*n))
        maxerror=max(abs(row['estimate']-row['population']) for row in rows)
        check(f'seeded reset sampling N={n}',35,maxerror<=eps,
              arithmetic='sampled',scope='one synthetic experiment, not a proof of confidence coverage',
              details={'words':len(words),'simultaneous_bound':eps,'observed_maximum':maxerror})
        hhat=np.array([[means[history+test] for history in HISTORIES] for test in TESTS])
        budget=2*eps;gap=float(np.linalg.svd(hhat,compute_uv=False)[-1]);cases=[]
        for symbol in SYMBOLS:
            ghat=np.array([[means[history+(symbol,)+test] for history in HISTORIES] for test in TESTS])
            if gap>budget:
                result=noisy_core_bound(hhat,ghat,h_error=budget,g_error=budget)
                actual=float(np.linalg.norm(result['operator']-np.asarray(model.operators[symbol],float),2))
                check(f'sampled operator bound N={n}, {symbol}',33,actual<=result['bound']+1e-10,
                      arithmetic='sampled',scope='conditional bound checked in one simulated reset experiment')
                cases.append({'symbol':list(symbol),'actual':actual,'bound':result['bound']})
        sampling.append({'trials_per_word':n,'word_count':len(words),'confidence_parameter':delta,
                         'epsilon':eps,'max_error':maxerror,'observed_gap':gap,'spectral_error_budget':budget,
                         'gap_certificate_available':gap>budget,'operators':cases,'counts':rows})
    # Exact nonlinear normalization error identity plus numerical norm bound.
    filterbounds=[]
    for symbol in SYMBOLS:
        B=np.asarray(model.operators[symbol],float);z=np.asarray(b0,float).reshape(-1)
        Bh=B+1e-5*np.array([[0,1],[-1,0]],float);zh=z+np.array([0,1e-4])
        u=B@z;v=Bh@zh;p=u[0];phat=v[0]
        zplus=u/p;zhplus=v/phat
        d=v-u;Rbound=math.sqrt(1+(5/8)**2)
        D=np.linalg.norm(Bh,2)*np.linalg.norm(zh-z)+np.linalg.norm(Bh-B,2)*Rbound
        bound=(1+Rbound)*D/(p-D)
        actual=float(np.linalg.norm(zhplus-zplus))
        check(f'normalization-aware error {symbol}',34,
              p>D and actual<=bound+1e-12 and np.allclose(zhplus-zplus,(np.eye(2)-np.outer(zplus,[1,0]))@d/phat,atol=1e-12),
              arithmetic='float64',scope='conditional finite-branch error bound')
        filterbounds.append({'symbol':list(symbol),'error':actual,'bound':float(bound),'probability':float(p)})
    tables={'scope':'population probabilities from a declared rational generator; not empirical observations',
            'tests':[[list(s) for s in w] for w in TESTS], 'histories':[[list(s) for s in w] for w in HISTORIES],
            'core':strings(h),'shifted':{f'{a},{o}':strings(g) for (a,o),g in gs.items()},
            'initial':strings(b0),'rank_upper_bound_assumed':2}
    (ROOT/'examples'/'population_tables.json').write_text(json.dumps(tables,indent=2)+'\n')
    report={'version':'0.3.0','status':'PASS','python':platform.python_version(),'sympy':sp.__version__,
            'numpy':np.__version__,'check_records':len(RESULTS),'arithmetic_counts':dict(Counter(r['arithmetic'] for r in RESULTS)),
            'exhaustive_word_comparisons':total_words,'maximum_word_length':5,
            'proof_kernel_run':False,'production_runtime_modified':False,'checks':RESULTS}
    (out/'controlled_stochastic_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'observable_table_certificate.json').write_text(json.dumps(model.certificate(),indent=2)+'\n')
    data={'scope':'explicit mathematical examples and seeded reset sampling, not external benchmarks',
          'filter_path':path,'initial_q':str(b0[1]),'rare_event':rare,'subspace':subspace,'noisy_core':noisy,
          'sampling':sampling,'filter_error_bounds':filterbounds}
    (out/'stochastic_figure_data.json').write_text(json.dumps(data,indent=2)+'\n')
    print(f"PASS: {len(RESULTS)} check records. Arithmetic: {report['arithmetic_counts']}.")
    print(f'Exact word comparisons: {total_words}, lengths zero through five.')
    print('No Lean run. No production-runtime modification. No external signal data.')


if __name__=='__main__':
    try:
        main()
    except Exception:
        (ROOT/'verification').mkdir(exist_ok=True)
        (ROOT/'verification'/'controlled_stochastic_failed_attempt.json').write_text(json.dumps(RESULTS,indent=2)+'\n')
        raise
