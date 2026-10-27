#!/usr/bin/env python3
"""Build deterministic OSL v0.5 status, manifest, and checksum files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from osl_model import digest

TRANSIENT_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".toc", ".pyc", ".pyo"}
TRANSIENT_PARTS = {"__pycache__", ".pytest_cache", "_renders", "_renders_v05"}
EXCLUDED = {"MANIFEST.json", "SHA256SUMS.txt"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def files_for_manifest(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        name = relative.as_posix()
        if name in EXCLUDED:
            continue
        if any(part in TRANSIENT_PARTS or part.startswith("_renders") for part in relative.parts):
            continue
        if "contact_sheet" in relative.name:
            continue
        if any(name.endswith(suffix) for suffix in TRANSIENT_SUFFIXES):
            continue
        result.append(path)
    return sorted(result)


def count_lines(paths: list[Path]) -> dict[str, int]:
    lines = nonblank = 0
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace").splitlines()
        lines += len(text)
        nonblank += sum(bool(line.strip()) for line in text)
    return {"file_count": len(paths), "lines": lines, "nonblank_lines": nonblank}


def load(root: Path, name: str) -> dict[str, Any]:
    return json.loads((root / name).read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    pdf = root / "operator_symbolic_ai_language_v0.5.pdf"
    examples = load(root, "EXAMPLE_RESULTS.json")
    unified = load(root, "V03_UNIFIED_VERIFICATION.json")
    tests = load(root, "TEST_REPORT.json")
    preflight = load(root, "PDF_PREFLIGHT.json")
    index = load(root, "V03_CERTIFICATE_INDEX.json")

    source_paths = sorted((root / "reference").glob("*.py"))
    test_paths = sorted((root / "tests").glob("*.py"))
    example_paths = sorted((root / "examples").glob("*.osl"))
    tex_paths = [root / "main.tex", *sorted((root / "sections").glob("*.tex"))]

    status: dict[str, Any] = {
        "schema": "operator-symbolic-ai.status.v3",
        "release_version": "0.5",
        "draft": "Finite Metatheory and Independent-Kernel Draft v0.5",
        "language": "OSL-Core 0.3",
        "scientific_status": "FINITE_COMPUTER_ASSISTED_METATHEORY_PASSED",
        "pdf": {"path": pdf.name, "sha256": sha256(pdf), "size_bytes": pdf.stat().st_size, "pages": preflight["pages"]},
        "conformance": {
            "program_count": examples["example_count"],
            "accepted_count": examples["accepted_count"],
            "expected_rejection_count": examples["expected_rejection_count"],
            "passed_count": examples["passed_count"],
            "paired_audits": examples["audit_passed_count"],
            "suite_digest": examples["suite_digest"],
        },
        "verification": {
            "all_checks_pass": unified["all_checks_pass"],
            "verification_digest": unified["verification_digest"],
            "certificate_index_digest": index["index_digest"],
            "focused_tests_passed": tests["pytest_passed"],
            "pdf_preflight_passed": preflight["all_checks_pass"],
            **unified["summary"],
        },
        "code_size": {
            "reference_python": count_lines(source_paths),
            "tests": count_lines(test_paths),
            "examples": count_lines(example_paths),
            "latex": count_lines(tex_paths),
        },
        "implemented": [
            "typed finite AST and static checks",
            "persistent, affine, and linear proof resources",
            "provenance-aware autobiographical memory",
            "bounded, expiring, and revocable capabilities",
            "temporal contracts",
            "transaction rollback with append-only audit history",
            "source-statement semantic boundary receipts",
            "finite verified session graphs",
            "quarantined neural proposals",
            "paired and static information-flow audits",
            "independent receipt/proof replay",
            "exhaustive finite abstract-state certificates",
        ],
        "claim_boundary": "Computer-assisted finite evidence for the declared OSL-Core 0.3 models and packaged programs. The Python runtime remains trusted; arbitrary OSL programs, principal authentication, universal noninterference, unbounded distributed liveness, and neural semantic truth are not proved.",
    }
    status["status_digest"] = digest(status)
    (root / "STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    paths = files_for_manifest(root)
    entries = {
        path.relative_to(root).as_posix(): {"sha256": sha256(path), "size_bytes": path.stat().st_size}
        for path in paths
    }
    manifest: dict[str, Any] = {
        "schema": "operator-symbolic-ai.release-manifest.v3",
        "release_version": "0.5",
        "language": "OSL-Core 0.3",
        "file_count": len(entries),
        "files": entries,
        "pdf_sha256": sha256(pdf),
        "example_suite_digest": examples["suite_digest"],
        "unified_verification_digest": unified["verification_digest"],
        "certificate_index_digest": index["index_digest"],
        "status_sha256": sha256(root / "STATUS.json"),
    }
    manifest["manifest_digest"] = digest(manifest)
    (root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_paths = [*paths, root / "MANIFEST.json"]
    lines = [f"{sha256(path)}  {path.relative_to(root).as_posix()}" for path in sorted(checksum_paths)]
    (root / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": "built", "manifest_files": len(entries), "manifest_sha256": sha256(root / 'MANIFEST.json'), "checksum_entries": len(lines)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
