#!/usr/bin/env python3
"""Strict development control compilation with immutable inputs and provenance."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, time
ROOT = Path('/workspace/scratch/5d9f7f8127b0')
DEV = ROOT / 'limits_v1.11.0/development/controls'
BUILD = DEV / 'build'
(BASE := ROOT / 'budget_v1.10.0/integration/runs/clean_budget_01/build')
RUNTIME = ROOT / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
BUILD.mkdir(exist_ok=True)
for p in sorted(BASE.rglob('*.olean')):
    q = BUILD / p.relative_to(BASE)
    q.parent.mkdir(parents=True, exist_ok=True)
    if not q.exists(): q.symlink_to(p)
for section in ['basic', 'strong', 'noise']:
    for p in sorted((DEV.parent / section / 'build/KomorebiSpace').glob('*.olean')):
        q = BUILD / 'KomorebiSpace' / p.name
        if not q.is_symlink(): shutil.copyfile(p, q)
for raw in sys.argv[1:]:
    source = (ROOT / raw).resolve()
    i = 1
    while (DEV / f'attempt_{i:03d}').exists(): i += 1
    run = DEV / f'attempt_{i:03d}'
    run.mkdir()
    snapshot = run / source.name
    snapshot.write_bytes(source.read_bytes())
    env = os.environ.copy()
    env['LD_PRELOAD'] = str(RUNTIME / 'compat/app_path.so')
    paths = [BUILD] + sorted((RUNTIME / 'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
    env['LEAN_PATH'] = ':'.join(map(str, paths))
    deps = {str(p.relative_to(BUILD)): sha(p) for p in sorted(BUILD.rglob('*.olean'))}
    cmd = [str(RUNTIME / 'toolchain/bin/lean'), '-j1', '-DwarningAsError=true', '-DautoImplicit=false', str(snapshot)]
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (run / 'compile.log').write_bytes(result.stdout)
    receipt = {'source': str(source.relative_to(ROOT)), 'source_sha256': sha(snapshot),
        'source_unchanged': source.read_bytes() == snapshot.read_bytes(), 'command': cmd,
        'cwd': str(ROOT), 'environment': {k: env[k] for k in ['LD_PRELOAD', 'LEAN_PATH']},
        'dependency_olean_sha256': deps, 'exit_code': result.returncode,
        'log_sha256': sha(run / 'compile.log'), 'elapsed_seconds': time.monotonic()-start,
        'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (run / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k: receipt[k] for k in ['source','source_sha256','exit_code','elapsed_seconds']}), flush=True)
    print(result.stdout.decode(), flush=True)
