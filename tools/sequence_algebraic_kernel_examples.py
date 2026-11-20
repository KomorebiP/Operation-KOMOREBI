#!/usr/bin/env python3
"""Exact coefficients for the worked algebraic-kernel examples.

Author: Komorebi P.
Uses Python's standard library. The direct coefficient expansion and the
compositional generating-function expansion are separate algorithms. These
finite checks supplement the written formal-series proof.
"""
from fractions import Fraction
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
    """Directly expand [t**n] A(t)*Phi(t)**n."""
    a = _mul(_series(numerator, count), _inverse(_series(denominator, count)))
    power = _series([1], count)
    polynomial = _series(phi, count)
    result = []
    for n in range(count):
        result.append(sum(a[n-k] * power[k] for k in range(n+1)))
        power = _mul(power, polynomial)
    return result


def kernel_generating_coefficients(phi, numerator=(1,), denominator=(1,), count=10):
    """Expand A(T)/(1-x*Phi'(T)) by formal composition and inversion."""
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
    }


if __name__ == '__main__':
    print(json.dumps({f'Example {k}': [str(x) for x in values]
                      for k, values in example_values().items()}, indent=2))
