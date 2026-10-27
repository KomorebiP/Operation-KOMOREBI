import subprocess,json,time,sys
from pathlib import Path
p=Path('/mnt/data/core25/runtime_recovery'); start=time.time()
cmd=[sys.executable,'-u','/mnt/data/core25/Machine_Native_Reasoning_Lean_Core24/tools/restore_runtime.py','--parts','/mnt/data/lean_parts','--out','/mnt/data/lean-compact.tar.xz','--extract-to','/mnt/data/lean_runtime']
with (p/'restore.log').open('w') as f:
 try:
  result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  code=result.returncode
 except subprocess.TimeoutExpired:
  code=124
(p/'result.json').write_text(json.dumps({'command':cmd,'returncode':code,'seconds':time.time()-start,'status':'PASS' if code==0 else 'FAIL'},indent=2))
sys.exit(code)
