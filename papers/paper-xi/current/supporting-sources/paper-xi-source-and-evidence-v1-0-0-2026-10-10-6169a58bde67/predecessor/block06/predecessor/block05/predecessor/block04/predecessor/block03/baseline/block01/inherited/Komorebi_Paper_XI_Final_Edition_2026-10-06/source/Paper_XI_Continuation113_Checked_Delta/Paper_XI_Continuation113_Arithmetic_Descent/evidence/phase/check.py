from pathlib import Path
import os, subprocess, json, hashlib, time, sys, shutil
root=Path('/workspace/scratch/bec226d7ce4b')
proj=root/'Paper_XI_Continuation113_Arithmetic_Descent'
kit=root/'runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2'
evidence=proj/'evidence/phase'
source=proj/'formalization/PaperXI/CyclicNormalization113.lean'
objects=evidence/'objects'
base=root/'Paper_XI_Continuation112_Realization_Test/build'
env=os.environ.copy()
env['LD_PRELOAD']=str(kit/'compat/app_path.so')
env['LEAN_PATH']=':'.join(map(str,[objects,base]+sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))))
name=sys.argv[1] if len(sys.argv)>1 else 'attempt01'
snap=evidence/(name+'.lean')
shutil.copy2(source,snap)
argv=[str(kit/'toolchain/bin/lean'),'-j1','-DmaxHeartbeats=3000000','-DwarningAsError=true','-o',str(objects/'PaperXI/CyclicNormalization113.olean'),'-i',str(objects/'PaperXI/CyclicNormalization113.ilean'),str(source)]
t0=time.monotonic(); r=subprocess.run(argv,env=env,cwd=proj,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
(evidence/(name+'.log')).write_text(r.stdout)
receipt={'argv':argv,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'exit_code':r.returncode,'seconds':time.monotonic()-t0,'baseline_rebuilt':False}
(evidence/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(r.stdout);print(json.dumps(receipt,indent=2));sys.exit(r.returncode)
