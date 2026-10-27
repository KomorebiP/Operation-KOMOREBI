"""Structural tests for the v0.3.2 execution-correction layer.

Author: Komorebi P.

These tests do not deserialize checkpoints or evaluate learned endpoints.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from v032 import freeze_v032 as freeze
from v032 import run_v032 as runner


ROOT = Path(__file__).resolve().parent.parent


class V032CorrectionContractTests(unittest.TestCase):
    def test_v031_abort_evidence_is_preserved_before_ledger(self) -> None:
        observed = freeze.validate_v031_abort_evidence(ROOT)
        runtime_observed = runner._validate_v031_abort_evidence()
        self.assertTrue(observed["passed"])
        self.assertTrue(observed["run_started_ledger_absent"])
        self.assertTrue(observed["registered_result_absent"])
        self.assertEqual(
            observed["invalid_attempt_sha256"],
            freeze.EXPECTED_V031_INVALID_SHA256,
        )
        self.assertEqual(runtime_observed, observed)

    def test_nested_v031_freeze_authenticates_all_scientific_bytes(self) -> None:
        structural_only = (
            os.environ.get("KOMOREBI_V032_PREENDPOINT_STRUCTURAL_ONLY") == "1"
        )
        observed = freeze.validate_v031_frozen_bytes(
            ROOT, include_checkpoint_bytes=not structural_only
        )
        self.assertTrue(observed["passed"])
        self.assertEqual(observed["frozen_file_count"], 27)
        self.assertEqual(observed["validated_file_count"], 25 if structural_only else 27)
        self.assertEqual(
            observed["freeze_sha256"],
            freeze.EXPECTED_V031_EXECUTION_FREEZE_SHA256,
        )

    def test_lineage_runner_provenance_is_triply_consistent(self) -> None:
        observed = freeze.validate_lineage_provenance(ROOT)
        self.assertTrue(observed["passed"])
        self.assertEqual(
            observed["runner_sha256"],
            "1557b5c31a548c6af8c2da22ca63035e51a61267eed1d9bcf53f09ec1a841e94",
        )

    def test_corrected_lineage_accepts_actual_record_and_derives_merge(self) -> None:
        with (ROOT / "results" / "LINEAGE_REGRESSION.json").open(
            "r", encoding="utf-8"
        ) as handle:
            payload = json.load(handle)
        observed = runner._validate_lineage_payload(payload)
        self.assertTrue(observed["passed"])
        self.assertEqual(
            observed["seeds"]["0"]["derived_maximum_merge_multiplicity"], 1
        )
        self.assertEqual(
            observed["seeds"]["1"]["derived_maximum_merge_multiplicity"], 1
        )
        self.assertNotIn("maximum_merge_multiplicity", payload["seeds"]["0"])

    def test_corrected_lineage_rejects_episode_merge_violation(self) -> None:
        with (ROOT / "results" / "LINEAGE_REGRESSION.json").open(
            "r", encoding="utf-8"
        ) as handle:
            payload = json.load(handle)
        mutated = copy.deepcopy(payload)
        mutated["seeds"]["0"]["episodes"][7]["maximum_merge_multiplicity"] = 2
        with self.assertRaisesRegex(ValueError, "maximum_merge_multiplicity"):
            runner._validate_lineage_payload(mutated)

    def test_corrected_lineage_rejects_seed_aggregate_violation(self) -> None:
        with (ROOT / "results" / "LINEAGE_REGRESSION.json").open(
            "r", encoding="utf-8"
        ) as handle:
            payload = json.load(handle)
        mutated = copy.deepcopy(payload)
        mutated["seeds"]["1"]["decision_count"] = 61_439
        with self.assertRaisesRegex(ValueError, "decision_count"):
            runner._validate_lineage_payload(mutated)

    def test_corrected_lineage_rejects_unregistered_root_field(self) -> None:
        with (ROOT / "results" / "LINEAGE_REGRESSION.json").open(
            "r", encoding="utf-8"
        ) as handle:
            payload = json.load(handle)
        mutated = copy.deepcopy(payload)
        mutated["unregistered"] = True
        with self.assertRaisesRegex(ValueError, "root keys changed"):
            runner._validate_lineage_payload(mutated)

    def test_preregistration_reuses_exact_scientific_profile_and_claims(self) -> None:
        observed = freeze.validate_preregistration(
            ROOT / "v032" / "V032_PREREGISTRATION.json"
        )
        self.assertTrue(observed["passed"])
        self.assertEqual(runner.CLAIM_BOUNDARY, freeze.EXPECTED_CLAIM_BOUNDARY)

    def test_runner_delegates_every_scientific_module_to_frozen_v031(self) -> None:
        observed = freeze.validate_runner_contract(ROOT)
        self.assertTrue(observed["passed"])
        self.assertEqual(observed["delegated_module_count"], 5)
        self.assertLess(
            observed["ledger_call_line"], observed["checkpoint_snapshot_call_line"]
        )
        self.assertEqual(observed["restricted_loader_call_count"], 1)

    def test_bootstrap_authentication_precedes_numpy_import(self) -> None:
        observed = freeze.validate_runner_contract(ROOT)
        self.assertTrue(observed["passed"])
        self.assertEqual(observed["exact_path_local_module_count"], 9)
        self.assertLess(
            observed["isolated_mode_guard_line"],
            observed["ledger_call_line"],
        )
        self.assertGreater(observed["freeze_isolated_mode_guard_line"], 0)

    def test_imported_runner_cannot_cross_execution_boundary(self) -> None:
        self.assertFalse(runner._BOOTSTRAP_AUTHENTICATED)
        with self.assertRaisesRegex(RuntimeError, "authenticated direct CLI"):
            runner.run_registered()
        with tempfile.TemporaryDirectory(prefix="komorebi-v032-lock-test-") as tmp:
            fake_here = Path(tmp)
            lock_target = fake_here / "V032_EXECUTION_FREEZE.json"
            lock_target.write_text("frozen\n", encoding="utf-8")
            original_here = runner.HERE
            try:
                runner.HERE = fake_here
                descriptor = runner._acquire_execution_lock()
                try:
                    contender = subprocess.run(
                        [
                            sys.executable,
                            "-I",
                            "-B",
                            "-c",
                            (
                                "import fcntl,os,sys\n"
                                "fd=os.open(sys.argv[1],os.O_RDONLY)\n"
                                "try:\n"
                                " fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)\n"
                                "except BlockingIOError:\n"
                                " raise SystemExit(0)\n"
                                "raise SystemExit(1)\n"
                            ),
                            str(lock_target),
                        ],
                        check=False,
                    )
                    self.assertEqual(contender.returncode, 0)
                finally:
                    runner._release_execution_lock(descriptor)
            finally:
                runner.HERE = original_here
        with tempfile.TemporaryDirectory(prefix="komorebi-v032-source-test-") as tmp:
            source = Path(tmp) / "retained_source.py"
            authenticated = b"VALUE = 'authenticated'\n"
            source.write_bytes(authenticated)
            original_authenticated = runner._BOOTSTRAP_AUTHENTICATED
            original_sources = runner._AUTHENTICATED_PYTHON_SOURCE_BYTES
            module_name = "_komorebi_v032_retained_source_test"
            try:
                runner._BOOTSTRAP_AUTHENTICATED = True
                runner._AUTHENTICATED_PYTHON_SOURCE_BYTES = {
                    source.resolve(): authenticated
                }
                source.write_text("VALUE = 'mutated'\n", encoding="utf-8")
                module = runner._load_registered_local_module(module_name, source)
                self.assertEqual(module.VALUE, "authenticated")
            finally:
                sys.modules.pop(module_name, None)
                runner._AUTHENTICATED_PYTHON_SOURCE_BYTES = original_sources
                runner._BOOTSTRAP_AUTHENTICATED = original_authenticated

    def test_local_import_shadow_check_passes(self) -> None:
        observed = runner._reject_local_import_shadowing()
        self.assertTrue(observed["passed"])
        self.assertEqual(observed["registered_module_count"], 11)

    def test_requirements_are_exactly_pinned(self) -> None:
        observed = freeze.validate_requirements(ROOT)
        self.assertTrue(observed["passed"])
        self.assertEqual(observed["content"], "numpy==2.3.5")

    def test_import_creates_no_v032_execution_artifact(self) -> None:
        self.assertFalse(runner.RUN_STARTED_PATH.exists())
        self.assertFalse(runner.INVALID_ATTEMPT_PATH.exists())
        self.assertFalse(runner.RESULT_PATH.exists())

    def test_v032_paths_do_not_alias_v031_artifacts(self) -> None:
        self.assertNotEqual(runner.RUN_STARTED_PATH, runner.V031_RUN_STARTED_PATH)
        self.assertNotEqual(runner.RESULT_PATH, runner.V031_RESULT_PATH)
        self.assertNotEqual(runner.INVALID_ATTEMPT_PATH, runner.V031_INVALID_ATTEMPT_PATH)


if __name__ == "__main__":
    unittest.main()
