"""Block 22 exact finite local quadratic audit (standard library only).

Arithmetic roots solve y^2 = -1 at an arithmetic prime p. Coefficient roots
solve x^2 = +1 and parameterize unit-valued characters of the two-element group.
The finite local quotient map is a model: it does not compute Galois groups.
"""

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

ARITHMETIC_PRIME_MAX = 47
ARITHMETIC_MODULUS_MAX = 100000
COEFFICIENT_DEPTHS = ((2, 8), (3, 5))
BASELINE_SHA256 = 'fbe69e04d5e693f6f91b7af7090b04ec43a3467feea1c17cd53fbc9cd9cffbf2'


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def primes_up_to(bound):
    # Trial division does not use the splitting criterion under test.
    return [n for n in range(2, bound + 1)
            if all(n % d != 0 for d in range(2, math.isqrt(n) + 1))]


def arithmetic_roots(modulus):
    """All residues solving y^2 = -1, including modulus-one zero ring."""
    return [y for y in range(modulus) if (y*y + 1) % modulus == 0]


def coefficient_roots(modulus):
    """All residues solving x^2 = +1; kept separate from arithmetic roots."""
    return [x for x in range(modulus) if (x*x - 1) % modulus == 0]


def unit_characters(modulus):
    """Independently enumerate all unital C2 -> units homomorphisms.

    C2 is represented additively by 0 and 1. Only the identity image is fixed;
    every generator candidate is checked for being a unit and for all four
    group-law pairs, without invoking coefficient_roots.
    """
    output = []
    for generator_image in range(modulus):
        if math.gcd(generator_image, modulus) != 1:
            continue
        values = (1 % modulus, generator_image)
        if all(values[(g+h) % 2] == values[g]*values[h] % modulus
               for g in range(2) for h in range(2)):
            output.append(values)
    return output


def local_quotient_map(arithmetic_prime):
    """Declared finite quotient model, independently checked as a homomorphism.

    Split primes have zero map C2 -> C2, other primes the identity map. The
    assignment is the mathematical interpretation being corroborated, not an
    algorithm that constructs a local absolute Galois group or its image.
    """
    return (0, 0) if arithmetic_prime % 4 == 1 else (0, 1)


def restrict(values, quotient_map):
    return tuple(values[quotient_map[g]] for g in range(2))


def audit_arithmetic(prime, counts):
    levels = []
    modulus, depth = 1, 0
    while modulus <= ARITHMETIC_MODULUS_MAX:
        roots = arithmetic_roots(modulus)
        if depth == 0:
            expected_count = 1
        elif prime == 2:
            expected_count = 1 if depth == 1 else 0
        else:
            expected_count = 2 if prime % 4 == 1 else 0
        need(len(roots) == expected_count,
             f'arithmetic root criterion failed at {prime}^{depth}')
        counts['arithmetic_levels'] += 1
        counts['arithmetic_residue_candidates'] += modulus
        counts['arithmetic_roots'] += len(roots)
        levels.append({'depth': depth, 'modulus': modulus, 'minus_one_roots': roots})
        modulus *= prime
        depth += 1
    edges = []
    for lower, upper in zip(levels, levels[1:]):
        m = lower['modulus']
        # Independent method: produce candidates parent + k*m, not a scan of
        # the high root list. Record every parent's full root-lift fiber.
        fibers = []
        for parent in lower['minus_one_roots']:
            lifts = []
            for digit in range(prime):
                candidate = parent + digit*m
                counts['arithmetic_lift_candidates'] += 1
                if (candidate*candidate + 1) % (m*prime) == 0:
                    lifts.append(candidate)
            scan_fiber = [y for y in upper['minus_one_roots'] if y % m == parent]
            need(lifts == scan_fiber, f'full lift fiber failed at {prime}^{lower["depth"]}')
            if prime != 2 and lower['depth'] >= 1:
                need(len(lifts) == 1, f'odd-prime unique root lift failed at {prime}^{lower["depth"]}')
            fibers.append({'parent': parent, 'lifts': lifts})
            counts['arithmetic_root_lift_fibers'] += 1
        need(sorted(y for fiber in fibers for y in fiber['lifts']) == upper['minus_one_roots'],
             'root-lift construction omitted a high root')
        edges.append({'lower_depth': lower['depth'], 'upper_depth': upper['depth'], 'fibers': fibers})
        counts['arithmetic_reduction_edges'] += 1
    if prime != 2:
        need((1 - (-1)) % prime != 0, 'odd-prime plus/minus-one collision')
        counts['odd_prime_sign_noncollisions'] += 1
    return {'arithmetic_prime': prime, 'split_flag_for_finite_model': prime % 4 == 1,
            'levels': levels, 'full_lift_fibers': edges}


