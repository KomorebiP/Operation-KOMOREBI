"""Retain immutable, bounded development attempts for individual WR15 controls."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, platform, shutil, subprocess, time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT.parent
parser = argparse.ArgumentParser()
parser.add_argument('fixture')
parser.add_argument('--project-objects', action='append', default=[])
args = parser.parse_args()
source = (ROOT / 'formal/tests' / args.fixture).resolve()
assert source.is_relative_to(ROOT / 'formal/tests') and source.is_file()
runtime_record = json.loads((ROOT / 'recovery/runtime_recovery.json').read_text())
runtime = Path(runtime_record['runtime_root'])
base = ROOT / 'development/controls'
index = 1
while (base / f'attempt_{index:03}').exists(): index += 1
attempt = base / f'attempt_{index:03}'
attempt.mkdir()
copied = attempt / source.name
shutil.copy2(source, copied)
env = os.environ.copy()
env['LD_PRELOAD'] = str(runtime / 'compat/app_path.so')
paths = [str(Path(p).resolve()) for p in args.project_objects]
paths += runtime_record['environment']['LEAN_PATH'].split(':')
env['LEAN_PATH'] = ':'.join(paths)
argv = [str(runtime / 'toolchain/bin/lean'), '-j1', '-DwarningAsError=true',
        '-DautoImplicit=false', str(copied)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(source)
started = datetime.now(timezone.utc).isoformat()
t0 = time.monotonic()
timeout = False
try:
    run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, timeout=120)
    stdout, stderr, code = run.stdout, run.stderr, run.returncode
except subprocess.TimeoutExpired as e:
    stdout, stderr, code = e.stdout or b'', e.stderr or b'', None
    timeout = True
elapsed = time.monotonic() - t0
(attempt/'stdout.txt').write_bytes(stdout)
(attempt/'stderr.txt').write_bytes(stderr)
objects = {}
for p in args.project_objects:
    root = Path(p).resolve()
    objects[str(root)] = {str(f.relative_to(root)):sha(f) for f in sorted(root.rglob('*.olean'))}
receipt = {'base_checkpoint':'KS-v1.11.0-WR08-WR09-WR16-complete', 'fixture':args.fixture,
    'argv':argv, 'cwd':str(ROOT), 'environment':{k:env[k] for k in ['LD_PRELOAD','LEAN_PATH']},
    'compiler_sha256':sha(runtime/'toolchain/bin/lean'), 'adapter_sha256':sha(runtime/'compat/app_path.so'),
    'source_sha256':before, 'source_unchanged':sha(source)==before, 'copied_source_sha256':sha(copied),
    'project_objects_sha256':objects, 'started_utc':started,'elapsed_seconds':elapsed,
    'exit_code':code,'timeout':timeout,'stdout_sha256':sha(attempt/'stdout.txt'),
    'stderr_sha256':sha(attempt/'stderr.txt'), 'classification':'pending actual diagnostic review',
    'scope':'Development fixture execution only; final acceptance requires cumulative replay.'}
(attempt/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
manifest = {'schema_version':1,'claim_id':'WR15-development-control-'+str(index),
    'repository':{'commit':'archive:40a5ddecb526dcb1f60c4475e3648f2b5aa906d2b4b5070f4a8b1c59db4d83d1','dirty':True},
    'command':repr(argv),'environment':{'software':['Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d',platform.python_version()], 'hardware':platform.machine()},
    'mathematics':{'assertion_tested':'Compile one exact fixture and retain its diagnostic for intended-outcome review',
      'coefficient_domain':'Real numbers, exact Lean propositions','conventions':'Column vectors, transpose covectors, actual Hilbert norms',
      'inputs':[args.fixture],'bounds':{'fixture_files':1,'timeout_seconds':120},
      'non_claims':['No universal mathematical conclusion follows from fixture success or rejection alone.']},
    'randomness':{'used':False,'generator':'','seed':None},
    'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':code if code is not None else 'timeout'},
    'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [copied,attempt/'stdout.txt',attempt/'stderr.txt',attempt/'receipt.json']],
    'checks':['Source before/after digest retained','Exact argv, environment, compiler and dependency-object digests retained'],
    'result':'Execution recorded; expected-outcome verdict awaits log inspection',
    'residual_risks':['Lean kernel and pinned caches trusted','Development project objects are not clean-replay evidence','Legacy manifest limits supplemented by receipt source/command bindings']}
(attempt/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'attempt':str(attempt),'fixture':args.fixture,'exit_code':code,'timeout':timeout,'stdout':stdout.decode(errors='replace'),'stderr':stderr.decode(errors='replace')}))
