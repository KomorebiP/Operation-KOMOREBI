#!/usr/bin/env python3
"""Pin the independent review evidence without a manifest self-cycle."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'checks/claim91_audit'
MATHLIB=Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages/mathlib')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def entry(p,**meta):
    p=Path(p);full=p if p.is_absolute() else ROOT/p
    return {'path':str(p),'sha256':sha(full),**meta}
graph=json.loads((AUDIT/'DependencyGraph.json').read_text());new=graph['new_modules']
closure=sorted(set(graph['internal_edges'])-set(new))
frozen=json.loads((AUDIT/'FrozenBlock24Verification.json').read_text())
frozen_sources={m['module']:m['source_sha256'] for m in frozen['modules']}
for n in closure:assert sha(ROOT/'lean/PaperX'/f'{n}.lean')==frozen_sources[n]
for n in new:
    result=json.loads((AUDIT/f'{n}.json').read_text())
    assert result['exit_code']==0
    assert sha(ROOT/result['source'])==result['source_sha256']
assert json.loads((AUDIT/'AxiomSummary.json').read_text())['audited_count']==60
assert json.loads((AUDIT/'EdgeApplications.json').read_text())['exit_code']==0
reviewed=['GeneralCharacters','SimpleModuleSeparation','ProfiniteSeparation','DenseTraceSeparation','TraceRecovery','FiniteSeparation','CommonSpine','ConditionalArithmeticSpine','CompletionExamples','QuadraticCharacters','QuadraticAlgebra']
for n in reviewed:assert sha(ROOT/'lean/PaperX'/f'{n}.lean')==frozen_sources[n]
external=[]
for rel,h in re.findall(r'\| `(Mathlib/[^`]+)` \| `([a-f0-9]{64})`', (AUDIT/'MathlibSourceReview.md').read_text()):
    assert sha(MATHLIB/rel)==h
    external.append(entry(MATHLIB/rel,role='primary',review_mode='independent_exact_source',revision=frozen['mathlib_revision']))
for rel in ['Mathlib/RepresentationTheory/Character.lean','Mathlib/RepresentationTheory/Irreducible.lean','Mathlib/RingTheory/SimpleModule/Basic.lean']:
    external.append(entry(MATHLIB/rel,role='primary',review_mode='independent_exact_source',revision=frozen['mathlib_revision']))
evidence=[entry('references/PRSC_X_v0.24.0_Checked_Proof_Bundle.zip',role='frozen_predecessor_archive')]
for p in sorted(AUDIT.iterdir()):
    if p.is_file():evidence.append(entry(p.relative_to(ROOT),role='independent_review_evidence'))
evidence.append(entry('CLAIM91_PROOF_AUDIT.md',role='independent_audit_report'))
manifest={
  'schema':'claim91-independent-proof-audit-sources-v1',
  'audit_kind':'independent_exact_source_with_isolated_compilation',
  'primary_verdict':'incomplete, with the smallest missing implication',
  'full_source_claim':'Claim 9.1 remains partial: general cofinite arithmetic Frobenius coverage is missing.',
  'frozen_predecessor_archive':entry('references/PRSC_X_v0.24.0_Checked_Proof_Bundle.zip'),
  'source_statement':entry('source/Projector_Resolved_Seed_Calculus_X_Block24_Amended.tex',role='authoritative_raw_statement',locators=['Section 8 lines 760-806','Claim 9.1 theorem/proof lines 1053-1083']),
  'new_production_sources':[entry(f'lean/PaperX/{n}.lean',role='primary',review_mode='independent_exact_source') for n in new],
  'internal_dependency_source_closure':[entry(f'lean/PaperX/{n}.lean',role='internal_dependency',review_mode='frozen_source_closure_hash_check') for n in closure],
  'reviewed_predecessor_definition_sources':[entry(f'lean/PaperX/{n}.lean',role='predecessor_definition_or_proof',review_mode='independent_exact_source') for n in reviewed],
  'scope_materials_consulted':[entry(p,role='context_after_raw_source_review') for p in ['CLAIM91_TARGET_CONTRACT.md','claim91_scope_review.md']],
  'external_primary_sources':external,
  'evidence':evidence,
  'self_cycle_policy':'The manifest does not hash itself. The independent report is the final evidence entry. Mutable provenance, README and Block25 amended TeX are excluded.'
}
(ROOT/'CLAIM91_PROOF_AUDIT_SOURCES.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'new_production_sources':len(new),'internal_dependency_source_closure':len(closure),'reviewed_predecessor_definition_sources':len(reviewed),'external_primary_sources':len(external),'evidence':len(evidence),'report_sha256':sha(ROOT/'CLAIM91_PROOF_AUDIT.md'),'manifest_sha256':sha(ROOT/'CLAIM91_PROOF_AUDIT_SOURCES.json')},indent=2))
