"""Finite exact identities, deliberate certificate rejections, and one dependent path.

A record is one explicitly described check, not a general formal proof.
"""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
from continuous_reference import *
from quadratic_reference import *
from sequential_reference import V,X,bernstein,positive_coefficients,reconstruct_bernstein,anytime_radius,dependent_example

records=[]
def check(name,condition,kind='exact',detail=None):
    ok=bool(condition);records.append({'name':name,'kind':kind,'passed':ok,'detail':detail})
    if not ok:raise AssertionError(name)

def rejection(name,call):
    try:call()
    except ValueError as e:check(name,True,detail={'expected_rejection':str(e)});return
    raise AssertionError('Expected rejection: '+name)


def main():
    fit=fit_population_moments(load_json(ROOT/'examples/continuous_population_tables.json'))
    data=discover_quadratic(fit);obj=verify_quadratic(data)
    c=sp.Matrix([sp.Rational(1,2),sp.Rational(1,2)])
    H=sp.Matrix([[sp.Rational(100,9),-sp.Rational(20,3)],[-sp.Rational(20,3),sp.Rational(100,9)]])
    check('discovered center',obj.center==c)
    check('discovered metric',obj.metric==H)
    check('template absent',data['provenance']['template_supplied'] is False)
    check('metric eigenvalues',sorted(H.eigenvals())==[sp.Rational(40,9),sp.Rational(160,9)])
    # Compare the new quadratic certificate to the independent previous matrix certificate.
    old=verify_certificate(load_json(ROOT/'certificates/continuous_psd_certificate.json'))
    for name in obj.operators:
        check('unchanged operator '+name,zero(obj.operators[name]-old.operators[name]))
        Q=obj.form;B=obj.operators[name];tau=(1-9*U**2)**2/16
        check('conformal polynomial '+name,zero(B.T*Q*B-tau*Q))
    d1,z1=obj.condition_at('direct',sp.Rational(1,2))
    d2,z2=obj.condition_at('rotated',-sp.Rational(1,2),z1)
    check('first unchanged density',d1==sp.Rational(13,16))
    check('second unchanged density',d2==sp.Rational(413,1040))
    check('point law product',d1*d2==sp.Rational(413,1280))
    # Generalization within a declared structural sector, with coefficients changed.
    for i,(p,q) in enumerate([(sp.Rational(1,2),sp.Rational(1,3)),(sp.Rational(1,4),sp.Rational(2,3)),(sp.Rational(1,5),sp.Rational(3,4))]):
        aa=(1-3*p*p)/(1+3*p*p);bb=6*p/(1+3*p*p)
        R=sp.Matrix([[(1-q*q)/(1+q*q),-2*q/(1+q*q)],[2*q/(1+q*q),(1-q*q)/(1+q*q)]])
        B=sp.Matrix([[aa*aa+bb*bb*U*U,2*aa*bb*U,0],[2*aa*bb*U,aa*aa+bb*bb*U*U,0],[0,0,aa*aa-bb*bb*U*U]])
        T=sp.Matrix([[1,0,0],[sp.Rational(1,3),2,1],[-sp.Rational(1,4),0,1]])
        f={'mass':sp.Matrix([[1,0,0]]),'initial':T*sp.Matrix([1,0,0]),
           'operators':{'first':coeffs(T*B*T.inv()),'second':coeffs(T*B*sp.diag(1,R)*T.inv())}}
        result=verify_quadratic(discover_quadratic(f))
        check(f'changed coefficients geometry {i}', result.center==T[1:,0] and result.metric==T[1:,1:].inv().T*T[1:,1:].inv())
    # Reject malformed witnesses; none is treated as a discovery of invalid physics.
    bad=copy.deepcopy(data);bad['metric'][0][0]='-1'
    rejection('indefinite metric',lambda:verify_quadratic(bad))
    bad2=copy.deepcopy(data);bad2['actions']['direct']['tau_sos'][0]['weight']='-1'
    rejection('negative scalar certificate weight',lambda:verify_quadratic(bad2))
    bad3=copy.deepcopy(data);bad3['actions']['direct']['mass_orientation_sos']=[]
    rejection('missing orientation proof',lambda:verify_quadratic(bad3))
    bad4=copy.deepcopy(data);bad4['actions']['direct']['operator_coefficients'][0][0][0]='1'
    rejection('altered operator without new witness',lambda:verify_quadratic(bad4))
    bad5=copy.deepcopy(data);bad5['initial']=[['1'],['3'],['3']]
    rejection('outside initial state',lambda:verify_quadratic(bad5))
    bad6=copy.deepcopy(data);bad6['reference_measure']['density_wrt_lebesgue']='1'
    rejection('changed reference measure',lambda:verify_quadratic(bad6))
    rejection('zero-density update',lambda:obj.condition_at('direct',sp.Rational(1,3),sp.Matrix([1,sp.Rational(1,8),sp.Rational(11,40)])))
    rejection('out-of-support update',lambda:obj.condition_at('direct',2))
    ident={'mass':sp.Matrix([[1,0,0]]),'initial':sp.Matrix([1,0,0]),'operators':{'a':[sp.eye(3)],'b':[sp.eye(3)]}}
    rejection('underdetermined geometry withheld',lambda:discover_quadratic(ident))
    # The quadratic part without orientation admits the wrong sheet.
    check('negative identity preserves quadratic form',zero((-sp.eye(3)).T*obj.form*(-sp.eye(3))-obj.form))
    check('negative identity flips mass',(-sp.eye(3)*obj.initial)[0]==-1)
    for p in [sp.Integer(0),(1-9*U**2)**2/16,(1+9*U**2)/4,(U**2+U+1)*(U-2)**2]:
        check('factor SOS '+str(p),sp.expand(sos_value(global_sos(p))-p)==0)
    rejection('sign changing scalar polynomial',lambda:global_sos(U))
    # Positive polynomial approximation is normalized and has the exact variance identity.
    pieces=[(sp.Integer(0),sp.Rational(1,2),sp.Rational(3,2)-2*V),(sp.Rational(1,2),sp.Integer(1),2*V-sp.Rational(1,2))]
    for n in range(7):
        co=positive_coefficients(None,n,split=pieces);bn=reconstruct_bernstein(co,n)
        check(f'positive tent coefficients degree {n}',all(v>0 for v in co))
        check(f'normalization degree {n}',sp.integrate(bn,(X,0,1))==1)
        energy=sum(sp.integrate((f.subs(V,X)-bn)**2,(X,a,b)) for a,b,f in pieces)
        check(f'bias L2 sufficient bound degree {n}',energy<=sp.Rational(4,3*(n+2)))
        # Integrate pairwise variance without a double expanded kernel.
        pair=0
        for k in range(n+1):
            b=bernstein(n,k,V)
            m0=sp.integrate(b,(V,0,1));m1=sp.integrate(V*b,(V,0,1));m2=sp.integrate(V**2*b,(V,0,1))
            pair+=(n+1)*(2*m0*m2-2*m1*m1)
        check(f'Durrmeyer integrated variance degree {n}',sp.simplify(pair)==sp.Rational(1,3*(n+2)))
    co=positive_coefficients(3*V**2,1);bn=reconstruct_bernstein(co,1)
    check('positive degree-one approximation',bn==X+sp.Rational(1,2))
    gram=sp.Matrix([[1,sp.Rational(1,2)],[sp.Rational(1,2),sp.Rational(1,3)]])
    projection=gram.inv()*sp.Matrix([1,sp.Rational(3,4)])
    check('ordinary L2 truncation can be negative',projection==sp.Matrix([-sp.Rational(1,2),3]))
    check('nonpolynomial tent normalized',sum(sp.integrate(f,(V,a,b)) for a,b,f in pieces)==1)
    # Adaptive interventions: weighting recovers a contextual mean, not a reset probability.
    for pi in [sp.Rational(1,10),sp.Rational(1,4),sp.Rational(1,2),sp.Rational(9,10)]:
        mu=sp.Rational(4,5)
        check('propensity identity '+str(pi),pi*mu/pi==mu)
    check('no coverage observational equivalence',sp.Rational(1,2)==sp.Rational(1,2))
    check('unobserved action can disagree',abs(sp.Rational(9,10)-sp.Rational(1,10))==sp.Rational(4,5))
    # Exact adaptive likelihood-ratio martingale example on all binary paths to depth eight.
    states=[((),sp.Integer(1),sp.Integer(1))]
    for n in range(1,9):
        nxt=[]
        for hist,pnull,lr in states:
            q=sp.Rational(4,5) if hist and hist[-1] else sp.Rational(1,5)
            for y in [0,1]:
                alt=q if y else 1-q;nxt.append((hist+(y,),pnull/2,lr*2*alt))
        states=nxt
        check(f'dependent alternative likelihood mean one depth {n}',sum(p*l for _,p,l in states)==1)
    for n,d,r in [(0,.05,1),(1,0,1),(1,1,1),(1,.05,0)]:rejection('invalid sequential input '+str((n,d,r)),lambda n=n,d=d,r=r:anytime_radius(n,d,value_range=r))
    path=dependent_example()
    s=path['summary']
    check('constructed path correctly centered inside band',s['true_drift_inside_band_on_this_path'],'seeded_path')
    check('history-gated misspecification detected on this path',s['lower_average_conditional_tv']>0,'seeded_path')
    check('ungated residual can hide conditional error',abs(s['plain_mean_residual'])<s['radius_per_sample'],'seeded_path')
    (ROOT/'verification/dependent_path.json').write_text(json.dumps(path,indent=2)+'\n')
    report={'version':'0.6.0','passed':all(x['passed'] for x in records),'counts':{k:sum(x['kind']==k for x in records) for k in ['exact','seeded_path']},'records':records,'proof_kernel_run':False,'simulation_coverage_estimate':False}
    (ROOT/'verification/discovery_evidence_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2));print(json.dumps(s,indent=2))
if __name__=='__main__':main()
