from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PACKAGE_MANIFEST.json"


def included_files() -> list[Path]:
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if path == MANIFEST or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        result.append(path)
    return sorted(result, key=lambda item: item.relative_to(ROOT).as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    require(MANIFEST.is_file(), "PACKAGE_MANIFEST.json is missing")
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = document["entries"]
    expected_paths = [entry["path"] for entry in entries]
    actual_files = included_files()
    actual_paths = [path.relative_to(ROOT).as_posix() for path in actual_files]
    require(expected_paths == actual_paths, "manifest does not exactly cover regular package files")
    for entry, path in zip(entries, actual_files):
        require(entry["bytes"] == path.stat().st_size, f"size mismatch: {entry['path']}")
        require(entry["sha256"] == sha256(path), f"SHA-256 mismatch: {entry['path']}")
    print("V061_PACKAGE_VALID")
    print(f"manifest_files={len(entries)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"V061_PACKAGE_INVALID: {exc}", file=sys.stderr)
        raise

