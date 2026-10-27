"""Verify the complete OSL lineage bundle using only the Python standard library."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import zipfile


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "BUNDLE_MANIFEST.json"
CHECKSUM_PATH = ROOT / "SHA256SUMS.txt"
REPORT_PATH = ROOT / "BUNDLE_VERIFICATION_REPORT.json"
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache"}
EXCLUDED_TOP_LEVEL = {"packages", "lineage_notes", "original_archives"}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def included_files() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and path != CHECKSUM_PATH
        and path.suffix != ".pyc"
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
        and path.relative_to(ROOT).parts[0] not in EXCLUDED_TOP_LEVEL
    ]


def verify_checksums(errors: list[str]) -> int:
    if not CHECKSUM_PATH.is_file():
        errors.append("SHA256SUMS.txt is missing")
        return 0
    entries: dict[str, str] = {}
    for line_number, line in enumerate(CHECKSUM_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed checksum line {line_number}")
            continue
        if relative in entries:
            errors.append(f"duplicate checksum path {relative}")
        entries[relative] = expected
    expected_paths = {path.relative_to(ROOT).as_posix() for path in included_files()}
    if set(entries) != expected_paths:
        errors.append("checksum manifest file set does not match bundle file set")
    for relative, expected in entries.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing file {relative}")
        elif sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"checksum mismatch for {relative}")
    return len(entries)


def verify_package(package: dict, errors: list[str]) -> dict:
    expanded = ROOT / package["expanded_path"]
    archive = ROOT / package["archive_path"]
    expanded_files = sorted(path for path in expanded.rglob("*") if path.is_file()) if expanded.is_dir() else []
    expanded_bytes = sum(path.stat().st_size for path in expanded_files)
    archive_size = archive.stat().st_size if archive.is_file() else None
    archive_digest = sha256(archive.read_bytes()).hexdigest() if archive.is_file() else None
    archive_crc_valid = False
    if archive.is_file():
        try:
            with zipfile.ZipFile(archive) as handle:
                archive_crc_valid = handle.testzip() is None
        except (OSError, zipfile.BadZipFile):
            archive_crc_valid = False
    checks = {
        "expanded_file_count": len(expanded_files) == package["expanded_file_count"],
        "expanded_bytes": expanded_bytes == package["expanded_bytes"],
        "archive_bytes": archive_size == package["archive_bytes"],
        "archive_sha256": archive_digest == package["archive_sha256"],
        "archive_crc": archive_crc_valid,
    }
    if not all(checks.values()):
        errors.append(f"package verification failed for {package['expanded_path']}")
    return {
        "release": package["release"],
        "expanded_path": package["expanded_path"],
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)
    errors: list[str] = []
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    packages = [verify_package(package, errors) for package in manifest["packages"]]
    checksum_entries = verify_checksums(errors)
    report = {
        "schema": "osl.complete-lineage.bundle-verification.v1",
        "bundle": manifest["bundle_name"],
        "all_checks_pass": not errors,
        "checksum_entries": checksum_entries,
        "packages": packages,
        "errors": errors,
    }
    if args.write_report:
        REPORT_PATH.write_text(canonical_json(report) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
