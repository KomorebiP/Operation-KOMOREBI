#!/usr/bin/env python3
"""Verify the immutable file set in the RRCT v0.49 compact release."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXCLUDED = {
    "validation/V0_49_BUILD_SHA256SUMS.txt",
    "validation/V0_49_BUILD_SHA256SUMS.txt.sha256",
}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_files(root: Path) -> set[str]:
    files: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in EXCLUDED:
            continue
        parts = path.relative_to(root).parts
        if any(part in EXCLUDED_PARTS for part in parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.add(relative)
    return files


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "validation/V0_49_BUILD_SHA256SUMS.txt"
    companion = manifest.with_suffix(manifest.suffix + ".sha256")
    if not manifest.is_file() or not companion.is_file():
        raise RuntimeError("v0.49 build manifest or companion is missing")
    manifest_sha = sha256(manifest)
    tokens = companion.read_text(encoding="utf-8").strip().split()
    checks: dict[str, bool] = {
        "manifest_companion_matches": bool(tokens and tokens[0] == manifest_sha)
    }
    lines = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    entries: dict[str, str] = {}
    duplicate = False
    for line in lines:
        digest, relative = line.split("  ", 1)
        if relative in entries:
            duplicate = True
        entries[relative] = digest
    checks["no_duplicate_entries"] = not duplicate and len(entries) == len(lines)
    checks["file_set_exact"] = set(entries) == expected_files(root)
    failed_files = [
        relative
        for relative, digest in entries.items()
        if not (root / relative).is_file() or sha256(root / relative) != digest
    ]
    checks["all_file_hashes_match"] = not failed_files
    payload = {
        "schema": "rrct.v049.build_manifest_verification.v1",
        "version": "0.49.0.dev1",
        "manifest_sha256": manifest_sha,
        "entry_count": len(entries),
        "checks": checks,
        "failed_files": failed_files,
        "all_checks_pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
