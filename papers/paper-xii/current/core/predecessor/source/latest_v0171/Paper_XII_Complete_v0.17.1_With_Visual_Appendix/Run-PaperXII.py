#!/usr/bin/env python3
"""Run bundle tasks in disposable build copies, preserving all shipped evidence."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def run(command: list[str], cwd: Path) -> None:
    print('Running:', ' '.join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)

def workcopy(source: str, name: str, fresh: bool) -> Path:
    target = ROOT / 'build' / name
    if target.exists():
        if not fresh:
            raise RuntimeError(f'{target} already exists. Add --fresh to replace only this build copy.')
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / source, target)
    return target

def bash() -> str:
    program = shutil.which('bash')
    if program is None:
        raise RuntimeError('Bash is required for this task. Use the documented Linux/WSL environment.')
    return program

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('task', choices=['verify', 'examples', 'figures', 'appendix', 'manuscript', 'pdfs', 'lean'])
    ap.add_argument('--kit', type=Path, help='Existing Komorebi portable Lean 4.34.0-rc2 kit root (Linux/WSL).')
    ap.add_argument('--fresh', action='store_true', help='Replace only the selected disposable build copy.')
    args = ap.parse_args()
    if args.task == 'verify':
        run([sys.executable, str(ROOT / 'tools/verify_bundle.py')], ROOT)
    elif args.task == 'figures':
        target = ROOT / 'build/original_figures'
        if target.exists():
            if not args.fresh:
                raise RuntimeError(f'{target} exists. Add --fresh to replace this generated output.')
            shutil.rmtree(target)
        run([sys.executable, str(ROOT / 'tools/generate_original_figures.py'), '--output', str(target)], ROOT)
        print('Original figure outputs:', target)
    elif args.task in ('examples', 'appendix'):
        w = workcopy('visual_appendix', args.task, args.fresh)
        script = w / ('checks/verify_examples.py' if args.task == 'examples' else 'build.py')
        run([sys.executable, str(script)], w)
        print('Outputs and fresh records:', w)
    elif args.task in ('manuscript', 'pdfs'):
        w = workcopy('formal_release/paper', 'manuscript', args.fresh)
        run([bash(), str(w / 'Build-Paper.sh')], w)
        print('Manuscript output:', w / 'Paper_XII_Revised_Formalization_Complete_v0.17.0.pdf')
        if args.task == 'pdfs':
            a = workcopy('visual_appendix', 'appendix', args.fresh)
            shutil.copy2(w / 'Paper_XII_Revised_Formalization_Complete_v0.17.0.pdf',
                         a / 'original/Paper_XII_v0.17.0.pdf')
            run([sys.executable, str(a / 'build.py')], a)
            print('Rebuilt combined PDF:', a / 'Paper_XII_With_Visual_Appendix.pdf')
    elif args.task == 'lean':
        if args.kit is None:
            raise RuntimeError('The lean task requires --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2')
        kit = args.kit.expanduser().resolve()
        if not (kit / 'toolchain/bin/lean').is_file() or not (kit / 'workspace').is_dir():
            raise RuntimeError('The supplied --kit does not contain toolchain/bin/lean and workspace/.')
        w = workcopy('formal_release', 'lean_replay', args.fresh)
        run([bash(), str(w / 'Run-Reverified.sh'), str(kit)], w)
        print('Fresh Lean replay evidence:', w)
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
        print(f'FAILED: {e}', file=sys.stderr)
        raise SystemExit(1)
