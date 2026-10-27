from pathlib import Path
import os,subprocess,time,json,hashlib
root=Path(__file__).resolve().parents[2]
base=root.parent/'Paper_XI_Continuation112_Realization_Test'
kit=root.parent/'runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2'
module='CyclicDefect113'
source=root/'formalization/PaperXI'/f'{module}.lean'
out=root/'evidence/equivariant'
n=len(list(out.glob(f'{module}_attempt*.json')))+1
stem=out/f'{module}_attempt{n:02}'
stem.with_suffix('.lean').write_bytes(source.read_bytes())
env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so');env['PATH']=str(kit/'toolchain/bin')+':'+env['PATH']
env['LEAN_PATH']=':'.join(map(str,[out/'objects',*sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]))
obj=out/'objects/PaperXI'/module
argv=[str(kit/'toolchain/bin/lean'),'-j1','-DmaxHeartbeats=3000000','-DwarningAsError=true','-o',str(obj.with_suffix('.olean')),'-i',str(obj.with_suffix('.ilean')),str(source)]
t=time.monotonic()
try:
 r=subprocess.run(argv,cwd=root,env=env,capture_output=True,text=True,timeout=120); rc,log=r.returncode,r.stdout+r.stderr
except subprocess.TimeoutExpired as e: rc,log=124,str(e)
stem.with_suffix('.log').write_text(log)
record={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'argv':argv,'base112_sha256':'4df3bff07c05985e302d5e9f4104de8f6374c17ca695b1e2e451432572272ae5','exit_code':rc,'seconds':time.monotonic()-t,'baseline_rebuilt':False}
stem.with_suffix('.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));print(log)
raise SystemExit(rc)
