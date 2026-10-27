#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/robust_quote_workflow.py'
OUT=ROOT/'results/v0.38.0/robust_quote_workflow_regression.json'
ENV=os.environ.copy(); ENV.setdefault('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')

def call(args):
    cp=subprocess.run([sys.executable,str(TOOL)]+list(map(str,args)),cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert cp.returncode==0,(args,cp.returncode,cp.stdout,cp.stderr)
    return json.loads(cp.stdout)

def main():
    base=ROOT/'results/v0.38.0/workflow_normal_runs'
    shutil.rmtree(base,ignore_errors=True); base.mkdir(parents=True)
    warm=call(['start',ROOT/'examples/robust_quote/workflow_warm.json','--run-dir',base/'warm'])
    assert warm['status']=='acknowledged' and warm['external_calls']=={'warm':1,'cold':0}
    cold=call(['start',ROOT/'examples/robust_quote/workflow_cold.json','--run-dir',base/'cold'])
    assert cold['status']=='acknowledged' and cold['external_calls']=={'warm':0,'cold':1}
    result={'schema':'avoc-v0.38-workflow-regression-v1','warm_selected':warm,'cold_selected':cold,
            'result':'selected-only normal workflows passed',
            'non_claims':['SQLite/Python/OS are trusted boundaries','missing unselected paths test lazy opening, not hostile filesystem behavior']}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':result['result'],'scenarios':2},sort_keys=True))
if __name__=='__main__': main()
