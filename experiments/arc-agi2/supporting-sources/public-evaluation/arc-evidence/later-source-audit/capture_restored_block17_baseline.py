"""Authenticate restored source content and capture a separate mtime baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
REFERENCE_SHA256 = "e655bcf293478ed4da1ce51f903095b0121e285893ecb3e95a49e8749bf47ec8"


def file_hash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, reference, output = (p.resolve() for p in (args.root, args.reference, args.output))
    if output.is_relative_to(root) or output == reference or output.exists():
        raise ValueError("baseline must be a new file outside frozen source; preserve the original reference")
    reference_bytes = reference.read_bytes()
    if hashlib.sha256(reference_bytes).hexdigest() != REFERENCE_SHA256:
        raise ValueError("archived original source snapshot identity changed")
    expected = json.loads(reference_bytes.decode("utf-8"))
    paths = {str(p.relative_to(root)): p for p in root.rglob("*") if p.is_file()}
    if set(paths) != set(expected) or len(paths) != 388:
        raise ValueError("restored source inventory differs from the archived snapshot")
    baseline = {}
    for name, path in sorted(paths.items()):
        before = path.stat()
        sha = file_hash(path)
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError(f"source changed while authenticating: {name}")
        if after.st_size != expected[name]["size"] or sha != expected[name]["sha256"]:
            raise ValueError(f"restored source content differs from archived source: {name}")
        baseline[name] = {"size": after.st_size, "mtime_ns": after.st_mtime_ns, "sha256": sha}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"baseline": str(output), "files": len(baseline),
                      "source_content_and_inventory_identical_to_archived_snapshot": True,
                      "original_reference_preserved": True,
                      "baseline_sha256": file_hash(output)}, indent=2))


if __name__ == "__main__":
    main()
