#!/usr/bin/env python3
"""v26: exact/finite corroboration of the scale-sensitive cubic jet obstruction.
The universal theorem is in Lean. Zero residues are censored, never exact zeros.
Run with --generic, or --actual B [--alternate] --precision P.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, random, time
from pathlib import Path
from collections import Counter
import check_critical_value as base
import check_critical_replay as alt

COUNT=Counter()
def check(cond,label):
    if not cond: raise AssertionError(label)
    COUNT[label]+=1

def jet(a,k):return [math.comb(n,k)*a[n] for n in range(k,len(a))]
def ev(a,x):
    r=0
    for v in reversed(a):r=r*x+v
    return r

def v2(x):return None if x==0 else (abs(x)&-abs(x)).bit_length()-1

def lift(a,p):
    q=jet(a,2);dq=base.deriv(q);M=1<<p
    check(q[1]%2==1 and all(z%2==0 for z in q[2:]),'half-second affine reduction')
    c=0
    for k in range(p):
        if base.ev(q,c,1<<(k+1)):c+=1<<k
    n=0
    for _ in range(p.bit_length()+3):
        n=(n-base.ev(q,n,M)*pow(base.ev(dq,n,M),-1,M))%M
    check(n==c,'binary/Newton inflection agreement')
    check(base.ev(q,c,M)==0,'certified inflection residue')
    return c

def generic():
    rng=random.Random(2026100426);out=[]
    # Exact planted critical zeros; all inflection centers are known exactly.
    for _ in range(240):
        s=(1<<rng.randrange(0,5))*rng.randrange(1,16,2)
        h=rng.randrange(-64,65) or 2
        u=rng.randrange(-15,16,2)
        R=[rng.randrange(-20,21) for _ in range(rng.randrange(1,7))]
        rh=ev(R,h);rp=ev(jet(R,1),h)
        e=4*rh+h*rp
        A=-3*u*h*h-4*s*h**3*e
        C=2*u*h**3+4*s*h**4*(e-rh)
        F=[C,A,0,u]+[4*s*x for x in R]
        check(ev(F,h)==0,'planted exact value zero')
        check(ev(jet(F,1),h)==0,'planted exact derivative zero')
        D=4*A**3+27*u*C*C
        factor=16*s*h**7*(-27*u*u*rh+9*u*s*h*(3*(e-rh)**2-4*e*e)-16*s*s*h*h*e**3)
        check(D==factor,'exact discriminant remainder factor')
        check(D%(16*s*h**7)==0,'scale-sensitive ideal inclusion')
        check(v2(A)==2*v2(h),'critical radius valuation')
        check(v2(C)==1+3*v2(h),'critical value valuation')
        if D:
            check(v2(D)>=4+v2(s)+7*v2(h),'no false nondegeneracy on planted roots')
        # Translate by arbitrary integers and reconstruct four jets independently.
        rho=rng.randrange(-20,21)
        G=[sum(F[n]*math.comb(n,k)*(-rho)**(n-k) for n in range(k,len(F))) for k in range(len(F))]
        check(ev(jet(G,2),rho)==0,'translated exact inflection')
        check(ev(G,rho)==C and ev(jet(G,1),rho)==A and ev(jet(G,3),rho)==u,'translated jet invariance')
    # The strict threshold is sharp, including a nonzero jet discriminant at a double root.
    for d in range(1,12):
        h=1<<d;A=-3*h*h-16*h**3;C=2*h**3+12*h**4
        D=4*A**3+27*C*C
        check(v2(D)==4+7*d,'sharp nonzero boundary discriminant')
        check(ev([C,A,0,1,4],h)==0 and ev([A,0,3,16],h)==0,'sharp double control')
        out.append({'kind':'synthetic sharp boundary','h':h,'v_D':v2(D),'bound':4+7*d})
    # Modulus-16 shape, also kernel checked by CubicUnitCertificates.lean.
    p=[12,5,10,11,8]
    for y in range(16):
        if ev(jet(p,2),y)%16==0:
            D=(4*ev(jet(p,1),y)**3+27*ev(jet(p,3),y)*ev(p,y)**2)%16
            check(D!=0,'finite inflection residue shape nonzero')
        check(not(ev(p,y)%16==0 and ev(jet(p,1),y)%16==0),'finite root-slope check')
    # Independent lower-index Bernoulli checks, not the same modular implementation.
    exact=base.bernoullis(80)
    for n in range(2,81,2):
        for P in [16,32,64]:
            check(base.twoB(n,P)==base.fmod(2*exact[n],P),'rational Bernoulli comparison')
    return out

def actual(B,P,alternate):
    if B not in [3,7,11,15]:raise ValueError('declared finite input family is B in {3,7,11,15}')
    if P<192 or P>320:raise ValueError('declared resource bound is 192<=P<=320')
    base.B=base.bernoullis(max(256,P))
    r=B*(1<<640)-161;M=1<<P
    bound=(r.bit_count()-1)//3
    costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
    mu=min(costs);j=max(q for q,w in enumerate(costs) if w==mu)
    check((mu,j)==(-154,161),'original carry index and minimum')
    if alternate:
        G=alt.reconstruct_alt(r,mu,P)
        shifted=base.shift(G,90,M)
        L=[(x<<(7*n))%M for n,x in enumerate(shifted) if 7*n<P]
    else:
        G,m0,j0=base.residual(r,P)
        check((m0,j0)==(mu,j),'residual/carry agreement')
        L=base.local(G,90,7,P)
    content=min(base.v2(x,P) for x in L)
    check(content==162,'original coordinate content')
    F=[x>>content for x in L];p=P-content;mod=1<<p
    check(F[3]%2==1 and all(x%8==0 for x in F[4:]),'eight-divisible full retained tail')
    # Infinite coefficients beyond degree 4 are >= 2n-6 by the inherited actual
    # Euler core theorem. Thus the single mod8 degree-four test upgrades the exact tail.
    check(F[4]%16==8,'tail has exact scale eight')
    rho=lift(F,p)
    A=base.ev(jet(F,1),rho,mod);C=base.ev(F,rho,mod);v=base.ev(jet(F,3),rho,mod)
    D=(4*A**3+27*v*C*C)%mod
    check(A!=0 and C!=0 and D!=0,'values below certified precision')
    va,vc,vd=v2(A),v2(C),v2(D)
    passes=2*vd<10+7*va
    check(passes,'scaled discriminant excludes critical zero')
    # All coefficients and jets from previous release are compared at common precision.
    parent=Path(__file__).resolve().parents[1]/f'evidence/v25_actual_{B}.json'
    old=json.loads(parent.read_text())['records'][0];shared=min(p,old['precision']);sm=1<<shared
    prev=list(map(int,old['coefficients']))
    for n in range(max(len(F),len(prev))):
        check((F[n] if n<len(F) else 0)%sm==(prev[n] if n<len(prev) else 0)%sm,'full previous coefficient agreement')
    check(rho%sm==int(old['inflection_residue'])%sm,'previous inflection agreement')
    check(A%sm==int(old['A_residue'])%sm and C%sm==int(old['C_residue'])%sm,'previous value-slope agreement')
    # Original finite packet values: no use of lifted critical point as an exact root.
    gam=base.gamma(r,mu,P,7)
    from fractions import Fraction
    for x in range(8):
        prod=1;value=0
        for q in range(x+1):
            if q:prod=prod*(x-q+1)*(2*x-2*q+1)%M
            src=base.fmod(Fraction(9**(x-q+1)-1,8*(x-q+1)*(2*x-2*q+1)),P)
            value=(value+gam[q]*prod*src)%M
        check(base.ev(G,x,M)==value,'original terminating packet value')
    return [{'kind':'fixed actual Euler index','B':B,'r':str(r),'j':j,'mu':mu,
        'global_precision':P,'content':content,'precision':p,'ball':[90,7],
        'coefficients':list(map(str,F)),'inflection_residue':str(rho),
        'A_residue':str(A),'C_residue':str(C),'v_residue':str(v),'D_residue':str(D),
        'v_A':va,'v_C':vc,'v_D':vd,'tail_scale_valuation':1,
        'old_norm_mismatch':2*vc!=2+3*va,'scaled_discriminant_passes':passes,
        'unit_data_mod8':{'A_odd':(A>>va)%8,'C_odd':(C>>vc)%8,'cubic_jet':v%8},
        'alternate_routes':alternate}]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--generic',action='store_true');g.add_argument('--actual',type=int)
    ap.add_argument('--precision',type=int,default=256);ap.add_argument('--alternate',action='store_true')
    ns=ap.parse_args()
    if ns.output.exists():raise FileExistsError(ns.output)
    start=time.monotonic()
    records=generic() if ns.generic else actual(ns.actual,ns.precision,ns.alternate)
    report={'status':'PASS','counts':dict(COUNT),'total_registered_checks':sum(COUNT.values()),
        'records':records,'seconds':time.monotonic()-start,'python':platform.python_version(),
        'seed':2026100426,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic':'exact integers/rationals and modular integers; no floating scientific arithmetic',
        'nonclaims':['No universal Euler simplicity','No new infinite multiplier family',
          'Arithmetic instances are not original-index Lean proofs','Zero residues are not exact zeros'],
        'shared_components':['modular Bernoulli evaluator','polynomial multiplication']}
    ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
    for r in records:
        if r.get('kind')=='fixed actual Euler index':
            print({k:r[k] for k in ['B','precision','v_A','v_C','v_D','old_norm_mismatch','scaled_discriminant_passes']})
if __name__=='__main__':main()
