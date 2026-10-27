#!/usr/bin/env python3
"""v25 exact/modular checks. Universal claims are separate Lean proofs.
No zero residue is reported as an exact dyadic zero; synthetic cases stay labelled.
"""
from __future__ import annotations
import argparse, json, math, random, time, platform
from collections import Counter
from pathlib import Path
import check_critical_value as old

counts=Counter()
def check(c,label):
    if not c: raise AssertionError(label)
    counts[label]+=1

def evz(a,x):
    v=0
    for c in reversed(a):v=v*x+c
    return v

def jet(a,k):return [math.comb(n,k)*a[n] for n in range(k,len(a))]
def vv(n,p=10**9):return old.v2(n,p)

def lift_inflection(a,p):
    q=jet(a,2)
    check(q[1]%2==1 and all(c%2==0 for c in q[2:]),'affine half-second derivative')
    r=0
    for k in range(p):
        if old.ev(q,r,1<<(k+1)):r+=1<<k
        check(old.ev(q,r,1<<(k+1))==0,'binary inflection lift')
    # Independent Newton lift at fixed final modulus.
    n=0;dq=old.deriv(q);mod=1<<p
    for _ in range(p.bit_length()+3):
        n=(n-old.ev(q,n,mod)*pow(old.ev(dq,n,mod),-1,mod))%mod
    check(n==r,'Newton versus binary inflection')
    return r

def audit(a,p=64,critical=()):
    mod=1<<p
    check(a[3]%2==1 and all(c%4==0 for c in a[4:]),'full cubic class')
    rho=lift_inflection(a,p)
    g=jet(a,1);q=jet(a,2)
    A=old.ev(g,rho,mod);C=old.ev(a,rho,mod)
    for x in range(-5,10):
        e=vv((x-rho)%mod,p)
        check(vv(old.ev(q,x,mod),p)==e,'curvature-distance identity')
        check(vv((old.ev(g,x,mod)-A)%mod,p)==min(p,2*e),'slope-distance identity')
        bound=min(p,e+vv(old.ev(g,x,mod),p),3*e)
        check(vv((old.ev(a,x,mod)-C)%mod,p)>=bound,'trial-value bound')
        for y in [0,2,7,-3]:
            d=y-x
            expr=2*(evz(a,y)-evz(a,x))-d*(evz(g,x)+evz(g,y))
            check(vv(expr)==3*vv(d) if d else expr==0,'exact integer trapezoid')
    for x in critical:
        check(evz(g,x)==0,'planted critical point exact')
        e=vv((x-rho)%mod,p)
        check(vv(A,p)==min(p,2*e),'critical slope radius')
        check(vv((old.ev(a,x,mod)-C)%mod,p)==min(p,1+3*e),'critical value from inflection')
    for x in critical:
        for y in critical:
            if x!=y:
                check(vv(evz(a,y)-evz(a,x))==3*vv(y-x)-1,'critical value separation exact')
    return {'precision':p,'inflection_residue':str(rho),'C_residue':str(C),
            'A_residue':str(A),'v_C':vv(C,p),'v_A':vv(A,p),
            'norm_mismatch': C!=0 and A!=0 and 2*vv(C,p)!=2+3*vv(A,p)}

def generic():
    rng=random.Random(20261004);records=[]
    for _ in range(80):
        R=[rng.randrange(-40,41) for _ in range(rng.randrange(1,7))]
        a=[rng.randrange(-100,101),rng.randrange(-100,101),rng.randrange(-50,51),rng.randrange(-40,41)*2+1]+[4*t for t in R]
        audit(a)
    # Two independently planted exact critical points; no floating point roots.
    for _ in range(60):
        x=rng.randrange(-16,17);y=x+2*rng.randrange(1,20)
        u=2*rng.randrange(-10,11)+1
        T=[0]*4+[rng.randrange(-12,13) for _ in range(4)]
        dt=old.deriv(T)
        divided=(evz(dt,y)-evz(dt,x))//(y-x)
        c=(-3*u*(x+y)-4*divided)//2
        b=-2*c*x-3*u*x*x-4*evz(dt,x)
        a=[rng.randrange(-40,41),b,c,u]+[4*t for t in T[4:]]
        audit(a,64,(x,y))
    # Exact repeated-zero controls, on the equality boundary, not Euler counterexamples.
    for s in [1,2,3,4,8,16]:
        a=[2*s**3,-3*s*s,0,1]
        rec=audit(a,64,(s,-s))
        check(evz(a,s)==0 and evz(old.deriv(a),s)==0,'exact cubic double zero')
        check(2*rec['v_C']==2+3*rec['v_A'],'equality boundary can be degenerate')
        records.append({'kind':'synthetic double','s':s,**rec})
    a=[2,3,0,1];rec=audit(a)
    check(2*rec['v_C']==2+3*rec['v_A'],'inconclusive equality control')
    check(4*3**3+27*2**2!=0,'equality can be nondegenerate')
    records.append({'kind':'synthetic equality but no repeated root','reduced_discriminant':216,**rec})
    return records

def actual(B,p):
    r=B*(1<<640)-161
    t=time.monotonic();G,mu,j=old.residual(r,p)
    check((mu,j)==(-154,161),'actual terminal161 carry')
    L=old.local(G,90,7,p);c=min(vv(z,p) for z in L)
    F=[z>>c for z in L];P=p-c
    check(F[3]%2==1 and all(z%4==0 for z in F[4:]),'actual cubic normalization')
    # Actual functions are known coefficientwise mod 2^P; this evaluator never uses
    # the lifted residues as exact algebraic points.
    rho=lift_inflection(F,P)
    mod=1<<P;C=old.ev(F,rho,mod);A=old.ev(jet(F,1),rho,mod)
    rec={'kind':'actual Euler finite certificate','B':B,'global_precision':p,
         'r':str(r),'j':j,'mu':mu,'ball':[90,7],'content':c,'precision':P,
         'coefficients':[str(x) for x in F],'inflection_residue':str(rho),
         'C_residue':str(C),'A_residue':str(A),'v_C':vv(C,P),'v_A':vv(A,P),
         'norm_mismatch':C!=0 and A!=0 and 2*vv(C,P)!=2+3*vv(A,P),
         'seconds':time.monotonic()-t}
    # Hasse Taylor error at trial integer points, with an explicit precision cap.
    for x in [0,1,2,6,7,17,31,65]:
        e=vv((x-rho)%mod,P)
        check(vv(old.ev(jet(F,2),x,mod),P)==e,'actual inflection distance')
        check(vv((old.ev(jet(F,1),x,mod)-A)%mod,P)==min(P,2*e),'actual slope distance')
    return rec

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--actual',type=int,nargs='*');p.add_argument('--precision',type=int,default=224)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    t=time.monotonic()
    records=[actual(b,a.precision) for b in a.actual] if a.actual else generic()
    obj={'status':'PASS','scope':'bounded exact/modular corroboration; not new Euler parameter-family coverage',
         'python':platform.python_version(),'counts':dict(counts),'total':sum(counts.values()),
         'seconds':time.monotonic()-t,'records':records}
    a.output.write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({k:v for k,v in obj.items() if k!='records'},indent=2))
    for r in records:print({k:v for k,v in r.items() if k not in ['coefficients','r']})
if __name__=='__main__':main()
