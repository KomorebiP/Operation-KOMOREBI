#!/usr/bin/env python3
"""Offline integrity and finite-evidence verifier for the Core 0.5 package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


EXPECTED_SCHEMA = "osl.core05.release-manifest.v1"
EXPECTED_RELEASE = "OSL-Core 0.5 Semantic Independence v0.1.0"
GENERATED_NAMES = {
    "MANIFEST.json",
    "SHA256SUMS",
    ".MANIFEST.json.core05.tmp",
    ".SHA256SUMS.core05.tmp",
}
EXCLUDED_PARTS = {
    ".core05_venv",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    ".git",
    ".svn",
    "htmlcov",
}
TRANSIENT_NAMES = {".coverage", "coverage.xml", ".DS_Store"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo", ".tmp", ".part"}
EXCLUDED_TOP_LEVEL = {"tmp"}
OUTPUT_TRANSIENT_PARTS = {"tmp", "_tmp", "render", "renders", "_render"}
REQUIRED_RELEASE_PATHS = {
    "output/pdf/OSL_Core_0.5_Semantic_Independence_Technical_Update.pdf",
    "reference/build_core05_pdf.py",
}
EXCLUDED_RELATIVE_PATHS = {
    "verify_core04.sh",
    "verify_core04.ps1",
    "reference/build_core04_manifest.py",
    "reference/build_core04_archive.py",
    "reference/generate_core04_evidence.py",
    "reference/generate_core04_bridge_report.py",
    "reference/generate_core04_adversarial_report.py",
    "reference/verify_core04_package.py",
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def excluded(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    if relative.as_posix() in EXCLUDED_RELATIVE_PATHS:
        return True
    if relative.parts and relative.parts[0] in EXCLUDED_TOP_LEVEL:
        return True
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return True
    if path.name in GENERATED_NAMES or path.name in TRANSIENT_NAMES:
        return True
    if path.name == f"{root.name}.zip":
        return True
    if (
        relative.parts
        and relative.parts[0] == "output"
        and any(part in OUTPUT_TRANSIENT_PARTS for part in relative.parts[1:])
    ):
        return True
    return path.suffix.lower() in TRANSIENT_SUFFIXES


def expected_package_paths(root: Path) -> tuple[list[str], list[str]]:
    paths = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
    symlinks = [
        path.relative_to(root).as_posix()
        for path in paths
        if not excluded(root, path) and path.is_symlink()
    ]
    files = [
        path.relative_to(root).as_posix()
        for path in paths
        if not excluded(root, path) and not path.is_symlink() and path.is_file()
    ]
    return files, symlinks


def load_json(path: Path, failures: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.append(f"json:{path.name}:{type(exc).__name__}")
        return None
    if not isinstance(value, dict):
        failures.append(f"json:{path.name}:not_object")
        return None
    return value


def expect_fields(
    filename: str,
    report: dict[str, Any] | None,
    expected: dict[str, Any],
    failures: list[str],
) -> None:
    if report is None:
        return
    for key, value in expected.items():
        if report.get(key) != value:
            failures.append(f"evidence:{filename}:{key}")


def verify_embedded_digest(
    filename: str,
    report: dict[str, Any] | None,
    field: str,
    failures: list[str],
) -> None:
    if report is None:
        return
    unsigned = dict(report)
    observed = unsigned.pop(field, None)
    if not isinstance(observed, str) or observed != digest(unsigned):
        failures.append(f"evidence:{filename}:{field}")


def verify_trace_bundle(root: Path, failures: list[str]) -> dict[str, Any]:
    path = root / "CORE05_TRACE_BUNDLE.jsonl"
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, 1):
                if not raw.endswith("\n"):
                    failures.append(f"trace:newline:{line_number}")
                text = raw.strip()
                if not text:
                    failures.append(f"trace:empty_line:{line_number}")
                    continue
                try:
                    value = json.loads(text)
                except json.JSONDecodeError:
                    failures.append(f"trace:json:{line_number}")
                    continue
                if not isinstance(value, dict):
                    failures.append(f"trace:not_object:{line_number}")
                    continue
                records.append(value)
    except (OSError, UnicodeError) as exc:
        failures.append(f"trace:read:{type(exc).__name__}")
        return {"record_count": 0, "sha256": None}

    if len(records) != 66:
        failures.append("trace:record_count")
    seen_files: set[str] = set()
    for index, record in enumerate(records):
        if record.get("schema") != "osl.core05.source-bound-trace.v1":
            failures.append(f"trace:schema:{index}")
        if record.get("language_version") != "OSL-Core 0.5":
            failures.append(f"trace:language_version:{index}")
        if record.get("evidence_profile") != "v0.5-semantic-independence":
            failures.append(f"trace:evidence_profile:{index}")
        if record.get("verification_status") != "V05_SEMANTIC_INDEPENDENCE_VERIFIED":
            failures.append(f"trace:verification_status:{index}")
        filename = record.get("file")
        if not isinstance(filename, str) or filename in seen_files:
            failures.append(f"trace:file:{index}")
        else:
            seen_files.add(filename)
        unsigned = dict(record)
        observed_digest = unsigned.pop("record_digest", None)
        if observed_digest != digest(unsigned):
            failures.append(f"trace:record_digest:{index}")
        base = record.get("base_kernel_report")
        semantic = record.get("semantic_independence_report")
        if not isinstance(base, dict) or base.get("independent_checks_pass") is not True:
            failures.append(f"trace:base_kernel:{index}")
        if (
            not isinstance(semantic, dict)
            or semantic.get("independent_checks_pass") is not True
        ):
            failures.append(f"trace:semantic_independence:{index}")
        receipts = record.get("receipts")
        if not isinstance(receipts, list) or not receipts:
            failures.append(f"trace:receipts:{index}")
            continue
        for receipt_index, receipt in enumerate(receipts):
            if not isinstance(receipt, dict):
                failures.append(f"trace:receipt_object:{index}:{receipt_index}")
                continue
            if receipt.get("schema") != "osl.core.receipt.v2":
                failures.append(f"trace:receipt_schema:{index}:{receipt_index}")
            if receipt.get("core_version") != "0.5":
                failures.append(f"trace:receipt_version:{index}:{receipt_index}")
        if receipts[-1].get("kind") not in {"program_complete", "program_reject"}:
            failures.append(f"trace:terminal:{index}")

    return {"record_count": len(records), "sha256": sha256(path)}


def verify_evidence(root: Path, failures: list[str]) -> None:
    conformance_name = "CORE05_CONFORMANCE_REPORT.json"
    conformance = load_json(root / conformance_name, failures)
    expect_fields(
        conformance_name,
        conformance,
        {
            "schema": "osl.core05.conformance-suite.v1",
            "language_version": "OSL-Core 0.5",
            "receipt_schema": "osl.core.receipt.v2",
            "evidence_profile": "v0.5-semantic-independence",
            "program_count": 66,
            "accepted_count": 42,
            "rejected_count": 24,
            "receipt_count": 1825,
            "terminal_phase_counts": {
                "complete": 42,
                "finalization": 2,
                "statement": 20,
                "static": 2,
            },
            "base_independent_verified_count": 66,
            "semantic_independence_verified_count": 66,
            "supplementary_replay_verified_count": 66,
            "passed_count": 66,
            "failed_count": 0,
            "all_checks_pass": True,
        },
        failures,
    )
    verify_embedded_digest(conformance_name, conformance, "suite_digest", failures)
    if conformance is not None:
        records = conformance.get("records")
        if not isinstance(records, list) or len(records) != 66:
            failures.append(f"evidence:{conformance_name}:records")
        elif not all(isinstance(item, dict) and item.get("passed") is True for item in records):
            failures.append(f"evidence:{conformance_name}:record_pass")

    trace_summary = verify_trace_bundle(root, failures)

    semantic_name = "CORE05_SEMANTIC_REPORT.json"
    semantic = load_json(root / semantic_name, failures)
    expect_fields(
        semantic_name,
        semantic,
        {
            "schema": "osl.core05.semantic-suite-summary.v1",
            "language_version": "OSL-Core 0.5",
            "program_count": 66,
            "component_verified_counts": {
                "contracts": 66,
                "intrinsics": 66,
                "metadata": 66,
                "numeric": 66,
                "sessions": 66,
            },
            "semantic_independence_verified_count": 66,
            "trace_bundle_file": "CORE05_TRACE_BUNDLE.jsonl",
            "trace_bundle_sha256": trace_summary["sha256"],
            "all_checks_pass": True,
        },
        failures,
    )
    verify_embedded_digest(semantic_name, semantic, "suite_digest", failures)
    if semantic is not None:
        delegated = semantic.get("remaining_delegated_semantics")
        if not isinstance(delegated, list) or not delegated:
            failures.append(f"evidence:{semantic_name}:remaining_delegated_semantics")

    bridge_name = "CORE05_DISCOVERY_BRIDGE_REPORT.json"
    bridge = load_json(root / bridge_name, failures)
    expect_fields(
        bridge_name,
        bridge,
        {
            "schema": "osl.core05.discovery-bridge-suite.v1",
            "language_version": "OSL-Core 0.5",
            "evidence_profile": "v0.5-semantic-independence",
            "program_count": 3,
            "accepted_count": 3,
            "receipt_count": 71,
            "base_independent_verified_count": 3,
            "semantic_independence_verified_count": 3,
            "supplementary_replay_verified_count": 3,
            "all_checks_pass": True,
        },
        failures,
    )
    verify_embedded_digest(bridge_name, bridge, "suite_digest", failures)
    if bridge is not None:
        records = bridge.get("records")
        if not isinstance(records, list) or len(records) != 3:
            failures.append(f"evidence:{bridge_name}:records")
        elif not all(isinstance(item, dict) and item.get("passed") is True for item in records):
            failures.append(f"evidence:{bridge_name}:record_pass")

    focused_name = "CORE05_FOCUSED_REPORT.json"
    focused = load_json(root / focused_name, failures)
    focused_files = [
        "tests/test_core05_semantic_numeric.py",
        "tests/test_core05_semantic_contracts.py",
        "tests/test_core05_semantic_sessions.py",
        "tests/test_core05_semantic_meta.py",
        "tests/test_core05_semantic_intrinsics.py",
        "tests/test_core05_semantic_kernel.py",
        "tests/test_core05_language_hardening.py",
    ]
    expect_fields(
        focused_name,
        focused,
        {
            "schema": "osl.core05.focused-test-suite.v1",
            "language_version": "OSL-Core 0.5",
            "files": focused_files,
            "category_case_counts": {
                "numeric": 16,
                "contracts": 16,
                "sessions": 11,
                "metadata": 6,
                "intrinsics": 3,
                "integration": 4,
                "language_hardening": 19,
            },
            "case_count": 75,
            "passed_count": 75,
            "failed_count": 0,
            "pytest_exit_code": 0,
            "all_checks_pass": True,
        },
        failures,
    )
    verify_embedded_digest(focused_name, focused, "report_digest", failures)

    test_name = "TEST_REPORT.json"
    test_report = load_json(root / test_name, failures)
    python_source_count = sum(
        not excluded(root, path)
        for path in (
            list((root / "reference").glob("*.py"))
            + list((root / "tests").glob("*.py"))
        )
    )
    expect_fields(
        test_name,
        test_report,
        {
            "schema": "osl.core.test-report.v2",
            "language_version": "OSL-Core 0.5",
            "pytest_exit_code": 0,
            "pytest_passed": 168,
            "pytest_failed": 0,
            "pytest_skipped": 0,
            "pytest_xfailed": 0,
            "pytest_xpassed": 0,
            "pytest_deselected": 0,
            "pytest_errors": 0,
            "python_source_count": python_source_count,
            "syntax_failure_count": 0,
            "syntax_failures": [],
            "all_checks_pass": True,
        },
        failures,
    )
    verify_embedded_digest(test_name, test_report, "report_digest", failures)

    historical = {
        "CORE04_CONFORMANCE_REPORT.json": {
            "schema": "osl.core04.conformance-suite.v1",
            "evidence_profile": "v0.4-native",
            "verification_status": "V04_NATIVE_VERIFIED",
            "example_count": 66,
            "accepted_count": 42,
            "rejected_count": 24,
            "audit_receipt_count": 1825,
            "all_checks_pass": True,
        },
        "CORE04_KERNEL_REPORT.json": {
            "schema": "osl.core04.strict-kernel-suite.v1",
            "evidence_profile": "v0.4-native",
            "verification_status": "V04_NATIVE_VERIFIED",
            "program_count": 66,
            "verified_program_count": 66,
            "independent_verified_program_count": 66,
            "supplementary_replay_verified_count": 66,
            "audit_receipt_count": 1825,
            "all_checks_pass": True,
        },
        "CORE04_DISCOVERY_BRIDGE_REPORT.json": {
            "schema": "osl.core04.discovery-bridge-suite.v1",
            "evidence_profile": "v0.4-native",
            "verification_status": "V04_NATIVE_VERIFIED",
            "program_count": 3,
            "accepted_count": 3,
            "receipt_count": 71,
            "supplementary_replay_verified_count": 3,
            "all_checks_pass": True,
        },
        "ADVERSARIAL_MUTATION_REPORT.json": {
            "schema": "osl.core04.adversarial-suite.v1",
            "language_version": "OSL-Core 0.4",
            "case_count": 24,
            "passed_count": 24,
            "failed_count": 0,
            "pytest_exit_code": 0,
            "all_checks_pass": True,
        },
    }
    for filename, expected in historical.items():
        report = load_json(root / filename, failures)
        expect_fields(filename, report, expected, failures)
        if filename == "ADVERSARIAL_MUTATION_REPORT.json":
            verify_embedded_digest(filename, report, "report_digest", failures)


def verify_manifest(root: Path, failures: list[str]) -> int:
    manifest_path = root / "MANIFEST.json"
    sums_path = root / "SHA256SUMS"
    for path in (manifest_path, sums_path):
        if path.is_symlink():
            failures.append(f"symlink:{path.name}")
        if not path.is_file():
            failures.append(f"missing:{path.name}")
    manifest = load_json(manifest_path, failures)
    if manifest is None:
        return 0

    expected_manifest_keys = {
        "schema",
        "release",
        "archive_name",
        "file_count",
        "files",
        "manifest_digest",
    }
    if set(manifest) != expected_manifest_keys:
        failures.append("manifest_fields")
    unsigned = dict(manifest)
    observed_manifest_digest = unsigned.pop("manifest_digest", None)
    if observed_manifest_digest != digest(unsigned):
        failures.append("manifest_digest")
    if manifest.get("schema") != EXPECTED_SCHEMA:
        failures.append("manifest_schema")
    if manifest.get("release") != EXPECTED_RELEASE:
        failures.append("manifest_release")
    if manifest.get("archive_name") != f"{root.name}.zip":
        failures.append("manifest_archive_name")

    records = manifest.get("files")
    if not isinstance(records, list):
        failures.append("manifest_files")
        records = []
    if manifest.get("file_count") != len(records):
        failures.append("manifest_file_count")

    listed_paths: list[str] = []
    seen_paths: set[str] = set()
    root_resolved = root.resolve()
    expected_record_keys = {"path", "size_bytes", "sha256"}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            failures.append(f"record_type:{index}")
            continue
        if set(record) != expected_record_keys:
            failures.append(f"record_fields:{index}")
        relative = record.get("path")
        if not isinstance(relative, str) or not relative:
            failures.append(f"record_path:{index}")
            continue
        pure = PurePosixPath(relative)
        if (
            pure.is_absolute()
            or not pure.parts
            or ".." in pure.parts
            or relative != pure.as_posix()
            or "\\" in relative
        ):
            failures.append(f"unsafe_path:{relative}")
            continue
        if relative in seen_paths:
            failures.append(f"duplicate_path:{relative}")
            continue
        seen_paths.add(relative)
        listed_paths.append(relative)
        path = root.joinpath(*pure.parts)
        try:
            path.resolve().relative_to(root_resolved)
        except (OSError, ValueError):
            failures.append(f"escaped_path:{relative}")
            continue
        if path.is_symlink():
            failures.append(f"symlink:{relative}")
            continue
        if not path.is_file():
            failures.append(f"missing:{relative}")
            continue
        size = record.get("size_bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            failures.append(f"size_format:{relative}")
        elif path.stat().st_size != size:
            failures.append(f"size:{relative}")
        expected_hash = record.get("sha256")
        if not isinstance(expected_hash, str) or SHA256_PATTERN.fullmatch(expected_hash) is None:
            failures.append(f"sha256_format:{relative}")
        elif sha256(path) != expected_hash:
            failures.append(f"sha256:{relative}")

    if listed_paths != sorted(listed_paths):
        failures.append("manifest_path_order")
    for required in sorted(REQUIRED_RELEASE_PATHS):
        if required not in seen_paths:
            failures.append(f"required_release_deliverable:{required}")
    pdf_path = root / "output/pdf/OSL_Core_0.5_Semantic_Independence_Technical_Update.pdf"
    if pdf_path.is_file():
        try:
            with pdf_path.open("rb") as handle:
                pdf_header = handle.read(5)
            if pdf_header != b"%PDF-" or pdf_path.stat().st_size < 10_000:
                failures.append("required_release_deliverable:technical_pdf_invalid")
        except OSError:
            failures.append("required_release_deliverable:technical_pdf_read")
    expected_paths, symlinks = expected_package_paths(root)
    failures.extend(f"symlink:{path}" for path in symlinks)
    if listed_paths != expected_paths:
        failures.extend(
            f"unlisted:{path}" for path in sorted(set(expected_paths) - set(listed_paths))
        )
        failures.extend(
            f"not_packaged:{path}" for path in sorted(set(listed_paths) - set(expected_paths))
        )

    expected_sums = "".join(
        f"{record.get('sha256')}  {record.get('path')}\n"
        for record in records
        if isinstance(record, dict)
    )
    try:
        observed_sums = sums_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        failures.append("SHA256SUMS_read")
    else:
        if observed_sums != expected_sums:
            failures.append("SHA256SUMS")
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="release directory (defaults to this script's package root)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    failures: list[str] = []
    if not root.is_dir():
        failures.append("root_not_directory")
        checked_file_count = 0
    else:
        checked_file_count = verify_manifest(root, failures)
        verify_evidence(root, failures)

    result: dict[str, Any] = {
        "schema": "osl.core05.offline-verification.v1",
        "release": EXPECTED_RELEASE,
        "checked_file_count": checked_file_count,
        "failure_count": len(failures),
        "failures": failures,
        "all_checks_pass": not failures,
        "claim_boundary": (
            "This checks packaged bytes, deterministic integrity metadata, and the "
            "declared finite Core 0.5 evidence reports. It does not authenticate a "
            "package signer or prove the interpreter for all programs."
        ),
    }
    result["verification_digest"] = digest(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
