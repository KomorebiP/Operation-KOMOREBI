#!/usr/bin/env python3
"""Finite exact and high-precision checks for the finite-prime sieve family.

The universal claims are proved in new_results/multi_prime_sieve.md.
Output is a JSON record, optionally redirected by --output for a bounded runner.
No numerical root is described as an interval certificate.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb, factorial
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

try:
    import mpmath as mp
except ModuleNotFoundError:
    project_dependencies = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
    if project_dependencies.is_dir():
        sys.path.insert(0, str(project_dependencies))
    import mpmath as mp

mp.mp.dps = 320
START = time.monotonic()
COUNTS = {'exact_rational_assertions': 0, 'numerical_assertions': 0,
          'orthogonality_conditions': 0, 'recurrence_cases': 0}


def exact(condition):
    assert condition
    COUNTS['exact_rational_assertions'] += 1


def numerical(condition):
    assert condition
    COUNTS['numerical_assertions'] += 1


def decimal(value, digits=90):
    return mp.nstr(value, digits)


def rational(value):
    return str(value.numerator) if value.denominator == 1 else f'{value.numerator}/{value.denominator}'


def floating(value):
    return mp.mpf(value.numerator)/value.denominator if isinstance(value, Q) else mp.mpf(value)


def subsets(items):
    return (part for size in range(len(items)+1) for part in combinations(items, size))


@lru_cache(None)
def bernoulli(n):
    if n == 0:
        return Q(1)
    return -sum(Q(comb(n+1, k))*bernoulli(k) for k in range(n))/Q(n+1)


@lru_cache(None)
def zeta_pi_coefficient(k):
    """Exact coefficient of pi^(2k) in zeta(2k)."""
    return Q((-1)**(k+1)*2**(2*k-1), factorial(2*k))*bernoulli(2*k)


@lru_cache(None)
def squarefree_pi_coefficient(k):
    """D(2k) = coefficient*pi^(-2k)."""
    return zeta_pi_coefficient(k)/zeta_pi_coefficient(2*k)


@lru_cache(None)
def d_value(s):
    return mp.zeta(s)/mp.zeta(2*s)


def euler_weight(s, strengths, subset_expansion=False):
    if subset_expansion:
        result = Q(0)
        for sub in subsets(tuple(sorted(strengths))):
            term = Q(1)
            for p in sub:
                term *= strengths[p]/Q(p**s+1)
            result += term
        return result
    value = Q(1)
    for p, lam in sorted(strengths.items()):
        value *= 1+lam/Q(p**s+1)
    return value


def exact_moment_polynomial(j, strengths, subset_expansion=False):
    out = {}
    for r in range(2*j+1):
        exponent = 2+r
        value = (Q((-1)**r*comb(2*j, r))
                 *squarefree_pi_coefficient(exponent)
                 *euler_weight(4+2*r, strengths, subset_expansion))
        out[exponent] = out.get(exponent, Q(0))+value
    return {e: c for e, c in out.items() if c}


def moments(count, strengths, depth=0):
    return [sum(mp.mpf((-1)**r*comb(2*j, r))*d_value(4+2*r)
                *floating(euler_weight(4+2*r, strengths))
                for r in range(2*j+1))
            for j in range(depth, depth+count)]


def inner(a, b, mu, shift=0):
    return sum(floating(ai)*floating(bj)*mu[i+j+shift]
               for i, ai in enumerate(a) for j, bj in enumerate(b))


def polynomial(n, mu):
    if n == 0:
        return [mp.mpf(1)]
    hankel = mp.matrix([[mu[i+j] for j in range(n)] for i in range(n)])
    return list(mp.lu_solve(hankel, mp.matrix([-mu[n+i] for i in range(n)])))+[mp.mpf(1)]


def multiply(a, b):
    out = [Q(0)]*(len(a)+len(b)-1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i+j] += ai*bj
    return out


def node(n):
    return (1-Q(1, n*n))**2


def evaluate(coefficients, x):
    value = Q(0)
    for c in reversed(coefficients):
        value = value*x+c
    return value


def isolator(a, m):
    xa = node(a)
    coefficients = [Q(1)]
    for n in range(1, a):
        xn = node(n)
        coefficients = multiply(coefficients, [-xn/(xa-xn), 1/(xa-xn)])
    for _ in range(m):
        coefficients = multiply(coefficients, [1/(1-xa), -1/(1-xa)])
    return coefficients


def detector_constants(a):
    c = Q(1)
    for n in range(1, a):
        c *= (1-node(n))/(node(a)-node(n))
    return c, (1-node(a+1))/(1-node(a))


def squarefree(n):
    d = 2
    while d*d <= n:
        if n % (d*d) == 0:
            return False
        d += 1
    return True


def atom_weight(n, strengths):
    if not squarefree(n):
        return Q(0)
    value = Q(1, n**4)
    for p, lam in strengths.items():
        if n % p == 0:
            value *= 1+lam
    return value


# Exact coordinate comparisons, with independent finite-subset expansion.
strength_values = [Q(-1), Q(-1, 2), Q(0), Q(1), Q(3)]
exact_cases = []
for values in product(strength_values, repeat=2):
    strengths = dict(zip((2, 3), values))
    for s in range(4, 34, 2):
        exact(euler_weight(s, strengths) == euler_weight(s, strengths, True))
    for j in range(9):
        first = exact_moment_polynomial(j, strengths)
        second = exact_moment_polynomial(j, strengths, True)
        exact(first == second)
        exact(all(isinstance(c, Q) and 2 <= exponent <= 2+2*j
                  for exponent, c in first.items()))
    exact_cases.append({'primes': [2, 3], 'strengths': [rational(v) for v in values]})

exact(squarefree_pi_coefficient(2) == 105)
exact(squarefree_pi_coefficient(3) == Q(675675, 691))
exact(squarefree_pi_coefficient(4) == Q(34459425, 3617))

# Evaluate exact pi-coordinate moments against the direct even-zeta formula.
coordinate_error = mp.mpf(0)
for values in [(Q(-1), Q(-1)), (Q(-1, 2), Q(3)), (Q(1), Q(1))]:
    strengths = dict(zip((2, 3), values))
    mu = moments(7, strengths)
    for j in range(7):
        coordinate = sum(floating(c)*mp.pi**(-2*e)
                         for e, c in exact_moment_polynomial(j, strengths).items())
        err = abs(coordinate-mu[j])
        coordinate_error = max(coordinate_error, err)
        numerical(err < mp.mpf('1e-300'))

# Orthogonality and recurrence grid; each numerical check is bounded explicitly.
grid = []
sample_polynomials = []
maximum_orthogonality_error = mp.mpf(0)
maximum_recurrence_error = mp.mpf(0)
parameter_grid = [(dict(zip((2, 3), values)), depth, 5)
                  for values in product(strength_values, repeat=2)
                  for depth in [0, 1, 3]]
parameter_grid += [(dict(zip((2, 3, 5), values)), 0, 4)
                   for values in product([Q(-1), Q(0), Q(1)], repeat=3)]
for strengths, depth, degree in parameter_grid:
    mu = moments(2*degree+3, strengths, depth)
    ps = [polynomial(n, mu) for n in range(degree+1)]
    norms = [inner(poly, poly, mu) for poly in ps]
    numerical(all(value > 0 for value in norms))
    for n in range(1, degree+1):
        for j in range(n):
            error = abs(inner(ps[n], [mp.mpf(0)]*j+[mp.mpf(1)], mu))
            maximum_orthogonality_error = max(maximum_orthogonality_error, error)
            numerical(error < mp.mpf('1e-270'))
            COUNTS['orthogonality_conditions'] += 1
        an = inner(ps[n], ps[n], mu, 1)/norms[n]
        numerical(0 < an < 1)
        numerical(norms[n]/norms[n-1] > 0)
    for n in range(1, degree):
        an = inner(ps[n], ps[n], mu, 1)/norms[n]
        bn = norms[n]/norms[n-1]
        recurrence = [mp.mpf(0)]*(n+2)
        for j, coefficient in enumerate(ps[n]):
            recurrence[j+1] += coefficient
            recurrence[j] -= an*coefficient
        for j, coefficient in enumerate(ps[n-1]):
            recurrence[j] -= bn*coefficient
        error = max(abs(a-b) for a, b in zip(recurrence, ps[n+1]))
        maximum_recurrence_error = max(maximum_recurrence_error, error)
        numerical(error < mp.mpf('1e-260'))
        COUNTS['recurrence_cases'] += 1
    grid.append({'primes': sorted(strengths),
                 'strengths': [rational(strengths[p]) for p in sorted(strengths)],
                 'depth': depth, 'maximum_degree': degree})
    if depth == 0 and strengths in [{2: Q(-1), 3: Q(-1)},
                                  {2: Q(-1, 2), 3: Q(1)},
                                  {2: Q(1), 3: Q(1)},
                                  {2: Q(-1), 3: Q(-1), 5: Q(-1)}]:
        sample_polynomials.append({'primes': sorted(strengths),
            'strengths': [rational(strengths[p]) for p in sorted(strengths)],
            'p1_coefficients_ascending': list(map(decimal, ps[1])),
            'p2_coefficients_ascending': list(map(decimal, ps[2])),
            'p3_coefficients_ascending': list(map(decimal, ps[3])),
            'moments_0_to_5': list(map(decimal, mu[:6]))})

# Independent finite squarefree sums, with an a priori omitted-tail bound.
direct_sum_cases = []
direct_n = 2000
nodes = [(n, floating(node(n))) for n in range(1, direct_n+1) if squarefree(n)]
for strengths in [{2: Q(-1), 3: Q(-1)}, {2: Q(-1, 2), 3: Q(3)},
                  {2: Q(1), 3: Q(1)}, {2: Q(-1), 3: Q(-1), 5: Q(-1)}]:
    mu = moments(6, strengths)
    direct = [mp.mpf(0)]*6
    for n, x in nodes:
        weight = floating(atom_weight(n, strengths))
        power = mp.mpf(1)
        for j in range(6):
            direct[j] += weight*power
            power *= x
    c = Q(1)
    for lam in strengths.values():
        c *= max(Q(1), 1+lam)
    envelope = floating(c/Q(3*direct_n**3))
    errors = [mu[j]-direct[j] for j in range(6)]
    for error in errors:
        numerical(-mp.mpf('1e-300') <= error <= envelope)
    direct_sum_cases.append({'primes': sorted(strengths),
        'strengths': [rational(strengths[p]) for p in sorted(strengths)],
        'n_max': direct_n, 'moment_indices': [0, 5],
        'maximum_difference': decimal(max(errors)), 'proven_tail_envelope': decimal(envelope)})

# Conditional definite pencils: positive other strengths, including deletions.
fiber_cases = [(2, {3: Q(-1)}), (2, {3: Q(3)}), (3, {2: Q(-1)}),
               (3, {2: Q(0)}), (5, {2: Q(-1), 3: Q(-1)}),
               (7, {2: Q(1, 2), 3: Q(-1), 5: Q(2)})]
fiber_roots = []
margin_bounds = []
maximum_relative_pencil_residual = mp.mpf(0)
for p, others in fiber_cases:
    largest_order = max(6, p+2)
    full = moments(2*largest_order+1, {**others, p: Q(0)})
    without = moments(2*largest_order+1, {**others, p: Q(-1)})
    previous_delta = None
    for order in range(1, largest_order+1):
        a = mp.matrix([[without[i+j] for j in range(order)] for i in range(order)])
        b = mp.matrix([[full[i+j]-without[i+j] for j in range(order)] for i in range(order)])
        la = mp.cholesky(a)
        mp.cholesky(b)
        inverse = la**-1
        eigenvalues, _ = mp.eigsy(inverse*b*inverse.T)
        numerical(all(value > 0 for value in eigenvalues))
        roots = [-1-1/value for value in eigenvalues]
        numerical(all(value < -1 for value in roots))
        for root in roots:
            matrix = a+(1+root)*b
            scale = max(mp.mpf(1), max(abs(value) for value in matrix))
            residual = abs(mp.det(matrix))/scale**order
            maximum_relative_pencil_residual = max(maximum_relative_pencil_residual, residual)
            numerical(residual < mp.mpf('1e-250'))
        delta = -1-max(roots)
        if previous_delta is not None:
            numerical(delta <= previous_delta)
        previous_delta = delta
        fiber_roots.append({'prime_variable': p,
            'other_strengths': {str(q): rational(lam) for q, lam in sorted(others.items())},
            'hankel_order': order, 'roots_approximate': list(map(decimal, roots)),
            'nearest_margin': decimal(delta)})
        if p <= order <= p+2:
            m = order-p
            cp, rp = detector_constants(p)
            ck = Q(1)
            for lam in others.values():
                ck *= max(Q(1), 1+lam)
            simple = Q(p)*ck*cp*cp*rp**(2*m)/3
            tail = d_value(4)*floating(Q(p**4, p**4+1))
            for q, lam in others.items():
                tail *= floating(1+lam/Q(q**4+1))
            tail -= sum(floating(atom_weight(n, others)) for n in range(1, p))
            sharp = p**4*floating(cp*cp*rp**(2*m))*tail
            numerical(0 < delta <= sharp <= floating(simple))
            margin_bounds.append({'prime_variable': p,
                'other_strengths': {str(q): rational(lam) for q, lam in sorted(others.items())},
                'hankel_order': order, 'nearest_margin': decimal(delta),
                'rational_upper_bound': rational(simple), 'arithmetic_upper_bound': decimal(sharp)})

# Exact isolating-polynomial geometry, followed by certified sign bounds.
for p in [2, 3, 5, 7]:
    cp, rp = detector_constants(p)
    exact(0 < rp < 1)
    for m in [0, 1, 3]:
        coefficients = isolator(p, m)
        exact(len(coefficients)-1 == p-1+m)
        exact(evaluate(coefficients, node(p)) == 1)
        for n in range(1, p):
            exact(evaluate(coefficients, node(n)) == 0)
        for n in [p+1, p+2, 2*p, 2*p+1]:
            exact(abs(evaluate(coefficients, node(n))) <= cp*rp**m)

bad_cases = [(2, {2: Q(-1001, 1000), 3: Q(-1)}),
             (3, {2: Q(-1), 3: Q(-1001, 1000)}),
             (5, {2: Q(-2), 3: Q(-3), 5: Q(-101, 100)}),
             (7, {2: Q(1, 2), 3: Q(-1), 5: Q(2), 7: Q(-10001, 10000)})]
negative_detectors = []
for p, strengths in bad_cases:
    cp, rp = detector_constants(p)
    c = Q(1)
    for lam in strengths.values():
        c *= max(Q(1), abs(1+lam))
    m = 0
    while Q(p)*c*cp*cp*rp**(2*m)/3 >= -(1+strengths[p]):
        m += 1
        assert m < 200
    bound = Q(1+strengths[p], p**4)+c*cp*cp*rp**(2*m)/Q(3*p**3)
    exact(bound < 0)
    coefficients = isolator(p, m)
    exact(evaluate(coefficients, node(p)) == 1)
    mu = moments(2*(len(coefficients)-1)+1, strengths)
    norm = inner(coefficients, coefficients, mu)
    numerical(norm < floating(bound) < 0)
    negative_detectors.append({'prime_negative_atom': p,
        'strengths': {str(q): rational(lam) for q, lam in sorted(strengths.items())},
        'm': m, 'polynomial_degree': len(coefficients)-1, 'hankel_order': len(coefficients),
        'negative_atom_weight_exact': rational(atom_weight(p, strengths)),
        'norm_upper_bound_exact': rational(bound), 'norm_approximate': decimal(norm),
        'coefficient_count': len(coefficients),
        'exact_certificate': 'rational upper bound is strictly negative; see Theorem2'})

# Exact finite nonconvexity anchors and additive positivity geometry.
anchors = [{2: Q(0), 3: Q(0)}, {2: Q(-34), 3: Q(-164)}, {2: Q(-17), 3: Q(-82)}]
anchor_factors = [euler_weight(4, strengths) for strengths in anchors]
exact(anchor_factors == [Q(1), Q(1), Q(0)])
semidefinite_anchors = [{2: Q(0), 3: Q(0)}, {2: Q(-34), 3: Q(-246)},
                       {2: Q(-68, 5), 3: Q(-492, 5)}]
semidefinite_factors = [euler_weight(4, strengths) for strengths in semidefinite_anchors]
exact(semidefinite_factors == [Q(1), Q(2), Q(-1, 25)])
additive_cases = 0
for values in product([Q(-2), Q(-3, 4), Q(0), Q(1)], repeat=3):
    feasible = all(1+sum(values[i] for i in subset) >= 0
                   for subset in subsets((0, 1, 2)))
    exact(feasible == (1+sum(value for value in values if value < 0) >= 0))
    additive_cases += 1
exact(1+Q(-3, 4)+Q(-3, 4) < 0)
exact((1+Q(-3, 4))*(1+Q(-3, 4)) > 0)

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path,
                    default=Path(__file__).resolve().parents[1]/'evidence'/'multi_prime_sieve_checks.json')
args = parser.parse_args()
source = Path(__file__).resolve()
report = {
    'claim_id': 'SF-DISCOVERY-100-MULTI-PRIME',
    'status': 'passed',
    'precision_decimal_digits': mp.mp.dps,
    'software': {'python': platform.python_version(), 'mpmath': mp.__version__},
    'runtime_seconds': round(time.monotonic()-START, 6),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'arithmetic': {'exact': 'fractions.Fraction; exact Bernoulli and even-zeta coordinates',
                   'numerical': 'mpmath at320digits; numerical pencil roots are not interval-certified'},
    'counts': COUNTS,
    'exact_coordinate_parameter_cases': exact_cases,
    'coordinate_evaluation_error_maximum': decimal(coordinate_error),
    'orthogonal_parameter_cases': len(grid),
    'orthogonal_grid': grid,
    'maximum_absolute_orthogonality_error': decimal(maximum_orthogonality_error),
    'maximum_recurrence_error': decimal(maximum_recurrence_error),
    'sample_polynomials': sample_polynomials,
    'direct_sum_cases': direct_sum_cases,
    'conditional_fiber_root_cases': fiber_roots,
    'conditional_margin_bound_cases': margin_bounds,
    'maximum_relative_pencil_residual': decimal(maximum_relative_pencil_residual),
    'negative_atom_detectors': negative_detectors,
    'nonconvex_order_one_example': {'primes': [2, 3],
        'parameter_points': [[rational(strengths[p]) for p in [2, 3]] for strengths in anchors],
        'mass_factors_relative_to_D4_exact': list(map(rational, anchor_factors))},
    'nonconvex_semidefinite_example': {'primes': [2, 3],
        'parameter_points': [[rational(strengths[p]) for p in [2, 3]] for strengths in semidefinite_anchors],
        'convex_weights_first_two': ['3/5', '2/5'],
        'mass_factors_relative_to_D4_exact': list(map(rational, semidefinite_factors))},
    'additive_domain_cases': additive_cases,
    'non_claims': ['finite numerical checks are not a universal proof',
                   'floating roots are not interval certificates',
                   'no historical novelty claim', 'no global multivariate real-stability claim'],
    'run_history': [{'status': 'passed', 'failed_check': None,
                     'interpretation': 'All declared finite assertions passed in this run.'}]
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'status': report['status'], 'counts': COUNTS,
                  'orthogonal_parameter_cases': len(grid),
                  'conditional_fiber_root_cases': len(fiber_roots),
                  'negative_atom_detectors': len(negative_detectors),
                  'runtime_seconds': report['runtime_seconds']}, indent=2))
