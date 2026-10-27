#!/usr/bin/env python3
"""Two deliberately invalid Lean inputs must be rejected by the pinned compiler."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);a=p.parse_args()
 root=Path(__file__).resolve().parent;dst=root/'negative';dst.mkdir(exist_ok=True)
 out=[]
 for name,text in [('FalseEquality','example : (1 : Nat) = 0 := by rfl\n'),('Placeholder','example : False := by sorry\n')]:
  src=dst/(name+'.lean');src.write_text(text)
  argv=['bash',str(a.runtime.resolve()/'run.sh'),'lake','env','lean','-j1','-DwarningAsError=true',str(src)]
  t=time.monotonic();r=subprocess.run(argv,cwd=a.runtime/'workspace',capture_output=True,text=True,timeout=30)
  log=dst/(name+'.log');log.write_text(r.stdout+r.stderr)
  expected=('Tactic' in log.read_text() or 'rfl' in log.read_text()) if name=='FalseEquality' else 'sorry' in log.read_text()
  assert r.returncode!=0 and expected,(name,r.returncode,log.read_text())
  out.append({'name':name,'argv':argv,'exit_status':r.returncode,'elapsed_seconds':round(time.monotonic()-t,3),
   'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
   'expected_rejection':True})
 (root/'NEGATIVE_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print('Both negative controls rejected as expected')
if __name__=='__main__':main()
