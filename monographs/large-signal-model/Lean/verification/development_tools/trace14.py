import os,sys,json,time,subprocess,pathlib
root=pathlib.Path('/workspace/scratch/2e8d212e9ca7/work14/Komorebi_LSM_Lean_0.14.0')
kit=pathlib.Path('/workspace/scratch/2e8d212e9ca7/runtime11/Komorebi_Portable_Lean_4.34.0-rc2')
env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so');env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env['PATH']
pkgs=json.loads((root/'lake-manifest.json').read_text())['packages'];build=root/'.build/lib/lean'
build.mkdir(parents=True,exist_ok=True)
env['LEAN_PATH']=os.pathsep.join([str(build)]+[str(kit/'workspace/.lake/packages'/p['name']/'.lake/build/lib/lean') for p in pkgs])
logs=root/'verification/development_block14';logs.mkdir(parents=True,exist_ok=True)
for arg in sys.argv[1:]:
 p=root/arg;out=build/p.relative_to(root).with_suffix('.olean');out.parent.mkdir(parents=True,exist_ok=True)
 idx=max([int(p.name[:4]) for p in logs.iterdir() if p.name[:4].isdigit()]+[0])+1;(logs/f'{idx:04}_{p.name}').write_bytes(p.read_bytes())
 cmd=['strace','-f','-e','trace=openat,creat,write,rename','-o',str(logs/'tail_write_trace.log'),str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-o',str(out),str(p)];start=time.time()
 r=subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True,timeout=180)
 (logs/f'{idx:04}.json').write_text(json.dumps({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'seconds':time.time()-start},indent=2))
 print(p.name,r.returncode,r.stdout,r.stderr,flush=True)
 if r.returncode:sys.exit(r.returncode)
