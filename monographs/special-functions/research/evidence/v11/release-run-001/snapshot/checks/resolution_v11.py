#!/usr/bin/env python3
"""Exact finite certificates for the SF-DISCOVERY-110 resolution atlas.
Run from the release root: python checks/resolution_v11.py
Standard library only. Analytic universal claims are proved in
research_v11/resolution_atlas.md. Floating displays are not interval arithmetic.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = 'SF-DISCOVERY-100'
EXACT = 0
FLOAT = 0

def ex(test):
    global EXACT
    EXACT += 1
    if not test:
        raise AssertionError(f'exact assertion {EXACT} failed')

def fl(test):
    global FLOAT
    FLOAT += 1
    if not test:
        raise AssertionError(f'floating assertion {FLOAT} failed')

def node(n):
    return (1-F(1,n*n))**2

def squarefree(n):
    return all(n % (k*k) for k in range(2, math.isqrt(n)+1))

def positive_nodes(count, p=2):
    out=[]
    n=1
    while len(out)<count:
        if n%p and squarefree(n): out.append(n)
        n+=1
    return out

def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def ev(poly,x):
    ans=F(0)
    for c in reversed(poly): ans=ans*x+c
    return ans

def interpolating_bound(labels):
    """Returns exact K with sup_[0,1] f² <= K sum n^-4 f(x_n)²."""
    ys=[node(n) for n in labels]
    K=F(0)
    bounds=[]
    polynomials=[]
    for i,(n,y) in enumerate(zip(labels,ys)):
        b=F(1); poly=[F(1)]
        for j,z in enumerate(ys):
            if i!=j:
                b*=max(z,1-z)/abs(y-z)
                poly=mul(poly,[-z/(y-z),1/(y-z)])
        K+=n**4*b*b
        bounds.append(b); polynomials.append(poly)
    return K,bounds,polynomials

def tailored_detector(delta, killed, m, p=2):
    """All p-free squarefree nodes <= last killed label must be present."""
    target=node(p)
    poly=[F(1)]
    C=F(1)
    for n in killed:
        y=node(n)
        poly=mul(poly,[-y/(target-y),1/(target-y)])
        C*=(1-y)/abs(target-y)
    for _ in range(m): poly=mul(poly,[1/(1-target),-1/(1-target)])
    cutoff=killed[-1]
    following=positive_nodes(len(killed)+1,p)[-1]
    r=(1-node(following))/(1-target)
    upper=-delta/F(p**4)+C*C*r**(2*m)/F(3*cutoff**3)
    return dict(degree=len(poly)-1,killed=killed,m=m,C=C,r=r,upper=upper,poly=poly,following=following)

def best_detector(delta, max_killed=12):
    labels=positive_nodes(max_killed+1)
    candidates=[]
    for k in range(1,max_killed+1):
        killed=labels[:k]
        m=0
        while True:
            item=tailored_detector(delta,killed,m)
            if item['upper']<0:break
            m+=1
        candidates.append(item)
    return min(candidates,key=lambda x:(x['degree'],len(x['killed']),x['m']))

def coefficients(epsilon,last):
    out=[F(1)]
    for n in range(1,last+1):
        scale=(1-epsilon)*F(1,4)**(2*n)+epsilon*F(3,4)**(2*n)
        out.append(scale*sum((out[i]*out[n-1-i] for i in range(n)),F(0))/(2*n+1))
    return out

def diagonal(last): return coefficients(F(1),last)

def compact_lipschitz(last=40):
    d=diagonal(last)
    # f_(3/4)(4/3) <= tan(4/3) <= 12, from cos x >= 1-x²/2.
    t=F(3,4)
    tail=12*(last+1)*t**(2*last+3)
    return sum((n*d[n] for n in range(1,last+1)),F(0))+tail,tail

def slow_upper_type():
    q=.25;rho=.5;m=q;Q=q
    N=0
    while Q**(-N)<3/m:N+=1
    V=(2**(N+1)-1)*math.log(2)+(2**(N+1)-N-2)*math.log(1/Q)
    B=math.log(1/(q*q))+math.log(2)
    return math.exp(-rho)*(V+1+math.log(1/m)+B)

def weak_tap_radius(epsilon):
    rho=math.log(2)/math.log(4/3)
    cminus=math.log(2)/(4/epsilon+8/3)**rho
    cplus=slow_upper_type()
    R=max(math.e,(2*cplus/cminus)**(1/(rho-.5)),(2*math.log(2)/cminus)**(1/rho))
    return rho,cminus,cplus,R

def prime_visibility(p, eta=1e-6):
    # a=beta=2,Q=1. D(4)=105/pi^4 is an exact identity.
    lam=-2*math.log1p(-p**-2)
    D4=105/math.pi**4
    raw_lower=math.log(eta*(p**4+1)/D4)/lam
    lower=raw_lower if raw_lower>=0 else None
    upper=max(0.,math.log(eta*p**4)/lam)
    log10_condition=math.log10((p**4+1)/(16*D4))+( -2*math.log(.75)-lam)*upper/math.log(10)
    return dict(p=p,lambda_p=lam,threshold=eta,invisible_until=lower,visible_by=upper,log10_cancellation_lower=log10_condition)

def encode(item):
    if isinstance(item,F):return {'numerator':str(item.numerator),'denominator':str(item.denominator),'decimal':float(item)}
    if isinstance(item,dict):return {str(k):encode(v) for k,v in item.items()}
    if isinstance(item,(list,tuple)):return [encode(x) for x in item]
    return item

def main():
    global EXACT,FLOAT
    EXACT=FLOAT=0
    start=time.monotonic()
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'evidence/v11/resolution_checks.json');args=parser.parse_args()
    labels=positive_nodes(10)
    low=[]
    for count in range(1,8):
        used=labels[:count];K,bounds,polys=interpolating_bound(used)
        ex(K>0)
        for i,poly in enumerate(polys):
            for j,n in enumerate(used):ex(ev(poly,node(n))==int(i==j))
            for x in (F(0),F(1,5),F(1,2),F(4,5),F(1)):
                ex(abs(ev(poly,x))<=bounds[i])
        # The exact polynomial identity for each basis monomial independently
        # verifies reconstruction, beyond just testing interpolation nodes.
        for power in range(count):
            reconstructed=[sum(node(n)**power*poly[k] for n,poly in zip(used,polys)) for k in range(count)]
            ex(reconstructed==[F(int(k==power)) for k in range(count)])
        low.append(dict(degree=count-1,labels=used,K=K,delta_threshold=12/K))
    defects=[]
    for power in range(1,16):
        delta=F(1,10**power)
        item=best_detector(delta)
        ex(item['upper']<0)
        ex(ev(item['poly'],node(2))==1)
        ex(F(0)<item['r']<1)
        for n in item['killed']:ex(ev(item['poly'],node(n))==0)
        for n in positive_nodes(30)[len(item['killed']):]:
            ex(abs(ev(item['poly'],node(n)))<=item['C']*item['r']**item['m'])
        certified=max(entry['degree'] for entry in low if delta<entry['delta_threshold'])
        ex(certified<item['degree'])
        defects.append(dict(delta=delta,positive_through_degree=certified,detector=item))
    chosen=defects[11]
    ex(chosen['positive_through_degree']==4)
    ex(chosen['detector']['degree']==7)
    ex(chosen['detector']['killed']==[1,3,5,7])
    ex(chosen['detector']['m']==3)
    # Direct exact finite norms and absolute finite-tail domination. The
    # analytical integral envelope covers all still uncomputed nodes.
    delta=chosen['delta'];P=chosen['detector']['poly'];cutoff=100
    finite=sum((F(1,n**4)*(1 if n%2 else -delta)*ev(P,node(n))**2 for n in range(1,cutoff+1) if squarefree(n)),F(0))
    ex(finite<0)
    ex(finite<=chosen['detector']['upper'])
    d=diagonal(20);base=coefficients(F(0),20)
    for eps in [F(1,10),F(1,1000),F(1,10**6)]:
        c=coefficients(eps,20)
        for n in range(21):
            ex(c[n]>=base[n])
            ex(c[n]-base[n]<=eps*n*d[n])
    lip,tail=compact_lipschitz()
    ex(F(0)<lip<F(1,2))
    ex(tail<F(1,10**6))
    ex(F(41)*(F(3,4)**2)<=F(40)) # tail n*t^(2n+1) decreases from n=41
    weak=[]
    fl(abs(slow_upper_type()-math.exp(-.5)*(1+22*math.log(2)))<1e-13)
    for exp in [1,3,6,9,12]:
        eps=10.**-exp;rho,cminus,cplus,R=weak_tap_radius(eps)
        fl(cminus>0 and cplus>0 and R>=math.e)
        # Small relative allowance is only a floating algebra check, not a proof.
        fl(cminus*R**rho>=(cplus*math.sqrt(R)+math.log(2))*(1-1e-12))
        weak.append(dict(epsilon=eps,rho=rho,cminus=cminus,cplus=cplus,ratio_two_sufficient_radius=R))
    prime=[]
    for p in [11,31,101,1009,10007]:
        item=prime_visibility(p)
        fl(item['invisible_until'] is None or 0<=item['invisible_until']<=item['visible_by'])
        # Exact rational integer-depth envelope at T=5 uses e^(5lambda_p)
        # = (1-p^-2)^-10, and D4 < 4/3. Every derived tail is positive.
        upper=F(4,3)/F(p**4+1)/(1-F(1,p*p))**10
        ex(upper>F(1,p**4))
        item['disk_radius_5_rational_upper']=upper
        for k in range(4):
            # -log(1-u) <= u/(1-u), so lambda_p <= 2/(p²-1).
            derivative_upper=upper*F(2,p*p-1)**k
            ex(derivative_upper>0)
        prime.append(item)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),ROOT/'research_v11/TARGET_CONTRACT.json',ROOT/'new_results/dilation_type.md',ROOT/'new_results/arithmetic_inverse.md',ROOT/'new_results/multi_prime_sieve.md',ROOT/'research_v11/resolution_atlas.md']}
    report=dict(checkpoint='SF-DISCOVERY-110',base_checkpoint=BASE,status='PASS',exact_assertions=EXACT,floating_assertions=FLOAT,elapsed_seconds=time.monotonic()-start,python=platform.python_version(),input_sha256=hashes,low_degree_certificates=low,defect_certificates=defects,chosen_finite_norm=finite,weak_tap_compact_lipschitz_upper=lip,weak_tap_lipschitz_tail=tail,weak_tap_examples=weak,prime_examples=prime,limitations=['Finite assertions check exact identities and certificates. The general statements use the local proofs.','Floating displays are not directed-rounding intervals.','Passing and failing degree bounds do not determine the minimal detecting degree.','This script has no third-party dependencies.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(report),indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['checkpoint','status','exact_assertions','floating_assertions','elapsed_seconds']}))

if __name__=='__main__':main()
