#!/usr/bin/env python3
"""Bounded fresh ORIGINAL Block17 compilation; no solution paths or scoring.

One new process/session per task. Children receive only sanitized demonstrations
and query inputs, never expected records or the cached census. Watchdog expiry
is an incomplete observation, not failed equivalence. Outputs stay exterior.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent.parent
SOURCE = WORKSPACE / 'arc-fullbank/block17'
LOG_CAP = 65536


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def utc():
    return datetime.now(timezone.utc).isoformat()


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def read(path):
    with Path(path).open(encoding='utf-8') as handle:
        return json.load(handle, object_pairs_hook=no_duplicates,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != 'content_hash'}
    return {**body, 'content_hash': digest(body)}


def atomic_json(path, value):
    path = Path(path)
    partial = path.with_name(path.name + '.partial')
    require(not partial.exists(), 'stale partial: ' + str(partial))
    try:
        with partial.open('x', encoding='utf-8', newline='\n') as handle:
            for chunk in json.JSONEncoder(sort_keys=True, indent=2,
                    ensure_ascii=False, allow_nan=False).iterencode(value):
                handle.write(chunk)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(partial, path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def identity(path):
    path = Path(path).resolve(strict=True)
    before = path.stat()
    with path.open('rb') as handle:
        sha = hashlib.file_digest(handle, 'sha256').hexdigest()
    after = path.stat()
    require((before.st_size, before.st_mtime_ns, before.st_ino) ==
            (after.st_size, after.st_mtime_ns, after.st_ino), 'input changed while hashing')
    return {'path': str(path), 'bytes': after.st_size, 'sha256': sha}


def same_content_identity(left, right):
    """Location may change on restore; authenticated bytes must remain exact."""
    return all(left.get(key) == right.get(key) for key in ('bytes', 'sha256'))


def source_inventory(source, original):
    found = {}
    for path in sorted(Path(source).rglob('*')):
        require(not path.is_symlink(), 'source contains symlink')
        if path.is_file():
            ident = identity(path)
            found[path.relative_to(source).as_posix()] = {
                'bytes': ident['bytes'], 'sha256': ident['sha256'],
                'mtime_ns': path.stat().st_mtime_ns}
    require({k: v['sha256'] for k, v in found.items()} == original['files'],
            'original source inventory/content differs')
    return found


def load_engine(source):
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(source).resolve()))
    import engine
    require(Path(engine.__file__).resolve() == Path(source).resolve() / 'engine.py',
            'wrong engine module')
    require(Path(engine.contract.__file__).resolve() == Path(source).resolve() / 'contract.py',
            'wrong contract module')
    return engine


def validate_record(engine, task, record):
    engine.verify(record)
    require(set(record) == {'task_semantic_hash', 'base', 'candidates', 'receipts', 'content_hash'},
            'record fields differ')
    require(record['task_semantic_hash'] == engine.contract.digest(task), 'record task binding differs')
    require(isinstance(record['base'], list) and len(record['base']) == len(task['test']), 'base arity differs')
    for row in record['base']:
        require(isinstance(row, dict) and set(row) == {'attempt_1', 'attempt_2'}, 'base attempts differ')
        for grid in row.values():
            engine.contract.validate_grid(grid)
    require(isinstance(record['candidates'], list) and isinstance(record['receipts'], dict), 'record arrays/maps differ')
    previous = None
    for candidate in record['candidates']:
        require(isinstance(candidate, dict) and isinstance(candidate.get('entrant'), str), 'candidate provider differs')
        candidate_hash = candidate.get('candidate_hash')
        require(candidate_hash == engine.contract.digest({k: v for k, v in candidate.items() if k != 'candidate_hash'}),
                'candidate seal differs')
        require(previous is None or candidate_hash >= previous, 'candidate order differs')
        previous = candidate_hash
        outputs = candidate.get('test_outputs')
        require(isinstance(outputs, list) and len(outputs) == len(task['test']), 'candidate arity differs')
        for grid in outputs:
            engine.contract.validate_grid(grid)
        require(candidate.get('behavior_hash') == engine.contract.digest(outputs), 'candidate behavior differs')


def provider_identities(record):
    groups = defaultdict(list)
    for candidate in record['candidates']:
        groups[candidate['entrant']].append(candidate['candidate_hash'])
    return {name: sorted(values) for name, values in sorted(groups.items())}


def compare_records(engine, task, expected, fresh):
    validate_record(engine, task, expected)
    validate_record(engine, task, fresh)
    left, right = provider_identities(expected), provider_identities(fresh)
    providers = {}
    for name in sorted(set(left) | set(right)):
        a, b = left.get(name, []), right.get(name, [])
        providers[name] = {'expected_count': len(a), 'fresh_count': len(b), 'identities_exact': a == b,
            'expected_identities_hash': engine.contract.digest(a), 'fresh_identities_hash': engine.contract.digest(b)}
    canonical = engine.contract.canonical_json
    base_exact = canonical(expected['base']) == canonical(fresh['base'])
    receipts_exact = canonical(expected['receipts']) == canonical(fresh['receipts'])
    expected_full, fresh_full = engine.contract.digest(expected), engine.contract.digest(fresh)
    return {'full_canonical_record_hash_expected': expected_full,
        'full_canonical_record_hash_fresh': fresh_full, 'entire_record_hash_exact': expected_full == fresh_full,
        'expected_record_content_hash': expected['content_hash'], 'fresh_record_content_hash': fresh['content_hash'],
        'base_exact': base_exact, 'receipts_exact': receipts_exact, 'providers': providers,
        'candidate_identities_by_provider_exact': left == right,
        'equivalent': expected_full == fresh_full and base_exact and receipts_exact and left == right}


def progress(event):
    print(json.dumps(event, sort_keys=True), flush=True)


def owned_stop(process):
    """Only our still-running Popen child in its freshly created local session."""
    actions = []
    for sig, grace in ((signal.SIGTERM, 3), (signal.SIGKILL, 3)):
        if process.poll() is not None:
            break
        try:
            require(os.getpgid(process.pid) == process.pid and os.getsid(process.pid) == process.pid,
                    'owned child process group/session differs; refusing group signal')
            os.killpg(process.pid, sig)
            actions.append({'signal': sig.name, 'owned_local_pid_and_group': process.pid})
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=grace)
            break
        except subprocess.TimeoutExpired:
            continue
    require(process.poll() is not None, 'owned diagnostic child did not stop')
    return actions


def run_owned(command, cwd, log_path, timeout, notify=progress):
    require(math.isfinite(timeout) and timeout > 0, 'watchdog must be positive and finite')
    env = dict(os.environ)
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=cwd, env=env, start_new_session=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log_stats = {'received_bytes': 0, 'written_bytes': 0}

    def drain():
        with Path(log_path).open('xb') as handle:
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                log_stats['received_bytes'] += len(chunk)
                kept = chunk[:max(0, LOG_CAP - log_stats['written_bytes'])]
                handle.write(kept)
                log_stats['written_bytes'] += len(kept)

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    timed_out = False
    actions = []
    try:
        while process.poll() is None:
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                timed_out = True
                actions = owned_stop(process)
                break
            try:
                process.wait(timeout=min(remaining, 15))
            except subprocess.TimeoutExpired:
                notify({'event': 'child_watchdog_observation', 'elapsed_seconds': round(time.monotonic() - started, 3),
                        'timeout_seconds': timeout})
    except BaseException:
        if process.poll() is None:
            owned_stop(process)
        raise
    finally:
        reader.join(timeout=3)
    require(not reader.is_alive(), 'owned child stdout did not close')
    return {'exit_code': process.returncode, 'external_watchdog_timeout': timed_out,
        'wall_seconds': time.monotonic() - started, 'stop_actions': actions, 'log': identity(log_path),
        'log_received_bytes': log_stats['received_bytes'], 'log_written_bytes': log_stats['written_bytes'],
        'log_truncated': log_stats['received_bytes'] > log_stats['written_bytes'],
        'child_pid_origin': 'Popen-owned local PID; never imported from host /proc'}


def child_main(args):
    result = {'schema': 'block17.fresh-original-child.v1', 'status': 'started', 'started_utc': utc(),
              'query_targets_opened': False, 'cached_records_opened': False}
    cpu_start = time.process_time()
    try:
        original = read(args.source_identity)
        before = source_inventory(args.source, original)
        engine = load_engine(args.source)
        task = engine.sanitize(read(args.task_input))
        result.update(task_semantic_hash=engine.contract.digest(task), code_hash=engine.code_hash(), bank_hash=engine.bank_hash(),
                      source=str(args.source.resolve()), historical_source=original.get('source'))
        atomic_json(args.child_result, seal(result))
        record = engine.compile_record(task, include_new=True)
        validate_record(engine, task, record)
        # Persist the completed record before any comparison. This child never
        # receives an expected-record/cache path and makes no comparison.
        atomic_json(args.record_output, record)
        after = source_inventory(args.source, original)
        require(before == after, 'source size/hash/mtime changed during fresh compilation')
        result.update(status='completed', record=identity(args.record_output), record_hash=record['content_hash'],
            source_before_hash=digest(before), source_after_hash=digest(after), source_unchanged=True)
        code = 0
    except BaseException as error:
        result.update(status='child_exception', exception_type=type(error).__name__,
                      exception_message=str(error)[:512])
        code = 1
    result.update(finished_utc=utc(), own_cpu_seconds=time.process_time() - cpu_start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    atomic_json(args.child_result, seal(result))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--challenges', type=Path, default=HERE / 'selected_challenges.json')
    parser.add_argument('--expected-records', type=Path, default=HERE / 'expected_records.json')
    parser.add_argument('--selection-audit', type=Path, default=HERE / 'selection_audit.json')
    parser.add_argument('--source-identity', type=Path, default=HERE / 'original_source_identity.json')
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output-dir', type=Path, default=HERE / 'fresh_original_training')
    parser.add_argument('--timeout', type=float, default=90)
    parser.add_argument('--workers', type=int, choices=(1,), default=1,
                        help='Sequential memory-safe mode; at most one compiler child')
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--task-input', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--record-output', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--child-result', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        require(all((args.task_input, args.record_output, args.child_result)), 'child paths missing')
        return child_main(args)
    require(math.isfinite(args.timeout) and args.timeout > 0, 'watchdog must be positive and finite')
    output = args.output_dir.resolve()
    require(output.parent == HERE and not output.exists(), 'output must be a new direct directory under diagnosis')
    inputs = {name: identity(path) for name, path in {
        'challenges': args.challenges, 'expected_records': args.expected_records,
        'selection_audit': args.selection_audit, 'source_identity': args.source_identity,
        'runner': Path(__file__)}.items()}
    require(inputs['challenges']['bytes'] <= 1024 * 1024 and inputs['expected_records']['bytes'] <= 64 * 1024 * 1024,
            'bounded selected input size exceeded')
    original = read(args.source_identity)
    require(len(original['files']) == 388, 'expected original388-file source inventory')
    before = source_inventory(args.source, original)
    engine = load_engine(args.source)
    challenges = read(args.challenges)
    require(isinstance(challenges, dict) and 1 <= len(challenges) <= 6, 'requires1..6 selected challenges')
    clean = {key: engine.sanitize(task) for key, task in challenges.items()}
    expected = read(args.expected_records)
    require(set(clean) == set(expected), 'selected/expected task membership differs')
    audit = read(args.selection_audit)
    engine.verify(audit)
    require(audit.get('integrity_pass') is True and audit.get('query_targets_opened') is False,
            'selection provenance scope differs')
    for name, key in (('challenges', 'selected_challenges.json'), ('expected_records', 'expected_records.json')):
        require(same_content_identity(audit['outputs'][key], inputs[name]), 'selection output content identity differs')
    header = audit['original_training_census_header']
    bindings = {'code_hash': engine.code_hash(), 'bank_hash': engine.bank_hash()}
    require(all(header.get(k) == v for k, v in bindings.items()) and header.get('limits') == engine.LIMITS and
            header.get('scope') == 'all_banks' and header.get('label_access') == 'demonstrations_only' and
            header.get('champion_fallback') is False and header.get('schema') == 'komorebi.block17.combined_census.v1',
            'archived fullbank merger/source/limits bindings differ')
    require(all(isinstance(header.get(k), str) and len(header[k]) == 64 for k in
                ('old_census_hash', 'reused_block16_census_hash', 'content_hash', 'challenges_hash')),
            'archived merger identity absent')
    order = audit['selected_task_ids_in_selection_order']
    require(len(order) == len(clean) and len(set(order)) == len(order) and set(order) == set(clean), 'selection order differs')
    for key in order:
        validate_record(engine, clean[key], expected[key])
        require(expected[key]['content_hash'] == audit['selected_task_record_hashes'][key], 'selected archived record differs')
    output.mkdir()
    atomic_json(output / 'source_before.json', before)
    results = {}
    report = {'schema': 'block17.fresh-original-training-comparison.v1', 'started_utc': utc(),
        'inputs': inputs, 'source': str(args.source.resolve()), 'historical_source': original.get('source'),
        'historical_selection_output_identities': audit['outputs'], 'source_bindings': bindings,
        'timeout_seconds_per_task_external': args.timeout, 'workers': 1, 'selection_order': order,
        'query_targets_opened': False, 'benchmark_score_claimed': False, 'results': results,
        'claim_scope': 'Fresh original fullbank compilation versus authenticated cached selected training records; no held-out score or patched fullbank run.'}
    atomic_json(output / 'progress.json', seal(report))
    for key in order:
        folder = output / digest(key)
        folder.mkdir()
        task_path, record_path, child_path = folder / 'task_input.json', folder / 'fresh_record.json', folder / 'child_result.json'
        atomic_json(task_path, clean[key])
        progress({'event': 'fresh_original_task_started', 'task_id': key, 'external_timeout_seconds': args.timeout})
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--child', '--source', str(args.source.resolve()),
            '--source-identity', str(args.source_identity.resolve()), '--task-input', str(task_path),
            '--record-output', str(record_path), '--child-result', str(child_path)]
        result = run_owned(command, args.source, folder / 'bounded_child.log', args.timeout)
        result.update(task_id=key, record_present=record_path.is_file())
        if result['external_watchdog_timeout']:
            result.update(status='incomplete_timeout', equivalence=None)
        elif result['exit_code'] != 0:
            result.update(status='incomplete_child_error', equivalence=None)
            if child_path.is_file(): result['child_report'] = read(child_path)
        else:
            try:
                child = read(child_path); engine.verify(child)
                require(child['status'] == 'completed' and child.get('source_unchanged') is True and
                        all(child.get(k) == v for k, v in bindings.items()) and
                        child['task_semantic_hash'] == engine.contract.digest(clean[key]), 'child validation/bindings differ')
                require(child['record'] == identity(record_path), 'persisted fresh record differs from child receipt')
                fresh = read(record_path)
                comparison = compare_records(engine, clean[key], expected[key], fresh)
                result.update(status='completed_equal' if comparison['equivalent'] else 'completed_mismatch',
                    equivalence=comparison['equivalent'], comparison=comparison, child_report=child)
                del fresh
            except Exception as error:
                result.update(status='incomplete_validation_error', equivalence=None,
                              exception_type=type(error).__name__, exception_message=str(error)[:512])
        results[key] = result
        atomic_json(folder / 'comparison.json', seal(result))
        atomic_json(output / 'progress.json', seal(report))
        progress({'event': 'fresh_original_task_finished', 'task_id': key, 'status': result['status'],
                  'wall_seconds': round(result['wall_seconds'], 3), 'equivalence': result['equivalence']})
    after = source_inventory(args.source, original)
    atomic_json(output / 'source_after.json', after)
    require(before == after, 'original source changed during run')
    require(all(identity(row['path']) == row for row in inputs.values()), 'run input bytes changed')
    complete = sum(r['status'].startswith('completed_') for r in results.values())
    equal = sum(r['status'] == 'completed_equal' for r in results.values())
    mismatch = sum(r['status'] == 'completed_mismatch' for r in results.values())
    report.update(finished_utc=utc(), source_unchanged=True, source_before_hash=digest(before),
        source_after_hash=digest(after), completed_tasks=complete, equivalent_tasks=equal,
        mismatching_tasks=mismatch, incomplete_tasks=len(order) - complete,
        all_selected_completed_equal=equal == len(order), inputs_unchanged=True,
        limitations=['Timeout/error tasks are incomplete and carry no equivalence verdict.',
            'The selected training sample is bounded and is not universal equivalence or a benchmark score.',
            'Children compile fresh; only the parent reads cached expected selected records for comparison.',
            'Source identities are point-in-time checks; no unrelated process is controlled.'])
    atomic_json(output / 'comparison_report.json', seal(report))
    progress({'event': 'fresh_original_comparison_finished', 'completed': complete, 'equal': equal,
              'mismatch': mismatch, 'incomplete': len(order) - complete, 'report': str(output / 'comparison_report.json')})
    return 3 if complete != len(order) else (2 if mismatch else 0)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({'event': 'runner_validation_error', 'exception_type': type(error).__name__,
                          'exception_message': str(error)[:512]}), file=sys.stderr, flush=True)
        raise SystemExit(1)
