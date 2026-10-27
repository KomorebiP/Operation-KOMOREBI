"""Checkpoint-free synthetic tests for the prospective v0.3 factorial runner.

The suite deliberately does not open the fresh production bank or any learned
checkpoint. Its fixtures compile the exact D4 action into small NumPy arrays
and exercise the scoring path using synthetic counts.
"""

from __future__ import annotations

from collections import OrderedDict
import copy
from pathlib import Path
import sys
import unittest
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_factorial_probe as probe


def exact_compiler_arrays() -> dict[str, np.ndarray]:
    """Return a float32 state dict that realizes the visible D4 tables exactly."""

    anchors = np.zeros((probe.N_STATES, probe.HIDDEN_DIM), dtype=np.float32)
    anchors[:, : probe.N_STATES] = np.eye(probe.N_STATES, dtype=np.float32)
    decoder = anchors.copy()
    weight = np.zeros(
        (
            probe.HIDDEN_DIM * probe.HIDDEN_DIM,
            probe.N_STATES * probe.N_STATES,
        ),
        dtype=np.float32,
    )
    for source in range(probe.N_STATES):
        for target in range(probe.N_STATES):
            feature = source * probe.N_STATES + target
            weight[target * probe.HIDDEN_DIM + source, feature] = np.float32(1.0)
            for dimension in range(probe.N_STATES, probe.HIDDEN_DIM):
                weight[
                    dimension * probe.HIDDEN_DIM + dimension,
                    feature,
                ] = np.float32(1.0 / probe.N_STATES)
    return {
        "metric_log_diagonal": np.zeros(probe.HIDDEN_DIM, dtype=np.float32),
        "metric_strict_lower": np.zeros(
            probe.HIDDEN_DIM * (probe.HIDDEN_DIM - 1) // 2,
            dtype=np.float32,
        ),
        "state_embedding.weight": anchors,
        "operator_encoder.weight": weight,
        "decoder.weight": decoder,
    }


def synthetic_bank(contexts: int = 4) -> dict[str, np.ndarray]:
    """Build context permutations and slot swaps without sampling any bank."""

    permutations = (
        np.arange(probe.N_STATES, dtype=np.int64),
        np.arange(probe.N_STATES - 1, -1, -1, dtype=np.int64),
        np.asarray((2, 5, 0, 7, 3, 1, 6, 4), dtype=np.int64),
        np.asarray((7, 0, 4, 1, 6, 2, 5, 3), dtype=np.int64),
    )
    canonical = probe.canonical_d4_maps()
    tables: list[np.ndarray] = []
    maps: list[np.ndarray] = []
    phis: list[np.ndarray] = []
    slots: list[np.ndarray] = []
    for context in range(contexts):
        phi = permutations[context % len(permutations)]
        inverse = np.argsort(phi)
        canonical_maps = np.empty((2, probe.N_STATES), dtype=np.int64)
        for operator in range(2):
            canonical_target = canonical[operator, inverse]
            canonical_maps[operator] = phi[canonical_target]
        swap = context % 2
        physical_maps = canonical_maps[[swap, 1 - swap]]
        canonical_to_slot = np.asarray((swap, 1 - swap), dtype=np.int64)
        tables.append(np.eye(probe.N_STATES, dtype=np.float32)[physical_maps])
        maps.append(physical_maps)
        phis.append(phi)
        slots.append(canonical_to_slot)
    return {
        "tables": np.ascontiguousarray(tables, dtype=np.float32),
        "maps": np.ascontiguousarray(maps, dtype=np.int64),
        "phi": np.ascontiguousarray(phis, dtype=np.int64),
        "canonical_to_slot": np.ascontiguousarray(slots, dtype=np.int64),
    }


def fraction(numerator: int, denominator: int) -> dict[str, float | int | None]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def passing_section_audit() -> dict[str, object]:
    return {
        "section_defined": True,
        "section_consistency": {
            "self_decoded_section": fraction(8, 8),
        },
        "one_step_semantic_commutation": {
            "per_generator": {
                "0": {
                    "self_decoded_section": fraction(99, 100),
                    "self_decoded_section_worst_context": fraction(95, 100),
                },
                "1": {
                    "self_decoded_section": fraction(99, 100),
                    "self_decoded_section_worst_context": fraction(95, 100),
                },
            },
        },
    }


def passing_length_fixture() -> dict[str, object]:
    """Use exact boundary values for every H5/H6 performance gate."""

    return {
        "task_accuracy": fraction(198, 200),
        "all_words_task_correct": fraction(99, 100),
        "worst_context": fraction(95, 100),
        "joint_task_counts_with_native": {
            "both_correct": 196,
            "clean_only": 0,
            "condition_only": 2,
            "both_wrong": 2,
        },
    }


