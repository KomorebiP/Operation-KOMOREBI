#!/usr/bin/env python3
"""Validate and seal the v0.3.2 release without touching frozen artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import os
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

# The scan below is intentionally open to inherited lineage material, while this
# independent inventory prevents a reduced release from being silently sealed.
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


def validate_registered_artifacts(root: Path) -> None:
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
        not (root / "results/V031_RUN_STARTED.json").exists(),
        "unexpected v0.3.1 run ledger",
    )
    require(
        not (root / "results/V031_ENTRY_CONE_HOLONOMY_RESULTS.json").exists(),
        "unexpected v0.3.1 result",
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
        "run-start ledger identity or digest chain mismatch",
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
    require(
        result.get("integrity_gates") == EXPECTED_GATES,
        "registered integrity gate map mismatch",
    )
    integrity = result.get("integrity", {})
    require(
        integrity.get("execution_freeze", {}).get("freeze_sha256")
        == FIXED_DIGESTS[V032_FREEZE]
        and integrity.get("run_started_ledger", {}).get("sha256")
        == FIXED_DIGESTS[LEDGER]
        and integrity.get("v031_abort_evidence", {}).get("invalid_attempt_sha256")
        == FIXED_DIGESTS[V031_ABORT],
        "registered result digest chain mismatch",
    )


def validate_analysis_receipt(root: Path) -> None:
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
    require(isinstance(artifacts, dict), "analysis artifact map is missing")
    require(
        set(artifacts) == EXPECTED_ANALYSIS_ARTIFACTS,
        "analysis artifact inventory mismatch",
    )
    for relative, record in artifacts.items():
        path = safe_file(root, relative)
        require(
            path.stat().st_size == record.get("size_bytes"),
            f"analysis artifact size mismatch: {relative}",
        )
        require(
            sha256(path) == record.get("sha256"),
            f"analysis artifact hash mismatch: {relative}",
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


def eligible_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise RuntimeError(f"release must not contain symlink: {relative}")
        if path.is_dir():
            if path.name == "__pycache__":
                raise RuntimeError(f"release must not contain cache: {relative}")
            continue
        if path.name in {MANIFEST, CHECKSUMS}:
            continue
        if path.suffix == ".pyc" or path.name.startswith(".") or path.name.endswith(".tmp"):
            raise RuntimeError(f"release contains transient file: {relative}")
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    root = Path(__file__).resolve().parent
    for relative in REQUIRED_RELEASE_FILES:
        safe_file(root, relative)
    validate_registered_artifacts(root)
    validate_analysis_receipt(root)
    files = eligible_files(root)
    records = {
        path.relative_to(root).as_posix(): {
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
        }
        for path in files
    }
    require(
        REQUIRED_RELEASE_FILES <= set(records),
        "required release inventory is incomplete",
    )
    manifest = {
        "schema": "komorebi.neuralese.entry_cone_holonomy.release_manifest.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "RELEASE_INTEGRITY_COMPLETE",
        "scientific_design_version": "0.3.1",
        "correction_runner_version": VERSION,
        "registered_result": {"path": RESULT, "sha256": FIXED_DIGESTS[RESULT]},
        "fixed_digest_anchors": FIXED_DIGESTS,
        "required_release_inventory": sorted(REQUIRED_RELEASE_FILES),
        "analysis_artifact_inventory": sorted(EXPECTED_ANALYSIS_ARTIFACTS),
        "integrity_gate_contract": EXPECTED_GATES,
        "file_count": len(records),
        "total_manifested_bytes": sum(
            record["size_bytes"] for record in records.values()
        ),
        "files": records,
        "exclusions": [
            "V032_RELEASE_MANIFEST.json (self)",
            "V032_SHA256SUMS.txt (self-referential checksum impossible)",
        ],
    }
    atomic_write(
        root / MANIFEST,
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    checksum_paths = files + [root / MANIFEST]
    checksum_lines = [
        f"{sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(
            checksum_paths, key=lambda path: path.relative_to(root).as_posix()
        )
    ]
    atomic_write(root / CHECKSUMS, "\n".join(checksum_lines) + "\n")
    print(f"MANIFEST={root / MANIFEST}")
    print(f"MANIFEST_SHA256={sha256(root / MANIFEST)}")
    print(f"FILE_COUNT={len(records)}")
    print(f"TOTAL_MANIFESTED_BYTES={manifest['total_manifested_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
