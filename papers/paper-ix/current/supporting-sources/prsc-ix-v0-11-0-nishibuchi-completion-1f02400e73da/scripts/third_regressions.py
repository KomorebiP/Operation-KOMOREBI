#!/usr/bin/env python3
"""Exact finite mirrors of the dyadic formulas; not Lean extraction.
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
import time


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def v2(x: Q) -> int:
    """Finite valuation. Zero must be handled separately, not assigned value zero."""
    if not x:
        raise ValueError('The finite valuation of zero is not defined')
    a, b, result = abs(x.numerator), x.denominator, 0
    while a % 2 == 0:
        a //= 2
        result += 1
    while b % 2 == 0:
        b //= 2
        result -= 1
    return result


def multiply(a: list[Q], b: list[Q], degree: int) -> list[Q]:
    return [sum((a[i]*b[n-i] for i in range(n+1) if i < len(a) and n-i < len(b)), Q(0))
            for n in range(degree+1)]


def reciprocal(a: list[Q]) -> list[Q]:
    if not a or a[0] == 0:
        raise ValueError('The constant term must be nonzero')
    result = [1/a[0]]
    for n in range(1,len(a)):
        result.append(-sum((a[i]*result[n-i] for i in range(1,n+1)), Q(0))/a[0])
    return result


def alpha(m: int) -> Q:
    if m < 0:
        raise ValueError('Index must be nonnegative')
    return Q(2**(2*m+1), factorial(2*m+2))


def betas(max_m: int) -> list[Q]:
    if max_m < 0:
        raise ValueError('Index must be nonnegative')
    return reciprocal([alpha(m) for m in range(max_m+1)])


def source_even_degree(degree: int) -> Q:
    if degree < 0 or degree % 2:
        raise ValueError('Source degree must be nonnegative and even')
    return Q(3**(degree+2)-1, 4*(degree+1)*(degree+2))


def euler_numbers(degree: int) -> list[int]:
    if degree < 0:
        raise ValueError('Degree must be nonnegative')
    e = [1]
    for n in range(1, degree+1):
        e.append(-sum(comb(n, j)*e[n-j] for j in range(2,n+1,2)))
    return e


def bernoulli_numbers(degree: int) -> list[Q]:
    b = [Q(1)]
    for n in range(1,degree+1):
        b.append(-sum((Q(comb(n+1,j))*b[j] for j in range(n)),Q(0))/(n+1))
    return b


def term(row: int, m: int, beta: list[Q]) -> Q:
    if row < 0 or m < 0 or m > row or m >= len(beta):
        raise ValueError('Invalid row/index or insufficient coefficients')
    return beta[m] * 2**(2*m) * (factorial(2*row)//factorial(2*(row-m))) * source_even_degree(2*(row-m))


def truncation(row: int, depth: int, beta: list[Q]) -> Q:
    if row < 0 or depth < 0 or len(beta) <= min(row,depth):
        raise ValueError('Invalid row/depth or insufficient coefficients')
    return sum((term(row,m,beta) for m in range(min(row,depth)+1)), Q(0))


def run() -> dict:
    start=time.monotonic()
    max_row=48;degree=2*max_row
    a=[alpha(m) for m in range(max_row+1)]
    b=betas(max_row)
    e=euler_numbers(degree)
    br=bernoulli_numbers(degree)
    for m in range(max_row+1):
        require(a[m].denominator%2==1, f'Kernel integrality {m}')
        require(b[m].denominator%2==1, f'Inverse integrality {m}')
        require(v2(source_even_degree(2*m))==0, f'Source unit {m}')
        if m:
            require(b[m] == -Q(2**(2*m)*(2*m-1),factorial(2*m))*br[2*m], f'Bernoulli mirror {m}')
    sinc=[Q(1,factorial(n+1)) if n%2==0 else Q(0) for n in range(degree+1)]
    sinc_square=multiply(sinc,sinc,degree)
    require(sinc_square == [a[n//2] if n%2==0 else Q(0) for n in range(degree+1)],'Actual sinhc square')
    inverse_full=reciprocal(sinc_square)
    require(inverse_full == [b[n//2] if n%2==0 else Q(0) for n in range(degree+1)],'Actual inverse coefficient convention')
    r=[source_even_degree(n)/factorial(n) if n%2==0 else Q(0) for n in range(degree+1)]
    reconstructed=multiply([inverse_full[n]*2**n for n in range(degree+1)],r,degree)
    require(reconstructed == [Q(e[n],factorial(n)) for n in range(degree+1)],'Full dyadic identity')
    rows=0;depth_cases=0;zero_errors=0;nonzero_errors=0;retained_exact=0
    observations=[]
    for row in range(max_row+1):
        require(truncation(row,row,b) == e[2*row], f'Exact reconstruction {row}')
        rows+=1
        for depth in range(max_row+4):
            value=truncation(row,depth,b);error=Q(e[2*row])-value
            require((error / 2**(2*depth+2)).denominator%2==1, f'Normalized error {row},{depth}')
            if error:
                nonzero_errors+=1
                require(v2(error)>=2*depth+2, f'Valuation bound {row},{depth}')
            else:
                zero_errors+=1
            if depth>=row:
                require(error==0, f'Full retention {row},{depth}')
                retained_exact+=1
            if row in [0,1,4,6,16,48] and depth<=min(row+1,7):
                observations.append({'even_degree':2*row,'depth':depth,'truncation':str(value),
                    'error':str(error),'v2_error':v2(error) if error else None,
                    'zero_error':not bool(error),'guaranteed_exponent':2*depth+2})
            depth_cases+=1
    require([b[i] for i in range(5)] == [Q(1),-Q(1,3),Q(1,15),-Q(2,189),Q(1,675)],'Beta anchors')
    require([term(4,m,b) for m in range(5)] == [Q(7381,45),-Q(6560,3),Q(163072,15),-Q(204800,9),Q(229376,15)],'Example terms')
    require(v2(Q(e[8])-truncation(4,0,b))==5,'Example depth zero')
    require(v2(Q(e[8])-truncation(4,3,b))==15,'Example depth three')
    # Three negative mathematical controls, not mere rejection by an input validator.
    unscaled=sum((b[m]*Q(factorial(2),factorial(2-2*m))*source_even_degree(2-2*m) for m in range(2)),Q(0))
    require(unscaled != e[2], 'Missing scale incorrectly accepted')
    require(b[1] != -Q(2,3),'Factorial convention incorrectly accepted')
    require(not v2(Q(e[8])-truncation(4,0,b))>=6,'Excess precision incorrectly accepted')
    return {'status':'PASS','author':'Komorebi P.','created_utc':datetime.now(timezone.utc).isoformat(),
            'max_even_degree':degree,'kernel_integrality_cases':max_row+1,'inverse_integrality_cases':max_row+1,
            'source_unit_cases':max_row+1,'bernoulli_formula_finite_checks':max_row,'series_coefficients_compared':degree+1,
            'exact_reconstruction_rows':rows,'truncation_depth_cases':depth_cases,'nonzero_errors_checked':nonzero_errors,
            'zero_errors_handled_separately':zero_errors,'full_retention_cases':retained_exact,
            'mathematical_negative_controls':3,'selected_observations':observations,
            'seconds':round(time.monotonic()-start,3),
            'boundary':'Independent exact-rational finite mirrors. Not Lean extraction. Not a replacement for universal proofs. Bernoulli formula checked only on this finite range.'}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=run();report['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    text=json.dumps(report,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text,end='')
    return 0


if __name__=='__main__': raise SystemExit(main())
