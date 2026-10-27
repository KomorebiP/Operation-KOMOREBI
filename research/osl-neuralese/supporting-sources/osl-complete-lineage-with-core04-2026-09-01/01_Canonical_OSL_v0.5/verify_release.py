#!/usr/bin/env python3
"""Verify the immutable OSL-Core 0.3 / manuscript v0.5 payload."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

TRANSIENT_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".toc", ".pyc", ".pyo"}
TRANSIENT_PARTS = {"__pycache__", ".pytest_cache", "_renders", "_renders_v05"}
MANIFEST_EXCLUDED = {"MANIFEST.json", "SHA256SUMS.txt"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def immutable_files(root: Path) -> set[str]:
    result: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        if relative in MANIFEST_EXCLUDED:
            continue
        if any(part in TRANSIENT_PARTS or part.startswith("_renders") for part in relative_path.parts):
            continue
        if "contact_sheet" in relative_path.name:
            continue
        if any(relative.endswith(suffix) for suffix in TRANSIENT_SUFFIXES):
            continue
        result.add(relative)
    return result


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parent
    required_names = [
        "SHA256SUMS.txt", "MANIFEST.json", "STATUS.json",
        "operator_symbolic_ai_language_v0.5.pdf", "EXAMPLE_RESULTS.json",
        "TEST_REPORT.json", "PDF_PREFLIGHT.json", "V03_UNIFIED_VERIFICATION.json",
        "V03_CERTIFICATE_INDEX.json", "COMPACT_CLOSURE_CERTIFICATE.json",
        "FINITE_METACORE_CERTIFICATE.json", "INDEPENDENT_KERNEL_REPORT.json",
        "TRACE_VERIFICATION.json", "INFORMATION_FLOW_REPORT.json",
        "SESSION_VERIFICATION_REPORT.json",
    ]
    failures: list[str] = []
    for name in required_names:
        if not (root / name).is_file():
            failures.append(f"missing:{name}")
    if failures:
        print(json.dumps({"all_checks_pass": False, "failed_checks": failures}, indent=2))
        return 1

    manifest = load(root / "MANIFEST.json")
    status = load(root / "STATUS.json")
    examples = load(root / "EXAMPLE_RESULTS.json")
    tests = load(root / "TEST_REPORT.json")
    preflight = load(root / "PDF_PREFLIGHT.json")
    unified = load(root / "V03_UNIFIED_VERIFICATION.json")
    index = load(root / "V03_CERTIFICATE_INDEX.json")

    if manifest.get("schema") != "operator-symbolic-ai.release-manifest.v3": failures.append("manifest_schema")
    if manifest.get("release_version") != "0.5": failures.append("manifest_version")
    if manifest.get("language") != "OSL-Core 0.3": failures.append("manifest_language")
    if status.get("schema") != "operator-symbolic-ai.status.v3": failures.append("status_schema")
    if status.get("release_version") != "0.5": failures.append("status_version")
    if status.get("language") != "OSL-Core 0.3": failures.append("status_language")
    if examples.get("example_count") != 66 or examples.get("passed_count") != 66: failures.append("example_counts")
    if examples.get("accepted_count") != 42 or examples.get("expected_rejection_count") != 24: failures.append("example_split")
    if examples.get("audit_count") != 2 or examples.get("audit_passed_count") != 2: failures.append("audit_counts")
    if tests.get("pytest_passed") != 61 or not tests.get("all_checks_pass"): failures.append("test_report")
    if not preflight.get("all_checks_pass"): failures.append("pdf_preflight")
    if not unified.get("all_checks_pass"): failures.append("unified_verification")
    if not index.get("all_checks_pass"): failures.append("certificate_index")

    for artifact, meta in index.get("artifacts", {}).items():
        path = root / artifact
        if not path.is_file():
            failures.append(f"certificate_missing:{artifact}")
        elif sha256(path) != meta.get("sha256"):
            failures.append(f"certificate_sha256:{artifact}")

    entries = manifest.get("files", {})
    expected_set = immutable_files(root)
    if set(entries) != expected_set:
        failures.append(
            "manifest_file_set:missing=" + str(sorted(expected_set - set(entries)))
            + ":unexpected=" + str(sorted(set(entries) - expected_set))
        )

    checked_manifest = 0
    for relative, metadata in entries.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"manifest_missing:{relative}")
            continue
        checked_manifest += 1
        if path.stat().st_size != int(metadata.get("size_bytes", -1)):
            failures.append(f"manifest_size:{relative}")
        if sha256(path) != metadata.get("sha256"):
            failures.append(f"manifest_sha256:{relative}")

    pdf = root / "operator_symbolic_ai_language_v0.5.pdf"
    if manifest.get("file_count") != len(entries): failures.append("manifest_file_count")
    if manifest.get("pdf_sha256") != sha256(pdf): failures.append("pdf_sha256")
    if manifest.get("example_suite_digest") != examples.get("suite_digest"): failures.append("example_suite_digest")
    if manifest.get("unified_verification_digest") != unified.get("verification_digest"): failures.append("unified_digest")
    if manifest.get("certificate_index_digest") != index.get("index_digest"): failures.append("index_digest")
    if manifest.get("status_sha256") != sha256(root / "STATUS.json"): failures.append("status_sha256")

    checked_checksums = 0
    seen: set[str] = set()
    for raw in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split("  ", 1)
        if relative in seen: failures.append(f"duplicate_checksum:{relative}")
        seen.add(relative)
        path = root / relative
        if not path.is_file():
            failures.append(f"checksum_missing:{relative}")
            continue
        checked_checksums += 1
        if sha256(path) != expected: failures.append(f"checksum_sha256:{relative}")

    payload = {
        "schema": "operator-symbolic-ai.release-verification.v3",
        "release_version": "0.5",
        "language": "OSL-Core 0.3",
        "manifest_sha256": sha256(root / "MANIFEST.json"),
        "status_sha256": sha256(root / "STATUS.json"),
        "pdf_sha256": sha256(pdf),
        "unified_verification_digest": unified.get("verification_digest"),
        "certificate_index_digest": index.get("index_digest"),
        "manifest_files_checked": checked_manifest,
        "checksum_files_checked": checked_checksums,
        "failed_checks": failures,
        "all_checks_pass": not failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
