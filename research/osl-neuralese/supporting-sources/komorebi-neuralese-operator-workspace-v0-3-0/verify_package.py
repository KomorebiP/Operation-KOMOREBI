#!/usr/bin/env python3
"""Fail-closed verification for the Komorebi v0.3.0 release package.

Scientific gate failure is a valid recorded outcome.  This verifier therefore
does not require every primary gate to pass; it independently rebuilds the
aggregate and gate decisions and requires the result receipt, evidence ledger,
and package manifest to preserve that outcome exactly.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from komorebi_neuralese.reporting import code_files, tree_digest
from komorebi_neuralese.sparse_task import (
    MONOMIAL_FAMILY,
    SHEAR_FAMILY,
    context_audit_record,
)
from komorebi_neuralese.splits import audit_coordinate_splits
from komorebi_neuralese.version import VERSION
from run_experiment import _aggregate_all, _evaluate_gates


EXPECTED_VERSION = "0.3.0"
EXPECTED_CODE_DIGEST = "814ea6f2301523965bf8d94dd9da8bbb598451f03e0200cae1cde2ab8de53624"
EXPECTED_CODE_FILES = 29
EXPECTED_COORDINATE_SPLIT_DIGEST = "3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340"
EXPECTED_PRIMARY_PROTOCOL_DIGEST = "ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf"
EXPECTED_PRIMARY_SEAL_DIGEST = "84c15ffcef8553288fe3e3393e7056ca0c1cfcdd8c78639f61d0adfe6d80f5c9"
EXPECTED_QUALIFICATION_PROTOCOL_DIGEST = "0bca42f89400904180f36872aaa4fb8040c2cb848b86e50dc084eb90a47634a0"
EXPECTED_QUALIFICATION_RECEIPT_DIGEST = "511d706bd82f910d1817e21e99aa58823e86707b5652736fd74281e2d75e7f55"
EXPECTED_V02_ARCHIVE_DIGEST = "9bd43069b1b184943aee32465c73c2441f4842165ede5c41a9f28f5f97b9e73d"
MINIMUM_TESTS = 179

PRIMARY_PROTOCOL = ROOT / "protocols" / "V0_3_STAGE_A_PRIMARY.json"
PRIMARY_SEAL = ROOT / "protocols" / "V0_3_STAGE_A_PRIMARY_SEAL.json"
QUALIFICATION_PROTOCOL = ROOT / "protocols" / "V0_3_STAGE_A_QUALIFICATION.json"
PRIMARY = ROOT / "results" / "v0.3.0" / "stage_a_primary_v3"
QUALIFICATION = ROOT / "results" / "v0.3.0" / "stage_a_qualification_v3"
REPRODUCIBILITY = ROOT / "results" / "v0.3.0" / "stage_a_reproducibility"

GENERATED_FILES = {"MANIFEST.json", "SHA256SUMS.txt"}
FORBIDDEN_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "local_runs",
}
FORBIDDEN_FILE_NAMES = {".DS_Store", "RUNNING.json", "FAILED.json"}

REQUIRED_CURRENT_DOCS = (
    "README.md",
    "RESEARCH_SPEC.md",
    "CLAIM_BOUNDARY.md",
    "TEST_PLAN.md",
    "AUDIT_NOTES.md",
    "CHANGELOG.md",
    "LINEAGE.md",
    "RESULTS_INDEX.md",
    "results/v0.3.0/INTEGRATED_FINDINGS.md",
)

EXPECTED_TRAINING_SUPPORTS = (
    {
        "length": 1,
        "candidate_pairs": 25008,
        "accepted_pairs": 25008,
        "exact_acceptance_numerator": 25008,
        "exact_acceptance_denominator": 25008,
        "digest": "265cc1737ac80cf2afcfd2261a16b5d5d8770286511c3e1b6a7bac9bb3f326cb",
    },
    {
        "length": 2,
        "candidate_pairs": 50016,
        "accepted_pairs": 32120,
        "exact_acceptance_numerator": 32120,
        "exact_acceptance_denominator": 50016,
        "digest": "c1074929f34aadefb48ad52de8882afe29e388e07cb6be66ed7b71d1d343be3b",
    },
    {
        "length": 3,
        "candidate_pairs": 100032,
        "accepted_pairs": 37936,
        "exact_acceptance_numerator": 37936,
        "exact_acceptance_denominator": 100032,
        "digest": "7f5ab4a82c43e918f8485e0768cd6d1dd11c7fa37ac732ccf2d3644032ecae3d",
    },
    {
        "length": 4,
        "candidate_pairs": 200064,
        "accepted_pairs": 45680,
        "exact_acceptance_numerator": 45680,
        "exact_acceptance_denominator": 200064,
        "digest": "7759e2320e3f3a8992f7d5654a1f1688d5cd15bd599dc09b0cdcccdce4ee5813",
    },
)

EXPECTED_SPARSE_AUDITS = {
    "monomial": {
        "catalog_digest": "77d8d985a569420e1bcfdd230a6d7b36e2496498028ece9ade77a61d67fa4334",
        "bounded_supported_maps": 1902,
        "bounded_contamination": {"dev": 0, "test": 0},
        "bounded_witness_digest": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "bounded_novelty": True,
        "global_depth_two_maps": 19861,
        "global_contamination": {"dev": 48, "test": 48},
        "global_witness_digest": "d72912af618d48c6517bf4913d0099b49e7f22191a8a644a935e1d21a6c7da18",
        "global_all_heldout_witnessed": True,
        "unbounded_novelty": False,
    },
    "shear": {
        "catalog_digest": "87a40820648367a6c6fc6b03a51ce8335bed71e0dded4b3b39160563c92fa05a",
        "bounded_supported_maps": 1192,
        "bounded_contamination": {"dev": 43, "test": 43},
        "bounded_witness_digest": "e24de9b50a3b06c3d958f8b19d31216d81410cd9847d23eeb04a526be9af4190",
        "bounded_novelty": False,
        "global_depth_two_maps": 13151,
        "global_contamination": {"dev": 48, "test": 48},
        "global_witness_digest": "a8f57ab80177320b97ed9736deb1c85b523b74cf6f0efd947f40f22923bc52f3",
        "global_all_heldout_witnessed": True,
        "unbounded_novelty": False,
    },
}


class PackageVerificationError(RuntimeError):
    """Raised on the first fail-closed package-integrity violation."""


def fail(message: str) -> None:
    raise PackageVerificationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"required JSON file is missing: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"could not parse JSON file {path}: {error}")
    if not isinstance(value, dict):
        fail(f"expected a JSON object in {path}")
    return value


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        fail(f"value is not finite canonical JSON: {error}")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def assert_equal(observed: Any, expected: Any, label: str) -> None:
    if observed != expected:
        fail(f"{label} mismatch: expected {expected!r}, observed {observed!r}")


def included_files(*, include_manifest: bool) -> set[str]:
    output: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in FORBIDDEN_DIRECTORY_NAMES for part in relative.parts):
            continue
        if path.name in FORBIDDEN_FILE_NAMES or path.suffix in {".pyc", ".pyo"}:
            continue
        name = relative.as_posix()
        if name == "SHA256SUMS.txt" or (name == "MANIFEST.json" and not include_manifest):
            continue
        output.add(name)
    return output


def verify_no_forbidden_artifacts() -> None:
    bad: list[str] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in FORBIDDEN_DIRECTORY_NAMES for part in relative.parts):
            bad.append(relative.as_posix() + ("/" if path.is_dir() else ""))
            continue
        if path.is_file() and (path.name in FORBIDDEN_FILE_NAMES or path.suffix in {".pyc", ".pyo"}):
            bad.append(relative.as_posix())
    if bad:
        fail("forbidden cache, local-run, or incomplete-run artifacts remain: " + ", ".join(sorted(set(bad))[:40]))


def verify_current_documents() -> None:
    for relative in REQUIRED_CURRENT_DOCS:
        path = ROOT / relative
        if not path.is_file():
            fail(f"required current-release document is missing: {relative}")
        text = path.read_text(encoding="utf-8")
        if "0.3.0" not in text:
            fail(f"current-release document does not identify v0.3.0: {relative}")
    analysis_readme = (ROOT / "analysis_tools" / "README.md").read_text(encoding="utf-8")
    if "results/v0.3.0/stage_a_primary_v3" not in analysis_readme:
        fail("analysis_tools/README.md does not point to the sealed v0.3 primary path")
    launcher_requirements = {
        "RUN_QUALIFICATION.ps1": "V0_3_STAGE_A_QUALIFICATION.json",
        "RUN_PRIMARY.ps1": "V0_3_STAGE_A_PRIMARY.json",
        "VERIFY.ps1": "verify_package.py",
    }
    for relative, needle in launcher_requirements.items():
        path = ROOT / relative
        if not path.is_file() or needle not in path.read_text(encoding="utf-8"):
            fail(f"launcher is missing or stale: {relative}")


def _normalized_supports(supports: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(supports, list):
        fail("conditioning support receipt is not a list")
    normalized: list[dict[str, Any]] = []
    for support in supports:
        if not isinstance(support, dict):
            fail("conditioning support receipt contains a non-object")
        item = {key: support.get(key) for key in EXPECTED_TRAINING_SUPPORTS[0]}
        numerator = int(item["exact_acceptance_numerator"])
        denominator = int(item["exact_acceptance_denominator"])
        probability = support.get("acceptance_probability")
        if not isinstance(probability, (int, float)) or not math.isclose(
            float(probability), numerator / denominator, rel_tol=0.0, abs_tol=1e-15
        ):
            fail(f"conditioning support probability is inconsistent at length {item['length']}")
        normalized.append(item)
    return tuple(sorted(normalized, key=lambda item: int(item["length"])))


def verify_training_sampling_audit(
    audit: Mapping[str, Any], protocol: Mapping[str, Any], *, label: str
) -> None:
    training = protocol["training"]
    steps = int(training["steps"])
    batch = int(training["batch_size"])
    expected_examples = steps * batch
    required = {
        "fail_closed": True,
        "word_product_scope": "contiguous",
        "word_product_split": "train",
        "coordinate_split": "train",
        "conditioned_sampler_backend": "cached_exact_v1",
        "auxiliary_paths_independently_filtered": True,
        "generated_group_closure_constrained": False,
        "split_violations": 0,
        "accepted_examples": expected_examples,
        "candidate_examples": expected_examples,
        "rejected_examples": 0,
        "training_batches": steps,
    }
    for key, expected in required.items():
        assert_equal(audit.get(key), expected, f"{label} training sampling {key}")
    assert_equal(audit.get("sampling_methods"), ["direct_conditioned_uniform"], f"{label} sampling methods")
    assert_equal(_normalized_supports(audit.get("conditioning_supports")), EXPECTED_TRAINING_SUPPORTS, f"{label} conditioning supports")
    by_length = audit.get("by_length")
    if not isinstance(by_length, dict) or set(by_length) != {"1", "2", "3", "4"}:
        fail(f"{label} training length receipt is incomplete")
    if sum(int(item.get("batches", -1)) for item in by_length.values()) != steps:
        fail(f"{label} training length batches do not sum to the frozen step count")
    if sum(int(item.get("accepted_examples", -1)) for item in by_length.values()) != expected_examples:
        fail(f"{label} training length examples do not sum to the frozen total")
    for length, item in by_length.items():
        if item.get("sampling_methods") != ["direct_conditioned_uniform"]:
            fail(f"{label} length-{length} sampling method mismatch")
        expected_digest = EXPECTED_TRAINING_SUPPORTS[int(length) - 1]["digest"]
        if item.get("conditioning_support_digests") != [expected_digest]:
            fail(f"{label} length-{length} support digest mismatch")
        accepted = int(item.get("accepted_examples", -1))
        if accepted < 0 or int(item.get("candidate_examples", -2)) != accepted or int(item.get("rejected_examples", -1)) != 0:
            fail(f"{label} length-{length} direct-sampler accounting mismatch")
    schedule = audit.get("length_schedule")
    if not isinstance(schedule, dict):
        fail(f"{label} independent length schedule receipt is missing")
    if schedule.get("independent_of_episode_sampler") is not True or schedule.get("steps") != steps:
        fail(f"{label} independent length schedule receipt failed")
    if schedule.get("minimum") != int(training["train_min_length"]) or schedule.get("maximum") != int(training["train_max_length"]):
        fail(f"{label} length schedule range mismatch")
    if not is_sha256(schedule.get("sha256")):
        fail(f"{label} length schedule digest is malformed")


def verify_split_conditioned_receipt(
    metrics: Mapping[str, Any], protocol: Mapping[str, Any], *, label: str
) -> None:
    evaluation = protocol["evaluation"]
    split = str(evaluation["coordinate_split"])
    depths = [int(value) for value in evaluation["semantic_holdout_depths"]]
    examples = int(evaluation["semantic_holdout_examples"])
    if metrics.get("available") is not True:
        fail(f"{label} split-conditioned final-action assay is unavailable")
    exact_fields = {
        "metric": "split_conditioned_full_composite_final_action_accuracy",
        "family": str(evaluation["semantic_holdout_family"]),
        "coordinate_split": split,
        "primitive_map_split": split,
        "composite_target_map_split": split,
        "primitive_split_enforced": True,
        "full_composite_split_enforced": True,
        "requested_depths": depths,
        "evaluated_depths": depths,
        "examples_per_depth": examples,
    }
    for key, expected in exact_fields.items():
        assert_equal(metrics.get(key), expected, f"{label} split-conditioned {key}")
    by_depth = metrics.get("by_depth")
    if not isinstance(by_depth, dict) or set(by_depth) != {str(value) for value in depths}:
        fail(f"{label} split-conditioned depth set mismatch")
    overall_digest = hashlib.sha256(
        b"komorebi-neuralese/heldout-composite-word-rejection-sampler/v1"
    )
    total_drawn = total_accepted = total_rejected = total_correct = 0
    total_candidate_counts = {name: 0 for name in ("train", "dev", "test")}
    total_primitive_counts = {name: 0 for name in ("train", "dev", "test")}
    for depth in depths:
        item = by_depth[str(depth)]
        receipt = item.get("acceptance_receipt")
        if not isinstance(receipt, dict):
            fail(f"{label} depth-{depth} acceptance receipt is missing")
        drawn = int(receipt.get("candidate_examples_drawn", -1))
        accepted = int(receipt.get("accepted_examples", -1))
        rejected = int(receipt.get("rejected_examples", -1))
        expected_fields = {
            "method": "deterministic_rejection_on_full_composite_map_split",
            "word_depth": depth,
            "requested_split": split,
            "requested_examples": examples,
            "accepted_examples": examples,
            "model_evaluated_examples": examples,
            "model_evaluated_rejected_examples": 0,
            "only_accepted_examples_evaluated": True,
            "primitive_split_violations": 0,
            "target_consistency_violations": 0,
            "candidate_accounting_exact": True,
            "acceptance_accounting_exact": True,
            "rejection_accounting_exact": True,
        }
        for key, expected in expected_fields.items():
            assert_equal(receipt.get(key), expected, f"{label} depth-{depth} {key}")
        if drawn != accepted + rejected or accepted != examples or drawn <= accepted:
            fail(f"{label} depth-{depth} candidate accounting mismatch")
        candidate_counts = receipt.get("candidate_composite_split_counts")
        accepted_counts = receipt.get("accepted_composite_split_counts")
        rejected_counts = receipt.get("rejected_composite_split_counts")
        primitive_counts = receipt.get("primitive_map_split_counts")
        if not all(isinstance(value, dict) for value in (candidate_counts, accepted_counts, rejected_counts, primitive_counts)):
            fail(f"{label} depth-{depth} split count receipt is malformed")
        if sum(int(value) for value in candidate_counts.values()) != drawn:
            fail(f"{label} depth-{depth} candidate split counts do not sum")
        if accepted_counts.get(split) != accepted or any(accepted_counts.get(name) != 0 for name in accepted_counts if name != split):
            fail(f"{label} depth-{depth} accepted composite split leaked")
        if candidate_counts.get(split) != accepted:
            fail(f"{label} depth-{depth} requested-split candidates differ from accepted examples")
        if sum(int(value) for value in rejected_counts.values()) != rejected or rejected_counts.get(split) != 0:
            fail(f"{label} depth-{depth} rejected split accounting mismatch")
        if primitive_counts.get(split) != 2 * drawn or any(primitive_counts.get(name) != 0 for name in primitive_counts if name != split):
            fail(f"{label} depth-{depth} primitive-table split leaked")
        if int(receipt.get("accepted_unique_composite_maps", 0)) <= 0:
            fail(f"{label} depth-{depth} accepted no distinct composite maps")
        candidate_sha = receipt.get("candidate_stream_sha256")
        accepted_sha = receipt.get("accepted_examples_sha256")
        if not is_sha256(candidate_sha) or not is_sha256(accepted_sha):
            fail(f"{label} depth-{depth} sample-stream digest is malformed")
        overall_digest.update(depth.to_bytes(8, "big", signed=False))
        overall_digest.update(bytes.fromhex(candidate_sha))
        overall_digest.update(bytes.fromhex(accepted_sha))
        correct = int(item.get("correct", -1))
        if item.get("examples") != examples or correct < 0 or correct > examples:
            fail(f"{label} depth-{depth} score accounting mismatch")
        if float(item.get("endpoint_accuracy", -1.0)) != correct / examples:
            fail(f"{label} depth-{depth} endpoint accuracy does not match exact count")
        finite = float(item.get("finite_logits_fraction", -1.0))
        if not (0.0 <= finite <= 1.0):
            fail(f"{label} depth-{depth} finite-logit fraction is invalid")
        total_drawn += drawn
        total_accepted += accepted
        total_rejected += rejected
        total_correct += correct
        for name in total_candidate_counts:
            total_candidate_counts[name] += int(candidate_counts.get(name, 0))
            total_primitive_counts[name] += int(primitive_counts.get(name, 0))
    overall = metrics.get("acceptance_receipt")
    if not isinstance(overall, dict):
        fail(f"{label} aggregate split-conditioned receipt is missing")
    aggregate_fields = {
        "candidate_examples_drawn": total_drawn,
        "accepted_examples": total_accepted,
        "rejected_examples": total_rejected,
        "candidate_composite_split_counts": total_candidate_counts,
        "primitive_map_split_counts": total_primitive_counts,
        "all_primitive_maps_in_requested_split": True,
        "all_accepted_full_composites_in_requested_split": True,
        "only_accepted_examples_evaluated": True,
        "model_evaluated_examples": total_accepted,
        "model_evaluated_rejected_examples": 0,
        "depth_receipts_sha256": overall_digest.hexdigest(),
    }
    for key, expected in aggregate_fields.items():
        assert_equal(overall.get(key), expected, f"{label} aggregate final-action {key}")
    if float(metrics.get("endpoint_accuracy", -1.0)) != total_correct / total_accepted:
        fail(f"{label} aggregate split-conditioned endpoint accuracy is inconsistent")


def verify_exact_oracle(
    run_dir: Path,
    *,
    code_digest: str,
    protocol_digest: str,
    coordinate_digest: str,
) -> None:
    oracle = read_json(run_dir / "EXACT_ORACLE.json")
    identity = (
        oracle.get("package_version"),
        oracle.get("code_digest"),
        oracle.get("protocol_digest"),
        oracle.get("coordinate_split_digest"),
        oracle.get("role"),
    )
    expected = (VERSION, code_digest, protocol_digest, coordinate_digest, "exact_structured_ceiling_only")
    assert_equal(identity, expected, f"{run_dir.name} exact-oracle provenance")
    integrity = oracle.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("passed") is not True:
        fail(f"{run_dir.name} exact structured oracle failed")
    checks = integrity.get("checks")
    if not isinstance(checks, dict) or not checks or not all(value is True for value in checks.values()):
        fail(f"{run_dir.name} exact structured oracle integrity checks are incomplete")


def _load_transport_records(
    run_dir: Path,
    protocol: Mapping[str, Any],
    *,
    code_digest: str,
    protocol_digest: str,
    coordinate_digest: str,
) -> list[dict[str, Any]]:
    config = protocol.get("transport", {})
    if not config.get("enabled", False):
        actual = list((run_dir / "transport").glob("*.json")) if (run_dir / "transport").is_dir() else []
        if actual:
            fail(f"{run_dir.name} contains transport records although transport is disabled")
        return []
    expected = [
        (str(arm), int(pair[0]), int(pair[1]))
        for arm in config["arms"]
        for pair in config["seed_pairs"]
    ]
    records: list[dict[str, Any]] = []
    expected_paths: set[str] = set()
    for arm, source_seed, target_seed in expected:
        path = run_dir / "transport" / f"{arm}_{source_seed}_to_{target_seed}.json"
        expected_paths.add(path.name)
        record = read_json(path)
        identity = (
            record.get("arm"),
            record.get("source_seed"),
            record.get("target_seed"),
            record.get("package_version"),
            record.get("code_digest"),
            record.get("protocol_digest"),
            record.get("coordinate_split_digest"),
        )
        expected_identity = (arm, source_seed, target_seed, VERSION, code_digest, protocol_digest, coordinate_digest)
        assert_equal(identity, expected_identity, f"transport receipt {path.name}")
        metrics = record.get("metrics")
        if not isinstance(metrics, dict) or metrics.get("available") is not True:
            fail(f"transport metrics are unavailable: {path.name}")
        if metrics.get("anchor_coordinate_split") != "train" or metrics.get("test_coordinate_split") != protocol["evaluation"]["coordinate_split"]:
            fail(f"transport coordinate boundary mismatch: {path.name}")
        if metrics.get("anchor_vectors") != int(config["anchor_examples"]):
            fail(f"transport anchor count mismatch: {path.name}")
        by_family = metrics.get("by_family")
        if not isinstance(by_family, dict) or set(by_family) != {"d4", "c8", "mixed_cycle", "random"}:
            fail(f"transport family set mismatch: {path.name}")
        expected_examples = int(config["test_examples"])
        if any(int(item.get("examples", -1)) != expected_examples for item in by_family.values()):
            fail(f"transport per-family evaluation count mismatch: {path.name}")
        baseline_fields = {
            "decode_reembed_state_patch_accuracy",
            "decode_target_reembed_accuracy",
            "shuffled_pair_state_patch_accuracy",
            "random_map_state_patch_accuracy",
            "heldout_hidden_r2",
            "aligned_state_patch_accuracy",
        }
        for family, item in by_family.items():
            if item.get("available") is not True or item.get("coordinate_split") != protocol["evaluation"]["coordinate_split"]:
                fail(f"transport family receipt failed for {path.name}/{family}")
            if not baseline_fields <= set(item):
                fail(f"transport baseline set is incomplete for {path.name}/{family}")
        records.append(record)
    actual_paths = {path.name for path in (run_dir / "transport").glob("*.json")}
    assert_equal(actual_paths, expected_paths, f"{run_dir.name} transport record set")
    return records


def verify_completed_run(
    run_dir: Path,
    frozen_protocol_path: Path,
    *,
    expected_cells: int,
    expected_gate_count: int,
    qualification_must_pass: bool = False,
) -> dict[str, Any]:
    if (run_dir / "RUNNING.json").exists() or (run_dir / "FAILED.json").exists():
        fail(f"{run_dir.name} contains an incomplete-run marker")
    required_outputs = (
        "PROTOCOL.json",
        "RECEIPT.json",
        "AGGREGATE.json",
        "GATES.json",
        "GRID_AUDIT.json",
        "COORDINATE_SPLIT_AUDIT.json",
        "EXACT_ORACLE.json",
        "REPORT.md",
        "summary.csv",
        "heldout_depth_accuracy.png",
        "heldout_operator_geometry.png",
    )
    missing = [name for name in required_outputs if not (run_dir / name).is_file()]
    if missing:
        fail(f"{run_dir.name} is missing required outputs: {missing}")
    if frozen_protocol_path.read_bytes() != (run_dir / "PROTOCOL.json").read_bytes():
        fail(f"{run_dir.name} copied protocol differs from the frozen protocol")
    protocol = read_json(frozen_protocol_path)
    protocol_digest = sha256(frozen_protocol_path)
    code_digest = tree_digest(ROOT, code_files(ROOT))
    coordinate_digest = EXPECTED_COORDINATE_SPLIT_DIGEST
    receipt = read_json(run_dir / "RECEIPT.json")
    expected_identity = (VERSION, protocol["protocol_id"], code_digest, protocol_digest, coordinate_digest)
    observed_identity = (
        receipt.get("package_version"),
        receipt.get("protocol_id"),
        receipt.get("code_digest"),
        receipt.get("protocol_digest"),
        receipt.get("coordinate_split_digest"),
    )
    assert_equal(observed_identity, expected_identity, f"{run_dir.name} receipt provenance")
    if receipt.get("status") != "complete" or receipt.get("grid_complete") is not True:
        fail(f"{run_dir.name} completion receipt failed")
    if receipt.get("exact_oracle_passed") is not True:
        fail(f"{run_dir.name} exact-oracle receipt failed")
    expected_arms = list(protocol["arms"])
    expected_seeds = [int(seed) for seed in protocol["seeds"]]
    assert_equal(receipt.get("arms"), expected_arms, f"{run_dir.name} receipt arms")
    assert_equal(receipt.get("seeds"), expected_seeds, f"{run_dir.name} receipt seeds")
    if len(expected_arms) * len(expected_seeds) != expected_cells:
        fail(f"{run_dir.name} frozen protocol does not define {expected_cells} cells")
    grid = read_json(run_dir / "GRID_AUDIT.json")
    expected_grid = {
        "expected_cells": expected_cells,
        "observed_cells": expected_cells,
        "missing_cells": [],
        "unexpected_cells": [],
        "complete": True,
    }
    assert_equal(grid, expected_grid, f"{run_dir.name} grid audit")
    split = read_json(run_dir / "COORDINATE_SPLIT_AUDIT.json")
    if split.get("passed") is not True or split.get("complete") is not True or split.get("disjoint") is not True:
        fail(f"{run_dir.name} coordinate split audit failed")
    if split.get("digest") != coordinate_digest or any(int(value) != 0 for value in split.get("pairwise_intersections", {}).values()):
        fail(f"{run_dir.name} coordinate split digest or intersections mismatch")
    verify_exact_oracle(
        run_dir,
        code_digest=code_digest,
        protocol_digest=protocol_digest,
        coordinate_digest=coordinate_digest,
    )

    records: dict[str, list[dict[str, Any]]] = {arm: [] for arm in expected_arms}
    expected_record_paths: set[str] = set()
    expected_checkpoint_paths: set[str] = set()
    initial_digests_by_seed: dict[int, set[str]] = {seed: set() for seed in expected_seeds}
    for arm in expected_arms:
        for seed in expected_seeds:
            record_path = run_dir / "arms" / arm / f"seed_{seed}.json"
            checkpoint_path = run_dir / "checkpoints" / arm / f"seed_{seed}.pt"
            if not record_path.is_file() or not checkpoint_path.is_file():
                fail(f"missing {run_dir.name} cell {arm}/{seed}")
            record = read_json(record_path)
            identity = (
                record.get("arm"),
                record.get("seed"),
                record.get("package_version"),
                record.get("protocol_id"),
                record.get("analysis_status"),
                record.get("code_digest"),
                record.get("protocol_digest"),
                record.get("coordinate_split_digest"),
            )
            expected_record_identity = (
                arm,
                seed,
                VERSION,
                protocol["protocol_id"],
                protocol["analysis_status"],
                code_digest,
                protocol_digest,
                coordinate_digest,
            )
            assert_equal(identity, expected_record_identity, f"{run_dir.name} record {arm}/{seed}")
            digest = record.get("initial_tensor_digest")
            if not is_sha256(digest):
                fail(f"{run_dir.name} initial tensor digest is malformed for {arm}/{seed}")
            initial_digests_by_seed[seed].add(digest)
            training = record.get("training")
            if not isinstance(training, dict) or not isinstance(training.get("sampling_audit"), dict):
                fail(f"{run_dir.name} training receipt is missing for {arm}/{seed}")
            verify_training_sampling_audit(
                training["sampling_audit"], protocol, label=f"{run_dir.name}/{arm}/{seed}"
            )
            metrics = record.get("metrics")
            if not isinstance(metrics, dict) or not isinstance(metrics.get("split_conditioned_final_action"), dict):
                fail(f"{run_dir.name} split-conditioned metrics are missing for {arm}/{seed}")
            verify_split_conditioned_receipt(
                metrics["split_conditioned_final_action"],
                protocol,
                label=f"{run_dir.name}/{arm}/{seed}",
            )
            try:
                import torch

                checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
            except Exception as error:
                fail(f"could not safely load checkpoint {checkpoint_path}: {error}")
            if not isinstance(checkpoint, dict) or not isinstance(checkpoint.get("state_dict"), Mapping) or not checkpoint["state_dict"]:
                fail(f"checkpoint has no state dictionary: {checkpoint_path}")
            checkpoint_identity = (
                checkpoint.get("arm"),
                checkpoint.get("seed"),
                checkpoint.get("package_version"),
                checkpoint.get("protocol_id"),
                checkpoint.get("analysis_status"),
                checkpoint.get("code_digest"),
                checkpoint.get("protocol_digest"),
                checkpoint.get("coordinate_split_digest"),
            )
            assert_equal(checkpoint_identity, expected_record_identity, f"{run_dir.name} checkpoint {arm}/{seed}")
            if checkpoint.get("config") != record.get("config"):
                fail(f"checkpoint and record configs differ for {run_dir.name}/{arm}/{seed}")
            for key, value in checkpoint["state_dict"].items():
                if hasattr(value, "is_floating_point") and value.is_floating_point() and not bool(torch.isfinite(value).all()):
                    fail(f"non-finite checkpoint tensor {key} in {run_dir.name}/{arm}/{seed}")
            records[arm].append(record)
            expected_record_paths.add(record_path.relative_to(run_dir).as_posix())
            expected_checkpoint_paths.add(checkpoint_path.relative_to(run_dir).as_posix())
    if any(len(values) != 1 for values in initial_digests_by_seed.values()):
        fail(f"{run_dir.name} arms were not initialized from matched raw tensors by seed")
    actual_records = {path.relative_to(run_dir).as_posix() for path in (run_dir / "arms").glob("*/seed_*.json")}
    actual_checkpoints = {path.relative_to(run_dir).as_posix() for path in (run_dir / "checkpoints").glob("*/seed_*.pt")}
    assert_equal(actual_records, expected_record_paths, f"{run_dir.name} arm record inventory")
    assert_equal(actual_checkpoints, expected_checkpoint_paths, f"{run_dir.name} checkpoint inventory")

    transport_records = _load_transport_records(
        run_dir,
        protocol,
        code_digest=code_digest,
        protocol_digest=protocol_digest,
        coordinate_digest=coordinate_digest,
    )
    assert_equal(receipt.get("transport_records"), len(transport_records), f"{run_dir.name} transport count")
    aggregate = read_json(run_dir / "AGGREGATE.json")
    recomputed_aggregate = _aggregate_all(records, transport_records)
    assert_equal(aggregate, recomputed_aggregate, f"{run_dir.name} recomputed aggregate")
    stored_gates = read_json(run_dir / "GATES.json")
    recomputed_gates = _evaluate_gates(protocol, recomputed_aggregate)
    if len(recomputed_gates) != expected_gate_count:
        fail(f"{run_dir.name} gate count differs from the frozen {expected_gate_count}")
    all_passed = bool(recomputed_gates) and all(bool(item.get("passed")) for item in recomputed_gates.values())
    expected_gate_record = {"all_gates_passed": all_passed, "gates": recomputed_gates}
    assert_equal(stored_gates, expected_gate_record, f"{run_dir.name} recomputed gates")
    expected_status = "pass" if all_passed else "fail"
    assert_equal(receipt.get("scientific_gate_status"), expected_status, f"{run_dir.name} gate status")
    assert_equal(receipt.get("all_gates_passed"), all_passed, f"{run_dir.name} all-gates receipt")
    if qualification_must_pass and not all_passed:
        fail("sealed development qualification no longer passes all eight gates")

    combined_sampling = receipt.get("training_sampling_audit")
    if not isinstance(combined_sampling, dict):
        fail(f"{run_dir.name} combined training sampling audit is missing")
    expected_total = expected_cells * int(protocol["training"]["steps"]) * int(protocol["training"]["batch_size"])
    combined_fields = {
        "cells": expected_cells,
        "word_product_scopes": ["contiguous"],
        "sampling_methods": ["direct_conditioned_uniform"],
        "conditioned_sampler_backends": ["cached_exact_v1"],
        "direct_conditioning_receipts_complete": True,
        "conditioned_sampler_backend_frozen": True,
        "all_fail_closed": True,
        "total_accepted_examples": expected_total,
        "total_candidate_examples": expected_total,
        "total_rejected_examples": 0,
        "total_split_violations": 0,
        "counter_arithmetic_exact": True,
    }
    for key, expected in combined_fields.items():
        assert_equal(combined_sampling.get(key), expected, f"{run_dir.name} combined sampling {key}")
    assert_equal(_normalized_supports(combined_sampling.get("conditioning_supports")), EXPECTED_TRAINING_SUPPORTS, f"{run_dir.name} combined supports")
    return {
        "status": receipt["status"],
        "scientific_gate_status": expected_status,
        "all_gates_passed": all_passed,
        "passed_gates": sum(bool(item["passed"]) for item in recomputed_gates.values()),
        "failed_gates": sum(not bool(item["passed"]) for item in recomputed_gates.values()),
        "gate_count": len(recomputed_gates),
        "arm_seed_cells": expected_cells,
        "training_seeds": len(expected_seeds),
        "transport_pairs": len(transport_records),
        "total_training_examples": expected_total,
        "receipt_sha256": sha256(run_dir / "RECEIPT.json"),
    }


def sparse_audit_summary() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for family in (MONOMIAL_FAMILY, SHEAR_FAMILY):
        record = context_audit_record(family)
        bounded = record["train_closure"]["bounded_within_context_training_support"]
        global_scope = record["train_closure"]["global_train_generator_closure"]
        summary = {
            "catalog_digest": record["digest"],
            "bounded_supported_maps": bounded["unique_supported_map_count"],
            "bounded_contamination": bounded["contamination_counts"],
            "bounded_witness_digest": bounded["witness_digest"],
            "bounded_novelty": bounded["operator_novelty_passed"],
            "global_depth_two_maps": global_scope["unique_depth_two_map_count"],
            "global_contamination": global_scope["contamination_counts"],
            "global_witness_digest": global_scope["witness_digest"],
            "global_all_heldout_witnessed": global_scope["all_heldout_witnessed"],
            "unbounded_novelty": global_scope["operator_novelty_passed"],
        }
        assert_equal(summary, EXPECTED_SPARSE_AUDITS[family], f"sparse {family} closure audit")
        if record["factor_combinations"].get("passed") is not True:
            fail(f"sparse {family} factor-combination split audit failed")
        output[family] = summary
    return output


def verify_reproducibility(primary_protocol_digest: str) -> dict[str, Any]:
    path = REPRODUCIBILITY / "REPRODUCIBILITY.json"
    replay = read_json(path)
    if replay.get("status") != "pass" or replay.get("overall_passed") is not True:
        fail("single-cell reproducibility replay did not pass")
    if (replay.get("package_version"), replay.get("arm"), replay.get("seed")) != (VERSION, "hard_correct", 300):
        fail("single-cell reproducibility replay identity mismatch")
    if replay.get("protocols", {}).get("primary_protocol_sha256") != primary_protocol_digest:
        fail("reproducibility replay primary protocol digest mismatch")
    validation = replay.get("validation")
    required_true = (
        "primary_provenance",
        "replay_provenance",
        "exclusions_symmetric",
        "metrics_exactly_equal",
        "semantic_record_exactly_equal",
        "state_tensor_bytes_equal",
        "state_auxiliary_values_equal",
        "state_sha256_equal",
        "checkpoint_metadata_equal_after_exclusions",
        "canonical_checkpoint_sha256_equal",
    )
    if not isinstance(validation, dict) or any(validation.get(key) is not True for key in required_true):
        fail("single-cell reproducibility replay required checks are incomplete")
    if replay.get("metrics_exactly_equal") is not True or replay.get("metric_difference_count") != 0 or replay.get("mismatches") != []:
        fail("single-cell reproducibility replay compatibility receipt failed")
    if replay.get("max_parameter_absolute_difference") != 0.0:
        fail("single-cell reproducibility replay parameters are not bitwise exact")
    return {
        "status": replay["status"],
        "overall_passed": replay["overall_passed"],
        "arm": replay["arm"],
        "seed": replay["seed"],
        "sha256": sha256(path),
    }


def verify_primary_recovery() -> dict[str, Any]:
    """Validate the bounded recovery ledger for the interrupted primary run."""

    path = PRIMARY / "RECOVERY_EVENTS.json"
    try:
        events = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"could not parse primary recovery events: {error}")
    if not isinstance(events, list) or len(events) != 12:
        fail("primary recovery ledger must contain exactly 12 events")
    expected_sessions = (
        ("resume_paused", 0, 0, 0, 0, 17),
        ("resume_paused", 8, 0, 8, 0, 25),
        ("resume_paused", 8, 0, 8, 0, 33),
        ("resume_paused", 8, 0, 8, 0, 41),
        ("resume_paused", 7, 0, 7, 0, 48),
        ("recovery_complete", 0, 6, 0, 6, 48),
    )
    reason = "execution_supervisor_interrupted_original_runner_without_FAILED_record"
    for index, event in enumerate(events):
        if not isinstance(event, dict) or event.get("reason") != reason:
            fail(f"primary recovery event {index} has invalid provenance")
        if not isinstance(event.get("started_utc"), str) or not isinstance(event.get("pid"), int):
            fail(f"primary recovery event {index} is missing runtime provenance")
    for session_index, expected in enumerate(expected_sessions):
        started = events[2 * session_index]
        finished = events[2 * session_index + 1]
        event_type, max_cells, max_transports, new_cells, new_transports, validated_cells = expected
        assert_equal(started.get("event"), "resume_started", f"primary recovery session {session_index} start event")
        assert_equal(finished.get("event"), event_type, f"primary recovery session {session_index} finish event")
        for key, value in (
            ("max_new_cells", max_cells),
            ("max_new_transports", max_transports),
        ):
            assert_equal(started.get(key), value, f"primary recovery session {session_index} start {key}")
            assert_equal(finished.get(key), value, f"primary recovery session {session_index} finish {key}")
        assert_equal(finished.get("new_cells", 0), new_cells, f"primary recovery session {session_index} new cells")
        assert_equal(finished.get("new_transports", 0), new_transports, f"primary recovery session {session_index} new transports")
        assert_equal(finished.get("validated_cells"), validated_cells, f"primary recovery session {session_index} validated cells")
        for key in ("started_utc", "pid"):
            assert_equal(finished.get(key), started.get(key), f"primary recovery session {session_index} paired {key}")
        if not isinstance(finished.get("finished_utc"), str):
            fail(f"primary recovery session {session_index} is missing finish time")
    return {
        "status": "validated_bounded_recovery",
        "events": len(events),
        "original_completed_cells": 17,
        "recovered_cells": sum(session[3] for session in expected_sessions),
        "transport_pairs": expected_sessions[-1][4],
    }


def verify_posthoc(primary_facts: Mapping[str, Any], primary_protocol: Mapping[str, Any]) -> dict[str, Any]:
    path = PRIMARY / "POSTHOC_DESCRIPTIVE.json"
    markdown = PRIMARY / "POSTHOC_DESCRIPTIVE.md"
    if not markdown.is_file():
        fail("post-hoc descriptive Markdown report is missing")
    posthoc = read_json(path)
    expected_identity = (
        1,
        "komorebi-v0.3-posthoc-seed-paired-bootstrap",
        "posthoc_descriptive_not_preregistered_not_a_frozen_gate",
        "complete",
        primary_protocol["protocol_id"],
        100_000,
    )
    observed_identity = (
        posthoc.get("schema_version"),
        posthoc.get("analysis_id"),
        posthoc.get("analysis_status"),
        posthoc.get("primary_receipt_status"),
        posthoc.get("protocol_id"),
        posthoc.get("replicates_per_contrast_metric"),
    )
    assert_equal(observed_identity, expected_identity, "post-hoc analysis identity")
    provenance = posthoc.get("provenance")
    if not isinstance(provenance, dict):
        fail("post-hoc provenance receipt is missing")
    if provenance.get("protocol_sha256") != EXPECTED_PRIMARY_PROTOCOL_DIGEST:
        fail("post-hoc primary protocol digest mismatch")
    if provenance.get("receipt_sha256") != primary_facts["receipt_sha256"]:
        fail("post-hoc primary receipt digest mismatch")
    if provenance.get("code_digest") != EXPECTED_CODE_DIGEST or provenance.get("coordinate_split_digest") != EXPECTED_COORDINATE_SPLIT_DIGEST:
        fail("post-hoc scientific provenance mismatch")
    inventory = provenance.get("inventory")
    if not isinstance(inventory, list) or len(inventory) != primary_facts["arm_seed_cells"]:
        fail("post-hoc input inventory is incomplete")
    for item in inventory:
        target = PRIMARY / str(item.get("path", ""))
        if not target.is_file() or item.get("sha256") != sha256(target):
            fail(f"post-hoc inventory hash mismatch: {item.get('path')}")
    contrasts = posthoc.get("contrasts")
    if not isinstance(contrasts, list) or not contrasts:
        fail("post-hoc paired contrast set is empty")
    for contrast in contrasts:
        bootstrap = contrast.get("bootstrap", {})
        if bootstrap.get("generator") != "numpy.random.Generator(numpy.random.PCG64)" or bootstrap.get("replicates") != 100_000:
            fail("post-hoc bootstrap generator or replicate count mismatch")
        if not is_sha256(bootstrap.get("seed_sha256")):
            fail("post-hoc bootstrap seed digest is malformed")
    semantic = copy.deepcopy(posthoc)
    expected_payload = semantic.pop("analysis_payload_sha256", None)
    semantic.pop("created_utc", None)
    if expected_payload != canonical_json_sha256(semantic):
        fail("post-hoc analysis payload digest mismatch")
    return {
        "analysis_status": posthoc["analysis_status"],
        "replicates_per_contrast_metric": posthoc["replicates_per_contrast_metric"],
        "contrast_count": len(contrasts),
        "sha256": sha256(path),
    }


def verify_prior_releases() -> list[dict[str, Any]]:
    releases = read_json(ROOT / "PRIOR_RELEASES.json")
    if releases.get("schema") != "komorebi.neuralese.prior_releases.v1":
        fail("prior-release ledger schema mismatch")
    items = releases.get("releases")
    if not isinstance(items, list) or not items:
        fail("prior-release ledger is empty")
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("version"), str):
            fail("prior-release ledger contains a malformed record")
        version = item["version"]
        if version in seen:
            fail(f"duplicate prior release in ledger: {version}")
        seen.add(version)
        relative = Path(str(item.get("archive", "")))
        if relative.is_absolute() or ".." in relative.parts:
            fail(f"unsafe prior-release archive path: {relative}")
        archive = ROOT / relative
        if not archive.is_file() or sha256(archive) != item.get("sha256"):
            fail(f"prior-release archive hash mismatch: {version}")
        output.append({"version": version, "archive": relative.as_posix(), "sha256": item["sha256"]})
    by_version = {item["version"]: item for item in output}
    if by_version.get("0.2.0", {}).get("sha256") != EXPECTED_V02_ARCHIVE_DIGEST:
        fail("the preserved v0.2.0 archive is missing or has the wrong hash")
    return output


def verify_evidence_ledger(primary_facts: Mapping[str, Any], primary_protocol: Mapping[str, Any]) -> str:
    path = ROOT / "EVIDENCE_LEDGER.json"
    ledger = read_json(path)
    if ledger.get("package_version") != VERSION:
        fail("evidence ledger package version mismatch")
    primary = ledger.get("primary")
    if not isinstance(primary, dict):
        fail("evidence ledger primary receipt is missing")
    expected = {
        "analysis_status": primary_protocol["analysis_status"],
        "protocol_id": primary_protocol["protocol_id"],
        "protocol_digest": EXPECTED_PRIMARY_PROTOCOL_DIGEST,
        "code_digest": EXPECTED_CODE_DIGEST,
        "scientific_gate_status": primary_facts["scientific_gate_status"],
        "all_gates_passed": primary_facts["all_gates_passed"],
        "passed_gate_count": primary_facts["passed_gates"],
        "failed_gate_count": primary_facts["failed_gates"],
        "arm_seed_cells": primary_facts["arm_seed_cells"],
        "training_seeds": primary_facts["training_seeds"],
        "transport_pairs": primary_facts["transport_pairs"],
    }
    for key, value in expected.items():
        assert_equal(primary.get(key), value, f"evidence ledger primary {key}")
    claims = ledger.get("claims")
    if not isinstance(claims, list) or not claims:
        fail("evidence ledger contains no claim records")
    for claim in claims:
        evidence = claim.get("evidence") if isinstance(claim, dict) else None
        if not isinstance(evidence, list) or not evidence:
            fail("evidence ledger claim is missing evidence paths")
        for relative_text in evidence:
            relative = Path(str(relative_text))
            if relative.is_absolute() or ".." in relative.parts or not (ROOT / relative).exists():
                fail(f"evidence ledger path is unsafe or missing: {relative_text}")
    return sha256(path)


def verify_frozen_inputs() -> dict[str, Any]:
    if VERSION != EXPECTED_VERSION:
        fail(f"package module version is {VERSION}, expected {EXPECTED_VERSION}")
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if project.get("project", {}).get("version") != VERSION:
        fail("pyproject and package module version disagree")
    scientific_files = code_files(ROOT)
    code_digest = tree_digest(ROOT, scientific_files)
    assert_equal(len(scientific_files), EXPECTED_CODE_FILES, "scientific code file count")
    assert_equal(code_digest, EXPECTED_CODE_DIGEST, "scientific code digest")
    hashes = {
        "primary_protocol": sha256(PRIMARY_PROTOCOL),
        "primary_seal": sha256(PRIMARY_SEAL),
        "qualification_protocol": sha256(QUALIFICATION_PROTOCOL),
        "qualification_receipt": sha256(QUALIFICATION / "RECEIPT.json"),
    }
    expected_hashes = {
        "primary_protocol": EXPECTED_PRIMARY_PROTOCOL_DIGEST,
        "primary_seal": EXPECTED_PRIMARY_SEAL_DIGEST,
        "qualification_protocol": EXPECTED_QUALIFICATION_PROTOCOL_DIGEST,
        "qualification_receipt": EXPECTED_QUALIFICATION_RECEIPT_DIGEST,
    }
    assert_equal(hashes, expected_hashes, "sealed input digests")
    primary_protocol = read_json(PRIMARY_PROTOCOL)
    qualification_protocol = read_json(QUALIFICATION_PROTOCOL)
    for label, protocol in (("primary", primary_protocol), ("qualification", qualification_protocol)):
        if protocol.get("package_version") != VERSION or protocol.get("expected_code_digest") != code_digest:
            fail(f"{label} protocol version or code digest mismatch")
        if protocol.get("expected_coordinate_split_digest") != EXPECTED_COORDINATE_SPLIT_DIGEST:
            fail(f"{label} protocol coordinate split digest mismatch")
        if protocol.get("training", {}).get("word_product_scope") != "contiguous" or protocol.get("training", {}).get("conditioned_sampler_backend") != "cached_exact_v1":
            fail(f"{label} protocol does not freeze strict contiguous-path direct sampling")
    split = audit_coordinate_splits()
    if split.passed is not True or split.digest != EXPECTED_COORDINATE_SPLIT_DIGEST:
        fail("recomputed coordinate split audit failed")
    seal = read_json(PRIMARY_SEAL)
    seal_expected = {
        "status": "sealed_before_primary_test_execution",
        "package_version": VERSION,
        "primary_protocol_path": "protocols/V0_3_STAGE_A_PRIMARY.json",
        "primary_protocol_sha256": EXPECTED_PRIMARY_PROTOCOL_DIGEST,
        "scientific_code_sha256": EXPECTED_CODE_DIGEST,
        "scientific_code_files": EXPECTED_CODE_FILES,
        "coordinate_split_sha256": EXPECTED_COORDINATE_SPLIT_DIGEST,
        "primary_test_coordinate_split": "test",
        "primary_expected_cells": 48,
        "primary_frozen_gates": 26,
        "qualification_receipt_path": "results/v0.3.0/stage_a_qualification_v3/RECEIPT.json",
        "qualification_receipt_sha256": EXPECTED_QUALIFICATION_RECEIPT_DIGEST,
        "qualification_protocol_sha256": EXPECTED_QUALIFICATION_PROTOCOL_DIGEST,
        "qualification_all_gates_passed": True,
        "qualification_observed_cells": 16,
        "primary_output_path": "results/v0.3.0/stage_a_primary_v3",
        "primary_output_absent_at_seal": True,
        "test_coordinates_opened_before_seal": False,
    }
    for key, expected in seal_expected.items():
        assert_equal(seal.get(key), expected, f"primary seal {key}")
    return {"code_digest": code_digest, "code_files": len(scientific_files), **hashes}


def release_facts() -> dict[str, Any]:
    """Validate all non-manifest release evidence and return manifest facts."""

    verify_no_forbidden_artifacts()
    verify_current_documents()
    frozen = verify_frozen_inputs()
    qualification = verify_completed_run(
        QUALIFICATION,
        QUALIFICATION_PROTOCOL,
        expected_cells=16,
        expected_gate_count=8,
        qualification_must_pass=True,
    )
    primary_protocol = read_json(PRIMARY_PROTOCOL)
    primary = verify_completed_run(
        PRIMARY,
        PRIMARY_PROTOCOL,
        expected_cells=48,
        expected_gate_count=26,
    )
    recovery = verify_primary_recovery()
    reproducibility = verify_reproducibility(EXPECTED_PRIMARY_PROTOCOL_DIGEST)
    posthoc = verify_posthoc(primary, primary_protocol)
    sparse = sparse_audit_summary()
    prior_releases = verify_prior_releases()
    ledger_sha = verify_evidence_ledger(primary, primary_protocol)
    return {
        "scientific_code_digest": frozen["code_digest"],
        "scientific_code_files": frozen["code_files"],
        "coordinate_split_digest": EXPECTED_COORDINATE_SPLIT_DIGEST,
        "protocols": {
            "primary_sha256": frozen["primary_protocol"],
            "primary_seal_sha256": frozen["primary_seal"],
            "qualification_sha256": frozen["qualification_protocol"],
            "qualification_receipt_sha256": frozen["qualification_receipt"],
        },
        "qualification_outcome": qualification,
        "primary_outcome": primary,
        "primary_recovery": recovery,
        "reproducibility": reproducibility,
        "posthoc": posthoc,
        "sparse_stage_b_audits": sparse,
        "evidence_ledger_sha256": ledger_sha,
        "prior_releases": prior_releases,
        "verification_requirements": {
            "minimum_test_count": MINIMUM_TESTS,
            "scientific_gate_policy": "recomputed_outcome_must_match; individual primary gates may pass or fail",
            "forbidden_incomplete_markers": sorted(FORBIDDEN_FILE_NAMES),
        },
    }


def verify_checksums() -> None:
    path = ROOT / "SHA256SUMS.txt"
    if not path.is_file():
        fail("SHA256SUMS.txt is missing")
    records: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, relative_text = line.split("  ", 1)
        except ValueError:
            fail("malformed checksum line")
        relative = Path(relative_text)
        if relative.is_absolute() or ".." in relative.parts or relative_text in records:
            fail(f"unsafe or duplicate checksum path: {relative_text}")
        if not is_sha256(expected):
            fail(f"malformed checksum digest: {relative_text}")
        target = ROOT / relative
        if not target.is_file() or sha256(target) != expected:
            fail(f"checksum mismatch: {relative_text}")
        records[relative_text] = expected
    expected_paths = included_files(include_manifest=True)
    if set(records) != expected_paths:
        fail(
            "checksum inventory mismatch: "
            f"missing={sorted(expected_paths - set(records))}, "
            f"extra={sorted(set(records) - expected_paths)}"
        )


def verify_manifest(facts: Mapping[str, Any]) -> dict[str, Any]:
    manifest = read_json(ROOT / "MANIFEST.json")
    if manifest.get("schema") != "komorebi.neuralese.package_manifest.v3" or manifest.get("version") != VERSION:
        fail("manifest schema or version mismatch")
    for key, expected in facts.items():
        assert_equal(manifest.get(key), expected, f"manifest {key}")
    records = manifest.get("files")
    if not isinstance(records, list) or manifest.get("file_count") != len(records):
        fail("manifest file count mismatch")
    observed: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            fail("manifest contains a non-object file record")
        relative_text = str(record.get("path", ""))
        relative = Path(relative_text)
        if not relative_text or relative.is_absolute() or ".." in relative.parts or relative_text in observed:
            fail(f"manifest contains an unsafe or duplicate path: {relative_text}")
        target = ROOT / relative
        if not target.is_file() or target.stat().st_size != record.get("size") or sha256(target) != record.get("sha256"):
            fail(f"manifest record mismatch: {relative_text}")
        observed.add(relative_text)
    assert_equal(observed, included_files(include_manifest=False), "manifest payload inventory")
    return manifest


def run_test_suite() -> int:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", str(ROOT / "tests")]
    completed = subprocess.run(command, cwd=ROOT, env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = completed.stdout.strip()
    if output:
        print(output)
    if completed.returncode != 0:
        fail(f"test suite failed with exit code {completed.returncode}")
    matches = re.findall(r"(\d+) passed", output)
    if not matches:
        fail("could not recover the passed-test count from pytest output")
    count = int(matches[-1])
    if count < MINIMUM_TESTS:
        fail(f"only {count} tests passed; at least {MINIMUM_TESTS} are required")
    return count


def run_analysis_tool_self_checks() -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for relative in ("analysis_tools/replay_verifier.py", "analysis_tools/paired_bootstrap.py"):
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / relative), "--self-check"],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if completed.stdout.strip():
            print(completed.stdout.strip())
        if completed.returncode != 0:
            fail(f"analysis-tool self-check failed: {relative}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(list(argv) if argv is not None else None)
    try:
        facts = release_facts()
        verify_checksums()
        manifest = verify_manifest(facts)
        tests = run_test_suite()
        run_analysis_tool_self_checks()
    except PackageVerificationError as error:
        print(f"PACKAGE_VERIFY_FAIL: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "PACKAGE_VERIFY_PASS",
                "version": VERSION,
                "scientific_code_digest": facts["scientific_code_digest"],
                "files": manifest["file_count"],
                "tests_passed": tests,
                "primary": facts["primary_outcome"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
