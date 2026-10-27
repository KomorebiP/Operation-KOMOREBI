#!/usr/bin/env python3
"""Package the audited 1.0 source and evidence, with byte-level verification."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
NAME = "Komorebi_Special_Function_Discovery_v1.0"
EXCLUDED_NAMES = {"main.aux", "main.log", "main.out", "main.toc",
                  "package_manifest.json", "SHA256SUMS"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    qa = json.loads((ROOT / "evidence/final_qa.json").read_text())
    assert qa["status"] == "passed"
    assert qa["pdf_sha256"] == sha256(ROOT / "main.pdf")
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts
                   and p.suffix != ".pyc" and p.name not in EXCLUDED_NAMES)
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in paths}
    manifest = {
        "checkpoint": "SF-DISCOVERY-100", "author": "Komorebi P.",
        "pdf_pages": 75, "unique_figures": 18, "proof_appendices": 5,
        "sequence_rows": 18, "exact_assertions": 19871, "numerical_assertions": 5576,
        "files": hashes,
        "hash_scope": "Every packaged source/evidence file except this manifest and SHA256SUMS; SHA256SUMS also covers this manifest.",
        "excluded": ["LaTeX transient files", "Python bytecode/cache", "page-render QA previews outside this project", "external dependencies and third-party papers"],
        "review": ["evidence/v1_independent_audit.md", "evidence/v1_manuscript_review.md", "evidence/v1_visual_review.md", "evidence/final_qa.json"],
        "novelty": "Unresolved for candidate extensions; established mechanisms attributed separately.",
    }
    manifest_path = ROOT / "package_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    paths.append(manifest_path)
    sums = ROOT / "SHA256SUMS"
    sums.write_text("".join(f"{sha256(p)}  {p.relative_to(ROOT)}\n" for p in sorted(paths)))
    paths.append(sums)
    pdf_out = ROOT.parent / (NAME + ".pdf")
    archive = ROOT.parent / (NAME + "_Source.zip")
    shutil.copy2(ROOT / "main.pdf", pdf_out)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(paths):
            name = f"{ROOT.name}/{path.relative_to(ROOT)}"
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(paths)
        for path in paths:
            member = f"{ROOT.name}/{path.relative_to(ROOT)}"
            assert hashlib.sha256(z.read(member)).hexdigest() == sha256(path), member
    assert sha256(pdf_out) == qa["pdf_sha256"]
    print(json.dumps({"status": "verified", "files": len(paths),
                      "pdf": str(pdf_out), "pdf_sha256": sha256(pdf_out),
                      "archive": str(archive), "archive_sha256": sha256(archive),
                      "archive_bytes": archive.stat().st_size}))


if __name__ == "__main__":
    main()
