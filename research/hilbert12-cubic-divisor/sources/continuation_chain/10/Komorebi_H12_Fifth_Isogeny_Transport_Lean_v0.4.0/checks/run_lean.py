#!/usr/bin/env python3
"""Pinned clean Lean verification in four synchronous stages, with source hashes."""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,shutil,signal,subprocess,time
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODULES=['H12Taps','H12NormAlgebra','H12OrbitObstruction','H12NormProjector','H12PacketCarries','H12NormSemigroup','H12SignedGeometry','H12SignedAlgebra','H12ThreeStepTransport','H12CoprimeNormalization','H12FifthTorsionAlgebra','H12CanonicalTheta','H12FifthIsogeny','H12TateMarking','H12FifthModuli']
PARTS={1:MODULES[:6],2:MODULES[6:9],3:MODULES[9:12],4:MODULES[12:]+['H12Audit']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def execute(cmd,**kwargs):
 timeout=kwargs.pop('timeout');p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True,**kwargs)
 try:out,_=p.communicate(timeout=timeout)
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGKILL);out,_=p.communicate();raise TimeoutError(f'{cmd}: {out}')
 return p.returncode,out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=pathlib.Path);ap.add_argument('--part',required=True,type=int,choices=[1,2,3,4]);ap.add_argument('--timeout',default=120,type=int);a=ap.parse_args()
 rt=a.runtime.resolve();binary=rt/'toolchain/bin/lean';started=datetime.now(timezone.utc).isoformat();tic=time.perf_counter()
 version=subprocess.check_output([str(binary),'--version'],text=True).strip()
 assert '4.34.0-rc2' in version and '6a10ac8c22beadecabdbb0919c2b50214762f91d' in version
 pins=json.loads((rt/'workspace/lake-manifest.json').read_text());assert [p['rev'] for p in pins['packages'] if p['name']=='mathlib']==['aeb72f1e9981b6d35b426b16dca7759be3e7ba06']
 raw=subprocess.check_output(['bash',str(rt/'run.sh'),'lake','env','/usr/bin/env','-0'],cwd=rt/'workspace',timeout=a.timeout)
 env=os.environ.copy();env.update(dict(v.decode().split('=',1) for v in raw.split(b'\0') if v));env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 src={p.name:sha(p) for p in (ROOT/'formalization').glob('*.lean')};names=[]
 for mod in MODULES:
  txt=(ROOT/'formalization'/f'{mod}.lean').read_text();code=re.sub(r'/\-.*?\-/','',txt,flags=re.S);code=re.sub(r'--[^\n]*','',code)
  assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',code),mod
  ns=re.search(r'^namespace (\S+)',txt,re.M).group(1);names.extend(ns+'.'+n for n in re.findall(r'^theorem (\w+)',txt,re.M))
 build=ROOT/'.lean-check';logs=ROOT/'evidence/lean';logs.mkdir(parents=True,exist_ok=True)
 if a.part==1:
  if build.exists():shutil.rmtree(build)
  build.mkdir()
  for p in (ROOT/'formalization').glob('*.lean'):shutil.copy2(p,build/p.name)
  records=[];elapsed=0
 else:
  old=json.loads((ROOT/f'evidence/lean_stage{a.part-1}.json').read_text());assert old['source_hashes']==src
  for n,h in old['compiled_hashes'].items():assert sha(build/n)==h
  records=old['modules'];elapsed=old['runtime_seconds'];started=old['started_at']
 env['LEAN_PATH']=str(build)+':'+env['LEAN_PATH']
 for mod in PARTS[a.part]:
  cmd=[str(binary),'-j1','-DwarningAsError=true','-o',mod+'.olean',mod+'.lean'];t=time.perf_counter();ret,out=execute(cmd,cwd=build,env=env,timeout=a.timeout);(logs/(mod+'.log')).write_text(out)
  r={'module':mod,'command':cmd,'exit_code':ret,'runtime_seconds':time.perf_counter()-t};records.append(r);print(mod,ret,round(r['runtime_seconds'],2),flush=True)
  if ret:raise RuntimeError('Compilation failed: '+mod+'\n'+out)
 assert src=={p.name:sha(p) for p in (ROOT/'formalization').glob('*.lean')}
 record={'started_at':started,'runtime_seconds':elapsed+time.perf_counter()-tic,'source_hashes':src,'compiled_hashes':{p.name:sha(p) for p in build.glob('*.olean')},'modules':records}
 if a.part<4:
  (ROOT/f'evidence/lean_stage{a.part}.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS stage',a.part,'(not a whole-project verdict)');return
 audit=(logs/'H12Audit.log').read_text();found=re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]",audit);found +=[(n,'') for n in re.findall(r"'([^']+)' does not depend on any axioms",audit)]
 assert {n for n,_ in found}==set(names),'Audit coverage'
 for name,deps in found:assert set(x.strip() for x in deps.split(',') if x.strip())<={'propext','Classical.choice','Quot.sound'},name
 (build/'RejectedControl.lean').write_text('module\npublic import Mathlib.Data.Int.Basic\npublic section\nexample : (0 : ℤ)=1 := by decide\n')
 ret,out=execute([str(binary),'-j1','-DwarningAsError=true','RejectedControl.lean'],cwd=build,env=env,timeout=a.timeout);(logs/'RejectedControl.log').write_text(out);assert ret!=0 and 'error' in out
 record.update(theorem_count=len(names),theorems=names,axiom_audit=dict(found),lean_version=version,mathlib_revision='aeb72f1e9981b6d35b426b16dca7759be3e7ba06',negative_control={'exit_code':ret,'assertion':'(0 : Int) = 1','expected':'rejected'},scope='Explicit fifth-isogeny field/polynomial identities, generator re-marking, moduli involution and inherited algebra. Analytic uniformization, differentiation, morphism/degree interpretation and gamma-arithmetic equality not formalized.')
 record['runtime_seconds']=elapsed+time.perf_counter()-tic
 (ROOT/'evidence/lean_results.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS',len(names),'theorems, full axiom audit, rejected false statement')
if __name__=='__main__':main()
