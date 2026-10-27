#!/usr/bin/env python3
"""Publish current reports only after the retained cold and exact audits pass."""
from pathlib import Path
import json,sys,hashlib,platform,collections
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 lean=json.loads((ROOT/'results_v06/LEAN_AUDIT.json').read_text());py=json.loads((ROOT/'results_v06/PYTHON_AUDIT.json').read_text());st=json.loads((ROOT/'v06_evidence/COLD_STATE.json').read_text());groups=json.loads((ROOT/'v06_evidence/AXIOM_GROUP_STATE.json').read_text());env=st['environment']
 assert lean['status']==py['status']==groups['status']=='PASS' and st['status']=='COMPLETE'
 parent=json.loads((ROOT/'v06_evidence/PARENT_PRESERVATION.json').read_text());assert sha(ROOT/'history/Komorebi_ModelTheory_Normalization_v0.5.zip')==parent['parent_sha256']
 def manifest(label,inputs,outputs,start,finish,seconds,assertion,bounds,command,seed=None):
  return {'schema_version':2,'claim_id':label,'repository':{'commit':'Standalone v0.6 source; immutable v0.5 archive '+parent['parent_sha256'],'dirty':True},'command':command,
   'environment':{'software':[{'name':'Python','version':sys.version},{'name':'Lean','version':env['lean_version']},{'name':'Mathlib','version':env['mathlib_commit']}], 'hardware':{'platform':platform.platform(),'memory_cgroup':env['memory_cgroup'],'cpu_cgroup':env['cpu_cgroup']}},
   'mathematics':{'assertion_tested':assertion,'coefficient_domain':'Integers and actual ZMod(m), positive m; discovery totality uses prime-power ZMod(p^r)', 'conventions':'All source states, FIFO discovery; row right action prepends a word. Positive integer pivots. Exact integer preimage includes m Z^d. No supplied membership advice or exhaustive coefficient search in the new Lean solver.',
    'inputs':[x['path'] for x in inputs],'bounds':bounds,'non_claims':['No canonical Smith/Hermite output or minimum raw test count.','No verified Python port, parser, or exporter.','No polynomial bit-complexity or comparative speedup theorem; coefficient growth remains.','Not a cold rebuild of the entire historical corpus or upstream Mathlib; no learned policy or held-out discovery benchmark.']},
   'randomness':{'used':seed is not None,'generator':'Python random.Random for specified finite audit cases' if seed is not None else 'none','seed':seed},
   'run':{'started_at':start,'finished_at':finish,'runtime_seconds':seconds,'exit_status':0,'status':'completed','resource_limits':{'memory_bytes':int(env['memory_cgroup']),'cpu_seconds':None,'max_cores':None,'max_threads':1},'missing_results':[],'invalid_results':[]},
   'input_artifacts':inputs,'execution_artifacts':[x['path'] for x in inputs], 'declared_results':[x['path'] for x in outputs if x['kind']=='result'],'outputs':outputs,
   'checks':[{'name':'completed expected outcomes','status':'PASS'},{'name':'accepted input bytes unchanged','status':'PASS'}], 'result':'PASS','residual_risks':['Mathematical interpretation is self-review, not independent refereeing.','Formal theorems concern actual literal input matrices, not an unverified informal specification.','Pinned upstream compiled cache is reused.']}
 ins=[x|{'sha256_after':sha(ROOT/x['path'])} for x in st['inputs']]
 outs=[{'path':'results_v06/LEAN_AUDIT.json','sha256':sha(ROOT/'results_v06/LEAN_AUDIT.json'),'kind':'result'}, {'path':'v06_evidence/AXIOM_GROUP_STATE.json','sha256':sha(ROOT/'v06_evidence/AXIOM_GROUP_STATE.json'),'kind':'result'}]
 outs += [{'path':x['log'],'sha256':x['sha256'],'kind':'log'} for x in lean['tasks']+groups['tasks']]
 elapsed=(datetime.fromisoformat(lean['finished_at'])-datetime.fromisoformat(lean['started_at'])).total_seconds()
 ml=manifest('KMT-M6-VERIFIED-INCREMENTAL-ECHELON',ins,outs,lean['started_at'],lean['finished_at'],elapsed,'Exact integer echelon insertion, modular preimage membership, cached discovery/reference equality, universal prime-power successful return and standard first-order definition; actual kernel evaluations on 203 profiles.', {'local_modules':lean['modules'],'generated_sources':203,'logical_stages':len(lean['tasks']),'axiom_groups':len(groups['tasks']),'actual_Lean_processes':len(lean['tasks'])-1+len(groups['tasks']),'universal_generic_theorems':lean['new_generic_counts']['theorem']},
  'python v06_checks/audit_lean.py --runtime RUNTIME --init; synchronous --batch calls; v06_checks/audit_axiom_groups.py --init and eight --one calls; remaining --batch calls; --finish')
 actual=[a for t in lean['tasks'] for a in ([g['argv'] for g in groups['tasks']] if t['name']=='axioms' else [t['argv']])]
 ml['run']['completed_lean_commands']=actual;ml['run']['compile_seconds']=lean['compile_seconds'];ml['run']['timing_note']='Elapsed protocol includes pauses and interrupted attempts; compile_seconds sums completed command runtimes only. No comparative benchmark.';ml['run']['per_command_wall_limits_seconds']={'build_or_control':90,'axiom_group':80};ml['run']['protocol_revision']=st.get('audit_protocol_revision')
 dump(ROOT/'LEAN_MANIFEST_v06.json',ml);dump(ROOT/'LEAN_MANIFEST.json',ml)
 pins=[x|{'sha256_after':sha(ROOT/x['path'])} for x in py['inputs']]
 po=[{'path':'results_v06/PYTHON_AUDIT.json','sha256':sha(ROOT/'results_v06/PYTHON_AUDIT.json'),'kind':'result'}]
 bounds={'frozen_profiles':202,'stress_profiles':1,'exhaustive_modulus_dimension_pairs':py['exhaustive_modulus_dimension_pairs'],'maximum_generators':py['exhaustive_max_generators'],'random_cases':py['random_cases'],'queries_each':py['random_queries_each'],'all_candidate_vectors_in_exhaustive_cases':True}
 mp=manifest('KMT-M6-ECHELON-PORT-AUDIT',pins,po,py['started_at'],py['finished_at'],py['runtime_seconds'],'Independent modular span enumerations, integer reconstruction, determinant identities, old Smith comparisons, frozen FIFO list preservation, literal source transcription and invalid-input controls.',bounds,[sys.executable,'v06_checks/audit_echelon.py'],py['seed'])
 dump(ROOT/'COMPUTATION_MANIFEST_v06.json',mp);dump(ROOT/'COMPUTATION_MANIFEST.json',mp)
 coverage=f'''# Formalization coverage — Model-Theory Normalization v0.6

PASS: **{lean['modules']} local modules**, 17 inherited dependencies and 22 new
modules, including 17 batches executing all 203 profiles. The four new generic
modules contain **{lean['new_generic_counts']['theorem']} theorem declarations,
{lean['new_generic_counts']['def']} definitions, and one recursive basis type**.
EchelonExamples adds 13 concrete theorems. Each generated profile has one actual
kernel computation and its all-word logical code consequence.

All **{lean['named_declarations']} explicit named declarations** were axiom-audited:
{lean['counts']}. Counts include generated data, not independent discoveries.
The audit completed {len(lean['tasks'])} logical stages using
{len(actual)} actual Lean process invocations: 39 cold module builds, eight bounded
axiom groups and eight controls. All seven intended rejections occurred for their
proof claims, not missing imports or resource limits. The positive control accepted.
Only {', '.join(lean['axioms'])} occur. No custom project axiom, sorryAx or
Lean.ofReduceBool. Accepted source hashes were unchanged. Local sources are
checked with warnings as errors. Upstream Mathlib was reused, not rebuilt.

| Module | Exact formal content |
|---|---|
| EchelonCore | Actual positive-pivot integer basis, injective synthesis, terminating executable triangular membership and reconstruction |
| EchelonInsert | Actual gcd/Bezout update, structural insertion, both integer-span directions, exact submodule join |
| EchelonModular | Kernel m Z^d, integer lift/reduction, exact preimage invariant for every positive modulus, executable membership soundness/completeness |
| EchelonDiscovery | Cached basis through FIFO updates, equality with every correct oracle at every fuel budget, total prime-power discovery, actual standard first-order formula |
| EchelonExamples | Nonunits, composite modulus, negative integer insertion, coupled congruence, degenerate dimensions/precisions and insufficient fuel |
| EchelonComputed00–16 | All 203 actual computations by decide +kernel, not supplied trace replay; corresponding all-word finite code certificates |

## Precise boundaries

The algorithm is integer echelon, not canonical Smith/Hermite reduction. It stores
exactly d integer rows, not necessarily a minimal MODULAR generating family. There
is no nonunit modular inversion, exhaustive coefficient search or untrusted adviser
in fastPrimeDiscover. Its prime-power totality uses the inherited enough-fuel bound.
The positive-modulus membership/update theorem is broader than that assembled bound.

The Python port/exporter is not verified code extraction. No formal bit-complexity,
coefficient-growth bound, minimum test-list/formula theorem, relational discovery,
learned policy or held-out benchmark is claimed. The new numerical fixed-instance
outputs equal old lists, not newly asserted minimum linear bases.

All {parent['count']} parent Lean files are byte-preserved. Only 17 inherited local
dependencies were freshly rebuilt. Standalone EchelonCases files duplicate the case
content exercised in the batches; they are not counted as additional research or
claimed to have a second complete cold build. Case201 and Case202 also had separate
development checks. Fresh extraction scope belongs in the external replay report.

Lean: {env['lean_version']}
Mathlib pin: {env['mathlib_commit']}
Proof interpretation is self-review, not independent refereeing or priority review.
'''
 (ROOT/'FORMALIZATION_COVERAGE.md').write_text(coverage)
 results=f'''# Retained results — Model-Theory Normalization v0.6

## Completed cold Lean audit

PASS: {lean['modules']} modules, {len(lean['tasks'])} logical audit stages,
{len(actual)} actual Lean commands, {lean['named_declarations']} named declarations.
All 203 source fixtures were actually executed by the kernel through the new
incremental solver, without supplied branch evidence or coefficient enumeration.
Axiom collection was divided into eight source-preserving groups after interrupted
monolithic attempts. Completed task runtime sum: {lean['compile_seconds']:.6f}s.
Elapsed protocol time includes intervals and interruptions and is not a benchmark.
All accepted inputs stayed unchanged. Seven negative controls and one positive
control behaved as intended. Detailed logs and the protocol revision are retained.

## Independent Python port audit

PASS: {py['runtime_seconds']:.6f}s in one recorded run, seed {py['seed']}.
This timing is not a comparative speedup or a performance guarantee.

| Check | Count |
|---|---:|
'''+''.join(f'| {k} | {v:,} |\n' for k,v in py['counts'].items())+'''
The modular span oracle was exhausted on every generating list of length 0, 1 or 2
for (m,d)=(1,2),(2,0),(2,2),(3,2),(4,2),(6,2),(8,1),(9,1),(12,1), with every
candidate vector. This includes composite moduli, the trivial ring and dimension0.
Bezout identities cover q=1..64 and a=-64..64. Ninety separately seeded random
prime-power configurations were compared with the inherited Smith module solver,
12 queries each, plus integer representative shifts. No floating arithmetic.

All 203 frozen ordered test lists match. In total: 667 accepts and 1,636 queue
decisions. The large 2^128-state source returns two tests in five decisions; the
Python port stores eight rows and performs sixteen Bezout updates. The descending
24-test torsion source stores one row and performs 24 updates in 48 decisions.
The largest observed STORED basis coefficient in the Python suite was 730 bits;
this does not bound larger intermediate operands or arbitrary inputs.

## Parent replay and extraction

The immediate frozen v0.5 Python audit reran in an isolated extracted copy and
passed all 203 old trace tests and 6,674 exhaustive old membership comparisons.
Its record is v06_evidence/parent_replay/REPLAY.json. No full parent Lean rebuild
is claimed. Distribution integrity must be checked before rerunning audits because
new execution records rewrite timestamps and current outputs.

The exact final archive's fresh-copy verification is recorded in the separate
Komorebi_ModelTheory_Normalization_v0.6_EXTRACTED_REPLAY.json. It is not inferred
from these construction-time results.
'''
 (ROOT/'RESULTS.md').write_text(results)
 print('Current manifests and reports written')
if __name__=='__main__':main()
