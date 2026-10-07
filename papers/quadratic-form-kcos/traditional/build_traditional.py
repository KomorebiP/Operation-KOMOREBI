#!/usr/bin/env python3
"""Build the complete traditional edition; keep three-pass logs for review."""
from pathlib import Path
import shutil,subprocess,sys
base=Path(__file__).resolve().parent
if shutil.which('pdflatex') is None:
 raise SystemExit('pdflatex is required (TeX Live or an equivalent LaTeX installation).')
if '--skip-figures' not in sys.argv:
 for generator in ['relayout_figures.py','relayout_late.py']:
  subprocess.run([sys.executable,str(base/generator)],cwd=base,check=True)
subprocess.run([sys.executable,str(base/'check_figure_reviews.py')],cwd=base,check=True)
for stage in range(1,4):
 logfile=base/f'build_replay_pass{stage}.log'
 with logfile.open('w') as f:
  subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','Quadratic_Form_KCOS_Traditional.tex'],cwd=base,stdout=f,stderr=subprocess.STDOUT,check=True)
final=(base/'build_replay_pass3.log').read_text()
for marker in ['Overfull','undefined references','undefined citations']:
 if marker in final:
  raise SystemExit(f'Final LaTeX preflight found {marker}; inspect the retained build log.')
if '--skip-markdown' not in sys.argv:
 if shutil.which('pandoc') is None:
  raise SystemExit('PDF built. Pandoc is required to regenerate Markdown; use --skip-markdown for PDF only.')
 subprocess.run([sys.executable,str(base/'export_markdown.py')],cwd=base,check=True)
print(base/'Quadratic_Form_KCOS_Traditional.pdf')
