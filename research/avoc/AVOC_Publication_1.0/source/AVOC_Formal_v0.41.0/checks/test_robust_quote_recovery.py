#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/robust_quote_workflow.py'
OUT=ROOT/'results/v0.38.0/robust_quote_recovery_regression.json'
ENV=os.environ.copy(); ENV.setdefault('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')

def call(args):
    cp=subprocess.run([sys.executable,str(TOOL)]+list(map(str,args)),cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert cp.returncode==0,(args,cp.returncode,cp.stdout,cp.stderr)
    return json.loads(cp.stdout)

def main():
    run=ROOT/'results/v0.38.0/workflow_recovery_run'
    shutil.rmtree(run,ignore_errors=True)
    log=ROOT/'results/v0.38.0/workflow_recovery_process.log'
    with log.open('w') as f:
        cp=subprocess.run([sys.executable,str(TOOL),'start',str(ROOT/'examples/robust_quote/workflow_warm.json'),'--run-dir',str(run),'--inject-after-commit'],cwd=ROOT,env=ENV,text=True,stdout=f,stderr=subprocess.STDOUT,timeout=90)
    assert cp.returncode==97,(cp.returncode,log.read_text())
    before=call(['inspect','--run-dir',run])
    assert before['status']=='committed' and before['external_calls']=={'warm':1,'cold':0}
    after=call(['resume','--run-dir',run])
    assert after['status']=='acknowledged' and after['external_calls']=={'warm':1,'cold':0}
    again=call(['resume','--run-dir',run])
    assert again==after
    result={'schema':'avoc-v0.38-recovery-regression-v1','before_recovery':before,
            'after_recovery':after,'duplicate_resume':again,
            'result':'commit-before-ack recovery passed without another external operation',
            'non_claims':['controlled interpreter exit is not electrical power-loss certification','SQLite/Python/OS are trusted boundaries']}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':result['result'],'external_calls':after['external_calls']},sort_keys=True))
if __name__=='__main__': main()
