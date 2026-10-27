from __future__ import annotations

import unittest

import numpy as np

from holonomy_spectroscopy import (
    NumericalRayError,
    apply_relation_blocks,
    apply_word_ray,
    compare_generator_and_block_execution,
    compare_with_published_witness_record,
    decision_cone_survival,
    decoder_facet_margins,
    eigenspectrum,
    nearest_positive_scalar_identity,
    normalize_positive_ray,
    positive_ray_geometry,
    positive_rescaled_matrix_power,
    relation_spectroscopy,
    word_product,
)


class MatrixConventionTests(unittest.TestCase):
    def test_temporal_word_uses_reverse_matrix_order(self) -> None:
        first = np.array([[1.0, 2.0], [0.0, 1.0]])
        second = np.array([[2.0, 0.0], [1.0, 1.0]])
        codes = np.stack((first, second))
        observed = word_product(codes, (0, 1))
        np.testing.assert_allclose(observed, second @ first, atol=0.0, rtol=0.0)

    def test_fractional_word_and_repeat_count_are_rejected(self) -> None:
        codes = np.stack((np.eye(2),))
        with self.assertRaises(ValueError):
            word_product(codes, (0.9,))
        with self.assertRaises(ValueError):
            compare_generator_and_block_execution(
                codes, np.array([[1.0, 0.0]]), (0,), 1.5
            )

    def test_relation_block_matches_generator_normalization(self) -> None:
        codes = np.array(
            [
                [[1.2, 0.2, 0.1], [0.1, 0.9, -0.1], [0.0, 0.3, 1.1]],
                [[0.8, -0.1, 0.2], [0.2, 1.3, 0.0], [0.1, 0.0, 0.7]],
            ]
        )
        states = np.array([[1.0, 0.2, -0.1], [0.3, 1.0, 0.4]])
        comparison = compare_generator_and_block_execution(
            codes, states, (1, 0, 1, 0), 32
        )
        self.assertLess(comparison["maximum_unit_l2"], 2e-14)

    def test_unscaled_zero_product_is_rejected(self) -> None:
        with self.assertRaises(NumericalRayError):
            apply_relation_blocks(np.zeros((2, 2)), np.array([1.0, 0.0]), 1)

    def test_composite_radial_shrink_does_not_trigger_state_guard(self) -> None:
        # Each registered generator output has norm 1e-7 (> 1e-12), while the
        # two-generator composite has norm scale 1e-14 (< 1e-12). The latter is
        # not itself a generator-level state and must be positively rescaled.
        codes = np.stack((1e-7 * np.eye(2),))
        comparison = compare_generator_and_block_execution(
            codes, np.array([[1.0, 0.0]]), (0, 0), 4
        )
        self.assertLess(comparison["maximum_unit_l2"], 1e-15)

    def test_positive_rescaled_power_preserves_power_ray(self) -> None:
        matrix = 1e-3 * np.array([[1.0, 0.2], [0.1, 0.9]])
        observed = positive_rescaled_matrix_power(matrix, 32)
        reference = np.linalg.matrix_power(matrix / np.linalg.norm(matrix), 32)
        reference /= np.linalg.norm(reference)
        np.testing.assert_allclose(observed, reference, atol=2e-14, rtol=2e-14)


class PositiveScalarTests(unittest.TestCase):
    def test_positive_scalar_identity_has_zero_defect(self) -> None:
        result = nearest_positive_scalar_identity(2.5 * np.eye(3))
        self.assertTrue(result["positive_alpha_minimizer_attained"])
        self.assertEqual(result["alpha_or_boundary"], 2.5)
        self.assertEqual(result["frobenius_residual"], 0.0)

    def test_strict_positive_problem_can_have_only_boundary_infimum(self) -> None:
        result = nearest_positive_scalar_identity(-2.0 * np.eye(2))
        self.assertFalse(result["positive_alpha_minimizer_attained"])
        self.assertEqual(result["alpha_or_boundary"], 0.0)
        self.assertEqual(result["relative_frobenius_residual"], 1.0)


