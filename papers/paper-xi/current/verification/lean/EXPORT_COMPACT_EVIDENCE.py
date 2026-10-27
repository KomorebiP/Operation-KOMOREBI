#!/usr/bin/env python3
"""Copy finalized Paper XI verification evidence while omitting build objects.

Usage: python3 EXPORT_COMPACT_EVIDENCE.py PROJECT_ROOT NEW_OUTPUT_DIRECTORY
The source project's RELEASE_VERIFICATION.json must already report PASS.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    project = Path(sys.argv[1]).resolve()
    source = project / "evidence"
    target = Path(sys.argv[2]).resolve()
    if target.exists() or target.is_relative_to(source):
        raise RuntimeError("Evidence export must use a new directory outside the source evidence")
    summary = json.loads((source / "RELEASE_VERIFICATION.json").read_text())
    if summary["status"] != "PASS":
        raise RuntimeError("Cannot export an incomplete verification as the finalized release")
    excluded_parts = {"objects", ".runtime", ".lake", "__pycache__", "cache"}
    included = []
    omitted = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if (set(relative.parts) & excluded_parts or ".olean" in path.name
                or path.suffix in {".ilean", ".pyc", ".o", ".a", ".so", ".zst"}):
            omitted.append(str(relative))
            continue
        if path.is_symlink():
            raise RuntimeError(f"Evidence file is a symlink: {relative}")
        fingerprint = digest(path)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        if digest(destination) != fingerprint or digest(path) != fingerprint:
            raise RuntimeError(f"Evidence changed while copied: {relative}")
        included.append({"path": str(relative), "sha256": fingerprint,
                         "bytes": destination.stat().st_size})
    manifest = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PASS", "file_count_excluding_this_manifest": len(included),
        "bytes_excluding_this_manifest": sum(row["bytes"] for row in included),
        "files": included, "omitted_file_count": len(omitted),
        "omitted_kind": "Compiled objects, caches and runtime artifacts; their receipt fingerprints are retained.",
        "path_mapping": {"original_project_sources": "formalization/",
                         "original_project_evidence": "verification/lean/"},
    }
    (target / "COMPACT_EVIDENCE_EXPORT.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: manifest[key] for key in [
        "status", "file_count_excluding_this_manifest", "bytes_excluding_this_manifest",
        "omitted_file_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
