#!/usr/bin/env python3
"""Record a formal build command and source hashes before and after execution."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import time

def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*.lean')) if '.lake' not in p.parts}

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
parser.add_argument('--cwd', required=True)
parser.add_argument('--runtime-bin', required=True)
parser.add_argument('--compat-shim')
parser.add_argument('--mathlib-cache')
parser.add_argument('--timeout', type=int, default=900)
parser.add_argument('command', nargs=argparse.REMAINDER)
args = parser.parse_args()
cwd = Path(args.cwd).resolve()
runtime = Path(args.runtime_bin).resolve()
out = Path(__file__).resolve().parent
env = os.environ.copy()
env['PATH'] = str(runtime) + os.pathsep + env['PATH']
env['LEAN_BIN'] = str(runtime / 'lean')
env['LAKE_BIN'] = str(runtime / 'lake')
if args.compat_shim:
    env['LD_PRELOAD'] = str(Path(args.compat_shim).resolve())
if args.mathlib_cache:
    env['MATHLIB_CACHE_DIR'] = str(Path(args.mathlib_cache).resolve())
argv = args.command
if argv and argv[0] == '--':
    argv = argv[1:]
before = hashes(cwd)
started = time.monotonic()
result = {'argv': argv, 'cwd': str(cwd), 'runtime_bin': str(runtime),
          'timeout_seconds': args.timeout, 'source_hashes_before': before}
result['runtime_versions'] = {}
for executable in ['lean', 'lake']:
    version = subprocess.run([str(runtime / executable), '--version'],
                             env=env, capture_output=True, text=True)
    result['runtime_versions'][executable] = {
        'exit_code': version.returncode, 'output': version.stdout + version.stderr}
if args.compat_shim:
    shim = Path(args.compat_shim).resolve()
    result['host_compatibility_shim'] = {
        'path': str(shim), 'sha256': hashlib.sha256(shim.read_bytes()).hexdigest(),
        'effect': 'readlink on the calling process own /proc/PID/exe uses /proc/self/exe only'}
if args.mathlib_cache:
    result['mathlib_cache_directory'] = str(Path(args.mathlib_cache).resolve())
try:
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=args.timeout)
    output = proc.stdout + proc.stderr
    result.update(exit_code=proc.returncode, timed_out=False)
except subprocess.TimeoutExpired as error:
    def decode(value):
        return value.decode(errors='replace') if isinstance(value, bytes) else value or ''
    output = decode(error.stdout) + decode(error.stderr)
    result.update(exit_code=None, timed_out=True)
result['elapsed_seconds'] = round(time.monotonic() - started, 6)
result['source_hashes_after'] = hashes(cwd)
result['source_bytes_unchanged'] = before == result['source_hashes_after']
log = out / (args.name + '.log')
log.write_text(output)
result['log'] = log.name
result['log_sha256'] = hashlib.sha256(log.read_bytes()).hexdigest()
(out / (args.name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if not k.startswith('source_hashes')}))
raise SystemExit(result['exit_code'] if result['exit_code'] is not None else 124)
