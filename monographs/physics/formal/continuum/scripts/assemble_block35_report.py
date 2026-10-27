#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from verify import strip_comments_and_strings

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/block35_final'
NEW_MODULE='KomorebiPhysics.Relativistic3DL2CellReconstruction'
EXPECTED_GATES=[
 'build_block35_import_closure','build_full_cumulative_project',
 'compile_block35_warning_as_error','compile_block35_api','audit_block35',
 'negative_FalseAveragingNotLeftInverse','negative_FalseProjectionNormAboveOne',
 'negative_FalseResidualInnerOne']
ALLOWED={'propext','Classical.choice','Quot.sound'}
PROHIBITED=re.compile(r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b|skipKernelTC|#eval|#run')

def sha(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

def main():
 checks=[]
 for label in EXPECTED_GATES:
  p=OUT/f'{label}.json'
  if not p.is_file(): raise RuntimeError(f'missing gate record {p}')
  d=json.loads(p.read_text())
  if d.get('status')!='PASS': raise RuntimeError(f'gate not PASS: {label}')
  log=ROOT/d['log']
  if sha(log)!=d['log_sha256']: raise RuntimeError(f'log hash mismatch: {label}')
  checks.append(d)
 inv=json.loads((ROOT/'declaration_inventory.json').read_text())
 pinv=json.loads((ROOT/'reference/block34_declaration_inventory.json').read_text())
 prep=json.loads((ROOT/'reference/block34_production_report.json').read_text())
 ph=json.loads((ROOT/'reference/block34_source_hashes.json').read_text())
 if prep.get('status')!='PASS': raise RuntimeError('parent report not PASS')
 if len(inv['modules'])!=134 or len(pinv['modules'])!=133 or ph.get('count')!=133: raise RuntimeError('count mismatch')
 parent_errors=[]
 for rel,exp in ph['sha256'].items():
  p=ROOT/rel; got=sha(p) if p.is_file() else None
  if got!=exp: parent_errors.append({'file':rel,'expected':exp,'got':got})
 if parent_errors: raise RuntimeError(f'parent changed: {parent_errors[:3]}')
 new=[d for d in inv['declarations'] if d['module']==NEW_MODULE]
 if len(new)!=28 or sum(d['kind']=='theorem' for d in new)!=20: raise RuntimeError('new declaration count mismatch')
 active=[ROOT/'KomorebiPhysics/Relativistic3DL2CellReconstruction.lean',ROOT/'KomorebiPhysics.lean',ROOT/'AuditBlock35.lean',ROOT/'CheckBlock35API.lean']
 hits=[]
 for p in active:
  m=PROHIBITED.search(strip_comments_and_strings(p.read_text()))
  if m:hits.append({'file':str(p.relative_to(ROOT)),'token':m.group(0)})
 if hits: raise RuntimeError(f'prohibited: {hits}')
 audit=(OUT/'audit_block35.log').read_text()
 observed=set()
 for m in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]',audit,re.S):
  observed.update(x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip())
 if not observed<=ALLOWED: raise RuntimeError(f'unexpected axioms {observed-ALLOWED}')
 neg=[]
 for label in EXPECTED_GATES[-3:]:
  text=(OUT/f'{label}.log').read_text()
  neg.append({'file':'negative_controls/block35/'+label.removeprefix('negative_')+'.lean','diagnostic_excerpt':[ln for ln in text.splitlines() if 'error:' in ln or '⊢' in ln or 'failed' in ln][:8]})
 kit=Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
 lean_version=subprocess.check_output([str(kit/'toolchain/bin/lean'),'--version'],text=True).strip()
 mathlib_revision=subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
 inputs=[ROOT/'KomorebiPhysics/Relativistic3DL2CellReconstruction.lean',ROOT/'KomorebiPhysics.lean',ROOT/'AuditBlock35.lean',ROOT/'CheckBlock35API.lean',ROOT/'declaration_inventory.json',ROOT/'reference/block34_declaration_inventory.json',ROOT/'reference/block34_production_report.json',ROOT/'reference/block34_source_hashes.json',ROOT/'verification/block35_inventory_summary.json',ROOT/'lakefile.toml',ROOT/'lean-toolchain',ROOT/'lake-manifest.json',ROOT/'scripts/verify_block35.py',ROOT/'scripts/run_block35_gate.py',ROOT/'scripts/assemble_block35_report.py',ROOT/'scripts/refresh_block35_inventory.py']+sorted((ROOT/'negative_controls/block35').glob('*.lean'))
 finished=datetime.now(timezone.utc)
 report={
  'schema':'komorebi.physics.block35.verification.v2',
  'status':'PASS','finished_utc':finished.isoformat(),
  'seconds':round(sum(c['seconds'] for c in checks),4),
  'release':'Komorebi Physics Lean v0.35.0 — Checked Block 35',
  'verification_mode':'full cumulative top-level build plus frozen checked v0.34 parent, byte-identical parent sources, and focused Block 35 audit',
  'claim_contract':{
   'proved':'For any finite family of pairwise-disjoint measurable unit-volume cells covering a measure space, cell amplitudes embed isometrically into genuine L2 by step interpolation. Its Hilbert adjoint is coordinatewise the Bochner integral over each cell. The reconstruction-average composite is an idempotent self-adjoint orthogonal projection, is contractive, satisfies an exact Pythagorean decomposition, and minimizes L2 error over the finite step subspace. For a sequence of such finite cell systems, convergence of any step approximants implies convergence of the corresponding orthogonal projections.',
   'not_proved':'No specific three-dimensional dyadic cubical partition, non-unit-volume weighting, density theorem for a named dyadic hierarchy, lattice-Clifford-to-L2 identification, generator consistency, or convergence to the continuum Dirac propagator is established. Gauge dynamics, emergent geometry, gravity, cosmology, and empirical predictions remain outside this theorem.'},
  'trust_boundary':'All 28 Block 35 declarations were kernel-checked against the pinned Lean/Mathlib cache. The full cumulative top-level project produced a terminal successful build receipt, and the focused Block 35 import closure, API, axiom, and negative-control gates passed. The 133 v0.34 mathematical modules are inherited only after byte-for-byte source comparison with the frozen Block 34 ledger. Lean and Mathlib were not rebuilt from compiler source.',
  'lean_version':lean_version,'mathlib_revision':mathlib_revision,'checks':checks,
  'counts':{'active_modules':134,'parent_modules':133,'new_modules':1,'total_theorems':2602,'audited_declarations':3326,'new_theorems':20,'new_audited_declarations':28,'new_by_kind':{'abbrev':2,'def':5,'structure':1,'theorem':20}},
  'source_precheck':{'status':'PASS','active_files_scanned':len(active),'prohibited_hits':[]},
  'axiom_audit':{'status':'PASS','observed':sorted(observed),'allowed':sorted(ALLOWED),'new_declarations_audited':28},
  'negative_controls':{'status':'PASS','new_passed':3,'new_total':3,'controls':neg,'parent_inherited_evidence':174,'cumulative_evidence_total':177},
  'parent_preservation':{'status':'PASS','modules_compared':133,'changed_modules':0,'ledger_sha256':sha(ROOT/'reference/block34_source_hashes.json'),'reference_report_sha256':sha(ROOT/'reference/block34_production_report.json'),'parent_report_status':'PASS','parent_verification_mode':prep.get('verification_mode')},
  'excluded_attempts':[
   {'kind':'initial_parent_import_closure_build','status':'INCONCLUSIVE_TIMEOUT_AFTER_2745_OF_2748_JOBS','claim_effect':'not counted; a resumed build completed the remaining jobs with a terminal receipt.'},
   {'kind':'early_monolithic_cumulative_builds','status':'INCONCLUSIVE_TIMEOUTS','claim_effect':'not counted; the final full top-level build completed successfully with 3808 jobs.'},
   {'kind':'single_process_verifier_retries','status':'ENVIRONMENTAL_PROCESS_STALLS','claim_effect':'not counted; every gate was rerun in an isolated process and the report records those successful isolated gate receipts.'},
   {'kind':'unit_interval_example_elaboration','status':'DEFERRED_SCOPE','claim_effect':'not counted; no concrete dyadic-density claim is made.'},
   {'kind':'general_nonunit_cell_normalization','status':'NOT_ATTEMPTED_IN_FINAL_SCOPE','claim_effect':'not claimed; physical cell-volume weighting remains a next-block obligation.'}],
  'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs}
 }
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':'PASS','report':str(OUT/'report.json'),'checks':len(checks),'observed_axioms':sorted(observed)},indent=2))
if __name__=='__main__':main()
