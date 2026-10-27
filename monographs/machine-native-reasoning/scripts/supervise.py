#!/usr/bin/env python3
"""Run one complete local gate and retain the supervisor's actual exit status.
Per-command process-group cleanup is handled by verify.py. No external service is used.
"""
from pathlib import Path
import argparse,json,os,signal,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--runtime',required=True)
 ap.add_argument('--out',required=True,help='New project-relative evidence directory')
 ap.add_argument('--whole-timeout',type=int,default=900)
 a=ap.parse_args();out=Path(a.out)
 if out.is_absolute() or '..' in out.parts:ap.error('--out must be project-relative')
 if a.whole_timeout<=0:ap.error('timeout must be positive')
 log=ROOT/out.parent/(out.name+'_supervisor.log')
 receipt=ROOT/out.parent/(out.name+'_supervisor.json')
 if log.exists() or receipt.exists():ap.error('Supervisor output already exists')
 log.parent.mkdir(parents=True,exist_ok=True)
 argv=[sys.executable,str(ROOT/'scripts/verify.py'),'--runtime',str(Path(a.runtime).resolve()),'--out',str(out)]
 t=time.time();status='completed'
 with log.open('x') as f:
  p=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=p.wait(timeout=a.whole_timeout)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGKILL);p.wait();code=-9;status='timeout'
 record={'argv':argv,'started_at':t,'ended_at':time.time(),'status':status,'exit_code':code,'supervisor_wall_limit':a.whole_timeout}
 receipt.write_text(json.dumps(record,indent=2)+'\n')
 print(status,code,'seconds',record['ended_at']-t)
 return 0 if code==0 else 1
if __name__=='__main__':raise SystemExit(main())
