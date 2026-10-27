"""Stream a completed fresh Block 17 census through an unchanged dispatcher.

This external adapter changes aggregation only. It does not compile candidates,
execute candidate programs, accept target paths, or score predictions. Each run
emits one explicitly selected frozen policy after authenticating the whole census.
"""
from __future__ import annotations

import argparse
import gc
import gzip
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


class JSONStream:
    def __init__(self, path):
        self.stream = gzip.open(path, 'rt', encoding='utf-8', newline='') if str(path).endswith('.gz') else open(path, 'rt', encoding='utf-8', newline='')
        self.buffer = ''
        self.pos = 0
        self.eof = False
        self.decoder = json.JSONDecoder(object_pairs_hook=no_duplicates)
        self.bytes_digest = hashlib.sha256()
        self.bytes_read = 0

    def refill(self):
        self.buffer = self.buffer[self.pos:]
        self.pos = 0
        chunk = self.stream.read(1024 * 1024)
        if not chunk:
            self.eof = True
            return False
        raw = chunk.encode('utf-8')
        self.bytes_digest.update(raw)
        self.bytes_read += len(raw)
        self.buffer += chunk
        return True

    def peek(self):
        while True:
            while self.pos < len(self.buffer) and self.buffer[self.pos].isspace():
                self.pos += 1
            if self.pos < len(self.buffer):
                return self.buffer[self.pos]
            if self.eof:
                return ''
            self.refill()

    def expect(self, char):
        if self.peek() != char:
            raise ValueError(f"expected {char!r}, observed {self.peek()!r}")
        self.pos += 1

    def value(self):
        self.peek()
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer, self.pos)
                # A number at a chunk boundary may continue in the next chunk.
                if end == len(self.buffer) and not self.eof:
                    self.refill()
                    continue
                if end < len(self.buffer) and not (self.buffer[end].isspace() or self.buffer[end] in ',}:]'):
                    if not self.eof:
                        self.refill()
                        continue
                    raise ValueError('invalid JSON value delimiter')
                self.pos = end
                return value
            except json.JSONDecodeError:
                if self.eof:
                    raise
                self.refill()

    def close(self):
        self.stream.close()


def sha256_file(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


POLICIES = ('typed_recent', 'typed_supported')


def file_identity(path):
    path = Path(path)
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size,
            'sha256': sha256_file(path)}


def source_identity(engine, solver):
    return {'code_hash': engine.code_hash(), 'bank_hash': engine.bank_hash(),
            'prediction_hash': solver.prediction_hash()}


def validate_test_membership(engine, task_id, task, record):
    """Authenticate output positions and grids without executing any program."""
    arity = len(task['test'])
    if not isinstance(record.get('base'), list) or len(record['base']) != arity:
        raise ValueError(f'base test membership differs: {task_id}')
    for index, row in enumerate(record['base']):
        if not isinstance(row, dict) or set(row) != {'attempt_1', 'attempt_2'}:
            raise ValueError(f'base attempt schema differs: {task_id}:{index}')
        for attempt in ('attempt_1', 'attempt_2'):
            engine.contract.validate_grid(row[attempt], what=f'{task_id}:{index}:{attempt}')
    if not isinstance(record.get('candidates'), list):
        raise ValueError(f'candidate list missing: {task_id}')
    for candidate in record['candidates']:
        outputs = candidate.get('test_outputs')
        if not isinstance(outputs, list) or len(outputs) != arity:
            raise ValueError(f'candidate test membership differs: {task_id}')
        for index, grid in enumerate(outputs):
            engine.contract.validate_grid(grid, what=f'{task_id}:candidate:{index}')
        if candidate.get('behavior_hash') != engine.contract.digest(outputs):
            raise ValueError(f'candidate behavior binding differs: {task_id}')
        if candidate.get('candidate_hash') != engine.contract.digest(
                {k: v for k, v in candidate.items() if k != 'candidate_hash'}):
            raise ValueError(f'candidate content binding differs: {task_id}')
        if ('task_semantic_hash' in candidate and
                candidate['task_semantic_hash'] != record['task_semantic_hash']):
            raise ValueError(f'candidate task binding differs: {task_id}')
    if not isinstance(record.get('receipts'), dict):
        raise ValueError(f'compiler receipt mapping missing: {task_id}')


def append_dispatch(engine, solver, aggregate, task_id, task, record, policy, bindings):
    """Only corpus aggregation changes; frozen ranking/attempt construction runs."""
    subset = engine.seal({'scope': 'all_banks', 'records': {task_id: record},
        'challenges_hash': engine.contract.digest({task_id: task}),
        'bank_hash': bindings['bank_hash'], 'code_hash': bindings['code_hash']})
    dispatched = solver.dispatch({task_id: task}, subset, policy)
    engine.verify(dispatched)
    if aggregate is None:
        aggregate = {k: v for k, v in dispatched.items() if k != 'content_hash'}
        aggregate['decisions'] = {}
        aggregate['submission'] = {}
    else:
        for key, value in dispatched.items():
            if key not in ('content_hash', 'census_hash', 'decisions', 'submission'):
                if aggregate.get(key) != value:
                    raise ValueError(f'dispatch header changed between tasks: {key}')
    aggregate['decisions'][task_id] = dispatched['decisions'][task_id]
    aggregate['submission'][task_id] = dispatched['submission'][task_id]
    return aggregate


