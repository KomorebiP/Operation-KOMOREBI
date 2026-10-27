#!/usr/bin/env python3
"""Independent exact-arithmetic mirrors for Paper IX's second block.

These are finite regression tests, not extraction or execution of Lean definitions.
Author: Komorebi P.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb, factorial
from pathlib import Path


def euler_numbers(degree: int) -> list[int]:
    """Binomial inverse of cosh, independent of the congruential Lean construction."""
    if degree < 0:
        raise ValueError('Degree must be nonnegative')
    result = [1]
    for n in range(1, degree + 1):
        result.append(-sum(comb(n, r) * result[n-r] for r in range(2, n+1, 2)))
    return result


def product(a: list[Q], b: list[Q], degree: int) -> list[Q]:
    return [sum((a[r] * b[n-r] for r in range(n+1)), Q(0)) for n in range(degree+1)]


def reciprocal(a: list[Q]) -> list[Q]:
    if not a or not a[0]:
        raise ValueError('A nonzero constant term is required')
    b = [1/a[0]]
    for n in range(1,len(a)):
        b.append(-sum((a[r]*b[n-r] for r in range(1,n+1)),Q(0))/a[0])
    return b


def signed_inverse(e: list[int]) -> list[int]:
    return [sum(comb(n,r)*e[r]*e[n-r] for r in range(n+1)) for n in range(len(e))]


def odd_power(p: int, degree: int) -> int:
    if p < 0 or degree < 0:
        raise ValueError('Length and degree must be nonnegative')
    return sum((-1)**a * (2*a+1)**degree for a in range(p))


def truncated(p: int, row: int, depth: int, inverse: list[int]) -> int:
    if p < 1 or p%2 != 1:
        raise ValueError('The reconstruction requires an odd positive length')
    if row < 0 or depth < 0 or len(inverse) <= 2*row:
        raise ValueError('Invalid row/depth or insufficient inverse coefficients')
    return sum(comb(2*row,2*m)*inverse[2*m]*p**(2*m)*odd_power(p,2*(row-m))
               for m in range(min(row,depth)+1))


def run() -> dict:
    max_row=12
    degree=2*max_row+1
    e=euler_numbers(degree)
    b=signed_inverse(e)
    cosh=[Q(int(n%2==0),factorial(n)) for n in range(degree+1)]
    sech=reciprocal(cosh)
    cosine=[Q((-1)**(n//2),factorial(n)) if n%2==0 else Q(0) for n in range(degree+1)]
    sine=[Q((-1)**(n//2),factorial(n)) if n%2 else Q(0) for n in range(degree+1)]
    secant=reciprocal(cosine)
    tangent=product(sine,secant,degree)
    zigzag=[(secant[n]+tangent[n])*factorial(n) for n in range(degree+1)]
    for n in range(degree+1):
        assert e[n]==sech[n]*factorial(n)
    for m in range(max_row+1):
        assert b[2*m]==(-1)**m*zigzag[2*m+1]
    counts={'euler_generating_coefficients':degree+1,
            'signed_zigzag_bridges':max_row+1,
            'odd_generating_coefficients':0,'even_generating_coefficients':0,
            'reconstruction_rows':0,'congruence_depths':0,'full_depth_exact':0}
    lengths=list(range(1,36,2))
    for p in lengths:
        factor=[Q((1 if n==0 else 0)+(2*p)**n,2*factorial(n)) for n in range(degree+1)]
        closed=product(factor,sech,degree)
        cosh_p=[Q(p**n,factorial(n)) if n%2==0 else Q(0) for n in range(degree+1)]
        even_closed=product(product(cosh_p,cosh_p,degree),sech,degree)
        for n in range(degree+1):
            assert closed[n]==Q(odd_power(p,n),factorial(n))
            assert even_closed[n]==(closed[n] if n%2==0 else 0)
            counts['odd_generating_coefficients']+=1
            counts['even_generating_coefficients']+=1
        for row in range(max_row+1):
            assert truncated(p,row,row,b)==e[2*row]
            counts['reconstruction_rows']+=1
            for depth in range(row+4):
                t=truncated(p,row,depth,b)
                assert (e[2*row]-t)%p**(2*depth+2)==0
                counts['congruence_depths']+=1
                if depth>=row:
                    assert t==e[2*row]
                    counts['full_depth_exact']+=1
    rejected=0
    for p,row,depth in [(0,0,0),(2,1,1),(4,3,1),(6,4,0),(-1,1,1),(3,-1,0),(3,1,-1)]:
        try:
            truncated(p,row,depth,b)
        except ValueError:
            rejected+=1
        else:
            raise AssertionError('Invalid reconstruction input accepted')
    # This is the manuscript's exact row, not a tolerance comparison.
    error=e[8]-truncated(5,4,2,b)
    assert error==-2731000000 and error%(5**6)==0 and error%(5**7)!=0
    assert odd_power(2,0)==0 and e[0]==1
    assert e[:9]==[1,0,-1,0,5,0,-61,0,1385]
    return {'status':'PASS','created_utc':datetime.now(timezone.utc).isoformat(),
            'mode':'independent exact Python mirrors, not Lean extraction',
            'max_even_row_index':max_row,'max_generating_degree':degree,
            'odd_lengths':lengths,'counts':counts,'invalid_inputs_rejected':rejected,
            'sharp_example':{'p':5,'euler_degree':8,'depth':2,'euler':e[8],
                             'truncation':truncated(5,4,2,b),'error':error,
                             'divisible_by_5_power_6':True,'divisible_by_5_power_7':False},
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    text=json.dumps(run(),indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    print(text,end='')


if __name__=='__main__':
    main()
