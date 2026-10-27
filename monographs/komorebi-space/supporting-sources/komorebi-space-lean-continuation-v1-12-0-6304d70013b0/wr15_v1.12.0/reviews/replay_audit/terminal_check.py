"""Reviewer-owned terminal evidence reconstruction; does not execute Lean."""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE = ROOT / "wr15_v1.12.0"
OUT = Path(__file__).resolve().parent
BASE = ROOT / "recovery/v1.11.0/Komorebi_Space_Lean_Continuation_v1.11.0/limits_v1.11.0/integration/runs/clean_limits_01"
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
    assert rec["schema"] == "komorebi-space-wr15-clean-replay-v1"
    assert post["schema"] == "komorebi-space-wr15-postflight-v1"
    assert rec["label"] == run.name and rec["attempt_number"] == int(run.name.rsplit("_",1)[1])
    assert rec["status"] == post["status"] == "PASS"
    assert "failure" not in rec and "failure" not in post
    assert rec["lean_executed"] and rec["clean_project_build"] and rec["initial_project_objects"] == {}
    assert all(rec[k] is True for k in ("source_unchanged_during_run","helpers_unchanged_during_run","objects_unchanged_after_compile","runtime_unchanged_during_run","inherited_declarations_preserved"))
    assert post["run_receipt_sha256"] == start_record_hashes["receipt.json"]
    reviewpath = PHASE/"reviews/reviewed_helpers.json"
    assert post["review_manifest_sha256"] == digest(reviewpath)
    review = read(reviewpath)
    assert rec["reviewed_helpers_path"] == str(reviewpath)
    preflight_path = OUT/"preflight_checks.json"
    preflight = read(preflight_path)
    assert preflight["status"] == "PASS"
    assert preflight["helper_manifest_sha256"] == digest(reviewpath)
    assert rec["reviewed_helpers_sha256"] == digest(reviewpath)
    assert datetime.datetime.fromisoformat(review["reviewed_utc"]) <= datetime.datetime.fromisoformat(rec["started_utc"])
    assert review["status"] == "PASS"
    assert filemap(PHASE/"integration/scripts") == review["files"] == rec["verifier_input_sha256"] == post["reviewed_verifier_sha256"]
    assert digest(PHASE/"integration/postflight/validate.py") == review["postflight_sha256"] == post["validator_sha256"]
    assert rec["postflight_sha256"] == review["postflight_sha256"]
    assembly = Path(rec["assembly_path"])
    invpath = assembly/"inventory.json"
    inv = read(invpath)
    assert inv["schema"] == "komorebi-space-wr15-assembly-v1"
    assert inv["helpers_sha256"] == review["files"]
    assert inv["parent_receipt_path"] == str(BASE/"receipt.json")
    assert inv["parent_recovered_run_path"] == str(BASE)
    assert rec["compile_policy"] == {"threads":1,"warningAsError":True,"autoImplicit":False}
    for field in ["compile_order","source_sha256","compile_targets","production_modules","entrypoints","new_modules","controls"]:
        assert rec[field] == inv[field]
    assert digest(invpath) == rec["inventory_sha256"] == post["inventory_sha256"]
    source,build = run/"source",run/"build"
    sources = filemap(source)
    assert sources == filemap(assembly/"source") == inv["project_file_sha256"] == rec["source_snapshot_sha256"] == post["source_snapshot_sha256"]
    objects = filemap(build)
    assert objects == rec["object_sha256"] == rec["postcompile_object_sha256"] == post["object_sha256"]
    inherited = read(BASE/"receipt.json")
    assert inv["parent_historical_assembly_path"] == inherited["assembly_path"]
    assert inv["parent_historical_runtime_path"] == inherited["runtime"]
    assert digest(BASE/"receipt.json") == "1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0"
    assert digest(BASE/"postflight.json") == "37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d"
    assert digest(BASE/"axioms.json") == "b6806e522fa0a562e91adfa3fcc3347401de7ffd7d21d7e0e5a90888d955b1f8"
    parent_catalogue = read(source/"parent_declarations.json")
    for field,filename in [("parent_receipt_sha256","receipt.json"),("parent_postflight_sha256","postflight.json"),("parent_axiom_report_sha256","axioms.json")]:
        assert rec[field] == inv[field] == parent_catalogue[field] == digest(BASE/filename)
    assert rec["parent_declarations"] == inv["parent_declarations"] == 4982
    parentsource = filemap(BASE/"source")
    assert parentsource == inherited["source_snapshot_sha256"] == inv["parent_source_snapshot_sha256"]
    allowed = {"KomorebiSpaceCombined.lean","ExportAudit.lean","control_manifest.json","new_modules.txt","type_modules.txt","wanted_modules.txt","parent_declarations.json"}
    assert all(sources.get(k) == v for k,v in parentsource.items() if k not in allowed)
    assert (source/"KomorebiSpaceCombined.lean").read_text() == (BASE/"source/KomorebiSpaceCombined.lean").read_text()+"".join(f"import {m}\n" for m in rec["new_modules"])
    assert digest(source/"ExportAudit.lean") == review["files"]["ExportAudit.lean"]
    assert {p.name:digest(p) for p in (PHASE/"formal/KomorebiSpace").glob("*.lean")} == preflight["new_source_sha256"]
    assert filemap(PHASE/"formal/tests") == preflight["new_control_source_sha256"]
    for name,h in preflight["new_source_sha256"].items():
        assert digest(source/"KomorebiSpace"/name) == h
    for name,h in preflight["new_control_source_sha256"].items():
        if name != "control_manifest.json":
            assert digest(source/"tests/wr15"/name) == h
    files = sorted((source/"KomorebiSpace").rglob("*.lean")) + sorted(source.glob("KomorebiSpace*.lean"))
    modules = {".".join(p.relative_to(source).with_suffix("").parts):p for p in files}
    assert set(modules) == set(rec["compile_order"])
    assert len(modules) == 156 and sum("." in m for m in modules) == 153
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
    assert [c for c in controls if c["scope"]!="wr15"] == inherited["controls"]
    newcontrols = [{"path":"tests/wr15/"+c["path"],"kind":c["kind"],"scope":"wr15","required_markers":c["required_markers"]}
                   for c in preflight["control_manifest"]]
    assert [c for c in controls if c["scope"]=="wr15"] == sorted(newcontrols,key=lambda c:c["path"])
    assert rec["compile_order"] == preflight["compile_order"]
    assert {p.relative_to(source).as_posix() for p in (source/"tests").rglob("*.lean")} == {c["path"] for c in controls}
    pins = read(source/"pinned-dependencies.json")["packages"]
    assert rec["dependencies"] == [{"name":p["name"],"expected":p["rev"],"actual":p["rev"]} for p in pins]
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
    assert len(labels) == len(set(labels)) == preflight["expected_commands"]
    assert post["command_count"] == len(labels)
    assert labels == [c["label"] for c in rec["commands"]] == rec["exact_command_labels"] == post["exact_command_labels"]
    assert {p.name for p in (run/"logs").iterdir()} == {x+".log" for x in labels}
    assert not (run/"logs").is_symlink()
    assert not any(p.is_symlink() for p in (run/"logs").iterdir())
    control_results=[]
    for command,(label,argv,control) in zip(rec["commands"],expected,strict=True):
        assert command["argv"] == argv and command["cwd"] == str(source)
        assert command["passed"] is True and command["timeout"] is False
        assert command["log"] == f"logs/{label}.log"
        log=run/command["log"]; out=log.read_text(errors="replace")
        assert digest(log) == command["log_sha256"] == post["command_log_sha256"][command["log"]]
        negative=bool(control and control["kind"]!="positive")
        assert command["expected_rejection"] == negative
        assert command["exit_code"] == (1 if negative else 0)
        markers=[] if control is None else control["required_markers"]
        assert command["required_markers"] == markers
        if negative:
            assert "error:" in out.lower() and all(m in out for m in markers)
            assert not any(b in out.lower() for b in BAD)
        if label == "lean_version":
            assert out.strip() == rec["lean_version"]
            assert "4.34.0-rc2" in out and "6a10ac8c22beadecabdbb0919c2b50214762f91d" in out
        if label.startswith("pin_") or label.startswith("terminal_pin_"):
            pin = next(p for p in pins if label in ("pin_"+p["name"],"terminal_pin_"+p["name"]))
            assert out.strip() == pin["rev"]
        if control:
            control_results.append({"path":control["path"],"kind":control["kind"],"exit_code":command["exit_code"],"required_markers":markers,"source_sha256":digest(source/control["path"]),"log_sha256":digest(log),"diagnostic":out})
    auditpath=run/"axioms.json";audit=read(auditpath);rows=audit["declarations"]
    assert digest(auditpath)==rec["axiom_report_sha256"]==post["axiom_report_sha256"]
    assert len(rows)==len({r["name"] for r in rows})==audit["count"]==rec["axiom_declarations"]==post["axiom_declarations"]
    assert not audit["unexpected"] and all(not r["unsafe"] and set(r["axioms"])<=ALLOWED for r in rows)
    assert rec["axiom_union"] == sorted({a for r in rows for a in r["axioms"]})
    old=read(BASE/"axioms.json")["declarations"]
    old_now=[r for r in rows if r["module"] not in rec["new_modules"]]
    new=sorted([r for r in rows if r["module"] in rec["new_modules"]],key=lambda r:r["name"])
    assert identities(old_now)==identities(old) and len(old_now)==4982
    assert len(new)==rec["new_axiom_declarations"]==post["new_axiom_declarations"]
    assert set(rec["compile_order"])-set(rec["entrypoints"]) <= {r["module"] for r in rows} <= set(rec["compile_order"])
    assert rec["new_modules"] == ["KomorebiSpace.CoordinateBasisChange", "KomorebiSpace.CoordinateCovector"]
    assert identities(old)==read(source/"parent_declarations.json")["declarations"]
    assert all(r["type_mode"]=="full" and r["type"] and "⋯" not in r["type"] for r in new)
    assert new==read(run/"new_declarations.json")
    assert sorted(rows,key=lambda r:(r["module"],r["name"]))==read(run/"declarations_sorted.json")
    catalogue_hashes = {name:digest(run/name) for name in ["new_declarations.json","declarations_sorted.json"]}
    runtimepath=run/"runtime_snapshot.json"; runtimerec=read(runtimepath)
    assert digest(runtimepath)==rec["runtime_snapshot_sha256"]==post["runtime_snapshot_sha256"]
    assert len(runtimerec["file_sha256"])==rec["runtime_file_count"]==post["runtime_file_count"]
    caches=[]
    for pin in pins:
        cache=runtime/"workspace/.lake/packages"/pin["name"]/".lake/build/lib/lean"
        assert rec["dependency_cache_directories"][pin["name"]] == {"path":str(cache),"exists":cache.is_dir()}
        if cache.is_dir():caches.append(cache)
    assert rec["environment"]["LEAN_PATH"] == ":".join(map(str,[build]+caches))
    scopes=["toolchain/bin","toolchain/lib"]+[p.relative_to(runtime).as_posix() for p in caches]
    assert scopes == rec["runtime_scopes"] == runtimerec["scopes"]
    runtime_files, runtime_links, resolved = {}, {}, {}
    for scope in scopes:
        directory=runtime/scope
        assert directory.is_dir() and not directory.is_symlink()
        for path in sorted(directory.rglob("*")):
            rel=path.relative_to(runtime).as_posix()
            if path.is_symlink():
                assert path.is_file(), path
                runtime_links[rel]=os.readlink(path)
            if path.is_file():
                real=str(path.resolve())
                if real not in resolved:resolved[real]=digest(path)
                runtime_files[rel]=resolved[real]
    assert runtime_files == runtimerec["file_sha256"] and runtime_links == runtimerec["symlink_targets"]
    assert digest(lean) == rec["lean_binary_sha256"]
    adapter=rec.get("executable_path_adapter")
    if adapter:
        assert digest(Path(adapter["path"])) == adapter["sha256"]
        assert rec["environment"]["LD_PRELOAD"] == adapter["path"]
    else:assert "LD_PRELOAD" not in rec["environment"]
    assert post["gates"] == {name:True for name in ["complete_command_inventory","complete_source_and_control_snapshot","final_object_inventory","all_project_axioms_audited","all_new_types_exported","inherited_declarations_preserved","runtime_endpoint_identity"]}
    assert filemap(source) == sources and filemap(build) == objects and filemap(assembly/"source") == sources
    assert filemap(PHASE/"integration/scripts") == review["files"]
    assert digest(PHASE/"integration/postflight/validate.py") == review["postflight_sha256"]
    assert digest(reviewpath) == rec["reviewed_helpers_sha256"]
    assert filemap(BASE/"source") == parentsource
    assert digest(BASE/"receipt.json") == "1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0"
    assert digest(BASE/"postflight.json") == "37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d"
    assert digest(BASE/"axioms.json") == "b6806e522fa0a562e91adfa3fcc3347401de7ffd7d21d7e0e5a90888d955b1f8"
    assert all(digest(run/c["log"]) == c["log_sha256"] for c in rec["commands"])
    assert digest(auditpath)==rec["axiom_report_sha256"]
    assert new==read(run/"new_declarations.json")
    assert sorted(rows,key=lambda r:(r["module"],r["name"]))==read(run/"declarations_sorted.json")
    assert {name:digest(run/name) for name in catalogue_hashes} == catalogue_hashes
    assert digest(runtimepath)==rec["runtime_snapshot_sha256"]
    assert digest(invpath)==rec["inventory_sha256"]
    assert read(preflight_path)==preflight
    assert {p.name:digest(p) for p in (recpath,postpath)}==start_record_hashes
    summary={"status":"PASS","reviewer":"/root/wr15_replay_audit","checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"lean_executed_by_this_check":False,"run":str(run),"assembly":str(assembly),"record_sha256":start_record_hashes,"inventory_sha256":digest(invpath),"helper_manifest_sha256":digest(reviewpath),"axiom_report_sha256":digest(auditpath),"runtime_snapshot_sha256":digest(runtimepath),"compile_targets":len(modules),"production_modules":153,"source_files":len(sources),"objects":len(objects),"command_count":len(labels),"declarations":len(rows),"inherited_declarations":len(old_now),"new_declarations":len(new),"new_module_counts":dict(collections.Counter(r["module"] for r in new)),"new_declaration_kinds":dict(collections.Counter(r["kind"] for r in new)),"new_type_characters":sum(len(r["type"]) for r in new),"axiom_union":sorted({a for r in rows for a in r["axioms"]}),"control_counts":dict(collections.Counter(c["kind"] for c in controls)),"runtime_file_count":len(runtimerec["file_sha256"]),"runtime_check_scope":"Independently reconstructed complete current runtime/cache file and symlink map, in addition to bindings and reviewed postflight.","control_results":control_results}
    assert not (OUT/"terminal_checks.json").exists(), "Preserve previous terminal reviewer record"
    (OUT/"terminal_checks.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k!="control_results"},indent=2,sort_keys=True))
    for c in control_results:
        if c["kind"]!="positive":print("\n"+c["path"]+"\n"+c["diagnostic"])


if __name__=="__main__":main()
