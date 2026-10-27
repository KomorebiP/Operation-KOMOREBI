#!/usr/bin/env python3
"""Replay immutable Paper XII finite checks and authenticate historical evidence.
No Lean compiler is invoked. Outputs must be outside the release tree.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--gates',nargs='*');a=ap.parse_args()
 out=a.output.resolve()
 if out==ROOT or ROOT in out.parents:raise ValueError('Keep replay outputs outside the release tree')
 out.mkdir(parents=True,exist_ok=True)
 pre=ROOT/'predecessor';bundle=pre/'source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix';base=pre/'verification/computation'
 task=base/'replay_task.py'
 gates=[]
 for name in ['integrity','original-finite','appendix-exact']:
  gates.append((name,task,[name,'--project',str(pre),'--bundle',str(bundle),'--output',str(out/name)]))
 gates += [('visual-exact',pre/'editable/visual_guide/checks/verify_examples.py',['--output',str(out/'visual-exact.json')]),
  ('primitive-benchmark',base/'benchmark_no_bytecode.py',['--source',str(bundle/'history/original_manuscript/verification/verify_paper_xii.py'),'--output',str(out/'primitive-benchmark.json')]),
  ('native-record-authentication',base/'audit_native_reverification.py',['--project',str(pre),'--output',str(out/'native-record-authentication.json')])]
 if (ROOT/'tools/test_release.py').exists():gates.append(('publication-regressions',ROOT/'tools/test_release.py',['--output',str(out/'publication-regressions.json')]))
 env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLBACKEND='Agg',PYTHONHASHSEED='0')
 records=[]
 for name,script,args in gates:
  if a.gates and name not in a.gates:continue
  cmd=[sys.executable,str(script),*args];t=time.time();print('Running',name,flush=True)
  try:
   p=subprocess.run(cmd,capture_output=True,text=True,env=env,cwd=out,timeout=240)
   timed=False;code=p.returncode;stdout=p.stdout;stderr=p.stderr
  except subprocess.TimeoutExpired as e:
   timed=True;code=None;stdout=e.stdout or '';stderr=e.stderr or ''
   if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
   if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
  (out/(name+'.stdout.log')).write_text(stdout);(out/(name+'.stderr.log')).write_text(stderr)
  rec={'gate':name,'script':str(script.relative_to(ROOT)),'script_sha256':sha(script),'exit_code':code,'timed_out':timed,'elapsed_seconds':round(time.time()-t,3),'status':'PASS' if code==0 else 'FAIL','stdout_sha256':sha(out/(name+'.stdout.log')),'stderr_sha256':sha(out/(name+'.stderr.log'))}
  records.append(rec);print(name,rec['status'],rec['elapsed_seconds'],flush=True)
  if code!=0:print(stderr[-4000:],flush=True)
 report={'status':'PASS' if records and all(r['status']=='PASS' for r in records) else 'FAIL','python':sys.version,'platform':platform.platform(),'fresh_lean':False,'scope':'Named bounded computations, publication tests and authentication of inherited records only','gates':records}
 (out/'REPLAY.json').write_text(json.dumps(report,indent=2)+'\n');return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
