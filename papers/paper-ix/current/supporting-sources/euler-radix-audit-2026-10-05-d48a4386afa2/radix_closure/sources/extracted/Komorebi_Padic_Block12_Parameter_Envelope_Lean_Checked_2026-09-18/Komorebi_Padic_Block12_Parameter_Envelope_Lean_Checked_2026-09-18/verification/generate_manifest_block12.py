#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 build=json.loads((ROOT/'results/BUILD_VERIFICATION_BLOCK12.json').read_text())
 finite=json.loads((ROOT/'results/parameter_envelope_audit.json').read_text())
 patterns=[
  'lean/**/*.lean','compiled_rc2/**/*.olean','compiled_rc2/**/*.ilean',
  'verification/AxiomAuditBlock12.lean','verification/LeanParameter*Vector_*.lean','verification/RejectFalse.lean','verification/RejectSorry.lean',
  'verification/audit_source_block12.py','verification/generate_axiom_audit_block12.py','verification/parse_axiom_audit_block12.py','verification/generate_parameter_envelope_vectors.py','verification/verify_parameter_envelope.py','verification/verify_negative_controls_block12.py','verification/generate_build_verification_block12.py','verification/generate_manifest_block12.py','verification/verify_release.py',
  'results/static_source_audit_block12.json','results/axiom_audit_block12.json','results/kernel_controls_block12.json','results/lean_parameter_envelope_vectors.json','results/parameter_envelope_audit.json','results/BUILD_VERIFICATION_BLOCK12.json','results/theorem_names_block12.txt','results/theorem_locations_block12.json','results/parameter_envelope_vector_generation.json',
  'logs/clean_build_block12.log','logs/clean_build_block12.time','logs/axiom_audit_block12.log','logs/axiom_audit_block12_clean.time','logs/parameter_envelope_audit.log','logs/parameter_envelope_audit.time','logs/reject_false_block12.log','logs/reject_sorry_block12.log','logs/LeanParameter*_clean.log','logs/LeanParameter*_clean.time',
  'predecessor/BLOCK11_THEOREM_HEADERS.json','predecessor/PREDECESSOR_COMPLETE_VERIFICATION.json','predecessor/PREDECESSOR_BLOCK11_VERIFICATION.json',
  'START_HERE.md','CONTINUE_HERE.md','PROOF_BOUNDARY.md','LEAN_STATUS.md','BLOCK12_THEOREM_INDEX.md','THEOREM_NOTE.md','COMPUTATION_CONTRACT.md','RUN_METADATA.json','PROGRESS.md','AUDIT.md','DEVELOPMENT_FAILURES.md','SELF_AUDIT.md','RELEASE_NOTES.md','FINAL_HANDOFF.md','REPRODUCE.md','TOOLCHAIN_PROVENANCE.md','lakefile.lean','lake-manifest.json','lean-toolchain','verify_all.sh','build_lean.sh','build_lean.ps1','baseline_build.log'
 ]
 paths=set()
 for pat in patterns:
  for p in ROOT.glob(pat):
   if p.is_file():paths.add(p)
 rels=sorted(str(p.relative_to(ROOT)) for p in paths)
 manifest={
  'schema':'komorebi-padic-block12-computation-manifest-v1','status':'PASS','generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
  'claim':{'universal':'Exact elimination of B and d, exact parameter-envelope rewrite, monotone transport to r-1, and compiler-total bounds.','finite_surrogate':'Totalized arithmetic grids, adjacent monotonicity, concrete compiler cases, native_decide vectors, and stress cases.','nonclaim':'Finite success is not the universal proof.'},
  'environment':build['environment'],'runtime_archive':build['runtime_archive'],'clean_build':build['clean_build'],'lean':build['lean'],
  'computation':{'block12':{'status':finite['status'],'recorded_checks_and_cases':finite['total_recorded_checks_and_cases'],'failure_count':finite['failure_count'],'parameters':finite['parameters'],'stress_parameter_records':finite['stress_parameter_records'],'compiler_stress_records':finite['compiler_stress_records']},'retained_predecessor_recorded_checks_and_cases':build['computation']['retained_predecessor_exact_checks_and_cases'],'cumulative_recorded_checks_and_cases':build['computation']['cumulative_recorded_exact_checks_and_cases']},
  'paths':rels,'sha256':{rel:sha(ROOT/rel) for rel in rels}
 }
 out=ROOT/'COMPUTATION_MANIFEST.json';out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 (ROOT/'COMPUTATION_MANIFEST.sha256').write_text(f'{sha(out)}  {out.name}\n')
 print(json.dumps({'status':'PASS','paths':len(rels),'manifest':str(out),'sha256':sha(out)},indent=2))
if __name__=='__main__':main()
