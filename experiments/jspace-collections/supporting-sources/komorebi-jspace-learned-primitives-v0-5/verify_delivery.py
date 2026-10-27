"""Replay frozen predictions and reconstruct programs from development evidence. Komorebi P."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
from primitive_model import Kernels, Catalog
from executor import Executor
from run_experiment import hashfile, make_catalog, write
from cli import ROOT, load_bank


def verify():
    folder = ROOT / 'results'
    sources = json.loads((folder/'training_freeze.json').read_text())['sources']
    for name, sha in sources.items(): assert hashfile(ROOT/name) == sha, name
    for name, sha in json.loads((folder/'model_freeze.json').read_text()).items():
        assert hashfile(folder/'models'/name) == sha, name
    for name, sha in json.loads((folder/'prediction_freeze.json').read_text()).items():
        assert hashfile(folder/name) == sha, name
    models = {(seed, p.stem.rsplit('_', 1)[0]): Kernels.load(p)
              for seed in range(3) for p in (folder/'models').glob(f'*_{seed}.npz')}
    inputs = np.load(folder/'primitive_test_inputs.npz')
    counts = {}; max_replay_error = 0.

    def compare(kind, value, saved):
        nonlocal max_replay_error
        value, saved = np.asarray(value), np.asarray(saved)
        error = float(np.max(abs(value-saved)))
        assert np.array_equal(value, saved), (kind, error)
        max_replay_error = max(max_replay_error, error)
        counts[kind] = counts.get(kind, 0) + value.size

    for row in json.loads((folder/'primitive_predictions.json').read_text()):
        compare('primitive', models[row['seed'], row['model']].predict(inputs[row['cohort']]), row['predictions'])
    libraries = json.loads((folder/'program_libraries.json').read_text())
    for row in json.loads((folder/'composition_predictions.json').read_text()):
        executor = Executor(Catalog(models[row['seed'], row['model']],
                            make_catalog(folder, row['seed']).accepted, {'status':'evaluation_only_substitution'}))
        values = [executor.evaluate(entry['expression'], inputs[row['cohort']])
                  for entry in libraries[row['seed']]['entries']]
        compare('composition', values, row['predictions'])
    for row in json.loads((folder/'depth_predictions.json').read_text()):
        state = np.array(row['inputs'])
        for _ in range(row['depth']): state = models[row['seed'],row['model']].call('channel_42', state, state)
        compare('depth', state, row['predictions'])
    tasks = json.loads((folder/'workspace_tasks.json').read_text())
    banks = {s: load_bank(folder/f'workspaces_{s}.json', s) for s in range(3)}
    for row in json.loads((folder/'workspace_predictions.json').read_text()):
        task = tasks[row['case']]
        for cohort, a, b in [('in_range','q1','q2'),('larger_inputs','wide1','wide2')]:
            compare('workspace', banks[row['seed']].read('rule_'+str(row['case']), task[a], task[b]), row[cohort])
    # No final query inputs or targets are passed into this reconstruction.
    rebuilt = 0
    for library in libraries:
        executor = Executor(make_catalog(folder, library['seed']))
        entries = library['entries']
        candidates = executor.enumerate(np.array(entries[0]['demo_xy']), max_calls=3)
        assert len(candidates) == library['enumerated_programs']
        values = np.stack([c['values'] for c in candidates])
        for entry in entries:
            errors = np.max(abs(values-np.array(entry['demo_outputs'])), axis=1)
            candidate = candidates[int(np.flatnonzero(errors<=1e-6)[0])]
            assert candidate['expression'] == entry['expression']
            assert executor.catalog.kernels.identity() == entry['kernel_identity']
            error = np.max(abs(executor.evaluate(candidate['expression'], np.array(entry['validation_xy']))
                               - np.array(entry['validation_outputs'])))
            assert error <= 1e-6
            rebuilt += 1
    commands = 0
    with tempfile.TemporaryDirectory() as temp:
        bank = Path(temp)/'editable.json'
        def run(*args, good=True):
            nonlocal commands
            process = subprocess.run([sys.executable, str(ROOT/'cli.py'), '--bank', str(bank), *args],
                                     capture_output=True, text=True)
            assert (process.returncode == 0) == good, process.stderr
            commands += 1
            return json.loads(process.stdout) if good else process.stderr
        run('init'); run('fork','rule_0','trial')
        before = run('read','trial','2','1','--other','1','0')
        run('edit-amplitude','trial','0.5')
        after = run('read','trial','2','1','--other','1','0')
        assert np.max(abs(np.array(list(after.values()))-np.array(list(before.values()))-[4,3.5,4.5]))<1e-6
        old_hash = hashfile(bank)
        run('edit-amplitude','trial','nan',good=False)
        assert hashfile(bank) == old_hash
        assert run('undo','trial')['undone']
        assert run('read','trial','2','1','--other','1','0') == before
        assert abs(run('primitive','channel_42','3','4')['value']-12)<1e-6
        run('primitive','channel_63','3','4',good=False)
        run('init',good=False)
    report = {'author':'Komorebi P.', 'status':'passed', 'frozen_sources_verified':len(sources),
              'frozen_models_verified':len(models), 'exact_replayed_values_by_kind':counts,
              'exact_replayed_values':sum(counts.values()), 'maximum_replay_error':max_replay_error,
              'programs_reconstructed_from_development_only':rebuilt, 'live_cli_commands':commands,
              'rejected_nan_edit_preserved_file':True, 'powershell_runtime_executed':False}
    write(folder/'delivery_verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__': verify()