def finish_dispatch(engine, aggregate, census_hash):
    if aggregate is None:
        raise ValueError('empty census cannot produce an ARC submission')
    aggregate['census_hash'] = census_hash
    return engine.seal(aggregate)


def stream_dispatch(engine, solver, challenges, census_path, policy, bindings):
    """Verify the original whole-census seal while retaining one record at a time."""
    if policy not in POLICIES:
        raise ValueError('policy must be explicitly selected from frozen audited policies')
    challenge_hash = engine.contract.digest(challenges)
    expected_run_hash = engine.contract.digest({'code': bindings['code_hash'],
        'bank': bindings['bank_hash'], 'challenges': challenges,
        'include_new': True, 'limits': engine.LIMITS})
    canonical = engine.contract.canonical_json
    census_digest = hashlib.sha256()
    census_digest.update(b'{')
    first_top = True
    previous_top = None
    metadata = {}
    records_seen = set()
    receipts_by_task = {}
    errors = []
    candidate_count = 0
    result = None
    stream = JSONStream(census_path)
    try:
        stream.expect('{')
        while stream.peek() != '}':
            key = stream.value()
            if not isinstance(key, str) or (previous_top is not None and key <= previous_top):
                raise ValueError('top-level census keys must be unique and sorted')
            previous_top = key
            stream.expect(':')
            if key != 'content_hash':
                if not first_top:
                    census_digest.update(b',')
                census_digest.update(canonical(key).encode('utf-8') + b':')
                first_top = False
            if key == 'records':
                if metadata.get('bank_hash') != bindings['bank_hash']:
                    raise ValueError('census bank binding differs')
                if metadata.get('code_hash') != bindings['code_hash']:
                    raise ValueError('census code binding differs')
                if metadata.get('challenges_hash') != challenge_hash:
                    raise ValueError('census challenge binding differs')
                if metadata.get('limits') != engine.LIMITS:
                    raise ValueError('census fixed search limits differ')
                if metadata.get('label_access') != 'demonstrations_only':
                    raise ValueError('wrong census label scope')
                if metadata.get('champion_fallback') is not False:
                    raise ValueError('champion fallback enabled or unspecified')
                stream.expect('{')
                census_digest.update(b'{')
                first_record = True
                previous_record = None
                while stream.peek() != '}':
                    task_id = stream.value()
                    if not isinstance(task_id, str) or (previous_record is not None and task_id <= previous_record):
                        raise ValueError('task record keys must be unique and sorted')
                    previous_record = task_id
                    stream.expect(':')
                    record = stream.value()
                    if task_id not in challenges:
                        raise ValueError('unknown census task')
                    task = challenges[task_id]
                    engine.verify(record)
                    if record.get('task_semantic_hash') != engine.contract.digest(task):
                        raise ValueError('record semantic input binding differs')
                    validate_test_membership(engine, task_id, task, record)
                    if not first_record:
                        census_digest.update(b',')
                    census_digest.update(canonical(task_id).encode('utf-8') + b':' + canonical(record).encode('utf-8'))
                    first_record = False
                    result = append_dispatch(engine, solver, result, task_id, task, record, policy, bindings)
                    candidate_count += len(record['candidates'])
                    receipts_by_task[task_id] = record['receipts']
                    for provider, receipt in record['receipts'].items():
                        if receipt.get('status') != 'ok':
                            errors.append({'task_id': task_id, 'provider': provider, **receipt})
                    records_seen.add(task_id)
                    del record
                    if len(records_seen) % 25 == 0:
                        gc.collect()
                        print(json.dumps({'completed': len(records_seen), 'candidate_count': candidate_count,
                            'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024}), flush=True)
                    delimiter = stream.peek()
                    if delimiter == ',':
                        stream.expect(',')
                    elif delimiter != '}':
                        raise ValueError('invalid records delimiter')
                stream.expect('}')
                census_digest.update(b'}')
            else:
                value = stream.value()
                metadata[key] = value
                if key != 'content_hash':
                    census_digest.update(canonical(value).encode('utf-8'))
            delimiter = stream.peek()
            if delimiter == ',':
                stream.expect(',')
            elif delimiter != '}':
                raise ValueError('invalid top-level delimiter')
        stream.expect('}')
        if stream.peek():
            raise ValueError('trailing census content')
        census_digest.update(b'}')
        if census_digest.hexdigest() != metadata.get('content_hash'):
            raise ValueError('streamed census semantic seal differs')
        if metadata.get('schema') != 'komorebi.block17.live_census.v1':
            raise ValueError('census is not a fresh engine.scan census')
        if metadata.get('scope') != 'all_banks':
            raise ValueError('wrong census bank scope')
        if metadata.get('run_hash') != expected_run_hash:
            raise ValueError('fresh scan run binding differs')
        if metadata.get('limits') != engine.LIMITS:
            raise ValueError('fixed engine search limits differ')
        if records_seen != set(challenges):
            raise ValueError('census task membership differs')
        if (set(result['submission']) != set(challenges) or
                set(result['decisions']) != set(challenges)):
            raise ValueError('prediction task membership differs')
        for task_id, rows in result['submission'].items():
            if len(rows) != len(challenges[task_id]['test']):
                raise ValueError('prediction test membership differs')
        result = finish_dispatch(engine, result, metadata['content_hash'])
        receipt = {'census_hash': metadata['content_hash'], 'fresh_run_hash': expected_run_hash,
            'streamed_utf8_sha256': stream.bytes_digest.hexdigest(),
            'streamed_utf8_bytes': stream.bytes_read,
            'records': len(records_seen), 'test_outputs': sum(len(t['test']) for t in challenges.values()),
            'candidates': candidate_count, 'compiler_receipts_by_task': receipts_by_task,
            'error_receipt_count': len(errors), 'error_receipts': errors}
        return result, receipt
    finally:
        stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--challenges', type=Path, required=True)
    parser.add_argument('--census', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--policy', choices=POLICIES, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output_dir.resolve()
    if out.is_relative_to(root):
        raise ValueError('output must remain outside frozen source')
    if str(args.census).endswith('.gz'):
        raise ValueError('fresh adapter requires the completed plain UTF-8 census')
    sys.path.insert(0, str(root))
    import engine
    import solver
    if Path(engine.__file__).resolve() != root / 'engine.py' or Path(solver.__file__).resolve() != root / 'solver.py':
        raise ValueError('dispatcher modules did not load from requested frozen source')
    start = time.monotonic()
    engine.initialize()
    bindings = source_identity(engine, solver)
    census_before = file_identity(args.census)
    challenges_before = file_identity(args.challenges)
    challenge_raw = json.loads(args.challenges.read_text(encoding='utf-8'), object_pairs_hook=no_duplicates)
    challenges = {key: engine.sanitize(task) for key, task in challenge_raw.items()}
    del challenge_raw
    result, receipt = stream_dispatch(engine, solver, challenges, args.census, args.policy, bindings)
    census_after = file_identity(args.census)
    challenges_after = file_identity(args.challenges)
    if census_before != census_after:
        raise ValueError('raw census SHA-256/size changed during dispatch')
    if challenges_before != challenges_after:
        raise ValueError('raw challenges SHA-256/size changed during dispatch')
    if (receipt['streamed_utf8_sha256'] != census_before['sha256'] or
            receipt['streamed_utf8_bytes'] != census_before['bytes']):
        raise ValueError('streamed plain census bytes differ from authenticated input file')
    engine.initialize()
    if bindings != source_identity(engine, solver):
        raise ValueError('frozen source identity changed during dispatch')
    out.mkdir(parents=True, exist_ok=True)
    output = out / (args.policy + '_dispatch.json')
    engine.write(output, result)
    engine.verify(result)
    audit = {'schema': 'komorebi.block17.fresh-streamed-dispatch-audit.v1',
        'scope': 'Dispatch of a completed fresh compiler census; no compiler calls or program replay in this adapter.',
        'policy': args.policy, 'source_root': str(root), 'source_before_and_after': bindings,
        'source_unchanged_by_hash': True, 'census_before_and_after': census_before,
        'challenges_before_and_after': challenges_before,
        'raw_census_before_after_sha256_and_size_verified': True,
        'streamed_semantic_census_seal_verified': True,
        'all_record_content_and_task_bindings_verified': True,
        'exact_task_and_test_membership_verified': True,
        'all_banks_scope_verified': True, 'fixed_limits': engine.LIMITS,
        'fresh_run_hash_verified': True, 'prediction_label_access': 'demonstrations_only',
        'champion_fallback': False, 'aggregation': 'unchanged frozen dispatcher called once per task',
        'unchanged_frozen_dispatcher_calls': receipt['records'], 'target_paths_accepted': False,
        'prediction': {**file_identity(output), 'content_hash': result['content_hash'],
            'submission_hash': engine.contract.digest(result['submission'])},
        **receipt, 'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'elapsed_seconds': time.monotonic() - start,
        'integrity_pass': True,
        'compilation_error_free': receipt['error_receipt_count'] == 0}
    engine.write(out / (args.policy + '_dispatch_audit.json'), audit)
    print(json.dumps({k: audit[k] for k in ('policy', 'records', 'test_outputs', 'candidates',
        'error_receipt_count', 'maximum_resident_mib', 'elapsed_seconds', 'integrity_pass')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
