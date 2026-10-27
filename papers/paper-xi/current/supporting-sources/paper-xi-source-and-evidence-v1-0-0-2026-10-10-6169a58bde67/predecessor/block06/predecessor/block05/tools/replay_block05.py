#!/usr/bin/env python3
"""Replay four named finite suites without modifying the checkpoint.

This does not run historical arithmetic matrix constructors or Lean/Lake.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.output.resolve()
    if out.is_relative_to(root):
        raise SystemExit('Replay output must be outside the immutable checkpoint.')
    out.mkdir(parents=True, exist_ok=True)
    b4 = root / 'predecessor/block04'
    b3 = b4 / 'predecessor/block03'
    jobs = [
        ('block05_atlas_models', root/'tools/test_atlas.py', 28),
        ('block04_exact_models', b4/'tools/exact_checks_block04.py', 23),
        ('block03_exact_models', b3/'tools/exact_checks_block03.py', 15),
        ('block01_exact_models', b3/'baseline/block01/tools/exact_checks.py', 12),
    ]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    records = []
    for label, source, expected in jobs:
        target = out / (label+'.json')
        # Do not accept a stale result left by an earlier execution.
        target.unlink(missing_ok=True)
        start = time.monotonic()
        print('RUN', label, flush=True)
        item = {'gate':label, 'expected_test_methods':expected,
                'source':source.relative_to(root).as_posix(),
                'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
        try:
            run = subprocess.run([sys.executable, str(source), '--output', str(target)],
                                 cwd=out, env=env, text=True, capture_output=True, timeout=90)
            (out/(label+'.stdout.log')).write_text(run.stdout)
            (out/(label+'.stderr.log')).write_text(run.stderr)
            data = json.loads(target.read_text()) if target.exists() else {}
            count = data.get('test_methods', data.get('methods', data.get('unittest_methods')))
            ok = run.returncode == 0 and data.get('status') == 'passed' and count == expected
            item.update(status='passed' if ok else 'failed', returncode=run.returncode,
                        reported_test_methods=count,
                        result_sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None)
        except subprocess.TimeoutExpired as exc:
            item.update(status='timeout', error=str(exc))
        except (OSError, ValueError) as exc:
            item.update(status='failed', error=str(exc))
        item['seconds'] = round(time.monotonic()-start, 3)
        (out/(label+'.receipt.json')).write_text(json.dumps(item, indent=2)+'\n')
        records.append(item)
        print(item['status'], flush=True)
    result = {'status':'passed' if all(x['status']=='passed' for x in records) else 'failed',
              'gates':records,
              'scope':'Four finite suites only. No direct matrix constructor, seven extra historical B03 arithmetic executions, Lean compiler, or external theorem audit.'}
    (out/'REPLAY_SUMMARY.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return int(result['status'] != 'passed')

if __name__ == '__main__':
    raise SystemExit(main())
