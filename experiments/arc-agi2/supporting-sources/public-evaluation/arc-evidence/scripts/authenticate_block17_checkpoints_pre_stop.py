#!/usr/bin/env python3
"""Provisional labels-free checkpoint authentication before owning scan stops.

No scanner control, runtime import, compiler/program/dispatcher, census assembly,
freeze or scoring. A passing receipt is a stable observation, not a stop receipt
or final gate. Existing final gates are unchanged and remain required afterward.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys

ASSEMBLER_SHA = '9b726bab8273860b0dcfb804378efc353b6b711086cbe03bfd0abecffe342d92'


def load_primitives(workspace):
    path = Path(workspace) / 'arc-evidence/scripts/assemble_block17_census_streaming.py'
    require(hashlib.sha256(path.read_bytes()).hexdigest() == ASSEMBLER_SHA,
            'reviewed exterior primitive module differs')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('pre_stop_primitives', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.identity(path)['sha256'] == ASSEMBLER_SHA, 'primitive source changed during import')
    return module


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def replay_bundle(asm, bundle, program_hash, example_index, input_grid, output_grid):
    require(isinstance(bundle, dict) and set(bundle) == {
        'trace_mode', 'program_hash', 'input_hash', 'output_hash', 'stage_count',
        'stages', 'example_index', 'receipt_hash'}, 'replay bundle fields differ')
    require(bundle['receipt_hash'] == asm.digest({k:v for k,v in bundle.items() if k != 'receipt_hash'}),
            'replay bundle receipt hash differs')
    require(bundle['program_hash'] == program_hash and type(bundle['example_index']) is int and
            bundle['example_index'] == example_index, 'replay program/example binding differs')
    require(bundle['input_hash'] == asm.digest(input_grid) and bundle['output_hash'] == asm.digest(output_grid),
            'replay input/output binding differs')
    stages = bundle['stages']
    require(bundle['trace_mode'] in {'single_stage', 'detailed'} and isinstance(stages, list) and
            1 <= len(stages) <= asm.LIMITS['max_replay_stages'] and
            type(bundle['stage_count']) is int and bundle['stage_count'] == len(stages),
            'replay trace mode/stage count differs')
    require(bundle['trace_mode'] != 'single_stage' or len(stages) == 1,
            'single-stage replay has multiple stages')
    previous = bundle['input_hash']
    for index, stage in enumerate(stages):
        require(isinstance(stage, dict) and set(stage) == {
            'index', 'name', 'program_hash', 'source_hash', 'successor_hash', 'receipt_hash'},
            'replay stage fields differ')
        require(type(stage['index']) is int and stage['index'] == index and
                stage['program_hash'] == program_hash and stage['source_hash'] == previous,
                'replay stage chain differs')
        require(stage['receipt_hash'] == asm.digest({k:v for k,v in stage.items() if k != 'receipt_hash'}),
                'replay stage receipt hash differs')
        previous = stage['successor_hash']
    require(previous == bundle['output_hash'], 'replay chain output differs')
    return len(stages)


def deeper_record_checks(asm, task_id, task, record, entrant_blocks, legacy_names, receipt_names):
    # Base attempt lists and compiler status dictionaries have no independent
    # seal in the frozen engine; load_record authenticates their enclosing seal.
    require(set(record['receipts']) == set(receipt_names), 'compiler receipt inventory differs: ' + task_id)
    require(all(isinstance(r, dict) and isinstance(r.get('status'), str)
                for r in record['receipts'].values()), 'compiler status dictionary differs: ' + task_id)
    counts = {'legacy_candidates': 0, 'modern_verified_candidates': 0,
              'modern_not_supplied_candidates': 0, 'replay_bundles': 0, 'replay_stages': 0,
              'compiler_status_dictionaries_bound_by_record_seal': len(record['receipts']),
              'base_attempt_pairs_bound_by_record_seal': len(record['base']),
              'compiler_non_ok_statuses': sum(r['status'] != 'ok' for r in record['receipts'].values())}
    for candidate in record['candidates']:
        name = candidate.get('entrant')
        require(name in entrant_blocks and type(candidate.get('source_block')) is int and
                candidate['source_block'] == entrant_blocks[name], 'candidate entrant/block binding differs')
        if name in legacy_names:
            require('execution_replay' not in candidate and 'origin_candidate_hash' not in candidate,
                    'legacy candidate has unexpected modern replay/annotation')
            require(candidate.get('task_semantic_hash') == asm.digest(task), 'legacy candidate task binding differs')
            counts['legacy_candidates'] += 1
            continue
        require(candidate.get('origin_candidate_hash') == asm.digest({k:v for k,v in candidate.items()
                if k not in {'candidate_hash', 'origin_candidate_hash', 'source_block'}}),
                'modern origin candidate hash differs')
        replay = candidate.get('execution_replay')
        require(isinstance(candidate.get('program'), dict) and isinstance(replay, dict),
                'modern candidate replay/program mapping differs')
        program_hash = asm.digest(candidate['program'])
        require(replay.get('program_hash') == program_hash, 'modern replay program hash differs')
        train_outputs = candidate.get('train_outputs')
        require(isinstance(train_outputs, list) and len(train_outputs) == len(task['train']),
                'modern demonstration output arity differs')
        for example, grid in zip(task['train'], train_outputs):
            asm.validate_grid(grid)
            require(grid == example['output'], 'modern demonstration output differs')
        if replay.get('status') == 'not_supplied':
            require(set(replay) == {'status', 'hook', 'program_hash', 'train', 'test'} and
                    replay['hook'] is None and replay['train'] == [] and replay['test'] == [],
                    'not-supplied replay shape differs')
            counts['modern_not_supplied_candidates'] += 1
        elif replay.get('status') == 'verified':
            asm.verify(replay)
            require(set(replay) == {'status', 'hook', 'program_hash', 'train', 'test', 'content_hash'} and
                    replay['hook'] == 'replay_program(program, grid)', 'verified replay fields differ')
            counts['modern_verified_candidates'] += 1
            for split in ('train', 'test'):
                outputs = candidate.get(split + '_outputs')
                bundles = replay.get(split)
                require(isinstance(outputs, list) and len(outputs) == len(task[split]) and
                        isinstance(bundles, list) and len(bundles) == len(outputs), 'modern replay arity differs')
                for index, (example, output, bundle) in enumerate(zip(task[split], outputs, bundles)):
                    asm.validate_grid(output)
                    if split == 'train':
                        require(output == example['output'], 'modern demonstration output differs')
                    counts['replay_stages'] += replay_bundle(asm, bundle, program_hash,
                                                            index, example['input'], output)
                    counts['replay_bundles'] += 1
        else:
            raise ValueError('modern replay status differs')
    return counts


def available_completion_agreement(asm, metadata, record_hashes, header, scheduler_sha, planned_scope=57):
    asm.verify(metadata)
    require(all(metadata.get(key) == header[key] for key in ('run_hash', 'code_hash', 'bank_hash')) and
            metadata.get('limits') == asm.LIMITS and metadata.get('label_access') == 'demonstrations_only' and
            metadata.get('source_changes') is False and metadata.get('policy_changes') is False and
            metadata.get('scheduler_sha256') == scheduler_sha, 'supplemental provisional bindings differ')
    reserved = metadata.get('reserved_active_task_ids')
    require(isinstance(reserved, list) and all(isinstance(k, str) for k in reserved) and
            len(reserved) == len(set(reserved)) and set(reserved) <= set(record_hashes),
            'supplemental reserved membership differs')
    require(type(metadata.get('initial_missing')) is int and
            len(reserved) <= metadata['initial_missing'] <= len(record_hashes) and
            metadata['initial_missing'] - len(reserved) == planned_scope,
            'supplemental planned scope differs')
    require(isinstance(metadata.get('events'), list), 'supplemental events missing')
    started, active, skipped = set(), set(), set()
    checked = []
    for index, event in enumerate(metadata['events']):
        require(isinstance(event, dict), 'supplemental event mapping differs')
        task_id = event.get('task_id')
        require(task_id in record_hashes and task_id not in reserved, 'supplemental event membership differs')
        kind = event.get('event')
        if kind == 'started':
            require(task_id not in started and task_id not in skipped, 'supplemental start order differs')
            started.add(task_id); active.add(task_id)
        elif kind in {'checkpoint_written', 'duplicate_identical_not_overwritten'}:
            require(task_id in active, 'supplemental completion has no active start')
            require(event.get('record_hash') == record_hashes[task_id],
                    'available supplemental completion hash differs: ' + task_id)
            checked.append({'event_index': index, 'task_id': task_id, 'event': kind,
                            'record_hash': event['record_hash']})
            active.remove(task_id)
        elif kind == 'skip_existing':
            require(task_id not in started and task_id not in skipped and 'record_hash' not in event,
                    'supplemental skip order differs')
            skipped.add(task_id)
        else:
            raise ValueError('unknown supplemental event')
    accounted = len(started | skipped)
    require(accounted <= planned_scope, 'supplemental event scope exceeds plan')
    terminal_observed = bool(metadata.get('completed_utc'))
    if terminal_observed:
        require(not active and accounted == planned_scope, 'terminal supplemental event scope incomplete')
    return {'completion_event_agreements': checked, 'skip_existing_tasks': sorted(skipped),
            'active_tasks_at_snapshot': sorted(active), 'not_started_tasks_at_snapshot': planned_scope - accounted,
            'terminal_metadata_observed': terminal_observed,
            'duplicate_completion_events_checked': sum(e['event'] != 'checkpoint_written' for e in checked)}


def authenticate_records(asm, adapter, clean, paths, ids, header, metadata, scheduler_sha,
                         entrant_blocks, legacy_names, receipt_names, stability_check, planned_scope=57):
    asm.check_header(header, clean)
    require(set(clean) == set(paths) == set(ids), 'checkpoint task membership differs')
    hashes, counts = {}, {}
    for key in sorted(clean):
        record = asm.load_record(key, clean[key], paths[key], ids[key], header['run_hash'], adapter)
        local = deeper_record_checks(asm, key, clean[key], record, entrant_blocks, legacy_names, receipt_names)
        hashes[key] = record['content_hash']
        for name, value in local.items(): counts[name] = counts.get(name, 0) + value
        del record
    events = available_completion_agreement(asm, metadata, hashes, header, scheduler_sha, planned_scope)
    stability_check()
    return {'record_hashes': hashes, 'diagnostic_counts': counts, **events}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', required=True, type=Path)
    p.add_argument('--source-snapshot', type=Path)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    workspace = args.workspace.resolve(strict=True)
    evidence = workspace / 'arc-evidence'; output = evidence / 'fullbank-public-evaluation'
    report_path = (args.report or output / 'checkpoint_pre_stop_authentication.json').resolve()
    require(report_path.parent == output.resolve() and report_path.suffix == '.json',
            'report must be a new direct JSON file in fullbank-public-evaluation')
    require(not report_path.exists() and not report_path.with_name(report_path.name + '.partial').exists(),
            'report/partial already exists; select a fresh report path')
    root = workspace / 'arc-fullbank/block17'
    snapshot = (args.source_snapshot or evidence / 'later-source-audit/block17_source_before.json').resolve(strict=True)
    original = evidence / 'later-source-audit/block17_source_before.json'
    challenges = workspace / 'arc-offline-data/arc-agi_evaluation_challenges.json'
    metadata_path = output / 'supplemental_scan_metadata.json'
    asm = load_primitives(workspace)
    adapter, adapter_id = asm.load_helper(evidence / 'later-source-audit/stream_fresh_block17_dispatch.py',
                                         'pre_stop_adapter', asm.PINS['adapter_sha256'])
    input_paths = {'challenges': challenges, 'source_snapshot': snapshot, 'original_source_snapshot': original,
                   'supplemental_metadata': metadata_path, 'checker': Path(__file__),
                   'primitive_source': evidence / 'scripts/assemble_block17_census_streaming.py',
                   'scheduler': evidence / 'scripts/supplement_block17_scan.py'}
    inputs = {name: asm.identity(path) for name,path in input_paths.items()}; inputs['adapter'] = adapter_id
    require(inputs['challenges']['sha256'] == asm.PINS['challenges_sha256'] and
            inputs['original_source_snapshot']['sha256'] == asm.PINS['original_snapshot_sha256'] and
            inputs['scheduler']['sha256'] == asm.PINS['scheduler_sha256'], 'pinned inputs differ')
    raw = asm.read_json(challenges)
    require(isinstance(raw, dict), 'challenge mapping differs')
    clean = {key: asm.sanitize(task) for key,task in raw.items()}; del raw
    require(len(clean) == 120 and sum(len(t['test']) for t in clean.values()) == 172,
            'requires all120 tasks and172 output positions')
    paths = asm.checkpoint_paths((output / 'census.json').with_suffix('.tasks'), clean)
    ids = {key: asm.identity(path) for key,path in paths.items()}
    baseline = asm.read_json(snapshot)
    require(asm.content_inventory(baseline) == asm.content_inventory(asm.read_json(original)),
            'selected source content/inventory differs from historical pinned baseline')
    require(asm.source_inventory(root) == baseline, 'actual source inventory/bytes/mtime differs')
    bindings = asm.source_bindings(root)
    require(bindings == {key: asm.PINS[key] for key in ('code_hash','bank_hash')}, 'pinned source bindings differ')
    header = asm.census_header(clean, **bindings, run_hash=asm.PINS['run_hash'])
    require(header['challenges_hash'] == asm.PINS['challenges_hash'], 'clean challenge hash differs')
    legacy = {f'legacy_block{n}':n for n in range(6,13)}
    bank13 = asm.read_json(root/'bank13.json'); bank_new = asm.read_json(root/'bank14_15.json')
    entrants = {**legacy, **{name:13 for name in bank13}, **{name:item['source_block'] for name,item in bank_new.items()}}
    receipts = set(entrants) | {'core_blocks2_4'}
    require(len(legacy) == 7 and len(bank13) == 21 and len(bank_new) == 48 and len(receipts) == 77,
            'frozen entrant/receipt registry membership differs')
    metadata = asm.read_json(metadata_path)

    def stable():
        require(all(asm.identity(value['path']) == value for value in inputs.values()), 'provisional input raw identity changed')
        require(asm.checkpoint_paths(output/'census.tasks',clean) == paths and
                all(asm.identity(paths[key]) == value for key,value in ids.items()), 'checkpoint raw inventory/identity changed')
        require(asm.source_inventory(root) == baseline and asm.source_bindings(root) == bindings,
                'provisional source identity/bindings changed')

    result = authenticate_records(asm, adapter, clean, paths, ids, header, metadata,
        inputs['scheduler']['sha256'], entrants, set(legacy), receipts, stable)
    report = asm.seal({'schema':'komorebi.block17.checkpoint-pre-stop-authentication.v1',
        'recorded_at_utc':datetime.now(timezone.utc).isoformat(), 'provisional_pre_stop_check':True,
        'tasks':120, 'test_outputs':172, 'run_hash':header['run_hash'], 'source_bindings':bindings,
        'inputs_before_and_after':inputs, 'final_checkpoint_identities':ids, **result,
        'supplemental_metadata_content_hash':metadata['content_hash'], 'all_inputs_stable_during_authentication':True,
        'targets_opened':False, 'frozen_runtime_imported':False, 'compiler_dispatcher_ranking_program_calls':0,
        'scanner_control_calls':0, 'census_assembly_invoked':False, 'scans_stopped_claimed':False,
        'terminal_final_agreement_claimed':False, 'benchmark_success_claimed':False,
        'maximum_resident_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        'nested_replay_scope':'Pure recorded hash/seal/program/input/output/stage-chain consistency; no replay execution.',
        'unsealed_scope':'Base attempt lists and compiler status dictionaries are unsealed in frozen runtime and authenticated by enclosing record/wrapper seals; not_supplied replay has no independent seal.',
        'limitations':['This stable checkpoint observation does not authorize or prove owning-session stops.',
            'Live duplicate writers/metadata can change after observation; root must capture actual stops then run unchanged final gates.',
            'All available supplemental completion/duplicate events were checked; active/not-started tasks are reported without inventing terminal completion.',
            'Nested modern replay checks are diagnostics, not actual program execution or a change to existing gates.',
            'Existing source formats that fail a diagnostic require scoped review; rejection does not alone establish compiler failure.'],
        'integrity_pass':True})
    # Only this new small report is written; all source/checkpoint inputs stay read-only.
    require(report_path.parent.is_dir(), 'report parent directory missing')
    asm.write_audit(report_path,report)
    print(json.dumps({'report':str(report_path),'tasks':120,'test_outputs':172,'integrity_pass':True,
        'provisional_pre_stop_check':True,'scans_stopped_claimed':False,'targets_opened':False}),flush=True)


if __name__ == '__main__': main()
