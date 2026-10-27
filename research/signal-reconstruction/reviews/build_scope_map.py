#!/usr/bin/env python3
"""Locate inherited prose claims without assigning them Lean coverage."""
from pathlib import Path
import csv
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--upstream',type=Path,help='Directory containing preserved inherited source packages')
args = parser.parse_args()
bundled = ROOT / 'sources'
UPSTREAM = (args.upstream.resolve() if args.upstream is not None else
            bundled if list(bundled.rglob('Universal_Unknown_Edge_Recovery.tex')) else
            ROOT.parents[1] / 'work' / 'signal' / 'upstream')
NAMES = [
    ('U', 'Universal_Unknown_Edge_Recovery.tex'),
    ('C', 'Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex'),
    ('B', 'Complex_Signal_Image_Gibbs_Benchmark.tex'),
]
REPAIRS = {
    'No uniform Lipschitz recovery over colliding edges': 'define matched circular location metric and use a fixed-order pair of narrow pulses',
    'No separation-free stability': 'define target metric and use a fixed-order witness',
    'Universal finite-dictionary recovery': 'declare full-rank spark convention or use spark>min(2s,N)',
    'Finite dictionary identifiability': 'declare full-rank spark convention or retain the null-secant criterion',
    'Finite-dictionary noise bound': 'handle s=0 and empty coefficient space separately',
    'Exact multi-offset phase': 'require at least one adjacent product R>=1',
    'Resolved synthesis inequality': 'require bounded linear smooth reconstruction',
    'Universal unknown-edge recovery in \\(\\EdgeClass\\)': 'specify almost-everywhere equality or a right-continuous representative and handle zero order separately',
}
EXTERNAL = {
    'Order recovery under a singular-value gap': ['Weyl singular-value perturbation bound'],
    'Deterministic root-disk certificate': ['Rouche strict-boundary theorem'],
}
records = []
source_files = []
for prefix, name in NAMES:
    hits = list(UPSTREAM.rglob(name))
    if len(hits) != 1:
        raise RuntimeError(f'Expected exactly one source {name}, got {len(hits)}')
    p = hits[0]
    raw = p.read_bytes()
    text = raw.decode('utf-8')
    sha = hashlib.sha256(raw).hexdigest()
    source_files.append({'basename':name, 'sha256':sha, 'bytes':len(raw),
                         'upstream_relative_path':str(p.relative_to(UPSTREAM))})
    pattern = r'\\begin\{(theorem|proposition|lemma|corollary)\}\[([^\]]*)\]'
    for i, m in enumerate(re.finditer(pattern, text), 1):
        end = text.index('\\end{' + m[1] + '}', m.end())
        statement = text[m.end():end].strip()
        next_environment = re.search(r'\\begin\{(?:theorem|proposition|lemma|corollary)\}', text[end:])
        proof_begin = text.find('\\begin{proof}',end)
        proof = None
        if proof_begin >= 0 and (next_environment is None or proof_begin < end + next_environment.start()):
            proof_end = text.find('\\end{proof}',proof_begin)
            proof = text[proof_begin+len('\\begin{proof}'):proof_end].strip()
        name = m[2]
        records.append({
            'inherited_claim_id':f'{prefix}-{i:02d}', 'title':name,
            'kind':m[1], 'source_basename':p.name, 'source_sha256':sha,
            'source_line':text.count('\n',0,m.start())+1,
            'statement_tex':statement,
            'statement_sha256':hashlib.sha256(statement.encode()).hexdigest(),
            'proof_tex':proof,
            'proof_sha256':hashlib.sha256(proof.encode()).hexdigest() if proof is not None else None,
            'evidence_layer':'inherited_manuscript_proof',
            'formal_status':'no_dedicated_signal_lean_declaration_identified_in_bounded_search',
            'publication_repair':REPAIRS.get(name),
            'external_inputs':EXTERNAL.get(name,[]),
            'review_scope':'source scope and selected direct implications; not final companion reconciliation',
        })

related = [
    {'file':'KnownEdge.lean','declaration':'KomorebiPaperV.known_edge_error',
     'scope':'Exact algebraic cancellation of a supplied known edge; no edge estimator'},
    {'file':'MaskPerturbation.lean','declaration':'KomorebiPaperV.MaskPerturbation.finite_p_perturbation',
     'scope':'Supplied measurable masks/amplitudes, 1<=p<infinity, extended seminorm'},
    {'file':'MaskPerturbation.lean','declaration':'KomorebiPaperV.MaskPerturbation.infinity_perturbation',
     'scope':'Supplied masks/amplitudes and essential-supremum bound'},
    {'file':'MaskPerturbation.lean','declaration':'KomorebiPaperV.MaskPerturbation.full_signal_perturbation',
     'scope':'Supplied background and edge error estimates combined'},
]
inventory = ROOT/'lean/Related_Declaration_Inventory.json'
if inventory.is_file():
    indexed = {r['name']:r for r in json.loads(inventory.read_text())}
    for relation in related:
        declaration = indexed[relation['declaration']]
        relation.update({'source_file':declaration['file'],'source_line':declaration['line'],
                         'source_sha256':declaration['source_sha256'],
                         'evidence':'preserved_related_Paper_V_v1.1.0_source_and_inherited_checks_with_fresh_static_correspondence',
                         'signal_specific_formal_certificate':False})
