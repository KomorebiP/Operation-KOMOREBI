#!/usr/bin/env python3
"""Fresh bounded Paper X finite replay from an explicitly selected source tree.

No baseline file is changed. New evidence is prepared for the same relative
location in a future release root. Mathematical statements are not expanded.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
BASELINE = Path('/workspace/scratch/fbc994080222/paper_x_baseline/inner/Paper_X')
OUTPUT_REL = 'verification/2026-10-20/finite'
BLOCK = 'inherited_baseline/original_releases/block27'
DEPS = Path('/workspace/scratch/fbc994080222/p5_finite_current/dependency_packages')
sys.path.insert(0, str(DEPS))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {p.relative_to(path).as_posix(): digest(p)
            for p in sorted(path.rglob('*')) if p.is_file()}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def observed_source_bounds(path):
    text = path.read_text()
    result = []
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, (ast.For, ast.comprehension)):
            result.append({'line': getattr(n, 'lineno', None),
                           'iterator_expression': ast.get_source_segment(text, n.iter) or ast.unparse(n.iter)})
        elif isinstance(n, ast.Assert):
            result.append({'line': n.lineno, 'assertion': ast.unparse(n.test)})
    return result


def main():
    additions = HERE / 'package_additions'
    if additions.exists():
        raise SystemExit('Refusing to replace previous evidence')
    before = tree(BASELINE)
    started = datetime.now(timezone.utc).isoformat()
    software = [{'name': 'Python', 'version': platform.python_version()}] + [
        {'name': name, 'version': importlib.metadata.version(name)}
        for name in ['numpy', 'sympy', 'matplotlib', 'pytest']]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg',
               PYTHONPATH=str(DEPS) + os.pathsep + os.environ.get('PYTHONPATH', ''))
    records = []
    with tempfile.TemporaryDirectory(prefix='paper-x-finite-selected-baseline-') as temporary:
        stage = Path(temporary) / 'Paper_X'
        shutil.copytree(BASELINE, stage)
        tools = stage / 'verification/finite_tools'
        tools.mkdir()
        for name in ['run_experiment.py', 'validate_manifest.py']:
            shutil.copy2(HERE / 'tools' / name, tools / name)
        evidence = stage / OUTPUT_REL
        common = ['verification/finite_tools/run_experiment.py', 'verification/finite_tools/validate_manifest.py']
        jobs = [('documented_seven_gates', None)] + [(name, f'exact_{name}.py') for name in
            ['precision', 'summands', 'families', 'logarithms', 'quadratic_packets', 'local_quadratic']]
        for name, filename in jobs:
            out = OUTPUT_REL + '/runs/' + name
            if filename is None:
                inputs = sorted(before) + common
                maths = {
                    'assertion_tested': 'The unchanged documented seven-gate launcher completes preservation/source-lineage checks, reader regressions, exact symbolic examples, original pytest and worked models, and saved residue source/object digest checks.',
                    'coefficient_domain': 'Exact integers, rational/SymPy finite examples and original NumPy floating illustrations; hashes are byte-level metadata.',
                    'conventions': 'Original column-vector packet operations, selected finite forest and occupancy models, and inherited source contracts.',
                    'inputs': ['Explicitly selected unchanged October10 Paper_X source tree'],
                    'bounds': {'gates': 7, 'reader_test_methods': 13,
                        'canonical_four_level_towers': {'primes': [2, 3, 5, 7], 'towers': 3123},
                        'visual_positive_assertions': 263, 'visual_adverse_controls': 14,
                        'original_pytest_functions_in_source': 28,
                        'residue_digest_check': '255 saved source/object pairs; compiler is not invoked'},
                    'non_claims': ['No Lean compilation or full transitive axiom audit.',
                        'Exact finite examples and floating illustrations do not certify universal companion/carrier existence or nonzero occupancy.',
                        'The saved object checks retain inherited compiler status.']}
                cmd = [sys.executable, '-B', 'verification/run_checks.py', '--output', out + '/gates']
                results = [out + '/gates/RESULTS.json', out + '/gates/visual_exact_results.json',
                           out + '/gates/original_models.json'] + [out + '/gates/' + n + '.log' for n in
                    ['preservation', 'source_integrity', 'reader_regressions', 'visual_exact',
                     'original_pytest', 'original_worked_models', 'residue_saved_hashes']]
                randomness = {'used': False, 'generator': '', 'seed': None}
            else:
                code = BLOCK + '/checks/' + filename
                inputs = [code] + common
                if name == 'families':
                    inputs.append(BLOCK + '/checks/exact_summands.py')
                template_path = stage / BLOCK / 'checks' / (name.replace('_packets', '') + '_run') / 'manifest.json'
                if name == 'local_quadratic':
                    template_path = stage / BLOCK / 'checks/local_quadratic_run/manifest.json'
                if name == 'precision':
                    # This older checker emits a v1 sidecar at a fixed legacy path.
                    # The outer v2 run supplies observed inputs and enforced limits.
                    maths = {'assertion_tested': 'Finite integral C2, C4 and S3 averaging preserves the implemented retained precision and satisfies the explicit obstruction controls.',
                        'coefficient_domain': 'Exact integers and fractions.Fraction',
                        'conventions': 'Column-vector integral group actions, exact Reynolds average divided by group order, p-integral congruences.',
                        'inputs': [code], 'bounds': {'C2_frame_entries': [-2, 2], 'C2_moduli': [4, 8],
                            'C4_modulus': 8, 'S3_moduli': [4, 9], 'S3_extra_lift_digits': [2, 3]},
                        'non_claims': ['No universal complete-DVR lifting, arithmetic realization or Lean theorem is proved by this finite run.']}
                    randomness = {'used': False, 'generator': '', 'seed': None}
                else:
                    old = json.loads(template_path.read_text())
                    maths, randomness = old['mathematics'], old['randomness']
                    inputs.append(template_path.relative_to(stage).as_posix())
                maths['bounds']['executed_source_expressions'] = observed_source_bounds(stage / code)
                maths['non_claims'].append('Current execution replays existing finite code, and does not expand the selected amended conditional manuscript contract.')
                # A disposable branch copy preserves all original fixed output files.
                inline = (
                    "import pathlib,tempfile,shutil,subprocess,sys,json,hashlib;"
                    "root=pathlib.Path.cwd();out=root/sys.argv[1];src=root/sys.argv[2];"
                    "tmp=tempfile.TemporaryDirectory(prefix='paperx-finite-branch-');"
                    "work=pathlib.Path(tmp.name)/'block27';shutil.copytree(src,work);"
                    "script=work/'checks'/sys.argv[3];"
                    "argv=[sys.executable,'-B',str(script)];"
                    "argv+=[] if sys.argv[3]=='exact_precision.py' else ['--output',str(out/'result.json')];"
                    "p=subprocess.run(argv,cwd=work,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);"
                    "(out/'command.log').write_text(p.stdout);print(p.stdout,end='');"
                    "record={'argv':argv,'cwd':str(work),'exit_status':p.returncode,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest()};"
                    "(out/'EXECUTION.json').write_text(json.dumps(record,indent=2)+'\\n');"
                    "shutil.copy2(work/'exact_precision.json',out/'result.json') if sys.argv[3]=='exact_precision.py' and (work/'exact_precision.json').exists() else None;"
                    "shutil.copy2(work/'exact_precision_manifest.json',out/'LEGACY_INNER_MANIFEST.json') if sys.argv[3]=='exact_precision.py' and (work/'exact_precision_manifest.json').exists() else None;"
                    "tmp.cleanup();sys.exit(p.returncode)")
                cmd = [sys.executable, '-B', '-c', inline, out, BLOCK, filename]
                results = [out + '/result.json', out + '/command.log', out + '/EXECUTION.json']
                if name == 'precision':
                    results.append(out + '/LEGACY_INNER_MANIFEST.json')
            contract = {'claim_id': 'PAPER_X_SELECTED_OCT10_FINITE_REPLAY_' + name.upper(),
                'mathematics': maths, 'execution_artifacts': sorted(set(inputs)),
                'software': software, 'randomness': randomness}
            cpath = evidence / 'contracts' / (name + '.json')
            write(cpath, contract)
            argv = [sys.executable, '-B', str(tools / 'run_experiment.py'), '--root', str(stage),
                '--contract', str(cpath), '--output', out, '--timeout', '600',
                '--max-output-bytes', '4194304', '--max-memory-bytes', '4294967296',
                '--max-cpu-seconds', '540', '--max-cores', '1', '--max-threads', '1']
            for item in contract['execution_artifacts']:
                argv += ['--input', item]
            for item in results:
                argv += ['--result', item]
            argv += ['--'] + cmd
            p = subprocess.run(argv, cwd=stage, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            log = evidence / 'launcher_logs' / (name + '.log')
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(p.stdout)
            manifest = stage / out / 'manifest.json'
            validation = subprocess.run([sys.executable, '-B', str(tools / 'validate_manifest.py'),
                str(manifest), '--root', str(stage)], cwd=stage, env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (log.parent / (name + '_validation.log')).write_text(validation.stdout)
            m = json.loads(manifest.read_text()) if manifest.exists() else {}
            record = {'suite': name, 'execution_exit': p.returncode, 'manifest_validation_exit': validation.returncode,
                'run_status': m.get('run', {}).get('status', 'NO_MANIFEST'), 'manifest': out + '/manifest.json'}
            if name == 'documented_seven_gates':
                if (stage / out / 'gates/RESULTS.json').exists():
                    d = json.loads((stage / out / 'gates/RESULTS.json').read_text())
                    record['gates'] = d
                    v = json.loads((stage / out / 'gates/visual_exact_results.json').read_text())
                    record['visual_scope'] = {k: v[k] for k in ['positive_assertions', 'negative_controls_rejected', 'bounds', 'coefficient_domains']}
                    old_models = json.loads((stage / 'inherited_baseline/original_companion/results/residual_seed_results.json').read_text())
                    new_models = json.loads((stage / out / 'gates/original_models.json').read_text())
                    def leaves(x):
                        if isinstance(x, dict): return sum((leaves(v) for v in x.values()), [])
                        if isinstance(x, list): return sum((leaves(v) for v in x), [])
                        return [x]
                    fields = [x for x in leaves(new_models) if isinstance(x, (int, float)) and not isinstance(x, bool)]
                    record['worked_model_comparison'] = {'record_equal': old_models == new_models,
                        'numeric_fields': len(fields), 'scope': 'Exact comparison of stored JSON values; floating values remain numerical model outputs.'}
                    write(stage / out / 'MODEL_COMPARISON.json', record['worked_model_comparison'])
                    if old_models != new_models:
                        record['interpretation_failure'] = 'Worked model JSON differs'
                    if not d['complete'] or not d['all_passed']:
                        record['interpretation_failure'] = 'Documented gate set incomplete or failed'
            elif (stage / out / 'result.json').exists():
                d = json.loads((stage / out / 'result.json').read_text())
                record['result_summary'] = {k: d[k] for k in ['status', 'verdict', 'counts', 'totals', 'bounds', 'target_depth', 'non_claims'] if k in d}
            records.append(record)
            print(json.dumps({k: record[k] for k in ['suite', 'execution_exit', 'manifest_validation_exit', 'run_status']}), flush=True)
        unchanged = before == tree(BASELINE)
        write(evidence / 'BASELINE_PRESERVATION.json', {'status': 'PASS' if unchanged else 'INPUTS_CHANGED',
            'selected_baseline_path': str(BASELINE), 'files': len(before), 'hashes_before': before,
            'hashes_after': tree(BASELINE)})
        passed = unchanged and all(r['execution_exit'] == r['manifest_validation_exit'] == 0 and
            r['run_status'] == 'completed' and 'interpretation_failure' not in r for r in records)
        report = {'schema': 'komorebi.paper-x.selected-baseline-finite-replay/1',
            'status': 'PASS_STATED_FINITE_SCOPE' if passed else 'INCOMPLETE_OR_FAILED',
            'selected_baseline': 'Explicit October10 source selection. Missing newer October16/17 packages were not recovered or silently substituted.',
            'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
            'software': software, 'hardware': platform.platform(), 'driver_sha256': digest(Path(__file__)),
            'runs': records, 'baseline_unchanged': unchanged, 'fresh_lean_execution': False,
            'relative_evidence_location_for_release_integration': OUTPUT_REL,
            'non_claims': ['Counts in different suites overlap and must not be summed into theorem coverage.',
                'No universal companion, carrier or nonzero-occupancy existence is tested.',
                'No fresh Lean compilation or axiom replay; stored source/object hashes retain historical compilation scope.',
                'Floating dimension/plot outputs do not become exact mathematical certificates by JSON equality.',
                'The selected amended conditional contract remains distinct from stronger later attempts.']}
        write(evidence / 'FINITE_REPLAY.json', report)
        shutil.copy2(Path(__file__), evidence / 'REPLAY_DRIVER.py')
        (additions / 'verification').mkdir(parents=True)
        shutil.copytree(evidence, additions / OUTPUT_REL)
        shutil.copytree(tools, additions / 'verification/finite_tools')
        validations = []
        for record in records:
            check = subprocess.run([sys.executable, '-B', str(tools / 'validate_manifest.py'),
                str(stage / record['manifest']), '--root', str(stage)], cwd=stage, env=env,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            validations.append({'suite': record['suite'], 'exit_status': check.returncode})
        write(additions / OUTPUT_REL / 'FINAL_STAGE_MANIFEST_VALIDATION.json', validations)
    write(HERE / 'FINITE_REPLAY.json', report)
    print(json.dumps({'status': report['status'], 'all_final_stage_manifests_valid': all(x['exit_status'] == 0 for x in validations),
        'package_additions': str(additions), 'baseline_unchanged': unchanged}), flush=True)
    return 0 if passed and all(x['exit_status'] == 0 for x in validations) else 1


if __name__ == '__main__':
    raise SystemExit(main())
