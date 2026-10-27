#!/usr/bin/env python3
"""Bounded command runner with immutable source snapshots and explicit exits."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,time,signal,sys
ROOT=Path(__file__).resolve().parents[1]
RT=Path(os.environ.get('KOMOREBI_LEAN_RUNTIME','/mnt/data/block32/runtime/Komorebi_Portable_Lean_4.34.0-rc2'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
    files=list((ROOT/'lean').rglob('*.lean'))+list((ROOT/'verification').rglob('*.lean'))+list((ROOT/'verification').rglob('*.py'))
    files += [ROOT/f for f in ['lakefile.lean','lake-manifest.json','lean-toolchain','verify_release.py','validate_manifest.py','COMPUTATION_CONTRACT.md','verification/theorem_inventory.json','verification/final_plan.json']]
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(files) if p.is_file()}
def main():
    label=sys.argv[1];argv=sys.argv[2:];out=ROOT/'results';out.mkdir(exist_ok=True)
    before=snapshot();start=time.monotonic();started=datetime.now(timezone.utc).isoformat();status='launch-failed';rc=127
    with (out/(label+'.log')).open('w') as log:
      try:
        env=os.environ|{'PATH':str(RT/'toolchain/bin')+':'+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1'}
        cp=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:rc=cp.wait(timeout=int(os.environ.get('JOB_TIMEOUT','900')));status='completed' if rc==0 else 'failed'
        except subprocess.TimeoutExpired:
            os.killpg(cp.pid,signal.SIGKILL);cp.wait();rc=124;status='timeout'
      except Exception as e:log.write(repr(e))
    after=snapshot();rec={'label':label,'argv':argv,'started_utc':started,'runtime_seconds':time.monotonic()-start,
      'exit_status':rc,'status':status,'inputs_unchanged':before==after,'inputs_before':before,'inputs_after':after,
      'log_sha256':sha(out/(label+'.log'))}
    (out/(label+'.json')).write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rec.items() if not k.startswith('inputs_')},indent=2),flush=True)
    return rc if before==after else 99
if __name__=='__main__':sys.exit(main())
