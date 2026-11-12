"""Komorebi P. Exact mixed RLC degree-two topology inversion.

A proof-producing candidate generator, NOT a complete general positive-real
biquadratic classifier. All parameter arithmetic is rational.

Search four equivalent orientations (duality and s->1/s) of
R0 + (R1 || (s*L + (R2 || 1/(s*C)))).

Exactly reconstructs component network and invokes an independent KCL verifier.
"""
from __future__ import annotations
from fractions import Fraction as F
from dataclasses import dataclass
import sys,json
from pathlib import Path
from algebraic_witness import verify_algebraic_circuit


def frac(x):
    if isinstance(x,(float,bool)):
        raise ValueError('Use exact rational values, not floating-point coefficients')
    return F(x)

def normalized(P,Q):
    P=[frac(x) for x in P];Q=[frac(x) for x in Q]
    while len(P)>1 and P[-1]==0:P.pop()
    while len(Q)>1 and Q[-1]==0:Q.pop()
    if len(P)!=3 or len(Q)!=3 or Q[-1]==0 or P[-1]==0:
        raise ValueError('This fast path requires numerator and denominator degree exactly two')
    if Q[-1]<0:P=[-x for x in P];Q=[-x for x in Q]
    return P,Q

@dataclass(frozen=True)
class Leaf:
    typ:str  # R/L/C
    value:F

@dataclass(frozen=True)
class Comp:
    op:str
    children:tuple

def series(*xs):return Comp('series',tuple(xs))
def parallel(*xs):return Comp('parallel',tuple(xs))
def R(x):return Leaf('R',frac(x))
def L(x):return Leaf('L',frac(x))
def C(x):return Leaf('C',frac(x))

def dual(t):
    """Network dual, reciprocal impedance, all component parameters positive."""
    if isinstance(t,Leaf):
        if t.typ=='R':return Leaf('R',1/t.value)
        if t.typ=='L':return Leaf('C',t.value)
        return Leaf('L',t.value)
    return Comp('parallel' if t.op=='series' else 'series',tuple(dual(x) for x in t.children))

def frequency_inverse(t):
    """Equivalent element circuit whose impedance is Z_old(1/s)."""
    if isinstance(t,Leaf):
        if t.typ=='R':return t
        if t.typ=='L':return Leaf('C',1/t.value)
        return Leaf('L',1/t.value)
    return Comp(t.op,tuple(frequency_inverse(x) for x in t.children))

def topology_tree(r0,r1,r2,l,c):
    body=parallel(R(r1),series(L(l),parallel(R(r2),C(c))))
    return series(R(r0),body) if r0>0 else body

def inverse_coefficients(P,Q):
    """Derive exact components of R0 + R1||(L + (R2||C)).
    The invariant F(R0)=0 is *linear* because quadratic terms cancel.
    Returns either a circuit or None. Not sufficient for general biquadratics.
    """
    a0,a1,a2=P;b0,b1,b2=Q
    f0=b0*a2*a2-b1*a1*a2+b2*a1*a1-b2*a0*a2
    f1=a0*b2*b2-a1*b1*b2-a2*b0*b2+a2*b1*b1
    if f1==0:
        if f0!=0:return None
        choices=[F(0),a2/(2*b2),a2/(4*b2)]
    else:
        choices=[-f0/f1]
    for x in choices:
        if x<0:continue
        aa0=a0-x*b0;aa1=a1-x*b1;aa2=a2-x*b2
        r1=aa2/b2
        t=b1*r1-aa1
        if min(r1,aa0,aa1,t)<=0:continue
        l=r1*r1*b2/t
        c=t/(aa0*r1)
        r2=aa0*r1*r1*b2/(aa1*t)
        if min(l,c,r2)<=0:continue
        # Identity is checked independently from graph topology by witness verifier.
        yield x,r1,r2,l,c

def graph(tree):
    """Create a two-terminal multigraph, then compact its node labels.
    Nodes port 1 and ground 0, fresh internal nodes 2,3,...
    """
    edges=[];next_id=2
    def add(t,a,b):
        nonlocal next_id
        if isinstance(t,Leaf):
            if t.value<=0:raise ValueError('Nonpositive leaf')
            edges.append([t.typ,a,b,t.value]);return
        if t.op=='parallel':
            for child in t.children:add(child,a,b)
        else:
            v=a
            for j,child in enumerate(t.children):
                w=b if j==len(t.children)-1 else next_id
                if j<len(t.children)-1:next_id+=1
                add(child,v,w);v=w
    add(tree,1,0)
    # A pair may have multiple branches of different types, but merge identical
    # type/pair branches before passing them to the strict independent verifier.
    merge={}
    for typ,a,b,v in edges:
        a,b=sorted((a,b));key=(typ,a,b)
        if key in merge:
            if typ=='R': merge[key]=1/(1/merge[key]+1/v)
            elif typ=='C':merge[key]+=v
            else:merge[key]=1/(1/merge[key]+1/v)
        else:merge[key]=v
    return [(typ,a,b,v) for (typ,a,b),v in merge.items()]

def circuit_certificate(P,Q,t):
    rows=[]
    for typ,a,b,value in graph(t):
        kind={'R':'g','L':'h','C':'c'}[typ]
        adm=value if kind=='c' else 1/value
        rows.append({'type':kind,'nodes':[a,b],'coefficient':[str(adm)]})
    q=sum(r['type']!='g' for r in rows)
    return {'format':'komorebi-algebraic-circuit-v1',
            'target':{'P':list(map(str,P)),'Q':list(map(str,Q))},
            'storage_budget':q,'field':{'polynomial':['0','1'],'interval':['-1','1']},
            'branches':rows}

def find_exact(P,Q):
    P,Q=normalized(P,Q)
    for inv in (False,True):
        for freq in (False,True):
            pp,qq=(list(Q),list(P)) if inv else (list(P),list(Q))
            if freq:pp=list(reversed(pp));qq=list(reversed(qq))
            if not qq[-1] or not pp[-1]:continue
            if qq[-1]<0:pp=[-a for a in pp];qq=[-a for a in qq]
            for vals in inverse_coefficients(pp,qq):
                t=topology_tree(*vals)
                if freq:t=frequency_inverse(t)
                if inv:t=dual(t)
                certificate=circuit_certificate(P,Q,t)
                try:
                    check=verify_algebraic_circuit(certificate,
                        expected_target={'P':P,'Q':Q},expected_budget=2)
                except ValueError:
                    continue
                if check['actual_storage']!=2 or check['reduced_target_degree']!=2:
                    continue
                return {'status':'CERTIFIED_MINIMUM','minimum_reactive_count':2,
                    'route':'exact 4/5-component mixed RLC canonical template',
                    'orientation':{'admittance_dual':inv,'frequency_inverted':freq},
                    'certificate':certificate,'verification':check,
                    'closed_form_parameters':[str(x) for x in vals]}
    return {'status':'UNKNOWN','reason':'No positive rational solution in this limited template family; not a nonexistence proof'}

if __name__=='__main__':
    target=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(find_exact(target['P'],target['Q']),indent=2))
