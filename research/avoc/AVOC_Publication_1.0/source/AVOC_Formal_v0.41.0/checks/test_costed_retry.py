"""Actual file operations and SIGKILL boundaries, each in a fresh protected store."""
import argparse,copy,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import run_retry_workflow as app
from retry_store import RetryDatabase,RecoveryError
RD=ROOT/'results/v0.21.0/retry_tests'
CASES=['normal','retry_after_verifier_work','retry_after_admit_work','retry_registration',
 'interrupted_retry_and_duplicate_key','stale_worker_fenced','credit_exhaustion',
 'attempt_cap','abandon_no_evidence','committed_not_retried','retry_publish_rollback','changed_input']
def req(x,msg):
 if not x:raise AssertionError(msg)
def fixture(base):
 p=base/'input';p.mkdir()
 (p/'target.json').write_text(json.dumps({'schema':'avoc-proposition-1','task':'retry-proof','statement':['imp',['atom',0],['atom',0]],'dependencies':[]}))
 (p/'good.json').write_text('["intro", ["atom", 0], ["hyp", ["atom", 0]]]')
 (p/'bad.json').write_text('["true"]')
 c=dict(prior_true='1/2',success_if_false=1,success_if_true=1,register_fee=1,verify_fee=1,
  admit_fee=1,admission_value=8,research_budget=3,horizon=3,planning_work_per_decision=3000,
  planning_price_per_unit='1/1000',target_file='target.json',candidate_files=['bad.json','good.json'])
 f=p/'config.json';f.write_text(json.dumps(c));return f

def cli(config,run,cmd='start',key=None,expected=None,credit=5,cap=8,only=False):
 args=[sys.executable,str(ROOT/'tools/run_retry_workflow.py'),cmd]
 if cmd=='start':args += [str(config),'--attempt-budget',str(credit),'--max-attempts',str(cap)]
 args+=['--run-dir',str(run)]
 if key:args+=['--key',key,'--expected-attempt',str(expected)]
 if only:args+=['--recover-only']
 p=subprocess.run(args,capture_output=True,text=True,timeout=150)
 try:r=json.loads(p.stdout)
 except Exception:raise AssertionError(p.stdout+'\n'+p.stderr)
 return p.returncode,r

def kill(config,run,point,stage,mode='start',credit=5,cap=8,key='retry-1',expected=1):
 args=[sys.executable,str(ROOT/'checks/retry_crash_worker.py'),mode,str(config),str(run),point,stage,
 '--credit',str(credit),'--cap',str(cap),'--key',key,'--expected',str(expected)]
 p=subprocess.run(args,capture_output=True,text=True,timeout=150)
 req(p.returncode==-signal.SIGKILL,f'not killed: {p.returncode} {p.stdout} {p.stderr}')
 return {'point':point,'stage':stage,'signal':'SIGKILL','returncode':p.returncode}

def snapshot(run):
 db=RetryDatabase(run/'state.sqlite3')
 try:
  ops=db.operations();nat,ch=db.snapshot();b=db.book()
  calls=[json.loads(x[0]) for x in db.db.execute('SELECT record FROM invocations')]
  return {'book':b,'phases':[x['phase'] for x in ops], 'attempts':db.attempt_rows(),
    'confirmed':sum(x['phase']=='acknowledged' for x in ops),'admissions':len(nat['admitted']),
    'native':nat,'checked':ch,'confirmed_state':db.get('confirmed_state'),
    'checker_calls':sum(x['kind']=='checker' for x in calls),'planner_calls':sum(x['kind']=='planner' for x in calls)}
 finally:db.close()

def same_evidence(a,b):
 for k in ['confirmed','admissions','native','checked','confirmed_state']:req(a[k]==b[k],'changed evidence '+k)

