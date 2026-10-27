"""Rebuild the essay from sources. Requires Python 3.10+, matplotlib, numpy, and TeX Live.

The exact-check script uses the Python standard library only.
No Lean installation is used or claimed by this build.
"""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(args: list[str], log: Path | None = None) -> None:
    if log is None:
        subprocess.run(args, cwd=ROOT, check=True)
    else:
        with log.open('w', encoding='utf-8') as f:
            subprocess.run(args, cwd=ROOT, check=True, stdout=f, stderr=subprocess.STDOUT)


def main() -> int:
    if shutil.which('pdflatex') is None:
        print('Missing pdflatex. Install TeX Live or MiKTeX with the packages listed in README.md.', file=sys.stderr)
        return 2
    (ROOT/'audit').mkdir(exist_ok=True)
    try:
        run([sys.executable, 'exact_checks.py'])
        run([sys.executable, 'integrity_checks.py'])
        run([sys.executable, 'figures.py'])
        for i in range(1, 4):
            run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'Komorebi_Methodology.tex'], ROOT/'audit'/f'build_pass_{i}.log')
    except subprocess.CalledProcessError as exc:
        print(f'Build failed in {exc.cmd}. Exit code: {exc.returncode}. See audit logs where available.', file=sys.stderr)
        return exc.returncode or 1
    log = (ROOT/'audit'/'build_pass_3.log').read_text(errors='replace')
    issues = [line for line in log.splitlines() if any(key in line for key in ('Overfull', 'Underfull', 'LaTeX Warning:', 'Missing character:'))]
    if issues:
        print('PDF built, but typesetting review is required:\n'+'\n'.join(issues), file=sys.stderr)
        return 1
    print('Built Komorebi_Methodology.pdf; exact checks and final typesetting log passed.')
    print('Render and visually review the PDF after any editorial changes.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
