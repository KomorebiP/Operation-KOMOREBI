#!/usr/bin/env python3
"""Verify the immutable RRCT v0.51 compact-release file set."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXCLUDED = {
    "validation/V0_51_BUILD_SHA256SUMS.txt",
    "validation/V0_51_BUILD_SHA256SUMS.txt.sha256",
}
EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    "build",
    "rrct_prototype.egg-info",
}


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
        if any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.add(relative)
    return files


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "validation/V0_51_BUILD_SHA256SUMS.txt"
    companion = manifest.with_suffix(manifest.suffix + ".sha256")
    if not manifest.is_file() or not companion.is_file():
        raise RuntimeError("v0.51 build manifest or companion is missing")

    manifest_sha = sha256(manifest)
    companion_tokens = companion.read_text(encoding="utf-8").strip().split()
    checks: dict[str, bool] = {
        "manifest_companion_matches": bool(
            companion_tokens and companion_tokens[0] == manifest_sha
        )
    }

    entries: dict[str, str] = {}
    duplicate = False
    lines = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for line in lines:
        digest, relative = line.split("  ", 1)
        if relative in entries:
            duplicate = True
        entries[relative] = digest

    checks["no_duplicate_entries"] = not duplicate and len(entries) == len(lines)
    checks["file_set_exact"] = set(entries) == expected_files(root)
    for relative, expected in entries.items():
        path = root / relative
        checks[f"present::{relative}"] = path.is_file()
        checks[f"sha256::{relative}"] = bool(
            path.is_file() and sha256(path) == expected
        )

    payload = {
        "schema": "rrct.v051.build_manifest_verification.v1",
        "manifest_sha256": manifest_sha,
        "entry_count": len(entries),
        "all_checks_pass": all(checks.values()),
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
