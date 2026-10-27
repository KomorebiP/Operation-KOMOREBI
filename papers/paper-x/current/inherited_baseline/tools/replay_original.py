#!/usr/bin/env python3
"""Replay the recovered original Python companion without modifying its saved files.

Tests and figure generation run in an isolated copy. No Lean, installation or network calls.
Rendered-figure comparisons tolerate PDF metadata differences, not changed pixels.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,shutil,subprocess,sys,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'original_companion'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();out=a.output_dir.resolve()
 for tree in ['original_companion','original_releases','current_continuation','visual_appendix','manuscript','reading_editions','editorial_evidence']:
  p=ROOT/tree
  if out==p or p in out.parents:raise SystemExit('Choose an output directory outside preserved trees.')
 if out.exists() and any(out.iterdir()):raise SystemExit('Output directory must be new or empty.')
 out.mkdir(parents=True,exist_ok=True)
 import fitz
 before={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob('*') if p.is_file()};commands=[]
 env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 with tempfile.TemporaryDirectory(prefix='paper_x_original_') as td:
  w=Path(td)/'companion';shutil.copytree(SRC,w)
  def run(argv,name):
   t=time.monotonic()
   with (out/name).open('w') as f:r=subprocess.run(argv,cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   commands.append({'argv':argv,'exit_code':r.returncode,'seconds':time.monotonic()-t,'log':name})
   if r.returncode:raise RuntimeError('Original replay failed; see '+str(out/name))
  run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider'],'original_tests.log')
  run([sys.executable,'scripts/generate_all.py'],'original_generation.log')
  old=json.loads((SRC/'results/residual_seed_results.json').read_text());new=json.loads((w/'results/residual_seed_results.json').read_text())
  numeric=[];diff=[]
  def compare(x,y,path=''):
   if isinstance(x,dict):
    if not isinstance(y,dict) or x.keys()!=y.keys():diff.append(path+': keys');return
    for k in x:compare(x[k],y[k],path+'.'+k)
   elif isinstance(x,list):
    if not isinstance(y,list) or len(x)!=len(y):diff.append(path+': length');return
    for i,(u,v) in enumerate(zip(x,y)):compare(u,v,path+f'[{i}]')
   else:
    if isinstance(x,(int,float)) and not isinstance(x,bool):numeric.append(path)
    if x!=y:diff.append(path+': '+repr(x)+' != '+repr(y))
  compare(old,new)
  figures=[]
  for p in sorted((SRC/'figures').glob('*.pdf')):
   q=w/'figures'/p.name
   if not q.is_file():raise RuntimeError('Missing regenerated figure '+p.name)
   with fitz.open(p) as x,fitz.open(q) as y:
    eq=len(x)==len(y) and all(u.get_pixmap(alpha=False).samples==v.get_pixmap(alpha=False).samples for u,v in zip(x,y))
   figures.append({'name':p.name,'same_render_72dpi':eq,'same_bytes':sha(p)==sha(q)})
  shutil.copy2(w/'results/residual_seed_results.json',out/'regenerated_results.json')
  report={'status':'PASS' if not diff and all(v['same_render_72dpi'] for v in figures) else 'MISMATCH',
    'generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Original Python tests and finite examples/figure generation. No Lean invocation.',
    'commands':commands,'record_equal':old==new,'numeric_fields_compared':len(numeric),'record_differences':diff,'figures':figures,
    'generated_pdf_count':len(list((w/'figures').glob('*.pdf'))),'generated_png_count':len(list((w/'figures').glob('*.png'))),
    'python_version':platform.python_version(),'source_files_unchanged':before=={str(p.relative_to(SRC)):sha(p) for p in SRC.rglob('*') if p.is_file()}}
  (out/'ORIGINAL_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
  if report['status']!='PASS' or not report['source_files_unchanged']:raise RuntimeError('Replay discrepancy; inspect ORIGINAL_REPLAY.json')
  print('PASS:',len(figures),'figure PDFs;',len(numeric),'numerical fields; original sources unchanged.')
if __name__=='__main__':
 try:main()
 except (RuntimeError,OSError,subprocess.SubprocessError) as e:raise SystemExit(str(e)) from e
