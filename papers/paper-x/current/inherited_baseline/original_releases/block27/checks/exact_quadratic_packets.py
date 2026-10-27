"""Block 21: exact finite audits of quadratic ring points and C2 characters.

Only standard-library integer arithmetic is used. The finite reduction forests
do not decide which arbitrary finite prefixes extend to infinite branches.
"""

import argparse
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path


PRIME_DEPTHS = ((2, 12), (3, 7), (5, 5))
COEFFICIENT_PROBES = tuple(itertools.product(range(-2, 3), repeat=2))


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def square_roots_of_one(modulus):
    """Exhaustive direct evaluation; modulus one is the zero ring."""
    return [x for x in range(modulus) if (x*x - 1) % modulus == 0]


def character_values(modulus):
    """Independent enumeration of all unit-valued homomorphisms from C2.

    The identity image is imposed, and each possible generator image is tested
    against all four pairs of group elements. No root predicate is called.
    """
    one = 1 % modulus
    output = []
    for image in range(modulus):
        if math.gcd(image, modulus) != 1:
            continue
        values = (one, image)
        if all(values[(a+b) % 2] == values[a]*values[b] % modulus
               for a in range(2) for b in range(2)):
            output.append(image)
    return output


def quotient_add(left, right, modulus):
    return ((left[0] + right[0]) % modulus,
            (left[1] + right[1]) % modulus)


def quotient_mul(left, right, modulus):
    # Coefficient order is (1, X), with X^2 = 1.
    a, b = left
    c, d = right
    return ((a*c + b*d) % modulus, (a*d + b*c) % modulus)


def evaluate(pair, root, modulus):
    return (pair[0] + pair[1]*root) % modulus


