import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/workspace/scratch/5d9f7f8127b0')
DEV = ROOT / 'budget_v1.10.0/development/geometry'
SOURCE = ROOT / 'budget_v1.10.0/formal/KomorebiSpace/BudgetProfileGeometry.lean'
PORTABLE = ROOT / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
BUILD = DEV / 'build'
BUILD.mkdir(parents=True, exist_ok=True)
(BUILD / 'KomorebiSpace').mkdir(exist_ok=True)
index = 1
while (DEV / f'attempt_{index:03d}').exists():
    index += 1
run = DEV / f'attempt_{index:03d}'
run.mkdir()
for base_file in (ROOT / 'budget_v1.10.0/development/wr03/build/KomorebiSpace').iterdir():
    target = BUILD / 'KomorebiSpace' / base_file.name
    if not target.exists():
        target.symlink_to(base_file.resolve())
data = SOURCE.read_bytes()
(run / SOURCE.name).write_bytes(data)
base = json.loads((ROOT / 'continuation/integration/runs/wr01_wr02_overlay_01/receipt.json').read_text())
env = os.environ.copy()
env['LD_PRELOAD'] = str(PORTABLE / 'compat/app_path.so')
env['LEAN_PATH'] = str(BUILD) + ':' + base['environment']['LEAN_PATH']
cmd = [str(PORTABLE / 'toolchain/bin/lean'), '-j1', '-DwarningAsError=true', '-DautoImplicit=false',
       '-o', str(BUILD / 'KomorebiSpace/BudgetProfileGeometry.olean'), str(SOURCE)]
start = time.time()
with (run / 'compile.log').open('w') as log:
    proc = subprocess.run(cmd, cwd=ROOT / 'budget_v1.10.0/formal', env=env,
                          stdout=log, stderr=subprocess.STDOUT)
receipt = {'attempt': index, 'argv': cmd, 'cwd': str(ROOT / 'budget_v1.10.0/formal'),
           'environment': {k: env[k] for k in ['LD_PRELOAD', 'LEAN_PATH']},
           'source_sha256': hashlib.sha256(data).hexdigest(), 'exit_code': proc.returncode,
           'elapsed_seconds': time.time() - start,
           'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source_unchanged': SOURCE.read_bytes() == data}
receipt['log_sha256'] = hashlib.sha256((run / 'compile.log').read_bytes()).hexdigest()
if proc.returncode == 0:
    receipt['object_sha256'] = hashlib.sha256((BUILD / 'KomorebiSpace/BudgetProfileGeometry.olean').read_bytes()).hexdigest()
(run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
print((run / 'compile.log').read_text())
sys.exit(proc.returncode)
