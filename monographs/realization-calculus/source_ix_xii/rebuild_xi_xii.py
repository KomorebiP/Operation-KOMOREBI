#!/usr/bin/env python3
"""Rebuild the six current XI/XII reader components, using preserved figures.
Requires installed TeX fonts, pdfLaTeX/XeLaTeX/BibTeX and PyMuPDF. No formal
compiler, finite computation or figure generator runs. Research companions
remain their separately preserved frozen PDFs and are not rebuilt here.
"""
from pathlib import Path
import argparse,concurrent.futures,os,shutil,subprocess,json
ROOT=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve()
 if out.exists() and any(out.iterdir()):raise SystemExit('Use an empty output directory.')
 out.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TZ='UTC',PYTHONDONTWRITEBYTECODE='1')
 def run(cmd,cwd,log,timeout=300):
  q=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout);log.parent.mkdir(parents=True,exist_ok=True);log.write_text(q.stdout+q.stderr)
  if q.returncode:raise RuntimeError('Build failed; see '+str(log))
 def xi():
  target=out/'XI';target.mkdir()
  run(['python3','-B',str(ROOT/'XI/tools/build_readers.py'),'--output',str(target),'--stage','all'],ROOT,target.parent/'XI_driver.log',900)
 def xii():
  target=out/'XII';target.mkdir()
  for role,tag in [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]:
   work=target/role;shutil.copytree(ROOT/'XII/publication/source'/role,work)
   stem='Paper_XII_'+tag+'_Final'
   for suffix in ['.aux','.toc','.out','.log','.blg']:(work/(stem+suffix)).unlink(missing_ok=True)
   engine='xelatex' if role=='lean_guide' else 'pdflatex'
   command=[engine,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder',stem+'.tex']
   for i in range(3):
    run(command,work,work/f'pass{i+1}.stdout.log')
    if i==0 and role=='traditional':
     candidates=[s for s in ['bibtex','bibtex.original','bibtex8'] if shutil.which(s)]
     bib=next((s for s in candidates if subprocess.run([s,'--version'],capture_output=True).returncode==0),None)
     if bib is None:raise RuntimeError('No working BibTeX executable.')
     run([bib,stem],work,work/'bibliography.stdout.log')
  run(['python3','-B',str(ROOT/'XII/tools/build_readers.py'),'--output',str(target),'--stage','links'],ROOT,target/'links.log')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(xi),pool.submit(xii)]
  for f in futures:f.result()
 print('Rebuilt XI and XII; mathematical/formal evidence remains inherited.')
if __name__=='__main__':main()
