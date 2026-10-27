from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "PACKAGE_MANIFEST.sha256"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def included_files() -> set[str]:
    files = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == MANIFEST.name:
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if relative.startswith("generated/"):
            continue
        owned_output = False
        for parent in path.parents:
            if parent == ROOT:
                break
            if (parent / ".arithmetic_space_lab_output").is_file():
                owned_output = True
                break
        if owned_output and not relative.startswith("examples/"):
            continue
        files.add(relative)
    return files


def main() -> int:
    if not MANIFEST.is_file():
        print("PACKAGE_VERIFY=FAIL: PACKAGE_MANIFEST.sha256 is missing", file=sys.stderr)
        return 1
    expected: dict[str, str] = {}
    for line_number, line in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            checksum, relative = line.split("  ", 1)
        except ValueError:
            print(f"PACKAGE_VERIFY=FAIL: malformed manifest line {line_number}", file=sys.stderr)
            return 1
        expected[relative] = checksum
    actual = included_files()
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        print(f"PACKAGE_VERIFY=FAIL: missing={missing} extra={extra}", file=sys.stderr)
        return 1
    for relative, checksum in expected.items():
        if digest(ROOT / relative) != checksum:
            print(f"PACKAGE_VERIFY=FAIL: checksum mismatch for {relative}", file=sys.stderr)
            return 1
    print("PACKAGE_VERIFY=PASS")
    print(f"PACKAGE_FILES={len(expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