standalone = []
for p in sorted(UPSTREAM.rglob('infinite_packet_gibbs_reconstruction*.py')):
    raw = p.read_bytes()
    text = raw.decode('utf-8')
    locators = {}
    for target in ['class InfinitePacketGenerator:', 'def register_mask(', 'def _refit(',
                   'def complete_with_pixels(', 'def bounded_synthesis(',
                   'def benchmark_case(', 'def run_tests(']:
        at = text.find(target)
        if at>=0:locators[target]=text.count('\n',0,at)+1
    standalone.append({'basename':p.name,'sha256':hashlib.sha256(raw).hexdigest(),
                       'bytes':len(raw),'upstream_relative_path':str(p.relative_to(UPSTREAM)),
                       'locators':locators,
                       'evidence_layer':('bounded_python_source_review_no_execution'
                                         if p.name.endswith('_spd.py')
                                         else 'source_hash_and_function_locator_inventory_only')})
result = {
    'schema':'komorebi.signal.source-claim-associations.v1',
    'edition':'2026-10-06','author':'Komorebi P.',
    'primary_verdict':'correct_only_after_stated_restrictions_and_local_repairs',
    'dedicated_signal_formalization_identified':False,
    'no_formalization_claim_scope':'Bounded search and inspected original source packages only',
    'source_files':source_files,'claim_records':records,
    'source_lookup_root':str(UPSTREAM.relative_to(ROOT)) if UPSTREAM.is_relative_to(ROOT) else 'authoring_workspace_upstream',
    'standalone_source_records':standalone,
    'standalone_boundaries':[
        'full-pixel adaptive approximation, not blind finite-Fourier recovery',
        'ideal unbounded grammar distinct from finite candidate/mask caps',
        'ridge refit distinct from exact orthogonal projection',
        'nonlinear clipping distinct from bounded linear smooth synthesis',
        'full residual archive distinct from sparse compression',
        'historical per-method runtime zeros are placeholders caused by an unmatched method label'],
    'related_formal_infrastructure':related,
    'related_formal_locator':{'name':'Paper_V_Lean_Guide_Final.pdf',
                              'library_file_id':'libfile_19f5cc36cf4081918a8b744a5e2321a1',
                              'pages':[16,17],
                              'raw_proof_status':'validated_preserved_related_v1.1.0_sources_and_inherited_audits_static_only',
                              'current_source_root':'related_formal/paper_v/formalization/lean',
                              'latest_archive_status':'two_retrieved_copies_malformed_same_size_and_sha256',
                              'fallback_record':'provenance/PAPER_V_CHECKED_CHECKPOINT.json',
                              'fresh_signal_lean_build':False},
    'non_environment_repair':{
        'source':'Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex',
        'locator':'after Exact edge packet corollary, displayed L1 error estimate',
        'old_location_term_status':'refuted_by_two_jump_mean_zero_interval',
        'corrected_bound':'T/4 sum |a-ahat| + 2 sum |ahat| d(1-d/T)',
        'simpler_bound':'T sum |a-ahat| + 2 sum |ahat| d',
        'independent_review':'Definitions-only derivation by signal_edge_bound_check'},
    'empirical_boundary':{
        'controlled':'Finite-rate signals and exact finite dictionary images under tested conditions',
        'exploratory':'Out-of-dictionary shapes, text, rings, natural images, background mismatch',
        'solver_boundary':'Greedy selection and largest-singular-ratio order detection are implementation choices, not guaranteed by uniqueness/gap statements alone'},
}
(ROOT/'reviews'/'SIGNAL_SOURCE_CLAIM_ASSOCIATIONS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
with (ROOT/'reviews'/'SIGNAL_SOURCE_CLAIM_ASSOCIATIONS.csv').open('w',newline='') as f:
    cols=['inherited_claim_id','title','kind','source_basename','source_sha256','source_line','evidence_layer','formal_status','publication_repair']
    w=csv.DictWriter(f,fieldnames=cols)
    w.writeheader()
    for record in records:w.writerow({c:record[c] for c in cols})
print(json.dumps({'source_count':len(source_files),'inherited_named_claim_count':len(records),
                  'publication_repairs':sum(r['publication_repair'] is not None for r in records),
                  'dedicated_signal_lean_claim_count':0}))
