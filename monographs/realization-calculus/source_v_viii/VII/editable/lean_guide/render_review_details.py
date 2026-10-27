#!/usr/bin/env python3
"""Render representative dense guide pages at 120 dpi for visual review."""
from pathlib import Path
import hashlib,json,re
import fitz
H=Path(__file__).resolve().parent;Q=H/'qa';Q.mkdir(exist_ok=True)
PDF=H/'Paper_VII_Lean_Guide_Final.pdf';doc=fitz.open(PDF)
texts=[re.sub(r'\s+','',''.join(p.get_text())) for p in doc]
cues=['All19finiteitemsinthetraditionalcore','Strengthenedstatementsandtheendpointboundary','span_orbit_dimension','product_length_minimum','transported_derivative','smooth_range_bundle_atlas','local_connections_gauge','recovery_corrects','recovery_with_reference','projected_resolvent','Theactualcurrentfinitecomputations','Allnamedtheoremdeclarations','Pinnedcompileranddependencyrevisions','Exactexcerptregister']
rows=[{'cue':'cover','physical_page':1}]
for cue in cues:
    matches=[i+1 for i,text in enumerate(texts) if cue in text]
    if not matches:raise RuntimeError('Review cue not found: '+cue)
    # The contents only has section titles, so choose the first body occurrence.
    page=matches[0]
    if cue in ('Allnamedtheoremdeclarations','Exactexcerptregister') and len(matches)>1:page=matches[1]
    rows.append({'cue':cue,'physical_page':page})
rows.append({'cue':'last excerpt records','physical_page':len(doc)})
for stale in Q.glob('detail_*.png'):stale.unlink()
for page in sorted({r['physical_page'] for r in rows}):
    doc[page-1].get_pixmap(matrix=fitz.Matrix(120/72,120/72),alpha=False).save(Q/f'detail_{page:03d}.png')
result={'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'pages':len(doc),'detail_dpi':120,'selected_physical_pages':sorted({r['physical_page'] for r in rows}),'selection':rows}
(Q/'detail_selection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
