#!/usr/bin/env python3
"""Verify the immutable file set in the RRCT v0.56 compact release."""
from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "V0_56_BUILD_SHA256SUMS.txt"
COMPANION = ROOT / "V0_56_BUILD_SHA256SUMS.txt.sha256"
EXCLUDED = {MANIFEST.name, COMPANION.name}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_files() -> set[str]:
    files: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.as_posix() in EXCLUDED:
            continue
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.add(relative.as_posix())
    return files


def main() -> int:
    checks: dict[str, bool] = {
        "manifest_present": MANIFEST.is_file(),
        "companion_present": COMPANION.is_file(),
    }
    if not all(checks.values()):
        print(json.dumps({"status": "FAILED", "failed_checks": [name for name, passed in checks.items() if not passed]}, indent=2))
        return 1

    companion_tokens = COMPANION.read_text(encoding="utf-8").split()
    manifest_sha = sha256(MANIFEST)
    checks["companion_matches"] = bool(companion_tokens and companion_tokens[0] == manifest_sha)

    entries: dict[str, str] = {}
    duplicate = False
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        if relative in entries:
            duplicate = True
        entries[relative] = digest
    checks["no_duplicate_entries"] = not duplicate
    checks["exact_file_set"] = set(entries) == expected_files()
    for relative, digest in entries.items():
        path = ROOT / relative
        checks[f"present::{relative}"] = path.is_file()
        checks[f"sha256::{relative}"] = bool(path.is_file() and sha256(path) == digest)

    payload = {
        "schema": "rrct.v056.build_manifest_verification.v1",
        "status": "V056_BUILD_MANIFEST_VERIFIED" if all(checks.values()) else "V056_BUILD_MANIFEST_FAILED",
        "manifest_sha256": manifest_sha,
        "entry_count": len(entries),
        "checks_passed": sum(bool(value) for value in checks.values()),
        "check_count": len(checks),
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
