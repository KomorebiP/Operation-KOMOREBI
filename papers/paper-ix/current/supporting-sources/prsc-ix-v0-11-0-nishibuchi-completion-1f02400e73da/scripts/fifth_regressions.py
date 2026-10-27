#!/usr/bin/env python3
"""Independent exact-arithmetic mirrors for Paper IX block five.
Author: Komorebi P.
These checks are finite regressions, not execution of extracted Lean code.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, time
from fractions import Fraction as Q
from pathlib import Path

def require_nat(n: int, name: str) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError(name + " must be a nonnegative integer")

def require_prime(p: int) -> None:
    require_nat(p, "p")
    if p < 2 or any(p%d == 0 for d in range(2, math.isqrt(p)+1)):
        raise ValueError("p must be prime")

def packet_coefficients(N: int, j: int, last: int) -> list[Q]:
    require_nat(N,"N"); require_nat(j,"j"); require_nat(last,"last")
    if not N or j >= N: raise ValueError("require N>0 and 0<=j<N")
    values=[Q(1)]
    for n in range(1,last+1):
        values.append(-sum((Q(math.comb(N*n+j,N*q))*values[q] for q in range(n)),Q(0))
                      /math.comb(N*n+j,N*n))
    return values

def window_coefficients(p: int, m: int, j: int, last: int) -> list[Q]:
    require_prime(p);require_nat(m,"m");require_nat(j,"j")
    if not m or j>=p: raise ValueError("require m>0 and j<p")
    return packet_coefficients(m*p,j,last)

def reduced_inverse(p: int, m: int, last: int) -> list[int]:
    require_prime(p);require_nat(m,"m");require_nat(last,"last")
    if not m: raise ValueError("m must be positive in the manuscript interface")
    v=[1]
    for n in range(1,last+1):
        v.append(-sum(math.comb(m*n,m*q)*v[q] for q in range(n))%p)
    return v

def reduce_rational(q: Q, p: int) -> int:
    require_prime(p); q=Q(q)
    if q.denominator%p==0: raise ValueError("nonintegral rational has no residue in this map")
    return q.numerator*pow(q.denominator,-1,p)%p

def prime_decomposition(p: int, precision: int, a: int) -> tuple[int,int]:
    require_prime(p);require_nat(precision,"precision")
    if precision<1: raise ValueError("precision must be at least one")
    modulus=p**precision; a%=modulus
    if math.gcd(a,modulus)!=1: raise ValueError("a must be a unit")
    omega=pow(a,p**(precision-1),modulus)
    return omega,a*pow(omega,-1,modulus)%modulus

def dyadic_decomposition(precision: int, a: int) -> tuple[int,int]:
    require_nat(precision,"precision")
    if precision<2: raise ValueError("sign coordinate requires precision at least two")
    modulus=2**precision; a%=modulus
    if a%2==0: raise ValueError("a must be odd")
    sign=1 if a%4==1 else -1
    return sign%modulus,(sign*a)%modulus

def crt_address(exponent: int, odd_factor: int, r: int) -> tuple[int,int]:
    require_nat(exponent,"exponent");require_nat(odd_factor,"odd_factor");require_nat(r,"r")
    if odd_factor%2!=1: raise ValueError("odd_factor must be positive and odd")
    modulus=2**exponent*odd_factor
    if r>=modulus: raise ValueError("r must be a canonical combined address")
    return r%(2**exponent),r%odd_factor

def crt_reconstruct(exponent: int, odd_factor: int, r2: int, ro: int) -> int:
    require_nat(exponent,"exponent");require_nat(odd_factor,"odd_factor")
    require_nat(r2,"r2");require_nat(ro,"ro")
    two=2**exponent
    if odd_factor%2!=1 or r2>=two or ro>=odd_factor: raise ValueError("invalid CRT address")
    return r2+two*(((ro-r2)*pow(two,-1,odd_factor))%odd_factor)

def run() -> dict:
    start=time.monotonic();rng=random.Random(9052026)
    counts={k:0 for k in ["window_parameter_sets","window_coefficient_rows","unit_cases",
            "root_uniqueness_cases","precision_compatibility_cases","multiplicativity_cases",
            "dyadic_cases","dyadic_unique_cases","crt_addresses","selector_cases","invalid_inputs"]}
    digest=hashlib.sha256()
    def record(x): digest.update((repr(x)+"\n").encode())
    for p in [2,3,5,7,11,13]:
        for m in range(1,5):
            expected=reduced_inverse(p,m,12)
            for j in range(p):
                vals=window_coefficients(p,m,j,12); counts["window_parameter_sets"]+=1
                for n,(q,res) in enumerate(zip(vals,expected)):
                    assert q.denominator%p!=0 and reduce_rational(q,p)==res
                    counts["window_coefficient_rows"]+=1
                    record((p,m,j,n,str(q),res))
    for p in [2,3,5,7,11,13]:
        for precision in range(1,5):
            modulus=p**precision
            aa=list(range(modulus)) if modulus<=250 else [rng.randrange(modulus) for _ in range(150)]
            aa=[a for a in aa if math.gcd(a,modulus)==1]
            roots={a%p:a for a in range(modulus) if a%p and pow(a,p-1,modulus)==1} if modulus<=250 else None
            if roots is not None:
                assert len(roots)==p-1
                assert sum(pow(a,p-1,modulus)==1 for a in range(modulus) if a%p)==p-1
            for a in aa:
                w,v=prime_decomposition(p,precision,a)
                assert w*v%modulus==a and pow(w,p-1,modulus)==1
                assert w%p==a%p and v%p==1 and pow(v,p**(precision-1),modulus)==1
                counts["unit_cases"]+=1
                if roots is not None:
                    assert w==roots[a%p]; counts["root_uniqueness_cases"]+=1
                for k in range(1,precision+1):
                    ww,vv=prime_decomposition(p,k,a)
                    assert w%(p**k)==ww and v%(p**k)==vv
                    counts["precision_compatibility_cases"]+=1
                record((p,precision,a,w,v))
            for _ in range(24):
                a,b=rng.choice(aa),rng.choice(aa)
                wa,va=prime_decomposition(p,precision,a);wb,vb=prime_decomposition(p,precision,b)
                w,v=prime_decomposition(p,precision,a*b)
                assert w==wa*wb%modulus and v==va*vb%modulus
                counts["multiplicativity_cases"]+=1
    for precision in range(2,11):
        modulus=2**precision
        aa=list(range(1,modulus,2)) if precision<=8 else [2*rng.randrange(modulus//2)+1 for _ in range(100)]
        for a in aa:
            sign,v=dyadic_decomposition(precision,a)
            assert sign in [1,modulus-1] and v%4==1 and sign*v%modulus==a
            possibilities=[s for s in [1,modulus-1] if (s*a%modulus)%4==1]
            assert possibilities==[sign]
            counts["dyadic_cases"]+=1;counts["dyadic_unique_cases"]+=1
            record((precision,a,sign,v))
    for exponent in range(5):
        for odd in [1,3,5,7,9,15]:
            modulus=2**exponent*odd;addresses=set()
            for r in range(modulus):
                r2,ro=crt_address(exponent,odd,r);addresses.add((r2,ro))
                assert crt_reconstruct(exponent,odd,r2,ro)==r
                counts["crt_addresses"]+=1
                for n in [0,1,r,modulus+r,2*modulus+1]:
                    assert (n%modulus==r)==(n%(2**exponent)==r2 and n%odd==ro)
                    counts["selector_cases"]+=1
                record((exponent,odd,r,r2,ro))
            assert len(addresses)==modulus
    bad=[
        lambda:prime_decomposition(9,1,2), lambda:prime_decomposition(3,0,1),
        lambda:prime_decomposition(5,3,10),lambda:window_coefficients(3,2,3,1),
        lambda:window_coefficients(4,2,0,1),lambda:window_coefficients(3,0,0,1),
        lambda:reduce_rational(Q(-1,84),3),lambda:dyadic_decomposition(1,1),
        lambda:dyadic_decomposition(3,2),lambda:crt_address(1,2,0),
        lambda:crt_address(2,3,12),lambda:crt_reconstruct(2,3,4,0),
        lambda:crt_address(-1,3,0)]
    for call in bad:
        try: call()
        except ValueError: counts["invalid_inputs"]+=1
        else: raise AssertionError("invalid input accepted")
    assert prime_decomposition(3,2,2)==(8,7)
    assert dyadic_decomposition(3,3)==(7,5)
    assert packet_coefficients(6,3,1)[1]==Q(-1,84)
    return {"status":"PASS","seed":9052026,"counts":counts,"result_digest":digest.hexdigest(),
        "scope":"Independent exact-arithmetic mirrors, not extracted Lean execution or universal proofs.",
        "seconds":round(time.monotonic()-start,3)}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,help="Optional new result file; default prints without overwriting recorded evidence")
    args=parser.parse_args();res=run()
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(res,indent=2)+"\n")
    print(json.dumps(res,indent=2))
