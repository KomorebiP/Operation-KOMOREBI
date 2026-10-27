from __future__ import annotations

import json
import pathlib
from typing import Any

from .utils import sha256_file


EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXCLUDED_FILES = {
    "BUILD_SHA256SUMS.txt",
    "BUILD_SHA256SUMS.txt.sha256",
}


def expected_manifest_files(root: pathlib.Path) -> set[str]:
    files: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        rel = relative.as_posix()
        if rel in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.add(rel)
    return files


def verify_manifest(root: pathlib.Path) -> dict[str, Any]:
    manifest = root / "BUILD_SHA256SUMS.txt"
    companion = manifest.with_suffix(manifest.suffix + ".sha256")
    if not manifest.is_file():
        return {"status": "missing", "all_checks_pass": False, "failed": [str(manifest)]}
    failed: list[str] = []
    entries: dict[str, str] = {}
    duplicate = False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        if relative in entries:
            duplicate = True
        entries[relative] = digest
        path = root / relative
        if not path.is_file() or sha256_file(path) != digest:
            failed.append(relative)
    if duplicate:
        failed.append("duplicate_manifest_entry")
    expected = expected_manifest_files(root)
    if set(entries) != expected:
        missing = sorted(expected - set(entries))
        extra = sorted(set(entries) - expected)
        failed.extend(f"untracked::{item}" for item in missing)
        failed.extend(f"unexpected::{item}" for item in extra)
    manifest_digest = sha256_file(manifest)
    companion_matches = False
    if companion.is_file():
        tokens = companion.read_text(encoding="utf-8").strip().split()
        companion_matches = bool(tokens and tokens[0] == manifest_digest)
    if not companion_matches:
        failed.append("manifest_companion")
    return {
        "status": "verified" if not failed else "failed",
        "all_checks_pass": not failed,
        "entry_count": len(entries),
        "file_set_exact": set(entries) == expected,
        "companion_matches": companion_matches,
        "failed": sorted(set(failed)),
        "manifest_sha256": manifest_digest,
    }


def verify_vendor(root: pathlib.Path) -> dict[str, Any]:
    release_index_path = root / "vendor/RELEASE_INDEX.json"
    wheel_index_path = root / "vendor/WHEEL_INDEX.json"
    failed: list[str] = []
    release_count = 0
    wheel_count = 0
    if not release_index_path.is_file():
        failed.append(str(release_index_path))
    else:
        index = json.loads(release_index_path.read_text(encoding="utf-8"))
        release_count = len(index.get("releases", []))
        for release in index.get("releases", []):
            path = root / "vendor/releases" / release["archive"]
            if not path.is_file() or sha256_file(path) != release["sha256"]:
                failed.append(release["archive"])
    if not wheel_index_path.is_file():
        failed.append(str(wheel_index_path))
    else:
        index = json.loads(wheel_index_path.read_text(encoding="utf-8"))
        wheel_count = len(index.get("wheels", []))
        for wheel in index.get("wheels", []):
            path = root / "vendor/wheels" / wheel["name"]
            if not path.is_file() or sha256_file(path) != wheel["sha256"]:
                failed.append(wheel["name"])
    return {
        "status": "verified" if not failed else "failed",
        "all_checks_pass": not failed,
        "release_count": release_count,
        "wheel_count": wheel_count,
        "failed": failed,
    }
