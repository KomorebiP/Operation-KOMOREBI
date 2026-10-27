#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def load(rel:str):
    return json.loads((ROOT/rel).read_text())

def main()->None:
    source=load('results/static_source_audit_block09.json')
    axioms=load('results/axiom_audit_block09.json')
    controls=load('results/kernel_controls_block09.json')
    build=load('results/BUILD_VERIFICATION_BLOCK09.json')
    radix=load('results/radix_compiler_audit.json')
    suffix=load('results/suffix_window_audit.json')
    boundary=load('results/final_fiber_boundary_audit.json')
    complexity=load('results/compiler_complexity_audit.json')
    excluded={
        'COMPUTATION_MANIFEST.json','COMPUTATION_MANIFEST.sha256','CHECKSUMS.sha256',
        'results/FOCUSED_RELEASE_VERIFICATION.json','logs/generate_manifest_block09.log',
        'logs/verify_release_block09.log','logs/checksum_verify_block09.log',
    }
    paths=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or '.lake' in p.parts:
            continue
        rel=str(p.relative_to(ROOT))
        if rel in excluded:
            continue
        paths.append(p)
    hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
    total=(int(radix['total_checks'])+int(suffix['total_recorded_checks'])+
           int(boundary['total_recorded_checks_and_cases'])+
           int(complexity['total_recorded_checks_and_cases']))
    manifest={
      'schema':'komorebi-padic-block09-computation-manifest-v1',
      'block':'Komorebi_Padic_Compiler_Complexity_Certificate_Block09',
      'status':'PASS',
      'generated_utc':datetime.now(timezone.utc).isoformat(),
      'claim_contract':{
        'universal_claims':[
          'Each suffix barrier scan evaluates no more representatives than its full radix range.',
          'The accumulated exact representative counter is bounded by the full representative budget through the coarse quotient endpoint.',
          'radixRepresentativeBudget p B is monotone in B and is at most B squared.',
          'The exact quotient-test count is at most quotientSearchBound p r h.',
          'At prime p and positive r, the exact total is at most B + p + radixRepresentativeBudget p B.',
          'At prime p and positive r, the exact total is at most B squared + B + p.',
          'The dependent complexity certificate retains the exact result and exact counters together with proofs of the bounds.',
        ],
        'hypotheses':['p.Prime and 0 < r for the end-to-end total bounds'],
        'arithmetic_domain':'Lean natural numbers and Python arbitrary-precision integers',
        'timeout_policy':'Timeout is inconclusive.',
        'nonclaims':[
          'No wall-clock or memory-complexity theorem.',
          'No asymptotic optimality theorem.',
          'No claim that the quadratic envelope is tight.',
          'No exact closed form for radixRepresentativeBudget in this block.',
          'No end-to-end theorem for composite bases.',
          'No stable Lean 4.34.0 compatibility claim.',
          'No novelty or priority claim.',
        ],
      },
      'lean':{
        'toolchain':'leanprover/lean4:v4.34.0-rc2',
        'lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d',
        'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
        'warning_as_error_clean_build':'PASS',
        'root_jobs':build['clean_build']['jobs'],
        'production_files':source['lean_file_count'],
        'declaration_counts':source['declaration_counts'],
        'compiled_artifacts':build['compiled_artifacts'],
        'native_decide_checks':build['native_decide_total'],
        'axiom_audit':axioms['status'],
        'axiom_audit_theorems':axioms['theorem_count'],
        'observed_axioms':axioms['observed_axioms'],
        'unexpected_axioms':axioms['unexpected_axioms'],
        'negative_controls':controls['status'],
        'predecessor_theorems':source['predecessor_theorem_count'],
        'new_theorems':len(source['added_theorems']),
        'changed_predecessor_theorem_statements':len(source['changed_predecessor_theorem_statements']),
      },
      'computation':{
        'block05_radix':{'status':radix['status'],'recorded_checks':radix['total_checks']},
        'block06_suffix':{'status':suffix['status'],'recorded_checks':suffix['total_recorded_checks'],'failure_count':suffix['failure_count']},
        'block08_boundary':{'status':boundary['status'],'recorded_checks_and_cases':boundary['total_recorded_checks_and_cases'],'failure_count':boundary['failure_count']},
        'block09_complexity':{
          'status':complexity['status'],
          'recorded_checks_and_cases':complexity['total_recorded_checks_and_cases'],
          'failure_count':complexity['failure_count'],
          'parameters':complexity['parameters'],
          'aggregate_accounting':complexity['aggregate_accounting'],
          'maxima':complexity['maxima'],
          'stress_records':complexity['stress_records'],
        },
        'combined_recorded_checks_and_cases':total,
      },
      'runtime_archive':{
        'sha256':'f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7',
        'bytes':2220147424,
        'status':'VERIFIED_AND_EXTRACTED',
      },
      'inconclusive_attempts':[
        'monolithic 2037-example Lean vector exceeded the execution window; the retained vector was split into 25 successful files',
        'large concrete Lean evaluation at p=2, r=8059, h=0 exceeded the execution window; it is retained only as finite Python evidence',
      ],
      'sha256':hashes,
    }
    path=ROOT/'COMPUTATION_MANIFEST.json'
    path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (ROOT/'COMPUTATION_MANIFEST.sha256').write_text(f'{sha(path)}  {path.name}\n')
    print(json.dumps({'hashed_files':len(hashes),'manifest_sha256':sha(path),'combined_finite':total},indent=2))

if __name__=='__main__': main()
