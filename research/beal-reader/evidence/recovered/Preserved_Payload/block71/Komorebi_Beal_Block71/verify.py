#!/usr/bin/env python3
"""Replay Block71's declared checks, preserving immutable inputs.

Standard library only. Default replay does not rerun the historical chain.
Reports must be written outside the package. All tampering is in temporary copies.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parent
RESULTS = ('work71/verification/fixed_seven71.json',
           'work71/verification/independent_fixed_seven71.json')


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def relative_path(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts, 'Unsafe relative path: ' + name)
    dest = root.joinpath(*p.parts)
    require(dest.resolve().is_relative_to(root.resolve()), 'Path escapes root: ' + name)
    return dest


def integrity(root: Path) -> dict:
    manifest = json.loads((root/'MANIFEST.json').read_text())
    wanted = set(manifest['payloads']) | {'MANIFEST.json'}
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(actual == wanted, 'Payload file set mismatch')
    for name, expected in manifest['payloads'].items():
        require(digest(relative_path(root, name)) == expected, 'Payload hash changed: ' + name)
    record = json.loads((root/'work71/source_records/INHERITED_INPUTS.json').read_text())
    ancestor = root/'predecessor'/record['predecessor']
    require(digest(ancestor) == record['sha256'], 'Changed predecessor archive')
    # Reuse decoded ancestors. Their source bytes are already pinned by the outer ZIP.
    cache: dict[tuple[str, ...], bytes] = {(): ancestor.read_bytes()}
    checked = []
    for item in record['pinned_members']:
        prefix: tuple[str, ...] = ()
        for part in item['archive_chain']:
            key = prefix + (part,)
            if key not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[prefix])) as archive:
                    cache[key] = archive.read(part)
            prefix = key
        with zipfile.ZipFile(io.BytesIO(cache[prefix])) as archive:
            leaf = archive.read(item['member'])
        require(digest_bytes(leaf) == item['sha256'], 'Changed inherited source: '+item['member'])
        require(relative_path(root, item['copy']).read_bytes() == leaf, 'Changed source copy: '+item['copy'])
        checked.append({'member': item['member'], 'archive_depth': len(prefix)+1,
                        'copy': item['copy'], 'sha256': item['sha256']})
    return {'payload_count': len(manifest['payloads']), 'predecessor_sha256': record['sha256'],
            'pinned_source_count': len(checked), 'max_archive_depth': max(x['archive_depth'] for x in checked),
            'sources': checked}


def execute(argv: list[str], cwd: Path, *, timeout: int = 600) -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0',
               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    start = time.perf_counter()
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return {'argv': argv, 'runtime_seconds': time.perf_counter()-start,
                'exit_code': p.returncode, 'stdout': p.stdout, 'status': 'completed'}
    except subprocess.TimeoutExpired as err:
        out = err.stdout or ''
        if isinstance(out, bytes):
            out = out.decode(errors='replace')
        return {'argv': argv, 'runtime_seconds': time.perf_counter()-start,
                'exit_code': None, 'stdout': out, 'status': 'timeout'}


def safe_extract(archive: Path, dest: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP members')
        for name in names:
            relative_path(dest, name)
        z.extractall(dest)


def new_checks(root: Path, work: Path) -> dict:
    scratch = work/'new_replay'
    shutil.copytree(root, scratch)
    record_validation = execute([sys.executable, '-B', 'work71/computations/validate_v1_record.py',
                                 'work71/verification/COMPUTATION_MANIFEST.json', '--root', str(scratch)], scratch)
    require(record_validation['exit_code'] == 0, 'Computation manifest validation failed')
    computation_record = json.loads((scratch/'work71/verification/COMPUTATION_MANIFEST.json').read_text())
    for item in computation_record['input_artifacts']:
        require(item['sha256'] == item['sha256_after'] == digest(scratch/item['path']),
                'Changed computation record input: '+item['path'])
    before = {p: digest(root/p) for p in RESULTS}
    for name in RESULTS:
        (scratch/name).unlink()
    primary = execute([sys.executable, '-B', 'work71/computations/fixed_seven71.py',
                       '--output', RESULTS[0]], scratch)
    require(primary['exit_code'] == 0, 'Primary finite checks did not complete: '+str(primary))
    secondary = execute([sys.executable, '-B', 'work71/computations/independent_fixed_seven71.py',
                         '--certificate', RESULTS[0], '--output', RESULTS[1]], scratch)
    require(secondary['exit_code'] == 0, 'Separate finite checks did not complete: '+str(secondary))
    for name in RESULTS:
        require(digest(scratch/name) == before[name], 'Recomputed JSON differs: '+name)
    baseline = json.loads((scratch/RESULTS[0]).read_text())
    # Each specified alteration must be rejected for the intended scientific reason.
    corruptions = [
      ('named_unit', lambda x: x['named_unit_classes']['phi'].__setitem__(1, 4), 'Changed named unit class'),
      ('actual_RM', lambda x: x['compatible_root_matrices'][0].__setitem__(0, 2), 'Changed RM centralizer'),
      ('fermat_quotient', lambda x: x['fermat_by_A'].__setitem__('1', 1), 'Changed Fermat quotient'),
      ('accepted_count', lambda x: x.__setitem__('accepted_coefficient_A_triples', 0), 'Changed accepted count'),
      ('false_pattern_exclusion', lambda x: x.__setitem__('eliminated_predecessor_patterns', 8), 'False bounded exclusion'),
      ('hensel_root', lambda x: x['local_root_certificates'][0].__setitem__('B_mod_7pow18', 0), 'Changed 7-adic root certificate'),
      ('false_full_torsion', lambda x: x['negative_controls'].__setitem__('full_local_J7_rational_at7', True), 'False full torsion claim'),
    ]
    bad_path = work/'deliberately_corrupted.json'
    out_path = work/'corrupted_output.json'
    negative = []
    for name, change, diagnostic in corruptions:
        bad = copy.deepcopy(baseline)
        change(bad)
        bad_path.write_text(json.dumps(bad))
        if out_path.exists():
            out_path.unlink()
        job = execute([sys.executable, '-B', 'work71/computations/independent_fixed_seven71.py',
                       '--certificate', str(bad_path), '--output', str(out_path)], scratch)
        require(job['exit_code'] is not None and job['exit_code'] != 0 and diagnostic in job['stdout'],
                'Corruption not correctly rejected: '+name+' '+str(job))
        negative.append({'name': name, 'expected_diagnostic': diagnostic, 'rejected': True, 'execution': job})
    # An integrity-only subprocess must reject a modified payload before computation.
    old_readme = (scratch/'README.md').read_bytes()
    (scratch/'README.md').write_bytes(old_readme+b'\nDELIBERATE TAMPER\n')
    job = execute([sys.executable, '-B', 'verify.py', '--integrity-only'], scratch)
    require(job['exit_code'] is not None and job['exit_code'] != 0
            and 'Payload hash changed: README.md' in job['stdout'], 'Modified payload was not rejected')
    negative.append({'name': 'payload', 'expected_diagnostic': 'Payload hash changed: README.md',
                     'rejected': True, 'execution': job})
    (scratch/'README.md').write_bytes(old_readme)
    integrity(scratch)
    return {'computation_record_validation': record_validation, 'outputs_deleted_and_regenerated': list(RESULTS), 'output_sha256': before,
            'primary': primary, 'separate_implementation': secondary, 'negative_controls': negative,
            'finite_summary': {k: baseline[k] for k in ('unit_domain','principal_unit_inputs_mod343',
              'root_matrices_tested','period_unit_pairs','coefficient_A_triples','gauge_tests',
              'accepted_coefficient_A_triples','bounded_pattern_A_pairs','eliminated_predecessor_patterns')}}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path)
    p.add_argument('--integrity-only', action='store_true')
    p.add_argument('--replay-predecessor', action='store_true')
    args = p.parse_args()
    if args.report and args.report.resolve().is_relative_to(ROOT):
        p.error('--report must be outside the immutable package')
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    start = time.perf_counter()
    report: dict = {
      'schema': 'beal.block71.execution.v1', 'status': 'RUNNING', 'started_at': started,
      'environment': {'python': sys.version, 'platform': platform.platform(),
                      'bytecode_disabled': True, 'threads_per_scientific_process': 1},
      'scope': 'Immediate Block71 finite assertions; predecessor replay only when requested.',
      'proof_boundary': ['Written analytic and actual-representation implications are not certified by finite execution.',
                         'No new Lean compilation or independent mathematical review.',
                         'Eight predecessor patterns remain; no global branch closure.'],
      'resource_contract': {'each_subprocess_timeout_seconds': 600,
                            'predecessor_timeout_seconds_if_requested': 1200,
                            'memory_limit_bytes': None, 'randomness_used': False}}
    code = 0
    try:
        report['integrity'] = integrity(ROOT)
        if not args.integrity_only:
            with tempfile.TemporaryDirectory(prefix='beal71_') as td:
                work = Path(td)
                report['scientific_replay'] = new_checks(ROOT, work)
                if args.replay_predecessor:
                    destination = work/'predecessor_replay'
                    destination.mkdir()
                    source = next((ROOT/'predecessor').glob('*.zip'))
                    safe_extract(source, destination)
                    roots = list(destination.glob('*/verify.py'))
                    require(len(roots) == 1, 'Unexpected predecessor root')
                    target = work/'Block70_OptionalReplay.json'
                    job = execute([sys.executable, '-B', 'verify.py', '--report', str(target)],
                                  roots[0].parent, timeout=1200)
                    require(job['exit_code'] == 0 and target.is_file(), 'Optional predecessor replay failed')
                    r = json.loads(target.read_text())
                    require(r.get('status') == 'PASS_DECLARED_CHECKS', 'Predecessor status not accepted')
                    report['optional_immediate_predecessor'] = {'execution': job, 'report': r,
                                                               'full_historical_chain_requested': False}
        report['integrity_after'] = integrity(ROOT)
        report['status'] = 'PASS_INTEGRITY_ONLY' if args.integrity_only else 'PASS_DECLARED_CHECKS'
    except Exception as exc:
        code = 1
        report['status'] = 'FAILED'
        report['error'] = type(exc).__name__+': '+str(exc)
        print(report['error'], file=sys.stderr)
    report['runtime_seconds'] = time.perf_counter()-start
    report['exit_status'] = code
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
    print(report['status'], f"{report['runtime_seconds']:.3f}s")
    return code

if __name__ == '__main__':
    raise SystemExit(main())
