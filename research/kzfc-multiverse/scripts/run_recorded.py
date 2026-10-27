#!/usr/bin/env python3
"""Run the proof verifier and persist the observed top-level process exit status."""
from __future__ import annotations
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    argv = ['python3', 'scripts/verify.py', *sys.argv[1:]]
    destination = ROOT / 'verification'
    destination.mkdir(exist_ok=True)
    (destination / 'process_record.json').unlink(missing_ok=True)
    wrapper = pathlib.Path(__file__).resolve()
    before = digest(wrapper)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    with (destination / 'verification_driver.log').open('w') as log:
        completed = subprocess.run(argv, cwd=ROOT, stdout=log,
                                   stderr=subprocess.STDOUT, check=False)
    record = {'argv': argv, 'started_at': started,
              'runtime_seconds': time.monotonic() - start,
              'exit_status': completed.returncode,
              'wrapper_path': str(wrapper.relative_to(ROOT)),
              'wrapper_sha256_before': before,
              'wrapper_sha256_after': digest(wrapper),
              'child_timeout_policy': 'Each verifier child has the per-command timeout recorded in RESULTS.json.'}
    (destination / 'process_record.json').write_text(json.dumps(record, indent=2) + '\n')
    print((destination / 'verification_driver.log').read_text(), end='')
    print('Recorded verifier exit:', completed.returncode)
    return completed.returncode

if __name__ == '__main__':
    raise SystemExit(main())
