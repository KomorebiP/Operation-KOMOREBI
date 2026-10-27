#!/usr/bin/env python3
"""Build the complete edition using only relative bundled source/assets.
Requires an existing TeX distribution with pdflatex and bibtex. No downloads.
"""
from pathlib import Path
import subprocess, json, hashlib, re, shutil, sys, os
ROOT=Path(__file__).resolve().parent
NAME='Paper_VIII_Traditional_Final'
BUILD=ROOT/'build'
BUILD.mkdir(exist_ok=True)
for suffix in ['aux','toc','out','bbl','blg']:
 stale=BUILD/(NAME+'.'+suffix)
 if stale.exists():stale.unlink()
env=os.environ.copy()
env.setdefault('SOURCE_DATE_EPOCH','1791244800')
env.setdefault('FORCE_SOURCE_DATE','1')
for program in ['pdflatex','bibtex']:
 if not shutil.which(program):raise SystemExit(f'Required program not found: {program}')
commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build',NAME+'.tex'],['bibtex','build/'+NAME]]
commands+= [commands[0]]*3
for i,cmd in enumerate(commands,1):
 p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (BUILD/f'pass_{i}.txt').write_text(p.stdout)
 if p.returncode:
  print(p.stdout[-6000:]);raise SystemExit(f'Build pass {i} failed ({p.returncode}).')
log=(BUILD/(NAME+'.log')).read_text(errors='replace')
diagnostics=[l for l in log.splitlines() if any(x in l for x in ['Warning:','Overfull','Underfull','undefined','multiply defined','destination with the same identifier'])]
(ROOT/'evidence/FINAL_DIAGNOSTICS.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
shutil.copy2(BUILD/(NAME+'.pdf'),ROOT/(NAME+'.pdf'))
try:
 import fitz
 pdf=fitz.open(ROOT/(NAME+'.pdf'))
 info=dict(pages=len(pdf),bytes=(ROOT/(NAME+'.pdf')).stat().st_size,sha256=hashlib.sha256((ROOT/(NAME+'.pdf')).read_bytes()).hexdigest(),diagnostics=diagnostics)
except ImportError:
 info=dict(bytes=(ROOT/(NAME+'.pdf')).stat().st_size,sha256=hashlib.sha256((ROOT/(NAME+'.pdf')).read_bytes()).hexdigest(),diagnostics=diagnostics)
(ROOT/'evidence/BUILD_RESULT.json').write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps(info,indent=2))
if diagnostics:raise SystemExit('PDF built; resolve the recorded final diagnostics before release.')
