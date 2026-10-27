"""Reproduce the independent review's bounded exact-arithmetic checks.

These checks validate conventions and small cases. They are not a proof of
Collatz, an exhaustive coverage audit, or a Lean replay.
"""

from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
import argparse
import json
import platform


def accelerated_step(n):
    value = 3 * n + 1
    valuation = 0
    while value % 2 == 0:
        valuation += 1
        value //= 2
    return value, valuation


def run_checks():
    cylinder_cases = 0
    word_count = 0
    for length in range(5):
        for word in product(range(1, 5), repeat=length):
            total = 0
            correction = 0
            for valuation in word:
                correction = 3 * correction + 2**total
                total += valuation
            modulus = 2 ** (total + 1)
            residue = (
                (2**total - correction) * pow(3**length, -1, modulus)
            ) % modulus
            assert residue % 2 == 1
            word_count += 1
            for progression_index in range(5):
                source = residue + progression_index * modulus
                current = source
                observed_word = []
                for _ in word:
                    current, valuation = accelerated_step(current)
                    observed_word.append(valuation)
                assert tuple(observed_word) == word
                assert 2**total * current == 3**length * source + correction
                assert (current < source) == (
                    (2**total - 3**length) * source > correction
                )
                cylinder_cases += 1

    density_cases = []
    for ell in range(1, 4):
        for deficit_bound in range(3):
            length = 5 * ell
            threshold = 8 * ell + deficit_bound + 1
            density = sum(
                (
                    Fraction(comb(total - 1, length - 1), 2 ** (total + 1))
                    for total in range(length, threshold + 1)
                ),
                Fraction(),
            )
            upper_bound = (
                Fraction(1, 2)
                * Fraction(4, 3) ** (deficit_bound + 1)
                * Fraction(65536, 84375) ** ell
            )
            assert density <= upper_bound
            density_cases.append(
                {
                    "ell": ell,
                    "D": deficit_bound,
                    "word_length": length,
                    "valuation_sum_upper_bound": threshold,
                    "exact_all_integer_density": str(density),
                    "rational_density_majorant": str(upper_bound),
                    "passed": True,
                }
            )

    witness_prefix_cases = 0
    for horizon in range(101):
        source = 2 ** (horizon + 2) - 1
        current = source
        for prefix_length in range(horizon + 1):
            assert current == 3**prefix_length * 2 ** (
                horizon + 2 - prefix_length
            ) - 1
            assert current >= source
            current, _ = accelerated_step(current)
            witness_prefix_cases += 1

    current = 27
    total = 0
    correction = 0
    orbit_rows = []
    for step in range(1, 38):
        current, valuation = accelerated_step(current)
        correction = 3 * correction + 2**total
        total += valuation
        assert 2**total * current == 3**step * 27 + correction
        if step < 37:
            assert current >= 27
        orbit_rows.append([step, current, valuation, total, correction])
    assert orbit_rows[-1] == [37, 23, 3, 59, 1100931843921811423]
    assert orbit_rows[:10] == [
        [1, 41, 1, 1, 1],
        [2, 31, 2, 3, 5],
        [3, 47, 1, 4, 23],
        [4, 71, 1, 5, 85],
        [5, 107, 1, 6, 287],
        [6, 161, 1, 7, 925],
        [7, 121, 2, 9, 2903],
        [8, 91, 2, 11, 9221],
        [9, 137, 1, 12, 29711],
        [10, 103, 2, 14, 93229],
    ]

    return {
        "status": "passed",
        "arithmetic": "Python exact integers and fractions",
        "python_version": platform.python_version(),
        "cylinder_identity_descent": {
            "word_lengths": [0, 1, 2, 3, 4],
            "valuation_alphabet": [1, 2, 3, 4],
            "progression_indices": [0, 1, 2, 3, 4],
            "words": word_count,
            "instances": cylinder_cases,
            "passed": True,
        },
        "rare_word_density": density_cases,
        "fixed_horizon_witness": {
            "horizons": [0, 100],
            "prefix_instances": witness_prefix_cases,
            "passed": True,
        },
        "orbit_27": {
            "first_actual_descent_step": 37,
            "endpoint": 23,
            "last_valuation": 3,
            "shortcut_steps": 59,
            "offset": 1100931843921811423,
            "first_ten_rows": orbit_rows[:10],
            "passed": True,
        },
        "resolved_check_failure": (
            "An initial ad hoc reviewer assertion guessed the final valuation "
            "at step 37 as 4. The actual exact valuation is 3. The manuscript "
            "did not assert the guessed value, and all its displayed data "
            "passed after the reviewer expectation was corrected."
        ),
        "scope": [
            "Bounded checks of formulas and conventions only.",
            "Not a proof of universal Collatz descent or of RH.",
            "Not a full residue certificate coverage audit.",
            "No Lean compilation or historical verification replay.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("review_check_results.json"),
    )
    args = parser.parse_args()
    results = run_checks()
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(
        "PASS: 1705 cylinder/identity/descent cases, "
        "9 exact density bounds, 5151 fixed-horizon prefix cases, "
        "and the 27 first-descent table."
    )


if __name__ == "__main__":
    main()
