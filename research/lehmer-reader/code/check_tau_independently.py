#!/usr/bin/env python3
"""Exact independent Delta coefficients through 512, never a universal proof.

Compare the historical triangular recurrence against the defining binomial
product and an independently implemented logarithmic-derivative recurrence.
The table's integer tau values are exact. A floating ordinate is supplied only
for plotting tau(n)/(2*n^(11/2)), not as mathematical evidence.
"""
from pathlib import Path
import argparse
import importlib.util
import json
from math import isqrt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/checks/packet_core.py'

def logarithmic_derivative_tau(bound):
    # F = product (1-q^k)^24. n F_n = -24 sum sigma_1(j) F_(n-j).
    sigma = [0]*bound
    for d in range(1, bound):
        for j in range(d, bound, d):
            sigma[j] += d
    f = [1]+[0]*(bound-1)
    for n in range(1, bound):
        f[n], remainder = divmod(-24*sum(sigma[j]*f[n-j] for j in range(1,n+1)), n)
        assert remainder == 0
    return [0]+f

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('reviewed_packet_core', INPUT)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    bound = 512
    triangular = core.tau_triangular(bound)
    product = core.tau_from_product(bound)
    logarithmic = logarithmic_derivative_tau(bound)
    assert triangular == product == logarithmic
    assert triangular[1:11] == [1,-24,252,-1472,4830,-6048,-16744,84480,-113643,-115920]
    rows = [{'n':n,'tau':triangular[n],
             'prime': n>=2 and all(n%d for d in range(2,isqrt(n)+1)),
             'plot_normalized_tau': triangular[n]/(2*n**5.5)} for n in range(1,bound+1)]
    result = {'status':'PASS','coefficient_domain':'Z, exact arbitrary-precision integers',
              'bound':bound,'methods':['Historical triangular recurrence',
                         'Direct defining product via exact binomial factors',
                         'Independent logarithmic-derivative divisor-sum recurrence'],
              'equal_coefficient_count':bound,
              'nonzero_coefficient_count':sum(triangular[n] != 0 for n in range(1,bound+1)),
              'rows':rows,
              'non_claims':['No proof of Lehmer outside the finite executed bound',
                            'The normalized plot column is floating point only for display']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}, sort_keys=True))

if __name__ == '__main__':
    main()
