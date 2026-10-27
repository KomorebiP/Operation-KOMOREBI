#!/usr/bin/env python3
"""Compile the unchanged original ABCJet module under its exact original pin."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT/'evidence/formal'
PRIVATE = ROOT.parent/'abc_private_runtime'
output = Path(sys.argv[1]).resolve()
output.mkdir(parents=True,exist_ok=True)
project = PRIVATE/'jet_replay'
runtime = PRIVATE/'lean-4.19.0-linux/bin'
shim = PRIVATE/'proc_self_compat.so'
env = os.environ.copy()
env.update(PATH=str(runtime)+os.pathsep+env['PATH'],LD_PRELOAD=str(shim),
           MATHLIB_CACHE_DIR=str(PRIVATE/'mathlib_cache'))
records = []

def run(argv,name):
    start = time.monotonic()
    process = subprocess.run(argv,cwd=project,env=env,capture_output=True,text=True)
    log = output/(name+'.log');log.write_text(process.stdout+process.stderr)
    records.append({'argv':argv,'cwd':str(project),'exit_code':process.returncode,
                    'elapsed_seconds':round(time.monotonic()-start,6),
                    'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
    if process.returncode:
        (output/'result.json').write_text(json.dumps({'status':'FAIL','records':records},indent=2)+'\n')
        raise SystemExit(process.returncode)
    return process.stdout.strip()

lean_version = run([str(runtime/'lean'),'--version'],'lean_version')
lake_version = run([str(runtime/'lake'),'--version'],'lake_version')
if '4.19.0' not in lean_version or '6caaee842e94' not in lean_version:
    raise SystemExit('Exact ABCJet compiler pin mismatch')
inputs = ['ABCJet.lean','lean-toolchain','lakefile.toml']
expected = {name:hashlib.sha256((FORMAL/'jet_source'/name).read_bytes()).hexdigest() for name in inputs}
before = {name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in inputs}
if before != expected:
    raise SystemExit('ABCJet original source pin mismatch')
run([str(runtime/'lake'),'build'],'lake_build')
run([str(runtime/'lake'),'env','lean','-DwarningAsError=true','ABCJet.lean'],'direct_elaboration')
axiom_source = FORMAL/'ABCJetAxioms.lean'
(project/'ABCJetAxioms.lean').write_bytes(axiom_source.read_bytes())
axioms = run([str(runtime/'lake'),'env','lean','-DwarningAsError=true','ABCJetAxioms.lean'],'axioms')
after = {name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in inputs}
spec = importlib.util.spec_from_file_location('ktg_original_verifier',FORMAL/'ktg_source/verification/verify_block03.py')
module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
stripped = module.strip_lean_comments((project/'ABCJet.lean').read_text())
forbidden = sorted(set(m.group(0).strip() for m in re.finditer(r'\b(?:sorry|admit|unsafe)\b|^\s*axiom\b',stripped,re.MULTILINE)))
dependencies = sorted(set(axiom for group in re.findall(r'depends on axioms: \[([^\]]*)\]',axioms) for axiom in group.split(', ')))
unexpected = sorted(set(dependencies)-{'propext','Quot.sound','Classical.choice'})
lines = axioms.splitlines()
result = {'status':'PASS' if before==after and not forbidden and not unexpected and len(lines)==7 else 'FAIL',
          'lean_version':lean_version,'lake_version':lake_version,'original_module_count':1,
          'named_theorem_count':7,'axiom_audit_count':len(lines),'axiom_dependencies':dependencies,
          'unexpected_axiom_dependencies':unexpected,'forbidden_token_hits':forbidden,
          'source_hashes':before,'source_bytes_unchanged':before==after,
          'dependency_manifest_sha256':hashlib.sha256((project/'lake-manifest.json').read_bytes()).hexdigest(),
          'host_compatibility_shim_sha256':hashlib.sha256(shim.read_bytes()).hexdigest(),
          'host_compatibility_shim_effect':'Only the calling process own /proc/PID/exe readlink uses /proc/self/exe.',
          'records':records,'nonclaims':['Does not formalize the infinite polylogarithm series or p-adic convergence.','Does not formalize general Hankel determinants or valuation minimality.','Does not establish the global arithmetic witness or ABC bridge.']}
(output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_hashes']}))
raise SystemExit(0 if result['status']=='PASS' else 1)
