from __future__ import annotations

import json
from pathlib import Path

from g1d.integrity import MANIFEST_NAME, MANIFEST_SCHEMA, file_inventory, sha256_file


ROOT = Path(__file__).resolve().parent


def main() -> int:
    files = file_inventory(ROOT, exclude=(MANIFEST_NAME,))
    entries = [
        {"path": name, "size": path.stat().st_size, "sha256": sha256_file(path)}
        for name, path in sorted(files.items())
    ]
    value = {"schema": MANIFEST_SCHEMA, "entry_count": len(entries), "entries": entries}
    (ROOT / MANIFEST_NAME).write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"G1D_MANIFEST_BUILT files={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
