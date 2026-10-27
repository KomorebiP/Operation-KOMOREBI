#!/usr/bin/env python3
"""Compare all current component link destinations and page labels after merging."""
from pathlib import Path
import fitz,json
ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'evidence/INTEGRATED_READER_LAYOUT.json').read_text())
merged=fitz.open(ROOT/'publication/Paper_III_Complete_Reading_Edition_v1.0.0.pdf')
errors=[];checked=0;labels=0;defaults=0
for part in layout['parts']:
 doc=fitz.open(ROOT/part['source']);offset=part['start_page']-1;names=doc.resolve_names()
 has_labels=bool(doc.get_page_labels())
 for i,page in enumerate(doc):
  target=merged[offset+i]
  expected_label=page.get_label() if has_labels else str(i+1)
  if target.get_label()!=expected_label:errors.append({'page_label':part['name'],'page':i+1})
  labels+=1;defaults+=not has_labels
  source_links=page.get_links();target_links=target.get_links()
  if len(source_links)!=len(target_links):errors.append({'page_link_count':part['name'],'page':i+1});continue
  for a,b in zip(source_links,target_links):
   checked+=1
   if max(abs(x-y) for x,y in zip(a['from'],b['from']))>.002:errors.append({'hotspot':part['name'],'page':i+1})
   if a['kind']==fitz.LINK_NAMED:
    dest=names[a['nameddest']];point=fitz.Point(dest['to'])*doc[dest['page']].transformation_matrix
    if b['page']!=offset+dest['page'] or abs(b['to']-point)>.002:errors.append({'destination':part['name'],'page':i+1,'name':a['nameddest']})
   elif a['kind']==fitz.LINK_GOTO:
    if b['page']!=offset+a['page'] or abs(b['to']-a['to'])>.002:errors.append({'destination':part['name'],'page':i+1})
   elif a.get('uri')!=b.get('uri'):errors.append({'uri':part['name'],'page':i+1})
record={'status':'PASS' if not errors else 'FAIL','exact_destinations_checked':checked,'page_labels_checked':labels,'default_numbered_pages':defaults,'errors':errors,'tolerance_points':.002,'scope':'Every hotspot and resolved destination checked against its component offset and coordinate transform. Explicit component labels are preserved. Components without a PageLabels dictionary receive their ordinary one-based printed numbers.'}
(ROOT/'evidence/qa/PDF_NAVIGATION_QA.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
if errors:raise SystemExit(1)
