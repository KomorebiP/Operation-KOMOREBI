from pathlib import Path
from datetime import datetime,timezone
import subprocess,time,json,sys
root=Path('/mnt/data/Komorebi_Space_Monograph_v1.5.0')
label=sys.argv[1]
log=Path('/mnt/data')/f'ks15_{label}.log'
record=root/'audit/regularization'/f'{label}.json'
if record.exists():raise SystemExit('Refuse to replace prior build evidence')
start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
with log.open('w') as out:
 try:
  proc=subprocess.run(['bash','build.sh'],cwd=root,stdout=out,stderr=subprocess.STDOUT,timeout=170)
  code=proc.returncode;status='PASS' if code==0 else 'FAIL'
 except subprocess.TimeoutExpired:
  code=None;status='TIMEOUT'
r={'status':status,'started_utc':started,'ended_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'exit_code':code,'log':str(log),'scope':'Publication, finite checks, source preservation. Does not execute Lean.'}
record.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
print('\n'.join(log.read_text().splitlines()[-80:]))
