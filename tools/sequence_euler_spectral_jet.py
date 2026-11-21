"""Exact Euler spectral and local-jet certificates.

Author: Komorebi P.

Reproduces the 2026-11-20 continuation checkpoint.
No floating point, random sampling, or remote data is used.
Methods: Seidel--Entringer recurrence, finite Gaussian power sums,
and Eulerian polynomial arithmetic with repeated monic division.
"""
from __future__ import annotations

import argparse
import json
from math import lcm
from pathlib import Path

BASE = [1, 1, 1, 2, 5, 16, 61, 272, 1385, 7936, 50521, 353792, 2702765]


def entringer(max_n: int, modulus: int) -> list[int]:
    prev = [1]
    out = [1]
    for n in range(1, max_n + 1):
        current = [0]
        partial = 0
        for k in range(1, n + 1):
            partial = (partial + prev[n - k]) % modulus
            current.append(partial)
        out.append(partial)
        prev = current
    return out


def gaussian_sum_mod(q: int, n: int) -> tuple[int, int]:
    """Evaluate the finite sum in (Z/q)[i], n>=1 and q odd."""
    assert q >= 3 and q % 2 and n >= 1
    real = imag = 0
    for k in range(1, q + 1):
        value = pow(k, n, q)
        if k % 4 == 0:
            real += value
        elif k % 4 == 1:
            imag -= value
        elif k % 4 == 2:
            real -= value
        else:
            imag += value
    real %= q
    imag %= q
    phase = (n + 1) % 4
    if phase == 0:
        a, b = 2, 0
    elif phase == 1:
        a, b = 0, 2
    elif phase == 2:
        a, b = -2, 0
    else:
        a, b = 0, -2
    x = (a * real - b * imag) % q
    y = (a * imag + b * real) % q
    # 1 - (-i)**q = 1 +/- i; its inverse uses 2^{-1} modulo q.
    direction = 1 if q % 4 == 1 else -1
    inv2 = pow(2, -1, q)
    return ((x + direction * y) * inv2) % q, ((y - direction * x) * inv2) % q


def eulerian_coefficients(n: int, modulus: int) -> list[int]:
    """The ordinary Eulerian polynomial A_n(t), reduced modulo modulus."""
    assert n >= 1
    a = [1]
    for m in range(1, n):
        b = [0] * (m + 1)
        # A_(m+1)=(1+m*t) A_m+t(1-t) A_m'.
        for j, value in enumerate(a):
            b[j] = (b[j] + (j + 1) * value) % modulus
            b[j + 1] = (b[j + 1] + (m - j) * value) % modulus
        a = b
    return a


def q_adic_digits(poly: list[int], levels: int, modulus: int) -> list[tuple[int, int]]:
    """First digits in A(t)=sum_j (a_j+b_j*t)*(1+t*t)**j."""
    a = [int(v) % modulus for v in poly]
    digits = []
    for _ in range(levels):
        quotient = [0] * max(0, len(a) - 2)
        for k in range(len(a) - 1, 1, -1):
            value = a[k]
            quotient[k - 2] = value
            a[k - 2] = (a[k - 2] - value) % modulus
        digits.append(((a[0] if a else 0) % modulus,
                       (a[1] if len(a) > 1 else 0) % modulus))
        a = quotient
    return digits


def weighted_division(e: list[int], p: int, n: int, c: int) -> bool:
    return all(e[n + j] % (p ** (c + 1 - j)) == 0 for j in range(c + 1))


def jet_division(poly: list[int], p: int, c: int) -> tuple[bool, list[list[int]]]:
    digits = q_adic_digits(poly, c + 1, p ** (c + 1))
    condition = all(a % (p ** (c + 1 - j)) == 0
                    and b % (p ** (c + 1 - j)) == 0
                    for j, (a, b) in enumerate(digits))
    return condition, [list(digit) for digit in digits]


def certify() -> dict:
    output = {
        "author": "Komorebi P.",
        "status": "passed",
        "precision": "exact integers and modular Gaussian pairs",
        "spectral_checks": [],
        "period_jump_checks": [],
        "jet_checks": [],
        "known_positive_controls": [],
    }
    for q in [3, 5, 7, 9, 11, 13, 15, 21, 25, 27, 35, 43, 45, 49, 75, 81, 125, 169, 1849]:
        values = entringer(35, q)
        assert values[:13] == [v % q for v in BASE]
        for n in range(1, 36):
            a, b = gaussian_sum_mod(q, n)
            assert (a, b) == (values[n], 0), (q, n, a, b, values[n])
        output["spectral_checks"].append({"q": q, "n_range": [1, 35], "count": 35})

    cases = [(3, 1), (3, 2), (3, 3), (3, 4),
             (5, 1), (5, 2), (5, 3), (5, 4),
             (7, 1), (7, 2), (7, 3),
             (11, 1), (11, 2), (13, 1), (13, 2), (43, 1), (43, 2)]
    for p, r in cases:
        q = p ** r
        period = p ** (r - 1) * lcm(p - 1, 4)
        assert period <= 4500
        values = entringer(period + 18, q)
        for n in range(1, 19):
            epsilon = 1 if p % 4 == 1 else (-1) ** (n + 1)
            left = (values[n + period] - values[n]) % q
            right = (-epsilon * pow(p, n, q) * values[n]) % q
            assert left == right, (p, r, n, left, right)
        output["period_jump_checks"].append(
            {"p": p, "r": r, "period_L": period, "n_range": [1, 18], "count": 18}
        )

    for p in [3, 5, 7, 11, 13, 17, 19, 23, 43]:
        modulus = p ** 3
        max_n = 75
        euler = entringer(max_n + 2, modulus)
        singles = pairs = triples = 0
        for n in range(1, max_n + 1):
            poly = eulerian_coefficients(n, modulus)
            for c in range(3):
                condition, digits = jet_division(poly, p, c)
                direct = weighted_division(euler, p, n, c)
                assert condition == direct, (p, n, c, condition, direct, digits)
                if condition:
                    if c == 0:
                        singles += 1
                    elif c == 1:
                        pairs += 1
                    else:
                        triples += 1
        output["jet_checks"].append({
            "p": p,
            "n_range": [1, max_n],
            "c_values": [0, 1, 2],
            "count": max_n * 3,
            "matched_single": singles,
            "matched_pair": pairs,
            "matched_triple": triples,
        })

    p, n = 43, 978
    modulus = p ** 3
    euler = entringer(n + 2, modulus)
    poly = eulerian_coefficients(n, modulus)
    assert weighted_division(euler, p, n, 1)
    pair, _ = jet_division(poly, p, 1)
    assert pair
    triple, digits = jet_division(poly, p, 2)
    assert not triple
    output["known_positive_controls"].append({
        "p": p, "n": n, "weighted_pair": pair, "weighted_triple": triple,
        "E_n_mod_p_squared": euler[n] % (p * p),
        "E_n_plus1_mod_p": euler[n + 1] % p,
        "Q_adic_first_three_pairs_mod_p_cubed": digits,
    })
    output["total_spectral_comparisons"] = sum(item["count"] for item in output["spectral_checks"])
    output["total_jump_comparisons"] = sum(item["count"] for item in output["period_jump_checks"])
    output["total_jet_equivalences"] = sum(item["count"] for item in output["jet_checks"])
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    result = certify()
    if options.output is not None:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("spectral_checks", "period_jump_checks", "jet_checks")},
                     indent=2))


if __name__ == "__main__":
    main()
