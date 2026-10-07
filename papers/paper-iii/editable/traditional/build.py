#!/usr/bin/env python3
"""Portable PDF build; requires pdflatex and bibtex, with standard TeX packages."""
from pathlib import Path
import os, subprocess, sys
R=Path(__file__).resolve().parent
if '--assemble' in sys.argv:
    subprocess.run([sys.executable,str(R/'assemble.py')],cwd=R,check=True)
env=dict(os.environ);env['SOURCE_DATE_EPOCH']='1791158400'
stem='Paper_III_Traditional_Final'
for i,cmd in enumerate([['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['bibtex',stem],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]):
    r=subprocess.run(cmd,cwd=R,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (R/f'build_pass_{i+1}.txt').write_text(r.stdout)
    if r.returncode:
        print(r.stdout[-10000:]);raise SystemExit(r.returncode)
print(R/(stem+'.pdf'))
