#!/usr/bin/env python3
"""Run the supplied exact checks and save a project-local execution receipt.

This receipt is not an externally authenticated audit and is not a proof-assistant
certificate. Source code is pinned before and after each run. Subprocess wall
limits are enforced; no independent memory or operating-system isolation is added.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    paths=sorted((ROOT/'code').glob('*.py'))+[ROOT/'Self_Improving_Intelligence_v0.2.0.tex',ROOT/'build.sh']
    numbering=ROOT/'validation'/'document_numbers.json'
    if numbering.exists():paths.append(numbering)
    before={str(p.relative_to(ROOT)):digest(p) for p in paths}
    (ROOT/'validation').mkdir(exist_ok=True)
    start=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();runs=[]
    commands=[['code/check_finite_models.py'],['code/demo.py'],['code/check_discovery_models.py'],['code/demo_discovery.py'],['code/check_preservation.py'],['code/audit_source.py']]
    for args in commands:
        argv=[sys.executable,*args];t=time.perf_counter();log=ROOT/'validation'/f"{Path(args[0]).stem}_run.log"
        limit=90 if args[0].endswith('check_finite_models.py') else 45
        print('RUN',args[0],'wall limit',limit,flush=True)
        with log.open('w') as out:
            try:
                proc=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,timeout=limit,check=False)
                status='completed' if proc.returncode==0 else 'failed';exitstatus=proc.returncode
            except subprocess.TimeoutExpired:
                status='timeout';exitstatus=None
        runs.append({'argv':argv,'wall_limit_seconds':limit,'runtime_seconds':time.perf_counter()-t,
                     'exit_status':exitstatus,'status':status,'log':str(log.relative_to(ROOT))})
        print(log.read_text(),end='')
        if status!='completed':break
    after={str(p.relative_to(ROOT)):digest(p) for p in paths}
    outputs=sorted([p for p in (ROOT/'validation').glob('*.json') if p.name in
                    ('finite_checks.json','demonstration.json','cell_certificate.json','source_audit.json','discovery_checks.json','discovery_demonstration.json','discovery_policy.json','descendant_tree_16.json','calibration_tree.json','preservation_audit.json')])
    status='PASS' if len(runs)==len(commands) and all(x['status']=='completed' for x in runs) and before==after else 'FAIL'
    manifest={'schema':'komorebi-local-execution-1','status':status,'started_at':start,'runtime_seconds':time.perf_counter()-clock,
      'python':sys.version,'platform':platform.platform(),'executable':sys.executable,'git_revision':None,
      'arithmetic':'Integers, finite sets, fractions.Fraction','randomness_used':False,
      'inputs_before':before,'inputs_after':after,'runs':runs,
      'outputs':{str(p.relative_to(ROOT)):digest(p) for p in outputs},
      'limits':['No neural training or learned model was run.','No network access by these reference programs.',
                'No independent execution attestation or proof-kernel verification.',
                'No separate process memory limit or OS sandbox. The unchanged inherited suite has a 90-second wall timeout; other subprocesses have 45 seconds.',
                'Finite algorithmic cross-checks are authored in the same project.']}
    (ROOT/'validation'/'execution_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Execution receipt: {status}')
    if status!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
