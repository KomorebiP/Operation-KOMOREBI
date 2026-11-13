"""Passive physical counterexamples to sample-domain shortcuts. Author: Komorebi P.

These examples use six/seven reactive branches; they are NOT counterexamples
to a three/four-branch separator. Their reduced degrees are three/four.
"""
from fractions import Fraction as F
from exact_phasor import C,response,target_gamma
from pure_type_margins import P,Q,SAMPLES


def hughes_port_at_five():
    return [('L',5,2,F(1)),('R',2,0,F(4,9)),('R',5,3,F(1)),
            ('L',2,4,F(8,31)),('L',3,4,F(169,186)),
            ('C',3,4,F(186,169)),('C',4,0,F(31,8))]


def example(kind,epsilon):
    if not 0<epsilon:raise ValueError('Positive epsilon required')
    edges=hughes_port_at_five()
    if kind=='DC':edges.append(('C',1,5,1/epsilon))
    elif kind=='infinity':edges.append(('L',1,5,epsilon))
    elif kind=='resonance':edges.extend([('L',1,5,epsilon),('C',1,5,1/epsilon),('R',1,5,1/epsilon)])
    else:raise ValueError('Unknown barrier')
    return edges


def check_example(kind,epsilon):
    edges=example(kind,epsilon);error=F(0);comparisons=0
    frequencies=[C(s) for s in SAMPLES]+[C(0,F(1,2)),C(0,1),C(0,2)]
    for s in frequencies:
        h=target_gamma(P,Q,s);Z=(1+h)/(1-h)
        added=epsilon/s if kind=='DC' else epsilon*s if kind=='infinity' else epsilon*s/(s*s+epsilon*epsilon*s+1)
        expected=(Z+added-1)/(Z+added+1)
        actual=response(edges,s)['gamma'];assert actual==expected
        if not s.im:error=max(error,abs(actual.re-h.re));assert not actual.im
        comparisons+=1
    bound=epsilon if kind=='resonance' else 4*epsilon
    assert error<=bound
    result={'kind':kind,'epsilon':str(epsilon),'physical_reactive_branches':sum(k!='R' for k,_,_,_ in edges),
      'reduced_rational_degree':4 if kind=='resonance' else 3,'maximum_seven_sample_error':str(error),
      'analytic_sample_error_upper_bound':str(bound),'independent_nodal_comparisons':comparisons}
    if kind=='resonance':
        d=response(edges,C(0,1))['gamma']-C(0,1);assert d.normsq()==2/(1+2*epsilon+2*epsilon*epsilon)
        assert d.normsq()>F(199,100)
        result['resonant_reflection_error_squared']=str(d.normsq())
    else:
        # Endpoints follow from the positive series branch: an open at the
        # relevant endpoint has Gamma=1. The unmodified target is 4/9 or 1.
        result['endpoint_reflection_error']=str(F(18,13) if kind=='DC' else F(1))
    return result
