#!/usr/bin/env python3
"""Independent terminal integrity check. Does not execute Lean or import verifier code.

Requires an independently reviewed helper-hash manifest. Validates exact command
arguments, results and logs plus complete source, object and audit inventories.
It cannot authenticate the Lean compiler or external caches, nor detect a
transient input modification restored before both endpoint checks.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
BAD = ("unknown module", "unknown identifier", "unknown constant", "object file", "failed to load",
       "no such file", "not found", "cannot execute", "segmentation fault", "stack overflow",
       "maximum recursion depth", "maximum number of heartbeats", "out of memory", "failed to synthesize")

def digest(p):
    with p.open("rb") as f: return hashlib.file_digest(f, "sha256").hexdigest()
def tree(root):
    require(root.is_dir(), f"Missing directory: {root}")
    paths = sorted(root.rglob("*"))
    require(not any(p.is_symlink() for p in paths), "Evidence tree contains symlinks")
    return {p.relative_to(root).as_posix():digest(p) for p in paths if p.is_file() and "__pycache__" not in p.parts}
def require(condition, message):
    if not condition: raise ValueError(message)
def safe(root, rel):
    path = (root / rel).resolve()
    require(not Path(rel).is_absolute() and path.is_relative_to(root.resolve()), "Unsafe relative evidence path")
    return path

def runtime_tree(runtime, scopes):
    files, links, resolved = {}, {}, {}
    for scope in scopes:
        directory = runtime / scope
        require(directory.is_dir() and not directory.is_symlink(), "Missing/symlinked runtime scope")
        for p in sorted(directory.rglob("*")):
            rel = p.relative_to(runtime).as_posix()
            if p.is_symlink():
                require(p.is_file(), "Broken/directory runtime symlink")
                links[rel] = os.readlink(p)
            if p.is_file():
                target = str(p.resolve())
                if target not in resolved: resolved[target] = digest(p)
                files[rel] = resolved[target]
    return {"scopes":scopes,"file_sha256":files,"symlink_targets":links}

def validate(run, assembly, reviewpath):
    recpath = run / "receipt.json"; rechash = digest(recpath); rec = json.loads(recpath.read_text())
    invpath = assembly / "inventory.json"; invhash = digest(invpath); inv = json.loads(invpath.read_text())
    reviewhash = digest(reviewpath); review = json.loads(reviewpath.read_text())
    require(review.get("status") == "PASS", "Helper review is not accepted")
    reviewed = review["files"]
    require(digest(Path(__file__)) == review["postflight_sha256"], "Postflight differs from independently reviewed revision")
    require(tree(HOME / "scripts") == reviewed == rec.get("verifier_input_sha256") == inv.get("helpers_sha256"),
            "Helpers differ from independently reviewed revisions")
    require(rec.get("schema") == "komorebi-space-budget-clean-replay-v1" and rec.get("status") == "PASS", "Wrong or nonterminal receipt")
    require(rec.get("lean_executed") is True and rec.get("clean_project_build") is True, "No executed clean replay")
    for k in ("source_unchanged_during_run", "helpers_unchanged_during_run", "objects_unchanged_after_compile", "runtime_unchanged_during_run"):
        require(rec.get(k) is True, f"Missing preservation gate: {k}")
    require(rec.get("finished_utc") and rec.get("initial_project_objects") == {}, "Missing terminal or initial object evidence")
    require(rec.get("assembly_path") == str(assembly) and invhash == rec.get("inventory_sha256"), "Assembly identity differs")
    require(inv.get("schema") == "komorebi-space-budget-assembly-v1", "Wrong assembly schema")
    source, build = run / "source", run / "build"
    src = tree(source); objects = tree(build)
    require(digest(source/"ExportAudit.lean") == reviewed["ExportAudit.lean"], "Snapshot exporter differs from reviewed helper")
    require(src == tree(assembly / "source") == inv["project_file_sha256"] == rec["source_snapshot_sha256"], "Full source/control snapshot changed")
    for k in ("compile_order", "source_sha256", "compile_targets", "production_modules", "entrypoints", "new_modules", "controls"):
        require(rec[k] == inv[k], f"Wrong graph/control field: {k}")
    require(rec["compile_targets"] == len(rec["compile_order"]) == len(set(rec["compile_order"])), "Wrong target count")
    require(rec["production_modules"] + len(rec["entrypoints"]) == rec["compile_targets"], "Inconsistent production/entrypoint counts")
    actual_production = {p.relative_to(source).as_posix():digest(p) for p in (source / "KomorebiSpace").rglob("*.lean")}
    actual_production.update({p.relative_to(source).as_posix():digest(p) for p in source.glob("KomorebiSpace*.lean")})
    require(actual_production == rec["source_sha256"], "Actual production inventory differs")
    require(set(actual_production) == {m.replace(".", "/")+".lean" for m in rec["compile_order"]}, "Compile order does not cover production source")
    require((source / "wanted_modules.txt").read_text().splitlines() == rec["compile_order"], "Audit list does not cover full graph")
    require((source / "new_modules.txt").read_text().splitlines() == rec["new_modules"], "New type/module list differs")
    require(set(rec["new_modules"]) <= set((source / "type_modules.txt").read_text().splitlines()), "Type export selection omits new module")
    require(json.loads((source / "control_manifest.json").read_text())["controls"] == rec["controls"], "Control manifest differs")
    actual_controls = {p.relative_to(source).as_posix() for p in (source / "tests").rglob("*.lean")}
    require(actual_controls == {c["path"] for c in rec["controls"]}, "Control inventory omits/adds file")
    require(objects == rec["postcompile_object_sha256"] == rec["object_sha256"], "Objects changed after compile/audit")
    require(set(objects) == {m.replace(".", "/")+".olean" for m in rec["compile_order"]}, "Object inventory is incomplete/extra")
    require(rec["compile_policy"] == {"threads":1,"warningAsError":True,"autoImplicit":False}, "Wrong compiler policy")
    runtime = Path(rec["runtime"]); lean = runtime / "toolchain/bin/lean"
    require(digest(lean) == rec["lean_binary_sha256"], "Compiler binary changed")
    flags = [str(lean), "-j1", "-DwarningAsError=true", "-DautoImplicit=false"]
    pins = json.loads((source / "pinned-dependencies.json").read_text())["packages"]
    expected = [("lean_version", [str(lean), "--version"], False, [])]
    deps = []
    caches = []
    for pin in pins:
        pkg = runtime / "workspace/.lake/packages" / pin["name"]
        expected.extend([("pin_"+pin["name"], ["git", "-C", str(pkg), "rev-parse", "HEAD"], False, []),
                         ("clean_"+pin["name"], ["git", "-C", str(pkg), "diff", "--exit-code", "HEAD", "--"], False, [])])
        deps.append({"name":pin["name"],"expected":pin["rev"],"actual":pin["rev"]})
        cache = pkg / ".lake/build/lib/lean"
        require(rec["dependency_cache_directories"][pin["name"]] == {"path":str(cache),"exists":cache.is_dir()}, "External cache path changed")
        if cache.is_dir(): caches.append(str(cache))
    require(rec["dependencies"] == deps, "Wrong pin receipts")
    require(rec["environment"]["LEAN_PATH"] == ":".join([str(build)] + caches), "Lean search path includes unexpected objects")
    adapter = rec.get("executable_path_adapter")
    if adapter:
        require(digest(Path(adapter["path"])) == adapter["sha256"], "Path adapter changed")
        require(rec["environment"].get("LD_PRELOAD") == adapter["path"], "Unexpected preloaded library")
    else: require("LD_PRELOAD" not in rec["environment"], "Undeclared preloaded library")
    for m in rec["compile_order"]:
        rel = m.replace(".", "/")
        expected.append(("compile_"+m, flags+["-o",str(build/(rel+".olean")),str(source/(rel+".lean"))], False, []))
    expected.append(("axiom_export", flags+[str(source/"ExportAudit.lean")], False, []))
    for c in rec["controls"]:
        label = "control_"+c["path"].removeprefix("tests/").removesuffix(".lean").replace("/","_")
        expected.append((label,flags+[str(safe(source,c["path"]))],c["kind"] != "positive",c["required_markers"]))
    for pin in pins:
        pkg = runtime / "workspace/.lake/packages" / pin["name"]
        expected.extend([("terminal_pin_"+pin["name"], ["git", "-C", str(pkg), "rev-parse", "HEAD"], False, []),
                         ("terminal_clean_"+pin["name"], ["git", "-C", str(pkg), "diff", "--exit-code", "HEAD", "--"], False, [])])
    labels = [e[0] for e in expected]
    commands = rec["commands"]
    require(labels == [c["label"] for c in commands] == rec["exact_command_labels"] and len(set(labels)) == len(labels), "Command inventory missing/extra/reordered/duplicate")
    require({p.name for p in (run/"logs").iterdir()} == {x+".log" for x in labels}, "Unexpected/missing command log")
    loghashes = {}
    for cmd,(label,argv,negative,markers) in zip(commands,expected,strict=True):
        require(cmd["argv"] == argv and cmd["cwd"] == str(source), f"Wrong target/flags/cwd: {label}")
        require(cmd["passed"] is True and cmd["timeout"] is False, f"Failed/timed out command: {label}")
        require(cmd["expected_rejection"] is negative and cmd["required_markers"] == markers, f"Wrong expectation: {label}")
        require(cmd["log"] == f"logs/{label}.log", "Wrong log path")
        log = safe(run,cmd["log"]); require(not (run/cmd["log"]).is_symlink(), "Log symlink introduced"); loghashes[cmd["log"]] = digest(log)
        require(loghashes[cmd["log"]] == cmd["log_sha256"], f"Log changed: {label}")
        out = log.read_text(errors="replace")
        if negative:
            require(cmd["exit_code"] == 1 and "error:" in out.lower() and all(s in out for s in markers)
                    and not any(s in out.lower() for s in BAD), f"Unaccepted rejection reason: {label}")
        else: require(cmd["exit_code"] == 0, f"Nonzero positive command: {label}")
        if label.startswith("pin_") or label.startswith("terminal_pin_"):
            pin = next(p for p in pins if label in ("pin_"+p["name"], "terminal_pin_"+p["name"]))
            require(out.strip() == pin["rev"], "Wrong pin log")
    version = (run / "logs/lean_version.log").read_text().strip()
    require(version == rec["lean_version"] and "4.34.0-rc2" in version and "6a10ac8c22beadecabdbb0919c2b50214762f91d" in version, "Wrong compiler version")
    auditpath = run / "axioms.json"; audit = json.loads(auditpath.read_text()); rows = audit["declarations"]
    require(digest(auditpath) == rec["axiom_report_sha256"], "Axiom report changed")
    require(rows and not audit["unexpected"] and len(rows) == audit["count"] == rec["axiom_declarations"], "Wrong axiom count/failure")
    require(len({r["name"] for r in rows}) == len(rows), "Duplicate audited names")
    audited = {r["module"] for r in rows}
    require(set(rec["compile_order"])-set(rec["entrypoints"]) <= audited <= set(rec["compile_order"]), "Axiom scope incomplete/extra")
    require(all(not r["unsafe"] and set(r["axioms"]) <= AXIOMS for r in rows), "Unapproved axiom or unsafe declaration")
    require(rec["axiom_union"] == sorted({ax for r in rows for ax in r["axioms"]}), "Axiom union differs")
    newrows = sorted([r for r in rows if r["module"] in rec["new_modules"]],key=lambda r:r["name"])
    require(len(newrows) == rec["new_axiom_declarations"] and all(r["type"] and "⋯" not in r["type"] for r in newrows), "Missing/truncated new declaration type")
    require(json.loads((run/"new_declarations.json").read_text()) == newrows, "New declaration catalogue differs")
    require(json.loads((run/"declarations_sorted.json").read_text()) == sorted(rows,key=lambda r:(r["module"],r["name"])), "Sorted catalogue differs")
    catalogue_hashes = {name:digest(run/name) for name in ("new_declarations.json","declarations_sorted.json")}
    runtimepath = run / "runtime_snapshot.json"
    require(digest(runtimepath) == rec["runtime_snapshot_sha256"], "Runtime snapshot record changed")
    runtime_scopes = ["toolchain/bin", "toolchain/lib"] + [Path(p).relative_to(runtime).as_posix() for p in caches]
    require(runtime_scopes == rec["runtime_scopes"], "Wrong runtime/cache hash scope")
    runtime_record = json.loads(runtimepath.read_text())
    require(len(runtime_record["file_sha256"]) == rec["runtime_file_count"], "Runtime hash count differs")
    require(runtime_tree(runtime,runtime_scopes) == runtime_record, "Trusted runtime/cache bytes changed after replay")
    require(all(digest(safe(run,p)) == h for p,h in loghashes.items()), "Command log changed during postflight")
    require(digest(auditpath) == rec["axiom_report_sha256"], "Axiom report changed during postflight")
    require(all(digest(run/p) == h for p,h in catalogue_hashes.items()), "Declaration catalogue changed during postflight")
    require(digest(runtimepath) == rec["runtime_snapshot_sha256"], "Runtime snapshot record changed during postflight")
    require(not adapter or digest(Path(adapter["path"])) == adapter["sha256"], "Adapter changed during postflight")
    require(digest(lean) == rec["lean_binary_sha256"], "Compiler changed during postflight")
    require(tree(assembly/"source") == src, "Assembly changed during postflight")
    require(digest(Path(__file__)) == review["postflight_sha256"], "Postflight changed during validation")
    require(digest(recpath)==rechash and digest(invpath)==invhash and digest(reviewpath)==reviewhash
            and tree(source)==src and tree(build)==objects and tree(HOME/"scripts")==reviewed, "Inputs changed during postflight")
    return {"run_receipt_sha256":rechash,"inventory_sha256":invhash,"review_manifest_sha256":reviewhash,
            "reviewed_verifier_sha256":reviewed,"runtime_snapshot_sha256":digest(runtimepath),"runtime_file_count":rec["runtime_file_count"],"source_snapshot_sha256":src,"object_sha256":objects,
            "exact_command_labels":labels,"command_count":len(labels),"command_log_sha256":loghashes,
            "axiom_report_sha256":digest(auditpath),"axiom_declarations":len(rows),"new_axiom_declarations":len(newrows),
            "gates":{"complete_command_inventory":True,"complete_source_and_control_snapshot":True,
                     "final_object_inventory":True,"all_project_axioms_audited":True,"all_new_types_exported":True,"runtime_endpoint_identity":True}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",type=Path,required=True);p.add_argument("--assembly",type=Path,required=True)
    p.add_argument("--reviewed-helpers",type=Path,required=True)
    a=p.parse_args();run=a.run.resolve();out=run/"postflight.json"
    if out.exists():p.error("Refusing to overwrite postflight attempt")
    rec={"schema":"komorebi-space-budget-postflight-v1","status":"RUNNING","validator_sha256":digest(Path(__file__)),
         "started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"lean_executed":False,
         "scope":"Independent terminal integrity validation over independently reviewed helper revisions",
         "limitation":"Endpoint hashes cannot detect transient changes restored before recheck; compiler and external caches remain trusted."}
    try:rec.update(validate(run,a.assembly.resolve(),a.reviewed_helpers.resolve()));rec["status"]="PASS"
    except Exception as e:rec.update(status="FAIL",failure=f"{type(e).__name__}: {e}")
    rec["finished_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with out.open("x") as f:json.dump(rec,f,indent=2,sort_keys=True);f.write("\n")
    print(json.dumps({"status":rec["status"],"receipt":str(out),"failure":rec.get("failure")},indent=2))
    return 0 if rec["status"]=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