def audit_prime(prime, max_depth, counts):
    levels = []
    roots_at = []
    for depth in range(max_depth + 1):
        modulus = prime**depth
        roots = square_roots_of_one(modulus)
        need(roots == character_values(modulus),
             f"root-character enumeration mismatch at {prime}^{depth}")
        counts['residue_candidates'] += modulus
        counts['root_character_bijections'] += len(roots)
        counts['character_group_law_pairs'] += 4*len(roots)
        expected = {1 % modulus, (-1) % modulus}
        if prime == 2 and depth >= 3:
            expected |= {(2**(depth-1)+1) % modulus,
                         (2**(depth-1)-1) % modulus}
        need(roots == sorted(expected), f"root benchmark mismatch at {prime}^{depth}")
        roots_at.append(roots)
        levels.append({'depth': depth, 'modulus': modulus, 'roots': roots})
        # All coefficients in small rings; a declared fixed probe set otherwise.
        probes = (tuple(itertools.product(range(modulus), repeat=2))
                  if modulus <= 16 else COEFFICIENT_PROBES)
        for root in roots:
            need(evaluate((0, 0), root, modulus) == 0, 'zero evaluation')
            need(evaluate((1, 0), root, modulus) == 1 % modulus, 'one evaluation')
            need(evaluate((0, 1), root, modulus) == root, 'generator evaluation')
            for left in probes:
                for right in probes:
                    need(evaluate(quotient_add(left, right, modulus), root, modulus)
                         == (evaluate(left, root, modulus)
                             + evaluate(right, root, modulus)) % modulus,
                         'quotient addition evaluation')
                    need(evaluate(quotient_mul(left, right, modulus), root, modulus)
                         == evaluate(left, root, modulus)
                         * evaluate(right, root, modulus) % modulus,
                         'quotient multiplication evaluation')
                    counts['quotient_evaluation_pairs'] += 1
        counts['levels'] += 1

    transitions = []
    for depth in range(max_depth):
        modulus = prime**depth
        children = {str(x): [y for y in roots_at[depth+1] if y % modulus == x]
                    for x in roots_at[depth]}
        # Independently enumerate every residue lift, not just known next roots.
        for root in roots_at[depth]:
            possible = [root + k*modulus for k in range(prime)]
            passing = [y for y in possible if (y*y-1) % (prime*modulus) == 0]
            need(children[str(root)] == passing, 'residue-lift enumeration mismatch')
            counts['tested_lift_candidates'] += len(possible)
            counts['reduction_edges'] += len(passing)
            if prime == 2 and depth >= 3:
                expected_liftable = {1 % modulus, (-1) % modulus}
                need(bool(passing) == (root in expected_liftable), 'extra-root persistence')
            elif prime != 2 and depth >= 1:
                need(len(passing) == 1, 'odd-prime root has unique next lift')
        transitions.append({'source_depth': depth, 'children': children})

    stable_to_terminal = []
    for depth in range(max_depth + 1):
        modulus = prime**depth
        direct = sorted({x % modulus for x in roots_at[-1]})
        # Backward pruning of the finite tree gives an independent computation.
        pruned = set(roots_at[-1])
        for step in range(max_depth-1, depth-1, -1):
            pruned = {x for x in roots_at[step]
                      if any(y % (prime**step) == x for y in pruned)}
        need(direct == sorted(pruned), 'finite stable-core computation mismatch')
        if prime == 2 and depth < max_depth:
            need(direct == sorted({1 % modulus, (-1) % modulus}),
                 'finite stable core benchmark')
        stable_to_terminal.append({'depth': depth, 'roots_reaching_terminal': direct})

    # Every reduction pair and every retained root: C2 values and ring-point
    # evaluations commute with coefficient reduction, including zero rings.
    for high in range(max_depth + 1):
        for low in range(high + 1):
            source_modulus, target_modulus = prime**high, prime**low
            for root in roots_at[high]:
                reduced = root % target_modulus
                need(reduced in roots_at[low], 'root reduction')
                for group_element in range(2):
                    source = (1 % source_modulus, root)[group_element]
                    target = (1 % target_modulus, reduced)[group_element]
                    need(source % target_modulus == target, 'character naturality')
                    counts['character_naturality_values'] += 1
                for pair in COEFFICIENT_PROBES:
                    need(evaluate(pair, root, source_modulus) % target_modulus
                         == evaluate(pair, reduced, target_modulus), 'ring-point naturality')
                    counts['ring_point_naturality_values'] += 1

    finite_branches = [[root % (prime**depth) for depth in range(max_depth+1)]
                       for root in roots_at[-1]]
    for branch in finite_branches:
        need(all(branch[d] in roots_at[d] for d in range(max_depth+1)),
             'branch has an inadmissible point')
        need(all(branch[d+1] % (prime**d) == branch[d] for d in range(max_depth)),
             'branch is incoherent')
    counts['finite_terminal_branches'] += len(finite_branches)
    return {'prime': prime, 'terminal_depth': max_depth, 'levels': levels,
            'transitions': transitions, 'finite_stable_cores': stable_to_terminal,
            'complete_branches_to_terminal_only': finite_branches}


def binary_mul(left, right, length):
    """F2[epsilon]/epsilon^length, encoded by coefficient bits."""
    out = 0
    for bit in range(length):
        if (right >> bit) & 1:
            out ^= left << bit
    return out & ((1 << length)-1)


