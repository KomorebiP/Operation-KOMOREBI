#!/usr/bin/env python3
"""Tiny synthetic-only controls for the exterior Block17 census assembler.

No live challenge/checkpoint/target files, frozen runtime modules, compiler,
dispatcher or candidate programs are opened or invoked by these tests.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import tempfile


def load(path, name):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_reference_digest(value):
    # Independent ordinary frozen stdlib serialization, no streaming encoder.
    text = json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def frozen_reference_seal(value):
    result = copy.deepcopy(value)
    result.pop('content_hash', None)
    result['content_hash'] = frozen_reference_digest(result)
    return result


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True,
                              ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def fixture(folder, asm):
    clean = {
        'a-task': {'train': [{'input': [[0]], 'output': [[1]]}],
                   'test': [{'input': [[2]]}, {'input': [[3, 4]]}]},
        'z-\u96ea': {'train': [{'input': [[1, 2]], 'output': [[3]]}],
                   'test': [{'input': [[4]]}]},
    }
    bindings = {'code_hash': 'synthetic-code', 'bank_hash': 'synthetic-bank'}
    run_hash = frozen_reference_digest({'code': bindings['code_hash'],
        'bank': bindings['bank_hash'], 'challenges': clean, 'include_new': True,
        'limits': asm.LIMITS})
    header = asm.census_header(clean, **bindings, run_hash=run_hash)
    records = {}
    paths = {}
    folder.mkdir()
    for task_id, task in clean.items():
        task_hash = frozen_reference_digest(task)
        outputs = [[[index + 1]] for index, _ in enumerate(task['test'])]
        candidate = {'test_outputs': outputs, 'behavior_hash': frozen_reference_digest(outputs),
            'task_semantic_hash': task_hash, 'entrant': '\u03bb\u96ea', 'source_block': 13,
            'note': 'literal newline\n\tand \\" quote', 'weights': [0.1, -0.0, 1e-12, 1e20],
            'empty': {}, 'nested': [None, True, False, [], {'\u96ea': '\u2603'}]}
        candidate['candidate_hash'] = frozen_reference_digest(candidate)
        record = frozen_reference_seal({'task_semantic_hash': task_hash,
            'base': [{'attempt_1': [[1]], 'attempt_2': [[2]]} for _ in task['test']],
            'candidates': [candidate], 'receipts': {'synthetic': {'status': 'ok',
                'note': 'compiler was never called', 'nested': {'a': [1, 2]}}}})
        records[task_id] = record
        path = folder / (asm.digest(task_id) + '.json')
        paths[task_id] = path
        save(path, frozen_reference_seal({'run_hash': run_hash, 'record': record}))
    ids = {key: asm.identity(path) for key, path in paths.items()}
    metadata = asm.seal({'completed_utc': '2026-10-09T00:00:00+00:00',
        'run_hash': run_hash, **bindings, 'limits': asm.LIMITS,
        'label_access': 'demonstrations_only', 'source_changes': False, 'policy_changes': False,
        'scheduler_sha256': 'synthetic-scheduler', 'reserved_active_task_ids': [],
        'initial_missing': 2, 'events': [
            {'task_id': 'a-task', 'event': 'started'},
            {'task_id': 'a-task', 'event': 'checkpoint_written',
             'record_hash': records['a-task']['content_hash']},
            {'task_id': 'z-\u96ea', 'event': 'started'},
            {'task_id': 'z-\u96ea', 'event': 'duplicate_identical_not_overwritten',
             'record_hash': records['z-\u96ea']['content_hash']}]})
    inputs = {name: {'path': str((folder / (name + '.synthetic')).resolve()),
                     'bytes': 1, 'sha256': 'synthetic-identity'}
              for name in ('challenges', 'source_snapshot', 'supplemental_metadata')}
    pre = asm.seal({'schema': asm.PRE_SCHEMA, 'recorded_at_utc': '2026-10-09T00:00:00+00:00',
        'targets_opened': False, 'source_budget_policy_changes': False, 'all_scans_stopped': True,
        'tasks': 2, 'test_outputs': 3, 'run_hash': run_hash, 'source_bindings': bindings,
        **inputs, 'supplemental_metadata_content_hash': metadata['content_hash'],
        'checkpoints': ids, 'sessions': [
            {'role': 'primary_scan', 'session_id': 101, 'stopped': True, 'exit_code': 1,
             'mode': 'natural_exit', 'completion_evidence': 'synthetic failed aggregate after records'},
            {'role': 'supplemental_scan', 'session_id': 102, 'stopped': True, 'exit_code': 0,
             'mode': 'natural_exit', 'completion_evidence': 'synthetic terminal metadata'}]})
    return clean, header, records, paths, ids, metadata, inputs, pre


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    script = workspace / 'arc-evidence/scripts/assemble_block17_census_streaming.py'
    asm = load(script, 'synthetic_assembler')
    adapter, adapter_id = asm.load_helper(workspace / 'arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py',
        'synthetic_assembly_adapter', asm.PINS['adapter_sha256'])
    gate, gate_id = asm.load_helper(workspace / 'arc-evidence/scripts/authenticate_block17_supplement.py',
        'synthetic_assembly_agreement', asm.PINS['gate_sha256'])
    results = []
    with tempfile.TemporaryDirectory(prefix='block17-assembly-synthetic-') as temp:
        root = Path(temp)
        clean, header, records, paths, ids, metadata, inputs, pre = fixture(root / 'positive', asm)
        asm.validate_metadata(metadata, header, 'synthetic-scheduler', clean, planned_scope=2)
        asm.validate_pre_receipt(pre, clean, header, inputs, ids, metadata,
                                 expected_tasks=2, expected_outputs=3)
        stable_count = 0

        def stable():
            nonlocal stable_count
            assert all(asm.identity(paths[key]) == value for key, value in ids.items())
            stable_count += 1

        output = root / 'synthetic-census.json'
        actual = asm.assemble_records(clean, paths, ids, header, output, adapter, gate, metadata, stable)
        reference = frozen_reference_seal({**header, 'records': records})
        expected_bytes = (json.dumps(reference, indent=2, sort_keys=True,
                         ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
        assert output.read_bytes() == expected_bytes
        assert json.loads(output.read_text(encoding='utf-8')) == reference
        assert actual['content_hash'] == reference['content_hash']
        assert actual['record_hashes'] == {key: item['content_hash'] for key, item in records.items()}
        assert len(actual['completion_event_agreements']) == 2
        assert sum(row['event'] == 'duplicate_identical_not_overwritten'
                   for row in actual['completion_event_agreements']) == 1
        assert stable_count == 2 and not output.with_name(output.name + '.partial').exists()
        results.append({'name': 'two_tasks_three_outputs_frozen_object_seal_and_bytes', 'passed': True,
            'census_bytes': len(expected_bytes), 'census_sha256': hashlib.sha256(expected_bytes).hexdigest(),
            'census_content_hash': reference['content_hash']})

        def negative(name, mutation, expected_error):
            folder = root / name
            data = fixture(folder, asm)
            c, h, r, p, i, m, inp, pr = data
            out = root / (name + '-census.json')
            stability = lambda: None
            mutation(data)
            # Authenticate the changed raw input identity deliberately, so inner
            # negative controls reach their named semantic validator.
            i.update({key: asm.identity(path) for key, path in p.items()})
            try:
                asm.assemble_records(c, p, i, h, out, adapter, gate, m, stability)
            except (ValueError, KeyError, TypeError) as exc:
                assert expected_error in str(exc), (name, expected_error, str(exc))
                assert not out.exists() and not out.with_name(out.name + '.partial').exists()
                results.append({'name': name, 'passed': True, 'observed_rejection': str(exc)})
            else:
                raise AssertionError('negative control accepted: ' + name)

        def alter_wrapper(data, callback, reseal_wrapper=True):
            c, h, r, p, i, m, inp, pr = data
            value = asm.read_json(p['a-task'])
            callback(value)
            save(p['a-task'], asm.seal(value) if reseal_wrapper else value)

        def alter_record(data, callback, reseal_record=True):
            def change(wrapper):
                callback(wrapper['record'])
                if reseal_record:
                    wrapper['record'] = asm.seal(wrapper['record'])
            alter_wrapper(data, change)

        negative('wrapper_seal', lambda d: alter_wrapper(d, lambda w: w.update(content_hash='bad'), False),
                 'content hash mismatch')
        negative('wrapper_extra_key', lambda d: alter_wrapper(d, lambda w: w.update(extra=True)),
                 'wrapper keys differ')
        negative('checkpoint_run', lambda d: alter_wrapper(d, lambda w: w.update(run_hash='bad')),
                 'checkpoint run binding differs')
        negative('record_seal', lambda d: alter_record(d, lambda r: r.update(content_hash='bad'), False),
                 'content hash mismatch')
        negative('record_task', lambda d: alter_record(d, lambda r: r.update(task_semantic_hash='bad')),
                 'record task binding differs')
        negative('base_arity', lambda d: alter_record(d, lambda r: r['base'].pop()),
                 'base test membership differs')
        negative('base_grid_bool', lambda d: alter_record(d, lambda r: r['base'][0].update(attempt_1=[[True]])),
                 'invalid colors')
        negative('candidate_arity', lambda d: alter_record(d, lambda r: r['candidates'][0]['test_outputs'].pop()),
                 'candidate test membership differs')
        negative('candidate_behavior', lambda d: alter_record(d, lambda r: r['candidates'][0].update(behavior_hash='bad')),
                 'candidate behavior binding differs')
        negative('candidate_seal', lambda d: alter_record(d, lambda r: r['candidates'][0].update(candidate_hash='bad')),
                 'candidate content binding differs')

        def change_candidate_task(data):
            def change(record):
                candidate = record['candidates'][0]
                candidate['task_semantic_hash'] = 'bad'
                candidate['candidate_hash'] = asm.digest({key: value for key, value in candidate.items()
                                                         if key != 'candidate_hash'})
            alter_record(data, change)
        negative('candidate_task', change_candidate_task, 'candidate task binding differs')
        negative('missing_checkpoint_task', lambda d: d[3].pop('a-task'), 'checkpoint task membership differs')
        negative('extra_census_header', lambda d: d[1].update(candidate_tasks=2), 'census header keys differ')
        negative('supplement_duplicate_hash', lambda d: d[5]['events'][-1].update(record_hash='bad'),
                 'Supplemental completion differs')
        negative('supplement_incomplete', lambda d: d[5]['events'].pop(), 'unfinished tasks')

        # Input instability during the write pass must remove the sole partial.
        c, h, r, p, i, m, inp, pr = fixture(root / 'instability', asm)
        calls = 0
        def unstable():
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ValueError('synthetic post-write input instability')
        out = root / 'instability-census.json'
        try:
            asm.assemble_records(c, p, i, h, out, adapter, gate, m, unstable)
        except ValueError as exc:
            assert str(exc) == 'synthetic post-write input instability'
            assert not out.exists() and not out.with_name(out.name + '.partial').exists()
            results.append({'name': 'post_write_input_instability_cleans_partial', 'passed': True,
                            'observed_rejection': str(exc)})
        else:
            raise AssertionError('input instability accepted')

        def receipt_negative(name, change, expected):
            bad = copy.deepcopy(pre)
            change(bad)
            bad = asm.seal(bad)
            try:
                asm.validate_pre_receipt(bad, clean, header, inputs, ids, metadata,
                                         expected_tasks=2, expected_outputs=3)
            except ValueError as exc:
                assert expected in str(exc), (name, str(exc))
                results.append({'name': name, 'passed': True, 'observed_rejection': str(exc)})
            else:
                raise AssertionError('bad pre-assembly receipt accepted: ' + name)
        receipt_negative('pre_live_session', lambda p: p['sessions'][0].update(stopped=False), 'stop evidence differs')
        receipt_negative('pre_supplement_interrupted', lambda p: p['sessions'][1].update(mode='redundant_work_interrupt'),
                         'owning stop mode differs')
        receipt_negative('pre_same_session_id', lambda p: p['sessions'][1].update(session_id=101), 'stop evidence differs')
        receipt_negative('pre_wrong_checkpoint_identity', lambda p: p['checkpoints']['a-task'].update(sha256='bad'),
                         'checkpoint identities differ')
        receipt_negative('pre_targets_opened', lambda p: p.update(targets_opened=True), 'scope/stop evidence differs')
        receipt_negative('pre_wrong_counts', lambda p: p.update(tasks=120), 'task/output membership differs')
        receipt_negative('pre_predates_supplement_terminal',
                         lambda p: p.update(recorded_at_utc='2026-10-08T00:00:00+00:00'),
                         'predates terminal supplemental completion')

        for name, callback, expected in [
                ('metadata_unsealed', lambda m: m.update(content_hash='bad'), 'content hash mismatch'),
                ('metadata_not_terminal', lambda m: m.pop('completed_utc'), 'not terminal'),
                ('metadata_wrong_planned_scope', lambda m: m.update(initial_missing=1), 'planned scope differs')]:
            bad = copy.deepcopy(metadata)
            callback(bad)
            if name != 'metadata_unsealed':
                bad = asm.seal(bad)
            try:
                asm.validate_metadata(bad, header, 'synthetic-scheduler', clean, planned_scope=2)
            except ValueError as exc:
                assert expected in str(exc), (name, str(exc))
                results.append({'name': name, 'passed': True, 'observed_rejection': str(exc)})
            else:
                raise AssertionError('bad metadata accepted: ' + name)

        # Exact inventory includes stale temporary files, so no race is hidden.
        save(paths['a-task'].parent / 'unexpected.partial', {})
        try:
            asm.checkpoint_paths(paths['a-task'].parent, clean)
        except ValueError as exc:
            assert 'checkpoint inventory differs' in str(exc)
            results.append({'name': 'checkpoint_extra_temporary', 'passed': True,
                            'observed_rejection': str(exc)})
        else:
            raise AssertionError('extra checkpoint entry accepted')
        try:
            asm.sanitize({'train': [{'input': [[0]], 'output': [[1]]}],
                          'test': [{'input': [[2]], 'output': [[3]]}]})
        except ValueError as exc:
            assert 'attached test output rejected' in str(exc)
            results.append({'name': 'attached_query_output', 'passed': True,
                            'observed_rejection': str(exc)})
        else:
            raise AssertionError('attached query output accepted')

    report = asm.seal({'schema': 'komorebi.block17.streaming-assembly-synthetic-controls.v1',
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'preparation_only': True,
        'assembler': asm.identity(script), 'test': asm.identity(Path(__file__)),
        'helpers': {'adapter': adapter_id, 'agreement': gate_id},
        'tests': results, 'all_controls_pass': True,
        'positive_controls': 1, 'negative_controls': len(results) - 1,
        'targets_opened': False, 'live_challenges_checkpoints_census_read': False,
        'frozen_runtime_imported': False, 'compiler_dispatcher_program_calls': 0,
        'actual_production_assembly_performed': False,
        'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'scope': 'Two synthetic tasks / three outputs. Independent ordinary JSON serialization matches object, whole-body seal and exact pretty UTF8 bytes; negative controls isolate named failures.',
        'limitations': ['Synthetic equivalence is bounded evidence, not production execution or a memory bound.',
            'Production main is statically reviewed separately; tests do not authenticate live source inventory or owning sessions.',
            'The production CLI always requires 120 tasks / 172 outputs and fixed run/source/challenge bindings.']})
    save(args.report, report)
    print(json.dumps({'report': str(args.report), 'controls': len(results), 'all_controls_pass': True,
                      'targets_opened': False, 'actual_production_assembly_performed': False}))


if __name__ == '__main__':
    main()
