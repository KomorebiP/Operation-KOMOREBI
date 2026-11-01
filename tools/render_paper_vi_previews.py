"""Rebuild Paper VI web figure previews from retained one-page PDFs with Poppler.

Run from the repository root. Requires pdftoppm on PATH, or --pdftoppm PATH.
The frozen manuscript and PDF inputs are read without modification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def build(root, executable):
    source = root / 'papers/paper-vi/current/editable/traditional/extension_figures'
    output = root / 'website/assets/paper-vi-figures'
    output.mkdir(parents=True, exist_ok=True)
    records = {}
    for pdf in sorted(source.glob('*.pdf')):
        target = output / pdf.stem
        subprocess.run([executable, '-png', '-singlefile', '-scale-to-x', '1800',
                        '-scale-to-y', '-1', str(pdf), str(target)], check=True)
        target = target.with_suffix('.png')
        records[pdf.relative_to(root).as_posix()] = dict(
            source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
            asset=target.relative_to(root / 'website').as_posix(),
            asset_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    if len(records) != 15:
        raise ValueError('Review Paper VI figure coverage before updating previews')
    manifest = dict(conversion='Poppler pdftoppm; PNG; single page; width 1800 pixels; aspect ratio preserved',
                    figures=records)
    (root / 'website/paper-vi-figure-previews.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--pdftoppm', default=shutil.which('pdftoppm'))
    arguments = parser.parse_args()
    if not arguments.pdftoppm:
        parser.error('Install Poppler or supply --pdftoppm PATH')
    build(arguments.root.resolve(), arguments.pdftoppm)
