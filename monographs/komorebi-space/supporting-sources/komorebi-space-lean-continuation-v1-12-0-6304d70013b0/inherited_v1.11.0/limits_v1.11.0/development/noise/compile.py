import datetime, hashlib, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path('/workspace/scratch/5d9f7f8127b0')
DEV = ROOT / 'limits_v1.11.0/development/noise'
FORMAL = ROOT / 'limits_v1.11.0/formal'
SOURCE = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'limits_v1.11.0/formal/KomorebiSpace/RegularizationNoiseLimits.lean')
RUNTIME = ROOT / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
BASE = ROOT / 'budget_v1.10.0/integration/runs/clean_budget_01'
BUILD = DEV / 'build'
BUILD.mkdir(parents=True, exist_ok=True)
for p in sorted((BASE / 'build').rglob('*.olean')):
    q = BUILD / p.relative_to(BASE / 'build')
    q.parent.mkdir(parents=True, exist_ok=True)
    if not q.exists(): q.symlink_to(p)
for pair in sys.argv[2:]:
    name, path = pair.split('=', 1)
    q = BUILD / 'KomorebiSpace' / (name + '.olean')
    if q.is_symlink(): q.unlink()
    if not q.exists(): q.symlink_to(ROOT / path)
n = 1
while (DEV / f'attempt_{n:03d}').exists(): n += 1
out = DEV / f'attempt_{n:03d}'
out.mkdir()
data = SOURCE.read_bytes()
(out / SOURCE.name).write_bytes(data)
env = os.environ.copy()
env['LD_PRELOAD'] = str(RUNTIME / 'compat/app_path.so')
paths = [BUILD] + sorted((RUNTIME / 'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env['LEAN_PATH'] = ':'.join(map(str, paths))
obj = BUILD / 'KomorebiSpace' / (SOURCE.stem + '.olean')
if obj.is_symlink(): obj.unlink()
cmd = [str(RUNTIME/'toolchain/bin/lean'), '-j1', '-DwarningAsError=true', '-DautoImplicit=false', '-o', str(obj), str(SOURCE)]
deps = {str(p.relative_to(BUILD)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(BUILD.rglob('*.olean')) if p != obj}
start = time.time()
with (out/'compile.log').open('w') as log:
    proc = subprocess.run(cmd, cwd=FORMAL, env=env, stdout=log, stderr=subprocess.STDOUT)
receipt = {'attempt': n, 'argv': cmd, 'cwd': str(FORMAL), 'environment': {k:env[k] for k in ['LD_PRELOAD','LEAN_PATH']}, 'source_sha256': hashlib.sha256(data).hexdigest(), 'dependencies':deps, 'exit_code': proc.returncode, 'elapsed_seconds': time.time()-start, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source_unchanged': SOURCE.read_bytes()==data, 'log_sha256':hashlib.sha256((out/'compile.log').read_bytes()).hexdigest()}
if proc.returncode == 0: receipt['object_sha256'] = hashlib.sha256(obj.read_bytes()).hexdigest()
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['dependencies','environment']},indent=2))
print((out/'compile.log').read_text())
sys.exit(proc.returncode)
