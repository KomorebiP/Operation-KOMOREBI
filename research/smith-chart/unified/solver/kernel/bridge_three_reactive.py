"""Author: Komorebi P. Fixed bridge q=3 inversion using exact elimination.

Topology (port 1, ground 0, internal 2,3): R12,R23,R02,C03,C23,L13.
The leading impedance coefficient immediately determines g12=Q3/P3.
DC ratio eliminates g02 as a rational function of g23. The remaining
coefficient equations reduce to bivariate rational equations in g23 and
1/C23. A univariate resultant proposes all RATIONAL candidate conductances.
Every accepted circuit is checked by the independent exact graph checker.

This is a sufficient q=3 chart. No global theorem of q=3 sufficiency or
nonexistence is inferred when it returns UNKNOWN.
"""
from __future__ import annotations
from fractions import Fraction as F
from real_algebraic import trim,gcd
from algebraic_witness import verify_algebraic_circuit


def toF(v):
    if hasattr(v,'p') and hasattr(v,'q'):return F(int(v.p),int(v.q))
    return F(v)


def synthesize_bridge_q3(P,Q,max_resultant_degree=40):
    import sympy as S
    P=trim(P);Q=trim(Q)
    if len(P)!=4 or len(Q)!=4 or len(gcd(P,Q))>1 or not all((P[0],Q[0],P[-1],Q[-1])):
        return {'status':'UNKNOWN','reason':'Requires reduced exact degree-three numerator and denominator with nonzero endpoints'}
    a=Q[3]/P[3];r=Q[0]/P[0]
    if a<=0 or r<=0 or P[2]/P[3]<=0:return {'status':'UNKNOWN','reason':'No positive endpoint parameters'}
    p0=P[0]/P[3];p1=P[1]/P[3];p2=P[2]/P[3];q1=Q[1]/P[3];q2=Q[2]/P[3]
    b,y=S.symbols('b y');sf=lambda x:S.Rational(x.numerator,x.denominator)
    av,rv,p0v,p1v,p2v,q1v,q2v=map(sf,(a,r,p0,p1,p2,q1,q2))
    v=av+b;c=rv*v/(v-rv);W=v+c
    X=(p2v-W*y)/(av+c)
    h=p0v/(W*X*y)
    fs=[b*(av+c)*X*y +p0v/(W*y)-p1v,
        av*(b+c)*y+av*c*X+h-q2v,
        av*b*c*X*y+h*(W*y+c*X)-q1v]
    try:
        nums=[S.Poly(S.together(expr).as_numer_denom()[0],b,y,domain=S.QQ).as_expr() for expr in fs]
        res=S.Poly(S.resultant(nums[0],nums[1],y),b,domain=S.QQ)
        if res.is_zero or res.degree()>max_resultant_degree:
            return {'status':'UNKNOWN','reason':'Resultant degenerate or exceeds symbolic degree cap'}
        roots=res.ground_roots()
    except Exception as e:
        return {'status':'UNKNOWN','reason':f'Exact elimination failed: {type(e).__name__}'}
    checked=0
    for bb in roots:
        bf=toF(bb)
        if bf<=0 or a+bf<=r:continue
        numer_poly=[]
        for expr in nums:
            try:numer_poly.append(S.Poly(expr.subs(b,bb),y,domain=S.QQ))
            except Exception:break
        if len(numer_poly)!=3:continue
        yg=S.gcd(S.gcd(numer_poly[0],numer_poly[1]),numer_poly[2]);yyroots=yg.ground_roots()
        for yy in yyroots:
            Y=toF(yy);v=a+bf
            if Y<=0 or v<=r:continue
            cF=r*v/(v-r);Wf=v+cF
            X=(p2-Wf*Y)/(a+cF)
            if X<=0:continue
            d=1/X;e=1/Y;hF=p0/(Wf*X*Y)
            if min(bf,cF,d,e,hF)<=0:continue
            # Coefficients are admittance parameters (not physical R/L values).
            branches=[('g',1,2,a),('g',2,3,bf),('g',0,2,cF),
                      ('c',0,3,d),('c',2,3,e),('h',1,3,hF)]
            cert={'format':'komorebi-algebraic-circuit-v1',
                 'target':{'P':list(map(str,P)),'Q':list(map(str,Q))},
                 'storage_budget':3,
                 'field':{'polynomial':['0','1'],'interval':['-1','1']},
                 'branches':[{'type':k,'nodes':[u,w],'coefficient':[str(z)]} for k,u,w,z in branches]}
            checked+=1
            try:vfy=verify_algebraic_circuit(cert,{'P':P,'Q':Q},3)
            except (ValueError,ZeroDivisionError):continue
            if vfy['actual_storage']!=3 or vfy['reduced_target_degree']!=3:continue
            return {'status':'CERTIFIED_MINIMUM','route':'exact bivariate-elimination bridge inverse (rational-root chart)',
                'minimum_reactive_count':3,'certificate':cert,'verification':vfy,
                'resultant_degree':res.degree(),'rational_root_candidates':len(roots),
                'tested_candidates':checked,'parameters':{'g12':str(a),'g23':str(bf),'g02':str(cF),
                             'C03':str(d),'C23':str(e),'reciprocal_L13':str(hF)}}
    return {'status':'UNKNOWN','reason':'No certified rational-positive bridge witness; does not exclude algebraic or other topologies',
           'resultant_degree':res.degree(),'rational_root_candidates':len(roots),'tested_candidates':checked}

if __name__=='__main__':
    import json,sys
    from pathlib import Path
    d=json.loads(Path(sys.argv[1]).read_text());print(json.dumps(synthesize_bridge_q3(d['P'],d['Q']),indent=2))
