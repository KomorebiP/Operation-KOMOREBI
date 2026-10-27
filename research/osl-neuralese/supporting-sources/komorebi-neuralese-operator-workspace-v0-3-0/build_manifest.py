#!/usr/bin/env python3
"""Build the v0.3.0 package manifest and complete checksum inventory.

The command first runs every non-manifest evidence and integrity check.  It
refuses to seal an incomplete, stale, or internally inconsistent release tree.
The separate final verifier also runs the test suite and analysis self-checks.
Use ``--dry-run`` to perform the build-time checks without replacing generated
files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verify_package import (
    PackageVerificationError,
    VERSION,
    included_files,
    release_facts,
    sha256,
)


def _atomic_text(path: Path, value: str) -> None:
    """Replace a generated text artifact only after a complete fsync."""

    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        temporary.replace(path)
    finally:
        if not handle.closed:
            handle.close()
        temporary.unlink(missing_ok=True)


def _file_records(relative_paths: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative_text in sorted(relative_paths):
        path = ROOT / relative_text
        records.append(
            {
                "path": relative_text,
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return records


def build(*, dry_run: bool = False) -> dict[str, Any]:
    facts = release_facts()
    payload_paths = included_files(include_manifest=False)
    records = _file_records(payload_paths)
    manifest = {
        "schema": "komorebi.neuralese.package_manifest.v3",
        "version": VERSION,
        "file_count": len(records),
        "files": records,
        **facts,
    }
    if dry_run:
        return manifest
    _atomic_text(
        ROOT / "MANIFEST.json",
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    checksum_paths = included_files(include_manifest=True)
    checksums = "".join(
        f"{sha256(ROOT / relative)}  {relative}\n"
        for relative in sorted(checksum_paths)
    )
    _atomic_text(ROOT / "SHA256SUMS.txt", checksums)
    return manifest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate inputs and report the planned manifest without writing files",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        manifest = build(dry_run=args.dry_run)
    except PackageVerificationError as error:
        print(f"MANIFEST_BUILD_FAIL: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "MANIFEST_DRY_RUN_PASS" if args.dry_run else "MANIFEST_BUILD_PASS",
                "version": VERSION,
                "file_count": manifest["file_count"],
                "checksum_count": (
                    None if args.dry_run else len(included_files(include_manifest=True))
                ),
                "scientific_code_digest": manifest["scientific_code_digest"],
                "primary_scientific_gate_status": manifest["primary_outcome"][
                    "scientific_gate_status"
                ],
                "primary_passed_gates": manifest["primary_outcome"]["passed_gates"],
                "primary_failed_gates": manifest["primary_outcome"]["failed_gates"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
