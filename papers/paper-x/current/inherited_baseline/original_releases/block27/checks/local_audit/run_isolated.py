#!/usr/bin/env python3
"""Audit new Lean sources against archived predecessor objects only.

The project build directory is deliberately removed from LEAN_PATH. New proof
objects are temporary and are never copied into the released audit directory.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess, time, zipfile
ROOT=Path(__file__).resolve().parents[2]
BASE_SHA="fbe69e04d5e693f6f91b7af7090b04ec43a3467feea1c17cd53fbc9cd9cffbf2"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument("kit")
p.add_argument("modules",nargs="*")
p.add_argument("--edge",action="store_true")
p.add_argument("--work",default="/root/.codex/tmp/paperx22_independent_audit")
a=p.parse_args(); work=Path(a.work); work.mkdir(parents=True,exist_ok=True)
arch=ROOT/"references/PRSC_X_v0.21.0_Checked_TwentyFirst_Block.zip"
assert sha(arch)==BASE_SHA
base=work/"baseline"; fresh=work/"new"; (fresh/"PaperX").mkdir(parents=True,exist_ok=True)
records=[]
with zipfile.ZipFile(arch) as z:
    for name in z.namelist():
        parts=Path(name).parts
        if len(parts)==4 and parts[1]=="build" and parts[3].endswith(".olean"):
            dest=base/Path(*parts[2:]);dest.parent.mkdir(parents=True,exist_ok=True)
            data=z.read(name)
            if not dest.exists() or dest.read_bytes()!=data:dest.write_bytes(data)
            combined=fresh/Path(*parts[2:])
            combined.parent.mkdir(parents=True,exist_ok=True)
            if not combined.exists() or combined.read_bytes()!=data:combined.write_bytes(data)
            records.append({"module":parts[3][:-6],"sha256":hashlib.sha256(data).hexdigest()})
assert len(records)==138,len(records)
spec=importlib.util.spec_from_file_location("lean_env",ROOT/"checks/lean_env.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
lean,env=m.lean_env(a.kit)
old=env["LEAN_PATH"].split(os.pathsep)
assert old[0]==str(ROOT/"build"),old
assert all(str(ROOT/"build") not in x for x in old[1:])
env["LEAN_PATH"]=os.pathsep.join([str(fresh)]+old[1:])
meta={"baseline_archive_sha256":BASE_SHA,"baseline_object_count":138,"baseline_objects":records,"project_build_excluded":True,"lean_path":env["LEAN_PATH"],"fresh_new_objects":str(fresh)}
(ROOT/"checks/local_audit/environment.json").write_text(json.dumps(meta,indent=2)+"\n")
for name in a.modules:
    src=ROOT/"lean/PaperX"/(name+".lean")
    out=fresh/"PaperX"/(name+".olean")
    out.unlink(missing_ok=True)
    command=[lean,"-DwarningAsError=true","-o",str(out),str(src)]
    t=time.monotonic();run=subprocess.run(command,cwd=ROOT/"lean",env=env,text=True,capture_output=True)
    log=ROOT/"checks/local_audit"/(name+".log")
    log.write_text(run.stdout+run.stderr)
    rec={"source":str(src.relative_to(ROOT)),"source_sha256":sha(src),"command":command,"exit_code":run.returncode,"elapsed_seconds":time.monotonic()-t,"fresh_proof_sha256":sha(out) if out.exists() else None,"log":str(log.relative_to(ROOT))}
    (ROOT/"checks/local_audit"/(name+".json")).write_text(json.dumps(rec,indent=2)+"\n")
    print(name,run.returncode,flush=True)
    if run.returncode:print(run.stdout+run.stderr,flush=True);raise SystemExit(run.returncode)
if a.edge:
    src=ROOT/"checks/local_audit/EdgeApplications.lean"
    command=[lean,"-DwarningAsError=true",str(src)]
    t=time.monotonic();run=subprocess.run(command,cwd=ROOT/"lean",env=env,text=True,capture_output=True)
    (ROOT/"checks/local_audit/EdgeApplications.log").write_text(run.stdout+run.stderr)
    (ROOT/"checks/local_audit/EdgeApplications.json").write_text(json.dumps({"source_sha256":sha(src),"command":command,"exit_code":run.returncode,"elapsed_seconds":time.monotonic()-t},indent=2)+"\n")
    print("EdgeApplications",run.returncode,flush=True)
    if run.returncode:print(run.stdout+run.stderr,flush=True);raise SystemExit(run.returncode)
