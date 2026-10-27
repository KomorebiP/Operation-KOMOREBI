#!/usr/bin/env python3
"""Match final rendered bodies to reviewed predecessors; manual review is separate."""
from pathlib import Path
import fitz, hashlib, json

root=Path(__file__).resolve().parents[1]
old=root.parent/'monograph_v1.9.0/publication/Komorebi_Space_Monograph.pdf'
draft=root/'audit/draft_001/document.pdf'
layout=root/'audit/layout_002/document.pdf'
candidate1=root/'audit/final_candidate_001/document.pdf'
new=root/'publication/Komorebi_Space_Monograph.pdf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def body(p):
    return hashlib.sha256(p.get_pixmap(matrix=fitz.Matrix(1.4,1.4),
        clip=fitz.Rect(0,0,p.rect.width,738),alpha=False).samples).hexdigest()
known={}
sources=[]
for path,allowed in [(old,None),(draft,{1,2,5,101,102,107,108,110,142,151,154,156,157}),(layout,None),(candidate1,None)]:
    doc=fitz.open(path)
    sources.append({'path':str(path.resolve()),'sha256':sha(path),'reviewed_pages':'all' if allowed is None else sorted(allowed)})
    for i,p in enumerate(doc,1):
        if allowed is None or i in allowed:
            known[body(p)]={'source':str(path.resolve()),'page':i}
doc=fitz.open(new)
matches=[]
changed=[]
footer_issues=[]
for i,p in enumerate(doc,1):
    h=body(p)
    if h in known: matches.append({'final_page':i,'body_sha256':h,'reviewed_source':known[h]['source'],'reviewed_page':known[h]['page']})
    else: changed.append(i)
    if i>1:
        expected={2:'i',3:'ii',4:'iii',5:'iv'}.get(i,str(i-5))
        footer=[w[4] for w in p.get_text('words') if w[1]>=738 and w[0]>500]
        if footer != [expected]:footer_issues.append({'page':i,'expected':expected,'observed':footer})
out={'final_pdf_sha256':sha(new),'page_count':len(doc),'body_clip_pdf_points':[0,0,612,738],
     'comparison_sources':sources,'unchanged_body_matches':matches,'pages_needing_visual_review':changed,
     'footer_numbering_issues':footer_issues}
(root/'audit/FINAL_PAGE_MATCH.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'pages':len(doc),'matched':len(matches),'changed':changed,'footer_issues':footer_issues}))
