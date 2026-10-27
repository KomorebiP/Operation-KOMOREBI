#!/usr/bin/env python3
"""Rebuild the standalone guide and all vector figures in a chosen directory.

Requires Python 3.10+, SymPy, PyMuPDF, pdflatex and the packages used by the TeX
source. No network, AI imagery, Lean invocation, or source-archive mutation.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
NAME = 'Paper_XII_Visual_Guide_Final'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, default=ROOT)
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
for sub in ('source', 'graphics', 'checks', 'texbuild'):
    (OUT/sub).mkdir(exist_ok=True)
for rel in (NAME+'.tex', 'source/pages.tex', 'source/generate_graphics.py',
            'checks/verify_examples.py', 'build.py', 'README.md',
            'SOURCE_COVERAGE.md', 'requirements.txt', 'checks/SOURCE_ANCHORS.json'):
    if not (ROOT/rel).is_file():
        continue
    if (ROOT/rel).resolve() != (OUT/rel).resolve():
        shutil.copyfile(ROOT/rel, OUT/rel)

env = dict(os.environ, SOURCE_DATE_EPOCH='1791244800', FORCE_SOURCE_DATE='1', TZ='UTC')
def run(command, log):
    with (OUT/'texbuild'/log).open('w', encoding='utf8') as h:
        p = subprocess.run(command, cwd=OUT, env=env, stdout=h,
                           stderr=subprocess.STDOUT, timeout=180)
    if p.returncode:
        raise RuntimeError(f'Command failed ({p.returncode}); see {OUT/"texbuild"/log}')

run([sys.executable, str(ROOT/'checks/verify_examples.py'),
     '--output', str(OUT/'checks/EXACT_CHECKS.json')], 'examples.stdout')
run([sys.executable, str(ROOT/'source/generate_graphics.py'),
     '--output-dir', str(OUT/'graphics')], 'graphics.stdout')
tex = shutil.which('pdflatex')
if not tex:
    raise RuntimeError('pdflatex is required')
for n in (1, 2):
    run([tex, '-interaction=nonstopmode', '-halt-on-error',
         '-output-directory=texbuild', NAME+'.tex'], f'latex_{n}.stdout')
log = (OUT/'texbuild'/f'{NAME}.log').read_text(errors='replace')
bad = re.findall(r'Overfull \\[hv]box|undefined references|LaTeX Error', log)
if bad:
    raise RuntimeError(f'Layout/reference errors: {bad}')
shutil.copyfile(OUT/'texbuild'/f'{NAME}.pdf', OUT/f'{NAME}.pdf')

# Regenerate separately reusable PDF vector figures from the TikZ sources.
for figure in sorted((OUT/'graphics').glob('*.tex')):
    wrapper = OUT/'graphics'/f'{figure.stem}_wrapper.tex'
    wrapper.write_text(r'''\documentclass{article}
\pdfinfoomitdate=1
\pdfsuppressptexinfo=15
\pdftrailerid{}
\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,amssymb,tikz}
\usetikzlibrary{arrows.meta,decorations.pathreplacing,patterns,calc}
\usepackage[active,tightpage]{preview}
\PreviewEnvironment{tikzpicture}
\setlength\PreviewBorder{6pt}
\begin{document}
''' + f'\\input{{graphics/{figure.name}}}\n' + r'\end{document}'+'\n')
    run([tex, '-interaction=nonstopmode', '-halt-on-error',
         '-output-directory=texbuild', str(wrapper)], f'figure_{figure.stem}.stdout')
    shutil.copyfile(OUT/'texbuild'/f'{figure.stem}_wrapper.pdf',
                    OUT/'graphics'/f'{figure.stem}.pdf')
    wrapper.unlink()

doc = fitz.open(OUT/f'{NAME}.pdf')
topics=re.findall(r'\\vpage\{(\d+)\}\{([^{}]+)\}',
                  (OUT/'source/pages.tex').read_text())
if len(doc) != len(topics):
    raise RuntimeError(f'Unintentional continuation pages: {len(doc)} pages for {len(topics)} topics')
normalize=lambda s:' '.join(s.split())
for page, (identifier,title) in zip(doc, topics):
    if normalize(title) not in normalize(page.get_text()):
        raise RuntimeError(f'Misplaced topic {identifier}: {title}')
outline=doc.get_toc()
if len(outline)!=len(topics) or any(item[2]!=n for n,item in enumerate(outline,1)):
    raise RuntimeError('Outline destinations do not match topic pages')
pages = []
issues = []
for n, page in enumerate(doc, 1):
    outside=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                if not span['text'].strip():
                    continue
                x0,y0,x1,y1=span['bbox']
                if x0 < 20 or x1 > page.rect.width-20 or y0 < 10 or y1 > page.rect.height-10:
                    outside.append(span['text'])
    rasters=len(page.get_images())
    if outside or rasters:
        issues.append({'page':n, 'outside':outside, 'rasters':rasters})
    pages.append({'page':n, 'word_count':len(page.get_text().split()),
                  'raster_images':rasters, 'out_of_bounds_text':outside})
if issues:
    raise RuntimeError(f'PDF preflight failed: {issues}')
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
exact=json.loads((OUT/'checks/EXACT_CHECKS.json').read_text())
report={'status':'PASS', 'date':'2026-10-06', 'pages':len(doc),
        'example_check_count':exact['check_count'], 'all_figures_vector':True,
        'pdf_metadata':doc.metadata, 'pdf_sha256':sha(OUT/f'{NAME}.pdf'),
        'text_sha256':hashlib.sha256(''.join(p.get_text() for p in doc).encode()).hexdigest(),
        'overfull_boxes':0, 'unresolved_references':0,
        'underfull_boxes':len(re.findall(r'Underfull \\[hv]box',log)),
        'outline_items_on_correct_pages':len(outline),
        'page_checks':pages,
        'scope':'Exact illustrative examples and PDF build only; no new Lean verification.'}
(OUT/'checks/BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(doc)} pages; {exact["check_count"]} exact checks; vector figures regenerated.')
