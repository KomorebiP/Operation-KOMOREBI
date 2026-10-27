#!/usr/bin/env python3
"""Exact/modular checks for v24. All ranges are explicit; no sampled root is an exact dyadic root.
The universal theorems are Lean proofs. This program only corroborates stated bounded inputs.
Python 3.10+, standard library only. Output is a fresh JSON evidence record.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, random, time
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

COUNTS=Counter()
def check(cond: bool, label: str):
    if not cond: raise AssertionError(label)
    COUNTS[label]+=1

def v2(n: int, cap: int=10**9) -> int:
    return cap if n==0 else (abs(n)&-abs(n)).bit_length()-1

def ev(a:list[int],x:int,mod:int)->int:
    z=0
    for c in reversed(a): z=(z*x+c)%mod
    return z

def deriv(a:list[int])->list[int]: return [i*a[i] for i in range(1,len(a))]

def mul(a:list[int],b:list[int],mod:int)->list[int]:
    c=[0]*(len(a)+len(b)-1)
    for i,ai in enumerate(a):
        if ai:
            for j,bj in enumerate(b):
                if bj:c[i+j]=(c[i+j]+ai*bj)%mod
    return c

def shift(a:list[int],c:int,mod:int)->list[int]:
    # Horner affine translation; verification below uses direct binomial expansion.
    out=[0]
    for ai in reversed(a):
        nxt=[0]*(len(out)+1)
        for i,v in enumerate(out):
            nxt[i]=(nxt[i]+c*v)%mod;nxt[i+1]=(nxt[i+1]+v)%mod
        nxt[0]=(nxt[0]+ai)%mod;out=nxt
    while len(out)>1 and out[-1]==0:out.pop()
    return out

def local(a:list[int],c:int,k:int,P:int)->list[int]:
    mod=1<<P;dmax=min(len(a)-1,(P-1)//k) if k else len(a)-1
    # Independent direct binomial method, retaining precisely the non-forced coefficients.
    cp=[pow(c,n,mod) for n in range(len(a))]
    out=[]
    for d in range(dmax+1):
        z=sum(a[n]*math.comb(n,d)*cp[n-d] for n in range(d,len(a)))%mod
        out.append((z<<(k*d))%mod)
    return out

def bernoullis(n:int)->list[Fraction]:
    bs=[Fraction(1)]
    for k in range(1,n+1):
        bs.append(-sum(Fraction(math.comb(k+1,j))*bs[j] for j in range(k))/(k+1))
    return bs
B=bernoullis(256)

def fmod(x:Fraction,P:int)->int:
    if v2(x.numerator)-v2(x.denominator)<0:raise ValueError('nonintegral scalar')
    mod=1<<P
    return (x.numerator*pow(x.denominator,-1,mod))%mod

@lru_cache(None)
def twoB(n:int,P:int)->int:
    mod=1<<P;N=min(n,P);comb=1;s=0
    for k in range(N+1):
        if k:comb=comb*(n-k+1)//k
        if B[k]:s=(s+fmod(Fraction(comb*(1<<k))*B[k],P))%mod
    return s*pow((1-pow(2,n-1,mod))%mod,-1,mod)%mod

@lru_cache(None)
def source(P:int)->tuple[int,...]:
    mod=1<<P;N=[0]*P;fall=[1]
    for q in range(P+1):
        c=Fraction(8**q,math.factorial(q+1))
        if v2(c.numerator)-v2(c.denominator)<P:
            cm=fmod(c,P)
            for i,a in enumerate(fall):
                if i<P:N[i]=(N[i]+cm*a)%mod
        fall=mul(fall,[-q,1],mod)
    out=mul(N,[pow(-2,n,mod) for n in range(P)],mod)[:P]
    return tuple(out)

def gamma(r:int,mu:int,P:int,Q:int)->list[int]:
    mod=1<<P;baseB=twoB(2*r,P);invB=pow(baseB,-1,mod);inv0=pow((2*r-1)%mod,-1,mod)
    gam=[pow(2,-mu,mod)];od=1;vd=0
    for q in range(1,Q+1):
        for n in (2*r+2*q-1,2*r+2*q):
            k=v2(n);vd+=k;od=od*(n>>k)%mod
        k=5*q-mu-vd
        check(k==3*q+(r+q).bit_count()-r.bit_count()-mu,'gamma valuation identity')
        if k<0:raise ValueError('not a global minimum')
        if k>=P:gam.append(0);continue
        unit=((2*r+2*q-1)*inv0*twoB(2*r+2*q,P)*invB*pow(od,-1,mod))%mod
        gam.append((unit<<k)%mod)
    return gam

def residual(r:int,P:int)->tuple[list[int],int,int]:
    bound=(r.bit_count()-1)//3
    costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range(bound+1)]
    mu=min(costs);j=max(q for q,w in enumerate(costs) if w==mu)
    Q=max(0,(P+r.bit_count()+mu-2)//3);gam=gamma(r,mu,P,Q);mod=1<<P
    A=list(source(P));G=[0]*(2*Q+P);Pq=[1]
    for q,gq in enumerate(gam):
        if q:
            i=q-1;Pq=mul(Pq,[-i,1],mod);Pq=mul(Pq,[-2*i-1,2],mod)
        if gq:
            term=mul(Pq,shift(A,-q,mod),mod)
            for n,a in enumerate(term):G[n]=(G[n]+gq*a)%mod
    return G,mu,j

def lift_critical(F:list[int],P:int)->tuple[int,list[int]]:
    # F known modulo 2^(P+1). Half derivative modulo 2^P is unambiguous.
    Q=[((i*F[i])//2)%(1<<P) for i in range(1,len(F))]
    check(F[1]%2==0 and all((i*F[i])%2==0 for i in range(1,len(F))), 'integral half derivative')
    check(Q[1]%2==1 and all(x%2==0 for x in Q[2:]),'affine critical equation')
    c=0
    for k in range(P):
        m=1<<(k+1)
        if ev(Q,c,m):c+=1<<k
        check(ev(Q,c,m)==0,'critical binary lift')
    return c,Q

def audit_core(F:list[int],P:int)->dict:
    mod=1<<P;M=1<<(P+1);F=[x%M for x in F]
    check(F[2]%2==1 and all(x%4==0 for x in F[3:]),'quadratic tail class')
    c,Q=lift_critical(F,P);cv=ev(F,c,mod);a=F[0]%mod;b=(F[1]//2)%mod;u=F[2]%mod;ui=pow(u,-1,mod)
    check(v2(c,P)==v2(b,P),'critical center norm')
    R=[(x//4)%mod for x in F[3:]] or [0];Rp=deriv(R)
    S=(3*ev(R,c,mod)+c*ev(Rp,c,mod))%mod
    check((c+ui*b+2*ui*c*c*S)%mod==0,'exact nonlinear center identity')
    target=(a-ui*b*b+4*c**3*(ev(R,c,mod)+ui*c*S*S))%mod
    check(cv==target,'exact moved critical value identity')
    err=(cv-(a-ui*b*b))%mod;threshold=2+3*v2(b,P)
    check(v2(err,P)>=min(P,threshold),'third order critical error')
    for x in range(12):
        gap=(ev(F,x,mod)-cv)%mod
        check(v2(gap,P)==min(P,2*v2((x-c)%mod,P)),'exact stationary distance law')
        check(v2(gap,P)==min(P,2*v2(ev(Q,x,mod),P)),'exact value slope law')
        if v2(ev(F,x,mod),P)!=min(P,2*v2(ev(Q,x,mod),P)):
            check(cv!=0,'norm mismatch excludes zero')
    return {'P':P,'critical_center_residue':str(c),'critical_value_residue':str(cv),
            'critical_value_valuation':v2(cv,P),'first_corrected_scalar_valuation':v2((a-ui*b*b)%mod,P),
            'third_order_lower_bound':threshold,'norm_gap_passes':v2((a-ui*b*b)%mod,P)<threshold}

def run(output:Path, actual:bool)->None:
    if output.exists():raise FileExistsError(output)
    started=time.time();rng=random.Random(20261004);records=[]
    for _ in range(160):
        a=rng.randrange(-500,501);b=rng.randrange(-128,129);u=2*rng.randrange(-50,51)+1
        R=[rng.randrange(-20,21) for _ in range(rng.randrange(1,8))]
        audit_core([a,2*b,u]+[4*z for z in R],64)
    for e_order in range(0,10):
        e=1<<e_order
        for _ in range(6):
            c0=rng.randrange(1,100,2);c1=rng.randrange(-100,101);b1=rng.randrange(-100,101)
            u=2*rng.randrange(-50,51)+1;R=[rng.randrange(-10,11) for _ in range(4)]
            rec=audit_core([4*e*c0+16*e*e*c1,4*e*b1,u]+[4*z for z in R],80)
            if e_order>0:check(rec['critical_value_valuation']==2+e_order,'perturbation strict margin')
    for c in [2,4,6,8,16,32]:
        # (x-c)^2(1+4x): exact double zero; confirms that strictness is essential.
        F=[c*c,4*c*c-2*c,1-8*c,4]
        rec=audit_core(F,80)
        check(rec['critical_value_residue']=='0','negative double control')
        check(rec['first_corrected_scalar_valuation']==2+3*v2(c),'sharp boundary equality')
    # Confirm high-index Bernoulli routine against exact rational values and source values.
    for n in range(2,82,2):
        for P in [16,32,64]:check(twoB(n,P)==fmod(2*B[n],P),'Bernoulli independent exact comparison')
    for P in [16,32,64]:
        for n in range(16):
            exact=Fraction(9**(n+1)-1,8*(n+1)*(2*n+1))
            check(ev(list(source(P)),n,1<<P)==fmod(exact,P),'source exact integer comparison')
    if actual:
        for label,b,L,j,a,k,C in [
            ('terminal17-b1',1,64,17,3,4,16),
            ('terminal17-b3',3,64,17,3,4,16),
            ('terminal129-first-representative',4045,515,129,7528,15,147),
            ('terminal129-second-representative',44797,515,129,2920,15,147)]:
            r=b*(1<<L)-j;P=224 if j>17 else 96
            G,mu,found=residual(r,P);check(found==j,'actual terminal check')
            f=local(G,a,k,P)
            content=min(v2(z,P) for z in f)
            item={'label':label,'r':str(r),'mu':mu,'terminal':found,'global_P':P,'ball':[a,k],'content':content}
            if content!=C or len(f)<3 or ((f[2]>>C)&1)==0:
                item['status']='not the selected normalized quadratic; no theorem application'
                records.append(item);continue
            p=P-C-1
            coeff=[z>>C for z in f]
            if coeff[1]%2:
                item['status']='odd linear coefficient, derivative is a unit';records.append(item);continue
            item['result']=audit_core(coeff,p);item['status']='finite critical value calculation'
            # Original finite packet value at a nonnegative integer x is a separate evaluation route.
            for x in [0,1,2,5]:
                gam=gamma(r,mu,P,x);fall=1;val=0
                for q,gq in enumerate(gam):
                    if q:fall=fall*(x-q+1)*(2*x-2*q+1)%(1<<P)
                    av=fmod(Fraction(9**(x-q+1)-1,8*(x-q+1)*(2*(x-q)+1)),P)
                    val=(val+gq*fall*av)%(1<<P)
                check(ev(G,x,1<<P)==val,'actual finite packet value comparison')
            records.append(item)
    result={'status':'passed','total_registered_checks':sum(COUNTS.values()),'counts':dict(COUNTS),
            'actual_cases':records,'seed':20261004,'arithmetic':'exact integers and fractions; modular reductions',
            'nonclaims':['No universal Euler simplicity','Zero modulo a finite modulus is not exact zero',
                         'Actual finite cases do not classify entire multiplier families',
                         'Shared modular Bernoulli evaluator in actual coefficient and packet checks'],
            'seconds':time.time()-started,'python':platform.python_version(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--actual',action='store_true')
    ns=ap.parse_args();run(ns.output,ns.actual)
