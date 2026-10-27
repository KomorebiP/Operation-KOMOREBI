"""Reviewer-owned terminal evidence reconstruction; does not execute Lean."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE = ROOT / "limits_v1.11.0"
OUT = Path(__file__).resolve().parent
BASE = ROOT / "budget_v1.10.0/integration/runs/clean_budget_01"
ALLOWED = {"Classical.choice", "Quot.sound", "propext"}
BAD = ("unknown module", "unknown identifier", "unknown constant", "object file", "failed to load",
       "no such file", "not found", "cannot execute", "segmentation fault", "stack overflow",
       "maximum recursion depth", "maximum number of heartbeats", "out of memory", "failed to synthesize")


def digest(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(p):
    return json.loads(p.read_text())


def filemap(root):
    paths = sorted(root.rglob("*"))
    assert not any(p.is_symlink() for p in paths), root
    return {p.relative_to(root).as_posix():digest(p) for p in paths
            if p.is_file() and "__pycache__" not in p.parts}


def identities(rows):
    keys = ("name", "module", "kind", "unsafe", "axioms")
    return sorted([{k:sorted(r[k]) if k == "axioms" else r[k] for k in keys} for r in rows], key=lambda r:r["name"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    recpath, postpath = run/"receipt.json", run/"postflight.json"
    start_record_hashes = {p.name:digest(p) for p in (recpath,postpath)}
    rec,post = read(recpath),read(postpath)
    assert rec["status"] == post["status"] == "PASS"
    assert "failure" not in rec and "failure" not in post
    assert rec["lean_executed"] and rec["clean_project_build"] and rec["initial_project_objects"] == {}
    assert all(rec[k] is True for k in ("source_unchanged_during_run","helpers_unchanged_during_run","objects_unchanged_after_compile","runtime_unchanged_during_run","inherited_declarations_preserved"))
    assert post["run_receipt_sha256"] == start_record_hashes["receipt.json"]
    reviewpath = PHASE/"reviews/reviewed_helpers.json"
    assert post["review_manifest_sha256"] == digest(reviewpath)
    review = read(reviewpath)
    assert review["status"] == "PASS"
    assert filemap(PHASE/"integration/scripts") == review["files"] == rec["verifier_input_sha256"] == post["reviewed_verifier_sha256"]
    assert digest(PHASE/"integration/postflight/validate.py") == review["postflight_sha256"] == post["validator_sha256"]
    assembly = Path(rec["assembly_path"])
    invpath = assembly/"inventory.json"
    inv = read(invpath)
    assert digest(invpath) == rec["inventory_sha256"] == post["inventory_sha256"]
    source,build = run/"source",run/"build"
    sources = filemap(source)
    assert sources == filemap(assembly/"source") == inv["project_file_sha256"] == rec["source_snapshot_sha256"] == post["source_snapshot_sha256"]
    objects = filemap(build)
    assert objects == rec["object_sha256"] == rec["postcompile_object_sha256"] == post["object_sha256"]
    inherited = read(BASE/"receipt.json")
    assert digest(BASE/"receipt.json") == "42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376"
    assert digest(BASE/"postflight.json") == "b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2"
    assert digest(BASE/"axioms.json") == "5bd29f14954a05a1d59135dbec241f180da8c98532715cd9d94b0570e3942cfd"
    parentsource = filemap(BASE/"source")
    assert parentsource == inherited["source_snapshot_sha256"] == inv["parent_source_snapshot_sha256"]
    allowed = {"KomorebiSpaceCombined.lean","ExportAudit.lean","control_manifest.json","new_modules.txt","type_modules.txt","wanted_modules.txt"}
    assert all(sources.get(k) == v for k,v in parentsource.items() if k not in allowed)
    assert (source/"KomorebiSpaceCombined.lean").read_text() == (BASE/"source/KomorebiSpaceCombined.lean").read_text()+"".join(f"import {m}\n" for m in rec["new_modules"])
    assert digest(source/"ExportAudit.lean") == review["files"]["ExportAudit.lean"]
    assert {p.name:digest(p) for p in (PHASE/"formal/KomorebiSpace").glob("*.lean")} == review["reviewed_new_source_sha256"]
    assert filemap(PHASE/"formal/tests") == review["reviewed_new_control_source_sha256"]
    for name,h in review["reviewed_new_source_sha256"].items():
        assert digest(source/"KomorebiSpace"/name) == h
    for name,h in review["reviewed_new_control_source_sha256"].items():
        if name != "control_manifest.json":
            assert digest(source/"tests/limits"/name) == h
    files = sorted((source/"KomorebiSpace").rglob("*.lean")) + sorted(source.glob("KomorebiSpace*.lean"))
    modules = {".".join(p.relative_to(source).with_suffix("").parts):p for p in files}
    assert set(modules) == set(rec["compile_order"])
    assert len(modules) == 154 and sum("." in m for m in modules) == 151
    assert {p.relative_to(source).as_posix():digest(p) for p in files} == rec["source_sha256"]
    pos = {m:i for i,m in enumerate(rec["compile_order"])}
    imports = {m:[d for line in p.read_text().splitlines() if line.strip().startswith("import ")
                  for d in line.strip().split()[1:] if d.startswith("KomorebiSpace")] for m,p in modules.items()}
    assert all(d in modules and pos[d] < pos[m] for m,deps in imports.items() for d in deps)
    reachable=set()
    def visit(m):
        if m in reachable:return
        reachable.add(m)
        for d in imports[m]:visit(d)
    visit("KomorebiSpaceCombined")
    assert reachable == set(modules)
    assert set(objects) == {m.replace(".","/")+".olean" for m in modules}
    assert (source/"wanted_modules.txt").read_text().splitlines() == rec["compile_order"]
    assert (source/"new_modules.txt").read_text().splitlines() == rec["new_modules"]
    controls = read(source/"control_manifest.json")["controls"]
    assert controls == rec["controls"] == inv["controls"]
    assert [c for c in controls if c["scope"]!="limits"] == inherited["controls"]
    assert {p.relative_to(source).as_posix() for p in (source/"tests").rglob("*.lean")} == {c["path"] for c in controls}
    pins = read(source/"pinned-dependencies.json")["packages"]
    runtime = Path(rec["runtime"])
    lean = runtime/"toolchain/bin/lean"
    flags = [str(lean),"-j1","-DwarningAsError=true","-DautoImplicit=false"]
    expected=[("lean_version",[str(lean),"--version"],None)]
    for pin in pins:
        pkg=runtime/"workspace/.lake/packages"/pin["name"]
        expected.extend([("pin_"+pin["name"],["git","-C",str(pkg),"rev-parse","HEAD"],None),
                         ("clean_"+pin["name"],["git","-C",str(pkg),"diff","--exit-code","HEAD","--"],None)])
    for m in rec["compile_order"]:
        rel=m.replace(".","/")
        expected.append(("compile_"+m,flags+["-o",str(build/(rel+".olean")),str(source/(rel+".lean"))],None))
    expected.append(("axiom_export",flags+[str(source/"ExportAudit.lean")],None))
    for c in controls:
        label="control_"+c["path"].removeprefix("tests/").removesuffix(".lean").replace("/","_")
        expected.append((label,flags+[str(source/c["path"])],c))
    for pin in pins:
        pkg=runtime/"workspace/.lake/packages"/pin["name"]
        expected.extend([("terminal_pin_"+pin["name"],["git","-C",str(pkg),"rev-parse","HEAD"],None),
                         ("terminal_clean_"+pin["name"],["git","-C",str(pkg),"diff","--exit-code","HEAD","--"],None)])
    labels = [x[0] for x in expected]
    assert len(labels) == len(set(labels)) == 231
    assert labels == [c["label"] for c in rec["commands"]] == rec["exact_command_labels"] == post["exact_command_labels"]
    assert {p.name for p in (run/"logs").iterdir()} == {x+".log" for x in labels}
    control_results=[]
    for command,(label,argv,control) in zip(rec["commands"],expected,strict=True):
        assert command["argv"] == argv and command["cwd"] == str(source)
        assert command["passed"] is True and command["timeout"] is False
        log=run/command["log"]; out=log.read_text()
        assert digest(log) == command["log_sha256"] == post["command_log_sha256"][command["log"]]
        negative=bool(control and control["kind"]!="positive")
        assert command["expected_rejection"] == negative
        assert command["exit_code"] == (1 if negative else 0)
        markers=[] if control is None else control["required_markers"]
        assert command["required_markers"] == markers
        if negative:
            assert "error:" in out.lower() and all(m in out for m in markers)
            assert not any(b in out.lower() for b in BAD)
        if control:
            control_results.append({"path":control["path"],"kind":control["kind"],"exit_code":command["exit_code"],"required_markers":markers,"source_sha256":digest(source/control["path"]),"log_sha256":digest(log),"diagnostic":out})
    auditpath=run/"axioms.json";audit=read(auditpath);rows=audit["declarations"]
    assert digest(auditpath)==rec["axiom_report_sha256"]==post["axiom_report_sha256"]
    assert len(rows)==len({r["name"] for r in rows})==audit["count"]==rec["axiom_declarations"]
    assert not audit["unexpected"] and all(not r["unsafe"] and set(r["axioms"])<=ALLOWED for r in rows)
    old=read(BASE/"axioms.json")["declarations"]
    old_now=[r for r in rows if r["module"] not in rec["new_modules"]]
    new=sorted([r for r in rows if r["module"] in rec["new_modules"]],key=lambda r:r["name"])
    assert identities(old_now)==identities(old) and len(old_now)==4935
    assert len(new)==rec["new_axiom_declarations"]==post["new_axiom_declarations"]
    assert all(r["type_mode"]=="full" and r["type"] and "⋯" not in r["type"] for r in new)
    assert new==read(run/"new_declarations.json")
    assert sorted(rows,key=lambda r:(r["module"],r["name"]))==read(run/"declarations_sorted.json")
    runtimepath=run/"runtime_snapshot.json"; runtimerec=read(runtimepath)
    assert digest(runtimepath)==rec["runtime_snapshot_sha256"]==post["runtime_snapshot_sha256"]
    assert len(runtimerec["file_sha256"])==rec["runtime_file_count"]==post["runtime_file_count"]
    assert post["gates"] and all(post["gates"].values())
    assert {p.name:digest(p) for p in (recpath,postpath)}==start_record_hashes
    summary={"status":"PASS","reviewer":"/root/limits_replay_audit","checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"lean_executed_by_this_check":False,"run":str(run),"assembly":str(assembly),"record_sha256":start_record_hashes,"inventory_sha256":digest(invpath),"helper_manifest_sha256":digest(reviewpath),"axiom_report_sha256":digest(auditpath),"runtime_snapshot_sha256":digest(runtimepath),"compile_targets":len(modules),"production_modules":151,"source_files":len(sources),"objects":len(objects),"command_count":len(labels),"declarations":len(rows),"inherited_declarations":len(old_now),"new_declarations":len(new),"new_module_counts":dict(collections.Counter(r["module"] for r in new)),"new_declaration_kinds":dict(collections.Counter(r["kind"] for r in new)),"new_type_characters":sum(len(r["type"]) for r in new),"axiom_union":sorted({a for r in rows for a in r["axioms"]}),"control_counts":dict(collections.Counter(c["kind"] for c in controls)),"runtime_file_count":len(runtimerec["file_sha256"]),"runtime_check_scope":"Independently verified snapshot bindings and successful reviewed terminal postflight; this reviewer check does not repeat its complete runtime byte scan.","control_results":control_results}
    (OUT/"terminal_checks.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k!="control_results"},indent=2,sort_keys=True))
    for c in control_results:
        if c["kind"]!="positive":print("\n"+c["path"]+"\n"+c["diagnostic"])


if __name__=="__main__":main()
