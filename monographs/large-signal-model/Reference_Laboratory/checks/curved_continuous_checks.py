"""Exact finite checks for Propositions 50--61. Counts are records, not proofs."""
from __future__ import annotations
from copy import deepcopy
from itertools import product
from functools import cmp_to_key
from pathlib import Path
import json,time
import sympy as s
from continuous_reference import *
from continuous_generator import PENCIL,W,ROT,K,BASE,OPERATORS,MASS,INITIAL,TESTS,HISTORIES,population_tables,template
ROOT=Path(__file__).resolve().parents[1]
R=s.Rational
records=[]


def check(name,condition,detail=None):
    ok=bool(condition)
    row={'name':name,'kind':'exact_rational_or_symbolic','passed':ok}
    if detail is not None:row['detail']=detail
    records.append(row)
    if not ok:
        raise AssertionError(name)


def rejects(name,fn):
    try:fn()
    except (ValueError,KeyError,TypeError) as e:
        check(name,True,{'expected_rejection':str(e)})
    else:check(name,False,{'unexpected_acceptance':True})


def density_tv_equal_bins(n:int):
    """Exact one-step TV for initial state (1,0,0), using exact bin averages."""
    p=BASE[0,0];total=0
    for j in range(n):
        lo=-1+R(2*j,n);hi=-1+R(2*(j+1),n)
        mean=s.integrate(p,(U,lo,hi))/(hi-lo)
        difference=s.expand(p-mean);F=s.integrate(difference,U)
        split=[lo,hi]+[r for r in s.solve(difference,U) if r.is_real and lo<r<hi]
        split.sort(key=cmp_to_key(lambda a,b: -1 if a<b else (1 if a>b else 0)))
        for a,b in zip(split,split[1:]):
            total+=s.Abs(F.subs(U,b)-F.subs(U,a))/4
    return s.simplify(total)


