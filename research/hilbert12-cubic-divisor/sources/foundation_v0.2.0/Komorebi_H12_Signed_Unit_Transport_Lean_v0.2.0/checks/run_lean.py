#!/usr/bin/env python3
"""Pinned offline Lean build, split into synchronous stages with source integrity.
Stage 1 starts a fresh isolated directory and builds the inherited six modules.
Stage 2 authenticates stage 1, builds the three new modules, then audits all 83.
No network, no admitted proofs, and no native_decide. Compiler must be supplied.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, re, shutil, signal, subprocess, time
from datetime import datetime, timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODULES=['H12Taps','H12NormAlgebra','H12OrbitObstruction','H12NormProjector','H12PacketCarries','H12NormSemigroup','H12SignedGeometry','H12SignedAlgebra','H12ThreeStepTransport']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def execute(cmd,**kwargs):
 timeout=kwargs.pop('timeout')
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True,**kwargs)
 try: out,_=p.communicate(timeout=timeout)
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGKILL);out,_=p.communicate()
  raise TimeoutError(f'Command exceeded {timeout}s: {cmd}\n{out}')
 return p.returncode,out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=pathlib.Path);ap.add_argument('--timeout',type=int,default=120);ap.add_argument('--part',type=int,choices=[1,2],required=True);args=ap.parse_args()
 rt=args.runtime.resolve();binary=rt/'toolchain/bin/lean'
 if not binary.is_file():raise SystemExit('Missing compiler: '+str(binary))
 started=datetime.now(timezone.utc).isoformat();tic=time.perf_counter()
 version=subprocess.check_output([str(binary),'--version'],text=True).strip()
 if '4.34.0-rc2' not in version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:raise SystemExit('Pinned toolchain mismatch: '+version)
 lake_manifest=json.loads((rt/'workspace/lake-manifest.json').read_text())
 mathlib=[p for p in lake_manifest['packages'] if p['name']=='mathlib']
 if len(mathlib)!=1 or mathlib[0]['rev']!='aeb72f1e9981b6d35b426b16dca7759be3e7ba06':raise SystemExit('Mathlib pin mismatch')
 raw=subprocess.check_output(['bash',str(rt/'run.sh'),'lake','env','/usr/bin/env','-0'],cwd=rt/'workspace',timeout=args.timeout)
 env=os.environ.copy();env.update(dict(v.decode().split('=',1) for v in raw.split(b'\0') if v))
 env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 sources={p.name:sha(p) for p in (ROOT/'formalization').glob('*.lean')}
 statements=[]
 for module in MODULES:
  text=(ROOT/'formalization'/f'{module}.lean').read_text()
  code=re.sub(r'/\-.*?\-/','',text,flags=re.S);code=re.sub(r'--[^\n]*','',code)
  if re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',code):raise AssertionError('Prohibited proof construct in '+module)
  ns=re.search(r'^namespace (\S+)',text,re.M).group(1)
  statements += [ns+'.'+n for n in re.findall(r'^theorem (\w+)',text,re.M)]
 logdir=ROOT/'evidence/lean';logdir.mkdir(parents=True,exist_ok=True)
 td=ROOT/'.lean-check';state=ROOT/'evidence/lean_stage1.json'
 if args.part==1:
  if td.exists():shutil.rmtree(td)
  td.mkdir()
  for p in (ROOT/'formalization').glob('*.lean'):shutil.copy2(p,td/p.name)
  records=[];todo=MODULES[:6]
 else:
  if not state.is_file() or not td.is_dir():raise SystemExit('Run part 1 first')
  previous=json.loads(state.read_text())
  if previous['source_hashes']!=sources:raise AssertionError('Sources changed since stage 1; restart')
  for name,h in previous['compiled_hashes'].items():
   if not (td/name).is_file() or sha(td/name)!=h:raise AssertionError('Stage-1 compiled object changed')
  records=previous['modules'];todo=MODULES[6:]+['H12Audit']
 env['LEAN_PATH']=str(td)+':'+env['LEAN_PATH']
 for module in todo:
  cmd=[str(binary),'-j1','-DwarningAsError=true','-o',module+'.olean',module+'.lean']
  t=time.perf_counter();ret,out=execute(cmd,cwd=td,env=env,timeout=args.timeout)
  (logdir/(module+'.log')).write_text(out)
  rec={'module':module,'command':cmd,'exit_code':ret,'runtime_seconds':time.perf_counter()-t};records.append(rec)
  print(module,ret,round(rec['runtime_seconds'],2),flush=True)
  if ret:raise AssertionError(module+' failed; see '+str(logdir/(module+'.log')))
 if sources!={p.name:sha(p) for p in (ROOT/'formalization').glob('*.lean')}:raise AssertionError('Source changed during build')
 if args.part==1:
  state.write_text(json.dumps({'started_at':started,'runtime_seconds':time.perf_counter()-tic,'source_hashes':sources,'compiled_hashes':{p.name:sha(p) for p in td.glob('*.olean')},'modules':records},indent=2)+'\n')
  print('PASS stage 1: inherited modules; no whole-project verdict until stage 2.');return
 audit=(logdir/'H12Audit.log').read_text()
 found=re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]",audit)
 found += [(n,'') for n in re.findall(r"'([^']+)' does not depend on any axioms",audit)]
 if {n for n,_ in found}!=set(statements):raise AssertionError('Axiom audit coverage mismatch')
 allowed={'propext','Classical.choice','Quot.sound'}
 for name,axioms in found:
  if set(x.strip() for x in axioms.split(',') if x.strip())-allowed:raise AssertionError('Unexpected axiom for '+name+': '+axioms)
 (td/'RejectedControl.lean').write_text('module\npublic import Mathlib.Data.Int.Basic\npublic section\nexample : (0 : ℤ)=1 := by decide\n')
 cmd=[str(binary),'-j1','-DwarningAsError=true','RejectedControl.lean']
 ret,out=execute(cmd,cwd=td,env=env,timeout=args.timeout)
 (logdir/'RejectedControl.log').write_text(out)
 if ret==0 or 'error' not in out:raise AssertionError('False-statement negative control not rejected normally')
 negative={'exit_code':ret,'assertion':'(0 : Int) = 1','expected':'compiler rejects'}
 result={'started_at':previous['started_at'],'runtime_seconds':previous['runtime_seconds']+time.perf_counter()-tic,'lean_version':version,
 'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','theorem_count':len(statements),
 'theorems':statements,'axiom_audit':{n:a for n,a in found},'source_hashes':sources,'modules':records,
 'negative_control':negative,'scope':'Algebraic, combinatorial and explicitly conditional lemmas only; no analytic gamma or arithmetic special-value comparison formalized.'}
 (ROOT/'evidence/lean_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(f'PASS: {len(statements)} Lean theorems; all axiom dependencies audited; false statement rejected.')
if __name__=='__main__':main()
