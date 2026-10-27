"""Checkpoint-free adversarial tests for the v0.3 execution lifecycle.

Every filesystem mutation is redirected into a temporary directory.  The
suite never opens a learned checkpoint or the sealed production bank; compact
fixtures and mocks are used to drive verifier control flow instead.
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_factorial_probe as probe


def fraction(numerator: int, denominator: int) -> dict[str, int | float | None]:
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


def passing_length() -> dict[str, object]:
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


def verifier_prefix_fixture(
    interventions: tuple[str, ...],
    *,
    task_denominator: int,
) -> dict[str, object]:
    suffix_axis = [{"word": list(word)} for word in probe.words_upto()]

    def generic_condition() -> dict[str, object]:
        return {
            "task_accuracy": fraction(task_denominator, task_denominator),
            "per_length": {
                str(length): {"task_accuracy": fraction(1, 1)}
                for length in range(probe.SUFFIX_MAX_LENGTH + 1)
            },
            "per_suffix": copy.deepcopy(suffix_axis),
        }

    conditions = {name: generic_condition() for name in interventions}
    decoder = conditions["decoder_prototype"]
    decoder["per_length"]["0"] = {"task_accuracy": fraction(1, 1)}
    decoder["per_length"]["5"] = passing_length()
    decoder["per_length"]["6"] = passing_length()
    decoder["conditional_on_selector"] = {
        "task_accuracy_given_selector_correct": fraction(199, 200),
        "per_length": {
            "5": {
                "task_accuracy_given_selector_correct": fraction(199, 200)
            },
            "6": {
                "task_accuracy_given_selector_correct": fraction(199, 200)
            },
        },
    }
    oracle = conditions["oracle_prototype"]
    oracle["per_length"]["5"] = {"task_accuracy": fraction(199, 200)}
    oracle["per_length"]["6"] = {"task_accuracy": fraction(199, 200)}
    conditions["wrong_prototype_control"]["wrong_section_control"] = {
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
        "conditions": conditions,
        "factorial_integrity": {
            "decoder_label_tensor_reused_for_both_sections": True,
            "section_equality": {
                "anchor": {
                    "evaluable": True,
                    "bit_identical_on_correct_selection": True,
                },
                "prototype": {
                    "evaluable": True,
                    "bit_identical_on_correct_selection": True,
                },
            },
        },
    }


class SpendFirewallTests(unittest.TestCase):
    def test_concurrent_spend_attempts_allow_exactly_one_exclusive_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            spend_path = Path(temporary) / "state" / "EVALUATION_BANK_SPENT.json"
            state_directory = spend_path.parent
            armed = {
                "bank_verification": {
                    "bank_id": "bank-id",
                    "bank_sha256": "a" * 64,
                },
                "protocol_sha256": "b" * 64,
                "armed_receipt_sha256": "c" * 64,
            }
            reservation = probe.ResultReservation(
                bundle=Path(temporary) / "results" / "RESULTS.bundle",
                result_path=Path(temporary) / "result.reserved",
                commit_path=Path(temporary) / "commit.reserved",
                result_device=1,
                result_inode=2,
                commit_device=1,
                commit_inode=3,
                free_bytes_before=512,
                hardlink_publication_canary_completed=True,
            )
            readiness = {
                "status": "ALL_CHECKPOINTS_READY_BEFORE_FRESH_BANK_EVALUATION",
                "checkpoint_count": 0,
                "parameter_only": True,
                "fresh_bank_state_applied_to_checkpoint": False,
                "checkpoints": [],
            }
            barrier = threading.Barrier(2)

            def attempt() -> tuple[str, object]:
                barrier.wait(timeout=5)
                try:
                    return "written", probe.spend_fresh_bank(
                        armed,
                        result_reservation=reservation,
                        checkpoint_readiness=readiness,
                    )
                except FileExistsError as error:
                    return "refused", error

            with (
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "STATE_DIRECTORY", state_directory),
                mock.patch.object(probe, "MAX_RESULT_BYTES", 128),
                mock.patch.object(probe, "COMMIT_RESERVATION_BYTES", 64),
            ):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    outcomes = list(executor.map(lambda _: attempt(), range(2)))
                self.assertEqual(
                    sorted(status for status, _ in outcomes),
                    ["refused", "written"],
                )
                self.assertTrue(spend_path.is_file())
                stored = json.loads(spend_path.read_text(encoding="utf-8"))
                self.assertEqual(stored["status"], probe.SPEND_STATUS)
                self.assertEqual(
                    stored["checkpoint_readiness_sha256"],
                    probe.sha256_bytes(probe.canonical_json_bytes(readiness)),
                )
                self.assertFalse(stored["prospective_resume_permitted"])
                with self.assertRaises(FileExistsError):
                    probe.spend_fresh_bank(
                        armed,
                        result_reservation=reservation,
                        checkpoint_readiness=readiness,
                    )


class ImmutableInputTests(unittest.TestCase):
    def test_learned_panel_uses_snapshot_bytes_then_rejects_changed_bank_path(self) -> None:
        original = b'{"sealed":"original"}\n'
        replacement = b'{"sealed":"changed"}\n'
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            bank_path = directory / "FRESH_BANK.json"
            bank_path.write_bytes(original)
            loaded_sources: list[object] = []

            def materialize(source: Path | bytes):
                loaded_sources.append(source)
                bank_path.write_bytes(replacement)
                return (
                    {},
                    {},
                    OrderedDict(),
                    OrderedDict(),
                    {"bank_id": "bank-id"},
                )

            protocol = {
                "claim_boundary": {},
                "implementation_receipts": {},
                "status": probe.FROZEN_STATUS,
                "factorial": {},
            }
            verification = {
                "bank_id": "bank-id",
                "bank_sha256": probe.sha256_bytes(original),
            }
            with (
                mock.patch.object(probe, "EXPECTED_NUMPY_VERSION", np.__version__),
                mock.patch.object(probe, "ARMS", ("polar_cr",)),
                mock.patch.object(probe, "SEEDS", ()),
                mock.patch.object(
                    probe,
                    "load_fresh_bank_arrays",
                    side_effect=materialize,
                ),
                mock.patch.object(
                    probe,
                    "verify_source_metadata",
                    return_value=({}, {}, {}),
                ),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "fresh-bank file changed after the pre-spend snapshot",
                ):
                    probe.run_learned_panel(
                        directory,
                        directory / "sealed.zip",
                        protocol,
                        "d" * 64,
                        bank_path=bank_path,
                        bank_bytes=original,
                        bank_verification=verification,
                        spend_receipt={},
                        pre_spend_source_receipts={},
                        prepared_checkpoints=(),
                        pre_spend_checkpoint_readiness={
                            "status": "ALL_CHECKPOINTS_READY_BEFORE_FRESH_BANK_EVALUATION",
                            "checkpoint_count": 0,
                            "parameter_only": True,
                            "fresh_bank_state_applied_to_checkpoint": False,
                            "checkpoints": [],
                        },
                    )
            self.assertEqual(loaded_sources, [original])
            self.assertIsInstance(loaded_sources[0], bytes)


class ResultVerifierBoundaryTests(unittest.TestCase):
    def test_result_bundle_rejects_symlinked_member_before_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            bundle = directory / "RESULTS.bundle"
            bundle.mkdir()
            target = directory / "outside-result.json"
            target.write_text("{}\n", encoding="utf-8")
            os.symlink(target, bundle / "RESULT.json")
            (bundle / "COMMIT.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-symlink regular file"):
                probe.verify_result_bundle(
                    bundle,
                    root=directory,
                    archive=directory / "sealed.zip",
                )

    def test_recursive_exact_fraction_tamper_is_rejected(self) -> None:
        result = {
            "outer": [
                {
                    "middle": {
                        "inner": fraction(7, 10),
                    }
                }
            ]
        }
        self.assertEqual(probe.validate_fraction_records(result), 1)
        tampered = copy.deepcopy(result)
        tampered["outer"][0]["middle"]["inner"]["value"] = 0.8
        with self.assertRaisesRegex(ValueError, "fraction value mismatch"):
            probe.validate_fraction_records(tampered)

    def test_verifier_recomputes_gate_and_rejects_stale_stored_pass(self) -> None:
        interventions = (
            "native",
            "decoder_prototype",
            "oracle_prototype",
            "wrong_prototype_control",
        )
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            prospective = directory / "prospective"
            state = prospective / "state"
            bundle = prospective / "results" / "RESULTS.bundle"
            root = directory / "source"
            checkpoint = (
                root
                / "results"
                / "packet_closure_pilot"
                / "checkpoint.bin"
            )
            for path in (state, bundle, checkpoint.parent):
                path.mkdir(parents=True, exist_ok=True)

            protocol_path = prospective / "PROTOCOL.json"
            protocol_bytes = probe.canonical_json_bytes({"frozen": True})
            protocol_path.write_bytes(protocol_bytes)
            protocol_sha256 = probe.sha256_bytes(protocol_bytes)
            freeze_path = prospective / "FROZEN_PROTOCOL.sha256"
            freeze_path.write_text(f"{protocol_sha256}  PROTOCOL.json\n")
            preflight_path = prospective / "PREFLIGHT.json"
            preflight_path.write_bytes(probe.canonical_json_bytes({"pass": True}))
            synthetic_tests_path = prospective / "SYNTHETIC_TESTS.json"
            synthetic_tests_path.write_bytes(
                probe.canonical_json_bytes({"status": "PASS"})
            )

            bank_id = "test-bank"
            bank_bytes = probe.canonical_json_bytes({"bank_id": bank_id})
            (prospective / "FRESH_BANK.json").write_bytes(bank_bytes)
            bank_sha256 = probe.sha256_bytes(bank_bytes)
            checkpoint.write_bytes(b"synthetic checkpoint receipt only\n")
            checkpoint_sha256 = probe.sha256_file(checkpoint)
            checkpoint_receipt = {
                "path": "checkpoint.bin",
                "sha256": checkpoint_sha256,
                "state_dict_digest": "2" * 64,
            }
            readiness = {
                "status": "ALL_CHECKPOINTS_READY_BEFORE_FRESH_BANK_EVALUATION",
                "checkpoint_count": 1,
                "parameter_only": True,
                "fresh_bank_state_applied_to_checkpoint": False,
                "checkpoints": [
                    {
                        "arm": "polar_cr",
                        "seed": 101,
                        "path": checkpoint.as_posix(),
                        "sha256": checkpoint_sha256,
                        "state_dict_digest": checkpoint_receipt[
                            "state_dict_digest"
                        ],
                        "restricted_parameter_load_pass": True,
                    }
                ],
            }
            armed_path = prospective / "ARMED_RECEIPT.json"
            armed = {
                "status": "ARMED_PROSPECTIVE_EVALUATION_UNSPENT",
                "bank_id": bank_id,
                "bank_sha256": bank_sha256,
                "protocol_sha256": protocol_sha256,
            }
            armed_bytes = probe.canonical_json_bytes(armed)
            armed_path.write_bytes(armed_bytes)
            armed_sha256 = probe.sha256_bytes(armed_bytes)
            armed_hash_path = prospective / "ARMED_RECEIPT.sha256"
            armed_hash_path.write_text(f"{armed_sha256}  ARMED_RECEIPT.json\n")

            spend_path = state / "EVALUATION_BANK_SPENT.json"
            spend_document = {
                "status": probe.SPEND_STATUS,
                "bank_id": bank_id,
                "bank_sha256": bank_sha256,
                "protocol_sha256": protocol_sha256,
                "armed_receipt_sha256": armed_sha256,
                "runtime_numpy_version": probe.EXPECTED_NUMPY_VERSION,
                "checkpoint_readiness_sha256": probe.sha256_bytes(
                    probe.canonical_json_bytes(readiness)
                ),
                "result_capacity": {
                    "bundle": bundle.absolute().as_posix(),
                    "result_bytes_physically_reserved": probe.MAX_RESULT_BYTES,
                    "commit_bytes_physically_reserved": probe.COMMIT_RESERVATION_BYTES,
                    "free_bytes_before_reservation": probe.MIN_FREE_BYTES_BEFORE_SPEND,
                    "posix_fallocate_completed": True,
                    "same_directory_hardlink_publication_canary_completed": True,
                },
                "prospective_resume_permitted": False,
            }
            spend_bytes = probe.canonical_json_bytes(spend_document)
            spend_path.write_bytes(spend_bytes)
            spend_receipt = {
                **spend_document,
                "receipt_sha256": probe.sha256_bytes(spend_bytes),
            }

            task_denominator = (
                len(probe.words_upto())
                * probe.EVALUATION_CONTEXTS
                * probe.N_STATES
            )
            prefix = verifier_prefix_fixture(
                interventions,
                task_denominator=task_denominator,
            )
            passing_gate = probe.checkpoint_primary_gate(
                {"evaluation_00": prefix},
                passing_section_audit(),
            )
            self.assertTrue(passing_gate["pass"])

            # Change a metric after the stored pass was computed.  Hashes and
            # aggregate booleans are then rebuilt around the stale gate, so
            # only independent gate recomputation can detect the substitution.
            prefix["selector_diagnostics"]["decoder"] = fraction(0, 100)
            checkpoint_row = {
                "arm": "polar_cr",
                "seed": 101,
                "checkpoint": {
                    "path": checkpoint.as_posix(),
                    "observed_sha256": checkpoint_sha256,
                    "expected_sha256": checkpoint_sha256,
                    "state_dict_digest": checkpoint_receipt["state_dict_digest"],
                },
                "prefixes": {"evaluation_00": prefix},
                "section_audits": {"prototype": passing_section_audit()},
                "primary_gate": passing_gate,
            }
            source_summary = {"synthetic_source_receipts": True}
            result = {
                "schema": probe.RESULT_SCHEMA,
                "version": probe.VERSION,
                "protocol": {
                    "sha256": protocol_sha256,
                    "status": probe.FROZEN_STATUS,
                },
                "claim_boundary": probe.CLAIM_BOUNDARY_CONTRACT,
                "fresh_bank": {
                    "bank_id": bank_id,
                    "bank_sha256": bank_sha256,
                    "evaluated_from_pre_spend_immutable_byte_snapshot": True,
                },
                "spend_receipt": spend_receipt,
                "source_receipts": source_summary,
                "pre_spend_checkpoint_readiness": readiness,
                "checkpoint_count": 1,
                "checkpoints": [checkpoint_row],
                "labels": {
                    "arms": {"polar_cr": {"pass": True}},
                    "primary_arm_pass": True,
                    "full_fixed_checkpoint_cohort_pass": True,
                },
                "input_immutability": {
                    "fresh_bank_bytes_unchanged": True,
                    "fresh_bank_sha256_before": bank_sha256,
                    "fresh_bank_sha256_after": bank_sha256,
                    "all_checkpoint_hashes_unchanged": True,
                },
            }
            clean_correct = np.ones(
                (
                    len(probe.words_upto()),
                    probe.EVALUATION_CONTEXTS,
                    probe.N_STATES,
                ),
                dtype=bool,
            )
            checkpoint_row["clean_semantic_endpoint"] = {
                "correct_evidence": probe.packed_bool_evidence(clean_correct),
            }
            with (
                mock.patch.object(probe, "ARMS", ("polar_cr",)),
                mock.patch.object(probe, "SEEDS", (101,)),
                mock.patch.object(probe, "EVALUATION_PREFIXES", 1),
                mock.patch.object(probe, "INTERVENTIONS", interventions),
            ):
                result["design"] = {
                    "arms": list(probe.ARMS),
                    "seeds": list(probe.SEEDS),
                    "interventions": list(probe.INTERVENTIONS),
                    "suffixes": [list(word) for word in probe.words_upto()],
                    "primary_gate_contract": probe.PRIMARY_GATE_CONTRACT,
                    "work_bound": probe.expected_work_counts(),
                    "calibration_contexts": probe.CALIBRATION_CONTEXTS,
                    "evaluation_contexts": probe.EVALUATION_CONTEXTS,
                    "calibration_prefixes": {},
                    "evaluation_prefixes": {
                        "evaluation_00": [0] * probe.PREFIX_LENGTH
                    },
                }
            result_bytes = probe.canonical_json_bytes(result)
            (bundle / "RESULT.json").write_bytes(result_bytes)
            commit = {
                "schema": "komorebi.neuralese.semantic_retraction.result_commit.v1",
                "version": probe.VERSION,
                "status": "VERIFIED_RESULT_COMMITTED",
                "bank_id": bank_id,
                "spend_receipt_sha256": spend_receipt["receipt_sha256"],
                "result_filename": "RESULT.json",
                "result_bytes": len(result_bytes),
                "result_sha256": probe.sha256_bytes(result_bytes),
                "commit_written_last": True,
            }
            (bundle / "COMMIT.json").write_bytes(probe.canonical_json_bytes(commit))
            archive = directory / "sealed.zip"
            archive.write_bytes(b"synthetic sealed source receipt only\n")
            calibration_bank_for_verification = {
                "maps": np.empty((probe.CALIBRATION_CONTEXTS, 0), dtype=np.int64)
            }
            evaluation_bank_for_verification = {
                "maps": np.empty((probe.EVALUATION_CONTEXTS, 0), dtype=np.int64)
            }
            calibration_words_for_verification: OrderedDict[
                str, tuple[int, ...]
            ] = OrderedDict()
            evaluation_words_for_verification: OrderedDict[
                str, tuple[int, ...]
            ] = OrderedDict(
                [("evaluation_00", (0,) * probe.PREFIX_LENGTH)]
            )

            with ExitStack() as stack:
                simple_patches = {
                    "HERE": prospective,
                    "PROTOCOL_PATH": protocol_path,
                    "FREEZE_RECEIPT_PATH": freeze_path,
                    "PREFLIGHT_PATH": preflight_path,
                    "SYNTHETIC_TESTS_PATH": synthetic_tests_path,
                    "SPEND_PATH": spend_path,
                    "ARMED_RECEIPT_PATH": armed_path,
                    "ARMED_RECEIPT_HASH_PATH": armed_hash_path,
                    "ARMS": ("polar_cr",),
                    "SEEDS": (101,),
                    "EVALUATION_PREFIXES": 1,
                    "INTERVENTIONS": interventions,
                }
                for name, value in simple_patches.items():
                    stack.enter_context(mock.patch.object(probe, name, value))
                stack.enter_context(mock.patch.object(probe, "validate_protocol_design"))
                stack.enter_context(mock.patch.object(probe, "_require_equal_record"))
                stack.enter_context(mock.patch.object(probe, "verify_section_evidence"))
                stack.enter_context(
                    mock.patch.object(
                        probe,
                        "verify_condition_evidence",
                        return_value=clean_correct,
                    )
                )
                stack.enter_context(mock.patch.object(probe, "verify_selector_evidence"))
                stack.enter_context(
                    mock.patch.object(
                        probe,
                        "load_fresh_bank_arrays",
                        return_value=(
                            calibration_bank_for_verification,
                            evaluation_bank_for_verification,
                            calibration_words_for_verification,
                            evaluation_words_for_verification,
                            {"bank_id": bank_id},
                        ),
                    )
                )
                stack.enter_context(
                    mock.patch.object(
                        probe,
                        "expected_armed_receipt",
                        return_value=armed,
                    )
                )
                stack.enter_context(
                    mock.patch.object(
                        probe,
                        "verify_source_metadata",
                        return_value=(
                            {},
                            {("polar_cr", 101): checkpoint_receipt},
                            source_summary,
                        ),
                    )
                )
                stack.enter_context(
                    mock.patch(
                        "fresh_bank.verify_fresh_bank",
                        return_value={
                            "bank_id": bank_id,
                            "bank_sha256": bank_sha256,
                        },
                    )
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "checkpoint primary gate does not recompute from metrics",
                ):
                    probe.verify_result_bundle(
                        bundle,
                        root=root,
                        archive=archive,
                    )


class CapacityAndCommitBoundaryTests(unittest.TestCase):
    def test_spend_publication_error_preserves_capacity_when_marker_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            spend_path = directory / "state" / "EVALUATION_BANK_SPENT.json"
            spend_path.parent.mkdir()
            spend_path.write_bytes(b"partial")
            reservation = probe.ResultReservation(
                bundle=directory / "bundle",
                result_path=directory / "result.reserved",
                commit_path=directory / "commit.reserved",
                result_device=1,
                result_inode=2,
                commit_device=1,
                commit_inode=3,
                free_bytes_before=1024,
                hardlink_publication_canary_completed=True,
            )
            armed = {
                "bank_verification": {
                    "bank_id": "bank",
                    "bank_sha256": "a" * 64,
                }
            }
            error = OSError("synthetic spend fsync failure")
            with (
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "release_unspent_result_reservation") as release,
                mock.patch.object(probe, "write_spend_publication_failure") as failure,
            ):
                probe.handle_spend_publication_error(error, armed, reservation)
            release.assert_not_called()
            failure.assert_called_once_with(error, armed)

    def test_spend_publication_error_releases_capacity_without_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            spend_path = directory / "state" / "EVALUATION_BANK_SPENT.json"
            reservation = probe.ResultReservation(
                bundle=directory / "bundle",
                result_path=directory / "result.reserved",
                commit_path=directory / "commit.reserved",
                result_device=1,
                result_inode=2,
                commit_device=1,
                commit_inode=3,
                free_bytes_before=1024,
                hardlink_publication_canary_completed=True,
            )
            error = OSError("synthetic pre-create spend failure")
            with (
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "release_unspent_result_reservation") as release,
                mock.patch.object(probe, "write_spend_publication_failure") as failure,
            ):
                probe.handle_spend_publication_error(error, {}, reservation)
            release.assert_called_once_with(reservation)
            failure.assert_not_called()

    def test_low_space_refuses_reservation_before_any_spend(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            results = directory / "results"
            bundle = results / "RESULTS.bundle"
            spend_path = directory / "state" / "EVALUATION_BANK_SPENT.json"
            with (
                mock.patch.object(probe, "RESULTS_DIRECTORY", results),
                mock.patch.object(probe, "DEFAULT_BUNDLE", bundle),
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "MIN_FREE_BYTES_BEFORE_SPEND", 64),
                mock.patch.object(
                    probe.shutil,
                    "disk_usage",
                    return_value=mock.Mock(free=63),
                ),
                mock.patch.object(
                    probe,
                    "_allocate_regular_file",
                ) as allocate,
            ):
                with self.assertRaisesRegex(OSError, "insufficient free space"):
                    probe.reserve_result_bundle()
            allocate.assert_not_called()
            self.assertFalse(os.path.lexists(bundle))
            self.assertFalse(os.path.lexists(spend_path))

    def test_fallocate_failure_cleans_bundle_and_precedes_spend(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            results = directory / "results"
            bundle = results / "RESULTS.bundle"
            spend_path = directory / "state" / "EVALUATION_BANK_SPENT.json"
            with (
                mock.patch.object(probe, "RESULTS_DIRECTORY", results),
                mock.patch.object(probe, "DEFAULT_BUNDLE", bundle),
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "MAX_RESULT_BYTES", 128),
                mock.patch.object(probe, "COMMIT_RESERVATION_BYTES", 64),
                mock.patch.object(probe, "MIN_FREE_BYTES_BEFORE_SPEND", 0),
                mock.patch.object(
                    probe.shutil,
                    "disk_usage",
                    return_value=mock.Mock(free=1024),
                ),
                mock.patch.object(
                    probe.os,
                    "posix_fallocate",
                    side_effect=OSError("synthetic allocation failure"),
                    create=True,
                ),
            ):
                with self.assertRaisesRegex(OSError, "synthetic allocation failure"):
                    probe.reserve_result_bundle()
            self.assertFalse(os.path.lexists(bundle))
            self.assertFalse(os.path.lexists(spend_path))

    def test_hardlink_canary_failure_cleans_allocations_before_spend(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            results = directory / "results"
            bundle = results / "RESULTS.bundle"
            spend_path = directory / "state" / "EVALUATION_BANK_SPENT.json"

            def tiny_fallocate(descriptor: int, offset: int, size: int) -> None:
                self.assertEqual(offset, 0)
                os.ftruncate(descriptor, size)

            with (
                mock.patch.object(probe, "RESULTS_DIRECTORY", results),
                mock.patch.object(probe, "DEFAULT_BUNDLE", bundle),
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "MAX_RESULT_BYTES", 128),
                mock.patch.object(probe, "COMMIT_RESERVATION_BYTES", 64),
                mock.patch.object(probe, "MIN_FREE_BYTES_BEFORE_SPEND", 0),
                mock.patch.object(
                    probe.shutil,
                    "disk_usage",
                    return_value=mock.Mock(free=1024),
                ),
                mock.patch.object(
                    probe.os,
                    "link",
                    side_effect=OSError("synthetic hard-link failure"),
                ),
                mock.patch.object(
                    probe.os,
                    "posix_fallocate",
                    side_effect=tiny_fallocate,
                    create=True,
                ),
            ):
                with self.assertRaisesRegex(OSError, "synthetic hard-link failure"):
                    probe.reserve_result_bundle()
            self.assertFalse(os.path.lexists(bundle))
            self.assertFalse(os.path.lexists(spend_path))

    def test_staged_verification_failure_withholds_commit_and_allows_abort(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            results = directory / "results"
            bundle = results / "RESULTS.bundle"
            state = directory / "state"
            state.mkdir()

            def tiny_fallocate(descriptor: int, offset: int, size: int) -> None:
                self.assertEqual(offset, 0)
                os.ftruncate(descriptor, size)

            with (
                mock.patch.object(probe, "RESULTS_DIRECTORY", results),
                mock.patch.object(probe, "DEFAULT_BUNDLE", bundle),
                mock.patch.object(probe, "STATE_DIRECTORY", state),
                mock.patch.object(probe, "MAX_RESULT_BYTES", 4096),
                mock.patch.object(probe, "COMMIT_RESERVATION_BYTES", 2048),
                mock.patch.object(probe, "MIN_FREE_BYTES_BEFORE_SPEND", 0),
                mock.patch.object(
                    probe.shutil,
                    "disk_usage",
                    return_value=mock.Mock(free=8192),
                ),
                mock.patch.object(
                    probe.os,
                    "posix_fallocate",
                    side_effect=tiny_fallocate,
                    create=True,
                ),
            ):
                reservation = probe.reserve_result_bundle()
                self.assertTrue(
                    reservation.hardlink_publication_canary_completed
                )
                self.assertFalse(
                    os.path.lexists(bundle / probe.HARDLINK_CANARY_NAME)
                )
                result_metadata = reservation.result_path.lstat()
                self.assertEqual(
                    (int(result_metadata.st_dev), int(result_metadata.st_ino)),
                    (reservation.result_device, reservation.result_inode),
                )
                with mock.patch.object(
                    probe,
                    "verify_result_bundle",
                    side_effect=ValueError("synthetic staged verification failure"),
                ) as staged_verifier:
                    with self.assertRaisesRegex(
                        ValueError,
                        "synthetic staged verification failure",
                    ):
                        probe.commit_result_bundle(
                            {},
                            reservation,
                            root=directory,
                            archive=directory / "sealed.zip",
                        )
                staged_verifier.assert_called_once_with(
                    reservation.bundle,
                    root=directory,
                    archive=directory / "sealed.zip",
                    require_commit=False,
                )
                self.assertTrue((bundle / "RESULT.json").is_file())
                self.assertTrue((bundle / probe.COMMIT_RESERVATION_NAME).is_file())
                self.assertFalse(os.path.lexists(bundle / probe.RESULT_COMMIT_NAME))

                spend = {"bank_id": "bank", "receipt_sha256": "a" * 64}
                probe.write_abort_receipt(
                    ValueError("synthetic staged verification failure"),
                    spend,
                )
                abort = state / "ABORTED_SPENT.json"
                self.assertTrue(abort.is_file())
                self.assertEqual(
                    json.loads(abort.read_text(encoding="utf-8"))["status"],
                    "ABORTED_SPENT_NO_PROSPECTIVE_RESUME",
                )

    def test_abort_receipt_is_refused_after_terminal_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            bundle = directory / "results" / "RESULTS.bundle"
            state = directory / "state"
            bundle.mkdir(parents=True)
            state.mkdir()
            (bundle / probe.RESULT_COMMIT_NAME).write_bytes(b"terminal\n")
            with (
                mock.patch.object(probe, "DEFAULT_BUNDLE", bundle),
                mock.patch.object(probe, "STATE_DIRECTORY", state),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "refusing to write an abort receipt after terminal commit",
                ):
                    probe.write_abort_receipt(
                        RuntimeError("too late"),
                        {"bank_id": "bank", "receipt_sha256": "a" * 64},
                    )
            self.assertFalse((state / "ABORTED_SPENT.json").exists())


class ArmedReceiptTests(unittest.TestCase):
    def test_canonical_armed_receipt_passes_and_pretty_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            prospective = directory / "prospective"
            preflight_directory = directory / "preflight"
            prospective.mkdir()
            preflight_directory.mkdir()
            protocol_path = prospective / "PROTOCOL.json"
            freeze_path = prospective / "FROZEN_PROTOCOL.sha256"
            preflight_path = preflight_directory / "PREFLIGHT.json"
            synthetic_path = preflight_directory / "SYNTHETIC_TESTS.json"
            armed_path = prospective / "ARMED_RECEIPT.json"
            armed_hash_path = prospective / "ARMED_RECEIPT.sha256"
            spend_path = prospective / "state" / "EVALUATION_BANK_SPENT.json"
            bundle = prospective / "results" / "RESULTS.bundle"

            protocol_path.write_bytes(probe.canonical_json_bytes({"frozen": True}))
            freeze_path.write_text("frozen receipt\n", encoding="utf-8")
            preflight = {
                "schema": "komorebi.neuralese.semantic_retraction.parameter_preflight.v1",
                "version": probe.VERSION,
                "status": "PASS",
                "preflight_integrity_pass": True,
                "projection_diagnostic_is_nonblocking_for_core_factorial": True,
                "evaluation_bank_generated_or_opened": False,
            }
            preflight_path.write_bytes(probe.canonical_json_bytes(preflight))
            synthetic_path.write_bytes(
                probe.canonical_json_bytes({"status": "PASS"})
            )
            (prospective / "DESIGN_COMMIT.json").write_bytes(
                probe.canonical_json_bytes({"status": "FROZEN"})
            )
            bank_bytes = probe.canonical_json_bytes({"bank_id": "bank-id"})
            (prospective / "FRESH_BANK.json").write_bytes(bank_bytes)
            bank_verification = {
                "bank_id": "bank-id",
                "bank_sha256": probe.sha256_bytes(bank_bytes),
                "seal_receipt_sha256": "s" * 64,
            }
            protocol_sha256 = "p" * 64
            protocol = {
                "preflight": {"sha256": probe.sha256_file(preflight_path)}
            }

            with (
                mock.patch.object(probe, "HERE", prospective),
                mock.patch.object(probe, "PROTOCOL_PATH", protocol_path),
                mock.patch.object(probe, "FREEZE_RECEIPT_PATH", freeze_path),
                mock.patch.object(probe, "PREFLIGHT_PATH", preflight_path),
                mock.patch.object(probe, "SYNTHETIC_TESTS_PATH", synthetic_path),
                mock.patch.object(probe, "ARMED_RECEIPT_PATH", armed_path),
                mock.patch.object(
                    probe,
                    "ARMED_RECEIPT_HASH_PATH",
                    armed_hash_path,
                ),
                mock.patch.object(probe, "SPEND_PATH", spend_path),
                mock.patch.object(probe, "DEFAULT_BUNDLE", bundle),
                mock.patch.object(probe, "verify_runtime_contract"),
                mock.patch.object(
                    probe,
                    "load_fresh_bank_arrays",
                    return_value=(
                        {},
                        {},
                        OrderedDict(),
                        OrderedDict(),
                        {"bank_id": "bank-id"},
                    ),
                ),
                mock.patch.object(
                    probe,
                    "assert_learned_execution_unlocked",
                    return_value=(protocol, protocol_sha256),
                ),
                mock.patch(
                    "fresh_bank.verify_fresh_bank",
                    return_value=bank_verification,
                ),
            ):
                expected = probe.expected_armed_receipt(
                    protocol_sha256=protocol_sha256,
                    preflight_sha256=probe.sha256_file(preflight_path),
                    bank_verification=bank_verification,
                )
                canonical = probe.canonical_json_bytes(expected)
                armed_path.write_bytes(canonical)
                armed_hash_path.write_text(
                    f"{probe.sha256_bytes(canonical)}  ARMED_RECEIPT.json\n",
                    encoding="utf-8",
                )
                observed = probe.verify_execution_armed()
                self.assertEqual(observed["armed_receipt"], expected)

                pretty = (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode(
                    "utf-8"
                )
                armed_path.write_bytes(pretty)
                armed_hash_path.write_text(
                    f"{probe.sha256_bytes(pretty)}  ARMED_RECEIPT.json\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(RuntimeError, "not canonical JSON"):
                    probe.verify_execution_armed()


class MainOrderingTests(unittest.TestCase):
    def test_main_prepares_and_reserves_before_spend_then_commits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            protocol_path = directory / "PROTOCOL.json"
            protocol_path.write_bytes(probe.canonical_json_bytes({"frozen": True}))
            root = directory / "source"
            archive = directory / "sealed.zip"
            root.mkdir()
            archive.write_bytes(b"sealed fixture\n")
            args = argparse.Namespace(
                preflight=False,
                status=False,
                verify_result=False,
                validate_only=False,
                run_learned=True,
                root=root,
                archive=archive,
            )
            events: list[str] = []
            armed = {
                "protocol": {"frozen": True},
                "protocol_sha256": "a" * 64,
                "bank_bytes": b"snapshot",
                "bank_verification": {"bank_id": "bank"},
            }
            spend = {"bank_id": "bank", "receipt_sha256": "b" * 64}
            prepared = ()
            readiness = {
                "status": "ALL_CHECKPOINTS_READY_BEFORE_FRESH_BANK_EVALUATION",
                "checkpoint_count": 0,
                "parameter_only": True,
                "fresh_bank_state_applied_to_checkpoint": False,
                "checkpoints": [],
            }
            reservation = probe.ResultReservation(
                bundle=directory / "results" / "RESULTS.bundle",
                result_path=directory / "result.reserved",
                commit_path=directory / "commit.reserved",
                result_device=1,
                result_inode=2,
                commit_device=1,
                commit_inode=3,
                free_bytes_before=1024,
                hardlink_publication_canary_completed=True,
            )
            result = {
                "checkpoint_count": 0,
                "labels": {"primary_arm_pass": False},
                "runtime": {"elapsed_seconds": 0.0},
            }

            def record(name: str, returned: object):
                def call(*args: object, **kwargs: object) -> object:
                    del args, kwargs
                    events.append(name)
                    return returned

                return call

            with (
                mock.patch.object(probe, "PROTOCOL_PATH", protocol_path),
                mock.patch.object(probe, "parse_args", return_value=args),
                mock.patch.object(
                    probe,
                    "validate_protocol_design",
                    return_value={},
                ),
                mock.patch.object(
                    probe,
                    "verify_runtime_contract",
                    side_effect=record("runtime", {"match": True}),
                ),
                mock.patch.object(
                    probe,
                    "verify_execution_armed",
                    side_effect=record("armed", armed),
                ),
                mock.patch.object(
                    probe,
                    "spend_fresh_bank",
                    side_effect=record("spend", spend),
                ),
                mock.patch.object(
                    probe,
                    "verify_source_metadata",
                    side_effect=record("source", ({}, {}, {})),
                ),
                mock.patch.object(
                    probe,
                    "prepare_checkpoint_panel",
                    side_effect=record("prepare", (prepared, readiness)),
                ),
                mock.patch.object(
                    probe,
                    "reserve_result_bundle",
                    side_effect=record("reserve", reservation),
                ),
                mock.patch.object(
                    probe,
                    "run_learned_panel",
                    side_effect=record("panel", result),
                ),
                mock.patch.object(
                    probe,
                    "commit_result_bundle",
                    side_effect=record(
                        "commit",
                        {
                            "commit_sha256": "c" * 64,
                            "precommit_verification": {
                                "status": "VERIFIED_STAGED_RESULT"
                            },
                        },
                    ),
                ),
                mock.patch.object(
                    probe,
                    "verify_result_bundle",
                ) as postcommit_verifier,
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(probe.main(), 0)
            postcommit_verifier.assert_not_called()
            self.assertEqual(
                events,
                [
                    "runtime",
                    "armed",
                    "source",
                    "prepare",
                    "reserve",
                    "spend",
                    "panel",
                    "commit",
                ],
            )


if __name__ == "__main__":
    unittest.main()
