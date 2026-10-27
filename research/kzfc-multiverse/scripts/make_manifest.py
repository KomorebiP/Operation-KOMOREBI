#!/usr/bin/env python3
"""Build a provenance manifest from a completed recorded proof run.

This does not run Lean or reinterpret failed/incomplete runs as success.
Only hashes actually recorded by the verifier and wrapper are input evidence.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())

def main() -> int:
    r = load('verification/RESULTS.json')
    p = load('verification/process_record.json')
    c = load('verification_contract.json')
    if r.get('status') != 'PASS' or p.get('exit_status') != 0:
        raise ValueError('A complete PASS and zero staged-completion status are required')
    if not all(x.get('passed') for x in r['checks']):
        raise ValueError('A recorded check failed')
    before, after = r['input_hashes_before'], r['input_hashes_after']
    if before != after:
        raise ValueError('Proof execution inputs changed during the run')
    artifacts = []
    for name, sha in sorted(before.items()):
        if digest(ROOT / name) != sha:
            raise ValueError(f'Input changed since verification: {name}')
        artifacts.append({'path': name, 'sha256': sha, 'sha256_after': after[name]})
    wrapper = p['wrapper_path']
    if p['wrapper_sha256_before'] != p['wrapper_sha256_after']:
        raise ValueError('Recording wrapper changed during execution')
    if digest(ROOT / wrapper) != p['wrapper_sha256_after']:
        raise ValueError('Recording wrapper changed after execution')
    if wrapper not in before:
        artifacts.append({'path': wrapper, 'sha256': p['wrapper_sha256_before'],
                          'sha256_after': p['wrapper_sha256_after']})
    declared = c['declared_results']
    logs = sorted({x['log'] for x in r['checks'] if 'log' in x} |
                  {'verification/process_record.json',
                   'verification/staged_state.json'})
    outputs = [{'path': f, 'sha256': digest(ROOT/f), 'kind': 'result'} for f in declared]
    outputs += [{'path': f, 'sha256': digest(ROOT/f), 'kind': 'log'} for f in logs]
    m = {
        'schema_version': 2,
        'claim_id': c['claim_id'],
        'repository': {
            'commit': 'unavailable: archive-based project; recorded proof-input hashes and predecessor archive hash identify the source',
            'dirty': True,
            'predecessor_archive_sha256': digest(ROOT/'provenance/predecessor_v0.9.0.zip'),
        },
        'command': c['command'],
        'environment': {
            'software': [
                {'name': 'Lean', 'version': r['lean_version']},
                {'name': 'Lake', 'version': r['lake_version']},
                {'name': 'Mathlib', 'version': 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'},
                {'name': 'Python', 'version': platform.python_version()},
            ],
            'hardware': r['platform'] + '; observed cgroup memory maximum 4 GiB and CPU quota equivalent to four cores; no additional process affinity imposed',
            'dependency_provenance': 'Pinned dependency manifest and verified portable runtime archive. Dependency source, compiler and cache are external to this distribution.',
        },
        'mathematics': {
            'assertion_tested': c['mathematical_claim'],
            'coefficient_domain': c['input_domain'],
            'conventions': 'Strict <kappa support bounds; relative intersections inside the carrier; Kuratowski pair function graphs; initial-ordinal set code for the cardinal parameter; membership-only first-order syntax; Mathlib filter order is reversed inclusion.',
            'inputs': [x['path'] for x in artifacts],
            'bounds': c['bounds'],
            'non_claims': c['non_claims'],
        },
        'randomness': {'used': False, 'generator': 'none', 'seed': None},
        'run': {
            'started_at': p['started_at'],
            'runtime_seconds': p['runtime_seconds'],
            'exit_status': p['exit_status'],
            'status': 'completed',
            'resource_limits': {'memory_bytes': None, 'cpu_seconds': None,
                                'max_cores': None, 'max_threads': None},
            'wall_timeout_seconds_per_compiler_command': r['per_command_timeout_seconds'],
            'project_target_concurrency': 1,
            'environment_limits_observed': c['environment_limits_observed'],
            'missing_results': [], 'invalid_results': [],
        },
        'input_artifacts': artifacts,
        'execution_artifacts': [x['path'] for x in artifacts],
        'declared_results': declared,
        'outputs': outputs,
        'checks': r['checks'],
        'result': 'PASS: recorded clean serial staged build, separate elaboration of every mathematical module, complete 502-name theorem axiom audit, source scan, matching proof-input hashes, preserved predecessor mathematical sources and expected negative controls. Universal mathematical scope is supplied by kernel-checked proof terms, not finite testing.',
        'residual_risks': [
            'Lean compiler/kernel, ambient axioms, pinned dependency cache, runtime and platform are trusted. The dependency cache was not rebuilt from scratch in this run.',
            'Internal small-product arithmetic and the original Extension-to-Fine-to-Compactness forward implications are proved in arbitrary ZFC models. The internal compactness-to-extension converse remains unfinished. No separate proof-calculus extraction is claimed.',
            'The guard and closed sentence are interpreted, not proved true. No uncountable existence or independence claim is made.',
            'Input snapshots cover the recorded project proof files, dependency pins, contract, verifier and wrapper, not every external runtime byte. Predecessor reference files are pinned and checked against current source by the recorded equality audit.',
            'The runtime was restored from stored parts with the expected archive hash. Development parser, binder-substitution and elaboration errors are retained and were repaired. The final audit is a separate clean staged run. Direct container execution was unavailable and actual compiler commands were executed through Python subprocesses.',
        ],
    }
    target = ROOT/'verification/computation_manifest.json'
    target.write_text(json.dumps(m, indent=2)+'\n')
    print(f'Wrote {target.name}: {len(artifacts)} pinned inputs, {len(outputs)} hashed outputs.')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Manifest generation failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
