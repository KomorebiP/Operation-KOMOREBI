from pathlib import Path
import datetime,hashlib,json,os,subprocess,time
base=Path('/workspace/scratch/6a8ff46cf015/physics_next')
project=base/'work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
source=project/'KomorebiPhysics/Relativistic3DCenteredResolvent.lean'
attempts=base/'attempts/resolvent'
number=1
while (attempts/f'run_{number:03}.json').exists(): number+=1
stem=attempts/f'run_{number:03}'
snapshot=stem.with_suffix('.lean'); snapshot.write_bytes(source.read_bytes())
kit=base/'runtime/Komorebi_Portable_Lean_4.34.0-rc2'
env=os.environ.copy(); env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
env['LD_PRELOAD']=str(kit/'compat/app_path.so')
for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME'): env.pop(k,None)
obj=project/'.lake/build/lib/lean/KomorebiPhysics/Relativistic3DCenteredResolvent.olean'
argv=['lake','env','lean','-j1','-DwarningAsError=true','-o',str(obj),str(source.relative_to(project))]
started=datetime.datetime.now(datetime.timezone.utc).isoformat(); t=time.monotonic()
with stem.with_suffix('.log').open('w') as out:
 p=subprocess.run(argv,cwd=project,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=600)
r={'started_utc':started,'argv':argv,'returncode':p.returncode,'seconds':time.monotonic()-t,'source_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(stem.with_suffix('.log').read_bytes()).hexdigest()}
if p.returncode==0:r['object_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
stem.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r));raise SystemExit(p.returncode)
