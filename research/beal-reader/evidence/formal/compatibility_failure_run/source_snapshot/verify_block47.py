#!/usr/bin/env python3
"""Replay lane interfaces and exact mod-seven algebra in Block 47.

The imported pinned Mathlib cache is trusted in the normal Lean workflow.
This script makes no field-degree, discriminant-definition, ramification,
primitivity, or Beal-conjecture claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFICATION = ROOT / 'verification/formal'
MODULES = ['BealLaneCertificate', 'BealCorrelationExamples', 'BealModSevenCartier', 'BealBlock47']
REVISION = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    workspace = runtime / 'workspace'
    logs = VERIFICATION / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    lean = runtime / 'toolchain/bin/lean'
    checker = runtime / 'toolchain/bin/leanchecker'
    env = os.environ.copy()
    env['PATH'] = str(runtime / 'toolchain/bin') + ':' + env['PATH']
    libs = [str(p / '.lake/build/lib/lean')
            for p in (workspace / '.lake/packages').iterdir() if p.is_dir()]
    libs += [str(workspace / '.lake/build/lib/lean'), str(runtime / 'toolchain/lib/lean')]
    env['LEAN_PATH'] = ':'.join([str(ROOT / 'lean'), str(VERIFICATION)] + libs)

    def run(name, argv, timeout=90):
        started = time.monotonic()
        try:
            proc = subprocess.run([str(x) for x in argv], env=env, cwd=ROOT,
                                  text=True, capture_output=True, timeout=timeout)
            output = proc.stdout + proc.stderr
            code = proc.returncode
            status = 'PASS' if code == 0 and 'warning:' not in output else 'FAIL'
        except subprocess.TimeoutExpired as exc:
            output = str(exc.stdout) + str(exc.stderr)
            code = None
            status = 'TIMEOUT'
        log = logs / (name + '.log')
        log.write_text(output)
        record = {'argv': [str(x) for x in argv], 'exit_code': code, 'status': status,
                  'seconds': round(time.monotonic() - started, 4),
                  'log': str(log.relative_to(ROOT)), 'log_sha256': sha256(log)}
        log.with_suffix('.receipt.json').write_text(json.dumps(record, indent=2) + '\n')
        return record

    version = subprocess.check_output([str(lean), '--version'], env=env, text=True).strip()
    revision = subprocess.check_output(['git', '-C', str(workspace / '.lake/packages/mathlib'),
                                        'rev-parse', 'HEAD'], text=True).strip()
    result = {'schema': 'komorebi.beal.block47.formal_verification.v1',
              'runtime': {'version': version, 'mathlib_revision': revision,
                          'passed': '4.34.0-rc2' in version and revision == REVISION},
              'proof_boundary': 'Generic lane-exclusion interfaces, exact Boolean counterexamples, and sextic-cube coefficients and matrix identities over ZMod 7. Exhaustiveness, attachment, and sound arithmetic tests remain hypotheses. No geometric Cartier interpretation, Beal nonexistence, or modular-theorem application is asserted.',
              'compilations': [], 'negative_controls': []}
    declarations = []
    forbidden = {}
    for name in MODULES:
        path = ROOT / 'lean' / (name + '.lean')
        source = path.read_text()
        code = re.sub(r'/\-.*?\-/', '', source, flags=re.S)
        code = re.sub(r'--[^\n]*', '', code)
        hits = re.findall(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', code)
        if hits:
            forbidden[name] = hits
        for match in re.finditer(r'^(?:noncomputable )?(theorem|lemma|def)\s+(\w+)', source, re.M):
            declarations.append({'module': name, 'kind': match.group(1),
                                 'name': 'KomorebiBeal.Block47.' + match.group(2)})
        record = run('compile_' + name, [lean, '-DwarningAsError=true', '-o',
                                      path.with_suffix('.olean'), path])
        result['compilations'].append(record)
        if record['status'] != 'PASS':
            break
    result['source_scan'] = {'passed': not forbidden, 'hits': forbidden}
    result['source_sha256'] = {name + '.lean': sha256(ROOT / 'lean' / (name + '.lean'))
                               for name in MODULES}
    (VERIFICATION / 'declarations.json').write_text(json.dumps(declarations, indent=2) + '\n')
    external = set()
    bodies = []
    for name in MODULES:
        lines = (ROOT / 'lean' / (name + '.lean')).read_text().splitlines()
        external.update(line for line in lines if line.startswith('import Mathlib.'))
        bodies.append('\n'.join(line for line in lines if not line.startswith('import ')))
    replay = VERIFICATION / 'Beal47Replay.lean'
    replay.write_text('\n'.join(sorted(external)) + '\n\n' + '\n\n'.join(bodies) + '\n')
    result['replay_build'] = run('compile_replay', [lean, '-DwarningAsError=true', '-o',
                                                  replay.with_suffix('.olean'), replay])
    result['kernel_replay'] = run('kernel_project', [checker, '-v', 'Beal47Replay'])
    modules = re.findall(r'^replaying (\S+)$', (logs / 'kernel_project.log').read_text(), re.M)
    result['kernel_replay']['replayed_modules'] = modules
    result['kernel_replay']['exact_module_set'] = modules == ['Beal47Replay']
    result['replay_source_sha256'] = sha256(replay)
    theorem_names = [d['name'] for d in declarations if d['kind'] in ('theorem', 'lemma')]
    audit = VERIFICATION / 'AxiomAudit.lean'
    audit.write_text('import BealBlock47\n' + '\n'.join('#print axioms ' + name
                     for name in theorem_names) + '\n')
    command = run('axioms', [lean, '-DwarningAsError=true', audit])
    output = (logs / 'axioms.log').read_text()
    reported = re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)", output)
    dependencies = set()
    for match in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]', output):
        dependencies.update(x.strip().strip("'") for x in match.group(1).split(',') if x.strip())
    result['axiom_audit'] = {'command': command, 'theorems_requested': len(theorem_names),
                             'theorems_reported': len(reported), 'dependencies': sorted(dependencies),
                             'forbidden': sorted(dependencies - ALLOWED_AXIOMS),
                             'passed': command['status'] == 'PASS' and
                             set(reported) == set(theorem_names) and len(reported) == len(theorem_names)
                             and not (dependencies - ALLOWED_AXIOMS)}
    controls = {
        'false_candidate_swap':
            'import BealBlock47\n'
            'example : ∃ candidate : Bool, ∀ test : Bool, candidate = test := by\n'
            '  exact ⟨false, by intro test; rfl⟩\n',
        'false_offdiagonal_cancellation':
            'import BealBlock47\nopen KomorebiBeal.Block47\n'
            'example : ((freySexticModSeven 1 1) ^ 3).coeff 5 = 0 := by\n'
            '  rw [frey_cube_coeff_five]\n  decide\n',
        'placeholder': 'import BealBlock47\nexample : False := by sorry\n'}
    controls_dir = VERIFICATION / 'negative_controls'
    controls_dir.mkdir(exist_ok=True)
    for name, source in controls.items():
        path = controls_dir / (name + '.lean')
        path.write_text(source)
        record = run(name, [lean, '-DwarningAsError=true', path])
        output = (logs / (name + '.log')).read_text()
        rejected_for_expected_reason = (
            ('rfl' in output and 'failed' in output) if name == 'false_candidate_swap'
            else ('decide' in output and 'false' in output)
            if name == 'false_offdiagonal_cancellation'
            else 'declaration uses `sorry`' in output)
        result['negative_controls'].append({'name': name,
                                            'passed': record['exit_code'] not in (None, 0)
                                            and rejected_for_expected_reason,
                                            'rejected_for_expected_reason': rejected_for_expected_reason,
                                            'command': record})
    result['declaration_count'] = len(declarations)
    result['theorem_count'] = len(theorem_names)
    okay = (result['runtime']['passed'] and len(result['compilations']) == len(MODULES)
            and all(r['status'] == 'PASS' for r in result['compilations'])
            and result['replay_build']['status'] == 'PASS'
            and result['kernel_replay']['status'] == 'PASS'
            and result['kernel_replay']['exact_module_set']
            and result['axiom_audit']['passed'] and result['source_scan']['passed']
            and all(r['passed'] for r in result['negative_controls']))
    result['status'] = 'PASS_FORMAL_CERTIFICATE_AND_MOD7_ALGEBRA' if okay else 'INCOMPLETE'
    (VERIFICATION / 'BLOCK47_FORMAL_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'theorem_count': len(theorem_names),
                      'declaration_count': len(declarations),
                      'dependencies': sorted(dependencies)}, indent=2), flush=True)
    return 0 if okay else 1


if __name__ == '__main__':
    sys.exit(main())
