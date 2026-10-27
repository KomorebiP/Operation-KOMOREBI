from __future__ import annotations

import unittest

from arithmetic_space_lab.paired_stats import (
    mcnemar_exact_two_sided,
    paired_exact_group,
)


class PairedStatisticsTests(unittest.TestCase):
    def test_mcnemar_exact_known_small_case(self) -> None:
        self.assertEqual(mcnemar_exact_two_sided(0, 0), 1.0)
        self.assertAlmostEqual(mcnemar_exact_two_sided(4, 0), 0.125)
        self.assertAlmostEqual(
            mcnemar_exact_two_sided(0, 4),
            mcnemar_exact_two_sided(4, 0),
        )

    def test_paired_group_counts_discordant_outcomes(self) -> None:
        outcomes = [(True, True), (True, False), (True, False), (False, True), (False, False)]
        pairs = [
            (
                {"answer_exact_match": correct},
                {"answer_exact_match": shuffled},
            )
            for correct, shuffled in outcomes
        ]
        report = paired_exact_group(pairs)
        self.assertEqual(report["examples"], 5)
        self.assertEqual(report["correct_exact_count"], 3)
        self.assertEqual(report["shuffled_exact_count"], 2)
        self.assertEqual(report["correct_only"], 2)
        self.assertEqual(report["shuffled_only"], 1)
        self.assertEqual(report["both_correct"], 1)
        self.assertEqual(report["both_incorrect"], 1)
        self.assertAlmostEqual(report["rate_difference"], 0.2)


if __name__ == "__main__":
    unittest.main()
