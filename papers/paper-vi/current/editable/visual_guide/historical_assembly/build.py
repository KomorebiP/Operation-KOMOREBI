#!/usr/bin/env python3
"""Compile the standalone Paper VI visual guide in three TeX passes."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--check-only', action='store_true', help='Build in isolation and leave the delivered PDF untouched.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    destination = (args.output_dir or root).resolve()
    env = dict(os.environ, SOURCE_DATE_EPOCH='1791158400', FORCE_SOURCE_DATE='1')
    with tempfile.TemporaryDirectory(prefix='paper_vi_visual_') as tmp:
        stage = Path(tmp)
        shutil.copy2(root / 'Paper_VI_Visual_Guide_Final.tex', stage)
        for name in ('source', 'graphics'):
            shutil.copytree(root / name, stage / name)
        logs = []
        for number in range(1, 4):
            result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                'Paper_VI_Visual_Guide_Final.tex'], cwd=stage, env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logs.append(result.stdout)
            if result.returncode:
                destination.mkdir(parents=True, exist_ok=True)
                (destination / f'build_pass_{number}.txt').write_text(result.stdout)
                raise SystemExit(f'Build failed on pass {number}; inspect build_pass_{number}.txt')
        log = (stage / 'Paper_VI_Visual_Guide_Final.log').read_text()
        invalid = [line for line in log.splitlines() if any(x in line for x in
            ('Overfull', 'undefined references', 'undefined on input', 'Missing character:'))]
        if invalid:
            raise SystemExit('Final build warnings: ' + '\n'.join(invalid))
        if args.check_only:
            print('PASS: isolated three-pass build; delivered files unchanged.')
        else:
            destination.mkdir(parents=True, exist_ok=True)
            for suffix in ('pdf', 'log', 'aux'):
                shutil.copy2(stage / f'Paper_VI_Visual_Guide_Final.{suffix}', destination)
            for number, output in enumerate(logs, 1):
                (destination / f'build_pass_{number}.txt').write_text(output)
            print(destination / 'Paper_VI_Visual_Guide_Final.pdf')

if __name__ == '__main__':
    main()
