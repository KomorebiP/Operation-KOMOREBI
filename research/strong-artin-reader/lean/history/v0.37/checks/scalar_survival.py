#!/usr/bin/env python3
"""Exact finite survival test and digit lift for scalar unit power roots.

The input target is an integer representative. Survival uses only its residue
modulo p^H. Extra digits requested by lift_root require matching target digits.
The proof of the infinite assertion is in src/ResonantScalarHorizon.lean.
"""
from __future__ import annotations
import argparse,json,math

def prime(p):
    return p >= 2 and all(p % q for q in range(2, math.isqrt(p) + 1))

def valuation(p, d):
    if d <= 0:
        raise ValueError('Degree must be positive')
    a = 0
    while d % p == 0:
        d //= p
        a += 1
    return a

def certificate(p, d, m, prefix, target, candidate_cap=1000000):
    if not prime(p) or m <= 0 or prefix % p == 0:
        raise ValueError('Require prime p, positive prefix depth, and a unit prefix')
    s = valuation(p, d)
    k = max(m, s + 1)
    horizon = k + s
    mod_m,mod_k,mod_h = p**m,p**k,p**horizon
    count = p**(k-m)
    if count > candidate_cap:
        raise RuntimeError(f'Candidate cap exceeded: {count} > {candidate_cap}; no verdict')
    prefix %= mod_m
    # Test canonical refinements at depth k. The deep-prefix theorem proves
    # that each such refinement survives iff this single congruence holds.
    survivors = [b for b in range(prefix, mod_k, mod_m)
                 if pow(b,d,mod_h) == target % mod_h]
    return dict(p=p,degree=d,prefix_depth=m,prefix=prefix,
                degree_valuation=s,refinement_depth=k,horizon=horizon,
                target_mod_horizon=target%mod_h,candidates_tested=count,
                surviving_refinements=survivors,survives=bool(survivors))

def lift_root(p,d,m,prefix,target,precision):
    cert = certificate(p,d,m,prefix,target)
    if not cert['survives']:
        raise ValueError('The prescribed prefix has no root')
    s,k = cert['degree_valuation'],cert['refinement_depth']
    x = cert['surviving_refinements'][0]
    steps = []
    for j in range(k,max(k,precision)):
        modulus = p**(j+s+1)
        error = (pow(x,d,modulus) - target) % modulus
        assert error % (p**(j+s)) == 0
        quotient = error // (p**(j+s))
        derivative_unit = (d//(p**s))*pow(x,d-1,p) % p
        assert derivative_unit != 0
        digit = -quotient * pow(derivative_unit,-1,p) % p
        x += digit*p**j
        assert pow(x,d,modulus) == target % modulus
        steps.append(dict(root_precision=j+1,equation_precision=j+s+1,digit=digit))
    return dict(certificate=cert,root=x%(p**precision),precision=precision,steps=steps)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ['p','degree','prefix-depth','prefix','target']:
        ap.add_argument('--'+flag,type=int,required=True)
    ap.add_argument('--precision',type=int)
    a=ap.parse_args()
    if a.precision is not None and a.precision < a.prefix_depth:
        ap.error('Requested precision must preserve the prefix')
    fn=lift_root if a.precision else certificate
    args=[a.p,a.degree,a.prefix_depth,a.prefix,a.target]
    if a.precision:args.append(a.precision)
    print(json.dumps(fn(*args),indent=2))

if __name__=='__main__':main()
