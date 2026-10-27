#!/usr/bin/env python3
"""Execute a bounded verification mode without modifying source or baseline evidence."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import time
import zipfile

from check_integrity import verify as verify_integrity
from validate_manifest import validate as validate_manifest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAME = 'Komorebi_PNP_Complete_Packets_And_Projection_Block_2026-09-21.zip'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_safe(archive: Path, destination: Path) -> Path:
    """Reject traversal and symlink entries before extracting the pinned ZIP."""
    with zipfile.ZipFile(archive) as source:
        if sum(item.file_size for item in source.infolist()) > 64 * 1024 * 1024:
            raise ValueError('Archive exceeds the declared uncompressed size cap.')
        for item in source.infolist():
            path = (destination / item.filename).resolve()
            if not path.is_relative_to(destination.resolve()):
                raise ValueError(f'Unsafe archive path: {item.filename}')
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError(f'Archive symlink not allowed: {item.filename}')
        source.extractall(destination)
    return destination / 'komorebi_pnp_shared_generation'


def revision() -> tuple[str, bool]:
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                         stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT,
                                            stderr=subprocess.DEVNULL, text=True).strip())
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return 'unavailable: source archive; source seal identifies inputs', True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for mode in ('quick', 'full', 'history', 'all'):
        modes.add_argument('--' + mode, action='store_true')
    args = parser.parse_args()
    mode = next((m for m in ('all', 'history', 'full', 'quick') if getattr(args, m)), 'quick')
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE', '') not in ('', '0'):
        print('FAIL: optimized Python disables required scientific assertions.', file=sys.stderr)
        return 2
    try:
        integrity = verify_integrity(ROOT)
    except (ValueError, OSError, KeyError) as exc:
        print(f'FAIL: source integrity: {exc}', file=sys.stderr)
        return 2
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = ROOT / 'build/verification' / f'{stamp}-{mode}'
    out.mkdir(parents=True, exist_ok=False)
    logs = out / 'logs'
    logs.mkdir()
    started, timer = now(), time.perf_counter()
    sealed = json.loads((ROOT / 'integrity/SOURCE_SEAL.json').read_text(encoding='utf-8'))['files']
    pinned = sorted(set(sealed) | {'integrity/SOURCE_SEAL.json'})
    before = {p: sha(ROOT / p) for p in pinned}
    commit, dirty = revision()
    records, results, software = [], [], [{'name': 'Python', 'version': sys.version}]
    declared = [relative(out / 'summary.json')]
    if mode in ('full', 'all'):
        declared += [relative(out / 'active/results' / name) for name in (
            'completeness.json', 'projection.json', 'fingerprint.json',
            *[f'profiles{n}.bin' for n in range(1, 5)], 'degree_block02.json')]
    if mode in ('history', 'all'):
        declared.append(relative(out / 'historical_comparison.json'))
    status, exit_status, failure = 'completed', 0, None

    def execute(name: str, argv: list[str], cwd: Path, limit: int) -> None:
        start, launched = time.perf_counter(), now()
        log = logs / f'{name}.log'
        returncode, timed_out = None, False
        with log.open('w', encoding='utf-8') as stream:
            try:
                result = subprocess.run(argv, cwd=cwd, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=limit)
                returncode = result.returncode
            except subprocess.TimeoutExpired:
                returncode, timed_out = 124, True
                stream.write(f'\nTIMEOUT after {limit} seconds. Inconclusive.\n')
            except OSError as exc:
                stream.write(f'\nLAUNCH FAILED: {exc}\n')
                returncode = 127
        records.append({'name': name, 'argv': argv, 'cwd': relative(cwd),
                        'started_at': launched, 'elapsed_seconds': time.perf_counter() - start,
                        'wall_time_limit_seconds': limit, 'exit_status': returncode,
                        'log': relative(log), 'log_sha256': sha(log)})
        print(f'{name}: {"PASS" if returncode == 0 else "FAIL"}', flush=True)
        if timed_out:
            raise TimeoutError(f'{name}: see {relative(log)}')
        if returncode:
            raise RuntimeError(f'{name} exited {returncode}; see {relative(log)}')

    try:
        if mode != 'history':
            execute('quick_controls', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], ROOT, 120)
        if mode in ('full', 'all'):
            stage = out / 'active'
            (stage / 'results').mkdir(parents=True)
            shutil.copytree(ROOT / 'checks', stage / 'checks', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            cxx = shlex.split(os.environ.get('CXX', 'g++'))
            if not cxx:
                raise ValueError('CXX is empty.')
            version = subprocess.run(cxx + ['--version'], capture_output=True, text=True, timeout=15, check=True)
            software.append({'name': 'C++ compiler', 'version': version.stdout.splitlines()[0]})
            exe = stage / 'degree_profiles'
            if os.name == 'nt':
                exe = exe.with_suffix('.exe')
            execute('compile_profiles', cxx + ['-O2', '-std=c++17', str(stage / 'checks/degree_profiles.cpp'), '-o', str(exe)], stage, 60)
            for n in range(1, 5):
                execute(f'profiles{n}', [str(exe), str(n), str(stage / 'results' / f'profiles{n}.bin')], stage, 30)
            for checker in ('completeness', 'projection', 'fingerprint'):
                execute(checker, [sys.executable, str(stage / 'checks' / f'verify_{checker}.py')], stage, 120)
            expected = json.loads((ROOT / 'evidence/baseline/SHA256.json').read_text(encoding='utf-8'))
            for name, digest in expected.items():
                target = stage / 'results' / name
                if not target.is_file() or sha(target) != digest:
                    raise ValueError(f'Active scientific output differs from baseline: {name}')
                if name.endswith('.json'):
                    value = json.loads(target.read_text(encoding='utf-8'))
                    if value.get('status') != 'PASS':
                        raise ValueError(f'Nonpassing scientific report: {name}')
                results.append(relative(target))
            execute('degree_block02', [sys.executable, str(stage / 'checks/check_degree_block02.py'),
                    '--out', str(stage / 'results/degree_block02.json')], stage, 120)
            new_result = stage / 'results/degree_block02.json'
            if sha(new_result) != sha(ROOT / 'evidence/lean-block02/degree_controls.json'):
                raise ValueError('Block 02 exact finite result differs from the retained output.')
            results.append(relative(new_result))
        if mode in ('history', 'all'):
            archive = ROOT / 'archive/checkpoints' / SOURCE_NAME
            historical = extract_safe(archive, out / 'history')
            source_seal = json.loads((historical / 'ARTIFACT_SEAL.json').read_text(encoding='utf-8'))['files']
            for name, digest in source_seal.items():
                path = (historical / name).resolve()
                if not path.is_relative_to(historical.resolve()) or not path.is_file() or sha(path) != digest:
                    raise ValueError(f'Historical source seal mismatch: {name}')
            expected = json.loads((ROOT / 'evidence/baseline/SHA256.json').read_text(encoding='utf-8'))
            execute('historical_full_runner', [sys.executable, 'checks/run_all.py'], historical, 300)
            comparison = {name: sha(historical / 'results' / name) == digest for name, digest in expected.items()}
            if not all(comparison.values()):
                raise ValueError('Historical mathematical results do not match the sealed baseline.')
            target = out / 'historical_comparison.json'
            target.write_text(json.dumps({'status': 'PASS', 'archive_sha256': sha(archive),
                                         'source_sealed_files': len(source_seal),
                                         'scientific_outputs_equal': comparison,
                                         'scope': 'Pinned latest runner including its recursive historical replay.'}, indent=2) + '\n', encoding='utf-8')
            results.append(relative(target))
        if any(sha(ROOT / p) != digest for p, digest in before.items()):
            raise ValueError('An execution input changed during verification.')
    except TimeoutError as exc:
        status, exit_status, failure = 'timeout', 124, str(exc)
    except Exception as exc:
        status, exit_status, failure = 'failed', 1, str(exc)
    summary = {'status': 'PASS' if exit_status == 0 else 'FAIL', 'mode': mode,
               'source_integrity': integrity, 'subprocesses': len(records),
               'scientific_results_matched': len(results), 'failure': failure,
               'scope': 'Finite exact assertions and release reproduction; not universal formal verification.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    results.append(relative(out / 'summary.json'))
    after = {p: sha(ROOT / p) if (ROOT / p).is_file() else None for p in before}
    manifest = {
        'schema_version': 2, 'claim_id': 'Komorebi-Circuit-Obstructions-v' + (ROOT / 'VERSION').read_text().strip() + '-' + mode,
        'repository': {'commit': commit, 'dirty': dirty},
        'command': [sys.executable, 'scripts/verify.py', '--' + mode],
        'environment': {'software': software, 'hardware': platform.platform() + '; ' + platform.machine()},
        'mathematics': {
            'assertion_tested': 'Reproduce exact finite claim controls, canonical result files, and selected historical evidence in the declared verification mode.',
            'coefficient_domain': 'Exact integers, F2 truth tables, GF16 via t^4+t+1.',
            'conventions': 'Distinct-wire classical NCT gates; bit x is f(x); Toffoli and total gate costs are different.',
            'inputs': ['Versioned checkers, fixed baseline outputs, pinned archives, and generated bounded functions.'],
            'bounds': {'mode': mode, 'quick': 'all functions on 1..3 inputs and specified regression controls',
                       'full': 'profile tables 1..4 inputs; exact stated independent controls and family ranges in baseline JSON',
                       'history': 'pinned latest complete source runner; other archives only hash-checked'},
            'non_claims': ['Not a P-versus-NP proof.', 'This finite runner does not perform Lean verification; use verify_lean.py. No independent review or novelty audit.',
                           'Finite and sampled assertions retain their declared ranges.']},
        'randomness': {'used': mode in ('full', 'all', 'history'), 'generator': 'Python random.Random in fixed baseline controls', 'seed': 20260921},
        'run': {'started_at': started, 'finished_at': now(), 'runtime_seconds': time.perf_counter() - timer,
                'exit_status': exit_status, 'status': status, 'subprocesses': records,
                'resource_limits': {'memory_bytes': None, 'cpu_seconds': None, 'max_cores': None, 'max_threads': None},
                'limit_note': 'Per-command wall limits enforced; no extra OS memory/CPU/thread caps.'},
        'input_artifacts': [{'path': p, 'sha256': h, 'sha256_after': after[p]} for p, h in before.items()],
        'execution_artifacts': list(before), 'declared_results': declared,
        'outputs': ([{'path': p, 'sha256': sha(ROOT / p), 'kind': 'result'} for p in results] +
                    [{'path': r['log'], 'sha256': r['log_sha256'], 'kind': 'log'} for r in records]),
        'checks': ['Source-seal integrity', 'Bounded exact assertions for requested mode', 'Frozen scientific-output equality', 'Input hashes before/after'],
        'result': 'All requested finite checks passed.' if exit_status == 0 else 'Incomplete or failed execution: ' + str(failure),
        'residual_risks': ['Self-reviewed written mathematics, not a formal theorem certificate.', 'Runtime and compiler trusted.', 'Hosted CI not executed by local verification.']}
    if failure:
        manifest['run']['failure'] = failure
    path = out / 'manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    if exit_status == 0:
        errors = validate_manifest(manifest, root=ROOT, manifest_path=path)
        if errors:
            print('FAIL: manifest validation: ' + '; '.join(errors), file=sys.stderr)
            return 1
    print(json.dumps({'status': summary['status'], 'mode': mode, 'manifest': relative(path),
                      'seconds': manifest['run']['runtime_seconds'], 'failure': failure}, indent=2))
    return exit_status


if __name__ == '__main__':
    raise SystemExit(main())
