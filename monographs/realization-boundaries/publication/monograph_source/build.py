#!/usr/bin/env python3
"""Rebuild the monograph offline after installing its documented dependencies.

Exact tests are optional here and separate from the ordinary mathematical proofs.
The script never downloads dependencies or pretends to verify Lean declarations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print('+ ' + ' '.join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Replay all exact-arithmetic and release-contract suites.')
    parser.add_argument('--figures', action='store_true', help='Regenerate vector figures with Matplotlib.')
    args = parser.parse_args()
    output = ROOT / 'verification' / 'tex_build'
    output.mkdir(parents=True, exist_ok=True)
    try:
        if args.verify:
            for script, report in [('exact_checks.py', 'exact_checks.json'),
                                   ('supplemental_checks.py', 'supplemental_checks.json'),
                                   ('release_checks.py', 'release_checks.json')]:
                run([sys.executable, str(ROOT / 'src' / script), '--output',
                     str(ROOT / 'verification' / report)])
            core = json.loads((ROOT / 'verification' / 'exact_checks.json').read_text())
            extra = json.loads((ROOT / 'verification' / 'supplemental_checks.json').read_text())
            release = json.loads((ROOT / 'verification' / 'release_checks.json').read_text())
            if any(report['status'] != 'PASS' for report in (core, extra, release)):
                raise RuntimeError('An exact-arithmetic report did not pass.')
            counts = [('BaseAssertions', core['total_assertions']),
                      ('ExtraAssertions', extra['total_assertions']),
                      ('ReleaseAssertions', release['total_assertions']),
                      ('AllAssertions', core['total_assertions'] + extra['total_assertions'] + release['total_assertions'])]
            (ROOT / 'manuscript' / 'verification_counts.tex').write_text(
                ''.join(f'\\newcommand{{\\{name}}}{{{value:,}}}\n' for name, value in counts),
                encoding='utf-8')
        if args.figures:
            run([sys.executable, str(ROOT / 'src' / 'make_figures.py')])
        latexmk = shutil.which('latexmk')
        if latexmk is None:
            raise RuntimeError('latexmk was not found. Install a TeX distribution before rebuilding.')
        run([latexmk, '-pdf', '-interaction=nonstopmode', '-halt-on-error',
             '-outdir=../verification/tex_build', 'monograph.tex'], cwd=ROOT / 'manuscript')
        source = output / 'monograph.pdf'
        if not source.is_file():
            raise RuntimeError('The TeX process completed without producing the expected PDF.')
        destination = ROOT / 'Realization_Boundaries_Monograph.pdf'
        shutil.copy2(source, destination)
        print(f'Created {destination}', flush=True)
        return 0
    except (subprocess.CalledProcessError, RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f'Build failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
