#!/usr/bin/env python3
"""Schedule unchanged Block17 compilers in idle workers, without query labels.

This external scheduler preserves the complete engine run binding and source
limits. It writes authenticated checkpoints, never predictions or scores.
"""
from __future__ import annotations
import argparse
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime, timezone
import multiprocessing
import os
from pathlib import Path
import sys

EXPECTED_RUN_HASH = 'd5858775adc7c61a3593c6d058808ecefc97a85a696032213e7810b18cd0751e'


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--challenges', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--metadata', type=Path, required=True)
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--reserved-prefix', type=int, default=6)
    args = p.parse_args()
    if args.workers < 1 or args.reserved_prefix < 0:
        raise ValueError('invalid scheduling parameters')
    sys.path.insert(0, str(args.source.resolve()))
    import engine
    import contract
    multiprocessing.set_start_method('spawn')
    clean = {k: engine.sanitize(t) for k, t in engine.read(args.challenges).items()}
    if len(clean) != 120 or sum(len(t['test']) for t in clean.values()) != 172:
        raise ValueError('expected complete 120-task, 172-output challenge set')
    engine.initialize()
    run_hash = contract.digest({'code': engine.code_hash(), 'bank': engine.bank_hash(),
        'challenges': clean, 'include_new': True, 'limits': engine.LIMITS})
    if run_hash != EXPECTED_RUN_HASH:
        raise ValueError('complete run binding differs from the frozen public-evaluation run')
    checkpoint = args.output.with_suffix('.tasks')
    checkpoint.mkdir(parents=True, exist_ok=True)

    def path_for(key):
        return checkpoint / (contract.digest(key) + '.json')

    def authenticate(key):
        path = path_for(key)
        if not path.exists():
            return False
        item = engine.read(path)
        engine.verify(item)
        if item['run_hash'] != run_hash:
            raise ValueError('checkpoint run binding differs')
        engine.verify(item['record'])
        if item['record']['task_semantic_hash'] != contract.digest(clean[key]):
            raise ValueError('checkpoint task binding differs')
        return True

    missing = [k for k in sorted(clean) if not authenticate(k)]
    reserved = missing[:args.reserved_prefix]

    def complexity(key):
        task = clean[key]
        grids = [row[f] for row in task['train'] for f in ('input', 'output')]
        grids += [row['input'] for row in task['test']]
        sizes = [len(g) * len(g[0]) for g in grids]
        return max(sizes), sum(sizes), key

    pending = sorted(missing[args.reserved_prefix:], key=complexity)
    metadata = {'started_utc': utc(), 'run_hash': run_hash, 'code_hash': engine.code_hash(),
        'bank_hash': engine.bank_hash(), 'workers': args.workers,
        'reserved_active_task_ids': reserved, 'initial_missing': len(missing),
        'selection': 'ascending max demo/query-input grid cells, then total cells, then task ID',
        'compiler': 'unchanged engine.compile_record(task, include_new=True)',
        'scheduler_sha256': contract.sha256_file(Path(__file__)),
        'limits': engine.LIMITS, 'label_access': 'demonstrations_only',
        'source_changes': False, 'policy_changes': False, 'events': []}
    engine.write(args.metadata, engine.seal(metadata))
    print({'utc': utc(), 'reserved': reserved, 'supplemental_tasks': len(pending)}, flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=engine.initialize) as pool:
        active = {}
        while pending or active:
            while pending and len(active) < args.workers:
                key = pending.pop(0)
                if authenticate(key):
                    metadata['events'].append({'utc': utc(), 'task_id': key, 'event': 'skip_existing'})
                    continue
                future = pool.submit(engine.compile_record, clean[key], True)
                active[future] = key
                metadata['events'].append({'utc': utc(), 'task_id': key, 'event': 'started'})
                engine.write(args.metadata, engine.seal(metadata))
                print({'utc': utc(), 'task_id': key, 'event': 'started'}, flush=True)
            if not active:
                break
            finished, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in finished:
                key = active.pop(future)
                record = future.result()
                engine.verify(record)
                if record['task_semantic_hash'] != contract.digest(clean[key]):
                    raise ValueError('fresh record task binding differs')
                if authenticate(key):
                    existing = engine.read(path_for(key))['record']
                    if existing['content_hash'] != record['content_hash']:
                        raise ValueError('duplicate compilation differs; no checkpoint overwritten')
                    event = 'duplicate_identical_not_overwritten'
                else:
                    target = path_for(key)
                    # Use a distinct temporary path from engine.scan's writer.
                    temporary = target.with_name(target.name + f'.supplement-{os.getpid()}')
                    engine.write(temporary, engine.seal({'run_hash': run_hash, 'record': record}))
                    try:
                        os.link(temporary, target)
                        event = 'checkpoint_written'
                    except FileExistsError:
                        authenticate(key)
                        existing = engine.read(target)['record']
                        if existing['content_hash'] != record['content_hash']:
                            raise ValueError('racing duplicate differs; no checkpoint overwritten')
                        event = 'duplicate_identical_not_overwritten'
                    finally:
                        temporary.unlink(missing_ok=True)
                metadata['events'].append({'utc': utc(), 'task_id': key, 'event': event,
                    'record_hash': record['content_hash']})
                engine.write(args.metadata, engine.seal(metadata))
                print({'utc': utc(), 'task_id': key, 'event': event}, flush=True)
    metadata['completed_utc'] = utc()
    engine.write(args.metadata, engine.seal(metadata))


if __name__ == '__main__':
    main()
