from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, time

base = Path('/workspace/scratch/6a8ff46cf015/physics_next')
project = base / 'work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
kit = base / 'runtime/Komorebi_Portable_Lean_4.34.0-rc2'
source = project / 'KomorebiPhysics/Relativistic3DCenteredRates.lean'
root = base / 'attempts/rates'
attempt = root / ('attempt_' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
attempt.mkdir()
shutil.copy2(source, attempt / source.name)
obj = project / '.lake/build/lib/lean/KomorebiPhysics/Relativistic3DCenteredRates.olean'
obj.parent.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env['PATH'] = str(kit / 'toolchain/bin') + os.pathsep + env.get('PATH', '')
env['LD_PRELOAD'] = str(kit / 'compat/app_path.so')
for k in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME'):
    env.pop(k, None)
cmd = [str(kit / 'toolchain/bin/lake'), 'env', 'lean', '-j1', '-DwarningAsError=true', '-o', str(obj), str(source)]
start = time.monotonic()
with (attempt/'compile.log').open('w') as f:
    try:
        p = subprocess.run(cmd, cwd=project, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=240)
        rc = p.returncode
        timeout = False
    except subprocess.TimeoutExpired:
        rc = None
        timeout = True
record = {'argv':cmd,'cwd':str(project),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'returncode':rc,'timeout':timeout,'seconds':time.monotonic()-start,
          'log_sha256':hashlib.sha256((attempt/'compile.log').read_bytes()).hexdigest()}
(attempt/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(attempt)
print((attempt/'compile.log').read_text())
print(json.dumps(record))
sys.exit(rc if rc is not None else 124)
