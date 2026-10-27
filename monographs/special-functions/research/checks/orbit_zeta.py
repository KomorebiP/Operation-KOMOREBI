#!/usr/bin/env python3
"""Exact, bounded formal-series checks for d_N(w) and its power sums.

Run with Python's standard library only.  The JSON report goes to stdout;
the script writes no files.  These finite checks make no analytic convergence
or historical novelty claim.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import platform


N_VALUES = tuple(range(2, 9))
K_MAX = 8


class ExactAssertions:
    """Count one exact rational equality for each coefficient comparison."""

    def __init__(self):
        self.counts = Counter()

    def equal(self, actual, expected, category, label):
        self.counts[category] += 1
        if actual != expected:
            raise AssertionError(
                f"{category}: {label}: {actual} != {expected}"
            )

    @property
    def total(self):
        return sum(self.counts.values())


def coefficients(n, degree):
    """Return a_j = (-1)^j/(N*j)! for j=0,...,degree."""
    return [Fraction((-1) ** j, factorial(n * j))
            for j in range(degree + 1)]


def triangular_coefficients(a):
    """b_k = -k*a_k - sum_{j=1}^{k-1} a_j*b_{k-j}."""
    b = [Fraction(0)] * len(a)
    for k in range(1, len(a)):
        b[k] = -k * a[k] - sum(
            (a[j] * b[k - j] for j in range(1, k)), Fraction(0)
        )
    return b


def finite_formal_log_coefficients(a):
    """Compute -k*[w^k]log(1+u) using finite powers of u=a-1.

    Because u has zero constant term, powers above degree vanish in the
    quotient ring Q[w]/(w^(degree+1)).  This is an algebraic truncation,
    with no appeal to convergence of an infinite logarithm series.
    """
    degree = len(a) - 1
    u = a.copy()
    u[0] = Fraction(0)
    power = [Fraction(1)] + [Fraction(0)] * degree
    logarithm = [Fraction(0)] * (degree + 1)
    for exponent in range(1, degree + 1):
        next_power = [Fraction(0)] * (degree + 1)
        for left_degree, left_coefficient in enumerate(power):
            for right_degree in range(1, degree - left_degree + 1):
                next_power[left_degree + right_degree] += (
                    left_coefficient * u[right_degree]
                )
        power = next_power
        multiplier = Fraction((-1) ** (exponent + 1), exponent)
        for k in range(1, degree + 1):
            logarithm[k] += multiplier * power[k]
    return [-k * logarithm[k] for k in range(degree + 1)]


def reciprocal_derivative_coefficients(a):
    """Construct 1/d first, then multiply it by -w*d'(w)."""
    degree = len(a) - 1
    reciprocal = [Fraction(1)] + [Fraction(0)] * degree
    for k in range(1, degree + 1):
        reciprocal[k] = -sum(
            (a[j] * reciprocal[k - j] for j in range(1, k + 1)),
            Fraction(0),
        )
    return [Fraction(0)] + [
        sum((-j * a[j] * reciprocal[k - j]
             for j in range(1, k + 1)), Fraction(0))
        for k in range(1, degree + 1)
    ]


def bernoulli_numbers(max_index):
    """Build B_m independently from sum binom(m+1,j)*B_j=0.

    This uses the convention B_1=-1/2 and does not reuse any d_N
    coefficients, logarithm calculations, or reciprocal calculations.
    """
    bernoulli = [Fraction(1)]
    for m in range(1, max_index + 1):
        bernoulli.append(-sum(
            (comb(m + 1, j) * bernoulli[j] for j in range(m)),
            Fraction(0),
        ) / (m + 1))
    return bernoulli


def normalized_even_zeta(half_index, bernoulli):
    """Euler formula for zeta(2m)/pi^(2m), as an exact rational."""
    m = half_index
    return Fraction((-1) ** (m + 1) * 2 ** (2 * m - 1),
                    factorial(2 * m)) * bernoulli[2 * m]


def closed_power_sum(n, k, bernoulli):
    if n == 2:
        return (2 ** (2 * k) - 1) * normalized_even_zeta(k, bernoulli)
    if n == 4:
        return (Fraction(1, 2 ** (2 * k)) * (2 ** (4 * k) - 1)
                * normalized_even_zeta(2 * k, bernoulli))
    raise ValueError("Closed power sum implemented only for N=2 and N=4")


