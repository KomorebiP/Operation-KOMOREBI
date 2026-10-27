#!/usr/bin/env python3
"""Record immutable strong-limit development attempts against accepted dependencies."""
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
paths = [dev/'build']
paths += sorted((runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env = os.environ.copy()
env['LD_PRELOAD'] = str(runtime/'compat/app_path.so')
env['LEAN_PATH'] = ':'.join(map(str, paths))
deps = [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted((dev/'build/KomorebiSpace').glob('*.olean'))]
out = attempt / (source.stem + '.olean')
cmd = [str(runtime/'toolchain/bin/lean'), '-j1', '-DwarningAsError=true',
    '-DautoImplicit=false', '-o', str(out), str(snapshot)]
result = subprocess.run(cmd, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(attempt/'compile.log').write_bytes(result.stdout)
receipt = {'source':str(source.relative_to(root)), 'snapshot':str(snapshot.relative_to(root)),
    'source_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    'command':cmd, 'lean_path':env['LEAN_PATH'], 'ld_preload':env['LD_PRELOAD'],
    'dependencies':deps, 'exit_code':result.returncode,
    'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
if result.returncode == 0:
    receipt['olean_sha256'] = hashlib.sha256(out.read_bytes()).hexdigest()
    target = dev/'build/KomorebiSpace'/out.name
    if target.is_symlink():
        raise RuntimeError('Refusing to replace accepted dependency symlink')
    target.write_bytes(out.read_bytes())
(attempt/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('snapshot','source_sha256','exit_code')}))
print(result.stdout.decode())
sys.exit(result.returncode)
