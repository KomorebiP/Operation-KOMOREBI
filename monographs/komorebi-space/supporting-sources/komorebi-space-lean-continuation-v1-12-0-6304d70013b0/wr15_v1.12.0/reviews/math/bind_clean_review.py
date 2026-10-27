#!/usr/bin/env python3
"""Read-only terminal binding of the already completed WR15 semantic audit.

Creates reviewer outputs only under reviews/math/clean_wr15_01.  It never writes
to production source, the clean run, or that run's compiled-object directory.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

TASK = Path(__file__).resolve().parents[2]
RUN = TASK / "integration/runs/clean_wr15_01"
OUT = TASK / "reviews/math/clean_wr15_01"
APPROVED = {
    "KomorebiSpace/CoordinateCovector.lean":
        "151661fac5f9ef5e2212ef41d76bf179299b5da4c5df10bf07844f18e04decfe",
    "KomorebiSpace/CoordinateBasisChange.lean":
        "964ed871bf33db57c854b653125b9bf92416eefb5bc5df40877cd909ef366c07",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


receipt = json.loads((RUN / "receipt.json").read_text())
postflight = json.loads((RUN / "postflight.json").read_text())
assert receipt["status"] == "PASS", "Receipt is not terminal PASS"
assert postflight["status"] == "PASS", "Postflight is not terminal PASS"
assert receipt.get("finished_utc"), "Receipt has no terminal timestamp"
assert postflight["run_receipt_sha256"] == sha(RUN / "receipt.json")
assert postflight["axiom_report_sha256"] == sha(RUN / "axioms.json")
assert receipt["axiom_report_sha256"] == sha(RUN / "axioms.json")
assert not OUT.exists(), "Reviewer binding output already exists; preserve it"

for relative, expected in APPROVED.items():
    assert sha(TASK / "formal" / relative) == expected
    assert sha(RUN / "source" / relative) == expected
    assert receipt["source_snapshot_sha256"][relative] == expected

OUT.mkdir()
rows = json.loads((RUN / "new_declarations.json").read_text())
names = [r["name"] for r in rows]
assert len(set(names)) == len(names)
allowed = {"propext", "Classical.choice", "Quot.sound"}
assert all(r["type_mode"] == "full" and r["type"] and "⋯" not in r["type"] for r in rows)
assert all(not r["unsafe"] and set(r["axioms"]) <= allowed for r in rows)

public = {}
for relative in APPROVED:
    source = (RUN / "source" / relative).read_text()
    for kind, name in re.findall(r"^(?:noncomputable\s+)?(def|theorem)\s+(\w+)", source, re.M):
        public["KomorebiSpace.CoordinateCovector." + name] = (
            "definition" if kind == "def" else "theorem")
assert len(public) == 51
by_name = {r["name"]: r for r in rows}
assert all(name in by_name and by_name[name]["kind"] == kind for name, kind in public.items())
helpers = [r for r in rows if r["name"] not in public]

env = os.environ.copy()
env.update(receipt["environment"])
lean = Path(receipt["runtime"]) / "toolchain/bin/lean"
flags = [str(lean), "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
commands = []


def check_same_types(label, original_source, original_log):
    source = OUT / (label + ".lean")
    source.write_bytes(original_source.read_bytes())
    argv = flags + [str(source)]
    result = subprocess.run(argv, env=env, cwd=OUT, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = OUT / (label + ".log")
    log.write_text(result.stdout)
    commands.append({"label": label, "argv": argv, "cwd": str(OUT),
                     "exit_code": result.returncode, "log_sha256": sha(log)})
    assert result.returncode == 0, f"{label} failed; inspect reviewer log"
    equal = log.read_bytes() == original_log.read_bytes()
    assert equal, f"{label} output differs from reviewed public types"
    return {"all_types_and_axioms_byte_identical": equal,
            "new_log_sha256": sha(log), "reviewed_log_sha256": sha(original_log),
            "reviewed_log": str(original_log.relative_to(TASK))}


comparison = {
    "basis_17": check_same_types(
        "BasisTypesFromClean", TASK / "reviews/math/BasisTypes.lean",
        TASK / "reviews/math/basis_types.log"),
    "core_34": check_same_types(
        "CoreTypesFromClean", TASK / "development/coordinates/attempt_013/ExportTypes.lean",
        TASK / "development/coordinates/attempt_013/compile.log"),
}
write_json(OUT / "public_type_comparison.json", comparison)
write_json(OUT / "new_full_type_hashes.json",
           {r["name"]: hashlib.sha256(r["type"].encode()).hexdigest() for r in rows})
write_json(OUT / "generated_helpers_manifest.json", [
    {**{k: v for k, v in row.items() if k != "type"},
     "full_type_sha256": hashlib.sha256(row["type"].encode()).hexdigest(),
     "full_type_characters": len(row["type"])} for row in helpers])
(OUT / "helper_names.txt").write_text("\n".join(r["name"] for r in helpers) + "\n")
(OUT / "HelperTypes.lean").write_text('''import KomorebiSpace.CoordinateCovector
import Lean
set_option maxHeartbeats 0
set_option pp.maxSteps 10000000
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let names := (← IO.FS.readFile "helper_names.txt").splitOn "\\n"
  let mut rows : Array Json := #[]
  for (name, ci) in env.constants.toList do
    if names.contains name.toString then
      let typeString ← liftTermElabM do
        withOptions (fun o => o.setBool `pp.all false |>.setBool `pp.fullNames true
          |>.setBool `pp.universes true |>.setBool `pp.proofs false) do
          return (← Meta.ppExpr ci.type).pretty
      rows := rows.push <| Json.mkObj [("name", toJson name.toString),
        ("type", toJson typeString)]
  IO.FS.writeFile "generated_helpers_readable.json" (toJson rows).pretty
''')
argv = flags + [str(OUT / "HelperTypes.lean")]
result = subprocess.run(argv, env=env, cwd=OUT, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(OUT / "HelperTypes.log").write_text(result.stdout)
commands.append({"label": "HelperTypes", "argv": argv, "cwd": str(OUT),
                 "exit_code": result.returncode, "log_sha256": sha(OUT / "HelperTypes.log")})
assert result.returncode == 0
readable = json.loads((OUT / "generated_helpers_readable.json").read_text())
assert {r["name"] for r in readable} == {r["name"] for r in helpers}

write_json(OUT / "commands.json", {"commands": commands,
    "environment": {k: env[k] for k in ("LD_PRELOAD", "LEAN_PATH") if k in env}})
identities = {name: sha(RUN / name) for name in
              ("receipt.json", "postflight.json", "axioms.json", "new_declarations.json",
               "declarations_sorted.json")}
summary = {"schema": "wr15-independent-math-clean-binding-v1",
    "run": str(RUN.relative_to(TASK)), "receipt_status": receipt["status"],
    "postflight_status": postflight["status"], "terminal_identities": identities,
    "review_script_sha256": sha(__file__),
    "approved_source_hashes": APPROVED,
    "public_declarations": len(public), "generated_helpers": len(helpers),
    "all_new_declarations": len(rows), "public_type_comparison": comparison,
    "public_theorems": sum(kind == "theorem" for kind in public.values()),
    "public_definitions": sum(kind == "definition" for kind in public.values()),
    "compile_targets": receipt["compile_targets"],
    "controls": len(receipt["controls"]),
    "commands": len(receipt["commands"]),
    "new_full_type_hashes_sha256": sha(OUT / "new_full_type_hashes.json"),
    "axiom_union": sorted({a for r in rows for a in r["axioms"]}),
    "helper_manual_review": "PENDING: reviewer must inspect generated helper types"}
write_json(OUT / "binding.json", summary)
print(json.dumps(summary, indent=2))
