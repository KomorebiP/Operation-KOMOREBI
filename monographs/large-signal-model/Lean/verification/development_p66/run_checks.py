#!/usr/bin/env python3
"""Fresh source-bound P66 development checks using the shared gated Lean wrapper."""
from pathlib import Path
import subprocess,os,json,time,hashlib,importlib.util,datetime
ROOT=Path(__file__).resolve().parents[2]
WS=ROOT.parents[1]
OUT=Path(__file__).resolve().parent
LEAN=WS/'runtime/gated-bin/lean'
freeze=json.loads((OUT/'SOURCE_FREEZE.json').read_text())
names=list(freeze)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in names:assert sha(ROOT/f'KomorebiLSM/{n}.lean')==freeze[n]['source_sha256']
baseline=ROOT/'KomorebiLSM/PredictableResidual.lean'
assert sha(baseline)=='ace3ef2c5b8d499c10da957c7e34dac2b5751e7c6acc02696a36ce2b2548dc65'
report={'schema':'komorebi.p66-development-checks.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'complete':False,'modules':freeze,'stages':[],'gate':'runtime/gated-bin/lean (current wrapper; no old queued job accepted)'}
def save(): (OUT/'CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
def run(label,args,log,extra=None,control=False):
 env=os.environ.copy();env.update(extra or {})
 started=time.monotonic();r=subprocess.run([str(LEAN),'-j1','-DwarningAsError=true']+list(map(str,args)),cwd=WS,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (OUT/log).write_text(r.stdout)
 good=(r.returncode==1 and 'error: unsolved goals' in r.stdout and '⊢ False' in r.stdout and r.stdout.count('error:')==1) if control else r.returncode==0
 row={'label':label,'command':[str(LEAN),'-j1','-DwarningAsError=true']+list(map(str,args)),'environment_override':extra or {},'returncode':r.returncode,'seconds':round(time.monotonic()-started,6),'passed':good,'log':log,'log_sha256':sha(OUT/log)}
 report['stages'].append(row);save();print(json.dumps({k:row[k] for k in ['label','returncode','seconds','passed']}),flush=True)
 if not good: raise RuntimeError(label+' failed: '+r.stdout[:4000])
 return r.stdout
save()
for n in names:
 run('compile '+n,['-o',ROOT/f'.build/lib/lean/KomorebiLSM/{n}.olean',ROOT/f'KomorebiLSM/{n}.lean'],f'{n}_compile.log')
text=run('all named axioms',[OUT/'AxiomAudit.lean'],'axiom_audit.log')
spec=importlib.util.spec_from_file_location('verify',ROOT/'scripts/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
records=json.loads((OUT/'DECLARATIONS.json').read_text());parsed=v.parse_axioms(text,{x['name'] for x in records});(OUT/'AXIOMS.json').write_text(json.dumps(parsed,indent=2)+'\n')
report['axiom_records']=len(parsed);save()
sig=run('arbitrary-space public signatures',[OUT/'GeneralSpaceSignatures.lean'],'general_space_signatures.log')
assert 'StandardBorelSpace' not in sig and 'condExpKernel' not in sig
report['signature_check']={'StandardBorelSpace_absent':True,'condExpKernel_absent':True};save()
for n in names:
 text=run('kernel replay '+n,[ROOT/'scripts/ReplayModule.lean'],f'{n}_replay.log',{'KOMOREBI_REPLAY_MODULE':'KomorebiLSM.'+n})
 assert 'KERNEL_REPLAY_PASS KomorebiLSM.'+n in text
for n in ['ConditionalBernoulliMissingCentering','PredictableResidualMissingWidth','P66DuplicatedRuleBudget']:
 p=ROOT/f'negative_controls/{n}.lean';run('semantic False control '+n,[p],f'{n}_control.log',control=True)
 report.setdefault('negative_controls',[]).append({'path':str(p.relative_to(ROOT)),'source_sha256':sha(p)})
for n in names:assert sha(ROOT/f'KomorebiLSM/{n}.lean')==freeze[n]['source_sha256']
assert sha(baseline)=='ace3ef2c5b8d499c10da957c7e34dac2b5751e7c6acc02696a36ce2b2548dc65'
report.update(passed=True,complete=True,named_declarations=len(records),named_theorems=sum(x['kind']=='theorem' for x in records),allowed_axioms=['Classical.choice','Quot.sound','propext'],lean_commit='6a10ac8c22beadecabdbb0919c2b50214762f91d',mathlib_commit='aeb72f1e9981b6d35b426b16dca7759be3e7ba06')
save();print('P66_CHECKS_PASS',flush=True)
