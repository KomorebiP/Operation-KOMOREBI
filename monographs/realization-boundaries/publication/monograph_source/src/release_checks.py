"""Final-release regression checks using exact finite arithmetic only.

Tests input contracts, canonical normal forms, and finite instances of diagonal
unit inversion. The printed proofs, not this suite, establish infinite claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import time

from dense_lift_groups import (
    DenseLiftGroup, Element, is_prime, normalize, prime, prime_divisors,
    prime_index, sparse_scale,
)


def diagonal_unit(group: DenseLiftGroup, scalar: Fraction, x: Element) -> Element:
    """Use rational reduction, replacing zero/undefined scalar residues by one."""
    if not scalar:
        raise ValueError("The scalar for a diagonal unit must be nonzero.")
    exceptional = set(prime_divisors(scalar.numerator)) | set(prime_divisors(scalar.denominator))
    target = scalar * x.rational
    support = (set(dict(x.torsion)) | exceptional
               | set(prime_divisors(x.rational.denominator))
               | set(prime_divisors(target.denominator)))
    correction: dict[int, int] = {}
    for p in support:
        multiplier = 1 if p in exceptional else scalar.numerator * pow(scalar.denominator, -1, p) % p
        correction[p] = (multiplier * group.coordinate(x, p)
                         - group.section_value(target, p)) % p
    return Element.make(target, correction)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('verification/release_checks.json'))
    args = parser.parse_args()
    started = time.monotonic()
    counts: Counter[str] = Counter()
    rejected: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        counts[name] += 1

    def rejects(name: str, action, expected: type[Exception]) -> None:
        try:
            action()
        except expected:
            rejected.append(name)
            counts['input_contract_rejections'] += 1
        else:
            raise AssertionError(f'{name}: expected {expected.__name__}')

    g = DenseLiftGroup(lambda n: False)
    u = Element.make(1)
    for value in (0.1, '1/2', True, None):
        rejects(f'rational_{type(value).__name__}', lambda v=value: Element.make(v), TypeError)
    for value in (1.9, Fraction(1, 2), '2', True):
        rejects(f'residue_{type(value).__name__}', lambda v=value: normalize({3: v}), TypeError)
    for value in (2.0, '2', True):
        rejects(f'prime_label_{type(value).__name__}', lambda v=value: normalize({v: 1}), TypeError)
    for value in (0, 1, 4, -3):
        rejects(f'composite_support_{value}', lambda v=value: normalize({v: 1}), ValueError)
    # Warm the caches first: invalid equal-valued inputs must not bypass validation.
    check(is_prime(2) and prime(1) == 3 and prime_index(2) == 0, 'prime_helpers')
    for name, fn, value in [('is_prime_float', is_prime, 2.0),
                            ('prime_float', prime, 1.0),
                            ('prime_index_float', prime_index, 2.0),
                            ('factor_float', prime_divisors, 6.0)]:
        rejects(name, lambda f=fn, v=value: f(v), TypeError)
    for value in (0, -1):
        rejects(f'root_nonpositive_{value}', lambda v=value: g.root(u, v), ValueError)
    for value in (1.5, Fraction(2), '2', True):
        rejects(f'root_noninteger_{type(value).__name__}', lambda v=value: g.root(u, v), TypeError)
        rejects(f'scale_noninteger_{type(value).__name__}', lambda v=value: g.scale(v, u), TypeError)
    rejects('noncallable_selector', lambda: DenseLiftGroup(7), TypeError)
    for value in (None, 2, 'false', 0.0):
        rejects(f'nonbit_selector_{type(value).__name__}_{value}',
                lambda v=value: DenseLiftGroup(lambda _: v).selected(2), TypeError)
    rejects('negative_changed_index', lambda: g.finite_change_transport(u, g, {-1}), ValueError)
    rejects('fractional_changed_index', lambda: g.finite_change_transport(u, g, {0.5}), TypeError)
    rejects('floating_section', lambda: g.section_value(0.5, 3), TypeError)
    rejects('floating_cocycle', lambda: g.cocycle(Fraction(1, 2), 0.5), TypeError)
    rejects('fractional_sparse_scalar', lambda: sparse_scale(1.5, ((3, 1),)), TypeError)
    check(Element(Fraction(2, 4), ((3, 2), (3, 2), (2, 2)))
          == Element.make(Fraction(1, 2), {3: 1}), 'direct_constructor_canonical')
    check(Element.make(0, [(3, 1), (3, -1)]) == Element.make(0), 'zero_coordinates_removed')
    check(g.scale(-3, u) == g.neg(g.scale(3, u)), 'negative_integer_scaling')
    check(g.root(u, 1).root == u, 'unit_root_multiplier')
    check(DenseLiftGroup(lambda _: 0).selected(2), 'integer_bit_zero')
    check(DenseLiftGroup(lambda _: 1).selected(3), 'integer_bit_one')

    rng = random.Random(20261023)
    ps = [prime(i) for i in range(18)]
    scalars = [Fraction(1), Fraction(-1), Fraction(2, 3), Fraction(-5, 2), Fraction(3, 7)]
    for mask in range(8):
        group = DenseLiftGroup(lambda n, m=mask: bool((m >> (n % 3)) & 1))
        for _ in range(25):
            x = Element.make(Fraction(rng.randint(-20, 20), rng.randint(1, 24)),
                             {p: rng.randrange(p) for p in rng.sample(ps, 3)})
            y = Element.make(Fraction(rng.randint(-20, 20), rng.randint(1, 24)),
                             {p: rng.randrange(p) for p in rng.sample(ps, 2)})
            for scalar in scalars:
                fx = diagonal_unit(group, scalar, x)
                fy = diagonal_unit(group, scalar, y)
                check(diagonal_unit(group, 1 / scalar, fx) == x, 'diagonal_unit_left_inverse')
                check(diagonal_unit(group, scalar, diagonal_unit(group, 1 / scalar, x)) == x,
                      'diagonal_unit_right_inverse')
                check(diagonal_unit(group, scalar, group.add(x, y)) == group.add(fx, fy),
                      'diagonal_unit_homomorphism')
                for p in ps:
                    exceptional = p in prime_divisors(scalar.numerator) or p in prime_divisors(scalar.denominator)
                    multiplier = 1 if exceptional else scalar.numerator * pow(scalar.denominator, -1, p) % p
                    check(group.coordinate(fx, p) == multiplier * group.coordinate(x, p) % p,
                          'diagonal_unit_coordinate_identity')
    # A zero diagonal coordinate kills a nonzero torsion vector, so it cannot be a unit.
    e2 = Element.make(0, {2: 1})
    check(e2 != Element.make() and g.scale(2, e2) == Element.make(), 'nonunit_kills_torsion_witness')
    report = {
        'status': 'PASS', 'scope': 'Input contracts and finite exact arithmetic only.',
        'random_seed': 20261023, 'assertions': dict(sorted(counts.items())),
        'total_assertions': sum(counts.values()), 'rejected_inputs': rejected,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(Path(__file__).parent.glob('*.py'))},
        'not_proved_by_tests': ['Universal completion reflection', 'Infinite classification',
                                'Oracle lower bounds', 'Lean verification'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
