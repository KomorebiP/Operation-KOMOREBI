from pathlib import Path
import subprocess,sys,os,json,time,hashlib,traceback
root=Path(__file__).resolve().parents[1]
label=sys.argv[1]; cmd=sys.argv[2:]
env=os.environ.copy();runtime=env.get('KOMOREBI_LEAN_RUNTIME');env['PATH']=(str(Path(runtime)/'toolchain/bin')+os.pathsep if runtime else '')+env['PATH'];env['PYTHONDONTWRITEBYTECODE']='1'
def snapshot():
 paths=sorted(list((root/'lean').rglob('*.lean'))+list((root/'verification').rglob('*.lean'))+list((root/'verification').rglob('*.py'))+[root/f for f in ['lakefile.lean','lake-manifest.json','lean-toolchain']])
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
start=time.time();before=snapshot(); status='completed';exit=-1
try:
 with (root/'results'/f'{label}.log').open('w') as log:
  c=subprocess.run(cmd,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 exit=c.returncode; status='completed' if exit==0 else 'failed'
except subprocess.TimeoutExpired: status='timeout';exit=124
except Exception as e: status='launch-failed';(root/'results'/f'{label}.log').write_text(traceback.format_exc())
after=snapshot()
(root/'results'/f'{label}.json').write_text(json.dumps({'command':cmd,'started_epoch':start,'seconds':time.time()-start,'exit':exit,'status':status,'inputs_unchanged':before==after,'inputs_before':before,'inputs_after':after},indent=2))
print(label,exit,time.time()-start,flush=True)
