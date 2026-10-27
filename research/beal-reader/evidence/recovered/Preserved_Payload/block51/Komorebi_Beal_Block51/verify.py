#!/usr/bin/env python3
"""Replay the declared Beal Block 51 checks without modifying the package.

Python 3.10+, standard library only. This verifies finite arithmetic and
file integrity, not the universal prose proofs or the Beal conjecture.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def package_audit(root: Path) -> dict:
    manifest = root / 'PACKAGE_SHA256SUMS.txt'
    expected: dict[str, str] = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, rel = line.split('  ', 1)
        target = (root / rel).resolve()
        require(target.is_relative_to(root), f'Unsafe manifest path: {rel}')
        require(len(digest) == 64 and rel not in expected, 'Invalid/duplicate hash record')
        require(target.is_file(), f'Missing payload: {rel}')
        require(sha(target) == digest, f'Payload hash mismatch: {rel}')
        expected[rel] = digest
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts
              and p.name != '.DS_Store' and p != manifest}
    require(actual == set(expected), f'Unexpected/missing package members: {actual ^ set(expected)}')
    original = json.loads((root/'work51/verification/PREDECESSOR_INTEGRITY.json').read_text())
    checked = 0
    for rel, digest in original['inherited_files'].items():
        if rel in ('README.md', 'PACKAGE_SHA256SUMS.txt'):
            continue  # New root navigation/checksums; originals are in their ZIP.
        require(sha(root / rel) == digest, f'Frozen predecessor changed: {rel}')
        checked += 1
    archive_checks = []
    for name, record in original['archives'].items():
        path = root / 'predecessor' / name
        require(sha(path) == record['sha256'], f'Original archive changed: {name}')
        with zipfile.ZipFile(path) as archive:
            require(archive.testzip() is None, f'CRC failure: {name}')
        archive_checks.append(name)
    return {'status': 'PASS_BYTE_INTEGRITY', 'payload_hashes_checked': len(expected),
            'frozen_predecessor_files_checked': checked, 'original_archives_crc_checked': archive_checks,
            'intentional_root_replacements': ['README.md', 'PACKAGE_SHA256SUMS.txt'],
            'non_claim': 'Checksums and CRC do not prove mathematical correctness.'}


def jobs(legacy: bool) -> list[tuple[str, list[str], str]]:
    items = [('block51', ['work51/computations/depth_checks.py', '--output',
                        'work51/verification/depth_result.json'], 'work51/verification/depth_result.json')]
    if legacy:
        items += [
            ('local_types', ['work49/computations/local_types_exact.py'], 'work49/verification/local_types_run/result.json'),
            ('lastform', ['work49/computations/lastform_boundary.py', '--output', 'work49/verification/lastform_run/result.json'], 'work49/verification/lastform_run/result.json'),
            ('alt_elliptic', ['work49/computations/alt_elliptic_invariants.py'], 'work49/verification/alt_elliptic_run/result.json'),
            ('normalizer', ['work49/computations/lastform_normalizer.py', '--output', 'work49/verification/lastform_normalizer_run/result.json'], 'work49/verification/lastform_normalizer_run/result.json'),
            ('monodromy', ['work49/computations/lastform_monodromy.py', '--output', 'work49/verification/lastform_monodromy_run/result.json'], 'work49/verification/lastform_monodromy_run/result.json'),
            ('block50', ['work50/computations/extgeo_matrix_checks.py'], 'work50/verification/extgeo_run/result.json'),
        ]
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-predecessors', action='store_true')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--timeout', type=float, default=120.0,
                        help='Per-process wall seconds, positive; timeouts are inconclusive.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    report_path = (args.report or root.parent / (root.name + '_replay.json')).resolve()
    require(not report_path.is_relative_to(root), 'Write the replay report outside the immutable package.')
    require(args.timeout > 0, 'Timeout must be positive.')
    report = {'schema': 'komorebi.beal.portable-verifier.v1',
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
              'argv': sys.argv, 'random_seed': None, 'ordering': 'deterministic',
              'arithmetic': 'integers, exact Fraction arithmetic, and Q(sqrt(5)) rational pairs',
              'resource_caps': {'per_process_wall_seconds': args.timeout,
                                'cpu_limit_imposed_by_runner': None, 'memory_limit_imposed_by_runner': None},
              'runs': [], 'status': 'NOT_COMPLETED',
              'non_claims': ['No Beal proof', 'No Lean certification',
                             'No global realization of local examples', 'No universal conclusion from finite range alone']}
    start = time.monotonic()
    try:
        report['package_integrity'] = package_audit(root)
        load_bearing = [p for p in root.rglob('*') if p.is_file() and
                        (p.suffix in ('.py', '.html') or p.relative_to(root).as_posix().startswith('work51/notes/'))]
        before = {p.relative_to(root).as_posix(): sha(p) for p in sorted(load_bearing)}
        report['input_hashes_before'] = before
        with tempfile.TemporaryDirectory(prefix='beal51-replay-') as tmp:
            scratch = Path(tmp) / 'project'
            shutil.copytree(root, scratch, ignore=shutil.ignore_patterns('predecessor', '__pycache__', '.DS_Store'))
            env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
            for label, params, result_rel in jobs(args.replay_predecessors):
                argv = [sys.executable, *params]
                result_path = scratch / result_rel
                frozen = json.loads((root/result_rel).read_text(encoding='utf-8'))
                result_path.unlink(missing_ok=True)  # A stale result can never count as a replay.
                result_path.parent.mkdir(parents=True, exist_ok=True)
                row = {'label': label, 'argv': argv, 'cwd': str(scratch),
                       'started_utc': datetime.now(timezone.utc).isoformat(),
                       'script_sha256_before': sha(scratch/params[0]),
                       'reference_result_sha256': sha(root/result_rel)}
                tick = time.monotonic()
                try:
                    run = subprocess.run(argv, cwd=scratch, env=env, capture_output=True,
                                         text=True, encoding='utf-8', errors='replace', timeout=args.timeout)
                    row.update(exit_code=run.returncode, timed_out=False, stdout=run.stdout, stderr=run.stderr)
                    require(run.returncode == 0, f'{label}: exit {run.returncode}: {run.stderr}')
                    require(result_path.is_file(), f'{label}: no fresh result')
                    actual = json.loads(result_path.read_text(encoding='utf-8'))
                    row['result_sha256'] = sha(result_path)
                    row['result_matches_reference_json'] = actual == frozen
                    require(actual == frozen, f'{label}: different result from frozen reference')
                    row['script_sha256_after'] = sha(scratch/params[0])
                    require(row['script_sha256_after'] == row['script_sha256_before'], f'{label}: mutated source')
                    row['status'] = 'PASS_EXACT_REPLAY'
                    if label == 'block51':
                        report['block51_results'] = actual
                except subprocess.TimeoutExpired as exc:
                    row.update(status='INCONCLUSIVE_TIMEOUT', timed_out=True,
                               stdout=(exc.stdout or b'').decode('utf-8', 'replace') if isinstance(exc.stdout, bytes) else exc.stdout,
                               stderr=(exc.stderr or b'').decode('utf-8', 'replace') if isinstance(exc.stderr, bytes) else exc.stderr)
                    raise TimeoutError(f'{label}: time bound exceeded; no mathematical conclusion') from exc
                finally:
                    row['elapsed_seconds'] = time.monotonic() - tick
                    report['runs'].append(row)
                print(f'{label}: PASS_EXACT_REPLAY', flush=True)
        after = {rel: sha(root/rel) for rel in before}
        report['input_hashes_after'] = after
        require(before == after, 'Source/fixture hashes changed during replay')
        report['package_integrity_after'] = package_audit(root)
        report['status'] = 'PASS_DECLARED_REPLAYS_AND_BYTE_INTEGRITY'
    except TimeoutError as exc:
        report['status'] = 'INCONCLUSIVE_TIMEOUT'
        report['error'] = str(exc)
    except Exception as exc:
        report['status'] = 'FAILED_VERIFICATION'
        report['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        report['elapsed_seconds'] = time.monotonic() - start
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"{report['status']}\nReport: {report_path}", flush=True)
    return 0 if report['status'] == 'PASS_DECLARED_REPLAYS_AND_BYTE_INTEGRITY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
