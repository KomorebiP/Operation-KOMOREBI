from __future__ import annotations

import hashlib
import json
from itertools import product
import unittest

from matched_controls import (
    BUDGETS,
    ENDPOINT_NAMES,
    ENDPOINT_REPRESENTATIVE_WORDS,
    RELATION_WORDS,
    best_control,
    build_word_bank,
    endpoint_index,
    exposure_score,
    periodic_template,
    reference_word,
    word_features,
)


class D4EndpointTests(unittest.TestCase):
    def test_representatives_cover_d4(self) -> None:
        self.assertEqual(len(ENDPOINT_NAMES), 8)
        self.assertEqual(
            {endpoint_index(word) for word in ENDPOINT_REPRESENTATIVE_WORDS},
            set(range(8)),
        )

    def test_registered_repeated_relators_are_identity(self) -> None:
        for relation in RELATION_WORDS:
            for budget in BUDGETS:
                with self.subTest(relation=relation, budget=budget):
                    self.assertEqual(endpoint_index(reference_word(relation, budget)), 0)

    def test_length_parity_reaches_exactly_four_endpoints(self) -> None:
        even = {endpoint_index(word) for word in product((0, 1), repeat=6)}
        odd = {endpoint_index(word) for word in product((0, 1), repeat=7)}
        self.assertEqual(even, {0, 2, 5, 7})
        self.assertEqual(odd, {1, 3, 4, 6})
        self.assertTrue(even.isdisjoint(odd))
        self.assertEqual(even | odd, set(range(8)))


class FeatureTests(unittest.TestCase):
    def test_constant_and_alternating_run_moments_are_extremal(self) -> None:
        constant = word_features((0,) * 8)
        alternating = word_features((0, 1) * 4)
        self.assertEqual(constant.run_second_moment, 64)
        self.assertEqual(alternating.run_second_moment, 8)
        self.assertEqual(constant.directed_bigram_counts, (7, 0, 0, 0))
        self.assertEqual(alternating.directed_bigram_counts, (0, 4, 3, 0))

    def test_periodic_template_is_exact_prefix(self) -> None:
        self.assertEqual(periodic_template("frfr", 7), (1, 0, 1, 0, 1, 0, 1))
        self.assertEqual(periodic_template("r4", 5), (0, 0, 0, 0, 0))


class ExactOptimizerTests(unittest.TestCase):
    def _brute_best(self, reference: tuple[int, ...], endpoint: int) -> tuple[int, ...]:
        candidates = []
        reference_endpoint = endpoint_index(reference)
        for word in product((0, 1), repeat=len(reference)):
            if endpoint_index(word) != endpoint:
                continue
            if endpoint == reference_endpoint and word == reference:
                continue
            candidates.append((exposure_score(reference, word), word))
        if not candidates:
            raise ArithmeticError("brute-force fixture has no candidate")
        return min(candidates)[0]

    def test_dynamic_program_matches_exhaustive_constant_reference(self) -> None:
        reference = (0,) * 8
        for endpoint in (0, 2, 5, 7):
            with self.subTest(endpoint=endpoint):
                result = best_control(reference, endpoint)
                self.assertEqual(
                    tuple(result["matching"]["score"]),
                    self._brute_best(reference, endpoint),
                )

    def test_dynamic_program_matches_exhaustive_alternating_reference(self) -> None:
        reference = (1, 0) * 4
        for endpoint in (0, 2, 5, 7):
            with self.subTest(endpoint=endpoint):
                result = best_control(reference, endpoint)
                self.assertEqual(
                    tuple(result["matching"]["score"]),
                    self._brute_best(reference, endpoint),
                )

    def test_unreachable_exact_length_endpoint_is_rejected(self) -> None:
        with self.assertRaisesRegex(ArithmeticError, "unreachable"):
            best_control((0,) * 8, 1)

    def test_deterministic_replay(self) -> None:
        reference = (0, 1) * 8
        first = best_control(reference, 5)
        second = best_control(reference, 5)
        left = json.dumps(first, sort_keys=True, separators=(",", ":")).encode()
        right = json.dumps(second, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(left).digest(), hashlib.sha256(right).digest())


if __name__ == "__main__":
    unittest.main()
