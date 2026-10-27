#!/usr/bin/env python3
"""Portable replay with pinned upstream runtime; optionally recheck selected sources."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--selected',action='store_true');ap.add_argument('--cache',type=Path);a=ap.parse_args()
 state=json.loads((ROOT/'v08_evidence/COLD_STATE.json').read_text());rt=a.runtime.resolve()
 for x in state['inputs']:assert sha(ROOT/x['path'])==x['sha256'],x
 assert sha(rt/'toolchain/bin/lean')==state['environment']['lean_sha256']
 if a.selected:
  assert a.cache is not None,'selected source recheck needs a byte-verified previous cache'
  for x in state['artifacts']:
   old=Path(x['path']);f=a.cache/old.relative_to(Path(state['build']));assert sha(f)==x['sha256'],str(f)
  modules=['BoundedBezout','EuclidCost','BoundedInsertion','EchelonPeakCore','EchelonTemporaryBounds','BoundedDiscovery','BoundedArithmeticExamples','BoundedCase201','BoundedCase202']
 else:modules=state['modules']
 build=Path(tempfile.mkdtemp(prefix='komorebi-model08-recheck-'));logs=a.output.parent/(a.output.stem+'_logs');logs.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['LEAN_PATH']=':'.join([str(build)]+([str(a.cache)] if a.selected else [])+[str(p) for p in sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]);env['OMP_NUM_THREADS']='1'
 plan=[]
 for m in modules:
  out=build/(m+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
  plan.append((m,[str(rt/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-o',str(out),m+'.lean'],True))
 # Full mode replays all original axiom groups. Selected mode rechecks controls.
 for item in state['plan']:
  if item.get('axioms') and not a.selected:
   filename=Path(item['argv'][-1]).name;plan.append((item['name'],[str(rt/'toolchain/bin/lean'),'-j1',str(ROOT/'v08_checks/axioms'/filename)],True))
  if item['name'].startswith('control_'):
   filename=Path(item['argv'][-1]).name;plan.append((item['name'],[str(rt/'toolchain/bin/lean'),'-j1','-DwarningAsError=true',str(ROOT/'v08_checks/controls'/filename)],item['expect']))
 tasks=[]
 for name,argv,expected in plan:
  log=logs/(name.replace('/','_')+'.log');start=time.monotonic()
  with log.open('w') as f:
   try:p=subprocess.run(argv,cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=110);rc=p.returncode;timed=False
   except subprocess.TimeoutExpired:rc=124;timed=True
  txt=log.read_text();ok=(rc==0 if expected else rc!=0 and 'error:' in txt) and not timed
  if not expected and any(x in txt.lower() for x in ['unknown module','no such file','does not exist','heartbeats','out of memory']):ok=False
  tasks.append({'name':name,'argv':argv,'exit_code':rc,'expected_success':expected,'passed':ok,'timed_out':timed,'seconds':time.monotonic()-start,'log':str(log),'sha256':sha(log)})
  a.output.write_text(json.dumps({'status':'IN_PROGRESS' if ok else 'FAIL','selected':a.selected,'build':str(build),'tasks':tasks},indent=2)+'\n')
  print(name,ok,flush=True)
  if not ok:raise RuntimeError(txt[-4000:])
 for x in state['inputs']:assert sha(ROOT/x['path'])==x['sha256'],x
 a.output.write_text(json.dumps({'status':'PASS','selected':a.selected,'modules':len(modules),'tasks':tasks,'scope':'Selected fresh source checks using hash-matched supporting cache' if a.selected else 'Full fresh local rebuild using pinned upstream cache','all_inputs_unchanged':True,'build':str(build)},indent=2)+'\n')
if __name__=='__main__':main()
