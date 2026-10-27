#!/usr/bin/env python3
"""Typeset the inherited Block 27 amended LaTeX in an isolated working copy.

The Block 27 archive supplied LaTeX but not this compiled PDF. This edition recovered
its original figures and typeset the inherited text. No mathematical edits or Lean runs.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,re,shutil,subprocess,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();out=a.output_dir.resolve()
 for tree in ['original_companion','original_releases','current_continuation','visual_appendix','manuscript','reading_editions','editorial_evidence']:
  p=ROOT/tree
  if out==p or p in out.parents:raise SystemExit('Choose output outside preserved source/evidence trees.')
 if out.exists() and any(out.iterdir()):raise SystemExit('Output directory must be new or empty.')
 out.mkdir(parents=True,exist_ok=True)
 tex=shutil.which('pdflatex')
 if not tex:raise SystemExit('pdflatex is required.')
 import fitz
 src=ROOT/'manuscript/Paper_X_Block27_Amended.tex';saved=ROOT/'reading_editions/Paper_X_Amended_Manuscript.pdf';before=sha(src);commands=[]
 env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1789171200',FORCE_SOURCE_DATE='1')
 with tempfile.TemporaryDirectory(prefix='paper_x_manuscript_') as td:
  w=Path(td);shutil.copy2(src,w/'paper.tex');shutil.copytree(ROOT/'manuscript/figures',w/'figures')
  for k in range(1,4):
   t=time.monotonic();log=out/f'latex_{k}.log'
   with log.open('w') as f:r=subprocess.run([tex,'-interaction=nonstopmode','-halt-on-error','paper.tex'],cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   commands.append({'argv':[tex,'-interaction=nonstopmode','-halt-on-error','paper.tex'],'exit_code':r.returncode,'seconds':time.monotonic()-t,'log':log.name})
   if r.returncode:raise RuntimeError('LaTeX failure: '+str(log))
  lt=(w/'paper.log').read_text(errors='replace');shutil.copy2(w/'paper.log',out/'manuscript.log');target=out/'Paper_X_Amended_Manuscript.pdf';shutil.copy2(w/'paper.pdf',target)
  failures=re.findall(r'Overfull \\[hv]box|undefined references|LaTeX Error|Missing character',lt)
  comparisons=[]
  with fitz.open(saved) as d0,fitz.open(target) as d1:
   if len(d0)!=len(d1):failures.append('Page count differs')
   for i,(p,q) in enumerate(zip(d0,d1)):
    tr=p.get_text()==q.get_text();rr=p.get_pixmap(alpha=False).samples==q.get_pixmap(alpha=False).samples
    comparisons.append({'page':i+1,'same_text':tr,'same_render_72dpi':rr})
    if not (tr and rr):failures.append(f'Page {i+1} differs')
  report={'status':'PASS' if not failures else 'MISMATCH','generated_utc':datetime.now(timezone.utc).isoformat(),
   'scope':'Rebuild of inherited amended LaTeX with recovered original figures; comparison against this editorial edition\'s initially typeset PDF, not a preexisting Block 27 PDF.',
   'source_sha256':before,'source_unchanged':sha(src)==before,'pages':len(comparisons),'overfull_warnings':len(re.findall(r'Overfull \\[hv]box',lt)),
   'underfull_warnings':len(re.findall(r'Underfull \\[hv]box',lt)),'failures':failures,'page_comparisons':comparisons,'commands':commands,
   'latex_engine':subprocess.check_output([tex,'--version'],text=True).splitlines()[0],'pdf_sha256':sha(target)}
  (out/'MANUSCRIPT_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
  if failures or not report['source_unchanged']:raise RuntimeError('Rebuild differs; inspect MANUSCRIPT_REPLAY.json')
  print('PASS: 50-page inherited amended manuscript reproduced; no source edits.')
if __name__=='__main__':
 try:main()
 except (RuntimeError,OSError,subprocess.SubprocessError) as e:raise SystemExit(str(e)) from e