def passing_prefix_fixture() -> dict[str, object]:
    decoder_lengths = {
        "0": {"task_accuracy": fraction(8, 8)},
        "5": passing_length_fixture(),
        "6": passing_length_fixture(),
    }
    oracle_lengths = {
        "5": {"task_accuracy": fraction(199, 200)},
        "6": {"task_accuracy": fraction(199, 200)},
    }
    return {
        "selector_diagnostics": {
            "decoder": fraction(99, 100),
            "decoder_worst_context": fraction(98, 100),
            "decoder_prototype_reset_idempotence": {
                "selected_label_unchanged": fraction(100, 100),
                "maximum_hidden_discrepancy": 1e-6,
            },
        },
        "conditions": {
            "decoder_prototype": {
                "per_length": decoder_lengths,
                "conditional_on_selector": {
                    "task_accuracy_given_selector_correct": fraction(199, 200),
                    "per_length": {
                        "5": {
                            "task_accuracy_given_selector_correct": fraction(
                                199, 200
                            )
                        },
                        "6": {
                            "task_accuracy_given_selector_correct": fraction(
                                199, 200
                            )
                        },
                    },
                },
            },
            "oracle_prototype": {"per_length": oracle_lengths},
            "wrong_prototype_control": {
                "wrong_section_control": {
                    "counterfactual_accuracy": fraction(95, 100),
                    "factual_leakage": fraction(5, 100),
                    "per_length": {
                        "5": {
                            "counterfactual_accuracy": fraction(95, 100),
                            "factual_leakage": fraction(5, 100),
                        },
                        "6": {
                            "counterfactual_accuracy": fraction(95, 100),
                            "factual_leakage": fraction(5, 100),
                        },
                    },
                },
            },
        },
    }


class D4TargetAndRolloutTests(unittest.TestCase):
    def test_finite_float32_norm_overflow_is_procedural_failure(self) -> None:
        finite_large = np.full(
            (2, probe.HIDDEN_DIM),
            np.finfo(np.float32).max,
            dtype=np.float32,
        )
        with self.assertRaisesRegex(FloatingPointError, "normalization overflowed"):
            probe.normalize32(finite_large)
        deliberate_sentinel = np.full(
            (1, probe.HIDDEN_DIM),
            np.nan,
            dtype=np.float32,
        )
        self.assertTrue(np.isnan(probe.normalize32(deliberate_sentinel)).all())

    def test_exact_visible_targets_and_compiled_rollout_through_h6(self) -> None:
        bank = synthetic_bank()
        suffixes = probe.words_upto(6)
        self.assertEqual(len(suffixes), 127)
        self.assertEqual(suffixes[0], ())
        self.assertEqual(len(set(suffixes)), 127)

        targets = probe.build_targets(bank, suffixes)
        expected = np.empty_like(targets)
        canonical_maps = probe.canonical_d4_maps()
        for word_index, word in enumerate(suffixes):
            for context, phi in enumerate(bank["phi"]):
                inverse = np.argsort(phi)
                for visible_start in range(probe.N_STATES):
                    canonical_state = int(inverse[visible_start])
                    for operator in word:
                        canonical_state = int(
                            canonical_maps[int(operator), canonical_state]
                        )
                    expected[word_index, context, visible_start] = int(
                        phi[canonical_state]
                    )
        np.testing.assert_array_equal(targets, expected)

        arrays = exact_compiler_arrays()
        operators, receipt = probe.encode_operators32(
            arrays,
            bank["tables"],
            polar=False,
        )
        self.assertFalse(receipt["polar_retraction"])
        anchors = probe.normalized_anchors32(arrays)
        initial = np.broadcast_to(
            anchors[None, :, :],
            (bank["maps"].shape[0], probe.N_STATES, probe.HIDDEN_DIM),
        ).copy()
        hidden, logits = probe.rollout_suffix_tree32(
            initial,
            operators,
            bank["canonical_to_slot"],
            arrays["decoder.weight"],
            suffixes,
        )
        self.assertEqual(hidden.dtype, np.float32)
        self.assertEqual(logits.dtype, np.float32)
        np.testing.assert_array_equal(np.argmax(logits, axis=-1), targets)

    def test_wrong_control_uses_context_canonical_rotation(self) -> None:
        bank = synthetic_bank()
        wrong = probe.wrong_visible_labels(bank["phi"])
        factual = np.broadcast_to(
            np.arange(probe.N_STATES, dtype=np.int64), wrong.shape
        )
        inverse = np.argsort(bank["phi"], axis=1)
        factual_canonical = np.take_along_axis(inverse, factual, axis=1)
        wrong_canonical = np.take_along_axis(inverse, wrong, axis=1)
        np.testing.assert_array_equal(
            wrong_canonical,
            probe.canonical_d4_maps()[0, factual_canonical],
        )
        self.assertTrue(np.all(wrong != factual))


