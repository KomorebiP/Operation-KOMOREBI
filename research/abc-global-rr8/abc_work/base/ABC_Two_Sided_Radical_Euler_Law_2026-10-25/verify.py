#!/usr/bin/env python3
"""Exact integer checks for shifted-prime powerful part; float only for averages/products."""
from math import gcd, isqrt, log
import json, argparse


def primes_upto(n):
    sieve=bytearray(b'\x01')*(n+1)
    sieve[:2]=b'\x00\x00'
    for p in range(2,isqrt(n)+1):
        if sieve[p]: sieve[p*p::p]=b'\x00'*(((n-p*p)//p)+1)
    return [i for i in range(2,n+1) if sieve[i]]


def factor(n, primes):
    d={}
    for p in primes:
        if p*p>n: break
        if n%p == 0:
            e=0
            while n%p==0:
                e+=1;n//=p
            d[p]=e
    if n>1: d[n]=1
    return d


def m_and_squarefree(n, primes):
    f=factor(n,primes)
    m=1
    for p,e in f.items():
        if e>1: m*=p**(e-1)
    return m, (m==1)


def b_sigma_primepower(p,k,sig):
    if k==1: return 0
    return p**((k-1)*sig)-p**((k-2)*sig)


def check_divisor_identity(maxn, sig, primes):
    """Compute multiplicative divisor-sum exactly in integer exponent case sigma=1.
    For non-integer sigma compare with tight numerical relative tolerance."""
    maxerr=0.
    for n in range(1,maxn+1):
        f=factor(n,primes)
        original=1.
        for p,e in f.items(): original*=p**(sig*max(e-1,0))
        subsum=1.
        for p,e in f.items():
            subsum *= (1.+sum(b_sigma_primepower(p,k,sig) for k in range(2,e+1)))
        err=abs(original-subsum)/max(1.,original)
        maxerr=max(maxerr,err)
        assert err<5e-13,(n,original,subsum,err)
    return maxerr


def limiting_constants(Q,sig,primes):
    m=1.
    sq=1.
    for p in primes:
        if Q%p==0:continue
        ps=p**sig
        m *= (1 + (ps-1)/(p*(p-1)*(1-p**(sig-1))))
        sq *= (1 - 1/(p*(p-1)))
    return m,sq


def run(H=50000):
    plist=primes_upto(H)
    fps=primes_upto(isqrt(1+H*81)+1)
    limprimes=primes_upto(300000)
    sig=.25
    err=check_divisor_identity(10000,sig,fps)
    vals=[]
    for Q in [1,2,3,9,27,81]:
        measured_m=0.
        n_sq=0
        hits=0
        for h in plist:
            c=1+h*Q
            M,sq=m_and_squarefree(c,fps)
            measured_m+=M**sig
            n_sq+=int(sq)
            R=1
            for p in factor(h*Q,fps): R*=p
            for p in factor(c,fps): R*=p
            hits+=int(c>R)
        expected_m,expected_sq=limiting_constants(Q,sig,limprimes)
        vals.append({"Q":Q,"h_prime_count":len(plist),"squarefree_count":n_sq,"squarefree_fraction":n_sq/len(plist),"squarefree_limit_approx":expected_sq,"moment_sigma":sig,"moment_empirical":measured_m/len(plist),"moment_limit_approx":expected_m,"abc_hits":hits})
    # Exact two-sided theorem: for coprime prime multiplier h, an ABC hit iff
    # rad(1+hQ) <= Q/rad(Q). Also check exact primitive triples up to c=10000.
    checked=0
    per_Q=[]
    factor_primes=primes_upto(isqrt(1+H*625)+1)
    for Q in [1,2,4,9,12,27,81,243,256,625]:
        k=Q
        for p in factor(Q,factor_primes):
            k//=p
        found=[]
        for h in plist:
            if Q%h == 0: continue
            c=1+h*Q
            r=1
            for p in factor(c,factor_primes): r*=p
            d=h
            for p in factor(Q,factor_primes): d*=p
            assert (c>d*r)==(r<=k),(h,Q,c,d,r,k)
            checked+=1
            if c>d*r:
                found.append([h,c,r])
        per_Q.append({'Q':Q,'powerful_part_K':k,'abc_hits_h_upto_H':len(found),'first_hits':found[:5]})
    # Integer-valued coefficient convolution, sigma=1, independently checked.
    for n in range(1,10001):
        fac=factor(n,fps)
        via_divisor_expansion=1
        u=1
        for p,e in fac.items():
            u*=p**(e-1)
            via_divisor_expansion*=1+sum(p**(j-1)-p**(j-2) for j in range(2,e+1))
        assert u==via_divisor_expansion,(n,u,via_divisor_expansion)
    # General primitive triples with c <= 10000, counted once with a<=b.
    from math import gcd
    cutoff=10000
    radicals=[1]*(cutoff+1)
    for p in range(2,cutoff+1):
        if radicals[p]==1:
            for n in range(p,cutoff+1,p):radicals[n]*=p
    counts={1000:0,5000:0,10000:0}
    quality12={1000:0,5000:0,10000:0}
    for c in range(2,cutoff+1):
        for a in range(1,c//2+1):
            b=c-a
            if gcd(a,b)!=1:continue
            R=radicals[a]*radicals[b]*radicals[c]
            if c>R:
                for limit in counts:
                    if c<=limit:counts[limit]+=1
                if c**5>R**6:
                    for limit in quality12:
                        if c<=limit:quality12[limit]+=1
    assert counts=={1000:31,5000:80,10000:121},counts
    return {'H':H,'identity_check_n':10000,'identity_max_relative_error':err,
            'integer_divisor_expansion_checks':10000,'prime_product_cutoff':limprimes[-1],
            'prime_multiplier_classification_checks':checked,
            'prime_multiplier_cases':per_Q,'exact_abc_hit_counts':counts,
            'exact_abc_quality_above_1p2_counts':quality12,'samples':vals}

if __name__=='__main__':
    result=run()
    open('/mnt/data/abc_euler_product_upgrade_20261025/results.json','w').write(json.dumps(result,indent=2)+'\n')
    for row in result['samples']:
        print(f"Q={row['Q']:>2} npr={row['h_prime_count']:>4} sqfree={row['squarefree_fraction']:.5f} vs {row['squarefree_limit_approx']:.5f}, moment {row['moment_empirical']:.4f} vs {row['moment_limit_approx']:.4f}, hits={row['abc_hits']}")
    print('max relative identity error:',result['identity_max_relative_error'])
    print('classification checks:',result['prime_multiplier_classification_checks'])
    print('exact abc counts:',result['exact_abc_hit_counts'])
    print('prime Q cases:',[(z['Q'],z['powerful_part_K'],z['abc_hits_h_upto_H']) for z in result['prime_multiplier_cases']])
