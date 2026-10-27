#!/usr/bin/env python3
"""Exact coefficient checks and approximate Mellin-continuation benchmarks.

Command: PYTHONPATH=special_work/verification_dependencies python
  output/special_function_discovery_v1.0/checks/spectral_continuation.py

The universal continuation theorem is proved in the accompanying route.
These tests check finite algebra and high-precision numerical agreement.
They are not interval certificates or evidence of historical priority.
"""
from __future__ import annotations

import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / "special_work" / "verification_dependencies"))
import mpmath as mp


def quotient_coefficients(N: int, count: int):
    e = [Fraction(1, math.factorial(N * n)) for n in range(count + 1)]
    g = []
    for n in range(count):
        g.append((n + 1) * e[n + 1] - sum(e[j] * g[n - j] for j in range(1, n + 1)))
    return e, g


def logarithm_coefficients(e, count):
    """Independent finite log(1+v) implementation by polynomial powers."""
    power = [Fraction(0) for _ in range(count + 1)]
    power[0] = Fraction(1)
    result = [Fraction(0) for _ in range(count + 1)]
    for j in range(1, count + 1):
        power = [sum(power[k] * e[n - k] for k in range(n))
                 for n in range(count + 1)]
        for n in range(1, count + 1):
            result[n] += Fraction((-1) ** (j + 1), j) * power[n]
    return result


def bernoulli(n):
    work = [Fraction(0)] * (n + 1)
    for m in range(n + 1):
        work[m] = Fraction(1, m + 1)
        for j in range(m, 0, -1):
            work[j - 1] = j * (work[j - 1] - work[j])
    return work[0]


def exact_checks():
    total = 0
    for N in range(2, 11):
        e, g = quotient_coefficients(N, 40)
        logarithms = logarithm_coefficients(e, 40)
        for m in range(1, 41):
            assert g[m - 1] == m * logarithms[m]
            total += 1
        b = [None] + [(-1) ** (m + 1) * g[m - 1] for m in range(1, 41)]
        assert b[1] == Fraction(1, math.factorial(N))
        assert b[2] == Fraction(1, math.factorial(N) ** 2) - Fraction(2, math.factorial(2 * N))
        assert b[3] == (Fraction(1, math.factorial(N) ** 3)
                        - Fraction(3, math.factorial(N) * math.factorial(2 * N))
                        + Fraction(3, math.factorial(3 * N)))
        total += 3
        if N in (2, 4):
            for k in range(1, 13):
                if N == 2:
                    known = (2 ** (2 * k) - 1) * (-1) ** (k + 1) * bernoulli(2 * k)
                    known *= Fraction(2 ** (2 * k - 1), math.factorial(2 * k))
                else:
                    known = -(2 ** (4 * k) - 1) * bernoulli(4 * k)
                    known *= Fraction(2 ** (2 * k - 1), math.factorial(4 * k))
                assert b[k] == known
                total += 1
    return total


def numerical_g_coefficients(N, count):
    e = [1 / mp.factorial(N * n) for n in range(count + 1)]
    g = []
    for n in range(count):
        g.append((n + 1) * e[n + 1] - mp.fsum(e[j] * g[n - j] for j in range(1, n + 1)))
    return g


