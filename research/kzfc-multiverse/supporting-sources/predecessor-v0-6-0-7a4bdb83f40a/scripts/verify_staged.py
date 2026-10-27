#!/usr/bin/env python3
"""Resumable verification. No PASS is emitted until every pinned check completes."""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.util, json, os, pathlib, platform
import re, shutil, subprocess, sys, time, uuid
from graphlib import TopologicalSorter
ROOT=pathlib.Path(__file__).resolve().parents[1]
V=ROOT/'verification'
STATE=V/'staged_state.json'
spec=importlib.util.spec_from_file_location('verifier_utils',ROOT/'scripts/verify.py')
utils=importlib.util.module_from_spec(spec);spec.loader.exec_module(utils)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(o,indent=2)+'\n');t.replace(p)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def inputs():
 return ([ROOT/'Komorebi.lean']+sorted((ROOT/'Komorebi').rglob('*.lean'))+
  [ROOT/x for x in ['lakefile.toml','lake-manifest.json','lean-toolchain','verification_contract.json','scripts/verify.py','scripts/verify_staged.py']]+
  sorted((ROOT/'predecessor_sources').rglob('*.lean')))
def hashes():return {str(p.relative_to(ROOT)):digest(p) for p in inputs()}
def names():return utils.theorem_names([ROOT/'Komorebi.lean']+sorted((ROOT/'Komorebi').rglob('*.lean')))
def start():
 V.mkdir(exist_ok=True)
 for name in ['RESULTS.json','process_record.json','audit_coverage.json','computation_manifest.json']:(V/name).unlink(missing_ok=True)
 if (ROOT/'.lake/build').exists():shutil.rmtree(ROOT/'.lake/build')
 controls=V/'controls';controls.mkdir(exist_ok=True)
 (controls/'FalseProof.lean').write_text('example : False := by\n  exact True.intro\n')
 (controls/'Placeholder.lean').write_text('example : False := by\n  sorry\n')
 modules={'.'.join(p.relative_to(ROOT).with_suffix('').parts):p for p in [ROOT/'Komorebi.lean']+sorted((ROOT/'Komorebi').rglob('*.lean')) if p.name!='Audit.lean'}
 graph={m:{d for d in re.findall(r'^import\s+([\w.]+)',p.read_text(),re.M) if d in modules} for m,p in modules.items()}
 plan=[]
 def add(n,a,zero=True,match=None):plan.append({'name':n,'argv':a,'expect_zero':zero,'match':match})
 add('lean_version',['lean','--version'],match='4.34.0-rc2');add('lake_version',['lake','--version'])
 for m in TopologicalSorter(graph).static_order():
  if m!='Komorebi':add('build_'+m.split('.')[-1],['lake','build',m])
 add('clean_build',['lake','build','Komorebi'])
 for m,p in modules.items():add('check_'+p.stem,['lake','env','lean','-DwarningAsError=true',str(p.relative_to(ROOT))])
 add('axiom_audit',['lake','env','lean','-DwarningAsError=true','Komorebi/Foundation/Audit.lean'])
 add('negative_false_proof',['lake','env','lean','-DwarningAsError=true','verification/controls/FalseProof.lean'],False,'type mismatch')
 add('negative_placeholder',['lake','env','lean','-DwarningAsError=true','verification/controls/Placeholder.lean'],False,'sorry')
 s={'session_id':str(uuid.uuid4()),'started_at':now(),'start_timestamp':time.time(),'input_hashes_before':hashes(),'plan':plan,'records':[],'next_index':0,'status':'RUNNING','stage_invocations':[],'clean_project_cache':True,'per_command_timeout_seconds':120}
 s['stage_invocations'].append({'argv':sys.argv,'completed_at':now(),'exit_status':0})
 write(STATE,s);write(V/'theorems.json',names())
 print('Initialized clean staged run:',s['session_id'],len(plan),'compiler commands. No verdict yet.')
 return 0
def load():
 s=json.loads(STATE.read_text())
 if hashes()!=s['input_hashes_before']:raise ValueError('Pinned proof inputs changed; restart from a fresh clean session')
 return s
