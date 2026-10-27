#!/usr/bin/env python3
"""Synchronous cold audit with immutable input snapshots and resumable batches.
No PASS record is written until every planned build/control and axiom audit passes.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess,sys,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'v05_evidence/COLD_STATE.json'
PARENT_SHA='fca8f85dbf1cff576e4461fc8a1f68e9933770c65c95b8b747ba9338d967243b'
ALLOWED={'propext','Classical.choice','Quot.sound'}
NEW=['CertifiedMembership','CertifiedReplay','CertifiedOracle','CertifiedExamples']+[f'CheckedBatch{i:02}' for i in range(17)]

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')

def modules():
 seen=set();out=[]
 def visit(m):
  if m in seen:return
  seen.add(m);p=ROOT/'formalization'/(m+'.lean')
  for dep in re.findall(r'^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)',p.read_text(),re.M):
   dep=dep.replace('.','/')
   if (ROOT/'formalization'/(dep+'.lean')).exists():visit(dep)
  out.append(m)
 for n in NEW:visit(n)
 return out

def inventory(mods):
 rows=[]
 for m in mods:
  text=(ROOT/'formalization'/(m+'.lean')).read_text()
  ns=re.findall(r'^namespace\s+([\w.]+)\s*$',text,re.M)
  if len(ns)!=1:raise ValueError('namespace census '+m)
  for kind,name in re.findall(r'^(?:@\[[^\n]*?\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)',text,re.M):
   rows.append({'name':ns[0]+'.'+name,'kind':kind,'module':m,'new':m in NEW,'generated':m.startswith('CheckedBatch')})
 if len({x['name'] for x in rows})!=len(rows):raise ValueError('duplicate names')
 return rows

def init(runtime):
 if STATE.exists():raise ValueError('Existing audit state: resume or preserve it separately first')
 lean=runtime/'toolchain/bin/lean';mathlib=runtime/'workspace/.lake/packages/mathlib'
 pin=json.loads((ROOT/'source_records/PARENT_ENVIRONMENT.json').read_text())
 ver=subprocess.check_output([str(lean),'--version'],text=True).strip()
 if ver!=pin['lean_version'] or sha(lean)!=pin['lean_binary_sha256']:raise ValueError('Lean pin mismatch')
 revision=(mathlib/'.git/HEAD').read_text().strip()
 if revision!=pin['mathlib_commit']:raise ValueError('Mathlib metadata pin mismatch')
 for x in pin['mathlib_sources']:
  if sha(mathlib/x['path'])!=x['sha256']:raise ValueError('Mathlib source mismatch '+x['path'])
 parent=ROOT/'history/Komorebi_ModelTheory_Normalization_v0.4.zip'
 if sha(parent)!=PARENT_SHA:raise ValueError('parent archive hash')
 import zipfile
 preserved=[]
 with zipfile.ZipFile(parent) as z:
  for n in z.namelist():
   if '/formalization/' in n and n.endswith('.lean'):
    rel='formalization/'+n.split('/formalization/',1)[1]
    if (ROOT/rel).read_bytes()!=z.read(n):raise ValueError('parent source changed '+rel)
    preserved.append({'path':rel,'sha256':sha(ROOT/rel)})
 dump(ROOT/'v05_evidence/PARENT_PRESERVATION.json',{'parent_sha256':PARENT_SHA,'files':preserved,'count':len(preserved)})
 env={'lean_version':ver,'lean_binary_sha256':sha(lean),'mathlib_commit':revision,
      'mathlib_sources':pin['mathlib_sources'],'python':sys.version,
      'memory_cgroup':Path('/sys/fs/cgroup/memory.max').read_text().strip(),
      'cpu_cgroup':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
      'runtime_note':'Restored pinned compiled cache and source snapshot, not a rebuild of Mathlib.'}
 dump(ROOT/'v05_evidence/ENVIRONMENT.json',env)
 mods=modules();decls=inventory(mods)
 dump(ROOT/'v05_evidence/MODULES.json',mods);dump(ROOT/'v05_evidence/DECLARATIONS.json',decls)
 ax=ROOT/'v05_checks/AxiomAudit.lean'
 ax.write_text(''.join('import '+m.replace('/','.')+'\n' for m in mods)+'\n'+''.join('#print axioms '+x['name']+'\n' for x in decls))
 cd=ROOT/'v05_checks/controls';cd.mkdir(exist_ok=True)
 header='import CertifiedExamples\nopen Komorebi.Discovery Komorebi.Discovery.Certified Komorebi.Discovery.CertifiedExamples\n'
 controls={
 'Positive':('example : True := by trivial\n',True),
 'False':('example : False := by decide\n',False),
 'Placeholder':('example : True := by sorry\n',False),
 'FalseMembership':('example : checkMembership AA O [([],0)] (![1] : Fin 1 → R) (.combination [2]) = some true := by decide +kernel\n',False),
 'ZeroSeparator':('example : checkMembership AA O [] (![2] : Fin 1 → R) (.separation ![0]) = some false := by decide +kernel\n',False),
 'IncompleteQueue':('example : replaySource A O (valid.take 3) = some answer := by decide +kernel\n',False),
 'WrongFallback':('example : guardedPrimeDiscover 2 2 1 AA O badProposer = none := by decide +kernel\n',False)}
 for n,(text,_) in controls.items():(cd/(n+'.lean')).write_text(header+text)
 sources=[ROOT/'formalization'/(m+'.lean') for m in mods]+[ax,Path(__file__)]+list(cd.glob('*.lean'))
 sources+=[ROOT/'v05_evidence/DECLARATIONS.json',ROOT/'v05_evidence/EXPORTED_DATA.json',ROOT/'source_records/PARENT_ENVIRONMENT.json',ROOT/'tools/validate_manifest.py']
 inputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(sources))]
 b=Path(tempfile.mkdtemp(prefix='komorebi-model05-cold-'));plan=[]
 for m in mods:
  out=b/(m+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
  plan.append({'name':'build_'+m,'argv':[str(lean),'-j1','-DwarningAsError=true','-o',str(out),m+'.lean'],'expect':True,'module':m})
 plan.append({'name':'axioms','argv':[str(lean),'-j1','-DwarningAsError=true',str(ax)],'expect':True})
 for n,(_,success) in controls.items():plan.append({'name':'control_'+n,'argv':[str(lean),'-j1','-DwarningAsError=true',str(cd/(n+'.lean'))],'expect':success})
 st={'status':'IN_PROGRESS','started_at':now(),'runtime':str(runtime),'build':str(b),'environment':env,
     'inputs':inputs,'plan':plan,'tasks':[],'artifacts':[],'modules':mods,'declarations':decls}
 dump(STATE,st);print(json.dumps({'modules':len(mods),'new_modules':len(NEW),'declarations':len(decls),'tasks':len(plan),'build':str(b)},indent=2))

def verify(st):
 for x in st['inputs']:
  if sha(ROOT/x['path'])!=x['sha256']:raise ValueError('input changed '+x['path'])
 for x in st['artifacts']:
  if sha(x['path'])!=x['sha256']:raise ValueError('completed build artifact changed')
 for x in st['tasks']:
  if sha(ROOT/x['log'])!=x['sha256']:raise ValueError('completed log changed')

def batch(n):
 st=json.loads(STATE.read_text());verify(st)
 if st['status'] not in ['IN_PROGRESS','TASKS_COMPLETE']:raise ValueError(st['status'])
 rt=Path(st['runtime']);env=os.environ.copy();env['OMP_NUM_THREADS']='1';env['OPENBLAS_NUM_THREADS']='1'
 env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in (rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')])
 for spec in st['plan'][len(st['tasks']):len(st['tasks'])+n]:
  t=time.monotonic();log=ROOT/'v05_evidence/cold'/f'{spec["name"].replace("/","_")}.log';log.parent.mkdir(exist_ok=True)
  try:
   c=subprocess.run(spec['argv'],cwd=ROOT/'formalization',env=env,capture_output=True,text=True,timeout=90)
   out=c.stdout+c.stderr;rc=c.returncode;timeout=False
  except subprocess.TimeoutExpired as e:out=(e.stdout or b'');out=out.decode() if isinstance(out,bytes) else out;rc=None;timeout=True
  log.write_text(out);ok=not timeout and ((rc==0) if spec['expect'] else (rc is not None and rc>0 and 'error:' in out))
  if not spec['expect'] and any(x in out.lower() for x in ['does not exist','unknown module prefix','missing data','maximum number of heartbeats','deep recursion','out of memory']):ok=False
  task={'name':spec['name'],'argv':spec['argv'],'exit_code':rc,'expected_success':spec['expect'],
        'timed_out':timeout,'passed':ok,'seconds':time.monotonic()-t,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
  st['tasks'].append(task)
  if ok and 'module' in spec:
   for p in Path(st['build']).glob(spec['module']+'.*'):
    if p.is_file():st['artifacts'].append({'path':str(p),'sha256':sha(p)})
  if not ok:st['status']='FAILED'
  st['last_observed_at']=now();dump(STATE,st)
  print(len(st['tasks']),spec['name'],ok,round(task['seconds'],2),flush=True)
  if not ok:raise RuntimeError(out)
 if len(st['tasks'])==len(st['plan']):st['status']='TASKS_COMPLETE'
 verify(st);dump(STATE,st)
 print(st['status'],len(st['tasks']),len(st['plan']))

def finish():
 st=json.loads(STATE.read_text());verify(st)
 if len(st['tasks'])!=len(st['plan']) or not all(x['passed'] for x in st['tasks']):raise ValueError('incomplete audit')
 text=(ROOT/next(x['log'] for x in st['tasks'] if x['name']=='axioms')).read_text()
 axioms=set()
 for b in re.findall(r'depends on axioms:\s*\[([^]]*)\]',text,re.S):axioms.update(x.strip() for x in b.replace('\n',' ').split(',') if x.strip())
 audited=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",text))
 missing=[x['name'] for x in st['declarations'] if x['name'] not in audited]
 if missing or axioms-ALLOWED:raise ValueError({'missing':missing,'unexpected_axioms':sorted(axioms-ALLOWED)})
 st['status']='COMPLETE';st['finished_at']=now();dump(STATE,st)
 result={'status':'PASS','started_at':st['started_at'],'finished_at':st['finished_at'],
  'modules':len(st['modules']),'new_modules':len(NEW),'tasks':st['tasks'],
  'named_declarations':len(st['declarations']),'counts':dict(Counter(x['kind'] for x in st['declarations'])),
  'new_generic_counts':dict(Counter(x['kind'] for x in st['declarations'] if x['module'] in NEW[:3])),
  'new_concrete_counts':dict(Counter(x['kind'] for x in st['declarations'] if x['module']=='CertifiedExamples')),
  'generated_cases':203,'axioms':sorted(axioms),'all_declarations_audited':len(audited),
  'compile_seconds':sum(x['seconds'] for x in st['tasks']),
  'boundary':'Cold local selected dependency build; pinned Mathlib cache reused. Python producer/exporter unverified.'}
 dump(ROOT/'results_v05/LEAN_AUDIT.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='tasks'},indent=2))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--runtime',type=Path);a.add_argument('--init',action='store_true');a.add_argument('--batch',type=int);a.add_argument('--finish',action='store_true');args=a.parse_args()
 if args.init:init(args.runtime.resolve())
 elif args.batch:batch(args.batch)
 elif args.finish:finish()
 else:a.error('choose --init, --batch N, --finish')
