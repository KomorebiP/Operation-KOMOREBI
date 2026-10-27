#!/usr/bin/env python3
"""Rebuild the visual appendix in a temporary directory, then append the preserved paper.

Python 3.10+, SymPy, pypdf, PyMuPDF and a TeX installation with pdflatex are required.
No network access, Lean invocation, source edits, or modification of the original PDF.
The complete output and its audit are written to --output-dir.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'release_v1.2.1/paper/Projector_Resolved_Seed_Calculus_I.pdf'
# Zero-indexed pages of the preserved 40-page paper, checked against its printed statements.
SOURCE_PAGES = [5,5,12,10,7,23,16,17,19,18,20,9,11,12,28,28,25,25,26,32,10,33]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT.parent/'rebuilt')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    for protected in [ROOT, ROOT.parent/'release_v1.2.1']:
        if out == protected or protected in out.parents:
            raise SystemExit('Choose an output directory outside the preserved source directories.')
    try:
        import fitz
        import pypdf
        from pypdf import PdfReader, PdfWriter
        from pypdf.constants import PageLabelStyle
    except ImportError as exc:
        raise SystemExit(f'Missing Python dependency: {exc}. See visual_appendix/requirements.txt.') from exc
    tex = shutil.which('pdflatex')
    if not tex:
        raise SystemExit('pdflatex was not found. Install a TeX distribution with the packages listed in README.md.')
    if not BASE.is_file():
        raise SystemExit(f'Original manuscript is missing: {BASE}')
    out.mkdir(parents=True, exist_ok=True)
    logs = out/'build_logs'; logs.mkdir(exist_ok=True)
    before_sha = sha(BASE)
    env = os.environ.copy()
    env.setdefault('SOURCE_DATE_EPOCH', '1789171200')
    env.setdefault('FORCE_SOURCE_DATE', '1')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    commands = []
    with tempfile.TemporaryDirectory(prefix='paper_i_appendix_') as td:
        work = Path(td)
        shutil.copy2(ROOT/'appendix.tex', work/'appendix.tex')
        shutil.copytree(ROOT/'source', work/'source', ignore=shutil.ignore_patterns('__pycache__'))
        (work/'checks').mkdir(); (work/'build').mkdir()
        shutil.copy2(ROOT/'checks/verify_examples.py', work/'checks/verify_examples.py')
        def run(argv: list[str], logname: str) -> None:
            import time
            t = time.monotonic()
            with (logs/logname).open('w', encoding='utf8') as h:
                proc = subprocess.run(argv, cwd=work, env=env, stdout=h, stderr=subprocess.STDOUT, timeout=180)
            commands.append({'argv':argv, 'exit_code':proc.returncode, 'seconds':time.monotonic()-t, 'log':logname})
            if proc.returncode:
                raise RuntimeError(f'Build step failed ({proc.returncode}). See {logs/logname}.')
        run([sys.executable,'-W','error','checks/verify_examples.py'], 'exact_checks.log')
        run([sys.executable,'-W','error','source/generate_graphics.py'], 'generate_graphics.log')
        for i in (1,2):
            run([tex,'-interaction=nonstopmode','-halt-on-error','-output-directory=build','appendix.tex'], f'latex_pass_{i}.log')
        tex_log = (work/'build/appendix.log').read_text(errors='replace')
        errors = re.findall(r'Overfull \\[hv]box|Underfull \\[hv]box|undefined references|LaTeX Error|pdfTeX warning \(dest\)',tex_log)
        if errors:
            raise RuntimeError(f'Typesetting or reference audit failed: {errors}. See {logs}.')
        app = out/'Paper_I_Visual_Appendix.pdf'
        combined = out/'Paper_I_With_Visual_Appendix.pdf'
        shutil.copy2(work/'build/appendix.pdf', app)
        shutil.copy2(work/'build/appendix.log', logs/'appendix.log')
        shutil.copy2(work/'checks/EXACT_CHECKS.json', out/'EXACT_CHECKS.json')
        regenerated = {p.name:sha(p) for p in (work/'graphics').glob('*.tex')}
        shipped = {p.name:sha(p) for p in (ROOT/'graphics').glob('*.tex')}
        writer = PdfWriter()
        original_reader = PdfReader(BASE); appendix_reader = PdfReader(app)
        if (len(original_reader.pages),len(appendix_reader.pages)) != (40,22):
            raise RuntimeError('Expected 40 preserved manuscript pages and 22 appendix pages; check for layout spillovers.')
        writer.append(original_reader, outline_item='Paper I - preserved v1.2.1 manuscript')
        writer.append(appendix_reader, outline_item='Visual appendix - exact worked models')
        writer.set_page_label(0,39,style=PageLabelStyle.DECIMAL,start=1)
        writer.set_page_label(40,61,style=PageLabelStyle.DECIMAL,prefix='V-',start=1)
        writer.add_metadata({'/Title':'Paper I with Visual Appendix', '/Author':'Komorebi P.',
            '/Subject':'Preserved v1.2.1 manuscript followed by worked visual examples. Original formal contract unchanged.'})
        writer.page_mode = '/UseOutlines'
        with combined.open('wb') as h:
            writer.write(h)
        # Link each appendix source line back to its actual passage in the main paper.
        link_doc = fitz.open(combined)
        for i,target in enumerate(SOURCE_PAGES):
            page = link_doc[40+i]
            found = []
            for prefix in ('Reading source:', 'Main text:', 'Source release:'):
                found += page.search_for(prefix)
            if len(found) != 1:
                raise RuntimeError(f'Cannot uniquely locate source line on appendix page {i+1}.')
            r = found[0]
            page.insert_link({'kind':fitz.LINK_GOTO, 'from':fitz.Rect(57.6,r.y0,554.4,r.y1),
                              'page':target,'to':fitz.Point(0,0)})
        linked = out/'_linked.pdf'
        link_doc.save(linked); link_doc.close()
        linked.replace(combined)
        d0,d1,d2 = fitz.open(BASE),fitz.open(app),fitz.open(combined)
        checks=[]
        for kind,src,offset in [('original',d0,0),('appendix',d1,40)]:
            for i in range(len(src)):
                dst=d2[offset+i]
                a=src[i].get_pixmap(matrix=fitz.Matrix(.75,.75),alpha=False)
                b=dst.get_pixmap(matrix=fitz.Matrix(.75,.75),alpha=False)
                same_text=src[i].get_text()==dst.get_text()
                same_render=(a.width,a.height,a.samples)==(b.width,b.height,b.samples)
                if not (same_text and same_render):
                    raise RuntimeError(f'Page preservation failed: {kind} {i+1}')
                checks.append({'part':kind,'page':i+1,'same_text':same_text,'same_render_at_54_dpi':same_render})
        if [row[2] for row in d1.get_toc()] != list(range(1,23)):
            raise RuntimeError('Appendix bookmarks do not match the 22 intended pages.')
        page_checks=[]
        for i,page in enumerate(d1):
            words=len(page.get_text().split())
            outside=[]
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        if not span['text'].strip(): continue
                        x0,y0,x1,y1=span['bbox']
                        if x0<20 or x1>592 or y0<10 or y1>780:
                            outside.append(span['text'])
            images=len(page.get_images(full=True))
            if words<180 or outside or images:
                raise RuntimeError(f'Page geometry audit failed on V-{i+1}: {words}, {outside}, {images}')
            page_checks.append({'page':i+1,'word_count':words,'raster_image_objects':images,'outside_safe_bounds':outside})
        invalid=[]; links=0
        for i,page in enumerate(d2):
            for link in page.get_links():
                if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                    links+=1
                    if not 0<=link.get('page',-1)<len(d2): invalid.append(i+1)
                name=link.get('nameddest','')
                match=re.fullmatch(r'PIA\.visual(\d+)\.1',name)
                if match and link.get('page')!=39+int(match.group(1)):
                    invalid.append(i+1)
        if invalid: raise RuntimeError(f'Unresolved links on pages {invalid}')
        d0.close(); d1.close(); d2.close()
        if sha(BASE)!=before_sha: raise RuntimeError('Original manuscript changed unexpectedly.')
        exact=json.loads((out/'EXACT_CHECKS.json').read_text())
        report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Editorial appendix, exact example checks, PDF preservation and packaging. No Lean invocation.',
            'source_release':'Paper I v1.2.1; preserved certificate-explicit contract',
            'original_pages':40,'appendix_pages':22,'combined_pages':62,'vector_plates':len(regenerated),
            'exact_checks_passed':exact['check_count'],'regenerated_tikz_matches_shipped':regenerated==shipped,
            'source_line_links_added':22,'valid_internal_links':links,'invalid_internal_links':0,
            'latex_overfull_boxes':0,'latex_underfull_boxes':0,'latex_unresolved_references':0,
            'appendix_outline_entries':22,'all_appendix_graphics_vector':True,
            'source_pdf_sha256':before_sha,'appendix_pdf_sha256':sha(app),'combined_pdf_sha256':sha(combined),
            'python_version':platform.python_version(),'pymupdf_version':fitz.VersionBind,'pypdf_version':pypdf.__version__,
            'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],
            'source_date_epoch':env['SOURCE_DATE_EPOCH'],'commands':commands,
            'page_checks':page_checks,'preservation_checks':checks,
            'limits':['No fresh Lean verification. Inherited Lean records are retained unchanged.',
                      'Finite examples and bounded graph tests are not new universal proof certificates.',
                      'Preservation render comparison is at 54 dpi. Visual inspection is recorded separately.',
                      'Original diagrams remain in the preserved manuscript; new expository material is appended.']}
        (out/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f'PASS: 22-page appendix; 62-page combined paper; {exact["check_count"]} exact checks; all 62 pages preserved in assembly.')

if __name__=='__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit(f'Build failed: {exc}') from exc
