#!/usr/bin/env python3
"""Global learned-output-free contract tests for Neuralese v0.3.1.

Author: Komorebi P.

These tests must remain synthetic or symbolic.  They may hash checkpoint bytes,
but they must never call the restricted checkpoint loader or execute a learned
endpoint.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import freeze_v031 as freeze


DEFAULT_PACKAGE = Path(__file__).resolve().parent.parent
PACKAGE_ROOT = Path(os.environ.get("KOMOREBI_V031_PACKAGE_ROOT", DEFAULT_PACKAGE)).resolve()
V031 = PACKAGE_ROOT / "v031"

for directory in (V031, PACKAGE_ROOT):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

entry = importlib.import_module("entry_recurrence_probe")
spectroscopy = importlib.import_module("holonomy_spectroscopy")
runner = importlib.import_module("run_v031")


class _ToyWeights:
    def __init__(self) -> None:
        self.state_embedding = np.eye(8, dtype=np.float32)
        transpose_encoder = np.zeros((64, 64), dtype=np.float32)
        for row in range(8):
            for column in range(8):
                transpose_encoder[row * 8 + column, column * 8 + row] = 1.0
        self.operator_encoder = transpose_encoder
        self.decoder = np.eye(8, dtype=np.float32)

    def validate(self) -> None:
        return None


class _ToyCore:
    @staticmethod
    def encode_tables(weights, tables, dtype):
        requested = np.dtype(dtype)
        values = np.asarray(tables, dtype=requested)
        flat = values.reshape(-1, 64)
        encoded = flat @ weights.operator_encoder.astype(requested).T
        return encoded.reshape(values.shape)


def _permutation_matrix(mapping: tuple[int, ...]) -> np.ndarray:
    matrix = np.zeros((8, 8), dtype=np.float64)
    matrix[np.asarray(mapping, dtype=np.int64), np.arange(8)] = 1.0
    return matrix


class FrozenInputContractTests(unittest.TestCase):
    def test_prefreeze_validation_record_is_synthetic_and_complete(self) -> None:
        result = freeze.validate_prefreeze_validation(
            V031 / "V031_PREFREEZE_VALIDATION.json"
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["unit_test_count"], 75)

    def test_frozen_episode_serialization(self) -> None:
        result = freeze.validate_frozen_inputs(V031 / "V031_FROZEN_INPUTS.json")
        self.assertTrue(result["passed"])
        self.assertEqual(result["episode_count"], 16)
        self.assertEqual(result["operator_table_count"], 32)

    def test_base_transversal_covers_d4_exactly_once(self) -> None:
        value = json.loads((V031 / "V031_FROZEN_INPUTS.json").read_text(encoding="utf-8"))
        words = value["base_transversal"]["words"]
        actions = [freeze.d4_word_action(words[name]) for name in freeze.EXPECTED_ENDPOINT_NAMES]
        self.assertEqual(len(set(actions)), 8)
        self.assertTrue(all(words[name] for name in freeze.EXPECTED_ENDPOINT_NAMES))
        self.assertEqual(value["base_transversal"]["base_case_count_per_episode"], 8 * 8)

    def test_frozen_episode_self_hash_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "inputs.json"
            value = json.loads((V031 / "V031_FROZEN_INPUTS.json").read_text(encoding="utf-8"))
            value["checkpoints"]["0"]["episodes"][0]["phi"][0:2] = value["checkpoints"]["0"]["episodes"][0]["phi"][1::-1]
            candidate.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(freeze.FreezeValidationError, "self-hash mismatch"):
                freeze.validate_frozen_inputs(candidate)

    def test_frozen_episode_generator_replay_matches_serialization(self) -> None:
        generator = importlib.import_module("generate_v031_inputs")
        observed = json.loads((V031 / "V031_FROZEN_INPUTS.json").read_text(encoding="utf-8"))
        regenerated = generator.generate_inputs()
        self.assertEqual(freeze.canonical_json_bytes(observed), freeze.canonical_json_bytes(regenerated))


class MatchedWordBankContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = V031 / "V031_MATCHED_WORD_BANK.json"
        if not cls.path.is_file():
            raise unittest.SkipTest("V031_MATCHED_WORD_BANK.json not integrated yet")

    def test_bank_self_hash_counts_and_endpoints(self) -> None:
        result = freeze.validate_matched_word_bank(self.path)
        self.assertTrue(result["passed"])
        self.assertEqual(result["record_count"], 12)
        self.assertEqual(result["exact_length_control_word_count"], 48)

    def test_bank_has_complete_relation_budget_grid(self) -> None:
        bank = json.loads(self.path.read_text(encoding="utf-8"))
        pairs = {(record["relation"], record["budget"]) for record in bank["records"]}
        expected = {
            (relation, budget)
            for relation in freeze.EXPECTED_RELATIONS
            for budget in freeze.EXPECTED_BUDGETS
        }
        self.assertEqual(pairs, expected)

    def test_bank_self_hash_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "bank.json"
            value = json.loads(self.path.read_text(encoding="utf-8"))
            value["records"][0]["reference_word"][0] ^= 1
            candidate.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(freeze.FreezeValidationError, "self-hash mismatch"):
                freeze.validate_matched_word_bank(candidate)

    def test_runner_condition_index_is_exact_60_with_54_unique_words(self) -> None:
        bank = json.loads(self.path.read_text(encoding="utf-8"))
        conditions = runner.matched_condition_index(bank)
        self.assertEqual(len(conditions), 60)
        self.assertEqual(len({record["condition_id"] for record in conditions}), 60)
        self.assertEqual(len({record["word_id"] for record in conditions}), 54)

    def test_registered_severity_order_is_lexicographic(self) -> None:
        mild = {"severity": [1, 4, 2.0]}
        more_failures = {"severity": [2, 0, 0.0]}
        more_reveals = {"severity": [1, 5, 0.0]}
        worse_margin = {"severity": [1, 4, 3.0]}
        self.assertGreater(runner._severity(more_failures), runner._severity(mild))
        self.assertGreater(runner._severity(more_reveals), runner._severity(mild))
        self.assertGreater(runner._severity(worse_margin), runner._severity(mild))


class SyntheticExactRepresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.maps = np.asarray([freeze._R, freeze._F], dtype=np.int64)
        cls.codes = np.stack([_permutation_matrix(tuple(mapping)) for mapping in cls.maps])
        cls.decoder = np.eye(8, dtype=np.float64)
        cls.anchors = np.eye(8, dtype=np.float64)

    def test_exact_d4_relations_are_identity_matrices(self) -> None:
        for name, word in freeze.EXPECTED_RELATIONS.items():
            with self.subTest(relation=name):
                product = spectroscopy.word_product(self.codes, word)
                np.testing.assert_allclose(product, np.eye(8), atol=0.0, rtol=0.0)
                scalar = spectroscopy.nearest_positive_scalar_identity(product)
                self.assertEqual(scalar["frobenius_residual"], 0.0)

    def test_exact_representation_survives_decision_cone(self) -> None:
        result = spectroscopy.decision_cone_survival(
            self.codes,
            self.maps,
            self.decoder,
            self.anchors,
            np.arange(8, dtype=np.int64),
            8,
        )
        self.assertTrue(result["all_cases_survive"])
        self.assertTrue(all(event is None for event in result["first_failure"]))

    def test_exact_grouped_and_stepwise_relation_execution_agree(self) -> None:
        for name, word in freeze.EXPECTED_RELATIONS.items():
            with self.subTest(relation=name):
                comparison = spectroscopy.compare_generator_and_block_execution(
                    self.codes, self.anchors, word, 16
                )
                self.assertLessEqual(comparison["maximum_unit_l2"], 1e-15)
                self.assertLessEqual(comparison["maximum_positive_ray_angle"], 1e-15)

    def test_exact_entry_routes_collapse_to_native_anchors(self) -> None:
        tables = np.eye(8, dtype=np.float32)[self.maps]
        batch = SimpleNamespace(
            tables=tables[None, ...],
            maps=self.maps[None, ...],
            canonical_to_slot=np.array([[0, 1]], dtype=np.int64),
        )
        native, incoming, codes, maps = entry.incoming_representatives(
            _ToyWeights(), batch.tables[0], batch.maps[0], batch.canonical_to_slot[0], _ToyCore
        )
        np.testing.assert_allclose(incoming[0], native, atol=0.0, rtol=0.0)
        np.testing.assert_allclose(incoming[1], native, atol=0.0, rtol=0.0)
        tree = entry.enumerate_suffix_tree(
            np.stack((native, incoming[0], incoming[1])), codes, maps, np.eye(8), 8
        )
        for scheme in range(3):
            self.assertTrue(entry.scheme_summary(tree, scheme, 8)["strict_hard_pass"])


class FreezeTamperTests(unittest.TestCase):
    def test_digest_map_accepts_exact_bytes_and_rejects_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "scientific.py"
            path.write_bytes(b"registered\n")
            digest_map = {"scientific.py": freeze.file_sha256(path)}
            self.assertEqual(freeze.validate_digest_map(root, digest_map), digest_map)
            path.write_bytes(b"tampered\n")
            with self.assertRaisesRegex(freeze.FreezeValidationError, "digest mismatch"):
                freeze.validate_digest_map(root, digest_map)

    def test_digest_map_rejects_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(freeze.FreezeValidationError, "unsafe frozen path"):
                freeze.validate_digest_map(Path(temporary), {"../escape": "0" * 64})

    def test_execution_freeze_rejects_missing_and_extra_file_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            v031 = root / "v031"
            v031.mkdir()
            freeze_path = v031 / freeze.TARGET_NAME
            value = {
                "schema": freeze.SCHEMA,
                "version": freeze.VERSION,
                "author": freeze.AUTHOR,
                "status": "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION",
                "attestation": freeze.EXPECTED_ATTESTATION,
                "runtime_contract": {
                    "python_implementation": freeze.EXPECTED_PYTHON_IMPLEMENTATION,
                    "python_version": freeze.EXPECTED_PYTHON_VERSION,
                    "numpy_version": freeze.EXPECTED_NUMPY_VERSION,
                },
                "design_disclosure": {
                    "path": "DESIGN_DISCLOSURE.json",
                    "old_930000_931000_spectroscopy_and_continuations": (
                        "exploratory_design_context_only"
                    ),
                    "fresh_940000_941000_endpoints": (
                        "prospective_relative_to_exact_frozen_realizations"
                    ),
                    "confirmatory": False,
                },
                "files": {"unexpected.txt": "0" * 64},
            }
            freeze_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(freeze.FreezeValidationError, "key mismatch"):
                freeze.validate_execution_freeze(freeze_path, root)

    def test_atomic_creation_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "freeze.json"
            freeze._atomic_create_json(target, {"first": True})
            with self.assertRaises(FileExistsError):
                freeze._atomic_create_json(target, {"second": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"first": True})


class ExecutionBoundaryTests(unittest.TestCase):
    def test_imported_runner_cannot_cross_authenticated_cli_boundary(self) -> None:
        self.assertFalse(runner._BOOTSTRAP_AUTHENTICATED)
        with self.assertRaisesRegex(RuntimeError, "authenticated direct CLI"):
            runner.run_registered()

    def test_runtime_and_requirements_are_exactly_pinned(self) -> None:
        self.assertEqual(runner.EXPECTED_PYTHON_IMPLEMENTATION, "CPython")
        self.assertEqual(runner.EXPECTED_PYTHON_VERSION, "3.12.13")
        self.assertEqual(runner.EXPECTED_NUMPY_VERSION, "2.3.5")
        self.assertTrue(runner._validate_runtime_contract()["passed"])
        self.assertEqual(
            (V031 / "requirements.txt").read_text(encoding="utf-8"),
            "numpy==2.3.5\n",
        )

    def test_bootstrap_byte_set_matches_global_freeze_declaration(self) -> None:
        self.assertEqual(
            runner._BOOTSTRAP_REQUIRED_FILES,
            frozenset(freeze.REQUIRED_ROOT_RELATIVE_FILES),
        )

    def test_retired_entry_probe_cannot_access_learned_endpoints(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "run_probe is disabled"):
            entry.run_probe(Path("does-not-need-to-exist"), 1, 1)

    def test_any_prior_execution_artifact_blocks_a_run(self) -> None:
        old_paths = (
            runner.RUN_STARTED_PATH,
            runner.INVALID_ATTEMPT_PATH,
            runner.RESULT_PATH,
        )
        try:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                candidates = (
                    root / "started.json",
                    root / "invalid.json",
                    root / "result.json",
                )
                for selected in range(3):
                    for path in candidates:
                        if path.exists():
                            path.unlink()
                    candidates[selected].write_text("{}\n", encoding="utf-8")
                    runner.RUN_STARTED_PATH = candidates[0]
                    runner.INVALID_ATTEMPT_PATH = candidates[1]
                    runner.RESULT_PATH = candidates[2]
                    with self.assertRaisesRegex(FileExistsError, "artifact already exists"):
                        runner._refuse_existing_execution_artifacts()
        finally:
            (
                runner.RUN_STARTED_PATH,
                runner.INVALID_ATTEMPT_PATH,
                runner.RESULT_PATH,
            ) = old_paths

    def test_run_started_ledger_is_atomic_and_single_use(self) -> None:
        old_paths = (
            runner.RUN_STARTED_PATH,
            runner.INVALID_ATTEMPT_PATH,
            runner.RESULT_PATH,
        )
        try:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                runner.RUN_STARTED_PATH = root / "started.json"
                runner.INVALID_ATTEMPT_PATH = root / "invalid.json"
                runner.RESULT_PATH = root / "result.json"
                validation = runner._create_run_started_ledger(
                    {"freeze_sha256": "a" * 64}
                )
                self.assertTrue(validation["passed"])
                self.assertEqual(
                    json.loads(runner.RUN_STARTED_PATH.read_text(encoding="utf-8"))[
                        "status"
                    ],
                    "CREATED_BEFORE_LEARNED_CHECKPOINT_LOADING",
                )
                with self.assertRaises(FileExistsError):
                    runner._create_run_started_ledger({"freeze_sha256": "a" * 64})
        finally:
            (
                runner.RUN_STARTED_PATH,
                runner.INVALID_ATTEMPT_PATH,
                runner.RESULT_PATH,
            ) = old_paths

    def test_H2_requires_one_cell_to_cover_all_four_strata(self) -> None:
        split_cells = [
            {"checkpoint_seed": 0, "episode_half": "first", "relation": "f2", "repeat_count": 1},
            {"checkpoint_seed": 0, "episode_half": "second", "relation": "f2", "repeat_count": 1},
            {"checkpoint_seed": 1, "episode_half": "first", "relation": "r4", "repeat_count": 1},
            {"checkpoint_seed": 1, "episode_half": "second", "relation": "r4", "repeat_count": 1},
        ]
        self.assertEqual(runner._replicated_exit_cells(split_cells), [])
        same_cell = [
            {"checkpoint_seed": seed, "episode_half": half, "relation": "frfr", "repeat_count": 4}
            for seed in (0, 1)
            for half in ("first", "second")
        ]
        qualifying = runner._replicated_exit_cells(same_cell)
        self.assertEqual(len(qualifying), 1)
        self.assertEqual(qualifying[0]["relation"], "frfr")
        self.assertEqual(qualifying[0]["repeat_count"], 4)

    def test_M0_failure_invalidates_classification_without_hiding_raw_flags(self) -> None:
        raw = {"X0": True, "X1": False}
        self.assertEqual(
            runner._condition_diagnostic_predicates(raw, False),
            {"X0": None, "X1": None},
        )
        self.assertEqual(runner._condition_diagnostic_predicates(raw, True), raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
