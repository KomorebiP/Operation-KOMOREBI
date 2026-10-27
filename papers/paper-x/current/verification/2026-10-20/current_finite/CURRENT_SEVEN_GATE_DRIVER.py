#!/usr/bin/env python3
"""Replay the actual consumed Paper X scientific closure after reader-source freeze.

This is a new execution, not a refresh of earlier receipt hashes. It excludes
unconsumed publication PDFs and mutable release metadata from scientific pins.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/scratch/fbc994080222/paper_x_release/Paper_X_Final_Release_v1.0.0')
OUT = 'verification/2026-10-20/current_finite'
DEPS = Path('/workspace/scratch/fbc994080222/p5_finite_current/dependency_packages')
sys.path.insert(0, str(DEPS))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def closure(root):
    recovery = json.loads((root / 'verification/2026-10-10/INPUT_RECOVERY.json').read_text())['files']
    paths = {r['path'] for r in recovery if r['path'].startswith((
        'formal_preservation/', 'inherited_baseline/', 'current_continuation/', 'status_records/'))}
    paths.update(p.relative_to(root).as_posix() for p in (root / 'formal_preservation').rglob('*') if p.is_file())
    paths.update(['verification/run_checks.py', 'verification/source_integrity.py',
        'verification/tests/test_reader_regressions.py', 'verification/2026-10-10/INPUT_RECOVERY.json',
        'predecessor_files/manuscript/Paper_X_Block27_Amended.tex',
        'manuscript/Paper_X_Block27_Amended.tex', 'lean_guide/PRINTED_SOURCE_MANIFEST.json',
        'lean_guide/SOURCE_EXCERPT_LINEAGE.json', 'lean_guide/ConditionalOccupiedSystemCompletion.lean',
        'visual_appendix/checks/verify_examples.py', 'visual_appendix/source/models.py'])
    for row in json.loads((root / 'lean_guide/PRINTED_SOURCE_MANIFEST.json').read_text()):
        paths.update([row['source'], row['render']])
    for row in json.loads((root / 'lean_guide/SOURCE_EXCERPT_LINEAGE.json').read_text()):
        paths.update([row['reader_copy'], 'formal_preservation/' + row['payload_path']])
    return sorted(paths)


def main():
    additions = HERE / 'current_package_additions'
    if additions.exists():
        raise SystemExit('Refusing to replace prior current-source execution')
    inputs = closure(ROOT)
    before = {p: sha(ROOT / p) for p in inputs}
    versions = [{'name': 'Python', 'version': platform.python_version()}] + [
        {'name': n, 'version': importlib.metadata.version(n)}
        for n in ['numpy', 'sympy', 'matplotlib', 'pytest']]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg',
        PYTHONPATH=str(DEPS) + os.pathsep + os.environ.get('PYTHONPATH', ''))
    with tempfile.TemporaryDirectory(prefix='paper-x-current-frozen-sources-') as temporary:
        stage = Path(temporary) / 'Paper_X'
        shutil.copytree(ROOT, stage)
        tools = stage / 'verification/finite_tools'
        tools.mkdir(exist_ok=True)
        for n in ['run_experiment.py', 'validate_manifest.py']:
            if (tools / n).exists() and sha(tools / n) != sha(HERE / 'tools' / n):
                raise SystemExit('Existing bounded helper differs: ' + n)
            shutil.copy2(HERE / 'tools' / n, tools / n)
        artifacts = inputs + ['verification/finite_tools/run_experiment.py',
                              'verification/finite_tools/validate_manifest.py']
        artifacts = sorted(set(artifacts))
        contract = {'claim_id': 'PAPER_X_CURRENT_FROZEN_SOURCE_SEVEN_GATE_REPLAY',
            'mathematics': {'assertion_tested': 'The unchanged seven-gate launcher passes on the frozen current scientific/source-lineage inputs, with publication output bytes checked separately.',
                'coefficient_domain': 'Exact integers, finite rational/SymPy examples, original NumPy floating models, and byte-level provenance hashes',
                'conventions': 'Original conditional internal claim scope and original finite-model conventions are retained.',
                'inputs': ['Scientific/provenance closure actually read by the seven selected gates; immutable historical source/object records; current statement source and printed module views'],
                'bounds': {'gates': 7, 'reader_methods': 13, 'canonical_towers': 3123,
                    'visual_exact_assertions': 263, 'visual_false_controls': 14,
                    'original_pytest_functions': 28, 'saved_residue_modules': 255,
                    'source_closure_files_excluding_helpers': len(inputs)},
                'non_claims': ['No fresh Lean compilation or axiom replay.',
                    'No universal companion/carrier/nonzero occupancy existence follows from finite examples.',
                    'Publication PDFs, page routes and visual review require separate current bound evidence.',
                    'Floating model values remain numerical outputs even if their serialized values agree exactly.']},
            'execution_artifacts': artifacts, 'software': versions,
            'randomness': {'used': False, 'generator': '', 'seed': None}}
        output = stage / OUT
        cpath = output / 'contract.json'
        write(cpath, contract)
        run = OUT + '/run'
        results = [run + '/gates/RESULTS.json', run + '/gates/visual_exact_results.json',
                   run + '/gates/original_models.json'] + [run + '/gates/' + n + '.log' for n in
            ['preservation', 'source_integrity', 'reader_regressions', 'visual_exact',
             'original_pytest', 'original_worked_models', 'residue_saved_hashes']]
        argv = [sys.executable, '-B', str(tools / 'run_experiment.py'), '--root', str(stage),
            '--contract', str(cpath), '--output', run, '--timeout', '600', '--max-output-bytes', '4194304',
            '--max-memory-bytes', '4294967296', '--max-cpu-seconds', '540', '--max-cores', '1', '--max-threads', '1']
        for p in artifacts:
            argv += ['--input', p]
        for p in results:
            argv += ['--result', p]
        argv += ['--', sys.executable, '-B', 'verification/run_checks.py', '--output', run + '/gates']
        done = subprocess.run(argv, cwd=stage, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / 'launcher.log').write_text(done.stdout)
        manifest = stage / run / 'manifest.json'
        validation = subprocess.run([sys.executable, '-B', str(tools / 'validate_manifest.py'),
            str(manifest), '--root', str(stage)], cwd=stage, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / 'VALIDATION.log').write_text(validation.stdout)
        m = json.loads(manifest.read_text()) if manifest.exists() else {}
        result_path = stage / run / 'gates/RESULTS.json'
        gates = json.loads(result_path.read_text()) if result_path.exists() else None
        after = {p: sha(ROOT / p) for p in inputs}
        unchanged = before == after
        good = done.returncode == validation.returncode == 0 and m.get('run', {}).get('status') == 'completed' and \
            gates is not None and gates['all_passed'] and gates['complete'] and unchanged
        report = {'schema': 'komorebi.paper-x.current-source-seven-gate-replay/1',
            'status': 'PASS_STATED_FINITE_SCOPE' if good else 'INCOMPLETE_OR_FAILED',
            'observed_utc': datetime.now(timezone.utc).isoformat(), 'execution_exit': done.returncode,
            'manifest_validation_exit': validation.returncode, 'run_status': m.get('run', {}).get('status'),
            'manifest': run + '/manifest.json', 'gates': gates, 'scientific_input_files': len(inputs),
            'scientific_inputs_unchanged_during_execution': unchanged, 'input_hashes_before': before,
            'input_hashes_after': after, 'fresh_lean_execution': False,
            'scope': 'New execution after current source freeze. The earlier full October10 baseline run remains separate historical-selection evidence.'}
        write(output / 'CURRENT_FINITE_REPLAY.json', report)
        shutil.copy2(Path(__file__), output / 'CURRENT_SEVEN_GATE_DRIVER.py')
        shutil.copytree(output, additions / OUT)
        shutil.copytree(tools, additions / 'verification/finite_tools')
    write(HERE / 'CURRENT_FINITE_REPLAY.json', report)
    print(json.dumps({k: report[k] for k in ['status', 'execution_exit', 'manifest_validation_exit',
        'run_status', 'scientific_input_files', 'scientific_inputs_unchanged_during_execution']}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
