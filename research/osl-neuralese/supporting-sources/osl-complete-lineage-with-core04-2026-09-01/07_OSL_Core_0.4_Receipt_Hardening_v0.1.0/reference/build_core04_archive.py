#!/usr/bin/env python3
"""Build the deterministic distributable ZIP for the Core 0.4 release."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
FIXED_TIMESTAMP = (2026, 9, 1, 0, 0, 0)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    archive_path = root.parent / f"{root.name}.zip"
    paths = sorted(root.rglob("*"))
    symlinks = [
        path.relative_to(root).as_posix()
        for path in paths
        if path.is_symlink()
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    ]
    if symlinks:
        print(json.dumps({
            "all_checks_pass": False,
            "failure": "symlinks_not_permitted",
            "paths": symlinks,
        }, indent=2, sort_keys=True))
        return 1
    files = [
        path
        for path in paths
        if path.is_file()
        and path.suffix != ".pyc"
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    ]
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            relative = Path(root.name) / path.relative_to(root)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o100755 if path.suffix == ".sh" else 0o100644
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes())
    payload = {
        "all_checks_pass": True,
        "archive": archive_path.name,
        "file_count": len(files),
        "size_bytes": archive_path.stat().st_size,
        "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
