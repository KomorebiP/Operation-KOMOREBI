#!/usr/bin/env python3
"""Transparent structural tests for the shared v0.3.1 engine.

Author: Komorebi P.
"""

from __future__ import annotations

import unittest

import numpy as np

import v031_engine as engine


def permutation_matrix(mapping: np.ndarray) -> np.ndarray:
    matrix = np.zeros((8, 8), dtype=np.float64)
    matrix[mapping, np.arange(8)] = 1.0
    return matrix


class ExactD4EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rotation = np.array(
            [4 * (index // 4) + ((index % 4 + 1) % 4) for index in range(8)],
            dtype=np.int64,
        )
        reflection = np.array(
            [4 * (1 - index // 4) + ((-(index % 4)) % 4) for index in range(8)],
            dtype=np.int64,
        )
        cls.maps = np.stack((rotation, reflection))
        cls.codes = np.stack(
            (permutation_matrix(rotation), permutation_matrix(reflection))
        )
        cls.decoder = np.eye(8, dtype=np.float64)
        cls.anchors = np.eye(8, dtype=np.float64)
        cls.bank = engine.build_suffix_facet_bank(
            cls.codes, cls.maps, cls.decoder, 8
        )

    def test_suffix_bank_has_exact_registered_count_and_order(self) -> None:
        self.assertEqual(len(self.bank.words), 511)
        self.assertEqual(self.bank.words[0], ())
        self.assertEqual(self.bank.words[1:3], ((0,), (1,)))
        self.assertEqual(self.bank.words[3:7], ((0, 0), (0, 1), (1, 0), (1, 1)))
        self.assertGreater(self.bank.minimum_pulled_back_facet_norm, 0.0)

    def test_exact_representation_survives_and_recursion_agrees(self) -> None:
        result = engine.audit_states(
            self.bank,
            self.codes,
            self.maps,
            self.decoder,
            self.anchors,
            np.arange(8, dtype=np.int64),
        )
        self.assertTrue(result.summary["all_cases_survive"])
        self.assertEqual(result.summary["decision_count"], 8 * 511)
        recursion = result.summary["recursive_suffix_consistency"]
        self.assertTrue(recursion["passed"])
        self.assertIn("one-generator descendant traversal", recursion["method"])
        self.assertEqual(
            recursion["total_word_membership_mismatch_count_across_horizons"],
            0,
        )
        self.assertEqual(
            recursion["total_root_safe_mismatch_count_across_horizons"],
            0,
        )
        self.assertTrue(
            all(
                record[
                    "direct_full_word_and_one_step_membership_equal"
                ]
                for record in recursion["horizons"]
            )
        )
        self.assertAlmostEqual(
            result.summary["minimum_angular_clearance"],
            1.0 / np.sqrt(2.0),
        )

    def test_recursive_check_rejects_a_corrupted_direct_word_audit(self) -> None:
        result = engine.audit_states(
            self.bank,
            self.codes,
            self.maps,
            self.decoder,
            self.anchors,
            np.arange(8, dtype=np.int64),
        )
        direct = result.angular_clearances > 0.0
        corrupted = direct.copy()
        corrupted[0, 1] = False  # Case zero, one-step R descendant.
        recursion = engine.recursive_suffix_consistency(
            corrupted,
            self.codes,
            self.maps,
            self.decoder,
            self.anchors,
            np.arange(8, dtype=np.int64),
            8,
        )
        self.assertFalse(recursion["passed"])
        horizon_one = recursion["horizons"][1]
        self.assertEqual(horizon_one["word_membership_mismatch_count"], 1)
        self.assertEqual(horizon_one["root_safe_mismatch_count"], 1)
        self.assertFalse(horizon_one["direct_and_recursive_safe_equal"])

    def test_recursive_fold_includes_one_step_descendant_failures(self) -> None:
        codes = self.codes.copy()
        codes[0] = np.eye(8, dtype=np.float64)
        bank = engine.build_suffix_facet_bank(codes, self.maps, self.decoder, 2)
        result = engine.audit_states(
            bank,
            codes,
            self.maps,
            self.decoder,
            self.anchors,
            np.arange(8, dtype=np.int64),
        )
        recursion = result.summary["recursive_suffix_consistency"]
        self.assertTrue(recursion["passed"])
        self.assertEqual(recursion["horizons"][0]["direct_safe_case_count"], 8)
        self.assertEqual(recursion["horizons"][0]["recursive_safe_case_count"], 8)
        self.assertEqual(recursion["horizons"][1]["direct_safe_case_count"], 0)
        self.assertEqual(recursion["horizons"][1]["recursive_safe_case_count"], 0)

    def test_horizon_summary_uses_exact_cumulative_suffix_count(self) -> None:
        result = engine.audit_states(
            self.bank,
            self.codes,
            self.maps,
            self.decoder,
            self.anchors,
            np.arange(8, dtype=np.int64),
        )
        for horizon in range(9):
            summary = engine.summarize_audit_horizon(
                result, self.bank, horizon
            )
            self.assertEqual(summary["suffix_count_per_case"], 2 ** (horizon + 1) - 1)
            self.assertEqual(summary["safe_case_count"], 8)

    def test_wrong_state_reveals_against_baseline_at_empty_suffix(self) -> None:
        wrong = np.roll(self.anchors, 1, axis=0)
        result = engine.audit_states(
            self.bank,
            self.codes,
            self.maps,
            self.decoder,
            wrong,
            np.arange(8, dtype=np.int64),
            baseline_states=self.anchors,
        )
        self.assertEqual(result.summary["failure_case_count"], 8)
        self.assertEqual(result.summary["reveal_case_count"], 8)
        self.assertEqual(result.summary["first_failure_histogram"]["0"], 8)
        self.assertEqual(result.summary["first_reveal_histogram"]["0"], 8)

    def test_history_levels_are_start_major_and_binary_lexical(self) -> None:
        states, labels = engine.build_history_levels(
            self.codes, self.maps, self.anchors, 8
        )
        self.assertEqual([row.shape[0] for row in states], [8 * 2**d for d in range(9)])
        # For visible start zero, exact depth two is 00, 01, 10, 11.
        expected = []
        for word in ((0, 0), (0, 1), (1, 0), (1, 1)):
            current = 0
            for token in word:
                current = int(self.maps[token, current])
            expected.append(current)
        np.testing.assert_array_equal(labels[2][:4], expected)

    def test_history_locator_round_trip(self) -> None:
        locators = engine.history_case_locators(3)
        self.assertEqual(len(locators), 8 * 8)
        self.assertEqual(locators[0]["history"], [0, 0, 0])
        self.assertEqual(locators[7]["history"], [1, 1, 1])
        self.assertEqual(locators[8]["start"], 1)

    def test_vanishing_decoder_facet_fails_closed(self) -> None:
        decoder = self.decoder.copy()
        decoder[1] = decoder[0]
        with self.assertRaises(engine.NumericalRayError):
            engine.build_suffix_facet_bank(self.codes, self.maps, decoder, 2)

    def test_fractional_semantic_labels_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            engine.audit_states(
                self.bank,
                self.codes,
                self.maps,
                self.decoder,
                self.anchors,
                np.arange(8, dtype=np.float64),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
