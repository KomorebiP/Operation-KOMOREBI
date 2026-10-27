import pathlib,subprocess,os,json,hashlib,time,sys
root=pathlib.Path('/workspace/scratch/6a8ff46cf015/mnr_work/Machine_Native_Reasoning_Lean_Core25');rt=pathlib.Path('/workspace/scratch/6a8ff46cf015/mnr_runtime/Komorebi_Portable_Lean_4.34.0-rc2');obj=pathlib.Path('/workspace/scratch/6a8ff46cf015/mnr_occupancy_dev');env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[obj]+sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))));env['LEAN_NUM_THREADS']='1';env['LD_PRELOAD']=str(rt/'compat/app_path.so')
for n in sys.argv[1:]:
 src=root/'MachineTheory'/f'{n}.lean';out=obj/'MachineTheory'/f'{n}.olean';cmd=[str(rt/'toolchain/bin/lean'),'-j1','-M4096','-DwarningAsError=true','-o',str(out),str(src.relative_to(root))]
 t=time.monotonic();r=subprocess.run(cmd,cwd=root,env=env,text=True,capture_output=True,timeout=60);k=len(list(obj.glob('attempt_*.json')))+1
 (obj/f'attempt_{k:03}.json').write_text(json.dumps({'module':n,'command':cmd,'lean_path':env['LEAN_PATH'],'ld_preload':env['LD_PRELOAD'],'exit_code':r.returncode,'seconds':time.monotonic()-t,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':r.stdout+r.stderr},indent=2));print(n,r.returncode,flush=True);print(r.stdout+r.stderr,flush=True)
 if r.returncode:sys.exit(r.returncode)
