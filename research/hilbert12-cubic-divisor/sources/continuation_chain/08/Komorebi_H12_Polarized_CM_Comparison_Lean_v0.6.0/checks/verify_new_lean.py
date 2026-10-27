#!/usr/bin/env python3
"""Fresh, bounded verification of this block and its one inherited dependency.
Does not claim a successful replay of the entire inherited 154-theorem project.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
NEW=['H12CMNormCertificate','H12LineNorms','H12PolarizedReality']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=Path);a=ap.parse_args();rt=a.runtime.resolve();binary=rt/'toolchain/bin/lean'
 version=subprocess.check_output([str(binary),'--version'],text=True).strip();assert '4.34.0-rc2' in version
 pins=json.loads((rt/'workspace/lake-manifest.json').read_text());assert [p['rev'] for p in pins['packages'] if p['name']=='mathlib']==['aeb72f1e9981b6d35b426b16dca7759be3e7ba06']
 build=ROOT/'.new-lean-check';logs=ROOT/'evidence/new_lean';logs.mkdir(parents=True,exist_ok=True)
 if build.exists():shutil.rmtree(build)
 build.mkdir();mods=['H12CubicBranch']+NEW;names=[];sources={}
 for mod in mods:
  p=ROOT/'formalization'/f'{mod}.lean';s=p.read_text();code=re.sub(r'/\-.*?\-/','',s,flags=re.S);code=re.sub(r'--[^\n]*','',code)
  assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',code)
  shutil.copy2(p,build/p.name);sources[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
  if mod in NEW:
   ns=re.search(r'^namespace (\S+)',s,re.M).group(1);names += [ns+'.'+n for n in re.findall(r'^theorem (\w+)',s,re.M)]
 audit='module\n'+''.join(f'public import {m}\n' for m in NEW)+'public section\n'+''.join(f'#print axioms {n}\n' for n in names)
 (build/'NewAudit.lean').write_text(audit);(ROOT/'formalization/NewAudit.lean').write_text(audit)
 env=os.environ.copy();env['LEAN_PATH']=str(build)+':'+':'.join(str(p/'.lake/build/lib/lean') for p in (rt/'workspace/.lake/packages').iterdir() if p.is_dir())
 start=datetime.now(timezone.utc).isoformat();tic=time.monotonic();records=[]
 for mod in mods+['NewAudit']:
  cmd=[str(binary),'-j1','-DwarningAsError=true','-o',mod+'.olean',mod+'.lean'];t=time.monotonic();r=subprocess.run(cmd,cwd=build,env=env,capture_output=True,text=True,timeout=60)
  out=r.stdout+r.stderr;(logs/f'{mod}.log').write_text(out);records.append({'module':mod,'command':cmd,'exit_status':r.returncode,'seconds':time.monotonic()-t})
  print(mod,r.returncode,round(records[-1]['seconds'],3),flush=True)
  if r.returncode:raise RuntimeError(out)
 text=(logs/'NewAudit.log').read_text();found=re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]",text)+[(n,'') for n in re.findall(r"'([^']+)' does not depend on any axioms",text)]
 assert set(names)=={n for n,d in found}
 for n,d in found:assert {x.strip() for x in d.split(',') if x.strip()}<={'propext','Classical.choice','Quot.sound'},n
 (build/'FalseControl.lean').write_text('module\npublic import Mathlib.Data.Int.Basic\npublic section\nexample : (0 : ℤ)=1 := by decide\n')
 r=subprocess.run([str(binary),'-j1','-DwarningAsError=true','FalseControl.lean'],cwd=build,env=env,capture_output=True,text=True,timeout=30);out=r.stdout+r.stderr;(logs/'FalseControl.log').write_text(out);assert r.returncode!=0 and 'error' in out
 rec={'started_at':start,'seconds':time.monotonic()-tic,'exit_status':0,'new_theorem_count':len(names),'new_theorems':names,'axiom_audit':dict(found),'compiled_modules':records,'source_hashes':sources,'lean_version':version,'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','negative_control_exit_status':r.returncode,'scope':'Fresh verification of 18 new theorems and recompiled inherited H12CubicBranch dependency. Full inherited 154-theorem replay did not finish and is not claimed.'}
 (ROOT/'evidence/new_lean_results.json').write_text(json.dumps(rec,indent=2)+'\n');print('PASS',len(names),'new theorems, axiom audit, false control rejection')
if __name__=='__main__':main()
