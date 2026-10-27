#!/usr/bin/env python3
"""Run the companion tests and regenerate examples; do not certify Lean or prose."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    ap=argparse.ArgumentParser(); ap.add_argument('--out', type=Path, default=root/'verification/python_recheck'); a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={'status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'stages':[], 'not_checked':['Lean proofs','Independent mathematical novelty','Python algorithm formal verification','PDF visual review','Wheel packaging']}
    def save(): (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    env=os.environ.copy();env['PYTHONPATH']=str(root/'code/python')+os.pathsep+env.get('PYTHONPATH','');env['MPLBACKEND']='Agg';env['MPLCONFIGDIR']=str(out/'matplotlib_cache');env['PYTHONDONTWRITEBYTECODE']='1'
    stages=[('tests',[sys.executable,'-m','pytest','-q','-W','error','-p','no:cacheprovider','--import-mode=importlib',str(root/'code/python/tests')]),('experiments',[sys.executable,str(root/'code/python/run_all.py')])]
    for name,cmd in stages:
        log=out/(name+'.log');t=time.monotonic()
        try:
            with log.open('w') as f:p=subprocess.run(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
            code=p.returncode
        except subprocess.TimeoutExpired: code=124
        text=log.read_text(errors='replace'); passed=code==0
        row={'stage':name,'command':cmd,'returncode':code,'status':'PASS' if passed else 'FAIL','elapsed_seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        if name=='tests':
            m=re.search(r'(\d+) passed',text)
            row['tests_passed']=int(m.group(1)) if m else None
            passed=passed and m is not None and int(m.group(1))==33
            row['status']='PASS' if passed else 'FAIL'
        report['stages'].append(row);save();print(name+': '+row['status'],flush=True)
        if not passed: report['status']='FAIL';save();return 1
    report['status']='PASS';report['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save();return 0
if __name__=='__main__':raise SystemExit(main())
