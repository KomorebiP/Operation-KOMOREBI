#!/usr/bin/env python3
"""Rebuild the exact appendix and append it without rewriting the main manuscript.
Requires Python 3.10+, SymPy, pypdf, PyMuPDF, and a TeX installation with pdflatex.
Does not run Lean, invoke network services, or modify the original formal release.
"""
from __future__ import annotations
import hashlib,json,platform,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import fitz
from pypdf import PdfReader,PdfWriter
from pypdf.constants import PageLabelStyle

ROOT=Path(__file__).resolve().parent
B=ROOT/'build';B.mkdir(exist_ok=True)
CHECKS=ROOT/'checks';CHECKS.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args,logname):
    log=B/logname
    with log.open('w',encoding='utf8') as h:
        p=subprocess.run(args,cwd=ROOT,stdout=h,stderr=subprocess.STDOUT,timeout=180)
    if p.returncode:raise RuntimeError(f'Command failed ({p.returncode}): {args!r}. See {log}.')

run([sys.executable,str(CHECKS/'verify_examples.py')],'exact_checks.stdout')
run([sys.executable,str(ROOT/'source/generate_graphics.py')],'graphics.stdout')
tex=shutil.which('pdflatex')
if tex is None:raise RuntimeError('pdflatex not found. Install a TeX distribution before rebuilding.')
for i in (1,2):
    run([tex,'-interaction=nonstopmode','-halt-on-error','-output-directory=build','appendix.tex'],f'latex_pass_{i}.stdout')
log=(B/'appendix.log').read_text(errors='replace')
if re.search(r'Overfull \\[hv]box|undefined references|LaTeX Error',log):
    raise RuntimeError('Layout or reference failure in build/appendix.log.')
app=ROOT/'Paper_XII_Visual_Appendix.pdf';shutil.copy2(B/'appendix.pdf',app)
base=ROOT/'original/Paper_XII_v0.17.0.pdf'
joined=ROOT/'Paper_XII_With_Visual_Appendix.pdf'
a=PdfReader(base);b=PdfReader(app)
assert len(a.pages)==36 and len(b.pages)==18,(len(a.pages),len(b.pages))
w=PdfWriter()
w.append(a,outline_item='Paper XII - original 36-page manuscript')
w.append(b,outline_item='Visual appendix - worked examples and reading guide')
w.set_page_label(0,35,style=PageLabelStyle.DECIMAL,start=1)
w.set_page_label(36,53,style=PageLabelStyle.DECIMAL,prefix='V-',start=1)
w.add_metadata({'/Title':'Paper XII with Visual Appendix', '/Author':'Komorebi P.',
    '/Subject':'Formal release v0.17.0 followed by an explanatory visual appendix; formal contract unchanged.'})
w.page_mode='/UseOutlines'
with joined.open('wb') as h:w.write(h)

# Check preservation of every page in both parts, including the rendered geometry.
d0,d1,d2=fitz.open(base),fitz.open(app),fitz.open(joined)
comparisons=[]
for kind,src,offset in [('original',d0,0),('appendix',d1,36)]:
    for j in range(len(src)):
        dst=d2[offset+j]
        equaltext=src[j].get_text()==dst.get_text()
        p=src[j].get_pixmap(matrix=fitz.Matrix(.75,.75),alpha=False)
        q=dst.get_pixmap(matrix=fitz.Matrix(.75,.75),alpha=False)
        equalpixels=(p.width,p.height,p.samples)==(q.width,q.height,q.samples)
        if not equaltext or not equalpixels:raise AssertionError((kind,j+1,equaltext,equalpixels))
        comparisons.append({'part':kind,'page':j+1,'same_text':equaltext,'same_render_at_54_dpi':equalpixels})
issues=[];page_checks=[]
for j,page in enumerate(d1):
    txt=page.get_text()
    if len(txt.split())<120:issues.append(f'Possible spill/empty page {j+1}')
    outside=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for s in line['spans']:
                if not s['text'].strip():continue
                x0,y0,x1,y1=s['bbox']
                if x0<20 or x1>592 or y0<10 or y1>780:outside.append(s['text'])
    if outside:issues.append({'page':j+1,'out_of_bounds':outside})
    page_checks.append({'page':j+1,'word_count':len(txt.split()),'raster_image_objects':len(page.get_images()),
                        'outside_page_safe_bounds':outside})
assert not issues,issues
assert all(x['raster_image_objects']==0 for x in page_checks)
link_issues=[]
for j,page in enumerate(d2):
    for ln in page.get_links():
        if ln['kind']==fitz.LINK_GOTO and not (0<=ln.get('page',-1)<len(d2)):
            link_issues.append({'page':j+1,'link':ln})
assert not link_issues,link_issues
exact=json.loads((CHECKS/'EXACT_CHECKS.json').read_text())
report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'Editorial visual appendix. No new Lean verification or theorem claims.',
    'appendix_pages':18,'original_pages':36,'combined_pages':54,'exact_checks_passed':exact['check_count'],
    'all_appendix_graphics_vector':True,'all_original_pages_preserved_text_and_render':True,
    'all_appendix_pages_preserved_in_combined_file':True,'invalid_internal_links':0,
    'latex_overfull_boxes':0,'latex_unresolved_references':0,
    'latex_underfull_box_warnings':len(re.findall(r'Underfull \\[hv]box',log)),
    'python_version':platform.python_version(),'pymupdf_version':fitz.VersionBind,
    'source_pdf_sha256':sha(base),'appendix_pdf_sha256':sha(app),'combined_pdf_sha256':sha(joined),
    'page_checks':page_checks,'preservation_checks':comparisons,
    'limits':['The original formal claims are inherited, not reverified.',
              'Exact example checks do not certify arbitrary arithmetic inputs.',
              'Coordinate sketches explicitly show real closed points, not entire spectra.',
              'PDF rendering comparison uses 54 dpi; final visual inspection uses 140 dpi Poppler output.']}
(CHECKS/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: appendix 18 pages; combined paper 54 pages; 31 exact checks; all original pages preserved.')
