#!/usr/bin/env python3
"""Freshly compile and audit polynomial towers with arbitrary prescribed parameter paths.

Only the pinned portable Lean/Mathlib kit is reused. No project compiled file is reused.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
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
ADAPTER_SHA256 = 'fdcc7edf41b2c301abd13ec01041d44eee52148cbf05f2332bc39b23c5862853'


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
    environment = os.environ.copy()
    # Use the exact shipped compatibility adapter, without a /tmp duplicate.
    # It repairs executable-path discovery; no compiler or proof is modified.
    environment['LD_PRELOAD'] = str(kit/'compat/app_path.so')
    environment['TMPDIR'] = str(output)
    report = {'status': 'INCOMPLETE', 'started_at': utc, 'runs': [],
              'fresh_project_compilation': True, 'mathlib_rebuilt': False,
              'warnings_as_errors': True, 'allowed_axioms': sorted(ALLOWED)}

    def run(name: str, command: list[str], expected_error: str | None = None) -> str:
        start = time.monotonic()
        log = output / (name + '.log')
        try:
            proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  encoding='utf-8', errors='replace', timeout=380,
                                  env=environment)
            stdout, code, timed_out = proc.stdout, proc.returncode, False
        except subprocess.TimeoutExpired as exc:
            partial = exc.stdout or ''
            if isinstance(partial, bytes):
                partial = partial.decode('utf-8', errors='replace')
            stdout = partial + '\nGate subprocess timed out after 380 seconds.\n'
            code, timed_out = 124, True
        log.write_text(stdout)
        if expected_error is None:
            passed = code == 0 and re.search(r'error:|PANIC', stdout) is None
        else:
            passed = (code == 1 and 'error:' in stdout
                      and re.search(expected_error, stdout, re.I) is not None
                      and re.search(r'unknown module|unknown constant|does not exist|PANIC|timed out',
                                    stdout, re.I) is None)
        report['runs'].append({'name': name, 'command': command,
            'exit_code': code, 'seconds': round(time.monotonic()-start, 3),
            'log': log.name, 'log_sha256': sha(log), 'passed': passed,
            'expected_error': expected_error, 'timed_out': timed_out})
        print(f'{name}: {"PASS" if passed else "FAIL"}', flush=True)
        if not passed:
            raise RuntimeError(f'{name} failed; inspect {log}')
        return stdout

    try:
        if sha(kit/'compat/app_path.so') != ADAPTER_SHA256:
            raise ValueError('Shipped compatibility adapter hash mismatch')
        target = ROOT/'TARGET_CONTRACT.json'
        report['target_contract_sha256'] = sha(target)
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
            'lake_manifest_sha256': sha(kit/'workspace/lake-manifest.json'),
            'compatibility_adapter_sha256': sha(kit/'compat/app_path.so'),
            'compatibility_adapter_scope': 'Shipped executable-path discovery adapter only',
            'temporary_directory': str(output)}

        inventory = json.loads((ROOT/'inventory.json').read_text())
        modules, contracts = inventory['modules'], inventory['contracts']
        support = inventory['control_support']
        if 'PolynomialPrescribedPadicTower' not in {m['module'] for m in modules}:
            raise ValueError('Final actual polynomial prescribed-parameter tower module is missing')
        if 'PolynomialParameterTowerContracts' not in {m['module'] for m in contracts}:
            raise ValueError('Expanded prescribed-parameter tower statement contract is missing')
        if 'PolynomialParameterTowerControls' not in {m['module'] for m in support}:
            raise ValueError('Prescribed-parameter tower positive control module is missing')
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
        inherited = json.loads((ROOT/'audit/inherited_sources.json').read_text())
        for entry in inherited['modules']:
            if sha(ROOT/entry['source']) != entry['sha256']:
                raise ValueError('An inherited mathematical source changed: '+entry['source'])
        report['inherited_modules_preserved'] = len(inherited['modules'])
        report['inherited_source_record_sha256'] = sha(ROOT/'audit/inherited_sources.json')
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
        if len(expected) != sum(len(e['declarations']) for e in entries):
            raise ValueError('Duplicate fully qualified declaration across project files')
        if any(not e['declarations'] for e in entries):
            raise ValueError('Active source or contract has no inventoried declaration')
        audit = output/'PolynomialParameterTowerAxiomAudit.lean'
        audit.write_text('module\n'+'\n'.join('public import '+e['module'] for e in entries)+
            '\n@[expose] public section\n'+
            '\n'.join('#print axioms '+name for name in sorted(expected))+'\n')
        log = run('PolynomialParameterTowerAxiomAudit', runner+[str(audit)])
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
        if sha(target) != report['target_contract_sha256']:
            raise ValueError('Target contract changed during the gate')
        if sha(ROOT/'audit/inherited_sources.json') != report['inherited_source_record_sha256']:
            raise ValueError('Inherited source record changed during the gate')
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
        report['inventory_generator_sha256'] = sha(ROOT/'scripts/generate_parameter_tower_inventory.py')
        report['runner_sha256'] = sha(ROOT/'scripts/check_low_memory.py')
        result_path = output/'polynomial_parameter_towers_verification.json'
        result_path.write_text(json.dumps(report, indent=2)+'\n')
        manifest = {'schema_version': 1, 'claim_id': 'PaperIX.polynomial.prescribed_parameter_towers',
            'repository': {'commit': 'No Git repository; source hashes in inventory.json', 'dirty': False},
            'command': ' '.join(sys.argv),
            'environment': {'software': [
                {'name': 'Lean', 'version': report.get('runtime', {}).get('lean', 'runtime not yet verified')},
                {'name': 'Mathlib', 'version': MATHLIB_REVISION},
                {'name': 'Python', 'version': platform.python_version()}], 'hardware': platform.machine()},
            'mathematics': {
                'assertion_tested': 'Lean kernel acceptance of compatible integer polynomial solution towers for every compatible exact integer parameter path under only initial actual solved-Jacobian surjectivity; construction of such paths for every prescribed p-adic parameter target in the base ball; actual p-adic root endpoints with exact free coordinates and retained tower precisions; exactly p^(m-e) actual prescribed residue lifts for each next parameter digit; square solved-block uniqueness; inherited prescribed obstructions, lifting, chart, and root-motion theorems; expanded statement contracts and mathematically invalid controls',
                'coefficient_domain': 'Finite rectangular systems of integer polynomials in m solved and k parameter variables, e equations, positive modulus q, depth L>=1, actual lower root x, actual solved-coordinate Jacobian modulo q surjective. Exact integer towers include composite q and q=1; p-adic completion and count p^(m-e) require prime p. Uniqueness requires m=e',
                'conventions': 'A supplied integer parameter path starts exactly at x_free and its nth increment is divisible by q^(L+n). The constructed full tower starts exactly at x, has exactly those integer free coordinates, is a polynomial root to depth L+n and retains the initial actual solved Jacobian. For an arbitrary p-adic target tau congruent to x_free modulo p^L, both parameter path and full tower are constructed. The endpoint is an exact root with free part tau and is congruent to tower level n modulo p^(L+n). Prescribed branching counts actual residue classes, not integer representatives',
                'inputs': ['inventory.json'], 'bounds': {'compiler_seconds_per_file': 240, 'threads': 1},
                'non_claims': ['Universal native13.2/13.3', 'Invariance under arbitrary polynomial presentation changes', 'Rank-nullity cardinality formulas over composite moduli', 'Arbitrary singular infinite lifting', 'Analyticity of the nonlinear root map', 'Higher-order perturbation expansions', 'Prescribed infinite lifting without initial solved-block surjectivity', 'Analytic differentiability of the continuous parameter chart', 'Arbitrary p-adic coefficient extension of all rectangular chart interfaces', 'Uniqueness of roots for rectangular surjective Jacobians', 'Global integral descent', 'Independent Lean kernel implementation']},
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
