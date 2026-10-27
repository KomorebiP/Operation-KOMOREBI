#!/usr/bin/env python3
"""Resume the one pending axiom-audit stage using bounded groups of unchanged declarations."""
import sys,json,os,time,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'v06_checks'))
import audit_lean as audit
S=ROOT/'v06_evidence/AXIOM_GROUP_STATE.json'
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def init():
 st=json.loads(audit.STATE.read_text());audit.verify(st)
 assert len(st['tasks'])==39 and not S.exists()
 rd=ROOT/'v06_checks/axiom_groups';rd.mkdir(exist_ok=True)
 groups=[]
 for i,start in enumerate(range(0,len(st['declarations']),192)):
  ns=st['declarations'][start:start+192];ms=list(dict.fromkeys(n['module'] for n in ns))
  f=rd/f'Group{i:02}.lean';f.write_text(''.join('import '+m.replace('/','.')+'\n' for m in ms)+''.join('#print axioms '+x['name']+'\n' for x in ns))
  groups.append({'path':str(f.relative_to(ROOT)),'sha256':audit.sha(f),'names':[x['name'] for x in ns]})
 added=[{'path':str(Path(__file__).relative_to(ROOT)),'sha256':audit.sha(__file__)}]+[{k:g[k] for k in ('path','sha256')} for g in groups]
 st['inputs']+=added
 st['audit_protocol_revision']={'reason':'Monolithic axiom collection exceeded enclosing wall-clock limit three times after all 39 builds completed. No proof input changed. Resume the same names in bounded groups.','at':now(),'added_inputs':added,'original_pending_command':st['plan'][39]['argv']}
 dump(audit.STATE,st)
 dump(S,{'status':'IN_PROGRESS','started_at':now(),'groups':groups,'tasks':[],'declarations':len(st['declarations'])})
 print('groups',len(groups))
def run_one():
 st=json.loads(audit.STATE.read_text());audit.verify(st);gstate=json.loads(S.read_text());i=len(gstate['tasks'])
 if i==len(gstate['groups']):print('ALL GROUPS COMPLETE');return
 g=gstate['groups'][i];rt=Path(st['runtime']);env=os.environ.copy();env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in (rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]);env['OMP_NUM_THREADS']='1'
 log=ROOT/'v06_evidence/cold'/f'axioms_group_{i:02}.log'
 cmd=[str(rt/'toolchain/bin/lean'),'-j1','-DwarningAsError=true',str(ROOT/g['path'])]
 t=time.monotonic()
 with log.open('w') as f:
  try:c=subprocess.run(cmd,cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=80);rc=c.returncode;timed=False
  except subprocess.TimeoutExpired:rc=None;timed=True
 text=log.read_text();ok=(rc==0 and not timed and all(("'"+n+"'") in text for n in g['names']))
 rec={'name':f'axioms_group_{i:02}','argv':cmd,'exit_code':rc,'timed_out':timed,'passed':ok,'seconds':time.monotonic()-t,'log':str(log.relative_to(ROOT)),'sha256':audit.sha(log)}
 gstate['tasks'].append(rec);gstate['last_observed_at']=now();gstate['status']='IN_PROGRESS' if ok else 'FAILED';dump(S,gstate)
 print(i,ok,round(rec['seconds'],2),flush=True)
 if not ok:raise RuntimeError(text[-2000:])
 if len(gstate['tasks'])==len(gstate['groups']):
  combined=ROOT/'v06_evidence/cold/axioms.log';combined.write_text(''.join((ROOT/t['log']).read_text() for t in gstate['tasks']))
  rec={'name':'axioms','argv':[sys.executable,str(Path(__file__)), '--init; successive --one calls'], 'subcommands':[t['argv'] for t in gstate['tasks']], 'exit_code':0,'expected_success':True,'timed_out':False,'passed':True,'seconds':sum(t['seconds'] for t in gstate['tasks']),'log':str(combined.relative_to(ROOT)),'sha256':audit.sha(combined),'execution_note':'One logical audit stage, eight actual synchronous Lean processes; see AXIOM_GROUP_STATE.json for exact argv/outcomes.'}
  audit.verify(st);st['tasks'].append(rec);st['last_observed_at']=now();dump(audit.STATE,st);gstate['status']='PASS';gstate['finished_at']=now();dump(S,gstate)
  print('AXIOM STAGE COMPLETE')
if __name__=='__main__':
 if '--init' in sys.argv:init()
 else:run_one()
