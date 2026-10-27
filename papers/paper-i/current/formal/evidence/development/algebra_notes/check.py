import os,pathlib,subprocess,sys
r=pathlib.Path('/workspace/scratch/2e8d212e9ca7/runtime11/Komorebi_Portable_Lean_4.34.0-rc2')
b=pathlib.Path('/workspace/scratch/9f53d520971c/paper1_work/block08/Komorebi_Paper_I_Completion_Block08_v0.8.0_2026-10-12')
e=os.environ.copy();e['LD_PRELOAD']=str(r/'compat/app_path.so');e['LEAN_PATH']=':'.join(str(p) for p in [b/'evidence/final_audit/inherited_objects',b/'evidence/objects',*r.glob('workspace/.lake/packages/*/.lake/build/lib/lean'),pathlib.Path('/workspace/scratch/9f53d520971c/release_work/formal')])
args=sys.argv[1:];p=subprocess.run([str(r/'toolchain/bin/lean'),*args],env=e);sys.exit(p.returncode)
