from __future__ import annotations

import hashlib
import json
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


def main() -> int:
    entries = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in included_files()
    ]
    document = {
        "schema_version": "1.0",
        "root_name": ROOT.name,
        "exclusions": ["PACKAGE_MANIFEST.json", "**/__pycache__/**", "**/*.pyc"],
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("V061_MANIFEST_BUILT")
    print(f"files={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

