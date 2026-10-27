#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
LAKE = KIT/'toolchain/bin/lake'
LEAN = KIT/'toolchain/bin/lean'
COMMANDS = {
 'build_block35_import_closure': ([str(LAKE), '-Kjobs=16', '--wfail', 'build', 'KomorebiPhysics.Relativistic3DL2CellReconstruction'], False, None),
 'build_full_cumulative_project': ([str(LAKE), '-Kjobs=16', '--wfail', 'build', 'KomorebiPhysics'], False, None),
 'compile_block35_warning_as_error': ([str(LEAN), '-DwarningAsError=true', 'KomorebiPhysics/Relativistic3DL2CellReconstruction.lean'], False, None),
 'compile_block35_api': ([str(LEAN), '-DwarningAsError=true', 'CheckBlock35API.lean'], False, None),
 'audit_block35': ([str(LEAN), 'AuditBlock35.lean'], False, None),
 'negative_FalseAveragingNotLeftInverse': ([str(LEAN), '-DwarningAsError=true', 'negative_controls/block35/FalseAveragingNotLeftInverse.lean'], True, 'error:'),
 'negative_FalseProjectionNormAboveOne': ([str(LEAN), '-DwarningAsError=true', 'negative_controls/block35/FalseProjectionNormAboveOne.lean'], True, 'error:'),
 'negative_FalseResidualInnerOne': ([str(LEAN), '-DwarningAsError=true', 'negative_controls/block35/FalseResidualInnerOne.lean'], True, 'error:'),
}

def sha256(p: Path) -> str:
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('label', choices=COMMANDS); ap.add_argument('--out', default='verification/block35_final'); ap.add_argument('--timeout', type=int, default=1800); a=ap.parse_args()
 out=ROOT/a.out; out.mkdir(parents=True, exist_ok=True)
 argv, expected_failure, diagnostic=COMMANDS[a.label]
 env=os.environ.copy(); env['PATH']=str(KIT/'toolchain/bin')+os.pathsep+env.get('PATH','')
 for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT'): env.pop(k,None)
 if argv[0]==str(LEAN):
  env['LEAN_PATH']=subprocess.check_output([str(LAKE),'env','printenv','LEAN_PATH'],cwd=ROOT,env=env,text=True).strip()
 log=out/f'{a.label}.log'; t0=time.monotonic(); timed_out=False; rc=None
 with log.open('w',encoding='utf-8') as f:
  try:
   p=subprocess.run(argv,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,text=True,timeout=a.timeout)
   rc=p.returncode
  except subprocess.TimeoutExpired:
   timed_out=True; f.write('\nGATE_TIMEOUT\n')
 text=log.read_text(errors='replace'); lower=text.lower()
 if expected_failure:
  ok=not timed_out and rc not in (0,None) and diagnostic in text and 'unknown module prefix' not in lower and 'object file' not in lower and 'no such file or directory' not in lower
 else:
  ok=not timed_out and rc==0
 rec={'label':a.label,'argv':argv,'returncode':rc,'timed_out':timed_out,'seconds':round(time.monotonic()-t0,4),'expected_failure':expected_failure,'diagnostic':diagnostic,'status':'PASS' if ok else 'FAIL','log':str(log.relative_to(ROOT)),'log_sha256':sha256(log)}
 (out/f'{a.label}.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps(rec,indent=2))
 raise SystemExit(0 if ok else 1)
if __name__=='__main__': main()
