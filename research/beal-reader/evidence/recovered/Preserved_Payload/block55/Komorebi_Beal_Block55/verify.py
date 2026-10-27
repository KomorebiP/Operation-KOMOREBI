#!/usr/bin/env python3
"""Replay Block55 with exact payload/source checks and fresh finite outputs.
No proof of Beal, formal certificate, or independent mathematical review.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,platform,shutil,signal,stat,subprocess,sys,tempfile,time,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath

PREDECESSOR='Komorebi_Beal_Block54_Frobenius_Reciprocity_v5.4.0.zip'
EXPECTED='66ceadd141f44d56392344bf2797571977d4e3bd18f31282f42264f40852e689'
MANIFEST='PACKAGE_SHA256SUMS.txt'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def payload(root):
    return {str(p.relative_to(root)).replace(os.sep,'/'):sha(p) for p in sorted(root.rglob('*'))
        if p.is_file() and p.name!=MANIFEST and '__pycache__' not in p.parts and p.suffix!='.pyc'}
def audit(root):
    lines=(root/MANIFEST).read_text().splitlines();expected={}
    for line in lines:
        digest,name=line.split(maxsplit=1);name=name.strip()
        p=PurePosixPath(name)
        need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,'Unsafe manifest path')
        need(name not in expected,'Duplicate manifest path');expected[name]=digest
    actual=payload(root)
    need(set(actual)==set(expected),'Payload member set differs from manifest')
    need(actual==expected,'Payload SHA256 mismatch')
    need(sha(root/'predecessor'/PREDECESSOR)==EXPECTED,'Original predecessor ZIP changed')
    return {'status':'PASS_PAYLOAD_HASHES','payload_files':len(actual),'predecessor_sha256':EXPECTED}
def sources(root):
    rec=json.loads((root/'work55/source_records/INHERITED_INPUT_HASHES.json').read_text())
    need(rec['sha256']==EXPECTED,'Source record archive mismatch')
    with zipfile.ZipFile(root/'predecessor'/PREDECESSOR) as z:
        prefix='Komorebi_Beal_Block54/'
        for rel,digest in rec['files'].items():
            need(hashlib.sha256(z.read(prefix+rel)).hexdigest()==digest,'Inherited source changed: '+rel)
    for name in ('reciprocity_checks.py','frobenius_compatibility_checks.py'):
        need(sha(root/'work55/computations'/('inherited_'+name))==rec['files']['work54/computations/'+name],
             'Copied arithmetic source changed')
    return {'status':'PASS_INHERITED_SOURCE_HASHES','named_files':len(rec['files']),'byte_identical_copied_modules':2}
def extract_safe(archive,dest):
    with zipfile.ZipFile(archive) as z:
        seen=set()
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            need(not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename,'Unsafe ZIP path')
            need(i.filename not in seen,'Duplicate ZIP member');seen.add(i.filename)
            need(not stat.S_ISLNK(i.external_attr>>16),'ZIP symlink refused')
        need(z.testzip() is None,'ZIP CRC mismatch');z.extractall(dest)
def execute(label,argv,cwd,timeout,report):
    row={'label':label,'argv':argv,'cwd':str(cwd),'started_utc':datetime.now(timezone.utc).isoformat(),
         'wall_timeout_seconds':timeout};tick=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0')
    try:
        proc=subprocess.Popen(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,encoding='utf-8',errors='replace',start_new_session=(os.name=='posix'))
        row['pid']=proc.pid
        try:out,err=proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name=='posix':os.killpg(proc.pid,signal.SIGKILL)
            else:proc.kill()
            out,err=proc.communicate();row.update(status='INCONCLUSIVE_TIMEOUT',stdout=out,stderr=err,exit_code=proc.returncode)
            raise TimeoutError(label+': wall timeout; no mathematical conclusion')
        row.update(status='COMPLETED',exit_code=proc.returncode,stdout=out,stderr=err)
        return row
    finally:
        row['elapsed_seconds']=time.monotonic()-tick;report['runs'].append(row)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--replay-predecessors',action='store_true')
    p.add_argument('--report',type=Path);p.add_argument('--timeout-seconds',type=float,default=120)
    a=p.parse_args();root=Path(__file__).resolve().parent
    dest=(a.report or root.parent/'Block55_Replay.json').resolve()
    need(not dest.is_relative_to(root),'Report must be outside immutable package')
    need(math.isfinite(a.timeout_seconds) and a.timeout_seconds>0,'Invalid timeout')
    result={'schema':'komorebi.beal.block55.replay.v1','status':'NOT_COMPLETED','started_utc':datetime.now(timezone.utc).isoformat(),
      'argv':sys.argv,'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
      'arithmetic':'exact integers and finite fields; no floating-point proof decisions','random_seed':None,
      'resource_caps':{'per_job_wall_seconds':a.timeout_seconds,'predecessor_wrapper_wall_seconds':8*a.timeout_seconds,
                       'cpu_limit_imposed':None,'memory_limit_imposed':None},'runs':[],
      'nonclaims':['No proof of Beal','No new Lean compilation','No independent mathematical reviewer',
                   'Finite checks do not certify universal prose or inherited geometry']}
    started=time.monotonic()
    try:
        result['integrity_before']=audit(root);result['inherited_inputs']=sources(root)
        before=payload(root);result['input_hashes_before']=before
        with tempfile.TemporaryDirectory(prefix='beal55-') as tmp:
            tmp=Path(tmp)
            if a.replay_predecessors:
                extract_safe(root/'predecessor'/PREDECESSOR,tmp/'old')
                old=tmp/'old/Komorebi_Beal_Block54';report=tmp/'block54.json'
                row=execute('block54_and_selected_nested_predecessors',[sys.executable,'verify.py','--replay-predecessors',
                    '--timeout-seconds',str(a.timeout_seconds),'--report',str(report)],old,8*a.timeout_seconds,result)
                if report.exists():result['predecessor_replay']=json.loads(report.read_text())
                if result.get('predecessor_replay',{}).get('status')=='INCONCLUSIVE_TIMEOUT':
                    raise TimeoutError('Nested predecessor timeout; inconclusive')
                need(row['exit_code']==0 and report.exists(),'Predecessor replay failed')
                need(result['predecessor_replay']['status']=='PASS_DECLARED_CHECKS','Predecessor checks did not pass')
                row['status']='PASS_PREDECESSOR_REPLAY';print('predecessor: PASS',flush=True)
            else:result['predecessor_replay']={'status':'NOT_REQUESTED','byte_integrity_checked':True}
            scratch=tmp/'new';shutil.copytree(root,scratch,ignore=shutil.ignore_patterns('predecessor','__pycache__','*.pyc'))
            jobs=[
                ('local_maximal_checks','work55/computations/local_maximal_checks.py',['--output','work55/verification/local_maximal_checks.json'],'work55/verification/local_maximal_checks.json'),
                ('maximal_layer','work55/computations/maximal_layer.py',['--output','work55/verification/maximal_layer.json'],'work55/verification/maximal_layer.json'),
                ('independent_certificate','work55/computations/independent_certificate.py',['--primary','work55/verification/maximal_layer.json','--output','work55/verification/independent_certificate.json'],'work55/verification/independent_certificate.json'),
                ('exploratory_scan','work55/exploration/scan.py',[],'work55/exploration/scan_result.json')]
            for label,script,argv,target in jobs:
                ref=json.loads((root/target).read_text());out=scratch/target;out.unlink(missing_ok=True)
                source_before=sha(scratch/script)
                row=execute(label,[sys.executable,script,*argv],scratch,a.timeout_seconds,result)
                need(row['exit_code']==0 and out.exists(),label+': no successful fresh output')
                actual=json.loads(out.read_text());need(actual==ref,label+': full exact result differs')
                need(sha(scratch/script)==source_before,label+': script changed')
                row.update(status='PASS_EXACT_REPLAY',script_sha256=source_before,result_sha256=sha(out),reference_sha256=sha(root/target))
                print(label+': PASS_EXACT_REPLAY',flush=True)
            # Public CLI smoke test and deliberately invalid duplicate-prime input.
            smoke=tmp/'cli.json';script='work55/computations/maximal_layer.py'
            row=execute('public_support_cli',[sys.executable,script,'--primes','491','1471','--output',str(smoke)],scratch,a.timeout_seconds,result)
            need(row['exit_code']==0 and json.loads(smoke.read_text())['all_42_tests_injective'],'Public support CLI mismatch')
            row['status']='PASS_CLI_TEST'
            bad=tmp/'invalid.json'
            row=execute('duplicate_prime_negative_control',[sys.executable,script,'--primes','197','197','--output',str(bad)],scratch,a.timeout_seconds,result)
            need(row['exit_code']!=0 and not bad.exists(),'Duplicate prime input accepted')
            row['status']='PASS_EXPECTED_INPUT_REJECTION'
        after=payload(root);need(before==after,'Immutable inputs changed')
        result['input_hashes_after']=after;result['integrity_after']=audit(root);result['status']='PASS_DECLARED_CHECKS'
    except TimeoutError as e:result['status']='INCONCLUSIVE_TIMEOUT';result['error']=str(e)
    except Exception as e:result['status']='FAILED_VERIFICATION';result['error']=f'{type(e).__name__}: {e}'
    finally:
        result['elapsed_seconds']=time.monotonic()-started;result['finished_utc']=datetime.now(timezone.utc).isoformat()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']+'\nReport: '+str(dest),flush=True)
    return 0 if result['status']=='PASS_DECLARED_CHECKS' else 2
if __name__=='__main__':raise SystemExit(main())
