#!/usr/bin/env python3
"""Validate a complete replay receipt against this checkout without executing Lean.

This corroborates recorded process results, file identity, axiom coverage, and controls.
It does not authenticate a historical run or turn a cached replay into a public bootstrap.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any
import replay_lean

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'padic'
sys.path.insert(0, str(PROJECT / 'verification'))
from evidence_parser import parse_declared, parse_environment

NORMAL = [
    ('build', ['lake', 'build']),
    ('positive', ['lake', 'env', 'lean', '-DwarningAsError=true', 'verification/PositiveControl.lean']),
    ('concrete', ['lake', 'env', 'lean', '-DwarningAsError=true', 'verification/ResidualChecks.lean']),
    ('universal', ['lake', 'env', 'lean', '-DwarningAsError=true', 'verification/ResidualUniversal.lean']),
    ('declared_axioms', ['lake', 'env', 'lean', 'verification/AllAxioms34.lean']),
    ('environment_axioms', ['lake', 'env', 'lean', 'verification/KernelAxiomInventory.lean']),
]
NEGATIVES = ('FalseControl', 'PlaceholderControl', 'FalseAllWord', 'FalseIgnoreOutput', 'FalseLinearMinimum')
ALLOWED_AXIOMS = {'propext', 'Quot.sound', 'Classical.choice'}
SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def check_receipt(directory: Path, *, expected_snapshot: dict[str, str] | None = None,
                  manifest: dict[str, Any] | None = None,
                  inventory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read-only check; optional explicit inputs make adversarial tests self-contained."""
    directory = directory.resolve()
    errors: list[str] = []
    checks = 0
    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)
    summary: dict[str, Any] = {'status': 'FAIL', 'scope': (
        'Recorded clean project replay with exact proof-input hashes, command logs, '
        'axiom coverage and negative controls. Not cryptographic run attestation, '
        'a new Lean execution, a public bootstrap, or hosted-workflow verification.')}
    try:
        report_path = directory / 'REPLAY.json'
        require(not report_path.is_symlink(), 'Receipt must not be a symlink')
        report = json.loads(report_path.read_text(encoding='utf-8'))
        require(isinstance(report, dict), 'Receipt must be a JSON object')
        if not isinstance(report, dict):
            raise ValueError('Invalid receipt shape')
        expected_snapshot = replay_lean.snapshot() if expected_snapshot is None else expected_snapshot
        manifest = json.loads((PROJECT / 'lake-manifest.json').read_text()) if manifest is None else manifest
        inventory = json.loads((PROJECT / 'verification/theorem_inventory.json').read_text()) if inventory is None else inventory
        require(report.get('status') == 'PASS', 'Replay did not finish with PASS')
        require(report.get('clean_requested') is True and report.get('fresh_project_build') is True,
                'An empty project-local build is required')
        require(report.get('inputs_unchanged') is True, 'Frozen-input check did not pass')
        require(report.get('proof_source_hashes_before') == expected_snapshot,
                'Before-run proof inputs do not match this checkout')
        require(report.get('proof_source_hashes_after') == expected_snapshot,
                'After-run proof inputs do not match this checkout')
        for key in ('started_at_utc', 'finished_at_utc'):
            require(isinstance(report.get(key), str) and bool(report[key]), 'Missing timestamp: ' + key)
        commands = report.get('commands')
        if not isinstance(commands, list) or any(not isinstance(c, dict) for c in commands):
            raise ValueError('Commands must be a list of objects')
        expected_names = ['lean_version', 'lake_version'] + ['pin_' + p['name'] for p in manifest['packages']]
        expected_names += [name for name, _ in NORMAL] + list(NEGATIVES)
        require([c.get('name') for c in commands] == expected_names,
                'Command list is incomplete, duplicated, reordered, or unexpected')
        by_name = {c.get('name'): c for c in commands}
        logs: dict[str, str] = {}
        paths: set[str] = set()
        for c in commands:
            name = c.get('name')
            if not isinstance(name, str):
                raise ValueError('Command name must be text')
            is_negative = name in NEGATIVES
            require(c.get('status') == 'PASS', 'Command did not pass: ' + name)
            require(c.get('timeout') is False and c.get('launch_error') is None,
                    'Timeout or launch failure: ' + name)
            code = c.get('exit_code')
            require(type(code) is int and ((code != 0) if is_negative else (code == 0)),
                    'Incorrect exit status: ' + name)
            require(c.get('expected_rejection') is is_negative,
                    'Incorrect expected-rejection flag: ' + name)
            duration = c.get('seconds')
            require(type(duration) in (int, float) and math.isfinite(duration) and duration >= 0,
                    'Invalid elapsed time: ' + name)
            rel = c.get('log')
            if not isinstance(rel, str) or Path(rel).name != rel or rel in ('.', '..'):
                raise ValueError('Unsafe or nonlocal log path: ' + repr(rel))
            require(rel not in paths, 'Reused log file: ' + rel)
            paths.add(rel)
            path = directory / rel
            if path.is_symlink() or not path.is_file():
                raise ValueError('Missing or symlinked log: ' + rel)
            require(isinstance(c.get('sha256'), str) and bool(SHA256.fullmatch(c['sha256'])),
                    'Invalid log digest: ' + name)
            raw = path.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == c.get('sha256'), 'Log hash mismatch: ' + name)
            text = raw.decode('utf-8', errors='replace')
            logs[name] = text
            if is_negative:
                require(replay_lean.negative_is_expected(text, name == 'PlaceholderControl'),
                        'Negative control did not show its expected contradiction: ' + name)
        for name, argv in [('lean_version', ['lean', '--version']), ('lake_version', ['lake', '--version'])] + NORMAL:
            require(by_name.get(name, {}).get('argv') == argv, 'Changed command: ' + name)
        for name in NEGATIVES:
            require(by_name.get(name, {}).get('argv') == ['lake', 'env', 'lean', '-DwarningAsError=true',
                                                        f'verification/{name}.lean'], 'Changed control: ' + name)
        require(replay_lean.PIN in logs.get('lean_version', '') and replay_lean.COMMIT in logs.get('lean_version', ''),
                'Lean version/commit does not match the pin')
        for package in manifest['packages']:
            name = 'pin_' + package['name']
            c = by_name.get(name, {})
            argv = c.get('argv', [])
            require(isinstance(argv, list) and len(argv) == 5 and argv[:2] == ['git', '-C']
                    and argv[3:] == ['rev-parse', 'HEAD'] and isinstance(argv[2], str)
                    and Path(argv[2]).parts[-3:] == ('.lake', 'packages', package['name']),
                    'Changed dependency-pin command: ' + name)
            require(logs.get(name, '').strip() == package['rev'], 'Dependency pin differs: ' + name)
        require('Build completed successfully' in logs.get('build', ''), 'Missing successful build diagnostic')
        declared = parse_declared(logs.get('declared_axioms', ''))
        environment = parse_environment(logs.get('environment_axioms', ''))
        require(set(declared) == set(inventory['names']), 'Declared theorem coverage differs')
        require(set(declared) <= set(environment), 'Environment inventory omits declared theorems')
        require(all(declared[n] == environment[n][1] for n in set(declared) & set(environment)),
                'Declared and environment axiom routes disagree')
        require(all(ax <= ALLOWED_AXIOMS for _, ax in environment.values()), 'Unexpected theorem axioms')
        require(report.get('axiom_audit') == {'status': 'PASS', 'declared': len(declared), 'environment': len(environment)},
                'Recorded axiom totals differ from the actual logs')
        summary.update({'commands': len(commands), 'proof_inputs': len(expected_snapshot),
                        'declared_theorems': len(declared), 'environment_theorems': len(environment),
                        'axiom_free_declared': sum(not ax for ax in declared.values()),
                        'observed_axioms': sorted({ax for _, axs in environment.values() for ax in axs}),
                        'receipt_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest()})
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        errors.append(str(exc))
    summary.update(status='PASS' if not errors else 'FAIL', checks=checks, errors=errors)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt_directory', type=Path, help='Directory containing REPLAY.json and its logs')
    args = parser.parse_args()
    result = check_receipt(args.receipt_directory)
    print(json.dumps(result, indent=2))
    return int(result['status'] != 'PASS')

if __name__ == '__main__':
    raise SystemExit(main())
