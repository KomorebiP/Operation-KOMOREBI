#!/usr/bin/env python3
"""Recompile the new generic chain, examples and final case batch in a fresh directory.

The existing dependency cache must match the completed audit's artifact hashes.
This is a selected fresh-source recheck, NOT a second complete cold rebuild.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 s=json.loads((ROOT/'evidence/cold/STATE.json').read_text());assert s['status']=='PASS'
 for x in s['inputs']:assert sha(ROOT/x['path'])==x['sha256'],x
 old=Path(s['build'])
 for x in s['artifacts']:
  rel=Path(x['path']).relative_to(old);assert sha(a.cache/rel)==x['sha256'],rel
 lean=a.runtime/'toolchain/bin/lean';assert sha(lean)==s['environment']['lean_sha256']
 ml=a.runtime/'workspace/.lake/packages/mathlib';assert (ml/'.git/HEAD').read_text().strip()==s['environment']['mathlib_commit']
 out=Path(tempfile.mkdtemp(prefix='komorebi-model09-recheck-',dir='/mnt/data'))
 env=os.environ.copy();env['LEAN_PATH']=':'.join([str(out),str(a.cache)]+[str(x) for x in sorted((a.runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]);env['OMP_NUM_THREADS']='1'
 start=datetime.now(timezone.utc).isoformat();records=[]
 tasks=[]
 for m in ['CostedPrimitives','CostedLattice','CostedDiscovery','CostedBounds','CostedExamples','CostedComputed16']:
  tasks.append((m,[str(lean),'-j1','-DwarningAsError=true','-o',str(out/(m+'.olean')),m+'.lean'],True))
 for t in s['tasks']:
  if t['name'].startswith('control_'):
   source=ROOT/'checks/controls'/(t['name'].removeprefix('control_')+'.lean')
   tasks.append((t['name'],[str(lean),'-j1','-DwarningAsError=true',str(source)],t['expected_success']))
 report={'status':'IN_PROGRESS','started_at':start,'scope':'Six fresh-source module builds (four generic, examples, cases 192..202) and eight controls; hash-matched inherited local and pinned Mathlib cache reused. Not a second complete 203-case cold build.','build':str(out),'tasks':records}
 for name,cmd,expected in tasks:
  log=out/(name+'.log');t0=time.monotonic()
  with log.open('w') as f:
   try:rc=subprocess.run(cmd,cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120).returncode;timed=False
   except subprocess.TimeoutExpired:rc=124;timed=True
  text=log.read_text();ok=(rc==0 if expected else rc!=0 and 'error:' in text)
  if timed or any(x in text.lower() for x in ['unknown module','no such file','heartbeats','out of memory']):ok=False
  rec={'name':name,'argv':cmd,'exit_code':rc,'expected_success':expected,'timed_out':timed,'passed':ok,'seconds':time.monotonic()-t0,'log':str(log),'log_sha256':sha(log)};records.append(rec)
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(name,ok,round(rec['seconds'],3),flush=True)
  if not ok:report['status']='FAIL';a.output.write_text(json.dumps(report,indent=2)+'\n');raise RuntimeError(text[-6000:])
 for x in s['inputs']:assert sha(ROOT/x['path'])==x['sha256']
 report['status']='PASS';report['finished_at']=datetime.now(timezone.utc).isoformat();report['all_inputs_unchanged']=True;a.output.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
