#!/usr/bin/env python3
"""Cumulative verification for Komorebi Physics v0.36.0 / Block 36."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from verify import strip_comments_and_strings
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_KIT=Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
ALLOWED_AXIOMS={'propext','Classical.choice','Quot.sound'}
NEW_MODULE='KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction'
EXPECTED_LEAN='4.34.0-rc2'
EXPECTED_MATHLIB='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
EXPECTED_MODULES=135
EXPECTED_PARENT_MODULES=134
EXPECTED_NEW_DECLARATIONS=47
EXPECTED_NEW_THEOREMS=23
PROHIBITED=re.compile(r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b|skipKernelTC|#eval|#run')
NEG_DIAGNOSTICS={'WrongCellVolume':'error:','WrongCellCount':'error:','WrongThreeDimensionalScaling':'error:'}
def sha256(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--kit',type=Path,default=DEFAULT_KIT); ap.add_argument('--out',type=Path,default=ROOT/'verification/block36_final'); ap.add_argument('--timeout',type=int,default=1200); a=ap.parse_args()
 kit=a.kit.resolve(); lake=kit/'toolchain/bin/lake'; lean=kit/'toolchain/bin/lean'
 if not lake.is_file() or not lean.is_file(): raise FileNotFoundError(kit)
 out=a.out if a.out.is_absolute() else ROOT/a.out; out.mkdir(parents=True,exist_ok=True)
 started=datetime.now(timezone.utc); checks=[]; env=os.environ.copy(); env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
 for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT'): env.pop(k,None)
 def run(label,argv,*,expected_failure=False,diagnostic=None,timeout=None,run_env=None):
  t=time.monotonic(); log=out/f'{label}.log'; timed=False; rc=None
  print('VERIFIER_START',label,flush=True)
  with log.open('w',encoding='utf-8') as h:
   try:
    p=subprocess.run([str(x) for x in argv],cwd=ROOT,env=run_env or env,text=True,stdout=h,stderr=subprocess.STDOUT,timeout=timeout or a.timeout); rc=p.returncode
   except subprocess.TimeoutExpired:
    timed=True; h.write('\nVERIFIER_TIMEOUT\n')
  txt=log.read_text(errors='replace')
  if expected_failure:
   low=txt.lower(); ok=(not timed and rc not in (0,None) and diagnostic and diagnostic in txt and 'unknown module prefix' not in low and 'object file' not in low and 'no such file' not in low)
  else: ok=not timed and rc==0
  rec={'label':label,'argv':[str(x) for x in argv],'returncode':rc,'timed_out':timed,'seconds':round(time.monotonic()-t,4),'expected_failure':expected_failure,'status':'PASS' if ok else 'FAIL','log':str(log.relative_to(ROOT)),'log_sha256':sha256(log)}; checks.append(rec)
  print('VERIFIER_END',label,rec['status'],rec['seconds'],flush=True)
  if not ok: raise RuntimeError(f'{label} failed: {log}')
  return txt
 inv=json.loads((ROOT/'declaration_inventory.json').read_text()); pinv=json.loads((ROOT/'reference/block35_declaration_inventory.json').read_text()); prep=json.loads((ROOT/'reference/block35_production_report.json').read_text()); ph=json.loads((ROOT/'reference/block35_source_hashes.json').read_text())
 if prep.get('status')!='PASS': raise RuntimeError('parent report not PASS')
 if len(inv['modules'])!=EXPECTED_MODULES or len(pinv['modules'])!=EXPECTED_PARENT_MODULES: raise RuntimeError('module count mismatch')
 if ph.get('count')!=EXPECTED_PARENT_MODULES: raise RuntimeError('hash ledger count mismatch')
 if NEW_MODULE not in inv['modules'] or NEW_MODULE in pinv['modules']: raise RuntimeError('new module membership mismatch')
 decls=[d for d in inv['declarations'] if d['module']==NEW_MODULE]; th=sum(d['kind']=='theorem' for d in decls)
 if len(decls)!=EXPECTED_NEW_DECLARATIONS or th!=EXPECTED_NEW_THEOREMS: raise RuntimeError(f'new count mismatch {len(decls)} {th}')
 if len({d['name'] for d in inv['declarations']})!=len(inv['declarations']): raise RuntimeError('duplicate declarations')
 audit_names=re.findall(r'^#print axioms (\S+)$',(ROOT/'AuditBlock36.lean').read_text(),re.M)
 if audit_names != [d['name'] for d in decls]: raise RuntimeError('audit mismatch')
 if f'public import {NEW_MODULE}' not in (ROOT/'KomorebiPhysics.lean').read_text(): raise RuntimeError('top import missing')
 if 'version = "0.36.0"' not in (ROOT/'lakefile.toml').read_text(): raise RuntimeError('version mismatch')
 parent_errors=[]
 for rel,exp in ph['sha256'].items():
  p=ROOT/rel; got=sha256(p) if p.is_file() else None
  if got!=exp: parent_errors.append({'file':rel,'expected':exp,'got':got})
 if parent_errors: raise RuntimeError(f'parent source changed: {parent_errors[:5]}')
 active=[ROOT/(NEW_MODULE.replace('.','/')+'.lean'),ROOT/'KomorebiPhysics.lean',ROOT/'AuditBlock36.lean',ROOT/'CheckBlock36API.lean']
 hits=[]
 for p in active:
  m=PROHIBITED.search(strip_comments_and_strings(p.read_text()))
  if m: hits.append({'file':str(p.relative_to(ROOT)),'token':m.group(0)})
 if hits: raise RuntimeError(hits)
 module_files=[ROOT/(m.replace('.','/')+'.lean') for m in inv['modules']]
 source_th=sum(len(re.findall(r'\btheorem\s+',strip_comments_and_strings(p.read_text()))) for p in module_files)
 inventory_th=sum(d['kind']=='theorem' for d in inv['declarations'])
 if source_th!=inventory_th: raise RuntimeError(f'theorem mismatch {source_th} {inventory_th}')
 lv=subprocess.check_output([str(lean),'--version'],env=env,text=True).strip(); mr=subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
 if EXPECTED_LEAN not in lv or mr!=EXPECTED_MATHLIB: raise RuntimeError('pin mismatch')
 lp=subprocess.check_output([str(lake),'env','printenv','LEAN_PATH'],cwd=ROOT,env=env,text=True).strip(); lenv=env.copy(); lenv['LEAN_PATH']=lp
 run('build_block36_import_closure',[lake,'-Kjobs=8','--wfail','build',NEW_MODULE],timeout=900)
 run('build_full_cumulative_project',[lake,'-Kjobs=8','--wfail','build','KomorebiPhysics'],timeout=1200)
 run('compile_block36_warning_as_error',[lean,'-DwarningAsError=true','KomorebiPhysics/Relativistic3DWeightedDyadicReconstruction.lean'],timeout=600,run_env=lenv)
 run('compile_block36_api',[lean,'-DwarningAsError=true','CheckBlock36API.lean'],timeout=600,run_env=lenv)
 at=run('audit_block36',[lean,'AuditBlock36.lean'],timeout=600,run_env=lenv)
 obs=set()
 for m in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]',at,re.S): obs.update(x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip())
 if not obs<=ALLOWED_AXIOMS: raise RuntimeError(f'unexpected axioms {obs-ALLOWED_AXIOMS}')
 neg=[]
 for p in sorted((ROOT/'negative_controls/block36').glob('*.lean')):
  txt=run('negative_'+p.stem,[lean,'-DwarningAsError=true',p],expected_failure=True,diagnostic=NEG_DIAGNOSTICS[p.stem],timeout=300,run_env=lenv)
  neg.append({'file':str(p.relative_to(ROOT)),'diagnostic_excerpt':[l for l in txt.splitlines() if 'error:' in l or '⊢' in l][:8]})
 if len(neg)!=3: raise RuntimeError('negative count')
 proof_inputs=[ROOT/(NEW_MODULE.replace('.','/')+'.lean'),ROOT/'KomorebiPhysics.lean',ROOT/'AuditBlock36.lean',ROOT/'CheckBlock36API.lean',ROOT/'declaration_inventory.json',ROOT/'reference/block35_declaration_inventory.json',ROOT/'reference/block35_production_report.json',ROOT/'reference/block35_source_hashes.json',ROOT/'verification/block36_inventory_summary.json',ROOT/'lakefile.toml',ROOT/'lean-toolchain',ROOT/'lake-manifest.json',Path(__file__),ROOT/'scripts/refresh_block36_inventory.py']+sorted((ROOT/'negative_controls/block36').glob('*.lean'))
 finished=datetime.now(timezone.utc); parent_neg=prep['negative_controls']['cumulative_evidence_total']
 report={'schema':'komorebi.physics.block36.verification.v1','status':'PASS','started_utc':started.isoformat(),'finished_utc':finished.isoformat(),'seconds':round((finished-started).total_seconds(),4),'release':'Komorebi Physics Lean v0.36.0 — Checked Block 36','verification_mode':'terminal cumulative top-level build plus frozen checked v0.35 parent, byte-identical parent sources, and fresh focused Block 36 audit','claim_contract':{'proved':'For arbitrary equal-positive-volume finite measurable partitions, inverse-square-root cell normalization gives an exact linear isometry from finite PiLp coefficients into genuine continuum L2.  On the octree address continuum (Fin 8)^N with uniform product probability measure, level-n prefix cells form measurable disjoint covers of exact volume 8^-n = (2^-n)^3, their measure-correct interpolation is isometric, finite-prefix step subspaces are nested, and their algebraic union is dense in L2.  Hence every continuum L2 state admits arbitrarily accurate approximation by a finite-depth octree-step state.','not_proved':'The octree address continuum has not yet been formally identified measure-theoretically with the Euclidean unit cube or R^3.  The theorem does not establish continuum Dirac generator consistency, propagator convergence, nonabelian gauge dynamics, emergent Lorentzian geometry, gravity, cosmology, or empirical predictions.'},'trust_boundary':'All 47 named Block 36 declarations were kernel-checked against the pinned Lean/Mathlib cache; two additional anonymous typeclass instances were compiler-checked.  The complete cumulative target emitted a terminal successful build.  The 134 v0.35 mathematical modules are inherited only after byte-for-byte source comparison with the frozen Block 35 ledger and validation of its PASS report. Lean and Mathlib were not rebuilt from compiler source.','lean_version':lv,'mathlib_revision':mr,'checks':checks,'counts':{'active_modules':len(inv['modules']),'parent_modules':len(pinv['modules']),'new_modules':1,'total_theorems':inventory_th,'audited_declarations':len(inv['declarations']),'new_theorems':th,'new_audited_declarations':len(decls),'new_source_declarations_including_instances':52,'new_anonymous_instances':2,'new_by_kind':{k:sum(d['kind']==k for d in decls) for k in ['theorem','def','structure','abbrev']}},'source_precheck':{'status':'PASS','active_files_scanned':len(active),'prohibited_tokens_found':0,'cumulative_source_theorem_count':source_th},'axiom_audit':{'status':'PASS','allowed':sorted(ALLOWED_AXIOMS),'observed':sorted(obs),'declarations_checked':len(decls)},'negative_controls':{'status':'PASS','new_passed':len(neg),'new_total':len(neg),'controls':neg,'parent_inherited_evidence':parent_neg,'cumulative_evidence_total':parent_neg+len(neg)},'parent_preservation':{'status':'PASS','modules_compared':ph['count'],'changed_modules':0,'ledger_sha256':sha256(ROOT/'reference/block35_source_hashes.json'),'reference_report_sha256':sha256(ROOT/'reference/block35_production_report.json'),'parent_report_status':prep.get('status'),'parent_verification_mode':prep.get('verification_mode')},'excluded_attempts':[{'kind':'earlier_block36_checkpoint','status':'NO_SOURCE_NO_LAKE','claim_effect':'discarded; it contained no Lean source and no completed verification.'},{'kind':'cumulative_cache_population','status':'MULTIPLE_INCONCLUSIVE_OUTER_TIMEOUTS','claim_effect':'not counted; the resumed cache eventually produced a terminal successful 3924-job build receipt.'},{'kind':'euclidean_cube_identification','status':'DEFERRED_SCOPE','claim_effect':'not claimed; the checked continuum is the octree address product space, not yet a proved Euclidean-coordinate realization.'}],'source_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in proof_inputs}}
 rp=out/'report.json'; rp.write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({'status':'PASS','report':str(rp),'counts':report['counts'],'axioms':sorted(obs),'negative_controls':len(neg)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
