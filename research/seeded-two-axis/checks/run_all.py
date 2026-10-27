#!/usr/bin/env python3
"""Run the six bounded regression suites and record exact execution provenance.

Run from any directory. Output files in checks/ and audit/ are overwritten.
A successful suite tests the stated finite implementation contract, not a proof.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ('check_models.py', ['--max-length', '10'], 'base_regression_results.json'),
    ('check_interactions.py', [], 'interaction_results.json'),
    ('check_resolution_towers.py', [], 'resolution_results.json'),
    ('check_intrinsic_exchange.py', [], 'intrinsic_results.json'),
    ('check_action_lifting.py', [], 'action_lifting_results.json'),
    ('check_profinite_lifting.py', [], 'profinite_results.json'),
]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def main() -> int:
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    records = []
    for script, extra, output in CASES:
        script_path = ROOT/'checks'/script
        output_path = ROOT/'checks'/output
        argv = [sys.executable, str(Path('checks')/script), *extra,
                '--output', str(Path('checks')/output)]
        output_path.unlink(missing_ok=True)  # Never authenticate a stale report.
        before = sha(script_path); started = now(); tic = time.monotonic()
        try:
            run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True,
                                 text=True, timeout=40, check=False)
            stdout, stderr, code = run.stdout, run.stderr, run.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ''; stderr = exc.stderr or ''
            if isinstance(stdout, bytes): stdout = stdout.decode(errors='replace')
            if isinstance(stderr, bytes): stderr = stderr.decode(errors='replace')
            stderr += '\nRunner timeout after 40 seconds.\n'; code = 124
        wall = time.monotonic()-tic
        stem = Path(script).stem
        (ROOT/'audit'/f'{stem}_stdout.log').write_text(stdout)
        (ROOT/'audit'/f'{stem}_stderr.log').write_text(stderr)
        report = json.loads(output_path.read_text()) if code == 0 and output_path.exists() else {}
        entry = {'argv':argv, 'started_utc':started, 'finished_utc':now(),
                 'wall_seconds':wall, 'exit_code':code, 'report_status':report.get('status'),
                 'timeout_seconds':40, 'memory_cap':'not set',
                 'thread_caps':{'OPENBLAS_NUM_THREADS':'1', 'OMP_NUM_THREADS':'1'},
                 'script_sha256_before':before, 'script_sha256_after':sha(script_path),
                 'output':str(output_path.relative_to(ROOT)),
                 'output_sha256':sha(output_path) if code == 0 and output_path.exists() else None}
        records.append(entry)
        print(f'{script}: exit={code}, report={entry["report_status"]}, {wall:.3f}s')
        if code != 0 or report.get('status') != 'PASS' or before != sha(script_path):
            break
    passed = len(records)==len(CASES) and all(r['exit_code']==0 and r['report_status']=='PASS'
             and r['script_sha256_before']==r['script_sha256_after'] for r in records)
    manifest = {'schema':'komorebi-bounded-runs-v1', 'status':'PASS' if passed else 'FAIL',
                'python':platform.python_version(), 'platform':platform.platform(),
                'runner_sha256':sha(Path(__file__)), 'runs':records,
                'evidence_boundary':'Finite regression only; not Lean or universal theorem verification.'}
    (ROOT/'checks/all_runs.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return 0 if passed else 1

if __name__=='__main__':
    raise SystemExit(main())
