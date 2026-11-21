"""Exact finite independent checks for polynomial resolvent enclosures."""
import argparse,itertools,json
from fractions import Fraction as F
from pathlib import Path
import sympy as S
from polynomial_certificate import geometry,candidate,polynomials,evaluate,value,bernstein,leaves,cubic_envelope,bounds
from interval_certificate import endpoint,cell,evaluate as linear_evaluate

def rational(x):return F(str(S.cancel(x)))
def pair(z):
    a,b=S.expand_complex(S.cancel(z)).as_real_imag();return rational(a),rational(b)
def point(E,eta,g,r=F(0),delta=F(0)):
    re,im=pair(g);return dict(energy=str(E),eta=str(eta),center=dict(real=str(re+delta),imaginary=str(im)),radius=str(r))
def bezier(b,t):
    from math import comb
    return sum(x*comb(len(b)-1,j)*t**j*(1-t)**(len(b)-1-j) for j,x in enumerate(b))
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True)
    cases=[(S.Matrix([[0]]),S.Matrix([1])),(S.Matrix([[-2,1],[1,3]]),S.Matrix([1,-1])),(S.Matrix([[0,1+S.I],[1-S.I,2]]),S.Matrix([1,S.I])),(S.Matrix([[1,1,0],[1,-1,2],[0,2,3]]),S.Matrix([1,0,-1]))]
    stencils=[(F(0),F(1)),(F(-1),F(0),F(1)),(F(0),F(1),F(2)),(F(-1),F(0),F(1),F(2)),(F(0),F(1),F(2),F(3)),(F(-2),F(-1),F(0),F(1))]
    identities=inclusions=linear_checks=uniform_checks=display_checks=0
    for H,b in cases:
        assert H==H.conjugate().T
        for eta,h in itertools.product([F(1,10),F(1,2)],[F(1,10),F(1,2)]):
            saved={}
            def R(E):
                if E not in saved:saved[E]=(S.Rational(E.numerator,E.denominator)*S.eye(H.rows)+S.I*S.Rational(eta.numerator,eta.denominator)*S.eye(H.rows)-H).inv()
                return saved[E]
            for nodes in stencils:
                energies=[h*x for x in nodes];points=[point(E,eta,(b.conjugate().T*R(E)*b)[0],F(1,10000),F((-1)**j,10000)) for j,E in enumerate(energies)];i=nodes.index(F(0));record=candidate(points,list(range(len(nodes))),i);L,_,P=geometry(nodes)
                real,imag,radius=polynomials(points,record['stencil'],i,F(record['coefficient']));n=len(nodes)
                for t in [F(0),F(1,4),F(1,2),F(3,4),F(1)]:
                    E=h*t;interpolant=S.zeros(H.rows);product=R(E)
                    for j,Ea in enumerate(energies):interpolant+=S.Rational(value(L[j],t).numerator,value(L[j],t).denominator)*R(Ea);product=product*R(Ea)
                    factor=(-1)**n
                    for Ea in energies:factor*=E-Ea
                    difference=R(E)-interpolant-S.Rational(factor.numerator,factor.denominator)*product
                    assert all(S.cancel(x)==0 for x in difference);identities+=1
                    actual=pair((b.conjugate().T*R(E)*b)[0]);result=evaluate(points,record,i,t);c=result['center'];r=F(result['radius'])
                    assert r>=0 and (actual[0]-F(c['real']))**2+(actual[1]-F(c['imaginary']))**2<=r*r;inclusions+=1
                    assert r<=F(record['uniform_radius']);uniform_checks+=1
                    if n==2:
                        c0=cell(endpoint(points[0]['energy'],eta,points[0]['center'],points[0]['radius']),endpoint(points[1]['energy'],eta,points[1]['center'],points[1]['radius']));old=linear_evaluate(c0,t)
                        assert old['center']==result['center'] and F(old['radius'])<=r;linear_checks+=1
                for f in [(F(0),),(-F(1),F(2)),real,imag,radius,tuple(-x for x in imag)]:
                    for part in leaves(bernstein(f,max(3,len(f)-1))):
                        controls,padding=cubic_envelope(part)
                        for t in [F(j,16) for j in range(17)]:assert abs(bezier(part,t)-bezier(controls,t))<=padding;display_checks+=1
    # A zero-source Hermitian example makes signed radius interpolation invalid:
    # L_0(1/2)<0, while a valid endpoint disk has a positive real-center error.
    nodes=(F(-1),F(0),F(1),F(2));L,_,_=geometry(nodes);signed=value(L[0],F(1,2));assert signed<0 and abs(signed)>signed
    points=[dict(energy=str(x),eta='1',center=dict(real='1' if j==0 else '0',imaginary='0'),radius='1' if j==0 else '0') for j,x in enumerate(nodes)];r=candidate(points,list(range(4)),1);p0=evaluate(points,r,1,F(1,2));assert F(p0['radius'])>=abs(F(p0['center']['real']))
    invalid=0
    for ns in [(F(0),F(0)),(F(0),F(1,2),F(1)),(F(0),F(2))]:
        try:geometry(ns)
        except ValueError:invalid+=1
    assert invalid==3
    report=dict(status='passed',exact_operator_identities=identities,exact_response_inclusions=inclusions,uniform_point_checks=uniform_checks,legacy_linear_cross_checks=linear_checks,exact_display_envelope_checks=display_checks,signed_radius_counterexample=True,invalid_stencils_rejected=invalid,complex_hermitian_cases=True,scope='Deterministic finite exact tests; analytic interpolation and Bernstein proofs remain separate; project self-review')
    (a.output/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))
if __name__=='__main__':main()
