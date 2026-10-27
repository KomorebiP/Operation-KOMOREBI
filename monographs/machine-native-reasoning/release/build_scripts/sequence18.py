"""Track the second complete proof gate only after the first supervisor ends successfully."""
from pathlib import Path
import json, subprocess, time, sys, shutil
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
F=Path('/mnt/data/core25/fresh18_source')
RT=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2')
out=R/'evidence/SEQUENCE18.json';record={'status':'WAITING_PRIMARY','started_at':time.time()}
def save():out.write_text(json.dumps(record,indent=2)+'\n')
save()
try:
 deadline=time.monotonic()+1800
 while not (R/'evidence/final18_supervisor.json').exists():
  if time.monotonic()>deadline:raise TimeoutError('Primary receipt wait exceeded limit')
  time.sleep(2)
 a=json.loads((R/'evidence/final18_supervisor.json').read_text());b=json.loads((R/'evidence/final18/report.json').read_text())
 if a['status']!='completed' or a['exit_code']!=0 or b['status']!='PASS':raise RuntimeError('Primary gate did not pass; no extracted gate started')
 record.update(status='FRESH_RUNNING',primary_exit_code=a['exit_code'],fresh_started_at=time.time());save()
 cmd=[sys.executable,str(F/'scripts/supervise.py'),'--runtime',str(RT),'--out','evidence/fresh18','--whole-timeout','1800']
 record['fresh_argv']=cmd;save()
 with (R/'evidence/fresh18_launcher.log').open('wb') as log:
  p=subprocess.run(cmd,cwd=F,stdout=log,stderr=subprocess.STDOUT,timeout=1860)
 record['fresh_launcher_exit_code']=p.returncode
 # Preserve all outcomes, including a failed gate, before checking acceptance.
 if (F/'evidence').exists():
  for q in (F/'evidence').iterdir():
   target=R/'evidence'/q.name
   if q.is_dir():shutil.copytree(q,target,dirs_exist_ok=True)
   else:shutil.copy2(q,target)
 if p.returncode:raise RuntimeError('Extracted-source gate failed')
 record['status']='COMPARING';save()
 cmd=[sys.executable,str(R/'scripts/compare_rebuild.py'),'--final',str(R/'evidence/final18'),'--fresh',str(R/'evidence/fresh18'),'--snapshot',str(R/'evidence/CORE25_FROZEN_SOURCE.zip'),'--out',str(R/'evidence/CORE25_COMPARISON.json')]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=45)
 (R/'evidence/CORE25_COMPARISON.log').write_text(p.stdout+p.stderr)
 record['comparison_exit_code']=p.returncode
 if p.returncode:raise RuntimeError('Completed runs did not pass comparison')
 record['status']='PASS'
except Exception as exc:
 record['status']='FAIL';record['failure']=f'{type(exc).__name__}: {exc}'
record['ended_at']=time.time();save();print(record)
sys.exit(0 if record['status']=='PASS' else 1)
