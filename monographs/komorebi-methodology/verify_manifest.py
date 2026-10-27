"""Verify the complete inventory and byte hashes of a delivered source package.

Python 3.10+, standard library only. Run before rebuilding the package.
This is integrity relative to the supplied manifest, not authentication or proof.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path, PurePosixPath

MANIFEST_NAME = "MANIFEST_SHA256.txt"


def verify(root: Path) -> tuple[int, list[str], int]:
    """Return (exit code, diagnostics, checked hashes). Never accept an empty record."""
    root = root.resolve()
    manifest = root / MANIFEST_NAME
    if manifest.is_symlink():
        return 1, ["Manifest must not be a symbolic link."], 0
    try:
        records = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return 2, [f"Cannot read manifest: {exc}"], 0

    failures: list[str] = []
    listed: set[str] = set()
    checked = 0
    for line_number, record in enumerate(records, 1):
        if not record.strip() or record.startswith("#"):
            continue
        try:
            expected, relative = record.split("  ", 1)
            if not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError("invalid SHA-256 digest")
            path = PurePosixPath(relative)
            # Keep the inventory portable and do not normalize away unsafe paths.
            if (not relative or relative != path.as_posix() or path.is_absolute()
                    or any(p in {".", ".."} for p in path.parts)
                    or "\\" in relative or ":" in relative or "\x00" in relative):
                raise ValueError("unsafe or noncanonical relative path")
            if relative == MANIFEST_NAME:
                raise ValueError("the manifest must not list itself")
            if relative in listed:
                raise ValueError(f"duplicate inventory entry: {relative}")
            listed.add(relative)
            if any((root.joinpath(*path.parts[:i])).is_symlink()
                   for i in range(1, len(path.parts)+1)):
                raise ValueError(f"symbolic links are not permitted: {relative}")
            target = root.joinpath(*path.parts)
            if not target.resolve().is_relative_to(root):
                raise ValueError("path escapes the package directory")
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            checked += 1
            if actual != expected:
                failures.append(f"Digest mismatch: {relative}")
        except (OSError, ValueError, RuntimeError) as exc:
            failures.append(f"Manifest line {line_number}: {exc}")

    if not listed:
        failures.append("Manifest contains no file records.")

    actual_files: set[str] = set()
    try:
        for directory, dirnames, filenames in os.walk(root, followlinks=False, onerror=lambda exc: failures.append(f"Cannot inspect inventory: {exc}")):
            directory = Path(directory)
            for name in list(dirnames):
                item = directory / name
                if item.is_symlink():
                    failures.append(f"Symbolic directory is not permitted: {item.relative_to(root).as_posix()}")
                    dirnames.remove(name)
            for name in filenames:
                item = directory / name
                relative = item.relative_to(root).as_posix()
                if relative == MANIFEST_NAME:
                    continue
                actual_files.add(relative)
                if item.is_symlink():
                    failures.append(f"Symbolic file is not permitted: {relative}")
    except OSError as exc:
        failures.append(f"Cannot inspect package inventory: {exc}")
    for relative in sorted(actual_files - listed):
        failures.append(f"Unlisted file: {relative}")
    for relative in sorted(listed - actual_files):
        failures.append(f"Missing inventory file: {relative}")
    return (1 if failures else 0), failures, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="Directory containing the manifest and payload.")
    args = parser.parse_args()
    code, failures, checked = verify(args.root)
    if failures:
        print("Integrity check failed:\n" + "\n".join(failures), file=sys.stderr)
    else:
        print(f"PASS: complete inventory of {checked} files matches the delivered manifest.")
        print("This checks integrity relative to the manifest, not authenticity or mathematical correctness.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
