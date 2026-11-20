#!/usr/bin/env python3
"""Exact coefficients for the worked algebraic-kernel examples.

Author: Komorebi P.
Uses Python's standard library. The direct coefficient expansion and the
compositional generating-function expansion are separate algorithms. These
finite checks supplement the written formal-series proof.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb
import json


def _series(values, count):
    return [Fraction(values[i]) if i < len(values) else Fraction(0)
            for i in range(count)]


def _add(a, b):
    return [x + y for x, y in zip(a, b)]


def _mul(a, b):
    count = len(a)
    return [sum(a[j] * b[i-j] for j in range(i+1)) for i in range(count)]


def _inverse(a):
    if not a or not a[0]:
        raise ValueError('The denominator must have nonzero constant term.')
    result = [1 / a[0]]
    for n in range(1, len(a)):
        result.append(-sum(a[k] * result[n-k] for k in range(1, n+1)) / a[0])
    return result


def _compose(coefficients, argument):
    count = len(argument)
    result = _series([], count)
    for value in reversed(coefficients):
        result = _mul(result, argument)
        result[0] += value
    return result


def auxiliary_series(phi, count):
    """Return T modulo x**count, where T=x*Phi(T) and T(0)=0."""
    if count < 1 or not phi or not phi[0]:
        raise ValueError('Use a positive count and Phi(0) != 0.')
    phi = [Fraction(x) for x in phi]
    result = _series([], count)
    for _ in range(count):
        result = [Fraction(0)] + _compose(phi, result)[:-1]
    return result


def kernel_coefficients(phi, numerator=(1,), denominator=(1,), count=10):
    """Directly expand [t**n] F(t)*Phi(t)**n."""
    a = _mul(_series(numerator, count), _inverse(_series(denominator, count)))
    power = _series([1], count)
    polynomial = _series(phi, count)
    result = []
    for n in range(count):
        result.append(sum(a[n-k] * power[k] for k in range(n+1)))
        power = _mul(power, polynomial)
    return result


def kernel_generating_coefficients(phi, numerator=(1,), denominator=(1,), count=10):
    """Expand F(T)/(1-x*Phi'(T)) by formal composition and inversion."""
    t = auxiliary_series(phi, count)
    derivative = [i * Fraction(c) for i, c in enumerate(phi)][1:]
    jacobian = [Fraction(1)] + [-v for v in _compose(derivative, t)[:-1]]
    return _mul(_mul(_compose(numerator, t),
                     _inverse(_compose(denominator, t))), _inverse(jacobian))


def rational_at_auxiliary(phi, numerator, denominator, count=10):
    """Expand a rational function of T, with T=x*Phi(T)."""
    t = auxiliary_series(phi, count)
    return _mul(_compose(numerator, t), _inverse(_compose(denominator, t)))


def block_values(d=2, r=0, q=1, weights=None, count=10, block_weight=None):
    """Evaluate the defining finite sum, allowing an extra exact block weight."""
    if not isinstance(d, int) or isinstance(d, bool) or d < 1:
        raise ValueError('d must be a positive integer.')
    weights = [1] * d if weights is None else list(weights)
    if len(weights) != d:
        raise ValueError('Supply exactly d residue weights.')
    r, q = Fraction(r), Fraction(q)
    result = []
    for n in range(count):
        result.append(sum(Fraction(weights[k % d]) * q ** (k // d)
                          * (block_weight(k // d) if block_weight else 1)
                          * comb(n, k // d) * (-r) ** (n-k)
                          for k in range(n+1)))
    return result


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a


def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a+b
    return a


def pell(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+2*b
    return a


def residue_weighted_values(weight_functions, r=0, count=10):
    """Direct finite sums with an independent block weight on each residue."""
    d = len(weight_functions)
    if not d:
        raise ValueError('Supply at least one residue weight function.')
    r = Fraction(r)
    return [sum(Fraction(weight_functions[k % d](k // d))
                * comb(n, k // d) * (-r) ** (n-k)
                for k in range(n+1)) for n in range(count)]


def block_generating_polynomials(d=2, r=0, weights=None, count=10):
    """Return [x**n] G_q as exact polynomials in q, in ascending degree.

    This uses only the compositional generating function, not its defining
    binomial sum. Write T=x*C(q*x**d): its auxiliary equation shows that
    every power of q carries at least d powers of x. Thus [x**n] G_q has
    degree at most floor(n/d). Evaluating G_q at the distinct rational
    points 0,...,floor((count-1)/d) and using Newton interpolation recovers
    these polynomials exactly. No floating interpolation is used.
    """
    if not isinstance(d, int) or isinstance(d, bool) or d < 1:
        raise ValueError('d must be a positive integer.')
    if count < 1:
        raise ValueError('Use a positive coefficient count.')
    weights = (1,) * d if weights is None else tuple(weights)
    if len(weights) != d:
        raise ValueError('Supply exactly d residue weights.')
    return _block_generating_polynomials(
        d, Fraction(r), tuple(map(Fraction, weights)), count)


@lru_cache(maxsize=32)
def _block_generating_polynomials(d, r, weights, count):
    degree = (count-1) // d
    evaluations = [kernel_generating_coefficients(
        [1] + [0] * (d-1) + [q], weights, [1, r], count)
        for q in range(degree+1)]

    # Newton's basis binom(q,k), represented as rational coefficient lists.
    basis = [[Fraction(1)]]
    for k in range(degree):
        following = [Fraction(0)] * (k+2)
        for j, value in enumerate(basis[-1]):
            following[j] -= k * value / (k+1)
            following[j+1] += value / (k+1)
        basis.append(following)

    result = []
    for n in range(count):
        differences = [row[n] for row in evaluations]
        coefficients = [Fraction(0)] * (degree+1)
        for polynomial in basis:
            for j, value in enumerate(polynomial):
                coefficients[j] += differences[0] * value
            differences = [b-a for a, b in zip(differences, differences[1:])]
        result.append(tuple(coefficients))
    return tuple(result)


def quadratic_evaluate(polynomial, rational_part, radical_part, square):
    """Evaluate at a+b*sqrt(D), returning the exact pair (u,v).

    The output means u+v*sqrt(D). Negative D is permitted, so the same
    arithmetic also handles conjugate cube roots of unity.
    """
    a, b, d = map(Fraction, (rational_part, radical_part, square))
    u = v = Fraction(0)
    for coefficient in reversed(polynomial):
        u, v = u*a + v*b*d + coefficient, u*b + v*a
    return u, v


def _power_denominator(step, weight, exponent):
    """Coefficients of (1-weight*t**step)**exponent."""
    result = [Fraction(0)] * (step*exponent+1)
    for k in range(exponent+1):
        result[step*k] = comb(exponent, k) * (-weight)**k
    return result


def expanded_example_generating_values(count=24):
    """Expand the displayed GFs for Examples 24--32, independently of sums.

    Polynomial and finite-support cases use their explicit rational forms.
    Characteristic-root cases use the exact q-polynomials of the block GF,
    evaluated in quadratic fields. The direct algorithms generate their
    Lucas, Pell and Fibonacci weights by integer recurrences instead.
    """
    # Example 24: v=t^2, R=2+8v+2v^2+t*(3+13v-5v^2+v^3).
    polynomial = [2, 3, 8, 13, 2, -5, 0, 1]
    numerator24 = [0] * (len(polynomial)+4)
    for k, value in enumerate(polynomial):
        numerator24[k+2] += value
        numerator24[k+4] += value

    # Example 25: 6*t^6*(1+t^3)*(5-t^3)/(1-2*t^3)^5.
    numerator25 = [0] * 13
    numerator25[6], numerator25[9], numerator25[12] = 30, 24, -6

    dyadic = block_generating_polynomials(2, 0, count=count)
    ternary = block_generating_polynomials(3, 0, count=count)
    even = block_generating_polynomials(2, 0, [1, 0], count)
    odd = block_generating_polynomials(2, 0, [0, 1], count)
    signed = block_generating_polynomials(3, 1, count=count)
    phi = (Fraction(1, 2), Fraction(1, 2), 5)

    result = {
        24: rational_at_auxiliary(
            [1, 0, 1], numerator24, _power_denominator(2, 1, 5), count),
        25: rational_at_auxiliary(
            [1, 0, 0, 1], numerator25, _power_denominator(3, 2, 5), count),
        26: [2*quadratic_evaluate(p, *phi)[0] for p in dyadic],
        27: [quadratic_evaluate(p, 1, 1, 2)[1] for p in ternary],
        28: [(sum(p) + 2*quadratic_evaluate(
            p, Fraction(-1, 2), Fraction(1, 2), -3)[0]) / 3
             for p in dyadic],
        29: rational_at_auxiliary(
            [1], [1, 2, 2, 7, 12, 16, 8], [1, 2, 1], count),
        30: [2*quadratic_evaluate(e, *phi)[1]
             + 2*quadratic_evaluate(o, *phi)[0] for e, o in zip(even, odd)],
        31: [2*quadratic_evaluate(p, *phi)[1]
             + sum(c*2**m for m, c in enumerate(p)) for p in signed],
        # T=x*(1+2*T^2) rationalizes (1-4*x^2)/(1-8*x^2)^(3/2).
        32: rational_at_auxiliary(
            [1, 0, 2], [1, 0, 2, 0, 4, 0, 8],
            _power_denominator(2, 2, 3), count),
    }
    return result


def example_values(count=10):
    """Numerical worked instances; Example 7 instead displays polynomials."""
    return {
        1: [(3-1)**n for n in range(count)],
        2: [comb(2*n, n) for n in range(count)],
        3: [comb(3*n, n) for n in range(count)],
        4: kernel_coefficients([1, 1, 1], count=count),
        5: kernel_coefficients([1, 0, 1, 1], count=count),
        6: kernel_coefficients([1, 1, 1], denominator=[1, -1], count=count),
        8: block_values(r=-1, count=count),
        9: block_values(r=1, count=count),
        10: block_values(r=2, count=count),
        11: block_values(r=4, count=count),
        12: block_values(weights=[1, -1], count=count),
        13: block_values(q=2, count=count),
        14: block_values(d=3, count=count),
        15: block_values(d=3, r=1, count=count),
        16: block_values(d=3, r=2, weights=[1, 0, -1], count=count),
        17: block_values(d=4, count=count),
        18: block_values(d=4, weights=[1, 0, 0, 0], count=count),
        19: block_values(d=5, q=2, count=count),
        20: block_values(d=3, q=2, r=1, weights=[1, 2, 3], count=count),
        21: block_values(d=3, block_weight=lambda m: m+1, count=count),
        22: block_values(block_weight=lambda m: m, count=count),
        23: block_values(d=3, block_weight=fibonacci, count=count),
        24: block_values(block_weight=lambda m: m*m, count=count),
        25: block_values(d=3, weights=[1, 0, 0],
                         block_weight=lambda m: m*(m-1), count=count),
        26: block_values(block_weight=lucas, count=count),
        27: block_values(d=3, block_weight=pell, count=count),
        28: block_values(block_weight=lambda m: int(m % 3 == 0), count=count),
        29: block_values(d=3, r=1,
                         block_weight=lambda m: (1, 2)[m] if m < 2 else 0,
                         count=count),
        30: residue_weighted_values([fibonacci, lucas], count=count),
        31: block_values(d=3, r=1, block_weight=lambda m: fibonacci(m)+2**m,
                         count=count),
        32: block_values(r=1, q=2, block_weight=lambda m: m+1, count=count),
    }


if __name__ == '__main__':
    print(json.dumps({f'Example {k}': [str(x) for x in values]
                      for k, values in example_values().items()}, indent=2))
