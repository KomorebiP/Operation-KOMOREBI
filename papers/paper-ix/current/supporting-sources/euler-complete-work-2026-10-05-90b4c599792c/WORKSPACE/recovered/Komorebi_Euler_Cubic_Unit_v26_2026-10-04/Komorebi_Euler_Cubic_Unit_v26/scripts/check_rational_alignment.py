#!/usr/bin/env python3
"""Independent finite rational checks. Supplementary checks; the universal identification is proved in Euler/EulerIdentification.lean."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from math import comb, factorial
from pathlib import Path
import json


def bernoulli_table(n: int) -> list[Q]:
    b = [Q(1)]
    for m in range(1, n + 1):
        b.append(-sum((Q(comb(m+1,k))*b[k] for k in range(m)), Q(0)) / (m+1))
    return b


def valuation2(x: Q) -> int:
    if not x:
        raise ValueError('zero has infinite valuation; no finite value returned')
    def v(n: int) -> int:
        n = abs(n)
        return (n & -n).bit_length()-1
    return v(x.numerator)-v(x.denominator)


def source(n: int) -> Q:
    return Q(9**(n+1)-1, 8*(n+1)*(2*n+1))


def run(limit: int) -> dict:
    if not 1 <= limit <= 128:
        raise ValueError('Choose 1 <= --limit <= 128 for a bounded exact audit')
    b=bernoulli_table(2*limit)
    kappas=[-Q(2**(4*m)*(2*m-1))*b[2*m] for m in range(limit+1)]
    e=[1]
    for n in range(1,limit+1):
        e.append(-sum(comb(2*n,2*m)*e[m] for m in range(n)))
    counters={k:0 for k in ['source_rows','source_mod8','kernel_valuations','euler_rows',
        'nonempty_tail_bounds','sharp_first_rows']}
    for n in range(limit+1):
        newton=sum((Q(8**q,factorial(q+1))*Q(factorial(n),factorial(n-q))
                    for q in range(n+1)),Q(0))/(2*n+1)
        assert newton==source(n)
        counters['source_rows']+=1
        diff=source(n)-(1+2*n+4*n*n)
        assert diff==0 or valuation2(diff)>=3
        counters['source_mod8']+=1
        row=[kappas[m]*comb(2*n,2*m)*source(n-m) for m in range(n+1)]
        assert sum(row,Q(0))==e[n]
        counters['euler_rows']+=1
        if n:
            assert valuation2(kappas[n])==4*n-1
            counters['kernel_valuations']+=1
        for m in range(n):
            tail=sum(row[m+1:],Q(0))
            assert tail==0 or valuation2(tail)>=4*m+3
            counters['nonempty_tail_bounds']+=1
        if n:
            assert row[-1]==kappas[n]
            assert valuation2(row[-1])==4*(n-1)+3
            counters['sharp_first_rows']+=1
    return {'status':'PASS','limit':limit,'counts':counters,
            'total_registered_checks':sum(counters.values()),
            'method':'exact Python Fraction arithmetic; Bernoulli and Euler values from independent recurrences',
            'boundary':'Finite corroboration only. The universal identity is separately kernel-checked in Euler/EulerIdentification.lean and Euler/EulerError.lean.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--limit',type=int,default=32)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists(): raise FileExistsError('Refusing existing output')
    result=run(args.limit)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
