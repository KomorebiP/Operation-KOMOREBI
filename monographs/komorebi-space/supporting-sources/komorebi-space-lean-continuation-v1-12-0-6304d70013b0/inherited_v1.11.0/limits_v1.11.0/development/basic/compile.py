import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/workspace/scratch/5d9f7f8127b0')
DEV = ROOT / 'limits_v1.11.0/development/basic'
SOURCE = ROOT / (sys.argv[1] if len(sys.argv) > 1 else
                 'limits_v1.11.0/formal/KomorebiSpace/RegularizationLimits.lean')
PORTABLE = ROOT / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
BUILD = DEV / 'build'
BUILD.mkdir(parents=True, exist_ok=True)
(BUILD / 'KomorebiSpace').mkdir(exist_ok=True)
index = 1
while (DEV / f'attempt_{index:03d}').exists():
    index += 1
run = DEV / f'attempt_{index:03d}'
run.mkdir()
data = SOURCE.read_bytes()
(run / SOURCE.name).write_bytes(data)
base = json.loads((ROOT / 'budget_v1.10.0/integration/runs/clean_budget_01/receipt.json').read_text())
env = os.environ.copy()
env['LD_PRELOAD'] = str(PORTABLE / 'compat/app_path.so')
env['LEAN_PATH'] = str(BUILD) + ':' + base['environment']['LEAN_PATH']
cmd = [str(PORTABLE / 'toolchain/bin/lean'), '-j1', '-DwarningAsError=true', '-DautoImplicit=false']
if SOURCE.name == 'RegularizationLimits.lean':
    cmd += ['-o', str(BUILD / 'KomorebiSpace/RegularizationLimits.olean')]
cmd += [str(SOURCE)]
start = time.time()
with (run / 'compile.log').open('w') as log:
    proc = subprocess.run(cmd, cwd=ROOT / 'limits_v1.11.0/formal', env=env,
                          stdout=log, stderr=subprocess.STDOUT)
receipt = {'attempt': index, 'argv': cmd, 'cwd': str(ROOT / 'limits_v1.11.0/formal'),
           'environment': {k: env[k] for k in ['LD_PRELOAD', 'LEAN_PATH']},
           'source_sha256': hashlib.sha256(data).hexdigest(), 'exit_code': proc.returncode,
           'elapsed_seconds': time.time() - start,
           'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source_unchanged': SOURCE.read_bytes() == data}
receipt['log_sha256'] = hashlib.sha256((run / 'compile.log').read_bytes()).hexdigest()
if proc.returncode == 0 and SOURCE.name == 'RegularizationLimits.lean':
    receipt['object_sha256'] = hashlib.sha256((BUILD / 'KomorebiSpace/RegularizationLimits.olean').read_bytes()).hexdigest()
(run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
print((run / 'compile.log').read_text())
sys.exit(proc.returncode)
