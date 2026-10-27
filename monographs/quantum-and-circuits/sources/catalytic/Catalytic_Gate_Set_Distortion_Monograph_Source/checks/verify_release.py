#!/usr/bin/env python3
"""Replay the finite catalytic evidence with input hashes and a v2 manifest.

Usage: python3 checks/verify_release.py --out verification/current
Requires Python 3.10+, g++ supporting C++20, Bash and diff. No Python packages
are required. The core supplement regenerates its disposable _build directory.
This verifies the stated finite assertions, not the unbounded conjectures.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'verification/current')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest_root = Path(os.path.commonpath([str(ROOT), str(out)]))
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    source_paths = [p for folder in ('code', 'checks', 'core_extract/supplement')
                    for p in (ROOT / folder).rglob('*')
                    if p.is_file() and p.suffix in ('.py', '.cpp', '.sh', '.json', '.out')
                    and not any(part in ('_build', 'build', '__pycache__') for part in p.relative_to(ROOT).parts)]
    before = {str(p.relative_to(ROOT)): digest(p) for p in source_paths}
    checks = []
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'code'),
               CATALYTIC_CENSUS_BINARY=str(out / 'clifford_census'))
    def run(label: str, argv: list[str], cwd: Path = ROOT) -> None:
        t = time.monotonic()
        proc = subprocess.run(argv, cwd=cwd, env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1200)
        (out / (label + '.log')).write_text(proc.stdout)
        checks.append({'name': label, 'argv': argv, 'exit_status': proc.returncode,
                       'runtime_seconds': time.monotonic() - t})
        if proc.returncode:
            raise RuntimeError(f'{label} failed with exit status {proc.returncode}')
    status, failure = 'completed', None
    try:
        run('compile_clifford', ['g++', '-O3', '-std=c++20',
            str(ROOT / 'code/scripts/clifford_census.cpp'), '-o', str(out / 'clifford_census')])
        run('small_atlas', [sys.executable, str(ROOT / 'code/scripts/run_atlas.py'),
            '--output', str(out / 'atlas_small.json')])
        assert (out / 'atlas_small.json').read_bytes() == (ROOT / 'results/atlas_small.json').read_bytes()
        for metric, swap in [('total', False), ('total', True), ('entangling', False)]:
            name = 'clifford_n3_' + metric + ('_swap' if swap else '')
            run(name, [str(out / 'clifford_census'), '--n', '3', '--metric', metric]
                + (['--swap'] if swap else []) + ['--output', str(out / (name + '.json'))])
            assert json.loads((out / (name + '.json')).read_text()) == json.loads((ROOT / 'results' / (name + '.json')).read_text())
        run('core_full', ['bash', './run_all.sh'], ROOT / 'core_extract/supplement')
        run('orthogonal', [sys.executable, str(ROOT / 'checks/orthogonal_checks.py')])
        orthogonal = json.loads((out / 'orthogonal.log').read_text())
        assert orthogonal['status'] == 'PASS'
        sys.path.insert(0, str(ROOT / 'code'))
        spec = importlib.util.spec_from_file_location('catalytic_smoke', ROOT / 'code/tests/test_smoke.py')
        smoke = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(smoke)
        names = sorted(name for name in vars(smoke) if name.startswith('test_'))
        for name in names:
            getattr(smoke, name)()
        checks.append({'name': 'fixture_free_smoke_tests', 'tests': names, 'status': 'PASS',
                       'method': 'Direct invocation of unchanged fixture-free assertions; pytest not required.'})
        checks.append({'name': 'orthogonal_exact_checks', 'status': 'PASS', 'checks': orthogonal['checks']})
    except Exception as exc:
        status, failure = 'failed', repr(exc)
    after = {str(p.relative_to(ROOT)): digest(p) for p in source_paths}
    if before != after:
        status, failure = 'inputs-changed', 'At least one source or expected-output hash changed during execution.'
    outputs = [{'path': str(p.relative_to(manifest_root)), 'sha256': digest(p), 'kind': 'result' if p.suffix == '.json' else 'log'}
               for p in sorted(out.iterdir()) if p.is_file() and p.suffix in ('.log', '.json') and p.name != 'manifest.json']
    manifest = {
        'schema_version': 2, 'claim_id': 'catalytic-finite-release-replay',
        'repository': {'commit': 'unavailable: source archive without git metadata', 'dirty': True},
        'manifest_root': str(manifest_root),
        'command': [sys.executable, str(Path(__file__).resolve()), '--out', str(out)],
        'environment': {'software': [{'name': 'Python', 'version': platform.python_version()},
            {'name': 'g++', 'version': subprocess.check_output(['g++', '--version'], text=True).splitlines()[0]}],
            'hardware': platform.platform()},
        'mathematics': {'assertion_tested': 'Reproduce every packaged finite core/atlas result, compare frozen outputs, and check independent bounded invariants and all four analytic two-qubit matrices.',
            'coefficient_domain': 'Exact integers and finite rings/fields stated in individual programs',
            'conventions': 'Row transvections; binary symplectic quotient omits Pauli translations/global phases; no ancillas; declared 0/1 or unit-cost alphabets.',
            'inputs': [str((ROOT / n).relative_to(manifest_root)) for n in before], 'bounds': {'clifford_qubits': [1, 2, 3], 'affine_toffoli_bits': 3,
                'binary_complete_unitriangular_dimensions': [2, 3, 4, 5, 6], 'ternary_complete_unitriangular_dimensions': [2, 3, 4, 5],
                'selected_binary_snapshot_dimensions': [7, 8, 9]},
            'non_claims': ['No unrestricted quantum speedup', 'No larger-width Clifford or nonlinear classification',
                'No proof of universal symbolic assertions from finite checks', 'No Lean coverage for catalytic component']},
        'randomness': {'used': False, 'generator': '', 'seed': None},
        'run': {'started_at': started, 'runtime_seconds': time.monotonic()-begin,
            'exit_status': 0 if status == 'completed' else 1, 'status': status,
            'resource_limits': {'memory_bytes': None, 'cpu_seconds': None, 'max_cores': None, 'max_threads': None}},
        'outputs': outputs, 'checks': checks,
        'result': 'All finite assertions and frozen outputs matched.' if status == 'completed' else failure,
        'residual_risks': ['Finite source review does not certify all universal prose theorems or external source claims.',
                           'The imported core C++ searches are replayed and their coverage architecture inspected, not independently reimplemented in full.'],
        'input_artifacts': [{'path': str((ROOT / name).relative_to(manifest_root)), 'sha256': value, 'sha256_after': after[name]} for name,value in before.items()],
        'declared_results': [str((out / name).relative_to(manifest_root)) for name in ('atlas_small.json', 'clifford_n3_total.json', 'clifford_n3_total_swap.json', 'clifford_n3_entangling.json')]}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': status, 'manifest': str(out / 'manifest.json'), 'failure': failure}))
    return 0 if status == 'completed' else 1

if __name__ == '__main__':
    raise SystemExit(main())
