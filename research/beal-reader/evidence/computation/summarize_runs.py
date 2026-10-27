#!/usr/bin/env python3
"""Describe actual completed run records without changing their statuses."""
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/computation'
records=[]
for path in sorted(BASE.glob('*/manifest.json')):
    m=json.loads(path.read_text());folder=path.parent.name
    record={'path':path.relative_to(ROOT).as_posix(),'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'claim_id':m['claim_id'],'run':m['run'],'actual_argv':m['command'],'mathematical_bounds':m['mathematics']['bounds']}
    results=[]
    for resultpath in m['declared_results']:
        p=ROOT/resultpath
        if p.is_file():
            d=json.loads(p.read_text()) if p.suffix=='.json' else {}
            results.append({'path':resultpath,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'interpreted_status':d.get('status','No top-level status'),'complete_json_comparisons':len(d.get('complete_json_comparisons',{}))})
        else:results.append({'path':resultpath,'exists':False})
    record['results']=results
    if folder=='block67-run':record['interpretation']='Failed generic wrapper: original verifier exited 0 with its documented PASS, eight complete outputs and nine reject controls. Separate status-review and portable scientific success do not overwrite this failure.'
    elif folder=='block69-run':record['interpretation']='Resource-inconclusive original archive wrapper: 840 second wall cap, no final accepted scientific result. Later portable 69 success remains separate.'
    elif folder=='reader-data-qa-run':record['interpretation']='Failed independent QA test used cyclotomic residue degree instead of base-field inert degree in h. Original guide/scientific data unchanged. Corrected separately versioned QA uses Q=q².'
    elif folder=='unit-domain71-run':record['interpretation']='Legacy primary 2304 unit metadata is wrong; actual unchanged loop and separate original result give 2352. Historical bytes unchanged.'
    elif folder.startswith('portable'):record['interpretation']='Complete portable exact science comparison at original bounds; archive integrity and corruption controls not reasserted.'
    else:record['interpretation']='Read the declared result and audit report; successful process status alone is not a mathematical verdict.'
    records.append(record)
portable=[]
for record in records:
    match=re.fullmatch(r'portable(\d+)-run',Path(record['path']).parent.name)
    if match:
        assert record['run']['status']=='completed' and record['run']['exit_status']==0,record['path']
        assert any(r.get('interpreted_status','').startswith('PASS') for r in record['results']),record['path']
        portable.append(int(match.group(1)))
assert sorted(portable)==list(range(67,81)),portable
summary={'schema':1,'status':'ALL_RECORDS_RECONCILED_FAILURES_PRESERVED','records':records,'portable_blocks_completed':sorted(portable),'archive79_scope':'Immediate Block 79 default verifier was freshly replayed inside Block 80; no standalone block79-run record.','original_scientific_snapshots':{'files':166,'bytes':2040655,'pins':'evidence/computation/EXACT_SOURCE_PINS.json'},'additional_qa_snapshots':'readerqa_inputs and metadata71_inputs are separately pinned; not included in the 166 scientific-snapshot count.','actual_arithmetic_targets_authenticated':0,'patterns_eliminated':0,'nonclaims':['No full archival chain replay inferred.','No finite run proves Beal or authenticates inherited arithmetic geometry.']}
(BASE/'RUN_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Reconciled',len(records),'actual run records')
