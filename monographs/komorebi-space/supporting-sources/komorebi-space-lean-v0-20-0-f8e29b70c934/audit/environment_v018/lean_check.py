from pathlib import Path
import os,subprocess,sys,json,time,hashlib
root=Path('/mnt/data/Komorebi_Space_Lean_v0.18.0')
runtime=Path('/mnt/data/runtime_v018/Komorebi_Portable_Lean_4.34.0-rc2')
packages=runtime/'workspace/.lake/packages'
build=root/'.lake/dev/lib/lean';build.mkdir(parents=True,exist_ok=True)
env=dict(os.environ)
for key in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME'): env.pop(key,None)
env['PATH']=str(runtime/'toolchain/bin')+os.pathsep+env['PATH']
env['LEAN_PATH']=os.pathsep.join(map(str,[build]+[p/'.lake/build/lib/lean' for p in sorted(packages.iterdir()) if (p/'.lake/build/lib/lean').is_dir()]))
for mod in sys.argv[1:]:
 source=f'KomorebiSpace/{mod}.lean';out=build/f'KomorebiSpace/{mod}.olean';out.parent.mkdir(exist_ok=True,parents=True)
 argv=[str(runtime/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-DautoImplicit=false','-o',str(out),source]
 stamp=time.time_ns();start=time.monotonic()
 proc=subprocess.run(argv,cwd=root,env=env,capture_output=True,text=True,timeout=120)
 log=root/f'audit/development_v018/{mod}_{stamp}.log';log.write_text(proc.stdout+proc.stderr)
 rec={'module':mod,'argv':argv,'exit_status':proc.returncode,'elapsed_seconds':time.monotonic()-start,'source_sha256':hashlib.sha256((root/source).read_bytes()).hexdigest(),'log':str(log.relative_to(root))}
 log.with_suffix('.json').write_text(json.dumps(rec,indent=2))
 print(mod,proc.returncode,round(rec['elapsed_seconds'],2),flush=True);print(proc.stdout+proc.stderr,flush=True)
 if proc.returncode: sys.exit(proc.returncode)
