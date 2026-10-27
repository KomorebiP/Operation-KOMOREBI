#!/usr/bin/env python3
"""Create deterministic source and release archives for the bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


TITLE = (
    "Covariant Refinement-Fiber Dynamics: Symmetry Classification, "
    "Constraint Closure, Backreaction, and Radiative Bounds"
)
VERSION = "1.0.0"
RELEASE_DATE = "2026-08-19"
STEM = "Projector_Refinement_Physics_Covariant_Backreaction_Bridge"
ZIP_TIME = (2026, 8, 19, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def base_files(root: Path) -> list[Path]:
    top_level = [
        f"{STEM}.tex",
        "README.md",
        "CLAIM_STATUS.md",
        "RELEASE_NOTES.md",
        "REPRODUCIBILITY.md",
        "VERSION",
        "CITATION.cff",
        "RIGHTS.md",
        "requirements.txt",
        "claim_registry.csv",
        "parameter_registry.csv",
        "build.sh",
        "build.ps1",
        "generated_values.tex",
    ]
    files = [root / relative for relative in top_level]
    for directory, pattern in (
        ("code", "*.py"),
        ("data", "*"),
        ("figures", "*"),
        ("parent", "*"),
        ("source", "*.tex"),
    ):
        files.extend(
            path for path in sorted((root / directory).glob(pattern)) if path.is_file()
        )
    return sorted(set(files), key=lambda path: str(path.relative_to(root)))


def entry(root: Path, path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def write_zip(path: Path, root: Path, members: list[Path]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member in members:
            relative = str(member.relative_to(root))
            info = zipfile.ZipInfo(relative, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if member.name in {"build.sh"} else 0o644) << 16
            archive.writestr(info, member.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    pdf = args.pdf.resolve()
    output = args.output.resolve()
    if not pdf.is_file():
        raise SystemExit(f"missing validated PDF: {pdf}")
    output.mkdir(parents=True, exist_ok=True)

    files = base_files(root)
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise SystemExit(f"missing source members: {missing}")

    manifest = {
        "schema": "operation-komorebi.source-release.v1",
        "title": TITLE,
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "claim_boundary": (
            "Internally verified research bridge, not independent reproduction, "
            "literature priority, or empirical confirmation"
        ),
        "files": [entry(root, path) for path in files],
    }
    manifest_path = root / "RELEASE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    content_members = files + [manifest_path]
    sums_path = root / "SOURCE_CONTENT_SHA256SUMS.txt"
    sums_path.write_text(
        "\n".join(
            f"{sha256(path)}  {path.relative_to(root)}" for path in content_members
        )
        + "\n",
        encoding="utf-8",
    )
    source_members = content_members + [sums_path]

    source_zip = output / f"{STEM}_Source_and_Reproducibility_v{VERSION}.zip"
    write_zip(source_zip, root, source_members)

    release_pdf = output / f"{STEM}_v{VERSION}.pdf"
    shutil.copyfile(pdf, release_pdf)

    release_sums = output / "SHA256SUMS.txt"
    release_sums.write_text(
        f"{sha256(release_pdf)}  {release_pdf.name}\n"
        f"{sha256(source_zip)}  {source_zip.name}\n",
        encoding="utf-8",
    )

    bundle = output / f"{STEM}_Release_Bundle_v{VERSION}.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member in (release_pdf, source_zip, release_sums):
            info = zipfile.ZipInfo(member.name, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, member.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    print(
        json.dumps(
            {
                "pdf": str(release_pdf),
                "source_zip": str(source_zip),
                "bundle": str(bundle),
                "source_files": len(source_members),
                "pdf_sha256": sha256(release_pdf),
                "source_zip_sha256": sha256(source_zip),
                "bundle_sha256": sha256(bundle),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
