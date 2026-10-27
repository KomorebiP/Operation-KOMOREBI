#!/usr/bin/env python3
"""Replay Block59 from immutable inputs. Python 3.10+, standard library only.

A pass verifies the declared exact finite assertions and byte integrity.
It does not certify the inherited geometry, Lean proofs, or Beal.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,os,platform,shutil,signal,stat,subprocess,sys,tempfile,time,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath

PREDECESSOR='Komorebi_Beal_Block58_Good_Bad_Discriminant_Closure_v5.8.0.zip'
EXPECTED='68faba4f452fe2c8f88d6589589ccfb7d337f4fe2c73d8336f6b8e3a31980e5a'
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
    records=json.loads((root/'work59/source_records/INHERITED_INPUT_HASHES.json').read_text())
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
            raise TimeoutError(label+': timeout, no mathematical conclusion')
        row.update(status='COMPLETED',exit_code=p.returncode,stdout=out,stderr=err)
        return row
    finally:
        row['elapsed_seconds']=time.monotonic()-tick;report['runs'].append(row)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--replay-predecessors',action='store_true')
    p.add_argument('--report',type=Path)
    p.add_argument('--timeout-seconds',type=float,default=180)
    a=p.parse_args();root=Path(__file__).resolve().parent
    report=(a.report or root.parent/'Block59_Replay.json').resolve()
    need(not report.is_relative_to(root),'Report must be outside immutable package')
    need(math.isfinite(a.timeout_seconds) and a.timeout_seconds>0,'Invalid wall timeout')
    result={'schema':'komorebi.beal.block59.replay.v1','status':'NOT_COMPLETED','argv':sys.argv,
      'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,
      'platform':platform.platform(),'arithmetic':'exact integers, rational Q(phi), finite fields',
      'random_seed':None,'resource_caps':{'per_job_wall_seconds':a.timeout_seconds,
      'predecessor_wrapper_wall_seconds':12*a.timeout_seconds,'additional_cpu_limit':None,'additional_memory_limit':None},
      'runs':[],'nonclaims':['No proof of Beal or full depth-two exclusion','No new Lean compilation',
      'No independent mathematical review','Inherited actual geometry remains conditional',
      'Finite outputs do not certify analytic source/application theorems']}
    tick=time.monotonic()
    try:
        result['integrity_before']=audit(root);result['inherited_sources']=source_audit(root)
        with zipfile.ZipFile(root/'predecessor'/PREDECESSOR) as z:
            olddata=json.loads(z.read('Komorebi_Beal_Block58/work58/verification/primary_certificate.json'))
        cache=json.loads((root/'work59/source_records/frozen_block58_reciprocity.json').read_text())
        need(cache==olddata['reciprocity'],'Derived frozen reciprocity cache differs from original')
        result['derived_cache']='PASS_EXACT_JSON_PROJECTION'
        before=snapshot(root);result['input_hashes_before']=before
        with tempfile.TemporaryDirectory(prefix='beal59-') as tmp:
            tmp=Path(tmp)
            if a.replay_predecessors:
                safe_extract(root/'predecessor'/PREDECESSOR,tmp/'old')
                old=tmp/'old/Komorebi_Beal_Block58';out=tmp/'block58_replay.json'
                row=execute('block58_and_selected_nested_predecessors',
                    [sys.executable,'verify.py','--replay-predecessors','--report',str(out),
                     '--timeout-seconds',str(a.timeout_seconds)],old,12*a.timeout_seconds,result)
                if out.exists():result['predecessor_replay']=json.loads(out.read_text())
                if result.get('predecessor_replay',{}).get('status')=='INCONCLUSIVE_TIMEOUT':
                    raise TimeoutError('Nested predecessor timeout')
                need(row['exit_code']==0 and out.exists(),'Predecessor execution failed')
                need(result['predecessor_replay']['status']=='PASS_DECLARED_CHECKS','Predecessor did not pass')
                row['status']='PASS_PREDECESSOR_REPLAY';print('predecessor: PASS',flush=True)
            else:result['predecessor_replay']={'status':'NOT_REQUESTED','byte_integrity_checked':True}
            scratch=tmp/'scratch';shutil.copytree(root,scratch,ignore=shutil.ignore_patterns('predecessor','__pycache__','*.pyc'))
            jobs=[
              ('period_certificate','work59/computations/period_certificate.py',
                ['--output','work59/verification/period_certificate.json'],'work59/verification/period_certificate.json'),
              ('local_torsion_checks','work59/computations/local_torsion_checks.py',
                ['--output','work59/verification/local_torsion_checks.json'],'work59/verification/local_torsion_checks.json'),
              ('independent_period_certificate','work59/computations/independent_period_certificate.py',
                ['--primary','work59/verification/period_certificate.json','--output','work59/verification/independent_period_certificate.json'],
                'work59/verification/independent_period_certificate.json')]
            for label,script,argv,target in jobs:
                ref=json.loads((root/target).read_text());out=scratch/target;out.unlink(missing_ok=True)
                digest=sha(scratch/script)
                row=execute(label,[sys.executable,script,*argv],scratch,a.timeout_seconds,result)
                need(row['exit_code']==0 and out.exists(),label+': missing successful output')
                need(json.loads(out.read_text())==ref,label+': complete output differs')
                need(sha(scratch/script)==digest,label+': scientific source mutated')
                row.update(status='PASS_EXACT_REPLAY',script_sha256=digest,result_sha256=sha(out),reference_sha256=sha(root/target))
                print(label+': PASS_EXACT_REPLAY',flush=True)
            # Separate arithmetic corruption controls, not merely checksum mismatches.
            corrupt=json.loads((scratch/'work59/verification/period_certificate.json').read_text())
            corrupt['universe'][0]['phi_is_49_power']=True
            bad=tmp/'wrong_period.json';bad.write_text(json.dumps(corrupt));out=tmp/'reject_period_output.json'
            row=execute('altered_period_membership_negative_control',
                [sys.executable,'work59/computations/independent_period_certificate.py','--primary',str(bad),'--output',str(out)],
                scratch,a.timeout_seconds,result)
            need(row['exit_code']!=0 and not out.exists(),'Altered period membership was accepted')
            row['status']='PASS_EXPECTED_ARITHMETIC_REJECTION'
            source=scratch/'work59/source_records/frozen_block58_reciprocity.json'
            frozen=json.loads(source.read_text());frozen['matrix_mod7'][11][0]=(frozen['matrix_mod7'][11][0]+1)%7
            source.write_text(json.dumps(frozen));out=tmp/'reject_log_output.json'
            row=execute('altered_residue_row_negative_control',
                [sys.executable,'work59/computations/independent_period_certificate.py',
                '--primary','work59/verification/period_certificate.json','--output',str(out)],scratch,a.timeout_seconds,result)
            need(row['exit_code']!=0 and not out.exists(),'Altered residue log was accepted')
            row['status']='PASS_EXPECTED_ARITHMETIC_REJECTION'
        after=snapshot(root);need(before==after,'Immutable payload changed')
        result['input_hashes_after']=after;result['integrity_after']=audit(root);result['status']='PASS_DECLARED_CHECKS'
    except TimeoutError as e:result['status']='INCONCLUSIVE_TIMEOUT';result['error']=str(e)
    except Exception as e:result['status']='FAILED_VERIFICATION';result['error']=f'{type(e).__name__}: {e}'
    finally:
        result['elapsed_seconds']=time.monotonic()-tick;result['finished_utc']=datetime.now(timezone.utc).isoformat()
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']+'\nReport: '+str(report),flush=True)
    return 0 if result['status']=='PASS_DECLARED_CHECKS' else 2
if __name__=='__main__':raise SystemExit(main())
