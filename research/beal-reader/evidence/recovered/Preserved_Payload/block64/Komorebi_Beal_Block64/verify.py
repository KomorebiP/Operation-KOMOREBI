#!/usr/bin/env python3
"""Rebuild Block64 exact certificates and, optionally, the frozen predecessor chain."""
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
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
    need(actual==set(manifest['sha256']),'Payload member set mismatch')
    for name,sha in manifest['sha256'].items():need(digest(root/name)==sha,'Payload SHA256 mismatch: '+name)
    rec=json.loads((root/'work64/source_records/INHERITED_INPUTS.json').read_text())
    pred=next((root/'predecessor').glob('*.zip'));need(digest(pred)==rec['predecessor_sha256'],'Predecessor bytes changed')
    blobs={():pred.read_bytes()};leaf_data={}
    for row in rec['files']:
        chain=tuple(row['archive_chain'])
        for i in range(1,len(chain)+1):
            key=chain[:i]
            if key not in blobs:
                with zipfile.ZipFile(io.BytesIO(blobs[key[:-1]])) as z:blobs[key]=z.read(key[-1])
        with zipfile.ZipFile(io.BytesIO(blobs[chain])) as z:b=z.read(row['member'])
        need(hashlib.sha256(b).hexdigest()==row['sha256'],'Inherited source hash mismatch: '+row['member'])
        leaf_data[row['member']]=b
    fixture=json.loads((root/'work64/source_records/inherited_trace_sets.json').read_text())
    old=json.loads(leaf_data['Komorebi_Beal_Block63/work63/source_records/inherited_trace_sets.json'])
    need(all(fixture[k]==v for k,v in old.items()),'Inherited union/Kummer fixture changed')
    raw=leaf_data['Komorebi_Beal_Block62/work62/verification/pointcounts.json']
    need(fixture['source_pointcounts_sha256']==hashlib.sha256(raw).hexdigest(),'Paired-source hash mismatch')
    data=json.loads(raw)
    pairs={str(p['q']):[list(t) for t in sorted({tuple(r['defect_roots']) for r in p['rows'] if r['residual_pass']})] for p in data['primes']}
    need(pairs==fixture['paired_trace_sets'],'Paired-polynomial fixture changed')
    need(not rec['missing'],'Missing inherited source')
    return {'payload_files':len(actual),'inherited_leaf_files':len(rec['files']),
        'nested_archives_opened':len(blobs),'predecessor_sha256':digest(pred)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--integrity-only',action='store_true');ap.add_argument('--replay-predecessors',action='store_true')
    ap.add_argument('--report',type=Path);ap.add_argument('--job-timeout',type=int,default=1200)
    a=ap.parse_args();t0=time.monotonic();jobs=[]
    result={'schema':'beal.block64.verification.v1','status':'RUNNING','started_unix':time.time(),
            'python':sys.version,'platform':platform.platform(),'cpu_count_visible':os.cpu_count(),
            'job_timeout_seconds':a.job_timeout,'replay_predecessors':a.replay_predecessors,
            'limits':'Per-job wall-clock timeout. Standard-library exact arithmetic. Timeout means inconclusive.'}
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
            with tempfile.TemporaryDirectory(prefix='beal64_') as td:
                tmp=Path(td);scratch=tmp/'package';shutil.copytree(ROOT,scratch)
                C=scratch/'work64/computations';V=scratch/'work64/verification';F=scratch/'work64/source_records/inherited_trace_sets.json'
                outputs=['count281.json','independent_count281.json','conductor64.json','independent_conductor64.json','algebra64.json']
                for name in outputs:(V/name).unlink()
                run([C/'count281.py','--output',V/'count281.json'],scratch)
                run([C/'independent_count281.py','--counts',V/'count281.json','--output',V/'independent_count281.json'],scratch)
                run([C/'conductor64.py','--fixture',F,'--counts',V/'count281.json','--output',V/'conductor64.json'],scratch)
                run([C/'independent_conductor64.py','--fixture',F,'--counts',V/'count281.json','--certificate',V/'conductor64.json','--output',V/'independent_conductor64.json'],scratch)
                run([C/'algebra64.py','--output',V/'algebra64.json'],scratch)
                for name in outputs:
                    need(json.loads((V/name).read_text())==json.loads((ROOT/'work64/verification'/name).read_text()),'Full JSON replay mismatch: '+name)
                result['complete_json_replays']=outputs
                bad=tmp/'negative';bad.mkdir()
                j=json.loads((V/'count281.json').read_text());j['primes'][0]['rows'][0]['N1']+=1
                (bad/'count.json').write_text(json.dumps(j))
                run([C/'independent_count281.py','--counts',bad/'count.json','--output',bad/'out.json'],scratch,True,'Point-count row mismatch')
                j=json.loads((V/'conductor64.json').read_text());row=next(x for x in j['columns'] if x['q']==113);row['rows']['281']=(row['rows']['281']+1)%7
                (bad/'column.json').write_text(json.dumps(j))
                def check_bad(file,needle):
                    run([C/'independent_conductor64.py','--fixture',F,'--counts',V/'count281.json','--certificate',file,'--output',bad/'out.json'],scratch,True,needle)
                check_bad(bad/'column.json','Changed twisted row or Kummer ratio')
                j=json.loads((V/'conductor64.json').read_text());j['cases']['expanded_exclusion']['count']=1
                (bad/'survivor.json').write_text(json.dumps(j));check_bad(bad/'survivor.json','Independent survivor list differs')
                j=json.loads((V/'conductor64.json').read_text());j['paired_trace_sets']['211'].append([29,24])
                (bad/'pair.json').write_text(json.dumps(j));check_bad(bad/'pair.json','Changed source trace sets')
                (scratch/'README.md').write_text((scratch/'README.md').read_text()+'\nALTERED PAYLOAD\n')
                run([scratch/'verify.py','--integrity-only','--report',bad/'payload_report.json'],scratch,True,'Payload SHA256 mismatch')
                result['negative_controls']=['changed_point_count','changed281_twisted_column','invented_exclusion_survivor','false_common_polynomial_pair','altered_payload']
                if a.replay_predecessors:
                    olddir=tmp/'old';olddir.mkdir();safe_extract(next((ROOT/'predecessor').glob('*.zip')),olddir)
                    old=olddir/'Komorebi_Beal_Block63';rp=tmp/'Block63_Replay.json'
                    run([old/'verify.py','--replay-predecessors','--report',rp],old)
                    prior=json.loads(rp.read_text());need(prior.get('status')=='PASS','Unexpected predecessor status')
                    result['predecessor_replay']=prior
        result['status']='PASS'
    except subprocess.TimeoutExpired as exc:
        result['status']='INCONCLUSIVE_TIMEOUT';result['error']=str(exc);print(str(exc),file=sys.stderr)
    except Exception as exc:
        result['status']='FAIL';result['error']=str(exc);print(str(exc),file=sys.stderr)
    result['jobs']=jobs;result['elapsed_seconds']=time.monotonic()-t0;result['finished_unix']=time.time()
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],flush=True)
    return 0 if result['status']=='PASS' else (3 if result['status']=='INCONCLUSIVE_TIMEOUT' else 2)
if __name__=='__main__':sys.exit(main())
