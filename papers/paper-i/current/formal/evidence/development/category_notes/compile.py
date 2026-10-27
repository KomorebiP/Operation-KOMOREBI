import pathlib, os, subprocess, sys
root=pathlib.Path('/workspace/scratch/9f53d520971c')
kit=pathlib.Path('/workspace/scratch/2e8d212e9ca7/runtime11/Komorebi_Portable_Lean_4.34.0-rc2')
base=root/'paper1_work/block08/Komorebi_Paper_I_Completion_Block08_v0.8.0_2026-10-12'
paths=[root/'release_work/formal', base/'evidence/final_audit/inherited_objects',base/'evidence/fresh_main/objects']
paths+=list((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env=dict(os.environ,LEAN_PATH=':'.join(map(str,paths)),LD_PRELOAD=str(kit/'compat/app_path.so'))
name=sys.argv[1]
p=root/'release_work/formal'/name
log=root/'release_work/category_notes'/(p.stem+'.log')
cmd=[str(kit/'toolchain/bin/lean'),'-DwarningAsError=true','-o',str(p.with_suffix('.olean')),str(p)]
p1=subprocess.run(cmd,cwd=root/'release_work/formal',env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
log.write_text(p1.stdout)
print(p1.stdout)
sys.exit(p1.returncode)
