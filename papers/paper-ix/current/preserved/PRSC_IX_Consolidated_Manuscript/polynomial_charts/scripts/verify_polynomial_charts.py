#!/usr/bin/env python3
"""Freshly compile and audit polynomial local inverses and full rectangular parameter charts.

Only the pinned portable Lean/Mathlib kit is reused. No project compiled file is reused.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from source_audit import ALLOWED, inspect_source, parse_audits, sha

ROOT = Path(__file__).resolve().parents[1]
LEAN_VERSION = '4.34.0-rc2'
MATHLIB_REVISION = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='Must not already exist')
    args = parser.parse_args()
    kit, output = args.kit.resolve(), args.output.resolve()
    if output.exists():
        parser.error('--output must be a new directory')
    output.mkdir(parents=True)
    build = output / 'build'
    build.mkdir()
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    report = {'status': 'INCOMPLETE', 'started_at': utc, 'runs': [],
              'fresh_project_compilation': True, 'mathlib_rebuilt': False,
              'warnings_as_errors': True, 'allowed_axioms': sorted(ALLOWED)}

    def run(name: str, command: list[str], expected_error: str | None = None) -> str:
        start = time.monotonic()
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              encoding='utf-8', errors='replace', timeout=380)
        log = output / (name + '.log')
        log.write_text(proc.stdout)
        if expected_error is None:
            passed = proc.returncode == 0 and re.search(r'error:|PANIC', proc.stdout) is None
        else:
            passed = (proc.returncode == 1 and 'error:' in proc.stdout
                      and re.search(expected_error, proc.stdout, re.I) is not None
                      and re.search(r'unknown module|unknown constant|does not exist|PANIC|timed out',
                                    proc.stdout, re.I) is None)
        report['runs'].append({'name': name, 'command': command,
            'exit_code': proc.returncode, 'seconds': round(time.monotonic()-start, 3),
            'log': log.name, 'log_sha256': sha(log), 'passed': passed,
            'expected_error': expected_error})
        print(f'{name}: {"PASS" if passed else "FAIL"}', flush=True)
        if not passed:
            raise RuntimeError(f'{name} failed; inspect {log}')
        return proc.stdout

    try:
        run('SourceAuditParserRegression', [sys.executable, str(ROOT/'scripts/check_source_audit.py')])
        pin = (kit/'workspace/lean-toolchain').read_text().strip()
        packages = json.loads((kit/'workspace/lake-manifest.json').read_text())['packages']
        mathlib = next(p for p in packages if p['name'] == 'mathlib')
        if pin != 'leanprover/lean4:v'+LEAN_VERSION or mathlib['rev'] != MATHLIB_REVISION:
            raise ValueError('Portable kit version mismatch')
        version = run('LeanVersion', ['bash', str(kit/'run.sh'), 'lean', '--version']).strip()
        if LEAN_VERSION not in version:
            raise ValueError('Compiler version mismatch')
        report['runtime'] = {'lean': version, 'mathlib_revision': mathlib['rev'],
            'python': platform.python_version(), 'platform': platform.platform(),
            'lean_binary_sha256': sha(kit/'toolchain/bin/lean'),
            'lake_manifest_sha256': sha(kit/'workspace/lake-manifest.json')}

        inventory = json.loads((ROOT/'inventory.json').read_text())
        modules, contracts = inventory['modules'], inventory['contracts']
        support = inventory['control_support']
        if {p.stem for p in (ROOT/'formalization').glob('*.lean')} != {m['module'] for m in modules}:
            raise ValueError('Unexpected active source module')
        if {p.stem for p in (ROOT/'contracts').glob('*.lean')} != {m['module'] for m in contracts}:
            raise ValueError('Unexpected statement contract')
        if {str(p.relative_to(ROOT)) for p in (ROOT/'controls').glob('Invalid*.lean')} != {c['source'] for c in inventory['negative_controls']}:
            raise ValueError('Unexpected negative control')
        if {p.stem for p in (ROOT/'controls').glob('Polynomial*.lean')} != {m['module'] for m in support}:
            raise ValueError('Unexpected positive control support')
        entries = modules + support + contracts
        if [inspect_source(ROOT/e['source']) for e in entries] != entries:
            raise ValueError('Source inventory or hash mismatch')
        report['inventory_sha256'] = sha(ROOT/'inventory.json')
        report['source_inventory'] = inventory
        names = {e['module'] for e in entries}
        seen = set()
        runner = [sys.executable, str(ROOT/'scripts/check_low_memory.py'), '--kit', str(kit),
                  '--threads', '1', '--timeout', '240', '--import-dir', str(build)]
        for entry in entries:
            if any(i in names and i not in seen for i in entry['imports']):
                raise ValueError('Imports are not topologically ordered')
            name = entry['module']
            run(name, runner+['--output', str(build/(name+'.olean')), str(ROOT/entry['source'])])
            seen.add(name)

        expected = {d['name'] for e in entries for d in e['declarations']}
        audit = output/'PolynomialChartsAxiomAudit.lean'
        audit.write_text('module\n'+'\n'.join('public import '+e['module'] for e in entries)+
            '\n@[expose] public section\n'+
            '\n'.join('#print axioms '+name for name in sorted(expected))+'\n')
        log = run('PolynomialChartsAxiomAudit', runner+[str(audit)])
        report['axiom_dependencies'] = parse_audits(log, expected)
        for control in inventory['negative_controls']:
            path = ROOT/control['source']
            inspect_source(path)
            if sha(path) != control['sha256']:
                raise ValueError('Negative control hash mismatch')
            run(path.stem, runner+[str(path)], control['expected_error'])
        if [inspect_source(ROOT/e['source']) for e in entries] != entries:
            raise ValueError('Source changed during the gate')
        if sha(ROOT/'inventory.json') != report['inventory_sha256']:
            raise ValueError('Frozen inventory changed during the gate')
        report['module_count'] = len(modules)
        report['positive_control_modules'] = len(support)
        report['statement_contracts'] = len(contracts)
        report['negative_controls'] = len(inventory['negative_controls'])
        report['declarations'] = dict(Counter(d['kind'] for e in entries for d in e['declarations']))
        report['explicit_declaration_audits'] = len(expected)
        report['build_files'] = {p.name: sha(p) for p in build.iterdir() if p.is_file()}
        report['status'] = 'PASS'
    except Exception as exc:
        report['status'] = 'FAILED'
        report['error'] = str(exc)
    finally:
        report['seconds'] = round(time.monotonic()-started, 3)
        report['verifier_sha256'] = sha(Path(__file__))
        report['source_audit_sha256'] = sha(ROOT/'scripts/source_audit.py')
        report['source_audit_regression_sha256'] = sha(ROOT/'scripts/check_source_audit.py')
        report['inventory_generator_sha256'] = sha(ROOT/'scripts/generate_inventory.py')
        report['runner_sha256'] = sha(ROOT/'scripts/check_low_memory.py')
        result_path = output/'polynomial_charts_verification.json'
        result_path.write_text(json.dumps(report, indent=2)+'\n')
        manifest = {'schema_version': 1, 'claim_id': 'PaperIX.fixed_polynomial.continuous_parameter_charts',
            'repository': {'commit': 'No Git repository; source hashes in inventory.json', 'dirty': False},
            'command': ' '.join(sys.argv),
            'environment': {'software': [
                {'name': 'Lean', 'version': report.get('runtime', {}).get('lean', 'runtime not yet verified')},
                {'name': 'Mathlib', 'version': MATHLIB_REVISION},
                {'name': 'Python', 'version': platform.python_version()}], 'hardware': platform.machine()},
            'mathematics': {
                'assertion_tested': 'Lean kernel acceptance of polynomial local surjectivity for arbitrary p-adic targets, square local homeomorphisms, actual Jacobian minor selection and coordinate reordering, and continuous rectangular parameter charts for the full root locus with precision preservation and reflection; inherited integer towers, exact roots, and perturbation stability; explicit expanded statement contracts and mathematically invalid controls',
                'coefficient_domain': 'Finite systems of integer multivariable polynomials; integer towers for positive natural q; p-adic completion and rank formulas require prime p',
                'conventions': 'Prime p and L at least 1; actual integer polynomial systems evaluated in p-adic integers; full rectangular reduced Jacobian surjective at the integer base; coordinate permutation is constructed from surjectivity; root chart inverse is actual free-coordinate projection; congruences are equivalent at every nonnegative depth',
                'inputs': ['inventory.json'], 'bounds': {'compiler_seconds_per_file': 240, 'threads': 1},
                'non_claims': ['Universal native13.2/13.3', 'Invariance under arbitrary polynomial presentation changes', 'Rank-nullity cardinality formulas over composite moduli', 'Arbitrary singular infinite lifting', 'Full weighted perturbation theorem with rationally invertible Jacobian', 'Analytic differentiability of the continuous parameter chart', 'Lifting interfaces for arbitrary p-adic polynomial coefficients', 'Uniqueness of roots for rectangular surjective Jacobians', 'Global integral descent', 'Independent Lean kernel implementation']},
            'randomness': {'used': False, 'generator': '', 'seed': None},
            'run': {'started_at': utc, 'runtime_seconds': report['seconds'],
                    'exit_status': 0 if report['status']=='PASS' else 1},
            'outputs': [{'path': result_path.name, 'sha256': sha(result_path)}],
            'checks': [r['name']+': '+('PASS' if r['passed'] else 'FAIL') for r in report['runs']],
            'result': report['status'],
            'residual_risks': ['Uses the pinned Lean kernel and precompiled Mathlib dependencies with the listed standard axioms.', 'Schema version 1 manifest; exact source hashes and command arrays are recorded separately in inventory and verification report, and sources are rechecked at the end of the run.']}
        (output/'computation_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(report['status'], flush=True)
    return 0 if report['status']=='PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
