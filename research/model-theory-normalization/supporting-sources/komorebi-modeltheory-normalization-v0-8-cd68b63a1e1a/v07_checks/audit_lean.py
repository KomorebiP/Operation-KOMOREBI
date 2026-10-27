#!/usr/bin/env python3
"""Cold, input-pinned Lean audit in restartable synchronous subprocess steps."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse,hashlib,json,os,re,subprocess,tempfile,time,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'v07_evidence/COLD_STATE.json'
ALLOWED={'propext','Classical.choice','Quot.sound'}
NEW=['EchelonNormalize','EchelonBounds','EchelonCanonical','EchelonModularNormal','NormalizedDiscovery','NormalizedExamples']+[f'NormalizedComputed{i:02}' for i in range(17)]
PARENT_SHA='7a10778aa0200d130b648f66dd90d76393ed3a8a3bf822cfb747304f1a5e7628'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def modules():
 seen=set();out=[]
 def visit(m):
  if m in seen:return
  seen.add(m);p=ROOT/'formalization'/(m+'.lean')
  for dep in re.findall(r'^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)',p.read_text(),re.M):
   dep=dep.replace('.','/')
   if (ROOT/'formalization'/(dep+'.lean')).exists():visit(dep)
  out.append(m)
 for m in NEW:visit(m)
 return out

def init(rt):
 if STATE.exists():raise ValueError('preserve prior state or resume; do not overwrite')
 pin=json.loads((ROOT/'v06_evidence/ENVIRONMENT.json').read_text())
 lean=rt/'toolchain/bin/lean';ml=rt/'workspace/.lake/packages/mathlib'
 ver=subprocess.check_output([str(lean),'--version'],text=True).strip()
 assert ver==pin['lean_version'] and sha(lean)==pin['lean_binary_sha256']
 assert (ml/'.git/HEAD').read_text().strip()==pin['mathlib_commit']
 for f in pin['mathlib_sources']:assert sha(ml/f['path'])==f['sha256']
 par=ROOT/'history/Komorebi_ModelTheory_Normalization_v0.6.zip';assert sha(par)==PARENT_SHA
 preserved=[]
 with zipfile.ZipFile(par) as z:
  assert z.testzip() is None
  for n in z.namelist():
   if '/formalization/' in n and n.endswith('.lean'):
    rel='formalization/'+n.split('/formalization/',1)[1]
    assert (ROOT/rel).read_bytes()==z.read(n),rel
    preserved.append({'path':rel,'sha256':sha(ROOT/rel)})
 dump(ROOT/'v07_evidence/PARENT_PRESERVATION.json',{'parent_sha256':PARENT_SHA,'count':len(preserved),'files':preserved})
 mods=modules();decls=[]
 for m in mods:
  txt=(ROOT/'formalization'/(m+'.lean')).read_text();ns=re.findall(r'^namespace\s+([\w.]+)\s*$',txt,re.M);assert len(ns)==1,(m,ns)
  for kind,name in re.findall(r'^(?:@\[[^\n]*?\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)',txt,re.M):
   decls.append({'name':ns[0]+'.'+name,'kind':kind,'module':m,'new':m in NEW,'generated':m.startswith('NormalizedComputed')})
 assert len({d['name'] for d in decls})==len(decls)
 dump(ROOT/'v07_evidence/DECLARATIONS.json',decls);dump(ROOT/'v07_evidence/MODULES.json',mods)
 b=Path(tempfile.mkdtemp(prefix='komorebi-model07-cold-'));plan=[]
 for m in mods:
  out=b/(m+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
  plan.append({'name':'build_'+m,'argv':[str(lean),'-j1','-DwarningAsError=true','-o',str(out),m+'.lean'],'expect':True,'module':m})
 axfiles=[]
 for i,j in enumerate(range(0,len(decls),160)):
  names=decls[j:j+160];p=ROOT/f'v07_checks/axioms/Group{i:02}.lean';p.parent.mkdir(exist_ok=True)
  p.write_text(''.join('import '+m.replace('/','.')+'\n' for m in dict.fromkeys(x['module'] for x in names))+''.join('#print axioms '+x['name']+'\n' for x in names))
  axfiles.append(p);plan.append({'name':f'axioms_{i:02}','argv':[str(lean),'-j1','-DwarningAsError=true',str(p)],'expect':True,'axioms':True})
 hdr='import NormalizedExamples\nopen Komorebi.Echelon Komorebi.NormalizedExamples Komorebi.Discovery Komorebi.Discovery.NormalizedBackend Komorebi.Representation.Matrix\n'
 controls={
  'Positive':('example : entries (normalize bigTail)=![![2,2],![0,64]] := positive_tail_reduced\n',True),
  'False':('example : False := by decide\n',False),
  'Placeholder':('example : True := by sorry\n',False),
  'LostCoupling':('example : (coordinates (normalize coupled) ![2,0]).isSome=true := by decide +kernel\n',False),
  'WrongPivotReduction':('example : entries (normalize coupled)=![![2,0],![0,64]] := by decide +kernel\n',False),
  'StrictDiagonalBound':('example : entries (normalize coupled) 1 1 < 64 := by decide +kernel\n',False),
  'ZeroFuel':('example : normalizedRun 4 (fun a => rowRight (shearA a)) shearO 0 (diagonal 4 (by decide) 2) [] []=some (diagonal 4 (by decide) 2,[]) := by simp [normalizedRun]\n',False),
  'WrongOutput':('example : normalizedPrimeDiscover 2 2 2 (fun a => rowRight (shearA a)) shearO=some [([],0)] := by decide +kernel\n',False)}
 cfiles=[]
 for n,(body,expected) in controls.items():
  p=ROOT/f'v07_checks/controls/{n}.lean';p.parent.mkdir(exist_ok=True);p.write_text(hdr+body);cfiles.append(p)
  plan.append({'name':'control_'+n,'argv':[str(lean),'-j1','-DwarningAsError=true',str(p)],'expect':expected})
 inputs=[ROOT/'formalization'/(m+'.lean') for m in mods]+axfiles+cfiles+[Path(__file__),ROOT/'v07_evidence/DECLARATIONS.json',ROOT/'v06_evidence/EXPORTED_DATA.json',ROOT/'v06_evidence/ENVIRONMENT.json']
 env={'lean_version':ver,'lean_binary_sha256':sha(lean),'mathlib_commit':pin['mathlib_commit'],'python':sys.version,'cpu_cgroup':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_cgroup':Path('/sys/fs/cgroup/memory.max').read_text().strip()}
 dump(ROOT/'v07_evidence/ENVIRONMENT.json',env)
 state={'status':'IN_PROGRESS','started_at':now(),'runtime':str(rt),'build':str(b),'plan':plan,'tasks':[],'artifacts':[],'modules':mods,'declarations':decls,'environment':env,'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(inputs))]}
 dump(STATE,state);print('initialized',len(mods),'modules',len(decls),'names',len(plan),'tasks',flush=True)

def verify(st):
 for x in st['inputs']:assert sha(ROOT/x['path'])==x['sha256'],x
 for x in st['artifacts']:assert sha(x['path'])==x['sha256'],x
 for x in st['tasks']:assert sha(ROOT/x['log'])==x['sha256'],x

def batch(n):
 st=json.loads(STATE.read_text());verify(st);assert st['status'] in ['IN_PROGRESS','TASKS_COMPLETE']
 rt=Path(st['runtime']);env=os.environ.copy();env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in (rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]);env['OMP_NUM_THREADS']='1'
 for item in st['plan'][len(st['tasks']):len(st['tasks'])+n]:
  log=ROOT/'v07_evidence/cold'/(item['name'].replace('/','_')+'.log');log.parent.mkdir(exist_ok=True);t=time.monotonic()
  with log.open('w') as f:
   try:p=subprocess.run(item['argv'],cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90);rc=p.returncode;timed=False
   except subprocess.TimeoutExpired:rc=None;timed=True
  text=log.read_text();ok=not timed and ((rc==0) if item['expect'] else (rc not in [None,0] and 'error:' in text))
  if not item['expect'] and any(k in text.lower() for k in ['unknown module','does not exist','heartbeats','out of memory','deep recursion']):ok=False
  rec={'name':item['name'],'argv':item['argv'],'exit_code':rc,'timed_out':timed,'expected_success':item['expect'],'passed':ok,'seconds':time.monotonic()-t,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
  st['tasks'].append(rec);st['last_observed_at']=now()
  if ok and 'module' in item:
   for p in Path(st['build']).glob(item['module']+'.*'):
    if p.is_file():st['artifacts'].append({'path':str(p),'sha256':sha(p)})
  if not ok:st['status']='FAILED'
  dump(STATE,st);print(len(st['tasks']),item['name'],ok,round(rec['seconds'],2),flush=True)
  if not ok:raise RuntimeError(text[-6000:])
 if len(st['tasks'])==len(st['plan']):st['status']='TASKS_COMPLETE'
 verify(st);dump(STATE,st)

def finish():
 st=json.loads(STATE.read_text());verify(st)
 assert len(st['tasks'])==len(st['plan']) and all(t['passed'] for t in st['tasks'])
 txt=''.join((ROOT/t['log']).read_text() for t in st['tasks'] if t['name'].startswith('axioms_'))
 axioms=set()
 for x in re.findall(r'depends on axioms:\s*\[([^]]*)\]',txt,re.S):axioms.update(k.strip() for k in x.replace('\n',' ').split(',') if k.strip())
 names=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",txt))
 assert not axioms-ALLOWED,axioms
 assert names=={d['name'] for d in st['declarations']},(len(names),len(st['declarations']))
 st['status']='PASS';st['finished_at']=now();dump(STATE,st)
 result={'status':'PASS','started_at':st['started_at'],'finished_at':st['finished_at'],'modules':len(st['modules']),'new_modules':len(NEW),'task_count':len(st['tasks']),'named_declarations':len(names),'counts':dict(Counter(x['kind'] for x in st['declarations'])),'new_generic_counts':dict(Counter(x['kind'] for x in st['declarations'] if x['module'] in NEW[:5])),'cases':203,'axioms':sorted(axioms),'all_inputs_unchanged':True,'task_runtime_sum':sum(t['seconds'] for t in st['tasks']),'tasks':st['tasks'],'scope':'Cold local dependency build plus actual normalized kernel computations on 203 cases; upstream Mathlib cache reused. Stored basis bounds and canonicity formalized; general intermediate bit-complexity not claimed.'}
 dump(ROOT/'results_v07/LEAN_AUDIT.json',result);print('PASS',len(st['modules']),len(names),len(st['tasks']),flush=True)

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--runtime',type=Path);a.add_argument('--init',action='store_true');a.add_argument('--batch',type=int);a.add_argument('--finish',action='store_true');a.add_argument('--all',action='store_true');x=a.parse_args()
 if x.init:init(x.runtime.resolve())
 elif x.batch:batch(x.batch)
 elif x.finish:finish()
 elif x.all:
  while True:
   st=json.loads(STATE.read_text())
   if len(st['tasks'])==len(st['plan']):break
   batch(1)
  finish()
 else:a.error('choose an action')
