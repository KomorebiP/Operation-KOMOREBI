from pathlib import Path
import datetime, hashlib, json, os, subprocess, time

workspace = Path('/workspace/scratch/6a8ff46cf015')
project = workspace / 'physics_next/work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
kit = workspace / 'physics_next/runtime/Komorebi_Portable_Lean_4.34.0-rc2'
here = Path(__file__).resolve().parent
source = project / 'KomorebiPhysics/Relativistic3DModalPerturbation.lean'
attempt = here / ('attempt' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
attempt.mkdir()
raw = source.read_bytes()
(attempt / source.name).write_bytes(raw)
env = os.environ.copy()
env['PATH'] = str(kit/'toolchain/bin') + os.pathsep + env.get('PATH', '')
env['LD_PRELOAD'] = str(kit/'compat/app_path.so')
command = [str(kit/'toolchain/bin/lake'), 'env', 'lean', '-j1', '-DwarningAsError=true', '-o', '.lake/build/lib/lean/KomorebiPhysics/Relativistic3DModalPerturbation.olean', str(source.relative_to(project))]
started = time.monotonic()
with (attempt / 'compile.log').open('w') as log:
    result = subprocess.run(command, cwd=project, env=env, stdout=log, stderr=subprocess.STDOUT)
record = {'argv': command, 'cwd': str(project), 'source_sha256': hashlib.sha256(raw).hexdigest(), 'returncode': result.returncode, 'seconds': time.monotonic()-started, 'log_sha256': hashlib.sha256((attempt/'compile.log').read_bytes()).hexdigest()}
(attempt / 'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
print(str(attempt))
print((attempt/'compile.log').read_text())
raise SystemExit(result.returncode)
