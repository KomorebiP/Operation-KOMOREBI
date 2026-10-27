#!/usr/bin/env python3
"""Read-only source/output binding audit of the retained October 15 finite run.

This script hashes and compares saved records. It executes no mathematical
generator, renderer, pytest suite, or Lean process.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.release_root.resolve()
    out = (args.output_dir or Path(__file__).resolve().parent).resolve()
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    old_rel = Path("verification/release_2026-10-15/paper2_work/computation_final")
    old = root / old_rel
    retained_review = old / "reviewed_evidence.json"
    retained_manifest = old / "run_2026-10-15/manifest.json"
    review = json.loads(retained_review.read_text())
    manifest = json.loads(retained_manifest.read_text())
    old_result = json.loads((old / "run_2026-10-15/RESULT.json").read_text())
    continuity = json.loads((old / "historical_input_continuity.json").read_text())
    contract = json.loads((old / "contract.json").read_text())
    baseline_status_path = root / "verification/closeout_2026-10-19/history/baseline_root/RELEASE_STATUS.json"
    release_status = json.loads(baseline_status_path.read_text())

    def relocate(recorded: str) -> Path:
        p = PurePosixPath(recorded)
        if p.is_absolute() or ".." in p.parts:
            raise ValueError(f"Unsafe recorded path: {recorded!r}")
        prefix = "release_package/Komorebi_Paper_II_Release_2026-10-15/"
        if recorded.startswith(prefix):
            return root / recorded[len(prefix):]
        if recorded.startswith("paper2_work/"):
            return root / "verification/release_2026-10-15" / recorded
        raise ValueError(f"Unrecognized historical prefix: {recorded!r}")

    def binding(recorded: str, expected: str, expected_after: str | None = None,
                current: Path | None = None) -> dict:
        path = current or relocate(recorded)
        present = path.is_file()
        observed = digest(path) if present else None
        return {
            "recorded_path": recorded,
            "package_path": str(path.relative_to(root)),
            "expected_sha256": expected,
            "expected_sha256_after": expected_after,
            "observed_sha256": observed,
            "present": present,
            "matches": present and observed == expected and
                       (expected_after is None or observed == expected_after),
        }

    inputs = [binding(x["path"], x["sha256"], x["sha256_after"])
              for x in manifest["input_artifacts"]]
    outputs = [binding(x["path"], x["sha256"]) for x in manifest["outputs"]]
    retained_files = [binding(x["path"], x["sha256"]) for x in review["evidence_files"]]
    sources = [binding(x["path"], x["sha256"])
               for x in review["provenance"]["authoritative_sources"]]
    historical = [binding(x["path"], x["historical_sha256"], x["current_sha256"], root / x["path"])
                  for x in continuity["files"]]
    historical_manifest = binding(continuity["historical_manifest"],
                                  continuity["historical_manifest_sha256"])
    current_input_set = {x["path"] for x in manifest["input_artifacts"]}
    execution_set = set(manifest["execution_artifacts"])
    contract_execution_set = set(contract["execution_artifacts"])

    # Saved numerical records, without numerical execution or new tolerances.
    current_csv = list(csv.DictReader(io.StringIO(
        (root / "source/canonical_v1.2.1/results/numerical_summary.csv").read_text())))
    retained_csv = list(csv.DictReader(io.StringIO(
        (old / "run_2026-10-15/canonical/results/numerical_summary.csv").read_text())))
    current_json = json.loads((root / "source/canonical_v1.2.1/results/numerical_results.json").read_text())
    retained_json = json.loads((old / "run_2026-10-15/canonical/results/numerical_results.json").read_text())
    current_exact = json.loads((root / "editable/visual_guide/checks/EXACT_CHECKS.json").read_text())
    retained_exact = json.loads((old / "run_2026-10-15/EXACT_CHECKS.json").read_text())
    normalized = lambda data: {k: v for k, v in data.items() if k != "timestamp_utc"}
    figure = json.loads((old / "run_2026-10-15/figure_data.json").read_text())
    current_matrix = json.loads((root / "editable/traditional/figure_sources/matrix_visual_data.json").read_text())
    current_graph = json.loads((root / "editable/traditional/figure_sources/graph_visuals_validation.json").read_text())
    atlas = json.loads((old / "run_2026-10-15/atlas_comparison.json").read_text())
    atlas_bindings = []
    for plate in atlas["plates"]:
        for directory in ["editable/visual_guide/graphics", "editable/traditional/visual_graphics"]:
            rel = Path(directory) / plate["name"]
            atlas_bindings.append(binding(str(rel), plate["generated_sha256"], current=root / rel))
    expanded = old_result["expanded_groups"]
    integrity_group = "test_source_integrity"

    checks = {
        "retained_review_matches_old_release_status": digest(retained_review) ==
            release_status["bounded_computation"]["sha256"],
        "input_count_is_101": len(inputs) == 101 == review["input_artifact_count"],
        "all_101_inputs_match_recorded_before_and_after": all(x["matches"] for x in inputs),
        "all_retained_outputs_match_manifest": all(x["matches"] for x in outputs),
        "all_retained_review_evidence_files_match": all(x["matches"] for x in retained_files),
        "all_authoritative_sources_match": all(x["matches"] for x in sources),
        "historical_74_input_continuity_matches": len(historical) == 74 and
            all(x["matches"] for x in historical),
        "historical_manifest_binding_matches": historical_manifest["matches"],
        "execution_artifacts_equal_manifest_input_set": execution_set == current_input_set,
        "contract_execution_artifacts_equal_manifest_set": contract_execution_set == execution_set,
        "retained_run_completed_with_exit_zero": manifest["run"]["status"] == "completed" and
            manifest["run"]["exit_status"] == 0,
        "retained_result_status_pass": old_result["status"] == "PASS",
        "canonical_saved_json_equals_retained_json": current_json == retained_json,
        "all_9_csv_rows_equal_retained_and_reviewed_rows": len(current_csv) == 9 and
            current_csv == retained_csv == review["canonical_summary_rows"],
        "118_exact_saved_checks_equal_retained_except_timestamp":
            current_exact["check_count"] == retained_exact["check_count"] == 118 and
            normalized(current_exact) == normalized(retained_exact),
        "118_recorded_exact_checks_are_distinct_and_all_passed":
            len(current_exact["checks"]) == len({x["name"] for x in current_exact["checks"]}) == 118 and
            all(x["passed"] is True for x in current_exact["checks"]),
        "13_saved_figure_data_paths_unique_and_records_equal":
            len(figure["stems"]) == len(set(figure["stems"])) == 13 and
            figure["matrix"] == current_matrix and figure["graph"] == current_graph,
        "22_retained_atlas_sources_match_both_current_copies": len(atlas["plates"]) == 22 and
            all(x["matches"] for x in atlas_bindings) and
            len(list((root / "editable/visual_guide/graphics").glob("*.tex"))) == 22 and
            len(list((root / "editable/traditional/visual_graphics").glob("*.tex"))) == 22,
        "expanded_record_has_9_math_groups_and_1_archived_integrity_group":
            len(expanded) == 10 and expanded.count(integrity_group) == 1,
    }
    # Rehash after all reads so concurrent changes cannot silently gain continuity.
    for row in inputs:
        p = root / row["package_path"]
        row["observed_sha256_after_recheck"] = digest(p) if p.is_file() else None
        row["unchanged_during_recheck"] = row["observed_sha256_after_recheck"] == row["observed_sha256"]
    checks["all_101_inputs_stable_during_recheck"] = all(x["unchanged_during_recheck"] for x in inputs)
    all_bindings = inputs + outputs + retained_files + sources + historical + atlas_bindings + [historical_manifest]
    problems = [x for x in all_bindings if not x["matches"]]
    passed = all(checks.values())
    report = {
        "schema": "komorebi.paper-ii.retained-finite-evidence-rebinding/1",
        "claim_id": "PAPER-II-RETAINED-BOUNDED-EVIDENCE-REBIND-2026-10-19",
        "status": "PASS_FOR_RETAINED_FINITE_EVIDENCE_BINDINGS" if passed else "FAIL",
        "verdict": "AUDITED_NOT_EXECUTED_ALL_BINDINGS_MATCH" if passed else "PROVENANCE_INVALID_OR_STALE",
        "current_input_hashes_rechecked": len(inputs),
        "current_input_hashes_matched": sum(x["matches"] for x in inputs),
        "fresh_numerical_run": False,
        "source_of_mathematical_review": str(retained_review.relative_to(root)),
        "retained_review_sha256": digest(retained_review),
        "retained_run_manifest": str(retained_manifest.relative_to(root)),
        "retained_run_manifest_sha256": digest(retained_manifest),
        "retained_release_status": str(baseline_status_path.relative_to(root)),
        "retained_release_status_sha256": digest(baseline_status_path),
        "mathematical_scope": review["mathematical_contract"],
        "retained_run": manifest["run"],
        "retained_environment": manifest["environment"],
        "retained_randomness": manifest["randomness"],
        "fresh_run": {
            "assertion_tested": "Every retained input/output/source binding resolves to the current package and matches its recorded hash; saved finite records agree.",
            "kind": "read-only hash and saved-record comparison",
            "started_at_utc": started,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_seconds": round(time.monotonic() - timer, 6),
            "status": "completed" if passed else "failed",
            "mathematical_generators_executed": False,
            "pytest_executed": False,
            "lean_executed": False,
            "renderers_executed": False,
            "argv": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
            "script_package_path": str(Path(__file__).resolve().relative_to(root)),
            "script_sha256": digest(Path(__file__).resolve()),
            "python": sys.version,
            "platform": platform.platform(),
        },
        "counts": {
            "current_inputs": len(inputs), "matched_current_inputs": sum(x["matches"] for x in inputs),
            "input_file_extensions": dict(collections.Counter(Path(x["package_path"]).suffix or "[none]" for x in inputs)),
            "retained_manifest_outputs": len(outputs), "retained_review_evidence_files": len(retained_files),
            "authoritative_sources": len(sources), "historical_continuity_files": len(historical),
            "atlas_source_plates": len(atlas["plates"]), "atlas_current_copy_bindings": len(atlas_bindings),
            "canonical_summary_rows": len(current_csv), "retained_exact_visual_checks": current_exact["check_count"],
            "retained_figure_data_paths": len(figure["stems"]),
            "retained_expanded_mathematical_groups": len(expanded) - 1,
            "retained_archived_integrity_groups": 1,
        },
        "checks": checks,
        "missing_or_mismatched_bindings": problems,
        "path_relocation": {
            "release_package/Komorebi_Paper_II_Release_2026-10-15/": "[current release root]/",
            "paper2_work/": "verification/release_2026-10-15/paper2_work/",
            "historical_execution_argv": "Retained as historical provenance. Old absolute scratch paths are not current execution commands.",
            "historical_launch_scripts": "Preserved byte-for-byte. Their original release_package/paper2_work scaffold must be reconstructed or explicitly adapted for any future numerical replay; this hash-only audit does not execute them.",
        },
        "not_freshly_executed": [
            "All finite mathematical generators and assertions are retained October 15 evidence, not newly executed by this rebinding pass.",
            "Historical 48-case pytest suite is not newly rerun. The October 15 record reported pytest unavailable; current pytest availability was not tested because no test execution was authorized for this pass.",
            "PDF/PNG rendering is not rerun by this pass and was excluded from the October 15 bounded numerical contract.",
            "Lean and publication page/source verification belong to the separate final formal and publication audit.",
        ],
        "unreproducibility_findings": [],
        "reproduction_limit": "This audit establishes source/output continuity, not fresh mathematical reproduction. No mathematical reproduction command was attempted, so no new environment reproducibility verdict is made.",
        "fresh_record_comparisons": {
            "canonical_summary_rows": current_csv,
            "figure_stems": figure["stems"],
            "expanded_mathematical_groups": [x for x in expanded if x != integrity_group],
            "separate_archived_integrity_group": integrity_group,
        },
        "bindings": {
            "current_inputs": inputs, "retained_manifest_outputs": outputs,
            "retained_review_evidence_files": retained_files, "authoritative_sources": sources,
            "historical_continuity": historical, "historical_manifest": historical_manifest,
            "atlas_current_copies": atlas_bindings,
        },
        "non_claims": [
            "No universal theorem is inferred from finite examples or hash equality.",
            "Historical floating residuals retain their original rtol=1e-12 and atol=1e-14 interpretation; no precision was increased.",
            "Archived annals-source integrity evidence is not current publication source or layout evidence.",
        ],
    }
    report_path = out / "COMPUTATION_REBIND.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    short = f"""# Paper II retained finite computation evidence

