#!/usr/bin/env python3
"""Finalize an already completed human/source audit only for unchanged inputs.

This records review provenance; it cannot perform or replace mathematical or
visual review. A changed semantic-review source or PNG is a hard stop.
"""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime, timezone
from math import comb
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parent.parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    return json.loads((ROOT/p).read_text())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',required=True)
    args=parser.parse_args()
    run=Path(args.run)
    manifest=load(run/'manifest.json')
    finite=load(run/'finite_checks.json')
    assert manifest['schema_version']==2 and manifest['run']['status']=='completed' and manifest['run']['exit_status']==0
    assert finite['status']=='PASS' and finite['lesson_contract_families']==13
    # The actual manifest is validated separately by the mathbox validator.
    snapshot=load('evidence/v04_semantic_review_prebuild.json')
    for item in snapshot['source_files']+snapshot['figure_pngs']:
        assert sha(ROOT/item['path'])==item['sha256'], 'Review freshness failure: '+item['path']
    bridge=load('evidence/bridge_checks.json')
    operators=load('evidence/operator_checks.json')
    capstone=load('evidence/capstone_checks.json')
    b={r['id']:r['details'] for r in bridge['checks']}
    c={r['name']:r['details'] for r in capstone['checks']}
    o=operators['checks']
    f=[0,1]
    while len(f)<32:
        f.append(f[-1]+f[-2])
    assert b['B01']['cases'][0]['coefficients']==[2**n for n in range(19)]
    assert b['B01']['cases'][1]['coefficients']==[1]*19
    assert b['B01']['cases'][2]['coefficients']==[2**n-1 for n in range(19)]
    assert b['B02']['three_tap_output']==[sum(h*f[n-k] for k,h in enumerate([1,2,1]) if n>=k) for n in range(19)]
    assert b['B02']['boundary_correction']==[-int(n==1) for n in range(19)]
    assert b['B04']['central_binomial']==[comb(2*n,n) for n in range(19)]
    assert list(map(Q,b['B04']['Catalan']))==[Q(comb(2*n,n),n+1) for n in range(19)]
    assert list(map(Q,o['O01']['pulled_back_counts']))==[Q(1-n) for n in range(12)]
    assert list(map(Q,o['O02']['difference_coefficients']))==[0,0,0,4,0]
    assert o['O03']['causal_output_full_flush']==[1,2,-1,-2,0]
    assert o['O03']['causal_shifted_output_full_flush']==[6,2,-1,-2,-5]
    assert c['Fixed record and full finite residual']['full_output']==[0,1,0,0,0,0,0,0,-21,-13]
    assert c['Projection obstruction after the filter']['even_output_Q']==[0,0,0,-1,-21]
    assert c['Chunked execution and continuous phase clock']['all_positive_chunk_compositions']==128
    # Author-saved output hashes and every recorded input hash must remain fresh.
    author_pin_checks=[]
    for label,record in [('B',bridge),('O',operators),('C',capstone)]:
        if label=='O':
            source_items=record['inputs']; output_items=record['artifacts']
        else:
            source_items=record['input_artifacts']; output_items=record['outputs']
        for item in source_items+output_items:
            assert sha(ROOT/item['path'])==item['sha256'], 'Author evidence freshness failure: '+item['path']
        author_pin_checks.append({'record':label,'status':'PASS','source_artifacts':len(source_items),'output_artifacts':len(output_items)})
    source=load('evidence/OEIS_SOURCE_RECORDS.json')
    source_comparisons=[]
    expected={'A000045':f[:8], 'A000984':[comb(2*n,n) for n in range(8)],
              'A000108':[comb(2*n,n)//(n+1) for n in range(8)]}
    for r in source['records']:
        if r['id'] in expected:
            assert r['initial_index']==0 and r['first_eight_terms']==expected[r['id']]
            assert sha(ROOT/r['extraction_path'])==r['extraction_sha256']
            source_comparisons.append({'id':r['id'],'status':'PASS','starting_index':0,'terms_checked':8,
                                       'extraction_path':r['extraction_path'],'extraction_sha256':r['extraction_sha256']})
    assert len(source_comparisons)==3
    extra=['evidence/v04_independent_audit.py','evidence/v04_independent_contract.json',
           'evidence/v04_independent_audit.md','evidence/v04_finalize_audit.py',
           'evidence/v04_semantic_review_prebuild.json','evidence/OEIS_SOURCE_RECORDS.json',
           'source_data/oeis/A000045.txt','source_data/oeis/A000984.txt','source_data/oeis/A000108.txt',
           'evidence/bridge_checks.json','evidence/operator_checks.json','evidence/capstone_checks.json',
           str(run/'manifest.json'),str(run/'finite_checks.json')]
    pins=list(snapshot['source_files'])+[{'path':p,'sha256':sha(ROOT/p)} for p in extra]
    report={
      'schema':'komorebi-v04-independent-math-review-v1',
      'checked_at_utc':datetime.now(timezone.utc).isoformat(),
      'status':'PASS','primary_proof_audit_verdict':'proved as written',
      'verdict_scope':'The thirteen new displayed elementary identities and counterexamples, with their explicit coefficient, analytic, boundary, finite-record, and model conventions. No other volume-wide proof claim is being audited.',
      'coverage':{'lessons':13,'chapter_blocks':['B01-B04','O01-O03','C01-C06'],
                  'author_generators':3,'figures_individually_inspected':13,
                  'integration_hunks':['main.tex reading-route row and guide counts','addition_sources.tex closing bridges/capstone paragraph']},
      'independence':{'implementation':'Written from definitions before reading the new author generators; no author implementation imports.',
                      'second_review':'Fresh direct reductions of seeds, factorial normalization, integration, Bernoulli translation, boundaries, model repair and generic discarded-channel obstruction.',
                      'limitation':'Agent agreement is supporting review; direct reductions supply the mathematical argument.'},
      'universal_reductions':'evidence/v04_independent_audit.md',
      'finite_computation':{'verdict':'implementation and finite assertion verified in the stated range',
                            'contract':'evidence/v04_independent_contract.json','manifest':str(run/'manifest.json'),
                            'result':str(run/'finite_checks.json'),'lesson_families':13,
                            'exact_assertions':finite['assertion_count'],
                            'counts_include':'Conjunctions and coefficientwise predicates counted as their named mathematical checks; no statistical interpretation.',
                            'independent_chunk_enumerator':'Seven-boundary bit-mask subsets; all 128 positive P8 compositions, distinct from author recursive composition enumeration.'},
      'obligation_matrix':[{'lesson':r['id'],'types_hypotheses_boundaries':'passed','direct_reduction':'passed',
                            'bounded_independent_implementation':'passed','displayed_example_and_figure_semantics':'passed'} for r in finite['records']],
      'resolved_findings':snapshot['resolved_findings'],'unresolved_findings':[],
      'source_identifications':{'method':'Authorized project-local dated official extracts; no new external theorem dependency.',
                               'pinned_official_export_commit':source['source_commit'],'prefix_checks':source_comparisons,
                               'scope':'Identification and normalization only; no fresh live-entry or novelty claim.'},
      'author_serialization_checks':'Fourteen decisive source-record values independently compared to exact definitions; all PASS.',
      'author_hash_freshness':author_pin_checks,
      'proofreading':{'mode':'review only; authors applied two scoped clarifications',
                      'routine_edits_by_auditor':'none','mathematical_token_changes_by_auditor':'none',
                      'resolved_author_changes':['O01 Q/R/C factorial-normalization domain','C03/C04 explicit multiplication by A(z)'],
                      'unresolved':'none'},
      'semantic_review_freshness':'Every prebuild reviewed source and PNG remains byte-identical after full reproduction.',
      'source_pins':pins,'semantic_png_pins':snapshot['figure_pngs'],
      'non_claims':['Finite checks do not prove the universal identities; their direct reductions are separate.',
                    'No new Lean certificate, historical novelty finding, noisy-recovery theorem, hidden-state robustness claim, or continuous reconstruction accuracy.',
                    'Assembled-PDF layout and inherited-page preservation are audited separately by the parent workflow.']}
    (ROOT/'evidence/v04_independent_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'PASS','lessons':13,'exact_assertions':finite['assertion_count'],
                      'source_pins':len(pins),'PNG_pins':len(snapshot['figure_pngs'])}))

if __name__=='__main__':
    main()
