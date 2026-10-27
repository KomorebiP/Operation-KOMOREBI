"""Independent compiler replay; accepts only explicitly frozen module names."""
from pathlib import Path
import sys, os, json, shutil, subprocess, hashlib, time, fcntl

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'privatechecks' / 'audit_baseline'
KIT = Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
OUT = ROOT / 'privatechecks' / 'audit_replay'
MODULES = sys.argv[1:]
assert MODULES and all(m.isidentifier() for m in MODULES)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

srcdir = OUT/'lean'/'PaperX'
objdir = OUT/'build'/'PaperX'
logdir = OUT/'logs'
for directory in [srcdir, objdir, logdir]:
    directory.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env['PATH'] = str(KIT/'toolchain/bin') + os.pathsep + env['PATH']
lean = str(KIT/'toolchain/bin/lean')
probe = subprocess.run([lean, '--version'], capture_output=True, text=True, env=env)
if probe.returncode and 'failed to locate application' in probe.stdout+probe.stderr:
    env['LD_PRELOAD'] = str(KIT/'compat/app_path.so')
elif probe.returncode:
    raise RuntimeError(probe.stdout+probe.stderr)
lp = subprocess.check_output([str(KIT/'toolchain/bin/lake'), 'env', 'printenv', 'LEAN_PATH'],
    cwd=KIT/'workspace',env=env,text=True).strip()
env['LEAN_PATH'] = os.pathsep.join([str(OUT/'build'), str(BASE/'build'), lp])
frozen=json.loads((ROOT/'evidence/frozen_sources.json').read_text())
(BASE/'build/PaperX').mkdir(parents=True,exist_ok=True)
for row in frozen:
    name=row['module']
    assert digest(ROOT/'lean/PaperX'/f'{name}.lean')==row['source_sha256'], name
    original=ROOT/'build/PaperX'/f'{name}.olean'
    target=BASE/'build/PaperX'/f'{name}.olean'
    assert digest(original)==row['olean_sha256'], name
    if not target.exists(): shutil.copy2(original,target)
    assert digest(target)==row['olean_sha256'], name
    audit_target=OUT/'build/PaperX'/f'{name}.olean'
    if not audit_target.exists(): shutil.copy2(target,audit_target)
    assert digest(audit_target)==row['olean_sha256'], name
records_path = OUT/'compilation.json'
for module in MODULES:
    original = ROOT/'lean'/'PaperX'/f'{module}.lean'
    source = srcdir/f'{module}.lean'
    shutil.copy2(original, source)
    snapshot = digest(source)
    obj = objdir/f'{module}.olean'
    start = time.monotonic()
    cmd = [lean, '-DwarningAsError=true', '-o', str(obj), str(source)]
    logpath=logdir/f'{module}.log'
    if logpath.exists():
        stamp=time.time_ns(); shutil.copy2(logpath,logdir/f'{module}.prior.{stamp}.log')
    with logpath.open('w') as log:
        p = subprocess.run(cmd,cwd=OUT/'lean',env=env,stdout=log,stderr=subprocess.STDOUT)
    record = {'module':module,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,
        'source_sha256':snapshot,'source_unchanged':digest(original)==snapshot,'command':cmd}
    if p.returncode == 0:
        record['olean_sha256'] = digest(obj)
        authorobj = ROOT/'build'/'PaperX'/f'{module}.olean'
        if authorobj.exists():
            record['matches_author_olean'] = digest(authorobj)==digest(obj)
    (logdir/f'{module}.result.json').write_text(json.dumps(record,indent=2)+'\n')
    with (OUT/'compilation.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        records = json.loads(records_path.read_text()) if records_path.exists() else []
        records.append(record)
        tmp=records_path.with_suffix('.tmp'); tmp.write_text(json.dumps(records,indent=2)+'\n'); tmp.replace(records_path)
    print(json.dumps(record),flush=True)
    if p.returncode:
        raise SystemExit(p.returncode)
