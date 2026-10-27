#!/usr/bin/env python3
"""Aggregate actual Paper XI release receipts; refuse to describe missing gates as passed.

Usage: python3 GENERATE_RELEASE_REPORT.py /path/to/working/formalization-project
The positional argument is explicit so this retained report generator contains
no dependency on the original workspace's absolute path.
"""
from __future__ import annotations

import collections
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import platform
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    root = Path(sys.argv[1]).resolve()
    evidence = root / "evidence"

    def read(relative: str) -> dict:
        return json.loads((evidence / relative).read_text())

    def write(name: str, data: object) -> None:
        (evidence / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    first = read("replay/RESULT.json")
    continuation = read("replay_complete/RESULT.json")
    repair_attempt = read("replay_terminal_repaired/RESULT.json")
    synchronous_attempt = read("replay_terminal_synchronous/RESULT.json")
    final_replay_path = "evidence/replay_terminal_factored/RESULT.json"
    build = json.loads((root / final_replay_path).read_text())
    selected = read("axioms_selected_release/RESULT.json")
    terminal = read("axioms_terminal/RESULT.json")
    interface = read("axioms_interface_final/RESULT.json")
    controls = read("axiom_controls_final/RESULT.json")
    resume_controls = read("terminal_resume_controls/terminal_revision_resume_controls_03.json")
    resume_preflight = read("terminal_resume_controls/terminal_resume_actual_lineage_preflight_03.json")
    download = read("LEAN_DOWNLOAD_RECEIPT.json")
    pins = read("DEPENDENCY_PINS.json")
    cache = read("MATHLIB_CACHE_RECEIPT.json")
    adaptation = read("TERMINAL_COMPATIBILITY_REPAIR.json")
    restart = read("RESOURCE_RESTART.json")
    portable = read("PORTABLE_PROJECT_RECEIPT.json")
    catalogue = json.loads((root / "catalogues/SOURCE_CATALOG.json").read_text())["modules"]
    names = json.loads((root / "catalogues/DECLARATION_CATALOG.json").read_text())
    rows = {row["module"]: row for row in build["modules"]}
    population = collections.Counter(row["group"] for row in rows.values())
    expected_modules = set(catalogue) | {"PaperXI.ActualMonomialLocalGlobal", "PaperXI.SingleCandidateComparison"}
    expected_sources = {str(Path(*name.split(".")).with_suffix(".lean")) for name in expected_modules}
    if (len(build["modules"]) != 425 or len(rows) != 425 or set(rows) != expected_modules
            or population != {"selected": 423, "terminal": 1, "new_interface": 1}
            or any(row["status"] != "PASS" or row["exit_code"] != 0 for row in rows.values())
            or set(build["source_hashes_before"]) != expected_sources
            or set(build["source_hashes_after"]) != expected_sources):
        raise RuntimeError("Final compiled population is not exactly 423 + 1 + 1")
    if len(catalogue) != 423 or len(names) != 4342 or len({row["name"] for row in names}) != 4342:
        raise RuntimeError("Retained catalogue population changed")
    for result in [build, selected, terminal, interface, controls]:
        if result["status"] != "PASS":
            raise RuntimeError("A required release gate did not pass")
    if (build.get("synchronous_elaboration_requested") is not True
            or build.get("additional_lean_options") != ["-DElab.async=false"]
            or "-DElab.async=false" not in rows["PaperXI.ActualMonomialLocalGlobal"]["command"]):
        raise RuntimeError("The final terminal did not use the recorded synchronous execution option")
    if selected["module_count"] != 423 or selected["catalogued_names_resolved"] != 4342:
        raise RuntimeError("Selected axiom audit did not cover the complete catalogue")
    if len(controls["controls"]) != 2 or not all(row["status"] == "PASS" for row in controls["controls"]):
        raise RuntimeError("The two negative controls did not pass")
    if (resume_controls["result"] != "PASS" or len(resume_controls["checks"]) != 34
            or not all(row["passed"] for row in resume_controls["checks"])
            or resume_controls["run"]["exit_status"] != 0
            or resume_preflight["status"] != "PASS"
            or resume_preflight["authenticated_objects"] != 424
            or resume_preflight["script_sha256"] != build["script_sha256"]):
        raise RuntimeError("Terminal revision resume controls or actual lineage preflight did not pass")
    for item in resume_controls["input_artifacts"]:
        if item["sha256"] != item["sha256_after"] or digest(root / "scripts" / Path(item["path"]).name) != item["sha256"]:
            raise RuntimeError("The controlled terminal resume implementation changed")
    if (len(build["aggregates"]) != 3
            or {row["module"] for row in build["aggregates"]} != {"PaperXI", "PaperXITerminal", "PaperXIAdditions"}
            or not all(row["status"] == "PASS" and row["exit_code"] == 0 for row in build["aggregates"])):
        raise RuntimeError("An aggregate import failed")
    for row in build["aggregates"]:
        if digest(root / row["source_path"]) != row["source_sha256"]:
            raise RuntimeError("An aggregate import changed after compilation")
    selected_aggregate_imports = [line.split()[1] for line in (root / "PaperXI.lean").read_text().splitlines()
                                  if line.startswith("import ")]
    if len(selected_aggregate_imports) != 423 or set(selected_aggregate_imports) != set(catalogue):
        raise RuntimeError("The selected aggregate does not import exactly the selected catalogue")
    source_after = {path: digest(root / path) for path in build["source_hashes_before"]}
    if source_after != build["source_hashes_before"] or source_after != build["source_hashes_after"]:
        raise RuntimeError("A checked source changed before reporting")
    for name, row in rows.items():
        path = str(Path(*name.split(".")).with_suffix(".lean"))
        expected_group = "selected" if name in catalogue else ("terminal" if name.endswith(".ActualMonomialLocalGlobal") else "new_interface")
        if (row["source_path"] != path or row["source_sha256"] != source_after[path]
                or row["source_unchanged"] is not True or row["group"] != expected_group):
            raise RuntimeError("A final module row does not bind the expected source and population")
    for name, record in catalogue.items():
        path = str(Path(*name.split(".")).with_suffix(".lean"))
        if source_after.get(path) != record["sha256"]:
            raise RuntimeError(f"Final selected source differs from its retained catalogue: {name}")
    original_terminal = root / "terminal_original/ActualMonomialLocalGlobal.lean"
    repaired_terminal = root / "PaperXI/ActualMonomialLocalGlobal.lean"
    if digest(original_terminal) != adaptation["original_terminal_sha256"]:
        raise RuntimeError("The preserved original terminal changed")
    if digest(repaired_terminal) != adaptation["repaired_terminal_sha256"]:
        raise RuntimeError("The repaired terminal differs from its adaptation receipt")
    expected_patch = "".join(difflib.unified_diff(
        original_terminal.read_text().splitlines(True), repaired_terminal.read_text().splitlines(True),
        fromfile="terminal_original/ActualMonomialLocalGlobal.lean",
        tofile="PaperXI/ActualMonomialLocalGlobal.lean"))
    if (evidence / "TERMINAL_COMPATIBILITY_REPAIR.patch").read_text() != expected_patch:
        raise RuntimeError("The terminal compatibility patch does not reproduce the exact final difference")
    for artifact in adaptation["preserved_artifacts"]:
        if digest(root / artifact["path"]) != artifact["sha256"]:
            raise RuntimeError("A preserved terminal revision, diff, or review changed")
    review_binding = adaptation["independent_source_review"]
    review_path = root / review_binding["path"]
    if digest(review_path) != review_binding["sha256"]:
        raise RuntimeError("The final independent source review changed")
    review = json.loads(review_path.read_text())
    if (review_binding["reviewed_source_sha256"] != adaptation["repaired_terminal_sha256"]
            or review_binding["status"] != "passed_in_reviewed_scope"
            or review.get("status") != review_binding["status"]
            or review.get("source_sha256") != review_binding["reviewed_source_sha256"]
            or review.get("open_actionable_findings_in_meaning_or_hypotheses") != []
            or review.get("original_kernel_declaration_comparison") is not False):
        raise RuntimeError("The final source review does not certify the delivered terminal revision's static intent")
    if digest(root / "PaperXI/SingleCandidateComparison.lean") != adaptation["new_interface_source_sha256"]:
        raise RuntimeError("The separate interface differs from its source receipt")
    chain = []
    cursor_path = root / final_replay_path
    while True:
        cursor = json.loads(cursor_path.read_text())
        if any(str(cursor_path.relative_to(root)) == item["path"] for item in chain):
            raise RuntimeError("Cycle in source replay lineage")
        if cursor["status"] == "RUNNING" or cursor["source_hashes_before"] != cursor["source_hashes_after"]:
            raise RuntimeError("An unfinished or internally changed source replay is in the lineage")
        for field in ["lean_version", "lean_binary_sha256", "mathlib_commit"]:
            if cursor[field] != build[field]:
                raise RuntimeError("A source replay lineage runtime differs")
        chain.append({"path": str(cursor_path.relative_to(root)), "sha256": digest(cursor_path),
                      "status": cursor["status"], "paperxi_objects_reused": cursor["paperxi_objects_reused"],
                      "selected_modules_passed": cursor["selected_modules_passed"],
                      "lake_manifest_sha256": cursor.get("lake_manifest_sha256"),
                      "elapsed_seconds": cursor["elapsed_seconds"]})
        if not cursor.get("resume"):
            if cursor["paperxi_objects_reused"]:
                raise RuntimeError("The origin replay reused unauthenticated objects")
            break
        prior_path = (root / cursor["resume"]["result_path"]).resolve()
        if not prior_path.is_relative_to(root) or digest(prior_path) != cursor["resume"]["result_sha256"]:
            raise RuntimeError("A prior replay receipt changed")
        prior = json.loads(prior_path.read_text())
        prior_rows = {row["module"]: row for row in prior["modules"] if row["status"] == "PASS"}
        for row in cursor["modules"]:
            if row["status"] == "PASS" and "resumed_from" in row:
                old = prior_rows.get(row["module"])
                if old is None or row["source_sha256"] != old["source_sha256"]:
                    raise RuntimeError("A resumed module lacks the same successful source predecessor")
                if {Path(path).name: value for path, value in row["artifacts"].items()} != {Path(path).name: value for path, value in old["artifacts"].items()}:
                    raise RuntimeError("Resumed artifact fingerprints changed")
                if row["resumed_from"]["result_sha256"] != digest(prior_path):
                    raise RuntimeError("Per-module resume lineage differs from the replay lineage")
        cursor_path = prior_path
    expected_chain = ["evidence/replay_terminal_factored/RESULT.json",
                      "evidence/replay_terminal_synchronous/RESULT.json",
                      "evidence/replay_terminal_repaired/RESULT.json",
                      "evidence/replay_complete/RESULT.json", "evidence/replay/RESULT.json"]
    if [item["path"] for item in chain] != expected_chain or first["paperxi_objects_reused"]:
        raise RuntimeError("Expected exactly the retained five-attempt current-session lineage")
    if continuation["resume"]["authenticated_selected_modules"] != 421 or build["resume"]["authenticated_selected_modules"] != 423:
        raise RuntimeError("The asserted authenticated selected populations changed")
    terminal_path = "PaperXI/ActualMonomialLocalGlobal.lean"
    if first["source_hashes_before"][terminal_path] != adaptation["import_only_terminal_sha256"] or continuation["source_hashes_before"][terminal_path] != adaptation["import_only_terminal_sha256"]:
        raise RuntimeError("The preserved failed terminal revision differs")
    for path, fingerprint in source_after.items():
        if path != terminal_path and any(run["source_hashes_before"][path] != fingerprint for run in [first, continuation, repair_attempt, synchronous_attempt]):
            raise RuntimeError("A successful selected or interface source changed across attempts")
    if repair_attempt["source_hashes_after"] != synchronous_attempt["source_hashes_before"]:
        raise RuntimeError("A source changed between the first resource failure and synchronous retry")
    revision = build["resume"].get("terminal_revision")
    if not revision or build["resume"].get("mode") != "terminal_revision":
        raise RuntimeError("The final source change was not an explicit failed-terminal revision")
    if synchronous_attempt["source_hashes_after"][terminal_path] == source_after[terminal_path]:
        raise RuntimeError("The final proof-size repair was not recorded as a source revision")
    if (revision["old_sha256"] != synchronous_attempt["source_hashes_after"][terminal_path]
            or revision["new_sha256"] != source_after[terminal_path]
            or revision["invalidated_modules"] != ["PaperXI.ActualMonomialLocalGlobal"]
            or revision["previous_terminal_artifacts_reused"] is not False
            or revision["requires_fresh_compilation"] is not True):
        raise RuntimeError("The final explicit terminal revision metadata does not bind its exact source transition")
    if build["lake_manifest_sha256"] != digest(root / "lake-manifest.json") or continuation["lake_manifest_sha256"] != build["lake_manifest_sha256"]:
        raise RuntimeError("The manifest changed before terminal repair")
    for audit, expected_scope, expected_owners, expected_replay in [
        (selected, "selected", set(catalogue), "evidence/replay_complete/RESULT.json"),
        (terminal, "terminal", {"PaperXI.ActualMonomialLocalGlobal"}, final_replay_path),
        (interface, "new_interface", {"PaperXI.SingleCandidateComparison"}, "evidence/replay_complete/RESULT.json")]:
        if (audit["scope"] != expected_scope or set(audit["requested_modules"]) != expected_owners
                or len(audit["requested_modules"]) != len(expected_owners)
                or audit["module_count"] != len(expected_owners)
                or audit["source_replay_result_path"] != expected_replay):
            raise RuntimeError("An audit does not bind the exact intended scope and source replay")
        audit_build_path = root / audit["source_replay_result_path"]
        if audit["source_replay_result_sha256"] != digest(audit_build_path):
            raise RuntimeError("An audit's recorded source replay changed")
        if str(audit_build_path.relative_to(root)) not in {item["path"] for item in chain}:
            raise RuntimeError("An audit refers to a replay outside the authenticated lineage")
        if not audit["objects_unchanged"] or not audit["sources_unchanged"] or audit["forbidden_constants"]:
            raise RuntimeError("An audit integrity or axiom gate failed")
        for path, fingerprint in audit["source_hashes_before"].items():
            if source_after[path] != fingerprint:
                raise RuntimeError("An audited source differs from the final source")
        for path, fingerprint in audit["object_hashes_after"].items():
            if digest(root / path) != fingerprint:
                raise RuntimeError("An audited object changed before reporting")
    for row in [*rows.values(), *build["aggregates"]]:
        for path, fingerprint in row["artifacts"].items():
            if digest(root / path) != fingerprint:
                raise RuntimeError("A final compiled object changed before reporting")
    tower = rows["PaperXI.UnramifiedFieldTower"]
    active_build_seconds = sum(item["elapsed_seconds"] for item in chain)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    warnings = {group: sum(row["warning_lines"] for row in rows.values() if row["group"] == group)
                for group in population}
    scopes = {}
    for key, audit in [("selected", selected), ("terminal", terminal), ("new_interface", interface)]:
        scopes[key] = {field: audit[field] for field in [
            "module_count", "catalogued_name_count", "catalogued_names_resolved",
            "owned_constant_count", "compiler_auxiliary_count", "observed_axioms",
            "owned_constant_kinds", "unsafe_owned_constants", "seconds"]}
        scopes[key]["compile_status"] = "PASS"
        scopes[key]["axiom_audit_status"] = "PASS"
        scopes[key]["compiler_warning_lines"] = warnings[key]
        scopes[key]["compilation_result"] = {
            "path": audit["source_replay_result_path"],
            "sha256": audit["source_replay_result_sha256"]}
        audit_result_path = {"selected": "evidence/axioms_selected_release/RESULT.json",
                             "terminal": "evidence/axioms_terminal/RESULT.json",
                             "new_interface": "evidence/axioms_interface_final/RESULT.json"}[key]
        scopes[key]["axiom_audit_result"] = {
            "path": audit_result_path, "sha256": digest(root / audit_result_path)}
    summary = {
        "schema_version": 2, "recorded_at": now, "status": "PASS",
        "claim_id": "PAPERXI-RELEASE-SELECTED-423-FRESH-COMPILE-AND-AXIOM-AUDIT",
        "scopes": scopes,
        "final_replay_result": {"path": final_replay_path, "sha256": digest(root / final_replay_path)},
        "selected_source_hashes_match_retained_catalogue": True,
        "selected_423_sources_and_interface_unchanged_across_all_replays": True,
        "final_425_source_revision_hashes_unchanged_during_final_replay_and_reporting": True,
        "terminal_source_revised_between_failed_and_successful_replays": True,
        "all_sources_unchanged_between_resource_failure_and_synchronous_retry": True,
        "catalogue_population": {"selected_modules": 423, "unique_names": 4342},
        "compile_lineage": {
            "initial_result_status": first["status"],
            "initial_fresh_selected_passes": first["selected_modules_passed"],
            "initial_fresh_interface_passes": 1,
            "continued_first_attempt_authenticated_objects": continuation["resume"]["authenticated_modules"],
            "terminal_repair_authenticated_objects": repair_attempt["resume"]["authenticated_modules"],
            "synchronous_retry_authenticated_objects": synchronous_attempt["resume"]["authenticated_modules"],
            "factored_terminal_repair_authenticated_objects": build["resume"]["authenticated_modules"],
            "terminal_repair_newly_compiled_modules": sorted(row["module"] for row in rows.values()
                                                        if "resumed_from" not in row),
            "result_chain_newest_first": chain,
            "origin_manifest_note": "The first replay did not record a manifest fingerprint. The immediate predecessor and repaired replay do record and authenticate the identical pinned manifest; no missing historical fingerprint is inferred.",
            "historical_paperxi_objects_used": False,
            "external_mathlib_cache_used": True,
            "external_mathlib_rebuilt": False,
            "initial_compiler_stopped_early": restart,
            "terminal_resource_failure": read("TERMINAL_OOM_RETRY.json"),
            "terminal_synchronous_resource_failure": read("TERMINAL_SYNCHRONOUS_OOM.json"),
            "tower_successful_compile_seconds": tower["seconds"],
            "active_source_replay_wall_seconds_sum": active_build_seconds,
            "note": "All selected sources and the interface were freshly compiled unchanged in this release session. The final terminal revision was freshly compiled after diagnosed compatibility repairs. Only authenticated successful current-session objects are reused. Earlier failed runs remain failed."
        },
        "aggregate_imports": {row["module"]: row["status"] for row in build["aggregates"]},
        "negative_controls": [{k: row[k] for k in ["name", "status", "exit_code", "expected_error_text", "sentinel_checks"]}
                              for row in controls["controls"]],
        "terminal_revision_resume_controls": {"status": "PASS", "checks_passed": 34,
            "manifest": "terminal_resume_controls/terminal_revision_resume_controls_03.json",
            "actual_preflight_authenticated_objects": 424,
            "actual_preflight_receipt": "terminal_resume_controls/terminal_resume_actual_lineage_preflight_03.json"},
        "final_new_compilation_options": {
            "synchronous_elaboration_requested": build["synchronous_elaboration_requested"],
            "additional_lean_options": build["additional_lean_options"],
            "scope": "New terminal and aggregate compilations; resumed successful module rows retain their original commands."},
        "fresh_leanchecker_pass": False,
        "independent_kernel_implementation_used": False,
        "kernel_acceptance_basis": "All selected and added target sources were freshly elaborated and checked by the pinned Lean compiler. The axiom audit enumerates logical declarations in its imported private kernel environment.",
        "historical_checker_receipts": "historical/Continuation113_final_replay_corrected/",
        "lean_version": build["lean_version"],
        "lean_binary_sha256": build["lean_binary_sha256"],
        "mathlib_commit": build["mathlib_commit"],
        "dependencies": pins["dependencies"],
        "terminal_original_sha256": adaptation["original_terminal_sha256"],
        "terminal_repaired_sha256": adaptation["repaired_terminal_sha256"],
        "terminal_changes": adaptation["changes"],
        "terminal_compatibility_receipt": "TERMINAL_COMPATIBILITY_REPAIR.json",
        "catalogue_private_name_resolutions": selected["catalogue_private_name_resolutions"],
        "interface_sha256": adaptation["new_interface_source_sha256"],
        "portable_project_files": portable["file_count"],
        "portable_project_bytes": portable["bytes"],
        "interpretation_limits": [
            "The checks certify the formal declarations at their stated hypotheses; an informal-to-formal theorem correspondence requires manuscript review.",
            "The single-candidate interface uses a supplied admissible candidate and a separating factor system; it supplies no arithmetic existence theorem.",
            "The release checks do not establish actual automorphic realization, the original kappa normalization, Conjecture 66, or unrestricted local-global correspondence.",
            "Pinned external mathlib and dependency cache objects are imported rather than rebuilt.",
            "No fresh independent-checker claim is made."
        ]
    }
    write("RELEASE_VERIFICATION.json", summary)
    selected_ax = ", ".join(f"`{x}`" for x in selected["observed_axioms"])
    interface_ax = ", ".join(f"`{x}`" for x in interface["observed_axioms"])
    terminal_ax = ", ".join(f"`{x}`" for x in terminal["observed_axioms"])
    table = "\n".join(
        f"| {label} | {audit['module_count']:,} | {audit['catalogued_names_resolved']:,} | {audit['owned_constant_count']:,} | {audit['compiler_auxiliary_count']:,} | PASS |"
        for label, audit in [("Selected publication sources", selected),
                             ("Actual-monomial terminal", terminal),
                             ("Single-candidate interface", interface)])
    text = f"""# Fresh Lean verification for the Paper XI release

**All required formalization gates passed.** The 423 selected publication modules were freshly compiled with their retained source fingerprints unchanged. All 4,342 distinct catalogue names resolved to their recorded owning modules. The actual-monomial terminal and the new single-candidate comparison interface were compiled and audited separately. The complete machine-readable outcome is in [RELEASE_VERIFICATION.json](RELEASE_VERIFICATION.json).

## Exact populations and outcome

| Population | Modules | Catalogue names resolved | Owned logical declarations audited | Compiler-only auxiliary names listed | Outcome |
|---|---:|---:|---:|---:|---|
{table}

The terminal and interface do not change the selected 423-module or 4,342-name counts. The terminal has no entry in the publication declaration catalogue; its complete logical declaration population is still audited by owning module. All three aggregate imports passed. Compiler warning lines were retained: {warnings['selected']} in the selected files, {warnings['terminal']} in the terminal, and {warnings['new_interface']} in the interface. The selected source text was not edited to remove linter warnings. See [the final source replay](replay_terminal_synchronous/RESULT.json).

## Fresh compilation and restart history

The first replay began with an empty Paper XI object directory and compiled 421 selected modules plus the new interface successfully. The unfinished `UnramifiedFieldTower` compiler was manually stopped after {next(row['seconds'] for row in first['modules'] if row['module'] == 'PaperXI.UnramifiedFieldTower'):.2f} seconds, before the original 1,200-second limit, after finding a retained historical build duration of 1,588 seconds. That early stop discarded an unfinished attempt and is explicitly preserved as a failure of the first run, with signal and reason in [RESOURCE_RESTART.json](RESOURCE_RESTART.json). It was not a compiler rejection of the source.

The first continuation checked every source and completed-object fingerprint, copied only the 422 successful objects from this session's first replay, and used a 3,600-second per-module limit. It freshly compiled the tower and `ActualUnramifiedBaseChange`, completing all 423 selected modules and their aggregate. The tower completed successfully in {tower['seconds']:.2f} seconds, below the original 1,200-second limit; the earlier resource-driven stop was therefore not established to be necessary. The separately imported terminal then emitted concrete implicit-argument, name-resolution, syntax and proof-elaboration errors. Its known-failed compiler was stopped after the diagnostic was preserved, and the continuation honestly finalized as `PARTIAL_OR_FAIL`. This diagnostic-driven termination is distinct from the earlier premature tower stop.

The first repair replay permitted exactly one explicitly fingerprinted revision: the failed terminal. It authenticated the full prior replay lineage, the unchanged 423 selected sources and interface, their successful dependency closures, the runtime and immediate predecessor's pinned manifest, and all 424 successful current-session objects before reusing them. The terminal compiler then returned signal 9 after 228.15 seconds while the 8-GiB cgroup recorded one new out-of-memory kill. Its log was empty and no manual signal was sent. That third run remains a resource failure, with the exact observations in [TERMINAL_OOM_RETRY.json](TERMINAL_OOM_RETRY.json).

The fourth replay used the identical candidate04 source and ordinary authenticated resume, adding the execution option `-DElab.async=false` to process declarations synchronously. It also failed with signal 9 after 196.12 seconds and a second recorded cgroup out-of-memory kill; synchronous scheduling did not resolve the resource failure. See [TERMINAL_SYNCHRONOUS_OOM.json](TERMINAL_SYNCHRONOUS_OOM.json).

A bounded diagnostic then factored the comparison package into private component lemmas and isolated the kernel timeout to the lower-inclusion image witness. That witness used the retained equality in the reverse direction, forcing conversion between definitionally equal expressions. Using the equality in the exact forward direction of the required witness made the full bounded candidate diagnostic pass in 23.20 seconds; its reported kernel type checking dropped from 65.4 seconds in the failing diagnostic to 1.21 seconds. The public comparison-package theorem's header and conclusion are unchanged by this proof factoring and orientation correction. These diagnostics motivated and tested the repair; their source hashes, exact diffs, commands and logs are retained separately.

The fifth, final replay permitted this second explicitly fingerprinted revision of the failed terminal, authenticated all 424 successful objects and the entire four-run ancestry, and freshly compiled the repaired terminal plus all three aggregate imports. It retained synchronous elaboration as a recorded execution option. The first replay did not record a manifest fingerprint; that absent historical field is explicitly retained as a limitation, while subsequent replays record and authenticate the identical manifest. No inherited Paper XI object from the recovered archive was used.

The sum of the five source-run wall-clock durations was {active_build_seconds:.2f} seconds, including discarded failed elaboration. Bounded diagnostic candidates have their own separate receipts and are not counted as source-replay success. Each release compiler process used `-j1` and `maxHeartbeats=3000000`, with retained source-local options unchanged; the final retry also recorded synchronous elaboration. All selected-source and interface fingerprints remain unchanged across the complete attempt lineage. All 425 source fingerprints were identical across the two memory-failed attempts. The fifth run changes only the failed terminal; every final source fingerprint was stable during its replay and was checked again before this report. See [the initial attempt](replay/RESULT.json), [the failed-terminal continuation](replay_complete/RESULT.json), [the resource-failed repair attempt](replay_terminal_repaired/RESULT.json), [the resource-failed synchronous replay](replay_terminal_synchronous/RESULT.json), [the successful factored terminal replay](replay_terminal_factored/RESULT.json), and [the exact repair record](TERMINAL_COMPATIBILITY_REPAIR.json).

## Axiom and ownership audit

The audit resolves each requested source-catalogue name to its actual imported owner and kernel declaration, then enumerates every logical constant owned by the target modules in Lean's imported private kernel environment. Four catalogue entries require Lean's private-name mapping: two private `GraphTree` theorems and two named local `SpectralLocalField` instances. Each maps uniquely within its stated owning module, and both the source name and actual private kernel name are recorded. This includes generated declarations and private logical declarations. Each declaration's transitive axiom dependencies must belong to `Classical.choice`, `Quot.sound`, and `propext`. The observed union was {selected_ax} for the selected sources, {terminal_ax} for the terminal, and {interface_ax} for the interface. No forbidden axiom dependency was found.

Lean's ownership map also contains code-generator auxiliary names that are absent from its kernel constant map. The audit lists these separately and does not count them as logical declarations. This distinction follows the pinned Lean source definitions of `ModuleData.extraConstNames` and `Kernel.Environment.const2ModIdx`. The imported objects in each audited Paper XI dependency closure were authenticated against its successful source replay before the audit and fingerprinted again afterward. Selected and interface audits use the finalized continuation's already successful objects; the terminal audit uses the final repaired replay. Their sources and objects are connected by the authenticated current-session lineage and checked again before reporting. See [selected audit](axioms_selected_release/RESULT.json), [terminal audit](axioms_terminal/RESULT.json), and [interface audit](axioms_interface_final/RESULT.json); each directory retains the generated Lean audit, full log, resolved names and declaration-level axiom results.

Two isolated negative controls passed by being rejected for the intended reason: public and private uncatalogued custom axioms in a module with a safely catalogued theorem, and a deliberately missing catalogue name. The first control explicitly checks that both sentinel axioms are found and that the safely catalogued theorem has no axiom dependencies. Both Lean processes returned exit code 1 with the expected diagnostic. These fixtures are outside Paper XI and are not part of any release population. The [final control receipt](axiom_controls_final/RESULT.json) records the expected rejection checks.

The narrowly scoped terminal-revision resume implementation also passed focused acceptance and rejection controls, including rejection of changes to successful sources, dependency closures, manifests, runtime identity, receipt lineage and object fingerprints. A separate read-only preflight authenticated all 424 successful actual objects and their recorded ancestry under the exact implementation. The first repair replay exercised the explicit old-to-new terminal revision mode; the synchronous retry resumed those same sources without another revision, and the final replay exercised a second explicit failed-terminal revision through the complete ancestry. These checks are recorded under `terminal_resume_controls/` and remain distinct from the two axiom-audit controls.

The exploratory audit harness initially needed explicit `Nat` counter annotations and the distinction between compiler-only auxiliary names and logical declarations. Scaling to the full catalogue then required a larger recursion guard for its 4,342-entry literal, unique private-name resolution, a corrected generated variable name and matching Python population checks on the resolved kernel names. Every failed harness attempt and its executed script snapshot is retained. The final complete audit and negative controls passed. No selected theorem statement or proof body was changed in this process.

## Terminal repair and comparison interface

The preserved original terminal has SHA-256 `{adaptation['original_terminal_sha256']}`. The failed import-only version has SHA-256 `{adaptation['import_only_terminal_sha256']}`. The successfully compiled revision has SHA-256 `{adaptation['repaired_terminal_sha256']}`. The repair includes the missing ramification import, omitted namespace openings, named implicit-degree applications, a comment-syntax fix, explicit inclusion of already-declared standing hypotheses, local proof elaboration corrections, the retained constructed residue-tower instances, and five private component lemmas with the correctly oriented lower-inclusion witness. The last factoring and witness correction preserve the public comparison-package header and conclusion exactly. The complete final change list is in [TERMINAL_COMPATIBILITY_REPAIR.json](TERMINAL_COMPATIBILITY_REPAIR.json), with the [exact original-to-final diff](TERMINAL_COMPATIBILITY_REPAIR.patch). Every original and intermediate source, diff and diagnostic is preserved.

The independent source review checks each compatibility change against the original intended section data and the retained imported definitions. Making an already-declared standing hypothesis explicit changes the exported binder interface relative to the non-elaborating text. The release therefore does not claim that every terminal statement or proof body is byte-identical, or that an ill-typed original and a repaired version are kernel-equivalent. No successful original module build is available for a comparison of kernel declarations. The review and final compilation support the stated mathematical intent under the explicit hypotheses; they supply no new arithmetic realization theorem.

`PaperXI.SingleCandidateComparison.source` is an additional one-theorem module with SHA-256 `{adaptation['new_interface_source_sha256']}`. It applies the existing `LocalFactorIdentification.class_eq_iff` to one supplied admissible candidate and an admissible reference, with both factor profiles equal to the same declared profile. Its factor-equality hypothesis concerns that candidate. It does not require a realization-existence field or prove arithmetic existence. Its source, compilation and one-declaration audit are kept outside the selected catalogue counts.

## Environment and reproducibility

The Lean version is `{build['lean_version']}`. Its Linux binary fingerprint `{build['lean_binary_sha256']}` exactly matches the retained Continuation 113 environment. Mathlib is pinned to `{build['mathlib_commit']}`; all transitive package revisions are fixed in the delivered `lake-manifest.json`. The official Lean archive digest and binary match are recorded in [LEAN_DOWNLOAD_RECEIPT.json](LEAN_DOWNLOAD_RECEIPT.json), dependency revisions in [DEPENDENCY_PINS.json](DEPENDENCY_PINS.json), and official mathlib-cache retrieval in [MATHLIB_CACHE_RECEIPT.json](MATHLIB_CACHE_RECEIPT.json). External mathlib declarations were imported from the pinned official cache and were not rebuilt.

The portable project contains sources, catalogues, the original terminal, the failed import-only version, exact compatibility diffs, pinned Lake configuration and standard-library Python bootstrap/replay/audit scripts. It contains no downloaded runtime, dependency tree, cache or compiled objects. Its Linux x86_64 bootstrap, including WSL, downloads the official pinned dependencies into its own directory. The exact online setup components were exercised during runtime acquisition; the portable wrapper's offline pin/cache check passed. The convenience full-run wrapper was syntax and CLI checked; the individual release gates are the executions recorded here. The scripts compute paths from their own location and do not depend on the original workspace path. Raw command lines retain the actual execution paths for provenance.

## Scope of the result

Fresh source compilation checks the newly elaborated declarations through the pinned Lean kernel. No additional full `leanchecker` pass was run for this release, and no independent kernel implementation is claimed. The four-module Continuation 113 checker receipts are preserved under `historical/` and remain historical. The portable project offers the official same-kernel checker as an optional additional command.

These checks certify the formal declarations at their stated hypotheses. They do not establish that every informal manuscript statement is identical to a Lean theorem; that correspondence requires the manuscript review. They also do not supply actual automorphic realization, the original kappa normalization, Conjecture 66, or unrestricted local-global correspondence.
"""
    (evidence / "RELEASE_VERIFICATION.md").write_text(text)
    adaptation_final = dict(adaptation)
    adaptation_final.update(status="COMPILED_AND_AXIOM_AUDITED", completed_at=now,
                            terminal_owned_logical_declarations=terminal["owned_constant_count"],
                            interface_owned_logical_declarations=interface["owned_constant_count"],
                            selected_source_count=423, selected_catalogued_names=4342)
    write("ADDITIONS_FINAL_RESULT.json", adaptation_final)
    declared = ["replay_terminal_factored/RESULT.json", "axioms_selected_release/RESULT.json",
                "axioms_terminal/RESULT.json", "axioms_interface_final/RESULT.json",
                "axiom_controls_final/RESULT.json", "RELEASE_VERIFICATION.json", "RELEASE_VERIFICATION.md"]
    outputs = [{"path": "evidence/" + path, "sha256": digest(evidence / path),
                "kind": "report" if path.endswith(".md") else "result"} for path in declared]
    script_paths = ["evidence/replay/REPLAY_SCRIPT_EXECUTED.py",
                    "evidence/replay_complete/REPLAY_SCRIPT_EXECUTED.py",
                    "evidence/replay_terminal_repaired/REPLAY_SCRIPT_EXECUTED.py",
                    "evidence/replay_terminal_synchronous/REPLAY_SCRIPT_EXECUTED.py",
                    "evidence/replay_terminal_factored/REPLAY_SCRIPT_EXECUTED.py",
                    "scripts/axiom_audit.py", "scripts/audit_controls.py",
                    "evidence/GENERATE_RELEASE_REPORT.py"]
    artifact_inputs = [{"path": path, "sha256": before, "sha256_after": source_after[path]}
                       for path, before in sorted(build["source_hashes_before"].items())]
    started = dt.datetime.fromisoformat(first["started_at"])
    finished = max(dt.datetime.fromisoformat(result["completed_at"])
                   for result in [build, selected, terminal, interface, controls])
    manifest = {
        "schema_version": 2, "claim_id": summary["claim_id"],
        "repository": {"commit": None, "dirty": None,
                       "note": "The source project was recovered from an archive, not an identified Git checkout; immutable source and catalogue hashes define the inputs."},
        "command": {"initial_source_replay": first["argv"],
                    "continued_source_replay": continuation["argv"],
                    "repaired_terminal_source_replay": repair_attempt["argv"],
                    "synchronous_terminal_retry": synchronous_attempt["argv"],
                    "factored_terminal_source_replay": build["argv"],
                    "selected_axiom_audit": selected["command"],
                    "terminal_axiom_audit": terminal["command"],
                    "interface_axiom_audit": interface["command"],
                    "negative_controls": [row["command"] for row in controls["controls"]]},
        "environment": {
            "software": {"python": platform.python_version(), "lean": build["lean_version"],
                         "lean_binary_sha256": build["lean_binary_sha256"],
                         "mathlib_commit": build["mathlib_commit"], "dependencies": pins["dependencies"]},
            "hardware": {"architecture": platform.machine(), "visible_logical_cpus": os.cpu_count(),
                         "cgroup_cpu_quota_cores": 8, "cgroup_memory_limit_bytes": 8589934592}},
        "mathematics": {
            "assertion_tested": "All 423 catalogue-selected Lean source modules compile freshly under the stated pins; all 4342 catalogue names resolve to their owners; every logical declaration owned by those modules has transitive axiom dependencies within the three allowed standard axioms. The terminal and single-candidate interface satisfy the same compile and ownership/axiom checks as separately counted additions.",
            "coefficient_domain": "Exactly the types and hypotheses of the immutable selected Lean sources and separately fingerprinted additions.",
            "conventions": "Catalogue-based selection; generated/private logical declarations are included; compiler-only auxiliary names are listed separately; only current-session fresh objects may be resumed.",
            "inputs": ["catalogues/SOURCE_CATALOG.json", "catalogues/DECLARATION_CATALOG.json"],
            "bounds": {"selected_modules": 423, "catalogued_names": 4342, "terminal_modules": 1,
                       "interface_modules": 1, "selected_owned_logical_declarations": selected["owned_constant_count"]},
            "non_claims": summary["interpretation_limits"]},
        "randomness": {"used": False},
        "run": {"started_at": first["started_at"], "completed_at": finished.isoformat(),
                "runtime_seconds": (finished - started).total_seconds(), "status": "PASS",
                "exit_status": None,
                "exit_status_note": "This manifest aggregates separately recorded process receipts, not one shell-command exit. The initial run was partial after an early resource-driven SIGTERM; the continuation completed all selected sources but diagnosed terminal errors and was finalized after a terminal-only diagnostic SIGTERM. The first repaired-terminal run was killed with a contemporaneous cgroup OOM event. The unchanged-source synchronous retry suffered a second recorded OOM kill. The factored terminal replay and three audits exited successfully; both axiom negative controls deliberately exited 1.",
                "timeout_seconds": None, "max_output_bytes": None,
                "resource_limits": {"initial_compile_wall_seconds_per_module": 1200,
                                    "continued_compile_wall_seconds_per_module": 3600,
                                    "axiom_audit_wall_seconds_per_scope": 1200,
                                    "lean_threads_per_compilation": 1,
                                    "initial_parallel_compilers": first["jobs"],
                                    "continued_parallel_compilers": build["jobs"]},
                "missing_results": [], "invalid_results": []},
        "execution_artifacts": {path: {"sha256": digest(root / path)} for path in script_paths},
        "input_artifacts": artifact_inputs,
        "output_directory": "evidence",
        "declared_results": ["evidence/" + path for path in declared],
        "outputs": outputs,
        "checks": [
            {"check": "423 selected modules compile and retain catalogue fingerprints", "passed": True},
            {"check": "All 4342 distinct catalogue names resolve to their recorded owners", "passed": True},
            {"check": "All owned logical declarations in each scope have only allowed transitive axioms", "passed": True},
            {"check": "Terminal and interface compile and audit separately", "passed": True},
            {"check": "All three aggregate imports compile", "passed": True},
            {"check": "Negative controls reject the hidden custom axiom and absent name", "passed": True},
            {"check": "Source and audited-object hashes are unchanged", "passed": True},
            {"check": "Resume uses authenticated current-session fresh objects, no inherited archive objects", "passed": True},
            {"check": "Terminal-revision resume passed 34 focused controls and a read-only actual-lineage preflight", "passed": True}],
        "result": "PASS for the exact formal compilation, catalogue resolution and owning-module axiom assertions above. Mathematical interpretation remains limited to the stated source hypotheses.",
        "residual_risks": summary["interpretation_limits"],
        "failure_history": ["replay/RESULT.json", "RESOURCE_RESTART.json", "replay_complete/RESULT.json", "replay_terminal_repaired/RESULT.json", "TERMINAL_OOM_RETRY.json", "replay_terminal_synchronous/RESULT.json", "TERMINAL_SYNCHRONOUS_OOM.json", "terminal_repair/", "axiom_pilot/", "axiom_pilot_corrected/", "axioms_selected/", "axioms_selected_final/", "axioms_selected_resolved/", "axioms_selected_complete/"],
        "archive_path_mapping": {"original_project_sources": "formalization/",
                                 "original_project_evidence": "verification/lean/",
                                 "compiled_objects": "omitted; fingerprints retained in source replay and audit receipts",
                                 "downloaded_runtime_and_dependencies": "omitted; official pinned bootstrap provided"}
    }
    write("COMPUTATION_MANIFEST.json", manifest)
    print(json.dumps({"status": "PASS", "scopes": scopes,
                      "tower_seconds": tower["seconds"], "report_files_written": 4}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