Verdict: {report['verdict']}. This pass performed read-only hashing and saved-record comparison, not a fresh mathematical run.

All {len(inputs)} recorded current inputs match both historical before/after hashes and remain unchanged during this recheck. The {len(outputs)} manifest outputs, {len(retained_files)} retained review evidence files, {len(sources)} authoritative sources and {len(historical)} older continuity entries also resolve and match. There are {len(problems)} missing or mismatched bindings.

Saved records agree for all nine numerical summary rows, 118 named exact checks, 13 unique figure-data paths, 22 atlas source plates in both current copies, and nine expanded mathematical groups. The expanded archived-source integrity group remains separately identified.

The original finite domain, seed and floating tolerances remain in the JSON report. The October 15 mathematical execution is retained evidence. Its 48-case historical pytest suite was not freshly rerun, and this pass did not probe current pytest availability. No mathematical generator, renderer or Lean process ran. No new environment reproducibility failure is asserted without an attempted run.

The recheck is reproducible with `python3 verification/closeout_2026-10-19/computation/rebind_bounded_evidence.py --release-root .` from this package root. This is a provenance recheck command, not a numerical reproduction command.

Report: COMPUTATION_REBIND.json
"""
    (out / "README.md").write_text(short)
    print(json.dumps({"status": report["verdict"], "checks": len(checks),
                      "passed_checks": sum(checks.values()), "counts": report["counts"],
                      "report_sha256": digest(report_path)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
