from pathlib import Path
import zipfile,hashlib,shutil,subprocess,time,json,os
base=Path('/mnt/data'); w=base/'block29_work/current'; start=time.time()
a=base/'Komorebi_Padic_Block28_Support_Closure_Lean_Checked_2026-09-20.zip'
assert hashlib.sha256(a.read_bytes()).hexdigest()==a.with_suffix('.zip.sha256').read_text().split()[0]
with zipfile.ZipFile(a) as z:
 assert z.testzip() is None
 z.extractall(base/'block29_work/predecessor')
p=next((base/'block29_work/predecessor').iterdir());w.mkdir(parents=True,exist_ok=True)
for name in ['lean','lakefile.lean','lake-manifest.json','lean-toolchain']:
 src=p/name
 if src.is_dir():shutil.copytree(src,w/name,dirs_exist_ok=True)
 else:shutil.copy2(src,w/name)
(w/'verification').mkdir(exist_ok=True);(w/'results').mkdir(exist_ok=True)
for name in ['prepare_offline.py','run_job.py']:shutil.copy2(p/'verification'/name,w/'verification'/name)
subprocess.run(['python','verify_release.py'],cwd=p,stdout=open(w/'results/predecessor_integrity.log','w'),check=True)
for name in ['audit_support.py','audit_profiles.py']:
 (w/'verification/reference').mkdir(exist_ok=True)
 shutil.copy2(p/'verification'/name,w/'verification/reference'/name)
shutil.copytree(p/'verification/reference',w/'verification/reference',dirs_exist_ok=True)
print('predecessor restored and integrity passed',flush=True)
r=base/'runtime29';arc=r/'lean.tar.xz';h=hashlib.sha256()
with arc.open('wb') as out:
 for i in range(1,6):
  with zipfile.ZipFile(base/f'lean_compact_parts/Lean_Compact_{i:02}.zip') as z:
   with z.open(z.namelist()[0]) as src:
    while chunk:=src.read(8*1024*1024):out.write(chunk);h.update(chunk)
  print('assembled',i,flush=True)
actual=h.hexdigest();assert actual=='f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7'
print('archive sha256 verified; extracting',flush=True)
rc=subprocess.run(['bash','-c','set -o pipefail; xz -T2 -dc lean.tar.xz | tar -xf -'],cwd=r).returncode
assert rc==0
rt=r/'Komorebi_Portable_Lean_4.34.0-rc2'
(r/'RESTORE.json').write_text(json.dumps({'sha256':actual,'exit_code':rc,'seconds':time.time()-start},indent=2))
subprocess.run(['python','verification/prepare_offline.py',str(rt)],cwd=w,stdout=open(w/'results/prepare.log','w'),check=True)
env=os.environ|{'PATH':str(rt/'toolchain/bin')+':'+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1'}
print('runtime ready; baseline build',flush=True)
bs=time.time();old={str(f.relative_to(w)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (w/'lean').rglob('*.lean') if (p/f.relative_to(w)).exists()}
rc=subprocess.run(['lake','build'],cwd=w,env=env,stdout=open(w/'results/baseline_build.log','w'),stderr=subprocess.STDOUT).returncode
(w/'results/baseline_build.json').write_text(json.dumps({'exit':rc,'seconds':time.time()-bs,'predecessor_inputs_unchanged':all(hashlib.sha256((w/f).read_bytes()).hexdigest()==h for f,h in old.items()),'input_scope':'only inherited mathematical source files plus original root','predecessor_sources':old},indent=2))
print('baseline done',rc,flush=True)
