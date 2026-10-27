#!/usr/bin/env python3
"""Compile the formal core with the user's pinned offline Lean kit.
No network, no native_decide, no admitted proofs. An actual compiler is required.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, re, shutil, subprocess, tempfile, time
from datetime import datetime, timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODULES=['H12Taps','H12NormAlgebra','H12OrbitObstruction','H12NormProjector','H12PacketCarries','H12NormSemigroup']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=pathlib.Path);ap.add_argument('--timeout',type=int,default=90);args=ap.parse_args()
 rt=args.runtime.resolve();binary=rt/'toolchain/bin/lean'
 if not binary.is_file():raise SystemExit('Missing compiler: '+str(binary))
 started=datetime.now(timezone.utc).isoformat();tic=time.perf_counter()
 version=subprocess.check_output([str(binary),'--version'],text=True).strip()
 if '4.34.0-rc2' not in version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:raise SystemExit('Pinned toolchain mismatch: '+version)
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
 records=[]
 with tempfile.TemporaryDirectory(prefix='h12-lean-') as tmp:
  td=pathlib.Path(tmp)
  for p in (ROOT/'formalization').glob('*.lean'):shutil.copy2(p,td/p.name)
  env['LEAN_PATH']=str(td)+':'+env['LEAN_PATH']
  for module in MODULES+['H12Audit']:
   cmd=[str(binary),'-j1','-DwarningAsError=true','-o',module+'.olean',module+'.lean']
   t=time.perf_counter();p=subprocess.run(cmd,cwd=td,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=args.timeout)
   (logdir/(module+'.log')).write_text(p.stdout)
   rec={'module':module,'command':cmd,'exit_code':p.returncode,'runtime_seconds':time.perf_counter()-t}
   records.append(rec)
   if p.returncode:raise AssertionError(module+' failed; see '+str(logdir/(module+'.log')))
  audit=(logdir/'H12Audit.log').read_text()
  found=re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]",audit)
  found += [(n,'') for n in re.findall(r"'([^']+)' does not depend on any axioms",audit)]
  if {n for n,_ in found}!=set(statements):raise AssertionError('Axiom audit coverage mismatch')
  allowed={'propext','Classical.choice','Quot.sound'}
  for name,axioms in found:
   if set(x.strip() for x in axioms.split(',') if x.strip())-allowed:raise AssertionError('Unexpected axiom for '+name+': '+axioms)
  (td/'RejectedControl.lean').write_text('module\npublic import Mathlib.Data.Int.Basic\npublic section\nexample : (0 : ℤ)=1 := by decide\n')
  cmd=[str(binary),'-j1','-DwarningAsError=true','RejectedControl.lean']
  p=subprocess.run(cmd,cwd=td,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=args.timeout)
  (logdir/'RejectedControl.log').write_text(p.stdout)
  if p.returncode==0 or 'error' not in p.stdout:raise AssertionError('False-statement negative control not rejected normally')
  negative={'exit_code':p.returncode,'assertion':'(0 : Int) = 1','expected':'compiler rejects'}
 if sources!={p.name:sha(p) for p in (ROOT/'formalization').glob('*.lean')}:raise AssertionError('Source changed during build')
 result={'started_at':started,'runtime_seconds':time.perf_counter()-tic,'lean_version':version,
 'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','theorem_count':len(statements),
 'theorems':statements,'axiom_audit':{n:a for n,a in found},'source_hashes':sources,'modules':records,
 'negative_control':negative,'scope':'Algebraic, combinatorial and explicitly conditional lemmas only; no analytic gamma or arithmetic special-value comparison formalized.'}
 (ROOT/'evidence/lean_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(f'PASS: {len(statements)} Lean theorems; all axiom dependencies audited; false statement rejected.')
if __name__=='__main__':main()