def audit_nonreduced(counts):
    outputs = []
    root_tables = {}
    for length in range(2, 5):
        size = 1 << length
        roots = [x for x in range(size) if binary_mul(x, x, length) == 1]
        characters = []
        for x in range(size):
            is_unit = any(binary_mul(x, y, length) == 1 for y in range(size))
            if not is_unit:
                continue
            values = (1, x)
            if all(values[(a+b) % 2] == binary_mul(values[a], values[b], length)
                   for a in range(2) for b in range(2)):
                characters.append(x)
        need(characters == roots, 'nonreduced character bijection')
        need(len(roots) == 2**(length//2), 'nonreduced root benchmark')
        need(any(x != 1 for x in roots), 'nonreduced ring must have root beyond plus/minus one')
        root_tables[length] = roots
        counts['nonreduced_residue_candidates'] += size
        counts['nonreduced_root_character_bijections'] += len(roots)
        # Full ring coefficient domain, not a selected pair list.
        pairs = tuple(itertools.product(range(size), repeat=2))
        for root in roots:
            ev = lambda pair: pair[0] ^ binary_mul(pair[1], root, length)
            for left in pairs:
                for right in pairs:
                    a, b = left
                    c, d = right
                    product = (binary_mul(a, c, length) ^ binary_mul(b, d, length),
                               binary_mul(a, d, length) ^ binary_mul(b, c, length))
                    need(ev((a ^ c, b ^ d)) == (ev(left) ^ ev(right)),
                         'nonreduced addition evaluation')
                    need(ev(product) == binary_mul(ev(left), ev(right), length),
                         'nonreduced multiplication evaluation')
                    counts['nonreduced_quotient_evaluation_pairs'] += 1
        outputs.append({'epsilon_nilpotence': length, 'size': size,
                        'root_bit_vectors': roots, 'plus_minus_one_bit_vectors': [1]})
    for high in range(2, 5):
        for low in range(1, high+1):
            mask = (1 << low)-1
            target_roots = [x for x in range(1 << low) if binary_mul(x, x, low) == 1]
            for root in root_tables[high]:
                reduced = root & mask
                need(reduced in target_roots, 'nonreduced root reduction')
                for a in range(1 << high):
                    for b in range(1 << high):
                        need((a ^ binary_mul(b, root, high)) & mask
                             == (a & mask) ^ binary_mul(b & mask, reduced, low),
                             'nonreduced naturality')
                        counts['nonreduced_naturality_values'] += 1
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    counts = dict.fromkeys((
        'levels', 'residue_candidates', 'root_character_bijections',
        'character_group_law_pairs', 'quotient_evaluation_pairs',
        'tested_lift_candidates', 'reduction_edges', 'character_naturality_values',
        'ring_point_naturality_values', 'finite_terminal_branches',
        'nonreduced_residue_candidates', 'nonreduced_root_character_bijections',
        'nonreduced_quotient_evaluation_pairs', 'nonreduced_naturality_values'), 0)
    forests = [audit_prime(p, depth, counts) for p, depth in PRIME_DEPTHS]
    nonreduced = audit_nonreduced(counts)
    need(3 in square_roots_of_one(8), '3 modulo 8 is a root')
    need(all((x*x-1) % 16 != 0 for x in (3, 11)), '3 modulo 8 has no lift')
    need(1 % 2 == (-1) % 2 and 1 % 4 != (-1) % 4, 'packet collision and separation')
    result = {
        'schema_version': 1, 'status': 'PASS', 'arithmetic': 'exact integers only',
        'python_version': platform.python_version(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'bounds': {'prime_depths_inclusive': PRIME_DEPTHS,
                   'full_quotient_coefficients_when_modulus_at_most': 16,
                   'larger_modulus_coefficient_pairs': COEFFICIENT_PROBES,
                   'nonreduced_epsilon_lengths_inclusive': [2, 4]},
        'counts': counts, 'prime_power_forests': forests, 'nonreduced_rings': nonreduced,
        'boundaries': {
            'root_3_mod_8': {'lifts_mod_16': [3, 11], 'squares_mod_16': [9, 9],
                             'admissible_lifts': []},
            'plus_minus_packet_collision': {'mod_2': [1, 1], 'mod_4': [1, 3]},
            'warning': 'The finite forests classify branches only through their terminal depths.'},
        'non_claims': [
            'No universal proof or classification of infinite branches follows from this finite run.',
            'No Galois-group construction, arithmetic packet identification, or p-adic period comparison is executed here.',
            'No conclusion that roots are always plus/minus one in arbitrary commutative rings.',
            'No conclusion that every finite root extends to the next precision.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    need(json.loads(args.output.read_text())['counts'] == counts, 'result round trip')
    print(json.dumps({'status': 'PASS', 'counts': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