class CalibrationPrototypeTests(unittest.TestCase):
    def test_held_out_calibration_prototype_exact_construction(self) -> None:
        split: OrderedDict[str, np.ndarray] = OrderedDict()
        for prefix in range(probe.CALIBRATION_PREFIXES):
            value = np.zeros(
                (
                    probe.CALIBRATION_CONTEXTS,
                    probe.N_STATES,
                    probe.HIDDEN_DIM,
                ),
                dtype=np.float32,
            )
            value[:, :, : probe.N_STATES] = np.eye(
                probe.N_STATES, dtype=np.float32
            )[None, :, :]
            context_offset = (
                np.arange(probe.CALIBRATION_CONTEXTS, dtype=np.float32)
                * np.float32(1e-4)
            )
            value[:, :, probe.N_STATES + prefix % 4] = (
                np.float32(0.02 * (prefix + 1)) + context_offset[:, None]
            )
            split[f"calibration_{prefix:02d}"] = probe.normalize32(value)

        prototypes, receipt = probe.fit_calibration_prototypes(split)
        samples = np.concatenate(list(split.values()), axis=0)
        expected_resultant = samples.astype(np.float64).sum(axis=0)
        expected = np.asarray(
            expected_resultant
            / np.linalg.norm(expected_resultant, axis=-1, keepdims=True),
            dtype=np.float32,
        )
        np.testing.assert_array_equal(prototypes, expected)
        self.assertEqual(receipt["role"], "held_out_calibration_section")
        self.assertEqual(receipt["calibration_contexts"], 64)
        self.assertEqual(receipt["contributions_per_state"], 512)
        self.assertEqual(receipt["calibration_prefixes"], list(split))
        self.assertEqual(receipt["tensor"], probe.tensor_receipt(expected))

    def test_calibration_prototype_rejects_count_drift(self) -> None:
        missing_prefix = OrderedDict(
            (
                (f"calibration_{index:02d}", np.ones((64, 8, 12), np.float32))
                for index in range(7)
            )
        )
        with self.assertRaisesRegex(RuntimeError, "prefix count drifted"):
            probe.fit_calibration_prototypes(missing_prefix)

    def test_undefined_prototype_is_recorded_as_valid_negative(self) -> None:
        split = OrderedDict(
            (
                (
                    f"calibration_{index:02d}",
                    np.zeros(
                        (
                            probe.CALIBRATION_CONTEXTS,
                            probe.N_STATES,
                            probe.HIDDEN_DIM,
                        ),
                        dtype=np.float32,
                    ),
                )
                for index in range(probe.CALIBRATION_PREFIXES)
            )
        )
        prototypes, receipt = probe.fit_calibration_prototypes(split)
        self.assertFalse(receipt["usable"])
        self.assertEqual(receipt["defined_states"]["numerator"], 0)
        self.assertTrue(np.isnan(prototypes).all())

    def test_prototype_fit_precedes_evaluation_operator_construction(self) -> None:
        events: list[str] = []
        calibration_tables = np.zeros((1, 1), dtype=np.float32)
        evaluation_tables = np.ones((1, 1), dtype=np.float32)

        def encode(
            arrays: object,
            tables: np.ndarray,
            *,
            polar: bool,
        ) -> tuple[np.ndarray, dict[str, object]]:
            del arrays, polar
            if tables is calibration_tables:
                events.append("encode-calibration")
                return np.empty((0,), dtype=np.float32), {}
            events.append("encode-evaluation")
            raise RuntimeError("stop-after-order-check")

        def split(*args: object, **kwargs: object) -> OrderedDict[str, np.ndarray]:
            del args, kwargs
            events.append("calibration-prefix-rollout")
            value = np.ones(
                (
                    probe.CALIBRATION_CONTEXTS,
                    probe.N_STATES,
                    probe.HIDDEN_DIM,
                ),
                dtype=np.float32,
            )
            return OrderedDict(
                (f"calibration_{index:02d}", value.copy())
                for index in range(probe.CALIBRATION_PREFIXES)
            )

        def fit(
            states: object,
        ) -> tuple[np.ndarray, dict[str, object]]:
            del states
            events.append("fit-prototype")
            return (
                np.ones((probe.N_STATES, probe.HIDDEN_DIM), dtype=np.float32),
                {"usable": True},
            )

        with (
            mock.patch.object(probe, "encode_operators32", side_effect=encode),
            mock.patch.object(probe, "split_states_for_words32", side_effect=split),
            mock.patch.object(probe, "fit_calibration_prototypes", side_effect=fit),
            mock.patch.object(
                probe,
                "construct_anchor_projector32",
                return_value=(np.eye(probe.HIDDEN_DIM, dtype=np.float32), {"pass": True}),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "stop-after-order-check"):
                probe.evaluate_checkpoint(
                    "polar_cr",
                    101,
                    exact_compiler_arrays(),
                    {
                        "tables": calibration_tables,
                        "canonical_to_slot": np.empty((0,), dtype=np.int64),
                    },
                    {
                        "tables": evaluation_tables,
                        "canonical_to_slot": np.empty((0,), dtype=np.int64),
                    },
                    OrderedDict(),
                    OrderedDict(),
                )
        self.assertEqual(
            events,
            [
                "encode-calibration",
                "calibration-prefix-rollout",
                "fit-prototype",
                "encode-evaluation",
            ],
        )


class FactorialConstructionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bank = synthetic_bank()
        self.arrays = exact_compiler_arrays()
        self.anchors = probe.normalized_anchors32(self.arrays)
        prototype_raw = self.anchors.copy()
        prototype_raw[:, 8] = np.linspace(
            0.05, 0.12, probe.N_STATES, dtype=np.float32
        )
        self.prototypes = probe.normalize32(prototype_raw)
        true = np.broadcast_to(
            np.arange(probe.N_STATES, dtype=np.int64),
            (self.bank["maps"].shape[0], probe.N_STATES),
        )
        self.native = self.anchors[true].copy()
        self.native[0, 0] = self.anchors[1]
        nuisance = np.zeros(probe.HIDDEN_DIM, dtype=np.float32)
        nuisance[8] = np.float32(0.1)
        self.native[1, 3] = probe.normalize32(self.anchors[3] + nuisance)

    def test_all_core_cells_reuse_one_decoder_label_tensor(self) -> None:
        states, audit, labels = probe.construct_interventions32(
            self.native,
            self.anchors,
            self.arrays["decoder.weight"],
            self.prototypes,
            None,
            self.bank["phi"],
        )
        true = labels["true"]
        decoded = labels["decoder"]
        np.testing.assert_array_equal(states["oracle_anchor"], self.anchors[true])
        np.testing.assert_array_equal(
            states["oracle_prototype"], self.prototypes[true]
        )
        np.testing.assert_array_equal(states["decoder_anchor"], self.anchors[decoded])
        np.testing.assert_array_equal(
            states["decoder_prototype"], self.prototypes[decoded]
        )
        self.assertTrue(audit["decoder_label_tensor_reused_for_both_sections"])
        self.assertEqual(
            audit["shared_decoder_selected_labels_tensor"],
            probe.tensor_receipt(decoded.astype(np.int64)),
        )
        self.assertTrue(np.any(decoded != true))
        self.assertTrue(np.any(decoded == true))

    def test_oracle_decoder_rollouts_are_exact_on_correct_selection(self) -> None:
        states, _, labels = probe.construct_interventions32(
            self.native,
            self.anchors,
            self.arrays["decoder.weight"],
            self.prototypes,
            None,
            self.bank["phi"],
        )
        operators, _ = probe.encode_operators32(
            self.arrays,
            self.bank["tables"],
            polar=False,
        )
        suffixes = probe.words_upto(6)
        correct_selection = labels["decoder"] == labels["true"]
        for section in ("anchor", "prototype"):
            oracle_hidden, oracle_logits = probe.rollout_suffix_tree32(
                states[f"oracle_{section}"],
                operators,
                self.bank["canonical_to_slot"],
                self.arrays["decoder.weight"],
                suffixes,
            )
            decoder_hidden, decoder_logits = probe.rollout_suffix_tree32(
                states[f"decoder_{section}"],
                operators,
                self.bank["canonical_to_slot"],
                self.arrays["decoder.weight"],
                suffixes,
            )
            np.testing.assert_array_equal(
                oracle_hidden[:, correct_selection],
                decoder_hidden[:, correct_selection],
            )
            np.testing.assert_array_equal(
                oracle_logits[:, correct_selection],
                decoder_logits[:, correct_selection],
            )
            self.assertTrue(
                np.any(
                    np.argmax(oracle_logits[:, ~correct_selection], axis=-1)
                    != np.argmax(decoder_logits[:, ~correct_selection], axis=-1)
                )
            )

    def test_projection_none_is_isolated_from_factorial_cells(self) -> None:
        no_projection, no_audit, no_labels = probe.construct_interventions32(
            self.native,
            self.anchors,
            self.arrays["decoder.weight"],
            self.prototypes,
            None,
            self.bank["phi"],
        )
        with_projection, yes_audit, yes_labels = probe.construct_interventions32(
            self.native,
            self.anchors,
            self.arrays["decoder.weight"],
            self.prototypes,
            np.eye(probe.HIDDEN_DIM, dtype=np.float32),
            self.bank["phi"],
        )
        self.assertFalse(no_audit["anchor_projection_available"])
        self.assertTrue(yes_audit["anchor_projection_available"])
        self.assertTrue(np.isnan(no_projection["anchor_projection"]).all())
        self.assertTrue(np.isfinite(with_projection["anchor_projection"]).all())
        for name in probe.INTERVENTIONS:
            if name != "anchor_projection":
                np.testing.assert_array_equal(no_projection[name], with_projection[name])
        for name in no_labels:
            np.testing.assert_array_equal(no_labels[name], yes_labels[name])

    def test_globally_unusable_prototype_skips_recurrent_math(self) -> None:
        initial = np.zeros(
            (2, probe.N_STATES, probe.HIDDEN_DIM),
            dtype=np.float32,
        )
        initial[0, 0] = np.float32(np.finfo(np.float32).max)
        initial[1, 1] = np.nan
        operators = np.zeros(
            (2, 2, probe.HIDDEN_DIM, probe.HIDDEN_DIM),
            dtype=np.float32,
        )
        slots = np.zeros((2, 2), dtype=np.int64)
        decoder = np.zeros(
            (probe.N_STATES, probe.HIDDEN_DIM),
            dtype=np.float32,
        )
        suffixes = ((), (0,))
        with mock.patch.object(probe, "rollout_suffix_tree32") as rollout:
            hidden, logits, intentionally_undefined = probe.rollout_intervention32(
                "oracle_prototype",
                initial,
                operators,
                slots,
                decoder,
                suffixes,
                prototype_usable=False,
                projector_available=True,
            )
        rollout.assert_not_called()
        self.assertTrue(intentionally_undefined)
        self.assertEqual(
            hidden.shape,
            (len(suffixes), 2, probe.N_STATES, probe.HIDDEN_DIM),
        )
        self.assertEqual(
            logits.shape,
            (len(suffixes), 2, probe.N_STATES, probe.N_STATES),
        )
        self.assertTrue(np.isnan(hidden).all())
        self.assertTrue(np.isnan(logits).all())

    def test_finite_zero_native_rays_do_not_abort_nearest_diagnostics(self) -> None:
        native = np.zeros_like(self.native)
        states, audit, labels = probe.construct_interventions32(
            native,
            self.anchors,
            self.arrays["decoder.weight"],
            self.prototypes,
            None,
            self.bank["phi"],
        )
        self.assertEqual(audit["anchor_nearest_scores_defined"]["numerator"], 0)
        self.assertEqual(audit["native_cut_hidden_rays_defined"]["numerator"], 0)
        self.assertEqual(audit["decoder"]["numerator"], 0)
        self.assertEqual(
            audit["prototype_nearest_scores_defined"]["numerator"],
            0,
        )
        self.assertFalse(labels["anchor_nearest_defined"].any())
        self.assertFalse(labels["decoder_defined"].any())
        self.assertFalse(labels["prototype_nearest_defined"].any())
        self.assertTrue(np.all(states["anchor_nearest_anchor"] == 0.0))
        self.assertTrue(np.all(states["prototype_nearest_anchor"] == 0.0))
        self.assertTrue(np.isfinite(states["decoder_anchor"]).all())

    def test_finite_zero_stepped_rays_are_failed_commutation_not_abort(self) -> None:
        contexts = int(self.bank["maps"].shape[0])
        zero_operators = np.zeros(
            (contexts, 2, probe.HIDDEN_DIM, probe.HIDDEN_DIM),
            dtype=np.float32,
        )
        audit = probe.autonomous_section_audit(
            self.anchors,
            self.arrays["decoder.weight"],
            zero_operators,
            self.bank,
            section_name="synthetic_zero_step",
        )
        self.assertTrue(audit["section_defined"])
        for generator in ("0", "1"):
            row = audit["one_step_semantic_commutation"]["per_generator"][
                generator
            ]
            self.assertEqual(row["stepped_hidden_rays_defined"]["numerator"], 0)
            self.assertEqual(row["nearest_section_scores_defined"]["numerator"], 0)
            self.assertEqual(row["nearest_section"]["numerator"], 0)
            self.assertEqual(row["self_decoded_section"]["numerator"], 0)

    def test_oriented_ray_threshold_is_strict_and_exact(self) -> None:
        hidden = np.zeros((4, probe.HIDDEN_DIM), dtype=np.float64)
        hidden[1, 0] = probe.RAY_NORM_STRICT_MINIMUM / 2.0
        hidden[2, 0] = probe.RAY_NORM_STRICT_MINIMUM
        hidden[3, 0] = probe.RAY_NORM_STRICT_MINIMUM * 2.0
        selected, defined = probe.nearest_anchor_labels64(
            hidden,
            self.anchors,
            label="strict-threshold-test",
        )
        np.testing.assert_array_equal(
            defined,
            np.array([False, False, False, True]),
        )
        self.assertEqual(int(selected[3]), 0)


class IntegerGateTests(unittest.TestCase):
    def test_at_least_gate_uses_ceiling_integer_boundary(self) -> None:
        passing = probe.fraction_gate("unit", fraction(126, 127), 0.99)
        failing = probe.fraction_gate("unit", fraction(125, 127), 0.99)
        self.assertEqual(passing["integer_boundary"], 126)
        self.assertTrue(passing["pass"])
        self.assertFalse(failing["pass"])

    def test_at_most_gate_uses_floor_integer_boundary(self) -> None:
        passing = probe.fraction_gate(
            "unit", fraction(1, 200), 0.005, relation="at_most"
        )
        failing = probe.fraction_gate(
            "unit", fraction(2, 200), 0.005, relation="at_most"
        )
        self.assertEqual(passing["integer_boundary"], 1)
        self.assertTrue(passing["pass"])
        self.assertFalse(failing["pass"])

    def test_zero_denominator_fails_closed(self) -> None:
        result = probe.fraction_gate("unit", fraction(0, 0), 0.99)
        self.assertIsNone(result["integer_boundary"])
        self.assertFalse(result["pass"])

    def test_native_error_reduction_boundary_is_integer_exact(self) -> None:
        counts = {
            "both_correct": 196,
            "clean_only": 0,
            "condition_only": 2,
            "both_wrong": 2,
        }
        checks = probe.paired_native_gates(counts, total=200)
        reduction = next(
            check for check in checks if check["name"].startswith("native_net")
        )
        self.assertEqual(reduction["required_net_errors_removed"], 2)
        self.assertTrue(reduction["pass"])
        failed = copy.deepcopy(counts)
        failed["condition_only"] = 1
        failed["both_wrong"] = 3
        failed_reduction = next(
            check
            for check in probe.paired_native_gates(failed, total=200)
            if check["name"].startswith("native_net")
        )
        self.assertFalse(failed_reduction["pass"])


class PrimaryGateFixtureTests(unittest.TestCase):
    def passing_result(self) -> dict[str, object]:
        prefixes = OrderedDict(
            (
                ("prefix_alpha", passing_prefix_fixture()),
                ("prefix_beta", passing_prefix_fixture()),
            )
        )
        return probe.checkpoint_primary_gate(prefixes, passing_section_audit())

    def test_boundary_fixture_passes_every_prefix_and_both_horizons(self) -> None:
        result = self.passing_result()
        failures = [check["name"] for check in result["checks"] if not check["pass"]]
        self.assertEqual(failures, [])
        self.assertTrue(result["pass"])
        names = {check["name"] for check in result["checks"]}
        for prefix in ("prefix_alpha", "prefix_beta"):
            for horizon in (5, 6):
                self.assertIn(
                    f"{prefix}/H{horizon}/decoder_prototype_accuracy_at_least_0.99",
                    names,
                )

    def test_one_bad_prefix_cannot_be_hidden_by_another_prefix(self) -> None:
        prefixes = OrderedDict(
            (
                ("prefix_alpha", passing_prefix_fixture()),
                ("prefix_beta", passing_prefix_fixture()),
            )
        )
        prefixes["prefix_beta"]["selector_diagnostics"]["decoder"] = fraction(
            98, 100
        )
        result = probe.checkpoint_primary_gate(prefixes, passing_section_audit())
        self.assertFalse(result["pass"])
        failures = [check["name"] for check in result["checks"] if not check["pass"]]
        self.assertEqual(
            failures,
            ["prefix_beta/decoder_selector_at_least_0.99"],
        )

    def test_h5_and_h6_are_independently_pass_bearing(self) -> None:
        for horizon in (5, 6):
            with self.subTest(horizon=horizon):
                prefixes = OrderedDict(
                    (("prefix_alpha", passing_prefix_fixture()),)
                )
                prefixes["prefix_alpha"]["conditions"]["decoder_prototype"][
                    "per_length"
                ][str(horizon)]["task_accuracy"] = fraction(197, 200)
                result = probe.checkpoint_primary_gate(
                    prefixes,
                    passing_section_audit(),
                )
                self.assertFalse(result["pass"])
                failures = [
                    check["name"]
                    for check in result["checks"]
                    if not check["pass"]
                ]
                self.assertIn(
                    f"prefix_alpha/H{horizon}/decoder_prototype_accuracy_at_least_0.99",
                    failures,
                )
                other = 6 if horizon == 5 else 5
                self.assertNotIn(
                    f"prefix_alpha/H{other}/decoder_prototype_accuracy_at_least_0.99",
                    failures,
                )

    def test_low_native_error_is_interface_pass_not_repair_superiority(self) -> None:
        prefix = passing_prefix_fixture()
        for horizon in (5, 6):
            prefix["conditions"]["decoder_prototype"]["per_length"][str(horizon)][
                "joint_task_counts_with_native"
            ] = {
                "both_correct": 199,
                "clean_only": 0,
                "condition_only": 0,
                "both_wrong": 1,
            }
        result = probe.checkpoint_primary_gate(
            OrderedDict((("prefix_alpha", prefix),)),
            passing_section_audit(),
        )
        self.assertTrue(result["pass"])
        self.assertEqual(
            result["repair_superiority"]["status"],
            "NOT_EVALUABLE_LOW_NATIVE_ERROR",
        )
        self.assertIsNone(result["repair_superiority"]["pass"])

    def test_one_low_error_stratum_disables_all_operational_reduction_gates(self) -> None:
        prefix = passing_prefix_fixture()
        prefix["conditions"]["decoder_prototype"]["per_length"]["5"][
            "joint_task_counts_with_native"
        ] = {
            "both_correct": 199,
            "clean_only": 0,
            "condition_only": 0,
            "both_wrong": 1,
        }
        prefix["conditions"]["decoder_prototype"]["per_length"]["6"][
            "joint_task_counts_with_native"
        ] = {
            "both_correct": 198,
            "clean_only": 0,
            "condition_only": 0,
            "both_wrong": 2,
        }
        result = probe.checkpoint_primary_gate(
            OrderedDict((("prefix_alpha", prefix),)),
            passing_section_audit(),
        )
        self.assertTrue(result["pass"])
        self.assertEqual(
            result["repair_superiority"]["status"],
            "NOT_EVALUABLE_LOW_NATIVE_ERROR",
        )
        self.assertIsNone(result["repair_superiority"]["pass"])
        self.assertTrue(
            any(
                check.get("evaluable") is True and not check["pass"]
                for check in result["repair_superiority"]["checks"]
            )
        )
        operational_names = {check["name"] for check in result["checks"]}
        self.assertFalse(
            any("native_net_error_reduction" in name for name in operational_names)
        )

    def test_wrong_prototype_controls_are_independent_by_horizon(self) -> None:
        for horizon in (5, 6):
            with self.subTest(horizon=horizon):
                prefix = passing_prefix_fixture()
                prefix["conditions"]["wrong_prototype_control"][
                    "wrong_section_control"
                ]["per_length"][str(horizon)]["factual_leakage"] = fraction(6, 100)
                result = probe.checkpoint_primary_gate(
                    OrderedDict((("prefix_alpha", prefix),)),
                    passing_section_audit(),
                )
                failures = {
                    check["name"] for check in result["checks"] if not check["pass"]
                }
                self.assertIn(
                    f"prefix_alpha/H{horizon}/wrong_prototype_factual_leakage_at_most_0.05",
                    failures,
                )
                other = 6 if horizon == 5 else 5
                self.assertNotIn(
                    f"prefix_alpha/H{other}/wrong_prototype_factual_leakage_at_most_0.05",
                    failures,
                )


class WorkCountTests(unittest.TestCase):
    def test_work_counts_match_independent_integer_derivation(self) -> None:
        suffixes = sum(2**length for length in range(probe.SUFFIX_MAX_LENGTH + 1))
        self.assertEqual(suffixes, 127)
        calibration_states = (
            probe.CALIBRATION_CONTEXTS
            * probe.N_STATES
            * probe.CALIBRATION_PREFIXES
        )
        evaluation_states = (
            probe.EVALUATION_CONTEXTS
            * probe.N_STATES
            * probe.EVALUATION_PREFIXES
        )
        suffix_endpoints = (
            evaluation_states * suffixes * len(probe.INTERVENTIONS)
            + probe.EVALUATION_CONTEXTS * probe.N_STATES * suffixes
        )
        matvecs = (
            (calibration_states + evaluation_states) * probe.PREFIX_LENGTH
            + evaluation_states * len(probe.INTERVENTIONS) * (suffixes - 1)
            + probe.EVALUATION_CONTEXTS * probe.N_STATES * (suffixes - 1)
            + 4 * probe.EVALUATION_CONTEXTS * probe.N_STATES
        )
        expected = {
            "calibration_split_states_per_checkpoint": 4096,
            "evaluation_split_states_per_checkpoint": 4096,
            "suffix_endpoint_evaluations_per_checkpoint": suffix_endpoints,
            "float32_recurrent_matvecs_per_checkpoint": matvecs,
            "checkpoint_count": len(probe.ARMS) * len(probe.SEEDS),
            "total_suffix_endpoint_evaluations": suffix_endpoints
            * len(probe.ARMS)
            * len(probe.SEEDS),
            "total_float32_recurrent_matvecs": matvecs
            * len(probe.ARMS)
            * len(probe.SEEDS),
        }
        self.assertEqual(
            expected,
            {
                "calibration_split_states_per_checkpoint": 4_096,
                "evaluation_split_states_per_checkpoint": 4_096,
                "suffix_endpoint_evaluations_per_checkpoint": 6_307_328,
                "float32_recurrent_matvecs_per_checkpoint": 6_784_000,
                "checkpoint_count": 12,
                "total_suffix_endpoint_evaluations": 75_687_936,
                "total_float32_recurrent_matvecs": 81_408_000,
            },
        )
        self.assertEqual(probe.expected_work_counts(), expected)


class PackedEvidenceTests(unittest.TestCase):
    def test_defined_branch_nonfinite_rollout_is_procedural_failure(self) -> None:
        hidden = np.ones((1, probe.HIDDEN_DIM), dtype=np.float32)
        logits = np.ones((1, probe.N_STATES), dtype=np.float32)
        bad_hidden = hidden.copy()
        bad_hidden[0, 0] = np.nan
        with self.assertRaisesRegex(FloatingPointError, "nonfinite hidden"):
            probe.assert_finite_rollout(bad_hidden, logits, label="defined")
        bad_logits = logits.copy()
        bad_logits[0, 0] = np.inf
        with self.assertRaisesRegex(FloatingPointError, "nonfinite logit"):
            probe.assert_finite_rollout(hidden, bad_logits, label="defined")

    def test_boolean_evidence_roundtrips_and_authenticates(self) -> None:
        value = np.asarray(
            [[[False, True], [True, True]], [[True, False], [False, True]]],
            dtype=np.bool_,
        )
        receipt = probe.packed_bool_evidence(value)
        np.testing.assert_array_equal(probe.unpack_bool_evidence(receipt), value)
        tampered = copy.deepcopy(receipt)
        tampered["packed_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            probe.unpack_bool_evidence(tampered)

    def test_condition_rates_recompute_from_packed_case_evidence(self) -> None:
        suffixes = probe.words_upto()
        targets = np.broadcast_to(
            np.arange(probe.N_STATES, dtype=np.int64)[None, None, :],
            (len(suffixes), probe.EVALUATION_CONTEXTS, probe.N_STATES),
        ).copy()
        hidden = np.zeros(
            targets.shape + (probe.HIDDEN_DIM,),
            dtype=np.float32,
        )
        hidden[..., 0] = 1.0
        logits = np.eye(probe.N_STATES, dtype=np.float32)[targets]
        condition = probe.evaluate_condition(
            hidden,
            logits,
            hidden,
            logits,
            hidden,
            logits,
            targets,
            suffixes,
        )
        recomputed = probe.verify_condition_evidence(
            condition,
            suffixes,
            label="synthetic-perfect",
        )
        self.assertTrue(bool(recomputed.all()))
        tampered = copy.deepcopy(condition)
        tampered["per_length"]["6"]["task_accuracy"] = fraction(0, 1)
        with self.assertRaisesRegex(ValueError, "evidence-derived metric mismatch"):
            probe.verify_condition_evidence(
                tampered,
                suffixes,
                label="synthetic-tampered",
            )

    def test_negative_factorial_interaction_is_valid_signed_record(self) -> None:
        suffixes = probe.words_upto()
        shape = (len(suffixes), 1, 1)
        correct = {
            "decoder_prototype": np.zeros(shape, dtype=bool),
            "decoder_anchor": np.ones(shape, dtype=bool),
            "oracle_prototype": np.ones(shape, dtype=bool),
            "oracle_anchor": np.zeros(shape, dtype=bool),
            "native": np.zeros(shape, dtype=bool),
        }
        summary = probe.factorial_contrast_summary(correct, suffixes)
        interaction = summary["selector_by_section_interaction"]["all_H0_to_H6"]
        self.assertEqual(interaction["signed_numerator"], -2 * len(suffixes))
        self.assertEqual(interaction["signed_value"], -2.0)
        self.assertGreater(probe.validate_fraction_records(summary), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
