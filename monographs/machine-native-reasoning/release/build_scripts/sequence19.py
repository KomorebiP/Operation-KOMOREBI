#!/usr/bin/env python3
"""Run primary and independently extracted cold gates sequentially, then compare.

Freeze first with freeze19.py. All outcomes, including failures, are preserved.
Source/documentation files must not be edited once either gate starts.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--fresh',type=Path,required=True)
    ap.add_argument('--snapshot',type=Path,default=ROOT/'evidence/CORE32_FROZEN_SOURCE.zip')
    ap.add_argument('--whole-timeout',type=int,default=1800)
    args=ap.parse_args()
    runtime=args.runtime.resolve();fresh=args.fresh.resolve();snapshot=args.snapshot.resolve()
    output=ROOT/'evidence/SEQUENCE19.json'
    if output.exists():raise FileExistsError(output)
    for rel,base in [('final19',ROOT),('fresh19',fresh)]:
        if (base/'evidence'/rel).exists() or (base/'evidence'/(rel+'_supervisor.json')).exists():
            raise FileExistsError('Gate destination already exists: '+rel)
    record={'status':'RUNNING_PRIMARY','started_at':time.time(),'runs':[]}
    def save():output.write_text(json.dumps(record,indent=2)+'\n')
    output.parent.mkdir(parents=True,exist_ok=True);save()
    try:
        for label,base in [('final19',ROOT),('fresh19',fresh)]:
            cmd=[sys.executable,str(base/'scripts/supervise.py'),'--runtime',str(runtime),
                 '--out','evidence/'+label,'--whole-timeout',str(args.whole_timeout)]
            with (ROOT/'evidence'/('launch_'+label+'.log')).open('x') as log:
                run=subprocess.run(cmd,cwd=base,stdout=log,stderr=subprocess.STDOUT,timeout=args.whole_timeout+60)
            record['runs'].append({'label':label,'argv':cmd,'exit_code':run.returncode})
            if base!=ROOT and (base/'evidence').exists():
                for path in (base/'evidence').iterdir():
                    target=ROOT/'evidence'/path.name
                    if target.exists():raise FileExistsError('Refusing evidence replacement: '+str(target))
                    if path.is_dir():shutil.copytree(path,target)
                    else:shutil.copy2(path,target)
            save()
            receipt=json.loads((base/'evidence'/label/'report.json').read_text())
            supervisor=json.loads((base/'evidence'/(label+'_supervisor.json')).read_text())
            if run.returncode or receipt.get('status')!='PASS' or supervisor.get('exit_code')!=0 or supervisor.get('status')!='completed':
                raise RuntimeError(label+' did not pass; no subsequent gate admitted')
            record['status']='RUNNING_FRESH' if label=='final19' else 'COMPARING';save()
        cmd=[sys.executable,str(ROOT/'scripts/compare_rebuild.py'),'--final',str(ROOT/'evidence/final19'),
             '--fresh',str(ROOT/'evidence/fresh19'),'--snapshot',str(snapshot),'--out',str(ROOT/'evidence/CORE32_COMPARISON.json')]
        run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=45)
        (ROOT/'evidence/CORE32_COMPARISON.log').write_text(run.stdout+run.stderr)
        record['comparison_exit_code']=run.returncode
        if run.returncode:raise RuntimeError('Fresh comparison did not pass')
        record['status']='PASS'
    except Exception as exc:
        record['status']='FAIL';record['failure']=f'{type(exc).__name__}: {exc}'
    record['ended_at']=time.time();save();print(json.dumps(record,indent=2))
    return 0 if record['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
