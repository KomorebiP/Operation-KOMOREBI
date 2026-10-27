#!/usr/bin/env python3
"""Replay the bounded Block62 certificates. Python3.10+, standard library only.
Write reports outside the immutable package. Timeouts are inconclusive.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,os,platform,shutil,signal,stat
import subprocess,sys,tempfile,time,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath

PREDECESSOR='Komorebi_Beal_Block61_Twisted_Opposite_Depth_Two_Closure_v6.1.0.zip'
EXPECTED='a46b848be4b5406d413b7fdeaa1b88e4d1be823942cb71e4e86c7e3e809f21c8'
MANIFEST='PACKAGE_SHA256SUMS.txt'

def need(ok,message):
    if not ok:raise AssertionError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(root):
    out={}
    for p in sorted(root.rglob('*')):
        need(not p.is_symlink(),'Symlink in package: '+str(p))
        if p.is_file() and p.relative_to(root).as_posix()!=MANIFEST:
            out[p.relative_to(root).as_posix()]=sha(p)
    return out

def audit(root):
    records={}
    for line in (root/MANIFEST).read_text().splitlines():
        digest,name=line.split('  ',1);p=PurePosixPath(name)
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
    rec=json.loads((root/'work62/source_records/INHERITED_INPUT_HASHES.json').read_text())
    need(rec['sha256']==EXPECTED and rec['predecessor']==PREDECESSOR,'Wrong pinned predecessor')
    initial=(root/'predecessor'/PREDECESSOR).read_bytes();cache={():initial}
    for row in rec['named_inputs']:
        chain=row['member_chain']
        for j,name in enumerate(chain):
            prefix=tuple(chain[:j]);key=tuple(chain[:j+1])
            if key not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[prefix])) as z:cache[key]=z.read(name)
        val=cache[tuple(chain)]
        need(len(val)==row['bytes'] and hashlib.sha256(val).hexdigest()==row['sha256'],
             'Named inherited source changed: '+chain[-1])
    current=initial
    for row in rec['nested_archive_lineage']:
        need(len(current)==row['bytes'] and hashlib.sha256(current).hexdigest()==row['sha256'],
             'Nested archive changed: '+str(row['block']))
        with zipfile.ZipFile(io.BytesIO(current)) as z:
            need(len(z.namelist())==row['zip_members'],'Nested member count changed')
            if row['block']>51:
                children=[n for n in z.namelist() if '/predecessor/' in n and n.endswith('.zip')]
                need(len(children)==1,'Ambiguous nested lineage');current=z.read(children[0])
    return {'status':'PASS_NAMED_INPUTS','named_sources':len(rec['named_inputs']),
            'lineage_archives':len(rec['nested_archive_lineage']),'hashes_not_mathematical_proofs':True}

def extract_safely(src,dest):
    with zipfile.ZipFile(src) as z:
        seen=set()
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            need(not p.is_absolute() and '..' not in p.parts and chr(92) not in i.filename,'Unsafe ZIP path')
            need(i.filename not in seen,'Duplicate ZIP path');seen.add(i.filename)
            need(not stat.S_ISLNK(i.external_attr>>16),'ZIP symlink refused')
        need(z.testzip() is None,'ZIP CRC error');z.extractall(dest)

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
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--replay-predecessors',action='store_true')
    ap.add_argument('--report',type=Path)
    ap.add_argument('--timeout-seconds',type=float,default=180)
    a=ap.parse_args();root=Path(__file__).resolve().parent
    out=(a.report or root.parent/'Block62_Replay.json').resolve()
    need(not out.is_relative_to(root),'Report must be outside the immutable package')
    need(math.isfinite(a.timeout_seconds) and a.timeout_seconds>0,'Invalid wall timeout')
    result={'schema':'komorebi.beal.block62.replay.v1','status':'NOT_COMPLETED',
      'argv':sys.argv,'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
      'python_executable':sys.executable,'platform':platform.platform(),
      'arithmetic':'exact integers, finite fields, O/49, cyclotomic integers',
      'random_seed':None,'numerical_tolerance':None,'runs':[],
      'resource_caps':{'per_job_wall_seconds':a.timeout_seconds,'predecessor_wall_seconds':15*a.timeout_seconds,
        'additional_cpu_limit':None,'additional_memory_limit':None},
      'nonclaims':['No Beal solution','No universal depth-one exclusion',
        'No elimination of all complete H(C) subset U cases',
        'No new Lean compilation','No independent mathematical review',
        'Inherited geometry, Kummer and class-group inputs not independently proved']}
    start=time.monotonic()
    try:
        result['integrity_before']=audit(root);result['named_inherited_inputs']=audit_inherited(root)
        before=snapshot(root);result['input_hashes_before']=before
        with tempfile.TemporaryDirectory(prefix='beal62-') as td:
            tmp=Path(td)
            if a.replay_predecessors:
                extract_safely(root/'predecessor'/PREDECESSOR,tmp/'old')
                old=tmp/'old/Komorebi_Beal_Block61';report=tmp/'Block61_Replay.json'
                run=execute('block61_and_selected_nested_predecessors',
                    [sys.executable,'verify.py','--replay-predecessors','--report',str(report),
                     '--timeout-seconds',str(a.timeout_seconds)],old,15*a.timeout_seconds,result)
                if report.exists():result['predecessor_replay']=json.loads(report.read_text())
                if result.get('predecessor_replay',{}).get('status')=='INCONCLUSIVE_TIMEOUT':
                    raise TimeoutError('Nested predecessor timeout')
                need(run['exit_code']==0 and report.exists(),'Predecessor failed')
                need(result['predecessor_replay']['status']=='PASS_DECLARED_CHECKS','Predecessor not verified')
                run['status']='PASS_PREDECESSOR_REPLAY';print('predecessor: PASS',flush=True)
            else:result['predecessor_replay']={'status':'NOT_REQUESTED','byte_integrity_checked':True}
            scratch=tmp/'scratch';shutil.copytree(root,scratch)
            V='work62/verification/';C='work62/computations/'
            pc=V+'pointcounts.json';tr=V+'trace_product.json';lo=V+'low_congruence_extension.json'
            jobs=[
              ('pointcounts',C+'pointcounts.py',pc,[]),
              ('trace_product',C+'trace_product_certificate.py',tr,['--pointcounts',pc]),
              ('independent_count_residue_sieve',C+'independent_check.py',V+'independent_check.json',
                ['--pointcounts',pc,'--trace',tr]),
              ('matrix_identity',C+'matrix_checks.py',V+'matrix_checks.json',[]),
              ('low_congruence_extension',C+'low_congruence_extension.py',lo,['--base',tr]),
              ('independent_low_extension',C+'independent_low_extension.py',V+'independent_low_extension.json',
                ['--extension',lo,'--base',tr])]
            for label,script,target,extra in jobs:
                reference=json.loads((root/target).read_text());dest=scratch/target;dest.unlink()
                digest=sha(scratch/script)
                run=execute(label,[sys.executable,script,*extra,'--output',str(dest)],scratch,a.timeout_seconds,result)
                need(run['exit_code']==0 and dest.exists(),label+': process failed')
                need(json.loads(dest.read_text())==reference,label+': complete JSON differs')
                need(sha(scratch/script)==digest,'Scientific source changed')
                run.update(status='PASS_EXACT_REPLAY',script_sha256=digest,result_sha256=sha(dest),
                           expected_result_sha256=sha(root/target))
                print(label+': PASS_EXACT_REPLAY',flush=True)
            # Each negative input reaches an arithmetic assertion in the separate checker.
            controls=[
              ('altered_point_count',pc,lambda d:d['primes'][0]['rows'][0].__setitem__('N1',31),
               C+'independent_check.py','--pointcounts',['--trace',tr]),
              ('altered_twisted_residue',tr,lambda d:d['residue_evaluations']['29']['197']['residues'].__setitem__(0,0),
               C+'independent_check.py','--trace',['--pointcounts',pc]),
              ('invented_239_survivor',tr,lambda d:d['checkpoints']['239'].append({'alpha':[0,1,1],'beta':[0,2,6,2]}),
               C+'independent_check.py','--trace',['--pointcounts',pc]),
              ('altered_low_congruence_column',lo,lambda d:d['frobenius_rows']['29'].__setitem__(4,0),
               C+'independent_low_extension.py','--extension',['--base',tr])]
            for label,target,mutate,script,flag,extra in controls:
                data=json.loads((scratch/target).read_text());mutate(data)
                bad=tmp/(label+'.json');bad.write_text(json.dumps(data));reject_out=tmp/(label+'_output.json')
                run=execute(label,[sys.executable,script,flag,str(bad),*extra,'--output',str(reject_out)],
                    scratch,a.timeout_seconds,result)
                need(run['exit_code']!=0 and not reject_out.exists(),'Altered arithmetic accepted: '+label)
                need('AssertionError' in run['stderr'],'Rejection did not reach arithmetic assertion: '+label)
                run['status']='PASS_EXPECTED_ARITHMETIC_REJECTION'
                print(label+': PASS_EXPECTED_REJECTION',flush=True)
            corrupt=tmp/'corrupt';shutil.copytree(root,corrupt)
            f=corrupt/'work62/notes/DEPTH_ONE_EXCLUSION.md';f.write_text(f.read_text()+'\nTAMPER\n')
            try:audit(corrupt)
            except AssertionError as e:
                need(str(e)=='Payload hash mismatch: work62/notes/DEPTH_ONE_EXCLUSION.md','Wrong corruption failure')
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
