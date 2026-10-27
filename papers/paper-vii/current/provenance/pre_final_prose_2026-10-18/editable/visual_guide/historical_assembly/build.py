#!/usr/bin/env python3
"""Portable local build: exact extended checks, deterministic vector plates, two TeX passes.

Original SymPy-dependent models, plates and the 180-check record are preserved;
the original suite is not executed by this build. No installation or Lean run.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,platform,re,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def maths(s):return re.findall(r'\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)',s,re.S)
def main():
 import fitz
 tex=shutil.which('pdflatex')
 if not tex:raise SystemExit('pdflatex is required; no package installation is attempted.')
 finalmap=json.loads((ROOT/'provenance/FINAL_THEOREM_REGISTER.json').read_text());crosswalk=json.loads((ROOT/'SOURCE_CROSSWALK.json').read_text())
 if len(crosswalk)!=40:raise RuntimeError('Expected 40 final-edition source crosswalk rows')
 for row in crosswalk:
  for target in row['targets']:
   final=finalmap['labels'].get(target['final_label'])
   if not final or str(final['physical_page'])!=target['traditional_page'] or final['number']!=target['number']:raise RuntimeError('Final-edition reference mismatch on V-'+str(row['visual_page']))
 scope=json.loads((ROOT/'provenance/FORMAL_SCOPE_CHECK.json').read_text());ledger=json.loads((ROOT/'provenance/SAVED_FINITE_THEOREM_LEDGER.json').read_text())
 if len(ledger)!=19 or any(r['status']!='LEAN_CHECKED' for r in ledger) or scope['original_conjecture_count']!=5:raise RuntimeError('Saved formal contract metadata mismatch')
 logs=ROOT/'build_logs';logs.mkdir(exist_ok=True);before=json.loads((ROOT/'provenance/ORIGINAL_SOURCE_HASHES.json').read_text());preserved=[]
 for rel,h in before.items():
  if rel.startswith(('graphics/','source/models.py','source/generate_graphics.py','checks/verify_examples.py','checks/EXACT_CHECKS.json')):
   p=ROOT/rel
   if sha(p)!=h:raise RuntimeError('Changed original source '+rel)
   preserved.append({'path':rel,'sha256':h})
 original=(ROOT/'provenance/original_pages.tex').read_text();current=(ROOT/'source/pages.tex').read_text();a=maths(original);b=maths(current)
 if a!=b:raise RuntimeError('Original mathematical spans changed.')
 span_audit={'status':'PASS','original_span_count':len(a),'same_order_and_exact_bytes':True,'sha256':hashlib.sha256('\n'.join(a).encode()).hexdigest(),'method':'Ordered literal $...$, \\[...\\], and \\(...\\) spans. Original graphics and model hashes are checked separately.','mathematical_token_corrections':[]}
 (ROOT/'provenance/MATHEMATICAL_SPAN_PRESERVATION.json').write_text(json.dumps(span_audit,indent=2)+'\n')
 env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1791244800',FORCE_SOURCE_DATE='1',PYTHONDONTWRITEBYTECODE='1')
 commands=[]
 def run(argv,cwd,log):
  start=time.monotonic()
  with (logs/log).open('w') as f:r=subprocess.run(argv,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  commands.append({'argv':[str(x) for x in argv],'cwd':str(cwd),'exit_code':r.returncode,'runtime_seconds':time.monotonic()-start,'log':log})
  if r.returncode:raise RuntimeError('Command failed; see '+str(logs/log))
 run([sys.executable,'checks/verify_extended.py'],ROOT,'extended_checks.log')
 run([sys.executable,'source/generate_extensions.py'],ROOT,'extension_generation.log')
 with tempfile.TemporaryDirectory(prefix='paper_vii_visual_guide_') as td:
  work=Path(td)
  for name in ['source','graphics','graphics_extended']:shutil.copytree(ROOT/name,work/name,ignore=shutil.ignore_patterns('__pycache__'))
  shutil.copy2(ROOT/'appendix.tex',work/'appendix.tex')
  for i in [1,2]:run([tex,'-interaction=nonstopmode','-halt-on-error','appendix.tex'],work,f'latex_pass_{i}.log')
  log=(work/'appendix.log').read_text(errors='replace');shutil.copy2(work/'appendix.log',logs/'appendix.log')
  faults=re.findall(r'Overfull \\[hv]box|Underfull \\[hv]box|undefined references|LaTeX Error|Missing character|pdfTeX warning \(dest\)',log)
  out=ROOT/'Paper_VII_Visual_Guide_Final.pdf';shutil.copy2(work/'appendix.pdf',out)
  doc=fitz.open(out);pages=[]
  if len(doc)!=40:raise RuntimeError('Expected 40 pages; got '+str(len(doc)))
  toc=doc.get_toc()
  if len(toc)!=40 or [x[2] for x in toc]!=list(range(1,41)):raise RuntimeError('Bookmark/page mismatch')
  for i,page in enumerate(doc):
   outside=[]
   for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
     for span in line['spans']:
      if not span['text'].strip():continue
      x0,y0,x1,y1=span['bbox']
      if x0<20 or x1>592 or y0<10 or y1>780:outside.append(span['text'])
   text=page.get_text();images=len(page.get_images(full=True));bad='\ufffd' in text or bool(re.search(r'\?\?',text));invalid=[]
   for link in page.get_links():
    if link['kind']==fitz.LINK_GOTO and not 0<=link.get('page',-1)<40:invalid.append(str(link))
   pages.append({'page':i+1,'word_count':len(text.split()),'raster_image_objects':images,'outside_safe_bounds':outside,'replacement_glyph_or_question_refs':bad,'invalid_links':invalid})
   if outside or images or bad or invalid:raise RuntimeError('PDF preflight failed on page '+str(i+1))
  (ROOT/'PDF_TEXT.txt').write_text('\n\f\n'.join(p.get_text() for p in doc));doc.close()
  extended=json.loads((ROOT/'checks/EXTENDED_CHECKS.json').read_text());report={'status':'PASS' if not faults else 'TYPESETTING_WARNINGS','pdf_pages':40,'original_visual_pages':28,'new_worked_pages':12,'original_vector_plates':26,'new_vector_plates':12,'all_vector_sources_retained':True,'original_model_preserved':True,'original_math_span_preservation':span_audit,'plate_and_model_preservation':preserved,'fresh_positive_assertions':extended['positive_assertions'],'fresh_negative_controls_rejected':extended['negative_controls_rejected'],'inherited_original_check_count':180,'original_symbolic_tests_freshly_executed':False,'unavailable_dependency':'SymPy','lean_invoked':False,'saved_finite_ledger_items':19,'original_continuum_targets_open':5,'commands':commands,'latex_faults':faults,'page_checks':pages,'python_version':platform.python_version(),'pymupdf_version':fitz.VersionBind,'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],'pdf_sha256':sha(out),'traditional_reference_pdf_sha256':finalmap['pdf_sha256'],'traditional_reference_pdf_pages':finalmap['pdf_pages'],'source_crosswalk_sha256':sha(ROOT/'SOURCE_CROSSWALK.json'),'final_source_targets_verified':sum(len(row['targets']) for row in crosswalk),'scope':'Standalone editorial guide; exact bounded worked examples and PDF checks. No continuum certification or expanded formal contract.'}
  (ROOT/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
  if faults:raise RuntimeError('Typesetting warnings '+str(faults))
 print('PASS: 40-page visual guide; 26 original + 12 new vector plates; '+str(extended['positive_assertions'])+' fresh exact assertions.')
if __name__=='__main__':main()
