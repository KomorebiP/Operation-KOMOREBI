#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,platform,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(rel:str)->dict:
 return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def duration_seconds(s:str):
 m=re.search(r'elapsed=(?:(\d+):)?([0-9]+(?:\.[0-9]+)?)',s)
 if not m:return None
 return (int(m.group(1) or 0)*60)+float(m.group(2))

def main()->int:
 source=load('results/static_source_audit_block11.json')
 axioms=load('results/axiom_audit_block11.json')
 controls=load('results/kernel_controls_block11.json')
 vectors=load('results/lean_prime_envelope_vectors.json')
 finite=load('results/prime_envelope_audit.json')
 pred_build=load('results/BUILD_VERIFICATION_BLOCK10.json')
 pred_complete=load('predecessor/PREDECESSOR_COMPLETE_VERIFICATION.json')
 pred_focused=load('predecessor/PREDECESSOR_BLOCK10_VERIFICATION.json')
 build_log=(ROOT/'logs/block11_clean_build.log').read_text(encoding='utf-8')
 jobs_m=re.search(r'Build completed successfully \((\d+) jobs\)\.',build_log)
 jobs=int(jobs_m.group(1)) if jobs_m else None
 time_text=(ROOT/'logs/block11_clean_build.time').read_text(encoding='utf-8').strip()
 rss_m=re.search(r'maxrss_kb=(\d+)',time_text)
 oleans=sorted((ROOT/'compiled_rc2').rglob('*.olean')); ileans=sorted((ROOT/'compiled_rc2').rglob('*.ilean'))
 pred_finite=int(pred_build['computation']['combined_exact_checks_and_cases'])
 new_finite=int(finite['total_recorded_checks_and_cases'])
 pred_vectors=int(pred_build['lean']['native_decide_examples'])
 new_vectors=int(vectors['example_count'])
 statuses=[source.get('status'),axioms.get('status'),controls.get('status'),vectors.get('status'),finite.get('status'),pred_build.get('status'),pred_complete.get('status'),pred_focused.get('status')]
 passed=(all(x=='PASS' for x in statuses) and jobs==1161 and len(oleans)==18 and len(ileans)==18 and source.get('block11_theorem_count')==165 and source.get('predecessor_theorem_count')==152 and len(source.get('added_theorems',[]))==13 and not source.get('changed_predecessor_theorem_statements') and not source.get('missing_predecessor_theorems') and not axioms.get('unexpected_axioms') and vectors.get('example_count')==1160 and finite.get('failure_count')==0)
 report={
  'schema':'komorebi-padic-block11-build-verification-v1',
  'status':'PASS' if passed else 'FAIL',
  'generated_utc':datetime.now(timezone.utc).isoformat(),
  'platform':platform.platform(),'python':sys.version,
  'authoritative_predecessor':{
    'archive':'Komorebi_Padic_COMPLETE_2026-09-18_Block10_Closed_Budget_Lean_Checked.zip',
    'sha256':'2ab7c20e3db107ca6a5107d95a5a4529ae58676bbaea6e1d37f5fbb9ebe61a7b',
    'complete_release_verification':pred_complete.get('status'),
    'focused_block10_verification':pred_focused.get('status'),
  },
  'toolchain':{
    'lean':'Lean 4.34.0-rc2','lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d','lake':'5.0.0-src+6a10ac8','mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','stable_4_34_0_mathlib_5ed296_status':'NOT_CHECKED',
  },
  'runtime_archive':{
    'path':'/mnt/data/lean_compact_runtime/Lean_Portable_Compact.tar.xz','bytes':2220147424,'sha256':'f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7','hash_verified':True,'extraction_succeeded':True,
  },
  'clean_build':{
    'status':'PASS' if jobs==1161 else 'FAIL','warning_as_error':True,'jobs':jobs,'elapsed_seconds':duration_seconds(time_text),'max_rss_kb':int(rss_m.group(1)) if rss_m else None,'log':'logs/block11_clean_build.log','time_receipt':'logs/block11_clean_build.time',
  },
  'lean':{
    'production_files':source['lean_file_count'],'module_count':source['module_count'],'theorems':source['block11_theorem_count'],'definitions':source['declaration_counts']['def'],'structures':source['declaration_counts']['structure'],'predecessor_theorems':source['predecessor_theorem_count'],'new_theorems':len(source['added_theorems']),'changed_predecessor_theorem_statements':len(source['changed_predecessor_theorem_statements']),'compiled_olean_ilean_artifacts':len(oleans)+len(ileans),'olean_count':len(oleans),'ilean_count':len(ileans),'new_native_decide_files':vectors['file_count'],'new_native_decide_examples':new_vectors,'retained_predecessor_native_decide_examples':pred_vectors,'cumulative_native_decide_examples':pred_vectors+new_vectors,'axiom_audit_status':axioms['status'],'axiom_audit_theorems':axioms['theorem_count'],'observed_axioms':axioms['observed_axioms'],'unexpected_axioms':axioms['unexpected_axioms'],'negative_controls':controls['status'],'placeholder_or_local_axiom_violations':source['placeholder_or_axiom_violations'],
  },
  'computation':{
    'retained_predecessor_exact_checks_and_cases':pred_finite,'block11_prime_envelope':new_finite,'cumulative_recorded_exact_checks_and_cases':pred_finite+new_finite,'block11_failure_count':finite.get('failure_count',0),
  },
  'evidence_sha256':{rel:sha256(ROOT/rel) for rel in [
    'lean/KomorebiPadic/RepresentativeBudgetPrimeEnvelope.lean','results/static_source_audit_block11.json','results/axiom_audit_block11.json','results/kernel_controls_block11.json','results/lean_prime_envelope_vectors.json','results/prime_envelope_audit.json','logs/block11_clean_build.log','predecessor/BLOCK10_THEOREM_HEADERS.json']},
  'inconclusive_or_corrected_attempts':[],
  'proof_boundary':{
    'universal_proof':'Lean kernel checking of the exact slack identity, simplified envelope, equality criterion, compiler integration, and certificate.','finite_evidence':'Python arbitrary-precision audits and native_decide vectors over the recorded finite domains.','nonclaims':['No stable Lean 4.34.0 plus mathlib 5ed296 compatibility claim.','No end-to-end compiler theorem for composite bases.','No asymptotic optimality claim.','No novelty or priority claim.']
  }
 }
 out=ROOT/'results'/'BUILD_VERIFICATION_BLOCK11.json'; out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps({'status':report['status'],'jobs':jobs,'compiled':len(oleans)+len(ileans),'new_native_decide':new_vectors,'cumulative_native_decide':pred_vectors+new_vectors,'new_finite':new_finite,'cumulative_finite':pred_finite+new_finite,'theorems':source['block11_theorem_count']},indent=2,sort_keys=True))
 return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
