"""Exact constants for the separately written whole one-L/one-C proofs.
Author: Komorebi P. Positive-real samples; finite unit reference only.
"""
from fractions import Fraction as F
import json
from coefficient_fiber import certificate as fiber_certificate,fiber
from one_L_energy import interpolation,region,product
from pure_type_margins import SAMPLES,P,Q
from natural_graph_polynomials import value


def lagrange_bound(q,t):
    _,_,indices=interpolation(q)
    weights=[]
    for j in indices:
        L=product([(t-SAMPLES[k])/(SAMPLES[j]-SAMPLES[k]) for k in indices if k!=j])
        W=value([a+b for a,b in zip(P,Q)],SAMPLES[j])/2*max(F(1),SAMPLES[j]**q)
        weights.append((j,L,W))
    for e in range(q+3):assert sum(L*SAMPLES[j]**e for j,L,W in weights)==t**e
    return sum(abs(L)*W for j,L,W in weights)


def denominator_certificate(kind):
    if kind not in ('L','C'):raise ValueError('One L or one C required')
    eps=F(fiber_certificate(4)['coefficient_error_factor'])*F(1,10**11)
    B=(F(1,100)+5*eps)/3;r=F(1,60)-F(3,2)*B
    c=F(5,2) if kind=='L' else F(5)
    leading=6*(F(1,60)-B)-eps
    assert c*r-F(5,4)*eps>0 and leading>0
    return {'kind':kind,'sample_error_cap':'1/100000000000','natural_denominator':'P' if kind=='L' else 'Q',
      'imaginary_modulus_lower':'1/100','affine_error_upper':str(eps),'multiplier_coordinate_upper':str(B),
      'real_axis_positivity_factor':str(c*r-F(5,4)*eps),'quartic_leading_lower':str(leading),
      'dependency':'Written real-root theorem and coefficient projection; a small denominator would make a positive quartic without real roots.'}


def bounds(kind,q):
    if kind=='L':delta=F(1,10**(11 if q==3 else 30));eta=F(2,10**(7 if q==3 else 12));sigma=eta/2
    elif kind=='C':delta=F(1,10**(13 if q==3 else 37));eta=F(2,10**(7 if q==3 else 14));sigma=eta/(50 if q==3 else 25)
    else:raise ValueError('One L or one C required')
    if q not in (3,4):raise ValueError('Degree cap three/four required')
    inherited=F(1,10**6) if q==3 else F(1,10**(11 if kind=='L' else 13))
    assert delta+4*eta<inherited
    f=fiber_certificate(q);eps=F(f['coefficient_error_factor'])*delta
    distance=eps/(F(f['interior_minimum_coefficient'])+eps)
    vertices=[tuple(map(F,m)) for m in f['exact_nonnegative_fiber']['multiplier_vertices']]
    for m in vertices:
        x=fiber(q,m);p=x[:q+1];qq=x[q+1:]
        assert sum(p[:q-1])>=F(2,15) and sum(qq[:q-1])>=F(3,10) and sum(p[2:])>=F(1,5)
    assert F(2,15)-(q-1)*distance>=F(13,100)
    assert F(3,10)-(q-1)*distance>=F(29,100)
    assert F(1,5)-(q-1)*distance>=F(19,100)
    beta=F(1,13 if q==3 else 100);_,Ki,_=interpolation(q);e=Ki*delta/(3*beta)
    if q==3:
        assert F(13,1800)>F(1,144) and F(1,12)-4*distance>beta
    else:assert delta<=F(1,10**11)
    Klow=lagrange_bound(q,sigma);loss=(q-1)*sigma/eta
    result={'kind':kind,'reactive_budget':q,'margin':str(delta),'component_lower':str(eta),
      'component_upper':str(1/eta),'low_frequency':str(sigma),'inherited_margin':str(inherited),
      'rounding_error_upper':str(4*eta),'rounding_strict_slack':str(inherited-delta-4*eta),
      'fiber_distance_upper':str(distance),'imaginary_denominator_lower':str(beta),
      'imaginary_response_error_upper':str(e),'low_frequency_interpolation_factor':str(Klow)}
    if kind=='L':
        Ylow=value(Q,sigma)/value(P,sigma)-Klow*delta/(value(P,sigma)*F(13,100)*sigma**(q-2))
        Yupper=F(region(q)['DC_admittance_tradeoff_factor'])*delta+loss
        assert Ylow>Yupper
        result.update(positive_real_admittance_lower=str(Ylow),DC_trial_admittance_upper=str(Yupper),strict_slack=str(Ylow-Yupper))
    else:
        T=1/sigma;Khigh=lagrange_bound(q,T)
        r0=value(P,sigma)/value(Q,sigma)-Klow*delta/(value(Q,sigma)*F(29,100)*sigma**(q-2))-loss
        Yinf=value(Q,T)/value(P,T)-Khigh*delta/(value(P,T)*F(19,100)*T*T)-loss
        assert r0>e and Yinf>0 and 0<=e<1
        rinf=1/Yinf;assert (1-e)**2>rinf*e
        rhs=r0*(1+(1-e/r0)*(1-e*rinf/(1-e)**2))**2
        assert rinf<rhs
        result.update(high_frequency=str(T),high_frequency_interpolation_factor=str(Khigh),
          DC_resistance_lower=str(r0),infinite_admittance_lower=str(Yinf),infinite_resistance_upper=str(rinf),
          endpoint_inequality_RHS_lower=str(rhs),strict_slack=str(rhs-rinf))
    return result


def certificate():
    return {'status':'PASS','automatic_denominators':[denominator_certificate(k) for k in ('L','C')],
      'whole_class_margins':[bounds(k,q) for k in ('L','C') for q in (3,4)],
      'quantifiers':'Finite ordinary passive RLC graphs, positive finite values, arbitrary resistor count and placement, at most the stated reactive budget and at most one branch of the named kind; pure RC/RL and smaller budgets use stronger inherited margins. Maximum absolute reflection error over the same seven positive-real Laplace samples is strictly greater than the displayed margin.',
      'proof_dependencies':['Written one-kind quartic real-root theorem','Natural nonnegative graph coefficients and previous affine/nonnegative fiber theorem','Written one-L energy/DC trade-off','Written one-C endpoint inequality and endpoint-limit arguments','Written positive-real branch rounding plus inherited at-most-two-reactive margin'],
      'non_claims':['Finite exact checks alone are not universal proofs','The balanced two-L/two-C four-reactive class remains open','These tiny separation constants are not useful hardware tolerances','No new Lean, external review, priority or measurement claim']}


def verify(record):
    if record!=certificate():raise ValueError('Global typed-margin certificate binding differs')
    return {'status':'PASS'}


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(certificate(),indent=2))
