#!/usr/bin/env python3
"""Replay Block69 exact computations; no cached PASS flag substitutes for fresh outputs."""
from __future__ import annotations
import argparse,concurrent.futures,datetime,hashlib,io,json,os,pathlib,platform,shutil,subprocess,sys,tempfile,time,zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise AssertionError(msg)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,d):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def integrity(root):
 m=load(root/'MANIFEST.json')['payload_sha256'];actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
 need(actual==set(m)|{'MANIFEST.json'},'Package member set changed')
 for n,h in m.items():need(sha(root/n)==h,'Payload hash changed: '+n)
 return {'status':'PASS','payload_hashes':len(m),'member_count':len(actual)}
def inherited(root):
 d=load(root/'work69/source_records/INHERITED_INPUTS.json');zpath=root/'predecessor'/d['predecessor'];need(sha(zpath)==d['sha256'],'Predecessor bytes changed')
 with zipfile.ZipFile(zpath) as z:
  for p in d['pinned_members']:need(hashlib.sha256(z.read(p['member'])).hexdigest()==p['sha256'],'Inherited source changed: '+p['member'])
  for dst,src in d['copied_mappings'].items():need((root/dst).read_bytes()==z.read(src),'Copied inherited input changed: '+dst)
 return {'predecessor_sha256':d['sha256'],'pinned_immediate_members':len(d['pinned_members']),'copied_modules_and_inputs':len(d['copied_mappings']),'status':'PASS'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--report',type=pathlib.Path,required=True);p.add_argument('--integrity-only',action='store_true');p.add_argument('--replay-predecessors',action='store_true');p.add_argument('--job-timeout',type=float,default=300);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
 need(ROOT not in a.report.resolve().parents and a.report.resolve()!=ROOT,'Report must be outside immutable package')
 t=time.monotonic();report={'schema':'beal.block69.verification.v1','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'jobs':[],'negative_controls':[],'limitations':['Written conditional arithmetic conclusions; no new Lean compilation or external mathematical reviewer.','Default replay regenerates Block69 only. The observed Block68 replay is separately recorded; no full earlier historical rerun is implied.']}
 try:
  report['integrity']=integrity(ROOT);report['inherited_inputs']=inherited(ROOT)
  if not a.integrity_only:
   spec=load(ROOT/'work69/inputs/new_tests.json');qs=spec['test_order'];outputs=[f'{prefix}_{q}.json' for q in qs for prefix in ['count','independent_count']]+['columns69.json','independent_columns69.json','refinement69.json','independent_refinement69.json','support69.json','exploratory_inert69.json']
   with tempfile.TemporaryDirectory(prefix='beal69_replay_') as tmp:
    scratch=pathlib.Path(tmp)/'project';shutil.copytree(ROOT,scratch);v=scratch/'work69/verification';c=scratch/'work69/computations';inp=scratch/'work69/inputs'
    expected={n:sha(v/n) for n in outputs};expected_fixture=sha(inp/'fixture69.json')
    for n in outputs:(v/n).unlink()
    (inp/'fixture69.json').unlink()
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1';env['MKL_NUM_THREADS']='1'
    def run(name,script,args,reject=None,timeout=None):
     argv=[sys.executable,'-B',str(script),*map(str,args)];start=time.monotonic()
     try:r=subprocess.run(argv,cwd=scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout or a.job_timeout,check=False)
     except subprocess.TimeoutExpired as e:
      report['jobs'].append({'name':name,'argv':argv,'status':'TIMEOUT_INCONCLUSIVE','elapsed_seconds':time.monotonic()-start});raise RuntimeError('Timeout is inconclusive: '+name) from e
     event={'name':name,'argv':argv,'returncode':r.returncode,'elapsed_seconds':time.monotonic()-start,'output':r.stdout};report['jobs'].append(event)
     if reject is None:need(r.returncode==0,'Execution failed: '+name+'\n'+r.stdout[-3000:])
     else:
      need(r.returncode!=0 and reject in r.stdout,'Negative control wrong rejection: '+name+'\n'+r.stdout[-3000:]);report['negative_controls'].append({'name':name,'diagnostic':reject,'rejected':True})
     print(name,r.returncode,round(event['elapsed_seconds'],3),flush=True)
    def count_pair(q):
     run('counts_'+str(q),c/'count69.py',['--spec',inp/'new_tests.json','--q',q,'--output',v/f'count_{q}.json'])
     run('separate_counts_'+str(q),c/'independent_count69.py',['--spec',inp/'new_tests.json','--counts',v/f'count_{q}.json','--output',v/f'independent_count_{q}.json'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(2,a.workers))) as pool:list(pool.map(count_pair,qs))
    run('assemble_fixture',c/'assemble69.py',['--base',inp/'frozen_fixture68.json','--spec',inp/'new_tests.json','--counts-dir',v,'--output',inp/'fixture69.json'])
    need(sha(inp/'fixture69.json')==expected_fixture,'Changed regenerated fixture')
    run('all_twisted_columns',c/'columns68.py',['--fixture',inp/'fixture69.json','--output',v/'columns69.json'])
    run('separate_all_columns',c/'independent_columns68.py',['--fixture',inp/'fixture69.json','--certificate',v/'columns69.json','--output',v/'independent_columns69.json'])
    refine_args=['--sieve',inp/'frozen_sieve68.json','--fixture',inp/'fixture69.json','--spec',inp/'new_tests.json']
    run('complete_refinement',c/'refine69.py',refine_args+['--columns',v/'columns69.json','--output',v/'refinement69.json'])
    independent_args=refine_args+['--counts-dir',v,'--columns',v/'independent_columns69.json']
    run('separate_complete_refinement',c/'independent_refine69.py',independent_args+['--certificate',v/'refinement69.json','--output',v/'independent_refinement69.json'])
    run('support_summary',c/'support69.py',['--refinement',v/'refinement69.json','--columns',v/'columns69.json','--counts-dir',v,'--output',v/'support69.json'])
    run('failed_inert_route',c/'exploratory_inert69.py',['--output',v/'exploratory_inert69.json'])
    for n,h in expected.items():need(sha(v/n)==h,'Regenerated scientific output mismatch: '+n)
    report['regenerated_output_sha256']={n:sha(v/n) for n in outputs};report['regenerated_fixture_sha256']=sha(inp/'fixture69.json');report['output_comparisons']=len(outputs);report['result']=load(v/'support69.json')
    neg=pathlib.Path(tmp)/'negative';neg.mkdir()
    d=load(v/'columns69.json');next(x for x in d['columns'] if x['q']==307)['rows']['1471']=(next(x for x in d['columns'] if x['q']==307)['rows']['1471']+1)%7;save(neg/'column.json',d)
    run('reject_changed_degree_two_column',c/'independent_columns68.py',['--fixture',inp/'fixture69.json','--certificate',neg/'column.json','--output',neg/'unused.json'],'Changed degree-dependent twisted column')
    d=load(v/'columns69.json');d['universe'].remove(1483);save(neg/'missing.json',d)
    run('reject_omitted_conductor',c/'independent_columns68.py',['--fixture',inp/'fixture69.json','--certificate',neg/'missing.json','--output',neg/'unused.json'],'Incomplete conductor universe')
    d=load(v/'refinement69.json');d['survivor_count']=0;d['survivors']=[];save(neg/'false_zero.json',d)
    run('reject_false_zero',c/'independent_refine69.py',independent_args+['--certificate',neg/'false_zero.json','--output',neg/'unused.json'],'Changed complete survivor list')
    d=load(v/'refinement69.json');d['minimum_support']=9;save(neg/'false_bound.json',d)
    run('reject_inflated_support_bound',c/'independent_refine69.py',independent_args+['--certificate',neg/'false_bound.json','--output',neg/'unused.json'],'Changed minimum support bound')
    d=load(inp/'fixture69.json');d['paired_trace_sets']['1471'].append([24,31]);save(neg/'false_pair.json',d)
    badargs=['--sieve',inp/'frozen_sieve68.json','--fixture',neg/'false_pair.json','--spec',inp/'new_tests.json','--counts-dir',v,'--columns',v/'independent_columns69.json','--certificate',v/'refinement69.json','--output',neg/'unused.json']
    run('reject_invented_polynomial_pair',c/'independent_refine69.py',badargs,'Changed common polynomial pairs')
    # The count corruption test uses a complete count recomputation, not merely its checksum.
    d=load(v/f'count_{qs[0]}.json');d['primes'][0]['rows'][0]['N1']+=1;save(neg/'false_count.json',d)
    run('reject_altered_point_count',c/'independent_count69.py',['--spec',inp/'new_tests.json','--counts',neg/'false_count.json','--output',neg/'unused.json'],'Point-count row mismatch')
    original=(scratch/'README.md').read_bytes();(scratch/'README.md').write_bytes(original+b'\nCORRUPTION\n')
    try:integrity(scratch)
    except AssertionError as e:
     need('Payload hash changed: README.md' in str(e),'Wrong payload rejection');report['negative_controls'].append({'name':'reject_altered_payload','diagnostic':str(e),'rejected':True})
    else:raise AssertionError('Changed payload accepted')
    finally:(scratch/'README.md').write_bytes(original)
    prior=load(ROOT/'work69/verification/Block68_Replay.json');exitrec=load(ROOT/'work69/verification/Block68_Replay_exit.json')
    need(prior['status']=='PASS_DECLARED_CHECKS' and exitrec['returncode']==0,'Recorded predecessor replay failed')
    report['recorded_predecessor_replay']={'status':prior['status'],'sha256':sha(ROOT/'work69/verification/Block68_Replay.json'),'elapsed_seconds':exitrec['elapsed_seconds'],'meaning':'Observed Block68 default replay during Block69 development. It is not a fresh historical-chain replay in this invocation.'}
    if a.replay_predecessors:
     parent=pathlib.Path(tmp)/'previous';parent.mkdir();pinned=load(ROOT/'work69/source_records/INHERITED_INPUTS.json')
     with zipfile.ZipFile(ROOT/'predecessor'/pinned['predecessor']) as z:
      for n in z.namelist():need(not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts,'Unsafe predecessor path')
      z.extractall(parent)
     run('fresh_selected_predecessor_chain',parent/'Komorebi_Beal_Block68/verify.py',['--replay-predecessors','--report',pathlib.Path(tmp)/'prior.json'],timeout=3600)
     report['fresh_predecessor_replay']=load(pathlib.Path(tmp)/'prior.json')
    need(integrity(ROOT)==report['integrity'],'Immutable release changed')
  report['status']='PASS_DECLARED_CHECKS'
 except Exception as e:
  report['status']='FAILED';report['error']=type(e).__name__+': '+str(e);print(report['error'],file=sys.stderr,flush=True)
 report['elapsed_seconds']=time.monotonic()-t;report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(a.report,report);print(report['status'],flush=True)
 return 0 if report['status']=='PASS_DECLARED_CHECKS' else 1
if __name__=='__main__':raise SystemExit(main())
