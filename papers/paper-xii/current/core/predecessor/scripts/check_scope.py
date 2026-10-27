#!/usr/bin/env python3
"""Check release metadata, source preservation, crosswalks and companion notices."""
from pathlib import Path
import hashlib, json, re, sys
import fitz

root = Path(__file__).resolve().parent.parent
edition = json.loads((root/'EDITION.json').read_text())
checks = []
def check(name, passed): checks.append({'check':name,'passed':bool(passed)})
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

check('three final companions',len(edition['documents'])==3)
check('revised and original-wording counts remain separate',edition['inherited_revised_claims']=={'complete':49,'partial':0,'unchecked':0} and edition['inherited_original_wording_claims']=={'complete':41,'partial':7,'unchecked':1})
check('correct inherited status labels',edition['original_unchecked_claim']=='6.12' and '10.5' in edition['original_partial_claims'])
check('eight inherited amendments',edition['inherited_amendments']==['6.12','9.4','9.5','9.6','10.5','12.2','12.4','12.6'])
check('fresh Lean execution not claimed',edition['fresh_lean_replay'] is False)
check('production census',all(edition[k]==v for k,v in {'production_modules':96,'public_named_declarations':1229,'own_public_theorems':748,'reused_paper_x_theorems':81,'distinct_claim_targets':291}.items()))
check('52 complete proof environments retained',edition['original_proof_environments']==edition['retained_proof_environments']==52)
pages=0
for doc in edition['documents']:
    p=root/doc['path']; check(doc['role']+' PDF checksum',sha(p)==doc['sha256'] and p.stat().st_size==doc['bytes'])
    with fitz.open(p) as pdf:
        text=' '.join(page.get_text() for page in pdf)
        check(doc['role']+' page count',len(pdf)==doc['pages'])
        check(doc['role']+' supporting Markdown notice','.md' in text and ('included' in text.lower() or 'accompan' in text.lower()))
        check(doc['role']+' author metadata',pdf.metadata.get('author')=='Komorebi P.' and 'komorebip.' in re.sub(r'\s+','',text).casefold())
        check(doc['role']+' exact vector figures',all(not page.get_images(full=True) for page in pdf))
        pages+=len(pdf)
check('total PDF pages',pages==edition['total_pages'])

raw=json.loads((root/'provenance/RAW_SOURCE_PRESERVATION.json').read_text())
check('raw source inventory count',len(raw['payloads'])==raw['files']==edition['raw_source_files'])
check('every preserved source byte',all((root/r['path']).is_file() and (root/r['path']).stat().st_size==r['bytes'] and sha(root/r['path'])==r['sha256'] for r in raw['payloads']))
companion_preservation=json.loads((root/'provenance/COMPANION_SOURCE_PRESERVATION.json').read_text())
check('complete frozen companion packages preserved',all((root/r['path']).is_file() and sha(root/r['path'])==r['sha256'] for r in companion_preservation['payloads']))
for role in ['traditional','visual_guide','lean_guide']:
    folder=root/'editable'/role
    manifest=folder/'MANIFEST.sha256'
    if manifest.is_file():
        rows=[line.split('  ',1) for line in manifest.read_text().splitlines() if line.strip()]
    else:
        rows=[(digest,path) for path,digest in json.loads((folder/'MANIFEST_SHA256.json').read_text()).items()]
    check(role+' frozen package manifest',all((folder/path).is_file() and sha(folder/path)==digest for digest,path in rows))
index=(root/'SUPPLEMENTARY_INDEX.md').read_text()
markdown=sorted(str(p.relative_to(root)) for p in root.rglob('*.md'))
check('all Markdown files indexed',len(markdown)==edition['included_markdown_files'] and all(']('+p+')' in index for p in markdown))

census=json.loads((root/'editable/lean_guide/data/census.json').read_text())
crosswalk=json.loads((root/'editable/lean_guide/data/claim_crosswalk.json').read_text())
check('49 revised claim catalog rows',census['revised_claims']==49 and len(crosswalk['claims'])==49)
sources=list((root/'editable/lean_guide/formal_release/lean').rglob('*.lean'))
check('96 production Lean sources included',len(sources)==96)
check('no Paper XI import dependency',all(not re.search(r'^\s*import\s+PaperXI\.',p.read_text(),re.M) for p in sources))
prior=json.loads((root/'provenance/PREVIOUS_SERIES_STATUS.json').read_text());current=json.loads((root/'SERIES_STATUS.json').read_text())
check('completed I–XI records unchanged',all(a==b for a,b in zip(prior['papers'],current['papers']) if a['paper']!='XII'))
check('series closed after XII',current['finalized_papers']==12 and current['finalized_companion_documents']==36 and not current['active_authoring_papers'])
failed=[r['check'] for r in checks if not r['passed']]
report={'status':'FAIL' if failed else 'PASS','checks':checks,'failures':failed,'scope':'Metadata, source bytes, crosswalk size and PDF notices. This is not a proof audit, experiment or Lean replay.'}
print(json.dumps(report,indent=2));sys.exit(bool(failed))
