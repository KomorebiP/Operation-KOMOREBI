#!/usr/bin/env python3
"""Build deterministic file-integrity metadata for the Core 0.4 package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from osl_model import digest


EXCLUDED_NAMES = {
    "MANIFEST.json",
    "SHA256SUMS",
    "OSL_Core_0.4_Receipt_Hardening_v0.1.0.zip",
}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = sorted(root.rglob("*"))
    symlinks = [
        path.relative_to(root).as_posix()
        for path in paths
        if path.is_symlink()
        and path.name not in EXCLUDED_NAMES
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    ]
    if symlinks:
        print(json.dumps({
            "all_checks_pass": False,
            "failure": "symlinks_not_permitted",
            "paths": symlinks,
        }, indent=2, sort_keys=True))
        return 1
    files = [
        path
        for path in paths
        if path.is_file()
        and path.name not in EXCLUDED_NAMES
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
        and path.suffix != ".pyc"
    ]
    records = [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    payload = {
        "schema": "osl.core04.release-manifest.v1",
        "release": "OSL-Core 0.4 Receipt Hardening v0.1.0",
        "file_count": len(records),
        "files": records,
    }
    payload["manifest_digest"] = digest(payload)
    (root / "MANIFEST.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sums = "".join(f"{record['sha256']}  {record['path']}\n" for record in records)
    (root / "SHA256SUMS").write_text(sums, encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": True,
        "file_count": len(records),
        "manifest_digest": payload["manifest_digest"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
