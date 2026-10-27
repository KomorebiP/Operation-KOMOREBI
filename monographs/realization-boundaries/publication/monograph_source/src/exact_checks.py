"""Reproducible finite tests. None certify the infinite classification theorem."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import time

from dense_lift_groups import (DenseLiftGroup, Element, element_json, prime,
                              prime_divisors, normalize, sparse_add, sparse_scale)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("verification/current_checks.json"))
    args = parser.parse_args()
    counts: Counter[str] = Counter()
    started = time.time()
    rng = random.Random(20261022)

    def check(condition: bool, section: str, message: str = "") -> None:
        if not condition:
            raise AssertionError(f"{section}: {message}")
        counts[section] += 1

    masks = [DenseLiftGroup(lambda n, mask=mask: bool((mask >> (n % 3)) & 1))
             for mask in range(8)]
    rationals = [Fraction(0), Fraction(1), Fraction(-1), Fraction(1, 2),
                 Fraction(-1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(1, 5),
                 Fraction(4, 5), Fraction(1, 7), Fraction(1, 6), Fraction(-5, 6)]
    ps = [prime(i) for i in range(16)]
    zero = Element.make()

    # Exhaustive cocycle laws on this finite rational test set.
    for group in masks:
        for r, s in product(rationals, repeat=2):
            c = group.cocycle(r, s)
            check(c == group.cocycle(s, r), "cocycle_symmetry")
            allowed = set(prime_divisors(r.denominator * s.denominator))
            check(set(dict(c)) <= allowed, "cocycle_finite_support")
            for p in ps:
                expected = (group.section_value(r, p) + group.section_value(s, p)
                            - group.section_value(r+s, p)) % p
                check(dict(c).get(p, 0) == expected, "cocycle_coordinate_identity")
        for r, s, t in product(rationals, repeat=3):
            left = sparse_add(group.cocycle(r, s), group.cocycle(r+s, t))
            right = sparse_add(group.cocycle(s, t), group.cocycle(r, s+t))
            check(left == right, "cocycle_associativity")

    def random_element() -> Element:
        r = Fraction(rng.randint(-15, 15), rng.randint(1, 30))
        d = {p: rng.randrange(p) for p in rng.sample(ps, rng.randrange(5))}
        return Element.make(r, d)

    for group in masks:
        u = Element.make(1)
        for n in range(20):
            pe, po = prime(2*n), prime(2*n+1)
            e, o = group.root(u, pe), group.root(u, po)
            check((e.root is not None) == bool(group.bit(n)), "marked_bit_decode")
            check((o.root is not None) != bool(group.bit(n)), "marked_bit_decode")
            check((e.root is None) != (o.root is None), "exactly_one_root")
            if e.root is not None:
                check(group.scale(pe, e.root) == u, "marked_root_witness")
            if o.root is not None:
                check(group.scale(po, o.root) == u, "marked_root_witness")
        for _ in range(120):
            x, y, z = random_element(), random_element(), random_element()
            check(group.add(group.add(x, y), z) == group.add(x, group.add(y, z)),
                  "group_associativity")
            check(group.add(x, y) == group.add(y, x), "group_commutativity")
            check(group.add(x, zero) == x, "group_identity")
            check(group.add(x, group.neg(x)) == zero, "group_inverse")
            for p in ps:
                check(group.coordinate(group.add(x, y), p)
                      == (group.coordinate(x, p) + group.coordinate(y, p)) % p,
                      "ambient_coordinate_homomorphism")
            for m in (1, 2, 3, 4, 5, 6, 10, 12, 18, 30):
                res = group.root(x, m)
                obstruction = [p for p in prime_divisors(m) if group.coordinate(x, p)]
                check((res.root is None) == bool(obstruction), "integer_root_criterion")
                if res.root is not None:
                    check(group.scale(m, res.root) == x, "integer_root_witness")
                else:
                    check(res.obstructing_prime in obstruction, "integer_root_obstruction")
                representative = Element.make(0, {p: group.coordinate(x, p)
                                                   for p in prime_divisors(m)})
                difference = group.sub(x, representative)
                root = group.root(difference, m).root
                check(root is not None and group.scale(m, root) == difference,
                      "quotient_kernel_and_surjectivity")
            # A non-torsion element's signature agrees with A outside explicitly
            # bounded numerator, denominator, and finite-support exceptions.
            if x.rational:
                bad = (set(prime_divisors(x.rational.numerator))
                       | set(prime_divisors(x.rational.denominator))
                       | set(dict(x.torsion)))
                for n in range(18):
                    pe, po = prime(2*n), prime(2*n+1)
                    if pe in bad or po in bad:
                        continue
                    check((group.root(x, pe).root is not None) == bool(group.bit(n)),
                          "unmarked_signature_outside_finite_exceptions")
                    check((group.root(x, po).root is not None) != bool(group.bit(n)),
                          "unmarked_signature_outside_finite_exceptions")

    # Finite alterations must yield the SAME embedded group, not new iso types.
    changes = {0, 3, 7}
    first = DenseLiftGroup(lambda n: bool(n % 2))
    second = DenseLiftGroup(lambda n: bool(n % 2) ^ (n in changes))
    for _ in range(200):
        x, y = random_element(), random_element()
        fx = first.finite_change_transport(x, second, changes)
        fy = first.finite_change_transport(y, second, changes)
        fxy = first.finite_change_transport(first.add(x, y), second, changes)
        check(fxy == second.add(fx, fy), "finite_alteration_transport_homomorphism")
        check(second.finite_change_transport(fx, first, changes) == x,
              "finite_alteration_transport_inverse")
        for p in ps:
            check(first.coordinate(x, p) == second.coordinate(fx, p),
                  "finite_alteration_same_ambient_element")

    # Deliberately false simplifications, each rejected for its intended reason.
    controls: dict[str, bool] = {}
    g0, g1 = DenseLiftGroup(lambda n: False), DenseLiftGroup(lambda n: True)
    u = Element.make(1)
    half = Element.make(Fraction(1, 2))
    controls["naive_direct_product_addition_rejected"] = g0.add(half, half) != u
    controls["false_two_divisibility_rejected"] = g0.root(u, 2).obstructing_prime == 2
    controls["unadjusted_finite_change_coordinates_rejected"] = (
        g0.add(half, half) != g1.add(half, half))
    torsion = Element.make(0, {3: 1})
    controls["zero_torsion_root_correction_rejected"] = (
        g0.root(torsion, 2).root is not None and g0.scale(2, zero) != torsion)
    # Test the false C_4 quotient claim on mixed rational/torsion samples.
    # Group differences are tested by the explicit integer-root construction.
    candidates = [Element.make(Fraction(j, 2), {2: k})
                  for j in range(-2, 3) for k in range(2)]
    representatives = []
    for x in candidates:
        if not any(g0.root(g0.sub(x, y), 4).root is not None
                   for y in representatives):
            representatives.append(x)
    controls["prime_power_quotient_order_overclaim_rejected"] = (
        len(representatives) == 2 and len(representatives) != 4
        and all((g0.root(g0.sub(x, y), 2).root is not None)
                == (g0.root(g0.sub(x, y), 4).root is not None)
                for x, y in product(candidates, repeat=2)))
    try:
        g0.root(u, 0)
    except ValueError:
        controls["zero_multiplier_rejected"] = True
    else:
        controls["zero_multiplier_rejected"] = False
    for name, result in controls.items():
        check(result, "negative_controls", name)

    # Direct extraction of a selector bit from the exact canonical cocycle.
    for group in masks:
        for i in range(24):
            p = prime(i)
            c = group.cocycle(Fraction(1, p), Fraction(p-1, p))
            expected = normalize({p: -int(group.selected(p))})
            check(c == expected, "canonical_cocycle_bit_extraction")

    script_dir = Path(__file__).resolve().parent
    report = {
        "status": "PASS",
        "test_scope": "Finite exact arithmetic only; universal theorems have written proofs, not machine-checked proofs.",
        "python": platform.python_version(),
        "random_seed": 20261022,
        "assertions": dict(sorted(counts.items())),
        "total_assertions": sum(counts.values()),
        "negative_controls": controls,
        "elapsed_seconds": round(time.time()-started, 3),
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(script_dir.glob('*.py'))},
        "example": {
            "twice_half_A_empty": element_json(g0.scale(2, half)),
            "two_root_of_u_exists": False,
            "three_root_of_u": element_json(g0.root(u, 3).root)
        },
        "not_tested": ["Noncomputable masks", "All infinite groups", "Historical originality",
                       "Lean kernel verification", "Independent external review"]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
