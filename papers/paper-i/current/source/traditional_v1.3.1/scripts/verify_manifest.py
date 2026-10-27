#!/usr/bin/env python3
"""Check bundled SHA-256 values. This is integrity checking, not proof checking."""
from pathlib import Path
import hashlib
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "SHA256SUMS.txt"
    if not manifest.is_file():
        print("FAIL: SHA256SUMS.txt is missing", file=sys.stderr)
        return 1
    errors = []
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", 1)
            path = (root / relative).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError("missing or unsafe path")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != expected:
                raise ValueError("SHA-256 mismatch")
            checked += 1
        except (ValueError, OSError) as exc:
            errors.append(f"{line}: {exc}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Integrity PASS: {checked} files match their recorded SHA-256 values.")
    print("This does not establish the correctness of the contents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
