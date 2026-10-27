#!/usr/bin/env python3
"""Build the separate Paper IX visual guide, using exact standard-library models.

No network access, package installation, Lean invocation, or SymPy requirement.
All work happens in an isolated temporary directory. The original plates are
regenerated and compared against the delivered editable vector sources.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NAME='Paper_IX_Visual_Guide_Final'
EPOCH='1791244800'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'rebuilt')
    args=ap.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    tex=shutil.which('pdflatex')
    if not tex:raise SystemExit('pdflatex is required; no dependency is installed by this builder.')
    env=os.environ.copy();env.update(SOURCE_DATE_EPOCH=EPOCH,FORCE_SOURCE_DATE='1',PYTHONDONTWRITEBYTECODE='1')
    logs=out/'build_logs';logs.mkdir(exist_ok=True);commands=[]
    with tempfile.TemporaryDirectory(prefix='paper_ix_visual_') as td:
        work=Path(td)
        shutil.copy2(ROOT/'appendix.tex',work/'appendix.tex')
        for name in ['source','graphics','checks']:
            shutil.copytree(ROOT/name,work/name,ignore=shutil.ignore_patterns('__pycache__'))
        (work/'build').mkdir()
        def run(argv,name):
            start=time.monotonic()
            with (logs/name).open('w') as stream:
                proc=subprocess.run(argv,cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
            commands.append({'argv':argv,'exit_code':proc.returncode,'seconds':time.monotonic()-start,'log':name})
            if proc.returncode:raise RuntimeError('Build failed; inspect '+str(logs/name))
        run([sys.executable,'-W','error','checks/verify_examples_exact.py'],'fresh_exact_checks.log')
        run([sys.executable,'-W','error','source/generate_graphics.py'],'generate_original_plates.log')
        run([sys.executable,'-W','error','source/generate_new_graphics.py'],'generate_new_plates.log')
        regenerated={p.name:sha(p) for p in (work/'graphics').glob('*.tex')}
        shipped={p.name:sha(p) for p in (ROOT/'graphics').glob('*.tex')}
        if regenerated!=shipped:raise RuntimeError('Regenerated plates differ from delivered editable sources.')
        for passnum in [1,2]:
            run([tex,'-interaction=nonstopmode','-halt-on-error','-jobname='+NAME,'-output-directory=build','appendix.tex'],f'latex_pass_{passnum}.log')
        log=(work/'build'/f'{NAME}.log').read_text(errors='replace')
        faults=re.findall(r'Overfull \\[hv]box|undefined references|LaTeX Error|pdfTeX warning \(dest\)|Missing character',log)
        shutil.copy2(work/'build'/f'{NAME}.log',logs/f'{NAME}.log')
        shutil.copy2(work/'build'/f'{NAME}.aux',out/f'{NAME}.aux')
        dest=out/f'{NAME}.pdf';shutil.copy2(work/'build'/f'{NAME}.pdf',dest)
        if faults:raise RuntimeError('Typesetting faults: '+str(faults)+'; PDF retained for inspection.')
        shutil.copy2(work/'checks/FRESH_EXACT_CHECKS.json',out/'FRESH_EXACT_CHECKS.json')
        import fitz
        doc=fitz.open(dest);pages=[]
        if len(doc)!=34:raise RuntimeError(f'Expected 34 guide pages, observed {len(doc)}.')
        crosswalk_path=ROOT/'QA/FINAL_PAGE_CROSSWALK.json'
        if not crosswalk_path.is_file():raise RuntimeError('Missing final traditional locator crosswalk: '+str(crosswalk_path))
        crosswalk=json.loads(crosswalk_path.read_text())
        remote_links=0
        for number,page in enumerate(doc,1):
            outside=[]
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        if not span['text'].strip():continue
                        x0,y0,x1,y1=span['bbox']
                        if x0<20 or x1>page.rect.width-20 or y0<10 or y1>page.rect.height-10:outside.append(span['text'])
            if outside or page.get_images():raise RuntimeError(f'Page {number} fails safe geometry or contains raster images: {outside}')
            links=page.get_links()
            for link in links:
                if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
                    if not 0<=link.get('page',-1)<len(doc):raise RuntimeError('Invalid internal guide page link.')
            if crosswalk:
                requested=crosswalk['pages'][number-1]
                expected=[(x['relative_pdf_file'],x['pdf_zero_based_link_page']) for x in requested['traditional_targets']]
                actual=[(x.get('file'),x.get('page')) for x in links if x.get('file')=='Paper_IX_Traditional_Final.pdf']
                if expected!=actual:raise RuntimeError(f'Final traditional page links mismatch on guide page {number}.')
                remote_links+=len(actual)
            pages.append({'page':number,'words':len(page.get_text().split()),'raster_image_objects':0,'outside_safe_bounds':[]})
        marks=doc.get_toc()
        if [m[2] for m in marks]!=list(range(1,35)):raise RuntimeError('Guide page/bookmark mismatch.')
        doc.close()
        report={'status':'PASS','scope':'Separate visual guide build and PDF geometry; no Lean or historical SymPy replay.',
                'pages':34,'original_worked_pages':30,'additional_worked_pages':4,'original_vector_plates':28,'additional_vector_plates':4,
                'all_plates_regenerate_byte_identically':True,'pdf_sha256':sha(dest),'source_date_epoch':int(EPOCH),
                'python_version':platform.python_version(),'pymupdf_version':fitz.VersionBind,
                'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],
                'typesetting_faults':faults,'underfull_boxes':len(re.findall(r'Underfull \\[hv]box',log)),
                'remote_traditional_page_links_checked':remote_links,'crosswalk_present':crosswalk is not None,
                'commands':commands,'page_checks':pages}
        (out/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'status':'PASS','pages':34,'vector_plates':32,'pdf_sha256':report['pdf_sha256']},indent=2))

if __name__=='__main__':main()
