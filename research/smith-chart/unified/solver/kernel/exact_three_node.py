"""Komorebi P. Exact algebraic inversion of a coupled three-node RLC network.

Topology: g01 || ((g12 || h12/s) in series with (g02 || s*c02))
when using branch impedances. In admittance form y01=g01,
y12=g12+h12/s, y02=g02+s*c02. Resistor conductances may be 0.

The remaining inverse equation is a QUADRATIC in g01. The resulting
components may be irrational algebraic numbers. Search uses SymPy to isolate
quadratic roots, while an independent standard-library verifier checks the
exact circuit, physical signs, algebraic root and target identity.

This is a template family, not a complete degree-two RLC synthesis theorem.
"""
from fractions import Fraction as F
from math import gcd
from functools import reduce
from pathlib import Path
import sys,json
from real_algebraic import RealField
from algebraic_witness import verify_algebraic_circuit
from exact_biquadratic_templates import (normalized,Leaf,Comp,series,parallel,
        dual,frequency_inverse)

def fstr(x):return str(F(x))
def to_F(x):return F(int(x.p),int(x.q)) if hasattr(x,'p') else F(x)

def roots_of_quadratic(p):
    """Yield (exact defining polynomial, strict rational interval).
    SymPy is a root candidate generator only. Sturm and positivity are
    independently checked later.
    """
    from sympy import Poly,Symbol,Rational
    from sympy.polys.polytools import intervals
    x=Symbol('x')
    P=Poly(sum(Rational(z.numerator,z.denominator)*x**i for i,z in enumerate(p)),x,domain='QQ')
    if P.degree() < 0:return
    if P.degree()==0:return
    for (a,b),mult in P.intervals(eps=Rational(1,2**32)):
        lo=to_F(a);hi=to_F(b)
        if lo==hi:
            yield [str(-lo),'1'],[str(lo-1),str(lo+1)]
        elif mult==1:
            yield list(map(str,p)),[str(lo),str(hi)]

def raw_tree(gA,gB,gC,h,c):
    E=gA.field
    mkR=lambda g:Leaf('R',1/g)
    tail1=[Leaf('L',1/h)]
    if gB.sign()>0:tail1.insert(0,mkR(gB))
    tail2=[Leaf('C',c)]
    if gC.sign()>0:tail2.insert(0,mkR(gC))
    chain=series(parallel(*tail1) if len(tail1)>1 else tail1[0],
        parallel(*tail2) if len(tail2)>1 else tail2[0])
    return parallel(mkR(gA),chain) if gA.sign()>0 else chain

def node_branches(tree):
    edges=[];next_id=2
    def add(t,a,b):
        nonlocal next_id
        if isinstance(t,Leaf):
            if t.value.sign()<=0:raise ValueError('Nonpositive component')
            aa,bb=sorted((a,b));edges.append((t.typ,aa,bb,t.value));return
        if t.op=='parallel':
            for c in t.children:add(c,a,b)
        else:
            prev=a
            for k,c in enumerate(t.children):
                nxt=b if k==len(t.children)-1 else next_id
                if k<len(t.children)-1:next_id+=1
                add(c,prev,nxt);prev=nxt
    add(tree,1,0)
    merged={}
    for kind,a,b,value in edges:
        key=(kind,a,b)
        if key not in merged:merged[key]=value
        elif kind=='C':merged[key]+=value
        else:merged[key]=1/(1/merged[key]+1/value)
    return [(kind,a,b,value) for (kind,a,b),value in merged.items()]

def cert(P,Q,tree,field_poly,field_interval):
    branches=[]
    for typ,a,b,value in node_branches(tree):
        outtype={'R':'g','L':'h','C':'c'}[typ]
        coefficient=value if typ=='C' else 1/value
        branches.append({'type':outtype,'nodes':[a,b], 'coefficient':coefficient.serialize()})
    return {'format':'komorebi-algebraic-circuit-v1',
        'target':{'P':list(map(str,P)),'Q':list(map(str,Q))},
        'storage_budget':sum(x['type']!='g' for x in branches),
        'field':{'polynomial':field_poly,'interval':field_interval},
        'branches':branches}

def inverse_candidates(P,Q):
    a0,a1,a2=P;b0,b1,b2=Q
    if not a1 or not a0 or not a2:return
    A=b2/a2;B=b0/a0;S=A+B;T=b1/a1;K=a0*a2/(a1*a1)
    # T*(S-2g)=A*B-g^2+K*(S-2g)^2
    # [4K-1]g^2 + [2T-4KS]g + [AB + KS^2 - TS]=0.
    p=[A*B+K*S*S-T*S,2*T-4*K*S,4*K-1]
    while len(p)>1 and p[-1]==0:p.pop()
    for field_poly,interval in roots_of_quadratic(p):
        try:
            field=RealField(field_poly,interval)
            g=field.element([0,1]);gB=field.element(A)-g;gC=field.element(B)-g
            M=field.element(S)-2*g
            h=field.element(a0/a1)*M;c=field.element(a2/a1)*M
            if min(x.sign() for x in (g,gB,gC,h,c))<0 or h.sign()<=0 or c.sign()<=0:
                continue
            yield raw_tree(g,gB,gC,h,c),field_poly,interval
        except (ValueError,ZeroDivisionError):continue

def find_exact_three_node(P,Q):
    P,Q=normalized(P,Q)
    for inv in (False,True):
        for freq in (False,True):
            pp,qq=(list(Q),list(P)) if inv else (list(P),list(Q))
            if freq:pp=list(reversed(pp));qq=list(reversed(qq))
            if pp[-1]==0 or qq[-1]==0:continue
            if qq[-1]<0:pp=[-t for t in pp];qq=[-t for t in qq]
            for tree,field_poly,interval in inverse_candidates(pp,qq):
                if freq:tree=frequency_inverse(tree)
                if inv:tree=dual(tree)
                c=cert(P,Q,tree,field_poly,interval)
                try:check=verify_algebraic_circuit(c,{'P':P,'Q':Q},2)
                except (ValueError,ZeroDivisionError):continue
                if check['actual_storage']!=2 or check['reduced_target_degree']!=2:continue
                return {'status':'CERTIFIED_MINIMUM','route':'exact quadratic algebraic inverse on three-node mixed RLC family',
                    'minimum_reactive_count':2,'orientation':{'admittance_dual':inv,'frequency_inverted':freq},
                    'certificate':c,'verification':check}
    return {'status':'UNKNOWN','reason':'No acceptable positive root in the limited coupled three-node template family'}

if __name__=='__main__':
    data=json.loads(Path(sys.argv[1]).read_text());print(json.dumps(find_exact_three_node(data['P'],data['Q']),indent=2))
