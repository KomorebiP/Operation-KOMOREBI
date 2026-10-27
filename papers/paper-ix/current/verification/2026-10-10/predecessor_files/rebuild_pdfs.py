#!/usr/bin/env python3
"""Build the final Euler paper companions from the supplied sources and figures.
Requires existing TeX, Python, and fonts; downloads and Lean execution are absent.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess
ROOT=Path(__file__).resolve().parent
SPECS={
 'main':('pdflatex','sources/main','Paper_IX_Traditional_Final.tex','Paper_IX_Euler_Main_Final'),
 'visual':('pdflatex','sources','visual.tex','Paper_IX_Euler_Visual_Guide_Final'),
 'lean':('xelatex','sources/lean','Paper_IX_Lean_Guide_Final.tex','Paper_IX_Euler_Lean_Guide_Final'),
}
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--roles',nargs='+',choices=list(SPECS),default=list(SPECS))
 args=ap.parse_args()
 out=ROOT/'output/pdf';out.mkdir(parents=True,exist_ok=True)
 logs=ROOT/'evidence/pdf_build';logs.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['SOURCE_DATE_EPOCH']='1791244800';env['FORCE_SOURCE_DATE']='1'
 records=[]
 for role in args.roles:
  engine,folder,source,stem=SPECS[role]
  if not shutil.which(engine):raise SystemExit(f'Missing {engine}')
  work=ROOT/folder
  cmd=[engine,'-interaction=nonstopmode','-halt-on-error','-file-line-error','-jobname='+stem,source]
  for pno in range(1,5):
   run=subprocess.run(cmd,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
   (logs/f'{role}_pass_{pno}.txt').write_text(run.stdout)
   if run.returncode:print(run.stdout[-6000:]);raise SystemExit(f'{role}: build failed')
  log=(work/(stem+'.log')).read_text(errors='replace')
  markers=('Overfull','Missing character','undefined references','multiply defined','destination with the same identifier')
  bad=[x for x in log.splitlines() if any(m in x for m in markers)]
  if bad:raise SystemExit(f'{role}: layout/reference defects: '+str(bad))
  dest=out/(stem+'.pdf');shutil.copy2(work/(stem+'.pdf'),dest)
  import fitz
  with fitz.open(dest) as pdf:pages=len(pdf)
  records.append(dict(role=role,path=str(dest.relative_to(ROOT)),pages=pages,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),unresolved_layout_or_reference_diagnostics=bad))
 report=dict(status='PASS',scope='PDF compilation only; no Lean or universal arithmetic proof run',documents=records)
 (logs/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
