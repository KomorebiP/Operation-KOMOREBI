#!/usr/bin/env python3
"""Rebuild the mathematical supplement with LaTeX; render and inspect before replacing the PDF."""
import argparse,re,shutil,subprocess,datetime
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path);a=ap.parse_args()
out=a.output_dir or r/'verification/document_rebuild'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out.mkdir(parents=True,exist_ok=False)
name='Nishibuchi_Conjecture_Completion'
for x in [name+'.tex','verification_summary.tex']:shutil.copy2(r/'docs'/x,out/x)
for _ in range(2):
 p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=out,capture_output=True,text=True,timeout=90)
 if p.returncode:print(p.stdout);raise SystemExit(p.returncode)
log=(out/(name+'.log')).read_text()
issues=re.findall(r'^(?:Overfull|Underfull|.*Warning).*$',log,re.M)
if issues: print('\n'.join(issues));raise SystemExit('Review PDF diagnostics')
print(out/(name+'.pdf'))
