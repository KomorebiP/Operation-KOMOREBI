#!/usr/bin/env python3
"""Bounded end-to-end regression for AVOC v0.37 lazy staged recovery.

Run one case at a time on execution-capped hosts:
  python checks/test_lazy_staged_workflow.py --case warm
  python checks/test_lazy_staged_workflow.py --case cold
  python checks/test_lazy_staged_workflow.py --case crash
  python checks/test_lazy_staged_workflow.py --case invalid
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/'tools/lazy_staged_workflow.py'
DIRECT=ROOT/'tools/run_lazy_staged.py'
EX=ROOT/'examples/lazy_staged'
OUT=ROOT/'results/v0.37.0/runtime/final'
OUT.mkdir(parents=True,exist_ok=True)

def run(cmd, expect=(0,), timeout=900):
    t=time.monotonic()
    cp=subprocess.run(['python',*map(str,cmd)],cwd=ROOT,text=True,capture_output=True,
                      timeout=timeout,env=os.environ.copy())
    if cp.returncode not in expect:
        raise AssertionError(f"unexpected code {cp.returncode}\nSTDOUT={cp.stdout}\nSTDERR={cp.stderr}")
    data=json.loads(cp.stdout) if cp.stdout.strip() else None
    return data,cp,round(time.monotonic()-t,3)

def save(name,obj):
    (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def warm_case():
    d=OUT/'warm_run'; shutil.rmtree(d,ignore_errors=True)
    data,cp,seconds=run([WORKFLOW,'start',EX/'warm_selected.json','--run-dir',d,'--timeout',240])
    assert data['status']=='complete' and data['warm_calls']==1 and data['cold_calls']==0
    assert data['warm_present'] and not data['cold_present']
    rec={'case':'warm','seconds':seconds,'result':data}; save('warm',rec); return rec

def cold_case():
    d=OUT/'cold_run'; shutil.rmtree(d,ignore_errors=True)
    data,cp,seconds=run([WORKFLOW,'start',EX/'cold_selected.json','--run-dir',d,'--timeout',240])
    assert data['status']=='complete' and data['warm_calls']==0 and data['cold_calls']==1
    assert data['cold_present'] and not data['warm_present']
    rec={'case':'cold','seconds':seconds,'result':data}; save('cold',rec); return rec

def crash_case():
    d=OUT/'crash_run'; shutil.rmtree(d,ignore_errors=True)
    _,cp,s0=run([WORKFLOW,'start',EX/'warm_selected.json','--run-dir',d,'--timeout',240,
                 '--crash-after-commit',0],expect=(97,))
    mid,_,s1=run([WORKFLOW,'inspect','--run-dir',d])
    assert mid['next_seq']==0 and mid['operations'][0]['phase']=='committed' and mid['warm_calls']==1
    recovered,_,s2=run([WORKFLOW,'resume','--run-dir',d,'--recover-only','--timeout',240])
    assert recovered['next_seq']==1 and recovered['recovery_rechecks']==1 and recovered['warm_calls']==1
    final,_,s3=run([WORKFLOW,'resume','--run-dir',d,'--timeout',240])
    assert final['status']=='complete' and final['next_seq']==2 and final['warm_calls']==1
    repeat,_,s4=run([WORKFLOW,'resume','--run-dir',d,'--recover-only','--timeout',240])
    assert repeat['status']=='complete' and repeat['next_seq']==2 and repeat['warm_calls']==1
    rec={'case':'crash','seconds':s0+s1+s2+s3+s4,'crash_returncode':cp.returncode,
         'before_recovery':mid,'after_recovery':recovered,'final':final,'repeat':repeat}
    save('crash',rec); return rec

def invalid_case():
    valid_plan,_,s0=run([DIRECT,EX/'plan.json','--timeout',240])
    valid_transition,_,s1=run([DIRECT,EX/'warm_success.json','--timeout',240])
    after,_,s2=run([DIRECT,EX/'plan_after_warm.json','--timeout',240])
    assert valid_plan['choice']=='inspect_warm' and valid_plan['expected_value']=='14867'
    assert valid_transition['after']==['ready','untried',63,133,196,False]
    assert after['choice']=='deploy_warm' and after['expected_value']=='15000'
    rejected=[]
    seconds=s0+s1+s2
    for name in ['quote_mismatch_transition','fault_transition','deploy_before_ready']:
        data,cp,sec=run([DIRECT,EX/f'{name}.json','--timeout',240],expect=(2,))
        assert data is None
        rejected.append({'name':name,'returncode':cp.returncode,'stderr':cp.stderr.strip()})
        seconds+=sec
    rec={'case':'invalid','seconds':seconds,'initial':valid_plan,'success':valid_transition,
         'after':after,'rejected':rejected}; save('invalid',rec); return rec

CASES={'warm':warm_case,'cold':cold_case,'crash':crash_case,'invalid':invalid_case}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case',choices=[*CASES,'all'],default='all')
    ns=ap.parse_args()
    names=list(CASES) if ns.case=='all' else [ns.case]
    records=[CASES[n]() for n in names]
    if ns.case=='all': save('summary',{'passed':len(records),'cases':records})
    print(json.dumps({'passed':len(records),'cases':[r['case'] for r in records]},sort_keys=True))

if __name__=='__main__': main()
