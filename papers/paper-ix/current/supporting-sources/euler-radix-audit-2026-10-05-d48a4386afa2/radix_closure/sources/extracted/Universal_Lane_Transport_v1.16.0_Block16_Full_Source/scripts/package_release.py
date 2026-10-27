from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
FIXED_TIME = (2026, 8, 31, 0, 0, 0)
BUILD_SUFFIXES = {
    ".aux", ".bbl", ".bcf", ".blg", ".fdb_latexmk", ".fls", ".lof",
    ".log", ".lot", ".out", ".run.xml", ".synctex.gz", ".toc", ".pyc",
}
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", "dist", "rendered", "contact_sheets"}


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add_file(zf: ZipFile, path: Path, arcname: str) -> None:
    info = ZipInfo(arcname.replace("\\", "/"), FIXED_TIME)
    info.compress_type = ZIP_DEFLATED
    mode = 0o100755 if path.suffix == ".sh" else 0o100644
    info.external_attr = (mode & 0xFFFF) << 16
    zf.writestr(info, path.read_bytes())


def skipped(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_PARTS or part.endswith("_render") or part.endswith("_renders") for part in rel.parts):
        return True
    if any(path.name.endswith(suffix) for suffix in BUILD_SUFFIXES):
        return True
    return False


def write_zip(path: Path, files: list[Path]) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for item in sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix()):
            add_file(zf, item, item.relative_to(ROOT).as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run([sys.executable, str(ROOT / "scripts" / "check_release.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_manifests.py")], check=True)

    stem = f"Universal_Lane_Transport_v{VERSION}_Block16"
    full_zip = args.output_dir / f"{stem}_Full_Source.zip"
    compact_zip = args.output_dir / f"{stem}_Research_Extension.zip"
    checksums = args.output_dir / f"{stem}_SHA256SUMS.txt"

    full_files = [path for path in ROOT.rglob("*") if path.is_file() and not skipped(path)]
    write_zip(full_zip, full_files)

    compact_rel = [
        "README.md",
        "CHANGELOG.md",
        "CITATION.cff",
        "LICENSE",
        "VERSION",
        "requirements.txt",
        "docs/CLAIMS_AND_SCOPE.md",
        "docs/THEOREM_MAP.md",
        "docs/INDEPENDENT_REVIEW_GUIDE.md",
        "docs/BUILD_AND_REPRODUCIBILITY.md",
        "release/Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf",
        "release/Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.pdf",
        "release/VALIDATION.md",
        "release/PDF_PREFLIGHT.json",
        "release/SHA256SUMS.txt",
        "release/block16_holonomy_lane_transport_validation.json",
        "release/block16_publication_audit.json",
        "theorem/Universal_Lane_Transport_Theorem_section.tex",
        "theorem/Holonomy_Twisted_Lane_Transport_section.tex",
        "standalone/Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex",
        "standalone/README.md",
        "manuscript/block16_section.tex",
        "manuscript/verify_block15_lane_transport.py",
        "manuscript/verify_block16_holonomy_lane_transport.py",
        "manuscript/verify_block16_publication_audit.py",
        "manuscript/Komorebi_Theorem_Concordance_v0.3.json",
        "manuscript/results/block15_lane_transport_validation.json",
        "manuscript/results/block16_holonomy_lane_transport_validation.json",
        "manuscript/results/block16_publication_audit.json",
        "manuscript/generated/block16_counts.tex",
        "manuscript/generated/block16_validation_table.tex",
        "manuscript/generated/block16_publication_counts.tex",
        "manuscript/generated/block16_publication_audit_table.tex",
        "manuscript/CHANGELOG_Block16.md",
        "manuscript/PROGRESS_Block16.md",
        "manuscript/VALIDATION_Block16.md",
        "scripts/check_release.py",
    ]
    compact_files = [ROOT / rel for rel in compact_rel]
    missing = [path.relative_to(ROOT) for path in compact_files if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing compact package files: " + ", ".join(map(str, missing)))
    write_zip(compact_zip, compact_files)

    records = [
        ROOT / "release" / "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf",
        ROOT / "release" / "Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.pdf",
        compact_zip,
        full_zip,
    ]
    checksums.write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in records),
        encoding="utf-8",
    )

    for path in records + [checksums]:
        print(path)


if __name__ == "__main__":
    main()
