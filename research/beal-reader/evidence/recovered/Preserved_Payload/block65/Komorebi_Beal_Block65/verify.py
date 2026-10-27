#!/usr/bin/env python3
"""Rebuild Block65 certificates and optionally the byte-preserved predecessor chain."""
from __future__ import annotations
import argparse,hashlib,io,json,os,platform,shutil,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise AssertionError(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_extract(source,dest):
    with zipfile.ZipFile(source) as z:
        need(z.testzip() is None,'ZIP CRC failure')
        for name in z.namelist():need((dest/name).resolve().is_relative_to(dest.resolve()),'Unsafe ZIP path')
        z.extractall(dest)
def integrity(root):
    manifest=json.loads((root/'MANIFEST.json').read_text())
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix()!='MANIFEST.json'}
    need(actual==set(manifest['sha256']),'Payload member set mismatch')
    for name,sha in manifest['sha256'].items():need(digest(root/name)==sha,'Payload SHA256 mismatch: '+name)
    rec=json.loads((root/'work65/source_records/INHERITED_INPUTS.json').read_text())
    archives=list((root/'predecessor').glob('*.zip'));need(len(archives)==1,'Expected one frozen predecessor')
    pred=archives[0];need(digest(pred)==rec['predecessor_sha256'],'Predecessor bytes changed')
    with zipfile.ZipFile(pred) as z:
        leaf={}
        for row in rec['files']:
            b=z.read(row['member']);need(hashlib.sha256(b).hexdigest()==row['sha256'],'Inherited source mismatch '+row['member']);leaf[row['member']]=b
    prefix='Komorebi_Beal_Block64/'
    expected=json.loads(leaf[prefix+'work64/source_records/inherited_trace_sets.json'])
    counts=json.loads(leaf[prefix+'work64/verification/count281.json'])['primes'][0]
    conduct=json.loads(leaf[prefix+'work64/verification/conductor64.json'])
    expected['good_trace_sets']['281']=counts['trace_defect_set']
    expected['kummer_rows']['281']=conduct['kummer281']
    expected['paired_trace_sets']['281']=conduct['paired_trace_sets']['281']
    expected['inherited_coupled_survivors']=conduct['cases']['outside743_coupled']['survivors']
    fixture=json.loads((root/'work65/source_records/inherited_fixture.json').read_text())
    need(fixture==expected,'Merged inherited fixture differs')
    return {'payload_files':len(actual),'immediate_inherited_source_files':len(rec['files']),
            'predecessor_sha256':digest(pred),'fixture_derivation':'exactly matched'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--integrity-only',action='store_true');ap.add_argument('--replay-predecessors',action='store_true')
    ap.add_argument('--report',type=Path);ap.add_argument('--job-timeout',type=int,default=600)
    a=ap.parse_args();start=time.monotonic();jobs=[]
    result={'schema':'beal.block65.verification.v1','status':'RUNNING','started_unix':time.time(),
            'python':sys.version,'platform':platform.platform(),'cpu_count_visible':os.cpu_count(),
            'job_timeout_seconds':a.job_timeout,'replay_predecessors':a.replay_predecessors,
            'limits':'Per-job wall-clock cap. Standard-library exact arithmetic. Timeout is inconclusive.'}
    try:
        result['integrity']=integrity(ROOT)
        if not a.integrity_only:
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONOPTIMIZE='0')
            def run(args,cwd,negative=False,needle=None):
                argv=[sys.executable,'-B']+list(map(str,args));ts=time.monotonic()
                p=subprocess.run(argv,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=a.job_timeout)
                jobs.append({'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'elapsed_seconds':time.monotonic()-ts,
                             'expected_rejection':negative,'output':p.stdout})
                print('NEGATIVE' if negative else 'REPLAY',Path(argv[2]).name,p.returncode,flush=True)
                if negative:
                    need(p.returncode!=0,'Malformed input accepted')
                    if needle:need(needle in p.stdout,'Wrong rejection reason: '+str(needle))
                else:need(p.returncode==0,'Scientific job failed: '+str(args[0]))
                return p
            with tempfile.TemporaryDirectory(prefix='beal65_') as td:
                tmp=Path(td);scratch=tmp/'package';shutil.copytree(ROOT,scratch)
                C=scratch/'work65/computations';V=scratch/'work65/verification';F=scratch/'work65/source_records/inherited_fixture.json'
                outputs=['count379.json','independent_count379.json','conductor65.json','independent_conductor65.json','rigidity65.json','independent_rigidity65.json']
                for n in outputs:(V/n).unlink()
                run([C/'count379.py','--output',V/'count379.json'],scratch)
                run([C/'independent_count379.py','--counts',V/'count379.json','--output',V/'independent_count379.json'],scratch)
                run([C/'rigidity65.py','--output',V/'rigidity65.json'],scratch)
                run([C/'independent_rigidity65.py','--certificate',V/'rigidity65.json','--output',V/'independent_rigidity65.json'],scratch)
                run([C/'conductor65.py','--fixture',F,'--counts',V/'count379.json','--output',V/'conductor65.json'],scratch)
                run([C/'independent_conductor65.py','--fixture',F,'--counts',V/'count379.json','--certificate',V/'conductor65.json','--output',V/'independent_conductor65.json'],scratch)
                for n in outputs:
                    need(json.loads((V/n).read_text())==json.loads((ROOT/'work65/verification'/n).read_text()),'Complete JSON replay mismatch: '+n)
                result['complete_json_replays']=outputs
                bad=tmp/'negative';bad.mkdir()
                d=json.loads((V/'count379.json').read_text());d['primes'][0]['rows'][0]['N1']+=1
                (bad/'counts.json').write_text(json.dumps(d))
                run([C/'independent_count379.py','--counts',bad/'counts.json','--output',bad/'out.json'],scratch,True,'Point-count row mismatch')
                def corrupt_conductor(name,modify,needle):
                    d=json.loads((V/'conductor65.json').read_text());modify(d);p=bad/name;p.write_text(json.dumps(d))
                    run([C/'independent_conductor65.py','--fixture',F,'--counts',V/'count379.json','--certificate',p,'--output',bad/'out.json'],scratch,True,needle)
                def change_column(d):
                    z=next(z for z in d['columns'] if z['q']==547);z['rows']['379']=(z['rows']['379']+1)%7
                corrupt_conductor('column.json',change_column,'Changed twisted row or Kummer ratio')
                corrupt_conductor('count.json',lambda d:d['cases']['complete25_boundary'].__setitem__('count',0),'Independent survivor mismatch')
                corrupt_conductor('pair.json',lambda d:d['paired_trace_sets']['379'].append([17,38]),'Changed input paired_trace_sets')
                d=json.loads((V/'rigidity65.json').read_text());d['accepted_triples'].append([1,1,7])
                (bad/'rigidity.json').write_text(json.dumps(d))
                run([C/'independent_rigidity65.py','--certificate',bad/'rigidity.json','--output',bad/'out.json'],scratch,True,'Changed rigidity classification')
                (scratch/'README.md').write_text((scratch/'README.md').read_text()+'\nALTERED PAYLOAD\n')
                run([scratch/'verify.py','--integrity-only','--report',bad/'payload.json'],scratch,True,'Payload SHA256 mismatch')
                result['negative_controls']=['changed_point_count','changed_twisted_column','false_zero_survivor_count','invented_common_polynomial_pair','invalid_coefficient_triple','altered_payload']
                if a.replay_predecessors:
                    olddir=tmp/'predecessor';olddir.mkdir();safe_extract(next((ROOT/'predecessor').glob('*.zip')),olddir)
                    old=olddir/'Komorebi_Beal_Block64';rp=tmp/'Block64_Replay.json'
                    run([old/'verify.py','--replay-predecessors','--report',rp],old)
                    prior=json.loads(rp.read_text());need(prior.get('status')=='PASS','Unexpected predecessor status')
                    result['predecessor_replay']=prior
        result['status']='PASS'
    except subprocess.TimeoutExpired as exc:
        result['status']='INCONCLUSIVE_TIMEOUT';result['error']=str(exc);print(str(exc),file=sys.stderr)
    except Exception as exc:
        result['status']='FAIL';result['error']=str(exc);print(str(exc),file=sys.stderr)
    result['jobs']=jobs;result['elapsed_seconds']=time.monotonic()-start;result['finished_unix']=time.time()
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],flush=True)
    return 0 if result['status']=='PASS' else (3 if result['status']=='INCONCLUSIVE_TIMEOUT' else 2)
if __name__=='__main__':sys.exit(main())
