#!/usr/bin/env python3
"""Run the three explicitly scoped finite suites without modifying the package."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=a.output.resolve()
 if out.is_relative_to(root):raise SystemExit('Replay output must be outside the immutable checkpoint root.')
 out.mkdir(parents=True,exist_ok=True);base=root/'predecessor/block03'
 jobs=[('block04_exact_models',root/'tools/exact_checks_block04.py',23),('block03_exact_models',base/'tools/exact_checks_block03.py',15),('block01_exact_models',base/'baseline/block01/tools/exact_checks.py',12)]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');records=[]
 for label,source,expected in jobs:
  target=out/(label+'.json');cmd=[sys.executable,str(source),'--output',str(target)];t=time.monotonic()
  print('RUN',label,flush=True)
  try:
   r=subprocess.run(cmd,cwd=out,env=env,text=True,capture_output=True,timeout=90)
   (out/(label+'.stdout.log')).write_text(r.stdout);(out/(label+'.stderr.log')).write_text(r.stderr)
   data=json.loads(target.read_text()) if target.exists() else {}
   count=data.get('test_methods',data.get('methods',data.get('unittest_methods')))
   # Retained suites differ in their JSON field names; unittest stderr is retained too.
   item={'gate':label,'status':'passed' if r.returncode==0 and data.get('status')=='passed' and count==expected else 'failed','returncode':r.returncode,'expected_test_methods':expected,'reported_count_field':count,'result_sha256':hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None}
  except subprocess.TimeoutExpired as e:
   item={'gate':label,'status':'timeout','error':str(e)}
  item.update(source=source.relative_to(root).as_posix(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),seconds=round(time.monotonic()-t,3))
  (out/(label+'.receipt.json')).write_text(json.dumps(item,indent=2)+'\n');records.append(item);print(item['status'],flush=True)
 result={'status':'passed' if all(r['status']=='passed' for r in records) else 'failed','gates':records,'scope':'Three finite suites only. Seven additional historical B03 arithmetic executions were not rerun by this driver. No new arithmetic matrix-constructor or Lean run.'}
 (out/'REPLAY_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result['status']!='passed'
if __name__=='__main__':raise SystemExit(main())
