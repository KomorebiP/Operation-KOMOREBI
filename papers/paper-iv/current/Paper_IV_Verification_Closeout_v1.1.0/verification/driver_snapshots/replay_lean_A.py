#!/usr/bin/env python3
"""Pinned, serial, fail-closed Paper IV source replay. No dependency downloads.

A completed result checks all production modules, reviewed declaration kinds,
the inherited namespace axiom audit, and real compiler positive/negative controls.
A continuation may reuse objects only from this run's authenticated successful steps.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, signal, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEAN_SHA='e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
LEAN_COMMIT='6a10ac8c22beadecabdbb0919c2b50214762f91d'
ALLOWED={'propext','Classical.choice','Quot.sound'}

def sha(p:Path)->str:
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def stamp()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
def write_json(p:Path,data)->None:
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(data,indent=2)+'\n');q.replace(p)
def execute(argv:list[str],cwd:Path,env:dict[str,str],timeout:float,log:Path)->dict:
 begin=time.monotonic();record={'argv':argv,'cwd':str(cwd),'started_utc':stamp(),'timeout_seconds':timeout}
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('wb') as f:
  proc=subprocess.Popen(argv,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=(os.name=='posix'))
  try:code=proc.wait(timeout=timeout);record['timed_out']=False
  except subprocess.TimeoutExpired:
   if os.name=='posix':os.killpg(proc.pid,signal.SIGKILL)
   else:proc.kill()
   code=proc.wait();record['timed_out']=True
 record.update(returncode=code,seconds=round(time.monotonic()-begin,4),finished_utc=stamp(),log=str(log.relative_to(ROOT)) if log.is_relative_to(ROOT) else str(log),log_sha256=sha(log))
 return record

def diagnostic_accept(record:dict,text:str,kind:str)->bool:
 if record['timed_out']:return False
 if kind=='positive':return record['returncode']==0 and 'PAPER_IV_POSITIVE_CONTROL_PASS' in text
 if kind=='false':return record['returncode']>0 and 'error:' in text and ('false' in text.lower() or 'decide' in text)
 if kind=='sorry':return record['returncode']>0 and 'sorry' in text
 if kind=='missing-premise':return record['returncode']>0 and 'error:' in text and ('rfl' in text or 'not definitionally equal' in text)
 if kind=='custom-axiom':return record['returncode']>0 and 'PAPER_IV_CUSTOM_AXIOM_REJECTED' in text
 if kind=='wrong-kind':return record['returncode']>0 and 'PAPER_IV_WRONG_KIND_REJECTED' in text
 raise ValueError(kind)

def check_axiom_reports(text:str,expected:set[str])->dict:
 if 'sorryAx' in text:raise ValueError('Placeholder axiom in audit')
 pattern=r"^'([^'\n]+)' (?:depends on axioms:\s*\[([^\]]*)\]|(does not depend on any axioms))"
 found={}
 for m in re.finditer(pattern,text,re.M):
  name=m.group(1)
  if name in found:raise ValueError('Duplicate audit report '+name)
  ax={x.strip() for x in (m.group(2) or '').split(',') if x.strip()}
  if ax-ALLOWED:raise ValueError('Forbidden axioms '+str(ax-ALLOWED))
  found[name]=sorted(ax)
 if set(found)!=expected:raise ValueError(f'Audit name mismatch: missing={sorted(expected-set(found))[:10]}, extra={sorted(set(found)-expected)[:10]}')
 return {'names':len(found),'allowed_union':sorted({a for axioms in found.values() for a in axioms}),'reports':found}

def main()->int:
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--resume',action='store_true');ap.add_argument('--timeout',type=float,default=300);args=ap.parse_args()
 runtime=args.runtime.resolve();work=args.work.resolve();active=ROOT/'formalization/lean';out=work/'objects';logs=work/'logs';report_path=work/'REPLAY.json'
 contract=json.loads((ROOT/'verification/SOURCE_CONTRACT.json').read_text());spec_path=ROOT/contract['contract_relative'];spec=json.loads(spec_path.read_text())
 proof_sources={f:sha(active/f) for f in contract['source_sha256']}
 if proof_sources!=contract['source_sha256']:raise ValueError('Mathematical source identity mismatch')
 if sha(spec_path)!=contract['contract_sha256']:raise ValueError('Reviewed declaration contract changed')
 for path,digest in contract['configuration_sha256'].items():
  if sha(active/path)!=digest:raise ValueError('Configuration changed '+path)
 if not args.resume and work.exists():raise ValueError('Work directory exists. Choose an empty path or use --resume.')
 work.mkdir(parents=True,exist_ok=True);out.mkdir(exist_ok=True);logs.mkdir(exist_ok=True)
 report={'schema':'paper_iv.fresh_replay.v1','status':'RUNNING','started_utc':stamp(),'runtime':str(runtime),'source_contract_sha256':sha(ROOT/'verification/SOURCE_CONTRACT.json'),'checks':[],'production_done':[]}
 if args.resume:
  if not report_path.exists():raise ValueError('Cannot resume absent report')
  report=json.loads(report_path.read_text())
  if report['status']=='PASS':raise ValueError('Already complete; choose a new work directory for another replay')
  if report['source_contract_sha256']!=sha(ROOT/'verification/SOURCE_CONTRACT.json'):raise ValueError('Changed contract on resume')
  for entry in report['production_done']:
   for rel,digest in entry['objects'].items():
    if sha(out/rel)!=digest:raise ValueError('Prior object changed '+rel)
   if sha(ROOT/entry['source'])!=entry['source_sha256']:raise ValueError('Prior source changed')
  report['resume_events']=report.get('resume_events',[])+[{'at_utc':stamp(),'prior_status':report['status']}];report['status']='RUNNING'
 write_json(report_path,report)
 def persist():write_json(report_path,report)
 def run(label,argv,cwd=active,timeout=None):
  print('RUN',label,flush=True);r=execute([str(x) for x in argv],cwd,env,timeout or args.timeout,logs/(label+'.log'));r['label']=label;report['checks'].append(r);persist();return r,(logs/(label+'.log')).read_text(errors='replace')
 try:
  lean=runtime/'toolchain/bin/lean'
  if sha(lean)!=LEAN_SHA:raise ValueError('Pinned compiler hash mismatch')
  env=dict(os.environ,PATH=str(lean.parent)+os.pathsep+os.environ.get('PATH',''),MALLOC_ARENA_MAX='2',PYTHONDONTWRITEBYTECODE='1',TZ='UTC',LC_ALL='C.UTF-8')
  env.pop('LD_PRELOAD',None)
  pins=json.loads((active/'lake-manifest.json').read_text())['packages'];packages=runtime/'workspace/.lake/packages'
  libpaths=[str(out)];pin_results=[]
  for pkg in pins:
   path=packages/pkg['name'];p=subprocess.run(['git','-C',str(path),'rev-parse','HEAD'],capture_output=True,text=True,timeout=30)
   if p.returncode or p.stdout.strip()!=pkg['rev']:raise ValueError('Dependency revision mismatch '+pkg['name'])
   libpaths.append(str(path/'.lake/build/lib/lean'));pin_results.append({'name':pkg['name'],'rev':pkg['rev']})
  env['LEAN_PATH']=os.pathsep.join(libpaths);env['LEAN_SRC_PATH']=str(active)
  report['pins']={'lean_sha256':sha(lean),'lean_commit':LEAN_COMMIT,'dependencies':pin_results,'external_cache_reused_not_rebuilt':True};persist()
  vr,vt=run('lean_version',[lean,'--version'])
  if vr['returncode'] or LEAN_COMMIT not in vt:raise ValueError('Lean version check failed')
  flags=['-j1','-M3072','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3','-Dpp.unicode.fun=true']
  already=[x['module'] for x in report['production_done']]
  if already!=contract['production_modules'][:len(already)]:raise ValueError('Resume is not an exact production prefix')
  for module in contract['production_modules'][len(already):]:
   rel=Path(module.replace('.','/')+'.lean');dest=out/rel.with_suffix('.olean');dest.parent.mkdir(parents=True,exist_ok=True)
   r,t=run('compile_'+module,[lean,*flags,'-o',dest,'-i',dest.with_suffix('.ilean'),rel])
   if r['returncode'] or r['timed_out']:raise ValueError('Production compilation failed '+module+': '+t[-1500:])
   artifacts={p.relative_to(out).as_posix():sha(p) for p in dest.parent.glob(dest.stem+'.*') if p.is_file()}
   if dest.relative_to(out).as_posix() not in artifacts:raise ValueError('No compiled object '+module)
   report['production_done'].append({'module':module,'source':str((active/rel).relative_to(ROOT)),'source_sha256':sha(active/rel),'objects':artifacts});persist()
   print('PASS',len(report['production_done']),'/',len(contract['production_modules']),module,r['seconds'],flush=True)
  # Formal kind resolution in bounded commands using the exact reviewed contract.
  code=['import KomorebiPaperIV','open Lean Elab Command','set_option maxRecDepth 10000']
  for offset in range(0,len(spec['targets']),48):
   batch=spec['targets'][offset:offset+48];code+=['run_cmd do','  let env ← getEnv']
   for item in batch:
    c='thmInfo' if item['kind']=='theorem' else 'defnInfo';name=item['declaration']
    code += [f'  match env.find? ``{name} with',f'  | some (.{c} _) => pure ()',f'  | _ => throwError "PAPER_IV_KIND_MISMATCH: {name}"']
   code += [f'  logInfo "PAPER_IV_KIND_BATCH_PASS {offset} {len(batch)}"']
  code+=['run_cmd do',f'  logInfo "PAPER_IV_KIND_PASS {len(spec["targets"])}"']
  kinds=work/'ReviewedKinds.lean';kinds.write_text('\n'.join(code)+'\n')
  r,t=run('reviewed_kinds',[lean,*flags,kinds])
  if r['returncode'] or r['timed_out'] or t.count(f'PAPER_IV_KIND_PASS {len(spec["targets"])}')!=1:raise ValueError('Reviewed kind audit failed '+t[-1500:])
  for offset in range(0,len(spec['targets']),48):
   token=f'PAPER_IV_KIND_BATCH_PASS {offset} {len(spec["targets"][offset:offset+48])}'
   if t.count(token)!=1:raise ValueError('Kind batch missing/duplicate '+token)
  report['reviewed_kinds_passed']=len(spec['targets']);persist()
  audit=active/'KomorebiPaperIV/KernelAudit.lean';r,t=run('original_kernel_audit',[lean,*flags,audit])
  if r['returncode'] or r['timed_out']:raise ValueError('Kernel audit failed '+t[-1500:])
  parsed=check_axiom_reports(t,{x['declaration'] for x in spec['targets']})
  sent=f'FAIL-CLOSED PAPER IV v1.0.0 KERNEL AUDIT PASS: {spec["namespace_declarations"]} declarations ({spec["namespace_theorems"]} theoremInfo); {len(spec["targets"])} explicit mapped targets; allowed axioms only: propext, Classical.choice, Quot.sound'
  if t.count(sent)!=1:raise ValueError('Exact namespace sentinel missing/duplicate')
  report['kernel_audit']={'status':'PASS','namespace_declarations':spec['namespace_declarations'],'namespace_theorems':spec['namespace_theorems'],'mapped_targets':len(spec['targets']),'axiom_union':parsed['allowed_union']};write_json(work/'AXIOM_REPORTS.json',parsed);persist()
  fixtures={
   'positive':'import KomorebiPaperIV.CyclicFilters\nexample (f : PowerSeries Nat) : Komorebi.PaperIV.cyclicProjector 3 1 (Komorebi.PaperIV.cyclicProjector 3 1 f) = Komorebi.PaperIV.cyclicProjector 3 1 f := Komorebi.PaperIV.cyclicProjector_idempotent 3 1 f\nrun_cmd Lean.logInfo "PAPER_IV_POSITIVE_CONTROL_PASS"\n',
   'false':'import Mathlib.Data.Nat.Basic\ntheorem paperIVFalse : (0 : Nat) = 1 := by decide\n',
   'sorry':'import Mathlib.Data.Nat.Basic\ntheorem paperIVPlaceholder : (0 : Nat) = 1 := by sorry\n',
   'missing-premise':'import Mathlib.Data.Nat.Basic\ntheorem paperIVOmitted (a b : Nat) : a = b := by rfl\n',
   'custom-axiom':'import KomorebiPaperIV.CyclicFilters\nnamespace PaperIVNegativeFixture\naxiom injected : False\ntheorem invalid : False := injected\nend PaperIVNegativeFixture\nopen Lean Elab Command\nrun_cmd do\n  let axioms ← Lean.collectAxioms ``PaperIVNegativeFixture.invalid\n  if axioms.contains ``PaperIVNegativeFixture.injected then\n    throwError "PAPER_IV_CUSTOM_AXIOM_REJECTED"\n  else\n    logInfo "ERROR_CONTROL_MISSED_INJECTION"\n',
   'wrong-kind':'import KomorebiPaperIV.CyclicFilters\nopen Lean Elab Command\nrun_cmd do\n  let env ← getEnv\n  match env.find? ``Komorebi.PaperIV.cyclicProjector with\n  | some (.thmInfo _) => logInfo "ERROR_KIND_CONTROL_ACCEPTED_DEFINITION"\n  | _ => throwError "PAPER_IV_WRONG_KIND_REJECTED"\n'
  }
  controls=[]
  for name,source in fixtures.items():
   f=work/('Control_'+name.replace('-','_')+'.lean');f.write_text(source)
   r,t=run('control_'+name,[lean,*flags,f]);ok=diagnostic_accept(r,t,name);controls.append({'name':name,'passed':ok,'source_sha256':sha(f),'check_label':r['label']})
   report['controls']=controls;persist()
   if not ok:raise ValueError('Compiler control failed '+name+': '+t[-1500:])
  if {f:sha(active/f) for f in contract['source_sha256']}!=proof_sources:raise ValueError('Sources changed during execution')
  report['status']='PASS';report['finished_utc']=stamp();report['production_count']=len(report['production_done']);persist();print('PAPER_IV_REPLAY_PASS',report['production_count'],flush=True);return 0
 except BaseException as exc:
  report['status']='FAILED';report['finished_utc']=stamp();report['error']=str(exc);persist();print('PAPER_IV_REPLAY_FAILED:',exc,flush=True);return 1
if __name__=='__main__':sys.exit(main())
