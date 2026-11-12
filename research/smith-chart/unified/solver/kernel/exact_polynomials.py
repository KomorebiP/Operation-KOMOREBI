"""Author: Komorebi P. Sparse rational polynomials and exact refutation checking.
Only the Python standard library is used. Search code is outside this kernel.
"""
from __future__ import annotations
from fractions import Fraction as F
import hashlib, json, re

NAME = re.compile(r'^[A-Za-z_][A-Za-z_0-9]*$')

def rational(x):
    if isinstance(x, bool) or isinstance(x, float):
        raise ValueError('Use an integer or an exact rational string, never a float')
    return F(x)

def clean(p):
    return {m:rational(c) for m,c in p.items() if c}

def const(c):
    c=rational(c)
    return {():c} if c else {}

def var(name):
    if not NAME.fullmatch(name): raise ValueError('Invalid variable name')
    return {((name,1),):F(1)}

def add(*ps):
    out={}
    for p in ps:
        for m,c in p.items(): out[m]=out.get(m,F(0))+c
    return clean(out)

def scale(p,a):
    a=rational(a)
    return clean({m:c*a for m,c in p.items()})

def sub(p,q): return add(p,scale(q,-1))

def mul(p,q):
    out={}
    for a,c in p.items():
        for b,d in q.items():
            z=dict(a)
            for name,e in b:z[name]=z.get(name,0)+e
            m=tuple(sorted(z.items()))
            out[m]=out.get(m,F(0))+c*d
    return clean(out)

def power(p,k):
    if not isinstance(k,int) or k<0:raise ValueError('Nonnegative power required')
    out=const(1)
    while k:
        if k&1:out=mul(out,p)
        p=mul(p,p);k//=2
    return out

def square(p):return mul(p,p)

def degree(p): return max((sum(e for _,e in m) for m in p),default=-1)

def variables(p):return {name for m in p for name,_ in m}

def dump(p):return [[str(c),[[name,e] for name,e in m]] for m,c in sorted(p.items())]

def load(data,allowed=None):
    if not isinstance(data,list):raise ValueError('Polynomial must be a term list')
    out={}
    for row in data:
        if not isinstance(row,list) or len(row)!=2:raise ValueError('Bad polynomial term')
        c=rational(row[0]);m=[];seen=set()
        for name,e in row[1]:
            if not isinstance(name,str) or not NAME.fullmatch(name):raise ValueError('Bad variable')
            if name in seen or not isinstance(e,int) or isinstance(e,bool) or e<=0:raise ValueError('Bad exponent')
            if allowed is not None and name not in allowed:raise ValueError('Undeclared variable')
            seen.add(name);m.append((name,e))
        m=tuple(sorted(m));out[m]=out.get(m,F(0))+c
    return clean(out)

def digest(equations):
    payload=[[name,dump(equations[name])] for name in sorted(equations)]
    return hashlib.sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()

def check_refutation(equations,certificate):
    """Check -1 = sum w_i S_i^2 + sum A_j E_j, all w_i >= 0.
    The equations come from the caller, not from an untrusted proof payload.
    """
    if certificate.get('format')!='komorebi-rational-refutation-v1':raise ValueError('Wrong certificate format')
    if certificate.get('equations_sha256')!=digest(equations):raise ValueError('Equation binding mismatch')
    names=set().union(*(variables(p) for p in equations.values())) if equations else set()
    accum={};n_squares=0;n_multipliers=0
    for entry in certificate.get('squares',[]):
        w=rational(entry['weight'])
        if w<0:raise ValueError('Negative square weight')
        p=load(entry['polynomial'],names)
        accum=add(accum,scale(square(p),w));n_squares+=1
    for entry in certificate.get('multipliers',[]):
        name=entry['equation']
        if name not in equations:raise ValueError('Unknown equation')
        p=load(entry['polynomial'],names)
        accum=add(accum,mul(p,equations[name]));n_multipliers+=1
    if accum!=const(-1):raise ValueError('Exact refutation identity is false')
    return {'status':'PASS','kind':'independent rational polynomial refutation',
            'squares':n_squares,'equation_multipliers':n_multipliers,
            'equations_sha256':digest(equations),'arithmetic':'Python int and Fraction'}

def certificate(equations,squares=(),multipliers=()):
    return {'format':'komorebi-rational-refutation-v1','equations_sha256':digest(equations),
        'squares':[{'weight':str(rational(w)),'polynomial':dump(p)} for w,p in squares],
        'multipliers':[{'equation':name,'polynomial':dump(p)} for name,p in multipliers]}
