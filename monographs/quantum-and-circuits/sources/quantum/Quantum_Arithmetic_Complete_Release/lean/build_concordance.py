#!/usr/bin/env python3
"""Static, hash-bound source concordance. This is not a Lean proof checker."""
from pathlib import Path
import csv, hashlib, importlib.util, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'inputs/Komorebi_Quantum_Arithmetic_Lean_v0.2.0_Checked_1_/lean'
OLD = ROOT / 'inputs/Komorebi_Quantum_Arithmetic_Lean_v0.2.0_CHECKED/Komorebi_Quantum_Arithmetic_Lean_v0.2.0'
OUT = ROOT / 'lean'
MODULES = ['QuantumArithmeticBridge', 'FiniteFourier', 'SemanticBridge', 'Conventions', 'Publication']
spec = importlib.util.spec_from_file_location('original_verify_lean', SOURCE/'scripts/verify_lean.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
strip_comments = mod.strip_comments
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def qas(name):
    if name in ['publication_bridge', 'arithmetic_signal_quantum_bridge']: return ['QA18']
    if name.startswith('interpret_') or name.startswith('complexMatrix_') or name=='complexVector_mul': return ['QA17']
    if name in ['coprime_residues_exact','root_exact_order','zeta12_order_certificate','zeta12_inverse_certificate','root_is_exponential','root_power_twelve','rootPower_interpret']: return ['QA01','QA10']
    if name in ['normalized_fourier_left','normalized_fourier_right','fourier_unitary_left','fourier_unitary_right','fourierScale_interpret','fourier_entry_formula']: return ['QA03']
    if name in ['ramanujanC12_table','exact_phase_signal_lookup','complex_ramanujan_signal','ramanujan12_length']: return ['QA10']
    if name in ['ramanujan_dft_table','abs_ramanujan_dft_table']: return ['QA05','QA14']
    if name in ['projector12_shape','projector12_symmetric','projector12_idempotent','exact_projector_transport','exact_projector_matches_rational_table','projector_transport','projector_entry_formula','selector_idempotent','selector_selfAdjoint','projector_idempotent_complex','projector_selfAdjoint_complex']: return ['QA06','QA07']
    if name in ['stateScale_interpret','psi_entry_formula','chi_entry_formula','unitState_entry_formula','sqrt_twelve','sqrt_fortyeight','exact_state_preparation','exact_state_recovery','state_preparation','state_recovery','exact_unit_normalized','exact_psi_normalized','exact_chi_normalized','psi_normalized','chi_normalized','unitState_normalized']: return ['QA12']
    if name in ['same_computational_basis_probabilities','abs_ramanujan12_energy','exact_same_initial_probabilities','exact_orthogonal_states','same_initial_probabilities','states_orthogonal','absolute_signal_lookup']: return ['QA13']
    if name in ['recovered_mode_probability','recovered_total_probability','phase_stripping_coprime_probability','exact_coprime_mass_psi','exact_coprime_mass_chi','signed_state_recovers_arithmetic','unsigned_state_erases_arithmetic','recovered_probability_at','complete_phase_separation']: return ['QA14']
    if name=='no_reconstruction_from_initial_probabilities': return ['QA15']
    return ['QA07','QA11']

report = json.loads((SOURCE/'verification/final/REPORT.json').read_text())
log = (SOURCE/'verification/final/axiom_audit.log').read_text()
axioms = {}
for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]",log):
    axioms[m.group(1)] = [x.strip() for x in m.group(2).split(',') if x.strip()]
