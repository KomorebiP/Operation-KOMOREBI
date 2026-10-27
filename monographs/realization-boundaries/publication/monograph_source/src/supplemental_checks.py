"""Exact checks for monograph additions. These are finite implementation tests.

No finite test is represented as a proof of a universal group classification.
Uses Python 3.10+ and the standard library only.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import random
import time

from dense_lift_groups import DenseLiftGroup, Element, prime, prime_divisors


def rational_multiplier(group: DenseLiftGroup, c: Fraction, x: Element) -> Element:
    """Diagonal multiplication by c mod p, with 0 at denominator primes.

    This is a particular endomorphism, not a homomorphic embedding of Q into
    the endomorphism ring: exceptional coordinates matter in compositions.
    """
    c = Fraction(c)
    target = c * x.rational
    support = (set(dict(x.torsion))
               | set(prime_divisors(c.denominator))
               | set(prime_divisors(x.rational.denominator))
               | set(prime_divisors(target.denominator)))
    correction: dict[int, int] = {}
    for p in support:
        scalar = 0 if c.denominator % p == 0 else c.numerator * pow(c.denominator, -1, p) % p
        correction[p] = (scalar * group.coordinate(x, p)
                         - group.section_value(target, p)) % p
    return Element.make(target, correction)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('verification/supplemental_checks.json'))
    args = parser.parse_args()
    counts: Counter[str] = Counter()
    rng = random.Random(20261023)
    started = time.time()

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        counts[label] += 1

    groups = [DenseLiftGroup(lambda n, mask=mask: bool((mask >> (n % 3)) & 1))
              for mask in range(8)]
    ps = [prime(i) for i in range(16)]
    zero = Element.make()

    for group in groups:
        for _ in range(30):
            x = Element.make(Fraction(rng.randint(-10, 10), rng.randint(1, 15)),
                             {p: rng.randrange(p) for p in rng.sample(ps, 3)})
            y = Element.make(Fraction(rng.randint(-10, 10), rng.randint(1, 15)),
                             {p: rng.randrange(p) for p in rng.sample(ps, 2)})
            for c in (Fraction(0), Fraction(1), Fraction(-2), Fraction(1, 2),
                      Fraction(3, 5), Fraction(-5, 6)):
                fx, fy = rational_multiplier(group, c, x), rational_multiplier(group, c, y)
                check(rational_multiplier(group, c, group.add(x, y)) == group.add(fx, fy),
                      'rational_diagonal_endomorphism_addition')
                check(fx.rational == c*x.rational, 'rational_quotient_scalar')
                for p in ps:
                    scalar = 0 if c.denominator % p == 0 else c.numerator*pow(c.denominator, -1, p) % p
                    check(group.coordinate(fx, p) == scalar*group.coordinate(x, p) % p,
                          'diagonal_coordinate_formula')
            for m in (1, 2, 3, 4, 6, 12, 30):
                target = group.scale(m, x)
                base = group.root(target, m).root
                check(base is not None, 'constructed_target_has_root')
                assert base is not None
                factors = prime_divisors(m)
                roots = set()
                for residues in product(*(range(p) for p in factors)):
                    k = Element.make(0, dict(zip(factors, residues)))
                    check(group.scale(m, k) == zero, 'root_kernel_elements')
                    candidate = group.add(base, k)
                    check(group.scale(m, candidate) == target, 'root_fiber_witnesses')
                    roots.add(candidate)
                radical = 1
                for p in factors:
                    radical *= p
                check(len(roots) == radical, 'root_fiber_cardinality')

    G = DenseLiftGroup(lambda n: False)
    g = Element.make(1, {2: 1})
    check(G.scale(6, Element.make(Fraction(1, 6))) == g, 'worked_six_root')
    check(G.scale(2, Element.make(0, {3: 2})) == Element.make(0, {3: 1}), 'worked_torsion_root')
    H = DenseLiftGroup(lambda n: n == 0)
    half = Element.make(Fraction(1, 2))
    check(G.finite_change_transport(half, H, {0}) == Element.make(Fraction(1, 2), {3: 1}),
          'worked_half_transport')

    # A rational choice of representatives need not preserve multiplication
    # as a section Q -> End(G). At prime 2, the chosen inverse of 2 is zero.
    e2 = Element.make(0, {2: 1})
    two_then_half = rational_multiplier(G, Fraction(1, 2), rational_multiplier(G, Fraction(2), e2))
    check(two_then_half != e2, 'reject_rational_section_as_ring_embedding')

    report = {
        'status': 'PASS',
        'scope': 'Finite exact arithmetic only. Universal claims have printed proofs.',
        'random_seed': 20261023,
        'assertions': dict(sorted(counts.items())),
        'total_assertions': sum(counts.values()),
        'elapsed_seconds': round(time.time()-started, 3),
        'negative_controls': {'rational_section_is_not_a_ring_embedding': True},
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'not_tested': ['Noncomputable selectors', 'All infinite groups', 'Lean proof terms', 'Historical priority']
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
