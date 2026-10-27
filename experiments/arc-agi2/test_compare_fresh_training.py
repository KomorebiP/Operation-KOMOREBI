"""Synthetic comparison/watchdog controls; no frozen compiler imports/calls."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace


path = Path(__file__).with_name('compare_fresh_training.py')
spec = importlib.util.spec_from_file_location('fresh_compare_controls', path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def verify(value):
    if value.get('content_hash') != runner.digest({k: v for k, v in value.items() if k != 'content_hash'}):
        raise ValueError('content hash mismatch')


def grid(value):
    if not isinstance(value, list) or not value or not value[0]:
        raise ValueError('invalid grid')
    if any(len(row) != len(value[0]) or any(type(v) is not int or not 0 <= v <= 9 for v in row) for row in value):
        raise ValueError('invalid grid')


engine = SimpleNamespace(verify=verify, contract=SimpleNamespace(
    digest=runner.digest, canonical_json=canonical, validate_grid=grid))
task = {'train': [{'input': [[0]], 'output': [[1]]}], 'test': [{'input': [[2]]}]}


def fixture():
    candidate = {'entrant': 'synthetic', 'test_outputs': [[[3]]],
                 'behavior_hash': runner.digest([[[3]]]), 'program': {'op': 'never-executed'}}
    candidate['candidate_hash'] = runner.digest(candidate)
    return runner.seal({'task_semantic_hash': runner.digest(task),
        'base': [{'attempt_1': [[2]], 'attempt_2': [[3]]}],
        'candidates': [candidate], 'receipts': {'synthetic': {'status': 'ok', 'calls': 1}}})


def main():
    controls = []
    original = fixture()
    result = runner.compare_records(engine, task, original, copy.deepcopy(original))
    assert result['equivalent'] and result['providers']['synthetic']['identities_exact']
    controls.append('identical_completed_record_exact')
    assert runner.same_content_identity({'path': '/old/location', 'bytes': 3, 'sha256': 'abc'},
                                        {'path': '/restored/location', 'bytes': 3, 'sha256': 'abc'})
    assert not runner.same_content_identity({'path': '/old/location', 'bytes': 3, 'sha256': 'abc'},
                                            {'path': '/restored/location', 'bytes': 3, 'sha256': 'def'})
    controls.append('restored_paths_preserve_exact_content_binding')
    changed = copy.deepcopy(original)
    changed['receipts']['synthetic']['calls'] = True
    changed = runner.seal(changed)
    result = runner.compare_records(engine, task, original, changed)
    assert not result['equivalent'] and not result['receipts_exact'] and result['base_exact']
    controls.append('canonical_receipt_bool_integer_difference')
    changed = copy.deepcopy(original)
    changed['base'][0]['attempt_2'] = [[4]]
    changed = runner.seal(changed)
    assert not runner.compare_records(engine, task, original, changed)['base_exact']
    controls.append('resealed_base_difference')
    changed = copy.deepcopy(original)
    changed['candidates'] = []
    changed = runner.seal(changed)
    result = runner.compare_records(engine, task, original, changed)
    assert not result['candidate_identities_by_provider_exact']
    assert result['providers']['synthetic']['fresh_count'] == 0
    controls.append('provider_candidate_removal')
    for label, mutation in [
            ('record_seal_rejected', lambda r: r.update(content_hash='bad')),
            ('task_hash_rejected', lambda r: r.update(task_semantic_hash='bad'))]:
        changed = copy.deepcopy(original)
        mutation(changed)
        if label == 'task_hash_rejected': changed = runner.seal(changed)
        try:
            runner.validate_record(engine, task, changed)
        except ValueError:
            controls.append(label)
        else:
            raise AssertionError(label)
    with tempfile.TemporaryDirectory(prefix='fresh-training-controls-') as temp:
        folder = Path(temp)
        runner.atomic_json(folder / 'record.json', original)
        assert runner.read(folder / 'record.json') == original
        assert not (folder / 'record.json.partial').exists()
        controls.append('atomic_record_persistence')
        # This is an owned synthetic sleep child, never a compiler job.
        result = runner.run_owned([sys.executable, '-c', 'import time; time.sleep(30)'],
                                  folder, folder / 'timeout.log', 0.2, notify=lambda event: None)
        assert result['external_watchdog_timeout'] and result['exit_code'] != 0
        assert result['stop_actions'] and result['wall_seconds'] < 7
        controls.append('watchdog_stops_only_new_owned_group')
        result = runner.run_owned([sys.executable, '-c', 'import sys; sys.stdout.write("x"*100000)'],
                                  folder, folder / 'bounded.log', 5, notify=lambda event: None)
        assert result['exit_code'] == 0 and not result['external_watchdog_timeout']
        assert result['log_written_bytes'] == runner.LOG_CAP and result['log_received_bytes'] == 100000
        assert result['log_truncated']
        controls.append('stdout_drained_and_capped_without_blocking')
    report = runner.seal({'schema': 'block17.fresh-training-runner-synthetic-controls.v1',
        'recorded_at_utc': runner.utc(), 'controls': controls, 'all_controls_pass': True,
        'frozen_runtime_imported': False, 'compiler_calls': 0, 'query_targets_opened': False,
        'runner': runner.identity(path), 'test': runner.identity(Path(__file__))})
    runner.atomic_json(path.parent / 'fresh_training_runner_controls.json', report)
    print(json.dumps({'controls': len(controls), 'all_controls_pass': True, 'compiler_calls': 0}))


if __name__ == '__main__':
    main()
