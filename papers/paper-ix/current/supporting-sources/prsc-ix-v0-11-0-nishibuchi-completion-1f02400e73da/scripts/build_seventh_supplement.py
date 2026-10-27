#!/usr/bin/env python3
"""Build the mathematical supplement with pdflatex; fail on final layout diagnostics.
Author: Komorebi P. Requires pdflatex with the TeX packages listed in the source.
"""
from pathlib import Path
import re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'docs/Paper_IX_Seventh_Lean_Block_Supplement.tex'
if not shutil.which('pdflatex'):raise SystemExit('pdflatex is required for document rebuilding')
with tempfile.TemporaryDirectory(prefix='prsc-ix-document-') as d:
    out=Path(d)
    runs=[]
    for _ in range(2):
        p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',str(source)],cwd=source.parent,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
        runs.append(p.stdout)
        if p.returncode:raise RuntimeError(p.stdout)
    log=(out/(source.stem+'.log')).read_text()
    if re.search(r'Overfull|Underfull|LaTeX Warning|Package .* Warning|Undefined control sequence',log):
        raise RuntimeError('Final LaTeX diagnostics require review:\n'+log)
    pagecounts=re.findall(r'Output written on.*?\((\d+) pages?',log,re.S)
    if not pagecounts or int(pagecounts[-1])!=6:raise RuntimeError('Expected six pages')
    shutil.copyfile(out/(source.stem+'.pdf'),source.with_suffix('.pdf'))
    (ROOT/'verification/seventh_pdf_build.log').write_text(log)
    print('PASS: six pages; no final LaTeX warnings or overflow diagnostics')
