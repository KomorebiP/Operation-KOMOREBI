#!/usr/bin/env python3
"""Compile the authored Paper VI visual atlas with externally resolved fonts and packaged TeX assets.

The source tree is copied in full to an isolated directory. Chapters,
styles and vector assets are retained. Compilation does not regenerate prose,
data, figures, formal sources or the historical integration.
"""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode = True
from font_dependencies import resolve_fonts, stage_fonts
import os
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
STEM = 'Paper_VI_Visual_Guide_Final'


def atomic_copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    oldmtime = destination.stat().st_mtime if destination.exists() else 0
    descriptor, temporary = tempfile.mkstemp(dir=destination.parent,
                                             prefix='.' + destination.name + '.')
    os.close(descriptor)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
        stamp = max(time.time(), oldmtime + 2)
        os.utime(destination, (stamp, stamp))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory', '--output-dir', dest='output_directory',
                        type=Path, help='Write compiled files here. Sources are unchanged.')
    parser.add_argument('--check-only', action='store_true',
                        help='Compile in isolation without changing delivered files.')

    args = parser.parse_args()

    if shutil.which('xelatex') is None:
        parser.error('XeLaTeX is required. Install it through your TeX distribution.')
    font_record = resolve_fonts(include_code=False)
    destination = (args.output_directory or ROOT).expanduser().resolve()
    environment = dict(os.environ)
    environment.setdefault('SOURCE_DATE_EPOCH', '1791504000')
    environment['FORCE_SOURCE_DATE'] = '1'
    # Only generated manuscript products are excluded. Other PDF files are assets.
    ignore = shutil.ignore_patterns(
        'qa', '__pycache__', STEM + '.pdf', '*.aux', '*.log', '*.out', '*.toc',
        '*.lof', '*.lot', '*.bbl', '*.blg', '*.fdb_latexmk', '*.fls', '*.xdv',
        'build_pass_*.txt', 'build_bibtex.txt', 'historical_assembly')
    with tempfile.TemporaryDirectory(prefix='komorebi-paper-vi-visual_guide-') as temporary:
        stage = Path(temporary) / 'source'
        shutil.copytree(ROOT, stage, ignore=ignore)
        stage_fonts(stage, font_record)
        for name in ('TEXINPUTS', 'BIBINPUTS', 'BSTINPUTS'):
            environment[name] = str(stage) + os.pathsep + environment.get(name, '')
        command = ['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                   '-file-line-error', '-recorder', '-jobname=' + STEM, STEM + '.tex']
        transcripts = []

        def run_command(command, transcript_name):
            run = subprocess.run(command, cwd=stage, env=environment, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            transcript = stage / transcript_name
            transcript.write_text(run.stdout)
            transcripts.append(transcript)
            if run.returncode:
                if not args.check_only:
                    for recorded in transcripts:
                        atomic_copy(recorded, destination / recorded.name)
                print(run.stdout[-12000:])
                raise SystemExit('Compilation failed. See ' +
                                 str(destination / transcript_name) if not args.check_only
                                 else 'Compilation failed during isolated check.')

        for pass_number in range(1, 5):
            run_command(command, f'build_pass_{pass_number}.txt')
            if pass_number == 1:
                auxiliary = stage / (STEM + '.aux')
                if auxiliary.exists() and r'\bibdata' in auxiliary.read_text(errors='replace'):
                    if shutil.which('bibtex') is None:
                        raise SystemExit('BibTeX is required by this bibliography.')
                    run_command(['bibtex', STEM], 'build_bibtex.txt')
        pdf = stage / (STEM + '.pdf')
        if not pdf.is_file():
            raise SystemExit('Compilation completed without the expected PDF: ' + str(pdf))
        log = stage / (STEM + '.log')
        if log.exists():
            warnings = [line for line in log.read_text(errors='replace').splitlines()
                        if any(marker in line for marker in
                               ('Overfull', 'undefined references', 'undefined citations',
                                'undefined on input', 'Missing character:'))]
            if warnings:
                print('\n'.join(warnings))
                raise SystemExit('Final compilation has unresolved references or missing characters.')
        if not args.check_only:
            destination.mkdir(parents=True, exist_ok=True)
            (destination / 'FONT_DEPENDENCIES.json').write_text(json.dumps(font_record, indent=2) + '\n', encoding='utf-8')
        if args.check_only:
            print('PASS: isolated four-pass XeLaTeX build. Delivered files are unchanged.')
            return
        for suffix in ('pdf', 'log', 'aux', 'out', 'toc', 'lof', 'lot', 'bbl', 'blg', 'fls'):
            product = stage / (STEM + '.' + suffix)
            if product.is_file():
                atomic_copy(product, destination / product.name)
        for transcript in transcripts:
            atomic_copy(transcript, destination / transcript.name)
        print(destination / (STEM + '.pdf'))


if __name__ == '__main__':
    main()
