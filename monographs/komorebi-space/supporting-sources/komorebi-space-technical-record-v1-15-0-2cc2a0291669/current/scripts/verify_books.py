"""Check final PDF structure, final TeX diagnostics, and render every page."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import fitz

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--build', required=True)
args=parser.parse_args()
build=ROOT/'build'/args.build
out=ROOT/'build'/('review_'+args.build)
out.mkdir(parents=True,exist_ok=False)
books={'monograph':'Monograph','lean':'Lean_Guide','visual':'Visual_Guide'}
results={}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for key,stem in books.items():
    pdf=build/key/f'Komorebi_Space_{stem}.pdf'
    parent=ROOT.parent/'publication_v114/publication/books'/f'Komorebi_Space_{stem}_v1.14.0.pdf'
    doc,old=fitz.open(pdf),fitz.open(parent)
    same,changed,badlinks,outside=[],[],[],[]
    for i,page in enumerate(doc):
        for link in page.get_links():
            if link.get('kind')==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(doc):
                badlinks.append({'page':i+1,'link':str(link)})
        for block in page.get_text('blocks'):
            r=fitz.Rect(block[:4])
            if r.x0 < -0.5 or r.y0 < -0.5 or r.x1 > page.rect.width+0.5 or r.y1 > page.rect.height+0.5:
                outside.append({'page':i+1,'rect':list(r)})
        if i<len(old) and page.rect==old[i].rect and page.get_pixmap(dpi=72).samples==old[i].get_pixmap(dpi=72).samples:
            same.append(i+1)
        else: changed.append(i+1)
    (out/f'{key}_text.txt').write_text('\n\f\n'.join(p.get_text() for p in doc))
    log=build/key/f'Komorebi_Space_{stem}.log'
    lines=log.read_text(errors='replace').splitlines()
    findings,underfull,allowed=[],[],[]
    for i,line in enumerate(lines):
        if 'Underfull' in line: underfull.append(line)
        if line=='Package hyperref Warning: Token not allowed in a PDF string (Unicode):' and i+2<len(lines):
            detail='\n'.join(lines[i:i+3])
            if '\\hskip 10.95pt' in detail and 'replaced by space on input line' in detail:
                allowed.append(detail);continue
        if re.search(r'Overfull|undefined|multiply defined|Missing character|LaTeX Warning|Package .* Warning',line):
            findings.append(line)
    dest=out/key;dest.mkdir()
    cmd=['pdftoppm','-r','90','-png',str(pdf),str(dest/'page')]
    run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (dest/'render.log').write_bytes(run.stdout)
    assert run.returncode==0
    assert len(list(dest.glob('page-*.png')))==len(doc)
    results[key]={'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':len(doc),'parent_pages':len(old),
        'parent_sha256':sha(parent),'raster_comparison_dpi':72,'unchanged_pages':same,'changed_or_new_pages':changed,
        'invalid_internal_links':badlinks,'off_page_text':outside,'final_latex_findings':findings,
        'underfull_notices':underfull,'accepted_bookmark_spacing_notices':allowed,'metadata':doc.metadata,
        'render_command':cmd,'render_exit_code':run.returncode,'rendered_pages':len(doc)}
    print(key,len(doc),'pages;',len(changed),'changed;',len(findings),'findings',flush=True)
(out/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(not r['invalid_internal_links'] and not r['off_page_text'] and not r['final_latex_findings'] for r in results.values())
print('PASS structural checks; changed-page visual inspection remains separate.')
