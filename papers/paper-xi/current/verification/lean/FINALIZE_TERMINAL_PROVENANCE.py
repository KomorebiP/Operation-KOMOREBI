#!/usr/bin/env python3
"""Freeze terminal repair provenance and the portable source project after all required gates.
Usage: python3 FINALIZE_TERMINAL_PROVENANCE.py PROJECT_ROOT PORTABLE_DIRECTORY REVIEW_DIRECTORY
"""
from __future__ import annotations
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import sys


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    root, portable, reviews = map(lambda x: Path(x).resolve(), sys.argv[1:])
    ev = root / "evidence"
    build_path = ev / "replay_terminal_factored/RESULT.json"
    audit_path = ev / "axioms_terminal/RESULT.json"
    build, audit = [json.loads(p.read_text()) for p in [build_path, audit_path]]
    source = root / "PaperXI/ActualMonomialLocalGlobal.lean"
    final_sha = sha(source)
    owned = json.loads((ev / "axioms_terminal/OWNED_CONSTANTS.json").read_text())
    expected_helpers = {"lowerImage_succ_le_one", "actualObserved_eq_coordinates",
                        "actualObserved_swan_eq_standard", "actualObserved_artin_eq_standard",
                        "actualObserved_polynomial_eq_actual"}
    helper_rows = [row for row in owned if row["name"].split(".")[-1] in expected_helpers]
    if (len(helper_rows) != 5 or any(row["kind"] != "theorem" or row["unsafe"]
                                    or row["forbidden_axioms"] for row in helper_rows)):
        raise RuntimeError("The five private comparison helper theorems are not fully audited")
    original = root / "terminal_original/ActualMonomialLocalGlobal.lean"
    import_only = root / "terminal_original/ActualMonomialLocalGlobal.import_only.lean"
    interface = root / "PaperXI/SingleCandidateComparison.lean"
    final_review_source = reviews / "terminal_repair_review_final.json"
    review = json.loads(final_review_source.read_text())
    if (build["status"] != "PASS" or audit["status"] != "PASS"
            or build["source_hashes_after"][str(source.relative_to(root))] != final_sha
            or audit["source_replay_result_sha256"] != sha(build_path)
            or review.get("status") != "passed_in_reviewed_scope"
            or review.get("source_sha256") != final_sha
            or review.get("original_kernel_declaration_comparison") is not False
            or review.get("open_actionable_findings_in_meaning_or_hypotheses") != []):
        raise RuntimeError("Final compilation, audit, and independent static review do not agree")
    review_dest = ev / "terminal_repair/reviews"
    for suffix in ["json", "md"]:
        src = reviews / f"terminal_repair_review_final.{suffix}"
        dst = review_dest / src.name
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            raise RuntimeError("Refusing to overwrite a different stable review")
        shutil.copyfile(src, dst)
    for suffix in ["jsonl", "md"]:
        src = reviews / f"terminal_repair_review_history.{suffix}"
        dst = review_dest / f"terminal_repair_review_history_final_snapshot.{suffix}"
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            raise RuntimeError("Refusing to overwrite a changed final history snapshot")
        shutil.copyfile(src, dst)
    original_patch = "".join(difflib.unified_diff(
        original.read_text().splitlines(True), source.read_text().splitlines(True),
        fromfile="terminal_original/ActualMonomialLocalGlobal.lean",
        tofile="PaperXI/ActualMonomialLocalGlobal.lean"))
    (ev / "TERMINAL_COMPATIBILITY_REPAIR.patch").write_text(original_patch)
    changes = [
        {"kind": "import", "change": "Add PaperXI.RamificationPolyphase, already required by the retained lower-inclusion and projector APIs."},
        {"kind": "namespace_resolution", "change": "Open PaperXI.GeneratedIrreducibility for the retained representation actionEquiv and ValuativeRel for its residue-field notation."},
        {"kind": "implicit_arguments", "change": "Pass the local section degree n by name at existing applications whose exported n binder is implicit; imported explicit-n APIs are retained."},
        {"kind": "comment_syntax", "change": "Use an ordinary block comment before the htame variable declaration instead of a declaration doc comment."},
        {"kind": "standing_hypothesis_interface", "change": "Make the already-declared inertia-image and other standing section hypotheses explicit where Lean does not infer them from proof usage. This changes the exported binder interface relative to the non-elaborating text and adds no new arithmetic datum."},
        {"kind": "conductor_proof", "change": "Expose the same three-term finite Artin expression with change while keeping packetSwan folded, so the retained Swan-zero theorem rewrites the matching expression."},
        {"kind": "equality_orientation", "change": "Use the derived equation n=0 in its stated orientation against NeZero.ne n."},
        {"kind": "descent_proof", "change": "Rewrite the already-proved representation identity hσ while constructing the inertia-kernel premise, rather than after that premise is constructed."},
        {"kind": "constructed_local_instances", "change": "Install the retained residueTowerAlgebra and residueTowerFinite adapters locally for the final tower statements."},
        {"kind": "comparison_proof_factoring", "change": "Introduce five private helper theorems for the lower-image inclusion and four comparison components; reuse positive_lowerImage_trivial at r=0. The public actual_comparison_package header and conclusion are byte-identical to candidate04."},
        {"kind": "lower_image_witness_orientation", "change": "Apply the retained lift_lowerInclusion equality in its exact forward orientation, matching the image witness equation and avoiding the reversed-equality conversion isolated by the bounded diagnostic."}
    ]
    artifact_paths = [original, import_only, ev / "TERMINAL_IMPORT_REPAIR.patch",
                      ev / "TERMINAL_OOM_RETRY.json", ev / "TERMINAL_SYNCHRONOUS_OOM.json",
                      ev / "TERMINAL_OOM_TOOL_OBSERVATION_192740.json"]
    artifact_paths.extend(p for p in (ev / "terminal_repair").rglob("*") if p.is_file())
    preserved = [{"path": str(p.relative_to(root)), "sha256": sha(p)}
                 for p in sorted(set(artifact_paths))]
    review_path = review_dest / "terminal_repair_review_final.json"
    adaptation = {
        "schema_version": 2,
        "recorded_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "COMPILED_AND_AXIOM_AUDITED_WITH_INDEPENDENT_STATIC_REVIEW",
        "original_terminal_sha256": sha(original),
        "import_only_terminal_sha256": sha(import_only),
        "repaired_terminal_sha256": final_sha,
        "new_interface_source_sha256": sha(interface),
        "selected_source_count_unchanged": 423,
        "selected_catalogued_name_count_unchanged": 4342,
        "selected_sources_and_interface_byte_identical_across_all_replays": True,
        "terminal_not_in_selected_catalogue": True,
        "new_private_component_helpers": 5,
        "private_component_helper_audit": helper_rows,
        "terminal_owned_logical_declarations": audit["owned_constant_count"],
        "changes": changes,
        "all_terminal_statements_byte_identical_to_original": False,
        "original_kernel_declaration_comparison": False,
        "original_comparison_limitation": "No successful original module build is available for a comparison of kernel declarations.",
        "interpretation": "The independent source review supports the retained mathematical intent under its explicitly declared standing data. The final source is separately kernel-accepted and audited. No arithmetic realization or automorphic existence theorem is added.",
        "final_compilation_result": {"path": str(build_path.relative_to(root)), "sha256": sha(build_path)},
        "final_terminal_axiom_result": {"path": str(audit_path.relative_to(root)), "sha256": sha(audit_path)},
        "exact_original_to_final_patch": {"path": "evidence/TERMINAL_COMPATIBILITY_REPAIR.patch", "sha256": sha(ev / "TERMINAL_COMPATIBILITY_REPAIR.patch")},
        "independent_source_review": {"path": str(review_path.relative_to(root)), "sha256": sha(review_path),
                                      "reviewed_source_sha256": final_sha, "status": review["status"]},
        "preserved_artifacts": preserved
    }
    dump(ev / "TERMINAL_COMPATIBILITY_REPAIR.json", adaptation)
    portable.mkdir(exist_ok=True)
    for rel in ["PaperXI/ActualMonomialLocalGlobal.lean", "PaperXI/SingleCandidateComparison.lean",
                "terminal_original/ActualMonomialLocalGlobal.lean", "terminal_original/ActualMonomialLocalGlobal.import_only.lean",
                "README.md", "lean-toolchain", "lakefile.lean", "lake-manifest.json",
                "PaperXI.lean", "PaperXITerminal.lean", "PaperXIAdditions.lean"]:
        target = portable / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)
    source_catalogue = json.loads((root / "catalogues/SOURCE_CATALOG.json").read_text())["modules"]
    assert len(source_catalogue) == 423
    for module, row in source_catalogue.items():
        rel = Path(*module.split(".")).with_suffix(".lean")
        if sha(root / rel) != row["sha256"] or sha(portable / rel) != row["sha256"]:
            raise RuntimeError("A selected portable source differs from its retained catalogue: " + module)
    for script in sorted((root / "scripts").glob("*.py")):
        shutil.copyfile(script, portable / "scripts" / script.name)
    source_adaptations = {
        "schema_version": 2, "status": adaptation["status"],
        "terminal_module": "PaperXI.ActualMonomialLocalGlobal",
        "original_terminal_source": "terminal_original/ActualMonomialLocalGlobal.lean",
        "original_terminal_sha256": sha(original),
        "failed_import_only_source": "terminal_original/ActualMonomialLocalGlobal.import_only.lean",
        "failed_import_only_sha256": sha(import_only),
        "repaired_terminal_source": "PaperXI/ActualMonomialLocalGlobal.lean",
        "repaired_terminal_sha256": final_sha,
        "only_import_lines_changed": False,
        "terminal_not_in_selected_catalogue": True,
        "selected_catalogue_source_count_unchanged": 423,
        "selected_catalogued_names_unchanged": 4342,
        "new_interface_module": "PaperXI.SingleCandidateComparison",
        "new_interface_source_sha256": sha(interface),
        "changes": changes,
        "original_kernel_declaration_comparison": False,
        "original_comparison_limitation": adaptation["original_comparison_limitation"],
        "independent_source_review": "provenance/terminal_repair_review_final.json",
        "exact_original_to_final_patch": "provenance/TERMINAL_COMPATIBILITY_REPAIR.patch",
        "release_evidence_from_project_root": "../verification/lean",
        "note": "The portable project contains the final sources and review. Full current-session replay, audit, source revision, and failure receipts accompany it in the release verification directory; runtime paths in those raw receipts record the actual original execution."
    }
    for project in [root, portable]:
        dest = project / "provenance"
        dest.mkdir(exist_ok=True)
        old_adapt = dest / "SOURCE_ADAPTATIONS.json"
        if old_adapt.exists():
            previous = json.loads(old_adapt.read_text())
            if previous.get("only_import_lines_changed") is True:
                initial = dest / "INITIAL_IMPORT_ONLY_SOURCE_ADAPTATIONS.json"
                if not initial.exists():
                    shutil.copyfile(old_adapt, initial)
        dump(old_adapt, source_adaptations)
        for src in [ev / "TERMINAL_IMPORT_REPAIR.patch", ev / "TERMINAL_COMPATIBILITY_REPAIR.patch",
                    review_dest / "terminal_repair_review_final.json", review_dest / "terminal_repair_review_final.md"]:
            shutil.copyfile(src, dest / src.name)
    forbidden_parts = {".runtime", ".lake", "objects", "__pycache__", "cache"}
    files = {}
    total = 0
    for f in sorted(portable.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(portable)
        if f.is_symlink() or forbidden_parts.intersection(rel.parts) or ".olean" in f.name or f.suffix in {".ilean", ".pyc", ".o", ".a", ".so", ".zst"}:
            raise RuntimeError("Unexpected runtime/object artifact in portable project: " + str(rel))
        files[str(rel)] = sha(f)
        total += f.stat().st_size
    receipt = {
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "portable_directory": str(portable), "selected_modules": 423, "additional_modules": 2,
        "file_count": len(files), "bytes": total, "selected_catalogue_hashes_match": True,
        "final_terminal_source_sha256": final_sha,
        "runtime_and_dependencies_included": False, "compiled_objects_included": False,
        "files": files
    }
    dump(ev / "PORTABLE_PROJECT_RECEIPT.json", receipt)
    print(json.dumps({"status": "PASS", "portable_files": len(files), "portable_bytes": total,
                      "terminal_owned_logical_declarations": audit["owned_constant_count"],
                      "preserved_terminal_artifacts": len(preserved), "final_source_sha256": final_sha}, indent=2))


if __name__ == "__main__":
    main()
