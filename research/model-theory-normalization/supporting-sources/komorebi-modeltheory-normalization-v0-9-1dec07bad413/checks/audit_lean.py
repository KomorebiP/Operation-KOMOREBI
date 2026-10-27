"""Cold local verification of the costed evaluator and 203 exact result/count pairs.

Each completed task is checkpointed with immutable source and output hashes.
Only completion of the entire plan yields PASS. Upstream pinned cache is reused.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/cold';STATE=E/'STATE.json'
TARGETS=['CostedExamples']+[f'CostedComputed{i:02}' for i in range(17)]
NEW={'CostedPrimitives','CostedLattice','CostedDiscovery','CostedBounds','CostedExamples'}|set(TARGETS[1:])
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def closure(targets):
 seen=set();out=[]
 def visit(m):
  if m in seen:return
  seen.add(m);p=ROOT/'formalization'/(m.replace('.','/')+'.lean')
  for dep in re.findall(r'^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)',p.read_text(),re.M):
   if (ROOT/'formalization'/(dep.replace('.','/')+'.lean')).exists():visit(dep)
  out.append(m)
 for m in targets:visit(m)
 return out

def initialize(rt):
 if STATE.exists():raise RuntimeError('Existing audit state: preserve it rather than overwriting.')
 lean=rt/'toolchain/bin/lean';ml=rt/'workspace/.lake/packages/mathlib'
 version=subprocess.check_output([str(lean),'--version'],text=True).strip()
 if '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:raise RuntimeError(version)
 assert sha(lean)=='e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
 assert (ml/'.git/HEAD').read_text().strip()=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
 mods=closure(TARGETS);decls=[]
 for m in mods:
  text=(ROOT/'formalization'/(m.replace('.','/')+'.lean')).read_text()
  ns=re.findall(r'^namespace\s+([\w.]+)\s*$',text,re.M)
  assert len(ns)==1,(m,ns)
  assert not re.search(r'^\s*axiom\s',text,re.M)
  for kind,name in re.findall(r'^\s*(?:@\[[^\n]*?\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)',text,re.M):
   decls.append({'module':m,'kind':kind,'name':ns[0]+'.'+name,'new':m in NEW})
 assert len({d['name'] for d in decls})==len(decls)
 dump(ROOT/'evidence/DECLARATIONS.json',decls);dump(ROOT/'evidence/MODULES.json',mods)
 build=Path(tempfile.mkdtemp(prefix='komorebi-model09-cold-',dir='/mnt/data'))
 plan=[];drivers=[]
 for m in mods:
  out=build/(m.replace('.','/')+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
  plan.append({'name':'build_'+m,'module':m,'expected_success':True,'argv':[str(lean),'-j1','-DwarningAsError=true','-o',str(out),m.replace('.','/')+'.lean']})
 for j in range(0,len(decls),96):
  group=decls[j:j+96];f=ROOT/f'checks/axioms/Group{j//96:02}.lean';f.parent.mkdir(exist_ok=True)
  f.write_text('module\n'+''.join('import '+m+'\n' for m in dict.fromkeys(d['module'] for d in group))+''.join('#print axioms '+d['name']+'\n' for d in group))
  drivers.append(f);plan.append({'name':f'axioms_{j//96:02}','axioms':True,'expected_success':True,'argv':[str(lean),'-j1','-DwarningAsError=true',str(f)]})
 hdr='module\nimport CostedExamples\nopen Komorebi.Costed Komorebi.CostedExamples Komorebi.Echelon\n'
 controls={
  'Positive':('example : (updateEval fourBasis ![3,3]).2=58 := update_units\n',True),
  'False':('example : False := by decide\n',False),
  'Placeholder':('example : True := by sorry\n',False),
  'UndercountedUpdate':('example : (updateEval fourBasis ![3,3]).2=57 := by decide +kernel\n',False),
  'OmittedNormalization':('example : (normalizeEval fourBasis).2=0 := by decide +kernel\n',False),
  'WrongWordOrder':('example : (testEval actions observation ([0,1],0)).1=![1,1] := by decide +kernel\n',False),
  'FreeFailure':('example : (coordinatesEval fourBasis ![3,3]).2=0 := by decide +kernel\n',False),
  'BadGcd':('example : (gcdEval 240 46).1=1 := by decide +kernel\n',False),
 }
 for name,(body,ok) in controls.items():
  f=ROOT/f'checks/controls/{name}.lean';f.parent.mkdir(exist_ok=True);f.write_text(hdr+body);drivers.append(f)
  plan.append({'name':'control_'+name,'expected_success':ok,'argv':[str(lean),'-j1','-DwarningAsError=true',str(f)]})
 inputs=[ROOT/'formalization'/(m.replace('.','/')+'.lean') for m in mods]+drivers+[Path(__file__),ROOT/'evidence/DECLARATIONS.json',ROOT/'evidence/MODULES.json',ROOT/'source_records/COSTED_CASES.json']
 env={'lean_version':version,'lean_sha256':sha(lean),'mathlib_commit':(ml/'.git/HEAD').read_text().strip(),
      'cpu_quota':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_limit':Path('/sys/fs/cgroup/memory.max').read_text().strip()}
 dump(ROOT/'evidence/ENVIRONMENT.json',env)
 dump(STATE,{'status':'IN_PROGRESS','started_at':now(),'runtime':str(rt),'build':str(build),'modules':mods,'declarations':decls,'plan':plan,'tasks':[],
    'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(inputs))],'artifacts':[],'environment':env})
 print('initialized:',len(mods),'modules,',len(decls),'declarations,',len(plan),'tasks',flush=True)

def verify(st):
 for p in st['inputs']:assert sha(ROOT/p['path'])==p['sha256'],p
 for p in st['artifacts']:assert sha(p['path'])==p['sha256'],p
 for t in st['tasks']:assert sha(ROOT/t['log'])==t['log_sha256'],t

def run():
 st=json.loads(STATE.read_text());verify(st)
 assert st['status'] in ['IN_PROGRESS','PASS']
 rt=Path(st['runtime']);env=os.environ.copy();env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))])
 env['OMP_NUM_THREADS']='1'
 for task in st['plan'][len(st['tasks']):]:
  log=E/(task['name'].replace('/','_')+'.log');t0=time.monotonic()
  with log.open('w') as f:
   try:rc=subprocess.run(task['argv'],cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120).returncode;timed=False
   except subprocess.TimeoutExpired:rc=124;timed=True
  text=log.read_text();ok=(rc==0 if task['expected_success'] else rc!=0 and 'error:' in text)
  if timed:ok=False
  if not task['expected_success'] and any(x in text.lower() for x in ['unknown module','no such file','does not exist','heartbeats','out of memory','failed to synthesize']):ok=False
  rec={**task,'exit_code':rc,'timed_out':timed,'passed':ok,'seconds':time.monotonic()-t0,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)}
  st['tasks'].append(rec)
  if ok and 'module' in task:
   for f in Path(st['build']).glob(task['module'].replace('.','/')+'.*'):
    if f.is_file():st['artifacts'].append({'path':str(f),'sha256':sha(f)})
  if not ok:st['status']='FAILED'
  dump(STATE,st);print(len(st['tasks']),task['name'],ok,round(rec['seconds'],3),flush=True)
  if not ok:raise RuntimeError(text[-12000:])
 verify(st)
 text='\n'.join((ROOT/t['log']).read_text() for t in st['tasks'] if t.get('axioms'))
 ax=set()
 for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]',text,re.S):ax.update(x.strip() for x in group.replace('\n',' ').split(',') if x.strip())
 names=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",text))
 assert ax<=ALLOWED,ax
 assert names=={d['name'] for d in st['declarations']},(len(names),len(st['declarations']))
 st['status']='PASS';st['finished_at']=now();dump(STATE,st)
 report={'status':'PASS','modules':len(st['modules']),'inherited_modules':sum(m not in NEW for m in st['modules']),'tasks':len(st['tasks']),
   'named_declarations':len(names),'axioms':sorted(ax),'counts':dict(Counter(d['kind'] for d in st['declarations'])),
   'new_generic_counts':dict(Counter(d['kind'] for d in st['declarations'] if d['module'] in NEW and not d['module'].startswith('CostedComputed') and d['module']!='CostedExamples')),
   'kernel_result_and_cost_pairs':203,'all_inputs_unchanged':True,'compile_seconds_sum':sum(t['seconds'] for t in st['tasks']),
   'scope':'One cold build of local dependency closure, 203 exact computed result/count pairs, all declarations audited; pinned upstream cache reused.'}
 dump(ROOT/'results/LEAN_AUDIT.json',report);print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--init',action='store_true');p.add_argument('--runtime',type=Path);p.add_argument('--run',action='store_true');a=p.parse_args()
 if a.init:initialize(a.runtime.resolve())
 if a.run:run()
