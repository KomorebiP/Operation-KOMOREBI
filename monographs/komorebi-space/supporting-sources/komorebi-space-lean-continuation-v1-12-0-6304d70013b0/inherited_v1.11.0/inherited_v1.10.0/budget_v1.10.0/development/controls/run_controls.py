"""Immutable local development runs for the budget boundary controls."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / 'budget_v1.10.0/development/controls'
TESTS = ROOT / 'budget_v1.10.0/formal/tests'
RUNTIME = ROOT / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
number = 1
while (DEV / f'attempt_{number:03d}').exists():
    number += 1
run = DEV / f'attempt_{number:03d}'
run.mkdir()
build = run / 'build/KomorebiSpace'
build.mkdir(parents=True)
for source in (ROOT / 'continuation/integration/runs/wr01_wr02_overlay_01/build/KomorebiSpace').glob('*.olean'):
    (build / source.name).symlink_to(source)
dependencies = []
for module, folder in [('BudgetProfile', 'wr03'), ('BudgetProfileGeometry', 'geometry'),
                       ('BudgetDuality', 'wr04'), ('BudgetRobustness', 'wr05')]:
    source = ROOT / f'budget_v1.10.0/development/{folder}/build/KomorebiSpace/{module}.olean'
    dest = build / source.name
    shutil.copy2(source, dest)
    dependencies.append({'path':str(source.relative_to(ROOT)),
        'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
env = os.environ.copy()
env['LD_PRELOAD'] = str(RUNTIME / 'compat/app_path.so')
paths = [build.parent]
paths += sorted((RUNTIME / 'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env['LEAN_PATH'] = ':'.join(map(str, paths))
results = []
for source in sorted(TESTS.glob('*/*.lean')):
    rel = source.relative_to(TESTS)
    snapshot = run / 'sources' / rel
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(source.read_bytes())
    log = run / 'logs' / rel.with_suffix('.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(RUNTIME / 'toolchain/bin/lean'), '-j1', '-DwarningAsError=true',
           '-DautoImplicit=false', str(snapshot)]
    start = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_bytes(proc.stdout)
    record = {'path':str(rel), 'kind':rel.parts[0], 'source_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        'exit_code':proc.returncode, 'elapsed_seconds':time.time()-start, 'command':cmd,
        'log_sha256':hashlib.sha256(proc.stdout).hexdigest(), 'log':str(log.relative_to(ROOT)),
        'source_unchanged':snapshot.read_bytes()==source.read_bytes()}
    results.append(record)
    print(json.dumps({'path':str(rel), 'exit_code':proc.returncode}), flush=True)
    if proc.returncode != 0:
        print(proc.stdout.decode(), flush=True)
receipt = {'attempt':number, 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'dependencies':dependencies, 'environment':{k:env[k] for k in ['LD_PRELOAD','LEAN_PATH']},
    'controls':results}
(run/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
