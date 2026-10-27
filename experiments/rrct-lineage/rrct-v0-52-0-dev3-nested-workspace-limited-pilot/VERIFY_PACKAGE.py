#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "BUILD_SHA256SUMS.txt"
COMPANION = ROOT / "BUILD_SHA256SUMS.txt.sha256"
EXCLUDED = {MANIFEST.name, COMPANION.name}

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def expected_files() -> set[str]:
    out = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDED or "__pycache__" in path.parts or ".pytest_cache" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        out.add(rel)
    return out

def main() -> int:
    entries = {}
    for line in MANIFEST.read_text().splitlines():
        if line.strip():
            digest, rel = line.split("  ", 1); entries[rel] = digest
    failed = []
    if set(entries) != expected_files():
        failed.append("file_set")
    for rel, digest in entries.items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != digest:
            failed.append(rel)
    companion = COMPANION.read_text().split()[0]
    if companion != sha(MANIFEST):
        failed.append("manifest_companion")
    payload = {"schema": "rrct.v052.dev3.package_verification.v1", "entry_count": len(entries), "all_checks_pass": not failed, "failed": failed, "manifest_sha256": sha(MANIFEST)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
