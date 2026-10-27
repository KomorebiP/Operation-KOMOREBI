#!/usr/bin/env python3
"""Build the new atlas outside the immutable checkpoint.

Requires Python + Matplotlib + PyMuPDF and pdfLaTeX with standard PSNFSS,
hyperref, TikZ and the other packages listed in the wrapper. Uses installed fonts,
never a bundled font file. The existing readers are not rebuilt or modified.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
import fitz


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=a.output.resolve()
 if out.is_relative_to(root):raise SystemExit('Build output must be outside the checkpoint.')
 out.mkdir(parents=True,exist_ok=True);work=out/'source';shutil.copytree(root/'publication/source',work,dirs_exist_ok=True)
 engine=shutil.which('pdflatex')
 if not engine:raise SystemExit('pdfLaTeX was not found. Prebuilt PDFs remain readable without it.')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',SOURCE_DATE_EPOCH='1791590400',FORCE_SOURCE_DATE='1',TZ='UTC')
 start=time.monotonic()
 figdir=work/'figures'
 r=subprocess.run([sys.executable,str(root/'tools/draw_atlas.py'),'--output',str(figdir)],cwd=out,env=env,text=True,capture_output=True,timeout=120)
 (out/'figures.stdout.log').write_text(r.stdout);(out/'figures.stderr.log').write_text(r.stderr)
 if r.returncode:raise SystemExit('Figure generation failed; see figures.stderr.log')
 target=work/'Paper_XI_Conjecture66_Visual_Atlas.tex'
 for ext in ['aux','out','toc','log']:target.with_suffix('.'+ext).unlink(missing_ok=True)
 records=[]
 for i in range(3):
  cmd=[engine,'-interaction=nonstopmode','-halt-on-error',target.name]
  r=subprocess.run(cmd,cwd=work,env=env,text=True,capture_output=True,timeout=120)
  (out/f'latex_pass{i+1}.log').write_text(r.stdout+r.stderr)
  records.append({'pass':i+1,'returncode':r.returncode})
  if r.returncode:raise SystemExit(f'LaTeX pass {i+1} failed; see {out}/latex_pass{i+1}.log')
 log=target.with_suffix('.log').read_text(errors='replace')
 diag=[x for x in log.splitlines() if any(t in x for t in ['Warning:','Overfull','Underfull','Missing character'])]
 raw=target.with_suffix('.pdf');pdf=fitz.open(raw)
 cat=json.loads((root/'evidence/block05/PLATE_CATALOG.json').read_text())
 links=[]
 for plate in cat['plates']:
  marker='WORKED PLATE '+plate['id'];found=[]
  for i,page in enumerate(pdf):
   if marker in page.get_text():found.append(i)
  if len(found)!=1:raise SystemExit(f'Expected one page for {marker}, found {found}')
  pi=found[0];page=pdf[pi];hits=page.search_for('Companion source:')
  if len(hits)!=1:raise SystemExit(f'Expected one companion locator on {marker}')
  rect=fitz.Rect(hits[0].x0,hits[0].y0,page.rect.width-52,hits[0].y1+12)
  page.insert_link({'kind':fitz.LINK_GOTOR,'from':rect,'file':plate['source_reader'],'page':plate['pages'][0]-1,'to':fitz.Point(0,0),'zoom':0})
  links.append({'plate':plate['id'],'atlas_page':pi+1,'companion_page':plate['pages'][0],'file':plate['source_reader']})
 output=out/'Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf'
 pdf.save(output,garbage=4,deflate=True,no_new_id=True);pdf.close()
 result={'status':'passed','engine':engine,'passes':records,'diagnostics':diag,'atlas_pages':len(fitz.open(output)),
   'plate_count':len(cat['plates']),'companion_links':links,'raw_pdf_sha256':sha(raw),'pdf_sha256':sha(output),'seconds':round(time.monotonic()-start,3)}
 (out/'BUILD_RECORD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
