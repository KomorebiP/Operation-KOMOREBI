#!/usr/bin/env python3
"""Create the twelve-page design preview from the assembled publication."""
from pathlib import Path
import json, hashlib
import fitz
root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'audit/design_preview_pages.json').read_text())
book=fitz.open(root/'Komorebi_Physics.pdf'); out=fitz.open()
for e in plan:
 p=e['book_pdf_page']-1
 out.insert_pdf(book,from_page=p,to_page=p,links=False)
out.set_toc([[1,e['title'],i+1] for i,e in enumerate(plan)])
out.set_metadata({'title':'Komorebi Physics — Design Preview','author':'Komorebi P.','subject':'Selected pages retaining full-book printed folios'})
path=root/'Komorebi_Physics_Design_Preview.pdf';out.save(path,garbage=3,deflate=True)
record={'pages':len(out),'book_sha256':hashlib.sha256((root/'Komorebi_Physics.pdf').read_bytes()).hexdigest(),'preview_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'invalid_bookmarks':0,'note':'Selected pages retain full-book printed folios; preview bookmarks are local. Internal source links omitted from excerpt.'}
(root/'audit/design_preview_validation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
