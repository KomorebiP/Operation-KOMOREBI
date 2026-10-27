#!/usr/bin/env python3
"""Small exact checks reconstructed from definitions, not source fixtures.

Bounded arithmetic consistency only; this does not prove the infinite claims.
"""
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
import json

def valuation(q, p):
    q = Fraction(q)
    if q == 0:
        return "infinity"
    a, b, e = abs(q.numerator), q.denominator, 0
    while a % p == 0:
        a //= p
        e += 1
    while b % p == 0:
        b //= p
        e -= 1
    return e

def packet(n_modulus, address, last):
    values = [Fraction(1)]
    for n in range(1, last + 1):
        previous = sum(Fraction(comb(n_modulus*n+address, n_modulus*q))*values[q]
                       for q in range(n))
        values.append(-previous / comb(n_modulus*n+address, n_modulus*n))
    return values

def difference(values, n, step, order):
    return sum((-1)**(order-i)*comb(order, i)*values[n+i*step]
               for i in range(order+1))

def main():
    prefixes = {}
    expected = {0:[1,3,4,7,8,10,11], 1:[1,3,4,7,8,10,11],
                2:[4,6,9,13,16,22,23], 3:[2,8,8,15,15,19,23]}
    for j in range(4):
        values = packet(4, j, 7)
        observed = [valuation(difference(values, 0, 1, k), 2) for k in range(1,8)]
        assert observed == expected[j]
        prefixes[str(j)] = observed
    values = packet(6, 3, 2)
    normalized = values[2]-values[1]
    original = factorial(3)*normalized
    assert (values[1], values[2], normalized, original) == (
        Fraction(-1,84), Fraction(703,5460), Fraction(64,455), Fraction(384,455))
    assert valuation(normalized,3) == 0 and valuation(original,3) == 1
    seven = [int(x.numerator*pow(x.denominator,-1,7)%7) for x in packet(2,0,6)[1:]]
    assert seven == [6,5,2,6,5,2]
    record = {
        "status":"PASS", "arithmetic":"fractions.Fraction and Python exact integers",
        "bounds":{"dyadic_addresses":[0,1,2,3],"Newton_orders":[1,2,3,4,5,6,7]},
        "dyadic_Newton_valuations":prefixes,
        "normalization_loss":{"p":3,"N":6,"j":3,"n":1,"step":1,"order":1,
            "C1":str(values[1]),"C2":str(values[2]),"difference":str(normalized),
            "U_difference":str(original),"normalized_v3":0,"original_v3":1},
        "historical_mod7_positive_tail":seven,
        "non_claim":"No universal valuation theorem, infinite completion, or Lean execution follows from these bounded checks."
    }
    Path(__file__).with_name("small_exact_checks.json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({"status":"PASS","dyadic_addresses":4,"Newton_orders_per_address":7,
                      "normalization_counterexample_checked":True,"mod7_rows_checked":6}))

if __name__ == "__main__":
    main()
