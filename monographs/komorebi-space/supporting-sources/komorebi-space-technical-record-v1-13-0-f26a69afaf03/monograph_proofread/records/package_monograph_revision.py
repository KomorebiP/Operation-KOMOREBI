#!/usr/bin/env python3
"""Package the frozen final monograph proofreading revision.

This script is intentionally inert until invoked with a final PDF and a final
review summary. It does not compile books, revise sources, run Lean, or generate
the independent delivery-verification report.

Required summary fields:
  pdf_sha256: SHA-256 of the exact reviewed PDF
  pdf_pages: positive physical page count
  source_hashes: {"source/relative/path": SHA-256} for every source file
  changed_sources: [{"file": path, "before_sha256": hash, "after_sha256": hash}]
  reviewed_physical_pages: all integers from 1 through pdf_pages
  qa_complete: true
  unresolved_issues: []
Optional fields editorial_summary and validation are copied into the concise
publication review. The full supplied summary is retained in the technical ZIP.

Usage (from the publication working directory):
  python3 records/package_monograph_revision.py --pdf build/FINAL.pdf \
      --summary records/FINAL_PROOFREAD_SUMMARY.json
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

VERSION = "1.13.0"
PUBLIC_ROOT = f"Komorebi_Space_Publication_v{VERSION}"
TECH_ROOT = f"Komorebi_Space_Technical_Record_v{VERSION}"
MONOGRAPH = f"Komorebi_Space_Monograph_v{VERSION}.pdf"
EXTERNAL_REPORT = f"Komorebi_Space_Publication_Verification_v{VERSION}.json"
PUBLIC_ALLOWLIST = {"README.md", "books", "source", "lean", "examples", "tools", "verification"}
BUILD_SUFFIXES = {".json", ".log", ".aux", ".toc", ".fls", ".out", ".txt", ".md", ".csv", ".fdb_latexmk"}
SIGNED_URL = re.compile(
    rb"https?://[^\s\"<>]*[?&](?:sig|X-Amz-Signature|X-Goog-Signature|access_token)=",
    re.IGNORECASE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def safe_relative(name: str) -> str:
    require(bool(name) and "\\" not in name and "\x00" not in name, f"Unsafe path: {name!r}")
    parts = name.split("/")
    require(not name.startswith("/") and all(p not in {"", ".", ".."} for p in parts), f"Unsafe path: {name!r}")
    require(not any(":" in p for p in parts), f"Unsafe path: {name!r}")
    require(str(PurePosixPath(name)) == name, f"Noncanonical path: {name!r}")
    return name


def regular_file(path: Path) -> bytes:
    require(not path.is_symlink() and path.is_file(), f"Expected regular file: {path}")
    return path.read_bytes()


def collect_tree(root: Path, relative: str) -> dict[str, bytes]:
    base = root / relative
    require(base.is_dir() and not base.is_symlink(), f"Missing directory: {base}")
    result: dict[str, bytes] = {}
    for path in sorted(base.rglob("*")):
        require(not path.is_symlink(), f"Symlink not allowed: {path}")
        if path.is_dir():
            continue
        name = safe_relative(path.relative_to(root).as_posix())
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        result[name] = regular_file(path)
    return result


def validate_manifest(payload: dict[str, bytes], description: str) -> None:
    require("SHA256SUMS" in payload, f"Missing manifest: {description}")
    manifest: dict[str, str] = {}
    for line in payload["SHA256SUMS"].decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"Malformed manifest line in {description}")
        expected, name = match.groups()
        safe_relative(name)
        require(name not in manifest, f"Duplicate manifest name in {description}: {name}")
        manifest[name] = expected
    require(set(manifest) == set(payload) - {"SHA256SUMS"}, f"Incomplete manifest in {description}")
    for name, expected in manifest.items():
        require(digest(payload[name]) == expected, f"Manifest hash mismatch in {description}: {name}")


def read_archive(path: Path, expected_root: str) -> dict[str, bytes]:
    regular_file(path)
    payload: dict[str, bytes] = {}
    names: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            safe_relative(item.filename)
            require(item.filename not in names, f"Duplicate archive name: {item.filename}")
            names.add(item.filename)
            require(not item.is_dir(), f"Unexpected directory member: {item.filename}")
            mode = item.external_attr >> 16
            require(stat.S_IFMT(mode) in {0, stat.S_IFREG}, f"Nonregular archive member: {item.filename}")
            prefix = expected_root + "/"
            require(item.filename.startswith(prefix), f"Unexpected archive root: {item.filename}")
            relative = safe_relative(item.filename[len(prefix):])
            payload[relative] = archive.read(item)
        require(archive.testzip() is None, f"CRC failure: {path}")
    validate_manifest(payload, path.name)
    return payload


def add_manifest(payload: dict[str, bytes]) -> None:
    payload.pop("SHA256SUMS", None)
    payload["SHA256SUMS"] = "".join(
        f"{digest(data)}  {name}\n" for name, data in sorted(payload.items())
    ).encode("utf-8")
    validate_manifest(payload, "new payload")


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".packaging-", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_archive(path: Path, archive_root: str, payload: dict[str, bytes]) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".packaging-", suffix=".zip", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for relative, data in sorted(payload.items()):
                safe_relative(relative)
                item = zipfile.ZipInfo(archive_root + "/" + relative, date_time=(2026, 10, 14, 0, 0, 0))
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | 0o644) << 16
                item.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(item, data, compresslevel=6)
        # Read every emitted payload back and check its manifest before commit.
        emitted = read_archive(temporary, archive_root)
        require(emitted == payload, f"Archive payload round-trip failed: {path.name}")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return {"path": str(path.resolve()), "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size,
            "entries": len(payload), "payload_files": len(payload) - 1, "manifest_complete": True,
            "crc_and_payload_roundtrip": True, "safe_regular_unique_paths": True}


def preserved(before: dict[str, bytes], after: dict[str, bytes], prefix: str, exceptions: set[str] | None = None) -> int:
    names = {name for name in before if name.startswith(prefix)}
    current = {name for name in after if name.startswith(prefix)}
    require(names == current, f"Preserved tree membership changed: {prefix}")
    exceptions = exceptions or set()
    require(exceptions <= names, f"Preservation exception missing from tree: {prefix}")
    for name in names - exceptions:
        require(before[name] == after[name], f"Preserved bytes changed: {name}")
    return len(names - exceptions)


def private_new_path(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return any(p.startswith(".") or p == "__pycache__" for p in parts) or any(
        token in name.lower() for token in ["library_file_transfer", "library_upload", "library_hosted_apps", "private_helper", "signed_url"]
    )


def add_evidence(payload: dict[str, bytes], name: str, data: bytes) -> None:
    safe_relative(name)
    require(name not in payload, f"Technical evidence would overwrite historical payload: {name}")
    require(not private_new_path(name), f"Private helper or hidden path would be included: {name}")
    require(SIGNED_URL.search(data) is None, f"Signed service URL found in new evidence: {name}")
    payload[name] = data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    inputs = root.parent / "monograph_proofread_inputs"
    output = root.parent / "monograph_release_output"
    pdf = args.pdf.resolve()
    summary_path = args.summary.resolve()
    pdf_data = regular_file(pdf)
    summary_data = regular_file(summary_path)
    summary = json.loads(summary_data)
    require(summary.get("qa_complete") is True, "The final summary does not attest completed QA")
    require(summary.get("unresolved_issues") == [], "The final summary has unresolved or unspecified issues")
    require(summary.get("pdf_sha256") == digest(pdf_data), "The supplied PDF is not the frozen reviewed PDF")
    pages = summary.get("pdf_pages")
    require(type(pages) is int and pages > 0, "Missing valid physical page count")
    require(sorted(summary.get("reviewed_physical_pages", [])) == list(range(1, pages + 1)), "Page-by-page QA coverage is incomplete or duplicated")
    import fitz
    with fitz.open(stream=pdf_data, filetype="pdf") as document:
        require(len(document) == pages, "The actual PDF page count differs from the final summary")

    publication_path = inputs / (PUBLIC_ROOT + ".zip")
    technical_path = inputs / (TECH_ROOT + ".zip")
    parent_report_path = inputs / EXTERNAL_REPORT
    old_public = read_archive(publication_path, PUBLIC_ROOT)
    old_technical = read_archive(technical_path, TECH_ROOT)
    parent_record = json.loads(regular_file(root / "records/PARENT.json"))
    require(parent_record["sha256"] == digest(publication_path.read_bytes()), "Parent publication identity mismatch")
    require(parent_record["monograph_sha256"] == digest(old_public["books/" + MONOGRAPH]), "Parent monograph identity mismatch")

    public: dict[str, bytes] = {"README.md": regular_file(root / "README.md")}
    for tree in sorted(PUBLIC_ALLOWLIST - {"README.md"}):
        public.update(collect_tree(root, tree))
    current_source = {name: digest(data) for name, data in public.items() if name.startswith("source/")}
    require(summary.get("source_hashes") == current_source, "Source tree differs from the exact final-summary hash map")
    require(set(old_public) - {"SHA256SUMS"} <= set(public), "A parent public payload file is missing")
    old_source = {name: digest(data) for name, data in old_public.items() if name.startswith("source/")}
    require(set(old_source) == set(current_source), "Source membership changed unexpectedly")
    actual_changed_sources = [
        {"file": name, "before_sha256": old_source[name], "after_sha256": current_source[name]}
        for name in sorted(current_source) if old_source[name] != current_source[name]
    ]
    require(isinstance(summary.get("changed_sources"), list), "Missing explicit changed_sources list")
    require(sorted(summary["changed_sources"], key=lambda item: item["file"]) == actual_changed_sources,
            "Explicit changed_sources does not exactly match the source diff from the parent")
    preservation = {tree: preserved(old_public, public, tree + "/") for tree in ["lean", "examples"]}
    figure_exception = "source/figures/02_extension.tex"
    preservation["source/figures"] = preserved(old_public, public, "source/figures/", {figure_exception})
    require(any(item["file"] == figure_exception for item in actual_changed_sources),
            "Expected Figure 2 font-size correction is not in changed_sources")
    # Limit the one permitted figure-source edit to the recorded font-size
    # adjustment. All mathematical wording, coordinates, and other bytes remain.
    original_figure = old_public[figure_exception].decode("utf-8")
    revised_figure = public[figure_exception].decode("utf-8")
    old_label = r"node[lab,above] {quotient}"
    new_label = r"node[lab,above,font=\footnotesize] {quotient}"
    require(original_figure.count(old_label) == 2 and original_figure.replace(old_label, new_label) == revised_figure,
            "Figure 2 exception exceeds the two recorded quotient-label font-size adjustments")
    preservation["figure_tex_exception"] = figure_exception
    preservation["figure_tex_exception_scope"] = "Font-size commands only, explicitly bound by changed_sources and source_hashes"
    preservation["parent_technical_payload_preserved"] = len(old_technical) - 2
    preservation["accepted_verification"] = sum(name.startswith("accepted_verification/") for name in old_technical)
    preservation["previous_visual_revision"] = sum(name.startswith("visual_revision/") for name in old_technical)
    companion_books = [name for name in old_public if name.startswith("books/") and name != "books/" + MONOGRAPH]
    for name in companion_books:
        require(public[name] == old_public[name], f"Companion book changed: {name}")
    preservation["unchanged_companion_pdfs"] = len(companion_books)
    for name in ["source/Komorebi_Space_Visual_Guide.tex", "source/Komorebi_Space_Lean_Guide.tex"]:
        require(public[name] == old_public[name], f"Companion source changed: {name}")
    preservation["companion_entry_sources"] = 2
    public["books/" + MONOGRAPH] = pdf_data

    concise = {
        "edition": VERSION,
        "scope": "Final monograph proofreading and explanatory clarification. This record does not claim a new full Lean compilation or a new independent proof audit of every theorem.",
        "pdf_file": "books/" + MONOGRAPH,
        "pdf_sha256": digest(pdf_data), "pdf_pages": pages,
        "parent_publication_sha256": digest(publication_path.read_bytes()),
        "parent_monograph_sha256": digest(old_public["books/" + MONOGRAPH]),
        "final_summary_sha256": digest(summary_data),
        "editorial_summary": summary.get("editorial_summary", "See the detailed proofreading records in the accompanying Technical Record."),
        "validation": summary.get("validation", {}),
        "visual_review": {"qa_complete": True, "reviewed_physical_pages": list(range(1, pages + 1)), "unresolved_issues": []},
        "preservation": preservation,
        "source_hashes": current_source,
        "changed_sources": actual_changed_sources,
        "formal_scope": "Accepted production Lean source and prior proof evidence are preserved. No new Lean compilation is claimed for this editorial revision.",
    }
    edition = json.loads(public["verification/EDITION_VERIFICATION.json"])
    matches = [b for b in edition["books"] if b["file"] == "books/" + MONOGRAPH]
    require(len(matches) == 1, "Expected one monograph entry in edition verification")
    matches[0]["sha256"] = digest(pdf_data)
    matches[0]["pages"] = pages
    edition["monograph_proofread_revision"] = concise
    public["verification/EDITION_VERIFICATION.json"] = json_bytes(edition)
    public["verification/MONOGRAPH_PROOFREAD_REVIEW.json"] = json_bytes(concise)
    verification_readme = public["verification/README.md"].decode("utf-8")
    require("MONOGRAPH_PROOFREAD_REVIEW.json" in verification_readme and "histor" in verification_readme.lower(),
            "Update verification/README.md to identify current proofreading and historical visual-revision provenance")
    add_manifest(public)

    technical = {name: data for name, data in old_technical.items() if name not in {"README.md", "SHA256SUMS"}}
    add_evidence(technical, "monograph_proofread/parent_technical_README.md", old_technical["README.md"])
    add_evidence(technical, "monograph_proofread/parent_technical_SHA256SUMS.txt", old_technical["SHA256SUMS"])
    add_evidence(technical, "monograph_proofread/parent/" + publication_path.name, publication_path.read_bytes())
    add_evidence(technical, "monograph_proofread/parent/" + EXTERNAL_REPORT, regular_file(parent_report_path))
    add_evidence(technical, "monograph_proofread/final_summary.json", summary_data)
    add_evidence(technical, "monograph_proofread/public_review.json", json_bytes(concise))
    for directory in ["records", "review"]:
        for name, data in collect_tree(root, directory).items():
            require(not name.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")), f"Unexpected rendered artifact in records/review: {name}")
            add_evidence(technical, "monograph_proofread/" + name, data)
    for name, data in collect_tree(root, "build").items():
        path = PurePosixPath(name)
        if path.suffix.lower() not in BUILD_SUFFIXES or name == "build/package_result.json":
            continue
        add_evidence(technical, "monograph_proofread/" + name, data)
    # Retain compact explicit image identities even if individual reviewers use
    # differing record schemas. Full-page render PNGs are reproducible and omitted.
    image_manifest = []
    render_directory = (root / summary.get("render_directory", "build/page_review")).resolve()
    require(render_directory.is_relative_to(root), "Render directory must be inside the working package")
    for n in range(1, pages + 1):
        image_path = render_directory / f"page-{n:03d}.png"
        image_data = regular_file(image_path)
        image_manifest.append({"physical_page": n, "path": image_path.relative_to(root).as_posix(), "sha256": digest(image_data)})
    add_evidence(technical, "monograph_proofread/final_render_image_hashes.json", json_bytes({
        "pdf_sha256": digest(pdf_data), "physical_pages": pages, "images": image_manifest,
        "scope": "Hash inventory of final page renders; visual judgments and coverage are recorded separately in review/."}))
    render_report_path = render_directory / "render_report.json"
    render_report = json.loads(regular_file(render_report_path))
    require(render_report.get("pdf_sha256") == digest(pdf_data), "Final render report belongs to a different PDF")
    require(render_report.get("pages") == pages, "Final render report page count differs")
    require(render_report.get("outside_words") == [], "Final render report contains off-page words")
    require(render_report.get("unresolved_reference_text_pages") == [], "Final render report contains unresolved references")
    for name, data in old_technical.items():
        if name not in {"README.md", "SHA256SUMS"}:
            require(technical.get(name) == data, f"Historical technical payload changed: {name}")
    technical["README.md"] = (
        "# Komorebi Space: technical record\n\n"
        "This archive preserves the accepted formal baseline and the evidence for successive publication revisions.\n\n"
        "- `accepted_verification/`, `publication/`, and `visual_revision/` retain every parent payload file byte for byte. "
        "Their statements describe the corresponding historical verification or visual-guide revision.\n"
        "- `monograph_proofread/` records the current final monograph proofreading: exact source identities and changes, "
        "editorial reviews, build attempts and logs, PDF page coverage, and final render-image hashes. "
        "The full-page PNGs are reproducible and are not included.\n"
        "- `monograph_proofread/parent/` preserves the complete immediate parent publication ZIP and its external verification JSON. "
        "The prior technical README and checksum manifest are preserved beside that folder.\n\n"
        "The current monograph PDF identity is recorded in `monograph_proofread/final_summary.json`. "
        "The current publication ZIP and this technical ZIP receive a separate independent delivery-verification report. "
        "Archive self-hashes are not embedded inside their own archives.\n\n"
        "Production Lean, worked-example implementations, PDF/PNG figure assets, and the visual and Lean guide PDFs remain unchanged. "
        "The sole figure-source adjustment changes font-size commands in Figure 2 and is recorded with its exact hashes. "
        "The current work is an editorial revision; it does not claim a new full Lean compilation. "
        "Failed or superseded build attempts are retained with their reports so that the final accepted artifact can be distinguished from them.\n"
    ).encode("utf-8")
    add_manifest(technical)

    # All freeze, source, preservation, and render gates have passed. Output
    # mutation begins only here. Working sources and parent archives are untouched.
    output.mkdir(parents=True, exist_ok=True)
    public_result = write_archive(output / (PUBLIC_ROOT + ".zip"), PUBLIC_ROOT, public)
    technical_result = write_archive(output / (TECH_ROOT + ".zip"), TECH_ROOT, technical)
    atomic_bytes(output / MONOGRAPH, pdf_data)
    atomic_bytes(root / "books" / MONOGRAPH, pdf_data)
    atomic_bytes(root / "verification/EDITION_VERIFICATION.json", public["verification/EDITION_VERIFICATION.json"])
    atomic_bytes(root / "verification/MONOGRAPH_PROOFREAD_REVIEW.json", public["verification/MONOGRAPH_PROOFREAD_REVIEW.json"])
    atomic_bytes(root / "SHA256SUMS", public["SHA256SUMS"])
    result = {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "summary_path": str(summary_path), "summary_sha256": digest(summary_data),
        "outputs": [
            {"path": str((output / MONOGRAPH).resolve()), "sha256": digest(pdf_data), "bytes": len(pdf_data), "pages": pages},
            public_result, technical_result,
        ],
        "independent_verification_report": {"expected_path": str((output / EXTERNAL_REPORT).resolve()), "produced_by_this_script": False},
        "preservation": preservation,
        "public_top_level_counts": dict(Counter(name.split("/")[0] for name in public)),
        "technical_top_level_counts": dict(Counter(name.split("/")[0] for name in technical)),
        "source_freeze_verified": True, "complete_page_review_attested": True,
        "no_full_lean_compilation_claimed": True,
    }
    atomic_bytes(root / "build/package_result.json", json_bytes(result))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
