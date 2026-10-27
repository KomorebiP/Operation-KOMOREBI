#!/usr/bin/env python3
"""Exact counterexamples to an attempted valuation lift, with a second formula."""
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys

from packet_core import tau_triangular, tau_from_product, valuation


def primes_to(n):
    mark = bytearray(b'\x01')*(n+1)
    mark[:2] = b'\x00\x00'
    for d in range(2, isqrt(n)+1):
        if mark[d]:
            mark[d*d::d] = b'\x00'*((n-d*d)//d+1)
    return [p for p in range(2, n+1) if mark[p]]


def divisor_sums(n):
    sums = [[0]*(n+1) for _ in range(3)]
    for d in range(1, n+1):
        powers = [d**3, d**5, d**7]
        for j in range(d, n+1, d):
            for k in range(3):
                sums[k][j] += powers[k]
    return sums


def tau_eisenstein(n, sums):
    """[q^n](E4 E8-E6^2)/1728, independently of triangular recurrence."""
    s3, s5, s7 = sums
    numerator = 240*s3[n] + 480*s7[n] + 1008*s5[n]
    numerator += 115200*sum(s3[k]*s7[n-k] for k in range(1, n))
    numerator -= 254016*sum(s5[k]*s5[n-k] for k in range(1, n))
    answer, remainder = divmod(numerator, 1728)
    assert remainder == 0
    return answer


def main(path):
    bound = 150000
    tau = tau_triangular(bound)
    assert tau[:129] == tau_from_product(128)
    primes = primes_to(bound)
    rows = []
    expected = {2:(81919,20,14), 3:(8747,8,7), 5:(499,4,3)}
    for ell in (2,3,5):
        candidates = [p for p in primes if p != ell and (p+1)%ell == 0]
        bad = [p for p in candidates if valuation(tau[p],ell) != valuation(p+1,ell)]
        p = bad[0]
        assert (p,valuation(tau[p],ell),valuation(p+1,ell)) == expected[ell]
        rows.append({'ell':ell,'first_discrepancy_prime':p,'tau':tau[p],
                     'tau_valuation':valuation(tau[p],ell),
                     'p_plus_one_valuation':valuation(p+1,ell),
                     'candidate_primes_tested':len(candidates),
                     'discrepancies_in_range':len(bad)})
    chosen = [499,1249,8747,81919]
    sums = divisor_sums(max(chosen))
    independent = []
    for n in list(range(1,129))+chosen:
        answer = tau_eisenstein(n,sums)
        assert answer == tau[n]
        if n in chosen:
            assert all(n%d for d in range(2,isqrt(n)+1))
            independent.append({'prime':n,'tau':answer,
                                'v2':valuation(answer,2),'v3':valuation(answer,3),
                                'v5':valuation(answer,5)})
    assert valuation(tau[1249],5)==3 < valuation(1250,5)==4
    result={'status':'passed','bound':bound,'number_of_primes':len(primes),
            'first_discrepancies':rows,'independent_coefficients':independent,
            'direct_product_crosschecks':128,'eisenstein_crosschecks':132,
            'tau_array_sha256':hashlib.sha256(json.dumps(tau,separators=(',',':')).encode()).hexdigest()}
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main(sys.argv[1])
