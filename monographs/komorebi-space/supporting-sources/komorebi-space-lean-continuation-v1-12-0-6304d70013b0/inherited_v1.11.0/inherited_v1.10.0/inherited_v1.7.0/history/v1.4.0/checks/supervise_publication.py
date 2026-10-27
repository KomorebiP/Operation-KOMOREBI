#!/usr/bin/env python3
"""Run the publication build and retain a terminal receipt.

A unique label is required. This does not run the Lean compiler.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,subprocess,json,time,hashlib
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--label',required=True);a=p.parse_args()
if not a.label.replace('_','').replace('-','').isalnum():p.error('Use a simple alphanumeric label.')
out=R/'audit/deepening';out.mkdir(exist_ok=True,parents=True)
log=out/(a.label+'.stdout');receipt=out/(a.label+'.json')
if log.exists() or receipt.exists():raise SystemExit('Refusing to overwrite an existing audit label')
start=datetime.now(timezone.utc).isoformat();t=time.monotonic()
base={'started_utc':start,'argv':['bash','build.sh'],'log':str(log.relative_to(R)),'scope':'Publication build, exact tests and source checks. No fresh Lean replay.'}
try:
    with log.open('w') as f:
        result=subprocess.run(['bash','build.sh'],cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
    base.update(status='PASS' if result.returncode==0 else 'FAIL',exit_code=result.returncode)
except Exception as exc:
    base.update(status='FAIL',exit_code=None,error=repr(exc))
base.update(finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-t,
            log_sha256=hashlib.sha256(log.read_bytes()).hexdigest() if log.exists() else None)
receipt.write_text(json.dumps(base,indent=2)+'\n')
print(json.dumps(base,indent=2),flush=True)
