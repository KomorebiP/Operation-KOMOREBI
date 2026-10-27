#!/usr/bin/env python3
"""Build the appendix in isolation and append the unchanged Paper VI PDF.

Requires Python 3.10+, SymPy, mpmath, PyMuPDF, pypdf, and pdflatex with the listed
LaTeX packages. No network, source mutation, or Lean invocation is performed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, re, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'original_snapshot/manuscript/Paper_VI_Reviewed.pdf'
ORIGINAL_PAGES=34
APPENDIX_PAGES=28
# Zero-based pages; each source line is linked to a relevant original passage.
SOURCE_PAGES=[3,7,3,4,8,8,8,9,11,12,13,16,17,16,18,19,18,21,22,23,24,25,25,26,28,17,20,33]

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT.parent/'rebuilt')
    args=parser.parse_args();out=args.output_dir.resolve()
    for protected in (ROOT,ROOT.parent/'original_snapshot'):
        if out==protected or protected in out.parents:
            raise SystemExit('Use an output directory outside the preserved source trees.')
    try:
        import fitz,pypdf
        from pypdf import PdfReader,PdfWriter
        from pypdf.constants import PageLabelStyle
    except ImportError as exc:
        raise SystemExit(f'Missing dependency: {exc}. See visual_appendix/requirements.txt.') from exc
    tex=shutil.which('pdflatex')
    if not tex: raise SystemExit('pdflatex was not found; see visual_appendix/README.md.')
    if not BASE.is_file(): raise SystemExit(f'Preserved manuscript is missing: {BASE}')
    out.mkdir(parents=True,exist_ok=True);logs=out/'build_logs';logs.mkdir(exist_ok=True)
    before=sha(BASE);commands=[]
    env=os.environ.copy();env.setdefault('SOURCE_DATE_EPOCH','1789171200');env.setdefault('FORCE_SOURCE_DATE','1')
    env['PYTHONDONTWRITEBYTECODE']='1'
    with tempfile.TemporaryDirectory(prefix='paper_vi_appendix_') as td:
        work=Path(td)
        shutil.copy2(ROOT/'appendix.tex',work/'appendix.tex')
        shutil.copytree(ROOT/'source',work/'source',ignore=shutil.ignore_patterns('__pycache__'))
        (work/'checks').mkdir();(work/'build').mkdir()
        shutil.copy2(ROOT/'checks/verify_examples.py',work/'checks/verify_examples.py')
        def run(argv:list[str],logname:str)->None:
            t=time.monotonic()
            with (logs/logname).open('w',encoding='utf8') as h:
                p=subprocess.run(argv,cwd=work,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=180)
            commands.append({'argv':argv,'exit_code':p.returncode,'seconds':time.monotonic()-t,'log':logname})
            if p.returncode: raise RuntimeError(f'Build step failed. See {logs/logname}')
        run([sys.executable,'-W','error','checks/verify_examples.py'],'exact_checks.log')
        run([sys.executable,'-W','error','source/generate_graphics.py'],'generate_graphics.log')
        for i in (1,2):
            run([tex,'-interaction=nonstopmode','-halt-on-error','-output-directory=build','appendix.tex'],f'latex_pass_{i}.log')
        tex_log=(work/'build/appendix.log').read_text(errors='replace')
        faults=re.findall(r'Overfull \\[hv]box|Underfull \\[hv]box|undefined references|LaTeX Error|pdfTeX warning \(dest\)',tex_log)
        if faults: raise RuntimeError(f'Typesetting audit failed: {faults}. See {logs}')
        app=out/'Paper_VI_Visual_Appendix.pdf';combined=out/'Paper_VI_With_Visual_Appendix.pdf'
        shutil.copy2(work/'build/appendix.pdf',app)
        shutil.copy2(work/'build/appendix.log',logs/'appendix.log')
        shutil.copy2(work/'checks/EXACT_CHECKS.json',out/'EXACT_CHECKS.json')
        regenerated={p.name:sha(p) for p in sorted((work/'graphics').glob('*.tex'))}
        shipped={p.name:sha(p) for p in sorted((ROOT/'graphics').glob('*.tex'))}
        if regenerated!=shipped: raise RuntimeError('Regenerated vector plates differ from shipped sources.')
        writer=PdfWriter();a=PdfReader(BASE);b=PdfReader(app)
        if (len(a.pages),len(b.pages))!=(ORIGINAL_PAGES,APPENDIX_PAGES):
            raise RuntimeError(f'Expected 34 + 28 pages; got {len(a.pages)} + {len(b.pages)}. Check for layout spillover.')
        writer.append(a,outline_item='Paper VI - preserved v0.5.0 manuscript')
        writer.append(b,outline_item='Visual appendix - exact worked models')
        writer.set_page_label(0,ORIGINAL_PAGES-1,style=PageLabelStyle.DECIMAL,start=1)
        writer.set_page_label(ORIGINAL_PAGES,ORIGINAL_PAGES+APPENDIX_PAGES-1,style=PageLabelStyle.DECIMAL,prefix='V-',start=1)
        writer.add_metadata({'/Title':'Paper VI with Visual Appendix','/Author':'Komorebi P.',
            '/Subject':'Preserved v0.5.0 paper plus exact worked visual models. Formal contract unchanged.'})
        writer.page_mode='/UseOutlines'
        with combined.open('wb') as h: writer.write(h)
        linkdoc=fitz.open(combined)
        for i,target in enumerate(SOURCE_PAGES):
            page=linkdoc[ORIGINAL_PAGES+i];found=[]
            for prefix in ('Reading source:','Main text:','Source release:'): found+=page.search_for(prefix)
            if len(found)!=1: raise RuntimeError(f'Cannot locate unique source line on V-{i+1}')
            r=found[0]
            page.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(57.6,r.y0,554.4,r.y1),
                              'page':target,'to':fitz.Point(0,0)})
        temp=out/'_linked.pdf';linkdoc.save(temp);linkdoc.close();temp.replace(combined)
        d0,d1,d2=fitz.open(BASE),fitz.open(app),fitz.open(combined)
        preservation=[]
        for label,src,offset in [('original',d0,0),('appendix',d1,ORIGINAL_PAGES)]:
            for i in range(len(src)):
                a=src[i];b=d2[offset+i]
                pa=a.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pb=b.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
                text_equal=a.get_text()==b.get_text()
                render_equal=(pa.width,pa.height,pa.samples)==(pb.width,pb.height,pb.samples)
                if not (text_equal and render_equal): raise RuntimeError(f'Assembly altered {label} page {i+1}')
                preservation.append({'part':label,'page':i+1,'same_text':text_equal,'same_render_at_72_dpi':render_equal})
        if [v[2] for v in d1.get_toc()]!=list(range(1,APPENDIX_PAGES+1)):
            raise RuntimeError('Appendix bookmarks no longer correspond to their intended pages.')
        pages=[]
        for i,page in enumerate(d1):
            outside=[]
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        if not span['text'].strip():continue
                        x0,y0,x1,y1=span['bbox']
                        if x0<20 or x1>592 or y0<10 or y1>780:outside.append(span['text'])
            words=len(page.get_text().split());images=len(page.get_images(full=True))
            if outside or images or words<180:
                raise RuntimeError(f'Page geometry failed on V-{i+1}: words={words}, raster={images}, outside={outside}')
            pages.append({'page':i+1,'word_count':words,'raster_image_objects':images,'outside_safe_bounds':outside})
        invalid=[];nlinks=0
        for i,page in enumerate(d2):
            for link in page.get_links():
                if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
                    nlinks+=1
                    if not 0<=link.get('page',-1)<len(d2):invalid.append({'page':i+1,'link':str(link)})
                name=link.get('nameddest','');match=re.fullmatch(r'PVIA\.visual(\d+)\.1',name)
                if match and link.get('page')!=ORIGINAL_PAGES-1+int(match.group(1)):
                    invalid.append({'page':i+1,'wrong_appendix_target':name})
        if invalid:raise RuntimeError(f'Invalid combined links: {invalid}')
        d0.close();d1.close();d2.close()
        if sha(BASE)!=before:raise RuntimeError('The preserved PDF changed.')
        exact=json.loads((out/'EXACT_CHECKS.json').read_text())
        report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Editorial appendix construction, exact examples, and PDF assembly. No Lean invocation.',
            'source_release':'Paper VI v0.5.0 Checked Fifth Block; finite transfer and probabilistic contract unchanged',
            'original_pages':ORIGINAL_PAGES,'appendix_pages':APPENDIX_PAGES,'combined_pages':ORIGINAL_PAGES+APPENDIX_PAGES,
            'vector_plates':len(regenerated),'exact_checks_passed':exact['checks_passed'],'negative_controls_rejected':len(exact['invalid_controls_rejected']),
            'regenerated_tikz_matches_shipped':True,'source_line_links_added':APPENDIX_PAGES,
            'valid_internal_links':nlinks,'invalid_internal_links':0,'latex_overfull_boxes':0,'latex_underfull_boxes':0,
            'latex_unresolved_references':0,'all_appendix_graphics_vector':True,
            'source_pdf_sha256':before,'appendix_pdf_sha256':sha(app),'combined_pdf_sha256':sha(combined),
            'python_version':platform.python_version(),'pymupdf_version':fitz.VersionBind,'pypdf_version':pypdf.__version__,
            'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],
            'source_date_epoch':env['SOURCE_DATE_EPOCH'],'commands':commands,'page_checks':pages,'preservation_checks':preservation,
            'limits':['No fresh Lean verification. Inherited records are preserved separately.',
                      'Exact finite examples do not settle the three open continuum/refinement/latent realization questions.',
                      'Assembly render comparison is at 72 dpi; visual review is recorded separately.',
                      'All 34 original manuscript pages remain unchanged, including the inherited evidence boundary.']}
        (out/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f'PASS: {APPENDIX_PAGES}-page appendix, {ORIGINAL_PAGES+APPENDIX_PAGES}-page combined paper, {exact["checks_passed"]} exact checks.')

if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError) as exc:raise SystemExit(f'Build failed: {exc}') from exc
