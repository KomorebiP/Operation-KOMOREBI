#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "V0_54_BUILD_SHA256SUMS.txt"
COMPANION = MANIFEST.with_suffix(MANIFEST.suffix + ".sha256")
EXCLUDED = {
    MANIFEST.relative_to(ROOT).as_posix(),
    COMPANION.relative_to(ROOT).as_posix(),
}
TRANSIENT_PARTS = {"__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_files() -> set[str]:
    result: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        name = relative.as_posix()
        if name in EXCLUDED:
            continue
        if any(part in TRANSIENT_PARTS for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        result.add(name)
    return result


def main() -> int:
    checks: dict[str, bool] = {
        "manifest_present": MANIFEST.is_file(),
        "companion_present": COMPANION.is_file(),
    }
    if not MANIFEST.is_file() or not COMPANION.is_file():
        print(json.dumps({"all_checks_pass": False, "checks": checks}, indent=2))
        return 1
    checks["companion_matches"] = COMPANION.read_text().split()[0] == sha256(MANIFEST)
    entries: dict[str, str] = {}
    duplicate = False
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        duplicate = duplicate or relative in entries
        entries[relative] = digest
    checks["no_duplicates"] = not duplicate
    checks["exact_file_set"] = set(entries) == expected_files()
    for relative, digest in entries.items():
        path = ROOT / relative
        checks[f"present::{relative}"] = path.is_file()
        checks[f"sha::{relative}"] = path.is_file() and sha256(path) == digest
    payload = {
        "schema": "rrct.v054.build_manifest_verification.v1",
        "manifest_sha256": sha256(MANIFEST),
        "entry_count": len(entries),
        "all_checks_pass": all(checks.values()),
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