def case(name,base):
 config=fixture(base);run=base/'run'
 if name=='normal':
  code,r=cli(config,run);req(code==0 and r['status']=='admitted',str(r))
  before=snapshot(run);code,r=cli(config,run,'resume');after=snapshot(run)
  req(before==after,'normal duplicate resume changed logical/attempt state')
  return r
 stage='admit' if name=='retry_after_admit_work' else 'register' if name=='retry_registration' else 'verify'
 credit=2 if name=='credit_exhaustion' else 5
 cap=2 if name=='attempt_cap' else 8
 point='after_commit' if name=='committed_not_retried' else 'after_evaluation'
 crash=kill(config,run,point,stage,credit=credit,cap=cap);before=snapshot(run)
 expected=0 if stage=='register' else 2 if stage=='admit' else 1
 if name=='committed_not_retried':
  code,r=cli(config,run,'retry',key='recover-instead',expected=expected,only=True)
  after=snapshot(run)
  req(code==0 and r['resolution_disposition']=='already_committed_reconciled_not_retried',str(r))
  req(after['book'][0]==before['book'][0] and after['checker_calls']==before['checker_calls'],'committed reexecution')
  return {'crash':crash,'before':before,'recovery':r,'after':after}
 # Default resume remains non-retrying.
 code,blocked=cli(config,run,'resume',only=True);snap=snapshot(run)
 req(code==2 and blocked['status']=='aborted_uncommitted',str(blocked));req(before==snap,'default resume changed unfinished state')
 if name in ('credit_exhaustion','attempt_cap'):
  code,r=cli(config,run,'retry',key='blocked',expected=expected,only=True)
  after=snapshot(run);req(code==2,str(r));same_evidence(before,after)
  req(after['book']==before['book'] and after['checker_calls']==before['checker_calls'],'blocked retry charged or executed')
  return {'before':before,'blocked':r,'after':after}
 if name=='abandon_no_evidence':
  code,r=cli(config,run,'abandon',key='cancel-1',expected=expected);after=snapshot(run)
  req(code==0 and r['status']=='abandoned_uncommitted',str(r));same_evidence(before,after)
  req(after['book'][0]==before['book'][0] and after['book'][5],'refund or not terminal')
  dupcode,dup=cli(config,run,'abandon',key='cancel-1',expected=expected)
  req(dupcode==0 and snapshot(run)==after,'abandon not idempotent')
  code,r2=cli(config,run,'retry',key='too-late',expected=expected)
  req(code==2 and snapshot(run)==after,'retry after abandon')
  return {'before':before,'abandon':r,'after':after,'retry_rejected':r2}
 if name=='changed_input':
  f=config.parent/'good.json';f.write_text(f.read_text()+' ')
  code,r=cli(config,run,'retry',key='mutated',expected=expected)
  req(code==2 and snapshot(run)==before,'mutated candidate retried')
  return {'before':before,'rejection':r}
 if name in ('interrupted_retry_and_duplicate_key','stale_worker_fenced','retry_publish_rollback'):
  if name=='stale_worker_fenced':
   db=RetryDatabase(run/'state.sqlite3');old=db.operations()[-1];old['_attempt']=expected;db.close()
  p='after_store_write' if name=='retry_publish_rollback' else 'after_retry_intent'
  crash2=kill(config,run,p,stage,'retry',key='first-retry',expected=expected)
  middle=snapshot(run);same_evidence(before,middle)
  req(middle['book'][0]==before['book'][0]+1 and middle['book'][2]==before['book'][2]+1,'retry fee missing')
  if name=='stale_worker_fenced':
   db=RetryDatabase(run/'state.sqlite3')
   try:
    try:db.commit(old,old['before_native'],old['before_checked'],False,'retry-proof')
    except RecoveryError as e:req('stale attempt' in str(e),str(e))
    else:raise AssertionError('old attempt published')
   finally:db.close()
   req(snapshot(run)==middle,'stale attempt changed state')
  code,dup=cli(config,run,'retry',key='first-retry',expected=expected,only=True)
  req(dup.get('resolution_disposition')=='duplicate_authorization_no_execution',str(dup))
  req(snapshot(run)==middle,'duplicate authorization reexecuted/charged')
  code,r=cli(config,run,'retry',key='second-retry',expected=middle['book'][3][1])
  req(code==0 and r['status']=='admitted',str(r))
  req(r['nominal_attempt_debits']==5 and r['confirmed_state']['research_spent']==3 and r['wasted_nominal_fees']==2,'bad final costs')
  return {'crash':crash,'before':before,'retry_crash':crash2,'middle':middle,'duplicate':dup,'final':r}
 code,r=cli(config,run,'retry',key='explicit-retry',expected=expected)
 req(code==0 and r['status']=='admitted',str(r))
 after=snapshot(run)
 req(r['nominal_attempt_debits']==4 and r['confirmed_state']['research_spent']==3,'bad retry charge')
 req(r['wasted_nominal_fees']==1 and r['confirmed_state']['posterior_true']=='1/2','fault became evidence')
 _,dup=cli(config,run,'retry',key='explicit-retry',expected=expected)
 req(snapshot(run)==after,'successful retry reexecuted')
 return {'crash':crash,'before':before,'result':r,'after':after,'duplicate':dup}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1);a=p.parse_args()
 RD.mkdir(parents=True,exist_ok=True)
 for name in CASES[a.start:a.start+a.count]:
  base=RD/(name+'_'+str(time.time_ns()));base.mkdir();t=time.monotonic()
  try:result=case(name,base);record={'case':name,'passed':True,'seconds':time.monotonic()-t,'result':result}
  except Exception as e:
   record={'case':name,'passed':False,'seconds':time.monotonic()-t,'error':repr(e)}
   (RD/(name+'.json')).write_text(json.dumps(record,indent=2));raise
  record.update(directory=str(base.relative_to(ROOT)),source_pins=app.pins(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
  (RD/(name+'.json')).write_text(json.dumps(record,indent=2));print('PASS',name,record['seconds'],flush=True)
