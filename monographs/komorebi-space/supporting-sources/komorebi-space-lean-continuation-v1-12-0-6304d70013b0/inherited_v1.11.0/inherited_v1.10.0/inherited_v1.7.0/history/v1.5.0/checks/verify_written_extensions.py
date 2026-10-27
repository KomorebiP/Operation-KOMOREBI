#!/usr/bin/env python3
"""Check WR identifiers, scope metadata and source coverage, not proof validity."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data/written_extensions.json').read_text())
expected={f'WR{i:02d}' for i in range(1,13)}
if {e['id'] for e in rows}!=expected or len(rows)!=12:
    raise ValueError('Written-extension identifier inventory is incomplete or duplicated')
text='\n'.join(p.read_text() for p in (ROOT/'source/chapters').glob('*.tex'))
ids=re.findall(r'\\written\{(WR\d{2})\}',text)
if set(ids)!=expected or len(ids)!=len(rows):
    raise ValueError('Written-extension markers are incomplete or duplicated')
records=[]
for e in rows:
    source=ROOT/e['source'];s=source.read_text()
    if r'\label{'+e['id']+'}' not in s or e['lean_declarations']:
        raise ValueError('Missing theorem label or unsupported Lean assignment: '+e['id'])
    if e['evidence_status']!='COMPLETE_WRITTEN_PROOF_NOT_NEW_LEAN':
        raise ValueError('Wrong evidence status: '+e['id'])
    records.append({'id':e['id'],'source':e['source'],'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                    'status':e['evidence_status']})
result={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),'written_items':len(rows),
        'items':records,'scope':'Identifier, hash, and evidence-scope checks only. Not a proof checker or a new Lean run.'}
(ROOT/'audit/regularization/written_scope.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
