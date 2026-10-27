#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess,hashlib,platform,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel): return json.loads((ROOT/rel).read_text())
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def parse_time(path):
 text=path.read_text(); out={}
 for k,v in re.findall(r'(elapsed|maxrss|exit)=([0-9.]+)',text): out[k]=float(v) if k=='elapsed' else int(float(v))
 return out

def main():
 source=load('results/static_source_audit_block12.json'); axioms=load('results/axiom_audit_block12.json'); controls=load('results/kernel_controls_block12.json'); vectors=load('results/lean_parameter_envelope_vectors.json'); finite=load('results/parameter_envelope_audit.json'); pred=load('results/BUILD_VERIFICATION_BLOCK11.json')
 t=parse_time(ROOT/'logs/clean_build_block12.time')
 log=(ROOT/'logs/clean_build_block12.log').read_text(); m=re.search(r'Build completed successfully \((\d+) jobs\)',log); jobs=int(m.group(1)) if m else None
 olean=len(list((ROOT/'compiled_rc2').rglob('*.olean'))); ilean=len(list((ROOT/'compiled_rc2').rglob('*.ilean')))
 lean=subprocess.check_output(['lean','--version'],text=True).strip(); lake=subprocess.check_output(['lake','--version'],text=True).strip()
 manifest=json.loads((ROOT/'lake-manifest.json').read_text()); rev={p['name']:p.get('rev') for p in manifest['packages']}
 cumulative_native=pred['lean']['cumulative_native_decide_examples']+vectors['example_count']
 cumulative_finite=pred['computation']['cumulative_recorded_exact_checks_and_cases']+finite['total_recorded_checks_and_cases']
 passed=all([source['status']=='PASS',axioms['status']=='PASS',controls['status']=='PASS',vectors['status']=='PASS',finite['status']=='PASS',jobs==1162,t.get('exit')==0,olean==19,ilean==19,source['block12_theorem_count']==179,not source['changed_predecessor_theorem_statements']])
 report={
  'schema':'komorebi-padic-block12-build-verification-v1','status':'PASS' if passed else 'FAIL','generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
  'environment':{'platform':platform.platform(),'lean':lean,'lake':lake,'mathlib_revision':rev.get('mathlib'),'dependency_revisions':rev},
  'runtime_archive':{'name':'Lean_Portable_Compact.tar.xz','bytes':2220147424,'sha256':'f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7','parts':5},
  'clean_build':{'status':'PASS' if jobs==1162 and t.get('exit')==0 else 'FAIL','jobs':jobs,'warning_as_error':True,'elapsed_seconds':t.get('elapsed'),'max_rss_kb':t.get('maxrss'),'log':'logs/clean_build_block12.log','time_receipt':'logs/clean_build_block12.time'},
  'lean':{'production_files':source['lean_file_count'],'module_count':source['module_count'],'theorems':source['block12_theorem_count'],'predecessor_theorems':source['predecessor_theorem_count'],'new_theorems':len(source['added_theorems']),'definitions':source['declaration_counts'].get('def',0),'structures':source['declaration_counts'].get('structure',0),'changed_predecessor_theorem_statements':len(source['changed_predecessor_theorem_statements']),'placeholder_or_local_axiom_violations':source['placeholder_or_axiom_violations'],'axiom_audit_status':axioms['status'],'axiom_audit_theorems':axioms['theorem_count'],'observed_axioms':axioms['observed_axioms'],'unexpected_axioms':axioms['unexpected_axioms'],'negative_controls':controls['status'],'olean_count':olean,'ilean_count':ilean,'compiled_olean_ilean_artifacts':olean+ilean,'retained_predecessor_native_decide_examples':pred['lean']['cumulative_native_decide_examples'],'new_native_decide_examples':vectors['example_count'],'new_native_decide_files':vectors['file_count'],'cumulative_native_decide_examples':cumulative_native},
  'computation':{'retained_predecessor_exact_checks_and_cases':pred['computation']['cumulative_recorded_exact_checks_and_cases'],'block12_parameter_envelope':finite['total_recorded_checks_and_cases'],'block12_failure_count':finite['failure_count'],'cumulative_recorded_exact_checks_and_cases':cumulative_finite},
  'proof_boundary':{'universal_lean':['The final-block quotient at the search bound equals coarseK/(p*(p-1)) for all natural bases.','The Block 11 envelope is exactly the direct (p,r,h) parameter envelope.','The parameter envelope is monotone in coarseK.','coarseK(r,h) is at most r-1.','The exact compiler total is bounded by both the parameter envelope and the h-free raw-precision envelope for prime p and positive r.'],'finite_only':['Dense totalized arithmetic grids, monotonicity lanes, concrete compiler cases, and large arbitrary-precision stress cases.'],'nonclaims':['The envelopes are not asserted to be exact operation counts.','No asymptotic optimality or external novelty claim is made.','The stable Lean 4.34.0 / mathlib 5ed296 lane was not executed.']},
  'receipts':{'source_audit':'results/static_source_audit_block12.json','axiom_audit':'results/axiom_audit_block12.json','negative_controls':'results/kernel_controls_block12.json','native_vectors':'results/lean_parameter_envelope_vectors.json','finite_audit':'results/parameter_envelope_audit.json','predecessor_complete':'predecessor/PREDECESSOR_COMPLETE_VERIFICATION.json','predecessor_focused':'predecessor/PREDECESSOR_BLOCK11_VERIFICATION.json'},
 }
 out=ROOT/'results'/'BUILD_VERIFICATION_BLOCK12.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':report['status'],'jobs':jobs,'theorems':report['lean']['theorems'],'compiled':olean+ilean,'native_decide':cumulative_native,'finite':cumulative_finite,'output':str(out)},indent=2))
 raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
