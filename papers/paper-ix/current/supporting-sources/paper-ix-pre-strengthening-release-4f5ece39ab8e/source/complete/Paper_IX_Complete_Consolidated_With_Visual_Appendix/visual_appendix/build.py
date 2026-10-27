#!/usr/bin/env python3
"""Build Paper IX's exact visual appendix and its preserved-manuscript reading edition.

Builds occur in a temporary directory. No network access or Lean invocation.
The supplied 48-page consolidated manuscript is never retypeset or edited here.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'original_snapshot/manuscript/consolidated/Paper_IX_Consolidated.pdf'
APPENDIX_PAGES=30
SOURCE_PAGES=[0,3,1,3,4,10,14,6,9,11,12,7,18,18,23,20,22,23,25,28,27,40,32,38,33,36,35,41,22,43]

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,default=ROOT.parent/'rebuilt');args=ap.parse_args();out=args.output_dir.resolve()
    for protected in [ROOT,ROOT.parent/'original_snapshot',ROOT.parent/'editorial_evidence',ROOT.parent/'reading_editions']:
        if out==protected or protected in out.parents:raise SystemExit('Output must be outside preserved source and evidence trees.')
    import fitz,pypdf
    from pypdf import PdfReader,PdfWriter
    from pypdf.constants import PageLabelStyle
    tex=shutil.which('pdflatex')
    if not tex:raise SystemExit('pdflatex is missing. See visual_appendix/README.md.')
    if not BASE.is_file():raise SystemExit('Missing preserved input: '+str(BASE))
    out.mkdir(parents=True,exist_ok=True);logs=out/'build_logs';logs.mkdir(exist_ok=True);before=sha(BASE);commands=[]
    env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1789171200',FORCE_SOURCE_DATE='1',PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='paper_ix_appendix_') as td:
        w=Path(td);shutil.copy2(ROOT/'appendix.tex',w/'appendix.tex');shutil.copytree(ROOT/'source',w/'source',ignore=shutil.ignore_patterns('__pycache__'))
        (w/'checks').mkdir();(w/'graphics').mkdir();(w/'build').mkdir();shutil.copy2(ROOT/'checks/verify_examples.py',w/'checks/verify_examples.py')
        def run(argv:list[str],log:str)->None:
            start=time.monotonic()
            with (logs/log).open('w') as h:p=subprocess.run(argv,cwd=w,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=180)
            commands.append({'argv':argv,'exit_code':p.returncode,'seconds':time.monotonic()-start,'log':log})
            if p.returncode:raise RuntimeError('Build failed: '+str(logs/log))
        run([sys.executable,'-W','error','checks/verify_examples.py'],'exact_checks.log')
        run([sys.executable,'-W','error','source/generate_graphics.py'],'generate_graphics.log')
        for j in [1,2]:run([tex,'-interaction=nonstopmode','-halt-on-error','-output-directory=build','appendix.tex'],f'latex_pass_{j}.log')
        tl=(w/'build/appendix.log').read_text(errors='replace');faults=re.findall(r'Overfull \\[hv]box|Underfull \\[hv]box|undefined references|LaTeX Error|pdfTeX warning \(dest\)|Missing character',tl)
        shutil.copy2(w/'build/appendix.log',logs/'appendix.log')
        app=out/'Paper_IX_Visual_Appendix.pdf';shutil.copy2(w/'build/appendix.pdf',app)
        if faults:raise RuntimeError('Typesetting warnings: '+str(faults)+'; PDF retained for inspection.')
        regenerated={p.name:sha(p) for p in (w/'graphics').glob('*.tex')};shipped={p.name:sha(p) for p in (ROOT/'graphics').glob('*.tex')}
        if regenerated!=shipped:raise RuntimeError('Regenerated TikZ differs from shipped source.')
        shutil.copy2(w/'checks/EXACT_CHECKS.json',out/'EXACT_CHECKS.json')
        d0,dA=fitz.open(BASE),fitz.open(app)
        if [len(d0),len(dA)]!=[48,APPENDIX_PAGES]:raise RuntimeError(f'Page count mismatch: {[len(d0),len(dA)]}')
        offset=48;combined=out/'Paper_IX_With_Visual_Appendix.pdf';writer=PdfWriter()
        writer.append(PdfReader(BASE),outline_item='Paper IX - preserved consolidated manuscript')
        writer.append(PdfReader(app),outline_item='Visual appendix - exact worked examples')
        writer.set_page_label(0,offset-1,style=PageLabelStyle.DECIMAL,start=1)
        writer.set_page_label(offset,offset+APPENDIX_PAGES-1,style=PageLabelStyle.DECIMAL,prefix='V-',start=1)
        writer.add_metadata({'/Author':'Komorebi P.','/Title':'Paper IX with Visual Appendix','/Subject':'Arithmetic packets, dyadic towers, and local polynomial deformation. New explanatory models; no new Lean certification.'});writer.page_mode='/UseOutlines'
        with combined.open('wb') as f:writer.write(f)
        d=fitz.open(combined)
        for j,target in enumerate(SOURCE_PAGES):
            page=d[offset+j];hits=page.search_for('Main text:')
            if len(hits)!=1:raise RuntimeError(f'Missing source link on V-{j+1}: {hits}')
            r=hits[0];page.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(56.69,r.y0,538.6,r.y1),'page':target,'to':fitz.Point(0,0)})
        temp=out/'_linked.pdf';d.save(temp);d.close();temp.replace(combined);d=fitz.open(combined)
        preservation=[]
        for label,src,off in [('original',d0,0),('appendix',dA,offset)]:
            for j,p in enumerate(src):
                q=d[off+j];pa=p.get_pixmap(alpha=False);pb=q.get_pixmap(alpha=False)
                tr=p.get_text()==q.get_text();rr=(pa.width,pa.height,pa.samples)==(pb.width,pb.height,pb.samples)
                if not(tr and rr):raise RuntimeError(f'Assembly changed {label} page {j+1}')
                preservation.append({'part':label,'page':j+1,'same_text':tr,'same_render_at_72_dpi':rr})
        if [x[2] for x in dA.get_toc()]!=list(range(1,APPENDIX_PAGES+1)):raise RuntimeError('Appendix bookmark/page mismatch')
        pages=[]
        for j,p in enumerate(dA):
            outside=[]
            for b in p.get_text('dict')['blocks']:
                for l in b.get('lines',[]):
                    for sp in l['spans']:
                        if not sp['text'].strip():continue
                        x0,y0,x1,y1=sp['bbox']
                        if x0<20 or x1>p.rect.width-20 or y0<10 or y1>p.rect.height-10:outside.append(sp['text'])
            words=len(p.get_text().split());images=len(p.get_images(full=True))
            if outside or images or words<160:raise RuntimeError(f'Page V-{j+1} geometry: {words} words, {images} raster, outside={outside}')
            pages.append({'page':j+1,'word_count':words,'raster_image_objects':images,'outside_safe_bounds':outside})
        invalid=[];nl=0
        for j,p in enumerate(d):
            for link in p.get_links():
                if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED):
                    nl+=1
                    if not 0<=link.get('page',-1)<len(d):invalid.append((j+1,str(link)))
                m=re.fullmatch(r'PIXA\.visual(\d+)\.1',link.get('nameddest',''))
                if m and link.get('page')!=offset-1+int(m[1]):invalid.append((j+1,'incorrect appendix destination'))
        if invalid:raise RuntimeError('Invalid combined links: '+str(invalid[:8]))
        for doc in [d0,dA,d]:doc.close()
        if sha(BASE)!=before:raise RuntimeError('Original source PDF changed')
        ex=json.loads((out/'EXACT_CHECKS.json').read_text())
        report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Editorial appendix, finite/symbolic example checks and PDF assembly. No Lean invocation.',
          'formal_source':'Paper IX consolidated proofread manuscript, 8 September 2026','original_pages':48,'appendix_pages':30,'combined_pages':78,
          'vector_plates':len(regenerated),'checks_passed':ex['checks_passed'],'negative_controls_rejected':ex['negative_controls_rejected'],'positive_case_evaluations':ex['positive_case_evaluations'],
          'all_appendix_graphics_vector':True,'source_line_links_added':30,'valid_internal_links':nl,'invalid_internal_links':0,
          'latex_overfull_boxes':0,'latex_underfull_boxes':0,'latex_unresolved_references':0,'regenerated_tikz_matches_shipped':True,
          'source_pdf_sha256':before,'appendix_pdf_sha256':sha(app),'combined_pdf_sha256':sha(combined),
          'python_version':platform.python_version(),'sympy_version':__import__('sympy').__version__,'pymupdf_version':fitz.VersionBind,'pypdf_version':pypdf.__version__,
          'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],'commands':commands,'page_checks':pages,'preservation_checks':preservation,
          'limits':['No fresh Lean verification or expanded formal contract.','Finite examples do not authenticate external statement correspondence or priority.','No missing historical experiment package has been reconstructed.','Original consolidated manuscript is preserved unchanged; its open questions remain open.']}
        (out/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: 30-page appendix; 78-page combined edition;',ex['checks_passed'],'checks')
if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError) as exc:raise SystemExit(str(exc)) from exc
