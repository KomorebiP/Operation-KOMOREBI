#!/usr/bin/env python3
"""Recheck Paper II source/evidence and publication bindings without compiling Lean.

Run from any directory with --root pointing to the extracted release.
Requires Python 3 and PyMuPDF for PDF object/text inspection.
Write --output outside the extracted release to leave its manifest unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output.resolve()
    if out == root or root in out.parents:
        parser.error("--output must be outside the release tree")
    out.mkdir(parents=True, exist_ok=True)
    closeout = root / "verification/closeout_2026-10-19"
    receipt = json.loads((closeout / "attempt02_m4096/verification.json").read_text())
    spec = importlib.util.spec_from_file_location(
        "paper2_audit", closeout / "audit_driver/verify_release.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows, empty = module.inspect_sources(root / "formal/current")
    manifest = closeout / "attempt02_m4096/execution_inputs/release_modules.json"
    frozen = json.loads(manifest.read_text())
    errors = []
    if receipt["status"] != "PASS":
        errors.append("recorded_replay_not_pass")
    if rows != frozen:
        errors.append("production_sources_differ_from_frozen_manifest")
    for name, want in receipt["source_configuration"].items():
        if sha(root / "formal/current" / name) != want:
            errors.append(name)
    for row in receipt["audit_inputs"]:
        path = closeout / "audit_driver" / row["path"]
        if not path.is_file() or sha(path) != row["sha256"]:
            errors.append("audit/" + row["path"])
    if sha(manifest) != receipt["manifest_sha256"]:
        errors.append("frozen_manifest_hash")
    source_result = {
        "status": "PASS" if not errors else "FAIL",
        "checks": {
            "strict_production_source_policy": "PASS",
            "production_modules": len(rows),
            "source_order_matches_recorded_manifest": rows == frozen,
            "source_configuration_files": len(receipt["source_configuration"]),
            "audit_input_files": len(receipt["audit_inputs"]),
            "frozen_manifest_hash_matches": sha(manifest) == receipt["manifest_sha256"],
        },
        "errors": errors,
        "fresh_lean_execution": False,
        "receipt_date": receipt["finished_utc"],
    }
    (out / "source_binding_audit.json").write_text(
        json.dumps(source_result, indent=2) + "\n")

    import fitz
    corpath = root / "formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json"
    correspondence = json.loads(corpath.read_text())
    review = json.loads((root / "publication/FINAL_PUBLICATION_REVIEW.json").read_text())
    pub_errors = []
    for name, digest in correspondence["current_chapter_sha256"].items():
        if sha(root / name) != digest:
            pub_errors.append(name)
    if sha(corpath) != review["current_correspondence_sha256"]:
        pub_errors.append("current_correspondence_sha256")
    qa = root / review["page_qa"]["path"]
    if sha(qa) != review["page_qa"]["sha256"]:
        pub_errors.append("page_qa_sha256")
    pdfs = []
    for record in review["pdfs"]:
        path = root / record["path"]
        with fitz.open(path) as doc:
            data = {
                "path": record["path"],
                "pages": len(doc),
                "expected_pages": record["pages"],
                "sha256_matches": sha(path) == record["sha256"],
                "encrypted": doc.is_encrypted,
                "empty_text_pages": [],
                "unresolved_reference_pages": [],
                "out_of_bounds_internal_links": [],
            }
            for index, page in enumerate(doc):
                text = page.get_text()
                if not text.strip():
                    data["empty_text_pages"].append(index + 1)
                if "??" in text or "\ufffd" in text:
                    data["unresolved_reference_pages"].append(index + 1)
                for link in page.get_links():
                    if link.get("kind") == fitz.LINK_GOTO and not (
                        0 <= link.get("page", -1) < len(doc)
                    ):
                        data["out_of_bounds_internal_links"].append(
                            {"page": index + 1, "target": link.get("page")})
        if (data["pages"] != record["pages"] or not data["sha256_matches"]
            or data["encrypted"] or data["unresolved_reference_pages"]
            or data["out_of_bounds_internal_links"]):
            pub_errors.append(record["path"])
        pdfs.append(data)
    publication_result = {
        "status": "PASS" if not pub_errors else "FAIL",
        "manuscript_chapter_hashes": len(correspondence["current_chapter_sha256"]),
        "correspondence_status": correspondence["status"],
        "recorded_proof_counts": correspondence["final_proof_counts"],
        "correspondence_hash_matches_review":
            sha(corpath) == review["current_correspondence_sha256"],
        "recorded_page_qa_hash_matches": sha(qa) == review["page_qa"]["sha256"],
        "pdf_checks": pdfs,
        "errors": pub_errors,
        "fresh_full_visual_review": False,
        "note": (
            "Unchanged PDFs retain the October 19 visual review. This check reads "
            "PDF objects, text, page counts, link targets, and exact bytes."),
    }
    (out / "publication_binding_audit.json").write_text(
        json.dumps(publication_result, indent=2) + "\n")
    print(json.dumps({
        "source_bindings": source_result["status"],
        "publication_bindings": publication_result["status"],
        "fresh_lean_execution": False,
    }, indent=2))
    return int(bool(errors or pub_errors))

if __name__ == "__main__":
    raise SystemExit(main())

