#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for rec in data["files"]:
        path = ROOT / rec["path"]
        if not path.is_file():
            failures.append({"path": rec["path"], "failure": "MISSING"})
            continue
        size = path.stat().st_size
        digest = sha256(path)
        if size != rec["size_bytes"] or digest != rec["sha256"]:
            failures.append({
                "path": rec["path"],
                "failure": "MISMATCH",
                "expected_size": rec["size_bytes"],
                "actual_size": size,
                "expected_sha256": rec["sha256"],
                "actual_sha256": digest,
            })
    expected = {rec["path"] for rec in data["files"]}
    actual = {
        str(p.relative_to(ROOT)).replace("\\", "/")
        for p in ROOT.rglob("*")
        if p.is_file()
        and p != MANIFEST
        and ".lake" not in p.parts
        and "__pycache__" not in p.parts
    }
    extras = sorted(actual - expected)
    if extras:
        failures.append({"failure": "UNMANIFESTED_FILES", "paths": extras})
    print(json.dumps({
        "status": "PASS" if not failures else "FAIL",
        "checked": len(data["files"]),
        "failures": failures,
    }, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