def audit_coefficients(coefficient_prime, maximum_depth, arithmetic_primes, counts):
    levels = []
    for depth in range(maximum_depth + 1):
        modulus = coefficient_prime**depth
        roots = coefficient_roots(modulus)
        characters = unit_characters(modulus)
        need(roots == [v[1] for v in characters], 'coefficient root/character mismatch')
        counts['coefficient_levels'] += 1
        counts['coefficient_residue_candidates'] += modulus
        counts['coefficient_root_character_matches'] += len(roots)
        counts['coefficient_character_group_law_pairs'] += 4*len(roots)
        restrictions = []
        for p in arithmetic_primes:
            q = local_quotient_map(p)
            need(q[0] == 0 and all(q[(g+h) % 2] == (q[g]+q[h]) % 2
                                      for g in range(2) for h in range(2)),
                 'local quotient model is not a homomorphism')
            for values in characters:
                local_values = restrict(values, q)
                trivial = all(v == 1 % modulus for v in local_values)
                need(trivial == (p % 4 == 1 or values[1] == 1 % modulus),
                     f'local triviality criterion failed at arithmetic p={p}, coefficient {modulus}')
                need(all(math.gcd(v, modulus) == 1 for v in local_values), 'nonunit local value')
                need(all(local_values[(g+h) % 2] == local_values[g]*local_values[h] % modulus
                         for g in range(2) for h in range(2)), 'local character law')
                counts['local_restriction_cases'] += 1
                counts['local_character_group_law_pairs'] += 4
                restrictions.append({'arithmetic_prime': p, 'generator_image': values[1],
                                     'local_values': list(local_values), 'is_trivial': trivial})
        levels.append({'depth': depth, 'modulus': modulus, 'plus_one_roots': roots,
                       'characters': [list(v) for v in characters], 'restrictions': restrictions})
    for high in levels:
        for low in levels[:high['depth'] + 1]:
            counts['coefficient_reduction_maps'] += 1
            for values in high['characters']:
                reduced = tuple(v % low['modulus'] for v in values)
                need(list(reduced) in low['characters'], 'coefficient reduction not a character')
                for p in arithmetic_primes:
                    q = local_quotient_map(p)
                    left = tuple(v % low['modulus'] for v in restrict(values, q))
                    right = restrict(reduced, q)
                    need(left == right, 'local restriction/coefficient reduction naturality')
                    counts['coefficient_local_naturality_values'] += 2
                    if all(v == 1 % high['modulus'] for v in restrict(values, q)):
                        need(all(v == 1 % low['modulus'] for v in right),
                             'local triviality failed to descend')
                        counts['local_triviality_reduction_implications'] += 1
    return {'coefficient_prime': coefficient_prime, 'maximum_depth': maximum_depth, 'levels': levels}


def audit_boundaries():
    need(arithmetic_roots(2) == [1] and arithmetic_roots(4) == [],
         'exceptional arithmetic prime-two benchmark')
    need(arithmetic_roots(5) == [2, 3], 'split arithmetic prime-five benchmark')
    need(arithmetic_roots(3) == [], 'nonsplit arithmetic prime-three benchmark')
    trivial_mod2, sign_mod2 = (1, 1), (1, (-1) % 2)
    trivial_mod4, sign_mod4 = (1, 1), (1, (-1) % 4)
    need(trivial_mod2 == sign_mod2 and trivial_mod4 != sign_mod4,
         'dyadic coefficient sign benchmark')
    for p in (2, 3, 7):
        need(restrict(sign_mod2, local_quotient_map(p)) == trivial_mod2,
             'residual local sign collision')
        need(restrict(sign_mod4, local_quotient_map(p)) != trivial_mod4,
             'local sign separation modulo four')
    need(restrict(sign_mod4, local_quotient_map(5)) == trivial_mod4,
         'split-prime sign restriction should be trivial')
    need(3 in coefficient_roots(8) and not any(x % 8 == 3 for x in coefficient_roots(16)),
         'coefficient character mod-eight nonlifting benchmark')
    return {'arithmetic_minus_one_mod_two': [1], 'arithmetic_minus_one_mod_four': [],
            'coefficient_plus_one_mod_two': [1], 'coefficient_plus_one_mod_four': [1, 3],
            'dyadic_sign_same_mod_two_distinct_mod_four': True,
            'sign_local_mod_four_nontrivial_at_model_primes': [2, 3, 7],
            'sign_local_mod_four_trivial_at_model_prime': 5,
            'coefficient_three_mod_eight_has_no_lift_mod_sixteen': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    count_names = ('arithmetic_primes arithmetic_levels arithmetic_residue_candidates '
                   'arithmetic_roots arithmetic_lift_candidates arithmetic_root_lift_fibers '
                   'arithmetic_reduction_edges odd_prime_sign_noncollisions coefficient_levels '
                   'coefficient_residue_candidates coefficient_root_character_matches '
                   'coefficient_character_group_law_pairs local_restriction_cases '
                   'local_character_group_law_pairs coefficient_reduction_maps '
                   'coefficient_local_naturality_values local_triviality_reduction_implications').split()
    counts = dict.fromkeys(count_names, 0)
    primes = primes_up_to(ARITHMETIC_PRIME_MAX)
    need(primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
         'prime enumeration benchmark mismatch')
    counts['arithmetic_primes'] = len(primes)
    arithmetic = [audit_arithmetic(p, counts) for p in primes]
    coefficients = [audit_coefficients(p, d, primes, counts) for p, d in COEFFICIENT_DEPTHS]
    boundaries = audit_boundaries()
    result = {
        'schema_version': 1, 'block': 22, 'status': 'passed_exact_bounded_assertions',
        'baseline_archive_sha256': BASELINE_SHA256,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'python_version': platform.python_version(), 'arithmetic_domain': 'exact integer residues',
        'counts': counts,
        'bounds': {'arithmetic_prime_maximum': ARITHMETIC_PRIME_MAX,
                   'arithmetic_modulus_maximum': ARITHMETIC_MODULUS_MAX,
                   'coefficient_prime_maximum_depth': [list(x) for x in COEFFICIENT_DEPTHS]},
        'arithmetic_minus_one_roots': arithmetic,
        'coefficient_plus_one_characters': coefficients,
        'boundary_checks': boundaries,
        'non_claims': [
            'The finite local quotient map is a declared C2 model, not an executed absolute Galois group.',
            'No p-adic root theorem, inertia identification, Hodge-Tate statement, or Weil-Deligne attachment is proved by this run.',
            'Arithmetic-prime roots of minus one and coefficient-prime roots of plus one have different roles.',
            'The complete lift fibers stop at the displayed finite terminal depths.',
            'No general arithmetic claim or infinite-lift existence follows from finite output.']}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'counts': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
