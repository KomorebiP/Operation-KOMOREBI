#!/usr/bin/env python3
"""Immutable per-attempt WR04 compiler record; no shared-state mutations."""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time
root = pathlib.Path(__file__).resolve().parents[3]
dev = root / 'budget_v1.10.0/development/wr04'
src = pathlib.Path(sys.argv[1]).resolve()
attempts = dev / 'attempts'
attempts.mkdir(parents=True, exist_ok=True)
count = len(list(attempts.glob('[0-9][0-9][0-9]')))+1
out = attempts / f'{count:03d}'
out.mkdir()
snapshot = out / src.name
shutil.copy2(src, snapshot)
kit = root / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
env = os.environ.copy()
env['LD_PRELOAD'] = str(kit/'compat/app_path.so')
paths = [dev/'build', root/'budget_v1.10.0/development/wr03/build', root/'continuation/integration/runs/wr01_wr02_overlay_01/build']
paths.extend(sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')))
env['LEAN_PATH'] = ':'.join(map(str, paths))
build = dev/'build/KomorebiSpace'
build.mkdir(parents=True, exist_ok=True)
for dependency in (root/'budget_v1.10.0/development/wr03/build/KomorebiSpace').glob('*.olean'):
    dest = build/dependency.name
    if not dest.exists() and not dest.is_symlink():
        dest.symlink_to(dependency)
cmd = [str(kit/'toolchain/bin/lean'), '-j1', '-DwarningAsError=true', '-DautoImplicit=false', '-o', str(build/(src.stem+'.olean')), str(src)]
start = time.time()
proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
(out/'compiler.log').write_text(proc.stdout)
receipt = {'attempt': count, 'source': str(src.relative_to(root)), 'source_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(), 'command': cmd, 'lean_path': env['LEAN_PATH'], 'exit_code': proc.returncode, 'elapsed_seconds': round(time.time()-start,3), 'log_sha256': hashlib.sha256((out/'compiler.log').read_bytes()).hexdigest()}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'Attempt {count:03d}: exit {proc.returncode}; {receipt["elapsed_seconds"]} seconds')
print(proc.stdout)
sys.exit(proc.returncode)