def main():
    start=time.perf_counter()
    m,x,y=s.symbols('m x y',real=True);z=s.Matrix([m,x,y]);J=embedding(PENCIL,z)
    check('matrix_embedding_trace',s.trace(J)==m)
    check('matrix_embedding_determinant',s.expand(J.det()-(m*m-x*x-y*y)/4)==0)
    check('rotation_weighted_congruence',zero(embedding(PENCIL,ROT*z)-W*J*W.T/5))
    old0=s.Matrix([1,1,0]);P0=s.Matrix([[1,0],[0,0]]);P1=s.Matrix([[0,1],[0,0]])
    for tag,Q,effect in [('plus',P0,s.Matrix([[R(1,2),R(1,2),0]])),('minus',P1,s.Matrix([[R(1,2),-R(1,2),0]]))]:
        check('old_probe_'+tag,zero(embedding(PENCIL,old0*(effect*z))-Q*J*Q.T))
    check('old_probe_mass',P0.T*P0+P1.T*P1==s.eye(2))
    check('old_rotation_mass',W.T*W==5*s.eye(2))
    for state in [s.Matrix([1,0,0]),s.Matrix([1,1,0]),s.Matrix([1,0,1]),s.Matrix([1,R(3,5),R(4,5)]),s.Matrix([1,R(1,3),R(1,4)])]:
        check('disk_point_'+str(list(state)),psd(embedding(PENCIL,state)))
    check('outside_disk_rejected',not psd(embedding(PENCIL,s.Matrix([1,1,1]))))
    for a,B in OPERATORS.items():
        liftK=K if a=='direct' else K*W;weight=1 if a=='direct' else R(1,5)
        check(a+'_polynomial_intertwining',zero(embedding(PENCIL,B*z)-weight*liftK*J*liftK.T))
        check(a+'_integrated_mass',zero(MASS*integral(B)-MASS))
        check(a+'_congruence_integrated_trace',integral(weight*liftK.T*liftK)==s.eye(2))
        # A constant PSD Gram factor is a symbolic certificate on the entire line.
        kv=s.Matrix([liftK[i,j] for j in range(2) for i in range(2)])
        Ch=weight*kv*kv.T
        for i,P in enumerate(PENCIL):
            output=s.Matrix(2,2,lambda k,l:sum(Ch[k+2*p,l+2*q]*P[p,q] for p in range(2) for q in range(2)))
            check(f'{a}_choi_basis_{i}',zero(output-weight*liftK*P*liftK.T))
    check('continuous_nonselective_operator',integral(BASE)==s.diag(1,1,-R(1,2)))
    check('actions_do_not_commute',not zero(BASE.subs(U,R(1,2))*ROT*BASE.subs(U,R(1,3))-BASE.subs(U,R(1,3))*BASE.subs(U,R(1,2))*ROT))
    # A support-only SOS term needs not be positive outside its declared interval.
    scalar={'schema':'komorebi.polynomial-psd-certificate.v1','reference_measure':template()['reference_measure'],
            'embedding':[[['1']]],'mass':[['1']],'initial':[['1']],'interior':[['1']],
            'actions':{'a':{'operator_coefficients':[[['3/2']],[['0']],[['-3/2']]],
                            'positive_terms':[{'weight':'3/2','multiplier':'one_minus_u_squared','coefficients':[[['1']]]}]}}}
    scalar_model=verify_certificate(scalar)
    check('interval_multiplier_certificate',scalar_model.verification['status']=='PASS')
    check('interval_does_not_claim_global_positivity',scalar_model.operators['a'].subs(U,2)[0]<0)
    rejects('interval_support_guard',lambda:scalar_model.condition_at('a',2))
    data=population_tables();fitted=fit_population_moments(data);tmp=template()
    check('core_determinant',fitted['core_determinant']==R(81,25600))
    check('moment_gram_determinant',fitted['moment_gram_determinant']==R(4,135))
    gram=s.Matrix(3,3,lambda j,k:moment(j+k))
    check('moment_gram_positive_definite',psd(gram,strict=True))
    check('moment_inverse',gram.inv()==s.Matrix([[R(9,4),0,-R(15,4)],[0,3,0],[-R(15,4),0,R(45,4)]]))
    for a,B in OPERATORS.items():
        check(a+'_observable_reconstruction',zero(polynomial(fitted['operators'][a])-TESTS*B*TESTS.inv()))
        for j in range(3):
            check(f'{a}_moment_roundtrip_{j}',zero(integral(U**j*polynomial(fitted['operators'][a]))-matrix(data['shifted_moment_tables'][a][j])*matrix(data['core']).inv()))
    aligned=recognize_template(fitted,tmp)
    check('template_alignment',aligned==TESTS)
    cert=certificate_from_template(fitted,tmp,aligned);model=verify_certificate(cert);canonical=verify_certificate(tmp)
    check('certificate_replay',model.verification['status']=='PASS')
    check('trace_in_observable_coordinates',model.mass==MASS)
    for state in [INITIAL,s.Matrix([1,1,0]),s.Matrix([1,0,-1])]:
        check('transported_embedding_'+str(list(state)),embedding(model.pencil,TESTS*state)==embedding(PENCIL,state))
    p,z1=canonical.condition_at('direct',R(1,2));q,z2=canonical.condition_at('rotated',-R(1,2),z1)
    check('first_density',p==R(13,16));check('first_posterior',z1==s.Matrix([1,R(12,13),0]))
    check('second_density',q==R(413,1040));check('second_posterior',z2==s.Matrix([1,-R(312,413),-R(240,413)]))
    check('joint_density',p*q==R(413,1280))
    check('posterior_determinant',embedding(PENCIL,z2).det()==R(15625,682276))
    check('density_can_exceed_one',canonical.condition_at('direct',1,s.Matrix([1,1,0]))[0]==4)
    rejects('zero_density_has_no_posterior',lambda:canonical.condition_at('direct',R(1,3),s.Matrix([1,-1,0])))
    rejects('non_normalized_state',lambda:canonical.condition_at('direct',0,s.Matrix([2,0,0])))
    rejects('outside_state_domain',lambda:canonical.condition_at('direct',0,s.Matrix([1,1,1])))
    check('reference_measure_rescaling',zero((BASE/2)*2-BASE))
    # Joint interval probability is a probability, unlike the listed point densities.
    plus=integral(BASE,0,1)
    joint=plus*ROT*plus*INITIAL
    check('two_interval_probability',joint[0]==R(107,320))
    check('two_interval_posterior',joint/joint[0]==s.Matrix([1,R(96,107),-R(24,107)]))
    # Finite moments do not identify a density outside its declared degree class.
    P3=(5*U**3-3*U)/2
    for j in range(3):check(f'legendre_unseen_moment_{j}',s.integrate(U**j*P3,(U,-1,1))==0)
    a=s.sqrt(R(3,5))
    l1=s.integrate(-P3,(U,0,a))+s.integrate(P3,(U,a,1))
    check('legendre_absolute_integral',s.simplify(l1)==R(13,40))
    check('legendre_endpoint_bounds',P3.subs(U,1)==1 and P3.subs(U,-1)==-1)
    check('legendre_critical_bounds',s.simplify(P3.subs(U,1/s.sqrt(5))**2)==R(1,5))
    # Conditional covariance of transformations recovers the exact bin kernel.
    c,h=s.symbols('c h',real=True)
    Kmid=K.subs(U,c);K1=coeffs(K,1)[1]
    averaged=s.integrate(K*J*K.T,(U,c-h/2,c+h/2))/h
    check('matrix_covariance_identity',zero(averaged-Kmid*J*Kmid.T-h*h*K1*J*K1.T/12))
    for n in [1,2,3,4,8]:
        avg_sum=s.zeros(3);mid_sum=s.zeros(3)
        for j in range(n):
            lo=-1+R(2*j,n);hi=-1+R(2*(j+1),n);mid=(lo+hi)/2
            A=integral(BASE,lo,hi);avg_sum+=A;mid_sum+=BASE.subs(U,mid)/n
            # Same polynomial identity but instantiated with rational endpoints.
            check(f'bin_{n}_{j}_positive_covariance',zero(embedding(PENCIL,A*z)-((hi-lo)/2)*(K.subs(U,mid)*J*K.subs(U,mid).T+(hi-lo)**2*K1*J*K1.T/12)))
        check(f'bin_{n}_mass',zero(MASS*avg_sum-MASS))
        check(f'bin_{n}_midpoint_defect',MASS*mid_sum==s.Matrix([[1-R(3,4*n*n),0,0]]))
    # Every bin word to length four: independent vector and matrix recurrences.
    branches=[]
    for a,B in OPERATORS.items():
        Apre=s.eye(2) if a=='direct' else W;w=1 if a=='direct' else R(1,5)
        for lo,hi in [(-1,0),(0,1)]:
            interval=R(hi-lo,2);mid=R(lo+hi,2);var=R((hi-lo)**2,12)
            C0=K.subs(U,mid)*Apre;C1=K1*Apre
            branches.append((integral(B,lo,hi),w*interval,C0,C1,var))
    count=0
    for depth in range(5):
        for word in product(range(len(branches)),repeat=depth):
            v=INITIAL;X=embedding(PENCIL,INITIAL)
            for j in word:
                A,w,C0,C1,var=branches[j];v=A*v;X=w*(C0*X*C0.T+var*C1*X*C1.T)
            if embedding(PENCIL,v)!=X or not psd(X):raise AssertionError(f'word mismatch {word}')
            count+=1
    check('all_binned_words_through_length_four',True,{'words_compared':count,'proof_scope':'finite instances only'})
    # Certificate negative controls. A malformed witness must be rejected.
    bad=deepcopy(cert);bad['actions']['direct']['positive_terms'][0]['weight']='-1'
    rejects('negative_weight',lambda:verify_certificate(bad))
    bad2=deepcopy(cert);bad2['actions']['direct']['operator_coefficients'][0][0][0]='99'
    rejects('mass_drift',lambda:verify_certificate(bad2))
    bad3=deepcopy(cert);bad3['actions']['direct']['positive_terms'][0]['coefficients'][0][0][0]='7'
    rejects('false_intertwining',lambda:verify_certificate(bad3))
    bad4=deepcopy(tmp);bad4['initial']=[['1'],['2'],['0']]
    rejects('invalid_initial',lambda:verify_certificate(bad4))
    bad5=deepcopy(tmp);bad5['embedding'][2]=bad5['embedding'][1]
    rejects('noninjective_embedding',lambda:verify_certificate(bad5))
    bad6=deepcopy(tmp);bad6['interior']=[['1'],['1'],['0']]
    rejects('interior_must_be_strict',lambda:verify_certificate(bad6))
    bad7=deepcopy(tmp);bad7['reference_measure']['density_wrt_lebesgue']='1'
    rejects('wrong_base_measure',lambda:verify_certificate(bad7))
    bad8=deepcopy(data);bad8['core'][2]=bad8['core'][1]
    rejects('singular_observable_core',lambda:fit_population_moments(bad8))
    for q in [0.5,True,'sqrt(2)','1/0','__import__("os")']:
        rejects('exact_coefficient_guard_'+str(q),lambda q=q:rational(q))
    rejects('fractional_moment_index',lambda:moment(R(1,2)))
    check('symbolic_integer_index_supported',moment(s.Integer(2))==R(1,3))
    # Measure-average error records for one example, not a universal risk estimate.
    tv_rows=[]
    for n in [1,2,4,8,16]:
        tv=density_tv_equal_bins(n)
        check(f'exact_density_smoothing_bound_{n}',bool(tv>=0) and bool(tv<=min(1,R(2,n))),{'tv_exact':str(tv),'n':n})
        tv_rows.append({'n':n,'total_variation_exact':str(tv),'total_variation':float(tv),'certified_upper_bound':float(min(1,R(2,n)))})
    output={'suite':'curved_continuous','passed':all(r['passed'] for r in records),
            'records':len(records),'exact':len(records),'float':0,'sampling':0,
            'elapsed_seconds':time.perf_counter()-start,'checks':records,
            'density_smoothing':tv_rows,'binned_words':count,
            'scope':'Written propositions carry the general arguments. This file checks finite instances.'}
    path=ROOT/'verification/curved_continuous_checks.json'
    path.write_text(json.dumps(output,indent=2)+'\n')
    print(f'PASS: {len(records)} exact records; {count} binned words in one grouped record.')
    print(f'Elapsed: {time.perf_counter()-start:.2f} s')
if __name__=='__main__':main()
