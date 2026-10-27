#!/usr/bin/env python3
"""Execute a bounded verification command, preserving hashes and diagnostics."""
from pathlib import Path
from datetime import datetime, timezone
import os, sys, subprocess, hashlib, time, json, signal
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_current';OUT.mkdir(exist_ok=True)
RT=Path(os.environ.get('KOMOREBI_LEAN_RUNTIME','/mnt/data/runtime30/Komorebi_Portable_Lean_4.34.0-rc2'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
 ps=list((ROOT/'lean').rglob('*.lean'))+list((ROOT/'verification').rglob('*.lean'))+list((ROOT/'verification').rglob('*.py'))
 ps += [ROOT/n for n in ('lakefile.lean','lean-toolchain','lake-manifest.json','verify_release.py','REPRODUCE.sh','verification/final_plan.json','verification/theorem_inventory.json')]
 return {str(p.relative_to(ROOT)):sha(p) for p in sorted(ps) if p.is_file()}
def main():
 label=sys.argv[1]; argv=sys.argv[2:]
 before=snapshot(); started=datetime.now(timezone.utc).isoformat();t=time.monotonic();rc=127;status='launch-failed'
 env=os.environ|{'PATH':str(RT/'toolchain/bin')+':'+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1'}
 with (OUT/(label+'.log')).open('w') as log:
  try:
   p=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:rc=p.wait(timeout=int(os.environ.get('JOB_TIMEOUT','600')));status='completed' if rc==0 else 'failed'
   except subprocess.TimeoutExpired:
    os.killpg(p.pid,signal.SIGKILL);p.wait();rc=124;status='timeout'
  except Exception as e:log.write(repr(e))
 after=snapshot()
 data={'label':label,'argv':argv,'cwd':str(ROOT),'started_utc':started,'runtime_seconds':time.monotonic()-t,'exit_status':rc,'status':status,'inputs_unchanged':before==after,'inputs_before':before,'inputs_after':after,'log_sha256':sha(OUT/(label+'.log'))}
 (OUT/(label+'.json')).write_text(json.dumps(data,indent=2))
 print(json.dumps({k:v for k,v in data.items() if k not in ('inputs_before','inputs_after')},indent=2),flush=True)
 return rc
if __name__=='__main__':sys.exit(main())
