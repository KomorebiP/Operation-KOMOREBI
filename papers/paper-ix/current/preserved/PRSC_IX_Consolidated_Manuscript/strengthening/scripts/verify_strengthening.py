#!/usr/bin/env python3
"""Rebuild and audit the dyadic continuation against the pinned Paper IX baseline."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--baseline-root', type=Path, required=True)
    parser.add_argument('--baseline-build', type=Path,
                        help='Reuse a successfully audited baseline build, checking every recorded hash')
    parser.add_argument('--output', type=Path, required=True, help='New directory for fresh outputs')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    baseline = args.baseline_root.resolve()
    kit = args.kit.resolve()
    output = args.output.resolve()
    if output.exists(): parser.error('--output must not exist')
    output.mkdir(parents=True)
    report = {'status': 'INCOMPLETE', 'baseline_rebuilt': args.baseline_build is None,
              'runs': [], 'mathlib_rebuilt': False, 'compiler_warnings_are_errors': True}
    started = time.monotonic()

    def run(name: str, command: list[str], expected_error: str | None = None) -> None:
        start = time.monotonic()
        log = output / (name + '.log')
        with log.open('w') as stream:
            proc = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        text = log.read_text()
        passed = (proc.returncode == 0 if expected_error is None else
                  proc.returncode != 0 and re.search(expected_error, text, re.I) is not None
                  and re.search(r'unknown module|unknown constant|PANIC|timed out', text, re.I) is None)
        report['runs'].append({'name': name, 'command': command, 'exit_code': proc.returncode,
             'seconds': round(time.monotonic()-start, 3), 'log_sha256': sha(log),
             'expected_error': expected_error, 'passed': passed})
        print(f'{name}: {"PASS" if passed else "FAIL"}', flush=True)
        if not passed: raise RuntimeError(f'{name} failed: inspect {log}')

    try:
        run('baseline_manifest', [sys.executable, str(baseline/'scripts/check_manifest.py')])
        if args.baseline_build:
            base_build = args.baseline_build.resolve()
        else:
            before = set((baseline/'verification/runs').glob('*'))
            run('baseline_fresh', ['bash', str(baseline/'Run-Portable.sh'), str(kit)])
            added = set((baseline/'verification/runs').glob('*')) - before
            if len(added) != 1: raise ValueError('Expected one fresh baseline verification directory')
            base_build = added.pop()/'build'
        base_report_path = base_build.parent/'verification.json'
        base_report = json.loads(base_report_path.read_text())
        if base_report['status'] != 'LEAN_BUILD_AND_AXIOM_AUDIT_PASS':
            raise ValueError('Baseline build did not pass')
        if base_report['inventory_sha256'] != sha(baseline/'inventory.json'):
            raise ValueError('Baseline source inventory differs from the verified build')
        for name, digest in base_report['build_files'].items():
            if sha(base_build/name) != digest: raise ValueError('Baseline compiled hash mismatch: '+name)
        report['baseline_report_sha256'] = sha(base_report_path)
        report['baseline_inventory_sha256'] = sha(baseline/'inventory.json')
        report['baseline_compiled_file_count'] = len(base_report['build_files'])
        spec = importlib.util.spec_from_file_location('baseline_verifier', baseline/'scripts/verify.py')
        if spec is None or spec.loader is None: raise ValueError('Cannot load baseline audit utilities')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        verifier.ROOT = root
        pinned = json.loads((root/'inventory.json').read_text())
        names = [entry['module'] for entry in pinned['modules']]
        if {p.stem for p in (root/'formalization').glob('*.lean')} != set(names):
            raise ValueError('Active module set differs from inventory')
        observed = [verifier.inspect_source(root/'formalization'/(name+'.lean')) for name in names]
        if observed != pinned['modules']: raise ValueError('Continuation source inventory mismatch')
        report['source_inventory'] = pinned
        build = output/'build'
        build.mkdir()
        for source in base_build.iterdir():
            if source.is_file(): (build/source.name).symlink_to(source)
        runner = [sys.executable, str(baseline/'scripts/check_low_memory.py'), '--kit', str(kit),
                  '--threads', '1', '--timeout', '240', '--import-dir', str(build)]
        seen = set()
        for entry in observed:
            if any(dep in names and dep not in seen for dep in entry['imports']):
                raise ValueError('Module list is not topologically ordered')
            name = entry['module']
            run(name, runner+['--output', str(build/(name+'.olean')), str(root/entry['source'])])
            seen.add(name)
        expected = {d['name'] for entry in observed for d in entry['declarations']}
        audit = output/'ContinuationAxiomAudit.lean'
        audit.write_text('module\n'+'\n'.join('public import '+name for name in names)+
                         '\n@[expose] public section\n'+
                         '\n'.join('#print axioms '+name for name in sorted(expected))+'\n')
        run('ContinuationAxiomAudit', runner+[str(audit)])
        report['axiom_dependencies'] = verifier.parse_audits(
            (output/'ContinuationAxiomAudit.log').read_text(), expected)
        for control in pinned['controls']:
            path = root/control['source']
            if sha(path) != control['sha256']: raise ValueError('Control hash mismatch')
            run(path.stem, runner+[str(path)], control.get('expected_error'))
        report['status'] = 'PASS'
        report['new_module_count'] = len(observed)
        report['explicit_declaration_count'] = len(expected)
        report['new_build_files'] = {p.name: sha(p) for p in build.iterdir()
                                     if p.is_file() and not p.is_symlink()}
    except Exception as exc:
        report['status'] = 'FAILED'
        report['error'] = str(exc)
    finally:
        report['seconds'] = round(time.monotonic()-started, 3)
        (output/'continuation_verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], flush=True)
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