def main():
    checks = ExactAssertions()
    computed = {}
    coefficient_rows = []
    for n in N_VALUES:
        a = coefficients(n, K_MAX)
        triangular = triangular_coefficients(a)
        logarithm = finite_formal_log_coefficients(a)
        reciprocal_derivative = reciprocal_derivative_coefficients(a)
        for k in range(1, K_MAX + 1):
            label = f"N={n}, k={k}"
            checks.equal(triangular[k], logarithm[k],
                         "triangular_vs_finite_formal_log", label)
            checks.equal(triangular[k], reciprocal_derivative[k],
                         "triangular_vs_reciprocal_derivative", label)
        computed[n] = triangular
        coefficient_rows.append({
            "N": n,
            "k": list(range(1, K_MAX + 1)),
            "b_k": [str(value) for value in triangular[1:]],
            "formal_log_matches_each_k": True,
            "reciprocal_derivative_matches_each_k": True,
        })

    bernoulli = bernoulli_numbers(4 * K_MAX)
    closed_rows = []
    formulas = {
        2: "(2^(2k)-1)*zeta(2k)/pi^(2k)",
        4: "2^(-2k)*(2^(4k)-1)*zeta(4k)/pi^(4k)",
    }
    for n in (2, 4):
        values = []
        for k in range(1, K_MAX + 1):
            value = closed_power_sum(n, k, bernoulli)
            checks.equal(computed[n][k], value, "closed_power_sum",
                         f"N={n}, k={k}")
            values.append(str(value))
        closed_rows.append({"N": n, "formula": formulas[n],
                            "k": list(range(1, K_MAX + 1)),
                            "closed_formula_values": values})

    benchmarks = {
        2: [Fraction(1, 2), Fraction(1, 6), Fraction(1, 15),
            Fraction(17, 630)],
        3: [Fraction(1, 6), Fraction(1, 40), Fraction(53, 13440)],
        5: [Fraction(1, 120), Fraction(5, 72576),
            Fraction(997, 1743565824)],
    }
    benchmark_rows = []
    for n, expected_values in benchmarks.items():
        for k, expected in enumerate(expected_values, start=1):
            actual = computed[n][k]
            checks.equal(actual, expected, "explicit_benchmark",
                         f"N={n}, k={k}")
            benchmark_rows.append({"N": n, "k": k,
                                   "expected": str(expected),
                                   "actual": str(actual)})

    report = {
        "status": "PASS",
        "checkpoint": "SF-DISCOVERY-001",
        "software": {"python": platform.python_version(),
                     "dependencies": "Python standard library only"},
        "arithmetic": "Exact rational arithmetic using fractions.Fraction; no floating-point comparisons",
        "bounds": {"N": list(N_VALUES), "k": [1, K_MAX],
                   "formal_series_degree": K_MAX,
                   "maximum_factorial_argument": max(N_VALUES) * K_MAX,
                   "bernoulli_maximum_index": 4 * K_MAX,
                   "closed_power_sum_N": [2, 4],
                   "benchmark_k_by_N": {str(n): len(values)
                                        for n, values in benchmarks.items()}},
        "exact_assertion_count": checks.total,
        "exact_assertions_by_category": dict(checks.counts),
        "counting_convention": "One exact coefficient equality is one assertion; 56+56+16+10=138",
        "result_tables": {"coefficient_law": coefficient_rows,
                          "closed_power_sums": closed_rows,
                          "explicit_benchmarks": benchmark_rows},
        "bernoulli_construction": {
            "recurrence": "B_0=1; B_m=-(1/(m+1))*sum_{j=0}^{m-1} binom(m+1,j)*B_j",
            "convention": "B_1=-1/2",
            "even_zeta_formula": "zeta(2m)/pi^(2m)=(-1)^(m+1)*2^(2m-1)*B_(2m)/(2m)!",
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "non_claims": [
            "Checks are bounded to the listed integer N and coefficient k values; they are not a proof for all N or k.",
            "Formal truncation checks do not establish analytic convergence, zero locations, a canonical product, or infinite root-sum identities.",
            "The Bernoulli formula is used as an exact closed-form reference; this script does not prove Euler's even-zeta theorem.",
            "No historical novelty claim is made.",
        ],
    }
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
