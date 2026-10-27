#!/usr/bin/env python3
"""Independent truth-bitset oracle, exact campaign oracle, and protected-store tests."""
from __future__ import annotations
from pathlib import Path
import copy,functools,itertools,json,os,sqlite3,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import synthesize_upgrade as runtime
RD=ROOT/'results/v0.25.0';RD.mkdir(exist_ok=True)

def freeze(p): return tuple(freeze(x) if isinstance(x,list) else x for x in p)
def thaw(p): return [thaw(x) if isinstance(x,tuple) else x for x in p]
@functools.lru_cache(None)
def size(p): return 1 if p[0] in ('literal','variable') else 1+sum(size(x) for x in p[1:])
@functools.lru_cache(None)
def signature(p):
 op=p[0]
 if op=='literal': return 255 if p[1] else 0
 if op=='variable': return (0b11110000,0b11001100,0b10101010)[p[1]]
 if op=='not': return 255^signature(p[1])
 a,b=signature(p[1]),signature(p[2])
 return a&b if op=='and' else a|b if op=='or' else a^b
@functools.lru_cache(None)
def grammar(d):
 atoms=(('literal',False),('literal',True),('variable',0),('variable',1),('variable',2))
 if d==0:return atoms
 prev=grammar(d-1)
 return prev+tuple(('not',p) for p in prev)+tuple((op,p,q) for op in ('and','or','xor') for p,q in itertools.product(prev,repeat=2))

