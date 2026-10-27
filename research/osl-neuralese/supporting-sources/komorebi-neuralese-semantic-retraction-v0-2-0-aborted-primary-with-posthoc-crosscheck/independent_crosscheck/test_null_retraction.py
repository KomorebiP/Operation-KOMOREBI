from __future__ import annotations

import ast
import copy
import io
import json
import pickle
from pathlib import Path
import tempfile
import unittest

import numpy as np

import probe_null_retraction as probe


class StaticProtocolTests(unittest.TestCase):
    def test_protocol_and_work_bound_match_runtime(self) -> None:
        result = probe.validate_protocol_design(probe.load_protocol())
        self.assertTrue(result["valid"])
        self.assertEqual(result["suffix_word_count"], 31)
        self.assertEqual(
            result["bounded_work"]["total_float32_recurrent_matvecs"],
            4_497_408,
        )

    def test_source_does_not_import_torch(self) -> None:
        source = Path(probe.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertNotIn("torch", imported)

    def test_restricted_unpickler_blocks_arbitrary_global(self) -> None:
        payload = pickle.dumps(eval)
        with self.assertRaises(pickle.UnpicklingError):
            probe.RestrictedTorchUnpickler(io.BytesIO(payload)).load()

    def test_draft_firewall_blocks_learned_execution(self) -> None:
        protocol = probe.load_protocol()
        if protocol["status"] != probe.FROZEN_STATUS:
            with self.assertRaises(RuntimeError):
                probe.assert_learned_execution_unlocked()

    def test_frozen_status_alone_never_unlocks_execution(self) -> None:
        protocol = copy.deepcopy(probe.load_protocol())
        protocol["status"] = probe.FROZEN_STATUS
        protocol_bytes = (json.dumps(protocol, sort_keys=True) + "\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "FROZEN_PROTOCOL.sha256"
            missing = probe.validate_protocol_design(
                protocol,
                protocol_bytes=protocol_bytes,
                freeze_receipt_path=receipt,
            )
            self.assertFalse(missing["learned_execution_unlocked"])
            receipt.write_text("0" * 64 + "\n", encoding="utf-8")
            mismatch = probe.validate_protocol_design(
                protocol,
                protocol_bytes=protocol_bytes,
                freeze_receipt_path=receipt,
            )
            self.assertFalse(mismatch["learned_execution_unlocked"])
            receipt.write_text(probe.sha256_bytes(protocol_bytes) + "\n", encoding="utf-8")
            matched = probe.validate_protocol_design(
                protocol,
                protocol_bytes=protocol_bytes,
                freeze_receipt_path=receipt,
            )
            self.assertTrue(matched["learned_execution_unlocked"])

    def test_output_path_cannot_alias_or_enter_protected_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "source"
            root.mkdir()
            archive = base / "sealed.zip"
            archive.write_bytes(b"sealed")
            with self.assertRaises(ValueError):
                probe.validate_output_path(root, archive, archive)
            with self.assertRaises(ValueError):
                probe.validate_output_path(root, archive, root / "RESULTS.json")
            existing = base / "existing.json"
            existing.write_text("{}", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                probe.validate_output_path(root, archive, existing)
            allowed = base / "new-results" / "RESULTS.json"
            self.assertEqual(
                probe.validate_output_path(root, archive, allowed),
                allowed.resolve(),
            )


class BankAndWordTests(unittest.TestCase):
    def test_suffixes_are_complete_and_prefix_ordered(self) -> None:
        words = probe.words_upto()
        self.assertEqual(len(words), 31)
        self.assertEqual(words[0], ())
        self.assertEqual(len(set(words)), 31)
        positions = {word: index for index, word in enumerate(words)}
        for index, word in enumerate(words[1:], start=1):
            self.assertLess(positions[word[:-1]], index)

    def test_regenerated_null_bank_has_sealed_digest(self) -> None:
        bank = probe.regenerate_null_bank()
        self.assertEqual(
            probe.tensor_receipt(bank["tables"])["sha256"],
            "f634413d5e470f176261e9e7a9cb5acfbf29e14c288154861211bee45d8fa0b7",
        )
        self.assertEqual(bank["tables"].dtype, np.float32)
        self.assertEqual(bank["maps"].dtype, np.int64)

    def test_all_stress_prefixes_are_semantic_identities(self) -> None:
        result = probe.validate_stress_semantics(probe.regenerate_null_bank())
        self.assertEqual(
            {name: row["length"] for name, row in result.items()},
            {"r4_x16": 64, "f2_x16": 32, "frfr_x16": 64},
        )
        self.assertTrue(
            all(row["identity_on_all_context_states"] for row in result.values())
        )

    def test_wrong_control_is_context_canonical_and_distinct(self) -> None:
        bank = probe.regenerate_null_bank()
        wrong = probe.wrong_visible_labels(bank["phi"])
        factual = np.broadcast_to(np.arange(8), wrong.shape)
        self.assertTrue(np.all(wrong != factual))
        inverse = np.argsort(bank["phi"], axis=1)
        factual_canonical = np.take_along_axis(inverse, factual, axis=1)
        wrong_canonical = np.take_along_axis(inverse, wrong, axis=1)
        expected = probe.canonical_d4_maps()[0, factual_canonical]
        self.assertTrue(np.array_equal(wrong_canonical, expected))


def exact_compiler_arrays() -> dict[str, np.ndarray]:
    anchors = np.zeros((8, 12), dtype=np.float32)
    anchors[:, :8] = np.eye(8, dtype=np.float32)
    decoder = anchors.copy()
    weight = np.zeros((12 * 12, 8 * 8), dtype=np.float32)
    for source in range(8):
        for target in range(8):
            feature = source * 8 + target
            weight[target * 12 + source, feature] = np.float32(1.0)
            for dimension in range(8, 12):
                weight[dimension * 12 + dimension, feature] = np.float32(1.0 / 8.0)
    return {
        "metric_log_diagonal": np.zeros(12, dtype=np.float32),
        "metric_strict_lower": np.zeros(66, dtype=np.float32),
        "state_embedding.weight": anchors,
        "operator_encoder.weight": weight,
        "decoder.weight": decoder,
    }


class SyntheticMechanismTests(unittest.TestCase):
    def test_frozen_numeric_summary_and_undefined_maximum_policies(self) -> None:
        values = np.arange(20, dtype=np.float64)
        self.assertEqual(probe.numeric_summary(values)["p95"], 19.0)
        angles = probe.oriented_angles64(
            np.array([[1.0, 0.0], [1e-13, 0.0]], dtype=np.float64),
            np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64),
        )
        self.assertAlmostEqual(float(angles[0]), np.pi / 2.0)
        self.assertTrue(np.isnan(angles[1]))
        suffix_values = np.array([[0.2, 0.3], [np.nan, 0.1]], dtype=np.float64)
        np.testing.assert_array_equal(
            probe.maximum_over_suffix(suffix_values, undefined_fill=np.pi),
            np.array([np.pi, 0.3]),
        )

    def test_numpy_state_digest_has_fixed_torch_compatible_receipt(self) -> None:
        self.assertEqual(
            probe.state_dict_digest_numpy(exact_compiler_arrays()),
            "8ddb121cb1310810aa39686a4cf2080f0e47228c60ed06513435b533d5a24d99",
        )

    def test_float32_normalization_and_step_contract(self) -> None:
        hidden = np.arange(64 * 8 * 12, dtype=np.float32).reshape(64, 8, 12) + 1
        normalized = probe.normalize32(hidden)
        self.assertEqual(normalized.dtype, np.float32)
        np.testing.assert_allclose(
            np.linalg.norm(normalized, axis=-1),
            np.ones((64, 8), dtype=np.float32),
            atol=2e-6,
            rtol=2e-6,
        )

    def test_nonfinite_and_zero_ray_selectors_fail_closed(self) -> None:
        with self.assertRaises(FloatingPointError):
            probe.finite_argmax(
                np.array([[np.inf, 0.0]], dtype=np.float32),
                label="unit nonfinite",
            )
        with self.assertRaises(FloatingPointError):
            probe.nearest_anchor_labels64(
                np.zeros((1, 12), dtype=np.float32),
                np.eye(8, 12, dtype=np.float32),
                label="unit zero ray",
            )

    def test_zero_hidden_endpoint_never_receives_argmax_credit(self) -> None:
        hidden = np.zeros((1, 1, 1, 12), dtype=np.float32)
        logits = np.zeros((1, 1, 1, 8), dtype=np.float32)
        reference_hidden = hidden.copy()
        reference_hidden[..., 0] = 1.0
        reference_logits = logits.copy()
        targets = np.zeros((1, 1, 1), dtype=np.int64)
        result = probe.evaluate_condition(
            hidden,
            logits,
            reference_hidden,
            reference_logits,
            reference_hidden,
            reference_logits,
            targets,
            ((),),
        )
        self.assertEqual(result["logits_finite"]["value"], 1.0)
        self.assertEqual(result["hidden_ray_defined"]["value"], 0.0)
        self.assertEqual(result["endpoint_valid"]["value"], 0.0)
        self.assertEqual(result["task_accuracy"]["value"], 0.0)
        clean = probe.clean_reference_summary(hidden, logits, targets)
        self.assertEqual(clean["task_accuracy"]["value"], 0.0)

    def test_crossfit_excludes_test_context_fold_and_prefix(self) -> None:
        names = tuple(probe.STRESS_BASE_WORDS)
        split: dict[str, np.ndarray] = {}
        for prefix_index, name in enumerate(names):
            value = np.zeros((64, 8, 12), dtype=np.float32)
            value[:, :, :8] = np.eye(8, dtype=np.float32)[None, :, :]
            value[:, :, 8 + prefix_index] = np.float32(0.25 * (prefix_index + 1))
            split[name] = probe.normalize32(value)
        prototypes, receipt = probe.crossfit_prototypes(split)
        expected_samples = np.concatenate(
            [split[names[1]][1::2], split[names[2]][1::2]],
            axis=0,
        )
        expected = expected_samples.astype(np.float64).sum(axis=0)
        expected /= np.linalg.norm(expected, axis=-1, keepdims=True)
        np.testing.assert_allclose(prototypes[0, 0], expected.astype(np.float32), atol=2e-7)
        self.assertTrue(all(row["contributions_per_state"] == 64 for row in receipt["records"]))

    def test_exact_compiler_full_sensitivity_panel(self) -> None:
        result = probe.evaluate_checkpoint(
            "euclidean_supervised",
            101,
            exact_compiler_arrays(),
            probe.regenerate_null_bank(),
        )
        self.assertIn(
            "raw_operator_singular_values",
            result["operator_construction"],
        )
        self.assertEqual(result["clean_semantic_endpoint"]["task_accuracy"]["value"], 1.0)
        audit = result["autonomous_section_audit"]
        self.assertEqual(audit["section_consistency"]["self_decoded_anchor"]["value"], 1.0)
        self.assertEqual(audit["reset_idempotence"]["self_decoded_anchor"]["value"], 1.0)
        self.assertEqual(
            audit["one_step_semantic_commutation"]["self_decoded_anchor"]["value"],
            1.0,
        )
        expected_good = {
            "native",
            "oracle_anchor",
            "self_decoded_anchor",
            "nearest_ray_anchor",
            "crossfit_oracle_prototype",
        }
        for prefix in result["prefixes"].values():
            self.assertEqual(prefix["selector_diagnostics"]["self_decoded_anchor"]["value"], 1.0)
            self.assertEqual(prefix["selector_diagnostics"]["nearest_ray_anchor"]["value"], 1.0)
            for name in expected_good:
                condition = prefix["conditions"][name]
                self.assertEqual(condition["task_accuracy"]["value"], 1.0)
                self.assertEqual(condition["clean_prediction_agreement"]["value"], 1.0)
            wrong = prefix["conditions"]["wrong_anchor_control"]["wrong_anchor_control"]
            self.assertEqual(wrong["counterfactual_accuracy"]["value"], 1.0)
            self.assertEqual(wrong["factual_leakage"]["value"], 0.0)

    def test_exact_compiler_polar_full_sensitivity_panel(self) -> None:
        result = probe.evaluate_checkpoint(
            "polar_supervised",
            101,
            exact_compiler_arrays(),
            probe.regenerate_null_bank(),
        )
        self.assertEqual(result["clean_semantic_endpoint"]["task_accuracy"]["value"], 1.0)
        self.assertLessEqual(
            result["operator_construction"]["maximum_orthogonality_defect_frobenius"],
            1e-6,
        )
        for prefix in result["prefixes"].values():
            for name in probe.INTERVENTIONS[:-1]:
                self.assertEqual(prefix["conditions"][name]["task_accuracy"]["value"], 1.0)
            wrong = prefix["conditions"]["wrong_anchor_control"]["wrong_anchor_control"]
            self.assertEqual(wrong["counterfactual_accuracy"]["value"], 1.0)
            self.assertEqual(wrong["factual_leakage"]["value"], 0.0)


if __name__ == "__main__":
    unittest.main()
