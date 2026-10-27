#!/usr/bin/env python3
"""Rebuild Block70's finite certificates in scratch space, then test rejection paths.
This verifies the declared computations, not the upstream analytical or Galois proofs.
"""
from __future__ import annotations
import argparse, concurrent.futures, datetime, hashlib, json, os, pathlib, platform, shutil, subprocess, sys, tempfile, time, zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise AssertionError(msg)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
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
 d=load(root/'work70/source_records/INHERITED_INPUTS.json');p=root/'predecessor'/d['predecessor'];need(sha(p)==d['sha256'],'Predecessor bytes changed')
 with zipfile.ZipFile(p) as z:
  for x in d['pinned_members']:need(hashlib.sha256(z.read(x['member'])).hexdigest()==x['sha256'],'Inherited source changed: '+x['member'])
  for dst,src in d['copied_mappings'].items():need((root/dst).read_bytes()==z.read(src),'Copied inherited input changed: '+dst)
 return {'status':'PASS','predecessor_sha256':d['sha256'],'pinned_immediate_members':len(d['pinned_members']),'copied_modules_and_inputs':len(d['copied_mappings'])}

def main():
 p=argparse.ArgumentParser();p.add_argument('--report',type=pathlib.Path,required=True);p.add_argument('--integrity-only',action='store_true');p.add_argument('--replay-predecessors',action='store_true');p.add_argument('--workers',type=int,default=2);p.add_argument('--job-timeout',type=float,default=600);a=p.parse_args()
 need(a.report.resolve()!=ROOT and ROOT not in a.report.resolve().parents,'Report must be outside immutable package')
 started=time.monotonic();report={'schema':'beal.block70.verification.v1','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'cpu_count':os.cpu_count(),'workers':max(1,min(2,a.workers)),'jobs':[],'negative_controls':[],'limitations':['Conditional arithmetic conclusions; no new Lean or independent mathematical review.','Default rebuilds Block70 only. The separately observed Block69 replay is retained, not a fresh historical-chain assertion.','Target-specific N2 coverage does not claim the complete good Frobenius polynomial set.','The abstract escape vector is not an actual global Frey representation or integer solution.']}
 try:
  report['integrity']=integrity(ROOT);report['inherited_inputs']=inherited(ROOT)
  if not a.integrity_only:
   qs=load(ROOT/'work70/inputs/new_tests.json')['test_order'];names=['columns70.json','independent_columns70.json','refinement70.json','independent_refinement70.json','finite_sieve_limit70.json','independent_sieve_limit70.json']+[f'{t}_{q}.json' for q in qs for t in ['targeted','independent_targeted']]
   with tempfile.TemporaryDirectory(prefix='beal70_replay_') as td:
    scratch=pathlib.Path(td)/'project';shutil.copytree(ROOT,scratch);W=scratch/'work70';C=W/'computations';I=W/'inputs';V=W/'verification';N=pathlib.Path(td)/'negative';N.mkdir()
    expected={n:sha(V/n) for n in names};expected_fixture=sha(I/'fixture70.json')
    for n in names:(V/n).unlink()
    (I/'fixture70.json').unlink()
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def run(name,script,args,reject=None,timeout=None,cwd=None):
     argv=[sys.executable,'-B',str(script),*map(str,args)];t=time.monotonic()
     try:r=subprocess.run(argv,cwd=cwd or scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout or a.job_timeout,check=False)
     except subprocess.TimeoutExpired as e:
      report['jobs'].append({'name':name,'argv':argv,'status':'TIMEOUT_INCONCLUSIVE','elapsed_seconds':time.monotonic()-t});raise RuntimeError('Timeout is inconclusive: '+name) from e
     event={'name':name,'argv':argv,'returncode':r.returncode,'elapsed_seconds':time.monotonic()-t,'output':r.stdout};report['jobs'].append(event)
     if reject is None:need(r.returncode==0,'Execution failed: '+name+'\n'+r.stdout[-3000:])
     else:
      need(r.returncode!=0 and reject in r.stdout,'Wrong negative-control rejection: '+name+'\n'+r.stdout[-3000:]);report['negative_controls'].append({'name':name,'diagnostic':reject,'rejected':True})
     print(name,r.returncode,round(event['elapsed_seconds'],3),flush=True)
    run('prepare_fixture',C/'prepare70.py',['--base',I/'frozen_fixture69.json','--spec',I/'new_tests.json','--output',I/'fixture70.json'])
    need(sha(I/'fixture70.json')==expected_fixture,'Generated fixture changed')
    run('all_twisted_columns',C/'columns68.py',['--fixture',I/'fixture70.json','--output',V/'columns70.json'])
    ci=['--fixture',I/'fixture70.json']
    run('independent_columns',C/'independent_columns68.py',ci+['--certificate',V/'columns70.json','--output',V/'independent_columns70.json'])
    def primary_args(q,out):return ['--q',q,'--sieve',I/'frozen_refinement69.json','--fixture',I/'fixture70.json','--columns',V/'columns70.json','--output',out]
    def secondary_args(inp,out):return ['--counts',inp,'--sieve',I/'frozen_refinement69.json','--fixture',I/'fixture70.json','--columns',V/'independent_columns70.json','--output',out]
    def counts(q):
     run('primary_target_'+str(q),C/'targeted_count70.py',primary_args(q,V/f'targeted_{q}.json'))
     run('independent_target_'+str(q),C/'independent_targeted70.py',secondary_args(V/f'targeted_{q}.json',V/f'independent_targeted_{q}.json'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(2,a.workers))) as pool:list(pool.map(counts,qs))
    ri=['--sieve',I/'frozen_refinement69.json','--spec',I/'new_tests.json','--counts-dir',V]
    run('refinement',C/'refine70.py',ri+['--output',V/'refinement70.json'])
    run('independent_refinement',C/'independent_refine70.py',ri+['--certificate',V/'refinement70.json','--output',V/'independent_refinement70.json'])
    run('abstract_escape',C/'finite_sieve_limit70.py',ci+['--output',V/'finite_sieve_limit70.json'])
    run('independent_abstract_escape',C/'independent_sieve_limit70.py',ci+['--certificate',V/'finite_sieve_limit70.json','--output',V/'independent_sieve_limit70.json'])
    for n,h in expected.items():need(sha(V/n)==h,'Regenerated output mismatch: '+n)
    report['regenerated_outputs']={n:sha(V/n) for n in names};report['regenerated_fixture_sha256']=sha(I/'fixture70.json');report['output_comparisons']=len(names);report['result']=load(V/'refinement70.json');report['abstract_escape']=load(V/'independent_sieve_limit70.json')
    # Tamper checks invoke the actual separate checker; no expected success flags suffice.
    d=load(V/'columns70.json');rec=next(c for c in d['columns'] if c['q']==307);rec['rows']['2129']=(rec['rows']['2129']+1)%7;save(N/'bad_column.json',d)
    run('reject_degree_two_column',C/'independent_columns68.py',ci+['--certificate',N/'bad_column.json','--output',N/'x.json'],reject='Changed degree-dependent twisted column')
    d=load(V/'columns70.json');d['columns'].pop();save(N/'missing_column.json',d)
    run('reject_omitted_conductor',C/'independent_columns68.py',ci+['--certificate',N/'missing_column.json','--output',N/'x.json'],reject='Wrong number of conductor factors')
    d=load(V/'targeted_2269.json');case=next(x for x in d['record']['cases'] if x['bad_allowed'] and x['beta_value']!=0);case['bad_allowed']=False;save(N/'wrong_bad.json',d)
    run('reject_nonzero_beta_zero_products',C/'independent_targeted70.py',secondary_args(N/'wrong_bad.json',N/'x.json'),reject='Wrong predicted product or bad-reduction condition')
    d=load(V/'targeted_2269.json');next(x for x in d['record']['rows'] if x['N2'] is not None)['N2']=None;save(N/'missing_n2.json',d)
    run('reject_unjustified_second_count_omission',C/'independent_targeted70.py',secondary_args(N/'missing_n2.json',N/'x.json'),reject='Missing required second count')
    d=load(V/'targeted_2269.json');d['record']['rows'][0]['N1']+=1;save(N/'changed_n1.json',d)
    run('reject_changed_point_count',C/'independent_targeted70.py',secondary_args(N/'changed_n1.json',N/'x.json'),reject='Point-count row mismatch N1')
    d=load(V/'refinement70.json');d['survivor_count']=0;d['survivors']=[];save(N/'false_zero.json',d)
    run('reject_false_zero_survivors',C/'independent_refine70.py',ri+['--certificate',N/'false_zero.json','--output',N/'x.json'],reject='Changed complete survivor list')
    d=load(V/'refinement70.json');d['minimum_support']=10;save(N/'false_ten.json',d)
    run('reject_inflated_support',C/'independent_refine70.py',ri+['--certificate',N/'false_ten.json','--output',N/'x.json'],reject='Changed minimum support bound')
    d=load(V/'finite_sieve_limit70.json');d['inertia'][0]=(d['inertia'][0]+1)%7;save(N/'bad_escape.json',d)
    run('reject_false_escape_vector',C/'independent_sieve_limit70.py',ci+['--certificate',N/'bad_escape.json','--output',N/'x.json'],reject='Escape vector does not annihilate every fixed row')
    (scratch/'README.md').write_text((scratch/'README.md').read_text()+'\nINTENTIONAL CORRUPTION\n')
    run('reject_modified_payload',scratch/'verify.py',['--integrity-only','--report',N/'integrity_report.json'],reject='Payload hash changed: README.md')
    if a.replay_predecessors:
     pred=next((ROOT/'predecessor').glob('*.zip'));pr=pathlib.Path(td)/'predecessor';pr.mkdir()
     with zipfile.ZipFile(pred) as z:
      for member in z.namelist():need(not pathlib.PurePosixPath(member).is_absolute() and '..' not in pathlib.PurePosixPath(member).parts,'Unsafe predecessor member')
      z.extractall(pr)
     proot=pr/'Komorebi_Beal_Block69';dest=pathlib.Path(td)/'Block69_Historical_Replay.json'
     run('selected_predecessor_history',proot/'verify.py',['--replay-predecessors','--report',dest,'--job-timeout',a.job_timeout],timeout=max(2400,a.job_timeout),cwd=proot)
     report['fresh_predecessor_replay']=load(dest)
  report['status']='PASS_DECLARED_CHECKS';report['exit_status']=0
 except Exception as e:
  report['status']='FAILED_OR_INCONCLUSIVE';report['error']=repr(e);report['exit_status']=1
 finally:
  report['elapsed_seconds']=time.monotonic()-started;report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(a.report,report)
 if report['exit_status']:
  print(report['error'],file=sys.stderr);raise SystemExit(1)
 print('PASS_DECLARED_CHECKS',round(report['elapsed_seconds'],3),flush=True)
if __name__=='__main__':main()
