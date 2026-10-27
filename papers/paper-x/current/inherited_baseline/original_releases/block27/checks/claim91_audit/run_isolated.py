#!/usr/bin/env python3
"""Independent source compilation with frozen Block24 objects as the only PaperX cache."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, time, zipfile
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('/root/.codex/tmp/paperx_block24')
KIT=Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
ARCHIVE=ROOT/'references/PRSC_X_v0.24.0_Checked_Proof_Bundle.zip'
EXPECTED='8bff25880aa4bc30d85a8674a33e99c11dde98e60053e19135515d4eabf68ad5'
OUT=ROOT/'checks/claim91_audit'
WORK=Path('/root/.codex/tmp/paperx_block25_independent_claim91')
NEW=['IrreducibleCharacterRigidity','CofiniteConjugacyCoverage','CompatibleSystemRigidity','CompatibleSystemSeparation','FiniteAvoidanceBoundary','CyclotomicPrimeCoverage','CyclotomicSystemSeparation','CyclotomicFrobeniusPrimes']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,indent=2)+'\n')
a=argparse.ArgumentParser();a.add_argument('modules',nargs='*');a.add_argument('--work',default=str(WORK));a.add_argument('--init',action='store_true');a.add_argument('--axioms',action='store_true');a.add_argument('--edge',action='store_true');args=a.parse_args();WORK=Path(args.work).resolve()
assert sha(ARCHIVE)==EXPECTED
with zipfile.ZipFile(ARCHIVE) as z:
    prefix=z.namelist()[0].split('/')[0]+'/'
    frozen=z.read(prefix+'verification.json')
    assert frozen==(BASE/'verification.json').read_bytes()
    verify=json.loads(frozen)
    assert verify['module_count']==153 and len(verify['modules'])==153
    if args.init:
        assert not WORK.exists(), 'Use a fresh work directory; never inherit new proof objects.'
        (WORK/'PaperX').mkdir(parents=True)
        records=[]
        for m in verify['modules']:
            name=m['module']; src=BASE/'lean/PaperX'/f'{name}.lean';obj=BASE/'build/PaperX'/f'{name}.olean'
            assert sha(src)==m['source_sha256']
            assert sha(obj)==m['olean_sha256']
            assert obj.read_bytes()==z.read(prefix+'build/PaperX/'+f'{name}.olean')
            shutil.copy2(obj,WORK/'PaperX'/obj.name)
            records.append({'module':name,'source_sha256':sha(src),'olean_sha256':sha(obj),'archive_bytes_match':True})
        write(OUT/'BaselineVerification.json',{'archive_sha256':EXPECTED,'verification_sha256':hashlib.sha256(frozen).hexdigest(),'object_count':153,'objects':records})
        (OUT/'FrozenBlock24Verification.json').write_bytes(frozen)
# Construct runtime environment independently; no project build path is admitted.
env=os.environ.copy()
for k in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(k,None)
lean=KIT/'toolchain/bin/lean';env['PATH']=str(KIT/'toolchain/bin')+os.pathsep+env['PATH']
probe=subprocess.run([str(lean),'--version'],env=env,text=True,capture_output=True)
if probe.returncode and 'failed to locate application' in probe.stdout+probe.stderr:
    env['LD_PRELOAD']=str(KIT/'compat/app_path.so')
    probe=subprocess.run([str(lean),'--version'],env=env,text=True,capture_output=True)
assert probe.returncode==0,probe.stderr
assert sha(lean)==verify['lean_sha256']
shared=KIT/'toolchain/lib/lean/libleanshared.so';assert sha(shared)==verify['lean_shared_sha256']
paths=subprocess.check_output([str(KIT/'toolchain/bin/lake'),'env','printenv','LEAN_PATH'],cwd=KIT/'workspace',env=env,text=True).strip()
# Resolve relative Lake search entries to their kit workspace. Never use cwd lookup.
resolved=[str((KIT/'workspace'/p).resolve()) if not Path(p).is_absolute() else p for p in paths.split(os.pathsep) if p]
assert not any('/paperx_' in p for p in resolved),resolved
env['LEAN_PATH']=os.pathsep.join([str(WORK)]+resolved)
write(OUT/'Environment.json',{'lean_version':probe.stdout.strip(),'lean_sha256':sha(lean),'lean_shared_sha256':sha(shared),'mathlib_revision':verify['mathlib_revision'],'lean_path':env['LEAN_PATH'],'project_build_excluded':True,'baseline_object_count':153,'work':str(WORK)})
def run(name,src,out=None):
    command=[str(lean),'-DwarningAsError=true']
    if out is not None:
        assert not out.exists(),f'Refusing to inherit output {out}'
        command+=['-o',str(out)]
    command.append(str(src));start=time.monotonic();p=subprocess.run(command,cwd=ROOT/'lean',env=env,text=True,capture_output=True)
    log=OUT/f'{name}.log';log.write_text(p.stdout+p.stderr)
    record={'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'command':command,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,'olean_sha256':sha(out) if out and out.exists() else None,'log':str(log.relative_to(ROOT))}
    write(OUT/f'{name}.json',record);print(name,p.returncode,flush=True)
    if p.returncode:print(p.stdout+p.stderr,flush=True);raise SystemExit(p.returncode)
for module in args.modules:
    assert module in NEW
    run(module,ROOT/'lean/PaperX'/f'{module}.lean',WORK/'PaperX'/f'{module}.olean')
if args.axioms:
    names=[]
    for module in NEW:
        src=ROOT/'lean/PaperX'/f'{module}.lean'
        for match in re.finditer(r'^(?:@\[[^\]]*\][ \t]*)?(?:noncomputable\s+)?(?:theorem|lemma|def|abbrev)\s+(\w+)',src.read_text(),re.M):
            names.append(f'PaperX.{module}.{match.group(1)}')
    axsrc=OUT/'AllNewAxioms.lean';axsrc.write_text('\n'.join('import PaperX.'+m for m in NEW)+'\n\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
    write(OUT/'NewDeclarations.json',{'count':len(names),'declarations':names})
    run('AllNewAxioms',axsrc)
    log=(OUT/'AllNewAxioms.log').read_text();bad=[]
    for bracket in re.findall(r'depends on axioms: \[([^\]]*)\]',log):
        bad += [x.strip() for x in bracket.split(',') if x.strip() not in ['propext','Classical.choice','Quot.sound']]
    audited=re.findall(r"'([^']+)' (?:depends on axioms:|does not depend on any axioms)",log)
    assert audited==names,(audited,names)
    assert not bad,bad
    write(OUT/'AxiomSummary.json',{'audited_count':len(audited),'declarations':audited,'allowed_axioms':['Classical.choice','Quot.sound','propext'],'unexpected_axioms':bad,'status':'passed'})
if args.edge:run('EdgeApplications',OUT/'EdgeApplications.lean')
