"""Package the final manuscripts, selected evidence, figures and validation records."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "output"
PDF_OUTPUT = OUTPUT / "pdf"
PDF_OUTPUT.mkdir(parents=True, exist_ok=True)
required = [
    "collatz/SOURCES.md", "collatz/PROOFREADING.md",
    "riemann/SOURCES.md", "riemann/PROOFREADING.md",
    "shared/REVIEW_v1.1.md", "shared/LAYOUT_VALIDATION_v1.1.json", "AUTHORING_REPORT_v1.1.md",
    "collatz_visual/PROOFREADING.md", "riemann_visual/PROOFREADING.md",
    "pdf/Komorebi_Collatz_Conjecture_Piece_v1.1.pdf",
    "pdf/Komorebi_Riemann_Conjecture_Piece_v1.1.pdf",
    "pdf/Komorebi_Collatz_Visual_Guide_v1.1.pdf",
    "pdf/Komorebi_Riemann_Visual_Guide_v1.1.pdf",
]
for relative in required:
    if not (ROOT / relative).is_file():
        raise SystemExit(f"Required final file is missing: {relative}")

def include(path):
    relative = path.relative_to(ROOT)
    if relative.parts[:2] == ("shared", "review_expansion_run"):
        return False
    if "__pycache__" in relative.parts:
        return False
    if path.name == "MANIFEST.json" or path.suffix in {".aux", ".log", ".out", ".toc", ".pyc"}:
        return False
    if len(relative.parts) == 2 and relative.parts[0] in {"collatz", "riemann", "collatz_visual", "riemann_visual"} and path.name == "main.pdf":
        return False
    return True

files = sorted(path for path in ROOT.rglob("*") if path.is_file() and include(path))
entries = [{
    "path": path.relative_to(ROOT).as_posix(),
    "bytes": path.stat().st_size,
    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
} for path in files]
manifest = ROOT / "MANIFEST.json"
manifest.write_text(json.dumps({
    "edition": "1.1", "date": "2026-10-08", "author": "Komorebi P.",
    "scope": "Expanded monographs, separate visual guides, figures, selected recovered evidence and audit records",
    "self_excluded": "MANIFEST.json", "files": entries,
}, indent=2) + "\n")

archive = OUTPUT / "Komorebi_Collatz_and_Riemann_Source_and_Evidence_v1.1.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for path in files + [manifest]:
        bundle.write(path, "Komorebi_Conjecture_Set_v1.1/" + path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as bundle:
    bad = bundle.testzip()
    if bad:
        raise SystemExit(f"Archive CRC failure: {bad}")
    for entry in entries:
        data = bundle.read("Komorebi_Conjecture_Set_v1.1/" + entry["path"])
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise SystemExit(f"Manifest mismatch: {entry['path']}")
for pdf in sorted((ROOT / "pdf").glob("*.pdf")):
    target = PDF_OUTPUT / pdf.name
    shutil.copyfile(pdf, target)
    print(target)
print(archive)
print(f"Verified {len(entries)} payload files, plus the manifest")
