#!/usr/bin/env python3
"""Record minimal run context even when a hosted dependency bootstrap fails.

No credentials or general environment dump are collected. This record alone can
never satisfy the proof-replay gate; that requires REPLAY.json and checked logs.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

KEYS = ('GITHUB_REPOSITORY', 'GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT',
        'GITHUB_WORKFLOW_REF', 'RUNNER_OS', 'RUNNER_ARCH', 'BOOTSTRAP_OUTCOME', 'REPLAY_OUTCOME')

def workflow_record(environ: dict[str, str]) -> dict:
    return {'record_type': 'workflow_context_only', 'proof_verified': False,
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
            'context': {key: environ.get(key, 'unavailable') for key in KEYS},
            'boundary': 'Context and step outcomes are not a passing proof receipt. Missing, skipped, failed, or cancelled proof stages do not close the reproduction gate.'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(workflow_record(dict(os.environ)), stream, indent=2)
        stream.write('\n')
    print('Recorded workflow context only; no proof result inferred.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
