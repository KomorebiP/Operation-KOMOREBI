#!/usr/bin/env python3
"""Explicit 4.19 compatibility check, not the historical 4.34 exact replay."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT/'evidence/formal'
WORKSPACE = ROOT.parent
runtime = WORKSPACE/'abc_private_runtime/lean-4.19.0-linux'
cache = WORKSPACE/'abc_private_runtime/jet_checked_replay'
shim = WORKSPACE/'abc_private_runtime/proc_self_compat.so'
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
project = out/'source_snapshot'
shutil.copytree(FORMAL/'historical_source',project)
env = os.environ.copy()
env['LD_PRELOAD'] = str(shim)
env['PATH'] = str(runtime/'bin')+os.pathsep+env['PATH']
libs = sorted(p/'.lake/build/lib/lean' for p in (cache/'.lake/packages').iterdir() if p.is_dir())
env['LEAN_PATH'] = os.pathsep.join(str(p) for p in [project, *libs, cache/'.lake/build/lib/lean',runtime/'lib/lean'])
records=[]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(argv,name,expected=0):
    started=time.monotonic()
    p=subprocess.run([str(x) for x in argv],cwd=project,env=env,capture_output=True,text=True,timeout=120)
    log=out/(name+'.log');log.write_text(p.stdout+p.stderr)
    r={'argv':[str(x) for x in argv], 'cwd':str(project), 'exit_code':p.returncode,
       'expected_exit_code':expected,'elapsed_seconds':time.monotonic()-started,
       'log':str(log.relative_to(ROOT)), 'log_sha256':sha(log)}
    records.append(r)
    return p

version=command([runtime/'bin/lean','--version'],'lean_version')
assert version.returncode==0 and '4.19.0' in version.stdout and '6caaee842e94' in version.stdout
mathlib=cache/'.lake/packages/mathlib'
rev=subprocess.check_output(['git','-C',str(mathlib),'rev-parse','HEAD'],text=True).strip()
assert rev=='c44e0c8ee63ca166450922a373c7409c5d26b00b'
expected={p.name:sha(p) for p in (FORMAL/'historical_source').glob('*.lean')}
modules=['BealLaneCertificate','BealCorrelationExamples','BealModSevenCartier','BealBlock47','BealBlock48LocalAlgebra']
passed=True
for module in modules:
    p=command([runtime/'bin/lean','-j','1','-DwarningAsError=true','-o',project/(module+'.olean'),project/(module+'.lean')],module)
    if p.returncode:
        passed=False
        break
targets=[]
for module in modules:
    source=(project/(module+'.lean')).read_text()
    namespace='KomorebiBeal.Block48.' if module=='BealBlock48LocalAlgebra' else 'KomorebiBeal.Block47.'
    targets.extend(namespace+m.group(1) for m in re.finditer(r'^theorem\s+(\w+)',source,re.M))
axioms=''
if passed:
    audit=project/'AxiomAudit.lean'
    audit.write_text('import BealBlock47\nimport BealBlock48LocalAlgebra\n'+ '\n'.join('#print axioms '+t for t in targets)+'\n')
    p=command([runtime/'bin/lean','-j','1','-DwarningAsError=true',audit],'axioms')
    axioms=p.stdout
    passed=passed and p.returncode==0
reported=re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)",axioms)
dependencies=sorted(set(x.strip() for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]',axioms) for x in group.split(',') if x.strip()))
unexpected=sorted(set(dependencies)-{'propext','Classical.choice','Quot.sound'})
passed=passed and set(targets)<=set(reported) and not unexpected
result={'status':'PASS' if passed else 'FAIL','source_edition':'byte-identical recovered historical sources',
 'run_kind':'explicit new Lean4.19/mathlib4.19 compatibility check; not exact historical4.34 replay',
 'compiler_version':version.stdout.strip(),'mathlib_commit':rev,'historical_mathlib_commit':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
 'source_hashes':expected,'source_snapshot_hashes':{p.name:sha(p) for p in project.glob('Beal*.lean')},
 'module_count':len(modules),'theorem_targets':targets,'axiom_targets_requested':len(targets),
 'axiom_targets_reported':len(set(reported)), 'standard_axiom_dependencies':dependencies,
 'unexpected_axiom_dependencies':unexpected,'records':records,'shim_sha256':sha(shim),
 'compiler_sha256':sha(runtime/'bin/lean'),'nonclaims':['No claim that the exact historical mathlib4.34 dependency was replayed.','No number theoretic modular attachment, geometric Cartier interpretation, arithmetic affine target or general Beal theorem is established.']}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in {'records','theorem_targets','source_hashes','source_snapshot_hashes'}}))
raise SystemExit(0 if passed else 1)
