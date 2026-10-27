"""Select a small cached activation sample without targets or runtime imports."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
SEEDS = ('00576224', '007bbfb7', '0d3d703e')
RECORD_CAP = 32 * 1024 * 1024
TOTAL_CAP = 64 * 1024 * 1024
PARSER_SHA = '3c7811352a40328cff2e1c56db0cbc4f889759e31dd6b455edc6fb2fbbec8d56'


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def identity(path):
    with path.open('rb') as handle:
        sha = hashlib.file_digest(handle, 'sha256').hexdigest()
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': sha}


def seal(value):
    return {**value, 'content_hash': digest(value)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace', type=Path, required=True)
    args = ap.parse_args()
    workspace = args.workspace.resolve()
    root = workspace / 'arc-fullbank/block17'
    output = workspace / 'arc-evidence/block17-limitfix-diagnosis'
    output.mkdir(parents=True, exist_ok=True)
    paths = {name: output / name for name in ('selected_challenges.json',
                                            'expected_records.json', 'selection_audit.json')}
    require(not any(p.exists() for p in paths.values()), 'selection outputs already exist')
    challenges_path = workspace / 'arc-offline-data/arc-agi_training_challenges.json'
    census_path = root / 'results/census.json.gz'
    parser_path = workspace / 'arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py'
    registry_path = root / 'bank14_15.json'
    manifest_path = root / 'release_manifest.json'
    storage_path = root / 'results/census_storage.json'
    inputs = {name: identity(path) for name, path in (
        ('challenges', challenges_path), ('census', census_path), ('parser', parser_path),
        ('registry', registry_path), ('release_manifest', manifest_path), ('storage', storage_path))}
    require(inputs['parser']['sha256'] == PARSER_SHA, 'stream parser pin differs')
    manifest = json.loads(manifest_path.read_text())
    expected = manifest['files']['results/census.json.gz']
    require(all(inputs['census'][key] == expected[key] for key in ('bytes', 'sha256')),
            'cached compressed census differs from original release')
    storage = json.loads(storage_path.read_text())
    raw_challenges = json.loads(challenges_path.read_text())
    clean = {}
    for task_id, task in raw_challenges.items():
        require(all('output' not in row for row in task['test']), 'attached query targets')
        clean[task_id] = {'train': [{'input': r['input'], 'output': r['output']} for r in task['train']],
                          'test': [{'input': r['input']} for r in task['test']]}
    require(len(clean) == 1000 and sum(len(t['test']) for t in clean.values()) == 1076,
            'training challenge membership differs')
    rank = {task_id: (sum(len(row) for part in ('train', 'test') for example in task[part]
                              for row in example['input']), task_id)
            for task_id, task in clean.items()}
    modern = set(json.loads(registry_path.read_text()))
    require(len(modern) == 48, 'modern registry membership differs')
    spec = importlib.util.spec_from_file_location('selection_parser', parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    stream = parser.JSONStream(census_path)
    metadata, details, best, files = {}, {}, {}, {}
    providers, errors = Counter(), Counter()
    temporary = output / 'selection_temp_records'
    require(not temporary.exists(), 'temporary selection directory already exists')
    temporary.mkdir()
    full_digest = hashlib.sha256(b'{')
    first_top, previous_top = True, None
    start = time.monotonic()
    try:
        stream.expect('{')
        while stream.peek() != '}':
            key = stream.value()
            require(isinstance(key, str) and (previous_top is None or key > previous_top),
                    'top keys not unique and sorted')
            previous_top = key
            stream.expect(':')
            if key != 'content_hash':
                if not first_top:
                    full_digest.update(b',')
                full_digest.update(canonical(key) + b':')
                first_top = False
            if key == 'records':
                stream.expect('{')
                full_digest.update(b'{')
                first_record, previous_task = True, None
                while stream.peek() != '}':
                    task_id = stream.value()
                    require(task_id in clean and (previous_task is None or task_id > previous_task),
                            'unknown or duplicate/unsorted task')
                    previous_task = task_id
                    stream.expect(':')
                    record = stream.value()
                    require(record['content_hash'] == digest({k: v for k, v in record.items()
                                                            if k != 'content_hash'}),
                            'cached record seal mismatch')
                    require(record['task_semantic_hash'] == digest(clean[task_id]),
                            'cached record challenge binding mismatch')
                    record_raw = canonical(record)
                    if not first_record:
                        full_digest.update(b',')
                    full_digest.update(canonical(task_id) + b':' + record_raw)
                    first_record = False
                    counts = Counter(c['entrant'] for c in record['candidates'])
                    providers.update(counts)
                    errors.update(p for p, r in record['receipts'].items() if r.get('status') != 'ok')
                    details[task_id] = {'input_cells': rank[task_id][0],
                        'record_hash': record['content_hash'], 'record_canonical_bytes': len(record_raw),
                        'candidate_count': len(record['candidates']), 'candidate_provider_counts': dict(counts),
                        'modern_providers': sorted(set(counts) & modern)}
                    eligible = len(record_raw) <= RECORD_CAP or task_id in SEEDS
                    improving = []
                    if eligible and task_id not in SEEDS:
                        for provider in (set(counts) & modern) | ({'extraction'} if counts['extraction'] else set()):
                            if provider not in best or rank[task_id] < rank[best[provider]]:
                                improving.append(provider)
                    if task_id in SEEDS or improving:
                        path = temporary / (task_id + '.json')
                        path.write_bytes(record_raw)
                        files[task_id] = path
                        for provider in improving:
                            best[provider] = task_id
                        retained = set(SEEDS) | set(best.values())
                        for obsolete in set(files) - retained:
                            files.pop(obsolete).unlink()
                    del record, record_raw
                    if len(details) % 100 == 0:
                        print(json.dumps({'authenticated_records': len(details),
                            'elapsed_seconds': round(time.monotonic() - start, 2),
                            'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024}),
                            flush=True)
                    if stream.peek() == ',':
                        stream.expect(',')
                    else:
                        require(stream.peek() == '}', 'invalid record delimiter')
                stream.expect('}')
                full_digest.update(b'}')
            else:
                value = stream.value()
                metadata[key] = value
                if key != 'content_hash':
                    full_digest.update(canonical(value))
            if stream.peek() == ',':
                stream.expect(',')
            else:
                require(stream.peek() == '}', 'invalid top delimiter')
        stream.expect('}')
        require(not stream.peek(), 'trailing census content')
        full_digest.update(b'}')
        require(set(details) == set(clean), 'incomplete cached record membership')
        require(full_digest.hexdigest() == metadata['content_hash'] == storage['census_content_hash'],
                'complete semantic census seal mismatch')
        require(stream.bytes_read == storage['uncompressed_bytes'] and
                stream.bytes_digest.hexdigest() == storage['uncompressed_sha256'],
                'decompressed census byte identity differs')
        require(metadata['challenges_hash'] == digest(clean), 'header challenge hash differs')
        require(metadata['scope'] == 'all_banks' and metadata['label_access'] == 'demonstrations_only'
                and metadata['champion_fallback'] is False, 'cached scope differs')
        require(sum(providers.values()) == 12391, 'cached candidate count differs')
        source_files = {n: identity(root / n)['sha256'] for n in
                        ('engine.py', 'legacy.py', 'action_adapter.py', 'contract.py', 'memo.py')}
        require(metadata['code_hash'] == digest(source_files), 'original code hash differs')
        require(metadata['bank_hash'] == digest({n: json.loads((root / n).read_text()) for n in
                ('vendor_manifest.json', 'bank13.json', 'bank14_15.json')}), 'original bank hash differs')
        selected = list(SEEDS)
        reasons = {key: 'retained archived full-bank compiler validation sample' for key in SEEDS}
        covered = set().union(*(set(details[key]['modern_providers']) for key in selected))
        if providers['extraction'] and not any(details[k]['candidate_provider_counts'].get('extraction') for k in selected):
            require('extraction' in best, 'all extraction records exceed selection record-size cap')
            selected.append(best['extraction'])
            reasons[selected[-1]] = 'smallest eligible input-cell task with cached extraction candidate'
            covered.update(details[selected[-1]]['modern_providers'])
        while len(selected) < 6:
            available = {key for provider, key in best.items() if provider in modern - covered and key not in selected}
            available = {key for key in available if sum(details[k]['record_canonical_bytes'] for k in selected)
                         + details[key]['record_canonical_bytes'] <= TOTAL_CAP}
            if not available:
                break
            key = min(available, key=lambda k: rank[k])
            selected.append(key)
            reasons[key] = 'smallest eligible input-cell task adding an uncovered modern provider'
            covered.update(details[key]['modern_providers'])
        require(sum(details[k]['record_canonical_bytes'] for k in selected) <= TOTAL_CAP,
                'selected record total exceeds cap')
        paths['selected_challenges.json'].write_bytes(canonical({k: clean[k] for k in selected}) + b'\n')
        # Stream concatenated original records: no selected aggregate object is required.
        with paths['expected_records.json'].open('wb') as handle:
            handle.write(b'{')
            for index, key in enumerate(sorted(selected)):
                if index:
                    handle.write(b',')
                handle.write(canonical(key) + b':')
                with files[key].open('rb') as source:
                    while chunk := source.read(1024 * 1024):
                        handle.write(chunk)
            handle.write(b'}\n')
        for name, before in inputs.items():
            require(identity(Path(before['path'])) == before, 'selection input changed: ' + name)
        audit = seal({'schema': 'arc.block17.limitfix-label-free-training-selection.v1',
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'integrity_pass': True,
            'selection_rule': 'Keep archived3; optional smallest extraction activation; greedily add smallest '
                '(all train+test input cells, lexical task ID) task with an uncovered exact bank14_15 provider; '
                'at most6; eligible cached records<=32MiB, selected total<=64MiB.',
            'selected_task_ids_in_selection_order': selected,
            'selection_reasons': reasons, 'selected_tasks': {k: details[k] for k in selected},
            'selected_task_record_hashes': {k: details[k]['record_hash'] for k in selected},
            'original_training_census_header': metadata, 'input_identities': inputs,
            'original_code_source_files_sha256': source_files,
            'cached_candidate_provider_counts': dict(providers),
            'cached_candidate_count': sum(providers.values()), 'cached_extraction_candidates': providers['extraction'],
            'cached_extraction_tasks': sum(d['candidate_provider_counts'].get('extraction', 0) > 0 for d in details.values()),
            'cached_non_ok_receipts_by_provider': dict(errors), 'authenticated_cached_tasks': len(details),
            'authenticated_cached_test_outputs': sum(len(t['test']) for t in clean.values()),
            'complete_semantic_census_hash': full_digest.hexdigest(),
            'decompressed_census_sha256': stream.bytes_digest.hexdigest(), 'decompressed_census_bytes': stream.bytes_read,
            'selected_modern_providers': sorted(covered), 'modern_provider_registry': sorted(modern),
            'outputs': {name: identity(paths[name]) for name in ('selected_challenges.json', 'expected_records.json')},
            'selector_sha256': identity(Path(__file__))['sha256'],
            'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            'elapsed_seconds': time.monotonic() - start, 'query_targets_opened': False,
            'compiler_dispatcher_program_calls': 0, 'frozen_runtime_imports': 0,
            'limitations': ['Cached activation selection does not establish fresh generation equivalence.',
                'Cached candidate test predictions are retained but are never compared with query truth.',
                'Streaming decoder retains one full record; record-size eligibility caps apply to retained subset, not decoder peak.']})
        paths['selection_audit.json'].write_bytes(canonical(audit) + b'\n')
        print(json.dumps({'integrity_pass': True, 'selected_task_ids': selected,
              'cached_extraction_candidates': providers['extraction'],
              'outputs': {name: str(path) for name, path in paths.items()}}), flush=True)
    finally:
        stream.close()
        for path in temporary.glob('*.json'):
            path.unlink()
        temporary.rmdir()


if __name__ == '__main__':
    main()
