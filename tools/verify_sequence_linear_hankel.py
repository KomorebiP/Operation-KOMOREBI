"""Uniform order-nine identity via a complete degree-18 polynomial certificate.

Author: Komorebi P. All arithmetic and Euclidean identities use Fractions.
"""
import argparse
from fractions import Fraction as F
from pathlib import Path
import json
import time
import sequence_rational_hankel as new
from sequence_differential_hankel import structured_differential_hankel
from test_sequence_differential_hankel import direct_hankel


def trim(poly):
    poly = list(poly)
    while len(poly)>1 and not poly[-1]:
        poly.pop()
    return poly


def add(p, q):
    return trim([(p[j] if j<len(p) else 0)+(q[j] if j<len(q) else 0)
                 for j in range(max(len(p), len(q)))])


def scale(p, c):
    return trim([F(c)*x for x in p])


def multiply(p, q):
    result = [F(0)]*(len(p)+len(q)-1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            result[i+j] += x*y
    return trim(result)


def power(p, n):
    result = [F(1)]
    for _ in range(n):
        result = multiply(result, p)
    return result


def divide(p, q):
    remainder, q = trim(p), trim(q)
    quotient = [F(0)]*max(1, len(p)-len(q)+1)
    while any(remainder) and len(remainder)>=len(q):
        shift = len(remainder)-len(q)
        coefficient = remainder[-1]/q[-1]
        quotient[shift] += coefficient
        subtract = [F(0)]*shift+scale(q, -coefficient)
        remainder = add(remainder, subtract)
    return trim(quotient), remainder


def bezout(p, q):
    a, b, u, v, x, y = p, q, [F(1)], [F(0)], [F(0)], [F(1)]
    while any(b):
        quotient, remainder = divide(a, b)
        a, b, u, x, v, y = (b, remainder, x,
                            add(u, scale(multiply(quotient, x), -1)), y,
                            add(v, scale(multiply(quotient, y), -1)))
    return scale(a, 1/a[-1]), scale(u, 1/a[-1]), scale(v, 1/a[-1])


def characteristic(a, b):
    return power(multiply([-2*a, 1], [4*a*a, -4*(a-b), 1]), 3)


def interpolate(values):
    """Monomial coefficients from values at the consecutive integers 0,...,n."""
    result = [F(0)]
    n = len(values)-1
    for j, value in enumerate(values):
        term, denominator = [F(value)], F(1)
        for k in range(n+1):
            if k!=j:
                term = multiply(term, [-k, 1])
                denominator *= j-k
        result = add(result, scale(term, 1/denominator))
    return result+[F(0)]*(n+1-len(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    numerators = []
    vectors, early, direct = 0, 0, 0
    for a in range(19):
        coeffs = characteristic(a, 1)
        certificate = {'start': 9, 'states': 70, 'order': 9,
                       'coefficients': coeffs}
        if not new.verify_certificate([a, 1], [1], certificate):
            raise AssertionError(('nonzero full-state residue', a))
        vectors += 1
        values = structured_differential_hankel([a, 1], [1], 17)
        for n in range(1, 9):
            if sum(coeffs[j]*values[n+j] for j in range(10)):
                raise AssertionError(('nonzero early residue', a, n))
            early += 1
        for n in range(18):
            if values[n]!=direct_hankel([a, 1], [1], n):
                raise AssertionError(('direct determinant disagreement', a, n))
            direct += 1
        if new.linear_hankel_determinants(a, 1, 17)!=values:
            raise AssertionError(('rational OGF implementation', a))
        denominator = list(reversed(coeffs))
        numerators.append([sum(denominator[j]*values[n-j]
                               for j in range(n+1)) for n in range(10)])
    # N_n is homogeneous of degree n in (a,b). Recover ALL its coefficients.
    homogeneous_numerators = [interpolate([numerators[a][n] for a in range(n+1)])
                             for n in range(10)]
    off_grid = [(-F(2, 3), F(5, 7)), (4, -3), (2, 0), (0, 0), (0, 2)]
    off_grid_checks = 0
    for a, b in off_grid:
        values = structured_differential_hankel([a, b], [1], 22)
        if new.linear_hankel_determinants(a, b, 22)!=values:
            raise AssertionError(('off-grid rational OGF implementation', a, b))
        coeffs = characteristic(a, b)
        denominator = list(reversed(coeffs))
        for n in range(1, 14):
            if sum(coeffs[j]*values[n+j] for j in range(10)):
                raise AssertionError(('off-grid recurrence', a, b, n))
            off_grid_checks += 1
        for n in range(10):
            expected = sum(coefficient*a**j*b**(n-j)
                           for j, coefficient in enumerate(homogeneous_numerators[n]))
            actual = sum(denominator[j]*values[n-j] for j in range(n+1))
            if expected!=actual:
                raise AssertionError(('homogeneous numerator', a, b, n))
            off_grid_checks += 1
    sample_num, sample_den = numerators[1], list(reversed(characteristic(1, 1)))
    common, u, v = bezout(sample_num, sample_den)
    identity = add(multiply(u, sample_num), multiply(v, sample_den))
    if common!=[F(1)] or identity!=[F(1)]:
        raise AssertionError('sample numerator and denominator are not certified coprime')
    result = {
        'claim': 'For every characteristic-zero a,b, [(S-2a)(S^2-4(a-b)S+4a^2)]^3 W_n=0 for n>=1',
        'uniform_reduction': {
            'fixed_M': 1, 'fixed_K': 9, 'fixed_transfer_states': 70,
            'full_state_residual_homogeneous_degree': 18,
            'interpolation_variable': 'a at b=1',
            'evaluation_points': list(range(19)),
            'early_residual_homogeneous_degrees': list(range(10, 18)),
            'reason_complete': '19 distinct values determine every polynomial of degree at most 18; homogeneity recovers every a^j b^(18-j) coefficient including b=0.',
        },
        'full_state_vector_identities': vectors,
        'early_index_identities': early,
        'independent_direct_determinants': direct,
        'additional_off_grid_checks': off_grid_checks,
        'ogf_numerator_homogeneous_coefficients': [
            {'z_degree': n, 'coefficients_of_a_power_j_b_power_n_minus_j': list(map(str, poly))}
            for n, poly in enumerate(homogeneous_numerators)],
        'ogf_denominator': '[(1-2az)(1-4(a-b)z+4a^2 z^2)]^3',
        'sample_a1_b1': {
            'numerator': list(map(str, sample_num)),
            'denominator': list(map(str, sample_den)),
            'bezout_u': list(map(str, u)), 'bezout_v': list(map(str, v)),
            'bezout_identity': 'u*numerator+v*denominator=1',
            'minimal_eventual_order': 9,
        },
        'elapsed_seconds': time.perf_counter()-started,
        'scope': 'Uniform conclusion uses the separately reviewed degree/homogeneity reduction; this is not inference from an unspecified finite prefix.',
    }
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in (
        'full_state_vector_identities', 'early_index_identities',
        'independent_direct_determinants', 'additional_off_grid_checks',
        'elapsed_seconds')}))


if __name__=='__main__':
    main()
