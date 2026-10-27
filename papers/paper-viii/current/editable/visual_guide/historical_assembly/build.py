#!/usr/bin/env python3
"""Deterministic isolated standalone build; no dependency installation or Lean.

Retains the historical SymPy model/checker and original editable vector plates.
Runs the independent exact standard-library checks and regenerates only four
new plates, then typesets twice in a clean temporary directory.
"""
from pathlib import Path
import hashlib,json,os,platform,re,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def spans(s):return re.findall(r'\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)',s,re.S)
def main():
    import fitz
    tex=shutil.which('pdflatex')
    if not tex:raise SystemExit('pdflatex is required; no installation is attempted.')
    prior=json.loads((ROOT/'provenance/ORIGINAL_SOURCE_HASHES.json').read_text());preserved=[]
    for rel,h in prior.items():
        if rel.startswith(('graphics/','source/models.py','source/drawing.py','source/generate_graphics.py','checks/verify_examples.py','checks/EXACT_CHECKS.json')):
            if sha(ROOT/rel)!=h:raise RuntimeError('Original source modified: '+rel)
            preserved.append({'path':rel,'sha256':h})
    a=spans((ROOT/'provenance/original_pages.tex').read_text());b=spans((ROOT/'source/pages.tex').read_text())
    if a!=b:raise RuntimeError('An original mathematical span changed.')
    span_report={'status':'PASS','original_span_count':len(a),'ordered_literal_spans_preserved':True,'math_span_sha256':hashlib.sha256('\n'.join(a).encode()).hexdigest(),'mathematical_token_changes':[]}
    (ROOT/'provenance/MATHEMATICAL_SPAN_PRESERVATION.json').write_text(json.dumps(span_report,indent=2)+'\n')
    logs=ROOT/'build_logs';logs.mkdir(exist_ok=True);commands=[]
    env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1791244800',FORCE_SOURCE_DATE='1',PYTHONDONTWRITEBYTECODE='1')
    def run(argv,cwd,log):
        t=time.monotonic()
        with (logs/log).open('w') as f:p=subprocess.run(argv,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
        commands.append({'argv':[str(v) for v in argv],'cwd':str(cwd),'exit_code':p.returncode,'seconds':time.monotonic()-t,'log':log})
        if p.returncode:raise RuntimeError('Command failed; see '+str(logs/log))
    run([sys.executable,'-W','error','checks/verify_portable.py'],ROOT,'portable_checks.log')
    before={p.name:sha(p) for p in (ROOT/'graphics').glob('*.tex') if p.stem in ('complex_core','inverse_closure','shared_family','quantization')}
    run([sys.executable,'-W','error','source/generate_extensions.py'],ROOT,'extensions.log')
    after={p.name:sha(p) for p in (ROOT/'graphics').glob('*.tex') if p.stem in ('complex_core','inverse_closure','shared_family','quantization')}
    if before and before!=after:raise RuntimeError('New plates do not regenerate identically.')
    with tempfile.TemporaryDirectory(prefix='paper_viii_visual_guide_') as td:
        w=Path(td)
        for name in ('source','graphics'):shutil.copytree(ROOT/name,w/name,ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT/'appendix.tex',w/'appendix.tex')
        for i in (1,2):run([tex,'-interaction=nonstopmode','-halt-on-error','appendix.tex'],w,f'latex_pass_{i}.log')
        log=(w/'appendix.log').read_text(errors='replace');shutil.copy2(w/'appendix.log',logs/'appendix.log')
        faults=re.findall(r'Overfull \\[hv]box|Underfull \\[hv]box|undefined references|LaTeX Error|Missing character|pdfTeX warning \(dest\)',log)
        out=ROOT/'Paper_VIII_Visual_Guide_Final.pdf';shutil.copy2(w/'appendix.pdf',out)
    d=fitz.open(out);toc=d.get_toc();names=d.resolve_names();pages=[];links=0
    if len(d)!=32:raise RuntimeError('Expected 32 guide pages; got '+str(len(d)))
    if len(toc)!=32 or [x[2] for x in toc]!=list(range(1,33)):raise RuntimeError('Bookmark/page mismatch.')
    for i,p in enumerate(d):
        outside=[];invalid=[]
        for bl in p.get_text('dict')['blocks']:
            for line in bl.get('lines',[]):
                for sp in line['spans']:
                    if not sp['text'].strip():continue
                    x0,y0,x1,y1=sp['bbox']
                    if x0<20 or x1>592 or y0<10 or y1>780:outside.append(sp['text'])
        for link in p.get_links():
            if link['kind']==fitz.LINK_GOTO:
                target=link.get('page',-1);links+=1
                if not 0<=target<len(d):invalid.append(str(link))
            elif link['kind']==fitz.LINK_NAMED:
                named=link.get('nameddest','');target=names.get(named,{}).get('page',-1);links+=1
                if not 0<=target<len(d):invalid.append(str(link))
                m=re.fullmatch(r'PVIIIA\.visual(\d+)\.1',named)
                if m and target!=int(m[1])-1:invalid.append('Wrong visual destination '+named)
        text=p.get_text();bad='\ufffd' in text or '??' in text;images=len(p.get_images(full=True))
        pages.append({'page':i+1,'word_count':len(text.split()),'raster_image_objects':images,'outside_safe_bounds':outside,'invalid_links':invalid,'replacement_or_unresolved_reference':bad})
        if outside or invalid or images or bad:raise RuntimeError('PDF preflight failed on page '+str(i+1))
    (ROOT/'PDF_TEXT.txt').write_text('\n\f\n'.join(p.get_text() for p in d));d.close()
    checks=json.loads((ROOT/'checks/PORTABLE_CHECKS.json').read_text());inherited=json.loads((ROOT/'provenance/INHERITED_EXACT_CHECKS.json').read_text())
    mapfile=ROOT/'SOURCE_CROSSWALK.json';source_map=json.loads(mapfile.read_text()) if mapfile.exists() else []
    register_file=ROOT/'provenance/FINAL_TRADITIONAL_REGISTER.json';register=json.loads(register_file.read_text()) if register_file.exists() else {}
    if source_map:
        if len(source_map)!=32:raise RuntimeError('Incomplete source crosswalk.')
        for row in source_map:
            for target in row['targets']:
                recorded=register.get('labels',{}).get(target['label'])
                if recorded!=target:raise RuntimeError('Traditional reference mismatch on guide page '+str(row['visual_page']))
    report={'status':'PASS' if not faults else 'TYPESETTING_WARNINGS','pdf_pages':32,'original_worked_pages':28,'new_worked_pages':4,'original_vector_plates':26,'new_vector_plates':4,
       'original_math_span_preservation':span_report,'preserved_original_files':preserved,'fresh_positive_assertions':checks['positive_assertions'],'fresh_invalid_controls_rejected':checks['negative_controls_rejected'],
       'historical_sympy_assertions':inherited['checks_passed'],'historical_sympy_suite_executed':False,'historical_sympy_unavailable_reason':'SymPy is absent; original code and recorded outputs are preserved.',
       'lean_invoked':False,'new_gpu_timing':False,'latex_faults':faults,'page_checks':pages,'valid_internal_links':links,'source_map_rows':len(source_map),
       'source_reference_status':'Final edition verified' if source_map and all(r.get('final_targets_verified') for r in source_map) else 'Awaiting final traditional register',
       'commands':commands,'python_version':platform.python_version(),'pymupdf_version':fitz.VersionBind,'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],
       'pdf_sha256':sha(out),'scope':'Standalone exposition and exact bounded worked instances; no expanded formal, factorization, or timing contract.'}
    if register:
        report.update(traditional_reference_pdf_sha256=register['pdf_sha256'],traditional_reference_pdf_pages=register['pdf_pages'],final_source_targets_verified=sum(len(r['targets']) for r in source_map),source_crosswalk_sha256=sha(mapfile))
    (ROOT/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    if faults:raise RuntimeError('Typesetting warnings: '+str(faults))
    print('PASS: 32-page guide; 26 original and 4 new vector plates; '+str(checks['positive_assertions'])+' fresh exact assertions.')
if __name__=='__main__':main()
