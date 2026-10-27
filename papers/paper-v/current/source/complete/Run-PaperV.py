#!/usr/bin/env python3
"""Verify or reproduce the Paper V reader's bundle without changing its source trees.

Python 3.10+. 'verify' uses only the standard library. Other modes need the
requirements described in START_HERE.md. No mode invokes Lean.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)

def verify() -> None:
    manifest = json.loads((ROOT / 'FILE_MANIFEST.json').read_text(encoding='utf8'))
    entries = manifest['files']
    for relative, expected in entries.items():
        path = ROOT / relative
        require(path.is_file() and not path.is_symlink(), f'Missing or linked file: {relative}')
        require(ROOT in path.resolve().parents, f'Unsafe manifest path: {relative}')
        require(sha(path) == expected, f'Checksum mismatch: {relative}')
    baseline = json.loads((ROOT / 'verification/ORIGINAL_SNAPSHOT_HASHES.json').read_text(encoding='utf8'))
    # The original inventory is a direct mapping, not a newly inferred census.
    if 'files' in baseline:
        baseline = baseline['files']
    for relative, expected in baseline.items():
        require(sha(ROOT / 'original_snapshot' / relative) == expected,
                f'Original source was changed: {relative}')
    print(f'PASS: {len(entries)} distributed file hashes and {len(baseline)} original files verified.')
    print('This is an integrity check, not a fresh Lean build.')

def output_directory(value: Path) -> Path:
    path = value.resolve()
    for protected in (ROOT / 'original_snapshot', ROOT / 'visual_appendix', ROOT / 'verification', ROOT / 'reading'):
        require(path != protected and protected not in path.parents,
                'Use an output directory outside the preserved source/evidence trees.')
    require(path != ROOT, 'Use a separate output directory, not the bundle root.')
    path.mkdir(parents=True, exist_ok=True)
    return path

def examples(out: Path) -> None:
    # Work in isolation: rerunning a timestamped audit must not mutate its shipped copy.
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    with tempfile.TemporaryDirectory(prefix='paper_v_examples_') as td:
        work = Path(td)
        shutil.copytree(ROOT / 'visual_appendix/source', work / 'source',
                        ignore=shutil.ignore_patterns('__pycache__'))
        (work / 'checks').mkdir()
        shutil.copy2(ROOT / 'visual_appendix/checks/verify_examples.py', work / 'checks/verify_examples.py')
        with (out / 'exact_examples.log').open('w', encoding='utf8') as log:
            process = subprocess.run([sys.executable, '-W', 'error', 'checks/verify_examples.py'],
                                     cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        require(process.returncode == 0, f'Example replay failed: {out / "exact_examples.log"}')
        record = json.loads((work / 'checks/EXACT_CHECKS.json').read_text(encoding='utf8'))
        require(record['status'] == 'PASS', 'Example report did not pass.')
        shutil.copy2(work / 'checks/EXACT_CHECKS.json', out / 'EXACT_CHECKS.json')
        print(f'PASS: {record["checks_passed"]} exact checks; '
              f'{len(record["invalid_controls_rejected"])} false controls rejected.')

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['verify', 'examples', 'build', 'original-checks'])
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'rebuilt')
    args = parser.parse_args()
    if args.command == 'verify':
        verify()
        return
    out = output_directory(args.output_dir)
    if args.command == 'examples':
        examples(out)
    else:
        script = (ROOT / 'visual_appendix/build.py' if args.command == 'build'
                  else ROOT / 'tools/audit_original.py')
        process = subprocess.run([sys.executable, str(script), '--output-dir', str(out)], cwd=ROOT)
        require(process.returncode == 0, f'{args.command} failed. Inspect {out} for retained logs.')

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit(f'FAILED: {exc}') from exc
