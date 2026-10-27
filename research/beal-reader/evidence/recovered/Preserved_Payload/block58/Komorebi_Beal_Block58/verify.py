#!/usr/bin/env python3
"""Replay Block58 from immutable inputs. Python 3.10+, standard library only.

A pass verifies the declared exact finite assertions and byte integrity.
It does not certify the inherited geometry, Lean proofs, or Beal.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,os,platform,shutil,signal,stat,subprocess,sys,tempfile,time,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath

PREDECESSOR='Komorebi_Beal_Block57_Forced_Bad_Frobenius_v5.7.0.zip'
EXPECTED='86919491378566d3393d67ab41e56ab96a24cf8f7bfb15eff5ea28a01f9d6331'
MANIFEST='PACKAGE_SHA256SUMS.txt'

def need(x,msg):
    if not x:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snapshot(root):
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.relative_to(root).as_posix()!=MANIFEST
            and '__pycache__' not in p.parts and p.suffix!='.pyc'}
def audit(root):
    expected={}
    for line in (root/MANIFEST).read_text().splitlines():
        digest,name=line.split(maxsplit=1);name=name.strip();p=PurePosixPath(name)
        need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,'Unsafe manifest path')
        need(name not in expected,'Duplicate manifest entry');expected[name]=digest
    actual=snapshot(root)
    need(set(actual)==set(expected),'Payload member set mismatch')
    need(actual==expected,'Payload SHA256 mismatch')
    need(sha(root/'predecessor'/PREDECESSOR)==EXPECTED,'Predecessor bytes changed')
    return {'status':'PASS_PAYLOAD_HASHES','payload_files':len(actual),'predecessor_sha256':EXPECTED}
def source_audit(root):
    records=json.loads((root/'work58/source_records/INHERITED_INPUT_HASHES.json').read_text())
    need(records['predecessor_sha256']==EXPECTED,'Wrong source checkpoint')
    cache={(): (root/'predecessor'/PREDECESSOR).read_bytes()}
    for row in records['files']:
        chain=()
        for member in row['archive_chain']:
            key=chain+(member,)
            if key not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[chain])) as z:cache[key]=z.read(member)
            chain=key
        with zipfile.ZipFile(io.BytesIO(cache[chain])) as z:content=z.read(row['member'])
        need(hashlib.sha256(content).hexdigest()==row['sha256'],'Inherited source hash mismatch: '+row['member'])
    for rec in records.get('copied_modules',[]):
        need(sha(root/rec['local_path'])==rec['sha256'],'Copied inherited arithmetic changed')
    return {'status':'PASS_NAMED_SOURCE_HASHES','named_files':len(records['files']),
            'copied_modules':len(records.get('copied_modules',[])),'nested_archives_read':len(cache)}
def safe_extract(path,dest):
    with zipfile.ZipFile(path) as z:
        names=set()
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            need(not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename,'Unsafe ZIP member')
            need(i.filename not in names,'Duplicate ZIP member');names.add(i.filename)
            need(not stat.S_ISLNK(i.external_attr>>16),'ZIP symlink refused')
        need(z.testzip() is None,'ZIP CRC mismatch');z.extractall(dest)
def execute(label,argv,cwd,timeout,report):
    row={'label':label,'argv':argv,'cwd':str(cwd),'wall_timeout_seconds':timeout,
         'started_utc':datetime.now(timezone.utc).isoformat()};tick=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0')
    try:
        p=subprocess.Popen(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                           text=True,encoding='utf-8',errors='replace',start_new_session=(os.name=='posix'))
        row['pid']=p.pid
        try:out,err=p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name=='posix':os.killpg(p.pid,signal.SIGKILL)
            else:p.kill()
            out,err=p.communicate();row.update(status='INCONCLUSIVE_TIMEOUT',exit_code=p.returncode,stdout=out,stderr=err)
            raise TimeoutError(label+': timeout, no mathematical conclusion')
        row.update(status='COMPLETED',exit_code=p.returncode,stdout=out,stderr=err)
        return row
    finally:
        row['elapsed_seconds']=time.monotonic()-tick;report['runs'].append(row)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--replay-predecessors',action='store_true')
    p.add_argument('--report',type=Path);p.add_argument('--timeout-seconds',type=float,default=180)
    a=p.parse_args();root=Path(__file__).resolve().parent
    report=(a.report or root.parent/'Block58_Replay.json').resolve()
    need(not report.is_relative_to(root),'Report must be outside the immutable package')
    need(math.isfinite(a.timeout_seconds) and a.timeout_seconds>0,'Invalid wall timeout')
    result={'schema':'komorebi.beal.block58.replay.v1','status':'NOT_COMPLETED','argv':sys.argv,
            'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,
            'platform':platform.platform(),'arithmetic':'exact integers and finite fields','random_seed':None,
            'resource_caps':{'per_job_wall_seconds':a.timeout_seconds,
                             'predecessor_wrapper_wall_seconds':12*a.timeout_seconds,
                             'additional_cpu_limit':None,'additional_memory_limit':None},
            'runs':[],'nonclaims':['No proof of Beal','No new Lean compilation',
                                   'No independent mathematical review','Inherited geometry remains conditional']}
    tick=time.monotonic()
    try:
        result['integrity_before']=audit(root);result['inherited_sources']=source_audit(root)
        before=snapshot(root);result['input_hashes_before']=before
        with tempfile.TemporaryDirectory(prefix='beal58-') as tmp:
            tmp=Path(tmp)
            if a.replay_predecessors:
                safe_extract(root/'predecessor'/PREDECESSOR,tmp/'old')
                old=tmp/'old/Komorebi_Beal_Block57';out=tmp/'block57_replay.json'
                row=execute('block57_and_selected_nested_predecessors',
                            [sys.executable,'verify.py','--replay-predecessors','--report',str(out),
                             '--timeout-seconds',str(a.timeout_seconds)],old,12*a.timeout_seconds,result)
                if out.exists():result['predecessor_replay']=json.loads(out.read_text())
                if result.get('predecessor_replay',{}).get('status')=='INCONCLUSIVE_TIMEOUT':raise TimeoutError('Nested predecessor timeout')
                need(row['exit_code']==0 and out.exists(),'Predecessor execution failed')
                need(result['predecessor_replay']['status']=='PASS_DECLARED_CHECKS','Predecessor checks did not pass')
                row['status']='PASS_PREDECESSOR_REPLAY';print('predecessor: PASS',flush=True)
            else:result['predecessor_replay']={'status':'NOT_REQUESTED','byte_integrity_checked':True}
            scratch=tmp/'scratch';shutil.copytree(root,scratch,ignore=shutil.ignore_patterns('predecessor','__pycache__','*.pyc'))
            jobs=[
                ('primary_certificate','work58/computations/primary_certificate.py',
                 ['--output','work58/verification/primary_certificate.json'],'work58/verification/primary_certificate.json'),
                ('discriminant_checks','work58/computations/discriminant_checks.py',
                 ['--output','work58/verification/discriminant_checks.json'],'work58/verification/discriminant_checks.json'),
                ('independent_certificate','work58/computations/independent_certificate.py',
                 ['--primary','work58/verification/primary_certificate.json',
                  '--discriminant','work58/verification/discriminant_checks.json',
                  '--output','work58/verification/independent_certificate.json'],
                 'work58/verification/independent_certificate.json')]
            for label,script,argv,target in jobs:
                ref=json.loads((root/target).read_text());out=scratch/target;out.unlink(missing_ok=True)
                digest=sha(scratch/script)
                row=execute(label,[sys.executable,script,*argv],scratch,a.timeout_seconds,result)
                need(row['exit_code']==0 and out.exists(),label+': no successful fresh output')
                need(json.loads(out.read_text())==ref,label+': full exact result differs')
                need(sha(scratch/script)==digest,label+': script changed during execution')
                row.update(status='PASS_EXACT_REPLAY',script_sha256=digest,result_sha256=sha(out),reference_sha256=sha(root/target))
                print(label+': PASS_EXACT_REPLAY',flush=True)
            # Altered arithmetic must be independently rejected, not just mismatch hashes.
            for kind in ('point_count','residue_row'):
                corrupt=json.loads((scratch/'work58/verification/primary_certificate.json').read_text())
                if kind=='point_count':
                    corrupt['finite_frobenius'][0]['rows'][0]['N1']+=1
                else:
                    x=corrupt['reciprocity']['places'][0]['logs_mod7']
                    x[11]=(x[11]+1)%7
                bad=tmp/('wrong_'+kind+'.json');bad.write_text(json.dumps(corrupt))
                out=tmp/('must_not_exist_'+kind+'.json')
                row=execute('altered_'+kind+'_negative_control',
                    [sys.executable,'work58/computations/independent_certificate.py','--primary',str(bad),
                     '--discriminant','work58/verification/discriminant_checks.json','--output',str(out)],
                    scratch,a.timeout_seconds,result)
                need(row['exit_code']!=0 and not out.exists(),'Altered arithmetic was accepted: '+kind)
                row['status']='PASS_EXPECTED_ARITHMETIC_REJECTION'
        after=snapshot(root);need(before==after,'Immutable inputs changed')
        result['input_hashes_after']=after;result['integrity_after']=audit(root)
        result['status']='PASS_DECLARED_CHECKS'
    except TimeoutError as e:result['status']='INCONCLUSIVE_TIMEOUT';result['error']=str(e)
    except Exception as e:result['status']='FAILED_VERIFICATION';result['error']=f'{type(e).__name__}: {e}'
    finally:
        result['elapsed_seconds']=time.monotonic()-tick;result['finished_utc']=datetime.now(timezone.utc).isoformat()
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']+'\nReport: '+str(report),flush=True)
    return 0 if result['status']=='PASS_DECLARED_CHECKS' else 2
if __name__=='__main__':raise SystemExit(main())
