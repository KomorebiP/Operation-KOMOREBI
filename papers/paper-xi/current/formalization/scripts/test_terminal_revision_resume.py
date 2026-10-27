#!/usr/bin/env python3
"""Focused temporary-fixture controls for replay.py's terminal revision gate.

No Lean compiler is invoked and no production source/receipt/object is changed.
--output names a new JSON computation manifest; detailed results are written
beside it. All fixtures contain 423 selected sources and the two additions.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPLAY = SCRIPT.with_name("replay.py")
spec = importlib.util.spec_from_file_location("paperxi_resume_controls_target", REPLAY)
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


class Fixture:
    def __init__(self, root: Path):
        self.root = root
        self.selected = [f"PaperXI.Fixture{i:03d}" for i in range(423)]
        self.groups = {name: "selected" for name in self.selected}
        self.groups.update({replay.TERMINAL_MODULE: "terminal", replay.INTERFACE_MODULE: "new_interface"})
        self.graph = {name: ({self.selected[i-1]} if i else set()) for i, name in enumerate(self.selected)}
        self.graph[replay.INTERFACE_MODULE] = {self.selected[0]}
        self.graph[replay.TERMINAL_MODULE] = {self.selected[-1]}
        for name in self.groups:
            source = root / self.source(name)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("".join(f"import {dep}\n" for dep in sorted(self.graph[name]))
                              + "def fixtureValue := 0\n")
        write_json(root / "lake-manifest.json", {"fixture": "pinned dependencies"})
        self.old_hashes = self.source_hashes()
        self.old = self.old_hashes[replay.TERMINAL_SOURCE]
        common = {"status": "PARTIAL_OR_FAIL", "started_at": "2026-01-01T00:00:00+00:00",
                  "completed_at": "2026-01-01T00:01:00+00:00", "elapsed_seconds": 60,
                  "lean_version": "fixture Lean pin", "lean_binary_sha256": "1" * 64,
                  "mathlib_commit": "2" * 40, "all_sources_unchanged": True,
                  "source_hashes_before": self.old_hashes, "source_hashes_after": self.old_hashes}
        self.first = {**copy.deepcopy(common), "paperxi_objects_reused": False, "modules": []}
        self.second = {**copy.deepcopy(common), "paperxi_objects_reused": True,
                       "lake_manifest_sha256": digest(root / "lake-manifest.json"), "modules": []}
        self.first_dir = root / "evidence/first"
        self.second_dir = root / "evidence/second"
        self.first_path = self.first_dir / "RESULT.json"
        self.second_path = self.second_dir / "RESULT.json"
        inherited = set(self.selected[:421]) | {replay.INTERFACE_MODULE}
        for name in self.groups:
            first_pass = name in inherited
            self.first["modules"].append(self.row(name, self.first_dir, "PASS" if first_pass else "BLOCKED"))
        self.save_first()
        first_rows = {row["module"]: row for row in self.first["modules"]}
        for name in self.groups:
            if name in inherited:
                old_row = first_rows[name]
                row = copy.deepcopy(old_row)
                row["artifacts"] = self.artifacts(name, self.second_dir)
                row["resumed_from"] = {"result_path": "evidence/first/RESULT.json",
                                       "result_sha256": digest(self.first_path),
                                       "original_artifacts": copy.deepcopy(old_row["artifacts"])}
            else:
                row = self.row(name, self.second_dir, "FAIL" if name == replay.TERMINAL_MODULE else "PASS")
            self.second["modules"].append(row)
        self.second["resume"] = {"result_path": "evidence/first/RESULT.json",
                                 "result_sha256": digest(self.first_path),
                                 "authenticated_modules": 422, "authenticated_selected_modules": 421,
                                 "earlier_report_reused_paperxi_objects": False}
        self.save_second()
        for folder in [self.first_dir, self.second_dir]:
            write_json(folder / "DEPENDENCY_GRAPH.json", {name: sorted(deps) for name, deps in self.graph.items()})
        terminal = root / replay.TERMINAL_SOURCE
        terminal.write_text(terminal.read_text().replace(":= 0", ":= 1"))
        self.new = digest(terminal)
        self.current = {**copy.deepcopy(common), "lake_manifest_sha256": digest(root / "lake-manifest.json"),
                        "source_hashes_before": self.source_hashes()}

    @staticmethod
    def source(name):
        return str(Path(*name.split(".")).with_suffix(".lean"))

    def source_hashes(self):
        return {self.source(name): digest(self.root / self.source(name)) for name in self.groups}

    def artifacts(self, name, folder):
        result = {}
        for suffix in [".olean", ".ilean"]:
            path = folder / "objects" / (str(Path(*name.split("."))) + suffix)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(("synthetic object " + name + suffix).encode())
            result[str(path.relative_to(self.root))] = digest(path)
        return result

    def row(self, name, folder, status):
        if status == "BLOCKED":
            return {"module": name, "group": self.groups[name], "status": status}
        return {"module": name, "group": self.groups[name], "status": status,
                "exit_code": 0 if status == "PASS" else -15,
                "source_path": self.source(name), "source_sha256": self.old_hashes[self.source(name)],
                "source_unchanged": True, "artifacts": self.artifacts(name, folder) if status == "PASS" else {}}

    def get(self, name, first=False):
        return next(row for row in (self.first if first else self.second)["modules"] if row["module"] == name)

    def save_first(self):
        write_json(self.first_path, self.first)

    def save_second(self):
        write_json(self.second_path, self.second)

    def change_source(self, name):
        p = self.root / self.source(name)
        p.write_text(p.read_text() + "-- a changed successful source\n")
        self.current["source_hashes_before"] = self.source_hashes()

    def make_unchanged(self):
        p = self.root / replay.TERMINAL_SOURCE
        p.write_text(p.read_text().replace(":= 1", ":= 0"))
        self.current["source_hashes_before"] = self.source_hashes()

    def state(self):
        return {str(p.relative_to(self.root)): ("symlink:" + str(p.readlink()) if p.is_symlink() else digest(p))
                for p in sorted(self.root.rglob("*")) if p.is_file() or p.is_symlink()}


def altered_receipt(f, key, value):
    f.second[key] = value
    f.save_second()


def changed_terminal_status(f, value):
    f.get(replay.TERMINAL_MODULE)["status"] = value
    f.save_second()


def changed_graph(f):
    graph = {name: sorted(deps) for name, deps in f.graph.items()}
    graph[f.selected[0]] = [f.selected[-1]]
    write_json(f.second_dir / "DEPENDENCY_GRAPH.json", graph)


def corrupt_object(f, first=False):
    row = f.get(f.selected[0], first=first)
    p = f.root / next(iter(row["artifacts"]))
    p.write_bytes(b"corrupted synthetic object")


def changed_inherited_content(f):
    row = f.get(f.selected[0])
    relative = next(iter(row["artifacts"]))
    p = f.root / relative
    p.write_bytes(b"coherently rehashed but noninherited object")
    row["artifacts"][relative] = digest(p)
    f.save_second()


def unsafe_object(f):
    row = f.get(f.selected[0])
    row["artifacts"]["../outside.olean"] = "0" * 64
    f.save_second()


def symlink_object(f):
    p = f.root / next(iter(f.get(f.selected[0])["artifacts"]))
    other = p.with_suffix(p.suffix + ".saved")
    p.rename(other)
    p.symlink_to(other)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    details = output.with_name(output.stem + ".results.json")
    if output.exists() or details.exists():
        parser.error("Choose new output paths; controls do not overwrite receipts")
    began = dt.datetime.now(dt.timezone.utc).isoformat()
    started = time.monotonic()
    inputs = {str(path): digest(path) for path in [REPLAY, SCRIPT]}
    cases = [
        ("explicit_failed_terminal_revision_accepted", True, None, "revision", None),
        ("unchanged_default_resume_accepted", True, lambda f: f.make_unchanged(), "default", None),
        ("changed_terminal_without_flag_rejected", False, None, "default", "without an explicit"),
        ("wrong_old_fingerprint_rejected", False, None, "wrong_old", "fingerprints or source identity"),
        ("wrong_new_fingerprint_rejected", False, None, "wrong_new", "fingerprints or source identity"),
        ("revision_without_actual_change_rejected", False, lambda f: f.make_unchanged(), "revision", "exactly the terminal"),
        ("changed_selected_source_rejected", False, lambda f: f.change_source(f.selected[0]), "revision", "successful source receipt"),
        ("changed_interface_source_rejected", False, lambda f: f.change_source(replay.INTERFACE_MODULE), "revision", "successful source receipt"),
        ("running_predecessor_rejected", False, lambda f: altered_receipt(f, "status", "RUNNING"), "revision", "unfinished or invalid"),
        ("unfinalized_source_map_rejected", False, lambda f: altered_receipt(f, "source_hashes_after", {}), "revision", "unfinalized source hashes"),
        ("passed_overall_predecessor_rejected", False, lambda f: altered_receipt(f, "status", "PASS"), "revision", "finalized failed terminal"),
        ("blocked_terminal_rejected", False, lambda f: changed_terminal_status(f, "BLOCKED"), "revision", "finalized failed terminal"),
        ("previously_passed_terminal_rejected", False, lambda f: changed_terminal_status(f, "PASS"), "revision", "successful source receipt"),
        ("incomplete_successful_population_rejected", False,
         lambda f: (f.get(f.selected[-1]).update(status="FAIL"), f.save_second()), "revision", "all 423 selected modules"),
        ("changed_current_manifest_rejected", False, lambda f: (f.root / "lake-manifest.json").write_text("{}\n"), "revision", "Current dependency manifest"),
        ("changed_recorded_manifest_rejected", False, lambda f: altered_receipt(f, "lake_manifest_sha256", "9" * 64), "revision", "dependency manifest mismatch"),
        ("missing_predecessor_manifest_rejected", False, lambda f: altered_receipt(f, "lake_manifest_sha256", None), "revision", "lacks a dependency manifest"),
        ("manifest_changed_during_prior_run_rejected", False, lambda f: altered_receipt(f, "lake_manifest_sha256_after", "8" * 64), "revision", "changed during its execution"),
        ("runtime_changed_during_prior_run_rejected", False, lambda f: altered_receipt(f, "lean_binary_sha256_after", "7" * 64), "revision", "changed during its execution"),
        ("runtime_version_mismatch_rejected", False, lambda f: altered_receipt(f, "lean_version", "different"), "revision", "runtime mismatch"),
        ("runtime_binary_mismatch_rejected", False, lambda f: altered_receipt(f, "lean_binary_sha256", "3" * 64), "revision", "runtime mismatch"),
        ("mathlib_pin_mismatch_rejected", False, lambda f: altered_receipt(f, "mathlib_commit", "4" * 40), "revision", "runtime mismatch"),
        ("changed_saved_import_graph_rejected", False, changed_graph, "revision", "import/dependency closure"),
        ("changed_current_import_graph_rejected", False, lambda f: f.graph[f.selected[0]].add(f.selected[-1]), "revision", "import/dependency closure"),
        ("corrupted_latest_object_rejected", False, corrupt_object, "revision", "object path or fingerprint"),
        ("corrupted_ancestor_object_rejected", False, lambda f: corrupt_object(f, first=True), "revision", "object path or fingerprint"),
        ("changed_ancestor_receipt_hash_rejected", False, lambda f: f.first_path.write_text(f.first_path.read_text() + " "), "revision", "ancestor result fingerprint"),
        ("forged_inherited_origin_rejected", False,
         lambda f: (f.get(f.selected[0])["resumed_from"].update(result_sha256="5" * 64), f.save_second()), "revision", "inherited object/source lineage"),
        ("rehashed_noninherited_object_rejected", False, changed_inherited_content, "revision", "inherited object/source lineage"),
        ("inherited_population_count_mismatch_rejected", False,
         lambda f: (f.second["resume"].update(authenticated_modules=423), f.save_second()), "revision", "inherited-module population"),
        ("duplicate_module_result_rejected", False,
         lambda f: (f.second["modules"].append(copy.deepcopy(f.second["modules"][0])), f.save_second()), "revision", "missing, duplicated or changed"),
        ("escaping_object_path_rejected", False, unsafe_object, "revision", "object path or fingerprint"),
        ("symlinked_object_rejected", False, symlink_object, "revision", "symlinked"),
    ]
    results = []
    for name, should_accept, mutate, mode, expected_error in cases:
        t = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="paperxi_terminal_resume_") as tmp:
            f = Fixture(Path(tmp))
            if mutate:
                mutate(f)
            before = f.state()
            revision = None if mode == "default" else (("0" * 64 if mode == "wrong_old" else f.old),
                                                        ("f" * 64 if mode == "wrong_new" else f.new))
            error, plan = None, None
            try:
                plan = replay.authenticate_resume(f.root, f.second_dir, f.current, f.groups, f.graph, revision)
                accepted = True
            except RuntimeError as exc:
                accepted, error = False, str(exc)
            unchanged = before == f.state()
            outcome = accepted == should_accept and unchanged
            if expected_error:
                outcome = outcome and error is not None and expected_error in error
            if accepted:
                metadata = plan["resume"]
                outcome = outcome and (len(plan["rows"]) == 424
                    and replay.TERMINAL_MODULE not in {row["module"] for row in plan["rows"]}
                    and metadata["authenticated_selected_modules"] == 423
                    and len(metadata["lineage"]) == 2
                    and metadata["lineage"][0]["inherited_modules"] == 0
                    and metadata["lineage"][1]["inherited_modules"] == 422
                    and metadata["ancestors_without_recorded_manifest"] == ["evidence/first/RESULT.json"])
                if mode == "revision":
                    outcome = outcome and metadata["terminal_revision"]["invalidated_modules"] == [replay.TERMINAL_MODULE]
            results.append({"name": name, "expected_accept": should_accept, "accepted": accepted,
                            "inputs_unchanged": unchanged, "error": error,
                            "status": "PASS" if outcome else "FAIL", "seconds": time.monotonic() - t})
    cli = subprocess.run([sys.executable, "-B", str(REPLAY), "--terminal-revision", "a" * 64, "b" * 64],
                         capture_output=True, text=True)
    cli_ok = cli.returncode == 2 and "requires --resume" in cli.stderr
    results.append({"name": "revision_cli_without_resume_rejected", "status": "PASS" if cli_ok else "FAIL",
                    "exit_code": cli.returncode, "expected_exit_code": 2})
    inputs_after = {path: digest(Path(path)) for path in inputs}
    passed = all(row["status"] == "PASS" for row in results) and inputs == inputs_after
    result = {"status": "PASS" if passed else "FAIL", "control_count": len(results),
              "scope": "Synthetic resume-authentication controls; no Lean compilation or final release assertion.",
              "results": results}
    write_json(details, result)
    manifest = {"schema_version": 2, "claim_id": "PAPERXI-TERMINAL-REVISION-RESUME-INTEGRITY",
        "repository": {"commit": None, "dirty": None, "note": "Recovered archive project; exact script hashes identify the inputs."},
        "command": [sys.executable, *sys.argv],
        "environment": {"software": [{"name": "Python", "version": platform.python_version()}],
                        "hardware": {"architecture": platform.machine(), "platform": platform.platform()}},
        "mathematics": {"assertion_tested": "The bounded acceptance/rejection controls enforce the explicit failed-terminal source-change contract and authenticate unchanged successful objects and multi-run lineage.",
                        "coefficient_domain": "SHA-256 fingerprints and exact JSON/string/file comparisons",
                        "conventions": "Each fixture has 423 selected sources, one interface, one terminal and two finalized ancestor runs; fixture object bytes are synthetic.",
                        "inputs": [str(REPLAY), str(SCRIPT)], "bounds": {"controls": len(results), "fixture_modules": 425, "ancestor_runs": 2},
                        "non_claims": ["Does not compile Lean or certify terminal mathematics.", "Does not replace the final replay or axiom audit.", "Does not retrospectively fill the first-run manifest gap."]},
        "randomness": {"used": False},
        "run": {"started_at": began, "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "runtime_seconds": time.monotonic() - started, "exit_status": 0 if passed else 1,
                "status": "completed" if passed else "failed", "resource_limits": {"max_threads": 1}},
        "outputs": [{"path": details.name, "sha256": digest(details), "kind": "result"}],
        "checks": [{"check": row["name"], "passed": row["status"] == "PASS"} for row in results],
        "result": result["status"], "residual_risks": result["scope"],
        "input_artifacts": [{"path": path, "sha256": before, "sha256_after": inputs_after[path]} for path, before in inputs.items()],
        "declared_results": [details.name]}
    write_json(output, manifest)
    print(json.dumps({"status": result["status"], "controls": len(results), "manifest": str(output),
                      "results": str(details), "failed": [row["name"] for row in results if row["status"] != "PASS"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
