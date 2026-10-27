#!/usr/bin/env python3
"""Create a bounded design tour with the full book's printed folios."""
from pathlib import Path
import json,hashlib
import fitz
ROOT=Path(__file__).resolve().parent
spec=json.loads((ROOT/'book/build_spec.json').read_text())
source=fitz.open(ROOT/'output/Komorebi_Core_Papers.pdf')
selected=[0,5]
for part in spec['parts']:
    selected.append(part['divider_index'])
    comp=part['components'][0]
    # Choose a substantive interior page, not another treatment cover.
    local=min(comp['pages']-1,max(3,min(12,comp['pages']//4)))
    selected.append(comp['index_start']+local)
for paper,role in [('IV','visual'),('XI','research_atlas')]:
    part=next(p for p in spec['parts'] if p['paper']==paper)
    matches=[c for c in part['components'] if c['role']==role]
    if not matches and paper=='XI':matches=[part['components'][-1]]
    c=matches[0];selected.append(c['index_start']+min(5,c['pages']-1))
selected=list(dict.fromkeys(selected))
preview=fitz.open()
for i in selected:preview.insert_pdf(source,from_page=i,to_page=i,links=False,annots=False)
preview.set_metadata({'title':'Komorebi Core Papers: Design Preview','author':'Komorebi P.',
                      'subject':'Selected pages; printed folios belong to the complete collected edition',
                      'creator':'Komorebi core monograph publication source'})
preview.set_toc([[1,'Book page '+str(p+1)+' / '+source[p].get_label(),i+1] for i,p in enumerate(selected)])
out=ROOT/'output/Komorebi_Core_Papers_Design_Preview.pdf'
preview.save(out,garbage=3,deflate=True)
report={'pages':len(preview),'source_book_pages':[p+1 for p in selected],
        'source_sha256':hashlib.file_digest((ROOT/'output/Komorebi_Core_Papers.pdf').open('rb'),'sha256').hexdigest(),
        'preview_sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),
        'note':'A selected-page design tour, not a shortened mathematical edition. Source links omitted in preview.'}
(ROOT/'book/preview_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
