from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def entry(p, **kw):
    return {'path': str(p.relative_to(ROOT)), 'sha256': sha(p), **kw}

comp = json.loads((OUT / 'CompileSummary.json').read_text())
closure = json.loads((OUT / 'DependencyClosure.json').read_text())
external = json.loads((OUT / 'ExternalSourceCache.json').read_text())
axioms = json.loads((OUT / 'AxiomSummary.json').read_text())
names = json.loads((OUT / 'names.json').read_text())
newpaths = {f'lean/PaperX/{name}.lean' for name in names}
predecessors = [r['path'] for r in closure['sources'] if r['path'] not in newpaths]
evidence = [ROOT / path for path in [
    'BLOCK27_PROOF_AUDIT.md', 'BLOCK27_TARGET_CONTRACT.md',
    'BLOCK27_SCOPE_RESOLUTION.md', 'GENERAL_COVERAGE_INTERFACE.md',
    'NEXT_TARGET.md', 'source/Projector_Resolved_Seed_Calculus_X_Block27_Amended.tex',
    'source/Block27_Amendments.patch', 'proofreading_structure.json', 'proofreading_patch.json']]
evidence += [p for p in sorted(OUT.rglob('*')) if p.is_file()
             and not {'build', 'external_sources', '__pycache__'}.intersection(p.relative_to(OUT).parts)]
manifest = {
    'schema': 'paperx.block27.independent-proof-audit.v1',
    'audit_kind': 'independent_exact_source',
    'primary_verdict': 'incomplete, with the smallest missing implication',
    'verdict_scope': 'full source Claim 9.1',
    'full_source_claim': {
        'claim': 'Claim 9.1, Finite Frobenius separation', 'status': 'partial',
        'missing_implication': 'Rational-base prescribed-conjugacy arithmetic prime coverage after every finite deletion; general-base applications additionally require corresponding actual-prime/norm-power attachment and coverage over F, or a proved transfer.'},
    'restricted_result': {
        'status': 'proved as written', 'new_modules': 8, 'source_theorem_lemma_count': 59,
        'environment_audited_declarations': axioms['total_declarations'],
        'axiom_union': axioms['axiom_union'], 'defect_found_in_final_Lean_sources': False,
        'description': 'Actual rational-base integral-prime Frobenius restriction to arbitrary finite normal number fields, discriminant unramifiedness, choice and embedding independence, and exact conditional arithmetic coverage equivalences.'},
    'frozen_predecessor_archive': {
        'name': 'PRSC_X_v0.26.0_Checked_TwentySixth_Block.zip',
        'sha256': '82bf63a4d4f2c10edb06ba4e43b4cf80855d651a7e16eb7c3956892d88e73679',
        'production_source_count': 170},
    'source_statement': entry(ROOT / 'source/Projector_Resolved_Seed_Calculus_X_Block26_Amended.tex',
        role='primary_source_statement', locator='Section Compatible carriers and finite Frobenius separation, theorem Finite Frobenius separation'),
    'new_production_sources': [entry(ROOT / r['path'], role='primary',
        review_mode='independent_exact_source') for r in comp['compilations']],
    'internal_dependency_source_closure': [{**r, 'role': 'internal_dependency_source_inventory'}
        for r in closure['sources']],
    'reviewed_predecessor_definition_sources': [entry(ROOT / p,
        role='reviewed_predecessor_definition_or_proof', review_mode='independent_exact_source') for p in predecessors],
    'external_primary_sources': external['sources'],
    'evidence': [entry(p, role='independent_audit_evidence') for p in evidence],
    'temporary_inputs': {
        'description': 'The copied 170 predecessor proof objects were removed after isolated compilation and transitive axiom review. Their source and object hashes remain historical input records. The eight independently built new objects remain available.',
        'restore': 'run_audit.py restores predecessor object inputs from the frozen Block 26 tree before replay.'},
    'self_cycle_policy': 'This manifest does not hash itself. Its audit document and immutable source/evidence files are leaves. Mutable final release summaries, measured-count placeholders, and another reviewer still writing their report are excluded.'}
assert len(manifest['new_production_sources']) == 8
assert len(predecessors) == 8
for section in ['new_production_sources', 'internal_dependency_source_closure',
                'reviewed_predecessor_definition_sources', 'external_primary_sources', 'evidence']:
    for row in manifest[section]:
        assert sha(ROOT / row['path']) == row['sha256'], row
(ROOT / 'BLOCK27_PROOF_AUDIT_SOURCES.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({k: len(manifest[k]) for k in ['new_production_sources',
    'internal_dependency_source_closure', 'reviewed_predecessor_definition_sources',
    'external_primary_sources', 'evidence']}, indent=2))
