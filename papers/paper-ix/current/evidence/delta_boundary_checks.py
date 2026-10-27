"""Independent exact, bounded checks of the final Euler mathematical delta.

The reciprocal is reconstructed from its defining triangular recurrence.
This does not prove a universal statement and imports no checkpoint engine.
"""
from fractions import Fraction
from itertools import product
from math import comb, factorial
from pathlib import Path
import json
import sys


def vp(value, prime=2):
    if value == 0:
        return float("inf")
    value = Fraction(value)
    numerator, denominator = abs(value.numerator), value.denominator
    exponent = 0
    while numerator % prime == 0:
        numerator //= prime
        exponent += 1
    while denominator % prime == 0:
        denominator //= prime
        exponent -= 1
    return exponent


def packet(width, address, last_row):
    values = [Fraction(1)]
    for row in range(1, last_row + 1):
        values.append(
            -sum(Fraction(comb(width * row + address, width * q)) * values[q]
                 for q in range(row))
            / comb(width * row + address, width * row)
        )
    return values


def mixed(values, row, steps):
    weights = {row: 1}
    for step in steps:
        updated = {}
        for index, weight in weights.items():
            updated[index] = updated.get(index, 0) - weight
            updated[index + step] = updated.get(index + step, 0) + weight
        weights = updated
    return sum(weight * values[index] for index, weight in weights.items())


def main():
    counts = dict(sharp_j01=0, mixed_parity_j01=0,
                  sharp_j2_power_orders=0, generic_prime_power=0,
                  root_source_units=0)
    values = [packet(4, j, 36) for j in range(4)]
    # Hand-computable definition checks, not included in the family counters.
    assert values[0][:2] == [1, -1]
    assert values[1][:3] == [1, Fraction(-1, 5), Fraction(121, 45)]
    assert values[2][:3] == [1, Fraction(-1, 15), Fraction(13, 45)]
    for j in (0, 1):
        for row in range(4):
            for order in range(1, 7):
                for step in range(1, 5):
                    exponent = order + vp(factorial(order)) + order * vp(step)
                    assert vp(mixed(values[j], row, [step] * order)) == exponent
                    counts["sharp_j01"] += 1
        for row in range(3):
            for order in range(1, 5):
                for steps in product(range(1, 4), repeat=order):
                    exponent = order + vp(factorial(order)) + sum(map(vp, steps))
                    observed = vp(mixed(values[j], row, steps))
                    exact = order % 2 == 1 or sum(h % 2 == 0 for h in steps) % 2 == 0
                    assert (observed == exponent) == exact
                    assert observed >= exponent + (not exact)
                    counts["mixed_parity_j01"] += 1
    for row in range(3):
        for order in (1, 2, 4, 8):
            for steps in product((1, 2), repeat=order):
                base = {1: 4, 2: 6}.get(order, 2 * order + vp(factorial(order)) + order // 2)
                exponent = base + sum(map(vp, steps))
                assert vp(mixed(values[2], row, steps)) == exponent
                counts["sharp_j2_power_orders"] += 1
    for prime, width in ((2, 1), (2, 2), (2, 4), (2, 8), (3, 3), (3, 9), (5, 5)):
        for address in range(width):
            source_values = packet(width, address, 12)
            signed = [(-1) ** row * value for row, value in enumerate(source_values)]
            for row in range(3):
                for steps in ((1,), (2,), (1, 2), (2, 2), (1, 1, 1)):
                    value = mixed(source_values if prime == 2 else signed, row, steps)
                    exponent = len(steps) + sum(vp(h, prime) for h in steps)
                    assert vp(value, prime) >= exponent
                    counts["generic_prime_power"] += 1
    for row in range(25):
        source = Fraction(3 ** (2 * row + 2) - 1, 4 * (2 * row + 1) * (2 * row + 2))
        assert vp(source) == 0
        counts["root_source_units"] += 1
    counter = mixed(values[0], 0, (1, 2))
    assert counter == -33728 and vp(counter) == 6
    result = {
        "status": "passed",
        "counts": counts,
        "family_assertions": sum(counts.values()),
        "additional_definition_checks": 3,
        "additional_cancellation_control": 1,
        "mixed_cancellation_example": {"value": str(counter), "valuation": vp(counter), "baseline": 4},
        "non_claim": "These finite cases do not prove any universal theorem and are not added to inherited checkpoint totals.",
    }
    output = Path(sys.argv[1])
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
