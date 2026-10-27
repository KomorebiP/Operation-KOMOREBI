#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def load(rel): return json.loads((ROOT/rel).read_text())
def main():
 build=load('results/BUILD_VERIFICATION_BLOCK11.json'); finite=load('results/prime_envelope_audit.json')
 rels=[
  'lean/KomorebiPadic/RepresentativeBudgetPrimeEnvelope.lean','lean/KomorebiPadic.lean',
  'verification/verify_prime_envelope.py','verification/audit_source_block11.py',
  'verification/generate_axiom_audit_block11.py','verification/parse_axiom_audit_block11.py',
  'verification/verify_negative_controls_block11.py','verification/generate_prime_envelope_vectors.py',
  'results/BUILD_VERIFICATION_BLOCK11.json','results/static_source_audit_block11.json',
  'results/axiom_audit_block11.json','results/kernel_controls_block11.json',
  'results/lean_prime_envelope_vectors.json','results/prime_envelope_audit.json',
  'predecessor/BLOCK10_THEOREM_HEADERS.json','predecessor/PREDECESSOR_COMPLETE_VERIFICATION.json',
  'predecessor/PREDECESSOR_BLOCK10_VERIFICATION.json','logs/block11_clean_build.log',
  'logs/axiom_audit_block11.log','COMPUTATION_CONTRACT.md','PROOF_BOUNDARY.md','CONTINUE_HERE.md'
 ]
 manifest={
  'schema':'komorebi-padic-block11-computation-manifest-v1',
  'block':'Komorebi_Padic_Prime_Sensitive_Envelope_Block11',
  'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
  'claim_contract':{
   'arithmetic_domain':'Lean natural numbers and Python arbitrary-precision integers',
   'hypotheses':['0 < p for the representative slack identity and triangular inequality.','p.Prime and 0 < r for the end-to-end compiler total bound and certificate.'],
   'universal_claims':['The exact representative budget plus d*(p-(s+1)) equals B+p*d*(d+1)/2.','The triangular envelope is exact iff d=0 or s+1=p.','The triangular envelope is at most B^2.','The exact compiler total is bounded by the integrated prime-sensitive envelope.','The prime-sensitive envelope is at most the earlier quadratic envelope.'],
   'timeout_policy':'Timeout is inconclusive.',
   'nonclaims':build['proof_boundary']['nonclaims'],
  },
  'lean':build['lean'],
  'computation':{
   'block11_prime_envelope':{'status':finite['status'],'failure_count':finite['failure_count'],'recorded_checks_and_cases':finite['total_recorded_checks_and_cases'],'parameters':finite['parameters'],'stress_records':finite['compiler_stress_records']},
   'retained_predecessor_recorded_checks_and_cases':build['computation']['retained_predecessor_exact_checks_and_cases'],
   'cumulative_recorded_checks_and_cases':build['computation']['cumulative_recorded_exact_checks_and_cases'],
  },
  'runtime_archive':build['runtime_archive'],
  'sha256':{rel:sha256(ROOT/rel) for rel in rels},
 }
 out=ROOT/'COMPUTATION_MANIFEST.json'; out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 detached=ROOT/'COMPUTATION_MANIFEST.sha256'; detached.write_text(f"{sha256(out)}  {out.name}\n")
 print(json.dumps({'status':'PASS','paths':len(rels),'manifest':str(out),'sha256':sha256(out)},indent=2))
if __name__=='__main__': main()
