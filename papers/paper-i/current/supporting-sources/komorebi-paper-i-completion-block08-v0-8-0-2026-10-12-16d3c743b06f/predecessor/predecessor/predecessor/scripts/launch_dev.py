from pathlib import Path
import subprocess,sys,json,time
r=Path(__file__).resolve().parents[1]
prefix=r/'evidence'/('dev_driver_'+str(time.time_ns()))
with prefix.with_suffix('.log').open('w') as f:
 p=subprocess.Popen([sys.executable,str(r/'scripts/dev_check.py'),*sys.argv[1:]],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
rec={'pid':p.pid,'log':str(prefix.with_suffix('.log')),'args':sys.argv[1:],'time':time.time()}
prefix.with_suffix('.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec))
