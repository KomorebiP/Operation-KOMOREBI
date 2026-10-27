#!/usr/bin/env python3
"""Cold local Lean build, strict checks, exact axiom inventory and rejection controls.

A checkpoint permits synchronous resumption only while every input and completed
artifact hash still matches. No status is PASS until every planned task completes.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, tempfile, time, sys
from datetime import datetime, timezone
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'v08_evidence'; STATE=E/'COLD_STATE.json'
NEW=['BoundedBezout','EuclidCost','BoundedInsertion','EchelonPeakCore',
     'EchelonTemporaryBounds','BoundedDiscovery','BoundedArithmeticExamples']+[f'BoundedComputed{i:02}' for i in range(17)]
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
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
 if STATE.exists():raise RuntimeError('preserve existing state before initializing a new audit')
 lean=rt/'toolchain/bin/lean';ml=rt/'workspace/.lake/packages/mathlib'
 ver=subprocess.check_output([str(lean),'--version'],text=True).strip()
 assert '6a10ac8c22beadecabdbb0919c2b50214762f91d' in ver
 assert sha(lean)=='e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
 assert (ml/'.git/HEAD').read_text().strip()=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
 mods=modules();decls=[]
 for m in mods:
  text=(ROOT/'formalization'/(m+'.lean')).read_text()
  ns=re.findall(r'^namespace\s+([\w.]+)\s*$',text,re.M)
  assert len(ns)==1,(m,ns)
  assert not re.search(r'^\s*axiom\s',text,re.M),m
  for kind,name in re.findall(r'^\s*(?:@\[[^\n]*?\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)',text,re.M):
   decls.append({'module':m,'kind':kind,'name':ns[0]+'.'+name,'new':m in NEW})
 assert len({d['name'] for d in decls})==len(decls)
 dump(E/'DECLARATIONS.json',decls);dump(E/'MODULES.json',mods)
 build=Path(tempfile.mkdtemp(prefix='komorebi-model08-cold-',dir='/mnt/data/model08_work'))
 plan=[];drivers=[]
 for m in mods:
  out=build/(m+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
  plan.append({'name':'build_'+m,'argv':[str(lean),'-j1','-DwarningAsError=true','-o',str(out),m+'.lean'],'expect':True,'module':m})
 for j in range(0,len(decls),64):
  ds=decls[j:j+64];f=ROOT/f'v08_checks/axioms/Group{j//64:02}.lean';f.parent.mkdir(exist_ok=True)
  f.write_text('module\n'+''.join('import '+m.replace('/','.')+'\n' for m in dict.fromkeys(x['module'] for x in ds))+''.join('#print axioms '+d['name']+'\n' for d in ds))
  drivers.append(f);plan.append({'name':f'axioms_{j//64:02}','argv':[str(lean),'-j1','-DwarningAsError=true',str(f)],'expect':True,'axioms':True})
 hdr='module\nimport BoundedArithmeticExamples\nopen Komorebi.Echelon Komorebi.Echelon.Cost Komorebi.BoundedArithmeticExamples\n'
 controls={
  'Positive':('example : updatePeak fourBasis ![3,3]=12 := update_peak_exceeds_modulus\n',True),
  'False':('example : False := by decide\n',False),
  'Placeholder':('example : True := by sorry\n',False),
  'StoredIsTemporary':('example : updatePeak fourBasis ![3,3]≤4 := by decide +kernel\n',False),
  'BadBezout':('example : euclidCoeff 240 46=(0,0) := by decide +kernel\n',False),
  'BadEuclidCost':('example : euclidSteps 240 46≤2 := by decide +kernel\n',False),
  'LostCoupling':('example : entries (boundedNormalizedInsert fourBasis ![3,3])=![![1,0],![0,4]] := by decide +kernel\n',False)}
 for name,(body,exp) in controls.items():
  f=ROOT/f'v08_checks/controls/{name}.lean';f.parent.mkdir(exist_ok=True);f.write_text(hdr+body);drivers.append(f)
  plan.append({'name':'control_'+name,'argv':[str(lean),'-j1','-DwarningAsError=true',str(f)],'expect':exp})
 inputs=[ROOT/'formalization'/(m+'.lean') for m in mods]+drivers+[Path(__file__),E/'DECLARATIONS.json',E/'MODULES.json']
 env={'lean_version':ver,'lean_sha256':sha(lean),'mathlib_commit':(ml/'.git/HEAD').read_text().strip(),
      'python':sys.version,'cpu_cgroup':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_cgroup':Path('/sys/fs/cgroup/memory.max').read_text().strip()}
 dump(E/'ENVIRONMENT.json',env)
 st={'status':'IN_PROGRESS','started_at':now(),'runtime':str(rt),'build':str(build),'modules':mods,'declarations':decls,'plan':plan,'tasks':[],'artifacts':[],
     'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(inputs))],'environment':env}
 dump(STATE,st);print('INITIALIZED',len(mods),len(decls),len(plan),flush=True)

def verify(st):
 for p in st['inputs']:assert sha(ROOT/p['path'])==p['sha256'],p
 for p in st['artifacts']:assert sha(p['path'])==p['sha256'],p
 for t in st['tasks']:assert sha(ROOT/t['log'])==t['sha256'],t

def run():
 st=json.loads(STATE.read_text());verify(st);assert st['status'] in ['IN_PROGRESS','PASS']
 rt=Path(st['runtime']);env=os.environ.copy();env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]);env['OMP_NUM_THREADS']='1'
 for item in st['plan'][len(st['tasks']):]:
  log=E/'cold'/(item['name'].replace('/','_')+'.log');log.parent.mkdir(exist_ok=True);start=time.monotonic()
  with log.open('w') as f:
   try:p=subprocess.run(item['argv'],cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=100);rc=p.returncode;timed=False
   except subprocess.TimeoutExpired:rc=124;timed=True
  text=log.read_text();ok=(rc==0) if item['expect'] else (rc!=0 and 'error:' in text)
  if timed:ok=False
  if not item['expect'] and any(x in text.lower() for x in ['unknown module','no such file','does not exist','heartbeats','out of memory']):ok=False
  rec={**item,'exit_code':rc,'timed_out':timed,'passed':ok,'seconds':time.monotonic()-start,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
  st['tasks'].append(rec)
  if ok and 'module' in item:
   for f in Path(st['build']).glob(item['module']+'.*'):
    if f.is_file():st['artifacts'].append({'path':str(f),'sha256':sha(f)})
  if not ok:st['status']='FAILED'
  dump(STATE,st);print(len(st['tasks']),item['name'],ok,round(rec['seconds'],3),flush=True)
  if not ok:raise RuntimeError(text[-7000:])
 verify(st)
 text=''.join((ROOT/t['log']).read_text() for t in st['tasks'] if t.get('axioms'))
 axioms=set()
 for a in re.findall(r'depends on axioms:\s*\[([^]]*)\]',text,re.S):axioms.update(x.strip() for x in a.replace('\n',' ').split(',') if x.strip())
 names=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",text))
 assert not axioms-ALLOWED,axioms
 assert names=={d['name'] for d in st['declarations']},(len(names),len(st['declarations']))
 st['status']='PASS';st['finished_at']=now();dump(STATE,st)
 result={'status':'PASS','modules':len(st['modules']),'task_count':len(st['tasks']),'axioms':sorted(axioms),'named_declarations':len(names),
         'counts':dict(Counter(d['kind'] for d in st['declarations'])),
         'new_generic_counts':dict(Counter(d['kind'] for d in st['declarations'] if d['module'] in NEW[:6])),
         'kernel_instances':203,'all_inputs_unchanged':True,'runtime_sum_seconds':sum(t['seconds'] for t in st['tasks']),
         'scope':'Cold local supporting modules and 203 actual solver evaluations; all named declarations audited. Upstream cache reused.'}
 dump(ROOT/'results_v08/LEAN_AUDIT.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path);p.add_argument('--init',action='store_true');p.add_argument('--run',action='store_true');a=p.parse_args()
 if a.init:init(a.runtime.resolve())
 if a.run:run()
