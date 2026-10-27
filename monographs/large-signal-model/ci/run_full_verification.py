#!/usr/bin/env python3
"""Run the unchanged source-bound release verifier with new receipts outside Lean/."""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path

def digest(path: Path) -> str:return hashlib.sha256(path.read_bytes()).hexdigest()
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=Path('Lean'))
    ap.add_argument('--kit',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--timeout',type=int,default=900)
    args=ap.parse_args();project=args.project.resolve();out=args.out.resolve()
    if not 1<=args.timeout<=3600:ap.error('--timeout must be between 1 and 3600 seconds')
    if out.is_relative_to(project):ap.error('Fresh receipts must be outside immutable Lean/.')
    out.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(project/'scripts/verify.py'),'--kit',str(args.kit.resolve()),'--out',str(out),'--timeout',str(args.timeout)]
    receipt={'kind':'fresh GitHub/local verifier invocation','passed':False,'command':command,
             'github_commit':os.environ.get('GITHUB_SHA'),'platform':platform.platform(),
             'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    start=time.monotonic()
    try:
        code=subprocess.run(command,cwd=project,env=env).returncode
        receipt['returncode']=code
        if code!=0:raise RuntimeError(f'The Lean verifier failed with exit {code}.')
        report=json.loads((out/'report.json').read_text())
        if not report.get('passed') or not report.get('complete'):raise ValueError('The verifier did not produce a complete PASS report.')
        for name,h in report['source_snapshot'].items():
            path=(project/name).resolve()
            if not path.is_relative_to(project) or digest(path)!=h:raise ValueError(f'Source changed after verification: {name}')
        receipt.update(passed=True,report_sha256=digest(out/'report.json'),counts=report['counts'])
    except Exception as exc:
        receipt['failure']=str(exc)
    finally:
        receipt['seconds']=round(time.monotonic()-start,3)
        receipt['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        (out.parent/'ci_run.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not receipt['passed']:
        print('VERIFICATION FAILED: '+receipt['failure'],file=sys.stderr);return 1
    print('Fresh clean Lean verification passed. The original release evidence was not overwritten.')
    return 0
if __name__=='__main__':raise SystemExit(main())
