#!/usr/bin/env python3
"""Aggregate actual Paper XI release receipts; refuse to describe missing gates as passed.

Usage: python3 GENERATE_RELEASE_REPORT.py /path/to/working/formalization-project
The positional argument is explicit so this retained report generator contains
no dependency on the original workspace's absolute path.
"""
from __future__ import annotations

import collections
import datetime as dt
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
    build = read("replay_complete/RESULT.json")
    selected = read("axioms_selected/RESULT.json")
    terminal = read("axioms_terminal/RESULT.json")
    interface = read("axioms_interface_final/RESULT.json")
    controls = read("axiom_controls_final/RESULT.json")
    download = read("LEAN_DOWNLOAD_RECEIPT.json")
    pins = read("DEPENDENCY_PINS.json")
    cache = read("MATHLIB_CACHE_RECEIPT.json")
    adaptation = read("ADDITIONS_RECEIPT.json")
    restart = read("RESOURCE_RESTART.json")
    portable = read("PORTABLE_PROJECT_RECEIPT.json")
    catalogue = json.loads((root / "catalogues/SOURCE_CATALOG.json").read_text())["modules"]
    names = json.loads((root / "catalogues/DECLARATION_CATALOG.json").read_text())
    rows = {row["module"]: row for row in build["modules"]}
    population = collections.Counter(row["group"] for row in rows.values())
    if len(rows) != 425 or population != {"selected": 423, "terminal": 1, "new_interface": 1}:
        raise RuntimeError("Final compiled population is not exactly 423 + 1 + 1")
    if len(catalogue) != 423 or len(names) != 4342 or len({row["name"] for row in names}) != 4342:
        raise RuntimeError("Retained catalogue population changed")
    for result in [build, selected, terminal, interface, controls]:
        if result["status"] != "PASS":
            raise RuntimeError("A required release gate did not pass")
    if selected["module_count"] != 423 or selected["catalogued_names_resolved"] != 4342:
        raise RuntimeError("Selected axiom audit did not cover the complete catalogue")
    if len(controls["controls"]) != 2 or not all(row["status"] == "PASS" for row in controls["controls"]):
        raise RuntimeError("The two negative controls did not pass")
    if len(build["aggregates"]) != 3 or not all(row["status"] == "PASS" for row in build["aggregates"]):
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
    for name, record in catalogue.items():
        path = str(Path(*name.split(".")).with_suffix(".lean"))
        if source_after.get(path) != record["sha256"]:
            raise RuntimeError(f"Final selected source differs from its retained catalogue: {name}")
    original_terminal = root / "terminal_original/ActualMonomialLocalGlobal.lean"
    repaired_terminal = root / "PaperXI/ActualMonomialLocalGlobal.lean"
    if digest(original_terminal) != adaptation["original_terminal_sha256"]:
        raise RuntimeError("The preserved original terminal changed")
    if digest(repaired_terminal) != adaptation["patched_terminal_sha256"]:
        raise RuntimeError("The repaired terminal differs from its adaptation receipt")
    insertion = b"import PaperXI.RamificationPolyphase\n"
    if repaired_terminal.read_bytes().count(insertion) != 1 or repaired_terminal.read_bytes().replace(insertion, b"", 1) != original_terminal.read_bytes():
        raise RuntimeError("The terminal change is not exactly the recorded added import line")
    if digest(root / "PaperXI/SingleCandidateComparison.lean") != adaptation["new_interface_source_sha256"]:
        raise RuntimeError("The separate interface differs from its source receipt")
    if first["paperxi_objects_reused"] or build["resume"]["earlier_report_reused_paperxi_objects"]:
        raise RuntimeError("The asserted fresh-object lineage does not hold")
    if digest(evidence / "replay/RESULT.json") != build["resume"]["result_sha256"]:
        raise RuntimeError("The earlier authenticated replay receipt changed")
    if build["resume"]["authenticated_selected_modules"] != 421:
        raise RuntimeError("The asserted first-attempt population changed")
    for audit in [selected, terminal, interface]:
        if audit["source_replay_result_sha256"] != digest(evidence / "replay_complete/RESULT.json"):
            raise RuntimeError("An audit refers to another source replay")
        if not audit["objects_unchanged"] or not audit["sources_unchanged"] or audit["forbidden_constants"]:
            raise RuntimeError("An audit integrity or axiom gate failed")
    tower = rows["PaperXI.UnramifiedFieldTower"]
    active_build_seconds = first["elapsed_seconds"] + build["elapsed_seconds"]
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
    summary = {
        "schema_version": 2, "recorded_at": now, "status": "PASS",
        "claim_id": "PAPERXI-RELEASE-SELECTED-423-FRESH-COMPILE-AND-AXIOM-AUDIT",
        "scopes": scopes,
        "selected_source_hashes_match_retained_catalogue": True,
        "all_425_sources_unchanged_through_release_reporting": True,
        "catalogue_population": {"selected_modules": 423, "unique_names": 4342},
        "compile_lineage": {
            "initial_result_status": first["status"],
            "initial_fresh_selected_passes": first["selected_modules_passed"],
            "initial_fresh_interface_passes": 1,
            "continuation_authenticated_objects": build["resume"]["authenticated_modules"],
            "continuation_newly_compiled_modules": sorted(row["module"] for row in rows.values()
                                                        if "resumed_from" not in row),
            "historical_paperxi_objects_used": False,
            "external_mathlib_cache_used": True,
            "external_mathlib_rebuilt": False,
            "initial_compiler_stopped_early": restart,
            "tower_successful_compile_seconds": tower["seconds"],
            "active_source_replay_wall_seconds_sum": active_build_seconds,
            "note": "Every target was freshly compiled in this release session. The continuation reuses only authenticated successful objects from the first fresh attempt. It does not make the first partial attempt a successful run."
        },
        "aggregate_imports": {row["module"]: row["status"] for row in build["aggregates"]},
        "negative_controls": [{k: row[k] for k in ["name", "status", "exit_code", "expected_error_text", "sentinel_checks"]}
                              for row in controls["controls"]],
        "fresh_leanchecker_pass": False,
        "independent_kernel_implementation_used": False,
        "kernel_acceptance_basis": "All selected and added target sources were freshly elaborated and checked by the pinned Lean compiler. The axiom audit enumerates logical declarations in its imported private kernel environment.",
        "historical_checker_receipts": "historical/Continuation113_final_replay_corrected/",
        "lean_version": build["lean_version"],
        "lean_binary_sha256": build["lean_binary_sha256"],
        "mathlib_commit": build["mathlib_commit"],
        "dependencies": pins["dependencies"],
        "terminal_original_sha256": adaptation["original_terminal_sha256"],
        "terminal_repaired_sha256": adaptation["patched_terminal_sha256"],
        "terminal_only_change": "Added import PaperXI.RamificationPolyphase; all nonimport lines unchanged.",
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

The terminal and interface do not change the selected 423-module or 4,342-name counts. The terminal has no entry in the publication declaration catalogue; its complete logical declaration population is still audited by owning module. All three aggregate imports passed. Compiler warning lines were retained: {warnings['selected']} in the selected files, {warnings['terminal']} in the terminal, and {warnings['new_interface']} in the interface. The selected source text was not edited to remove linter warnings. See [the complete source replay](replay_complete/RESULT.json).

## Fresh compilation and restart history

The first replay began with an empty Paper XI object directory and compiled 421 selected modules plus the new interface successfully. The unfinished `UnramifiedFieldTower` compiler was manually stopped after {next(row['seconds'] for row in first['modules'] if row['module'] == 'PaperXI.UnramifiedFieldTower'):.2f} seconds, before the original 1,200-second limit, after finding a retained historical build duration of 1,588 seconds. That early stop discarded an unfinished attempt and is explicitly preserved as a failure of the first run, with signal and reason in [RESOURCE_RESTART.json](RESOURCE_RESTART.json). It was not a compiler rejection of the source.

The continuation checked every source and completed-object fingerprint, copied only the 422 successful objects from this session's first replay, and used a 3,600-second per-module limit. It freshly compiled the tower, `ActualUnramifiedBaseChange`, and the terminal. The tower completed successfully in {tower['seconds']:.2f} seconds. The sum of the two source-run wall-clock durations was {active_build_seconds:.2f} seconds, including the discarded attempt; the receipts preserve each run's separate timestamps and commands. No inherited Paper XI object from the recovered archive was used. The successful continuation records the exact earlier receipt hash and object lineage; it does not overwrite the first run's `PARTIAL_OR_FAIL` result.

Each compiler process used `-j1` and the command-line `maxHeartbeats=3000000` setting, with any retained source-local options unchanged. All 425 source fingerprints were rechecked after compilation and again before this report. Details are in [the initial attempt](replay/RESULT.json) and [the completed continuation](replay_complete/RESULT.json).

## Axiom and ownership audit

The audit resolves each requested name to its actual imported owner and enumerates every logical constant owned by the target modules in Lean's imported private kernel environment. This includes generated declarations and private logical declarations. Each declaration's transitive axiom dependencies must belong to `Classical.choice`, `Quot.sound`, and `propext`. The observed union was {selected_ax} for the selected sources, {terminal_ax} for the terminal, and {interface_ax} for the interface. No forbidden axiom dependency was found.

Lean's ownership map also contains code-generator auxiliary names that are absent from its kernel constant map. The audit lists these separately and does not count them as logical declarations. This distinction follows the pinned Lean source definitions of `ModuleData.extraConstNames` and `Kernel.Environment.const2ModIdx`. The imported objects in each audited Paper XI dependency closure were authenticated against the successful replay receipt before the audit and fingerprinted again afterward. See [selected audit](axioms_selected/RESULT.json), [terminal audit](axioms_terminal/RESULT.json), and [interface audit](axioms_interface_final/RESULT.json); each directory retains the generated Lean audit, full log, resolved names and declaration-level axiom results.

Two isolated negative controls passed by being rejected for the intended reason: public and private uncatalogued custom axioms in a module with a safely catalogued theorem, and a deliberately missing catalogue name. The first control explicitly checks that both sentinel axioms are found and that the safely catalogued theorem has no axiom dependencies. Both Lean processes returned exit code 1 with the expected diagnostic. These fixtures are outside Paper XI and are not part of any release population. The [final control receipt](axiom_controls_final/RESULT.json) records the expected rejection checks.

The exploratory audit harness initially needed explicit `Nat` counter annotations, then needed to distinguish compiler-only auxiliary names from logical declarations. Those failed harness attempts are retained under `axiom_pilot/` and `axiom_pilot_corrected/`. The corrected kernel-backed population passed its pilot, final complete audit and negative controls. No selected theorem statement or proof body was changed in this process.

## Terminal repair and comparison interface

The preserved original terminal has SHA-256 `{adaptation['original_terminal_sha256']}`. Its compiled copy has SHA-256 `{adaptation['patched_terminal_sha256']}`. The sole change adds `import PaperXI.RamificationPolyphase`; every nonimport line, including all mathematical statements and proof bodies, remains unchanged. The original source is delivered with the portable project and the [exact diff](TERMINAL_IMPORT_REPAIR.patch) is retained here.

`PaperXI.SingleCandidateComparison.source` is an additional one-theorem module with SHA-256 `{adaptation['new_interface_source_sha256']}`. It applies the existing `LocalFactorIdentification.class_eq_iff` to one supplied admissible candidate and an admissible reference, with both factor profiles equal to the same declared profile. Its factor-equality hypothesis concerns that candidate. It does not require a realization-existence field or prove arithmetic existence. Its source, compilation and one-declaration audit are kept outside the selected catalogue counts.

## Environment and reproducibility

The Lean version is `{build['lean_version']}`. Its Linux binary fingerprint `{build['lean_binary_sha256']}` exactly matches the retained Continuation 113 environment. Mathlib is pinned to `{build['mathlib_commit']}`; all transitive package revisions are fixed in the delivered `lake-manifest.json`. The official Lean archive digest and binary match are recorded in [LEAN_DOWNLOAD_RECEIPT.json](LEAN_DOWNLOAD_RECEIPT.json), dependency revisions in [DEPENDENCY_PINS.json](DEPENDENCY_PINS.json), and official mathlib-cache retrieval in [MATHLIB_CACHE_RECEIPT.json](MATHLIB_CACHE_RECEIPT.json). External mathlib declarations were imported from the pinned official cache and were not rebuilt.

The portable project contains sources, catalogues, the original terminal, exact import diff, pinned Lake configuration and standard-library Python bootstrap/replay/audit scripts. It contains no downloaded runtime, dependency tree, cache or compiled objects. Its Linux x86_64 bootstrap, including WSL, downloads the official pinned dependencies into its own directory. The exact online setup components were exercised during runtime acquisition; the portable wrapper's offline pin/cache check passed. The convenience full-run wrapper was syntax checked; the individual release gates are the executions recorded here. The scripts compute paths from their own location and do not depend on the original workspace path. Raw command lines retain the actual execution paths for provenance.

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
    declared = ["replay_complete/RESULT.json", "axioms_selected/RESULT.json",
                "axioms_terminal/RESULT.json", "axioms_interface_final/RESULT.json",
                "axiom_controls_final/RESULT.json", "RELEASE_VERIFICATION.json", "RELEASE_VERIFICATION.md"]
    outputs = [{"path": "evidence/" + path, "sha256": digest(evidence / path),
                "kind": "report" if path.endswith(".md") else "result"} for path in declared]
    script_paths = ["evidence/replay/REPLAY_SCRIPT_EXECUTED.py",
                    "evidence/replay_complete/REPLAY_SCRIPT_EXECUTED.py",
                    "scripts/axiom_audit.py", "scripts/audit_controls.py",
                    "evidence/GENERATE_RELEASE_REPORT.py"]
    artifact_inputs = [{"path": path, "sha256": before, "sha256_after": source_after[path]}
                       for path, before in sorted(build["source_hashes_before"].items())]
    started = dt.datetime.fromisoformat(first["started_at"])
    finished = dt.datetime.fromisoformat(controls["completed_at"])
    manifest = {
        "schema_version": 2, "claim_id": summary["claim_id"],
        "repository": {"commit": None, "dirty": None,
                       "note": "The source project was recovered from an archive, not an identified Git checkout; immutable source and catalogue hashes define the inputs."},
        "command": {"initial_source_replay": first["argv"],
                    "continued_source_replay": build["argv"],
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
        "run": {"started_at": first["started_at"], "completed_at": controls["completed_at"],
                "runtime_seconds": (finished - started).total_seconds(), "status": "PASS",
                "exit_status": None,
                "exit_status_note": "This manifest aggregates separately recorded process receipts; it is not a single shell-command exit record. The initial source run was partial after a manual SIGTERM. The final compilation and three audits exited successfully; both negative controls deliberately exited 1.",
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
            {"check": "Resume uses authenticated current-session fresh objects, no inherited archive objects", "passed": True}],
        "result": "PASS for the exact formal compilation, catalogue resolution and owning-module axiom assertions above. Mathematical interpretation remains limited to the stated source hypotheses.",
        "residual_risks": summary["interpretation_limits"],
        "failure_history": ["replay/RESULT.json", "RESOURCE_RESTART.json", "axiom_pilot/", "axiom_pilot_corrected/"],
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