class MellinContinuation:
    """Approximate evaluation; local series and exponential tail are truncated."""
    def __init__(self, N, count=None):
        self.N = N
        self.count = count or {2: 180, 3: 120, 4: 90, 5: 80}.get(N, 100)
        self.g = numerical_g_coefficients(N, self.count)
        self.pairs = [(mp.cos(2 * mp.pi * j / N) - 1,
                       mp.sin(2 * mp.pi * j / N))
                      for j in range(1, (N - 1) // 2 + 1)]

    def log_tail_derivative(self, u):
        h, hp = mp.mpf(0), mp.mpf(0)
        for beta, gamma in self.pairs:
            factor = 2 * mp.exp(beta * u)
            cs, sn = mp.cos(gamma * u), mp.sin(gamma * u)
            h += factor * cs
            hp += factor * (beta * cs - gamma * sn)
        if self.N % 2 == 0:
            term = mp.exp(-2 * u)
            h += term
            hp -= 2 * term
        return hp / (1 + h)

    def bracket(self, s):
        s = mp.mpc(s)
        local = mp.fsum(self.g[n] / (n + 1 - s) for n in range(len(self.g)))
        tail = mp.quad(lambda u: mp.power(u, -self.N * s) * self.log_tail_derivative(u),
                       [1, 2, 4, 8, 16, 32, 64, mp.inf])
        return local + tail + 1 / (self.N * s - 1)

    def __call__(self, s):
        s = mp.mpc(s)
        if not s.imag and s.real == int(s.real):
            m = int(s.real)
            if m <= 0:
                return mp.mpf(0)
            if m <= len(self.g):
                return (-1) ** (m + 1) * self.g[m - 1]
        return mp.sin(mp.pi * s) / mp.pi * self.bracket(s)


def encode(z):
    return {"real": mp.nstr(mp.re(z), 65), "imag": mp.nstr(mp.im(z), 65)}


def shifted_benchmarks():
    """Independent N=2 quadrature for the shifted regularized product."""
    checks = []
    for a in (mp.mpf(0), mp.mpf("0.25"), mp.mpf(2), mp.mpf(9)):
        def local(x):
            u = mp.sqrt(a + x * x)
            if not u:
                return mp.mpf(0)
            return x * mp.tanh(u) / u
        u0 = mp.sqrt(a + 1)
        local_integral = mp.quad(local, [0, mp.mpf("0.5"), 1])
        exponential_tail = mp.quad(lambda u: -2 * mp.exp(-2 * u) / (1 + mp.exp(-2 * u)),
                                   [u0, u0 + 1, u0 + 4, u0 + 16, mp.inf])
        # Integrate the algebraic leading tail exactly; the remaining tail decays exponentially.
        derivative = local_integral + (1 - u0) + exponential_tail - 1
        known = -mp.log(2 * mp.cosh(mp.sqrt(a)))
        error = abs(derivative - known)
        assert error < mp.mpf("1e-70"), (a, error)
        checks.append({"N": 2, "shift_a": mp.nstr(a),
                       "quadrature_Z_prime_0": encode(derivative),
                       "known_half_integer_laplacian_value": encode(known),
                       "regularized_product": encode(mp.exp(-derivative)),
                       "exact_product_formula": "2*cosh(sqrt(a))",
                       "absolute_derivative_error": mp.nstr(error, 8)})
    return checks


def main():
    mp.mp.dps = 80
    path = ROOT / "evidence" / "spectral_continuation_checks.json"
    if "--shift-only" in sys.argv:
        result = json.loads(path.read_text())
        result["shifted_N2_product_benchmarks"] = shifted_benchmarks()
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"status": "passed", "additional_shifted_benchmarks": 4,
                          "exact_assertions_unchanged": result["exact_assertions"]}, indent=2))
        return
    assertions = exact_checks()
    records = []
    maximum_error = mp.mpf(0)
    points = [mp.mpf("0.75"), mp.mpf("0.4"), mp.mpf("-0.5"),
              mp.mpf("-1.5"), mp.mpf("1.25"), mp.mpf("2.25"),
              mp.mpc("-2.3", "0.4"), mp.mpc("0.6", "0.3")]
    functions = {}
    for N in (2, 4):
        f = functions[N] = MellinContinuation(N)
        for s in points:
            actual = f(s)
            known = (mp.pi ** (-2 * s) * mp.zeta(2 * s, mp.mpf("0.5")) if N == 2
                     else (mp.sqrt(2) * mp.pi) ** (-4 * s) * mp.zeta(4 * s, mp.mpf("0.5")))
            error = abs(actual - known)
            maximum_error = max(maximum_error, error)
            assert error < mp.mpf("1e-55"), (N, s, error)
            records.append({"N": N, "s": encode(s), "value": encode(actual),
                            "known_hurwitz_value": encode(known), "absolute_error": mp.nstr(error, 8)})
    new_values = []
    derivative_errors = []
    for N in (2, 3, 4, 5):
        f = functions.get(N) or MellinContinuation(N)
        functions[N] = f
        derivative_error = abs(f.bracket(0) + mp.log(N))
        assert derivative_error < mp.mpf("1e-55"), (N, derivative_error)
        derivative_errors.append({"N": N, "numerical_Z_prime_0": encode(f.bracket(0)),
                                  "exact_formula": "-log(N)",
                                  "absolute_error": mp.nstr(derivative_error, 8)})
        if N in (3, 5):
            for s in (mp.mpf("-0.5"), mp.mpc("-1.2", "0.3"), mp.mpf("0.6")):
                value = f(s)
                with mp.workdps(45):
                    low = MellinContinuation(N)(s)
                difference = abs(value - low)
                assert difference < mp.mpf("1e-35"), (N, s, difference)
                new_values.append({"N": N, "s": encode(s), "value": encode(value),
                                   "precision_consistency_error": mp.nstr(difference, 8),
                                   "interpretation": "approximation; no interval certificate"})
    result = {
        "claim_id": "SF-DISCOVERY-100-SPECTRAL",
        "status": "passed",
        "coefficient_domain": "exact rationals for finite algebra; mpmath floating arithmetic for quadrature",
        "branch": "principal Arg(w) in (-pi,pi); the seed has no zeros on the negative ray",
        "software": {"python": platform.python_version(), "mpmath": mp.__version__},
        "exact_assertions": assertions,
        "exact_bounds": {"N": [2, 10], "logarithm_and_quotient_degree": 40,
                         "N2_N4_hurwitz_even_zeta_anchors": 12},
        "numerical_precision_decimal_digits": 80,
        "known_benchmark_cases": records,
        "maximum_absolute_benchmark_error": mp.nstr(maximum_error, 10),
        "derivative_zero_checks": derivative_errors,
        "N3_N5_values": new_values,
        "shifted_N2_product_benchmarks": shifted_benchmarks(),
        "numerical_nonclaims": ["No numerical zero locations are required.",
                                 "Quadrature and truncated Taylor sums are not certified balls.",
                                 "Finite assertions do not prove universal continuation or novelty."],
        "universal_proof": "new_results/spectral_continuation.md",
        "run_history": []
    }
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "passed", "exact_assertions": assertions,
                      "known_benchmark_cases": len(records),
                      "maximum_absolute_benchmark_error": mp.nstr(maximum_error, 10),
                      "new_values": len(new_values), "evidence": str(path)}, indent=2))


if __name__ == "__main__":
    main()
