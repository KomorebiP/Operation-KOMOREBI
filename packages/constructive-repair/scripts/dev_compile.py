from pathlib import Path
import sys, subprocess, hashlib, json, time, os
root=Path(__file__).resolve().parents[1]; p=root/'lean'; out=root/'evidence/development'
kit=Path(os.environ.get('KOMOREBI_LEAN_KIT','/mnt/data/runtime_recovery/Komorebi_Portable_Lean_4.34.0-rc2'))
for name in sys.argv[1:]:
 src=p/(name.replace('.','/')+'.lean'); i=1+len(list(out.glob('attempt_*.json')))
 base=out/f'attempt_{i:03d}_{src.stem}';base.with_suffix('.lean.txt').write_bytes(src.read_bytes())
 target=p/'.lake/build/lib/lean'/src.relative_to(p).with_suffix('.olean');target.parent.mkdir(parents=True,exist_ok=True)
 cmd=['bash',str(kit/'run.sh'),'lake','env','lean','-j1','-DwarningAsError=true','-DmaxHeartbeats=2000000','-o',str(target),str(src.relative_to(p))]
 t=time.monotonic();q=subprocess.run(cmd,cwd=p,text=True,capture_output=True,timeout=150, encoding="utf-8");log=q.stdout+q.stderr
 base.with_suffix('.log').write_text(log, encoding="utf-8");base.with_suffix('.json').write_text(json.dumps({'source':str(src.relative_to(root)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'command':cmd,'seconds':time.monotonic()-t,'returncode':q.returncode},indent=2), encoding="utf-8")
 print(name,'RC',q.returncode,'SECONDS',round(time.monotonic()-t,3));print(log)
 if q.returncode:sys.exit(q.returncode)
