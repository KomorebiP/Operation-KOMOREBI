#!/usr/bin/env python3
"""Compile the authored Paper II Lean guide with bundled TeX assets."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'publication'))
from current_publication import configuration, source_epoch
STEM = 'Paper_II_Lean_Guide_Final'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-directory', type=Path,
                    help='Put compiled files in this directory. Sources remain unchanged.')

parser.add_argument('--edition-date', help='ISO date for the deterministic TeX timestamp')
args = parser.parse_args()
_, edition_day = configuration(edition_date=args.edition_date)

if shutil.which('xelatex') is None:
    raise SystemExit('XeLaTeX is required. Install it through your TeX distribution.')
out = args.output_directory.expanduser().resolve() if args.output_directory else ROOT
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ)
env['SOURCE_DATE_EPOCH'] = source_epoch(edition_day)
env['FORCE_SOURCE_DATE'] = '1'
for name in ('TEXINPUTS', 'BIBINPUTS', 'BSTINPUTS'):
    env[name] = str(ROOT) + os.pathsep + env.get(name, '')
command = ['xelatex', '-interaction=nonstopmode', '-halt-on-error',
           '-file-line-error', '-recorder', '-output-directory=' + str(out),
           '-jobname=' + STEM, STEM + '.tex']
for pass_number in range(1, 5):
    run = subprocess.run(command, cwd=ROOT, env=env, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    transcript = out / f'build_pass_{pass_number}.txt'
    transcript.write_text(run.stdout)
    if run.returncode:
        raise SystemExit(f'XeLaTeX failed on pass {pass_number}. See {transcript}')
    if pass_number == 1:
        aux = out / (STEM + '.aux')
        if aux.exists() and r'\bibdata' in aux.read_text(errors='replace'):
            if shutil.which('bibtex') is None:
                raise SystemExit('BibTeX is required by this bibliography.')
            bib = subprocess.run(['bibtex', STEM], cwd=out, env=env, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (out / 'build_bibtex.txt').write_text(bib.stdout)
            if bib.returncode:
                raise SystemExit(f'BibTeX failed. See {out / "build_bibtex.txt"}')
pdf = out / (STEM + '.pdf')
if not pdf.is_file():
    raise SystemExit('Compilation completed without the expected PDF: ' + str(pdf))
print(pdf)
