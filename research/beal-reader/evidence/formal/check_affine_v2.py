#!/usr/bin/env python3
"""Fresh strict compilation of the ReaderAffine source under Lean4.19; no extra checker binary available."""
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
project = WORKSPACE/'beal_private_formal'/out.name
project.mkdir(parents=True, exist_ok=False)
source = FORMAL/'BealAffine.lean'
shutil.copyfile(source,project/'BealAffine.lean')
env = os.environ.copy()
env['LD_PRELOAD'] = str(shim)
env['PATH'] = str(runtime/'bin')+os.pathsep+env['PATH']
libs = sorted(p/'.lake/build/lib/lean' for p in (cache/'.lake/packages').iterdir() if p.is_dir())
env['LEAN_PATH'] = os.pathsep.join(str(p) for p in [project, *libs, cache/'.lake/build/lib/lean',runtime/'lib/lean'])
records=[]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(argv,name):
    started=time.monotonic()
    p=subprocess.run([str(x) for x in argv],cwd=project,env=env,capture_output=True,text=True,timeout=120)
    log=out/(name+'.log');log.write_text(p.stdout+p.stderr)
    r={'argv':[str(x) for x in argv], 'cwd':str(project), 'exit_code':p.returncode,
       'elapsed_seconds':time.monotonic()-started,'log':str(log.relative_to(ROOT)), 'log_sha256':sha(log)}
    records.append(r)
    if p.returncode:
        (out/'result.json').write_text(json.dumps({'status':'FAIL','records':records},indent=2)+'\n')
        raise SystemExit(p.returncode)
    return p

version=command([runtime/'bin/lean','--version'],'lean_version')
assert '4.19.0' in version.stdout and '6caaee842e94' in version.stdout
rev=subprocess.check_output(['git','-C',str(cache/'.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
assert rev=='c44e0c8ee63ca166450922a373c7409c5d26b00b'
before=sha(source)
compile=command([runtime/'bin/lean','-j','1','-DwarningAsError=true','-o',project/'BealAffine.olean',project/'BealAffine.lean'],'strict_compile_and_axioms')
# Lean4.19 official distribution does not include the optional leanchecker executable.
# Successful elaboration still checks the produced proofs with Lean's kernel.
targets=re.findall(r'^#print axioms (\S+)',source.read_text(),re.M)
reported=re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)",compile.stdout)
dependencies=sorted(set(x.strip() for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]',compile.stdout) for x in group.split(',') if x.strip()))
unexpected=sorted(set(dependencies)-{'propext','Classical.choice','Quot.sound'})
# Nested Lean comments are removed rather than trusting word hits in documentation.
text=source.read_text();code=[];depth=0;i=0
while i<len(text):
    if text.startswith('/-',i):depth+=1;i+=2
    elif depth and text.startswith('-/',i):depth-=1;i+=2
    elif depth:i+=1
    elif text.startswith('--',i):
        i=text.find('\n',i)
        if i<0:break
    else:code.append(text[i]);i+=1
forbidden=re.findall(r'\b(?:sorry|admit|unsafe|native_decide)\b|^\s*axiom\b',''.join(code),re.M)
passed=set(targets)==set(reported) and len(targets)==len(reported)==11 and not forbidden and not unexpected and sha(source)==before and sha(project/'BealAffine.lean')==before
result={'status':'PASS' if passed else 'FAIL','source_sha256':before,'compiled_source_sha256':sha(project/'BealAffine.lean'),
 'source_bytes_unchanged':sha(source)==before,'module_count':1,'public_theorem_count':11,'axiom_targets':targets,
 'axiom_reports':reported,'axiom_dependencies':dependencies,'unexpected_axiom_dependencies':unexpected,
 'forbidden_token_hits':forbidden,'compiler_version':version.stdout.strip(),'compiler_sha256':sha(runtime/'bin/lean'),
 'mathlib_commit':rev,'dependency_manifest_sha256':sha(cache/'lake-manifest.json'),'shim_sha256':sha(shim),
 'shim_effect':'Only the calling process own /proc/PID/exe readlink uses /proc/self/exe.',
 'compiled_olean_sha256':sha(project/'BealAffine.olean'),'kernel_replay':'No extra leanchecker run; strict source elaboration kernel-checks generated proofs and imports trusted pinned dependency oleans.','records':records,
 'nonclaims':['No continuous Galois cochain or finite-S Poitou-Tate theorem is encoded.','No actual 15x10 matrix or full left-null basis is encoded; complete_null_test assumes kerN=rangeA explicitly.','No arithmetic target, primitive realization, higher lifting, Frey attachment, or general Beal nonexistence theorem is established.']}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in {'records','axiom_targets','axiom_reports'}}))
raise SystemExit(0 if passed else 1)
