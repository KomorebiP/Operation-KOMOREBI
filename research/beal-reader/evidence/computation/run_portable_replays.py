#!/usr/bin/env python3
"""Run bundled historical scientific replays with complete version-2 input pins."""
import argparse, concurrent.futures, json, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blocks',nargs='+',type=int,choices=range(67,80),default=list(range(67,80)))
    p.add_argument('--suffix',default='run')
    p.add_argument('--workers',type=int,choices=(1,2),default=2)
    ns=p.parse_args()
    def one(n):
        contract=f'evidence/computation/contracts/portable{n}.json'
        inputs=json.loads(Path(contract).read_text())['execution_artifacts']
        output=f'evidence/computation/portable{n}-{ns.suffix}'
        argv=[sys.executable,'evidence/computation/tools/run_experiment.py','--root','.', '--contract',contract]
        for path in inputs:argv+=['--input',path]
        argv+=['--output',output,'--result',output+'/report.json','--timeout','900','--max-output-bytes','2097152','--max-memory-bytes','2147483648','--max-cpu-seconds','800','--max-cores','2','--max-threads','1',
               '--',sys.executable,'-B','evidence/computation/portable_historical.py','--block',str(n),'--output',output]
        cp=subprocess.run(argv,capture_output=True,text=True)
        print(json.dumps({'block':n,'exit_status':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}),flush=True)
        return cp.returncode
    with concurrent.futures.ThreadPoolExecutor(max_workers=ns.workers) as pool:
        results=list(pool.map(one,ns.blocks))
    return int(any(results))

if __name__=='__main__':
    raise SystemExit(main())
