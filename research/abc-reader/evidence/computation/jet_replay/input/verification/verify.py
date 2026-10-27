#!/usr/bin/env python3
"""Exact finite verification for the ABC jet-determinant continuation.

Standard-library only. No floating-point value is proof-bearing.
The general infinite-series/valuation statements are proved separately in proofs/.
This verifier tests finite identities, exact modular evaluations, and counterexample bounds.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations
from math import comb, factorial, gcd, isqrt, lcm, prod
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
COUNTS: Counter[str] = Counter()


def check(condition: bool, family: str, context: object = None) -> None:
    if not condition:
        raise AssertionError(f"{family}: {context!r}")
    COUNTS[family] += 1


def primes_up_to(n: int) -> list[int]:
    return [p for p in range(2, n + 1) if all(p % d for d in range(2, isqrt(p) + 1))]


def factor(n: int) -> dict[int, int]:
    if n < 1:
        raise ValueError("factor expects a positive integer")
    out: dict[int, int] = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p = 3 if p == 2 else p + 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def rad(n: int) -> int:
    return prod(factor(n))


def vp_int(n: int, p: int) -> int:
    if n == 0:
        raise ValueError("v_p(0) is infinite; do not silently substitute an integer")
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def vp(q: F | int, p: int) -> int:
    q = F(q)
    return vp_int(q.numerator, p) - vp_int(q.denominator, p)


def det(matrix: list[list[F | int]]) -> F:
    a = [[F(x) for x in row] for row in matrix]
    n = len(a)
    if any(len(row) != n for row in a):
        raise ValueError("matrix must be square")
    answer = F(1)
    for i in range(n):
        pivot = next((j for j in range(i, n) if a[j][i]), None)
        if pivot is None:
            return F(0)
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            answer = -answer
        t = a[i][i]
        answer *= t
        for j in range(i + 1, n):
            c = a[j][i] / t
            for k in range(i + 1, n):
                a[j][k] -= c * a[i][k]
            a[j][i] = F(0)
    return answer


def bareiss(matrix: list[list[int]]) -> int:
    a = [row[:] for row in matrix]
    n = len(a)
    if n == 0:
        return 1
    sign = 1
    previous = 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        current = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * current - a[i][k] * a[k][j]
                quotient, rem = divmod(numerator, previous)
                if rem:
                    raise ArithmeticError("Bareiss division was not exact")
                a[i][j] = quotient
            a[i][k] = 0
        previous = current
    return sign * a[-1][-1]


def vandermonde_coefficient(indices: tuple[int, ...]) -> F:
    return F(1, prod(indices)) * prod((F(1, a) - F(1, b)) ** 2 for a, b in combinations(indices, 2))


def moment_det(r: int, indices: list[int], t: F) -> F:
    moments = [sum((t**k / k**s for k in indices), F(0)) for s in range(1, 2 * r)]
    return det([[moments[i + j] for j in range(r)] for i in range(r)])


def gram_polynomial(r: int, indices: list[int]) -> dict[int, F]:
    out: dict[int, F] = defaultdict(F)
    for ks in combinations(indices, r):
        out[sum(ks)] += vandermonde_coefficient(ks)
    return dict(out)


def first_units(p: int, r: int) -> list[int]:
    return [j + (j - 1) // (p - 1) for j in range(1, r + 1)]


def unit_energy(p: int, r: int) -> int:
    # Minimum sum of v_p(k_j-k_i) over r distinct p-units.
    answer = 0
    residue_classes = p - 1
    while residue_classes < r:
        q, b = divmod(r, residue_classes)
        answer += residue_classes * q * (q - 1) // 2 + b * q
        residue_classes *= p
    return answer


def denominator_budget(r: int, p: int) -> int:
    # For each ordered index i, bound (2r-1)v_p(k_i) - (k_i-i).
    a = 2 * r - 1
    total = 0
    for i in range(1, r + 1):
        best = 0
        h, power = 1, p
        while True:
            least_multiple = ((i + power - 1) // power) * power
            best = max(best, a * h - (least_multiple - i))
            # Beyond this point the upper envelope a*h-power+r is negative
            # and its successive differences are nonpositive.
            if power > a * h + r and (p - 1) * power >= a:
                break
            h += 1
            power *= p
        total += best
    return total


def jet_coefficients(m: int) -> list[int]:
    coefficients = [0, 1]
    for j in range(1, m + 1):
        new = [0] * (len(coefficients) + 1)
        for s, c in enumerate(coefficients):
            new[s] -= c
            new[s + 1] += j * c
        coefficients = new
    return coefficients


def verify_jets() -> None:
    for m in range(0, 31):
        cs = jet_coefficients(m)
        check(sum(abs(c) for c in cs) == factorial(m + 1), "jet_l1", m)
        check(gcd(*cs) == 1, "jet_primitive", m)
        for k in range(1, 81):
            actual = sum((F(c, factorial(m + 1) * k**s) for s, c in enumerate(cs)), F(0))
            expected = F((-1)**m * comb(k, m + 1), k**(m + 2)) if k >= m + 1 else F(0)
            check(actual == expected, "jet_coefficient_identity", (m, k))
        for p in primes_up_to(31):
            first = m + 1 if (m + 1) % p else m + 2
            c = F(comb(first, m + 1), first**(m + 2))
            check(vp(c, p) == 0, "jet_depleted_leading_unit", (m, p))


def verify_normalization() -> list[dict[str, int]]:
    records = []
    for c in range(2, 251):
        for a in range(1, (c + 1) // 2):
            b = c - a
            if gcd(a, b) != 1:
                continue
            ra, rb, rc = rad(a), rad(b), rad(c)
            R = ra * rb * rc
            Q = a * b * c // R
            check(F(Q, a * b) == F(c, R), "abc_balanced_defect", (a, b, c))
            check(F(c // rc, ra * rb) == F(c, R), "abc_output_normalization", (a, b, c))
    # Symbolic family: 1 + 2^k = 2^k+1, checked for a finite exact sample.
    for k in range(1, 31):
        c = 2**k + 1
        R = 2 * rad(c)
        Q = 2**k * c // R
        check(Q >= 2**(k-1), "unit_family_Q_lower", k)
        check(R <= 3 * 2**k, "unit_family_R_upper", k)
        check(Q**2 >= R if k >= 4 else True, "unit_family_sqrt_counterexamples", k)
        if k in (4, 8, 12, 16, 20, 24, 28, 30):
            records.append({"k": k, "a": 1, "b": 2**k, "c": c, "R": R, "Q": Q})
    # Balanced square family: t^2 + (t+1)^2 = c.
    for t in range(1, 81):
        a, b, c = t*t, (t+1)**2, t*t+(t+1)**2
        R = rad(a*b*c)
        Q = a*b*c // R
        check(gcd(a, b) == 1, "square_family_primitive", t)
        check(Q >= t*(t+1), "square_family_Q_lower", t)
        check(R <= t*(t+1)*c, "square_family_R_upper", t)
    return records


def verify_determinants() -> None:
    for r in range(1, 6):
        for K in range(r, r + 5):
            indices = list(range(1, K + 1))
            polynomial = gram_polynomial(r, indices)
            S = r * (r + 1) // 2
            top = r*K - r*(r-1)//2
            leading = F(1, prod(k**(2*k-1) for k in range(1, r + 1)))
            check(min(polynomial) == S and max(polynomial) == top, "det_exact_degrees", (r, K))
            check(polynomial[S] == leading, "det_exact_leading_coefficient", (r, K))
            for t in (F(1, 3), F(2, 3), F(-1, 2)):
                expanded = sum((co * t**degree for degree, co in polynomial.items()), F(0))
                computed = moment_det(r, indices, t)
                check(computed == expanded, "finite_cauchy_binet", (r, K, str(t)))
                if t > 0:
                    check(computed > 0, "finite_positive_definite", (r, K, str(t)))
            L = lcm(*indices)
            scaled = {d: c * L**(r*r) for d, c in polynomial.items()}
            check(all(c.denominator == 1 for c in scaled.values()), "truncation_denominator_clearance", (r, K))
            for p in [p for p in primes_up_to(29) if p > K][:3]:
                for e in (1, 2):
                    a, c = 1, p**e
                    integer = sum((int(co) * a**degree * c**(top-degree) for degree, co in scaled.items()))
                    check(integer % p != 0, "truncation_loses_output_contact", (r, K, p, e))
    check(gram_polynomial(2, [1, 2]) == {3:F(1,8)}, "explicit_rank2_K2")
    check(gram_polynomial(2, [1, 2, 3]) == {3:F(1,8),4:F(4,27),5:F(1,216)}, "explicit_rank2_K3")


def verify_residue_energy() -> None:
    for p in (2, 3, 5, 7):
        candidates = first_units(p, 11)
        for r in range(1, 7):
            minimum = unit_energy(p, r)
            first = tuple(candidates[:r])
            first_energy = sum(vp_int(b-a,p) for a,b in combinations(first,2))
            check(first_energy == minimum, "unit_energy_first_set", (p, r))
            for ks in combinations(candidates, r):
                energy = sum(vp_int(b-a,p) for a,b in combinations(ks,2))
                check(energy >= minimum, "unit_energy_minimality", (p, r, ks))


def verify_padic_determinants() -> list[dict[str, int]]:
    records = []
    for p in (2, 3, 5, 7, 11, 13, 17):
        for r in range(1, 9):
            S = sum(first_units(p, r))
            energy = unit_energy(p, r)
            for e in (1, 2, 3):
                predicted = e*S + 2*energy
                precision = predicted + 2
                modulus = p**precision
                # Terms beyond K are zero mod p^precision, since all k are p-units.
                K = (precision-1)//e
                for unit in (1, p-1, p+1):
                    t = p**e * unit
                    moments = []
                    for s in range(1, 2*r):
                        total = 0
                        for k in range(1, K+1):
                            if k % p:
                                total += pow(t,k,modulus) * pow(pow(k,s,modulus),-1,modulus)
                        moments.append(total % modulus)
                    matrix = [[moments[i+j] for j in range(r)] for i in range(r)]
                    residue = bareiss(matrix) % modulus
                    check(residue != 0, "padic_nonzero_residue", (p,r,e,unit))
                    check(vp_int(residue,p) == predicted, "padic_exact_valuation", (p,r,e,unit))
            if r in (2, 3, 4, 8):
                records.append({"p":p,"rank":r,"S":S,"energy":energy,"v_for_e1":S+2*energy})
    return records


def verify_raw_budget() -> list[dict[str, object]]:
    out = []
    for r in range(1, 9):
        ps = primes_up_to(max(3*r+5,31))
        budget = {p:denominator_budget(r,p) for p in ps}
        for p,C in budget.items():
            check(C == 0 if p>3*r-1 else True, "raw_budget_small_prime_support", (r,p,C))
            for i in range(1,r+1):
                # Check the individual summands against their separately recomputed bound.
                a=2*r-1
                individual = max([0]+[a*h-(((i+p**h-1)//p**h)*p**h-i) for h in range(1,15)])
                for k in range(i,301):
                    check(a*vp_int(k,p)-(k-i) <= individual, "raw_budget_integer_bound", (r,p,i,k))
        out.append({"rank":r,"C_p":{str(p):C for p,C in budget.items() if C}})
    for r in range(1,5):
        S=r*(r+1)//2
        for K in range(r,r+5):
            polynomial=gram_polynomial(r,list(range(1,K+1)))
            for p in (2,3,5,7,11,13):
                C=denominator_budget(r,p)
                for e in (1,2):
                    for u in (1,p+1):
                        value=sum((co*F(p**e*u)**degree for degree,co in polynomial.items()),F(0))
                        check(value != 0 and vp(value,p)>=S*e-C,"raw_padic_lower_bound",(r,K,p,e,u))
                        if p>3*r-1:
                            check(vp(value,p)==S*e,"raw_good_prime_exact",(r,K,p,e,u))
    return out


def verify_stored_triangle() -> dict[str, object]:
    corpus=ROOT/'source_context'/'Projector_Resolved_ABC_Attack_XII_TRIANGLE_CORPUS.csv'
    if not corpus.exists():
        return {"status":"NOT_RUN", "reason":"Optional predecessor corpus not present"}
    rows=list(csv.DictReader(corpus.open(newline='')))
    for row in rows:
        Ca,Cb,Cc = (int(row[k]) for k in ('C_a','C_b','C_c'))
        A,B,G = (int(row[k]) for k in ('cross_a','cross_b','cross_c'))
        check(gcd(Ca,Cb)==gcd(Ca,Cc)==gcd(Cb,Cc)==1,"stored_triangle_pairwise_coprime",row.get('index'))
        D=gcd(Ca,A)*gcd(Cb,B)*gcd(Cc,G)
        check(D==int(row['triangle_defect']),"stored_triangle_defect_formula",row.get('index'))
        check(Ca*Cb*Cc//D==int(row['triangle_image_order']),"stored_triangle_image_formula",row.get('index'))
    return {"status":"PASS", "rows":len(rows), "sha256":hashlib.sha256(corpus.read_bytes()).hexdigest(),
            "scope":"Replays stored moduli/phases only, not the upstream arithmetic construction"}


def main() -> None:
    started=time.time()
    verify_jets()
    families=verify_normalization()
    verify_determinants()
    verify_residue_energy()
    padic=verify_padic_determinants()
    raw=verify_raw_budget()
    triangle=verify_stored_triangle()
    report={"status":"PASS", "python":sys.version, "platform":platform.platform(),
            "elapsed_seconds_diagnostic_only":round(time.time()-started,3),
            "checks":dict(sorted(COUNTS.items())), "total_checks":sum(COUNTS.values()),
            "counterexample_family_samples":families, "padic_determinant_samples":padic,
            "raw_small_prime_budgets":raw,"stored_triangle_replay":triangle,
            "boundaries":["Finite tests are not the proofs of infinite statements.",
                          "No product formula is asserted for polylogarithmic period values.",
                          "No global arithmetic determinant with the required height bound is constructed.",
                          "No abc proof or IUT Corollary 3.12 repair is claimed.",
                          "Lean source is uncompiled in this runtime."]}
    path=ROOT/'verification'/'results.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({"status":"PASS","total_checks":sum(COUNTS.values()),"families":dict(sorted(COUNTS.items())),"seconds":round(time.time()-started,3)},indent=2))


if __name__=='__main__':
    main()
