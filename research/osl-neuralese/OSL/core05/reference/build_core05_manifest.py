#!/usr/bin/env python3
"""Build deterministic integrity metadata for the OSL-Core 0.5 release."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "osl.core05.release-manifest.v1"
RELEASE_NAME = "OSL-Core 0.5 Semantic Independence v0.1.0"
GENERATED_NAMES = {
    "MANIFEST.json",
    "SHA256SUMS",
    ".MANIFEST.json.core05.tmp",
    ".SHA256SUMS.core05.tmp",
}
EXCLUDED_PARTS = {
    ".core05_venv",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    ".git",
    ".svn",
    "htmlcov",
}
TRANSIENT_NAMES = {".coverage", "coverage.xml", ".DS_Store"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo", ".tmp", ".part"}
EXCLUDED_TOP_LEVEL = {"tmp"}
OUTPUT_TRANSIENT_PARTS = {"tmp", "_tmp", "render", "renders", "_render"}
REQUIRED_RELEASE_PATHS = {
    "output/pdf/OSL_Core_0.5_Semantic_Independence_Technical_Update.pdf",
    "reference/build_core05_pdf.py",
}
EXCLUDED_RELATIVE_PATHS = {
    "verify_core04.sh",
    "verify_core04.ps1",
    "reference/build_core04_manifest.py",
    "reference/build_core04_archive.py",
    "reference/generate_core04_evidence.py",
    "reference/generate_core04_bridge_report.py",
    "reference/generate_core04_adversarial_report.py",
    "reference/verify_core04_package.py",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def excluded(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    if relative.as_posix() in EXCLUDED_RELATIVE_PATHS:
        return True
    if relative.parts and relative.parts[0] in EXCLUDED_TOP_LEVEL:
        return True
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return True
    if path.name in GENERATED_NAMES or path.name in TRANSIENT_NAMES:
        return True
    if path.name == f"{root.name}.zip":
        return True
    if (
        relative.parts
        and relative.parts[0] == "output"
        and any(part in OUTPUT_TRANSIENT_PARTS for part in relative.parts[1:])
    ):
        return True
    return path.suffix.lower() in TRANSIENT_SUFFIXES


def collect_release_files(root: Path) -> tuple[list[Path], list[str]]:
    paths = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
    symlinks = [
        path.relative_to(root).as_posix()
        for path in paths
        if not excluded(root, path) and path.is_symlink()
    ]
    files = [
        path
        for path in paths
        if not excluded(root, path) and not path.is_symlink() and path.is_file()
    ]
    return files, symlinks


def build_payload(root: Path) -> tuple[dict[str, Any], str, list[str]]:
    files, symlinks = collect_release_files(root)
    records: list[dict[str, Any]] = []
    for path in files:
        data = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    payload: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "release": RELEASE_NAME,
        "archive_name": f"{root.name}.zip",
        "file_count": len(records),
        "files": records,
    }
    payload["manifest_digest"] = digest(payload)
    sums = "".join(
        f"{record['sha256']}  {record['path']}\n" for record in records
    )
    return payload, sums, symlinks


def atomic_write_text(path: Path, temporary_name: str, text: str) -> None:
    temporary = path.parent / temporary_name
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="release directory (defaults to this script's package root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="enumerate and hash inputs without writing manifest files",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(json.dumps({"all_checks_pass": False, "failure": "root_not_directory"}))
        return 1

    try:
        payload, sums, symlinks = build_payload(root)
    except OSError as exc:
        print(
            json.dumps(
                {
                    "all_checks_pass": False,
                    "failure": "release_input_read",
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    if symlinks:
        print(
            json.dumps(
                {
                    "all_checks_pass": False,
                    "failure": "symlinks_not_permitted",
                    "paths": symlinks,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    listed_paths = {record["path"] for record in payload["files"]}
    missing_required = sorted(REQUIRED_RELEASE_PATHS - listed_paths)
    if missing_required:
        print(
            json.dumps(
                {
                    "all_checks_pass": False,
                    "failure": "required_release_deliverable_missing",
                    "paths": missing_required,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    if not args.dry_run:
        atomic_write_text(
            root / "MANIFEST.json",
            ".MANIFEST.json.core05.tmp",
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        )
        atomic_write_text(
            root / "SHA256SUMS",
            ".SHA256SUMS.core05.tmp",
            sums,
        )

    result = {
        "schema": MANIFEST_SCHEMA,
        "all_checks_pass": True,
        "dry_run": args.dry_run,
        "file_count": payload["file_count"],
        "manifest_digest": payload["manifest_digest"],
        "archive_name": payload["archive_name"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
