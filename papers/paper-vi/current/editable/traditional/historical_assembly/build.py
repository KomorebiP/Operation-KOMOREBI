#!/usr/bin/env python3
"""Compile portable final source; original research and figures are not rerun."""
from pathlib import Path
import os,subprocess,sys
R=Path(__file__).resolve().parent
if '--assemble' in sys.argv:subprocess.run([sys.executable,str(R/'assemble.py')],cwd=R,check=True)
env=dict(os.environ);env['SOURCE_DATE_EPOCH']='1791158400'
stem='Paper_VI_Traditional_Final'
for suffix in ['aux','toc','out','lof','lot']:
 (R/(stem+'.'+suffix)).unlink(missing_ok=True)
commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['bibtex',stem]]+[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]*3
for i,cmd in enumerate(commands,1):
 p=subprocess.run(cmd,cwd=R,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (R/f'build_pass_{i}.txt').write_text(p.stdout)
 if p.returncode:
  print(p.stdout[-10000:]);raise SystemExit(p.returncode)
print(R/(stem+'.pdf'))
