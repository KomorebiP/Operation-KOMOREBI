#!/usr/bin/env python3
"""Compile this portable traditional-paper source; no mathematics or figures rerun."""
from pathlib import Path
import os, subprocess,sys
R=Path(__file__).resolve().parent
if '--assemble' in sys.argv:
 subprocess.run([sys.executable,str(R/'assemble.py')],cwd=R,check=True)
env=dict(os.environ);env['SOURCE_DATE_EPOCH']='1791158400'
stem='Paper_IV_Traditional_Final'
commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['bibtex',stem],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]
for i,cmd in enumerate(commands,1):
 result=subprocess.run(cmd,cwd=R,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (R/f'build_pass_{i}.txt').write_text(result.stdout)
 if result.returncode:
  print(result.stdout[-10000:]);raise SystemExit(result.returncode)
print(R/(stem+'.pdf'))
