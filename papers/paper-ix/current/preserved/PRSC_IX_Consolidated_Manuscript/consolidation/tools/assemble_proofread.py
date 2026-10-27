#!/usr/bin/env python3
"""Package the proofread Paper IX manuscript while preserving its prior release.

This is a release step, not a compiler or mathematical proof checker. It refuses
stale builds and reviews, then verifies every packaged byte against its manifest.
Run only after the final manuscript, indexes and reviews have been frozen.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d9a353eaeb99fc2b6e1299d712306cdecf2e71fe08fd9effffb3da3e24f371f3"
BASE_FILES = 2232
RELEASE = "PRSC_IX_Consolidated_Manuscript"
PREFIX = RELEASE + "/"
HISTORY = "historical/consolidated_pre_proofread/"
RETIRED_REVIEWS = {
    "consolidation/audit/MANUSCRIPT_REVIEW.json",
    "consolidation/audit/MANUSCRIPT_REVIEW.md",
    "consolidation/audit/PDF_VISUAL_REVIEW.json",
    "consolidation/audit/PDF_VISUAL_REVIEW.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def safe_relative(name: str) -> str:
    path = PurePosixPath(name)
    require(bool(name) and not path.is_absolute(), f"Invalid package path: {name}")
    require(".." not in path.parts and "\\" not in name, f"Unsafe package path: {name}")
    require(str(path) == name, f"Noncanonical package path: {name}")
    return name


def render_template(path: Path, values: dict[str, object]) -> bytes:
    text = path.read_text()
    for name, value in values.items():
        text = text.replace("{{" + name + "}}", str(value))
    require(not re.search(r"\{\{[A-Z_]+\}\}", text), f"Unfilled placeholder: {path}")
    return text.encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-directory", type=Path, default=ROOT)
    parser.add_argument("--base-archive", type=Path)
    parser.add_argument("--output-directory", type=Path)
    args = parser.parse_args()
    root = args.staging_directory.resolve()
    base_path = (args.base_archive or root / "before" / (RELEASE + ".zip")).resolve()
    output_dir = (args.output_directory or root.parent / "output").resolve()
    require(digest(base_path.read_bytes()) == BASE_SHA, "The immutable base archive hash does not match.")

    build_path = root / "build/BUILD_REPORT.json"
    build = load(build_path)
    require(build.get("status") == "PASS", "The final PDF build has not passed.")
    require(build.get("sources_unchanged_during_build") is True, "Sources changed during the build.")
    current_hashes = {
        str(path.relative_to(root / "manuscript")): digest(path.read_bytes())
        for path in sorted((root / "manuscript").rglob("*.tex"))
    }
    require(bool(current_hashes), "No manuscript TeX files were found.")
    require(current_hashes == build.get("source_hashes"), "The PDF build is stale relative to the current TeX.")
    pdf_path = root / "build/Paper_IX_Consolidated.pdf"
    pdf = pdf_path.read_bytes()
    pdf_sha = digest(pdf)
    require(pdf_sha == build.get("pdf_sha256"), "The PDF differs from the build report.")
    pdfinfo = subprocess.run(["pdfinfo", str(pdf_path)], text=True,
                             capture_output=True, check=True).stdout
    page_match = re.search(r"^Pages:\s+(\d+)\s*$", pdfinfo, flags=re.MULTILINE)
    require(page_match is not None, "pdfinfo did not provide a page count.")
    pages = int(page_match.group(1))

    review_paths = {
        "semantic": root / "editorial/SEMANTIC_REVIEW.json",
        "completeness": root / "editorial/COMPLETENESS_REVIEW.json",
        "visual": root / "editorial/PDF_VISUAL_REVIEW.json",
    }
    reviews = {kind: load(path) for kind, path in review_paths.items()}
    for kind in ("semantic", "completeness"):
        review = reviews[kind]
        require(review.get("status") == "PASS", f"The {kind} review has not passed.")
        require(review.get("manuscript_source_hashes") == current_hashes,
                f"The {kind} review is not bound to every current TeX source.")
    visual = reviews["visual"]
    require(visual.get("status") == "PASS", "The visual review has not passed.")
    require(visual.get("pdf_sha256") == pdf_sha and visual.get("pages") == pages,
            "The visual review is not bound to the current PDF and page count.")
    require(visual.get("pages_visually_reviewed") == pages,
            "The visual report must record inspection of every final page.")

    index_path = root / "audit/STATEMENT_INDEX.json"
    index = load(index_path)
    require(index.get("status") == "PASS", "The statement index has not passed.")
    require(index.get("manuscript_source_hashes") == current_hashes,
            "The statement index is not bound to the current TeX.")
    values = {
        "PAGE_COUNT": pages,
        "MAPPED_STATEMENTS": index["mapped_statements"],
        "SOURCE_LINKS": index["resolved_statement_source_links"],
        "PRIOR_FILE_COUNT": f"{BASE_FILES:,}",
    }

    # Collect replacements first, so every overwritten prior file can be moved
    # to history without relying on an incomplete hand-maintained path list.
    updates: dict[str, bytes] = {}
    for path in sorted((root / "manuscript").rglob("*.tex")):
        name = "manuscript/consolidated/" + str(path.relative_to(root / "manuscript"))
        updates[safe_relative(name)] = path.read_bytes()
    updates["manuscript/consolidated/Paper_IX_Consolidated.pdf"] = pdf
    for folder in ("audit", "tools", "editorial", "release_docs"):
        for path in sorted((root / folder).rglob("*")):
            if not path.is_file() or path.suffix not in {".json", ".md", ".csv", ".py"}:
                continue
            if "__pycache__" in path.parts:
                continue
            name = safe_relative("consolidation/" + folder + "/" + str(path.relative_to(root / folder)))
            if name not in RETIRED_REVIEWS:
                updates[name] = path.read_bytes()
    for name in ("BUILD_REPORT.json", "Paper_IX_Consolidated.log",
                 "latex_pass_1.txt", "latex_pass_2.txt", "latex_pass_3.txt"):
        updates["consolidation/build/" + name] = (root / "build" / name).read_bytes()
    for template, destination in {
        "README.md": "README.md",
        "REMAINING_CHECKLIST.md": "REMAINING_CHECKLIST.md",
        "MANUSCRIPT_README.md": "manuscript/README.md",
        "AUDIT_README.md": "consolidation/audit/README.md",
    }.items():
        updates[destination] = render_template(root / "release_docs" / template, values)
    for name, expected in current_hashes.items():
        require(digest(updates["manuscript/consolidated/" + name]) == expected,
                f"Manuscript changed during assembly: {name}")
    require(json.loads(updates["consolidation/build/BUILD_REPORT.json"]) == build,
            "The build report changed during assembly.")
    require(json.loads(updates["consolidation/audit/STATEMENT_INDEX.json"]) == index,
            "The statement index changed during assembly.")
    for kind, path in review_paths.items():
        require(json.loads(updates["consolidation/editorial/" + path.name]) == reviews[kind],
                f"The {kind} review changed during assembly.")

    generated = {"MANIFEST.json", "RELEASE_AUDIT.json", "PACKAGE_COMPLETENESS.json"}
    files: dict[str, bytes] = {}
    coverage: list[dict] = []
    with zipfile.ZipFile(base_path) as base:
        require(base.testzip() is None, "The base archive failed its CRC check.")
        entries = base.infolist()
        require(len(entries) == BASE_FILES, "The base archive file count has changed.")
        require(len({item.filename for item in entries}) == len(entries), "The base has duplicate paths.")
        for item in entries:
            require(not item.is_dir() and item.filename.startswith(PREFIX), "Unexpected base entry.")
            name = safe_relative(item.filename[len(PREFIX):])
            data = base.read(item)
            overwritten = name in generated or name in RETIRED_REVIEWS or (
                name in updates and updates[name] != data
            )
            destination = HISTORY + name if overwritten else name
            require(destination not in files, f"Historical path collision: {destination}")
            files[destination] = data
            coverage.append({"previous_path": name, "current_path": destination,
                             "bytes": len(data), "sha256": digest(data)})
    for name, data in updates.items():
        require(name not in files or files[name] == data, f"Unpreserved overwrite: {name}")
        files[name] = data
    relocated = sum(item["current_path"] != item["previous_path"] for item in coverage)
    files["PACKAGE_COMPLETENESS.json"] = encode({
        "status": "PASS",
        "previous_archive": base_path.name,
        "previous_archive_sha256": BASE_SHA,
        "previous_files": BASE_FILES,
        "files_preserved_by_content_hash": BASE_FILES,
        "files_relocated_to_history": relocated,
        "history_prefix": HISTORY,
        "coverage": coverage,
        "scope": "Every file in the prior consolidated archive is retained byte for byte. "
                 "Overwritten files and retired manuscript reviews are relocated to history. "
                 "This archive-preservation check does not establish mathematical completeness "
                 "over unavailable historical material.",
    })
    files["RELEASE_AUDIT.json"] = encode({
        "status": "PASS",
        "release": RELEASE,
        "author": "Komorebi P.",
        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
        "kind": "Proofreading, prose revision and source-grounded completeness restoration",
        "manuscript_pages": pages,
        "manuscript_pdf_sha256": pdf_sha,
        "manuscript_source_hashes": current_hashes,
        "mapped_statements": index["mapped_statements"],
        "resolved_statement_source_links": index["resolved_statement_source_links"],
        "retained_previous_files": BASE_FILES,
        "previous_archive_sha256": BASE_SHA,
        "Lean_sources_modified": False,
        "Lean_compilation_rerun": False,
        "review_bindings": {
            kind: {"path": "consolidation/editorial/" + path.name,
                   "sha256": digest(updates["consolidation/editorial/" + path.name])}
            for kind, path in review_paths.items()
        },
        "statement_index_sha256": digest(updates["consolidation/audit/STATEMENT_INDEX.json"]),
        "build_report_sha256": digest(updates["consolidation/build/BUILD_REPORT.json"]),
        "evidence_index_sha256": digest(updates["consolidation/audit/EVIDENCE_INDEX.json"]),
        "restored_exposition": [
            "Explicit denominator-clearing product",
            "Bernoulli boundary, with the classical derivation distinguished from Lean coverage",
            "Lucas standard-window reduction, residue independence and common period",
            "Signed zigzag coefficient identity",
            "Exact counterexample to removing the factorial loss",
            "Previously recorded native progress, with its separate evidence status",
            "Shared affine lifting at depth zero as well as positive depths",
        ],
        "remaining": [
            "General singular persistence for fraction-field rank-deficient Jacobians",
            "Native 13.2 and Native 13.3 in their unrestricted seed formulations",
            "Further exact arithmetic classifications and historical formula recovery",
            "Comparisons and extensions of every historical chart interface",
        ],
        "limits": [
            "The current reviews are bound to the identified manuscript revision; they are not new Lean compiler runs.",
            "The Bernoulli derivation and native prose/external results are not promoted to Lean-certified theorems.",
            "Earlier external-source review is retained; this editorial revision adds no fresh primary-source authentication.",
            "Original historical TeX, figure sources and the complete historical experiment package remain unavailable.",
        ],
    })
    for item in coverage:
        require(digest(files[item["current_path"]]) == item["sha256"], "Prior-file preservation failed.")
    manifest = {
        "release": RELEASE,
        "algorithm": "SHA-256",
        "manifest_excludes_itself": True,
        "file_count_excluding_manifest": len(files),
        "files": [{"path": name, "bytes": len(data), "sha256": digest(data)}
                  for name, data in sorted(files.items())],
    }
    files["MANIFEST.json"] = encode(manifest)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_zip = output_dir / (RELEASE + ".zip")
    standalone = output_dir / "Paper_IX_Consolidated.pdf"
    require(output_zip != base_path, "The output must not overwrite the immutable base archive.")
    temporary_paths = []
    try:
        with tempfile.NamedTemporaryFile(dir=output_dir, suffix=".zip", delete=False) as stream:
            temporary_zip = Path(stream.name)
        temporary_paths.append(temporary_zip)
        with zipfile.ZipFile(temporary_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, data in sorted(files.items()):
                archive.writestr(PREFIX + name, data)
        with zipfile.ZipFile(temporary_zip) as archive:
            require(archive.testzip() is None, "The completed archive failed its CRC check.")
            require(len(archive.infolist()) == len(files), "Packaged file count mismatch.")
            for item in manifest["files"]:
                data = archive.read(PREFIX + item["path"])
                require(len(data) == item["bytes"] and digest(data) == item["sha256"],
                        f"Manifest mismatch: {item['path']}")
            for item in coverage:
                require(digest(archive.read(PREFIX + item["current_path"])) == item["sha256"],
                        f"Previous content lost: {item['previous_path']}")
            require(archive.read(PREFIX + "MANIFEST.json") == files["MANIFEST.json"],
                    "The packaged manifest differs from the generated manifest.")
        with tempfile.NamedTemporaryFile(dir=output_dir, suffix=".pdf", delete=False) as stream:
            temporary_pdf = Path(stream.name)
            stream.write(pdf)
        temporary_paths.append(temporary_pdf)
        os.replace(temporary_zip, output_zip)
        os.replace(temporary_pdf, standalone)
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)
    print(json.dumps({
        "status": "PASS", "zip": str(output_zip), "files": len(files),
        "bytes": output_zip.stat().st_size, "sha256": digest(output_zip.read_bytes()),
        "prior_files_preserved": BASE_FILES, "prior_files_relocated": relocated,
        "pdf": str(standalone), "pdf_pages": pages, "pdf_sha256": pdf_sha,
    }, indent=2))


if __name__ == "__main__":
    main()
