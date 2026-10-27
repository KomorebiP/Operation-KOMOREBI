#!/usr/bin/env python3
"""Verify block 16 and its source dependencies serially.

Default rebuilds the block's whole project dependency closure, not the unrelated
full corpus. --reuse-project-dependencies records exact reused object hashes and
always recompiles the six new modules. Both modes reuse pinned Mathlib artifacts.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, platform, signal, subprocess, sys, time
import verify
ROOT=pathlib.Path(__file__).resolve().parents[1]
NEW=['CalibrationFrame','CalibrationRecovery','CalibrationSelection','CalibrationHierarchy','ApproximateCalibration','CalibrationExamples']
PREFIX='Komorebi.SufficientResolution.'

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--runtime',type=pathlib.Path,required=True)
 ap.add_argument('--out',default='verification/block16')
 ap.add_argument('--reuse-project-dependencies',action='store_true')
 ap.add_argument('--timeout',type=int,default=240)
 args=ap.parse_args();kit=args.runtime.resolve();out=(ROOT/args.out).resolve()
 if not out.is_relative_to(ROOT):ap.error('output must remain inside project')
 if args.timeout<=0:ap.error('timeout must be positive')
 out.mkdir(parents=True,exist_ok=True)
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.monotonic()
 events=[];passed=False;error=None;audited={};dep_objects={}
 seen=set();order=[]
 def visit(n):
  if n in seen:return
  seen.add(n)
  p=ROOT/'Komorebi/SufficientResolution'/f'{n}.lean'
  for line in p.read_text().splitlines():
   if line.startswith('import '+PREFIX):visit(line[len('import '+PREFIX):].strip())
  order.append(n)
 for n in NEW:visit(n)
 rows=[r for r in verify.registry() if pathlib.Path(r['file']).stem in NEW]
 source_paths=[ROOT/'KomorebiBlock16.lean', ROOT/'lakefile.toml',ROOT/'lake-manifest.json',ROOT/'lean-toolchain',
   ROOT/'scripts/verify.py',ROOT/'scripts/verify_block16.py',ROOT/'scripts/check_calibration.py']
 source_paths+=sorted((ROOT/'scripts').glob('*.py'))
 source_paths += [ROOT/'Komorebi/SufficientResolution'/f'{n}.lean' for n in order]
 source_paths=sorted(set(source_paths))
 before={str(p.relative_to(ROOT)):verify.sha(p) for p in source_paths}
 base=['bash',str(kit/'run.sh')]
 env=os.environ.copy();env['LEAN_NUM_THREADS']='1'
 def run(name,argv,expect_failure=False):
  log=out/f'{name}.log';start=time.monotonic();timed=False
  with log.open('w') as f:
   p=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:rc=p.wait(timeout=args.timeout)
   except subprocess.TimeoutExpired:
    timed=True;os.killpg(p.pid,signal.SIGKILL);p.wait();rc=124
  text=log.read_text(errors='replace');ok=(rc!=0 if expect_failure else rc==0) and not timed
  events.append({'name':name,'argv':argv,'exit_status':rc,'expected_failure':expect_failure,
    'timeout':timed,'seconds':time.monotonic()-start,'passed':ok,'log':str(log.relative_to(ROOT))})
  print(('PASS ' if ok else 'FAIL ')+name,flush=True)
  if not ok:raise RuntimeError(name+' failed: '+str(log))
  return text
 try:
  run('attach',base+['attach',str(ROOT)])
  ver=run('lean_version',base+['lean','--version'])
  if '4.34.0-rc2' not in ver:raise RuntimeError('Incorrect Lean version')
  manifest=json.loads((ROOT/'lake-manifest.json').read_text())
  for pkg in manifest['packages']:
   got=run('pin_'+pkg['name'],['git','-C',str(ROOT/manifest['packagesDir']/pkg['name']),'rev-parse','HEAD'])
   if got.strip()!=pkg['rev']:raise RuntimeError('Dependency revision mismatch')
  build=ROOT/'.lake/build/lib/lean';build.mkdir(parents=True,exist_ok=True)
  import re
  for src in sorted((ROOT/'Komorebi').rglob('*.lean')):
   text=re.sub(r'/\-.*?\-/','',src.read_text(),flags=re.S);text=re.sub(r'--[^\n]*','',text)
   if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',text):raise RuntimeError('Forbidden source: '+str(src))
  for n in order:
   src=ROOT/'Komorebi/SufficientResolution'/f'{n}.lean'
   text=re.sub(r'/\-.*?\-/','',src.read_text(),flags=re.S);text=re.sub(r'--[^\n]*','',text)
   if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',text):raise RuntimeError('Forbidden production source: '+n)
   obj=build/'Komorebi/SufficientResolution'/f'{n}.olean';obj.parent.mkdir(parents=True,exist_ok=True)
   if args.reuse_project_dependencies and n not in NEW:
    if not obj.is_file():raise RuntimeError('Missing reusable project dependency: '+n)
    dep_objects[n]={'source_sha256':verify.sha(src),'object_sha256':verify.sha(obj)}
   else:
    obj.unlink(missing_ok=True)
    run('compile_'+n,base+['lake','env','lean','-j1','-DwarningAsError=true','-o',str(obj.relative_to(ROOT)),str(src.relative_to(ROOT))])
  run('compile_block_root',base+['lake','env','lean','-j1','-DwarningAsError=true','-o',str((build/'KomorebiBlock16.olean').relative_to(ROOT)),'KomorebiBlock16.lean'])
  audit=out/'AuditNew.lean';audit.write_text('import KomorebiBlock16\n'+'\n'.join('#print axioms '+r['name'] for r in rows)+'\n')
  text=run('new_axiom_audit',base+['lake','env','lean','-j1','-DwarningAsError=true',str(audit.relative_to(ROOT))])
  audited=verify.parse_axioms(text)
  if set(audited)!={r['name'] for r in rows}:raise RuntimeError('Audit name coverage mismatch')
  if any(set(ax)-verify.ALLOWED for ax in audited.values()):raise RuntimeError('Unexpected axiom dependency')
  (out/'axioms.json').write_text(json.dumps(audited,indent=2)+'\n')
  sigs=out/'PrincipalSignatures.lean'
  sig_names=['CalibrationFrame.Frame.measured_operator_bound','CalibrationFrame.Frame.measured_operator_bound_of_analysis_bound','CalibrationFrame.Frame.exact_calibration_identifies','CalibrationFrame.equiv_calibration_bound','ApproximateCalibration.approximate_frame_bound','ApproximateCalibration.measured_approximate_operator_bound','CalibrationRecovery.generated_operator_bound','CalibrationRecovery.calibrated_consistent','CalibrationRecovery.calibrated_error_norm_limit','CalibrationSelection.exists_accepted_from_calibration','CalibrationSelection.calibrated_selected_consistent','CalibrationHierarchy.hierarchical_operator_bound','CalibrationExamples.partial_not_surjective','CalibrationExamples.arbitrarily_large_unseen_error','CalibrationExamples.perfect_partial_calibration_unbounded']
  sigs.write_text('import KomorebiBlock16\n'+'\n'.join('#check '+PREFIX+n for n in sig_names)+'\n')
  run('principal_signatures',base+['lake','env','lean','-j1','-DwarningAsError=true',str(sigs.relative_to(ROOT))])
  for n in order:run('kernel_'+n,base+['lake','env','leanchecker','--verbose',PREFIX+n])
  for name,body in [('false','theorem invalid : (0 : Nat) = 1 := by rfl\n'),('placeholder','theorem invalid : False := by sorry\n')]:
   p=out/(name+'.lean');p.write_text(body);run('negative_'+name,base+['lean','-DwarningAsError=true',str(p)],True)
  p=out/'CustomAxiom.lean';p.write_text('axiom forbidden : False\ntheorem invalid : False := forbidden\n#print axioms invalid\n')
  text=run('custom_axiom_compiles',base+['lean',str(p)])
  if not (set(verify.parse_axioms(text).get('invalid',[]))-verify.ALLOWED):raise RuntimeError('Custom-axiom screen failed')
  events.append({'name':'custom_axiom_rejected_by_allowlist','passed':True})
  run('exact_rational_calibration',[sys.executable,str(ROOT/'scripts/check_calibration.py')])
  run('inherited_operator_uncertainty',[sys.executable,str(ROOT/'scripts/check_operator_uncertainty.py')])
  run('inherited_inexact_controls',[sys.executable,str(ROOT/'scripts/check_inexact_discrepancy.py')])
  run('inherited_discrepancy_controls',[sys.executable,str(ROOT/'scripts/check_discrepancy.py')])
  run('inherited_limit_controls',[sys.executable,str(ROOT/'scripts/check_regularization_limits.py')])
  after={str(p.relative_to(ROOT)):verify.sha(p) for p in source_paths}
  if before!=after:raise RuntimeError('Executed inputs changed')
  passed=True
 except Exception as exc:error=str(exc);print('FAILED '+error,flush=True)
 after={str(p.relative_to(ROOT)):verify.sha(p) for p in source_paths}
 report={'passed':passed,'exit_status':0 if passed else 1,'error':error,'started_at':started,'runtime_seconds':time.monotonic()-clock,
 'verification_scope':('Six new block-16 modules freshly compiled; dependency objects reused with hashes; entire dependency closure replayed in the same kernel' if args.reuse_project_dependencies else 'Six new block-16 modules plus fresh compilation and same-kernel replay of their entire project dependency closure')+'; not a fresh full-corpus replay',
 'new_modules':NEW,'dependency_closure':order,'new_theorems':sum(r['kind'] in ('lemma','theorem') for r in rows),
 'new_named_declarations':len(rows),'axiom_audit_count':len(audited),'allowed_axioms':sorted(verify.ALLOWED),
 'reused_project_dependencies':dep_objects,'events':events,'platform':platform.platform(),
 'input_artifacts':[{'path':p,'sha256':h,'sha256_after':after[p]} for p,h in before.items()],
 'resource_limits':{'wall_seconds_per_command':args.timeout,'lean_threads':1,'serial':True},
 'trust_boundary':'Same Lean kernel for leanchecker; pinned Mathlib and listed project objects reused, not an independent kernel.',
 'non_claims':['Finite exact tests do not prove infinite limits.','No complete fresh inherited-corpus replay in this run.','The calibration truth-error allowance remains an external premise. No guarantee is inferred from nonspanning calibration. No nonlinear/constrained/arithmetic theorem or formally verified Python parser is claimed.']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'declarations.json').write_text(json.dumps(rows,indent=2)+'\n')

 manifest={'schema_version':1,'claim_id':'KSR-BLOCK16-CALIBRATION-CERTIFICATION',
  'repository':{'commit':None,'dirty':True,'note':'Input hashes preserved in report.json.'},
  'command':[sys.executable,'scripts/verify_block16.py','--runtime',str(kit),'--out',args.out]+(['--reuse-project-dependencies'] if args.reuse_project_dependencies else []),
  'environment':{'software':['Lean 4.34.0-rc2','Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
  'mathematics':{'assertion_tested':'The six block-16 source modules compile, all enumerated new declarations have only allowed transitive axioms, and the new modules and their project dependency closure replay in the same kernel.',
   'coefficient_domain':'Normed split calibration frames for operator certification, integrated with complete real Hilbert-space recovery; exact rational finite controls.',
   'conventions':'A split calibration synthesis U with bounded reconstruction R generates a whole-operator allowance from measured calibration truth error and model calibration fit. Redundant split frames are allowed. Approximate reconstruction with defect rho<1 incurs factor 1/(1-rho). Proper-subspace calibration admits arbitrarily large unseen operator error. Generated allowances feed the existing generalized discrepancy consistency theorem.',
   'inputs':list(before),'bounds':{'production_new_modules':len(NEW),'new_theorems':report['new_theorems'],'finite_control_dimensions':'72 exact-rational frame/model systems plus malformed and proper-subspace controls'},
   'non_claims':report['non_claims']},
  'randomness':{'used':True,'generator':'Python random.Random, finite controls only','seed':20260914},
  'run':{'started_at':started,'runtime_seconds':report['runtime_seconds'],'exit_status':0 if passed else 1},
  'outputs':[{'path':str((out/'report.json').relative_to(ROOT)),'sha256':verify.sha(out/'report.json')}],
  'checks':[e['name'] for e in events if e.get('passed')],
  'result':'PASS' if passed else 'FAIL: '+str(error),
  'residual_risks':['The same Lean kernel is used, not an independent implementation.','Listed project objects and pinned Mathlib cache may be reused.','No full fresh inherited-corpus replay.','Version-1 manifest with supplementary before/after input hashes.']}
 (out/'computation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

 print(json.dumps({'passed':passed,'new_theorems':report['new_theorems'],'audited':len(audited)}),flush=True)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
