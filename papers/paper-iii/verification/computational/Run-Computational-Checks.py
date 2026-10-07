#!/usr/bin/env python3
"""Rerun existing Paper III checks in temporary copies; never installs or runs Lean.

Requires NumPy, Matplotlib, and Pillow. SymPy 1.14.0 enables the optional exact
visual stage. Missing SymPy records an explicitly incomplete verification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and not any(x in p.parts for x in ('.lake', '__pycache__'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('finite-root', 'expanded-root', 'visual-root', 'output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--command-timeout', type=int, default=120)
    args = parser.parse_args()
    roots = {name: getattr(args, name + '_root').resolve()
             for name in ('finite', 'expanded', 'visual')}
    output = args.output_dir.resolve()
    if output.exists() or any(output.is_relative_to(p) for p in roots.values()):
        raise SystemExit('Output must be a new directory outside all source trees.')
    output.mkdir(parents=True)
    start = time.monotonic()
    before = {name: inventory(root) for name, root in roots.items()}
    commands = []
    result = {'started_utc': datetime.now(timezone.utc).isoformat(),
              'software': {'Python': platform.python_version()},
              'scope': 'Existing bounded examples and source integrity only; no new Lean compilation.',
              'input_roots': {k: str(v) for k, v in roots.items()}}
    for name in ('numpy', 'sympy', 'matplotlib', 'pillow', 'PyMuPDF', 'pypdf'):
        try:
            result['software'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result['software'][name] = None
    env = os.environ.copy()
    env.update({'PYTHONDONTWRITEBYTECODE': '1', 'MPLBACKEND': 'Agg',
                'SOURCE_DATE_EPOCH': '1788393600', 'TZ': 'UTC',
                'PATH': str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')})
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
        env[name] = '1'

    def run(name, argv, cwd):
        t0 = time.monotonic()
        rec = {'name': name, 'argv': [str(x) for x in argv], 'cwd': str(cwd),
               'started_utc': datetime.now(timezone.utc).isoformat(), 'timed_out': False}
        with (output / (name + '.stdout.txt')).open('wb') as out, \
                (output / (name + '.stderr.txt')).open('wb') as err:
            proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err,
                                    start_new_session=True)
            try:
                rec['exit_code'] = proc.wait(timeout=args.command_timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                rec['exit_code'] = proc.wait()
                rec['timed_out'] = True
        rec['seconds'] = round(time.monotonic() - t0, 6)
        rec['stdout'] = name + '.stdout.txt'
        rec['stderr'] = name + '.stderr.txt'
        commands.append(rec)
        print(name, 'exit=' + str(rec['exit_code']), flush=True)
        return rec['exit_code'] == 0

    with tempfile.TemporaryDirectory(prefix='paperIII-checks-') as tmp_name:
        tmp = Path(tmp_name)
        copies = {}
        for name, root in roots.items():
            copies[name] = tmp / name
            shutil.copytree(root, copies[name], ignore=shutil.ignore_patterns('.lake', '__pycache__'))
        env['MPLCONFIGDIR'] = str(tmp / 'mplconfig')
        offline = run('finite_release_integrity', ['bash', str(copies['finite'] / 'VERIFY.sh')], copies['finite'])
        release = json.loads((roots['finite'] / 'RELEASE.json').read_text())
        result['finite_integrity'] = {
            'offline_checker_passed': offline,
            'file_count': len(before['finite']),
            'checksum_entries': len((roots['finite'] / 'SHA256SUMS.txt').read_text().splitlines()),
            'interpretation': 'Static checks authenticate shipped bytes and internal report/transcript parity; they do not rerun Lean.'}
        result['inherited_lean_report'] = {
            'date': release['release_date'],
            'formalization': release['verification']['formalization'],
            'fresh_compilation': False,
            'transcript_sha256': sha(roots['finite'] / 'kernel_audit_output.txt'),
            'report_sha256': sha(roots['finite'] / 'provenance/VERIFICATION_REPORT.md')}
        expanded = run('expanded_verification',
                       [sys.executable, str(copies['expanded'] / 'verification/verify_strengthened.py')], copies['expanded'])
        expanded_text = (output / 'expanded_verification.stdout.txt').read_text()
        result['expanded_examples'] = {'passed': expanded, 'groups_passed': expanded_text.count('PASS:'),
                                      'expected_groups': 11,
                                      'arithmetic': 'Mixed exact integer/combinatorial checks and NumPy float64 examples with explicit tolerances.'}
        for p in (copies['finite'] / 'paper/figures').glob('*.png'):
            p.unlink()
        figures = run('canonical_figure_regeneration',
                      [sys.executable, str(copies['finite'] / 'paper/scripts/generate_figures.py')], copies['finite'] / 'paper')
        entries = []
        if figures:
            from PIL import Image, ImageChops
            for shipped in sorted((roots['finite'] / 'paper/figures').glob('*.png')):
                fresh = copies['finite'] / 'paper/figures' / shipped.name
                with Image.open(shipped) as a, Image.open(fresh) as b:
                    same_dimensions = a.size == b.size
                    pixel_same = same_dimensions and ImageChops.difference(a.convert('RGBA'), b.convert('RGBA')).getbbox() is None
                entries.append({'name': shipped.name, 'shipped_sha256': sha(shipped), 'fresh_sha256': sha(fresh),
                                'byte_identical': sha(shipped) == sha(fresh), 'pixel_identical': pixel_same})
        result['canonical_figures'] = {'generator_succeeded': figures, 'count': len(entries), 'entries': entries,
                                       'interpretation': 'Deterministic schematic regeneration, not additional mathematical tests.'}
        shipped_report = json.loads((roots['visual'] / 'checks/EXACT_CHECKS.json').read_text())
        result['inherited_visual_evidence'] = {
            'date': shipped_report['generated_utc'],
            'checks_passed': shipped_report['checks_passed'],
            'invalid_controls_rejected': len(shipped_report['invalid_controls_rejected']),
            'models_hash_matches': shipped_report['models_sha256'] == sha(roots['visual'] / 'source/models.py'),
            'checker_hash_matches': shipped_report['checker_sha256'] == sha(roots['visual'] / 'checks/verify_examples.py')}
        visual_available = importlib.util.find_spec('sympy') is not None
        result['visual_examples'] = {'executed': False, 'status': 'unavailable',
                                     'reason': 'SymPy is not installed; no dependency installation is attempted by this runner.'}
        result['visual_figures'] = {'executed': False, 'status': 'unavailable'}
        if visual_available:
            (copies['visual'] / 'checks/EXACT_CHECKS.json').unlink()
            visual_ok = run('exact_visual_examples', [sys.executable, str(copies['visual'] / 'checks/verify_examples.py')], copies['visual'])
            fresh_report = copies['visual'] / 'checks/EXACT_CHECKS.json'
            vr = json.loads(fresh_report.read_text()) if fresh_report.exists() else {}
            is_fresh = bool(vr) and vr['generated_utc'] != shipped_report['generated_utc']
            result['visual_examples'] = {'executed': True, 'passed': visual_ok and is_fresh,
                                         'checks_passed': vr['checks_passed'] if visual_ok and is_fresh else None,
                                         'controls_rejected': len(vr['invalid_controls_rejected']) if visual_ok and is_fresh else None}
            if visual_ok and is_fresh:
                shutil.copy2(fresh_report, output / 'EXACT_CHECKS.json')
            for p in (copies['visual'] / 'graphics').glob('*.tex'):
                p.unlink()
            graphics_ok = run('visual_graphics_regeneration', [sys.executable, str(copies['visual'] / 'source/generate_graphics.py')], copies['visual'])
            original = {p.name: sha(p) for p in (roots['visual'] / 'graphics').glob('*.tex')}
            regenerated = {p.name: sha(p) for p in (copies['visual'] / 'graphics').glob('*.tex')}
            result['visual_figures'] = {'executed': True, 'generator_succeeded': graphics_ok,
                                        'count': len(regenerated), 'byte_identical': original == regenerated,
                                        'original_sha256': original, 'regenerated_sha256': regenerated}
    after = {name: inventory(root) for name, root in roots.items()}
    source_unchanged = before == after
    (output / 'source_hashes_before.json').write_text(json.dumps(before, indent=2) + '\n')
    (output / 'source_hashes_after.json').write_text(json.dumps(after, indent=2) + '\n')
    result.update({'source_trees_unchanged': source_unchanged, 'commands': commands,
                   'runtime_seconds': round(time.monotonic() - start, 6)})
    hard_fail = (not offline or not expanded or result['expanded_examples']['groups_passed'] != 11
                 or not figures or len(entries) != 3 or not source_unchanged
                 or not all(row['byte_identical'] for row in entries))
    if visual_available:
        hard_fail = (hard_fail or not result['visual_examples']['passed']
                     or result['visual_examples']['checks_passed'] != 124
                     or result['visual_examples']['controls_rejected'] != 4
                     or not result['visual_figures']['generator_succeeded']
                     or result['visual_figures']['count'] != 22
                     or not result['visual_figures']['byte_identical'])
    result['status'] = 'FAIL' if hard_fail else 'PASS' if visual_available else 'PARTIAL: visual rerun unavailable'
    (output / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], flush=True)
    raise SystemExit(1 if hard_fail else 0)


if __name__ == '__main__':
    main()
