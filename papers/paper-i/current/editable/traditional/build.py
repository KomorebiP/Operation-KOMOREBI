#!/usr/bin/env python3
"""Rebuild the final traditional paper from the included editable sources."""
import argparse,json,re,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--check-examples',action='store_true');args=p.parse_args()
root=Path(__file__).resolve().parent
latex=shutil.which('xelatex')
if not latex:raise SystemExit('XeLaTeX is required. Install TeX Live with the packages listed in BUILD_README.txt.')
logs=root/'build_logs';logs.mkdir(exist_ok=True)
if args.check_examples:
 result=subprocess.run([sys.executable,str(root/'visual_checks/verify_examples.py')],cwd=root,text=True,capture_output=True)
 (logs/'visual_checks.log').write_text(result.stdout+result.stderr)
 if result.returncode:raise SystemExit('Exact visual checks failed; see build_logs/visual_checks.log.')
for i in range(1,4):
 result=subprocess.run([latex,'-interaction=nonstopmode','-halt-on-error','Paper_I_Traditional_Final.tex'],cwd=root,text=True,capture_output=True)
 (logs/f'latex_pass_{i}.log').write_text(result.stdout+result.stderr)
 if result.returncode:raise SystemExit(f'LaTeX pass {i} failed; see build_logs/latex_pass_{i}.log.')
log=(logs/'latex_pass_3.log').read_text()
issues=[line for line in log.splitlines() if re.search(r'Overfull|undefined references|multiply defined|Missing character',line)]
if issues:print('Layout/reference warnings:',*issues,sep='\n');raise SystemExit(1)
print('Built Paper_I_Traditional_Final.pdf with no overfull boxes or unresolved references.')
