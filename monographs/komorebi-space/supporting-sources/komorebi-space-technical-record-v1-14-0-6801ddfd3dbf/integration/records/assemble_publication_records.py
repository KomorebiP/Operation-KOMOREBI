"""Bind the final publication records to the accepted source and PDF bytes."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "publication"
VER = PUB / "verification"
NAMES = {"monograph": "Monograph", "lean": "Lean_Guide", "visual": "Visual_Guide"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


pdf = read("records/PDF_STRUCTURAL_CHECKS.json")
comparison = read("records/PDF_PAGE_COMPARISON.json")
counts = read("records/FORMAL_COUNTS.json")
audit = read("reviews/publication_integration_audit.json")
book_build = read("build/final_03/build_report.json")
assert book_build["source_unchanged"]
for path, digest in book_build["source_hashes"].items():
    assert sha(PUB / path) == digest, path
for name in NAMES.values():
    old = PUB / f"books/Komorebi_Space_{name}_v1.13.0.pdf"
    if old.exists():
        assert sha(old) == sha(ROOT / "parent_books" / old.name)
        old.unlink()
books = {}
for key, name in NAMES.items():
    target = PUB / f"books/Komorebi_Space_{name}_v1.14.0.pdf"
    shutil.copy2(ROOT / pdf[key]["file"], target)
    books[key] = {"file": str(target.relative_to(PUB)), "sha256": sha(target), "pages": pdf[key]["pages"]}
    assert sha(target) == pdf[key]["sha256"]

record = read("records/FINAL_TYPESETTING_CORRECTIONS.json")
record["status"] = "verified in final_03 rendered PDF"
record["accepted_lean_pdf"] = books["lean"]
record["independent_review"] = "reviews/lean_pdf_visual_review.json"
write(ROOT / "records/FINAL_TYPESETTING_CORRECTIONS.json", record)

root_visual_review = {
    "scope": "Final PDF layout review of changed monograph pages and visual-guide cover, with raster identity checks for inherited pages. Not a fresh proof audit of every page.",
    "render_dpi": 90,
    "monograph": {**books["monograph"], "reviewed_changed_pages": comparison["monograph"]["changed_or_new_pages"],
                   "unchanged_from_parent_pages": 150, "all_final_page_pngs_identical_to_reviewed_initial_render": True,
                   "unresolved_visual_defects": []},
    "visual": {**books["visual"], "reviewed_changed_pages": [1], "unchanged_from_parent_pages": 18,
                "all_final_page_pngs_identical_to_reviewed_initial_render": True, "unresolved_visual_defects": []},
    "lean_review": "lean_pdf_visual_review.json",
    "structural_record": "../records/PDF_STRUCTURAL_CHECKS.json",
    "notices": "Routine underfull-box and visual-bookmark spacing notices are retained in the structural record; no unresolved references, overflowing boxes, missing glyphs, invalid internal links or off-page text were found."
}
write(ROOT / "reviews/final_monograph_visual_review.json", root_visual_review)

integrated = {
    "edition": "1.14.0", "working_directory": "publication/lean", "logical_command": ["lake", "build"],
    "default_targets": ["KomorebiSpaceCombined", "KomorebiSpaceDiagonal"], "exit_code": 0, "lake_jobs": 3820,
    "log": "build/integrated_lake_build.log", "log_sha256": sha(ROOT / "build/integrated_lake_build.log"),
    "warning_or_error_lines": [], "historical_controls_replayed": False,
    "environment": "Pinned official compiler and dependencies from accepted diagonal completion; host compatibility wrapper disclosed in that record."
}
assert "Build completed successfully (3820 jobs)." in (ROOT / integrated["log"]).read_text()
assert not any("warning:" in s.lower() or "error:" in s.lower() for s in (ROOT / integrated["log"]).read_text().splitlines())
write(ROOT / "records/INTEGRATED_BUILD.json", integrated)

current = VER / "current"
current.mkdir(exist_ok=True)
for name in ["FORMAL_COUNTS.json", "THEOREM_MAP_CHECK.json", "monograph_math_preservation.json",
             "monograph_integration_changes.json", "FINAL_TYPESETTING_CORRECTIONS.json", "PDF_STRUCTURAL_CHECKS.json",
             "PDF_PAGE_COMPARISON.json", "INTEGRATED_BUILD.json", "VISUAL_REFERENCES.json"]:
    shutil.copy2(ROOT / "records" / name, current / name)
for path in (ROOT / "reviews").glob("*"):
    if path.is_file():
        shutil.copy2(path, current / path.name)
shutil.copy2(ROOT / "build/final_03/build_report.json", current / "BOOK_BUILD.json")
for name in ["integrated_lake_build.log", "theorem_map_check.log"]:
    shutil.copy2(ROOT / "build" / name, current / name)

write(VER / "MONOGRAPH_PROOFREAD_REVIEW.json", {
    "edition": "1.14.0", "scope": "Coverage and correspondence updates after accepted diagonal formalization; mathematical statements and printed proofs preserved.",
    **books["monograph"], "principal_analytic_groups_formalized": 16,
    "preserved_mathematical_environments": 192, "chapters_compared": 29,
    "preservation_record": "current/monograph_math_preservation.json",
    "source_review": "current/publication_integration_audit.json",
    "visual_review": "current/final_monograph_visual_review.json",
    "raster_comparison": comparison["monograph"],
    "historical_review": "history/MONOGRAPH_PROOFREAD_REVIEW_v1.13.0.json",
    "limitations": "Formal counterparts cover the stated sixteen result groups, not each alternative proof route or illustrative specialization. This editorial pass is not a fresh proof audit of all unchanged theorems."
})

write(VER / "VISUAL_GUIDE_REVIEW.json", {
    "edition": "1.14.0", **books["visual"], "investigations": 16,
    "scope": "Edition-title update; sixteen scene records and mathematical figure assets unchanged from v1.13.0.",
    "raster_comparison": comparison["visual"], "review": "current/final_monograph_visual_review.json",
    "monograph_reference_check": "current/VISUAL_REFERENCES.json",
    "historical_model_checks": {"generator_checks": 52, "independent_checks": 23, "rerun_this_edition": False,
                                "records": "visual/", "review": "history/VISUAL_GUIDE_REVIEW_v1.13.0.json"},
    "scope_limit": "Finite visual computations do not prove universal or infinite-dimensional conclusions."
})

source_identity = {}
for directory in ["source", "lean", "tools", "examples"]:
    for path in sorted((PUB / directory).rglob("*")):
        if path.is_file() and not path.is_symlink() and not any(s in {".lake", "__pycache__"} for s in path.parts):
            source_identity[str(path.relative_to(PUB))] = sha(path)
write(VER / "EDITION_VERIFICATION.json", {
    "edition": "1.14.0", "author": "Komorebi P.", "date": "2026-10-14",
    "scope": "Publication integration of accepted infinite-diagonal proofs, with a fresh integrated Lean build and final editorial review.",
    "counts": counts["totals"], "principal_analytic_theorem_groups": audit["principal_group_status_table"],
    "lean_version": "4.34.0-rc2", "lean_revision": "6a10ac8c22beadecabdbb0919c2b50214762f91d",
    "mathlib_revision": "aeb72f1e9981b6d35b426b16dca7759be3e7ba06",
    "permitted_axioms": ["Classical.choice", "Quot.sound", "propext"],
    "proof_source_preservation": {"accepted_diagonal_files": 164, "parent_files": 156, "all_byte_identical": True,
                                 "record": "current/FORMAL_COUNTS.json"},
    "integrated_build": integrated,
    "selected_declaration_check": {**read("records/THEOREM_MAP_CHECK.json"), "record": "current/THEOREM_MAP_CHECK.json"},
    "declaration_audit_scope": "Union of accepted 5048-declaration parent inventory and disjoint 273-declaration diagonal inventory; no fresh combined axiom audit claimed.",
    "controls": counts["controls"], "books": books, "source_identity": source_identity,
    "current_reviews": {str(path.relative_to(VER)): sha(path) for path in sorted(current.iterdir()) if path.is_file()},
    "accepted_diagonal_archive": {"file": "DIAGONAL_ACCEPTED_EVIDENCE.zip", "sha256": sha(VER / "DIAGONAL_ACCEPTED_EVIDENCE.zip")},
    "parent_publication_sha256": counts["parent_publication_sha256"],
    "parent_technical_record_sha256": "f26a69afaf03029a98204fef3d777c7a43a8bf4cae799039384fa8d0f6566042",
    "trust_boundary": "Lean kernel/compiler, standard axioms, pinned compiled external dependencies, and the execution platform. The external dependencies were not rebuilt from source as part of this publication integration.",
    "limitations": "All sixteen principal analytic result groups have formal counterparts under their hypotheses. Alternate printed proof routes, every illustrative calculation, and broader research targets are not thereby asserted formalized or solved."
})
with (ROOT / "records/PROGRESS_LEDGER.jsonl").open("a") as stream:
    stream.write(json.dumps({"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "event": "final_books_and_records_accepted",
                             "books": books, "source_review_obligations_passed": 24, "unresolved_source_or_visual_defects": 0}) + "\n")
print(json.dumps({"books": books, "source_identity_files": len(source_identity)}, indent=2))
