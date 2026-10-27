#!/usr/bin/env python3
"""Audit catalogue names and every imported constant owned by selected modules.

Lean's module-ownership map defines the audited population. Catalogue names
must resolve to their stated owning modules, and all owned constants are
checked for transitive axiom dependencies. The output includes generated and
private constants visible in the imported kernel environment.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import subprocess
import time

from replay import ROOT, locate_bin, runtime_environment, sha, stamp, write_json

ALLOWED = {"Classical.choice", "Quot.sound", "propext"}

LEAN_BODY = r'''
open Lean Elab Command

-- The release catalogue has 4,342 entries; elaborating its literal array
-- exceeds Lean's default recursion-depth guard before the audit can run.
set_option maxRecDepth 32768

private def auditKind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .inductInfo _ => "inductive"

private def auditOwners : Array Name := OWNERS
private def auditCatalogue : Array (Name × Name) := CATALOGUE

set_option maxHeartbeats 10000000 in
run_cmd do
  let env ← getEnv
  let allowed : Array Name := #[``Classical.choice, ``Quot.sound, ``propext]
  let mut forbidden : Nat := 0
  let mut count : Nat := 0
  let mut catalogueCount : Nat := 0
  let mut auxiliaryCount : Nat := 0
  let mut selectedIdxs : Std.HashSet ModuleIdx := {}
  for owner in auditOwners do
    let some idx := env.getModuleIdx? owner |
      throwError "Requested owning module is not imported: {owner}"
    selectedIdxs := selectedIdxs.insert idx
  for (name, expectedOwner) in auditCatalogue do
    unless (env.find? name).isSome do
      throwError "Catalogue name is absent: {name}"
    let some idx := env.getModuleIdxFor? name |
      throwError "Catalogue name has no imported owner: {name}"
    let owner := env.header.moduleNames[idx.toNat]!
    unless owner == expectedOwner do
      throwError "Catalogue owner mismatch for {name}: {owner} != {expectedOwner}"
    catalogueCount := catalogueCount + 1
    liftIO <| IO.println <| (Json.mkObj [
      ("event", toJson "catalogue"), ("name", toJson name.toString),
      ("module", toJson owner.toString)]).compress
  let entries := (env.const2ModIdx.toList.filter (fun entry => selectedIdxs.contains entry.2)).toArray.qsort (fun a b => Name.lt a.1 b.1)
  for (name, idx) in entries do
    let owner := env.header.moduleNames[idx.toNat]!
    if let some info := (env.setExporting false).toKernelEnv.find? name then
      let axioms ← collectAxioms name
      let extra := axioms.filter (fun ax => !allowed.contains ax)
      count := count + 1
      if !extra.isEmpty then forbidden := forbidden + 1
      liftIO <| IO.println <| (Json.mkObj [
        ("event", toJson "owned_constant"), ("name", toJson name.toString),
        ("module", toJson owner.toString), ("kind", toJson (auditKind info)),
        ("unsafe", toJson info.isUnsafe),
        ("axioms", toJson (axioms.map Name.toString)),
        ("forbidden_axioms", toJson (extra.map Name.toString))]).compress
    else
      auxiliaryCount := auxiliaryCount + 1
      liftIO <| IO.println <| (Json.mkObj [
        ("event", toJson "compiler_auxiliary"), ("name", toJson name.toString),
        ("module", toJson owner.toString)]).compress
  liftIO <| IO.println <| (Json.mkObj [
    ("event", toJson "summary"), ("owned_constant_count", toJson count),
    ("catalogue_count", toJson catalogueCount),
    ("compiler_auxiliary_count", toJson auxiliaryCount),
    ("forbidden_constant_count", toJson forbidden),
    ("requested_module_count", toJson auditOwners.size)]).compress
  unless forbidden == 0 do
    throwError "Nonstandard axioms found in {forbidden} owned constants"
'''


def lean_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def generate(imports: list[str], owners: list[str], catalogue: list[dict]) -> str:
    owners_text = "#[" + ", ".join(lean_string(x) + ".toName" for x in owners) + "]"
    catalogue_text = "#[\n" + ",\n".join(
        "  (" + lean_string(x["name"]) + ".toName, " + lean_string(x["module"]) + ".toName)"
        for x in catalogue) + "\n]"
    header = "".join("import " + x + "\n" for x in imports)
    header += "import Lean.Elab.Command\nimport Lean.Util.CollectAxioms\n"
    return header + LEAN_BODY.replace("OWNERS", owners_text).replace("CATALOGUE", catalogue_text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", default="evidence/replay")
    parser.add_argument("--out", required=True)
    parser.add_argument("--lean-bin")
    parser.add_argument("--scope", choices=["selected", "terminal", "new_interface"], default="selected")
    parser.add_argument("--module", action="append")
    args = parser.parse_args()
    replay = (ROOT / args.replay).resolve()
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        parser.error("--out must be a new directory inside this project")
    out.mkdir(parents=True)
    source_catalogue = json.loads((ROOT / "catalogues/SOURCE_CATALOG.json").read_text())["modules"]
    declaration_catalogue = json.loads((ROOT / "catalogues/DECLARATION_CATALOG.json").read_text())
    if args.scope == "selected":
        owners = sorted(source_catalogue)
    elif args.scope == "terminal":
        owners = ["PaperXI.ActualMonomialLocalGlobal"]
    else:
        owners = ["PaperXI.SingleCandidateComparison"]
    if args.module:
        if not set(args.module) <= set(owners):
            parser.error("--module must be within the declared scope")
        owners = sorted(set(args.module))
    if args.scope == "selected":
        catalogue = [x for x in declaration_catalogue if x["module"] in owners]
    elif args.scope == "new_interface":
        catalogue = [{"name": "PaperXI.SingleCandidateComparison.source", "module": owners[0]}]
    else:
        catalogue = []
    inputs = {str((ROOT / Path(*name.split(".")).with_suffix(".lean")).relative_to(ROOT)):
              sha(ROOT / Path(*name.split(".")).with_suffix(".lean")) for name in owners}
    build_path = replay / "RESULT.json"
    build = json.loads(build_path.read_text())
    passed_modules = {row["module"]: row for row in build["modules"] if row["status"] == "PASS"}
    graph = json.loads((replay / "DEPENDENCY_GRAPH.json").read_text())
    closure = set(owners)
    pending = list(owners)
    while pending:
        name = pending.pop()
        if name not in passed_modules:
            raise RuntimeError(f"The audited import closure was not successfully compiled: {name}")
        for dependency in graph[name]:
            if dependency not in closure:
                closure.add(dependency)
                pending.append(dependency)
    for path, digest in inputs.items():
        if build["source_hashes_before"].get(path) != digest:
            raise RuntimeError(f"Audited source differs from its replay input: {path}")
    object_inputs = {path: digest for name in closure
                     for path, digest in passed_modules[name]["artifacts"].items()}
    for path, digest in object_inputs.items():
        if sha(ROOT / path) != digest:
            raise RuntimeError(f"Audited import object differs from its replay receipt: {path}")
    bin_dir = locate_bin(args.lean_bin)
    env = runtime_environment(bin_dir, replay / "objects")
    lean_version = subprocess.check_output([str(bin_dir / "lean"), "--version"], env=env, text=True).strip()
    if lean_version != build["lean_version"] or sha(bin_dir / "lean") != build["lean_binary_sha256"]:
        raise RuntimeError("Audit compiler differs from the source replay compiler")
    source = out / "OwningModuleAudit.lean"
    source.write_text(generate(owners, owners, catalogue))
    command = [str(bin_dir / "lean"), "-j1", "-DwarningAsError=true", str(source)]
    started_at = stamp()
    t = time.monotonic()
    log = out / "AXIOMS.log"
    with log.open("w") as f:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT,
                                timeout=1200)
    events = []
    for line in log.read_text(errors="replace").splitlines():
        if line.startswith('{"'):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "event" in event:
                events.append(event)
    owned = [x for x in events if x["event"] == "owned_constant"]
    auxiliaries = [x for x in events if x["event"] == "compiler_auxiliary"]
    resolved = [x for x in events if x["event"] == "catalogue"]
    summaries = [x for x in events if x["event"] == "summary"]
    expected_catalogue = {(x["name"], x["module"]) for x in catalogue}
    observed_catalogue = {(x["name"], x["module"]) for x in resolved}
    owned_names = {(x["name"], x["module"]) for x in owned}
    by_module = collections.Counter(x["module"] for x in owned)
    forbidden = [x for x in owned if set(x["axioms"]) - ALLOWED]
    after = {path: sha(ROOT / path) for path in inputs}
    object_after = {path: sha(ROOT / path) for path in object_inputs}
    complete = (result.returncode == 0 and len(summaries) == 1
                and summaries[0]["owned_constant_count"] == len(owned)
                and summaries[0]["catalogue_count"] == len(catalogue)
                and summaries[0]["compiler_auxiliary_count"] == len(auxiliaries)
                and summaries[0]["requested_module_count"] == len(owners)
                and len(owned_names) == len(owned)
                and expected_catalogue == observed_catalogue
                and expected_catalogue <= owned_names
                and not forbidden and inputs == after and object_inputs == object_after)
    report = {
        "status": "PASS" if complete else "FAIL", "started_at": started_at,
        "completed_at": stamp(), "seconds": time.monotonic() - t,
        "scope": args.scope, "module_subset_requested": args.module,
        "command": command, "exit_code": result.returncode,
        "source_replay_result_path": str(build_path.relative_to(ROOT)),
        "source_replay_result_sha256": sha(build_path),
        "lean_version": lean_version, "lean_binary_sha256": sha(bin_dir / "lean"),
        "script_sha256": sha(Path(__file__)),
        "authenticated_import_closure_modules": sorted(closure),
        "object_hashes_before": object_inputs, "object_hashes_after": object_after,
        "objects_unchanged": object_inputs == object_after,
        "requested_modules": owners, "module_count": len(owners),
        "catalogued_name_count": len(catalogue), "catalogued_names_resolved": len(resolved),
        "catalogue_owner_checks_passed": expected_catalogue == observed_catalogue,
        "catalogue_is_subset_of_owned_constants": expected_catalogue <= owned_names,
        "owned_constant_count": len(owned), "owned_constant_counts_by_module": dict(sorted(by_module.items())),
        "compiler_auxiliary_count": len(auxiliaries),
        "compiler_auxiliary_note": "Lean's module-ownership map also records code-generator names absent from its kernel constant map; these are enumerated separately and are not logical declarations. See the pinned Lean Environment.lean definitions of ModuleData.extraConstNames and Kernel.Environment.const2ModIdx.",
        "owned_constant_kinds": dict(sorted(collections.Counter(x["kind"] for x in owned).items())),
        "unsafe_owned_constants": [x["name"] for x in owned if x["unsafe"]],
        "allowed_axioms": sorted(ALLOWED),
        "observed_axioms": sorted({ax for x in owned for ax in x["axioms"]}),
        "forbidden_constants": forbidden, "source_hashes_before": inputs,
        "source_hashes_after": after, "sources_unchanged": inputs == after,
        "audit_source_sha256": sha(source), "log_sha256": sha(log),
        "population_definition": "Every logical constant in the imported private kernel environment whose owner is a requested module, including generated and private logical declarations. Code-generator-only auxiliary names, which Lean documents as invisible to its kernel, are separately enumerated.",
        "external_dependencies": "Pinned official cache objects are imported, not rebuilt by this audit.",
        "interpretation": "Resolves the stated declaration names and checks transitive axiom dependencies over authenticated source-replay objects. Fresh source compilation establishes kernel acceptance separately; no independent-checker claim is made by this audit.",
    }
    write_json(out / "RESULT.json", report)
    write_json(out / "OWNED_CONSTANTS.json", owned)
    write_json(out / "COMPILER_AUXILIARIES.json", auxiliaries)
    write_json(out / "CATALOGUE_RESOLUTION.json", resolved)
    print(json.dumps({k: report[k] for k in ["status", "scope", "module_count", "catalogued_name_count",
          "catalogued_names_resolved", "owned_constant_count", "observed_axioms", "seconds"]}), flush=True)
    if not complete:
        print(log.read_text(errors="replace")[-8000:])
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
