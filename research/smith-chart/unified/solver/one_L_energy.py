"""Exact regional separators from the written one-L energy inequality.
Author: Komorebi P. No claim for excluded denominator/cancellation regions.
"""
from fractions import Fraction as F
from itertools import combinations
from math import isqrt
import json
from exact_phasor import C
from pure_type_margins import SAMPLES,P,Q,gamma
from coefficient_fiber import certificate as fiber_certificate


def product(values):
    out=1
    for v in values:out=out*v
    return out


def sqrt_upper(x,D=10**12):
    if x<0:raise ValueError('Nonnegative square-root argument required')
    k=isqrt(x.numerator*D*D//x.denominator)
    if k*k*x.denominator<x.numerator*D*D:k+=1
    out=F(k,D);assert out*out>=x
    return out


def interpolation(q):
    choices=[]
    for indices in combinations(range(7),q+3):
        K0=Ki=F(0);basis=[]
        for j in indices:
            s=SAMPLES[j];W=sum(F(a+b)*s**e for e,(a,b) in enumerate(zip(P,Q)))/2*max(F(1),s**q)
            L0=product([-SAMPLES[k]/(s-SAMPLES[k]) for k in indices if k!=j])
            Li=product([(C(0,1)-SAMPLES[k])/(s-SAMPLES[k]) for k in indices if k!=j])
            K0+=abs(L0)*W;Ki+=(abs(Li.re)+abs(Li.im))*W;basis.append((j,L0,Li))
        for e in range(q+3):
            assert sum(L0*SAMPLES[j]**e for j,L0,Li in basis)==int(e==0)
            assert sum((Li*SAMPLES[j]**e for j,L0,Li in basis),C())==C.make(product([C(0,1)]*e))
        choices.append((Ki,K0,indices))
    Ki,K0,indices=min(choices)
    return K0,Ki,indices


def region(q):
    if q not in (3,4):raise ValueError('Degree three/four required')
    delta=F(1,10**(9 if q==3 else 11));beta=F(1,13 if q==3 else 100)
    K0,Ki,indices=interpolation(q)
    e=Ki*delta/(3*beta);e0=15*K0*delta
    Y0lo=F(1,4);Yslo=F(23,14)-6*delta;Yshi=F(23,14)+6*delta
    assert 0<=e<Y0lo and delta<=F(1,4)
    assert F(9,4)-e0>Y0lo
    ratio=sqrt_upper(e/Y0lo);assert ratio<1
    A_lower=(Yslo+F(1,2)*(1-e))/F(5,4)
    RHS=Yshi/(1-ratio)+sqrt_upper(Yshi*e/F(5,4));assert A_lower>RHS
    tradeoff_ratio=sqrt_upper(F(1,1000));assert tradeoff_ratio<1
    tradeoff_RHS=Yshi/(1-tradeoff_ratio)+sqrt_upper(Yshi*e/F(5,4))
    assert A_lower>tradeoff_RHS
    tradeoff_factor=1000*Ki/(3*beta);assert tradeoff_factor*delta<F(1,4)
    # The fixed sample h(1/2) is the smallest h on this set.
    hmin=min(map(gamma,SAMPLES));assert 2/((1+hmin-F(1,4))*(1+hmin))<6
    inferred=None
    if q==3:
        old=fiber_certificate(3);eps=F(old['coefficient_error_factor'])*delta
        eta=eps/(F(old['interior_minimum_coefficient'])+eps)
        assert F(13,1800)>F(1,144) and F(1,12)-4*eta>beta
        inferred={'nonnegative_fiber_distance':str(eta),'P_i_lower':str(F(1,12)-4*eta),
                  'meaning':'No separate resonant-denominator guard is required at degree three.'}
    return {'degree_cap':q,'margin':str(delta),'sample_indices_for_interpolation':list(indices),
      'K0':str(K0),'Ki':str(Ki),'DC_admittance_lower_guard':'1/4',
      'DC_impedance_guard':'0 < Z(0) <= 4','sufficient_DC_P0_guard':'1/60',
      'P_i_guard':None if q==3 else '1/100','working_P_i_lower':str(beta),
      'resonant_guard_inferred':inferred,'loss_upper':str(e),'optional_P0_DC_error_upper':str(e0),
      'Re_A_lower':str(A_lower),'energy_RHS_upper':str(RHS),'strict_slack':str(A_lower-RHS),
      'DC_admittance_tradeoff_factor':str(tradeoff_factor),
      'tradeoff_RHS_upper':str(tradeoff_RHS),'tradeoff_strict_slack':str(A_lower-tradeoff_RHS)}


def certificate():
    k=F(region(3)['DC_admittance_tradeoff_factor'])
    example=1/(k*F(1,10**10));assert example>48
    return {'status':'PASS','regions':[region(3),region(4)],
      'universal_energy_scope':'One L, arbitrary C/R; unit-voltage phasors at s>0 and i, finite DC admittance Y0, E=Re Y(i)<Y0. Written Green/Dirichlet/cut proof; finite controls are separate.',
      'energy_inequality':'abs((Ys+i*s*Yi)/(1+s^2)) <= Ys/(1-sqrt(E/Y0)) + sqrt(Ys*E/(1+s^2))',
      'zero_loss_corollary':'One L, finite positive DC impedance and a finite nonzero loss-free imaginary-frequency phasor solution force negative imaginary impedance. No finite-positive infinity endpoint is needed for the sign; this weaker endpoint hypothesis does not force Z(i)=-i*L.',
      'regional_scope':'At q<=3, 0<Z(0)<=4 gives margin 1e-9. At q<=4, also abs(P(i))>=1/100 for the natural normalized graph pair gives margin 1e-11. Arbitrary resistor count; at most one L, with the zero-L class covered separately by its stronger RC margin. The sufficient P(0)>=1/60 test can establish the DC guard for a proposed close fit but is not necessary.',
      'tradeoff_scope':'For 0<delta<=the listed margin, any one-L fit with error <=delta has finite DC admittance Y0 < tradeoff_factor*delta. A DC short is separately excluded by the already accepted terminal-L/RC margin. At q=4 the listed P(i) guard is still required; q=3 needs no coefficient guard.',
      'degree_three_tradeoff_example':{'sample_error_upper':'1/10000000000','DC_resistance_strict_lower':str(example),'target_DC_resistance':'4/9'},
      'finite_solution_bridge':'The regional bounds make the natural port Dirichlet determinant nonzero at i and the DC admittance finite positive, so the required phasor hypotheses follow in these regions.',
      'non_claims':['No uniform whole-template margin','No elimination of the DC and degree-four resonant cancellation regions','No new Lean, independent review, hardware or novelty claim']}


def verify(record):
    if record!=certificate():raise ValueError('One-L regional certificate binding differs')
    return {'status':'PASS'}


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(certificate(),indent=2))
