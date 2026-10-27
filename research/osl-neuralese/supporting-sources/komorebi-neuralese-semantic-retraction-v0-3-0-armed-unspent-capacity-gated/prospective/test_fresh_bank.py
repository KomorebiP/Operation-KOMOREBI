from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fresh_bank as bank


FIXED_ROOT = bytes(range(32))


def empty_registry(parent_sha256: str = "0" * 64) -> dict[str, object]:
    return {
        "schema": bank.REGISTRY_SCHEMA,
        "version": bank.VERSION,
        "status": bank.REGISTRY_STATUS,
        "author": bank.AUTHOR,
        "context_key_definition": bank.REGISTRY_CONTEXT_KEY_DEFINITION,
        "path_word_sha256_definition": bank.REGISTRY_PATH_HASH_DEFINITION,
        "counts": {"unique_context_keys": 0, "unique_path_words": 0},
        "forbidden_context_keys": [],
        "forbidden_path_word_sha256": [],
        "parent_release": {"sha256": parent_sha256},
    }


def write_canonical(path: Path, value: object) -> None:
    path.write_bytes(bank.canonical_json_bytes(value))


def make_frozen_project(root: Path, *, pretty_registry: bool = False) -> dict[str, Path]:
    prospective = root / "prospective"
    artifacts = {
        field: root.joinpath(*parts) for field, parts in bank.DESIGN_FILE_MAP.items()
    }
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    reserved_documents = {
        "protocol_sha256",
        "frozen_protocol_receipt_sha256",
        "parameter_preflight_sha256",
        "synthetic_tests_sha256",
        "spent_bank_registry_sha256",
    }
    for index, (field, path) in enumerate(artifacts.items()):
        if field in reserved_documents:
            continue
        if field == "fresh_bank_implementation_sha256":
            path.write_bytes(Path(bank.__file__).read_bytes())
        elif field == "fresh_bank_test_sha256":
            path.write_bytes(Path(__file__).read_bytes())
        else:
            path.write_bytes(f"frozen unit artifact {index} {field}\n".encode("utf-8"))

    registry_path = artifacts["spent_bank_registry_sha256"]
    registry = empty_registry(bank.sha256_file(artifacts["parent_release_sha256"]))
    if pretty_registry:
        registry_path.write_text(
            json.dumps(registry, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        write_canonical(registry_path, registry)

    write_canonical(
        artifacts["parameter_preflight_sha256"],
        {
            "schema": "komorebi.neuralese.semantic_retraction.parameter_preflight.v1",
            "version": bank.VERSION,
            "status": "PASS",
            "preflight_integrity_pass": True,
            "projection_diagnostic_is_nonblocking_for_core_factorial": True,
            "evaluation_bank_generated_or_opened": False,
            "behavioral_rollout_generated": False,
            "prior_v0.4_evaluation_bank_opened": False,
            "runner_sha256": bank.sha256_file(artifacts["factorial_runner_sha256"]),
        },
    )
    synthetic_receipts = {
        field: bank.sha256_file(artifacts[field])
        for field in bank.SYNTHETIC_IMPLEMENTATION_FIELDS
    }
    write_canonical(
        artifacts["synthetic_tests_sha256"],
        {
            "schema": "komorebi.neuralese.semantic_retraction.synthetic_tests.v1",
            "version": bank.VERSION,
            "status": "PASS",
            "learned_checkpoint_opened": False,
            "production_bank_generated_or_opened": False,
            "checkpoint_free_unit_tests": {"status": "PASS"},
            "full_shape_synthetic_checkpoint": {
                "status": "PASS",
                "packed_evidence_recomputation": "PASS",
                "learned_checkpoint_opened": False,
                "production_entropy_used": False,
            },
            "implementation_receipts": synthetic_receipts,
        },
    )

    protocol_receipts = {
        field: bank.sha256_file(artifacts[field])
        for field in bank.PROTOCOL_IMPLEMENTATION_FIELDS
    }
    write_canonical(
        artifacts["protocol_sha256"],
        {
            "schema": bank.PROTOCOL_SCHEMA,
            "version": bank.VERSION,
            "status": bank.PROTOCOL_STATUS,
            "author": bank.AUTHOR,
            "runtime_contract": {"numpy_version": bank.NUMPY_VERSION},
            "fresh_bank_design": {
                "calibration_contexts": bank.CONTEXTS_PER_SPLIT,
                "evaluation_contexts": bank.CONTEXTS_PER_SPLIT,
                "calibration_prefixes": bank.PATHS_PER_SPLIT,
                "evaluation_prefixes": bank.PATHS_PER_SPLIT,
                "prefix_length": bank.PRIMARY_PATH_DEPTH,
                "entropy_available_before_design_commit": False,
                "calibration_evaluation_disjoint": True,
                "prior_bank_exclusion_required": True,
            },
            "implementation_receipts": protocol_receipts,
            "preflight": {
                "sha256": bank.sha256_file(artifacts["parameter_preflight_sha256"]),
                "evaluation_bank_generated_or_opened": False,
            },
            "synthetic_tests": {
                "sha256": bank.sha256_file(artifacts["synthetic_tests_sha256"]),
            },
            "scientific_boundaries": {
                "sha256": bank.sha256_file(artifacts["scientific_boundaries_sha256"]),
            },
            "lineage": {
                "parent_release_sha256": bank.sha256_file(
                    artifacts["parent_release_sha256"]
                ),
            },
        },
    )
    artifacts["frozen_protocol_receipt_sha256"].write_text(
        f"{bank.sha256_file(artifacts['protocol_sha256'])}  PROTOCOL.json\n",
        encoding="utf-8",
    )
    design = {
        "schema": bank.DESIGN_SCHEMA,
        "version": bank.VERSION,
        "status": bank.DESIGN_STATUS,
        "production_entropy_present": False,
        "numpy_version": bank.NUMPY_VERSION,
        **{field: bank.sha256_file(path) for field, path in artifacts.items()},
    }
    design_path = prospective / "DESIGN_COMMIT.json"
    write_canonical(design_path, design)
    return {
        "root": root,
        "design": design_path,
        "registry": registry_path,
        "bank": prospective / "FRESH_BANK.json",
        "draw": prospective / "FRESH_BANK_DRAW_RECEIPT.json",
        "seal": prospective / "FRESH_BANK_SEAL.json",
    }


class StaticIsolationTests(unittest.TestCase):
    def test_source_does_not_import_torch_or_checkpoint_modules(self) -> None:
        source = Path(bank.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertNotIn("torch", imported)
        self.assertNotIn("pickle", imported)
        self.assertNotIn("zipfile", imported)

    def test_constants_freeze_exact_bank_dimensions(self) -> None:
        self.assertEqual(bank.CONTEXTS_PER_SPLIT, 64)
        self.assertEqual(bank.PATHS_PER_SPLIT, 8)
        self.assertGreaterEqual(bank.PATHS_PER_SPLIT, 6)
        self.assertEqual(bank.PRIMARY_PATH_DEPTH, 64)


class KdfAndAlgebraTests(unittest.TestCase):
    def test_canonical_json_has_independent_exact_byte_vector(self) -> None:
        self.assertEqual(
            bank.canonical_json_bytes({"b": [2, 1], "a": "x"}),
            b'{"a":"x","b":[2,1]}\n',
        )

    def test_kdf_is_deterministic_domain_separated_and_fixed(self) -> None:
        observed = bank.hkdf_sha256(FIXED_ROOT, "context/calibration")
        self.assertEqual(
            observed.hex(),
            "c3bf5443e15bc69c48bfa64acca9e2d3f602d74517d3ac3bb8982e39807946ba",
        )
        self.assertEqual(observed, bank.hkdf_sha256(FIXED_ROOT, "context/calibration"))
        self.assertNotEqual(observed, bank.hkdf_sha256(FIXED_ROOT, "context/evaluation"))
        self.assertNotEqual(observed, bank.hkdf_sha256(FIXED_ROOT, "path/calibration"))

    def test_kdf_rejects_bad_root_domain_and_length(self) -> None:
        with self.assertRaises(ValueError):
            bank.hkdf_sha256(b"short", "context/calibration")
        with self.assertRaises(ValueError):
            bank.hkdf_sha256(FIXED_ROOT, "")
        with self.assertRaises(ValueError):
            bank.hkdf_sha256(FIXED_ROOT, "bad\x00domain")
        with self.assertRaises(ValueError):
            bank.hkdf_sha256(FIXED_ROOT, "valid", 0)

    def test_d4_generators_and_relations(self) -> None:
        maps = bank.canonical_d4_maps()
        self.assertEqual(maps.shape, (2, 8))
        np.testing.assert_array_equal(maps[0], np.array([1, 2, 3, 0, 5, 6, 7, 4]))
        np.testing.assert_array_equal(maps[1], np.array([4, 7, 6, 5, 0, 3, 2, 1]))
        for mapping in maps:
            np.testing.assert_array_equal(np.sort(mapping), np.arange(8))
        identity = np.arange(8)
        np.testing.assert_array_equal(bank.state_map_for_word((0, 0, 0, 0)), identity)
        np.testing.assert_array_equal(bank.state_map_for_word((1, 1)), identity)
        np.testing.assert_array_equal(bank.state_map_for_word((1, 0, 1, 0)), identity)

    def test_path_hash_matches_registry_contract(self) -> None:
        self.assertEqual(
            bank.path_word_sha256((0, 1, 1, 0)),
            "0f9e1a63971c82cd09223ce20291e23140a9780edcf6067f320aaad339edc6f9",
        )

    def test_context_key_matches_historical_registry_vector(self) -> None:
        maps = np.asarray(
            [
                [2, 6, 0, 7, 5, 4, 1, 3],
                [7, 0, 6, 2, 3, 1, 4, 5],
            ],
            dtype="<i8",
        )
        context = {
            "tables": np.eye(8, dtype="<f4")[maps],
            "canonical_to_slot": np.asarray([1, 0], dtype="<i8"),
        }
        self.assertEqual(
            bank.context_key(context),
            "282d850ec7788ce55ff60f60db870c5564d48336ce20990137b0838e4e33370e",
        )


class FreshMaterialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = bank.build_bank_document(
            FIXED_ROOT,
            design_commit_sha256="1" * 64,
            registry=empty_registry(),
            registry_sha256="2" * 64,
            draw_receipt_sha256="3" * 64,
        )

    def test_bank_is_deterministic_and_content_addressed(self) -> None:
        again = bank.build_bank_document(
            FIXED_ROOT,
            design_commit_sha256="1" * 64,
            registry=empty_registry(),
            registry_sha256="2" * 64,
            draw_receipt_sha256="3" * 64,
        )
        self.assertEqual(self.document, again)
        payload = self.document["payload"]
        self.assertEqual(self.document["payload_sha256"], bank.canonical_json_digest(payload))
        expected_bank_id = hashlib.sha256(
            b"komorebi.neuralese.semantic_retraction.bank_id.v1\x00"
            + bank.canonical_json_bytes(payload)
        ).hexdigest()
        self.assertEqual(self.document["bank_id"], expected_bank_id)
        # Whole-bank golden vector for the frozen NumPy 2.3.5 PCG64 contract.
        self.assertEqual(
            self.document["bank_id"],
            "01b608229a583406b061739b4ac16fae24b76b6b5f709d5d6fb85886487c2a2a",
        )
        self.assertEqual(
            self.document["payload_sha256"],
            "1070055d09d8d90200894e30c4bec4024996b6e73ddaaf9fd7dd0d46357bbaeb",
        )

    def test_context_splits_are_exactly_sized_unique_and_disjoint(self) -> None:
        payload = self.document["payload"]
        calibration = payload["splits"]["calibration"]["context_bank"]
        evaluation = payload["splits"]["evaluation"]["context_bank"]
        self.assertEqual(len(calibration["context_keys"]), 64)
        self.assertEqual(len(evaluation["context_keys"]), 64)
        self.assertEqual(len(set(calibration["context_keys"])), 64)
        self.assertEqual(len(set(evaluation["context_keys"])), 64)
        self.assertFalse(set(calibration["context_keys"]) & set(evaluation["context_keys"]))
        self.assertTrue(payload["exact_disjointness"]["pass"])

    def test_context_rows_reproduce_keys_and_tensor_receipts(self) -> None:
        canonical = bank.canonical_d4_maps()
        for split in ("calibration", "evaluation"):
            context_bank = self.document["payload"]["splits"][split]["context_bank"]
            for context in context_bank["contexts"]:
                arrays = {
                    "tables": np.asarray(context["tables"], dtype=np.float32),
                    "maps": np.asarray(context["maps"], dtype=np.int64),
                    "phi": np.asarray(context["phi"], dtype=np.int64),
                    "canonical_to_slot": np.asarray(
                        context["canonical_to_slot"], dtype=np.int64
                    ),
                }
                self.assertEqual(bank.context_key(arrays), context["context_key"])
                for name, array in arrays.items():
                    self.assertEqual(bank._tensor_receipt(array), context["tensor_receipts"][name])
                phi = arrays["phi"]
                inverse = np.argsort(phi)
                slots = arrays["canonical_to_slot"]
                for canonical_operator in range(2):
                    visible_map = arrays["maps"][slots[canonical_operator]]
                    expected_map = phi[canonical[canonical_operator][inverse]]
                    np.testing.assert_array_equal(visible_map, expected_map)
                np.testing.assert_array_equal(
                    arrays["tables"],
                    np.eye(8, dtype=np.float32)[arrays["maps"]],
                )

    def test_context_receipts_and_keys_are_explicitly_little_endian(self) -> None:
        context = self.document["payload"]["splits"]["calibration"]["context_bank"][
            "contexts"
        ][0]
        little = {
            "tables": np.asarray(context["tables"], dtype="<f4"),
            "canonical_to_slot": np.asarray(context["canonical_to_slot"], dtype="<i8"),
        }
        big = {
            "tables": np.asarray(context["tables"], dtype=">f4"),
            "canonical_to_slot": np.asarray(context["canonical_to_slot"], dtype=">i8"),
        }
        self.assertEqual(bank.context_key(little), bank.context_key(big))
        self.assertEqual(bank._tensor_receipt(little["tables"]), bank._tensor_receipt(big["tables"]))
        self.assertEqual(
            bank._tensor_receipt(little["canonical_to_slot"]),
            bank._tensor_receipt(big["canonical_to_slot"]),
        )
        self.assertEqual(bank._tensor_receipt(little["tables"])["dtype"], "<f4")
        self.assertEqual(bank._tensor_receipt(little["canonical_to_slot"])["dtype"], "<i8")

    def test_identity_path_splits_are_balanced_disjoint_and_exact_depth(self) -> None:
        splits = self.document["payload"]["splits"]
        hashes: dict[str, set[str]] = {}
        for split in ("calibration", "evaluation"):
            path_bank = splits[split]["identity_path_bank"]
            self.assertEqual(path_bank["count"], 8)
            self.assertEqual(len(path_bank["paths"]), path_bank["count"])
            hashes[split] = set(path_bank["word_sha256"])
            self.assertEqual(len(hashes[split]), 8)
            self.assertEqual(
                path_bank["word_sha256"],
                [record["word_sha256"] for record in path_bank["paths"]],
            )
            for record in path_bank["paths"]:
                word = record["word"]
                self.assertEqual(len(word), 64)
                self.assertEqual(record["exact_length"], 64)
                self.assertTrue(all(symbol in (0, 1) for symbol in word))
                self.assertEqual(word.count(0), 32)
                self.assertEqual(word.count(1), 32)
                self.assertEqual(record["generator_histogram"], {"r": 32, "f": 32})
                self.assertEqual(record["word_sha256"], bank.path_word_sha256(word))
                state_map = bank.state_map_for_word(word)
                np.testing.assert_array_equal(state_map, np.arange(8))
                self.assertEqual(record["full_state_map"], state_map.tolist())
                self.assertTrue(record["identity_on_all_eight_starts"])
                self.assertEqual(record["maximum_symbol_run"], bank.maximum_symbol_run(word))
        self.assertFalse(hashes["calibration"] & hashes["evaluation"])

    def test_identity_paths_are_identity_through_every_visible_context_slot(self) -> None:
        splits = self.document["payload"]["splits"]
        for split in ("calibration", "evaluation"):
            contexts = splits[split]["context_bank"]["contexts"]
            paths = splits[split]["identity_path_bank"]["paths"]
            for context in contexts:
                maps = np.asarray(context["maps"], dtype=np.int64)
                slots = np.asarray(context["canonical_to_slot"], dtype=np.int64)
                for path in paths:
                    current = np.arange(8, dtype=np.int64)
                    for canonical_operator in path["word"]:
                        current = maps[slots[canonical_operator], current]
                    np.testing.assert_array_equal(current, np.arange(8))

    def test_all_emitted_domains_and_derived_seeds_are_exact_and_distinct(self) -> None:
        payload = self.document["payload"]
        expected_domains = [
            "context/calibration",
            "context/evaluation",
            "path/calibration",
            "path/evaluation",
        ]
        self.assertEqual(payload["derivation"]["domains"], expected_domains)
        self.assertEqual(payload["derivation"]["numpy_version"], np.__version__)
        observed: dict[str, str] = {}
        for split in ("calibration", "evaluation"):
            split_value = payload["splits"][split]
            for name in ("context_bank", "identity_path_bank"):
                record = split_value[name]
                observed[record["domain"]] = record["derived_seed_hex"]
        self.assertEqual(set(observed), set(expected_domains))
        self.assertEqual(len(set(observed.values())), 4)
        for domain in expected_domains:
            self.assertEqual(observed[domain], bank.hkdf_sha256(FIXED_ROOT, domain).hex())

    def test_registry_exclusions_are_hard_constraints(self) -> None:
        initial = self.document["payload"]["splits"]
        forbidden_context = initial["calibration"]["context_bank"]["context_keys"][0]
        forbidden_path = initial["calibration"]["identity_path_bank"]["word_sha256"][0]
        registry = empty_registry()
        registry["forbidden_context_keys"] = [forbidden_context]
        registry["forbidden_path_word_sha256"] = [forbidden_path]
        registry["counts"] = {"unique_context_keys": 1, "unique_path_words": 1}
        regenerated = bank.build_bank_document(
            FIXED_ROOT,
            design_commit_sha256="1" * 64,
            registry=registry,
            registry_sha256="2" * 64,
            draw_receipt_sha256="3" * 64,
        )
        new_splits = regenerated["payload"]["splits"]
        all_contexts = {
            key
            for split in new_splits.values()
            for key in split["context_bank"]["context_keys"]
        }
        all_paths = {
            value
            for split in new_splits.values()
            for value in split["identity_path_bank"]["word_sha256"]
        }
        self.assertNotIn(forbidden_context, all_contexts)
        self.assertNotIn(forbidden_path, all_paths)


class RegistryAndCommitTests(unittest.TestCase):
    def test_registry_requires_sorted_unique_hashes(self) -> None:
        malformed = empty_registry()
        malformed["forbidden_context_keys"] = ["b" * 64, "a" * 64]
        with self.assertRaises(ValueError):
            bank.validate_registry_document(malformed)
        malformed["forbidden_context_keys"] = ["a" * 64, "a" * 64]
        with self.assertRaises(ValueError):
            bank.validate_registry_document(malformed)

    def test_design_commit_checks_all_local_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            result = bank.validate_design_commit(paths["design"], project_root=paths["root"])
            self.assertEqual(len(result["artifacts"]), len(bank.DESIGN_FILE_MAP))
            for parts in bank.DESIGN_FILE_MAP.values():
                frozen_file = paths["root"].joinpath(*parts)
                original = frozen_file.read_bytes()
                frozen_file.write_bytes(original + b"changed\n")
                with self.assertRaises(ValueError):
                    bank.validate_design_commit(
                        paths["design"], project_root=paths["root"]
                    )
                frozen_file.write_bytes(original)

            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            design["unbound_claim"] = True
            write_canonical(paths["design"], design)
            with self.assertRaisesRegex(ValueError, "unexpected"):
                bank.validate_design_commit(paths["design"], project_root=paths["root"])

    def test_design_cannot_commit_source_other_than_executing_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            substitute = paths["root"] / "prospective" / "fresh_bank.py"
            substitute.write_bytes(b"# internally consistent but not executing code\n")
            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            design["fresh_bank_implementation_sha256"] = bank.sha256_file(substitute)

            synthetic_path = paths["root"] / "preflight" / "SYNTHETIC_TESTS.json"
            synthetic = json.loads(synthetic_path.read_text(encoding="utf-8"))
            synthetic["implementation_receipts"]["fresh_bank_implementation_sha256"] = (
                design["fresh_bank_implementation_sha256"]
            )
            write_canonical(synthetic_path, synthetic)
            design["synthetic_tests_sha256"] = bank.sha256_file(synthetic_path)

            protocol_path = paths["root"] / "prospective" / "PROTOCOL.json"
            protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
            protocol["implementation_receipts"]["fresh_bank_implementation_sha256"] = (
                design["fresh_bank_implementation_sha256"]
            )
            protocol["synthetic_tests"]["sha256"] = design["synthetic_tests_sha256"]
            write_canonical(protocol_path, protocol)
            design["protocol_sha256"] = bank.sha256_file(protocol_path)

            freeze_path = paths["root"] / "prospective" / "FROZEN_PROTOCOL.sha256"
            freeze_path.write_text(
                f"{design['protocol_sha256']}  PROTOCOL.json\n",
                encoding="utf-8",
            )
            design["frozen_protocol_receipt_sha256"] = bank.sha256_file(freeze_path)
            write_canonical(paths["design"], design)
            with self.assertRaisesRegex(ValueError, "executing source"):
                bank.validate_design_commit(paths["design"], project_root=paths["root"])

    def test_noncanonical_commit_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            value = json.loads(paths["design"].read_text(encoding="utf-8"))
            paths["design"].write_text(json.dumps(value, indent=2), encoding="utf-8")
            with self.assertRaises(ValueError):
                bank.validate_design_commit(paths["design"], project_root=paths["root"])

    def test_design_requires_semantically_matching_protocol_freeze_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            freeze = paths["root"] / "prospective" / "FROZEN_PROTOCOL.sha256"
            freeze.write_text(f"{'0' * 64}  PROTOCOL.json\n", encoding="utf-8")
            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            design["frozen_protocol_receipt_sha256"] = bank.sha256_file(freeze)
            write_canonical(paths["design"], design)
            with self.assertRaisesRegex(ValueError, "does not bind"):
                bank.validate_design_commit(
                    paths["design"],
                    project_root=paths["root"],
                )


@mock.patch.object(bank, "MIN_FREE_BYTES_BEFORE_DRAW", 0)
class SealFirewallTests(unittest.TestCase):
    def test_low_free_space_blocks_before_entropy_and_terminal_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            calls = 0

            def entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return bytes(length)

            usage = shutil.disk_usage("/")._replace(free=0)
            with (
                mock.patch.object(bank, "MIN_FREE_BYTES_BEFORE_DRAW", 1),
                mock.patch.object(bank.shutil, "disk_usage", return_value=usage),
            ):
                with self.assertRaisesRegex(OSError, "before production entropy"):
                    bank.seal_fresh_bank(
                        design_commit_path=paths["design"],
                        registry_path=paths["registry"],
                        bank_path=paths["bank"],
                        draw_receipt_path=paths["draw"],
                        seal_receipt_path=paths["seal"],
                        entropy_source=entropy,
                        project_root=paths["root"],
                    )
            self.assertEqual(calls, 0)
            self.assertFalse(paths["draw"].exists())

    def test_pretty_registry_is_accepted_when_exact_raw_hash_is_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory), pretty_registry=True)
            raw_registry = paths["registry"].read_bytes()
            self.assertNotEqual(
                raw_registry,
                bank.canonical_json_bytes(json.loads(raw_registry)),
            )
            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            self.assertEqual(
                design["spent_bank_registry_sha256"],
                hashlib.sha256(raw_registry).hexdigest(),
            )
            bank.seal_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                entropy_source=lambda length: FIXED_ROOT,
                project_root=paths["root"],
            )
            verified = bank.verify_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                project_root=paths["root"],
            )
            self.assertEqual(verified["status"], "VERIFIED_READ_ONLY")

    def test_verify_rejects_byte_identical_registry_at_alternate_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            bank.seal_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                entropy_source=lambda length: FIXED_ROOT,
                project_root=paths["root"],
            )
            copied_registry = paths["root"] / "REGISTRY_COPY.json"
            copied_registry.write_bytes(paths["registry"].read_bytes())
            with self.assertRaisesRegex(ValueError, "fixed project path"):
                bank.verify_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=copied_registry,
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    project_root=paths["root"],
                )

    def test_seal_then_read_only_verify_and_refuse_redraw(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            calls: list[int] = []

            def fixed_entropy(length: int) -> bytes:
                calls.append(length)
                return FIXED_ROOT

            result = bank.seal_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                entropy_source=fixed_entropy,
                project_root=paths["root"],
            )
            self.assertEqual(calls, [32])
            verified = bank.verify_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                project_root=paths["root"],
            )
            self.assertEqual(verified["status"], "VERIFIED_READ_ONLY")
            self.assertEqual(verified["bank_id"], result["bank_id"])
            self.assertEqual(calls, [32])
            with self.assertRaises(FileExistsError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=fixed_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, [32], "redraw refusal must occur before entropy access")

    def test_invalid_design_fails_before_entropy_access(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            (paths["root"] / "prospective" / "PROTOCOL.json").write_bytes(b"tampered")
            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return os.urandom(length)

            with self.assertRaises(ValueError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)
            self.assertFalse(paths["draw"].exists())

    def test_coherently_rehashed_failed_preflight_cannot_draw_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            preflight_path = paths["root"] / "preflight" / "PREFLIGHT.json"
            preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
            preflight["status"] = "FAIL"
            write_canonical(preflight_path, preflight)

            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            design["parameter_preflight_sha256"] = bank.sha256_file(preflight_path)
            protocol_path = paths["root"] / "prospective" / "PROTOCOL.json"
            protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
            protocol["preflight"]["sha256"] = design["parameter_preflight_sha256"]
            write_canonical(protocol_path, protocol)
            design["protocol_sha256"] = bank.sha256_file(protocol_path)
            freeze_path = paths["root"] / "prospective" / "FROZEN_PROTOCOL.sha256"
            freeze_path.write_text(
                f"{design['protocol_sha256']}  PROTOCOL.json\n", encoding="utf-8"
            )
            design["frozen_protocol_receipt_sha256"] = bank.sha256_file(freeze_path)
            write_canonical(paths["design"], design)

            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return os.urandom(length)

            with self.assertRaisesRegex(ValueError, "preflight.*PASS"):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)
            self.assertFalse(paths["draw"].exists())

    def test_coherently_rehashed_entropy_using_synthetic_cannot_draw_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            synthetic_path = paths["root"] / "preflight" / "SYNTHETIC_TESTS.json"
            synthetic = json.loads(synthetic_path.read_text(encoding="utf-8"))
            synthetic["full_shape_synthetic_checkpoint"]["production_entropy_used"] = True
            write_canonical(synthetic_path, synthetic)

            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            design["synthetic_tests_sha256"] = bank.sha256_file(synthetic_path)
            protocol_path = paths["root"] / "prospective" / "PROTOCOL.json"
            protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
            protocol["synthetic_tests"]["sha256"] = design["synthetic_tests_sha256"]
            write_canonical(protocol_path, protocol)
            design["protocol_sha256"] = bank.sha256_file(protocol_path)
            freeze_path = paths["root"] / "prospective" / "FROZEN_PROTOCOL.sha256"
            freeze_path.write_text(
                f"{design['protocol_sha256']}  PROTOCOL.json\n", encoding="utf-8"
            )
            design["frozen_protocol_receipt_sha256"] = bank.sha256_file(freeze_path)
            write_canonical(paths["design"], design)

            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return os.urandom(length)

            with self.assertRaisesRegex(ValueError, "synthetic-test.*PASS"):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)
            self.assertFalse(paths["draw"].exists())

    def test_coherently_rehashed_draft_protocol_cannot_draw_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            protocol_path = paths["root"] / "prospective" / "PROTOCOL.json"
            freeze_path = paths["root"] / "prospective" / "FROZEN_PROTOCOL.sha256"
            protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
            protocol["status"] = "DRAFT_NO_PRODUCTION_ENTROPY"
            write_canonical(protocol_path, protocol)
            protocol_sha256 = bank.sha256_file(protocol_path)
            freeze_path.write_text(
                f"{protocol_sha256}  PROTOCOL.json\n",
                encoding="utf-8",
            )
            design = json.loads(paths["design"].read_text(encoding="utf-8"))
            design["protocol_sha256"] = protocol_sha256
            design["frozen_protocol_receipt_sha256"] = bank.sha256_file(
                freeze_path
            )
            write_canonical(paths["design"], design)
            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return os.urandom(length)

            with self.assertRaisesRegex(ValueError, "protocol is not frozen"):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)
            self.assertFalse(paths["draw"].exists())

    def test_existing_draw_receipt_alone_blocks_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            paths["draw"].write_bytes(b"prior production draw")
            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return b"x" * length

            with self.assertRaises(FileExistsError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)

    def test_failed_entropy_call_leaves_terminal_no_redraw_reservation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            calls = 0

            def broken_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return b"too short"

            with self.assertRaises(RuntimeError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=broken_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 1)
            self.assertTrue(paths["draw"].exists())
            self.assertEqual(paths["draw"].stat().st_size, 0)
            with self.assertRaises(FileExistsError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=broken_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 1)

    def test_alternate_draw_path_cannot_bypass_terminal_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            calls = 0

            def first_bad_then_good(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return b"short" if calls == 1 else FIXED_ROOT

            with self.assertRaises(RuntimeError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=first_bad_then_good,
                    project_root=paths["root"],
                )
            alternate_draw = paths["root"] / "prospective" / "ALTERNATE_DRAW.json"
            with self.assertRaises(ValueError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=alternate_draw,
                    seal_receipt_path=paths["seal"],
                    entropy_source=first_bad_then_good,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 1)
            self.assertFalse(alternate_draw.exists())

    def test_draw_fsync_failure_preserves_original_error_and_terminal_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            failure = OSError("simulated draw fsync failure")
            fsync_calls = 0

            def fail_when_filling_draw(descriptor: int) -> None:
                nonlocal fsync_calls
                fsync_calls += 1
                if fsync_calls == 3:
                    raise failure

            with mock.patch.object(bank.os, "fsync", side_effect=fail_when_filling_draw):
                with self.assertRaisesRegex(OSError, "simulated draw fsync failure"):
                    bank.seal_fresh_bank(
                        design_commit_path=paths["design"],
                        registry_path=paths["registry"],
                        bank_path=paths["bank"],
                        draw_receipt_path=paths["draw"],
                        seal_receipt_path=paths["seal"],
                        entropy_source=lambda length: FIXED_ROOT,
                        project_root=paths["root"],
                    )
            self.assertTrue(paths["draw"].exists())
            self.assertGreater(paths["draw"].stat().st_size, 0)
            with self.assertRaises(FileExistsError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=lambda length: FIXED_ROOT,
                    project_root=paths["root"],
                )

    def test_fdopen_construction_failure_closes_reserved_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reserved"
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            real_close = os.close
            with mock.patch.object(
                bank.os,
                "fdopen",
                side_effect=OSError("simulated fdopen failure"),
            ), mock.patch.object(bank.os, "close", wraps=real_close) as close_call:
                with self.assertRaisesRegex(OSError, "simulated fdopen failure"):
                    bank._write_reserved_file(descriptor, b"payload")
                close_call.assert_called_once_with(descriptor)

    def test_symlink_target_is_rejected_before_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            target = paths["root"] / "prospective" / "elsewhere.json"
            target.write_bytes(b"do not overwrite")
            paths["bank"].symlink_to(target)
            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return b"x" * length

            with self.assertRaises(ValueError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)
            self.assertEqual(target.read_bytes(), b"do not overwrite")

    def test_dotdot_target_alias_is_rejected_before_entropy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            subdirectory = paths["root"] / "prospective" / "sub"
            subdirectory.mkdir()
            alias = subdirectory / ".." / paths["bank"].name
            calls = 0

            def forbidden_entropy(length: int) -> bytes:
                nonlocal calls
                calls += 1
                return b"x" * length

            with self.assertRaises(ValueError):
                bank.seal_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=alias,
                    seal_receipt_path=paths["seal"],
                    entropy_source=forbidden_entropy,
                    project_root=paths["root"],
                )
            self.assertEqual(calls, 0)
            self.assertFalse(paths["bank"].exists())

    def test_tampered_bank_fails_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            bank.seal_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                entropy_source=lambda length: FIXED_ROOT,
                project_root=paths["root"],
            )
            document = json.loads(paths["bank"].read_text(encoding="utf-8"))
            document["payload"]["splits"]["evaluation"]["context_bank"]["count"] = 63
            paths["bank"].chmod(0o644)
            write_canonical(paths["bank"], document)
            with self.assertRaises(ValueError):
                bank.verify_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    project_root=paths["root"],
                )

    def test_coherently_rehashed_noncanonical_draw_schema_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_frozen_project(Path(directory))
            bank.seal_fresh_bank(
                design_commit_path=paths["design"],
                registry_path=paths["registry"],
                bank_path=paths["bank"],
                draw_receipt_path=paths["draw"],
                seal_receipt_path=paths["seal"],
                entropy_source=lambda length: FIXED_ROOT,
                project_root=paths["root"],
            )
            design_bytes = paths["design"].read_bytes()
            registry_bytes = paths["registry"].read_bytes()
            registry = json.loads(registry_bytes)
            draw = json.loads(paths["draw"].read_text(encoding="utf-8"))
            draw["version"] = "999.0"
            draw["unexpected_extension"] = True
            draw_bytes = bank.canonical_json_bytes(draw)
            forged_bank = bank.build_bank_document(
                FIXED_ROOT,
                design_commit_sha256=hashlib.sha256(design_bytes).hexdigest(),
                registry=registry,
                registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
                draw_receipt_sha256=hashlib.sha256(draw_bytes).hexdigest(),
            )
            forged_bank_bytes = bank.canonical_json_bytes(forged_bank)
            forged_seal = bank._seal_receipt_document(
                bank_path=paths["bank"],
                bank_bytes=forged_bank_bytes,
                bank_id=forged_bank["bank_id"],
                draw_receipt_path=paths["draw"],
                draw_receipt_bytes=draw_bytes,
                design_commit_sha256=hashlib.sha256(design_bytes).hexdigest(),
                registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
            )
            for path, payload in (
                (paths["draw"], draw_bytes),
                (paths["bank"], forged_bank_bytes),
                (paths["seal"], bank.canonical_json_bytes(forged_seal)),
            ):
                path.chmod(0o644)
                path.write_bytes(payload)
            with self.assertRaises(ValueError):
                bank.verify_fresh_bank(
                    design_commit_path=paths["design"],
                    registry_path=paths["registry"],
                    bank_path=paths["bank"],
                    draw_receipt_path=paths["draw"],
                    seal_receipt_path=paths["seal"],
                    project_root=paths["root"],
                )


if __name__ == "__main__":
    unittest.main()
