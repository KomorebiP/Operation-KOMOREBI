#!/usr/bin/env python3
"""Reproduce Paper IV checks in a NEW external working directory.

This does not edit frozen receipts, fetch packages, or install a compiler.
The full mode includes fresh compilation of all 118 production modules.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['records','finite','full'],default='records')
    ap.add_argument('--runtime',type=Path)
    ap.add_argument('--work',type=Path,required=True)
    args=ap.parse_args();work=args.work.resolve()
    if work.exists() or work.is_relative_to(ROOT):
        ap.error('Choose a new output directory outside the frozen release')
    if args.mode=='full' and not args.runtime:
        ap.error('--runtime is required for a fresh formal replay')
    work.mkdir(parents=True);report={'status':'RUNNING','mode':args.mode,'checks':[],
                                   'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    def save():
        (work/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    stages=[('frozen_records',[sys.executable,'-B',str(ROOT/'scripts/verify_release.py')],300),
            ('typed_source_contract',[sys.executable,'-B',str(ROOT/'scripts/validate_source_contract.py'),'--output',str(work/'SOURCE_MAP_CHECK.json')],300),
            ('verifier_controls',[sys.executable,'-B',str(ROOT/'scripts/test_verification.py'),str(work/'VERIFIER_TESTS.json')],300),
            ('integrity_controls',[sys.executable,'-B',str(ROOT/'scripts/test_integrity.py'),str(work/'INTEGRITY_TESTS.json')],300)]
    if args.mode in ('finite','full'):
        stages.append(('finite_replay',[sys.executable,'-B',str(ROOT/'scripts/replay_finite.py'),'--out',str(work/'finite')],1800))
    if args.mode=='full':
        stages.append(('formal_replay',[sys.executable,'-B',str(ROOT/'scripts/replay_lean.py'),'--runtime',str(args.runtime.resolve()),'--work',str(work/'lean')],18000))
    try:
        for name,command,budget in stages:
            print('RUN',name,flush=True);start=time.monotonic();log=work/(name+'.log')
            with log.open('wb') as output:
                process=subprocess.Popen(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,
                    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg'),start_new_session=(os.name=='posix'))
                timeout=False
                try:code=process.wait(timeout=budget)
                except subprocess.TimeoutExpired:
                    timeout=True
                    if os.name=='posix':os.killpg(process.pid,signal.SIGKILL)
                    else:process.kill()
                    code=process.wait()
            report['checks'].append({'name':name,'argv':command,'returncode':code,'timed_out':timeout,
                'seconds':time.monotonic()-start,'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()});save()
            if code!=0 or timeout:
                raise RuntimeError(f'{name} failed: code={code}, timeout={timeout}')
        report['status']='PASS'
    except Exception as error:
        report['status']='FAILED';report['error']=str(error)
    report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print(report['status'],flush=True)
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
