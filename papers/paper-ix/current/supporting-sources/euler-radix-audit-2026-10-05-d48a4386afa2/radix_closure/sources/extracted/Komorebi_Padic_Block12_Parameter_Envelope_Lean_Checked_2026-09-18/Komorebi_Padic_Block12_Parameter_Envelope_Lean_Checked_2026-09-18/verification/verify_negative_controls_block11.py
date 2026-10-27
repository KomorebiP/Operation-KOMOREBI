#!/usr/bin/env python3
from __future__ import annotations
import json,os,subprocess
from pathlib import Path

def main()->int:
 root=Path(__file__).resolve().parents[1]
 cases=[('false_theorem',root/'verification'/'RejectFalse.lean',root/'logs'/'reject_false_block11.log'),('sorry_placeholder',root/'verification'/'RejectSorry.lean',root/'logs'/'reject_sorry_block11.log')]
 records=[]; passed=True; env=dict(os.environ); env['TERM']='dumb'
 for name,source,log in cases:
  try:
   result=subprocess.run(['lake','env','lean','-DwarningAsError=true',str(source)],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180,check=False)
   log.write_text(result.stdout,encoding='utf-8')
   rejected=result.returncode!=0
   records.append({'name':name,'source':str(source.relative_to(root)),'exit_code':result.returncode,'timed_out':False,'rejected':rejected,'passed':rejected})
   passed &= rejected
  except subprocess.TimeoutExpired as exc:
   output=exc.stdout or ''
   if isinstance(output,bytes): output=output.decode(errors='replace')
   log.write_text(output+'\nTIMEOUT\n',encoding='utf-8')
   records.append({'name':name,'source':str(source.relative_to(root)),'exit_code':None,'timed_out':True,'rejected':False,'passed':False})
   passed=False
 report={'schema':'komorebi-padic-block11-negative-controls-v1','status':'PASS' if passed else 'FAIL','records':records}
 (root/'results'/'kernel_controls_block11.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2,sort_keys=True))
 return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
