#!/usr/bin/env python3
"""Classifier regression from actual superseded mixed control diagnostics.
No Lean process is launched. Captured receipts retain their original meaning.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lsm_verify',root/'scripts/verify.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
originals={
 'PositiveLiftMustBeStrict':'d096fdd836e2acc18fe573faccf3ec545c532b5926df6fbdc1e707edd9394953',
 'InconsistentDataAlwaysFits':'7ddf242b2b48e90c1a003f01694532ea8523f239013206bf6dba4546094761bd',
 'ImpossibleConditionalPrior':'d8d4be82e136194518b4e7ab087562f54fee8ec414f0155babe4fab15f41a0b9'}
for name,h in originals.items():
 p=root/'history/control_repairs'/(name+'.before.stdout.txt');assert sha(p)==h,name
 rec={'returncode':1,'timed_out':False,'stdout':p.read_text(),'stderr':''}
 assessment=mod.classify_negative_control(rec);assert not assessment['valid_rejection'],(name,assessment)
 rows.append({'name':name+' original mixed diagnostic is rejected','passed':True,'stdout_sha256':h})
 p=root/'history/control_repairs'/(name+'.fresh_clean_receipt.json');rec=json.loads(p.read_text())
 assessment=mod.classify_negative_control(rec);assert assessment['valid_rejection'],(name,assessment)
 rows.append({'name':name+' repaired clean diagnostic is accepted','passed':True,'receipt_sha256':sha(p)})
base={'returncode':1,'timed_out':False,'stdout':'file.lean:1:1: error: unsolved goals\n⊢ False\n','stderr':''}
assert mod.classify_negative_control(base)['valid_rejection'];rows.append({'name':'single mathematical failure accepted','passed':True})
for name,changes in [
 ('success is not rejection',{'returncode':0}),('abnormal exit is not rejection',{'returncode':2}),
 ('signal is not rejection',{'returncode':-9}),('timeout flag is not rejection',{'timed_out':True}),
 ('unproved true helper plus false goal is not clean',{'stdout':base['stdout']+'file.lean:2:1: error: unsolved goals\n⊢ 0 < (1 : ℝ)\n'}),
 ('missing diagnostics are not rejection',{'stdout':''})]:
 rec={**base,**changes};assert not mod.classify_negative_control(rec)['valid_rejection'],name
 rows.append({'name':name,'passed':True})
for message in ['failed to synthesize instance','error(lean.synthInstanceFailed): failure',
 'did not consume the patterns','unexpected token','expected token','invalid field','unknown module',
 'unknown identifier','unknown constant','does not exist','failed to open file',
 'maximum recursion depth','maximum number of heartbeats','deterministic execution timeout',
 'TIMED OUT','timeout limit exceeded','out of memory','PANIC','stack overflow']:
 rec={**base,'stdout':base['stdout']+'\n'+message}
 assert not mod.classify_negative_control(rec)['valid_rejection'],message
 rows.append({'name':'infrastructure failure rejected: '+message,'passed':True})
# Genuine rfl counterexamples need not print a final literal False goal.
rec={**base,'stdout':'file.lean:1:1: error: Tactic `rfl` failed: the left-hand side\n  0\nis not definitionally equal to the right-hand side\n  1\n'}
assert mod.classify_negative_control(rec)['valid_rejection'];rows.append({'name':'single intended equality rejection accepted','passed':True})
live=root/'verification/fresh_controls/report.json';checked=0
if live.is_file():
 for rec in json.loads(live.read_text()).get('results',[]):
  if rec.get('valid_rejection') is True:
   assessment=mod.classify_negative_control(rec)
   assert assessment['valid_rejection'],(rec['control'],assessment)
   checked+=1
report={'kind':'negative-control diagnostic classifier regression','passed':True,'case_count':len(rows),'cases':rows,
 'current_recorded_clean_rejections_checked':checked,'verifier_sha256':sha(root/'scripts/verify.py'),
 'scope':'Classifier behavior only; no new Lean executions and no cumulative execution acceptance inferred.'}
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(rows)} negative-control classifier cases and {checked} actual current clean receipts.')
