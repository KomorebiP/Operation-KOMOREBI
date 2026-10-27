from pathlib import Path
import json,os,subprocess,sys,time
r=Path(Path('/mnt/data/work04/root.txt').read_text().strip());kit=Path('/mnt/data/runtime/Komorebi_Portable_Lean_4.34.0-rc2');base=r/'evidence/baseline_fresh';out=r/'evidence/extension_fresh';record=r/'evidence/extension_process.json'
cmd=['bash',str(kit/'run.sh'),'lake','-d',str(kit/'workspace'),'env','python3',str(r/'scripts/verify_block04.py'),'--root',str(r),'--kit',str(kit),'--baseline',str(base),'--out',str(out)]
d={'state':'WAITING_FOR_BASELINE_IN_CURRENT_TURN','controller_pid':os.getpid(),'command':cmd};record.write_text(json.dumps(d,indent=2)+'\n')
start=time.monotonic()
while True:
 try:
  b=json.loads((base/'verification.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):b={}
 if b.get('status')=='PASS':break
 if b.get('status')=='FAIL':d.update(state='BASELINE_FAILED');record.write_text(json.dumps(d,indent=2)+'\n');sys.exit(1)
 if time.monotonic()-start>7200:d.update(state='WAIT_LIMIT_REACHED');record.write_text(json.dumps(d,indent=2)+'\n');sys.exit(2)
 time.sleep(5)
d.update(state='RUNNING',started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));record.write_text(json.dumps(d,indent=2)+'\n')
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
p=subprocess.Popen(cmd,env=env);d['child_pid']=p.pid;record.write_text(json.dumps(d,indent=2)+'\n');code=p.wait();d.update(state='FINISHED',exit_code=code,finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));record.write_text(json.dumps(d,indent=2)+'\n');sys.exit(code)
