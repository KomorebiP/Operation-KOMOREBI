#!/usr/bin/env python3
"""Replay the named bounded programs in isolated temporary copies."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,time
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--only',nargs='+',help='Run selected gate names only.');a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 source=root/'baseline/block01/inherited/Komorebi_Paper_XI_Final_Edition_2026-10-06/source'
 original=source/'Paper_XI_Continuation113_Checked_Delta/Paper_XI_Continuation113_Arithmetic_Descent'
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');results=[]
 with tempfile.TemporaryDirectory(prefix='paper_xi_b03_') as td:
  project=Path(td)/'c113';shutil.copytree(original,project);ar=project/'evidence/arithmetic'
  jobs=[('new_exact_models',[sys.executable,str(root/'tools/exact_checks_block03.py'),'--output',str(out/'new_exact_models.json')],root/'tools/exact_checks_block03.py'),('block01_exact_models',[sys.executable,str(root/'baseline/block01/tools/exact_checks.py'),'--output',str(out/'block01_exact_models.json')],root/'baseline/block01/tools/exact_checks.py')]
  for name in ['cyclotomic_check113','self_twist113']:
   jobs.append((name,[sys.executable,str(ar/(name+'.py'))],original/('evidence/arithmetic/'+name+'.py')))
  jobs += [('central_twist_'+str(k),[sys.executable,str(ar/'central_twist113.py'),str(k)],original/'evidence/arithmetic/central_twist113.py') for k in range(3)]
  jobs += [('independent_exclusion',[sys.executable,str(project/'evidence/independent/self_twist_exclusion_check113.py')],original/'evidence/independent/self_twist_exclusion_check113.py'),('central_normalization',[sys.executable,str(ar/'central_normalization_check113.py')],original/'evidence/arithmetic/central_normalization_check113.py')]
  for label,cmd,pin in jobs:
   if a.only and label not in a.only:continue
   begin=time.monotonic();print('RUN',label,flush=True)
   try:
    r=subprocess.run(cmd,cwd=project,env=env,text=True,capture_output=True,timeout=180)
    (out/(label+'.stdout.log')).write_text(r.stdout);(out/(label+'.stderr.log')).write_text(r.stderr)
    item={'gate':label,'returncode':r.returncode,'status':'passed' if r.returncode==0 else 'failed'}
   except subprocess.TimeoutExpired as e:
    item={'gate':label,'status':'timeout','timeout_seconds':180};(out/(label+'.timeout.txt')).write_text(str(e))
   item.update(seconds=round(time.monotonic()-begin,3),source=str(pin.relative_to(root)),sha256=hashlib.sha256(pin.read_bytes()).hexdigest());results.append(item);(out/(label+'.receipt.json')).write_text(json.dumps(item,indent=2)+'\n');print(item['status'],flush=True)
  receipts=out/'historical_program_receipts';receipts.mkdir(exist_ok=True)
  for p in project.rglob('*.json'):
   src=original/p.relative_to(project)
   if not src.exists() or p.read_bytes()!=src.read_bytes():
    target=receipts/p.relative_to(project);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 report={'status':'passed' if all(x['status']=='passed' for x in results) else 'failed','gates':results,'scope':'Fresh bounded replay. Arithmetic implications depend on stated ordinary proofs and classical inputs. No Lean build.'}
 (out/'REPLAY_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report['status']!='passed'
if __name__=='__main__':raise SystemExit(main())
