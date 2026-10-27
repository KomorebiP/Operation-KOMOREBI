#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
KIT = Path(os.environ.get('KOMOREBI_LEAN_KIT','/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2'))
LEAN = KIT/'toolchain/bin/lean'
OUT = ROOT/'verification_v0.11.0'
OUT.mkdir(exist_ok=True)
modules = [
 'WorldNetwork','WorldDual','AmalgamationNerve','WorldMorphism','TransportResidual',
 'AdditiveResidual','LogicalResidual','ResidualDescent','HigherObstructionExample',
 'ResidualExample','ZFCWorldInterface'
]

def sha(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def run(name, argv, expect=0, env=None):
    t=time.time(); p=subprocess.run(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
    (OUT/f'{name}.log').write_text(p.stdout)
    ok=(p.returncode==expect)
    return {'name':name,'argv':[str(x) for x in argv],'exit_code':p.returncode,'expected_exit':expect,'passed':ok,'seconds':time.time()-t,'log':f'verification_v0.11.0/{name}.log'}

lp=[str(ROOT/'.lake/build/lib/lean')]
for d in sorted((KIT/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')):
    if d.is_dir(): lp.append(str(d))
env=os.environ.copy(); env['LEAN_PATH']=':'.join(lp)
checks=[]
checks.append(run('lean_version',[LEAN,'--version'],env=env))

# Source marker scan, comments stripped.
bad=[]
for p in sorted((ROOT/'Komorebi/Multiverse').glob('*.lean')):
    t=p.read_text(); t=re.sub(r'/-.*?-/','',t,flags=re.S); t=re.sub(r'--.*','',t)
    for tok in ['sorry','admit','native_decide','run_tac','implemented_by']:
        if re.search(r'\b'+re.escape(tok)+r'\b',t): bad.append([p.name,tok])
    if re.search(r'(?m)^\s*(axiom|unsafe)\b',t): bad.append([p.name,'axiom/unsafe'])
checks.append({'name':'source_marker_scan','passed':not bad,'bad':bad})

# Exact predecessor Foundation preservation.
old=Path('/mnt/data/Komorebi_KZFC_ResidualReflection_v0.10.0/Komorebi/Foundation')
changed=[]
for p in sorted(old.glob('*.lean')):
    q=ROOT/'Komorebi/Foundation'/p.name
    if not q.exists() or sha(p)!=sha(q): changed.append(p.name)
checks.append({'name':'foundation_preservation','passed':not changed,'file_count':len(list(old.glob('*.lean'))),'changed':changed})

# Clean only branch products, retain verified predecessor/dependency oleans.
branch_build=ROOT/'.lake/build/lib/lean/Komorebi/Multiverse'
if branch_build.exists(): shutil.rmtree(branch_build)
branch_build.mkdir(parents=True,exist_ok=True)
root_olean=ROOT/'.lake/build/lib/lean/Komorebi.olean'
if root_olean.exists(): root_olean.unlink()

for m in modules:
    src=ROOT/'Komorebi/Multiverse'/f'{m}.lean'
    out=branch_build/f'{m}.olean'
    checks.append(run('compile_'+m,[LEAN,'-DwarningAsError=true','-o',out,src],env=env))
checks.append(run('compile_root',[LEAN,'-DwarningAsError=true','-o',root_olean,ROOT/'Komorebi.lean'],env=env))
checks.append(run('axiom_audit',[LEAN,'-DwarningAsError=true',OUT/'AxiomAudit.lean'],env=env))

false_file=OUT/'FalseControl.lean'
false_file.write_text('''import Komorebi.Multiverse.HigherObstructionExample\nopen Komorebi.Multiverse\nexample : TN.JointAmalgamable boundaryTriple := by\n  exact False.elim (boundaryTriple_not_joint (by assumption))\n''')
# This deliberately contains an impossible assumption use and must fail to elaborate.
checks.append(run('false_control',[LEAN,'-DwarningAsError=true',false_file],expect=1,env=env))
placeholder_file=OUT/'PlaceholderControl.lean'
placeholder_file.write_text('''import Komorebi.Multiverse.WorldNetwork\nexample : True := by sorry\n''')
checks.append(run('placeholder_control',[LEAN,'-DwarningAsError=true',placeholder_file],expect=1,env=env))

files=sorted((ROOT/'Komorebi/Multiverse').glob('*.lean'))
theorems=[]
for p in files:
    for m in re.finditer(r'(?m)^theorem\s+([A-Za-z0-9_]+)',p.read_text()): theorems.append(f'{p.name}:{m.group(1)}')

result={
 'status':'PASS' if all(c.get('passed',False) for c in checks) else 'FAIL',
 'generated_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'lean_path':str(LEAN),
 'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
 'verification_mode':'incremental branch rebuild against byte-identical verified v0.10 Foundation sources and pinned dependency cache',
 'module_count':len(files),
 'new_theorem_count':len(theorems),
 'new_source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in files},
 'checks':checks,
 'non_claims':[
  'No forcing or ground-model construction is formalized in Lean.',
  'The abstract triangle obstruction is not itself a Lean proof about actual Cohen extensions.',
  'No new ZFC axiom, consistency-strength theorem, independence theorem, or cohomology theory is claimed.',
  'An arbitrary complete obstruction tower is intentionally shown to be vacuous without extra admissibility structure.'
 ]
}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'status':result['status'],'module_count':result['module_count'],'new_theorem_count':result['new_theorem_count'],'checks':[(c['name'],c['passed'],c.get('exit_code')) for c in checks]},indent=2))
sys.exit(0 if result['status']=='PASS' else 1)
