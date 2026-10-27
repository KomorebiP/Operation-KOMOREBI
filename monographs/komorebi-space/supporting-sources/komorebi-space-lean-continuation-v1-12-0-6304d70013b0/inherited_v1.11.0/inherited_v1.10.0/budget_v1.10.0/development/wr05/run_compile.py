#!/usr/bin/env python3
"""Compile one immutable WR05 development snapshot against pinned dependencies."""
from pathlib import Path
import os, sys, json, hashlib, subprocess, datetime
root = Path(__file__).resolve().parents[3]
dev = Path(__file__).resolve().parent
source = Path(sys.argv[1]).resolve()
label = sys.argv[2]
attempt = dev / 'attempts' / label
attempt.mkdir(parents=True, exist_ok=False)
snapshot = attempt / source.name
snapshot.write_bytes(source.read_bytes())
runtime = root / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
paths = [dev/'build', root/'budget_v1.10.0/development/wr04/build',
    root/'budget_v1.10.0/development/wr03/build',
    root/'continuation/integration/runs/wr01_wr02_overlay_01/build']
paths += sorted((runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env = os.environ.copy()
env['LD_PRELOAD'] = str(runtime/'compat/app_path.so')
env['LEAN_PATH'] = ':'.join(map(str, paths))
deps = []
for module, directory in [('BudgetProfile', paths[2]), ('BudgetDuality', paths[1])]:
    q = directory/'KomorebiSpace'/f'{module}.olean'
    if q.exists():
        deps.append({'path':str(q.relative_to(root)), 'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
out = attempt / (source.stem + '.olean')
cmd = [str(runtime/'toolchain/bin/lean'), '-j1', '-DwarningAsError=true',
    '-DautoImplicit=false', '-o', str(out), str(snapshot)]
result = subprocess.run(cmd, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(attempt/'compile.log').write_bytes(result.stdout)
receipt = {'source':str(source.relative_to(root)), 'snapshot':str(snapshot.relative_to(root)),
    'source_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    'command':cmd, 'lean_path':env['LEAN_PATH'], 'dependencies':deps, 'exit_code':result.returncode,
    'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(attempt/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('snapshot','source_sha256','exit_code')}))
print(result.stdout.decode())
sys.exit(result.returncode)
