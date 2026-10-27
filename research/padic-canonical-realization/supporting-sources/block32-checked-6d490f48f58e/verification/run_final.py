#!/usr/bin/env python3
from pathlib import Path
import sys,subprocess,json,shutil,hashlib
root=Path(__file__).resolve().parents[1]
shutil.rmtree(root/'.lake/build',ignore_errors=True)
for row in json.loads((root/'verification/final_plan.json').read_text()):
    cp=subprocess.run([sys.executable,str(root/'verification/run_command.py'),row['label'],*row['argv']],cwd=root)
    log=(root/'results'/f"{row['label']}.log").read_text()
    if cp.returncode!=row['exit'] or ('diagnostic' in row and row['diagnostic'] not in log):
        print('FAILED_FINAL_PHASE',row['label'],cp.returncode,flush=True);sys.exit(1)
compiled=root/'compiled';shutil.rmtree(compiled,ignore_errors=True);compiled.mkdir()
for q in (root/'.lake/build/lib/lean').rglob('*'):
    if q.suffix in {'.olean','.ilean'}:
        dest=compiled/q.relative_to(root/'.lake/build/lib/lean');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
print('FINAL_PHASES_PASSED',flush=True)
