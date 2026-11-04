#!/usr/bin/env python3
"""Validate the bounded audit's saved results and emit a compact summary."""
import json
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'results'
IDS=['running-8192','running-16384','equal-8','clustered-8','mixed-12','wide-8',
     'scale-small','scale-large','deep-100','deep-1000','deep-5000','deep-5000-tight']
def load(name):return json.loads((RESULTS/(name+'.json')).read_text())
rows=[load(name) for name in IDS]
finite=[r for r in rows if r['finite_enclosure']]
assert len(finite)==11
assert all(r['reference_fully_contained'] for r in finite)
assert sum(r['accuracy_decision']['accepted'] for r in rows)==10
for row in finite:
    left,right=map(Decimal,row['engine']['log10_interval'].strip()[1:-1].split(','))
    rleft,rright=map(Decimal,row['independent_reference']['log10'])
    assert left<=rleft<=rright<=right,row['id']
assert not load('running-8192')['accuracy_decision']['accepted']
assert not load('wide-8')['finite_enclosure']
assert not load('wide-8')['accuracy_decision']['accepted']
controls=load('negative-controls')
assert len(controls['domain_and_budget_controls'])==14
assert all(r['rejected'] for r in controls['domain_and_budget_controls'][:-1])
assert controls['domain_and_budget_controls'][-1]['certified'] is False
assert len(controls['resource_api_probes'])==3
assert all(r['exceeded_declared_resource_cap'] and not r['certified'] for r in controls['resource_api_probes'])
comparison=load('comparisons')
assert comparison['provenance']['git_blob_sha1']=='ee7e6c1f81ffcb8a1496d5d1d43839bdf6d03867'
assert len(comparison['comparisons'])==7
for row in comparison['comparisons']:
    d=row['davies'];i=row['imhof_weighted']
    if row['case']=='wide-8':
        assert d['ifault']==1 and not d['success_flag_and_probability_range']
    else:
        assert d['ifault']==0 and d['success_flag_and_probability_range']
        assert d['observed_error_within_requested_absolute_accuracy']
    assert not i['warnings'] and i['observed_error_within_requested_absolute_accuracy']
assert all(load('matrix_example')['checks'].values())
assert len(load('packet-control')['rows'])==6
summary={'source_revision':load('environment')['source_revision'],
         'tail_evaluations':12,'finite_enclosures':11,'independent_reference_containments':11,
         'requested_widths_accepted':10,'domain_and_budget_controls':14,
         'resource_contract_findings':3,'davies_successes':6,'davies_failed_accuracy_requests':1,
         'weighted_imhof_observed_absolute_error_checks':7,
         'candidate_repair':'Separate generated patch; publication master unchanged',
         'timing_claim':'No equal-accuracy speed comparison',
         'case_summary':[{'id':r['id'],'q_decimal':r['input']['q'],'modes':r['engine']['K'],
             'requested_relative_accuracy':r['requested_relative_accuracy'],
             'log10_interval':r['engine']['log10_interval'],
             'independent_reference_log10_interval':r['independent_reference']['log10'],
             'ratio_upper':r['accuracy_decision']['ratio_upper'],
             'accepted':r['accuracy_decision']['accepted'],
             'finite_enclosure':r['finite_enclosure'],
             'reference_fully_contained':r['reference_fully_contained']} for r in rows]}
(RESULTS/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='case_summary'},indent=2))
