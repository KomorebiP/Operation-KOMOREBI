#!/usr/bin/env python3
"""Compare two complete guide builds without changing either PDF."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import fitz

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('first',type=Path)
parser.add_argument('second',type=Path)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--render-dir',type=Path)
args=parser.parse_args()
name='Paper_XII_Visual_Guide_Final.pdf'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a,b=args.first/name,args.second/name
assert sha(a)==sha(b), 'PDF bytes differ'
d,e=fitz.open(a),fitz.open(b)
assert len(d)==len(e)
pages=[]
links=[]
if args.render_dir:
    args.render_dir.mkdir(parents=True,exist_ok=True)
for n,(p,q) in enumerate(zip(d,e),1):
    assert p.get_text()==q.get_text(), ('text',n)
    r,s=p.get_pixmap(dpi=140),q.get_pixmap(dpi=140)
    assert (r.width,r.height,r.samples)==(s.width,s.height,s.samples), ('render',n)
    outside=[]
    for shape in p.get_drawings():
        z=shape['rect']
        if z.x0<-.5 or z.y0<-.5 or z.x1>p.rect.width+.5 or z.y1>p.rect.height+.5:
            outside.append(list(z))
    assert not outside, ('drawing bounds',n,outside)
    for link in p.get_links():
        if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED) and 'page' in link:
            assert 0<=link.get('page',-1)<len(d), ('internal link',n)
            links.append({'page':n,'destination':link['page']+1})
    if args.render_dir:
        r.save(str(args.render_dir/f'page_{n:02}.png'))
    pages.append({'page':n,'same_text':True,'same_140dpi_pixels':True,
                  'out_of_page_vector_rectangles':0})
figures=[]
for p in sorted((args.first/'graphics').glob('*')):
    if p.suffix not in {'.tex','.pdf'}:
        continue
    assert sha(p)==sha(args.second/'graphics'/p.name), ('figure bytes',p.name)
    if p.suffix=='.pdf':
        vector=fitz.open(p)
        assert all(not page.get_images() for page in vector), ('figure raster',p.name)
    figures.append({'file':p.name,'byte_identical':True,'sha256':sha(p)})
report={'status':'PASS','date':'2026-10-06',
        'comparison':'Two builds from frozen source into distinct directories',
        'pdf_byte_identical':True,'page_count':len(d),'pdf_sha256':sha(a),
        'same_all_page_text':True,'same_all_140dpi_page_renders':True,
        'vector_figure_files_identical':len(figures),'page_checks':pages,
        'figure_checks':figures,'valid_internal_links':len(links),
        'scope':'Reproducibility/document checks; no new Lean proof certificate.'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(d)} identical pages; {len(figures)} identical vector files; {len(links)} valid links.')
