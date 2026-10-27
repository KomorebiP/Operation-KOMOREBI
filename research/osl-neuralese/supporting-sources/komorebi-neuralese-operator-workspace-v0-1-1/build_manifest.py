#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDED = {"SHA256SUMS.txt", "MANIFEST.json"}


def main() -> int:
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.name in EXCLUDED or "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append({"path": relative, "size": path.stat().st_size, "sha256": digest})
    (ROOT / "SHA256SUMS.txt").write_text(
        "".join(f"{record['sha256']}  {record['path']}\n" for record in records), encoding="utf-8"
    )
    manifest = {
        "schema": "komorebi.neuralese.package_manifest.v1",
        "version": "0.1.1",
        "file_count": len(records),
        "files": records,
    }
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"file_count": len(records)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
