#!/usr/bin/env python3
"""Fresh project-only rebuild followed by every final verification phase."""
from pathlib import Path
import subprocess,os,json,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'verification/final_plan.json').read_text())
# This path is project-local. Dependency cache symlinks are retained.
shutil.rmtree(ROOT/'.lake/build',ignore_errors=True)
for step in plan:
 cp=subprocess.run([sys.executable,'verification/run_current.py',step['label'],*step['argv']],cwd=ROOT)
 if cp.returncode!=step['expected_exit']:
  print('FINAL_SEQUENCE_STOPPED',step['label'],cp.returncode,flush=True);sys.exit(1)
 if 'diagnostic' in step and step['diagnostic'] not in (ROOT/'results_current'/f"{step['label']}.log").read_text():
  print('WRONG_CONTROL_DIAGNOSTIC',step['label'],flush=True);sys.exit(1)
compiled=ROOT/'compiled';shutil.rmtree(compiled,ignore_errors=True);compiled.mkdir()
rows=[]
for p in sorted((ROOT/'.lake/build/lib/lean').rglob('*')):
 if p.suffix not in {'.olean','.ilean'}:continue
 rel=p.relative_to(ROOT/'.lake/build/lib/lean');dst=compiled/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
 rows.append({'path':str(rel),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(compiled/'ARTIFACT_HASHES.json').write_text(json.dumps(rows,indent=2))
print('FINAL_COMPILER_PHASES_PASSED',len(plan),flush=True)
