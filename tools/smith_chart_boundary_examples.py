"""Reproduce the Smith guide's exact witnesses and bounded sampling example.

Run from the repository root with: python -B tools/smith_chart_boundary_examples.py
The rational examples use fractions. The interpolation example scans a fixed,
finite set of angles in binary64 arithmetic; its maxima are sampled maxima,
not certified bounds over every angle. No external packages are required.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
import cmath
from fractions import Fraction as F
import json
import math
from pathlib import Path


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def project(coefficients: list[F], order: int, index: int) -> list[F]:
    return [a if m % order == index else F(0) for m, a in enumerate(coefficients)]


def evaluate(coefficients: list[F], t: F) -> F:
    return sum((a * t**m for m, a in enumerate(coefficients)), F(0))


def multiply_pair(a: tuple[F, F], b: tuple[F, F]) -> tuple[F, F]:
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def pair_power(a: tuple[F, F], n: int) -> tuple[F, F]:
    value = (F(1), F(0))
    for _ in range(n):
        value = multiply_pair(value, a)
    return value


def quantile(rho: float, mass: float) -> float:
    """Piecewise real inverse, evaluated only on the stated finite grid."""
    beta = (1 - rho*rho) / (1 + rho*rho)
    if mass < 0.25:
        return math.atan(beta * math.tan(2 * math.pi * mass))
    if mass == 0.25:
        return math.pi / 2
    if mass < 0.75:
        return math.pi + math.atan(beta * math.tan(2 * math.pi * (mass - 0.5)))
    if mass == 0.75:
        return 3 * math.pi / 2
    return 2 * math.pi + math.atan(beta * math.tan(2 * math.pi * (mass - 1)))


def sampling_scan(weighted: bool, rho: float = 0.9, count: int = 32,
                  scan_count: int = 65536) -> dict[str, float]:
    """Interpolate z(t) and h(t)=t in angle, at the named boundary nodes."""
    tau = 2 * math.pi
    angles = [quantile(rho, k/count) if weighted else tau*k/count for k in range(count)]
    check(all(a < b for a, b in zip(angles, angles[1:])), 'nodes must be strictly ordered')
    angles = [angles[-1]-tau, *angles, angles[0]+tau]

    def values(theta: float) -> tuple[complex, complex]:
        t = rho * cmath.exp(1j * theta)
        return t, (1+t)/(1-t)

    nodes = [values(theta) for theta in angles]
    worst_h = worst_z = 0.0
    for k in range(scan_count):
        theta = tau*k/scan_count
        j = bisect_right(angles, theta)-1
        fraction = (theta-angles[j])/(angles[j+1]-angles[j])
        h, z = values(theta)
        h_line = (1-fraction)*nodes[j][0] + fraction*nodes[j+1][0]
        z_line = (1-fraction)*nodes[j][1] + fraction*nodes[j+1][1]
        worst_h = max(worst_h, abs(h-h_line))
        worst_z = max(worst_z, abs(z-z_line))
    return {'h_max': worst_h, 'z_max': worst_z}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional JSON result path')
    args = parser.parse_args()

    # The phase ratio i has order four, not order two.
    phase_i = (F(0), F(1))
    start, target = (F(1, 2), F(0)), (F(0), F(1, 2))
    check(target not in (start, (-start[0], -start[1])), 'order-two target')
    check(multiply_pair(start, phase_i) == target, 'order-four target')
    check(pair_power(phase_i, 2) == (F(-1), F(0)), 'order-two failure')
    check(pair_power(phase_i, 4) == (F(1), F(0)), 'order-four reachability')
    check((F(-1, 3)-1)/(F(-1, 3)+1) == -2, 'outside passive disk')
    check((F(100)-50)/(F(100)+50) == F(1, 3), 'line-only mismatch')

    # A nonprimitive root cannot isolate the even coefficients of 1+t.
    t = F(1, 2)
    bogus_average = (evaluate([F(1), F(1)], t) * 2) / 2
    even_packet = evaluate(project([F(1), F(1)], 2, 0), t)
    check((bogus_average, even_packet) == (F(3, 2), F(1)), 'nonprimitive root')

    # Noncoprime orders 2 and 4 intersect at order 4, not order 8.
    polynomial = [F(1), F(0), F(0), F(0), F(1)]
    staged = evaluate(project(project(polynomial, 4, 0), 2, 0), t)
    product_order = evaluate(project(polynomial, 8, 0), t)
    check((staged, product_order) == (F(17, 16), F(1)), 'noncoprime projectors')

    # At -99/100 the two packets are large and cancel to the original value.
    t = F(-99, 100)
    p0 = (1+t*t)/(1-t*t)
    p1 = 2*t/(1-t*t)
    exact_z = (1+t)/(1-t)
    check((p0, p1, exact_z) == (F(19801, 199), F(-19800, 199), F(1, 199)),
          'packet cancellation')
    check(p0+p1 == exact_z, 'packet reconstruction')

    # Two distinct analytic functions give the same two finite samples.
    f0 = [F(1)]
    f1 = [F(15, 16), F(0), F(1, 4)]
    check(all(evaluate(f0, t) == evaluate(f1, t) == 1 for t in (F(-1, 2), F(1, 2))),
          'equal samples')
    check(evaluate(f0, F(0)) == 1 and evaluate(f1, F(0)) == F(15, 16),
          'different values at zero')
    check(F(15, 16)-F(1, 4) == F(11, 16), 'positive-real lower bound')

    uniform, weighted = sampling_scan(False), sampling_scan(True)
    for observed, expected, tolerance in (
        (uniform['z_max'], 5.999, 0.0005), (weighted['z_max'], 0.784, 0.0005),
        (uniform['h_max'], 0.00433, 0.000005), (weighted['h_max'], 0.12927, 0.000005),
    ):
        check(abs(observed-expected) < tolerance, 'sampling scan changed')

    result = {
        'status': 'PASS',
        'exact': {
            'phase_i_squared': '-1',
            'phase_i_fourth': '1',
            'outside_passive_disk_gamma': '-2',
            'line_only_load_gamma': '1/3',
            'nonprimitive_average_and_even_packet': [str(bogus_average), str(even_packet)],
            'noncoprime_staged_and_product_order': [str(staged), str(product_order)],
            'packet_cancellation': [str(p0), str(p1), str(exact_z)],
            'two_functions_at_zero': [str(evaluate(f0, F(0))), str(evaluate(f1, F(0)))],
            'positive_real_lower_bound': '11/16',
        },
        'finite_sampling': {'radius': 0.9, 'nodes': 32, 'scan_angles': 65536,
                            'uniform': uniform, 'equal_mass_boundaries': weighted},
        'scope': 'Exact rational witnesses and a finite binary64 scan; not a universal numeric error bound.'
    }
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
