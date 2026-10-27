#!/usr/bin/env python3
"""Exact verification for the square-kernel ABC sieve; stdlib only."""
import json, math
from pathlib import Path

def factor(n):
    assert n>=1
    f={}
    d=2
    while d*d<=n:
        if n%d==0:
            e=0
            while n%d==0:
                n//=d;e+=1
            f[d]=e
        d=3 if d==2 else d+2
    if n>1:f[n]=f.get(n,0)+1
    return f

def rad(n):
    x=1
    for p in factor(n): x*=p
    return x

def squarefree_kernel(n):
    x=1
    for p,e in factor(n).items():
        if e%2: x*=p
    return x

def rho(Q):
    if Q==1:return 1
    t=1
    for p,e in factor(Q).items():
        if p==2:t*=(1 if e==1 else 2 if e==2 else 4)
        else:t*=2
    return t

def integer_sieve(N):
    a=bytearray(b'\x01')*(N+1);a[:2]=b'\x00\x00'
    for d in range(2,math.isqrt(N)+1):
        if a[d]:a[d*d::d]=b'\x00'*(((N-d*d)//d)+1)
    return [i for i in range(2,N+1) if a[i]]

def count_by_roots(Q,H,T,a=1,prime_multiplier=True):
    primes=set(integer_sieve(H)) if prime_multiplier else None
    obs=[]
    for h in range(1,H+1):
        if primes is not None and h not in primes:continue
        if math.gcd(h,a*Q)!=1:continue
        if not prime_multiplier and rad(h)!=h:continue
        if squarefree_kernel(a+h*Q)<=T:
            obs.append(h)
    return obs

def radical_hits(Q,H,exponent_num=0,exponent_den=1,a=1):
    out=[]
    for h in integer_sieve(H):
        if math.gcd(h,a*Q)!=1:continue
        c=a+h*Q
        R=rad(a*h*Q*c)
        if (c**exponent_den > R**(exponent_den+exponent_num)):
            out.append({'h':h,'c':c,'R':R,'C':rad(c),'sfk':squarefree_kernel(c)})
    return out

def kernel_root_count(Q,m,a=1):
    return sum(1 for u in range(Q) if (m*u*u-a)%Q==0)

def main():
    results={}
    allroots=[]
    for Q in [1,2,4,8,9,16,27,63,81,100,125,243,256]:
        vals=[]
        for m in range(1, min(Q+2,65)):
            if math.gcd(m,Q)>1:continue
            n=kernel_root_count(Q,m)
            assert n in (0,rho(Q)),(Q,m,n,rho(Q))
            vals.append(n)
        allroots.append({'Q':Q,'rho':rho(Q),'tested_m':len(vals),'solvable_m':sum(int(v>0) for v in vals)})
    results['root_tests']=allroots
    cases=[]
    for Q,H in [(9,4000),(16,4000),(63,4000),(81,4000),(243,4000),(256,4000),(729,4000),(2025,2000)]:
        K=Q//rad(Q)
        hits=radical_hits(Q,H)
        bound=rho(Q)*(K+2*math.sqrt((1+H*Q)*K)/Q)
        assert len(hits)<=bound
        assert all(x['C']<=K and x['sfk']<=K for x in hits)
        exact_kernel=count_by_roots(Q,H,K)
        assert set(x['h'] for x in hits).issubset(set(exact_kernel))
        cases.append({'Q':Q,'H':H,'K':K,'rho':rho(Q),'hit_count':len(hits),'root_kernel_candidate_count':len(exact_kernel),'upper_bound':math.ceil(bound),'hits':hits[:12]})
    results['hit_tests']=cases
    advanced=[]
    for Q,H in [(16,4000),(81,4000),(243,4000),(729,4000)]:
        # check c>R^(11/10) via c^10>R^11
        epshits=radical_hits(Q,H,1,10)
        T=2*(1+H*Q)**(10/11)/(H*rad(Q))
        # safe floating T may be +/- rounding, no cases near threshold; exact test rational bound:
        # C < T iff C^11*(H*radQ)^11 < 2^11 * (1+HQ)^10
        for x in epshits:
            assert x['C']**11*(H*rad(Q))**11 < 2**11*(1+H*Q)**10
        bound=rho(Q)*(T+2*math.sqrt((1+H*Q)*T)/Q)
        assert len(epshits)<=bound
        advanced.append({'Q':Q,'H':H,'epsilon':'1/10','count':len(epshits),'upper_bound':math.ceil(bound),'hits':epshits[:10]})
    results['quality_tests']=advanced
    # General offset, prime multiplier h; test exact upper C and kernel lemma
    offsets=[]
    for a,Q,H in [(2,9,1000),(3,16,1000),(5,81,1000),(7,64,1000),(11,243,1000)]:
        assert math.gcd(a,Q)==1
        hits=radical_hits(Q,H,a=a)
        T=(a//rad(a))+(Q//rad(Q))
        assert all(x['C']<T for x in hits)
        candidate=count_by_roots(Q,H,T,a=a)
        assert set(x['h'] for x in hits).issubset(set(candidate))
        bound=rho(Q)*(T+2*math.sqrt((a+H*Q)*T)/Q)
        assert len(hits)<=bound
        offsets.append({'a':a,'Q':Q,'H':H,'T':T,'hit_count':len(hits),'candidates':len(candidate),'upper_bound':math.ceil(bound)})
    results['offset_tests']=offsets
    # Exact quadratic-polynomial realization and universal discriminant 4m.
    polys=[]
    for Q in [9,16,27,63,81,125,243,256]:
        K=Q//rad(Q)
        for m in range(1,K+1):
            if rad(m)!=m or math.gcd(m,Q)!=1:continue
            for u0 in range(Q):
                if (m*u0*u0-1)%Q:continue
                A=m*Q
                B=2*m*u0
                C=(m*u0*u0-1)//Q
                assert B*B-4*A*C==4*m
                for t in [0,1,3]:
                    u=u0+Q*t
                    assert Q*(A*t*t+B*t+C)+1==m*u*u
                polys.append((Q,m,u0))
    results['polynomial_discriminant_tests']=len(polys)
    # Perfect-square output forces prime h <= Q+2, for h coprime Q.
    sqr_examples=[]
    for Q in [9,16,27,63,81,125,243,256,729]:
        for h in integer_sieve(5000):
            if Q%h==0:continue
            c=1+h*Q
            if math.isqrt(c)**2==c:
                assert h<=Q+2,(Q,h,c)
                sqr_examples.append({'Q':Q,'h':h,'u':math.isqrt(c)})
    results['prime_square_output_examples']=sqr_examples
    # local exact symbolic checks with small examples
    results['checked_cases']={'root_modulus_cases':sum(x['tested_m'] for x in allroots),'prime_multiplier_instances':sum(x['H'] for x in cases),'quality_instances':sum(x['H'] for x in advanced),'offset_instances':sum(x['H'] for x in offsets)}
    output=Path(__file__).with_name('verification_results.json')
    output.write_text(json.dumps(results,indent=2))
    print('PASS',json.dumps(results['checked_cases']))
    for d in results['hit_tests']:
        print('Q',d['Q'],'H',d['H'],'hits',d['hit_count'],'bound',d['upper_bound'],'examples',[x['h'] for x in d['hits'][:8]])
    print('Quality 1/10',[(d['Q'],d['count']) for d in advanced])

if __name__=='__main__':main()
