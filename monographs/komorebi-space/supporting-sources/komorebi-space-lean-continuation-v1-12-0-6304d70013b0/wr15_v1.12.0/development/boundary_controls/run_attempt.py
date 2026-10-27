#!/usr/bin/env python3
"""Preserve each strict single-threaded Lean attempt before compiling."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time

WORK = Path('/workspace/scratch/5d9f7f8127b0')
ROOT = WORK / 'wr15_v1.12.0'
RUNTIME = WORK / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
HERE = ROOT / 'development/boundary_controls'
SOURCE = ROOT / 'formal/tests/positive/HilbertBoundaryCases.lean'
COMPILER = RUNTIME / 'toolchain/bin/lean'
ADAPTER = RUNTIME / 'compat/app_path.so'
BUILD = HERE / 'build'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

attempts = [int(p.name.split('_')[1]) for p in HERE.glob('attempt_[0-9]*')]
attempt = HERE / f'attempt_{max(attempts, default=0) + 1:03d}'
attempt.mkdir(parents=True)
snapshot = attempt / SOURCE.name
shutil.copyfile(SOURCE, snapshot)
output = BUILD / 'tests/positive/HilbertBoundaryCases.olean'
output.parent.mkdir(parents=True, exist_ok=True)
deps = sorted((RUNTIME / 'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env = dict(os.environ)
env['LEAN_PATH'] = ':'.join(map(str, [BUILD, ROOT / 'development/coordinates/build', ROOT / 'development/basis_change/build', *deps]))
env['LD_PRELOAD'] = str(ADAPTER)
cmd = [str(COMPILER), '-j1', '-DwarningAsError=true', '-DautoImplicit=false',
       '-o', str(output), str(SOURCE)]
(attempt / 'command.txt').write_text(shlex.join(cmd) + '\n')
(attempt / 'environment.json').write_text(json.dumps({
    'cwd': str(ROOT / 'formal'),
    'LEAN_PATH': env['LEAN_PATH'],
    'LD_PRELOAD': env['LD_PRELOAD'],
    'compiler_sha256': sha(COMPILER),
    'adapter_sha256': sha(ADAPTER),
    'source_sha256': sha(snapshot),
}, indent=2) + '\n')
start = time.monotonic()
with (attempt / 'compiler.log').open('w') as log:
    result = subprocess.run(cmd, cwd=ROOT / 'formal', env=env,
                            stdout=log, stderr=subprocess.STDOUT)
(attempt / 'result.json').write_text(json.dumps({
    'exit_code': result.returncode,
    'elapsed_seconds': round(time.monotonic() - start, 3),
    'source_sha256': sha(snapshot),
    'log_sha256': sha(attempt / 'compiler.log'),
    'output_sha256': sha(output) if result.returncode == 0 else None,
}, indent=2) + '\n')
print(attempt)
print((attempt / 'compiler.log').read_text())
raise SystemExit(result.returncode)
