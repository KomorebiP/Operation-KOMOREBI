#!/usr/bin/env python3
"""Inject a deliberately ill-typed theorem into the exact kernel-replay input."""
from pathlib import Path
import argparse,json,os,subprocess,sys

def main():
 p=argparse.ArgumentParser();p.add_argument('--kit',type=Path,required=True);p.add_argument('--objects',type=Path);a=p.parse_args();r=Path(__file__).resolve().parents[1]
 env=os.environ.copy();env['KOMOREBI_REPLAY_CORRUPT']='1'
 cmd=[sys.executable,str(r/'tools/run_lean.py'),'ReplayClosure','--kit',str(a.kit),'--source-root',str(r/'formal/audit'),'--tag','controls','--timeout','420']
 if a.objects:cmd.extend(['--objects',str(a.objects)])
 run=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 first=json.loads(run.stdout.splitlines()[0]);receipt=Path(first['receipt']);d=json.loads(receipt.read_text());log=(receipt.parent/'compile.log').read_text()
 accepted=d['status']=='FAIL' and d['exit_code']!=0 and 'REPLAY_CORRUPT_CONTROL_INJECTED' in log and 'REPLAY_CLOSURE_PASS' not in log and '(kernel) declaration type mismatch' in log and "while replaying declaration 'PaperIIIReplayControl.falseEquality'" in log
 report={'schema':'paper-iii.kernel-negative-control/1','status':'PASS' if accepted else 'FAIL','actual_compile_status':d['status'],'receipt':str(receipt.relative_to(r)),'injected_type':'(0 : Nat) = 1','injected_value':'Eq.refl (0 : Nat)','expected':'Kernel rejects the inserted theorem proof, not a timeout or import failure','exit_code':d['exit_code']}
 (r/'verification/KERNEL_NEGATIVE_CONTROL.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));print(log[-2500:])
 return 0 if accepted else 1
if __name__=='__main__':raise SystemExit(main())
