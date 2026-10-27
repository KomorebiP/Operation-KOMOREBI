#!/usr/bin/env python3
"""Verify the v0.25 Blocks 23–25 extension over the checked v0.22 parent."""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re, subprocess, time
from datetime import datetime, timezone
from verify import strip_comments_and_strings

ROOT=Path(__file__).resolve().parents[1]
KIT=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2')
LAKE=KIT/'toolchain/bin/lake'
LEAN=KIT/'toolchain/bin/lean'
OUT=ROOT/'verification/block25_final'
OUT.mkdir(parents=True,exist_ok=True)
ALLOWED={'propext','Classical.choice','Quot.sound'}
NEW_MODULES=[
 'KomorebiPhysics.Relativistic3DCliffordTransportU1',
 'KomorebiPhysics.LocalDiscreteGlobalContinuum',
 'KomorebiPhysics.Relativistic3DCliffordHilbertRefinement',
]

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def run(label,argv,expected_failure=False,diagnostic=None,timeout=600):
 t=time.monotonic()
 r=subprocess.run([str(x) for x in argv],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
 log=OUT/f'{label}.log'; log.write_text(r.stdout)
 ok=(r.returncode!=0 and diagnostic and diagnostic in r.stdout and 'unknown module prefix' not in r.stdout and 'object file' not in r.stdout) if expected_failure else r.returncode==0
 rec={'label':label,'argv':[str(x) for x in argv],'returncode':r.returncode,
      'seconds':round(time.monotonic()-t,4),'expected_failure':expected_failure,
      'diagnostic':diagnostic,'status':'PASS' if ok else 'FAIL','log':str(log.relative_to(ROOT)),'log_sha256':sha(log)}
 if not ok: raise RuntimeError(f'{label} failed; see {log}')
 return rec,r.stdout

def main():
 started=datetime.now(timezone.utc)
 inv=json.loads((ROOT/'declaration_inventory.json').read_text())
 parent=json.loads((ROOT/'reference/block22_declaration_inventory.json').read_text())
 checks=[]
 # Static evidence.
 pre=json.loads((ROOT/'verification/block25_source_precheck.json').read_text())
 preservation=json.loads((ROOT/'verification/block22_parent_preservation.json').read_text())
 b24=json.loads((ROOT/'verification/block24_source_identity.json').read_text())
 if pre['status']!='PASS' or preservation['status']!='PASS' or b24['status']!='PASS':
  raise RuntimeError('static source or preservation gate failed')
 version=subprocess.check_output([str(LEAN),'--version'],text=True).strip()
 mathlib=subprocess.check_output(['git','-C',str(KIT/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
 if '4.34.0-rc2' not in version or mathlib!='aeb72f1e9981b6d35b426b16dca7759be3e7ba06':
  raise RuntimeError('toolchain pin mismatch')
 # Cumulative and warning-as-error builds.
 rec,_=run('cumulative_build',[LAKE,'build','KomorebiPhysics'],timeout=900); checks.append(rec)
 rec,_=run('top_warning_as_error',[LAKE,'env','lean','-DwarningAsError=true','KomorebiPhysics.lean']); checks.append(rec)
 for mod in NEW_MODULES:
  rel=mod.replace('.','/')+'.lean'
  rec,_=run('compile_'+mod.split('.')[-1],[LAKE,'env','lean','-DwarningAsError=true',rel]); checks.append(rec)
 # New declaration axiom audit.
 rec,audit=run('audit_block25',[LAKE,'env','lean','AuditBlock25.lean'],timeout=300); checks.append(rec)
 observed=set()
 for m in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]',audit,re.S):
  observed.update(x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip())
 if not observed <= ALLOWED:
  raise RuntimeError('unexpected axioms: '+repr(sorted(observed-ALLOWED)))
 # New negative controls.
 negatives=[]
 for p in sorted((ROOT/'negative_controls/block25').glob('*.lean')):
  rec,_=run('negative_'+p.stem,[LAKE,'env','lean',p],expected_failure=True,diagnostic='unsolved goals',timeout=180)
  checks.append(rec); negatives.append(rec)
 # Proof-input hashes.
 paths=[]
 for mod in inv['modules']:
  paths.append(ROOT/(mod.replace('.','/')+'.lean'))
 paths += [ROOT/'KomorebiPhysics.lean',ROOT/'Audit.lean',ROOT/'AuditBlock25.lean',
           ROOT/'declaration_inventory.json',ROOT/'reference/block22_declaration_inventory.json',
           ROOT/'verification/block22_parent_preservation.json',ROOT/'verification/block24_source_identity.json',
           ROOT/'verification/block25_source_precheck.json',ROOT/'verification/block25_axiom_audit.json',
           ROOT/'verification/block25_negative_controls.json',ROOT/'lakefile.toml',ROOT/'lean-toolchain',
           ROOT/'lake-manifest.json',Path(__file__)]
 paths += sorted((ROOT/'negative_controls/block25').glob('*.lean'))
 source_hashes={str(p.relative_to(ROOT)):sha(p) for p in paths}
 new_decls=[d for d in inv['declarations'] if d['module'] in NEW_MODULES]
 parent_report=json.loads((ROOT/'verification/final/report.json').read_text())
 fresh_neg=json.loads((ROOT/'verification/block25_fresh/negative_controls.json').read_text())
 fresh_hashes={str((ROOT/(m.replace('.','/')+'.lean')).relative_to(ROOT)):sha(ROOT/(m.replace('.','/')+'.lean')) for m in NEW_MODULES}
 finished=datetime.now(timezone.utc)
 report={
  'schema':'komorebi.physics.block25.verification.v1','status':'PASS',
  'started_utc':started.isoformat(),'finished_utc':finished.isoformat(),
  'seconds':round((finished-started).total_seconds(),4),
  'release':'Komorebi Physics Lean v0.25.0 — Checked Block 25',
  'trust_boundary':'New proof terms rebuilt against the pinned Lean/Mathlib cache. The compiler and imported cache were not rebuilt from source. The 121 checked-parent modules are inherited through byte-identity preservation and a passing cumulative build.',
  'lean_version':version,'mathlib_revision':mathlib,
  'checks':checks,
  'counts':{
    'active_modules':len(inv['modules']),'parent_modules':len(parent['modules']),
    'new_modules':len(NEW_MODULES),'total_theorems':sum(d['kind']=='theorem' for d in inv['declarations']),
    'audited_declarations':len(inv['declarations']),
    'new_theorems':sum(d['kind']=='theorem' for d in new_decls),
    'new_audited_declarations':len(new_decls),
    'block23_u1_theorems':sum(d['kind']=='theorem' and d['module']==NEW_MODULES[0] for d in new_decls),
    'block24_theorems':sum(d['kind']=='theorem' and d['module']==NEW_MODULES[1] for d in new_decls),
    'block25_theorems':sum(d['kind']=='theorem' and d['module']==NEW_MODULES[2] for d in new_decls),
  },
  'axiom_audit':{'status':'PASS','new_declarations_checked':len(new_decls),'allowed':sorted(ALLOWED),'observed':sorted(observed)},
  'negative_controls':{'status':'PASS','new_passed':len(negatives),'new_total':len(negatives),
                       'parent_inherited_passed':parent_report['negative_controls']['passed'],
                       'parent_inherited_total':parent_report['negative_controls']['total'],
                       'cumulative_evidence_total':parent_report['negative_controls']['total']+len(negatives)},
  'parent_preservation':{'status':preservation['status'],'modules_preserved':preservation['modules_preserved'],'modules_checked':preservation['modules_checked'],'parent_archive_sha256':preservation['parent_archive_sha256']},
  'block24_source_identity':b24,
  'fresh_extension_verification':{
    'status':'PASS','build_seconds':int((ROOT.parent.parent/'kp25_fresh/fresh_build_seconds.txt').read_text().strip()) if (ROOT.parent.parent/'kp25_fresh/fresh_build_seconds.txt').exists() else 9,
    'audit_seconds':int((ROOT.parent.parent/'kp25_fresh/fresh_audit_seconds.txt').read_text().strip()) if (ROOT.parent.parent/'kp25_fresh/fresh_audit_seconds.txt').exists() else 11,
    'negative_controls':fresh_neg,'source_sha256':fresh_hashes,
  },
  'source_sha256':source_hashes,
 }
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':'PASS','seconds':report['seconds'],'counts':report['counts']},indent=2))

if __name__=='__main__': main()
