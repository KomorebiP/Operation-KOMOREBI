#!/usr/bin/env python3
"""Replay one authorized Paper III suite on byte-identical temporary inputs.

Never edits the authoritative sources. The visual suite's generated JSON remains
in temporary staging until it is copied into the declared result record.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from datetime import datetime, timezone

parser=argparse.ArgumentParser()
parser.add_argument('--suite',choices=['finite','strengthened','visual'],required=True)
parser.add_argument('--result',required=True)
args=parser.parse_args()
ROOT=Path.cwd().resolve()
result_path=ROOT/args.result
result_path.parent.mkdir(parents=True,exist_ok=True)
CACHE='/workspace/scratch/de82c13900d1/special_work/verification_dependencies'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
if args.suite=='finite':
    folder=ROOT/'source/finite'
    files=sorted(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    suite_root=Path('source/finite')
    entry=suite_root/'VERIFY.sh'
    executable='bash'
elif args.suite=='strengthened':
    suite_root=Path('source/expanded')
    files=[ROOT/suite_root/'verification/verify_strengthened.py',
           ROOT/suite_root/'PSC_Paper_III_Annals_Human_Edition_Strengthened.tex',
           ROOT/suite_root/'PSC_Paper_III_Annals_Human_Edition_Strengthened.bib']
    entry=suite_root/'verification/verify_strengthened.py'
    executable=sys.executable
else:
    suite_root=Path('editable/visual_guide')
    files=[ROOT/suite_root/'checks/verify_examples.py',ROOT/suite_root/'source/models.py']
    entry=suite_root/'checks/verify_examples.py'
    executable=sys.executable
inputs_before={p.relative_to(ROOT).as_posix():sha(p) for p in files}
start_utc=datetime.now(timezone.utc).isoformat();start=time.monotonic()
env=os.environ.copy()
env.pop('PYTHONOPTIMIZE',None)
env['PYTHONPATH']=CACHE
# The requested cache is missing. This intentional entry leaves installed packages available.
env['PYTHONDONTWRITEBYTECODE']='1'
env['TZ']='UTC'
with tempfile.TemporaryDirectory(prefix='paper3-'+args.suite+'-') as tmp:
    staging=Path(tmp)
    for p in files:
        dst=staging/p.relative_to(ROOT)
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dst)
        if sha(dst)!=inputs_before[p.relative_to(ROOT).as_posix()]:
            raise RuntimeError('Temporary copy differs from authoritative input: '+str(p))
    argv=[executable,str(staging/entry)]
    proc=subprocess.run(argv,cwd=staging/suite_root,env=env,text=True,capture_output=True,timeout=100)
    print(proc.stdout,end='')
    if proc.stderr: print(proc.stderr,end='',file=sys.stderr)
    scientific=None
    if args.suite=='visual':
        output=staging/suite_root/'checks/EXACT_CHECKS.json'
        if output.is_file(): scientific=json.loads(output.read_text())
    inputs_after={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    record={
      'suite':args.suite,'started_utc':start_utc,'runtime_seconds':time.monotonic()-start,
      'actual_child_argv':argv,'actual_child_cwd':str(staging/suite_root),
      'regeneration_command':[executable,str(entry)],
      'temporary_inputs_byte_identical':True,'source_inputs_unchanged':inputs_before==inputs_after,
      'authoritative_input_sha256_before':inputs_before,'authoritative_input_sha256_after':inputs_after,
      'child_exit_status':proc.returncode,
      'environment':{'PYTHONPATH':CACHE,'requested_cache_exists':Path(CACHE).is_dir(),
        'PYTHONOPTIMIZE':'removed so assertions remain active','PYTHONDONTWRITEBYTECODE':'1','TZ':'UTC',
        'network':'No script performs network operations. No dependencies fetched.'},
      'stdout':proc.stdout,'stderr':proc.stderr,
      'passed_group_lines':[line for line in proc.stdout.splitlines() if line.startswith('PASS: ')],
      'visual_scientific_result':scientific,
      'fresh_lean_invocation':False,
      'limitations':['Finite release verifier was run without --full.',
        'Historical saved Lean transcript is inspected by the offline verifier. It is not a fresh kernel run.',
        'Strengthened NumPy checks use floating arithmetic, seeded inputs, and explicit tolerances.',
        'Exact visual evidence concerns the displayed finite examples and finite ranges only.']}
    result_path.write_text(json.dumps(record,indent=2)+'\n')
if inputs_before!=inputs_after: raise SystemExit('Source inputs changed during isolated replay.')
raise SystemExit(proc.returncode)
