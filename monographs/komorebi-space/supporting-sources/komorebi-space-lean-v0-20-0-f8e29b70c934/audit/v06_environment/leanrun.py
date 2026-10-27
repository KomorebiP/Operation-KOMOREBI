from pathlib import Path
import os,subprocess,sys,time
runtime=Path('/mnt/data/Komorebi_Portable_Lean_4.34.0-rc2'); root=Path('/mnt/data/Komorebi_Space_Lean_v0.6.0')
build=root/'.lake/replay/lib/lean';build.mkdir(parents=True,exist_ok=True)
packages=runtime/'workspace/.lake/packages'
env=dict(os.environ); env['LEAN_PATH']=':'.join(map(str,[build,Path('/mnt/data/Komorebi_Space_Lean_v0.5.0/.lake/replay/lib/lean')]+[p/'.lake/build/lib/lean' for p in sorted(packages.iterdir()) if (p/'.lake/build/lib/lean').is_dir()]))
source=sys.argv[1]; output=build/Path(source).with_suffix('.olean');output.parent.mkdir(parents=True,exist_ok=True)
t=time.monotonic(); p=subprocess.run([str(runtime/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-DautoImplicit=false','-o',str(output),source],env=env,cwd=root,capture_output=True,text=True,timeout=120)
text=p.stdout+p.stderr
log=root/'audit/v06_development'; log.mkdir(parents=True,exist_ok=True)
(log/(Path(source).stem+'_'+str(time.time_ns())+'.log')).write_text(text)
print(text);print('EXIT',p.returncode,'TIME',time.monotonic()-t);raise SystemExit(p.returncode)
