#!/usr/bin/env python3
"""Repeat the KTG check with validated run provenance, without editing inputs."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT.parent / 'abc_private_runtime'
FORMAL = ROOT / 'evidence/formal'
output = Path(sys.argv[1]).resolve()
output.mkdir(parents=True, exist_ok=True)
source = FORMAL / 'ktg_source'
working = PRIVATE / 'ktg_provenance_working'
if working.exists():
    shutil.rmtree(working)
shutil.copytree(source, working)
runtime = PRIVATE / 'lean-4.34.0-rc2-linux/bin'
shim = PRIVATE / 'proc_self_compat.so'
env = os.environ.copy()
env.update(PATH=str(runtime) + os.pathsep + env['PATH'],
           LEAN_BIN=str(runtime / 'lean'), LAKE_BIN=str(runtime / 'lake'),
           LD_PRELOAD=str(shim))
records = []

def run(argv, cwd, name):
    start = time.monotonic()
    process = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    log = output / (name + '.log')
    log.write_text(process.stdout + process.stderr)
    records.append({'argv': argv, 'cwd': str(cwd), 'exit_code': process.returncode,
                    'elapsed_seconds': round(time.monotonic()-start, 6),
                    'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
    if process.returncode:
        (output/'result.json').write_text(json.dumps({'status':'FAIL', 'records':records},indent=2)+'\n')
        raise SystemExit(process.returncode)
    return process.stdout.strip()

lean_version = run([str(runtime/'lean'), '--version'], working, 'lean_version')
lake_version = run([str(runtime/'lake'), '--version'], working, 'lake_version')
if '4.34.0-rc2' not in lean_version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in lean_version:
    raise SystemExit('Exact compiler pin mismatch')
run([sys.executable, 'verification/verify_block03.py', '--clean'], working, 'verify_block03')
checked = json.loads((working/'verification/block03_final/verification.json').read_text())
shutil.copytree(working/'verification/block03_final', output/'checked', dirs_exist_ok=True)
axiom_source = FORMAL/'KTGAxioms.lean'
shutil.copy2(axiom_source,working/'formalization/lean/KTGAxioms.lean')
axioms = run([str(runtime/'lake'),'env','lean','-DwarningAsError=true','KTGAxioms.lean'], working/'formalization/lean','axioms')
original_hashes = {str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted((source/'formalization/lean').rglob('*.lean'))}
final_hashes = {rel:hashlib.sha256((working/rel).read_bytes()).hexdigest() for rel in original_hashes}
axiom_lines = axioms.splitlines()
result = {'status': 'PASS' if checked['status']=='PASS' and original_hashes==final_hashes else 'FAIL',
          'lean_version':lean_version,'lake_version':lake_version,'lean_source_count':checked['lean_source_count'],
          'source_hashes':original_hashes,'source_bytes_unchanged':original_hashes==final_hashes,
          'axiom_audit_count':len(axiom_lines),'axiom_free_count':sum('does not depend on any axioms' in line for line in axiom_lines),
          'axiom_dependencies':[line for line in axiom_lines if 'depends on axioms:' in line],
          'host_compatibility_shim_sha256':hashlib.sha256(shim.read_bytes()).hexdigest(),
          'host_compatibility_shim_effect':'Only the calling process own /proc/PID/exe readlink uses /proc/self/exe.',
          'records':records,'nonclaims':['No actual IUT objects have been instantiated.','No IUT-specific StepXiEWitnessPreservation inhabitant is supplied.','The Boolean countermodel is not a counterexample to IUT or ABC.']}
(output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_hashes']}))
raise SystemExit(0 if result['status']=='PASS' else 1)
