#!/usr/bin/env python3
"""Finite exact audits for SF-DISCOVERY-100 dilation type and tap continuity.

Universal analytic assertions are proved in new_results/dilation_type.md.
This deterministic script checks their finite algebraic surrogates; displayed
real constants use mpmath and are not interval-certified estimates of a type.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from math import factorial
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
DEP = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
if DEP.is_dir():
    sys.path.insert(0, str(DEP))
import mpmath as mp


def numeric_coefficients(channels, last):
    out = [F(1)]
    for n in range(1, last + 1):
        total = F(0)
        for h, q, r in channels:
            for i in range(n):
                j = n - 1 - i
                total += h * q ** (2 * i + 1) * r ** (2 * j + 1) * out[i] * out[j]
        out.append(total / (2 * n + 1))
    return out


def weight_polynomials(pairs, last):
    """Tuple-indexed Q[h_1,...,h_J] dictionaries, with scales fixed."""
    zeros = (0,) * len(pairs)
    out = [{zeros: F(1)}]
    for n in range(1, last + 1):
        p = {}
        for channel, (q, r) in enumerate(pairs):
            for i in range(n):
                j = n - 1 - i
                multiplier = q ** (2 * i + 1) * r ** (2 * j + 1) / (2 * n + 1)
                for left, a in out[i].items():
                    for right, b in out[j].items():
                        key = tuple(x + y + (k == channel)
                                    for k, (x, y) in enumerate(zip(left, right)))
                        p[key] = p.get(key, F(0)) + multiplier * a * b
        out.append(p)
    return out


def evaluate(p, weights):
    total = F(0)
    for exponents, value in p.items():
        for h, exponent in zip(weights, exponents):
            value *= h ** exponent
        total += value
    return total


def derivative(p, weights, k):
    total = F(0)
    for exponents, value in p.items():
        if not exponents[k]:
            continue
        value *= exponents[k]
        for j, (h, exponent) in enumerate(zip(weights, exponents)):
            value *= h ** (exponent - (j == k))
        total += value
    return total


@lru_cache(None)
def trees(n):
    """Every full ordered binary shape with n internal vertices."""
    if n == 0:
        return (None,)
    return tuple((left, right) for i in range(n)
                 for left in trees(i) for right in trees(n - 1 - i))


def tree_value(tree, channels):
    if tree is None:
        return 0, F(1)
    left_size, left_weight = tree_value(tree[0], channels)
    right_size, right_weight = tree_value(tree[1], channels)
    size = 1 + left_size + right_size
    root = sum(h * q ** (2 * left_size + 1) * r ** (2 * right_size + 1)
               for h, q, r in channels) / (2 * size + 1)
    return size, left_weight * right_weight * root


def mpf(q):
    return mp.mpf(q.numerator) / q.denominator


def order(q, r):
    q, r = mpf(q), mpf(r)
    left, right = mp.mpf(0), mp.mpf(1)
    while q ** right + r ** right > 1:
        right *= 2
    for _ in range(280):
        middle = (left + right) / 2
        if q ** middle + r ** middle > 1:
            left = middle
        else:
            right = middle
    return (left + right) / 2


def type_constants(channels):
    active = [channel for channel in channels if channel[0] > 0]
    roots = [order(q, r) for _, q, r in active]
    index = max(range(len(active)), key=lambda j: roots[j])
    rho = roots[index]
    h, q, r = active[index]
    length = 1 / h
    shift = max(q * length / (1 - q), r * length / (1 - r))
    seed_end = length + 2 / min(q, r)
    lower = mp.log(2) / mpf(seed_end + shift) ** rho
    qmax = max(max(q, r) for _, q, r in active)
    qmin = min(min(q, r) for _, q, r in active)
    seed_radius = F(3) / qmin
    n = 0
    while qmax ** (-n) < seed_radius:
        n += 1
    v = (2 ** (n + 1) - 1) * mp.log(2)
    v += (2 ** (n + 1) - n - 2) * mp.log(1 / mpf(qmax))
    delta = mp.log(1 / mpf(qmin))
    upper_shift = max(mp.log(1 / mpf(q * r)) for _, q, r in active) + mp.log(2)
    upper = mp.exp(-rho) * (v + 1 + delta + upper_shift)
    return {'order_display': mp.nstr(rho, 35),
            'maximizing_channel': index,
            'L_exact': str(length), 'C_exact': str(shift), 'B_exact': str(seed_end),
            'positive_lower_type_constant_display': mp.nstr(lower, 35),
            'finite_upper_type_constant_display': mp.nstr(upper, 35),
            'upper_seed_bootstrap_N': n}


def run():
    counts = {}
    def check(section, statement):
        if not statement:
            raise AssertionError(section)
        counts[section] = counts.get(section, 0) + 1

    mp.mp.dps = 90
    banks = [
        [(F(1), F(1, 4), F(1, 4))],
        [(F(1), F(1, 2), F(1, 2))],
        [(F(1), F(1, 3), F(2, 3))],
        [(F(1), F(3, 5), F(4, 5))],
        [(F(1, 4), F(1, 4), F(1, 4)), (F(3, 4), F(3, 4), F(3, 4))],
        [(F(999, 1000), F(1, 4), F(1, 4)), (F(1, 1000), F(3, 4), F(3, 4))],
        [(F(1, 2), F(1, 3), F(2, 3)), (F(1, 2), F(1, 4), F(3, 4))],
    ]
    for channels in banks:
        for h, q, r in channels:
            length = 1 / h
            shift = max(q * length / (1 - q), r * length / (1 - r))
            seed_end = length + 2 / min(q, r)
            qmax = max(q, r)
            step = (1 - qmax) * seed_end + qmax * length
            check('fixed_width_comparison', (1 - q) * shift >= q * length)
            check('fixed_width_comparison', (1 - r) * shift >= r * length)
            check('seed_child_domain', q * (seed_end - length) >= 2)
            check('seed_child_domain', r * (seed_end - length) >= 2)
            for k in range(16):
                radius = seed_end + F(k, 3) * step
                for contraction in (q, r):
                    child = contraction * (radius - length)
                    check('contraction_induction', child >= 2)
                    check('contraction_induction', child <= radius - step)
                    check('shifted_child_bound', child + shift >= contraction * (radius + shift))

    families = [
        ([(F(1, 4), F(1, 4)), (F(3, 4), F(3, 4))],
         [(F(i, 8), F(8 - i, 8)) for i in range(9)]),
        ([(F(1, 3), F(2, 3)), (F(1, 4), F(3, 4)), (F(1, 2), F(1, 2))],
         [(F(i, 4), F(j, 4), F(4 - i - j, 4))
          for i in range(5) for j in range(5 - i)]),
    ]
    for pairs, simplex in families:
        qmax = max(max(pair) for pair in pairs)
        polys = weight_polynomials(pairs, 9)
        diagonal = numeric_coefficients([(F(1), qmax, qmax)], 9)
        for n, p in enumerate(polys):
            for exponents, coefficient in p.items():
                check('positive_homogeneous_polynomials', coefficient >= 0)
                check('positive_homogeneous_polynomials', sum(exponents) == n)
                multinomial = factorial(n)
                for exponent in exponents:
                    multinomial //= factorial(exponent)
                check('coefficientwise_majorant', coefficient <= diagonal[n] * multinomial)
            for weights in simplex:
                check('simplex_majorant', evaluate(p, weights) <= diagonal[n])
                for k in range(len(weights)):
                    partial = derivative(p, weights, k)
                    check('derivative_simplex_bound', 0 <= partial <= n * diagonal[n])
            for weights in simplex:
                for other in simplex:
                    distance = sum(abs(h - g) for h, g in zip(weights, other))
                    difference = abs(evaluate(p, weights) - evaluate(p, other))
                    check('total_variation_coefficient_bound',
                          difference <= distance * n * diagonal[n] / 2)
        for weights in (simplex[0], simplex[len(simplex) // 2], simplex[-1]):
            channels = [(h, q, r) for h, (q, r) in zip(weights, pairs)]
            recurrence = numeric_coefficients(channels, 6)
            for n in range(7):
                direct = sum(tree_value(tree, channels)[1] for tree in trees(n))
                check('independent_ordered_tree_evaluation', direct == recurrence[n])
                check('independent_ordered_tree_evaluation', direct == evaluate(polys[n], weights))

    # Compact convergence evaluated with exact rational partial sums. The
    # displayed infinite-series bound is given analytically in the proof.
    qmax = F(3, 4)
    diagonal = numeric_coefficients([(F(1), qmax, qmax)], 30)
    base = numeric_coefficients([(F(1), F(1, 4), F(1, 4))], 30)
    compact_samples = []
    for epsilon in (F(1, 2), F(1, 10), F(1, 100), F(1, 1000)):
        c = numeric_coefficients([(1 - epsilon, F(1, 4), F(1, 4)),
                                  (epsilon, qmax, qmax)], 30)
        for n in range(31):
            check('weak_tap_positive_monotonicity', c[n] >= base[n])
            check('weak_tap_coefficient_bound', c[n] - base[n] <= epsilon * n * diagonal[n])
        difference = sum(c) - sum(base)
        bound = epsilon * sum(n * a for n, a in enumerate(diagonal))
        check('radius1_exact_partial_sum_bound', difference <= bound)
        compact_samples.append({'epsilon': str(epsilon),
                                'degree_61_difference_exact': str(difference),
                                'degree_61_bound_exact': str(bound),
                                'difference_decimal': mp.nstr(mpf(difference), 35),
                                'bound_decimal': mp.nstr(mpf(bound), 35)})

    samples = [dict(channels=[[str(x) for x in channel] for channel in channels],
                    **type_constants(channels)) for channels in banks]
    inputs = ['routes/asymmetric_dilation.md', 'new_results/dilation_type.md',
              'checks/dilation_type.py', 'TARGET_CONTRACT.json']
    return {'checkpoint': 'SF-DISCOVERY-100', 'route': 'positive lower type and tap continuity',
            'status': 'passed', 'python': platform.python_version(), 'mpmath': mp.__version__,
            'arithmetic': 'Q exact fractions and Q[h] polynomial dictionaries; mpmath displays only',
            'exact_assertions': sum(counts.values()), 'assertion_counts': counts,
            'bounds': {'rational_banks': len(banks), 'channel_constant_grid_steps': 16,
                       'weight_polynomial_n_max': 9, 'simplex_grids': [9, 15],
                       'direct_ordered_tree_n_max': 6, 'weak_tap_n_max': 30,
                       'weak_tap_epsilons': ['1/2', '1/10', '1/100', '1/1000'],
                       'mpmath_display_decimal_digits': mp.mp.dps},
            'type_constant_samples': samples, 'compact_samples': compact_samples,
            'input_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in inputs},
            'failure_history': [],
            'non_claims': ['Finite checks do not prove any universal analytic theorem.',
                           'Real constant displays are not interval certificates.',
                           'No type limit or angular regular growth is asserted.',
                           'No historical priority claim.']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'evidence/dilation_type_checks.json')
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'exact_assertions': result['exact_assertions'],
                      'output': str(args.output), 'assertion_counts': result['assertion_counts']}, indent=2))


if __name__ == '__main__':
    main()
