import datetime, hashlib, json, os, pathlib, shutil, subprocess, sys, time
root = pathlib.Path('/workspace/scratch/6a8ff46cf015')
project = root / 'physics_next/work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
kit = root / 'physics_next/runtime/Komorebi_Portable_Lean_4.34.0-rc2'
out = pathlib.Path(__file__).parent
target = sys.argv[1] if len(sys.argv) > 1 else 'KomorebiPhysics/Relativistic3DCenteredConvergence.lean'
number = len(list(out.glob('run_*.json'))) + 1
env = os.environ.copy()
env['PATH'] = str(kit/'toolchain/bin') + os.pathsep + env.get('PATH','')
env['LD_PRELOAD'] = str(kit/'compat/app_path.so')
argv = ['lake', 'env', 'lean', '-j1', '-DwarningAsError=true', '-o', '.lake/build/lib/lean/KomorebiPhysics/Relativistic3DCenteredConvergence.olean', target]
record = {'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'argv':argv, 'cwd':str(project), 'source':target, 'sha256':hashlib.sha256((project/target).read_bytes()).hexdigest()}
t=time.monotonic()
shutil.copyfile(project/target, out/f'run_{number:03}.lean')
try:
    process=subprocess.run(argv, cwd=project, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180, text=True)
    output, code = process.stdout, process.returncode
except subprocess.TimeoutExpired as e:
    output = str(e.stdout or '') + '\nTIMEOUT\n'
    code=124
record.update(exit_code=code,seconds=time.monotonic()-t)
log=out/f'run_{number:03}.log'
log.write_text(output)
record['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest()
(out/f'run_{number:03}.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2)); print(output)
sys.exit(code)
