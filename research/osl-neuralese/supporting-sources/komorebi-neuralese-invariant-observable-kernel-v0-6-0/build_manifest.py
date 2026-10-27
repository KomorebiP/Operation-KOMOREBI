#!/usr/bin/env python3
"""Build the deterministic, self-excluding v0.6 package manifest."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Iterable


ROOT = Path(__file__).resolve().parent
VERSION = "0.6.0"
AUTHOR = "Komorebi P."
MANIFEST_SCHEMA = "komorebi.neuralese.package_manifest.v6"
SELF_EXCLUDED = frozenset({"MANIFEST.json", "SHA256SUMS.txt"})


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_relative_path(relative: str) -> None:
    """Reject paths that could escape or be interpreted differently by tools."""

    parsed = PurePosixPath(relative)
    if (
        not relative
        or parsed.is_absolute()
        or relative != parsed.as_posix()
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or "\\" in relative
    ):
        raise ValueError(f"unsafe package path: {relative!r}")


def is_excluded(relative: str, path: Path) -> bool:
    return (
        relative in SELF_EXCLUDED
        or relative == "prof.out"
        or "__pycache__" in path.parts
        or ".pytest_cache" in path.parts
        or relative.startswith("results/local/")
        or relative.startswith("results/local_")
    )


def iter_package_files(root: Path = ROOT) -> Iterable[tuple[str, Path]]:
    """Yield every manifested file and fail closed on symbolic links."""

    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError(f"symbolic links are forbidden in the package: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        validate_relative_path(relative)
        if is_excluded(relative, path):
            continue
        yield relative, path


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    records = []
    for relative, path in iter_package_files(ROOT):
        records.append(
            {
                "path": relative,
                "size": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )

    sums = "".join(
        f"{record['sha256']}  {record['path']}\n" for record in records
    )
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "file_count": len(records),
        "files": records,
    }
    rendered = json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"
    atomic_text(ROOT / "SHA256SUMS.txt", sums)
    atomic_text(ROOT / "MANIFEST.json", rendered)
    print(
        json.dumps(
            {
                "author": AUTHOR,
                "file_count": len(records),
                "schema": MANIFEST_SCHEMA,
                "version": VERSION,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