def oracle(job):
 r,calls,total,d,limit,budget=job;r=freeze(r)
 cnt,g,nb=5,5,1
 for _ in range(d):cnt=2*cnt+3*cnt*cnt;g+=cnt;nb=2*nb+1
 fee=8*(size(r)+nb+1)
 if g<=budget: n=min(limit,cnt,(budget-g)//fee);generation=g;gs=grammar(d)[:n]
 else:n=0;generation=0;gs=()
 best=r;valid=0;improvements=0
 target=signature(r)
 for candidate in gs:
  if signature(candidate)==target:
   valid+=1
   if size(candidate)<size(best):best=candidate;improvements+=1
 search=generation+n*fee
 ev=8*(size(r)+size(best)+1)
 remaining=total-search
 if remaining<ev: ev=0;sw=0;active=r;promotions=0
 else:
  delta=calls*(size(r)-size(best))
  promotions=int(delta>=2 and ev+1<=remaining)
  sw=promotions;active=best if promotions else r
 charges=search+ev+sw
 return dict(candidate=thaw(best),active=thaw(active),reference_nodes=size(r),candidate_nodes=size(best),
  active_nodes=size(active),requested_pool_size=cnt,generated_pool_size=cnt if g<=budget else 0,
  generation_charge=generation,candidate_evaluation_charge=n*fee,tested=n,
  promotion_evaluation_charge=ev,switch_charge=sw,total_charge=charges,credits_remaining=total-charges,
  net=calls*(size(r)-size(active))-charges,promotions=promotions,valid_candidates=valid,
  invalid_candidates=n-valid,strict_improvements=improvements)

def batch(requests,tag):
 lean,env,_=runtime.environment()
 path=RD/(tag+'_requests.json');path.write_text(runtime.canonical(requests)+'\n')
 t=time.monotonic()
 p=subprocess.run([str(lean),'--run',str(ROOT/'tools/SynthesisMain.lean'),'--batch',str(path)],
  cwd=ROOT,env=env,text=True,capture_output=True,timeout=100)
 (RD/(tag+'_stdout.jsonl')).write_text(p.stdout)
 (RD/(tag+'_stderr.txt')).write_text(p.stderr)
 assert p.returncode==0,(p.returncode,p.stderr,p.stdout[-1000:])
 answers=[json.loads(x) for x in p.stdout.splitlines()]
 assert len(answers)==len(requests)
 return answers,dict(cases=len(requests),seconds=time.monotonic()-t,returncode=p.returncode)

def differential():
 v=lambda x:['variable',x]
 refs=[['literal',False],['literal',True],v(0),['not',v(1)],
       ['not',['or',['not',v(0)],['not',v(1)]]],
       ['not',['and',['not',v(0)],['not',v(2)]]],
       ['not',['not',['xor',v(0),v(1)]]],
       ['or',['and',v(0),v(1)],['and',v(0),['not',v(1)]]]]
 jobs=[]
 for r,d,calls,b,lim in itertools.product(refs,[0,1],[0,1,10000],[0,4,90,1000,10000],[0,5,85]):
  jobs.append([r,calls,b+500,d,lim,b])
 deeprefs=[
  ['not',['or',['not',v(0)],['or',['not',v(1)],['not',v(2)]]]],
  ['not',['not',['xor',v(0),['xor',v(1),v(2)]]]],
  ['or',['and',v(0),v(1)],['and',v(2),['or',v(0),v(1)]]]]
 for r,lim,b in itertools.product(deeprefs,[0,400,21845],[21934,100000,3500000]):
  jobs.append([r,100000,b+10000,2,lim,b])
 records=[];total_equivalence_obligations=0
 for offset in range(0,len(jobs),240):
  group=jobs[offset:offset+240]
  answers,rec=batch([['avoc-synthesis-v1',j] for j in group],f'differential_{offset:04}')
  for j,a in zip(group,answers):
   assert a['status']=='checked',a
   expected=oracle(j)
   for k,val in expected.items():
    if k in ('valid_candidates','invalid_candidates','strict_improvements'):continue
    assert a.get(k)==val,(j,k,a.get(k),val)
   actual=a['executions'];sig=signature(freeze(a['active']))
   for i,row in enumerate(actual):
    assert row['value']==bool((sig>>i)&1)
    assert row['visits']==size(freeze(a['active']))
    total_equivalence_obligations+=1
   assert signature(freeze(a['active']))==signature(freeze(j[0]))
  records.append(rec)
  print('campaign comparisons',offset+len(group),'/',len(jobs),flush=True)
 # Direct equivalence checker, with an independent bitset truth-table oracle.
 programs=list(grammar(1))
 pair_requests=[]
 for i,p in enumerate(programs):
  for q in [programs[(i*11+7)%85],p,('not',('not',p))]:
   pair_requests.append(['avoc-bool-check-v1',thaw(p),thaw(q)])
 answers,rec=batch(pair_requests,'checker')
 for w,a in zip(pair_requests,answers):
  assert a['equivalent']==(signature(freeze(w[1]))==signature(freeze(w[2])))
 records.append(rec)
 # Reject invalid inputs at the executed Lean wire, not only the wrapper.
 base=['avoc-synthesis-v1',jobs[0]]
 invalid=[['bad',[]],['avoc-bool-check-v1',['variable',3],['literal',True]],
  ['avoc-bool-check-v1',['literal',1],['literal',True]],
  ['avoc-bool-check-v1',['import','Mathlib'],['literal',True]]]
 for index,value in [(1,True),(2,-1),(3,3),(4,21846),(5,99999999),(1,1.5)]:
  w=copy.deepcopy(base);w[1][index]=value;invalid.append(w)
 answers,rec=batch(invalid,'invalid_wire')
 assert all(a['status']=='error' for a in answers),answers
 records.append(rec)
 result={'campaign_cases':len(jobs),'direct_checker_cases':len(pair_requests),
  'full_input_execution_checks':total_equivalence_obligations,'invalid_wire_cases':len(invalid),'records':records,
  'oracle':'Python bitset Boolean semantics and separately written exhaustive argmin/accounting; no random sampling',
  'range':'3 input bits, grammar depth 0/1 and stated depth-2 examples, exact integer costs'}
 (RD/'differential_summary.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

def live():
 base=runtime.load_config(ROOT/'examples/synthesis/pair.json');results=[]
 folder=Path(tempfile.mkdtemp(prefix='avoc-synthesis-live-',dir=RD))
 def record(name,fn):
  t=time.monotonic();fn();results.append({'name':name,'passed':True,'seconds':time.monotonic()-t});print('PASS',name,flush=True)
 def expect_error(fn):
  try:fn()
  except (RuntimeError,ValueError,OSError,sqlite3.Error):return
  raise AssertionError('expected rejection')
 good=folder/'good'
 def success():
  r=runtime.start(base,good);assert r['active_nodes']==3 and r['net']==23029
  (RD/'demo_pair.json').write_text(json.dumps(r,indent=2)+'\n')
  dbbefore=runtime.sha(good/'campaign.sqlite3')
  rr=runtime.inspect(good,True);assert rr['active']==r['active'] and not rr['reexecuted_search']
  assert runtime.sha(good/'campaign.sqlite3')==dbbefore
 record('generate_promote_persist_invoke',success)
 record('reject_existing_run',lambda:expect_error(lambda:runtime.start(base,good)))
 badcost=runtime.load_config(ROOT/'examples/synthesis/pair_unprofitable.json')
 def unprofitable():
  r=runtime.start(badcost,folder/'unprofitable');assert r['promotions']==1 and r['net']==-6968
  (RD/'demo_unprofitable.json').write_text(json.dumps(r,indent=2)+'\n')
 record('smaller_component_negative_campaign_net',unprofitable)
 guard=runtime.load_config(ROOT/'examples/synthesis/guard.json')
 def guardrun():
  r=runtime.start(guard,folder/'guard');assert r['active_nodes']==5 and r['reference_nodes']==9
  (RD/'demo_guard.json').write_text(json.dumps(r,indent=2)+'\n')
 record('three_flag_program_generated',guardrun)
 def unresolved(phase,name):
  path=folder/name
  def hook(p):
   if p==phase:raise RuntimeError('test interruption '+p)
  expect_error(lambda:runtime.start(base,path,hook=hook))
  info=runtime.inspect(path);assert info['phase']=='unconfirmed_search' and info['reserved_or_charged']==base['credits']
  expect_error(lambda:runtime.inspect(path,True))
 record('interrupted_before_generation_retains_reservation',lambda:unresolved('after_reservation','before'))
 record('interrupted_after_search_before_commit_no_dispatch',lambda:unresolved('after_search','searched'))
 record('interrupted_transaction_rolls_back_result',lambda:unresolved('inside_commit','transaction'))
 def committed():
  path=folder/'committed'
  def hook(p):
   if p=='after_commit':raise RuntimeError('lost response')
  expect_error(lambda:runtime.start(base,path,hook=hook))
  assert runtime.inspect(path,True)['active_nodes']==3
 record('committed_result_survives_lost_response',committed)
 # Use independent copies of the good store; never mutate the user's registry.
 import shutil
 def tamper(name,mutate):
  path=folder/name;shutil.copytree(good,path);mutate(path)
  expect_error(lambda:runtime.inspect(path,True))
 def change_result(path):
  db=sqlite3.connect(path/'campaign.sqlite3');r=json.loads(db.execute('select result from run').fetchone()[0]);r['active']=['literal',True]
  db.execute('update run set result=?',(runtime.canonical(r),));db.commit();db.close()
 record('changed_result_checksum_rejected',lambda:tamper('changed_result',change_result))
 def change_journal(path):
  db=sqlite3.connect(path/'campaign.sqlite3');r=json.loads(db.execute('select result from run').fetchone()[0]);r['journal'][0][4]=0
  text=runtime.canonical(r);db.execute('update run set result=?,result_hash=?',(text,__import__('hashlib').sha256(text.encode()).hexdigest()));db.commit();db.close()
 record('omitted_promotion_charge_rejected',lambda:tamper('changed_cost',change_journal))
 def change_authority(path):
  p=path/'authority.json';a=json.loads(p.read_text());a['job']['deployment_calls']=9;p.write_text(runtime.canonical(a))
 record('changed_frozen_objective_rejected',lambda:tamper('changed_authority',change_authority))
 def locktest():
  with runtime.locked(good):expect_error(lambda:runtime.inspect(good))
 record('cooperative_lock_rejected',locktest)
 for field,val in [('credits',True),('grammar_depth',3),('trial_limit',-1),('reference',['eval','os.system'])]:
  cfg=copy.deepcopy(base);cfg[field]=val
  record('wrapper_'+field,lambda cfg=cfg:expect_error(lambda:runtime.validate_config(cfg)))
 result={'case_count':len(results),'cases':results,'stores':str(folder),
  'scope':'actual file/SQLite/Lean subprocess tests plus controlled Python exceptions; not power-loss or universal filesystem proofs'}
 (RD/'live_summary.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

if __name__=='__main__':
 if '--live' in sys.argv:print(json.dumps(live(),indent=2))
 else:print(json.dumps(differential(),indent=2))
