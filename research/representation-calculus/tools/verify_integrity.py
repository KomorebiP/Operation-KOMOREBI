"""Verify the distribution files before rerunning audits, which replace run records.
The manifest cannot authenticate itself. Compare the ZIP's external SHA-256 when
establishing provenance. No files or external paths are modified by this checker.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "FILE_MANIFEST.json").read_text())
    if manifest.get("schema") != "komorebi-distribution-manifest-1":
        raise ValueError("Unsupported distribution manifest")
    seen: set[str] = set()
    failures: list[str] = []
    for record in manifest["files"]:
        name = record["path"]
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or "\\" in name or name in seen:
            raise ValueError(f"Invalid or duplicate distribution path: {name}")
        seen.add(name)
        path = root.joinpath(*rel.parts)
        if path.is_symlink() or not path.is_file() or root not in path.resolve().parents:
            failures.append(f"missing, non-file, or unsafe: {name}")
            continue
        raw = path.read_bytes()
        if len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
            failures.append(f"size/hash mismatch: {name}")
    if len(seen) != manifest["file_count"]:
        failures.append("manifest count mismatch")
    print(json.dumps({"status": "FAIL" if failures else "PASS", "checked_files":len(seen), "failures":failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Integrity validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
