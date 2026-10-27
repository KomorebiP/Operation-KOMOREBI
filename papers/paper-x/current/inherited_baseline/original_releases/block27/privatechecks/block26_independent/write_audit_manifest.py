from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p,**kw):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),**kw}
compile=json.loads((OUT/'CompileSummary.json').read_text())
closure=json.loads((OUT/'DependencyClosure.json').read_text())
external=json.loads((OUT/'ExternalSourceCache.json').read_text())
reviewed=['CompatibleSystemRigidity','IrreducibleCharacterRigidity','FiniteAvoidanceBoundary','ProfiniteSeparation','CompletionExamples','QuadraticCharacters','QuadraticAlgebra','CyclotomicFrobeniusPrimes','CyclotomicPrimeCoverage','CyclotomicSystemSeparation','CompatibleSystemSeparation','CofiniteConjugacyCoverage','FiniteSeparation','TraceRecovery','GeneralCharacters','DenseTraceSeparation','SimpleModuleSeparation']
files=[ROOT/'BLOCK26_PROOF_AUDIT.md']
for p in sorted(OUT.rglob('*')):
 if p.is_file() and 'build' not in p.relative_to(OUT).parts and 'external_sources' not in p.relative_to(OUT).parts and p.name!='ReviewNotes.md' and '__pycache__' not in p.parts:
  files.append(p)
x={
 'schema':'paperx.block26.independent-proof-audit.v1',
 'audit_kind':'independent_exact_source',
 'primary_verdict':'incomplete, with the smallest missing implication',
 'verdict_scope':'full source Claim 9.1',
 'full_source_claim':{'claim':'Claim 9.1, Finite Frobenius separation','status':'partial','missing_implication':'General arithmetic Frobenius coverage in the required finite quotients after every finite deletion; the proved arithmetic distribution covers one supplied finite cyclotomic quotient.'},
 'restricted_result':{'status':'proved as written','main_declaration':'PaperX.CyclotomicAbsoluteArithmeticSeparation.finite_arithmetic_system_separator','new_modules':9,'defect_found':False,'description':'Actual absolute Galois representations presented through one supplied finite cyclotomic quotient have a finite common algebraic separator with actual absolute integral-prime Frobenius witnesses, ideal inertia triviality, finite exclusions, and each member good-prime condition retained.'},
 'frozen_predecessor_archive':{'name':'PRSC_X_v0.25.0_Checked_TwentyFifth_Block.zip','sha256':'1ac6cc2b3dec7169c6b42c3c3625f3dcc809b3ccbee4af185fdacc3660abb133','production_source_count':161},
 'source_statement':entry(ROOT/'source/Projector_Resolved_Seed_Calculus_X_Block25_Amended.tex',role='primary_source_statement',locator='Section Compatible carriers and finite Frobenius separation, theorem Finite Frobenius separation'),
 'new_production_sources':[entry(ROOT/r['path'],role='primary',review_mode='independent_exact_source') for r in compile['compilations']],
 'internal_dependency_source_closure':[{**r,'role':'internal_dependency_source_inventory'} for r in closure['sources']],
 'reviewed_predecessor_definition_sources':[entry(ROOT/f'lean/PaperX/{n}.lean',role='reviewed_predecessor_definition_or_proof',review_mode='independent_exact_source') for n in reviewed],
 'external_primary_sources':external['sources'],
 'evidence':[entry(p,role='independent_audit_evidence') for p in files],
 'temporary_inputs':{'description':'The copied 161 predecessor objects were removed after isolated compilation and axiom review. Their original source paths and hashes are historical input records, not missing evidence leaves. Only the nine new object files remain in the temporary build; main evidence leaves do not pin that build directory.','restore':'run_audit.py restores predecessor object inputs from the frozen Block 25 tree on replay.'},
 'self_cycle_policy':'This manifest does not hash itself. The audit document is a leaf. Mutable release summaries and status documents are deliberately excluded.'
}
assert len(x['new_production_sources'])==9
for group in ['new_production_sources','internal_dependency_source_closure','reviewed_predecessor_definition_sources','external_primary_sources','evidence']:
 for r in x[group]:assert sha(ROOT/r['path'])==r['sha256'],r
(ROOT/'BLOCK26_PROOF_AUDIT_SOURCES.json').write_text(json.dumps(x,indent=2)+'\n')
print(json.dumps({k:len(x[k]) for k in ['new_production_sources','internal_dependency_source_closure','reviewed_predecessor_definition_sources','external_primary_sources','evidence']},indent=2))
