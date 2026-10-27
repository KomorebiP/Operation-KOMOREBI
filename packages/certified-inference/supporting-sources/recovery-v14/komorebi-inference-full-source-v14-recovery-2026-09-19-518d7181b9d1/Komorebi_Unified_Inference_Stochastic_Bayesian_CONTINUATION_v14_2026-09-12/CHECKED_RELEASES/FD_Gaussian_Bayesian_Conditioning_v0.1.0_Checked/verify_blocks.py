#!/usr/bin/env python3
"""Recheck one module or the whole FD Gaussian chain using the pinned portable runtime.

No downloads are performed. Every Lean invocation has its own wall-time cap.
An existing staged source with different bytes is never overwritten.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

PIN = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
LEAN_COMMIT = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--only', help='Check one named module against already checked dependencies')
    parser.add_argument('--timeout', type=int, default=75)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error('--timeout must be positive')
    package = Path(__file__).resolve().parent
    runtime = args.runtime.resolve()
    workspace = runtime / 'workspace'
    launch = runtime / 'run.sh'
    if not launch.is_file():
        raise RuntimeError('Missing portable runtime run.sh')
    version = subprocess.check_output(['bash', str(launch), 'lean', '--version'], text=True).strip()
    if '4.34.0-rc2' not in version or LEAN_COMMIT not in version:
        raise RuntimeError('Unexpected Lean runtime: ' + version)
    mathlib = workspace / '.lake/packages/mathlib'
    commit = subprocess.check_output(['git', '-c', f'safe.directory={mathlib}',
        '-C', str(mathlib), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != PIN:
        raise RuntimeError('Unexpected mathlib revision: ' + commit)
    modules = json.loads((package / 'MODULE_ORDER.json').read_text())
    if args.only and args.only not in modules:
        raise RuntimeError('Unknown module: ' + args.only)
    selected = [args.only] if args.only else modules
    sources = package / 'Komorebi'
    target = workspace / 'Komorebi'
    if target.is_symlink():
        raise RuntimeError('Workspace Komorebi directory is a symlink; use a regular directory')
    target.mkdir(exist_ok=True)
    cache = workspace / '.lake/build/lib/lean/Komorebi'
    cache.mkdir(parents=True, exist_ok=True)
    for name in selected:
        source = sources / (name + '.lean')
        text = source.read_text()
        # Intentionally conservative: placeholders are forbidden even in comments.
        if re.search(r'\b(?:sorry|admit|axiom|unsafe)\b', text):
            raise RuntimeError('Forbidden source token in ' + source.name)
        staged = target / source.name
        if staged.exists() and sha(staged) != sha(source):
            raise RuntimeError('Different existing staged source: ' + str(staged))
        shutil.copy2(source, staged)
    if not args.only:
        for name in modules:
            for path in cache.glob(name + '.olean*'):
                path.unlink()
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    audit = package / 'audit/rechecks' / stamp
    audit.mkdir(parents=True)
    results = []
    overall = 0
    for name in selected:
        source = sources / (name + '.lean')
        output = cache / (name + '.olean')
        before = sha(source)
        command = ['bash', str(launch), 'lake', 'env', 'lean',
            '-DwarningAsError=true', '-o', str(output), f'Komorebi/{name}.lean']
        record = {'module': name, 'command': command, 'source_sha256_before': before,
            'started_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'timeout_seconds': args.timeout, 'lean_version': version, 'mathlib_commit': commit}
        start = time.monotonic()
        log = audit / (name + '.log')
        with log.open('w') as stream:
            process = subprocess.Popen(command, cwd=workspace, stdout=stream,
                stderr=subprocess.STDOUT, start_new_session=True)
            try:
                rc = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                rc = 124
        record.update(runtime_seconds=round(time.monotonic()-start, 3), exit_status=rc,
            source_sha256_after=sha(source), log_sha256=sha(log))
        if rc == 0 and before != record['source_sha256_after']:
            rc = 125
            record['exit_status'] = rc
        if rc == 0:
            record['olean_sha256'] = sha(output)
        else:
            for path in cache.glob(name + '.olean*'):
                path.unlink()
        if name == 'FDConditioningAxiomAudit' and rc == 0:
            dependencies = re.findall(r'depends on axioms:\s*\[([^\]]*)\]', log.read_text(), re.S)
            if len(dependencies) != 51:
                raise RuntimeError('Axiom audit declaration count is not 51')
            found = {item.strip() for deps in dependencies for item in deps.split(',') if item.strip()}
            if not found <= ALLOWED_AXIOMS:
                raise RuntimeError('Unexpected axioms: ' + repr(found - ALLOWED_AXIOMS))
            record['axioms'] = sorted(found)
        (audit / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        results.append(record)
        print(f"{name}: RC={rc}, {record['runtime_seconds']} s", flush=True)
        if rc:
            print(log.read_text(), flush=True)
            overall = rc
            break
    (audit / 'RESULT.json').write_text(json.dumps({'exit_status': overall,
        'full_chain': not bool(args.only), 'completed_modules': len(results),
        'requested_modules': len(selected), 'records': results}, indent=2) + '\n')
    print('Audit directory:', audit)
    return overall

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('FAILED:', exc, file=sys.stderr)
        sys.exit(1)
