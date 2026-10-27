#!/usr/bin/env python3
"""Assemble authenticated, completed Block17 checkpoints without runtime imports.

Preparation artifact. Production use requires the separate sealed owning-session
pre-assembly stop receipt and exactly 120 tasks / 172 outputs. This script does
not scan, compile, dispatch, execute candidates, score, or accept target paths.
It leaves the frozen source and existing final gate/completion schema untouched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
from types import SimpleNamespace

LIMITS = {'max_candidates': 256, 'candidate_cap': 256,
          'max_total_candidates': 2048, 'max_replay_calls': 4096,
          'max_replay_stages': 64, 'max_trace_bytes': 1000000}
PINS = {
    'run_hash': 'd5858775adc7c61a3593c6d058808ecefc97a85a696032213e7810b18cd0751e',
    'code_hash': '0a71a156ba0bedc3d3b80c0a0667670e48052c952807b747a6b2bd45940f0a71',
    'bank_hash': '4c6cdd41dceae29af5b765d628d9efd8ceb98c877721feb5d4547c81c5081cab',
    'challenges_sha256': 'e7c62a4bd211867c6b538f66b8013b81f299663c82ca062f49a52bf439d6e4e8',
    'challenges_hash': 'f20b99ee5c2dfbc267e117f2d21f07f3bd599e590152f59b256d3a934c158de8',
    'original_snapshot_sha256': 'e655bcf293478ed4da1ce51f903095b0121e285893ecb3e95a49e8749bf47ec8',
    'adapter_sha256': '3c7811352a40328cff2e1c56db0cbc4f889759e31dd6b455edc6fb2fbbec8d56',
    'gate_sha256': 'a51d3a05ea10f90a2ce33aab0258bcabb6de95d970e68dd9b2875af73a81a4b4',
    'scheduler_sha256': 'bf612124af1784c64cfb574d3b83319d7d877bc4be35d28d9817ff2094673a39',
}
BODY_KEYS = {'schema', 'author', 'run_hash', 'code_hash', 'bank_hash',
             'challenges_hash', 'scope', 'limits', 'records',
             'label_access', 'champion_fallback'}
PRE_SCHEMA = 'komorebi.block17.scan-process-pre-assembly.v1'
PRE_KEYS = {'schema', 'recorded_at_utc', 'targets_opened',
            'source_budget_policy_changes', 'all_scans_stopped', 'tasks',
            'test_outputs', 'run_hash', 'challenges', 'source_snapshot',
            'source_bindings', 'supplemental_metadata',
            'supplemental_metadata_content_hash', 'checkpoints', 'sessions',
            'content_hash'}
CANONICAL = json.JSONEncoder(sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False, allow_nan=False)
PRETTY = json.JSONEncoder(sort_keys=True, indent=2,
                          ensure_ascii=False, allow_nan=False)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    # Reading one checkpoint is intentional; never load the complete census.
    with Path(path).open('r', encoding='utf-8') as handle:
        return json.load(handle, object_pairs_hook=no_duplicates,
                         parse_constant=lambda value: (_ for _ in ()).throw(
                             ValueError('nonfinite JSON: ' + value)))


def canonical_json(value):
    return CANONICAL.encode(value)


def digest(value):
    result = hashlib.sha256()
    update_json(result, value)
    return result.hexdigest()


def update_json(result, value):
    for chunk in CANONICAL.iterencode(value):
        result.update(chunk.encode('utf-8'))


def seal(value):
    body = {key: item for key, item in value.items() if key != 'content_hash'}
    return {**body, 'content_hash': digest(body)}


def verify(value):
    require(isinstance(value, dict), 'sealed value is not a mapping')
    require(value.get('content_hash') == digest(
        {key: item for key, item in value.items() if key != 'content_hash'}),
        'content hash mismatch')


def sha256_file(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def identity(path):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), 'expected regular file: ' + str(path))
    before = path.stat()
    result = {'path': str(path), 'bytes': before.st_size, 'sha256': sha256_file(path)}
    after = path.stat()
    require((before.st_size, before.st_mtime_ns, before.st_ino) ==
            (after.st_size, after.st_mtime_ns, after.st_ino),
            'file changed while hashing: ' + str(path))
    return result


def validate_grid(value, *, what='grid'):
    require(isinstance(value, list) and 1 <= len(value) <= 30,
            what + ': invalid row count')
    require(all(isinstance(row, list) and row for row in value),
            what + ': invalid rows')
    width = len(value[0])
    require(width <= 30 and all(len(row) == width for row in value),
            what + ': invalid width')
    require(all(type(cell) is int and 0 <= cell <= 9 for row in value for cell in row),
            what + ': invalid colors')
    return [list(row) for row in value]


def sanitize(task):
    require(isinstance(task, dict), 'task is not a mapping')
    for name in ('train', 'test'):
        require(isinstance(task.get(name), list) and 1 <= len(task[name]) <= 10,
                'invalid task arity')
    result = {'train': [], 'test': []}
    for name in result:
        for example in task[name]:
            require(isinstance(example, dict) and 'input' in example,
                    'missing example input')
            if name == 'test':
                require('output' not in example, 'attached test output rejected')
            else:
                require('output' in example, 'missing demonstration output')
            result[name].append({field: validate_grid(example[field])
                                 for field in (('input', 'output') if name == 'train' else ('input',))})
    return result


FACADE = SimpleNamespace(contract=SimpleNamespace(digest=digest,
    canonical_json=canonical_json, validate_grid=validate_grid), verify=verify,
    LIMITS=LIMITS)


def load_helper(path, name, pinned_sha):
    before = identity(path)
    require(before['sha256'] == pinned_sha, 'external helper source differs: ' + name)
    # The reviewed modules import engine only inside main, which is never called.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(identity(path) == before, 'helper changed during import')
    return module, before


def census_header(clean, code_hash, bank_hash, run_hash):
    return {'schema': 'komorebi.block17.live_census.v1', 'author': 'Komorebi P.',
            'run_hash': run_hash, 'code_hash': code_hash, 'bank_hash': bank_hash,
            'challenges_hash': digest(clean), 'scope': 'all_banks',
            'limits': dict(LIMITS), 'label_access': 'demonstrations_only',
            'champion_fallback': False}


def check_header(header, clean):
    require(set(header) == BODY_KEYS - {'records'}, 'census header keys differ')
    require(header['schema'] == 'komorebi.block17.live_census.v1' and
            header['author'] == 'Komorebi P.' and header['scope'] == 'all_banks',
            'census schema/author/scope differs')
    require(header['label_access'] == 'demonstrations_only' and
            header['champion_fallback'] is False and header['limits'] == LIMITS,
            'census label scope/fallback/limits differs')
    require(header['challenges_hash'] == digest(clean), 'census challenge binding differs')
    require(header['run_hash'] == digest({'code': header['code_hash'],
        'bank': header['bank_hash'], 'challenges': clean, 'include_new': True,
        'limits': LIMITS}), 'census run binding differs')


def checkpoint_paths(checkpoints, clean):
    paths = {key: Path(checkpoints) / (digest(key) + '.json') for key in clean}
    expected = {path.name for path in paths.values()}
    # Reject all extra/stale temporary entries, not only unknown .json files.
    require({path.name for path in Path(checkpoints).iterdir()} == expected,
            'checkpoint inventory differs from exact task membership')
    require(all(not path.is_symlink() and path.is_file() for path in paths.values()),
            'checkpoint is not a regular nonsymlink file')
    return paths


def load_record(task_id, task, path, expected_identity, run_hash, adapter):
    require(identity(path) == expected_identity, 'checkpoint changed before load: ' + task_id)
    wrapper = read_json(path)
    require(set(wrapper) == {'run_hash', 'record', 'content_hash'},
            'checkpoint wrapper keys differ: ' + task_id)
    verify(wrapper)
    require(wrapper['run_hash'] == run_hash, 'checkpoint run binding differs: ' + task_id)
    record = wrapper['record']
    verify(record)
    require(record.get('task_semantic_hash') == digest(task),
            'record task binding differs: ' + task_id)
    adapter.validate_test_membership(FACADE, task_id, task, record)
    require(identity(path) == expected_identity, 'checkpoint changed during load: ' + task_id)
    # Only the inner record survives the wrapper; no content is changed/resealed.
    return record


def validate_metadata(metadata, header, scheduler_sha, clean, planned_scope=57):
    verify(metadata)
    require(isinstance(metadata.get('completed_utc'), str) and metadata['completed_utc'],
            'supplemental metadata is not terminal')
    require(metadata.get('run_hash') == header['run_hash'] and
            metadata.get('code_hash') == header['code_hash'] and
            metadata.get('bank_hash') == header['bank_hash'],
            'supplemental source/run bindings differ')
    require(metadata.get('limits') == LIMITS and
            metadata.get('label_access') == 'demonstrations_only' and
            metadata.get('source_changes') is False and metadata.get('policy_changes') is False,
            'supplemental limits/label/source/policy scope differs')
    require(metadata.get('scheduler_sha256') == scheduler_sha, 'supplemental scheduler differs')
    reserved = metadata.get('reserved_active_task_ids')
    require(isinstance(reserved, list) and all(isinstance(key, str) for key in reserved) and
            len(set(reserved)) == len(reserved) and set(reserved) <= set(clean),
            'reserved supplemental task membership differs')
    require(type(metadata.get('initial_missing')) is int and
            len(reserved) <= metadata['initial_missing'] <= len(clean) and
            metadata['initial_missing'] - len(reserved) == planned_scope,
            'supplemental planned scope differs')
    require(isinstance(metadata.get('events'), list), 'supplemental events missing')


def validate_pre_stop_scope(pre, expected_tasks=120, expected_outputs=172):
    """Reject missing/invalid owning stop evidence before any dataset byte read."""
    verify(pre)
    require(set(pre) == PRE_KEYS and pre['schema'] == PRE_SCHEMA,
            'pre-assembly receipt schema differs')
    require(pre['all_scans_stopped'] is True and pre['targets_opened'] is False and
            pre['source_budget_policy_changes'] is False,
            'pre-assembly receipt scope/stop evidence differs')
    require(type(pre['tasks']) is int and type(pre['test_outputs']) is int and
            pre['tasks'] == expected_tasks and pre['test_outputs'] == expected_outputs,
            'pre-assembly task/output membership differs')
    stamp = datetime.fromisoformat(pre['recorded_at_utc'])
    require(stamp.utcoffset() is not None and stamp.utcoffset().total_seconds() == 0,
            'pre-assembly timestamp is not UTC')
    sessions = pre['sessions']
    require(isinstance(sessions, list) and len(sessions) == 2 and
            {row.get('role') for row in sessions} == {'primary_scan', 'supplemental_scan'},
            'pre-assembly owning roles differ')
    seen = set()
    for row in sessions:
        require(row.get('stopped') is True and type(row.get('session_id')) is int and
                row['session_id'] > 0 and row['session_id'] not in seen,
                'owning session stop evidence differs')
        seen.add(row['session_id'])
        require(row.get('exit_code') is None or type(row['exit_code']) is int,
                'owning exit code is not a captured integer/explicit unknown')
        require(isinstance(row.get('completion_evidence'), str) and
                row['completion_evidence'].strip(), 'owning completion evidence missing')
        allowed = ({'natural_exit', 'redundant_work_interrupt'} if
                   row['role'] == 'primary_scan' else {'natural_exit'})
        require(row.get('mode') in allowed, 'owning stop mode differs')
    # Exit codes remain honest evidence. A failed earlier aggregate write is not
    # represented as benchmark success merely because checkpoints are complete.


def validate_pre_receipt(pre, clean, header, inputs, checkpoint_ids, metadata,
                         expected_tasks=120, expected_outputs=172):
    validate_pre_stop_scope(pre, expected_tasks, expected_outputs)
    require(pre['tasks'] == len(clean) and pre['test_outputs'] ==
            sum(len(task['test']) for task in clean.values()),
            'pre-assembly task/output membership differs')
    require(pre['run_hash'] == header['run_hash'] and
            pre['source_bindings'] == {key: header[key] for key in ('code_hash', 'bank_hash')},
            'pre-assembly source/run bindings differ')
    require(all(pre[key] == inputs[key] for key in
                ('challenges', 'source_snapshot', 'supplemental_metadata')) and
            pre['supplemental_metadata_content_hash'] == metadata['content_hash'],
            'pre-assembly raw input identities differ')
    require(pre['checkpoints'] == checkpoint_ids and set(checkpoint_ids) == set(clean),
            'pre-assembly checkpoint identities differ')
    completed = datetime.fromisoformat(metadata['completed_utc'])
    require(completed.utcoffset() is not None and
            completed.utcoffset().total_seconds() == 0 and
            datetime.fromisoformat(pre['recorded_at_utc']) >= completed,
            'pre-assembly receipt predates terminal supplemental completion')


def source_inventory(root):
    result = {}
    for path in sorted(Path(root).rglob('*')):
        require(not path.is_symlink(), 'source inventory contains a symlink')
        if path.is_file():
            raw = identity(path)
            result[path.relative_to(root).as_posix()] = {
                'size': raw['bytes'], 'sha256': raw['sha256'], 'mtime_ns': path.stat().st_mtime_ns}
    return result


def content_inventory(snapshot):
    require(isinstance(snapshot, dict) and snapshot, 'source baseline inventory missing')
    result = {}
    for name, entry in snapshot.items():
        require(isinstance(name, str) and not Path(name).is_absolute() and
                '..' not in Path(name).parts and isinstance(entry, dict) and
                set(entry) == {'size', 'sha256', 'mtime_ns'}, 'source baseline schema differs')
        require(type(entry['size']) is int and entry['size'] >= 0 and
                type(entry['mtime_ns']) is int and isinstance(entry['sha256'], str),
                'source baseline entry differs')
        result[name] = {'size': entry['size'], 'sha256': entry['sha256']}
    return result


def source_bindings(root):
    code = digest({name: sha256_file(root / name) for name in
                   ('engine.py', 'legacy.py', 'action_adapter.py', 'contract.py', 'memo.py')})
    bank = digest({name: read_json(root / name) for name in
                   ('vendor_manifest.json', 'bank13.json', 'bank14_15.json')})
    return {'code_hash': code, 'bank_hash': bank}


def write_nested(handle, value, indent):
    # iterencode uses the identical stdlib pretty encoder as frozen write_json.
    # JSON string newlines are escaped; only formatting LFs acquire indentation.
    prefix = ' ' * indent
    for chunk in PRETTY.iterencode(value):
        handle.write(chunk.replace('\n', '\n' + prefix))


def stream_output_verify(path, clean, header, record_hashes, content_hash, adapter):
    whole = hashlib.sha256()
    whole.update(b'{')
    first = True
    previous = None
    observed_header = {}
    seen = set()
    stream = adapter.JSONStream(path)
    try:
        stream.expect('{')
        while stream.peek() != '}':
            key = stream.value()
            require(isinstance(key, str) and (previous is None or key > previous),
                    'output keys are not unique and sorted')
            previous = key
            stream.expect(':')
            if key != 'content_hash':
                if not first:
                    whole.update(b',')
                update_json(whole, key)
                whole.update(b':')
                first = False
            if key == 'records':
                whole.update(b'{')
                stream.expect('{')
                last_task = None
                first_task = True
                while stream.peek() != '}':
                    task_id = stream.value()
                    require(isinstance(task_id, str) and task_id in clean and
                            (last_task is None or task_id > last_task),
                            'output task membership/order differs')
                    last_task = task_id
                    stream.expect(':')
                    record = stream.value()
                    verify(record)
                    require(record['content_hash'] == record_hashes[task_id] and
                            record.get('task_semantic_hash') == digest(clean[task_id]),
                            'output record differs from authenticated checkpoint')
                    adapter.validate_test_membership(FACADE, task_id, clean[task_id], record)
                    if not first_task:
                        whole.update(b',')
                    update_json(whole, task_id)
                    whole.update(b':')
                    update_json(whole, record)
                    first_task = False
                    seen.add(task_id)
                    del record
                    delimiter = stream.peek()
                    if delimiter == ',':
                        stream.expect(',')
                    else:
                        require(delimiter == '}', 'output record delimiter differs')
                stream.expect('}')
                whole.update(b'}')
            else:
                value = stream.value()
                observed_header[key] = value
                if key != 'content_hash':
                    update_json(whole, value)
            delimiter = stream.peek()
            if delimiter == ',':
                stream.expect(',')
            else:
                require(delimiter == '}', 'output header delimiter differs')
        stream.expect('}')
        require(not stream.peek(), 'trailing output content')
        whole.update(b'}')
        require(seen == set(clean) and observed_header == {**header, 'content_hash': content_hash},
                'output full membership/header differs')
        require(whole.hexdigest() == content_hash, 'output streamed semantic seal differs')
    finally:
        stream.close()


def assemble_records(clean, paths, checkpoint_ids, header, output, adapter, gate,
                     metadata, stability_check):
    """Core writer; only the guarded production main uses actual inputs.

    Tiny synthetic tests may use this pure I/O core with synthetic bindings.
    All validation and supplemental agreement precede the first output byte.
    """
    output = Path(output)
    partial = output.with_name(output.name + '.partial')
    require(not output.exists() and not partial.exists(), 'output or partial already exists')
    check_header(header, clean)
    require(set(paths) == set(clean) == set(checkpoint_ids), 'checkpoint task membership differs')
    whole = hashlib.sha256()
    whole.update(b'{')
    record_hashes = {}
    candidate_count = candidate_tasks = error_receipts = 0
    for top_index, key in enumerate(sorted(BODY_KEYS)):
        if top_index:
            whole.update(b',')
        update_json(whole, key)
        whole.update(b':')
        if key != 'records':
            update_json(whole, header[key])
            continue
        whole.update(b'{')
        for index, task_id in enumerate(sorted(clean)):
            record = load_record(task_id, clean[task_id], paths[task_id],
                                 checkpoint_ids[task_id], header['run_hash'], adapter)
            if index:
                whole.update(b',')
            update_json(whole, task_id)
            whole.update(b':')
            update_json(whole, record)
            record_hashes[task_id] = record['content_hash']
            candidate_count += len(record['candidates'])
            candidate_tasks += bool(record['candidates'])
            error_receipts += sum(receipt.get('status') != 'ok'
                                  for receipt in record['receipts'].values())
            del record
        whole.update(b'}')
    whole.update(b'}')
    content_hash = whole.hexdigest()
    agreements, skipped = gate.completion_agreement(metadata, record_hashes, record_hashes)
    stability_check()
    # The sole full-size temporary file is opened exclusively. No canonical
    # census, record array reorder, or secondary full-size copy is produced.
    created_partial = False
    try:
        with partial.open('x', encoding='utf-8', newline='\n') as handle:
            created_partial = True
            handle.write('{\n')
            keys = sorted(BODY_KEYS | {'content_hash'})
            for top_index, key in enumerate(keys):
                handle.write('  ' + canonical_json(key) + ': ')
                if key == 'records':
                    handle.write('{\n')
                    for index, task_id in enumerate(sorted(clean)):
                        record = load_record(task_id, clean[task_id], paths[task_id],
                                             checkpoint_ids[task_id], header['run_hash'], adapter)
                        require(record['content_hash'] == record_hashes[task_id],
                                'record changed between passes')
                        handle.write('    ' + canonical_json(task_id) + ': ')
                        write_nested(handle, record, 4)
                        handle.write(',\n' if index + 1 < len(clean) else '\n')
                        del record
                    handle.write('  }')
                else:
                    write_nested(handle, content_hash if key == 'content_hash' else header[key], 2)
                handle.write(',\n' if top_index + 1 < len(keys) else '\n')
            handle.write('}\n')
            handle.flush()
            os.fsync(handle.fileno())
        stream_output_verify(partial, clean, header, record_hashes, content_hash, adapter)
        stability_check()
        require(not output.exists(), 'output appeared during assembly')
        # No-overwrite hard link publishes these same bytes atomically, then the
        # temporary name is removed. Both names briefly share one inode/data set.
        os.link(partial, output)
        partial.unlink()
        return {'content_hash': content_hash, 'record_hashes': record_hashes,
                'completion_event_agreements': agreements, 'skip_existing_tasks': skipped,
                'candidate_count': candidate_count, 'candidate_tasks': candidate_tasks,
                'error_receipts': error_receipts, 'census': identity(output)}
    except BaseException:
        if created_partial:
            partial.unlink(missing_ok=True)
        raise


def write_audit(path, value):
    path = Path(path)
    require(not path.exists(), 'assembly audit already exists')
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(PRETTY.encode(value) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--source-snapshot', type=Path,
                        help='Defaults to original current-run baseline; restored inventory must match it')
    parser.add_argument('--pre-assembly-receipt', type=Path,
                        help='Defaults to scan_process_pre_assembly.json; must contain actual owning stop evidence')
    args = parser.parse_args()
    workspace = args.workspace.resolve(strict=True)
    evidence = workspace / 'arc-evidence'
    output_dir = evidence / 'fullbank-public-evaluation'
    root = workspace / 'arc-fullbank/block17'
    census = output_dir / 'census.json'
    audit_path = output_dir / 'census_streaming_assembly_audit.json'
    require(not census.exists() and not census.with_name(census.name + '.partial').exists()
            and not audit_path.exists(), 'assembly output/partial/audit already exists')
    snapshot = (args.source_snapshot or evidence / 'later-source-audit/block17_source_before.json').resolve(strict=True)
    original = evidence / 'later-source-audit/block17_source_before.json'
    pre_path = (args.pre_assembly_receipt or output_dir / 'scan_process_pre_assembly.json').resolve(strict=True)
    pre_identity = identity(pre_path)
    pre = read_json(pre_path)
    validate_pre_stop_scope(pre)
    require(pre['run_hash'] == PINS['run_hash'] and
            pre['source_bindings'] == {key: PINS[key] for key in ('code_hash', 'bank_hash')},
            'pre-assembly pinned source/run bindings differ')
    require(identity(pre_path) == pre_identity, 'pre-assembly receipt changed during initial check')
    challenges = workspace / 'arc-offline-data/arc-agi_evaluation_challenges.json'
    metadata_path = output_dir / 'supplemental_scan_metadata.json'
    scheduler = evidence / 'scripts/supplement_block17_scan.py'
    adapter_path = evidence / 'later-source-audit/stream_fresh_block17_dispatch.py'
    gate_path = evidence / 'scripts/authenticate_block17_supplement.py'
    adapter, adapter_id = load_helper(adapter_path, 'assembly_adapter', PINS['adapter_sha256'])
    gate, gate_id = load_helper(gate_path, 'assembly_agreement', PINS['gate_sha256'])
    inputs = {name: identity(path) for name, path in {
        'challenges': challenges, 'source_snapshot': snapshot, 'original_source_snapshot': original,
        'supplemental_metadata': metadata_path, 'pre_assembly_receipt': pre_path,
        'scheduler': scheduler, 'assembler': Path(__file__)}.items()}
    inputs.update(adapter=adapter_id, agreement_helper=gate_id)
    require(inputs['pre_assembly_receipt'] == pre_identity,
            'pre-assembly receipt changed after initial check')
    require(inputs['original_source_snapshot']['sha256'] == PINS['original_snapshot_sha256'],
            'historical pinned source snapshot differs')
    require(inputs['challenges']['sha256'] == PINS['challenges_sha256'] and
            inputs['scheduler']['sha256'] == PINS['scheduler_sha256'],
            'pinned challenge/scheduler bytes differ')
    baseline = read_json(snapshot)
    historical = read_json(original)
    require(content_inventory(baseline) == content_inventory(historical),
            'selected source snapshot inventory/content differs from original')
    clean_raw = read_json(challenges)
    require(isinstance(clean_raw, dict) and all(isinstance(key, str) for key in clean_raw),
            'challenge task mapping differs')
    clean = {key: sanitize(task) for key, task in clean_raw.items()}
    del clean_raw
    require(len(clean) == 120 and sum(len(task['test']) for task in clean.values()) == 172,
            'requires exact 120 tasks and 172 output positions')
    bindings = source_bindings(root)
    require(bindings == {key: PINS[key] for key in ('code_hash', 'bank_hash')},
            'frozen code/bank bindings differ')
    header = census_header(clean, bindings['code_hash'], bindings['bank_hash'], PINS['run_hash'])
    check_header(header, clean)
    require(header['challenges_hash'] == PINS['challenges_hash'], 'clean challenge hash differs')
    paths = checkpoint_paths(census.with_suffix('.tasks'), clean)
    checkpoint_ids = {key: identity(path) for key, path in paths.items()}
    metadata = read_json(metadata_path)
    validate_metadata(metadata, header, inputs['scheduler']['sha256'], clean, planned_scope=57)
    validate_pre_receipt(pre, clean, header, inputs, checkpoint_ids, metadata)
    # Guard only after explicit owning-session evidence. Available /proc visibility
    # is a supplementary check, never the evidence that an owning session stopped.
    gate.scanners_exited(census)
    require(source_inventory(root) == baseline, 'actual source differs from selected baseline')

    def stability_check():
        for name, before in inputs.items():
            require(identity(before['path']) == before, 'assembly input changed: ' + name)
        require(checkpoint_paths(census.with_suffix('.tasks'), clean) == paths,
                'checkpoint inventory changed')
        require(all(identity(paths[key]) == before for key, before in checkpoint_ids.items()),
                'checkpoint raw identity changed')
        require(source_inventory(root) == baseline and source_bindings(root) == bindings,
                'source snapshot or bindings changed')
        gate.scanners_exited(census)

    result = assemble_records(clean, paths, checkpoint_ids, header, census, adapter, gate,
                              metadata, stability_check)
    audit = seal({'schema': 'komorebi.block17.census-streaming-assembly.v1',
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'tasks': 120,
        'test_outputs': 172, 'targets_opened': False,
        'compiler_dispatcher_ranking_program_calls': 0, 'source_budget_policy_changes': False,
        'inputs': inputs, 'final_checkpoint_identities': checkpoint_ids,
        'run_hash': header['run_hash'], 'census': result['census'],
        'census_content_hash': result['content_hash'], 'final_record_hashes': result['record_hashes'],
        'pre_assembly_receipt_content_hash': pre['content_hash'], 'owning_session_evidence': pre['sessions'],
        'supplemental_metadata_content_hash': metadata['content_hash'],
        'completion_event_agreements': result['completion_event_agreements'],
        'skip_existing_tasks': result['skip_existing_tasks'],
        'statistics_outside_census': {key: result[key] for key in
                                     ('candidate_count', 'candidate_tasks', 'error_receipts')},
        'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'all_input_identities_rechecked_before_publish': True,
        'all_checkpoint_wrapper_record_task_candidate_bindings_verified': True,
        'every_supplemental_completion_including_duplicates_matches': True,
        'whole_census_semantic_seal_streamed_and_verified': True,
        'format': 'Frozen stdlib sorted JSON, indent=2, ensure_ascii=False, allow_nan=False, UTF8, one terminal LF',
        'publication': 'one exclusive .partial, atomic no-overwrite hard link, remove partial; no second full-size data copy',
        'limitations': ['The largest individual checkpoint/record still fits in memory; no aggregate is materialized.',
            'Stop evidence is supplied by actual owning execution-session receipts plus available process observations.',
            'This assembly authenticates the actual final records; it makes no global scheduler equivalence claim.',
            'Root must capture the actual assembly session/exit and emit the unchanged final scan_process_completion receipt before the existing final gate.',
            'This assembly-only receipt does not claim benchmark/scanner success from session exit codes.'],
        'integrity_pass': True})
    write_audit(audit_path, audit)
    print(json.dumps({'census': str(census), 'audit': str(audit_path), 'tasks': 120,
                      'test_outputs': 172, 'targets_opened': False, 'integrity_pass': True}), flush=True)


if __name__ == '__main__':
    main()
