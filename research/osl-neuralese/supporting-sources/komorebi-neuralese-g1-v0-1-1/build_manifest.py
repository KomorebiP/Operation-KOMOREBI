from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from neuralese_g1.integrity import (
    PACKAGE_MANIFEST_NAME,
    PACKAGE_MANIFEST_SCHEMA,
    package_file_inventory,
    sha256_file,
)


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / PACKAGE_MANIFEST_NAME


def main() -> int:
    files = package_file_inventory(ROOT)
    entries = [
        {
            "path": name,
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for name, path in sorted(files.items())
    ]
    payload = {
        "schema": PACKAGE_MANIFEST_SCHEMA,
        "entry_count": len(entries),
        "entries": entries,
    }
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=MANIFEST.name + ".", suffix=".tmp", dir=ROOT
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, MANIFEST)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    print(f"G1_MANIFEST_BUILT files={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
