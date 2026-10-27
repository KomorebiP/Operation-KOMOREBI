#!/usr/bin/env python3
"""Reproduce the delivered exact suite and stage its scientific results."""
from pathlib import Path
import json, shutil, subprocess, sys

root=Path(__file__).resolve().parents[1]
out=root/'verification/final_computation'
out.mkdir(exist_ok=True)
for command in [('code/demo_commons.py',),('code/demo_accountability.py',),('validation/check_finite_models.py',)]:
    done=subprocess.run([sys.executable,*command],cwd=root,text=True,capture_output=True)
    (out/(Path(command[0]).stem+'_stdout.txt')).write_text(done.stdout)
    (out/(Path(command[0]).stem+'_stderr.txt')).write_text(done.stderr)
    if done.returncode:
        print(done.stdout);print(done.stderr,file=sys.stderr)
        raise SystemExit(done.returncode)
for name in ['finite_checks.json','computation_manifest.json','commons_joint_certificate.json','accountability_demo.json']:
    shutil.copy2(root/'validation'/name,out/name)
result=json.loads((out/'finite_checks.json').read_text())
print(json.dumps({k:result[k] for k in ['status','group_count','assertions','runtime_seconds']},indent=2))
raise SystemExit(result['status']!='PASS')
