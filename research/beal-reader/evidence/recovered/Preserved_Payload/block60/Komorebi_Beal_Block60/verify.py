#!/usr/bin/env python3
"""Replay Block60's declared finite checks and preserve all proof boundaries.
Python3.10+, standard library only. Put the report outside this immutable package.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, platform, shutil, signal, stat
import subprocess, sys, tempfile, time, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

PREDECESSOR='Komorebi_Beal_Block59_Natural_Torsion_Nodal_Period_v5.9.0.zip'
EXPECTED='c6e193ae9be07275f0b83baf70fb15c2390578fd6772a5dc5adc497f66f7d671'
MANIFEST='PACKAGE_SHA256SUMS.txt'


def need(ok,message):
    if not ok:raise AssertionError(message)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.relative_to(root).as_posix()!=MANIFEST}


def audit(root):
    records={}
    for line in (root/MANIFEST).read_text().splitlines():
        digest,name=line.split('  ',1)
        p=PurePosixPath(name)
        need(not p.is_absolute() and '..' not in p.parts and chr(92) not in name,'Unsafe manifest path')
        need(name not in records,'Duplicate manifest entry')
        need(len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'Invalid digest')
        records[name]=digest
    actual=snapshot(root)
    need(set(records)==set(actual),'Payload member set mismatch')
    for name,digest in records.items():need(actual[name]==digest,'Payload hash mismatch: '+name)
    need(sha(root/'predecessor'/PREDECESSOR)==EXPECTED,'Original predecessor changed')
    return {'status':'PASS_PAYLOAD_HASHES','payload_files':len(actual),'predecessor_sha256':EXPECTED}


def audit_inherited(root):
    records=json.loads((root/'work60/source_records/INHERITED_INPUT_HASHES.json').read_text())
    need(records['sha256']==EXPECTED and records['predecessor']==PREDECESSOR,'Wrong pinned predecessor')
    with zipfile.ZipFile(root/'predecessor'/PREDECESSOR) as z:
        for row in records['named_inputs']:
            need(hashlib.sha256(z.read(row['member'])).hexdigest()==row['sha256'],
                 'Named inherited source changed: '+row['member'])
    return {'status':'PASS_NAMED_INPUTS','named_sources':len(records['named_inputs']),
            'upstream_deeper_hashes_checked_by_predecessor_when_replayed':True}


def extract_safely(src,dest):
    with zipfile.ZipFile(src) as z:
        seen=set()
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            need(not p.is_absolute() and '..' not in p.parts and chr(92) not in i.filename,'Unsafe ZIP path')
            need(i.filename not in seen,'Duplicate ZIP path');seen.add(i.filename)
            need(not stat.S_ISLNK(i.external_attr>>16),'ZIP symlink refused')
        need(z.testzip() is None,'ZIP CRC error')
        z.extractall(dest)


def execute(label,argv,cwd,timeout,result):
    row={'label':label,'argv':argv,'cwd':str(cwd),'wall_limit_seconds':timeout,
         'started_utc':datetime.now(timezone.utc).isoformat()}
    start=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',PYTHONOPTIMIZE='0')
    try:
        p=subprocess.Popen(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,encoding='utf-8',errors='replace',start_new_session=(os.name=='posix'))
        row['pid']=p.pid
        try:out,err=p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name=='posix':os.killpg(p.pid,signal.SIGKILL)
            else:p.kill()
            out,err=p.communicate();row.update(status='INCONCLUSIVE_TIMEOUT',exit_code=p.returncode,stdout=out,stderr=err)
            raise TimeoutError(label+': timeout is inconclusive')
        row.update(status='COMPLETED',exit_code=p.returncode,stdout=out,stderr=err)
        return row
    finally:
        row['elapsed_seconds']=time.monotonic()-start;result['runs'].append(row)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--replay-predecessors',action='store_true')
    p.add_argument('--report',type=Path)
    p.add_argument('--timeout-seconds',type=float,default=180)
    a=p.parse_args();root=Path(__file__).resolve().parent
    out=(a.report or root.parent/'Block60_Replay.json').resolve()
    need(not out.is_relative_to(root),'Report must be outside the immutable package')
    need(math.isfinite(a.timeout_seconds) and a.timeout_seconds>0,'Invalid wall timeout')
    result={'schema':'komorebi.beal.block60.replay.v1','status':'NOT_COMPLETED',
      'argv':sys.argv,'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
      'python_executable':sys.executable,'platform':platform.platform(),
      'arithmetic':'exact rational quadratic fields, finite fields, integer modular lifts',
      'random_seed':None,'numerical_tolerance':None,
      'resource_caps':{'per_job_wall_seconds':a.timeout_seconds,'predecessor_wall_seconds':15*a.timeout_seconds,
        'additional_cpu_limit':None,'additional_memory_limit':None},
      'runs':[],'nonclaims':['No global beta or Beal solution constructed',
      'No new survivor prime exclusion','No new Lean compilation','No independent mathematical review',
      'Analytic comparison and upstream geometry are written conditional proofs']}
    start=time.monotonic()
    try:
        result['integrity_before']=audit(root);result['named_inherited_inputs']=audit_inherited(root)
        before=snapshot(root);result['input_hashes_before']=before
        with tempfile.TemporaryDirectory(prefix='beal60-') as tmp:
            tmp=Path(tmp)
            if a.replay_predecessors:
                extract_safely(root/'predecessor'/PREDECESSOR,tmp/'old')
                old=tmp/'old/Komorebi_Beal_Block59';report=tmp/'Block59_Replay.json'
                run=execute('block59_and_selected_nested_predecessors',
                    [sys.executable,'verify.py','--replay-predecessors','--report',str(report),
                     '--timeout-seconds',str(a.timeout_seconds)],old,15*a.timeout_seconds,result)
                if report.exists():result['predecessor_replay']=json.loads(report.read_text())
                if result.get('predecessor_replay',{}).get('status')=='INCONCLUSIVE_TIMEOUT':
                    raise TimeoutError('Nested predecessor timeout')
                need(run['exit_code']==0 and report.exists(),'Predecessor failed')
                need(result['predecessor_replay']['status']=='PASS_DECLARED_CHECKS','Predecessor not verified')
                run['status']='PASS_PREDECESSOR_REPLAY';print('predecessor: PASS',flush=True)
            else:result['predecessor_replay']={'status':'NOT_REQUESTED','byte_integrity_checked':True}
            scratch=tmp/'scratch'
            shutil.copytree(root,scratch)
            jobs=[('diagonal_period_certificate','work60/computations/diagonal_period_certificate.py',
                ['--output','work60/verification/diagonal_period_certificate.json'],
                'work60/verification/diagonal_period_certificate.json'),
              ('independent_diagonal_check','work60/computations/independent_diagonal_check.py',
                ['--primary','work60/verification/diagonal_period_certificate.json',
                 '--output','work60/verification/independent_diagonal_check.json'],
                'work60/verification/independent_diagonal_check.json')]
            for label,script,argv,target in jobs:
                reference=json.loads((root/target).read_text());dest=scratch/target;dest.unlink(missing_ok=True)
                digest=sha(scratch/script)
                run=execute(label,[sys.executable,script,*argv],scratch,a.timeout_seconds,result)
                need(run['exit_code']==0 and dest.exists(),label+': missing successful output')
                need(json.loads(dest.read_text())==reference,label+': complete JSON differs')
                need(sha(scratch/script)==digest,'Scientific source changed')
                run.update(status='PASS_EXACT_REPLAY',script_sha256=digest,result_sha256=sha(dest),
                           expected_result_sha256=sha(root/target))
                print(label+': PASS_EXACT_REPLAY',flush=True)
            for label,mutate in [
                ('wrong_smoothing_constant',lambda d:d['symbolic']['kappa_a'].__setitem__(0,'0')),
                ('false_local_torsion_flag',lambda d:d['witnesses'][0]['full_torsion_by_period_test'].__setitem__('49',False))]:
                data=json.loads((root/'work60/verification/diagonal_period_certificate.json').read_text())
                mutate(data);bad=tmp/(label+'.json');bad.write_text(json.dumps(data))
                reject_out=tmp/(label+'_output.json')
                run=execute(label,[sys.executable,'work60/computations/independent_diagonal_check.py',
                    '--primary',str(bad),'--output',str(reject_out)],scratch,a.timeout_seconds,result)
                need(run['exit_code']!=0 and not reject_out.exists(),'Altered arithmetic accepted: '+label)
                run['status']='PASS_EXPECTED_ARITHMETIC_REJECTION'
            # Independent payload-corruption check on a complete package copy.
            corrupt=tmp/'corrupt';shutil.copytree(root,corrupt)
            f=corrupt/'work60/notes/LOCAL_CRITERION.md';f.write_text(f.read_text()+'\nTAMPER\n')
            try:audit(corrupt)
            except AssertionError as e:
                need('Payload hash mismatch: work60/notes/LOCAL_CRITERION.md'==str(e),'Wrong corruption failure')
                result['payload_corruption_control']='PASS_EXPECTED_HASH_REJECTION'
            else:raise AssertionError('Altered payload accepted')
        after=snapshot(root);need(before==after,'Frozen package mutated')
        result['input_hashes_after']=after;result['integrity_after']=audit(root)
        result['status']='PASS_DECLARED_CHECKS'
    except TimeoutError as e:result.update(status='INCONCLUSIVE_TIMEOUT',error=str(e))
    except Exception as e:result.update(status='FAILED_VERIFICATION',error=f'{type(e).__name__}: {e}')
    finally:
        result['elapsed_seconds']=time.monotonic()-start;result['finished_utc']=datetime.now(timezone.utc).isoformat()
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']+'\nReport: '+str(out),flush=True)
    return 0 if result['status']=='PASS_DECLARED_CHECKS' else 2
if __name__=='__main__':raise SystemExit(main())
