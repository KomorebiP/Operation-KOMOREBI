#!/usr/bin/env python3
"""Rebuild the q=12 proofs, audit axioms, replay the kernel, and reject mutations.

Uses a previously restored Komorebi portable Lean kit. No downloads are made.
Every verification run gets a fresh build directory. A timeout is a failure,
including in a negative control. Python arithmetic is an independent check,
not a replacement for Lean.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

MODULES = [
    'QuantumArithmeticBridge',
    'QuantumArithmeticSpecification',
    'QuantumArithmeticComplex',
    'QuantumArithmeticUnitary',
]
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def theorem_names(text: str) -> list[str]:
    return re.findall(r'(?m)^(?:@\[[^\n]*\]\s*)?theorem\s+(\w+)', text)


def run_command(command: list[str], cwd: Path, env: dict[str, str],
                log: Path, timeout: int) -> dict:
    start = time.monotonic()
    with log.open('w', encoding='utf-8') as out:
        out.write('COMMAND ' + json.dumps(command) + '\n')
        out.flush()
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=out,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = 124
        result = {'command': command, 'exit_code': code,
                  'timed_out': timed_out, 'seconds': time.monotonic() - start,
                  'log': log.name}
        out.write('\nRESULT ' + json.dumps(result) + '\n')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', required=True, type=Path,
                        help='Root containing toolchain/bin/lean and workspace/.lake')
    parser.add_argument('--output', type=Path, default=None)
    parser.add_argument('--timeout', type=int, default=240,
                        help='Timeout per compiler/checker operation in seconds')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    kit = args.kit.resolve()
    output = (args.output or root / 'verification' / 'latest_run').resolve()
    output.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix='fresh_build_', dir=output))
    report: dict = {'status': 'RUNNING', 'build_directory': str(build),
                    'stages': [], 'source_sha256': {}, 'theorems': {},
                    'negative_controls': []}
    report_file = output / 'VERIFICATION.json'

    def save() -> None:
        report_file.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def checked(result: dict, label: str) -> None:
        report['stages'].append({'label': label, **result})
        save()
        if result['exit_code'] != 0 or result['timed_out']:
            raise RuntimeError(f'{label} failed. See {result["log"]}.')
        print('PASS', label, flush=True)

    try:
        if sys.platform != 'linux':
            raise RuntimeError('The portable compiler requires Linux x86-64, including WSL2.')
        lean = kit / 'toolchain' / 'bin' / 'lean'
        checker = kit / 'toolchain' / 'bin' / 'leanchecker'
        workspace = kit / 'workspace'
        for required in [lean, checker, workspace / 'lake-manifest.json', kit / 'run.sh']:
            if not required.exists():
                raise FileNotFoundError(required)
        manifest = json.loads((workspace / 'lake-manifest.json').read_text())
        mathlib = next(p for p in manifest['packages'] if p['name'] == 'mathlib')
        if mathlib['rev'] != EXPECTED_MATHLIB:
            raise RuntimeError('The portable Mathlib revision does not match the recorded pin.')
        capture = subprocess.run(
            ['bash', str(kit / 'run.sh'), 'lake', 'env', '/usr/bin/env', '-0'],
            cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=args.timeout, check=True)
        env = os.environ.copy()
        for entry in capture.stdout.split(b'\0'):
            if b'=' in entry:
                key, value = entry.split(b'=', 1)
                env[key.decode()] = value.decode()
        env['LEAN_PATH'] = str(build) + ':' + env['LEAN_PATH']
        # run.sh may have used a short-lived path adapter. Keep a local copy.
        preload = env.get('LD_PRELOAD', '')
        if preload and any(not Path(p).exists() for p in preload.split(':')):
            adapter = build / 'app_path.so'
            shutil.copy2(kit / 'compat' / 'app_path.so', adapter)
            env['LD_PRELOAD'] = str(adapter)
        version = subprocess.run([str(lean), '--version'], cwd=build, env=env,
                                 text=True, capture_output=True, timeout=30, check=True)
        if EXPECTED_LEAN not in version.stdout:
            raise RuntimeError('Unexpected Lean version: ' + version.stdout)
        report['lean_version'] = version.stdout.strip()
        report['mathlib_revision'] = EXPECTED_MATHLIB
        report['toolchain_lean_sha256'] = sha256(lean)
        report['runner_sha256'] = sha256(Path(__file__).resolve())
        save()

        for module in MODULES:
            source = root / (module + '.lean')
            text = source.read_text(encoding='utf-8')
            if re.search(r'\b(sorry|admit|native_decide)\b', text):
                raise RuntimeError(f'Forbidden proof placeholder or native decision tactic in {source.name}.')
            if re.search(r'(?m)^\s*(axiom|unsafe)\b', text):
                raise RuntimeError(f'Unexpected axiom/unsafe declaration in {source.name}.')
            report['source_sha256'][source.name] = sha256(source)
            report['theorems'][module] = theorem_names(text)
            target = build / source.name
            shutil.copy2(source, target)
            result = run_command(
                [str(lean), '-j1', '-DwarningAsError=true', '-o', module + '.olean', target.name],
                build, env, output / ('compile_' + module + '.log'), args.timeout)
            checked(result, 'compile ' + module)
            if not (build / (module + '.olean')).is_file():
                raise RuntimeError('Successful compiler did not produce expected object file.')

        audit = 'module\n' + ''.join('public import ' + m + '\n' for m in MODULES) + '\n'
        for names in report['theorems'].values():
            for name in names:
                audit += '#print axioms Komorebi.QuantumArithmetic.' + name + '\n'
        (build / 'AxiomAudit.lean').write_text(audit, encoding='utf-8')
        result = run_command([str(lean), '-j1', '-DwarningAsError=true', 'AxiomAudit.lean'],
                             build, env, output / 'axiom_audit.log', args.timeout)
        checked(result, 'axiom audit')
        audit_text = (output / 'axiom_audit.log').read_text()
        axiom_sets = re.findall(r'depends on axioms:\s*\[([^\]]*)\]', audit_text, re.S)
        no_axioms = audit_text.count('does not depend on any axioms')
        expected_count = sum(map(len, report['theorems'].values()))
        if len(axiom_sets) + no_axioms != expected_count:
            raise RuntimeError('Axiom audit did not cover every declared theorem.')
        used = {x.strip() for s in axiom_sets for x in s.split(',') if x.strip()}
        if used - ALLOWED_AXIOMS:
            raise RuntimeError('Unexpected axioms: ' + ', '.join(sorted(used - ALLOWED_AXIOMS)))
        report['theorem_count'] = expected_count
        report['axioms_used'] = sorted(used)
        save()

        for module in MODULES:
            result = run_command([str(checker), '--verbose', module], build, env,
                                 output / ('replay_' + module + '.log'), args.timeout)
            checked(result, 'kernel replay ' + module)

        # Prove the negation of every bad mutation independently. This removes
        # ambiguity when a decide failure mentions opaque reduction internals.
        control_source = root / 'tests' / 'ControlRefutations.lean'
        control_text = control_source.read_text()
        if re.search(r'\b(sorry|admit|native_decide)\b', control_text):
            raise RuntimeError('Forbidden proof construct in control refutations.')
        if re.search(r'(?m)^\s*(axiom|unsafe)\b', control_text):
            raise RuntimeError('Unexpected axiom/unsafe declaration in controls.')
        shutil.copy2(control_source, build / 'ControlRefutations.lean')
        report['source_sha256']['tests/ControlRefutations.lean'] = sha256(control_source)
        result = run_command(
            [str(lean), '-j1', '-DwarningAsError=true', '-o',
             'ControlRefutations.olean', 'ControlRefutations.lean'],
            build, env, output / 'control_refutations.log', args.timeout)
        checked(result, 'prove control refutations')
        control_log = (output / 'control_refutations.log').read_text()
        control_axioms = re.findall(r'depends on axioms:\s*\[([^\]]*)\]', control_log, re.S)
        if len(control_axioms) != 4:
            raise RuntimeError('Missing control-refutation axiom audit.')
        control_used = {a.strip() for group in control_axioms for a in group.split(',') if a.strip()}
        if control_used - ALLOWED_AXIOMS:
            raise RuntimeError('Unexpected axiom in a control refutation.')
        report['control_refutation_count'] = 4
        report['total_checked_named_theorems'] = expected_count + 4
        result = run_command([str(checker), '--verbose', 'ControlRefutations'],
                             build, env, output / 'replay_control_refutations.log', args.timeout)
        checked(result, 'kernel replay control refutations')

        original = (root / 'QuantumArithmeticBridge.lean').read_text()
        mutations = [
            ('wrong_energy', 'theorem ramanujan12_energy : sqEnergy ramanujan12 = 48',
             'theorem ramanujan12_energy : sqEnergy ramanujan12 = 49'),
            ('wrong_root_order', 'theorem zeta12_order_certificate : cPow zeta12 12 = cOne',
             'theorem zeta12_order_certificate : cPow zeta12 6 = cOne'),
            ('noise_retained', 'matVec projector12 noise12 = List.replicate 12 0',
             'matVec projector12 noise12 = noise12'),
            ('phase_mode_invented', '[cRat 16, cRat 0, cRat 4, cRat 0, cRat 4, cRat 0,',
             '[cRat 16, cRat 1, cRat 4, cRat 0, cRat 4, cRat 0,'),
        ]
        for label, before, after in mutations:
            if original.count(before) != 1:
                raise RuntimeError('Mutation target is not unique: ' + label)
            target = build / ('Negative_' + label + '.lean')
            target.write_text(original.replace(before, after, 1), encoding='utf-8')
            result = run_command([str(lean), '-j1', '-DwarningAsError=true', target.name],
                                 build, env, output / ('negative_' + label + '.log'), args.timeout)
            text = (output / result['log']).read_text()
            # A timeout or unrelated setup/import error is not a successful control.
            valid_rejection = (result['exit_code'] == 1 and not result['timed_out']
                               and 'error: Tactic `decide` failed for proposition' in text
                               and 'unknown identifier' not in text
                               and 'unknown module' not in text
                               and ('false' in text.lower() or 'isFalse' in text))
            report['negative_controls'].append({'label': label, 'expected_rejection': valid_rejection,
                                                'mutation': {'before': before, 'after': after}, **result})
            save()
            if not valid_rejection:
                raise RuntimeError('Negative control was accepted or inconclusive: ' + label)
            print('PASS rejected mutation', label, flush=True)

        result = run_command([sys.executable, str(root / 'verify_exact.py')], build, env,
                             output / 'python_exact.log', args.timeout)
        checked(result, 'independent Python exact arithmetic')
        report['status'] = 'PASS'
        save()
        print(f'PASS: {expected_count} theorems, {len(MODULES)} rebuilt/replayed modules, '
              f'{len(mutations)} rejected mutations.', flush=True)
        return 0
    except Exception as exc:
        report['status'] = 'FAIL'
        report['error'] = f'{type(exc).__name__}: {exc}'
        save()
        print(report['error'], file=sys.stderr, flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
