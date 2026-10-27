"""Replay new Lean modules from a fresh extraction using its predecessor objects."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,zipfile

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 archive=Path(sys.argv[1]).resolve();target=Path(sys.argv[2]).resolve();kit=Path(sys.argv[3]).resolve()
 target.mkdir()
 with zipfile.ZipFile(archive) as z:
  if any(n.startswith('/') or '..' in Path(n).parts for n in z.namelist()):raise ValueError('Unsafe archive path')
  z.extractall(target)
 roots=[p for p in target.iterdir() if p.is_dir()];assert len(roots)==1
 root=roots[0];sys.path.insert(0,str(root/'checks'))
 from lean_env import lean_env
 lean,env=lean_env(kit)
 result=json.loads((root/'verification.json').read_text());prov=json.loads((root/'provenance.json').read_text());new=set(prov['new_modules'])
 assert result['status']=='passed' and result['release']==prov['release']
 assert result['module_count']==len(result['modules'])==prov['predecessor_source_count']+len(new)
 assert new<={m['module'] for m in result['modules']}
 out=root/'replay_build';shutil.copytree(root/'build',out)
 for n in new:(out/'PaperX'/f'{n}.olean').unlink()
 env['LEAN_PATH']=str(out)+os.pathsep+env['LEAN_PATH'].split(os.pathsep,1)[1]
 runs=[]
 for m in result['modules']:
  n=m['module'];source=root/'lean/PaperX'/f'{n}.lean'
  assert sha(source)==m['source_sha256']
  if n not in new:
   assert sha(out/'PaperX'/f'{n}.olean')==m['olean_sha256'];continue
  dest=out/'PaperX'/f'{n}.olean';start=time.perf_counter()
  p=subprocess.run([lean,'-DwarningAsError=true','-o',str(dest),str(source)],cwd=root/'lean',env=env,capture_output=True,text=True,timeout=240)
  (target/f'{n}.log').write_text(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError(p.stdout+p.stderr)
  assert sha(dest)==m['olean_sha256'],n
  runs.append({'module':n,'exit_code':p.returncode,'seconds':time.perf_counter()-start,'source_sha256':sha(source),'olean_sha256':sha(dest),'matches_clean_build':True})
  print(n,'replay passed',flush=True)
 assert {r['module'] for r in runs}==new
 # Rerun the retained Block 22 experiment, explicitly as a predecessor regression.
 script=root/'checks/exact_local_quadratic.py';script_sha=sha(script)
 original=root/'exact_local_quadratic.json';original_sha=sha(original)
 assert original.read_bytes()==(root/'checks/local_quadratic_run/results.json').read_bytes()==(root/'checks/local_quadratic_review/results.json').read_bytes()
 regression_output=target/'predecessor_exact_local_quadratic.json'
 p=subprocess.run([sys.executable,str(script),'--output',str(regression_output)],cwd=root,capture_output=True,text=True,timeout=180)
 (target/'predecessor_exact_replay.log').write_text(p.stdout+p.stderr);assert p.returncode==0
 assert sha(script)==script_sha and sha(original)==original_sha
 assert regression_output.read_bytes()==original.read_bytes()
 regression={'status':'passed','originating_block':22,'script':'checks/exact_local_quadratic.py','script_sha256':script_sha,'result_sha256':sha(regression_output),'matches_archived_original_and_independent_review':True,'new_block_computation':False}
 report={'release':prov['release'],'status':'passed','source_payload_archive_sha256':sha(archive),'predecessor_objects_verified':len(result['modules'])-len(new),'new_module_count':len(new),'runs':runs,'predecessor_regression':regression,'scope':'All new modules recompiled from fresh extracted sources. Predecessor proof objects came solely from the extracted cumulative clean build. The retained Block 22 finite arithmetic experiment is replayed as a predecessor regression; no new bounded computation is claimed for these general and cyclotomic proofs. Final release metadata may be appended after this payload replay; all delivered production source/object hashes must remain identical.'}
 (target/'archive_replay.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':'passed','new_modules':len(runs),'predecessor_regression_matches':True}),flush=True)
if __name__=='__main__':main()
