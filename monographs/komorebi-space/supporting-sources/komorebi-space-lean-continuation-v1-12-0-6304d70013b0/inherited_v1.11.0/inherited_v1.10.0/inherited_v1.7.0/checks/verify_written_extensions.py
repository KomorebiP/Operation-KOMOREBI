#!/usr/bin/env python3
"""Check WR IDs and separate full, partial and written-only source correspondence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
from verify_focused_evidence import verify
ROOT=Path(__file__).resolve().parents[1]
release,receipt,audit=verify()
decls={r['name']:r for r in audit['declarations']}
rows=json.loads((ROOT/'data/written_extensions.json').read_text())
expected={f'WR{i:02d}' for i in range(1,17)}
if {e['id'] for e in rows}!=expected or len(rows)!=16:raise ValueError('WR inventory incomplete or duplicated')
text='\n'.join(p.read_text() for p in (ROOT/'source/chapters').glob('*.tex'))
ids=re.findall(r'\\written\{(WR\d{2})\}',text)
if set(ids)!=expected or len(ids)!=len(rows):raise ValueError('WR marker inventory incomplete or duplicated')
statuses={'FOCUSED_LEAN_COMPLETE':'Focused Lean counterpart verified. Examples and prose correspondence remain separately scoped.',
          'FOCUSED_LEAN_PARTIAL':'Partial focused Lean coverage. The limiting or additional conclusions retain written proofs.',
          'COMPLETE_WRITTEN_PROOF_NOT_NEW_LEAN':'Complete written proof. No new Lean counterpart is assigned.'}
counts={k:0 for k in statuses};records=[];tex=['% Generated source-bound WR evidence labels.']
for e in rows:
    p=ROOT/e['source'];s=p.read_text();status=e['evidence_status']
    if r'\label{'+e['id']+'}' not in s or status not in statuses:raise ValueError('Invalid label/status '+e['id'])
    names=e['lean_declarations']
    if bool(names)!=(status!='COMPLETE_WRITTEN_PROOF_NOT_NEW_LEAN'):raise ValueError('Inconsistent formal assignment')
    refs=[]
    for name in names:
        if name not in decls:raise ValueError('Not in accepted environment: '+name)
        module=decls[name]['module'];src=receipt['source_files'][module]
        refs.append({'name':name,'module':module,'source':src['path'],'source_sha256':src['sha256'],
                     'type':decls[name]['type'],'axioms':decls[name]['axioms']})
    records.append({'id':e['id'],'source':e['source'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
       'status':status,'coverage_note':e['coverage_note'],'source_references':refs})
    counts[status]+=1
    tex.append(r'\expandafter\def\csname WRstatus'+e['id']+r'\endcsname{'+statuses[status]+'}')
if counts!={'FOCUSED_LEAN_COMPLETE':4,'FOCUSED_LEAN_PARTIAL':2,'COMPLETE_WRITTEN_PROOF_NOT_NEW_LEAN':10}:raise ValueError('Unexpected coverage counts')
result={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),'written_items':len(rows),'counts':counts,
        'source_reference_count':sum(len(r['source_references']) for r in records),'items':records,
        'scope':'Editorial statement correspondence bound to accepted typed declarations. Not machine translation of prose.'}
(ROOT/'audit/regularization/written_scope.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'source/written_status.tex').write_text('\n'.join(tex)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='items'},indent=2))
