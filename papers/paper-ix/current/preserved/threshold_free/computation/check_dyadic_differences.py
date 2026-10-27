#!/usr/bin/env python3
"""Bounded exact checks of the reciprocal N=4 generalized Euler coefficients.

All large-range arithmetic is exact in Z/2^P Z. Every reciprocal denominator
binom(4m+j,j) is odd for 0 <= j <= 3 by Lucas' theorem, so no division loses
precision. A nonzero residue determines its exact 2-adic valuation; a zero
residue proves only the lower bound P. Independent rational ordinary-series
inversion cross-checks the initial coefficients.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
import json
import platform
import time

VERSION = "1.0.0"


def valuation(value: int, precision: int) -> int:
    return (value & -value).bit_length() - 1 if value else precision


def rational_coefficients(j: int, bound: int) -> list[Fraction]:
    """Invert the ordinary power series in z=t^4, then restore (4n)!."""
    source = [Fraction(factorial(j), factorial(4*n+j)) for n in range(bound+1)]
    reciprocal = [Fraction(1)]
    for n in range(1, bound+1):
        reciprocal.append(-sum((source[q] * reciprocal[n-q] for q in range(1,n+1)), Fraction(0)))
    return [coefficient * factorial(4*n) for n, coefficient in enumerate(reciprocal)]


def rational_to_mod(value: Fraction, modulus: int) -> int:
    assert value.denominator & 1, "A rational coefficient is not dyadically integral"
    return value.numerator * pow(value.denominator, -1, modulus) % modulus


def differences(values: list[int], step: int, modulus: int) -> list[int]:
    return [(values[n+step] - values[n]) % modulus for n in range(len(values)-step)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound", type=int, default=512)
    parser.add_argument("--precision", type=int, default=4096)
    parser.add_argument("--order", type=int, default=128)
    parser.add_argument("--rational-bound", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert args.bound > 0 and args.precision > 2*args.bound
    assert 0 <= args.rational_bound <= args.bound
    started = time.monotonic()
    modulus = 1 << args.precision
    triangular_binomials = [[comb(4*n,4*k) % modulus for k in range(n)] for n in range(1,args.bound+1)]
    steps = [1,2,3,4,5,7,8,9,13,16,31,32,63,64,127]
    mixed_step_lists = [[1,2],[2,2],[1,3],[3,5],[1,1,2],[2,3,4],[1,2,3,4],[1,3,5,7]]
    mixed_step_lists += [[u]*k for u in [1,2,3,4,7,8,13] for k in range(1,9)]
    mixed_step_lists += [[1,2,4,8,16,32,64][:k] for k in range(1,8)]
    result = {
        "version": VERSION, "python": platform.python_version(),
        "coefficient_definition": "C_j(n)=(4n)![t^(4n)](j! sum_{m>=0}t^(4m)/(4m+j)!)^(-1)",
        "bounds": vars(args) | {"output": str(args.output)},
        "modular_division_justification": "All binom(4m+j,j) are odd by Lucas; no precision loss.",
        "families": [], "non_claims": ["No tested bound implies the universal conjecture.", "A zero modulo 2^P only certifies valuation >=P."],
    }
    failures = []
    counts = {"rational_coefficients":0,"first_shift_equalities":0,"higher_difference_inequalities":0,"mixed_difference_inequalities":0,"newton_equalities":0}
    for j in range(4):
        denominators = [comb(4*m+j,j) for m in range(args.bound+1)]
        assert all(d & 1 for d in denominators)
        inverses = [pow(d,-1,modulus) for d in denominators]
        values = [1]
        for n in range(1,args.bound+1):
            values.append(-sum(c*values[k]*inverses[n-k] for k,c in enumerate(triangular_binomials[n-1])) % modulus)
        rational = rational_coefficients(j,args.rational_bound)
        for n,c in enumerate(rational):
            counts["rational_coefficients"] += 1
            if values[n] != rational_to_mod(c,modulus): failures.append({"check":"independent rational inversion","j":j,"n":n})
        first_constant = [1,1,4,2][j]
        for h in range(1,args.bound+1):
            expected = valuation(h,args.precision) + first_constant
            for n in range(args.bound-h+1):
                counts["first_shift_equalities"] += 1
                actual = valuation((values[n+h]-values[n])%modulus,args.precision)
                if actual != expected: failures.append({"check":"first shift law","j":j,"n":n,"h":h,"expected":expected,"actual":actual})
        newton = []
        row_minima = []
        row = values[:]
        for k in range(args.bound+1):
            newton.append(valuation(row[0],args.precision))
            row_minima.append(min(valuation(c,args.precision) for c in row))
            row = differences(row,1,modulus)
        for k in range(1,args.bound+1):
            counts["newton_equalities"] += 1
            if j in (0,1):
                expected = 2*k-k.bit_count()
                if newton[k] != expected: failures.append({"check":"Newton exact j0j1","j":j,"k":k,"expected":expected,"actual":newton[k]})
            elif j==2 and k>=3:
                expected = 14*(k//4)+[-1,2,8,9][k%4]
                if newton[k] != expected: failures.append({"check":"Newton exact j2 candidate","j":j,"k":k,"expected":expected,"actual":newton[k]})
        higher_ranges = []
        surplus = [0,0,3,1][j]
        for u in steps:
            row = values[:]
            maximum_order = min(args.order,args.bound//u)
            for k in range(1,maximum_order+1):
                row = differences(row,u,modulus)
                expected_bound = 2*k-k.bit_count()+k*valuation(u,args.precision)+surplus
                for n,c in enumerate(row):
                    counts["higher_difference_inequalities"] += 1
                    actual = valuation(c,args.precision)
                    if actual < expected_bound: failures.append({"check":"higher analytic bound","j":j,"n":n,"k":k,"u":u,"expected_lower_bound":expected_bound,"actual":actual})
            higher_ranges.append({"step":u,"maximum_order":maximum_order,"condition":"n+k*u<=bound"})
        mixed_ranges = []
        for sequence in mixed_step_lists:
            if sum(sequence)>args.bound: continue
            row=values[:]
            for u in sequence: row=differences(row,u,modulus)
            k=len(sequence)
            expected_bound = 2*k-k.bit_count()+sum(valuation(u,args.precision) for u in sequence)+surplus
            actual_min=min(valuation(c,args.precision) for c in row)
            for n,c in enumerate(row):
                counts["mixed_difference_inequalities"] += 1
                if valuation(c,args.precision)<expected_bound: failures.append({"check":"mixed analytic bound","j":j,"n":n,"steps":sequence,"expected_lower_bound":expected_bound,"actual":valuation(c,args.precision)})
            mixed_ranges.append({"steps":sequence,"expected_lower_bound":expected_bound,"actual_minimum":actual_min,"bases_tested":len(row)})
        result["families"].append({"j":j,"independent_initial_rationals":[str(c) for c in rational],"newton_valuations":newton,"unit_step_row_minimum_valuations":row_minima,"higher_step_ranges":higher_ranges,"mixed_step_ranges":mixed_ranges,"analytic_bound_surplus":surplus})
        print(json.dumps({"j":j,"newton_first_20":newton[:21],"first_shift_constant":first_constant,"failures_so_far":len(failures)}),flush=True)
    result.update(counts=counts, failures=failures, passed=not failures,runtime_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":not failures,"counts":counts,"runtime_seconds":result["runtime_seconds"]}),flush=True)
    if failures: raise SystemExit(1)


if __name__=="__main__": main()
