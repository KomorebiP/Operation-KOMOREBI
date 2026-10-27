#!/usr/bin/env python3
"""Build a checked source archive, excluding transient document QA and TeX files."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
SKIP_NAMES = {"BUNDLE_INDEX.json", "SHA256SUMS.txt"}
SKIP_DIRS = {"qa", "__pycache__", "build_logs"}
TEX_INTERMEDIATES = {".aux", ".out", ".toc", ".synctex", ".gz"}

def include(path):
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if path.name in SKIP_NAMES and len(rel.parts) == 1:
        return False
    if path.suffix in TEX_INTERMEDIATES:
        return False
    if rel.parts[0] in {"traditional", "visual", "lean"} and len(rel.parts) == 2:
        if path.suffix == ".log" or path.name.startswith("build_") and path.suffix == ".log":
            return False
    return path.is_file()

def main():
    files = sorted((p for p in ROOT.rglob("*") if include(p)), key=lambda p: str(p.relative_to(ROOT)))
    records = [{"path": p.relative_to(ROOT).as_posix(), "size_bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    index = {"edition": "2026-10-06", "author": "Komorebi P.", "files": records, "boundary": "Payload inventory and hashes, not mathematical proof certification. The frozen upstream archive has its own internal members."}
    (ROOT/"BUNDLE_INDEX.json").write_text(json.dumps(index, indent=2)+"\n")
    (ROOT/"SHA256SUMS.txt").write_text("".join(f"{r['sha256']}  {r['path']}\n" for r in records))
    files += [ROOT/"BUNDLE_INDEX.json", ROOT/"SHA256SUMS.txt"]
    archive = ROOT.parent / "Komorebi_Stratified_Universality_Final_Edition_2026-10-06.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(files, key=lambda p: str(p.relative_to(ROOT))):
            entry = zipfile.ZipInfo(ROOT.name+"/"+path.relative_to(ROOT).as_posix(), date_time=(2026,10,6,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o100755 if path.suffix == ".sh" else 0o100644
            entry.external_attr = mode << 16
            bundle.writestr(entry, path.read_bytes())
    with zipfile.ZipFile(archive) as bundle:
        bad = bundle.testzip()
        if bad:
            raise RuntimeError(f"ZIP integrity failure: {bad}")
        for record in records:
            data = bundle.read(ROOT.name+"/"+record["path"])
            if len(data) != record["size_bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise RuntimeError(f"Archived payload mismatch: {record['path']}")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n")
    print(json.dumps({"archive":str(archive),"members":len(files),"bytes":archive.stat().st_size,"sha256":digest,"payload_hashes_verified":len(records)},indent=2))

if __name__ == "__main__":
    main()
