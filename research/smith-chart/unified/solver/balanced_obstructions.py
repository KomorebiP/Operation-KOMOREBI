"""Three exact balanced counterexamples to scalar/first-jet shortcuts.
Author: Komorebi P. They are not Hughes realizations or close-fit examples.
"""
from fractions import Fraction as F
from exact_phasor import C,response as reference
from phasor_unit_voltage import response
from natural_graph_polynomials import pair,value
from real_root_constraints import real_roots_with_multiplicity as roots,gcd,derivative
from coefficient_fiber import multiply
from pure_type_margins import P as PH,Q as QH,SAMPLES,gamma


def controls():
    from resonant_mode_face import find_modes
    ti=C(0,1);tq=value(QH,ti)
    assert value(PH,ti)/tq==ti
    assert (value(derivative(PH),ti)*tq-value(PH,ti)*value(derivative(QH),ti))/(tq*tq)==C(5)
    examples=[
      [('L',1,2,F(1)),('C',2,0,F(2)),('C',1,3,F(1,2)),('L',3,0,F(1)),('R',2,3,F(1))],
      [('R',1,2,F(4,5)),('R',0,3,F(1)),('L',1,3,F(1)),('L',0,2,F(1)),('C',2,3,F(1)),('C',1,2,F(1))],
      [('L',1,2,F(1)),('C',2,3,F(1)),('L',3,4,F(2)),('C',4,0,F(1)),('R',1,3,F(5,9)),('R',2,0,F(4,9))]]
    rows=[]
    for j,g in enumerate(examples):
        p=pair(g);P,Q=p['P'],p['Q'];qi=value(Q,C(0,1));pi=value(P,C(0,1));imag=response(g,C(0,1))
        assert not find_modes(g)
        assert 1/imag['Y']==C(0,1) and reference(g,C(0,1))['gamma']==C(0,1)
        assert all(not a for (k,u,v,x),a in zip(g,imag['current']) if k=='R')
        ends=(P[0]/Q[0],P[-1]/Q[-1]);assert ends==((F(1),F(1)) if j==0 else (F(4,9),F(1)))
        err=max(abs((value(P,s)-value(Q,s))/(value(P,s)+value(Q,s))-gamma(s)) for s in SAMPLES)
        assert err==(F(260,1221),F(720,11999),F(5175,65083))[j]
        jet=(value(derivative(P),C(0,1))*qi-pi*value(derivative(Q),C(0,1)))/(qi*qi)
        counts=[roots(P),roots(Q)]
        if j==1:assert counts==[0,0] and len(gcd(P,Q))==1
        if j==2:
            assert jet==C(5)
            assert [a-b for a,b in zip(multiply(P,QH),multiply(Q,PH))]==[F(69,263)*a for a in (0,1,0,2,0,1,0)]
        rows.append({'control':j+1,'edges':[[k,u,v,str(x)] for k,u,v,x in g],
          'natural_P':list(map(str,P)),'natural_Q':list(map(str,Q)),
          'Z0':str(ends[0]),'Zinf':str(ends[1]),'Zi':'i','Re_Zi':'0',
          'Zprime_i':[str(jet.re),str(jet.im)],'real_root_counts':counts,'seven_sample_error':str(err)})
    # Orthogonal exact positivity identities for the second control's quartics.
    p=[4*x for x in multiply([F(9,13),F(13,8),F(1)],[F(9,13),F(13,8),F(1)])]
    p[2]+=F(187,208);p[0]+=F(352,169);assert p==[4,9,17,13,4]
    q=[4*x for x in multiply([F(9,10),F(9,8),F(1)],[F(9,10),F(9,8),F(1)])]
    for k,x in enumerate(multiply([F(396,379),F(1)],[F(396,379),F(1)])):q[k]+=F(379,80)*x
    q[0]+=F(5571,9475);assert q==[9,18,17,9,4]
    return {'status':'PASS','controls':rows,'strict_positive_quartic_SOS_identities':2,
      'refuted_shortcuts':['One-C scalar endpoint inequality extended to balanced graphs',
        'A real root in either natural polynomial forced by zero driven loss and target endpoints',
        'Target endpoints, Zi and first resonance derivative determine the balanced response'],
      'non_claims':['None is a target realization or close-fit counterexample','No balanced whole-class margin follows from these finite controls']}