def next_batch(count):
 s=load()
 if s['status']!='RUNNING':raise ValueError('Session not RUNNING')
 for _ in range(count):
  if s['next_index']==len(s['plan']):break
  task=s['plan'][s['next_index']];t=time.monotonic();started=now()
  try:
   cp=subprocess.run(task['argv'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=False,timeout=s['per_command_timeout_seconds']);rc=cp.returncode;out=cp.stdout
  except subprocess.TimeoutExpired as e:
   rc=124;out=e.stdout or ''
   if isinstance(out,bytes):out=out.decode(errors='replace')
   out+='\nCOMMAND TIMEOUT\n'
  log='verification/'+task['name']+'.log';(ROOT/log).write_text(out)
  ok=(rc==0 if task['expect_zero'] else rc!=0 and rc!=124)
  if task['match']:ok=ok and task['match'].lower() in out.lower()
  rec={'name':task['name'],'argv':task['argv'],'exit_code':rc,'passed':ok,'started_at':started,'seconds':time.monotonic()-t,'log':log,'log_sha256':digest(ROOT/log)}
  s['records'].append(rec);s['next_index']+=1
  if not ok:s['status']='FAILED'
  write(STATE,s);print(('PASS ' if ok else 'FAIL ')+task['name'],flush=True)
  if not ok:
   s['stage_invocations'].append({'argv':sys.argv,'completed_at':now(),'exit_status':1});write(STATE,s);return 1
 s['stage_invocations'].append({'argv':sys.argv,'completed_at':now(),'exit_status':0});write(STATE,s)
 print('Completed commands:',s['next_index'],'/',len(s['plan']))
 return 0
def finish():
 s=load()
 if s['status']!='RUNNING' or s['next_index']!=len(s['plan']):raise ValueError('Not all planned commands completed successfully')
 records=list(s['records'])
 if len(records)!=len(s['plan']) or [r['name'] for r in records]!=[t['name'] for t in s['plan']]:raise ValueError('Plan coverage mismatch')
 if not all(r['passed'] for r in records):raise ValueError('A compiler check failed')
 if not all(digest(ROOT/r['log'])==r['log_sha256'] for r in records):raise ValueError('A recorded compiler log changed')
 ns=names();axout=(V/'axiom_audit.log').read_text()
 printed=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",axout,re.M)
 commands=re.findall(r'^#print axioms ([\w.]+)',(ROOT/'Komorebi/Foundation/Audit.lean').read_text(),re.M)
 coverage={'passed':set(ns)==set(printed)==set(commands) and len(ns)==len(printed)==len(commands),'theorem_count':len(ns),'printed_count':len(printed),'missing':sorted(set(ns)-set(printed)),'unexpected':sorted(set(printed)-set(ns))}
 write(V/'audit_coverage.json',coverage);records.append({'name':'complete_theorem_audit_coverage',**coverage})
 axioms=set()
 for text in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',axout):axioms.update(x.strip() for x in text.split(',') if x.strip())
 records.append({'name':'axiom_allowlist','passed':axioms<={'propext','Classical.choice','Quot.sound'} and 'sorryAx' not in axout,'observed':sorted(axioms)})
 forbidden=re.compile(r'\b(?:axiom|sorry|admit|unsafe|implemented_by|native_decide|run_tac)\b')
 findings={str(p.relative_to(ROOT)):forbidden.findall(utils.uncomment(p.read_text())) for p in [ROOT/'Komorebi.lean']+sorted((ROOT/'Komorebi').rglob('*.lean'))}
 findings={k:v for k,v in findings.items() if v};records.append({'name':'source_scan','passed':not findings,'findings':findings})
 after=hashes();records.append({'name':'inputs_unchanged','passed':after==s['input_hashes_before']})
 old=ROOT/'predecessor_sources';preserved=[p for p in old.rglob('*.lean') if p.name not in ['Audit.lean','Komorebi.lean']]
 records.append({'name':'predecessor_theorem_sources_preserved','passed':all(digest(p)==digest(ROOT/p.relative_to(old)) for p in preserved),'files':len(preserved)})
 records.append({'name':'complete_command_plan_and_log_integrity','passed':True,'commands':len(s['plan']),'session_id':s['session_id']})
 passed=all(r['passed'] for r in records);code=0 if passed else 1
 c=json.loads((ROOT/'verification_contract.json').read_text())
 result={'status':'PASS' if passed else 'FAIL','started_at':s['started_at'],'runtime_seconds':time.time()-s['start_timestamp'],'checks':records,'input_hashes_before':s['input_hashes_before'],'input_hashes_after':after,'platform':platform.platform(),'cpu_count':os.cpu_count(),'lean_version':(V/'lean_version.log').read_text().strip(),'lake_version':(V/'lake_version.log').read_text().strip(),'theorem_count':len(ns),'axioms_observed':sorted(axioms),'per_command_timeout_seconds':s['per_command_timeout_seconds'],'build_strategy':'clean serial targets in hash-pinned resumable batches','non_claims':c['non_claims'],'session_id':s['session_id'],'compiler_seconds':sum(r['seconds'] for r in s['records'])}
 write(V/'RESULTS.json',result)
 s['status']=result['status'];s['stage_invocations'].append({'argv':sys.argv,'completed_at':now(),'exit_status':code});write(STATE,s)
 write(V/'process_record.json',{'record_kind':'completion of a staged verification session, not one uninterrupted compiler subprocess','session_id':s['session_id'],'started_at':s['started_at'],'runtime_seconds':result['runtime_seconds'],'exit_status':code,'invocations':s['stage_invocations'],'compiler_command_count':len(s['plan']),'all_compiler_exits_recorded_in':'verification/RESULTS.json','wrapper_path':'scripts/verify_staged.py','wrapper_sha256_before':s['input_hashes_before']['scripts/verify_staged.py'],'wrapper_sha256_after':after['scripts/verify_staged.py']})
 print(result['status'],len(ns),'theorems;',len(s['plan']),'compiler commands;',len(preserved),'predecessor mathematical modules')
 return code
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['start','next','finish','status']);a.add_argument('--count',type=int,default=5);args=a.parse_args()
 if args.count<1:raise ValueError('count must be positive')
 if args.action=='start':return start()
 if args.action=='next':return next_batch(args.count)
 if args.action=='finish':return finish()
 s=load();print(s['status'],s['next_index'],len(s['plan']));return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except (OSError,ValueError,KeyError,TypeError) as e:print('Verification failed:',e,file=sys.stderr);raise SystemExit(1)
