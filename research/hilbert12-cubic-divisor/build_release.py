#!/usr/bin/env python3
"""Compile the editable companion TeX; do not regenerate authored source."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
DOCUMENTS = {
    'traditional': 'H12_Cubic_Divisor_Traditional',
    'visual': 'H12_Cubic_Divisor_Visual_Guide',
    'lean': 'H12_Cubic_Divisor_Lean_Guide',
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=DOCUMENTS)
    parser.add_argument('--engine', default='pdflatex')
    args = parser.parse_args()
    engine = shutil.which(args.engine)
    if engine is None:
        parser.error(f'TeX engine unavailable: {args.engine}')
    records = []
    logroot = ROOT / 'verification/publication/rebuild'
    logroot.mkdir(parents=True, exist_ok=True)
    for folder, stem in DOCUMENTS.items():
        if args.only and folder != args.only:
            continue
        directory = ROOT / folder
        source = directory / f'{stem}.tex'
        if not source.is_file():
            raise FileNotFoundError(source)
        for iteration in range(1, 4):
            result = subprocess.run(
                [engine, '-interaction=nonstopmode', '-halt-on-error', source.name],
                cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                timeout=180,
            )
            (logroot / f'{folder}_{iteration}.log').write_bytes(result.stdout)
            if result.returncode:
                raise RuntimeError(f'{folder} pass {iteration} failed; see {logroot}')
        output = directory / f'{stem}.pdf'
        records.append({'document': folder, 'pdf': str(output.relative_to(ROOT)),
                        'bytes': output.stat().st_size,
                        'sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
    (logroot / 'BUILD_RESULT.json').write_text(json.dumps(records, indent=2)+'\n')
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()
