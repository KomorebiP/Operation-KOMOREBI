"""Freeze reviewer-checked production/control identities; no Lean execution."""
from pathlib import Path
import ast
import collections
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
PHASE = ROOT/"wr15_v1.12.0"
OUT = Path(__file__).resolve().parent
BASE = ROOT/"recovery/v1.11.0/Komorebi_Space_Lean_Continuation_v1.11.0/limits_v1.11.0/integration/runs/clean_limits_01"
NEW = ["KomorebiSpace.CoordinateBasisChange", "KomorebiSpace.CoordinateCovector"]

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()

def filemap(root):
    paths=sorted(root.rglob("*"))
    assert root.is_dir() and not any(p.is_symlink() for p in paths)
    return {p.relative_to(root).as_posix():digest(p) for p in paths if p.is_file() and "__pycache__" not in p.parts}

def read(path):
    return json.loads(path.read_text())

def main():
    report=OUT/"preflight_checks.json"
    assert not report.exists(), "Retain previous source/control review record"
    helper_review=read(PHASE/"reviews/reviewed_helpers.json")
    assert helper_review["status"] == "PASS"
    assert filemap(PHASE/"integration/scripts") == helper_review["files"]
    assert digest(PHASE/"integration/postflight/validate.py") == helper_review["postflight_sha256"]
    parent=read(BASE/"receipt.json")
    assert digest(BASE/"receipt.json") == "1fbbed1df05f74aa0c6b967cd3828b3985c7b3c4bb533027636719640978bdd0"
    assert digest(BASE/"postflight.json") == "37e7f09b13c7db2a9cb979f64402199d1a377a19f58ec698a605d7b78765bb9d"
    assert filemap(BASE/"source") == parent["source_snapshot_sha256"]
    files=sorted((BASE/"source/KomorebiSpace").rglob("*.lean"))+sorted((BASE/"source").glob("KomorebiSpace*.lean"))
    texts={".".join(p.relative_to(BASE/"source").with_suffix("").parts):p.read_text() for p in files}
    newfiles=sorted((PHASE/"formal/KomorebiSpace").rglob("*.lean"))
    newnames=[".".join(p.relative_to(PHASE/"formal").with_suffix("").parts) for p in newfiles]
    assert newnames == NEW
    for name,path in zip(newnames,newfiles,strict=True):
        assert name not in texts
        texts[name]=path.read_text()
    texts["KomorebiSpaceCombined"] += "".join(f"import {m}\n" for m in newnames)
    imports={m:[dep for line in body.splitlines() if line.strip().startswith("import ") for dep in line.strip().split()[1:] if dep.startswith("KomorebiSpace")] for m,body in texts.items()}
    active,done,order=set(),set(),[]
    def visit(module):
        assert module in texts and module not in active
        if module in done:return
        active.add(module)
        for dep in sorted(set(imports[module])):visit(dep)
        active.remove(module)
        done.add(module)
        order.append(module)
    visit("KomorebiSpaceCombined")
    assert done == set(texts) and len(texts)==156 and sum("." in m for m in texts)==153
    manifest=PHASE/"formal/tests/control_manifest.json"
    controls=read(manifest)["controls"]
    actual={p.relative_to(manifest.parent).as_posix() for p in manifest.parent.rglob("*.lean")}
    assert actual == {c["path"] for c in controls} and len(actual)==len(controls)
    assert {"positive","negative"} <= {c["kind"] for c in controls}
    for control in controls:
        path=Path(control["path"])
        assert len(path.parts)==2 and path.parts[0]==control["kind"] and ".." not in path.parts and not path.is_absolute()
        assert control["kind"] in ("positive","negative","policy")
        assert all(isinstance(marker,str) and marker for marker in control["required_markers"])
        assert control["kind"] == "positive" or control["required_markers"]
    cumulative=parent["controls"]+[dict(c,scope="wr15",path="tests/wr15/"+c["path"]) for c in controls]
    pins=read(BASE/"source/pinned-dependencies.json")["packages"]
    data={"schema":"komorebi-space-wr15-source-control-preflight-v1","status":"PASS","checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"lean_executed":False,"scope":"Frozen identities and independently reconstructed additive graph/control inventory after raw fixture review; final Lean outcomes remain pending.","helper_manifest_sha256":digest(PHASE/"reviews/reviewed_helpers.json"),"new_modules":newnames,"new_source_sha256":{p.name:digest(p) for p in newfiles},"new_control_source_sha256":filemap(manifest.parent),"compile_order":order,"compile_targets":156,"production_modules":153,"parent_source_files":len(parent["source_snapshot_sha256"]),"parent_declarations":4982,"new_control_counts":dict(collections.Counter(c["kind"] for c in controls)),"cumulative_control_counts":dict(collections.Counter(c["kind"] for c in cumulative)),"expected_commands":2+4*len(pins)+len(texts)+len(cumulative),"control_manifest":controls}
    report.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps(data,indent=2,sort_keys=True))

if __name__=="__main__":main()
