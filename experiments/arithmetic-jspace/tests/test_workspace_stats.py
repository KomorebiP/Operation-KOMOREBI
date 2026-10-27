from __future__ import annotations

import json
import unittest

from arithmetic_space_lab.workspace_stats import (
    benjamini_hochberg,
    effect_decision,
    equivalence_decision,
    evaluate_claim_ladder,
    exact_paired_permutation,
    exact_paired_sign_flip,
    hierarchical_bootstrap,
    holm_correction,
    multiplicity_report,
    wilson_interval,
)


class WorkspaceStatisticsTests(unittest.TestCase):
    def test_wilson_interval_and_empty_report(self) -> None:
        report = wilson_interval(5, 10)
        self.assertTrue(report["valid"])
        self.assertAlmostEqual(report["rate"], 0.5)
        self.assertAlmostEqual(report["lower"], 0.2365930905, places=8)
        self.assertAlmostEqual(report["upper"], 0.7634069095, places=8)
        empty = wilson_interval(0, 0)
        self.assertFalse(empty["valid"])
        self.assertIsNone(empty["lower"])
        with self.assertRaises(ValueError):
            wilson_interval(4, 3)

    def test_exact_seed_sign_flip(self) -> None:
        one_sided = exact_paired_sign_flip(
            {"seed3": 1.0, "seed1": 1.0, "seed2": 1.0},
            alternative="greater",
        )
        self.assertEqual(one_sided["assignments_enumerated"], 8)
        self.assertEqual(one_sided["extreme_assignments"], 1)
        self.assertAlmostEqual(one_sided["p_value"], 0.125)
        two_sided = exact_paired_sign_flip(
            {"seed1": 1.0, "seed2": 1.0, "seed3": 1.0}
        )
        self.assertAlmostEqual(two_sided["p_value"], 0.25)
        self.assertFalse(exact_paired_sign_flip({})["valid"])

    def test_exact_paired_permutation_builds_seed_effects(self) -> None:
        report = exact_paired_permutation(
            {
                "a": {"candidate": 0.7, "control": 0.2},
                "b": [0.8, 0.3],
                "c": {"candidate": 0.6, "control": 0.1},
            },
            alternative="greater",
        )
        self.assertAlmostEqual(report["mean_effect"], 0.5)
        self.assertEqual(report["seed_count"], 3)
        self.assertAlmostEqual(report["p_value"], 0.125)

    def test_hierarchical_bootstrap_is_deterministic_and_json_safe(self) -> None:
        outcomes = {
            "seed2": {"family_b": [1.0, 1.0], "family_a": [1.0]},
            "seed1": {"family_b": [1.0], "family_a": [1.0, 1.0]},
        }
        first = hierarchical_bootstrap(
            outcomes,
            replicates=200,
            random_seed=771,
            include_samples=True,
        )
        second = hierarchical_bootstrap(
            dict(reversed(list(outcomes.items()))),
            replicates=200,
            random_seed=771,
            include_samples=True,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["estimate"], 1.0)
        self.assertEqual(first["lower"], 1.0)
        self.assertEqual(first["upper"], 1.0)
        json.dumps(first, allow_nan=False)

    def test_hierarchical_bootstrap_accepts_item_records(self) -> None:
        report = hierarchical_bootstrap(
            {
                "s1": [
                    {"family_id": "a", "effect": 0.0},
                    {"family_id": "a", "effect": 1.0},
                    {"family_id": "b", "effect": 1.0},
                ],
                "s2": [
                    {"family_id": "a", "effect": 0.5},
                    {"family_id": "b", "effect": 0.5},
                ],
            },
            replicates=300,
            random_seed=42,
        )
        self.assertTrue(report["valid"])
        # s1 = mean(0.5, 1.0) = .75; s2 = .5; equal-seed estimate = .625.
        self.assertAlmostEqual(report["estimate"], 0.625)
        self.assertEqual(report["seed_count"], 2)
        self.assertEqual(report["family_count"], 4)
        self.assertEqual(report["item_count"], 5)

    def test_multiple_comparison_corrections(self) -> None:
        p_values = {"a": 0.01, "b": 0.03, "c": 0.04}
        holm = holm_correction(p_values)
        self.assertAlmostEqual(holm["results"]["a"]["adjusted_p"], 0.03)
        self.assertAlmostEqual(holm["results"]["b"]["adjusted_p"], 0.06)
        self.assertAlmostEqual(holm["results"]["c"]["adjusted_p"], 0.06)
        bh = benjamini_hochberg(p_values)
        self.assertAlmostEqual(bh["results"]["a"]["adjusted_p"], 0.03)
        self.assertAlmostEqual(bh["results"]["b"]["adjusted_p"], 0.04)
        self.assertAlmostEqual(bh["results"]["c"]["adjusted_p"], 0.04)
        combined = multiplicity_report({"primary": 0.01}, {"secondary": 0.2})
        self.assertEqual(combined["primary"]["method"], "holm")
        self.assertEqual(combined["secondary"]["method"], "benjamini_hochberg")
        json.dumps(combined, allow_nan=False)

    def test_effect_and_equivalence_decisions_fail_closed(self) -> None:
        effect = effect_decision(
            {"estimate": 0.25, "lower": 0.11, "upper": 0.38},
            minimum_effect=0.1,
        )
        self.assertTrue(effect["passed"])
        not_effect = effect_decision(
            {"estimate": 0.15, "lower": 0.09, "upper": 0.3},
            minimum_effect=0.1,
        )
        self.assertFalse(not_effect["passed"])
        equivalent = equivalence_decision(
            {"estimate": 0.01, "lower": -0.03, "upper": 0.04},
            margin=0.05,
        )
        self.assertTrue(equivalent["passed"])
        self.assertFalse(equivalence_decision({}, margin=0.05)["passed"])

    @staticmethod
    def _complete_evidence() -> dict[str, object]:
        return {
            "validity": {"passed": True},
            "competence": {"passed": True},
            "compact_representation": {"passed": True},
            "causal_necessity": {
                "candidate_vs_random": {"passed": True},
                "candidate_vs_pca": {"passed": True},
            },
            "directional_patch": {"passed": True},
            "rescue": {"passed": True},
            "mediation": {"passed": True},
            "multiple_consumers": {"passed": True, "consumer_count": 3},
            "arithmetic_vs_pseudo": {"passed": True},
            "confirmation": {
                "passed": True,
                "independent": True,
                "confirmatory_seed_ids": [2001, 2002, 2003],
            },
        }

    def test_claim_ladder_passes_only_complete_confirmatory_evidence(self) -> None:
        report = evaluate_claim_ladder(self._complete_evidence())
        self.assertTrue(report["established"])
        self.assertEqual(
            report["claim_status"], "ARITHMETIC_JSPACE_EQUIVALENT_SUPPORTED"
        )
        self.assertEqual(report["missing"], [])
        self.assertEqual(
            report["highest_rung"], "arithmetic_selective_independently_confirmed"
        )
        json.dumps(report, allow_nan=False)

    def test_claim_ladder_missing_or_nonindependent_data_fails_closed(self) -> None:
        incomplete = evaluate_claim_ladder({"validity": {"passed": True}})
        self.assertFalse(incomplete["established"])
        self.assertIn("competence", incomplete["missing"])

        evidence = self._complete_evidence()
        evidence["confirmation"] = {
            "passed": True,
            "independent": True,
            "confirmatory_seed_ids": [2001, 2001, 2002],
        }
        duplicate_seed_report = evaluate_claim_ladder(evidence)
        self.assertFalse(duplicate_seed_report["established"])
        self.assertFalse(
            duplicate_seed_report["checks"]["independent_confirmation"]["passed"]
        )

        evidence = self._complete_evidence()
        evidence["causal_necessity"]["candidate_vs_pca"] = {"passed": False}
        pca_failed = evaluate_claim_ladder(evidence)
        self.assertFalse(pca_failed["established"])
        self.assertIn("candidate_vs_pca_causal_necessity", pca_failed["failed"])


if __name__ == "__main__":
    unittest.main()
