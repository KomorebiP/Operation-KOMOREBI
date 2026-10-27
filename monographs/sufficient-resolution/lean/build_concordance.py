#!/usr/bin/env python3
"""Cross-map the traditional paper's claim register to actual source declarations."""
from __future__ import annotations
import argparse,csv,hashlib,json,pathlib

HERE=pathlib.Path(__file__).resolve().parent
def build(path):
    payload=json.loads(path.read_text())
    claims=payload if isinstance(payload,list) else payload['claims']
    registry={x['name']:x for x in json.loads((HERE/'Declaration_Inventory.json').read_text())}
    rows=[]
    for c in claims:
        names=[x['name'] for x in c['anchors']]
        assert names and all(n in registry for n in names),c['claim_id']
        records=[registry[n] for n in names]
        for a,r in zip(c['anchors'],records):
            assert a['source_sha256']==r['source_sha256'],(c['claim_id'],a['name'])
        rows.append({'claim_id':c['claim_id'],'block':c['block'],'title':c['title'],
                     'status':c['status'],'hypotheses':c['hypotheses'],
                     'hypotheses_tex':c['hypotheses_tex'],
                     'formula_tex':c['statement_tex'],'dependencies':c['dependencies'],
                     'declarations':names,'source_locations':[
                        {'name':r['name'],'kind':r['kind'],'file':'formal/'+r['file'],
                         'line':r['line'],'source_sha256':r['source_sha256']} for r in records],
                     'coverage':'Representative mapped declarations and their source hypotheses; supporting dependency proofs are not individually repeated in this row',
                     'evidence':'Existing source and block-scoped historical Lean records; no fresh final-edition Lean compilation'})
    assert [x['claim_id'] for x in rows]==[f'SR-{i:02d}' for i in range(1,65)]
    (HERE/'Claim_Lean_Concordance.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    fields=['claim_id','block','title','status','hypotheses','hypotheses_tex','formula_tex','dependencies','declarations','source_locations','coverage','evidence']
    with (HERE/'Claim_Lean_Concordance.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in row.items()})
    audit={'status':'PASS_CLAIM_TO_SOURCE_MAP','claim_count':64,
           'source_anchor_occurrences':sum(len(x['declarations']) for x in rows),
           'unique_source_anchors':len(set(n for x in rows for n in x['declarations'])),
           'input_concordance':path.relative_to(HERE.parent).as_posix(),
           'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
           'all_names_resolve':True,'all_source_hashes_match':True,'fresh_lean_compilation':False}
    (HERE/'CLAIM_MAPPING_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('concordance',type=pathlib.Path)
    build(ap.parse_args().concordance.resolve())
