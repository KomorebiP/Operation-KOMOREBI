#!/usr/bin/env python3
"""Synchronous, checkpointed audits. A PASS is written only after every planned task."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODULES=['BinaryWords','BinaryMulDiv','BinarySigned','BinaryEncoding','BinaryCosted','BinaryPricing','BinarySignedCost','BinaryBackend','BinaryExamples']
EXPECTED_PARENT='1dec07bad4136a5809059b0e3a0f014700909210d6c9f823627742fee07bba78'
ALLOWED={'propext','Classical.choice','Quot.sound'}
def digest(p:Path)->str:
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p:Path,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def inputs(kind):
 if kind=='LEAN':
  ps=list((ROOT/'formalization').glob('*.lean'))+list((ROOT/'checks/controls').glob('*.lean'))+[ROOT/'checks/AxiomAudit.lean',ROOT/'DECLARATIONS.json']
 else:
  ps=[ROOT/'binary_backend.py',ROOT/'checks/audit_python.py']+list((ROOT/'baseline').rglob('*.py'))+list((ROOT/'baseline').rglob('*.json'))
 ps += [ROOT/'checks/run_audit.py',ROOT/'tools/validate_manifest.py']
 return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(ps))}
def assert_inputs(before,kind):
 after=inputs(kind)
 if after!=before:raise RuntimeError('Accepted input files changed; refusing successful continuation')
 return after
def run(argv,cwd,env,log):
 t=time.monotonic();started=now()
 try:
  r=subprocess.run(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=45);rc=r.returncode;text=r.stdout;status='completed' if rc==0 else 'failed'
 except subprocess.TimeoutExpired as e:
  rc=124;text=e.stdout or '';text=text.decode() if isinstance(text,bytes) else text;status='timeout'
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(text)
 return {'argv':argv,'cwd':str(cwd),'started_at':started,'runtime_seconds':time.monotonic()-t,'returncode':rc,'process_status':status,'log':str(log.relative_to(ROOT))},text

def manifest(kind,state,result,logs,software):
 after=assert_inputs(state['inputs'],kind)
 rec={'schema_version':2,'claim_id':'MODEL-NORMALIZATION-0.10-'+kind,
  'repository':{'commit':'unavailable: local checkpoint; all inputs pinned by SHA-256','dirty':True,'parent_sha256':EXPECTED_PARENT},
  'command':state['command'],'environment':{'software':software,'hardware':platform.platform()+'; one Lean worker; no CPU-affinity guarantee'},
  'mathematics':{'assertion_tested':('Universal correctness and declared bit gate/cell cost bounds for the scalar binary backend; 27 finite kernel examples; rejection controls' if kind=='LEAN' else 'Independent finite scalar arithmetic tests and replacement of every arithmetic value in 203 frozen discovery fixtures'),
    'coefficient_domain':'exact natural and signed integers represented by little-endian Boolean words; positive divisor/modulus; canonical modular inputs in discovery port',
    'conventions':'LSB-first, leading-zero padding permitted; Euclidean signed division by positive divisors; gate/cell model excludes native runtime and conversion costs',
    'inputs':list(state['inputs']),'bounds':({'modules':9,'generic_theorems':78,'concrete_examples':27,'per_process_timeout_seconds':45} if kind=='LEAN' else {'fixtures':203,'unsigned_pairs':[0,63],'signed_pairs':[-32,32],'moduli':[1,24],'random_bit_widths':[16,32,64,128,256],'seed':2026092110}),
    'non_claims':['No universal lowering of the full discovery program to this bit backend','No CPU/bit-machine/allocation/queue/serialization/conversion runtime theorem','No verified Python extraction, independent referee review or novelty verdict','Parent Lean corpus and upstream Mathlib are not rebuilt']},
  'randomness':{'used':kind=='PYTHON','generator':'Python random.Random' if kind=='PYTHON' else 'none','seed':2026092110 if kind=='PYTHON' else None},
  'run':{'started_at':state['started_at'],'runtime_seconds':sum(t['runtime_seconds'] for t in state['tasks']),'exit_status':0,'status':'completed','missing_results':[],'invalid_results':[],
    'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':1},'per_process_timeout_seconds':45,'time_scope':'sum of completed subprocess durations, not end-to-end wall time'},
  'input_artifacts':[{'path':p,'sha256':h,'sha256_after':after[p]} for p,h in state['inputs'].items()],
  'execution_artifacts':list(state['inputs']),
  'declared_results':[result],
  'outputs':[{'path':result,'sha256':digest(ROOT/result),'kind':'result'}]+[{'path':p,'sha256':digest(ROOT/p),'kind':'log'} for p in logs],
  'checks':state['tasks'],'result':'PASS in the precise stated scope',
  'residual_risks':['Authoring-assistant self-review','Native compiler and upstream cached dependencies trusted as usual','Synthetic regression fixtures; no independently frozen discovery benchmark']}
 write(ROOT/f'{kind}_MANIFEST.json',rec)


def lean_init(runtime:Path,work:Path):
 statepath=work/'audit_state.json'
 if statepath.exists():raise RuntimeError('Checkpoint already exists; use a fresh --work directory')
 work.mkdir(parents=True,exist_ok=True);(work/'build').mkdir()
 lean=runtime/'toolchain/bin/lean';version=subprocess.check_output([str(lean),'--version'],text=True).strip()
 pin=(runtime/'workspace/.lake/packages/mathlib/.git/HEAD').read_text().strip()
 if '4.34.0-rc2' not in version or pin!='aeb72f1e9981b6d35b426b16dca7759be3e7ba06':raise RuntimeError('Wrong toolchain or Mathlib pin')
 software=[{'name':'Lean','version':version},{'name':'Mathlib','version':pin}]
 plan=[{'name':'build_'+m,'module':m,'expected_success':True} for m in MODULES]
 plan+=[{'name':'axioms','file':'checks/AxiomAudit.lean','expected_success':True}]
 for p in sorted((ROOT/'checks/controls').glob('*.lean')):plan.append({'name':'control_'+p.stem,'file':str(p.relative_to(ROOT)),'expected_success':p.stem=='positive'})
 state={'started_at':now(),'runtime':str(runtime),'lean_sha256':digest(lean),'software':software,'inputs':inputs('LEAN'),'plan':plan,'tasks':[],'status':'running','command':[sys.executable,'checks/run_audit.py','lean-init','--runtime',str(runtime),'--work',str(work)]}
 write(statepath,state);print('Initialized cold audit:',len(plan),'tasks;',len(state['inputs']),'pinned inputs')

def lean_step(work:Path,limit:int):
 sp=work/'audit_state.json';s=json.loads(sp.read_text());assert_inputs(s['inputs'],'LEAN')
 if s['status']!='running':raise RuntimeError('Audit is not running: '+s['status'])
 rt=Path(s['runtime']);lean=rt/'toolchain/bin/lean'
 if digest(lean)!=s['lean_sha256']:raise RuntimeError('Compiler changed')
 env=os.environ.copy();env['LEAN_PATH']=':'.join([str(work/'build')]+[str(p) for p in sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]);env['OMP_NUM_THREADS']='1'
 for item in s['plan'][len(s['tasks']):len(s['tasks'])+limit]:
  cmd=[str(lean),'-j1','-DwarningAsError=true']
  if 'module' in item:cmd+=['-o',str(work/'build'/(item['module']+'.olean')),str(ROOT/'formalization'/(item['module']+'.lean'))]
  else:cmd += [str(ROOT/item['file'])]
  rec,text=run(cmd,ROOT/'formalization',env,ROOT/'evidence/cold'/(item['name']+'.log'));rec['name']=item['name'];rec['expected_success']=item['expected_success']
  passed=(rec['returncode']==0) if item['expected_success'] else (rec['returncode'] not in (0,124) and 'error:' in text and not any(t in text.lower() for t in ['unknown module prefix','file not found','unknown package','unknown constant']))
  if item['name']=='axioms' and passed:
   ds=json.loads((ROOT/'DECLARATIONS.json').read_text());names={x['name'] for x in ds};found={};used=set()
   for line in text.splitlines():
    match=re.match(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[(.*)\])",line)
    if match:
     found[match[1]]=set(x.strip() for x in (match[2] or '').split(',') if x.strip());used.update(found[match[1]])
   passed=names<=set(found) and used<=ALLOWED
   rec['audited_count']=len(found);rec['expected_count']=len(names);rec['axioms']=sorted(used);rec['missing']=sorted(names-set(found));rec['unexpected_axioms']=sorted(used-ALLOWED)
  rec['passed']=passed;s['tasks'].append(rec)
  if not passed:s['status']='failed'
  write(sp,s);print(item['name'],rec['returncode'],'PASS' if passed else 'FAIL',round(rec['runtime_seconds'],3),flush=True)
  if not passed:print(text);raise RuntimeError('Cold audit failed at '+item['name'])
 if len(s['tasks'])==len(s['plan']):
  assert_inputs(s['inputs'],'LEAN');s['status']='completed';write(sp,s)
  ds=json.loads((ROOT/'DECLARATIONS.json').read_text());counts={k:sum(d['kind']==k for d in ds) for k in sorted({d['kind'] for d in ds})}
  outputs={str(p.relative_to(work/'build')):digest(p) for p in (work/'build').rglob('*') if p.is_file()}
  result={'status':'PASS','modules':MODULES,'module_count':len(MODULES),'declaration_counts':counts,'total_declarations':len(ds),'concrete_kernel_examples':27,'tasks':s['tasks'],'compiled_artifact_hashes':outputs,'source_hashes':s['inputs'],'lean_sha256':s['lean_sha256'],'software':s['software'],'scope':'Fresh cold build of new scalar backend only; pinned upstream cache reused; no full predecessor Lean replay'}
  write(ROOT/'results/LEAN_AUDIT.json',result)
  manifest('LEAN',s,'results/LEAN_AUDIT.json',[t['log'] for t in s['tasks']],s['software'])
  print('Completed LEAN audit and version-2 manifest')

def python_run():
 s={'started_at':now(),'inputs':inputs('PYTHON'),'command':[sys.executable,'checks/audit_python.py'],'tasks':[]}
 rec,text=run(s['command'],ROOT,os.environ.copy(),ROOT/'evidence/python/audit.log');rec['name']='independent_python_audit';rec['passed']=rec['returncode']==0;s['tasks'].append(rec)
 if not rec['passed']:print(text);raise RuntimeError('Python audit failed')
 assert_inputs(s['inputs'],'PYTHON');r=json.loads((ROOT/'results/PYTHON_AUDIT.json').read_text())
 if r.get('status')!='PASS' or len(r['cases'])!=203:raise RuntimeError('Result scope incomplete')
 manifest('PYTHON',s,'results/PYTHON_AUDIT.json',[rec['log']],[{'name':'Python','version':platform.python_version()}])
 print(text)

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['lean-init','lean-step','python']);a.add_argument('--runtime',type=Path);a.add_argument('--work',type=Path);a.add_argument('--limit',type=int,default=5);p=a.parse_args()
 if p.mode=='lean-init':lean_init(p.runtime,p.work)
 elif p.mode=='lean-step':lean_step(p.work,p.limit)
 else:python_run()
