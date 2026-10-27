#!/usr/bin/env python3
"""Run the unchanged Block47 verifier and Block48 source under their exact pins."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
FORMAL=ROOT/'evidence/formal'
WORKSPACE=ROOT.parent
PRIVATE=WORKSPACE/'beal_private_formal'
runtime=PRIVATE/'historical_runtime'
mathlib=PRIVATE/'mathlib_4.34'
shim=WORKSPACE/'abc_private_runtime/proc_self_compat.so'
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
project=PRIVATE/out.name;project.mkdir(parents=True,exist_ok=False)
(project/'lean').mkdir();(project/'verification/formal').mkdir(parents=True)
for p in (FORMAL/'historical_source').glob('*.lean'):shutil.copyfile(p,project/'lean'/p.name)
shutil.copyfile(FORMAL/'historical_source/verify_block47.py',project/'verification/formal/verify_block47.py')
env=os.environ.copy();env['LD_PRELOAD']=str(shim);env['PATH']=str(runtime/'toolchain/bin')+os.pathsep+env['PATH']
records=[]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def command(argv,name,timeout=400):
    start=time.monotonic();p=subprocess.run([str(x) for x in argv],cwd=project,env=env,capture_output=True,text=True,timeout=timeout)
    log=out/(name+'.log');log.write_text(p.stdout+p.stderr)
    records.append({'argv':[str(x) for x in argv],'cwd':str(project),'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)})
    return p

before={p.name:sha(p) for p in (FORMAL/'historical_source').glob('*.lean')}
version=command([runtime/'toolchain/bin/lean','--version'],'lean_version')
lake_version=command([runtime/'toolchain/bin/lake','--version'],'lake_version')
assert version.returncode==0 and '4.34.0-rc2' in version.stdout and '6a10ac8c22beadecabdbb0919c2b50214762f91d' in version.stdout
revision=subprocess.check_output(['git','-C',str(mathlib),'rev-parse','HEAD'],text=True).strip();assert revision=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
block47=command([sys.executable,project/'verification/formal/verify_block47.py','--runtime',runtime],'block47_verifier')
report_path=project/'verification/formal/BLOCK47_FORMAL_VERIFICATION.json'
b47=json.loads(report_path.read_text()) if report_path.exists() else {'status':'NO_RESULT'}
if (project/'verification/formal/logs').exists():shutil.copytree(project/'verification/formal/logs',out/'block47_logs')
for name in ['BLOCK47_FORMAL_VERIFICATION.json','declarations.json','Beal47Replay.lean','AxiomAudit.lean']:
    if (project/'verification/formal'/name).exists():shutil.copyfile(project/'verification/formal'/name,out/name)
libs=sorted(p/'.lake/build/lib/lean' for p in (mathlib/'.lake/packages').iterdir() if p.is_dir())
env['LEAN_PATH']=os.pathsep.join(str(p) for p in [project/'lean',*libs,mathlib/'.lake/build/lib/lean',runtime/'toolchain/lib/lean'])
source48=project/'lean/BealBlock48LocalAlgebra.lean'
block48=command([runtime/'toolchain/bin/lean','-j','1','-DwarningAsError=true',source48],'block48_strict_and_axioms')
targets48=re.findall(r'^#print axioms (\S+)',source48.read_text(),re.M)
reports48=re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)",block48.stdout)
dependencies48=sorted(set(x.strip() for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]',block48.stdout) for x in group.split(',') if x.strip()))
unexpected48=sorted(set(dependencies48)-{'propext','Classical.choice','Quot.sound'})
after={p.name:sha(p) for p in (FORMAL/'historical_source').glob('*.lean')}
copied={p.name:sha(p) for p in (project/'lean').glob('*.lean')}
passed=block47.returncode==0 and b47['status']=='PASS_FORMAL_CERTIFICATE_AND_MOD7_ALGEBRA' and block48.returncode==0 and set(targets48)==set(reports48) and len(reports48)==8 and not unexpected48 and before==after==copied
result={'status':'PASS' if passed else 'FAIL','run_kind':'exact original Lean4.34.0-rc2/mathlib commit replay',
 'compiler_version':version.stdout.strip(),'lake_version':lake_version.stdout.strip(),'compiler_sha256':sha(runtime/'toolchain/bin/lean'),
 'mathlib_commit':revision,'mathlib_dependency_manifest_sha256':sha(mathlib/'lake-manifest.json'),
 'source_hashes':before,'source_bytes_unchanged':before==after==copied,'original_block47_verifier_sha256':sha(FORMAL/'historical_source/verify_block47.py'),
 'block47_status':b47['status'],'block47_theorem_count':b47.get('theorem_count'),
 'block47_negative_controls':b47.get('negative_controls'),'block47_axiom_audit':b47.get('axiom_audit'),
 'block47_project_only_kernel_replay':b47.get('kernel_replay'),'block48_public_theorem_count':len(targets48),
 'block48_axiom_reports':reports48,'block48_axiom_dependencies':dependencies48,'block48_unexpected_axiom_dependencies':unexpected48,
 'shim_sha256':sha(shim),'shim_effect':'Only the calling process own /proc/PID/exe readlink uses /proc/self/exe.',
 'records':records,'nonclaims':['Imported mathlib caches are trusted in normal Lean workflow, project-only kernel replay does not recheck every imported dependency.','Generic exclusion theorem assumes complete lane cover, attachment and soundness. No actual arithmetic attachment, geometric Cartier identification, Fontaine-Laffaille dictionary, Block80 primitive, affine target or Beal theorem is formalized.']}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in {'source_hashes','records','block47_negative_controls','block47_axiom_audit','block47_project_only_kernel_replay'}}))
raise SystemExit(0 if passed else 1)
