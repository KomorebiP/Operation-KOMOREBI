#!/usr/bin/env python3
"""Exact bounded ray-character and Frey Frobenius audit; no global closure.

All arithmetic is integral. Point counts use the quadratic character via the
norm F_(q^2)->F_q; the earlier square-enumeration implementation is separately
compared at 11 and 19. Coefficient lists are constant term first.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIMES = (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61)


def chi(a, q):
    t = pow(a % q, (q-1)//2, q)
    return -1 if t == q-1 else t


def ray_characters():
    # Characters of F9* x F5* x {+,-}^2 in powers of a formal eighth root.
    # Generators: phi mod3, 3 mod5, sign at embedding sqrt5>0, other sign.
    chars = []
    for k in range(8):
        for j in range(4):
            for u in range(2):
                for v in range(2):
                    if (4*k + 4*j + 4*u + 4*v) % 8:
                        continue  # global unit -1
                    if (k + 2*j + 4*v) % 8:
                        continue  # global unit phi
                    e2 = (-4*k - 6*j) % 8  # inverse residues of positive 2
                    chars.append({'k': k, 'j': j, 'real_bits': [u, v],
                                  'Frob2_exponent_mod8': e2})
    selected = [c for c in chars if c['Frob2_exponent_mod8'] == 4]
    assert len(chars) == 8
    assert [(c['k'], c['j'], c['real_bits']) for c in selected] == [
        (0, 2, [1, 1]), (4, 2, [0, 0])]
    return {'all_characters': chars, 'Frob2_minus_one_characters': selected}


def values_at_q(q):
    f = 1 if chi(5, q) == 1 else 2
    a = pow(q, f, 5)
    assert a in (1, 4)
    cm = 1 if a == 1 else -1
    real = cm * pow(chi(-3, q), f)
    return f, cm, real


def point_count_polynomial(A, B, q):
    d = next(t for t in range(2, q) if chi(t, q) == -1)
    coeffs = (1, 0, 0, 10*B, 0, 12*A, 5*B*B)
    counts = []
    for degree in (1, 2):
        total = 0
        for x in range(q):
            for y in range(q if degree == 2 else 1):
                a = b = 0
                for c in coeffs:
                    a, b = (a*x + d*b*y + c) % q, (a*y + b*x) % q
                total += chi(a*a-d*b*b, q) if degree == 2 else chi(a, q)
        counts.append(q**degree + total + 2)  # two infinity points
    n1, n2 = counts
    s1 = q+1-n1
    numerator = s1*s1 - q*q - 1 + n2
    assert numerator % 2 == 0
    s2 = numerator//2
    return [q*q, -q*s1, s2, -s1, 1]


def over_K(poly, q, f):
    if f == 1:
        return poly
    # Product P(sqrt(T))*P(-sqrt(T)); eigenvalues are squared.
    s1, s2 = -poly[3], poly[2]
    return [q**4, q*q*(2*s2-s1*s1),
            s2*s2 + 2*q*q - 2*q*s1*s1, 2*s2-s1*s1, 1]


def has_root(poly, v):
    return sum(c*v**i for i, c in enumerate(poly)) % 7 == 0


def has_double_root(poly, v):
    return has_root(poly, v) and sum(i*c*v**(i-1)
                                   for i, c in enumerate(poly) if i) % 7 == 0


def bad_sign(q, f):
    if f == 2:
        # Nodes split over F_(q^2); the norm of their branch values is 45.
        return chi(45, q)
    roots = [r for r in range(q) if (r*r+r-1) % q == 0]
    signs = [chi(6-3*r, q) for r in roots]
    assert len(roots) == 2 and signs[0] == signs[1] != 0
    return signs[0]


def audit_prime(q, previous):
    f, cm, real = values_at_q(q)
    seventh_powers = {pow(c, 7, q) for c in range(1, q)}
    remaining = {(A, B) for A in range(q) for B in range(q)
                 if (A**3+B**5) % q}
    total_smooth = len(remaining)
    orbits = []
    checked = 0
    while remaining:
        A, B = min(remaining)
        orbit = {(A*pow(u, 5, q) % q, B*pow(u, 3, q) % q)
                 for u in range(1, q)}
        assert orbit <= remaining
        remaining -= orbit
        admissible = [(a, b) for a, b in sorted(orbit)
                      if (a**3+b**5) % q in seventh_powers]
        poly = point_count_polynomial(A, B, q)
        if q in previous:
            for pair in orbit:
                assert poly == previous[q][pair], (q, pair, poly)
                checked += 1
        kpoly = over_K(poly, q, f)
        orbits.append({'A': A, 'B': B, 'orbit_size': len(orbit),
                       'admissible_pair_count': len(admissible),
                       'one_admissible_pair': list(admissible[0]) if admissible else None,
                       'Pq': poly, 'PK': kpoly,
                       'CM_simple_root': has_root(kpoly, cm),
                       'CM_double_root': has_double_root(kpoly, cm),
                       'real_simple_root': has_root(kpoly, real),
                       'real_double_root': has_double_root(kpoly, real)})
    epsilon = bad_sign(q, f)
    assert epsilon == real  # audited finite instance of the written identity
    bad_roots = [epsilon % 7, (epsilon * pow(q, f, 7)) % 7]
    result = {'q': q, 'fK': f, 'CM_value': cm, 'real_value': real,
              'smooth_pairs_covered': total_smooth,
              'Beal_admissible_smooth_pairs': sum(r['admissible_pair_count'] for r in orbits),
              'prior_polynomials_compared': checked,
              'bad_torus_sign': epsilon, 'bad_roots_mod7': bad_roots,
              'singular_primitive_pairs': q-1,
              'CM_bad_compatible': cm % 7 in bad_roots,
              'real_bad_compatible': real % 7 in bad_roots,
              'orbits': orbits}
    for name in ('CM', 'real'):
        for multiplicity in ('simple', 'double'):
            key = name+'_'+multiplicity+'_root'
            result[name+'_'+multiplicity+'_smooth_survivors'] = sum(
                r['admissible_pair_count'] for r in orbits if r[key])
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    prior = json.loads((ROOT/'work47/verification/modular_correlations.json').read_text())
    previous = {11: {(r['A'], r['B']): r['jacobian_frobenius_polynomial']
                     for r in prior['q11_complete_smooth_Beal_point_counts']}, 19: {}}
    for r in prior['q19_weighted_orbit_point_counts']['orbits']:
        for u in range(1, 19):
            previous[19][r['A']*pow(u, 5, 19) % 19,
                         r['B']*pow(u, 3, 19) % 19] = r['jacobian_frobenius_polynomial']
    rows = [audit_prime(q, previous) for q in PRIMES]
    q11 = next(r for r in rows if r['q'] == 11)
    assert q11['CM_simple_smooth_survivors'] == 0 and not q11['CM_bad_compatible']
    assert sum(r['prior_polynomials_compared'] for r in rows) == 452
    assert all(r['real_bad_compatible'] for r in rows)
    result = {'status': 'EXACT_BOUNDED_SIEVE_WITH_SURVIVING_REAL_CHARACTER',
              'ray_group': ray_characters(), 'prime_checks': rows,
              'forced_C_divisors_from_simple_root': [r['q'] for r in rows
                  if r['real_simple_smooth_survivors'] == 0],
              'forced_C_divisors_from_double_root': [r['q'] for r in rows
                  if r['real_double_smooth_survivors'] == 0],
              'scope': 'Necessary character tests only. Singular C=0 lane survives at every tested prime; no integer nonexistence follows.'}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'],
                      'forced_C_divisors_from_simple_root': result['forced_C_divisors_from_simple_root'],
                      'forced_C_divisors_from_double_root': result['forced_C_divisors_from_double_root'],
                      'prime_summary': [{k: r[k] for k in ('q', 'fK', 'CM_value', 'real_value',
                          'Beal_admissible_smooth_pairs', 'real_simple_smooth_survivors',
                          'real_double_smooth_survivors')} for r in rows]}))


if __name__ == '__main__':
    main()
