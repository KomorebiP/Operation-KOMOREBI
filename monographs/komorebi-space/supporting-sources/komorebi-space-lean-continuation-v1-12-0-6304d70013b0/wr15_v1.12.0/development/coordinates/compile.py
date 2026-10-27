#!/usr/bin/env python3
"""Numbered, immutable development attempts; not an authoritative clean build."""
import hashlib, json, os, pathlib, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUNTIME = ROOT / 'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
BASE = ROOT / 'recovery/v1.11.0/Komorebi_Space_Lean_Continuation_v1.11.0/formal'
FORMAL = HERE.parents[1] / 'formal'
BUILD = HERE / 'build'
BUILD.mkdir(exist_ok=True)
env = os.environ.copy()
env['LD_PRELOAD'] = str(RUNTIME / 'compat/app_path.so')
env['LEAN_PATH'] = ':'.join(map(str, [BUILD, HERE.parent / 'basis_change/build', *sorted((RUNTIME / 'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]))

def compile_one(src, mod, attempt=True):
    if attempt:
        num = 1 + max([int(p.name.split('_')[1]) for p in HERE.glob('attempt_*')], default=0)
        dest = HERE / f'attempt_{num:03d}'
        dest.mkdir()
    else:
        dest = HERE / 'inherited' / mod
        dest.mkdir(parents=True, exist_ok=True)
    text = src.read_text()
    snap = dest / src.name
    snap.write_text(text)
    out = BUILD / (mod.replace('.', '/') + '.olean')
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(RUNTIME / 'toolchain/bin/lean'), '-j1', '-DwarningAsError=true', '-DautoImplicit=false', '-o', str(out), str(src)]
    (dest / 'command.json').write_text(json.dumps(cmd, indent=2) + '\n')
    (dest / 'environment.json').write_text(json.dumps({k:env[k] for k in ['LD_PRELOAD','LEAN_PATH']}, indent=2) + '\n')
    start = time.time()
    result = subprocess.run(cmd, env=env, cwd=src.parent.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (dest / 'compile.log').write_text(result.stdout)
    (dest / 'report.json').write_text(json.dumps({'module':mod, 'source_sha256':hashlib.sha256(text.encode()).hexdigest(), 'exit_code':result.returncode, 'seconds':time.time()-start}, indent=2) + '\n')
    print(f'{dest.relative_to(HERE)} exit={result.returncode}\n{result.stdout}', flush=True)
    return result.returncode

def inherited(mod):
    out = BUILD / (mod.replace('.', '/') + '.olean')
    if out.exists(): return
    src = BASE / (mod.replace('.', '/') + '.lean')
    for line in src.read_text().splitlines():
        if line.startswith('import KomorebiSpace.'):
            for dep in line[7:].split(): inherited(dep)
    if compile_one(src, mod, False): sys.exit(1)

if sys.argv[1] == 'parents':
    inherited('KomorebiSpace.ProtectedRegularizedRepair')
else:
    mod = sys.argv[1]
    src = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv)>2 else FORMAL / (mod.replace('.', '/') + '.lean')
    sys.exit(compile_one(src, mod))
