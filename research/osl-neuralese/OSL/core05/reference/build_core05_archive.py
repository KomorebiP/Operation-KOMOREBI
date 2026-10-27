#!/usr/bin/env python3
"""Build the deterministic distributable ZIP for OSL-Core 0.5."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile


FIXED_TIMESTAMP = (2026, 9, 1, 0, 0, 0)
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
TRANSIENT_NAMES = {
    ".coverage",
    "coverage.xml",
    ".DS_Store",
    ".MANIFEST.json.core05.tmp",
    ".SHA256SUMS.core05.tmp",
}
TRANSIENT_SUFFIXES = {".pyc", ".pyo", ".tmp", ".part"}
EXCLUDED_TOP_LEVEL = {"tmp"}
OUTPUT_TRANSIENT_PARTS = {"tmp", "_tmp", "render", "renders", "_render"}
REQUIRED_RELEASE_PATHS = {
    "MANIFEST.json",
    "SHA256SUMS",
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


def excluded(root: Path, path: Path, output: Path, temporary: Path) -> bool:
    relative = path.relative_to(root)
    if relative.as_posix() in EXCLUDED_RELATIVE_PATHS:
        return True
    if relative.parts and relative.parts[0] in EXCLUDED_TOP_LEVEL:
        return True
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return True
    if path.name in TRANSIENT_NAMES or path.suffix.lower() in TRANSIENT_SUFFIXES:
        return True
    if (
        relative.parts
        and relative.parts[0] == "output"
        and any(part in OUTPUT_TRANSIENT_PARTS for part in relative.parts[1:])
    ):
        return True
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path.absolute()
    if resolved in {output, temporary}:
        return True
    return path.name == f"{root.name}.zip"


def collect_release_files(
    root: Path, output: Path, temporary: Path
) -> tuple[list[Path], list[str]]:
    paths = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
    symlinks = [
        path.relative_to(root).as_posix()
        for path in paths
        if not excluded(root, path, output, temporary) and path.is_symlink()
    ]
    files = [
        path
        for path in paths
        if not excluded(root, path, output, temporary)
        and not path.is_symlink()
        and path.is_file()
    ]
    return files, symlinks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="release directory (defaults to this script's package root)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="ZIP path (defaults to the release directory's parent)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and enumerate inputs without creating a ZIP",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(json.dumps({"all_checks_pass": False, "failure": "root_not_directory"}))
        return 1
    output = (
        args.output.resolve()
        if args.output is not None
        else root.parent / f"{root.name}.zip"
    )
    if output.suffix.lower() != ".zip":
        print(json.dumps({"all_checks_pass": False, "failure": "output_not_zip"}))
        return 1
    temporary = output.parent / f".{output.name}.core05.tmp"

    files, symlinks = collect_release_files(root, output, temporary)
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
    present = {path.relative_to(root).as_posix() for path in files}
    missing = sorted(REQUIRED_RELEASE_PATHS - present)
    if missing:
        print(
            json.dumps(
                {
                    "all_checks_pass": False,
                    "failure": "required_release_file_missing",
                    "paths": missing,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    if args.dry_run:
        print(
            json.dumps(
                {
                    "all_checks_pass": True,
                    "dry_run": True,
                    "archive": output.name,
                    "file_count": len(files),
                    "fixed_timestamp": "2026-09-01T00:00:00",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            archive.comment = b""
            for path in files:
                relative = Path(root.name) / path.relative_to(root)
                info = zipfile.ZipInfo(relative.as_posix(), date_time=FIXED_TIMESTAMP)
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (
                    (0o100755 if path.suffix.lower() == ".sh" else 0o100644) << 16
                )
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        with zipfile.ZipFile(temporary, "r") as archive:
            bad_member = archive.testzip()
        if bad_member is not None:
            raise OSError(f"ZIP CRC failure: {bad_member}")
        os.replace(temporary, output)
    except (OSError, zipfile.BadZipFile) as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        print(
            json.dumps(
                {
                    "all_checks_pass": False,
                    "failure": "archive_build",
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    payload = {
        "all_checks_pass": True,
        "dry_run": False,
        "archive": output.name,
        "file_count": len(files),
        "size_bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "fixed_timestamp": "2026-09-01T00:00:00",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
