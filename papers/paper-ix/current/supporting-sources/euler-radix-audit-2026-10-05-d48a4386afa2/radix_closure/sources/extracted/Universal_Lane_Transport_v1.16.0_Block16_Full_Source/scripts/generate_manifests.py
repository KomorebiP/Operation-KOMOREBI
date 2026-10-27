from __future__ import annotations

from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def skipped(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_PARTS or part.endswith("_render") or part.endswith("_renders") for part in rel.parts):
        return True
    name = path.name
    if name in {"REPOSITORY_MANIFEST_SHA256.txt", "SOURCE_MANIFEST_SHA256.txt", "MANIFEST.sha256"}:
        return True
    if any(name.endswith(suffix) for suffix in BUILD_SUFFIXES):
        return True
    return False


def write_manifest(path: Path, files: list[Path], base: Path) -> None:
    lines = [f"{digest(item)}  {item.relative_to(base).as_posix()}" for item in sorted(files)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


repo_files = [path for path in ROOT.rglob("*") if path.is_file() and not skipped(path)]
write_manifest(ROOT / "REPOSITORY_MANIFEST_SHA256.txt", repo_files, ROOT)

manuscript = ROOT / "manuscript"
source_files = [
    path for path in manuscript.rglob("*")
    if path.is_file()
    and not skipped(path)
    and path.suffix.lower() != ".pdf"
    and "results" not in path.relative_to(manuscript).parts
]
write_manifest(manuscript / "SOURCE_MANIFEST_SHA256.txt", source_files, manuscript)
write_manifest(manuscript / "MANIFEST.sha256", source_files, manuscript)

print(ROOT / "REPOSITORY_MANIFEST_SHA256.txt")
print(manuscript / "SOURCE_MANIFEST_SHA256.txt")
print(manuscript / "MANIFEST.sha256")
