"""Verify the archived checkpoint's bytes and local Markdown references.

This checks provenance and completeness, not mathematical correctness.
Run: python3 verify_checkpoint.py
"""
import hashlib
import json
import re
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "CHECKPOINT_MANIFEST.json").read_text())
    errors = []
    for record in manifest["files"]:
        path = root / record["path"]
        if not path.is_file():
            errors.append(f"missing: {record['path']}")
            continue
        data = path.read_bytes()
        if len(data) != record["bytes"]:
            errors.append(f"size mismatch: {record['path']}")
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            errors.append(f"hash mismatch: {record['path']}")
    for name in ("README.md", "RESEARCH_STATUS.md"):
        path = root / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" not in target and not target.startswith("#"):
                if not (path.parent / target.split("#")[0]).exists():
                    errors.append(f"missing local reference in {name}: {target}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checkpoint verified: {len(manifest['files'])} pinned files; "
          "local report references resolve.")
    print("Hash verification does not replace the mathematical audits.")


if __name__ == "__main__":
    main()