for m in re.finditer(r"'([^']+)' does not depend on any axioms",log): axioms[m.group(1)] = []
inventory, defs, checks = [], [], []
for module in MODULES:
    p=SOURCE/(module+'.lean'); raw=p.read_text(); clean=strip_comments(raw)
    checks.append({'file':p.name,'sha256':sha(p),'matches_archived_report':sha(p)==report['source_sha256'][p.name]})
    bad=re.findall(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',clean)
    assert not bad, (module,bad)
    starts = list(re.finditer(r'\b(theorem|def|abbrev|structure)\s+([A-Za-z_][A-Za-z_0-9]*)',clean))
    for i,m in enumerate(starts):
        start=m.start(); end=starts[i+1].start() if i+1<len(starts) else len(clean)
        # The original comment stripper preserves newlines, not byte offsets.
        line=clean[:start].count('\n')+1
        endline=clean[:end].count('\n')+1
        text='\n'.join(raw.splitlines()[line-1:endline-1]).split('\nend Komorebi.QuantumArithmetic')[0].strip()
        # Attributes can precede the keyword on the same physical line.
        text=text[text.find(m.group(1)+' '+m.group(2)):]
        # Remove comments/attributes belonging to the next declaration from the excerpt.
        if m.group(1)=='theorem':
            body_start=text.find(':='); statement=text[:body_start].strip() if body_start>=0 else text
            name='Komorebi.QuantumArithmetic.'+m.group(2)
            assert name in axioms, name
            inventory.append({'module':module,'source_file':module+'.lean','source_line':line,
              'name':name,'basename':m.group(2),'statement_source':statement,
              'source_sha256':sha(p),'archived_axioms':axioms[name],
              'manuscript_claim_ids':qas(m.group(2)),
              'coverage_domain':'fixed q = 12, except explicitly quantified residual identity and nonreconstruction function',
              'evidence':'archived fresh-source Lean build + per-module Lean-kernel replay; current source/log hash match'})
        else: defs.append({'module':module,'kind':m.group(1),'name':m.group(2),'source_line':line})
assert len(inventory)==96 and len({r['name'] for r in inventory})==96
for c in report['checks']:
    p=SOURCE/'verification/final'/c['log']
    checks.append({'file':'verification/final/'+c['log'],'sha256':sha(p),
                   'matches_archived_report':sha(p)==c['log_sha256']})
assert all(c['matches_archived_report'] for c in checks)
assert len(axioms)==96
module_counts={m:sum(r['module']==m for r in inventory) for m in MODULES}
claims = [
 {'claim_id':'QA01','topic':'Primitive root and exact order','lean_coverage':'fixed q=12 root order; general-q proof only in manuscript','declarations':['zeta12_order_certificate','root_exact_order','root_is_exponential']},
 {'claim_id':'QA02','topic':'Character orthogonality','lean_coverage':'q=12 consequence through exact unitary identities; general-q identity not a separate current theorem','declarations':['normalized_fourier_left','normalized_fourier_right']},
 {'claim_id':'QA03','topic':'Fourier unitarity, inverse, Parseval','lean_coverage':'both q=12 complex unitary matrix identities; general Parseval proposition not separately exported','declarations':['fourier_unitary_left','fourier_unitary_right','fourier_entry_formula']},
 {'claim_id':'QA04','topic':'Ramanujan Mobius formula and integrality','lean_coverage':'not formalized for arbitrary q; literal q=12 integer table certified','declarations':['ramanujanC12_table','complex_ramanujan_signal']},
 {'claim_id':'QA05','topic':'Ramanujan Fourier support and energy','lean_coverage':'exact q=12 DFT tables and energy 48; general q*phi(q) identity remains prose','declarations':['ramanujan_dft_table','abs_ramanujan_dft_table','ramanujan12_energy']},
 {'claim_id':'QA06','topic':'Divisor-order projector family and completeness','lean_coverage':'q=12 primitive-order projector only; all-six-divisor family and general completeness not Lean','declarations':['projector_transport','projector_entry_formula']},
 {'claim_id':'QA07','topic':'Projector geometry and energy','lean_coverage':'q=12 Hermitian idempotence, displayed energies, explicit kernel, and all-vector residual reconstruction','declarations':['projector_idempotent_complex','projector_selfAdjoint_complex','energy_decomposition','projector_not_injective','projector_residual_reconstructs']},
 {'claim_id':'QA08','topic':'Residue polyphase recombination','lean_coverage':'not formalized in this checkpoint','declarations':[]},
 {'claim_id':'QA09','topic':'Polyphase alias equations','lean_coverage':'not formalized in this checkpoint','declarations':[]},
 {'claim_id':'QA10','topic':'q=12 arithmetic sample table','lean_coverage':'exact tables connected to actual complex primitive phases','declarations':['coprime_residues_exact','exact_phase_signal_lookup','complex_ramanujan_signal']},
 {'claim_id':'QA11','topic':'q=12 filter and orthogonal energy decomposition','lean_coverage':'fully certified for displayed vectors','declarations':['projector12_recovers_test_signal','retained_discarded_orthogonal','signal_decomposition','energy_decomposition']},
 {'claim_id':'QA12','topic':'Normalized state preparation and recovery','lean_coverage':'actual complex normalized vector identities','declarations':['state_preparation','state_recovery','psi_normalized','chi_normalized','unitState_normalized']},
 {'claim_id':'QA13','topic':'Equal initial histograms and orthogonal states','lean_coverage':'fully certified for psi and chi','declarations':['same_initial_probabilities','states_orthogonal','absolute_signal_lookup']},
 {'claim_id':'QA14','topic':'Opposite coprime probabilities after basis change','lean_coverage':'actual transformed complex states have mass 1 versus 0','declarations':['signed_state_recovers_arithmetic','unsigned_state_erases_arithmetic','recovered_probability_at']},
 {'claim_id':'QA15','topic':'No reconstruction from initial histogram','lean_coverage':'no vector-valued function can reconstruct both specified states from their identical histograms; up-to-global-phase strengthening is prose only','declarations':['no_reconstruction_from_initial_probabilities']},
 {'claim_id':'QA16','topic':'Projective measurement law','lean_coverage':'complex projector algebra and relevant probabilities certified; abstract measurement/update API not formalized','declarations':['projector_idempotent_complex','projector_selfAdjoint_complex','projector_fixes_psi','projector_kills_chi']},
 {'claim_id':'QA17','topic':'Exact arithmetic to complex interpretation','lean_coverage':'addition, multiplication, conjugation, powers, finite sums, matrices, adjoints, vectors, normSq and mass transferred','declarations':['interpret_mul','interpret_conj','complexMatrix_mul','complexMatrix_adjoint','complexVector_mul','interpret_normSq']},
 {'claim_id':'QA18','topic':'Central q=12 bridge','lean_coverage':'publication bundle together with separately exported filter, energy, unit-state normalization, projector actions, and noninjectivity results; general-q extensions not included','declarations':['publication_bridge','projector12_recovers_test_signal','signal_decomposition','retained_discarded_orthogonal','ramanujan12_energy','noise12_energy','testSignal12_energy','energy_decomposition','unitState_normalized','projector_fixes_psi','projector_kills_chi','projector_not_injective']},
 {'claim_id':'QA19','topic':'Continuous relative-phase response sin squared theta/2','lean_coverage':'prose extension, not an inherited Lean theorem','declarations':[]},
 {'claim_id':'QA20','topic':'Dephased selected probability 1/3','lean_coverage':'prose density-matrix calculation, not an inherited Lean theorem','declarations':[]}
]
for c in claims:
    for n in c['declarations']: assert n in {r['basename'] for r in inventory}
for c in claims:
    for row in inventory:
        if row['basename'] in c['declarations'] and c['claim_id'] not in row['manuscript_claim_ids']:
            row['manuscript_claim_ids'].append(c['claim_id'])
payload={'schema_version':1,'audit_kind':'static hash-bound formal concordance, not a proof checker',
 'authoritative_checkpoint':'Komorebi_Quantum_Arithmetic_Lean_v0.2.0_Checked(1).zip / lean',
 'authoritative_receipt':'checked_checkpoint/verification/final/REPORT.json',
 'archived_run_started_utc':report['started_utc'],'archived_run_finished_utc':report['finished_utc'],
 'archived_status':report['status'],'fresh_status_file':'FRESH_LEAN_STATUS.json',
 'module_theorem_counts':module_counts,'active_named_theorem_count':len(inventory),
 'active_definition_inventory':defs,'axiom_union':sorted({a for r in inventory for a in r['archived_axioms']}),
 'older_checkpoint_reconciliation':{'older':'Komorebi_Quantum_Arithmetic_Lean_v0.2.0_CHECKED.zip','modules':4,'mathematical_theorems':59,'positive_refutation_controls':4,'original_preserved_statements':22,'not_added_to_current_count':True,
 'closed_later':['explicit F D F-adjoint=P transport','actual normalized-state matrix actions','standard exponential Fourier convention','initial-histogram nonreconstruction']},
 'hash_reconciliation':checks,'negative_control_boundary':'Latest false-mode rejection stopped at opaque Decidable reduction; it is not a direct falsity certificate. Positive DFT table establishes the correct mode. Sign and admission controls have direct diagnostics. Earlier checkpoint explicit refutation controls remain earlier evidence.',
 'manuscript_claim_concordance':claims,'theorems':inventory}
(OUT/'Lean_Concordance.json').write_text(json.dumps(payload,indent=2)+'\n')
with (OUT/'Lean_Concordance.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['module','source_file','source_line','name','manuscript_claim_ids','archived_axioms','source_sha256','statement_source']);w.writeheader()
    for r in inventory:
        x={k:r[k] for k in w.fieldnames};x['manuscript_claim_ids']=';'.join(x['manuscript_claim_ids']);x['archived_axioms']=';'.join(x['archived_axioms']);w.writerow(x)
target=OUT/'checked_checkpoint'
if target.exists():shutil.rmtree(target)
shutil.copytree(SOURCE,target)
(OUT/'SOURCE_RECONCILIATION.json').write_text(json.dumps({'status':'PASS','module_counts':module_counts,'active_named_theorems':96,'checked_hashes':checks,'axiom_entries':len(axioms)},indent=2)+'\n')
print(json.dumps({'status':'PASS','module_counts':module_counts,'theorems':96,'definitions':len(defs),'hash_checks':len(checks)},indent=2))
