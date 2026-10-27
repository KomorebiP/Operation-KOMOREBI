#!/usr/bin/env python3
"""Replay explicit archived finite checks into new bounded evidence directories."""
from __future__ import annotations
import argparse, importlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
VERSION_MODULES={'NumPy':'numpy','Pandas':'pandas','Matplotlib':'matplotlib'}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--output',type=Path,required=True,help='New project-relative output directory')
    p.add_argument('--modes',nargs='+',default=['integrity','static','unit','original','sixth','fifth','structured','test-functions'],choices=['integrity','static','unit','original','sixth','fifth','structured','test-functions'])
    args=p.parse_args();root=args.root.resolve();output=args.output
    if output.is_absolute() or '..' in output.parts:raise SystemExit('Output must be a relative project path')
    base=root/output
    if base.exists():raise SystemExit('Output must be new')
    base.mkdir(parents=True)
    for mode in args.modes:
        contract=json.loads((root/'verification/contracts'/f'{mode}.json').read_text())
        for software in contract['software']:
            if software['name']=='Python':software['version']=sys.version.split()[0]
            elif software['name'] in VERSION_MODULES:software['version']=importlib.import_module(VERSION_MODULES[software['name']]).__version__
        cp=base/f'{mode}-contract.json';cp.write_text(json.dumps(contract,indent=2)+'\n')
        dest=output/mode
        argv=[sys.executable,str(root/'verification/checks/run_experiment.py'),'--root',str(root),'--contract',str(cp),'--output',str(dest),'--result',str(dest/'result.json'),'--timeout','240','--max-output-bytes','4194304','--max-memory-bytes','2147483648','--max-cpu-seconds','210','--max-cores','1','--max-threads','1']
        for rel in contract['execution_artifacts']:argv+=['--input',rel]
        argv+=['--',sys.executable,'verification/checks/replay.py',mode,'--out',str(dest/'result.json')]
        run=subprocess.run(argv,cwd=root)
        if run.returncode:raise SystemExit(run.returncode)
        check=subprocess.run([sys.executable,str(root/'verification/checks/validate_manifest.py'),str(root/dest/'manifest.json'),'--root',str(root)],cwd=root)
        if check.returncode:raise SystemExit(check.returncode)
if __name__=='__main__':main()
