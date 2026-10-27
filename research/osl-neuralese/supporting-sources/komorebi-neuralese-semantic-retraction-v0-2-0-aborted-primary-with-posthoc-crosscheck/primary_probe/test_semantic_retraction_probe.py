from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np
import torch

import run_semantic_retraction_probe as probe


class SemanticRetractionCheckpointFreeTests(unittest.TestCase):
    """Scientific and execution-firewall tests that never load a checkpoint."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.api = probe.import_v04_api(probe.DEFAULT_PACKAGE)
        cls.maps = cls.api["canonical_maps"]("d4").astype(np.int64)
        cls.context_banks = probe.make_disjoint_context_banks(
            cls.api["EpisodeGenerator"]
        )
        cls.path_banks = probe.make_disjoint_path_banks(cls.maps)
        cls.continuations = probe.make_continuation_bank()

    @staticmethod
    def exact_prototypes(model: probe.ExactCompiledModel) -> probe.PrototypeBundle:
        anchors = model.state_anchors()
        return probe.PrototypeBundle(
            torch32=anchors.clone(),
            numpy64=anchors.detach().cpu().numpy().astype(np.float64),
            audit={"source": "unit exact chart", "pass": True},
        )

    @staticmethod
    def synthetic_claim_inputs() -> tuple[dict[str, object], dict[str, object]]:
        """Minimal genuine gate inputs that derive the frozen 11-label matrix."""

        autonomous = {
            condition: {
                "pass": True,
                "structural_prerequisites_pass": True,
                "state_specificity": {"pass": True},
                "accuracy_margin_over_random_ray": 0.20,
            }
            for condition in ("self_anchor", "nearest_anchor", "self_prototype")
        }
        one_shot = {
            "fixed_gate_inputs": {
                "native_finite_decision_trace_agreement_h4_coverage_0_99": {
                    "pass": True
                },
                "native_finite_logit_trace_agreement_h4_p95": {"pass": True},
                "oracle": {
                    "oracle_anchor": {"pass": True},
                    "oracle_prototype": {"pass": True},
                },
                "autonomous": autonomous,
            }
        }
        periodic = {
            "fixed_behavioral_gate_inputs": {
                "self_anchor": {"behavioral_pass": True},
                "nearest_anchor": {"behavioral_pass": True},
                "self_prototype": {"behavioral_pass": True},
                "anchor_projection": {"behavioral_pass": True},
            }
        }
        return one_shot, periodic

    @staticmethod
    def write_json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def copy_census_without_loading(destination: Path) -> None:
        """Copy only manifest-bound census bytes; never deserialize a tensor."""

        source = probe.DEFAULT_PACKAGE
        shutil.copy2(source / "MANIFEST.json", destination / "MANIFEST.json")
        result_relative = Path("results/packet_closure_pilot")
        source_result = source / result_relative
        target_result = destination / result_relative
        (target_result / "checkpoints").mkdir(parents=True)
        shutil.copy2(
            source_result / "CHECKPOINT_SEAL.json",
            target_result / "CHECKPOINT_SEAL.json",
        )
        seal = json.loads(
            (source_result / "CHECKPOINT_SEAL.json").read_text(encoding="utf-8")
        )
        for record in seal["checkpoints"]:
            relative = Path(str(record["path"]))
            target = target_result / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_result / relative, target)

    @staticmethod
    def make_valid_synthetic_result_bundle(bundle: Path) -> dict[str, object]:
        """Create a tiny, internally consistent 4 x 3 bundle with no model data."""

        bundle.mkdir()
        checkpoint_directory = bundle / probe.CHECKPOINT_DIRECTORY_NAME
        checkpoint_directory.mkdir()
        checkpoint_descriptors = []
        run_checkpoint_records = []
        shards: dict[str, dict[str, object]] = {}
        for arm in probe.REQUIRED_ARMS:
            for seed in probe.REQUIRED_SEEDS:
                relative = (
                    f"{probe.CHECKPOINT_DIRECTORY_NAME}/{arm}__seed_{seed}.json"
                )
                path = bundle / relative
                checkpoint_filename = f"{arm}_seed{seed}.pt"
                checkpoint_sha256 = hashlib.sha256(
                    checkpoint_filename.encode("utf-8")
                ).hexdigest()
                one_shot, periodic = (
                    SemanticRetractionCheckpointFreeTests.synthetic_claim_inputs()
                )
                independent_claim_matrix = probe.build_independent_claim_matrix(
                    one_shot, periodic
                )
                independent_digest = hashlib.sha256(
                    (checkpoint_filename + ":independent").encode("utf-8")
                ).hexdigest()
                sealed_digest = hashlib.sha256(
                    (checkpoint_filename + ":sealed").encode("utf-8")
                ).hexdigest()
                state_control = {
                    "independent_digest_before": independent_digest,
                    "independent_digest_after": independent_digest,
                    "seal_compatible_digest_before": sealed_digest,
                    "seal_compatible_digest_after": sealed_digest,
                    "sealed_digest": sealed_digest,
                    "unchanged": True,
                    "seal_match": True,
                }
                shard = {
                    "schema": (
                        "komorebi.neuralese.semantic_retraction_checkpoint_result.v1"
                    ),
                    "version": probe.VERSION,
                    "author": probe.AUTHOR,
                    "arm": arm,
                    "seed": seed,
                    "model_family": (
                        "polar" if arm.startswith("polar_") else "raw"
                    ),
                    "checkpoint_filename": checkpoint_filename,
                    "checkpoint_sha256": checkpoint_sha256,
                    "whole_analysis_state_dict_control": state_control,
                    "prototype_audit": {"pass": True, "unit_fixture": True},
                    "one_shot_primary": one_shot,
                    "one_shot_stress_descriptive": {"unit_fixture": True},
                    "periodic": periodic,
                    "independent_claim_matrix": independent_claim_matrix,
                }
                shards[relative] = shard
                shard_sha = probe._write_json_exclusive(path, shard)
                checkpoint_descriptors.append(
                    {
                        "arm": arm,
                        "seed": seed,
                        "path": relative,
                        "sha256": shard_sha,
                    }
                )
                run_checkpoint_records.append(
                    {
                        "arm": arm,
                        "seed": seed,
                        "model_family": (
                            "polar" if arm.startswith("polar_") else "raw"
                        ),
                        "checkpoint_filename": checkpoint_filename,
                        "checkpoint_sha256": checkpoint_sha256,
                        "checkpoint_shard": relative,
                        "checkpoint_shard_sha256": shard_sha,
                        "checkpoint_shard_bytes": path.stat().st_size,
                        "whole_analysis_state_dict_unchanged": True,
                        "independent_claim_matrix": independent_claim_matrix,
                    }
                )

        exact = {
            "schema": "komorebi.neuralese.semantic_retraction_exact_control.v1",
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "source": "synthetic checkpoint-free unit fixture",
            "torch_thread_runtime": dict(probe.FROZEN_TORCH_THREAD_RECEIPT),
            "context_bank": {"unit_fixture": True},
            "path_bank": {"unit_fixture": True},
            "continuation_bank": {"unit_fixture": True},
            "audit": {"pass": True},
            "result": {"unit_fixture": True},
            "periodic": {"unit_fixture": True, "pass": True},
        }
        exact_path = bundle / probe.EXACT_CONTROL_FILENAME
        exact_sha = probe._write_json_exclusive(exact_path, exact)
        exact_descriptor = {"path": probe.EXACT_CONTROL_FILENAME, "sha256": exact_sha}
        exact_summary = {
            "path": probe.EXACT_CONTROL_FILENAME,
            "sha256": exact_sha,
            "serialized_bytes": exact_path.stat().st_size,
            "audit": exact["audit"],
            "context_bank": exact["context_bank"],
            "path_bank": exact["path_bank"],
            "continuation_bank": exact["continuation_bank"],
        }

        root_receipt = {
            "artifact_sha256": {
                "analysis_protocol": "9" * 64,
                "primary_implementation": "a" * 64,
                "primary_tests": "b" * 64,
                "primary_machine_contract": "1" * 64,
                "primary_manifest_dry_run": "2" * 64,
                "primary_static_review": "3" * 64,
                "theoretical_framework": "4" * 64,
                "independent_crosscheck_protocol": "d" * 64,
                "independent_crosscheck_implementation": "e" * 64,
                "independent_crosscheck_tests": "f" * 64,
                "independent_crosscheck_freeze_receipt": "0" * 64,
            },
            "schema": "komorebi.neuralese.semantic_retraction.protocol_receipt.v1",
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "status": "FROZEN_BEFORE_LEARNED_OUTCOMES",
            "path": probe.ROOT_PROTOCOL_RECEIPT_PATH.name,
            "file_sha256": "5" * 64,
            "receipt_sha256": "6" * 64,
            "source_provenance": {
                "source_archive_sha256": probe.EXPECTED_ARCHIVE_SHA256,
                "source_package_manifest_sha256": (
                    probe.EXPECTED_PACKAGE_MANIFEST_SHA256
                ),
            },
        }
        static_review = {
            "schema": "komorebi.neuralese.semantic_retraction.static_review.v1",
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "status": "PASS",
            "protocol_sha256": "9" * 64,
            "theoretical_framework_sha256": "4" * 64,
            "implementation_sha256": "a" * 64,
            "test_sha256": "b" * 64,
            "machine_contract_sha256": "1" * 64,
            "manifest_file_sha256": "2" * 64,
            "manifest_freeze_receipt_sha256": "c" * 64,
            "checks": {
                name: True for name in probe.REQUIRED_STATIC_REVIEW_CHECKS
            },
        }
        protocol = {
            "path": "ANALYSIS_PROTOCOL.md",
            "sha256": "9" * 64,
            "implementation_sha256": "a" * 64,
            "test_sha256": "b" * 64,
            "status": "FROZEN_POSTHOC",
            "static_review": static_review,
            "root_protocol_receipt": root_receipt,
        }
        context_banks = {"evaluation": {"sha256": "d" * 64}}
        path_banks = {"evaluation": {"sha256": "e" * 64}}
        continuation_bank = {"sha256": "f" * 64}
        random_key_manifest = {"sha256": "0" * 64}
        spend = {
            "schema": "komorebi.neuralese.evaluation_bank_spend.v1",
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "status": "SPENT_BEFORE_FIRST_LEARNED_EVALUATION",
            "created_unix_time_ns": 1,
            "no_rerun_or_resume_is_prospective": True,
            "crash_after_this_receipt_still_spends_bank": True,
            "planned_bundle_leaf_name": bundle.name,
            "planned_bundle_absolute_path_non_normative": str(bundle.resolve()),
            "protocol_sha256": protocol["sha256"],
            "implementation_sha256": protocol["implementation_sha256"],
            "test_sha256": protocol["test_sha256"],
            "machine_contract_sha256": root_receipt["artifact_sha256"][
                "primary_machine_contract"
            ],
            "manifest_file_sha256": root_receipt["artifact_sha256"][
                "primary_manifest_dry_run"
            ],
            "manifest_freeze_receipt_sha256": protocol["static_review"][
                "manifest_freeze_receipt_sha256"
            ],
            "static_review_file_sha256": root_receipt["artifact_sha256"][
                "primary_static_review"
            ],
            "theoretical_framework_sha256": root_receipt["artifact_sha256"][
                "theoretical_framework"
            ],
            "root_protocol_receipt_file_sha256": root_receipt["file_sha256"],
            "root_protocol_receipt_internal_sha256": root_receipt[
                "receipt_sha256"
            ],
            "source_archive_sha256": root_receipt["source_provenance"][
                "source_archive_sha256"
            ],
            "source_package_manifest_sha256": root_receipt["source_provenance"][
                "source_package_manifest_sha256"
            ],
            "evaluation_context_sha256": context_banks["evaluation"]["sha256"],
            "evaluation_path_sha256": path_banks["evaluation"]["sha256"],
            "continuation_sha256": continuation_bank["sha256"],
            "random_key_manifest_sha256": random_key_manifest["sha256"],
            "exact_control_sha256": exact_sha,
        }
        spend["receipt_sha256"] = probe.canonical_json_digest(spend)
        spend_path = bundle / probe.SPEND_RECEIPT_FILENAME
        spend_sha = probe._write_json_exclusive(spend_path, spend)
        spend_descriptor = {
            "path": probe.SPEND_RECEIPT_FILENAME,
            "sha256": spend_sha,
        }

        arm_claim_matrix = probe.aggregate_arm_claim_matrices(
            run_checkpoint_records
        )
        census = [
            {
                "arm": record["arm"],
                "seed": record["seed"],
                "checkpoint_sha256": record["checkpoint_sha256"],
                "sealed_state_dict_digest": shards[
                    record["checkpoint_shard"]
                ]["whole_analysis_state_dict_control"]["sealed_digest"],
            }
            for record in sorted(
                run_checkpoint_records,
                key=lambda row: (row["arm"], row["seed"]),
            )
        ]
        census_sha256 = probe.canonical_json_digest(census)
        source_integrity = {
            "archive_sha256_binding": probe.EXPECTED_ARCHIVE_SHA256,
            "manifest_sha256": probe.EXPECTED_PACKAGE_MANIFEST_SHA256,
            "source_file_count": 1,
            "ordered_source_receipt_sha256": "8" * 64,
        }
        loaded_modules = [
            {
                "module": "komorebi_neuralese",
                "source_path": "src/komorebi_neuralese/__init__.py",
                "sha256": "6" * 64,
            }
        ]
        loaded_module_digest = hashlib.sha256()
        for module_record in loaded_modules:
            loaded_module_digest.update(
                module_record["module"].encode("utf-8") + b"\0"
            )
            loaded_module_digest.update(
                module_record["source_path"].encode("utf-8") + b"\0"
            )
            loaded_module_digest.update(
                module_record["sha256"].encode("ascii") + b"\0"
            )
        checkpoint_seal_sha256 = "7" * 64
        source = {
            "archive_filename": probe.DEFAULT_ARCHIVE.name,
            "archive_absolute_path_non_normative": str(
                probe.DEFAULT_ARCHIVE.resolve()
            ),
            "archive_sha256": probe.EXPECTED_ARCHIVE_SHA256,
            "archive_verified": True,
            "package_source_integrity": source_integrity,
            "sealed_import_origin_receipt": {
                "sealed_source_root_forced_to_sys_path_zero": True,
                "loaded_module_count": 1,
                "loaded_modules": loaded_modules,
                "ordered_loaded_module_receipt_sha256": (
                    loaded_module_digest.hexdigest()
                ),
            },
            "checkpoint_seal_sha256": checkpoint_seal_sha256,
            "checkpoint_seal_manifest_binding": {
                "path": "results/packet_closure_pilot/CHECKPOINT_SEAL.json",
                "size": 1,
                "sha256": checkpoint_seal_sha256,
                "manifest_sha256": probe.EXPECTED_PACKAGE_MANIFEST_SHA256,
            },
            "official_checkpoint_count": 12,
            "seal_receipt_count": 12,
            "all_checkpoint_receipts_verified": True,
            "all_checkpoint_files_bound_to_sealed_package_manifest": True,
            "weights_only_load": True,
            "checkpoint_load_bound_to_prehashed_bytes": True,
            "strict_state_load": True,
            "one_model_loaded_at_a_time": True,
            "closing_provenance_reverification": {
                "archive_sha256_before": probe.EXPECTED_ARCHIVE_SHA256,
                "archive_sha256_after": probe.EXPECTED_ARCHIVE_SHA256,
                "source_integrity_before": source_integrity,
                "source_integrity_after": source_integrity,
                "checkpoint_census_before_sha256": census_sha256,
                "checkpoint_census_after_sha256": census_sha256,
                "checkpoint_seal_sha256_before": checkpoint_seal_sha256,
                "checkpoint_seal_sha256_after": checkpoint_seal_sha256,
                "all_reverified_before_commit": True,
            },
        }
        run = {
            "schema": probe.SCHEMA,
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "analysis_status": probe.ANALYSIS_STATUS,
            "result_validity": "VALID_ONLY_WITH_COMMIT",
            "claim_boundary": probe.CLAIM_BOUNDARY,
            "protocol": protocol,
            "source": source,
            "runtime": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "torch": torch.__version__,
                "device": "cpu",
                "intraop_threads": probe.TORCH_INTRAOP_THREADS,
                "interop_threads": probe.TORCH_INTEROP_THREADS,
                "model_and_operator_forward_dtype": "torch.float32",
                "diagnostic_dtype_after_detach": "numpy.float64",
                "elapsed_seconds": 0.0,
                "observed_peak_resident_set_bytes": 1,
                "declared_peak_working_set_ceiling_bytes": (
                    probe.DECLARED_PEAK_WORKING_SET_CEILING_BYTES
                ),
                "observed_peak_within_declared_ceiling": True,
                "pre_spend_resource_firewall": {
                    "free_bytes_before_spend": (
                        probe.MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND
                    ),
                    "required_free_bytes_before_spend": (
                        probe.MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND
                    ),
                    "headroom_pass": True,
                    "manifest_budget_checks_pass": True,
                },
            },
            "context_banks": context_banks,
            "path_banks": path_banks,
            "continuation_bank": continuation_bank,
            "random_key_manifest": random_key_manifest,
            "checkpoint_results": run_checkpoint_records,
            "exact_compiled_control": exact_summary,
            "evaluation_bank_spend_receipt": spend,
            "arm_level_independent_claim_matrix": arm_claim_matrix,
            "output_layout": {
                "one_checkpoint_shard_written_before_next_model_load": True,
                "bundle_root": ".",
                "run": probe.RUN_FILENAME,
                "exact_control": probe.EXACT_CONTROL_FILENAME,
                "internal_spend_receipt": probe.SPEND_RECEIPT_FILENAME,
                "checkpoint_directory": probe.CHECKPOINT_DIRECTORY_NAME,
                "manifest": probe.BUNDLE_MANIFEST_FILENAME,
                "commit": probe.COMMIT_FILENAME,
                "all_paths_relative_and_portable": True,
                "commit_written_last": True,
            },
        }
        run_path = bundle / probe.RUN_FILENAME
        run_sha = probe._write_json_exclusive(run_path, run)
        run_descriptor = {"path": probe.RUN_FILENAME, "sha256": run_sha}

        manifest = {
            "schema": "komorebi.neuralese.semantic_retraction_result_bundle.v1",
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "status": "COMPLETE_PENDING_COMMIT",
            "result_validity": "VALID_ONLY_WITH_COMMIT",
            "run": run_descriptor,
            "exact_control": exact_descriptor,
            "exact_control_summary": exact_summary,
            "spend_receipt": spend_descriptor,
            "checkpoint_shards": checkpoint_descriptors,
            "required_checkpoint_cells": [
                {"arm": arm, "seed": seed}
                for arm in probe.REQUIRED_ARMS
                for seed in probe.REQUIRED_SEEDS
            ],
            "arm_level_independent_claim_matrix": arm_claim_matrix,
        }
        manifest_path = bundle / probe.BUNDLE_MANIFEST_FILENAME
        manifest_sha = probe._write_json_exclusive(manifest_path, manifest)
        manifest_descriptor = {
            "path": probe.BUNDLE_MANIFEST_FILENAME,
            "sha256": manifest_sha,
        }

        commit = {
            "schema": "komorebi.neuralese.semantic_retraction_result_commit.v1",
            "version": probe.VERSION,
            "author": probe.AUTHOR,
            "status": "COMMITTED",
            "result_validity": "VALID_ONLY_WITH_THIS_COMMIT",
            "run": run_descriptor,
            "bundle_manifest": manifest_descriptor,
            "exact_control": exact_descriptor,
            "spend_receipt": spend_descriptor,
            "checkpoint_shard_count": 12,
        }
        commit_path = bundle / probe.COMMIT_FILENAME
        probe._write_json_exclusive(commit_path, commit)
        return {
            "bundle": bundle,
            "run": run,
            "run_path": run_path,
            "manifest": manifest,
            "manifest_path": manifest_path,
            "commit": commit,
            "commit_path": commit_path,
            "checkpoint_descriptors": checkpoint_descriptors,
            "shards": shards,
            "spend": spend,
            "spend_path": spend_path,
        }

    @staticmethod
    def refresh_synthetic_result_bundle(fixture: dict[str, object]) -> None:
        """Rebind all outer hashes after a deliberate deep-fixture mutation."""

        spend = fixture["spend"]
        assert isinstance(spend, dict)
        spend.pop("receipt_sha256", None)
        spend["receipt_sha256"] = probe.canonical_json_digest(spend)
        spend_path = fixture["spend_path"]
        assert isinstance(spend_path, Path)
        SemanticRetractionCheckpointFreeTests.write_json(spend_path, spend)
        spend_descriptor = {
            "path": probe.SPEND_RECEIPT_FILENAME,
            "sha256": probe.sha256_file(spend_path),
        }

        run = fixture["run"]
        assert isinstance(run, dict)
        run["evaluation_bank_spend_receipt"] = spend
        arm_claim_matrix = probe.aggregate_arm_claim_matrices(
            run["checkpoint_results"]
        )
        run["arm_level_independent_claim_matrix"] = arm_claim_matrix
        run_path = fixture["run_path"]
        assert isinstance(run_path, Path)
        SemanticRetractionCheckpointFreeTests.write_json(run_path, run)
        run_descriptor = {
            "path": probe.RUN_FILENAME,
            "sha256": probe.sha256_file(run_path),
        }

        manifest = fixture["manifest"]
        assert isinstance(manifest, dict)
        manifest["run"] = run_descriptor
        manifest["spend_receipt"] = spend_descriptor
        manifest["arm_level_independent_claim_matrix"] = arm_claim_matrix
        manifest_path = fixture["manifest_path"]
        assert isinstance(manifest_path, Path)
        SemanticRetractionCheckpointFreeTests.write_json(manifest_path, manifest)
        manifest_descriptor = {
            "path": probe.BUNDLE_MANIFEST_FILENAME,
            "sha256": probe.sha256_file(manifest_path),
        }

        commit = fixture["commit"]
        assert isinstance(commit, dict)
        commit["run"] = run_descriptor
        commit["bundle_manifest"] = manifest_descriptor
        commit["spend_receipt"] = spend_descriptor
        commit_path = fixture["commit_path"]
        assert isinstance(commit_path, Path)
        SemanticRetractionCheckpointFreeTests.write_json(commit_path, commit)

    def test_runtime_contract_constants_match_machine_contract(self) -> None:
        contract = probe.load_machine_contract()
        self.assertEqual(
            set(contract),
            {
                "schema",
                "version",
                "author",
                "status",
                "normative_protocol",
                "normative_protocol_sha256",
                "runtime_contract",
                "execution_firewall",
            },
        )
        self.assertEqual(
            contract["schema"],
            "komorebi.neuralese.semantic_retraction_runtime_contract.v1",
        )
        self.assertEqual(contract["version"], probe.VERSION)
        self.assertEqual(probe.AUTHOR, "Komorebi P.")
        self.assertEqual(contract["author"], probe.AUTHOR)
        self.assertEqual(contract["normative_protocol"], "../ANALYSIS_PROTOCOL.md")
        self.assertIn(contract["status"], {"DRAFT_LOCKED", "FROZEN_POSTHOC"})
        probe.validate_protocol_matches_runtime(contract)
        for mutation in (
            {**contract, "schema": "unit.invalid"},
            {**contract, "version": "0.0.0"},
            {**contract, "author": "unit invalid"},
            {**contract, "normative_protocol": "wrong.md"},
            {**contract, "unexpected": True},
        ):
            with self.assertRaisesRegex(
                RuntimeError, "(top-level key set|metadata)"
            ):
                probe.validate_protocol_matches_runtime(mutation)
        boolean_as_integer = json.loads(json.dumps(contract))
        firewall_key = next(iter(boolean_as_integer["execution_firewall"]))
        boolean_as_integer["execution_firewall"][firewall_key] = 1
        with self.assertRaisesRegex(RuntimeError, "execution_firewall"):
            probe.validate_protocol_matches_runtime(boolean_as_integer)
        integer_as_boolean = json.loads(json.dumps(contract))
        integer_as_boolean["runtime_contract"]["torch_intraop_threads"] = True
        with self.assertRaisesRegex(RuntimeError, "runtime_contract"):
            probe.validate_protocol_matches_runtime(integer_as_boolean)
        firewall = contract["execution_firewall"]
        self.assertTrue(
            firewall[
                "saved_manifest_publication_or_overwrite_forbidden_after_spend_or_static_release"
            ]
        )
        self.assertNotIn(
            "manifest_regeneration_forbidden_after_spend_or_static_release",
            firewall,
        )
        if contract["status"] == "FROZEN_POSTHOC":
            self.assertEqual(
                contract["normative_protocol_sha256"],
                probe.sha256_file(probe.PROTOCOL_PATH),
            )

    def test_trust_roots_hash_and_parse_single_file_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            payload = b'{"schema":"unit.snapshot","value":1}\n'
            path.write_bytes(payload)
            value, digest, observed = probe.read_json_snapshot(
                path, label="unit snapshot"
            )
            self.assertEqual(value, {"schema": "unit.snapshot", "value": 1})
            self.assertEqual(observed, payload)
            self.assertEqual(digest, hashlib.sha256(payload).hexdigest())

            initial = probe.os.stat(path)
            changed = types.SimpleNamespace(
                st_mode=initial.st_mode,
                st_dev=initial.st_dev,
                st_ino=initial.st_ino,
                st_size=initial.st_size,
                st_mtime_ns=initial.st_mtime_ns + 1,
                st_ctime_ns=initial.st_ctime_ns,
            )
            with mock.patch.object(
                probe.os, "fstat", side_effect=(initial, changed)
            ):
                with self.assertRaisesRegex(RuntimeError, "changed while"):
                    probe.read_file_snapshot(path, label="mutating unit snapshot")

        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            probe.loads_json_bytes_strict(b'{"x":1,"x":2}')
        with self.assertRaisesRegex(ValueError, "nonfinite JSON"):
            probe.loads_json_bytes_strict(b'{"x":NaN}')
        snapshot_users = {
            probe.load_sealed_package_manifest: "read_json_snapshot",
            probe.load_machine_contract: "read_json_snapshot",
            probe.assert_manifest_matches_runtime: "read_json_snapshot",
            probe.validate_root_protocol_receipt: "read_json_snapshot",
            probe.assert_protocol_frozen: "read_file_snapshot",
        }
        for function, required_call in snapshot_users.items():
            with self.subTest(function=function.__name__):
                self.assertIn(required_call, inspect.getsource(function))

    def test_d4_generators_and_left_action_relations(self) -> None:
        expected = np.asarray(
            [
                [1, 2, 3, 0, 5, 6, 7, 4],
                [4, 7, 6, 5, 0, 3, 2, 1],
            ],
            dtype=np.int64,
        )
        np.testing.assert_array_equal(self.maps, expected)
        identity = np.arange(8, dtype=np.int64)
        for relation in ((0, 0, 0, 0), (1, 1), (1, 0, 1, 0)):
            np.testing.assert_array_equal(
                probe.state_map_for_word(self.maps, relation), identity
            )
        shortest = probe.lexicographic_shortest_representatives(self.maps)
        self.assertEqual(
            tuple(len(word) % 2 for word in shortest),
            (0, 1, 0, 1, 1, 0, 1, 0),
        )
        self.assertEqual(
            tuple(probe.apply_state_word(self.maps, 0, word) for word in shortest),
            tuple(range(8)),
        )
        self.assertEqual(probe.apply_state_word(self.maps, 0, (0, 1)), 7)
        np.testing.assert_array_equal(
            probe.state_map_for_word(self.maps, (0, 1)),
            np.array([7, 6, 5, 4, 3, 2, 1, 0], dtype=np.int64),
        )

    def test_context_banks_are_disjoint_deterministic_and_d4_equivariant(self) -> None:
        repeated = probe.make_disjoint_context_banks(self.api["EpisodeGenerator"])
        key_sets: dict[str, set[str]] = {}
        for split in ("prior", "calibration", "evaluation"):
            bank = self.context_banks[split]
            key_sets[split] = set(bank.keys)
            self.assertEqual(bank.tables.shape, (32, 2, 8, 8))
            self.assertEqual(bank.tables.dtype, np.float32)
            self.assertEqual(bank.maps.dtype, np.int64)
            self.assertEqual(bank.phi.dtype, np.int64)
            self.assertEqual(bank.canonical_to_slot.dtype, np.int64)
            self.assertEqual(len(key_sets[split]), 32)
            self.assertEqual(bank.receipt["sha256"], repeated[split].receipt["sha256"])
            self.assertEqual(
                bank.receipt["raw_tensor_sha256"],
                repeated[split].receipt["raw_tensor_sha256"],
            )
            np.testing.assert_array_equal(bank.tables.argmax(axis=-1), bank.maps)
            for context_index in range(32):
                self.assertEqual(
                    sorted(bank.phi[context_index].tolist()), list(range(8))
                )
                self.assertEqual(
                    sorted(bank.canonical_to_slot[context_index].tolist()), [0, 1]
                )
                for action in range(2):
                    slot = int(bank.canonical_to_slot[context_index, action])
                    np.testing.assert_array_equal(
                        bank.maps[context_index, slot, bank.phi[context_index]],
                        bank.phi[context_index, self.maps[action]],
                    )
        self.assertFalse(key_sets["prior"] & key_sets["calibration"])
        self.assertFalse(key_sets["prior"] & key_sets["evaluation"])
        self.assertFalse(key_sets["calibration"] & key_sets["evaluation"])

    def test_path_banks_obey_all_frozen_pair_constraints(self) -> None:
        calibration = self.path_banks["calibration"]
        evaluation = self.path_banks["evaluation"]
        stress = self.path_banks["stress"]
        self.assertEqual(len(calibration.pairs), 48)
        self.assertEqual(len(evaluation.pairs), 48)
        self.assertEqual(len(stress.words_by_endpoint), 8)
        self.assertFalse(set(calibration.words) & set(evaluation.words))
        self.assertFalse(set(calibration.words) & set(stress.words_by_endpoint))
        self.assertFalse(set(evaluation.words) & set(stress.words_by_endpoint))
        shortest = probe.lexicographic_shortest_representatives(self.maps)
        for bank in (calibration, evaluation):
            cells: dict[tuple[int, int], int] = {}
            self.assertEqual(len(set(bank.words)), 96)
            for pair in bank.pairs:
                cells[(pair.nominal_band, pair.endpoint)] = (
                    cells.get((pair.nominal_band, pair.endpoint), 0) + 1
                )
                expected_length = pair.nominal_band + len(shortest[pair.endpoint]) % 2
                self.assertEqual(pair.exact_length, expected_length)
                self.assertLess(pair.word_a, pair.word_b)
                self.assertEqual(pair.number_r, pair.word_a.count(0))
                self.assertEqual(pair.number_r, pair.word_b.count(0))
                self.assertEqual(pair.number_f, pair.word_a.count(1))
                self.assertEqual(pair.number_f, pair.word_b.count(1))
                for word in (pair.word_a, pair.word_b):
                    self.assertEqual(len(word), expected_length)
                    self.assertLessEqual(probe.generator_count_imbalance(word), 2)
                    self.assertLessEqual(probe.maximum_symbol_run(word), 4)
                    self.assertEqual(
                        probe.apply_state_word(self.maps, 0, word), pair.endpoint
                    )
                    self.assertEqual(
                        tuple(probe.state_map_for_word(self.maps, word)),
                        pair.full_state_map,
                    )
                    for start in range(8):
                        manual = start
                        for action in word:
                            manual = int(self.maps[action, manual])
                        self.assertEqual(manual, pair.full_state_map[start])
            self.assertEqual(set(cells.values()), {2})
            self.assertEqual(len(cells), 24)
        for endpoint, word in enumerate(stress.words_by_endpoint):
            self.assertEqual(len(word), 16 + (len(shortest[endpoint]) % 2))
            self.assertEqual(probe.apply_state_word(self.maps, 0, word), endpoint)
            self.assertLessEqual(probe.generator_count_imbalance(word), 2)
            self.assertLessEqual(probe.maximum_symbol_run(word), 4)
            np.testing.assert_array_equal(
                probe.state_map_for_word(self.maps, word),
                probe.state_map_for_word(self.maps, shortest[endpoint]),
            )
            for start in range(8):
                manual = start
                for action in word:
                    manual = int(self.maps[action, manual])
                self.assertEqual(
                    manual,
                    stress.receipt["full_state_maps"][endpoint][start],
                )

    def test_path_manifests_are_deterministic(self) -> None:
        repeated = probe.make_disjoint_path_banks(self.maps)
        for split in ("calibration", "evaluation"):
            self.assertEqual(
                self.path_banks[split].receipt["sha256"],
                repeated[split].receipt["sha256"],
            )
            self.assertEqual(
                self.path_banks[split].receipt["raw_word_sha256"],
                repeated[split].receipt["raw_word_sha256"],
            )
        self.assertEqual(
            self.path_banks["stress"].receipt["sha256"],
            repeated["stress"].receipt["sha256"],
        )

    def test_continuation_and_stress_union_trie_is_complete(self) -> None:
        self.assertEqual(len(self.continuations.words), 31)
        self.assertEqual(self.continuations.words[0], ())
        self.assertEqual(len(set(self.continuations.words)), 31)
        expected_order = tuple(
            word
            for length in range(5)
            for word in itertools.product((0, 1), repeat=length)
        )
        self.assertEqual(self.continuations.words, expected_order)
        self.assertEqual(
            self.continuations.receipt["bfs_tags"],
            {
                "epsilon": [],
                "r": [0],
                "rr": [0, 0],
                "rrr": [0, 0, 0],
                "f": [1],
                "fr": [1, 0],
                "rrf": [0, 0, 1],
                "rf": [0, 1],
            },
        )
        for length in range(5):
            self.assertEqual(
                sum(len(word) == length for word in self.continuations.words),
                2**length,
            )

        requested = (
            *self.continuations.words,
            *self.path_banks["stress"].words_by_endpoint,
        )
        required_prefixes = {()}
        for word in requested:
            required_prefixes.update(word[:length] for length in range(1, len(word) + 1))
        self.assertEqual(len(required_prefixes) - 1, 129)

        class CountingExactModel(probe.ExactCompiledModel):
            def __init__(self) -> None:
                super().__init__()
                self.normalization_calls = 0

            def normalize_hidden(
                self, hidden: torch.Tensor, metric: torch.Tensor | None = None
            ) -> torch.Tensor:
                self.normalization_calls += 1
                return super().normalize_hidden(hidden, metric)

        model = CountingExactModel()
        context = self.context_banks["evaluation"]
        encoded = probe.encode_context_once(model, context.tables[0])
        starts = np.arange(8, dtype=np.int64)
        hidden = model.initial_hidden(
            torch.from_numpy(context.phi[0, starts]).long()
        )
        tree = probe.rollout_word_set_reusing_tree(
            model,
            hidden,
            encoded,
            context.canonical_to_slot[0],
            requested,
        )
        self.assertEqual(set(tree), set(requested))
        self.assertEqual(model.normalization_calls, len(required_prefixes))
        for word in requested:
            direct = probe.run_word_batch(
                model,
                encoded,
                context.canonical_to_slot[0],
                context.phi[0],
                starts,
                [word] * 8,
            )
            torch.testing.assert_close(tree[word].hidden, direct.hidden[-1])
            torch.testing.assert_close(tree[word].logits, direct.logits)

    def test_slot_conversion_respects_visible_operator_swap(self) -> None:
        words = ((0, 1, 1, 0), (1, 0, 0, 1))
        identity = probe.canonical_words_to_slots(words, np.array([0, 1]))
        swapped = probe.canonical_words_to_slots(words, np.array([1, 0]))
        np.testing.assert_array_equal(swapped, 1 - identity)
        with self.assertRaisesRegex(ValueError, "common length"):
            probe.canonical_words_to_slots(((0,), (0, 1)), np.array([0, 1]))

    def test_compile_anchor_action_closes_d4_in_full_ambient_space(self) -> None:
        anchors = np.zeros((12, 8), dtype=np.float64)
        anchors[:8] = np.eye(8)
        operators = np.stack(
            [probe.compile_anchor_action(anchors, visible_map) for visible_map in self.maps]
        )
        identity = np.eye(12)
        for relation in ((0, 0, 0, 0), (1, 1), (1, 0, 1, 0)):
            product = identity.copy()
            for action in relation:
                product = operators[action] @ product
            np.testing.assert_allclose(product, identity, atol=1e-12, rtol=0.0)

    def test_float64_projector_audit_and_float32_application(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        self.assertEqual(projector.numpy64.dtype, np.float64)
        self.assertEqual(projector.torch32.dtype, torch.float32)
        self.assertTrue(projector.audit["pass"])
        self.assertEqual(projector.audit["post_cast_rank"], 8)
        self.assertEqual(projector.audit["anchor_rank"], 8)
        self.assertAlmostEqual(projector.audit["trace"], 8.0, places=6)
        self.assertLessEqual(
            projector.audit["maximum_absolute_idempotence_residual"], 1e-5
        )
        self.assertLessEqual(
            projector.audit["maximum_absolute_g_self_adjointness_residual"], 1e-5
        )
        self.assertLessEqual(
            projector.audit["maximum_absolute_anchor_preservation_residual"],
            1e-5,
        )

    def test_interventions_have_exact_frozen_semantics(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        with torch.no_grad():
            model.decoder.weight.zero_()
            model.decoder.weight[:, :8] = torch.roll(
                torch.eye(8, dtype=torch.float32), shifts=2, dims=0
            )
        anchors = model.state_anchors()
        prototype_tensor = anchors.clone()
        prototype_tensor[:, 8] = torch.linspace(0.10, 0.17, 8)
        prototype_tensor = probe.checked_model_normalize(model, prototype_tensor)
        prototypes = probe.PrototypeBundle(
            torch32=prototype_tensor,
            numpy64=prototype_tensor.detach().cpu().numpy().astype(np.float64),
            audit={"source": "nondegenerate unit prototype chart", "pass": True},
        )
        true_canonical = torch.tensor([0, 3, 7], dtype=torch.long)
        phi = torch.tensor([4, 2, 7, 1, 6, 0, 5, 3], dtype=torch.long)
        true_visible = phi[true_canonical]
        nearest_visible = torch.tensor([0, 2, 5], dtype=torch.long)
        decoded_visible = torch.remainder(nearest_visible + 2, 8)
        hidden = anchors[nearest_visible].clone()
        hidden[:, 11] = torch.tensor([0.20, 0.30, 0.40])
        hidden = probe.checked_model_normalize(model, hidden)
        hidden_prime = anchors[torch.tensor([7, 6, 0])].clone()
        hidden_prime[:, 10] = torch.tensor([0.11, 0.12, 0.13])
        hidden_prime = probe.checked_model_normalize(model, hidden_prime)
        interventions = probe.construct_interventions(
            model,
            hidden,
            hidden_prime,
            true_canonical,
            phi,
            self.maps,
            projector,
            prototypes,
        )
        self.assertEqual(
            set(interventions.hidden), set(probe.INTERVENTION_NAMES) - {"random_ray"}
        )
        self.assertEqual(set(interventions.hidden), set(interventions.selected_visible))
        wrong_canonical = torch.from_numpy(
            self.maps[0, true_canonical.numpy()].astype(np.int64)
        ).long()
        wrong_visible = phi[wrong_canonical]
        expected_hidden = {
            "native_h": hidden,
            "native_h_prime": hidden_prime,
            "sham_scale": hidden,
            "oracle_anchor": anchors[true_visible],
            "self_anchor": anchors[decoded_visible],
            "nearest_anchor": anchors[nearest_visible],
            "oracle_prototype": prototype_tensor[true_visible],
            "self_prototype": prototype_tensor[nearest_visible],
            "anchor_projection": anchors[nearest_visible],
            "wrong_anchor": anchors[wrong_visible],
            "wrong_prototype": prototype_tensor[wrong_visible],
        }
        sentinel = torch.full_like(true_visible, -1)
        expected_selected = {
            "native_h": sentinel,
            "native_h_prime": sentinel,
            "sham_scale": sentinel,
            "oracle_anchor": true_visible,
            "self_anchor": decoded_visible,
            "nearest_anchor": nearest_visible,
            "oracle_prototype": true_visible,
            "self_prototype": nearest_visible,
            "anchor_projection": sentinel,
            "wrong_anchor": wrong_visible,
            "wrong_prototype": wrong_visible,
        }
        for name, candidate in interventions.hidden.items():
            self.assertEqual(candidate.dtype, torch.float32)
            self.assertTrue(bool(torch.isfinite(candidate).all()))
            torch.testing.assert_close(
                candidate, expected_hidden[name], atol=1e-6, rtol=0.0
            )
            torch.testing.assert_close(
                interventions.selected_visible[name], expected_selected[name]
            )
        self.assertFalse(torch.equal(hidden, hidden_prime))
        self.assertFalse(torch.equal(prototype_tensor, anchors))
        self.assertFalse(torch.equal(true_visible, decoded_visible))
        self.assertFalse(torch.equal(decoded_visible, nearest_visible))
        self.assertTrue(bool((wrong_visible != true_visible).all()))
        self.assertEqual(int(wrong_canonical[1]), 0)

    def test_projection_removes_complement_without_anchor_snapping(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        prototypes = self.exact_prototypes(model)
        phi = torch.arange(8, dtype=torch.long)
        hidden = torch.zeros((1, 12), dtype=torch.float32)
        hidden[0, 0] = 0.8
        hidden[0, 1] = 0.2
        hidden[0, 8] = 0.4
        hidden = model.normalize_hidden(hidden)
        interventions = probe.construct_interventions(
            model,
            hidden,
            hidden,
            torch.tensor([0], dtype=torch.long),
            phi,
            self.maps,
            projector,
            prototypes,
        )
        projected = interventions.hidden["anchor_projection"]
        self.assertAlmostEqual(float(projected[0, 8]), 0.0, places=6)
        self.assertGreater(float(projected[0, 1]), 0.0)
        self.assertLess(float(projected[0, 1]), float(projected[0, 0]))
        self.assertFalse(torch.equal(projected, model.state_anchors()[[0]]))

    def test_periodic_reset_conditions_are_nondegenerate_and_exact(self) -> None:
        model = probe.ExactCompiledModel()
        with torch.no_grad():
            model.decoder.weight.zero_()
            model.decoder.weight[:, :8] = torch.roll(
                torch.eye(8, dtype=torch.float32), shifts=2, dims=0
            )
        anchors = model.state_anchors()
        projector = probe.construct_anchor_projector(model)
        prototype_tensor = anchors.clone()
        prototype_tensor[:, 8] = torch.linspace(0.10, 0.17, 8)
        prototype_tensor = probe.checked_model_normalize(model, prototype_tensor)
        prototypes = probe.PrototypeBundle(
            torch32=prototype_tensor,
            numpy64=prototype_tensor.numpy().astype(np.float64),
            audit={"source": "nondegenerate periodic unit chart", "pass": True},
        )
        truth = torch.tensor([0, 3, 7], dtype=torch.long)
        phi = torch.tensor([4, 2, 7, 1, 6, 0, 5, 3], dtype=torch.long)
        true_visible = phi[truth]
        nearest_visible = torch.tensor([0, 2, 5], dtype=torch.long)
        decoded_visible = torch.remainder(nearest_visible + 2, 8)
        hidden = anchors[nearest_visible].clone()
        hidden[:, 11] = torch.tensor([0.20, 0.30, 0.40])
        hidden = probe.checked_model_normalize(model, hidden)
        sentinel = torch.full_like(truth, -1)
        expected = {
            "native": (hidden, sentinel),
            "sham_scale": (hidden, sentinel),
            "oracle_anchor": (anchors[true_visible], true_visible),
            "self_anchor": (anchors[decoded_visible], decoded_visible),
            "nearest_anchor": (anchors[nearest_visible], nearest_visible),
            "self_prototype": (
                prototype_tensor[nearest_visible],
                nearest_visible,
            ),
            "anchor_projection": (anchors[nearest_visible], sentinel),
        }
        for condition in probe.PERIODIC_CONDITION_NAMES:
            with self.subTest(condition=condition):
                state, selected = probe._periodic_reset(
                    condition,
                    model,
                    hidden,
                    truth,
                    phi,
                    projector,
                    prototypes,
                )
                torch.testing.assert_close(
                    state, expected[condition][0], atol=1e-6, rtol=0.0
                )
                torch.testing.assert_close(selected, expected[condition][1])

    def test_oriented_selector_rejects_antipodal_anchor(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        prototypes = self.exact_prototypes(model)
        hidden = -model.state_anchors()[[0]]
        interventions = probe.construct_interventions(
            model,
            hidden,
            hidden,
            torch.tensor([0], dtype=torch.long),
            torch.arange(8, dtype=torch.long),
            self.maps,
            projector,
            prototypes,
        )
        self.assertNotEqual(
            int(interventions.selected_visible["nearest_anchor"][0]), 0
        )

    def test_prototype_reduction_is_balanced_and_positive_ray(self) -> None:
        model = probe.ExactCompiledModel()
        states = model.state_anchors().repeat(3, 1)
        labels = torch.arange(8, dtype=torch.long).repeat(3)
        prototypes = probe.prototypes_from_labeled_states(model, states, labels)
        torch.testing.assert_close(prototypes.torch32, model.state_anchors())
        self.assertEqual(prototypes.torch32.dtype, torch.float32)
        self.assertTrue(prototypes.audit["balanced_visible_class_counts"])
        self.assertEqual(prototypes.audit["counts_by_visible_class"], [3] * 8)
        self.assertEqual(prototypes.audit["positive_ray_sign_flips"], 0)

    def test_diagnostics_promote_only_after_float32_and_report_tv(self) -> None:
        native_logits = torch.tensor([[3.0, 1.0], [0.0, 2.0]], dtype=torch.float32)
        candidate_logits = native_logits.clone()
        native_hidden = torch.eye(2, dtype=torch.float32)
        target = torch.tensor([0, 1], dtype=torch.long)
        metric = torch.eye(2, dtype=torch.float32)
        result = probe.paired_future_diagnostics(
            native_logits,
            candidate_logits,
            native_hidden,
            native_hidden.clone(),
            target,
            metric,
            native_prime_logits=native_logits.clone(),
            native_prime_hidden=native_hidden.clone(),
        )
        for values in result.values():
            self.assertEqual(values.dtype, np.float64)
        np.testing.assert_array_equal(result["accuracy"], np.ones(2))
        np.testing.assert_allclose(result["softmax_tv_to_native_h"], 0.0)
        np.testing.assert_allclose(
            result["centered_logit_angle_to_native_h"], 0.0, atol=3e-8
        )
        np.testing.assert_allclose(
            result["hidden_metric_angle_to_native_h"], 0.0, atol=3e-8
        )

    def test_nonfinite_and_wrong_dtype_diagnostics_fail_closed(self) -> None:
        logits = torch.tensor([[3.0, 1.0]], dtype=torch.float32)
        hidden = torch.tensor([[1.0, 0.0]], dtype=torch.float32)
        target = torch.tensor([0], dtype=torch.long)
        metric = torch.eye(2, dtype=torch.float32)
        with self.assertRaises(TypeError):
            probe.paired_future_diagnostics(
                logits.double(), logits, hidden, hidden, target, metric
            )
        bad_logits = logits.clone()
        bad_logits[0, 0] = float("nan")
        with self.assertRaises(FloatingPointError):
            probe.paired_future_diagnostics(
                logits, bad_logits, hidden, hidden, target, metric
            )
        with self.assertRaises(FloatingPointError):
            probe.paired_future_diagnostics(
                logits,
                logits,
                torch.zeros_like(hidden),
                torch.zeros_like(hidden),
                target,
                metric,
            )
        model = probe.ExactCompiledModel()
        with self.assertRaises(FloatingPointError):
            probe.checked_model_normalize(
                model, torch.zeros((1, 12), dtype=torch.float32)
            )
        nonfinite_hidden = torch.zeros((1, 12), dtype=torch.float32)
        nonfinite_hidden[0, 0] = float("inf")
        with self.assertRaises(FloatingPointError):
            probe.checked_decode_hidden(model, nonfinite_hidden)

    def test_every_diagnostic_tensor_boundary_is_float32_finite(self) -> None:
        arguments = {
            "native_logits": torch.tensor([[2.0, 0.0]], dtype=torch.float32),
            "candidate_logits": torch.tensor([[1.0, 3.0]], dtype=torch.float32),
            "native_hidden": torch.tensor([[1.0, 0.0]], dtype=torch.float32),
            "candidate_hidden": torch.tensor([[0.5, 1.0]], dtype=torch.float32),
            "target_visible": torch.tensor([1], dtype=torch.long),
            "metric": torch.eye(2, dtype=torch.float32),
            "native_prime_logits": torch.tensor(
                [[0.0, 2.0]], dtype=torch.float32
            ),
            "native_prime_hidden": torch.tensor(
                [[0.0, 1.0]], dtype=torch.float32
            ),
            "counterfactual_visible": torch.tensor([0], dtype=torch.long),
        }
        float_fields = (
            "native_logits",
            "candidate_logits",
            "native_hidden",
            "candidate_hidden",
            "metric",
            "native_prime_logits",
            "native_prime_hidden",
        )
        for field in float_fields:
            with self.subTest(field=field, defect="float64"):
                bad = dict(arguments)
                bad[field] = arguments[field].double()
                with self.assertRaises(TypeError):
                    probe.paired_future_diagnostics(**bad)
            with self.subTest(field=field, defect="nonfinite"):
                bad = dict(arguments)
                corrupt = arguments[field].clone()
                corrupt.reshape(-1)[0] = float("nan")
                bad[field] = corrupt
                with self.assertRaises(FloatingPointError):
                    probe.paired_future_diagnostics(**bad)
        for field in ("target_visible", "counterfactual_visible"):
            with self.subTest(field=field):
                bad = dict(arguments)
                bad[field] = arguments[field].to(dtype=torch.int32)
                with self.assertRaises(TypeError):
                    probe.paired_future_diagnostics(**bad)

    def test_diagnostic_numeric_oracle_and_undefined_angle_gate(self) -> None:
        native_logits = torch.tensor([[2.0, 0.0, -1.0]], dtype=torch.float32)
        candidate_logits = torch.tensor([[1.0, 2.0, -1.0]], dtype=torch.float32)
        native_hidden = torch.tensor([[1.0, 1.0]], dtype=torch.float32)
        candidate_hidden = torch.tensor([[1.0, -1.0]], dtype=torch.float32)
        metric = torch.tensor([[2.0, 0.0], [0.0, 1.0]], dtype=torch.float32)
        result = probe.paired_future_diagnostics(
            native_logits,
            candidate_logits,
            native_hidden,
            candidate_hidden,
            torch.tensor([1], dtype=torch.long),
            metric,
        )
        native64 = native_logits.numpy().astype(np.float64)[0]
        candidate64 = candidate_logits.numpy().astype(np.float64)[0]
        native_probability = np.exp(native64 - np.max(native64))
        native_probability /= np.sum(native_probability)
        candidate_probability = np.exp(candidate64 - np.max(candidate64))
        candidate_probability /= np.sum(candidate_probability)
        expected_tv = 0.5 * np.sum(
            np.abs(candidate_probability - native_probability)
        )
        native_centered = native64 - np.mean(native64)
        candidate_centered = candidate64 - np.mean(candidate64)
        expected_logit_angle = np.arccos(
            np.dot(native_centered, candidate_centered)
            / (
                np.linalg.norm(native_centered)
                * np.linalg.norm(candidate_centered)
            )
        )
        expected_hidden_angle = np.arccos(1.0 / 3.0)
        self.assertAlmostEqual(result["softmax_tv_to_native_h"][0], expected_tv)
        self.assertAlmostEqual(
            result["centered_logit_angle_to_native_h"][0],
            expected_logit_angle,
        )
        self.assertAlmostEqual(
            result["hidden_metric_angle_to_native_h"][0],
            expected_hidden_angle,
        )
        self.assertAlmostEqual(result["correct_margin"][0], 1.0)
        self.assertEqual(result["accuracy"][0], 1.0)
        self.assertEqual(result["native_h_accuracy"][0], 0.0)

        undefined = probe.paired_future_diagnostics(
            torch.zeros((1, 2), dtype=torch.float32),
            torch.tensor([[1.0, -1.0]], dtype=torch.float32),
            torch.tensor([[1.0, 0.0]], dtype=torch.float32),
            torch.tensor([[1.0, 0.0]], dtype=torch.float32),
            torch.tensor([0], dtype=torch.long),
            torch.eye(2, dtype=torch.float32),
        )
        angle = undefined["centered_logit_angle_to_native_h"]
        self.assertTrue(np.isnan(angle[0]))
        accumulator = probe.TensorAccumulator((1, 1, 1, 1))
        accumulator.add_batch(0, 0, 0, np.array([0]), undefined)
        self.assertEqual(accumulator.case_count[0, 0, 0, 0], 1)
        self.assertEqual(
            accumulator.finite_counts[
                "centered_logit_angle_to_native_h"
            ][0, 0, 0, 0],
            0,
        )
        gate_angle = float(
            np.where(np.isfinite(angle), angle, math.pi)[0]
        )
        native_summary = {
            "all_suffix_trace_equivalence_fraction": 1.0,
            "joint_all_suffix_correct_fraction": 1.0,
            "worst_context_trace_equivalence_fraction": 1.0,
            "p95_pairwise_maximum_centered_logit_angle_with_undefined_as_pi": (
                gate_angle
            ),
            "undefined_centered_logit_angle_count": int(np.count_nonzero(~np.isfinite(angle))),
            "p95_pairwise_maximum_softmax_total_variation": 0.0,
        }
        gates = probe.build_one_shot_gate_inputs(
            context_strata=probe.ContextStratumAccumulator(12, 0, 1),
            bands=(),
            native_summary=native_summary,
            exhaustive_selectors={},
            selector_correct={},
            selector_total={},
            selector_idempotent={},
            selector_cut_hidden_maximum={},
        )
        self.assertEqual(gate_angle, math.pi)
        self.assertFalse(
            gates["native_finite_logit_trace_agreement_h4_p95"]["pass"]
        )

    def test_batched_diagnostics_equal_rowwise_diagnostics(self) -> None:
        native_logits = torch.tensor(
            [[3.0, 1.0, -1.0], [0.5, 2.5, -0.5], [-1.0, 0.0, 3.0]],
            dtype=torch.float32,
        )
        candidate_logits = torch.tensor(
            [[2.5, 1.5, -1.0], [0.25, 2.75, -0.5], [-0.5, 0.0, 2.5]],
            dtype=torch.float32,
        )
        native_hidden = torch.eye(3, dtype=torch.float32)
        candidate_hidden = torch.tensor(
            [[1.0, 0.1, 0.0], [0.0, 1.0, 0.2], [0.1, 0.0, 1.0]],
            dtype=torch.float32,
        )
        target = torch.tensor([0, 1, 2], dtype=torch.long)
        metric = torch.eye(3, dtype=torch.float32)
        batched = probe.paired_future_diagnostics(
            native_logits,
            candidate_logits,
            native_hidden,
            candidate_hidden,
            target,
            metric,
        )
        rowwise: dict[str, list[float]] = {name: [] for name in batched}
        for row in range(3):
            single = probe.paired_future_diagnostics(
                native_logits[row : row + 1],
                candidate_logits[row : row + 1],
                native_hidden[row : row + 1],
                candidate_hidden[row : row + 1],
                target[row : row + 1],
                metric,
            )
            for name, values in single.items():
                rowwise[name].append(float(values[0]))
        for name, values in batched.items():
            np.testing.assert_allclose(
                values, np.asarray(rowwise[name], dtype=np.float64), rtol=0.0, atol=0.0
            )

    def test_dense_tensor_accumulator_is_exactly_scalar_equivalent(self) -> None:
        shape = (2, 2, 3, 8)
        dense = probe.TensorAccumulator(shape)
        scalar = probe.TensorAccumulator(shape)
        first_indices = np.asarray([0, 1], dtype=np.int64)
        second_indices = np.asarray([1, 0], dtype=np.int64)
        continuation_indices = np.asarray([0, 2], dtype=np.int64)
        cut_states = np.asarray(
            [
                list(range(8)) + list(range(8)),
                list(reversed(range(8))) + list(reversed(range(8))),
            ],
            dtype=np.int64,
        )
        base = np.arange(2 * 2 * 16, dtype=np.float64).reshape(2, 2, 16)
        metrics = {
            name: base + metric_index / 32.0
            for metric_index, name in enumerate(probe.TensorAccumulator.METRICS)
        }
        for angle_name in (
            "centered_logit_angle_to_native_h",
            "centered_logit_angle_to_native_h_prime",
        ):
            metrics[angle_name] = metrics[angle_name].copy()
            metrics[angle_name][0, 1, 3] = np.nan
            metrics[angle_name][1, 0, 12] = np.nan

        dense.add_dense_panel(
            first_indices,
            second_indices,
            continuation_indices,
            cut_states,
            metrics,
        )
        for mode_index, (first, second) in enumerate(
            zip(first_indices, second_indices)
        ):
            for continuation_position, continuation_index in enumerate(
                continuation_indices
            ):
                scalar.add_batch(
                    int(first),
                    int(second),
                    int(continuation_index),
                    cut_states[mode_index],
                    {
                        name: values[mode_index, continuation_position]
                        for name, values in metrics.items()
                    },
                )
        np.testing.assert_array_equal(dense.case_count, scalar.case_count)
        for name in probe.TensorAccumulator.METRICS:
            np.testing.assert_array_equal(dense.sums[name], scalar.sums[name])
            np.testing.assert_array_equal(
                dense.finite_counts[name], scalar.finite_counts[name]
            )
        self.assertTrue(
            np.any(
                dense.finite_counts["centered_logit_angle_to_native_h"]
                < dense.case_count
            )
        )

    def test_dense_context_strata_are_exactly_scalar_equivalent_with_selector_na(self) -> None:
        intervention_count = 3
        dense = probe.ContextStratumAccumulator(intervention_count, 2, 2)
        scalar = probe.ContextStratumAccumulator(intervention_count, 2, 2)
        lengths = (0, 1, 2, 3, 4)
        row_count = 4
        shape = (len(lengths), intervention_count, row_count)
        source_metrics = tuple(
            name
            for name in probe.ContextStratumAccumulator.METRICS
            if name
            not in (
                "correct_selection_and_suffix_correct",
                "correct_selection_denominator",
            )
        )
        base = np.arange(np.prod(shape), dtype=np.float64).reshape(shape) / 100.0
        diagnostics = {
            name: base + metric_index
            for metric_index, name in enumerate(source_metrics)
        }
        true_visible = np.asarray([0, 1, 2, 3], dtype=np.int64)
        selected_visible = (
            None,
            true_visible.copy(),
            np.asarray([0, 7, -1, 3], dtype=np.int64),
        )
        dense.add_dense_panel(
            1,
            0,
            lengths,
            diagnostics,
            selected_visible,
            true_visible,
        )
        for continuation_index, length in enumerate(lengths):
            for intervention_index in range(intervention_count):
                scalar.add_batch(
                    intervention_index,
                    1,
                    0,
                    length,
                    {
                        name: values[continuation_index, intervention_index]
                        for name, values in diagnostics.items()
                    },
                    selected_visible[intervention_index],
                    true_visible,
                )
        for name in probe.ContextStratumAccumulator.METRICS:
            np.testing.assert_array_equal(dense.sums[name], scalar.sums[name])
            np.testing.assert_array_equal(
                dense.finite_counts[name], scalar.finite_counts[name]
            )
        selection_counts = dense.finite_counts["correct_selection_denominator"]
        self.assertTrue(np.all(selection_counts[0, 1, 0] == 0))
        self.assertGreater(int(np.sum(selection_counts[1, 1, 0])), 0)

    def test_gate_level_zero_context_denominators_fail_oracle_and_autonomous(self) -> None:
        bands = (8, 64)
        intervention_index = {
            name: index for index, name in enumerate(probe.INTERVENTION_NAMES)
        }
        nonempty = probe.SUFFIX_STRATUM_NAMES.index("nonempty")

        def perfect_accumulator() -> probe.ContextStratumAccumulator:
            accumulator = probe.ContextStratumAccumulator(
                len(probe.INTERVENTION_NAMES), len(bands), 2
            )
            for name in probe.ContextStratumAccumulator.METRICS:
                accumulator.sums[name].fill(10.0)
                accumulator.finite_counts[name].fill(10)
            accumulator.sums["damage_numerator"].fill(0.0)
            accumulator.sums["rescue_numerator"].fill(0.0)
            for name in ("wrong_anchor", "wrong_prototype", "random_ray"):
                accumulator.sums["accuracy"][intervention_index[name]].fill(0.0)
            return accumulator

        exhaustive_record = {
            "section_validity_numerator": 1,
            "section_validity_denominator": 1,
            "decoder_consistency_numerator": 1,
            "decoder_consistency_denominator": 1,
            "idempotence_numerator": 1,
            "idempotence_denominator": 1,
            "maximum_absolute_hidden_idempotence_difference": 0.0,
            "generators": {
                generator: {
                    "numerator": 1,
                    "denominator": 1,
                    "worst_context_accuracy": 1.0,
                }
                for generator in ("r", "f")
            },
        }
        selector_names = ("self_anchor", "nearest_anchor", "self_prototype")
        exhaustive = {name: dict(exhaustive_record) for name in selector_names}
        selector_correct = {
            name: np.ones((2, 8), dtype=np.int64) for name in selector_names
        }
        selector_total = {
            name: np.ones((2, 8), dtype=np.int64) for name in selector_names
        }
        selector_idempotent = {name: (1, 1) for name in selector_names}
        selector_hidden = {name: 0.0 for name in selector_names}

        def gates(
            accumulator: probe.ContextStratumAccumulator,
        ) -> dict[str, object]:
            return probe.build_one_shot_gate_inputs(
                context_strata=accumulator,
                bands=bands,
                native_summary=None,
                exhaustive_selectors=exhaustive,
                selector_correct=selector_correct,
                selector_total=selector_total,
                selector_idempotent=selector_idempotent,
                selector_cut_hidden_maximum=selector_hidden,
            )

        baseline = gates(perfect_accumulator())
        self.assertTrue(baseline["oracle"]["oracle_anchor"]["pass"])
        self.assertTrue(baseline["autonomous"]["self_anchor"]["pass"])

        oracle_zero = perfect_accumulator()
        oracle_zero.sums["damage_denominator"][
            intervention_index["oracle_anchor"], 1, 1, nonempty
        ] = 0.0
        oracle_result = gates(oracle_zero)["oracle"]["oracle_anchor"]
        self.assertFalse(oracle_result["damage_nonempty_W4"]["all_context_denominators_positive"])
        self.assertFalse(oracle_result["pass"])

        autonomous_zero = perfect_accumulator()
        autonomous_zero.sums["correct_selection_denominator"][
            intervention_index["self_anchor"], 1, 1, nonempty
        ] = 0.0
        autonomous_result = gates(autonomous_zero)["autonomous"]["self_anchor"]
        self.assertFalse(
            autonomous_result["conditional_suffix_accuracy_given_correct_selection"][
                "all_context_denominators_positive"
            ]
        )
        self.assertFalse(autonomous_result["pass"])

    def test_custom_rollout_matches_packaged_float32_control(self) -> None:
        model = probe.ExactCompiledModel()
        contexts = probe.make_context_bank(
            self.api["EpisodeGenerator"], seed=77, count=1, split="unit"
        )
        encoded = probe.encode_context_once(model, contexts.tables[0])
        starts = np.arange(8, dtype=np.int64)
        word = (0, 1, 0, 0, 1)
        packaged = probe.run_word_batch(
            model,
            encoded,
            contexts.canonical_to_slot[0],
            contexts.phi[0],
            starts,
            [word] * 8,
        )
        initial = model.initial_hidden(
            torch.from_numpy(contexts.phi[0, starts]).long()
        )
        slots = torch.from_numpy(
            probe.canonical_words_to_slots(
                [word] * 8, contexts.canonical_to_slot[0]
            )
        ).long()
        custom = probe.custom_rollout_float32(
            model, initial, encoded.expand(8, -1, -1, -1), slots
        )
        self.assertEqual(custom.hidden[-1].dtype, torch.float32)
        self.assertEqual(custom.logits.dtype, torch.float32)
        torch.testing.assert_close(custom.hidden[-1], packaged.hidden[-1])
        torch.testing.assert_close(custom.logits, packaged.logits)

    def test_vectorized_periodic_engine_matches_scalar_engine(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        prototypes = self.exact_prototypes(model)
        context = probe.make_context_bank(
            self.api["EpisodeGenerator"], seed=88, count=1, split="unit"
        )
        encoded = probe.encode_context_once(model, context.tables[0])
        phi = torch.from_numpy(context.phi[0]).long()
        starts = torch.arange(8, dtype=torch.long)
        initial = model.initial_hidden(phi[starts])
        layout = probe.periodic_suffix_physical_layout()
        self.assertEqual(len(probe.periodic_repair_layout()), 24)
        self.assertEqual(len(layout), 25)
        word = (0, 1, 0, 1, 1, 0, 0, 1) * 2
        checkpoint_steps = (4, 8, 16)
        stacked = probe.periodic_evolve_stacked(
            model,
            torch.cat([initial.clone() for _ in layout]),
            encoded,
            context.canonical_to_slot[0],
            phi,
            self.maps,
            starts.repeat(len(layout)),
            word,
            elapsed_steps=0,
            layout=layout,
            mode_batch_size=8,
            projector=projector,
            prototypes=prototypes,
            checkpoint_steps=checkpoint_steps,
        )
        self.assertEqual(stacked.elapsed_steps, len(word))
        self.assertEqual(set(stacked.checkpoints), set(checkpoint_steps))
        for mode_index, (condition, cadence) in enumerate(layout):
            scalar = probe.periodic_evolve(
                model,
                initial,
                encoded,
                context.canonical_to_slot[0],
                phi,
                self.maps,
                starts,
                word,
                condition=condition,
                cadence=4 if condition == "native" else cadence,
                projector=projector,
                prototypes=prototypes,
                checkpoint_steps=checkpoint_steps,
            )
            rows = slice(mode_index * 8, (mode_index + 1) * 8)
            torch.testing.assert_close(stacked.hidden[rows], scalar.hidden)
            torch.testing.assert_close(stacked.logits[rows], scalar.logits)
            torch.testing.assert_close(stacked.true_canonical[rows], scalar.true_canonical)
            for checkpoint_step in checkpoint_steps:
                stacked_state, stacked_logits, stacked_truth = stacked.checkpoints[
                    checkpoint_step
                ]
                scalar_logits, scalar_truth = scalar.checkpoints[checkpoint_step]
                torch.testing.assert_close(
                    stacked_logits[rows], scalar_logits
                )
                torch.testing.assert_close(
                    stacked_truth[rows], scalar_truth
                )
                scalar_prefix = probe.periodic_evolve(
                    model,
                    initial,
                    encoded,
                    context.canonical_to_slot[0],
                    phi,
                    self.maps,
                    starts,
                    word[:checkpoint_step],
                    condition=condition,
                    cadence=4 if condition == "native" else cadence,
                    projector=projector,
                    prototypes=prototypes,
                )
                torch.testing.assert_close(
                    stacked_state[rows], scalar_prefix.hidden
                )
            if condition != "native":
                self.assertEqual(stacked.events[mode_index], scalar.events)
        for cadence in probe.PERIODIC_CADENCES:
            sham = stacked.sham_control_by_cadence[str(cadence)]
            self.assertEqual(sham["prediction_failures"], 0)
            self.assertLessEqual(sham["maximum_absolute_hidden_difference"], 1e-6)
            self.assertLessEqual(sham["maximum_absolute_logit_difference"], 1e-6)

    def test_periodic_absolute_clock_reset_counts_for_64_and_65_step_paths(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        prototypes = self.exact_prototypes(model)
        context = probe.make_context_bank(
            self.api["EpisodeGenerator"], seed=188, count=1, split="unit"
        )
        encoded = probe.encode_context_once(model, context.tables[0])
        phi = torch.from_numpy(context.phi[0]).long()
        starts = torch.arange(8, dtype=torch.long)
        initial = model.initial_hidden(phi[starts])
        for prefix_length in (64, 65):
            prefix_word = tuple(index % 2 for index in range(prefix_length))
            for cadence in probe.PERIODIC_CADENCES:
                prefix = probe.periodic_evolve(
                    model,
                    initial,
                    encoded,
                    context.canonical_to_slot[0],
                    phi,
                    self.maps,
                    starts,
                    prefix_word,
                    condition="oracle_anchor",
                    cadence=cadence,
                    projector=projector,
                    prototypes=prototypes,
                )
                for suffix_length in range(5):
                    suffix = probe.periodic_evolve(
                        model,
                        prefix.hidden,
                        encoded,
                        context.canonical_to_slot[0],
                        phi,
                        self.maps,
                        prefix.true_canonical,
                        (1,) * suffix_length,
                        condition="oracle_anchor",
                        cadence=cadence,
                        projector=projector,
                        prototypes=prototypes,
                        elapsed_steps=prefix.elapsed_steps,
                    )
                    total_steps = prefix_length + suffix_length
                    expected_events = 8 * (total_steps // cadence)
                    combined = probe._sum_periodic_events(prefix.events, suffix.events)
                    self.assertEqual(suffix.elapsed_steps, total_steps)
                    self.assertEqual(combined.reset_events, expected_events)
                    self.assertEqual(combined.selected_events, expected_events)
                    self.assertEqual(combined.selector_correct, expected_events)

    def test_periodic_suffix_trie_preserves_prefix_clock_phase(self) -> None:
        model = probe.ExactCompiledModel()
        projector = probe.construct_anchor_projector(model)
        prototypes = self.exact_prototypes(model)
        context = probe.make_context_bank(
            self.api["EpisodeGenerator"], seed=388, count=1, split="unit"
        )
        encoded = probe.encode_context_once(model, context.tables[0])
        phi = torch.from_numpy(context.phi[0]).long()
        starts = torch.arange(8, dtype=torch.long)
        initial = model.initial_hidden(phi[starts])
        layout = probe.periodic_suffix_physical_layout()
        prefix_word = (0, 1, 0, 1, 1)
        stacked_prefix = probe.periodic_evolve_stacked(
            model,
            torch.cat([initial.clone() for _ in layout]),
            encoded,
            context.canonical_to_slot[0],
            phi,
            self.maps,
            starts.repeat(len(layout)),
            prefix_word,
            elapsed_steps=0,
            layout=layout,
            mode_batch_size=8,
            projector=projector,
            prototypes=prototypes,
        )
        suffix_words = probe.make_continuation_bank(maximum_length=4).words
        suffix_tree = probe.periodic_suffix_tree_stacked(
            model,
            stacked_prefix,
            encoded,
            context.canonical_to_slot[0],
            phi,
            self.maps,
            suffix_words,
            layout=layout,
            mode_batch_size=8,
            projector=projector,
            prototypes=prototypes,
        )
        self.assertEqual(set(suffix_tree), set(suffix_words))
        for mode_index, (condition, cadence) in enumerate(layout):
            scalar_prefix = probe.periodic_evolve(
                model,
                initial,
                encoded,
                context.canonical_to_slot[0],
                phi,
                self.maps,
                starts,
                prefix_word,
                condition=condition,
                cadence=4 if condition == "native" else cadence,
                projector=projector,
                prototypes=prototypes,
            )
            for continuation in suffix_words:
                node = suffix_tree[continuation]
                self.assertEqual(
                    node.elapsed_steps, len(prefix_word) + len(continuation)
                )
                scalar_suffix = probe.periodic_evolve(
                    model,
                    scalar_prefix.hidden,
                    encoded,
                    context.canonical_to_slot[0],
                    phi,
                    self.maps,
                    scalar_prefix.true_canonical,
                    continuation,
                    condition=condition,
                    cadence=4 if condition == "native" else cadence,
                    projector=projector,
                    prototypes=prototypes,
                    elapsed_steps=scalar_prefix.elapsed_steps,
                )
                rows = slice(mode_index * 8, (mode_index + 1) * 8)
                torch.testing.assert_close(node.hidden[rows], scalar_suffix.hidden)
                torch.testing.assert_close(node.logits[rows], scalar_suffix.logits)
                torch.testing.assert_close(
                    node.true_canonical[rows], scalar_suffix.true_canonical
                )
                if condition != "native":
                    self.assertEqual(
                        node.events[mode_index], scalar_suffix.events
                    )

    def test_periodic_sham_validator_checks_every_step_receipt(self) -> None:
        control = {
            str(cadence): {
                "maximum_absolute_hidden_difference": 0.0,
                "maximum_absolute_logit_difference": 0.0,
                "prediction_failures": 0,
                "prediction_cases": 64,
            }
            for cadence in probe.PERIODIC_CADENCES
        }
        self.assertTrue(probe.validate_periodic_sham_control(control))
        injected_unreported_step = json.loads(json.dumps(control))
        injected_unreported_step["4"]["maximum_absolute_hidden_difference"] = 1e-3
        with self.assertRaisesRegex(RuntimeError, "sham"):
            probe.validate_periodic_sham_control(injected_unreported_step)
        missing_cadence = dict(control)
        missing_cadence.pop("16")
        with self.assertRaisesRegex(RuntimeError, "cadence"):
            probe.validate_periodic_sham_control(missing_cadence)

    def test_native_prefix_cache_packs_every_float32_step(self) -> None:
        model = probe.ExactCompiledModel()
        prototypes = self.exact_prototypes(model)
        context = probe.make_context_bank(
            self.api["EpisodeGenerator"], seed=288, count=1, split="unit"
        )
        full = probe.make_endpoint_matched_path_bank(
            self.maps,
            seed=probe.EVALUATION_PATH_SEED,
            split="unit",
            nominal_bands=(8,),
            pairs_per_endpoint_band=1,
        )
        pair = full.pairs[0]
        tiny = probe.PathPairBank("unit", (pair,), {"source": "unit subset"})
        cache: dict[tuple[int, int, int], probe.NativePrefixCacheEntry] = {}
        probe.evaluate_paired_model(
            model,
            context,
            tiny,
            probe.make_continuation_bank(maximum_length=0),
            self.maps,
            prototypes,
            native_prefix_cache=cache,
        )
        self.assertEqual(set(cache), {(0, 0, 0), (0, 0, 1)})
        for member_index, word in enumerate((pair.word_a, pair.word_b)):
            entry = cache[(0, 0, member_index)]
            self.assertEqual(entry.trajectory_hidden.shape, (len(word), 8, 12))
            self.assertEqual(entry.trajectory_hidden.dtype, torch.float32)
            self.assertTrue(bool(torch.isfinite(entry.trajectory_hidden).all()))
            torch.testing.assert_close(entry.trajectory_hidden[-1], entry.hidden)
            self.assertIn(8, entry.checkpoints)

    def test_frozen_single_thread_receipt_matches_runtime(self) -> None:
        self.assertEqual(probe.TORCH_INTRAOP_THREADS, 1)
        self.assertEqual(probe.TORCH_INTEROP_THREADS, 1)
        self.assertEqual(
            probe.FROZEN_TORCH_THREAD_RECEIPT,
            {"intraop_threads": 1, "interop_threads": 1},
        )
        self.assertEqual(torch.get_num_threads(), 1)
        self.assertEqual(torch.get_num_interop_threads(), 1)

    def test_small_exact_one_shot_control_passes(self) -> None:
        result = probe.run_exact_compiled_control(
            self.api,
            context_count=1,
            nominal_bands=(8,),
            pairs_per_endpoint_band=1,
            continuation_max_length=2,
            run_periodic=False,
        )
        self.assertTrue(result["audit"]["pass"])
        self.assertTrue(result["audit"]["complete_finite_required_panel"])
        self.assertEqual(result["audit"]["expected_accuracy_minimum"], 1.0)
        self.assertEqual(result["audit"]["wrong_control_accuracy_maximum"], 0.0)
        self.assertEqual(
            result["audit"]["wrong_control_counterfactual_accuracy_minimum"], 1.0
        )

    def test_random_key_order_and_runtime_consumption_match(self) -> None:
        pairs = self.path_banks["evaluation"].pairs[:2]
        tiny_bank = probe.PathPairBank(
            split="unit",
            pairs=pairs,
            receipt={"source": "unit subset"},
        )
        manifest = probe.make_random_key_manifest(2, tiny_bank, split_code=2)
        self.assertEqual(manifest["key_count"], 2 * 2 * 8 * 4)
        expected_keys = [
            list(
                probe.random_ray_key(
                    split_code=2,
                    context_id=context_id,
                    nominal_band=pair.nominal_band,
                    endpoint=pair.endpoint,
                    pair_id=pair.pair_index,
                    start=start,
                    draw_id=draw,
                )
            )
            for context_id in range(2)
            for pair in pairs
            for start in range(8)
            for draw in range(4)
        ]
        self.assertEqual(manifest["keys"], expected_keys)
        first_key = [
            probe.RANDOM_RAY_SEED,
            2,
            0,
            pairs[0].nominal_band,
            pairs[0].endpoint,
            pairs[0].pair_index,
            0,
            0,
        ]
        self.assertEqual(manifest["keys"][0], first_key)
        self.assertEqual(manifest["keys"][31][-2:], [7, 3])
        self.assertEqual(
            manifest["keys"][32][2:6],
            [
                0,
                pairs[1].nominal_band,
                pairs[1].endpoint,
                pairs[1].pair_index,
            ],
        )
        self.assertEqual(manifest["keys"][64][2], 1)
        independent_first_draw = np.random.Generator(
            np.random.PCG64(np.random.SeedSequence(first_key))
        ).standard_normal(12)
        np.testing.assert_array_equal(
            probe.random_base_standard_normal(first_key), independent_first_draw
        )
        expected_stream = hashlib.sha256()
        for key in expected_keys:
            expected_stream.update(
                np.ascontiguousarray(
                    probe.random_base_standard_normal(key), dtype=np.float64
                ).tobytes()
            )
        self.assertEqual(
            manifest["base_standard_normal_stream_sha256"],
            expected_stream.hexdigest(),
        )

        model = probe.ExactCompiledModel()
        observed_stream = hashlib.sha256()
        observed_rays = []
        for context_id in range(2):
            for pair in pairs:
                observed_rays.append(
                    probe.random_ray_states(
                        model,
                        split_code=2,
                        context_id=context_id,
                        pair=pair,
                        starts=range(8),
                        base_stream_digest=observed_stream,
                    )
                )
        self.assertEqual(observed_stream.hexdigest(), expected_stream.hexdigest())
        metric = model.invariant_metric()
        for rays in observed_rays:
            self.assertEqual(rays.shape, (4, 8, 12))
            self.assertEqual(rays.dtype, torch.float32)
            norm_squared = torch.einsum("...i,ij,...j->...", rays, metric, rays)
            torch.testing.assert_close(norm_squared, torch.ones_like(norm_squared))
        pair = pairs[0]
        repeated = probe.random_ray_states(
            model,
            split_code=2,
            context_id=0,
            pair=pair,
            starts=range(8),
        )
        torch.testing.assert_close(observed_rays[0], repeated)

    def test_manifest_is_deterministic_checkpoint_free_and_budgeted(self) -> None:
        with mock.patch.object(
            probe.torch,
            "load",
            side_effect=AssertionError("manifest must not deserialize checkpoints"),
        ):
            manifest = probe.manifest_only_dry_run(probe.DEFAULT_PACKAGE)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "MANIFEST_DRY_RUN.json"
                self.write_json(path, manifest)
                binding = probe.assert_manifest_matches_runtime(
                    path, package=probe.DEFAULT_PACKAGE
                )
        self.assertEqual(manifest["learned_checkpoint_load_count"], 0)
        self.assertEqual(binding["freeze_receipt_sha256"], manifest["freeze_receipt_sha256"])
        counts = manifest["counts"]
        self.assertEqual(counts["path_pairs_per_split"], 48)
        self.assertEqual(counts["random_key_count"], 32 * 48 * 8 * 4)
        self.assertEqual(counts["primary_suffix_tree_edges"], 30)
        self.assertEqual(counts["merged_W4_plus_stress_suffix_tree_edges"], 129)
        self.assertEqual(counts["incremental_stress_edges_beyond_W4"], 99)
        self.assertEqual(counts["periodic_prefix_physical_repair_modes"], 24)
        self.assertEqual(counts["periodic_suffix_physical_modes"], 25)
        self.assertEqual(counts["single_reset_interventions"], 12)
        self.assertEqual(counts["periodic_condition_cadence_logical_modes"], 28)

        budget = manifest["budget"]
        self.assertTrue(budget["chunk_ceiling_pass"])
        self.assertTrue(budget["estimated_peak_within_declared_ceiling"])
        self.assertLessEqual(
            budget["maximum_starting_state_chunk"], budget["required_chunk_ceiling"]
        )
        matvec = budget["float32_recurrent_matvec_per_checkpoint"]
        contributing = (
            "calibration_prefix",
            "evaluation_prefix_shared_primary_stress_periodic_native",
            "custom_rollout_control",
            "exhaustive_section_selector_generator_control",
            "cut_selector_commutation_control",
            "one_shot_merged_W4_plus_stress_tree",
            "periodic_repair_prefix_native_is_cached",
            "periodic_W4_physical_tree",
        )
        self.assertEqual(matvec["total"], sum(matvec[key] for key in contributing))
        self.assertEqual(
            budget["float32_recurrent_matvec_all_12_checkpoints"],
            12 * matvec["total"],
        )
        exact_total = budget["checkpoint_free_exact_compiled_preflight_matvec"][
            "total"
        ]
        self.assertEqual(
            budget["total_matvec_exact_preflight_plus_all_12_checkpoints"],
            exact_total + 12 * matvec["total"],
        )

    def test_manifest_internal_digest_and_budget_tamper_fail_closed(self) -> None:
        manifest = probe.manifest_only_dry_run(probe.DEFAULT_PACKAGE)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "MANIFEST_DRY_RUN.json"
            tampered = json.loads(json.dumps(manifest))
            tampered["budget"]["estimated_peak_within_declared_ceiling"] = False
            payload = dict(tampered)
            payload.pop("freeze_receipt_sha256", None)
            tampered["freeze_receipt_sha256"] = probe.canonical_json_digest(payload)
            self.write_json(path, tampered)
            with self.assertRaises(RuntimeError):
                probe.assert_manifest_matches_runtime(path, package=probe.DEFAULT_PACKAGE)

            tampered = json.loads(json.dumps(manifest))
            tampered["counts"]["random_key_count"] += 1
            self.write_json(path, tampered)
            with self.assertRaisesRegex(RuntimeError, "internally inconsistent"):
                probe.assert_manifest_matches_runtime(path, package=probe.DEFAULT_PACKAGE)

            for label, mutate in (
                (
                    "boolean as integer",
                    lambda payload: payload["budget"].__setitem__(
                        "chunk_ceiling_pass", 1
                    ),
                ),
                (
                    "integer as boolean",
                    lambda payload: payload["torch_thread_runtime"].__setitem__(
                        "intraop_threads", True
                    ),
                ),
            ):
                with self.subTest(type_tamper=label):
                    tampered = json.loads(json.dumps(manifest))
                    mutate(tampered)
                    digest_payload = dict(tampered)
                    digest_payload.pop("freeze_receipt_sha256", None)
                    tampered["freeze_receipt_sha256"] = (
                        probe.canonical_json_digest(digest_payload)
                    )
                    self.write_json(path, tampered)
                    with self.assertRaisesRegex(RuntimeError, "does not match"):
                        probe.assert_manifest_matches_runtime(
                            path, package=probe.DEFAULT_PACKAGE
                        )

    def test_source_manifest_binding_rejects_temp_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            shutil.copy2(
                probe.DEFAULT_PACKAGE / "MANIFEST.json", package / "MANIFEST.json"
            )
            shutil.copytree(probe.DEFAULT_PACKAGE / "src", package / "src")
            receipt = probe.verify_package_source_integrity(package)
            self.assertGreater(receipt["source_file_count"], 0)
            target = next(
                path
                for path in sorted((package / "src").rglob("*.py"))
                if path.is_file()
            )
            original = target.read_bytes()
            target.write_bytes(original + b"\n# unit-test tamper\n")
            with self.assertRaisesRegex(
                RuntimeError, "sealed source .* exceeds its frozen byte ceiling"
            ):
                probe.verify_package_source_integrity(package)
            target.write_bytes(original)
            same_size = bytearray(original)
            same_size[len(same_size) // 2] ^= 1
            target.write_bytes(same_size)
            with self.assertRaisesRegex(RuntimeError, "source SHA-256 mismatch"):
                probe.verify_package_source_integrity(package)

    def test_source_integrity_rejects_unmanifested_python_and_bytecode(self) -> None:
        poison_paths = (
            Path("src/unmanifested.py"),
            Path("src/unmanifested.pyc"),
            Path("src/komorebi_neuralese/__pycache__/poison.cpython-312.pyc"),
        )
        for relative in poison_paths:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                package = Path(directory)
                shutil.copy2(
                    probe.DEFAULT_PACKAGE / "MANIFEST.json",
                    package / "MANIFEST.json",
                )
                shutil.copytree(probe.DEFAULT_PACKAGE / "src", package / "src")
                poison = package / relative
                poison.parent.mkdir(parents=True, exist_ok=True)
                poison.write_bytes(b"unmanifested source poison\n")
                with self.assertRaisesRegex(RuntimeError, "file set differs"):
                    probe.verify_package_source_integrity(package)

    def test_sealed_import_does_not_create_bytecode_cache(self) -> None:
        source_root = probe.DEFAULT_PACKAGE / "src"
        probe.verify_package_source_integrity(probe.DEFAULT_PACKAGE)
        self.assertFalse(any(path.is_dir() for path in source_root.rglob("__pycache__")))
        self.assertFalse(any(path.is_file() for path in source_root.rglob("*.pyc")))
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            sys, "pycache_prefix", directory
        ):
            with self.assertRaisesRegex(RuntimeError, "bytecode-cache prefixes"):
                probe.import_v04_api(probe.DEFAULT_PACKAGE)
        self.assertIsNone(sys.pycache_prefix)
        with mock.patch.object(sys, "dont_write_bytecode", False):
            probe.import_v04_api(probe.DEFAULT_PACKAGE)
            self.assertTrue(sys.dont_write_bytecode)
        self.assertFalse(any(path.is_dir() for path in source_root.rglob("__pycache__")))
        self.assertFalse(any(path.is_file() for path in source_root.rglob("*.pyc")))
        probe.verify_package_source_integrity(probe.DEFAULT_PACKAGE)

    def test_checkpoint_census_binds_seal_and_checkpoint_without_loading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            self.copy_census_without_loading(package)
            with mock.patch.object(
                probe.torch,
                "load",
                side_effect=AssertionError("census must never deserialize a checkpoint"),
            ):
                verified, seal = probe.verify_checkpoint_census(package)
            self.assertEqual(len(verified), 12)
            self.assertEqual(len(seal["checkpoints"]), 12)

            seal_path = package / "results/packet_closure_pilot/CHECKPOINT_SEAL.json"
            original_seal = seal_path.read_bytes()
            seal_path.write_bytes(original_seal + b"\n")
            with self.assertRaisesRegex(
                RuntimeError, "sealed package artifact .* exceeds its frozen byte ceiling"
            ):
                probe.verify_checkpoint_census(package)
            seal_path.write_bytes(original_seal)
            same_size_seal = bytearray(original_seal)
            same_size_seal[len(same_size_seal) // 2] ^= 1
            seal_path.write_bytes(same_size_seal)
            with mock.patch.object(
                probe.torch,
                "load",
                side_effect=AssertionError("census must never deserialize a checkpoint"),
            ):
                with self.assertRaisesRegex(RuntimeError, "artifact SHA-256 mismatch"):
                    probe.verify_checkpoint_census(package)
            seal_path.write_bytes(original_seal)

            checkpoint = Path(verified[0]["checkpoint"])
            original_checkpoint = checkpoint.read_bytes()
            checkpoint.write_bytes(original_checkpoint + b"tamper")
            with mock.patch.object(
                probe.torch,
                "load",
                side_effect=AssertionError("census must never deserialize a checkpoint"),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "sealed package artifact .* exceeds its frozen byte ceiling",
                ):
                    probe.verify_checkpoint_census(package)
            checkpoint.write_bytes(original_checkpoint)
            same_size_checkpoint = bytearray(original_checkpoint)
            same_size_checkpoint[len(same_size_checkpoint) // 2] ^= 1
            checkpoint.write_bytes(same_size_checkpoint)
            with mock.patch.object(
                probe.torch,
                "load",
                side_effect=AssertionError("census must never deserialize a checkpoint"),
            ):
                with self.assertRaisesRegex(RuntimeError, "artifact SHA-256 mismatch"):
                    probe.verify_checkpoint_census(package)

    def test_checkpoint_loader_is_strict_and_weights_only_by_construction(self) -> None:
        loader_source = inspect.getsource(probe.load_one_verified_checkpoint)
        self.assertIn("weights_only=True", loader_source)
        self.assertIn("strict=True", loader_source)
        panel_source = inspect.getsource(probe.run_learned_panel)
        self.assertLess(
            panel_source.index("verify_checkpoint_census"),
            panel_source.index("load_one_verified_checkpoint"),
        )
        self.assertLess(
            panel_source.index("create_evaluation_bank_spend_receipt"),
            panel_source.index("load_one_verified_checkpoint"),
        )

        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "unit-checkpoint.pt"
            checkpoint_bytes = b"unit bytes that torch.load must receive exactly"
            checkpoint.write_bytes(checkpoint_bytes)
            arm = "euclidean_supervised"
            seed = 101
            sealed_digest = "d" * 64
            source_digest = "s" * 64
            contract_digest = "c" * 64
            arm_spec = probe.asdict(self.api["get_packet_closure_arm"](arm))
            payload = {
                "schema": "komorebi.neuralese.packet_closure.checkpoint.v1",
                "version": "0.4.0",
                "arm": arm,
                "train_config": {"seed": seed, "hidden_dim": 12},
                "source_digest": source_digest,
                "contract_sha256": contract_digest,
                "arm_spec": arm_spec,
                "state_dict": {"unit": torch.tensor([1.0])},
                "provenance": {"final_state_digest": sealed_digest},
            }
            incompatibility = types.SimpleNamespace(
                missing_keys=[], unexpected_keys=[]
            )
            fake_model = mock.Mock()
            fake_model.load_state_dict.return_value = incompatibility
            fake_model.to.return_value = fake_model
            fake_model.eval.return_value = fake_model
            constructors = {
                "raw": "ProjectiveLinearTableOperatorRNN",
                "polar": "PolarIsometricTableOperatorRNN",
            }
            constructor_name = constructors[arm_spec["model_family"]]
            fake_api = {
                "get_packet_closure_arm": self.api["get_packet_closure_arm"],
                "ProjectiveLinearTableOperatorRNN": mock.Mock(),
                "PolarIsometricTableOperatorRNN": mock.Mock(),
                "state_dict_digest": mock.Mock(return_value=sealed_digest),
            }
            fake_api[constructor_name].return_value = fake_model
            verified = {
                "checkpoint": checkpoint,
                "checkpoint_sha256": hashlib.sha256(checkpoint_bytes).hexdigest(),
                "arm": arm,
                "seed": seed,
                "sealed_state_dict_digest": sealed_digest,
                "sealed_manifest_binding": {"size": len(checkpoint_bytes)},
            }
            seal = {
                "source_digest": source_digest,
                "contract_sha256": contract_digest,
            }
            with mock.patch.object(
                probe, "read_file_snapshot", wraps=probe.read_file_snapshot
            ) as snapshot_reader, mock.patch.object(
                probe.torch, "load", return_value=payload
            ) as torch_load, mock.patch.object(probe, "verify_float32_model"):
                loaded = probe.load_one_verified_checkpoint(
                    verified, seal, fake_api
                )
            snapshot_reader.assert_called_once_with(
                checkpoint,
                label=f"sealed checkpoint {checkpoint.name}",
                maximum_bytes=len(checkpoint_bytes),
            )
            self.assertIs(loaded["model"], fake_model)
            load_buffer = torch_load.call_args.args[0]
            self.assertEqual(load_buffer.getvalue(), checkpoint_bytes)
            self.assertEqual(torch_load.call_args.kwargs["map_location"], "cpu")
            self.assertIs(torch_load.call_args.kwargs["weights_only"], True)
            fake_model.load_state_dict.assert_called_once_with(
                payload["state_dict"], strict=True
            )
            fake_model.to.assert_called_once_with(
                device="cpu", dtype=torch.float32
            )
            fake_model.eval.assert_called_once_with()
            tampered_checkpoint_bytes = bytearray(checkpoint_bytes)
            tampered_checkpoint_bytes[len(tampered_checkpoint_bytes) // 2] ^= 1
            checkpoint.write_bytes(tampered_checkpoint_bytes)
            with mock.patch.object(probe.torch, "load") as forbidden_load:
                with self.assertRaisesRegex(RuntimeError, "changed after census"):
                    probe.load_one_verified_checkpoint(verified, seal, fake_api)
            forbidden_load.assert_not_called()

    def test_learned_panel_terminal_precommit_revalidation_order(self) -> None:
        source = inspect.getsource(probe.run_learned_panel)
        run_publication = source.rindex(
            "run_sha = _write_json_exclusive(run_path, result)"
        )
        manifest_publication = source.rindex(
            "bundle_manifest_sha = _write_json_exclusive(bundle_manifest_path, bundle_manifest)"
        )
        terminal_archive = source.rindex("terminal_archive_sha = sha256_file(archive)")
        terminal_source = source.rindex(
            "terminal_source_integrity = verify_package_source_integrity(package)"
        )
        terminal_census = source.rindex(
            "terminal_checkpoint_census, terminal_seal = verify_checkpoint_census(package)"
        )
        terminal_freeze = source.rindex(
            "terminal_freeze = assert_protocol_frozen(package=package)"
        )
        terminal_compare = source.rindex(
            "type_strict_equal(terminal_freeze, freeze)"
        )
        commit_publication = source.rindex(
            "_write_json_exclusive(bundle_path / COMMIT_FILENAME, commit)"
        )
        self.assertLess(run_publication, manifest_publication)
        self.assertLess(manifest_publication, terminal_archive)
        self.assertLess(terminal_archive, terminal_source)
        self.assertLess(terminal_source, terminal_census)
        self.assertLess(terminal_census, terminal_freeze)
        self.assertLess(terminal_freeze, terminal_compare)
        self.assertLess(terminal_compare, commit_publication)
        self.assertNotIn(
            "load_one_verified_checkpoint",
            source[terminal_freeze:commit_publication],
        )
        self.assertNotIn(
            "_write_json_exclusive(", source[terminal_archive:commit_publication]
        )
        self.assertEqual(source[terminal_archive:].count("_write_json_exclusive("), 1)
        self.assertFalse(probe.type_strict_equal({"pass": True}, {"pass": 1}))

    def test_root_protocol_receipt_binds_framework_primary_and_crosscheck_bytes(self) -> None:
        project_root = probe.HERE.parent.resolve()
        with tempfile.TemporaryDirectory(dir=project_root) as directory:
            root = Path(directory)
            paths = {
                "analysis_protocol": root / "ANALYSIS_PROTOCOL.md",
                "theoretical_framework": root / "THEORETICAL_FRAMEWORK.md",
                "primary_implementation": root / "run_probe.py",
                "primary_tests": root / "test_probe.py",
                "primary_machine_contract": root / "PROTOCOL.json",
                "primary_manifest_dry_run": root / "MANIFEST_DRY_RUN.json",
                "primary_static_review": root / "STATIC_REVIEW_PASS.json",
                "independent_crosscheck_protocol": root / "cross_PROTOCOL.json",
                "independent_crosscheck_implementation": root / "cross_probe.py",
                "independent_crosscheck_tests": root / "cross_test.py",
                "independent_crosscheck_freeze_receipt": root / "cross_FROZEN.sha256",
            }
            for name, path in paths.items():
                if name != "independent_crosscheck_freeze_receipt":
                    path.write_text(f"unit artifact: {name}\n", encoding="utf-8")
            paths["independent_crosscheck_freeze_receipt"].write_text(
                probe.sha256_file(paths["independent_crosscheck_protocol"]) + "\n",
                encoding="utf-8",
            )
            artifact_paths = {
                name: path.resolve().relative_to(project_root).as_posix()
                for name, path in paths.items()
            }
            artifact_hashes = {
                name: probe.sha256_file(path) for name, path in paths.items()
            }
            manifest = {"freeze_receipt_sha256": "a" * 64}
            receipt = {
                "schema": "komorebi.neuralese.semantic_retraction.protocol_receipt.v1",
                "version": probe.VERSION,
                "author": probe.AUTHOR,
                "status": "FROZEN_BEFORE_LEARNED_OUTCOMES",
                "frozen_date": "2026-09-03",
                "frozen_before_learned_outcomes": True,
                "bank_seeds": {
                    "prior_context": probe.PRIOR_CONTEXT_SEED,
                    "calibration_context": probe.CALIBRATION_CONTEXT_SEED,
                    "evaluation_context": probe.EVALUATION_CONTEXT_SEED,
                    "calibration_path": probe.CALIBRATION_PATH_SEED,
                    "evaluation_path": probe.EVALUATION_PATH_SEED,
                    "stress_path": probe.STRESS_PATH_SEED,
                    "random_ray": probe.RANDOM_RAY_SEED,
                },
                "artifact_paths": artifact_paths,
                "artifact_sha256": artifact_hashes,
                "source_provenance": {
                    "source_archive_sha256": probe.EXPECTED_ARCHIVE_SHA256,
                    "source_package_manifest_sha256": (
                        probe.EXPECTED_PACKAGE_MANIFEST_SHA256
                    ),
                },
                "manifest_freeze_receipt_sha256": manifest[
                    "freeze_receipt_sha256"
                ],
            }
            receipt["receipt_sha256"] = probe.canonical_json_digest(receipt)
            receipt_path = root / "PROTOCOL_RECEIPT.json"
            self.write_json(receipt_path, receipt)
            patch_values = {
                "PROTOCOL_PATH": paths["analysis_protocol"],
                "THEORETICAL_FRAMEWORK_PATH": paths["theoretical_framework"],
                "TEST_PATH": paths["primary_tests"],
                "MACHINE_CONTRACT_PATH": paths["primary_machine_contract"],
                "MANIFEST_DRY_RUN_PATH": paths["primary_manifest_dry_run"],
                "STATIC_REVIEW_RELEASE_PATH": paths["primary_static_review"],
                "INDEPENDENT_CROSSCHECK_PROTOCOL_PATH": paths[
                    "independent_crosscheck_protocol"
                ],
                "INDEPENDENT_CROSSCHECK_IMPLEMENTATION_PATH": paths[
                    "independent_crosscheck_implementation"
                ],
                "INDEPENDENT_CROSSCHECK_TEST_PATH": paths[
                    "independent_crosscheck_tests"
                ],
                "INDEPENDENT_CROSSCHECK_FREEZE_RECEIPT_PATH": paths[
                    "independent_crosscheck_freeze_receipt"
                ],
                "ROOT_PROTOCOL_RECEIPT_PATH": receipt_path,
                "__file__": str(paths["primary_implementation"]),
            }
            with mock.patch.multiple(probe, **patch_values):
                validated = probe.validate_root_protocol_receipt(
                    manifest, receipt_path=receipt_path
                )
                self.assertEqual(
                    validated["receipt_sha256"], receipt["receipt_sha256"]
                )
                original_theory = paths["theoretical_framework"].read_bytes()
                paths["theoretical_framework"].write_bytes(
                    original_theory + b"stale\n"
                )
                with self.assertRaisesRegex(RuntimeError, "artifact hashes"):
                    probe.validate_root_protocol_receipt(
                        manifest, receipt_path=receipt_path
                    )
                paths["theoretical_framework"].write_bytes(original_theory)

                original_crosscheck = paths[
                    "independent_crosscheck_protocol"
                ].read_bytes()
                paths["independent_crosscheck_protocol"].write_bytes(
                    original_crosscheck + b"stale freeze binding\n"
                )
                resigned_crosscheck = json.loads(json.dumps(receipt))
                resigned_crosscheck["artifact_sha256"][
                    "independent_crosscheck_protocol"
                ] = probe.sha256_file(paths["independent_crosscheck_protocol"])
                resigned_crosscheck.pop("receipt_sha256")
                resigned_crosscheck["receipt_sha256"] = (
                    probe.canonical_json_digest(resigned_crosscheck)
                )
                self.write_json(receipt_path, resigned_crosscheck)
                with self.assertRaisesRegex(RuntimeError, "freeze receipt"):
                    probe.validate_root_protocol_receipt(
                        manifest, receipt_path=receipt_path
                    )
                paths["independent_crosscheck_protocol"].write_bytes(
                    original_crosscheck
                )

                wrong_manifest_binding = json.loads(json.dumps(receipt))
                wrong_manifest_binding["manifest_freeze_receipt_sha256"] = "e" * 64
                wrong_manifest_binding.pop("receipt_sha256")
                wrong_manifest_binding["receipt_sha256"] = (
                    probe.canonical_json_digest(wrong_manifest_binding)
                )
                self.write_json(receipt_path, wrong_manifest_binding)
                with self.assertRaisesRegex(RuntimeError, "manifest digest"):
                    probe.validate_root_protocol_receipt(
                        manifest, receipt_path=receipt_path
                    )

                integer_seed = json.loads(json.dumps(receipt))
                integer_seed["bank_seeds"]["prior_context"] = 1
                integer_seed.pop("receipt_sha256")
                integer_seed["receipt_sha256"] = probe.canonical_json_digest(
                    integer_seed
                )
                self.write_json(receipt_path, integer_seed)
                with mock.patch.object(probe, "PRIOR_CONTEXT_SEED", True):
                    with self.assertRaisesRegex(RuntimeError, "bank seeds"):
                        probe.validate_root_protocol_receipt(
                            manifest, receipt_path=receipt_path
                        )
                self.write_json(receipt_path, receipt)
                with self.assertRaisesRegex(RuntimeError, "receipt is absent"):
                    probe.validate_root_protocol_receipt(
                        manifest, receipt_path=root / "MISSING_RECEIPT.json"
                    )

    def test_freeze_hashes_and_static_review_pass_or_fail_closed(self) -> None:
        manifest_binding = {
            "file_sha256": "a" * 64,
            "freeze_receipt_sha256": "b" * 64,
            "receipts": {},
            "counts": {},
            "budget": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol_path = root / "ANALYSIS_PROTOCOL.md"
            machine_path = root / "PROTOCOL.json"
            review_path = root / "STATIC_REVIEW_PASS.json"
            manifest_path = root / "MANIFEST_DRY_RUN.json"
            theory_path = root / "THEORETICAL_FRAMEWORK.md"
            protocol_path.write_text(
                "# Unit protocol\n\n" + probe.REQUIRED_FROZEN_PROTOCOL_HEADER + "\n",
                encoding="utf-8",
            )
            theory_path.write_text("unit theoretical framework\n", encoding="utf-8")
            contract = json.loads(json.dumps(probe.load_machine_contract()))
            contract["status"] = "FROZEN_POSTHOC"
            contract["normative_protocol_sha256"] = probe.sha256_file(protocol_path)
            self.write_json(machine_path, contract)
            review = {
                "schema": (
                    "komorebi.neuralese.semantic_retraction.static_review.v1"
                ),
                "version": probe.VERSION,
                "author": probe.AUTHOR,
                "status": "PASS",
                "protocol_sha256": probe.sha256_file(protocol_path),
                "theoretical_framework_sha256": probe.sha256_file(theory_path),
                "implementation_sha256": probe.sha256_file(Path(probe.__file__)),
                "test_sha256": probe.sha256_file(probe.TEST_PATH),
                "machine_contract_sha256": probe.sha256_file(machine_path),
                "manifest_file_sha256": manifest_binding["file_sha256"],
                "manifest_freeze_receipt_sha256": manifest_binding[
                    "freeze_receipt_sha256"
                ],
                "checks": {
                    name: True for name in probe.REQUIRED_STATIC_REVIEW_CHECKS
                },
            }
            self.write_json(review_path, review)
            root_receipt_summary = {
                "status": "PASS",
                "receipt_sha256": "c" * 64,
                "artifact_sha256": {
                    "analysis_protocol": review["protocol_sha256"],
                    "primary_implementation": review["implementation_sha256"],
                    "primary_tests": review["test_sha256"],
                    "primary_machine_contract": review[
                        "machine_contract_sha256"
                    ],
                    "primary_manifest_dry_run": review["manifest_file_sha256"],
                    "primary_static_review": probe.sha256_file(review_path),
                    "theoretical_framework": review[
                        "theoretical_framework_sha256"
                    ],
                },
            }
            with mock.patch.object(
                probe,
                "assert_manifest_matches_runtime",
                return_value=manifest_binding,
            ), mock.patch.object(
                probe,
                "validate_root_protocol_receipt",
                return_value=root_receipt_summary,
            ) as root_receipt_validator, mock.patch.object(
                probe, "THEORETICAL_FRAMEWORK_PATH", theory_path
            ):
                frozen = probe.assert_protocol_frozen(
                    protocol_path,
                    machine_path,
                    review_path,
                    manifest_path,
                    probe.DEFAULT_PACKAGE,
                )
                self.assertEqual(frozen["review"]["status"], "PASS")
                self.assertEqual(frozen["root_protocol_receipt"]["status"], "PASS")
                root_receipt_validator.assert_called_once_with(manifest_binding)

                bad_reviews = {}
                bad_reviews["extra key"] = {**review, "unexpected": True}
                missing = dict(review)
                missing.pop("author")
                bad_reviews["missing key"] = missing
                false_check = json.loads(json.dumps(review))
                false_check["checks"][probe.REQUIRED_STATIC_REVIEW_CHECKS[0]] = False
                bad_reviews["false required check"] = false_check
                integer_check = json.loads(json.dumps(review))
                integer_check["checks"][probe.REQUIRED_STATIC_REVIEW_CHECKS[0]] = 1
                bad_reviews["integer required check"] = integer_check
                wrong_theory = dict(review)
                wrong_theory["theoretical_framework_sha256"] = "0" * 64
                bad_reviews["wrong theory hash"] = wrong_theory
                for label, bad_review in bad_reviews.items():
                    with self.subTest(static_review=label):
                        self.write_json(review_path, bad_review)
                        with self.assertRaisesRegex(RuntimeError, "static review"):
                            probe.assert_protocol_frozen(
                                protocol_path,
                                machine_path,
                                review_path,
                                manifest_path,
                                probe.DEFAULT_PACKAGE,
                            )

                self.write_json(review_path, review)
                protocol_path.write_text(
                    "# Unit protocol\n\nFreeze state: NOT FROZEN\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(RuntimeError, "exact frozen header"):
                    probe.assert_protocol_frozen(
                        protocol_path,
                        machine_path,
                        review_path,
                        manifest_path,
                        probe.DEFAULT_PACKAGE,
                    )
                protocol_path.write_text(
                    "# Unit protocol\n\n"
                    + probe.REQUIRED_FROZEN_PROTOCOL_HEADER
                    + "\n",
                    encoding="utf-8",
                )

                review_path.unlink()
                with self.assertRaisesRegex(RuntimeError, "release is absent"):
                    probe.assert_protocol_frozen(
                        protocol_path,
                        machine_path,
                        review_path,
                        manifest_path,
                        probe.DEFAULT_PACKAGE,
                    )

                protocol_path.write_text(
                    "# Unit protocol\n\n"
                    + probe.REQUIRED_FROZEN_PROTOCOL_HEADER
                    + "\nchanged after freeze\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(RuntimeError, "protocol bytes"):
                    probe.assert_protocol_frozen(
                        protocol_path,
                        machine_path,
                        review_path,
                        manifest_path,
                        probe.DEFAULT_PACKAGE,
                    )

            contract["status"] = "DRAFT_LOCKED"
            contract["normative_protocol_sha256"] = probe.sha256_file(protocol_path)
            self.write_json(machine_path, contract)
            with self.assertRaisesRegex(RuntimeError, "protocol is not frozen"):
                probe.assert_protocol_frozen(
                    protocol_path,
                    machine_path,
                    review_path,
                    manifest_path,
                    probe.DEFAULT_PACKAGE,
                )

    def test_exclusive_json_and_learned_output_reservations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.json"
            digest = probe._write_json_exclusive(artifact, {"finite": 1.0})
            self.assertEqual(digest, probe.sha256_file(artifact))
            with self.assertRaises(FileExistsError):
                probe._write_json_exclusive(artifact, {"finite": 2.0})
            with self.assertRaises(ValueError):
                probe._write_json_exclusive(root / "nan.json", {"bad": float("nan")})
            self.assertFalse((root / "nan.json").exists())

        collision_kinds = ("spend", "bundle")
        for collision in collision_kinds:
            with self.subTest(collision=collision), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output = root / "RESULTS.bundle"
                spend = root / "SPENT.json"
                bundle = probe.result_bundle_path(output)
                with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                    expected_bundle = probe.assert_fresh_learned_output_paths(
                        output, spend_path=spend
                    )
                self.assertEqual(expected_bundle, bundle)
                target = {"spend": spend, "bundle": bundle}[collision]
                if collision == "bundle":
                    target.mkdir()
                else:
                    target.write_text("reserved\n", encoding="utf-8")
                with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                    with self.assertRaisesRegex(RuntimeError, "already exists"):
                        probe.assert_fresh_learned_output_paths(output, spend_path=spend)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "RESULTS.bundle"
            custom_spend = root / "custom-spend.json"
            with self.assertRaisesRegex(RuntimeError, "global spend marker"):
                probe.assert_fresh_learned_output_paths(
                    output, spend_path=custom_spend
                )
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", output):
                with self.assertRaisesRegex(RuntimeError, "aliases"):
                    probe.assert_fresh_learned_output_paths(
                        output, spend_path=output
                    )

            dangling = root / "dangling.bundle"
            dangling.symlink_to(root / "missing-target", target_is_directory=True)
            spend = root / "SPENT.json"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                with self.assertRaisesRegex(RuntimeError, "already exists"):
                    probe.assert_fresh_learned_output_paths(
                        dangling, spend_path=spend
                    )

            suffixless = root / "RESULTS"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                with self.assertRaisesRegex(RuntimeError, "must end in .bundle"):
                    probe.assert_fresh_learned_output_paths(
                        suffixless, spend_path=spend
                    )

            outer = root / "outer.bundle"
            outer.mkdir()
            nested = outer / "inner.bundle"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                with self.assertRaisesRegex(RuntimeError, "may not be nested"):
                    probe.assert_fresh_learned_output_paths(
                        nested, spend_path=spend
                    )

            real_parent = root / "real-parent"
            real_parent.mkdir()
            alias_parent = root / "alias-parent"
            alias_parent.symlink_to(real_parent, target_is_directory=True)
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                with self.assertRaisesRegex(RuntimeError, "symbolic-link ancestry"):
                    probe.assert_fresh_learned_output_paths(
                        alias_parent / "RESULTS.bundle", spend_path=spend
                    )

            canonical = root / "subdir"
            canonical.mkdir()
            canonical_output = canonical / ".." / "CANONICAL.bundle"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                self.assertEqual(
                    probe.assert_fresh_learned_output_paths(
                        canonical_output, spend_path=spend
                    ),
                    root.resolve() / "CANONICAL.bundle",
                )

    def test_spend_receipt_is_durable_self_bound_and_non_overwritable(self) -> None:
        pair = self.path_banks["evaluation"].pairs[0]
        random_manifest = probe.make_random_key_manifest(
            1,
            probe.PathPairBank("unit", (pair,), {"source": "unit subset"}),
            split_code=2,
        )
        freeze = {
            "protocol_sha256": "1" * 64,
            "implementation_sha256": "2" * 64,
            "test_sha256": "3" * 64,
            "machine_contract_sha256": "c" * 64,
            "manifest": {
                "file_sha256": "4" * 64,
                "freeze_receipt_sha256": "5" * 64,
            },
            "root_protocol_receipt": {
                "artifact_sha256": {
                    "primary_static_review": "6" * 64,
                    "theoretical_framework": "7" * 64,
                },
                "file_sha256": "8" * 64,
                "receipt_sha256": "9" * 64,
                "source_provenance": {
                    "source_archive_sha256": "a" * 64,
                    "source_package_manifest_sha256": "b" * 64,
                },
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "RESULTS.bundle"
            spend = root / "SPENT.json"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                bundle = probe.assert_fresh_learned_output_paths(
                    output, spend_path=spend
                )
                probe.reserve_result_bundle(bundle)
                (bundle / probe.CHECKPOINT_DIRECTORY_NAME).mkdir()
                exact_sha = probe._write_json_exclusive(
                    bundle / probe.EXACT_CONTROL_FILENAME,
                    {"schema": "unit exact control", "audit": {"pass": True}},
                )
                receipt, receipt_file_sha = (
                    probe.create_evaluation_bank_spend_receipt(
                        bundle_path=bundle,
                        freeze=freeze,
                        context_banks=self.context_banks,
                        path_banks=self.path_banks,
                        continuations=self.continuations,
                        random_manifest=random_manifest,
                        exact_control_sha256=exact_sha,
                        spend_path=spend,
                    )
                )
            self.assertTrue(spend.is_file())
            self.assertTrue(output.is_dir())
            internal_spend = output / probe.SPEND_RECEIPT_FILENAME
            self.assertTrue(internal_spend.is_file())
            self.assertEqual(spend.read_bytes(), internal_spend.read_bytes())
            self.assertEqual(receipt_file_sha, probe.sha256_file(spend))
            claimed = receipt["receipt_sha256"]
            digest_payload = dict(receipt)
            digest_payload.pop("receipt_sha256")
            self.assertEqual(claimed, probe.canonical_json_digest(digest_payload))
            self.assertEqual(
                json.loads(spend.read_text(encoding="utf-8")), receipt
            )
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                with self.assertRaisesRegex(RuntimeError, "already spent"):
                    probe.create_evaluation_bank_spend_receipt(
                        bundle_path=output,
                        freeze=freeze,
                        context_banks=self.context_banks,
                        path_banks=self.path_banks,
                        continuations=self.continuations,
                        random_manifest=random_manifest,
                        exact_control_sha256=exact_sha,
                        spend_path=spend,
                    )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "RESULTS.bundle"
            spend = root / "SPENT.json"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                bundle = probe.assert_fresh_learned_output_paths(
                    output, spend_path=spend
                )
                probe.reserve_result_bundle(bundle)
                (bundle / probe.CHECKPOINT_DIRECTORY_NAME).mkdir()
                exact_sha = probe._write_json_exclusive(
                    bundle / probe.EXACT_CONTROL_FILENAME,
                    {"schema": "unit exact control", "audit": {"pass": True}},
                )
                real_writer = probe._write_json_exclusive

                def fail_internal_copy(path: Path, payload: object) -> str:
                    if Path(path) == bundle / probe.SPEND_RECEIPT_FILENAME:
                        raise OSError("simulated internal spend-copy failure")
                    return real_writer(path, payload)

                with mock.patch.object(
                    probe, "_write_json_exclusive", side_effect=fail_internal_copy
                ):
                    with self.assertRaisesRegex(
                        OSError, "simulated internal spend-copy failure"
                    ):
                        probe.create_evaluation_bank_spend_receipt(
                            bundle_path=bundle,
                            freeze=freeze,
                            context_banks=self.context_banks,
                            path_banks=self.path_banks,
                            continuations=self.continuations,
                            random_manifest=random_manifest,
                            exact_control_sha256=exact_sha,
                            spend_path=spend,
                        )
                self.assertTrue(spend.is_file())
                self.assertFalse(
                    (bundle / probe.SPEND_RECEIPT_FILENAME).exists()
                )
                with self.assertRaisesRegex(RuntimeError, "already spent"):
                    probe.create_evaluation_bank_spend_receipt(
                        bundle_path=bundle,
                        freeze=freeze,
                        context_banks=self.context_banks,
                        path_banks=self.path_banks,
                        continuations=self.continuations,
                        random_manifest=random_manifest,
                        exact_control_sha256=exact_sha,
                        spend_path=spend,
                    )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "RESULTS.bundle"
            spend = root / "SPENT.json"
            with mock.patch.object(probe, "EVALUATION_BANK_SPEND_PATH", spend):
                bundle = probe.assert_fresh_learned_output_paths(
                    output, spend_path=spend
                )
                probe.reserve_result_bundle(bundle)
                (bundle / probe.CHECKPOINT_DIRECTORY_NAME).mkdir()
                exact_sha = probe._write_json_exclusive(
                    bundle / probe.EXACT_CONTROL_FILENAME,
                    {"schema": "unit exact control", "audit": {"pass": True}},
                )
                real_writer = probe._write_json_exclusive

                def fail_global_marker(path: Path, payload: object) -> str:
                    if Path(path) == spend:
                        raise OSError("simulated global spend-marker failure")
                    return real_writer(path, payload)

                with mock.patch.object(
                    probe, "_write_json_exclusive", side_effect=fail_global_marker
                ):
                    with self.assertRaisesRegex(
                        OSError, "simulated global spend-marker failure"
                    ):
                        probe.create_evaluation_bank_spend_receipt(
                            bundle_path=bundle,
                            freeze=freeze,
                            context_banks=self.context_banks,
                            path_banks=self.path_banks,
                            continuations=self.continuations,
                            random_manifest=random_manifest,
                            exact_control_sha256=exact_sha,
                            spend_path=spend,
                        )
                self.assertFalse(spend.exists())
                self.assertFalse(
                    (bundle / probe.SPEND_RECEIPT_FILENAME).exists()
                )

    def test_control_output_guard_is_exclusive_protected_and_outside_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "CONTROL.json"
            self.assertEqual(probe.assert_safe_control_output_path(valid), valid)
            valid.write_text("reserved\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                probe.assert_safe_control_output_path(valid)

            dangling = root / "dangling.json"
            dangling.symlink_to(root / "missing-control")
            with self.assertRaises(FileExistsError):
                probe.assert_safe_control_output_path(dangling)

            bundle = root / "nested.bundle"
            bundle.mkdir()
            with self.assertRaisesRegex(RuntimeError, "result bundle"):
                probe.assert_safe_control_output_path(bundle / "CONTROL.json")

            package = root / "sealed-package"
            (package / "src").mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "sealed package"):
                probe.assert_safe_control_output_path(
                    package / "CONTROL.json", package=package
                )
            alias = root / "package-alias"
            alias.symlink_to(package, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "symbolic-link ancestry"):
                probe.assert_safe_control_output_path(
                    alias / "src" / "CONTROL.json", package=package
                )

        for protected in (
            probe.DEFAULT_RESULT_BUNDLE,
            probe.EVALUATION_BANK_SPEND_PATH,
            probe.PROTOCOL_PATH,
        ):
            with self.subTest(protected=protected):
                with self.assertRaises((RuntimeError, FileExistsError)):
                    probe.assert_safe_control_output_path(protected)
        main_source = inspect.getsource(probe.main)
        self.assertLess(
            main_source.index("assert_safe_control_output_path"),
            main_source.index("run_exact_compiled_control", main_source.index("run_controls")),
        )

    def test_manifest_budget_flags_and_pre_spend_disk_headroom_are_enforced(self) -> None:
        budget = {
            "maximum_checkpoint_shard_bytes": probe.MAXIMUM_CHECKPOINT_SHARD_BYTES,
            "maximum_exact_control_bytes": probe.MAXIMUM_EXACT_CONTROL_BYTES,
            "maximum_bundle_metadata_bytes": probe.MAXIMUM_BUNDLE_METADATA_BYTES,
            "result_disk_safety_margin_bytes": probe.RESULT_DISK_SAFETY_MARGIN_BYTES,
            "minimum_free_disk_bytes_before_spend": (
                probe.MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND
            ),
            "result_bundle_file_count": 17,
            "chunk_ceiling_pass": True,
            "estimated_peak_within_declared_ceiling": True,
            "maximum_starting_state_chunk": 200,
            "required_chunk_ceiling": 4096,
            "estimated_peak_working_set_bytes": 512,
            "declared_peak_working_set_ceiling_bytes": 1024,
        }
        freeze = {"manifest": {"budget": budget}}
        enough_disk = mock.Mock(
            free=probe.MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND + 1
        )
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            probe.shutil, "disk_usage", return_value=enough_disk
        ):
            result = probe.assert_manifest_budget_and_disk_headroom(
                freeze, Path(directory) / "RESULTS.bundle"
            )
            self.assertTrue(result["headroom_pass"])
            self.assertTrue(result["manifest_budget_checks_pass"])

            for flag in (
                "chunk_ceiling_pass",
                "estimated_peak_within_declared_ceiling",
            ):
                with self.subTest(flag=flag):
                    bad = json.loads(json.dumps(budget))
                    bad[flag] = False
                    with self.assertRaisesRegex(RuntimeError, "did not pass"):
                        probe.assert_manifest_budget_and_disk_headroom(
                            {"manifest": {"budget": bad}},
                            Path(directory) / "RESULTS.bundle",
                        )

            inconsistent = json.loads(json.dumps(budget))
            inconsistent["maximum_starting_state_chunk"] = 4097
            with self.assertRaisesRegex(RuntimeError, "inequalities"):
                probe.assert_manifest_budget_and_disk_headroom(
                    {"manifest": {"budget": inconsistent}},
                    Path(directory) / "RESULTS.bundle",
                )

            wrong_publication = json.loads(json.dumps(budget))
            wrong_publication["maximum_checkpoint_shard_bytes"] += 1
            with self.assertRaisesRegex(RuntimeError, "publication budget"):
                probe.assert_manifest_budget_and_disk_headroom(
                    {"manifest": {"budget": wrong_publication}},
                    Path(directory) / "RESULTS.bundle",
                )

        too_little_disk = mock.Mock(
            free=probe.MINIMUM_FREE_DISK_BYTES_BEFORE_SPEND - 1
        )
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            probe.shutil, "disk_usage", return_value=too_little_disk
        ):
            with self.assertRaisesRegex(RuntimeError, "insufficient free disk"):
                probe.assert_manifest_budget_and_disk_headroom(
                    freeze, Path(directory) / "RESULTS.bundle"
                )

    def test_result_bundle_verifier_accepts_exact_bundle_and_external_spend_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self.make_valid_synthetic_result_bundle(
                root / "RESULTS.bundle"
            )
            external_spend = root / "EVALUATION_BANK_SPENT.json"
            shutil.copy2(fixture["spend_path"], external_spend)
            portable = probe.verify_result_bundle(fixture["bundle"])
            self.assertFalse(portable["external_spend_marker_checked"])
            verified = probe.verify_result_bundle(
                fixture["bundle"], external_spend_path=external_spend
            )
            self.assertEqual(verified["status"], "PASS")
            self.assertEqual(verified["checkpoint_shard_count"], 12)
            self.assertTrue(verified["exact_file_set"])
            self.assertTrue(verified["portable_relative_paths"])
            self.assertTrue(verified["no_symbolic_links"])
            self.assertTrue(verified["external_spend_marker_checked"])

    def test_result_bundle_verifier_rejects_spend_semantic_tamper(self) -> None:
        mutations = {
            "extra key": lambda spend: spend.__setitem__("unexpected", True),
            "missing key": lambda spend: spend.pop("protocol_sha256"),
            "prospective false": lambda spend: spend.__setitem__(
                "no_rerun_or_resume_is_prospective", False
            ),
            "prospective integer": lambda spend: spend.__setitem__(
                "no_rerun_or_resume_is_prospective", 1
            ),
            "crash false": lambda spend: spend.__setitem__(
                "crash_after_this_receipt_still_spends_bank", False
            ),
            "crash integer": lambda spend: spend.__setitem__(
                "crash_after_this_receipt_still_spends_bank", 1
            ),
            "zero timestamp": lambda spend: spend.__setitem__(
                "created_unix_time_ns", 0
            ),
            "boolean timestamp": lambda spend: spend.__setitem__(
                "created_unix_time_ns", True
            ),
            "nonleaf name": lambda spend: spend.__setitem__(
                "planned_bundle_leaf_name", "nested/RESULTS.bundle"
            ),
            "suffixless name": lambda spend: spend.__setitem__(
                "planned_bundle_leaf_name", "RESULTS"
            ),
            "relative planned path": lambda spend: spend.__setitem__(
                "planned_bundle_absolute_path_non_normative", "RESULTS.bundle"
            ),
            "planned path name mismatch": lambda spend: spend.__setitem__(
                "planned_bundle_absolute_path_non_normative", "/tmp/OTHER.bundle"
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(spend_tamper=label), tempfile.TemporaryDirectory() as directory:
                fixture = self.make_valid_synthetic_result_bundle(
                    Path(directory) / "RESULTS.bundle"
                )
                spend = fixture["spend"]
                assert isinstance(spend, dict)
                mutate(spend)
                self.refresh_synthetic_result_bundle(fixture)
                with self.assertRaisesRegex(RuntimeError, "spend receipt"):
                    probe.verify_result_bundle(fixture["bundle"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self.make_valid_synthetic_result_bundle(
                root / "RESULTS.bundle"
            )
            spend = fixture["spend"]
            assert isinstance(spend, dict)
            spend["planned_bundle_leaf_name"] = "OTHER.bundle"
            spend["planned_bundle_absolute_path_non_normative"] = str(
                root / "OTHER.bundle"
            )
            self.refresh_synthetic_result_bundle(fixture)
            external_spend = root / "EVALUATION_BANK_SPENT.json"
            shutil.copy2(fixture["spend_path"], external_spend)
            with self.assertRaisesRegex(RuntimeError, "spend receipt is invalid"):
                probe.verify_result_bundle(fixture["bundle"])
            with self.assertRaisesRegex(RuntimeError, "spend receipt is invalid"):
                probe.verify_result_bundle(
                    fixture["bundle"], external_spend_path=external_spend
                )

    def test_result_bundle_verifier_revalidates_frozen_provenance_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.make_valid_synthetic_result_bundle(
                Path(directory) / "RESULTS.bundle"
            )
            run = fixture["run"]
            assert isinstance(run, dict)
            run["protocol"]["static_review"]["checks"][
                probe.REQUIRED_STATIC_REVIEW_CHECKS[0]
            ] = False
            self.refresh_synthetic_result_bundle(fixture)
            with self.assertRaisesRegex(RuntimeError, "static review"):
                probe.verify_result_bundle(fixture["bundle"])

        root_links = (
            ("analysis_protocol", "sha256"),
            ("primary_implementation", "implementation_sha256"),
            ("primary_tests", "test_sha256"),
        )
        for artifact_key, run_key in root_links:
            with self.subTest(root_link=artifact_key), tempfile.TemporaryDirectory() as directory:
                fixture = self.make_valid_synthetic_result_bundle(
                    Path(directory) / "RESULTS.bundle"
                )
                run = fixture["run"]
                assert isinstance(run, dict)
                self.assertEqual(
                    run["protocol"]["root_protocol_receipt"]["artifact_sha256"][
                        artifact_key
                    ],
                    run["protocol"][run_key],
                )
                run["protocol"]["root_protocol_receipt"]["artifact_sha256"][
                    artifact_key
                ] = "f" * 64
                self.refresh_synthetic_result_bundle(fixture)
                with self.assertRaisesRegex(RuntimeError, "terminal artifact receipt"):
                    probe.verify_result_bundle(fixture["bundle"])

    def test_result_bundle_verifier_recomputes_each_shard_claim_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.make_valid_synthetic_result_bundle(
                Path(directory) / "RESULTS.bundle"
            )
            descriptor = fixture["checkpoint_descriptors"][0]
            relative = descriptor["path"]
            shard = fixture["shards"][relative]
            label = probe.REQUIRED_PASS_BEARING_CLAIM_LABELS[0]
            # The producer's in-memory claim matrix may share mappings with its
            # gate inputs.  A serialized bundle cannot preserve those aliases,
            # so detach the claimed matrix before tampering with only the claim.
            shard["independent_claim_matrix"] = json.loads(
                json.dumps(shard["independent_claim_matrix"])
            )
            shard["independent_claim_matrix"][label]["pass"] = False
            shard_path = fixture["bundle"] / relative
            self.write_json(shard_path, shard)
            shard_sha = probe.sha256_file(shard_path)
            descriptor["sha256"] = shard_sha
            run = fixture["run"]
            record = next(
                row
                for row in run["checkpoint_results"]
                if row["arm"] == descriptor["arm"]
                and row["seed"] == descriptor["seed"]
            )
            record["checkpoint_shard_sha256"] = shard_sha
            record["checkpoint_shard_bytes"] = shard_path.stat().st_size
            record["independent_claim_matrix"] = shard[
                "independent_claim_matrix"
            ]
            self.refresh_synthetic_result_bundle(fixture)
            with self.assertRaisesRegex(RuntimeError, "differs from gate inputs"):
                probe.verify_result_bundle(fixture["bundle"])

    def test_result_bundle_verifier_requires_unchanged_seal_bound_state(self) -> None:
        mutations = {
            "unchanged false": lambda control: control.__setitem__(
                "unchanged", False
            ),
            "unchanged integer": lambda control: control.__setitem__(
                "unchanged", 1
            ),
            "seal match false": lambda control: control.__setitem__(
                "seal_match", False
            ),
            "independent digest changed": lambda control: control.__setitem__(
                "independent_digest_after", "f" * 64
            ),
            "seal digest changed": lambda control: control.__setitem__(
                "seal_compatible_digest_after", "f" * 64
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(state_control=label), tempfile.TemporaryDirectory() as directory:
                fixture = self.make_valid_synthetic_result_bundle(
                    Path(directory) / "RESULTS.bundle"
                )
                descriptor = fixture["checkpoint_descriptors"][0]
                relative = descriptor["path"]
                shard = fixture["shards"][relative]
                mutate(shard["whole_analysis_state_dict_control"])
                shard_path = fixture["bundle"] / relative
                self.write_json(shard_path, shard)
                shard_sha = probe.sha256_file(shard_path)
                descriptor["sha256"] = shard_sha
                run = fixture["run"]
                record = next(
                    row
                    for row in run["checkpoint_results"]
                    if row["arm"] == descriptor["arm"]
                    and row["seed"] == descriptor["seed"]
                )
                record["checkpoint_shard_sha256"] = shard_sha
                record["checkpoint_shard_bytes"] = shard_path.stat().st_size
                self.refresh_synthetic_result_bundle(fixture)
                with self.assertRaisesRegex(RuntimeError, "state control is invalid"):
                    probe.verify_result_bundle(fixture["bundle"])

        for invalid in (False, 1):
            with self.subTest(run_unchanged=invalid), tempfile.TemporaryDirectory() as directory:
                fixture = self.make_valid_synthetic_result_bundle(
                    Path(directory) / "RESULTS.bundle"
                )
                fixture["run"]["checkpoint_results"][0][
                    "whole_analysis_state_dict_unchanged"
                ] = invalid
                self.refresh_synthetic_result_bundle(fixture)
                with self.assertRaisesRegex(RuntimeError, "state-control flag"):
                    probe.verify_result_bundle(fixture["bundle"])

    def test_result_bundle_verifier_rejects_commit_hash_shard_extra_and_link_tamper(self) -> None:
        scenarios = (
            "missing_commit",
            "bad_commit",
            "run_hash",
            "shard_hash",
            "extra_root",
            "path_escape",
            "shard_symlink",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fixture = self.make_valid_synthetic_result_bundle(
                    root / "RESULTS.bundle"
                )
                bundle = fixture["bundle"]
                if scenario == "missing_commit":
                    fixture["commit_path"].unlink()
                elif scenario == "bad_commit":
                    commit = dict(fixture["commit"])
                    commit["status"] = "INCOMPLETE"
                    self.write_json(fixture["commit_path"], commit)
                elif scenario == "run_hash":
                    path = fixture["run_path"]
                    path.write_bytes(path.read_bytes() + b" ")
                elif scenario == "shard_hash":
                    relative = fixture["checkpoint_descriptors"][0]["path"]
                    path = bundle / relative
                    path.write_bytes(path.read_bytes() + b" ")
                elif scenario == "extra_root":
                    (bundle / "EXTRA.json").write_text("{}\n", encoding="utf-8")
                elif scenario == "path_escape":
                    commit = dict(fixture["commit"])
                    commit["run"] = dict(commit["run"])
                    commit["run"]["path"] = "../RUN.json"
                    self.write_json(fixture["commit_path"], commit)
                elif scenario == "shard_symlink":
                    relative = fixture["checkpoint_descriptors"][0]["path"]
                    path = bundle / relative
                    outside = root / "outside.json"
                    outside.write_text("{}\n", encoding="utf-8")
                    path.unlink()
                    path.symlink_to(outside)
                with self.assertRaises(RuntimeError):
                    probe.verify_result_bundle(bundle)

        resigned_mutations = {
            "commit count float": lambda fixture: fixture["commit"].__setitem__(
                "checkpoint_shard_count", 12.0
            ),
            "claim boundary changed": lambda fixture: fixture["run"].__setitem__(
                "claim_boundary", "UNIVERSAL THEOREM CLAIMED"
            ),
            "protocol extra key": lambda fixture: fixture["run"]["protocol"].__setitem__(
                "unexpected", True
            ),
            "protocol status changed": lambda fixture: fixture["run"]["protocol"].__setitem__(
                "status", "NOT_FROZEN"
            ),
            "source extra key": lambda fixture: fixture["run"]["source"].__setitem__(
                "unexpected", True
            ),
            "runtime extra key": lambda fixture: fixture["run"]["runtime"].__setitem__(
                "unexpected", True
            ),
            "output layout extra key": lambda fixture: fixture["run"][
                "output_layout"
            ].__setitem__("unexpected", True),
            "root artifact digest not SHA": lambda fixture: fixture["run"][
                "protocol"
            ]["root_protocol_receipt"]["artifact_sha256"].__setitem__(
                "independent_crosscheck_protocol", 1
            ),
            "sealed import digest mismatch": lambda fixture: fixture["run"][
                "source"
            ]["sealed_import_origin_receipt"].__setitem__(
                "ordered_loaded_module_receipt_sha256", "f" * 64
            ),
        }
        for label, mutate in resigned_mutations.items():
            with self.subTest(resigned_schema_tamper=label), tempfile.TemporaryDirectory() as directory:
                fixture = self.make_valid_synthetic_result_bundle(
                    Path(directory) / "RESULTS.bundle"
                )
                mutate(fixture)
                self.refresh_synthetic_result_bundle(fixture)
                with self.assertRaises(RuntimeError):
                    probe.verify_result_bundle(fixture["bundle"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self.make_valid_synthetic_result_bundle(
                root / "RESULTS.bundle"
            )
            fixture["run"]["source"]["archive_filename"] = "renamed-sealed.zip"
            fixture["run"]["source"][
                "archive_absolute_path_non_normative"
            ] = str(root / "renamed-sealed.zip")
            self.refresh_synthetic_result_bundle(fixture)
            self.assertEqual(
                probe.verify_result_bundle(fixture["bundle"])["status"], "PASS"
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self.make_valid_synthetic_result_bundle(
                root / "RESULTS.bundle"
            )
            fixture["run"]["source"]["archive_filename"] = "unsafe\\name.zip"
            fixture["run"]["source"][
                "archive_absolute_path_non_normative"
            ] = str(root / "unsafe\\name.zip")
            self.refresh_synthetic_result_bundle(fixture)
            with self.assertRaisesRegex(RuntimeError, "archive naming"):
                probe.verify_result_bundle(fixture["bundle"])

        def mutate_first_shard_identity(
            fixture: dict[str, object], key: str, value: object
        ) -> None:
            descriptor = fixture["checkpoint_descriptors"][0]
            relative = descriptor["path"]
            shard = fixture["shards"][relative]
            shard[key] = value
            shard_path = fixture["bundle"] / relative
            self.write_json(shard_path, shard)
            shard_sha = probe.sha256_file(shard_path)
            descriptor["sha256"] = shard_sha
            row = next(
                record
                for record in fixture["run"]["checkpoint_results"]
                if record["arm"] == descriptor["arm"]
                and record["seed"] == descriptor["seed"]
            )
            row[key] = value
            row["checkpoint_shard_sha256"] = shard_sha
            row["checkpoint_shard_bytes"] = shard_path.stat().st_size

        for key, invalid in (
            ("model_family", 1),
            ("checkpoint_filename", 1),
            ("checkpoint_sha256", "not-a-sha256"),
        ):
            with self.subTest(shard_identity_type=key), tempfile.TemporaryDirectory() as directory:
                fixture = self.make_valid_synthetic_result_bundle(
                    Path(directory) / "RESULTS.bundle"
                )
                mutate_first_shard_identity(fixture, key, invalid)
                self.refresh_synthetic_result_bundle(fixture)
                with self.assertRaises(RuntimeError):
                    probe.verify_result_bundle(fixture["bundle"])

    def test_import_origin_receipt_and_foreign_preload_rejection(self) -> None:
        receipt = self.api["import_origin_receipt"]
        self.assertTrue(receipt["sealed_source_root_forced_to_sys_path_zero"])
        self.assertGreater(receipt["loaded_module_count"], 0)
        self.assertTrue(
            all(
                record["source_path"].startswith("src/komorebi_neuralese/")
                for record in receipt["loaded_modules"]
            )
        )

        loaded = {
            name: module
            for name, module in sys.modules.items()
            if name == "komorebi_neuralese"
            or name.startswith("komorebi_neuralese.")
        }
        with tempfile.TemporaryDirectory() as directory:
            foreign_path = Path(directory) / "foreign.py"
            foreign_path.write_text("# foreign preload\n", encoding="utf-8")
            foreign = types.ModuleType("komorebi_neuralese.foreign_probe")
            foreign.__file__ = str(foreign_path)
            sys.modules[foreign.__name__] = foreign
            try:
                with self.assertRaisesRegex(RuntimeError, "foreign preloaded"):
                    probe.import_v04_api(probe.DEFAULT_PACKAGE)
            finally:
                for name in tuple(sys.modules):
                    if name == "komorebi_neuralese" or name.startswith(
                        "komorebi_neuralese."
                    ):
                        sys.modules.pop(name, None)
                sys.modules.update(loaded)

    def test_arm_labels_are_logical_and_over_exactly_three_seeds(self) -> None:
        for invalid_margin in ("0.20", True, math.nan):
            with self.subTest(invalid_random_margin=invalid_margin):
                one_shot, periodic = self.synthetic_claim_inputs()
                one_shot["fixed_gate_inputs"]["autonomous"]["self_anchor"][
                    "accuracy_margin_over_random_ray"
                ] = invalid_margin
                with self.assertRaisesRegex(RuntimeError, "finite real number"):
                    probe.build_independent_claim_matrix(one_shot, periodic)

        arms = probe.REQUIRED_ARMS
        labels = probe.REQUIRED_PASS_BEARING_CLAIM_LABELS
        self.assertEqual(len(labels), 11)
        failing_label = labels[-1]
        records = []
        for arm in arms:
            for seed in (101, 211, 307):
                records.append(
                    {
                        "arm": arm,
                        "seed": seed,
                        "checkpoint_shard": f"{arm}_{seed}.json",
                        "checkpoint_shard_sha256": str(seed) * 8,
                        "independent_claim_matrix": {
                            label: {
                                "pass": not (
                                    label == failing_label
                                    and arm == "polar_cr"
                                    and seed == 211
                                ),
                                "detail": seed,
                            }
                            for label in labels
                        } | {
                            "qualification": "not a pass-bearing label",
                        },
                    }
                )
        aggregate = probe.aggregate_arm_claim_matrices(records)
        self.assertTrue(aggregate["target_arm_not_privileged_in_computation"])
        for arm in arms:
            self.assertTrue(aggregate["arms"][arm]["labels"][labels[0]]["pass"])
        self.assertFalse(
            aggregate["arms"]["polar_cr"]["labels"][failing_label]["pass"]
        )
        self.assertTrue(
            aggregate["arms"]["euclidean_cr"]["labels"][failing_label]["pass"]
        )
        self.assertEqual(
            set(
                aggregate["arms"]["polar_cr"]["labels"][failing_label][
                    "per_seed"
                ]
            ),
            {"101", "211", "307"},
        )
        for failing_seed in probe.REQUIRED_SEEDS:
            with self.subTest(and_uses_seed=failing_seed):
                one_seed_fails = json.loads(json.dumps(records))
                for row in one_seed_fails:
                    row["independent_claim_matrix"][labels[0]]["pass"] = True
                target = next(
                    row
                    for row in one_seed_fails
                    if row["arm"] == "euclidean_cr"
                    and row["seed"] == failing_seed
                )
                target["independent_claim_matrix"][labels[0]]["pass"] = False
                seeded = probe.aggregate_arm_claim_matrices(one_seed_fails)
                self.assertFalse(
                    seeded["arms"]["euclidean_cr"]["labels"][labels[0]][
                        "pass"
                    ]
                )
        with self.assertRaisesRegex(RuntimeError, "exact unique 4 x 3"):
            probe.aggregate_arm_claim_matrices(records[:-1])
        with self.assertRaisesRegex(RuntimeError, "exact unique 4 x 3"):
            probe.aggregate_arm_claim_matrices([*records, dict(records[0])])

        missing_label = json.loads(json.dumps(records))
        missing_label[0]["independent_claim_matrix"].pop(labels[0])
        with self.assertRaisesRegex(RuntimeError, "exact frozen claim labels"):
            probe.aggregate_arm_claim_matrices(missing_label)
        extra_label = json.loads(json.dumps(records))
        extra_label[0]["independent_claim_matrix"]["UNFROZEN_EXTRA_LABEL"] = {
            "pass": True
        }
        with self.assertRaisesRegex(RuntimeError, "exact frozen claim labels"):
            probe.aggregate_arm_claim_matrices(extra_label)
        for invalid in (1, "true", None):
            with self.subTest(non_boolean_pass=invalid):
                non_boolean = json.loads(json.dumps(records))
                non_boolean[0]["independent_claim_matrix"][labels[0]][
                    "pass"
                ] = invalid
                with self.assertRaisesRegex(RuntimeError, "non-boolean pass"):
                    probe.aggregate_arm_claim_matrices(non_boolean)

    def test_whole_state_digests_are_equally_sensitive_and_analysis_is_read_only(self) -> None:
        model = probe.ExactCompiledModel()
        manual = hashlib.sha256()
        for name, tensor in sorted(model.state_dict().items()):
            array = tensor.detach().cpu().contiguous().numpy()
            manual.update(name.encode("utf-8") + b"\0")
            manual.update(str(array.dtype).encode("ascii") + b"\0")
            manual.update(np.asarray(array.shape, dtype=np.int64).tobytes())
            manual.update(array.tobytes())
        independent_before = probe._model_tensor_digest(model)
        sealed_format_before = self.api["state_dict_digest"](model)
        self.assertEqual(independent_before, manual.hexdigest())

        context = probe.make_context_bank(
            self.api["EpisodeGenerator"], seed=99, count=1, split="unit"
        )
        encoded = probe.encode_context_once(model, context.tables[0])
        projector = probe.construct_anchor_projector(model)
        prototypes = self.exact_prototypes(model)
        starts = torch.arange(8, dtype=torch.long)
        phi = torch.from_numpy(context.phi[0]).long()
        probe.periodic_evolve(
            model,
            model.initial_hidden(phi[starts]),
            encoded,
            context.canonical_to_slot[0],
            phi,
            self.maps,
            starts,
            (0, 1, 0, 1),
            condition="oracle_anchor",
            cadence=4,
            projector=projector,
            prototypes=prototypes,
        )
        self.assertEqual(independent_before, probe._model_tensor_digest(model))
        self.assertEqual(sealed_format_before, self.api["state_dict_digest"](model))

        original = model.decoder.weight.detach().clone()
        with torch.no_grad():
            model.decoder.weight[0, 0] += 0.25
        self.assertNotEqual(independent_before, probe._model_tensor_digest(model))
        self.assertNotEqual(sealed_format_before, self.api["state_dict_digest"](model))
        with torch.no_grad():
            model.decoder.weight.copy_(original)
        self.assertEqual(independent_before, probe._model_tensor_digest(model))
        self.assertEqual(sealed_format_before, self.api["state_dict_digest"](model))

        panel_source = inspect.getsource(probe.run_learned_panel)
        before_index = panel_source.index("whole_analysis_independent_digest_before")
        after_index = panel_source.index("whole_analysis_independent_digest_after")
        self.assertLess(before_index, panel_source.index("build_calibration_prototypes"))
        self.assertLess(panel_source.index("evaluate_periodic_model"), after_index)


if __name__ == "__main__":
    unittest.main(verbosity=2)
