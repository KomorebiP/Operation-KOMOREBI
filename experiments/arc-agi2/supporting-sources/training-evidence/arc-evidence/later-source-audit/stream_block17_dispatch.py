"""Bounded-memory replay of an authenticated Block 17 candidate census.

The frozen dispatcher is called on one authenticated task record at a time.
No candidate selection or compiler source is modified. Source and census
bindings, a streaming semantic census digest, and archived output byte identity
are checked before the separate scorer opens targets.
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


def score(submission, targets):
    if set(submission) != set(targets):
        raise ValueError('score task memberships differ')
    first = second = whole = total = 0
    for key, expected_outputs in targets.items():
        rows = submission[key]
        if len(rows) != len(expected_outputs):
            raise ValueError('score output arity differs')
        task_exact = True
        for row, expected in zip(rows, expected_outputs):
            if set(row) != {'attempt_1', 'attempt_2'}:
                raise ValueError('score attempt schema differs')
            exact1 = row['attempt_1'] == expected
            exact2 = exact1 or row['attempt_2'] == expected
            first += exact1
            second += exact2
            total += 1
            task_exact = task_exact and exact2
        whole += task_exact
    return {'pass1_exact_outputs': first, 'pass2_exact_outputs': second,
            'whole_tasks': whole, 'total_outputs': total, 'total_tasks': len(targets),
            'output_percent': 100 * second / total,
            'whole_task_percent': 100 * whole / len(targets)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--challenges', type=Path, required=True)
    parser.add_argument('--census', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--compare-dir', type=Path)
    parser.add_argument('--solutions', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output_dir.resolve()
    if out.is_relative_to(root):
        raise ValueError('output must remain outside frozen source')
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root))
    import engine
    import solver
    start = time.monotonic()
    engine.initialize()
    manifest = json.loads((root / 'release_manifest.json').read_text())
    census_relative = args.census.resolve().relative_to(root).as_posix()
    expected_file = manifest['files'][census_relative]
    census_sha = sha256_file(args.census)
    if args.census.stat().st_size != expected_file['bytes'] or census_sha != expected_file['sha256']:
        raise ValueError('compressed census is not byte-identical to release manifest')
    challenge_raw = json.loads(args.challenges.read_text())
    challenges = {key: engine.sanitize(task) for key, task in challenge_raw.items()}
    del challenge_raw
    challenge_hash = engine.contract.digest(challenges)
    bank_hash = engine.bank_hash()
    code_hash = engine.code_hash()
    policies = ('typed_recent', 'typed_supported')
    results = {policy: None for policy in policies}
    records_seen = set()
    errors = []
    candidate_count = 0
    metadata = {}
    canonical = engine.contract.canonical_json
    census_digest = hashlib.sha256()
    census_digest.update(b'{')
    first_top = True
    stream = JSONStream(args.census)
    previous_top = None
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
                if metadata.get('bank_hash') != bank_hash or metadata.get('code_hash') != code_hash:
                    raise ValueError('census source bindings differ')
                if metadata.get('challenges_hash') != challenge_hash:
                    raise ValueError('census challenge binding differs')
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
                    if record['task_semantic_hash'] != engine.contract.digest(task):
                        raise ValueError('record semantic input binding differs')
                    if not first_record:
                        census_digest.update(b',')
                    census_digest.update(canonical(task_id).encode('utf-8') + b':' + canonical(record).encode('utf-8'))
                    first_record = False
                    # This temporary one-task census changes only aggregation.
                    # All program ranking and attempt construction are frozen.
                    subset = engine.seal({'scope': 'all_banks', 'records': {task_id: record},
                        'challenges_hash': engine.contract.digest({task_id: task}),
                        'bank_hash': bank_hash, 'code_hash': code_hash})
                    for policy in policies:
                        dispatched = solver.dispatch({task_id: task}, subset, policy)
                        if results[policy] is None:
                            results[policy] = {k: v for k, v in dispatched.items() if k != 'content_hash'}
                            results[policy]['decisions'] = {}
                            results[policy]['submission'] = {}
                        results[policy]['decisions'][task_id] = dispatched['decisions'][task_id]
                        results[policy]['submission'][task_id] = dispatched['submission'][task_id]
                    candidate_count += len(record['candidates'])
                    for provider, receipt in record['receipts'].items():
                        if receipt.get('status') != 'ok':
                            errors.append({'task_id': task_id, 'provider': provider, **receipt})
                    records_seen.add(task_id)
                    del subset, record, dispatched
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
            raise ValueError('streamed census semantic hash differs')
        if metadata.get('scope') != 'all_banks' or metadata.get('champion_fallback') is not False:
            raise ValueError('wrong census scope or champion fallback')
        if metadata.get('label_access') != 'demonstrations_only' or records_seen != set(challenges):
            raise ValueError('wrong census label scope or task membership')
        storage_receipt = json.loads((root / 'results/census_storage.json').read_text())
        engine.verify(storage_receipt)
        if stream.bytes_digest.hexdigest() != storage_receipt['uncompressed_sha256'] or stream.bytes_read != storage_receipt['uncompressed_bytes']:
            raise ValueError('decompressed census byte identity differs')
    finally:
        stream.close()
    prediction_files = {}
    for policy in policies:
        result = results[policy]
        result['census_hash'] = metadata['content_hash']
        result = engine.seal(result)
        path = out / (policy + '_dispatch.json')
        engine.write(path, result)
        prediction_files[policy] = {'path': str(path), 'sha256': sha256_file(path), 'content_hash': result['content_hash']}
        if args.compare_dir:
            expected = args.compare_dir / (policy + '.json')
            if prediction_files[policy]['sha256'] != sha256_file(expected):
                raise ValueError(f'fresh streaming dispatch differs from archived {policy} bytes')
            prediction_files[policy]['archived_prediction_byte_identical'] = True
        results[policy] = result
    engine.initialize()
    if bank_hash != engine.bank_hash() or code_hash != engine.code_hash():
        raise ValueError('source changed during dispatch')
    # Separate scoring starts only after both predictions were sealed, written,
    # and authenticated. No targets entered any dispatch invocation.
    scores = {}
    if args.solutions:
        targets = json.loads(args.solutions.read_text())
        scores = {policy: score(results[policy]['submission'], targets) for policy in policies}
    report = {'schema': 'komorebi.block17.streaming-authenticated-dispatch.v1',
        'scope': 'Fresh dispatcher replay from frozen compiled records, not a new full compiler search.',
        'source_unchanged': True, 'compressed_census_sha256': census_sha,
        'manifest_census_bytes_verified': True, 'decompressed_census_bytes_verified': True,
        'streaming_semantic_census_hash_verified': True, 'census_hash': metadata['content_hash'],
        'bank_hash': bank_hash, 'code_hash': code_hash, 'challenge_hash': challenge_hash,
        'records': len(records_seen), 'candidates': candidate_count,
        'all_record_content_and_task_bindings_verified': True,
        'unchanged_frozen_dispatcher_calls': len(records_seen) * len(policies),
        'prediction_label_access': 'demonstrations_only', 'champion_fallback': False,
        'targets_opened_only_after_predictions_written': args.solutions is not None,
        'predictions': prediction_files, 'scores': scores,
        'error_receipt_count': len(errors), 'error_receipts': errors,
        'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'elapsed_seconds': time.monotonic() - start, 'overall_pass': True}
    engine.write(out / 'replay_report.json', report)
    print(json.dumps({k: report[k] for k in ('records', 'candidates', 'scores', 'error_receipt_count', 'maximum_resident_mib', 'elapsed_seconds', 'overall_pass')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