class SpectrumTests(unittest.TestCase):
    def test_positive_unique_dominant_is_only_candidate_attractor(self) -> None:
        result = eigenspectrum(np.diag([2.0, 1.0, 0.5]))
        self.assertTrue(result["unique_dominant_modulus"])
        self.assertEqual(
            result["projective_asymptotic_classification"],
            "candidate_positive_ray_fixed_attractor",
        )

    def test_negative_unique_dominant_is_positive_ray_two_cycle(self) -> None:
        result = eigenspectrum(np.diag([-2.0, 1.0]))
        self.assertEqual(
            result["projective_asymptotic_classification"],
            "candidate_positive_ray_two_cycle",
        )

    def test_tied_rotation_does_not_claim_attractor(self) -> None:
        theta = 0.2
        rotation = np.array(
            [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
        )
        result = eigenspectrum(rotation)
        self.assertFalse(result["unique_dominant_modulus"])
        self.assertEqual(
            result["projective_asymptotic_classification"],
            "no_unique_dominant_modulus",
        )

    def test_tiny_positive_ray_angle_is_numerically_resolved(self) -> None:
        left = np.array([[1.0, 0.0]])
        right = np.array([[1.0, 1e-12]])
        angle = float(positive_ray_geometry(left, right)["angle"][0])
        self.assertGreater(angle, 0.5e-12)
        self.assertLess(angle, 2.0e-12)

    def test_invalid_tolerances_and_norm_guards_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            eigenspectrum(np.eye(2), relative_tolerance=-1.0)
        with self.assertRaises(ValueError):
            normalize_positive_ray(np.array([1.0, 0.0]), minimum_norm=np.nan)


class DecisionConeTests(unittest.TestCase):
    def test_exact_permutation_representation_survives_all_suffixes(self) -> None:
        identity = np.eye(2)
        swap = np.array([[0.0, 1.0], [1.0, 0.0]])
        codes = np.stack((identity, swap))
        semantic_maps = np.array([[0, 1], [1, 0]], dtype=np.int64)
        decoder = np.eye(2)
        states = np.eye(2)
        result = decision_cone_survival(
            codes, semantic_maps, decoder, states, np.array([0, 1]), 5
        )
        self.assertTrue(result["all_cases_survive"])
        self.assertTrue(all(event is None for event in result["first_failure"]))

    def test_delayed_observability_finds_first_suffix_and_facet(self) -> None:
        # Generator 0 is an approximate identity relation: it shears class-0's
        # state but leaves the endpoint on the correct side of the x=y cone.
        # Generator 1 exposes the hidden y component one step later.
        shear = np.array([[1.0, 0.0], [0.9, 1.0]])
        expose = np.diag([1.0, 2.0])
        codes = np.stack((expose, shear))
        semantic_maps = np.array([[0, 1], [0, 1]], dtype=np.int64)
        decoder = np.eye(2)
        baseline = np.array([[1.0, 0.0]])
        loop = apply_word_ray(codes, baseline, (1,))
        result = decision_cone_survival(
            codes,
            semantic_maps,
            decoder,
            loop,
            np.array([0]),
            1,
            baseline_states=baseline,
        )
        event = result["first_failure"][0]
        reveal = result["first_reveal"][0]
        self.assertEqual(event["horizon"], 1)
        self.assertEqual(event["suffix"], [0])
        self.assertEqual(event["active_competitor"], 1)
        self.assertLess(event["target_margin"], 0.0)
        self.assertLess(event["normalized_pulled_back_facet_margin"], 0.0)
        self.assertLess(event["signed_spherical_boundary_distance"], 0.0)
        self.assertEqual(reveal["horizon"], 1)
        self.assertEqual(reveal["suffix"], [0])

    def test_float_semantic_labels_are_not_silently_truncated(self) -> None:
        codes = np.stack((np.eye(2),))
        semantic_maps = np.array([[0, 1]], dtype=np.int64)
        with self.assertRaises(ValueError):
            decision_cone_survival(
                codes,
                semantic_maps,
                np.eye(2),
                np.array([[1.0, 0.0]]),
                np.array([0.9]),
                0,
            )

    def test_float_decoder_targets_are_not_silently_truncated(self) -> None:
        with self.assertRaises(ValueError):
            decoder_facet_margins(
                np.eye(2), np.array([[1.0, 0.0]]), np.array([0.9])
            )

    def test_decision_cone_requires_one_dimensional_labels(self) -> None:
        codes = np.stack((np.eye(2),))
        semantic_maps = np.array([[0, 1]], dtype=np.int64)
        with self.assertRaises(ValueError):
            decision_cone_survival(
                codes,
                semantic_maps,
                np.eye(2),
                np.array([[1.0, 0.0]]),
                np.array([[0]], dtype=np.int64),
                0,
            )

    def test_relation_spectroscopy_reports_same_delayed_failure(self) -> None:
        shear = np.array([[1.0, 0.0], [0.9, 1.0]])
        expose = np.diag([1.0, 2.0])
        codes = np.stack((expose, shear))
        semantic_maps = np.array([[0, 1], [0, 1]], dtype=np.int64)
        decoder = np.eye(2)
        result = relation_spectroscopy(
            codes,
            semantic_maps,
            decoder,
            np.array([[1.0, 0.0]]),
            np.array([0]),
            relation_word=(1,),
            repeat_count=1,
            maximum_suffix_horizon=1,
        )
        self.assertTrue(result["identity_semantic_action"])
        self.assertEqual(
            result["decision_cone_survival"]["first_failure"][0]["horizon"], 1
        )

    def test_repeated_semantic_identity_is_reported_separately(self) -> None:
        swap = np.array([[0.0, 1.0], [1.0, 0.0]])
        result = relation_spectroscopy(
            np.stack((swap,)),
            np.array([[1, 0]], dtype=np.int64),
            np.eye(2),
            np.array([[1.0, 0.0]]),
            np.array([0], dtype=np.int64),
            relation_word=(0,),
            repeat_count=2,
            maximum_suffix_horizon=0,
        )
        self.assertFalse(result["identity_semantic_action"])
        self.assertTrue(result["repeated_identity_semantic_action"])
        self.assertEqual(result["repeated_semantic_action"], [0, 1])

    def test_relation_runner_rejects_nonpermutation_semantics(self) -> None:
        with self.assertRaises(ValueError):
            relation_spectroscopy(
                np.stack((np.eye(2),)),
                np.array([[0, 0]], dtype=np.int64),
                np.eye(2),
                np.array([[1.0, 0.0]]),
                np.array([0], dtype=np.int64),
                relation_word=(0,),
                repeat_count=1,
                maximum_suffix_horizon=0,
            )


class PublishedAgreementTests(unittest.TestCase):
    def test_agreement_helper_matches_v03_record_schema(self) -> None:
        cone = {
            "maximum_suffix_horizon": 3,
            "first_reveal": [
                None,
                {
                    "horizon": 3,
                    "suffix_index": 6,
                    "suffix": [1, 1, 0],
                },
            ],
            "first_failure": [
                None,
                {
                    "horizon": 3,
                    "suffix_index": 6,
                    "target_margin": -0.046917929229,
                    "suffix": [1, 1, 0],
                    "prediction": 1,
                    "target": 7,
                },
            ],
        }
        published = {
            "hard_counterexample_count": 1,
            "first_reveal_histogram": {
                "0": 0,
                "1": 0,
                "2": 0,
                "3": 1,
                ">3": 1,
            },
            "hard_counterexamples": [
                {
                    "case_index": 1,
                    "first_reveal_horizon": 3,
                    "first_revealing_suffix_index": 6,
                    "first_revealing_suffix": [1, 1, 0],
                }
            ],
            "identity_semantic_or_margin_failure_count": 1,
            "identity_semantic_or_margin_failures": [
                {
                    "case_index": 1,
                    "first_failure_horizon": 3,
                    "first_failure_suffix_index": 6,
                    "first_failure_suffix": [1, 1, 0],
                    "target_margin": -0.046917929229,
                    "argmax_correct": False,
                    "failure_kind": "wrong_argmax",
                }
            ],
        }
        result = compare_with_published_witness_record(cone, published)
        self.assertTrue(result["exact_agreement"])
        with self.assertRaises(ValueError):
            compare_with_published_witness_record(
                cone, published, margin_atol=-1.0
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
