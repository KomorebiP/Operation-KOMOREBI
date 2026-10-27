#!/usr/bin/env python3
"""Strict read-only verifier for the Neuralese v0.3.2 release."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


AUTHOR = "Komorebi P."
VERSION = "0.3.2"
MANIFEST = "V032_RELEASE_MANIFEST.json"
CHECKSUMS = "V032_SHA256SUMS.txt"
RESULT = "results/V032_ENTRY_CONE_HOLONOMY_RESULTS.json"
LEDGER = "results/V032_RUN_STARTED.json"
V032_FREEZE = "v032/V032_EXECUTION_FREEZE.json"
V031_FREEZE = "v031/V031_EXECUTION_FREEZE.json"
V031_ABORT = "results/V031_INVALID_ATTEMPT.json"
ANALYSIS_RECEIPT = "V032_ANALYSIS_COMPLETE.json"
POSTHOC_SUMMARY = "results/V032_POSTHOC_SUMMARY.json"

FIXED_DIGESTS = {
    V032_FREEZE: "82e6fcb66b6f8b905643c11ef0df08eaa6e0fda6f77b6e720231088504b40519",
    LEDGER: "7e6307886267ea1359cb110fc84839df135abd22343083fe3ee665c41bb55fd2",
    RESULT: "134135524c0b7017c4611ce385b3853fc33d8d883d1716e60f3f6aa1c9ffba5c",
    V031_FREEZE: "2600536f3009ed4294bad0432680021915d2b17a15fe6ab973bd835061f7f662",
    V031_ABORT: "e72b827ba30f7f3d16a5ff8837c5cec5716ebc20914982e98944c417db785f64",
}

EXPECTED_GATES = {
    "B0_all_base_transversal_cases_are_H8_eligible": True,
    "E0_source_input_and_numeric_integrity": True,
    "K1_direct_and_recursive_suffix_audits_agree": True,
    "M0_all_same_endpoint_shallow_baselines_are_H8_eligible": True,
    "M1_exact_12_plus_48_bank_executed": True,
    "P0_grouped_products_reproduce_stepwise_rays": True,
    "lineage_integrity": True,
}

EXPECTED_ANALYSIS_ARTIFACTS = {
    "figures/V032_IDENTITY_PATH_DISAGREEMENTS.png",
    "figures/V032_MATCHED_CLASSIFICATIONS.png",
    "figures/V032_MATCHED_LEX_COMPARISON.png",
    "figures/V032_RELATION_EXIT_BY_CHECKPOINT.png",
    "figures/V032_RELATION_EXIT_PROFILE.png",
    "results/V032_MATCHED_CLASSIFICATIONS.csv",
    "results/V032_POSTHOC_SUMMARY.json",
    "results/V032_RELATION_PROFILE.csv",
    "results/V032_RELATION_PROFILE_BY_CHECKPOINT.csv",
}

REQUIRED_RELEASE_FILES = {
    "README.md",
    "RESULTS_SUMMARY.md",
    "CLAIM_BOUNDARY.md",
    "NEXT_BLOCK.md",
    "REVISION_LOG.md",
    "V032_README.md",
    "V032_RESULTS_SUMMARY.md",
    "V032_CLAIM_BOUNDARY.md",
    "V032_NEXT_BLOCK.md",
    "V032_REVISION_LOG.md",
    ANALYSIS_RECEIPT,
    "posthoc_v032.py",
    "build_v032_release.py",
    "verify_v032_release.py",
    "requirements-posthoc.txt",
    V032_FREEZE,
    "v032/V032_ABORT_DISCLOSURE.json",
    "v032/V032_PREREGISTRATION.json",
    "v032/V032_RESEARCH_SPEC.md",
    "v032/run_v032.py",
    "v032/test_v032_contract.py",
    V031_FREEZE,
    V031_ABORT,
    LEDGER,
    RESULT,
    *EXPECTED_ANALYSIS_ARTIFACTS,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in output, f"duplicate JSON key: {key}")
        output[key] = value
    return output


def finite_float(value: str) -> float:
    parsed = float(value)
    require(math.isfinite(parsed), f"non-finite JSON float: {value}")
    return parsed


def strict_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=no_duplicate_object,
        parse_float=finite_float,
        parse_constant=lambda value: (_ for _ in ()).throw(
            RuntimeError(f"non-finite JSON constant: {value}")
        ),
    )


def safe_file(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and relative, "empty release path")
    candidate_relative = Path(relative)
    require(not candidate_relative.is_absolute(), f"absolute path rejected: {relative}")
    require(".." not in candidate_relative.parts, f"parent traversal rejected: {relative}")
    require(candidate_relative.as_posix() == relative, f"noncanonical path rejected: {relative}")
    candidate = (root / candidate_relative).resolve()
    require(candidate.is_relative_to(root), f"path escapes release root: {relative}")
    require(candidate.is_file() and not candidate.is_symlink(), f"missing file: {relative}")
    return candidate


def actual_release_files(root: Path) -> set[str]:
    output = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        require(not path.is_symlink(), f"unexpected symlink: {relative}")
        if path.is_dir():
            require(path.name != "__pycache__", f"unexpected cache: {relative}")
            continue
        require(
            path.suffix != ".pyc"
            and not path.name.startswith(".")
            and not path.name.endswith(".tmp"),
            f"unexpected transient file: {relative}",
        )
        output.add(relative)
    return output


def validate_frozen_maps(root: Path) -> None:
    v032 = strict_json(safe_file(root, V032_FREEZE))
    require(
        (
            v032.get("schema"),
            v032.get("version"),
            v032.get("author"),
            v032.get("status"),
        )
        == (
            "komorebi.neuralese.entry_cone_holonomy.correction_execution_freeze.v1",
            VERSION,
            AUTHOR,
            "FROZEN_BEFORE_V032_LEARNED_ENDPOINT_EXECUTION",
        ),
        "v0.3.2 freeze identity mismatch",
    )
    require(len(v032.get("files", {})) == 11, "v0.3.2 frozen map count mismatch")
    for relative, digest in v032["files"].items():
        require(
            sha256(safe_file(root, relative)) == digest,
            f"v0.3.2 frozen byte changed: {relative}",
        )
    require(
        v032.get("v031_execution_freeze_sha256") == FIXED_DIGESTS[V031_FREEZE]
        and v032.get("v031_invalid_attempt_sha256") == FIXED_DIGESTS[V031_ABORT],
        "v0.3.2 inherited digest pins changed",
    )

    v031 = strict_json(safe_file(root, V031_FREEZE))
    require(
        (
            v031.get("schema"),
            v031.get("version"),
            v031.get("author"),
            v031.get("status"),
        )
        == (
            "komorebi.neuralese.entry_cone_holonomy.execution_freeze.v1",
            "0.3.1",
            AUTHOR,
            "FROZEN_BEFORE_FRESH_LEARNED_ENDPOINT_EXECUTION",
        ),
        "v0.3.1 freeze identity mismatch",
    )
    require(len(v031.get("files", {})) == 27, "v0.3.1 frozen map count mismatch")
    for relative, digest in v031["files"].items():
        require(
            sha256(safe_file(root, relative)) == digest,
            f"v0.3.1 frozen byte changed: {relative}",
        )


def validate_internal_records(root: Path) -> None:
    for relative, digest in FIXED_DIGESTS.items():
        require(
            sha256(safe_file(root, relative)) == digest,
            f"fixed digest mismatch: {relative}",
        )
    require(
        not (root / "results/V032_INVALID_ATTEMPT.json").exists(),
        "unexpected v0.3.2 invalid-attempt artifact",
    )
    require(
        not (root / "results/V031_RUN_STARTED.json").exists()
        and not (root / "results/V031_ENTRY_CONE_HOLONOMY_RESULTS.json").exists(),
        "unexpected v0.3.1 success artifact",
    )
    validate_frozen_maps(root)

    ledger = strict_json(safe_file(root, LEDGER))
    require(
        ledger.get("schema") == "komorebi.neuralese.entry_cone_holonomy.run_started.v2"
        and ledger.get("version") == VERSION
        and ledger.get("author") == AUTHOR
        and ledger.get("status") == "CREATED_BEFORE_LEARNED_CHECKPOINT_LOADING"
        and ledger.get("execution_freeze_sha256") == FIXED_DIGESTS[V032_FREEZE]
        and ledger.get("v031_execution_freeze_sha256") == FIXED_DIGESTS[V031_FREEZE]
        and ledger.get("v031_abort_evidence_sha256") == FIXED_DIGESTS[V031_ABORT],
        "run-start ledger mismatch",
    )

    result = strict_json(safe_file(root, RESULT))
    require(
        result.get("schema") == "komorebi.neuralese.entry_cone_holonomy.result.v1"
        and result.get("version") == VERSION
        and result.get("correction_runner_version") == VERSION
        and result.get("scientific_design_version") == "0.3.1"
        and result.get("author") == AUTHOR
        and result.get("status") == "REGISTERED_EXECUTION_COMPLETE",
        "registered result identity mismatch",
    )
    require(result.get("integrity_gates") == EXPECTED_GATES, "integrity gate contract mismatch")
    require(
        result.get("integrity", {}).get("execution_freeze", {}).get("freeze_sha256")
        == FIXED_DIGESTS[V032_FREEZE]
        and result.get("integrity", {}).get("run_started_ledger", {}).get("sha256")
        == FIXED_DIGESTS[LEDGER]
        and result.get("integrity", {}).get("v031_abort_evidence", {}).get("invalid_attempt_sha256")
        == FIXED_DIGESTS[V031_ABORT],
        "registered result digest chain mismatch",
    )

    receipt = strict_json(safe_file(root, ANALYSIS_RECEIPT))
    require(
        receipt.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.analysis_complete.v1"
        and receipt.get("version") == VERSION
        and receipt.get("author") == AUTHOR
        and receipt.get("status") == "POSTHOC_ANALYSIS_COMPLETE"
        and receipt.get("analysis_class") == "deterministic_posthoc_derivation"
        and receipt.get("scientific_mutation") == "none"
        and receipt.get("checkpoint_deserialization") == "not_performed"
        and receipt.get("learned_endpoint_execution") == "not_performed",
        "analysis receipt identity mismatch",
    )
    require(
        receipt.get("registered_result")
        == {"path": RESULT, "sha256": FIXED_DIGESTS[RESULT]},
        "analysis receipt result anchor mismatch",
    )
    artifacts = receipt.get("artifacts")
    require(
        isinstance(artifacts, dict)
        and set(artifacts) == EXPECTED_ANALYSIS_ARTIFACTS,
        "analysis artifact inventory mismatch",
    )
    for relative, record in artifacts.items():
        path = safe_file(root, relative)
        require(
            path.stat().st_size == record.get("size_bytes")
            and sha256(path) == record.get("sha256"),
            f"analysis artifact mismatch: {relative}",
        )
    summary = strict_json(safe_file(root, POSTHOC_SUMMARY))
    require(
        summary.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.posthoc_summary.v1"
        and summary.get("version") == VERSION
        and summary.get("author") == AUTHOR
        and summary.get("source", {}).get("path") == RESULT
        and summary.get("source", {}).get("sha256") == FIXED_DIGESTS[RESULT],
        "posthoc summary result link mismatch",
    )


def main() -> int:
    root = Path(__file__).resolve().parent
    manifest = strict_json(safe_file(root, MANIFEST))
    require(
        set(manifest)
        == {
            "analysis_artifact_inventory",
            "author",
            "correction_runner_version",
            "exclusions",
            "file_count",
            "files",
            "fixed_digest_anchors",
            "integrity_gate_contract",
            "registered_result",
            "required_release_inventory",
            "schema",
            "scientific_design_version",
            "status",
            "total_manifested_bytes",
            "version",
        },
        "manifest top-level shape mismatch",
    )
    require(
        manifest.get("schema")
        == "komorebi.neuralese.entry_cone_holonomy.release_manifest.v1"
        and manifest.get("version") == VERSION
        and manifest.get("author") == AUTHOR
        and manifest.get("status") == "RELEASE_INTEGRITY_COMPLETE"
        and manifest.get("scientific_design_version") == "0.3.1"
        and manifest.get("correction_runner_version") == VERSION,
        "manifest identity mismatch",
    )
    require(
        manifest.get("registered_result")
        == {"path": RESULT, "sha256": FIXED_DIGESTS[RESULT]},
        "manifest result anchor mismatch",
    )
    require(manifest.get("fixed_digest_anchors") == FIXED_DIGESTS, "manifest fixed anchors mismatch")
    require(manifest.get("integrity_gate_contract") == EXPECTED_GATES, "manifest gate contract mismatch")
    require(
        manifest.get("required_release_inventory") == sorted(REQUIRED_RELEASE_FILES)
        and manifest.get("analysis_artifact_inventory")
        == sorted(EXPECTED_ANALYSIS_ARTIFACTS),
        "manifest independent inventory mismatch",
    )
    require(
        manifest.get("exclusions")
        == [
            "V032_RELEASE_MANIFEST.json (self)",
            "V032_SHA256SUMS.txt (self-referential checksum impossible)",
        ],
        "manifest exclusions mismatch",
    )

    records = manifest.get("files")
    require(isinstance(records, dict), "manifest files map is missing")
    require(RESULT in records, "canonical result is absent from manifest records")
    require(REQUIRED_RELEASE_FILES <= set(records), "required release file absent")
    expected_files = set(records) | {MANIFEST, CHECKSUMS}
    require(actual_release_files(root) == expected_files, "release file set mismatch")
    for relative, record in records.items():
        path = safe_file(root, relative)
        require(
            path.stat().st_size == record.get("size_bytes"),
            f"manifest size mismatch: {relative}",
        )
        require(
            sha256(path) == record.get("sha256"),
            f"manifest digest mismatch: {relative}",
        )
    require(len(records) == manifest.get("file_count"), "manifest file count mismatch")
    require(
        sum(record["size_bytes"] for record in records.values())
        == manifest.get("total_manifested_bytes"),
        "manifest byte total mismatch",
    )

    checksum_entries = {}
    for line in safe_file(root, CHECKSUMS).read_text(encoding="utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        require(separator and relative not in checksum_entries, f"bad checksum line: {line}")
        safe_file(root, relative)
        checksum_entries[relative] = digest
    require(
        set(checksum_entries) == set(records) | {MANIFEST},
        "checksum inventory mismatch",
    )
    for relative, digest in checksum_entries.items():
        require(sha256(safe_file(root, relative)) == digest, f"checksum mismatch: {relative}")

    validate_internal_records(root)
    print("V032_RELEASE_VERIFICATION=PASS")
    print(f"AUTHOR={AUTHOR}")
    print(f"VERSION={VERSION}")
    print(f"FILE_COUNT={len(records)}")
    print(f"RESULT_SHA256={FIXED_DIGESTS[RESULT]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
