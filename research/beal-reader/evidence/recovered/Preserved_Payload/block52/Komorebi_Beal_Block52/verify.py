#!/usr/bin/env python3
"""Replay Block52's exact finite checks and optionally the frozen predecessor.

Python3.10+, standard library only. A successful replay does not certify
universal prose proofs, external source theorems, or the Beal conjecture.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import zipfile

PREDECESSOR='Komorebi_Beal_Block51_Monodromy_Depth_v5.1.0.zip'
PREDECESSOR_SHA='2db43f22efa22e5e21ee2359eb132d4744a18c60dda39792f57f12a3385c5fd6'

def need(test: bool, message: str):
    if not test: raise ValueError(message)

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def payload(root: Path) -> dict[str,str]:
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.name!='.DS_Store' and '__pycache__' not in p.parts
            and p!=root/'PACKAGE_SHA256SUMS.txt'}

def audit(root: Path) -> dict:
    expected={}
    for line in (root/'PACKAGE_SHA256SUMS.txt').read_text().splitlines():
        if not line.strip(): continue
        digest,rel=line.split('  ',1)
        need(len(digest)==64 and rel not in expected,'Malformed/duplicate manifest entry')
        need((root/rel).resolve().is_relative_to(root),'Unsafe manifest path')
        expected[rel]=digest
    actual=payload(root)
    need(actual==expected,'Package payload/member/hash mismatch')
    zpath=root/'predecessor'/PREDECESSOR
    need(sha(zpath)==PREDECESSOR_SHA,'Frozen predecessor changed')
    with zipfile.ZipFile(zpath) as z:
        need(z.testzip() is None,'Predecessor CRC failed')
        count=len(z.infolist())
    return {'status':'PASS_BYTE_INTEGRITY','payload_files_checked':len(actual),
            'predecessor_sha256':PREDECESSOR_SHA,'predecessor_zip_members':count}

def extract_safe(zpath: Path, destination: Path):
    with zipfile.ZipFile(zpath) as z:
        names=set()
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            need(not p.is_absolute() and '..' not in p.parts and '\\' not in info.filename,
                 'Unsafe archive member path')
            need(info.filename not in names,'Duplicate archive member')
            names.add(info.filename)
            mode=(info.external_attr>>16)&0xffff
            need(not stat.S_ISLNK(mode),'Archive symlink refused')
        z.extractall(destination)

def execute(label: str, argv: list[str], cwd: Path, seconds: float, report: dict) -> dict:
    row={'label':label,'argv':argv,'cwd':str(cwd),
         'started_utc':datetime.now(timezone.utc).isoformat(),'wall_timeout_seconds':seconds}
    tick=time.monotonic()
    env=dict(os.environ,PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
    try:
        proc=subprocess.Popen(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              text=True,encoding='utf-8',errors='replace',start_new_session=(os.name=='posix'))
        try:
            stdout,stderr=proc.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:
            if os.name=='posix':
                os.killpg(proc.pid,signal.SIGKILL)
            else:
                proc.kill()
            stdout,stderr=proc.communicate()
            row.update(status='INCONCLUSIVE_TIMEOUT',timed_out=True,exit_code=proc.returncode,
                       stdout=stdout,stderr=stderr)
            raise TimeoutError(f'{label}: timeout, no mathematical conclusion')
        row.update(exit_code=proc.returncode,stdout=stdout,stderr=stderr,timed_out=False)
        row['status']='COMPLETED_ZERO_EXIT' if proc.returncode==0 else 'FAILED_PROCESS'
        return row
    finally:
        row['elapsed_seconds']=time.monotonic()-tick
        report['runs'].append(row)

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-predecessors',action='store_true')
    parser.add_argument('--timeout-seconds',type=float,default=120.0)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    dest=(args.report or root.parent/(root.name+'_replay.json')).resolve()
    need(not dest.is_relative_to(root),'Report must be outside the immutable package')
    need(math.isfinite(args.timeout_seconds) and args.timeout_seconds>0,'Timeout must be positive and finite')
    report={'schema':'komorebi.beal.block52.replay.v1','status':'NOT_COMPLETED',
            'started_utc':datetime.now(timezone.utc).isoformat(),'argv':sys.argv,
            'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
            'ordering':'deterministic','random_seed':None,'runs':[],
            'arithmetic':'exact integers; finite fields; integral quadratic ring',
            'resource_caps':{'per_new_job_wall_seconds':args.timeout_seconds,
                'predecessor_wrapper_wall_seconds':8*args.timeout_seconds,
                'cpu_limit_imposed_by_runner':None,'memory_limit_imposed_by_runner':None},
            'non_claims':['No proof of Beal or of the complete signature',
                'No new Lean certificate','No independent mathematical reviewer',
                'Finite runs do not certify external theorems or universal prose proofs']}
    tick=time.monotonic()
    try:
        report['integrity_before']=audit(root)
        before=payload(root);report['input_hashes_before']=before
        with tempfile.TemporaryDirectory(prefix='beal52-replay-') as tmp:
            tmp=Path(tmp)
            if args.replay_predecessors:
                extract_safe(root/'predecessor'/PREDECESSOR,tmp/'predecessor')
                roots=[p.parent for p in (tmp/'predecessor').glob('*/verify.py')]
                need(len(roots)==1,'Unexpected predecessor root structure')
                oldroot=roots[0];oldreport=tmp/'block51-replay.json'
                argv=[sys.executable,'verify.py','--replay-predecessors','--timeout',str(args.timeout_seconds),
                      '--report',str(oldreport)]
                row=execute('block51_and_six_selected_predecessors',argv,oldroot,8*args.timeout_seconds,report)
                if oldreport.exists():
                    olddata=json.loads(oldreport.read_text())
                    report['predecessor_replay']=olddata
                    if olddata.get('status')=='INCONCLUSIVE_TIMEOUT':
                        row['status']='INCONCLUSIVE_TIMEOUT'
                        raise TimeoutError('A nested predecessor job timed out; no mathematical conclusion')
                need(row['exit_code']==0 and oldreport.exists(),'Predecessor replay failed or omitted its report')
                need(report['predecessor_replay']['status']=='PASS_DECLARED_REPLAYS_AND_BYTE_INTEGRITY',
                     'Predecessor did not pass its declared verification')
                row['status']='PASS_DECLARED_PREDECESSOR_REPLAY'
                print('predecessor: PASS',flush=True)
            else:
                report['predecessor_replay']={'status':'NOT_REQUESTED','byte_integrity_checked':True}
            scratch=tmp/'new'
            shutil.copytree(root,scratch,ignore=shutil.ignore_patterns('predecessor','__pycache__','.DS_Store'))
            jobs=[('finite_frobenius','work52/computations/finite_frobenius.py',
                   ['--output','work52/verification/finite_frobenius.json'],'work52/verification/finite_frobenius.json'),
                  ('independent_pointcounts','work52/computations/independent_pointcounts.py',
                   ['--reference','work52/verification/finite_frobenius.json','--output','work52/verification/independent_pointcounts.json'],
                   'work52/verification/independent_pointcounts.json'),
                  ('kummer_and_matrix_checks','work52/computations/kummer_and_matrix_checks.py',
                   ['--output','work52/verification/kummer_and_matrix_checks.json'],'work52/verification/kummer_and_matrix_checks.json')]
            for label,script,params,target in jobs:
                reference=json.loads((root/target).read_text())
                actual_path=scratch/target
                actual_path.unlink(missing_ok=True)
                source_hash=sha(scratch/script)
                argv=[sys.executable,script,*params]
                row=execute(label,argv,scratch,args.timeout_seconds,report)
                row['script_sha256_before']=source_hash
                need(row['exit_code']==0,f'{label}: nonzero exit')
                need(actual_path.exists(),f'{label}: no fresh output')
                actual=json.loads(actual_path.read_text())
                row['result_matches_reference_json']=actual==reference
                row['fresh_result_sha256']=sha(actual_path)
                row['reference_result_sha256']=sha(root/target)
                row['script_sha256_after']=sha(scratch/script)
                need(row['script_sha256_after']==source_hash,f'{label}: source modified')
                need(actual==reference and actual.get('status')=='PASS',f'{label}: finite result mismatch')
                row['status']='PASS_EXACT_REPLAY'
                print(f'{label}: PASS_EXACT_REPLAY',flush=True)
        after=payload(root);report['input_hashes_after']=after
        need(before==after,'Package inputs changed during verification')
        report['integrity_after']=audit(root)
        report['status']='PASS_DECLARED_CHECKS'
    except TimeoutError as exc:
        report['status']='INCONCLUSIVE_TIMEOUT';report['error']=str(exc)
    except Exception as exc:
        report['status']='FAILED_VERIFICATION';report['error']=f'{type(exc).__name__}: {exc}'
    finally:
        report['finished_utc']=datetime.now(timezone.utc).isoformat()
        report['elapsed_seconds']=time.monotonic()-tick
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f"{report['status']}\nReport: {dest}",flush=True)
    return 0 if report['status']=='PASS_DECLARED_CHECKS' else 2

if __name__=='__main__':
    raise SystemExit(main())
