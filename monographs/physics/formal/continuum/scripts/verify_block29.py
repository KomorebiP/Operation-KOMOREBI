#!/usr/bin/env python3
"""Verify Komorebi Physics v0.29.0 / checked Block 29.

The 127 v0.28 mathematical modules are inherited only after byte-for-byte
source comparison with the checked parent record.  Block 29 and its complete
import closure are rebuilt, warning-checked, axiom-audited, and tested against
three negative controls.  A monolithic rebuild of every unrelated parent
module is not a claim of this verifier; the parent cumulative build is inherited
from the v0.28 checked report after source identity is established.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KIT = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULE = 'KomorebiPhysics.Relativistic3DEdgeCompatibility'
EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
PROHIBITED = re.compile(
    r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b'
    r'|skipKernelTC|#eval|#run'
)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--kit',type=Path,default=DEFAULT_KIT)
    ap.add_argument('--out',type=Path,default=ROOT/'verification/block29_final')
    ap.add_argument('--timeout',type=int,default=900)
    args=ap.parse_args()
    kit=args.kit.resolve(); lake=kit/'toolchain/bin/lake'; lean=kit/'toolchain/bin/lean'
    if not lake.is_file() or not lean.is_file(): raise FileNotFoundError(f'pinned kit incomplete: {kit}')
    out=args.out if args.out.is_absolute() else ROOT/args.out
    out.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc); checks=[]

    def run(label, argv, *, expected_failure=False, diagnostic=None, timeout=None):
        t0=time.monotonic()
        try:
            r=subprocess.run([str(x) for x in argv], cwd=ROOT, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                timeout=timeout or args.timeout)
            text=r.stdout; rc=r.returncode; timed_out=False
        except subprocess.TimeoutExpired as exc:
            text=(exc.stdout or '')+(exc.stderr or '')
            if isinstance(text,bytes): text=text.decode(errors='replace')
            rc=None; timed_out=True
        log=out/f'{label}.log'; log.write_text(text,encoding='utf-8')
        if expected_failure:
            ok=(not timed_out and rc not in (0,None) and diagnostic in text
                and 'unknown module prefix' not in text
                and 'object file' not in text
                and 'no such file or directory' not in text.lower())
        else:
            ok=(not timed_out and rc==0)
        rec={'label':label,'argv':[str(x) for x in argv],'returncode':rc,
             'timed_out':timed_out,'seconds':round(time.monotonic()-t0,4),
             'expected_failure':expected_failure,'diagnostic':diagnostic,
             'status':'PASS' if ok else 'FAIL','log':str(log.relative_to(ROOT)),
             'log_sha256':sha256(log)}
        checks.append(rec)
        if not ok: raise RuntimeError(f'{label} failed; see {log}')
        return text

    inv=json.loads((ROOT/'declaration_inventory.json').read_text())
    parent_inv=json.loads((ROOT/'reference/block28_declaration_inventory.json').read_text())
    parent_report=json.loads((ROOT/'reference/block28_production_report.json').read_text())
    if parent_report.get('status')!='PASS': raise RuntimeError('parent v0.28 report is not PASS')
    if len(inv['modules'])!=128: raise RuntimeError(f"expected 128 modules, found {len(inv['modules'])}")
    if len(parent_inv['modules'])!=127: raise RuntimeError(f"expected 127 parent modules, found {len(parent_inv['modules'])}")
    if NEW_MODULE not in inv['modules'] or NEW_MODULE in parent_inv['modules']:
        raise RuntimeError('new module membership mismatch')
    names=[d['name'] for d in inv['declarations']]
    if len(names)!=len(set(names)): raise RuntimeError('duplicate declaration names')

    module_files=[ROOT/(m.replace('.','/')+'.lean') for m in inv['modules']]
    active=[ROOT/(NEW_MODULE.replace('.','/')+'.lean'),ROOT/'KomorebiPhysics.lean',
        ROOT/'AuditBlock29.lean',ROOT/'CheckBlock29API.lean']
    hits=[]
    for p in active:
        if not p.is_file(): raise FileNotFoundError(p)
        m=PROHIBITED.search(strip_comments_and_strings(p.read_text()))
        if m: hits.append({'file':str(p.relative_to(ROOT)),'token':m.group(0)})
    if hits: raise RuntimeError(f'prohibited active tokens: {hits[:10]}')

    source_theorems=sum(len(re.findall(r'\btheorem\s+',strip_comments_and_strings(p.read_text()))) for p in module_files)
    inv_theorems=sum(d['kind']=='theorem' for d in inv['declarations'])
    if source_theorems!=inv_theorems: raise RuntimeError(f'theorem count mismatch {source_theorems}!={inv_theorems}')
    new=[d for d in inv['declarations'] if d['module']==NEW_MODULE]
    if len(new)!=65: raise RuntimeError(f'expected 65 Block 29 declarations, found {len(new)}')
    if sum(d['kind']=='theorem' for d in new)!=42: raise RuntimeError('expected 42 Block 29 theorems')
    audit_names=re.findall(r'^#print axioms (\S+)$',(ROOT/'AuditBlock29.lean').read_text(),re.M)
    if audit_names!=[d['name'] for d in new]: raise RuntimeError('AuditBlock29 mismatch')
    if 'public import '+NEW_MODULE not in (ROOT/'KomorebiPhysics.lean').read_text():
        raise RuntimeError('top-level import missing')
    if 'version = "0.29.0"' not in (ROOT/'lakefile.toml').read_text():
        raise RuntimeError('lakefile version mismatch')

    parent_errors=[]
    for mod in parent_inv['modules']:
        rel=mod.replace('.','/')+'.lean'; p=ROOT/rel
        expected=parent_report['source_sha256'].get(rel); got=sha256(p)
        if expected is None or got!=expected:
            parent_errors.append({'module':mod,'expected':expected,'got':got})
    if parent_errors: raise RuntimeError(f'v0.28 parent changed: {parent_errors[:5]}')

    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    mathlib=subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
    if EXPECTED_LEAN not in version: raise RuntimeError('Lean pin mismatch: '+version)
    if mathlib!=EXPECTED_MATHLIB: raise RuntimeError('Mathlib pin mismatch: '+mathlib)

    run('build_block29_import_closure',[lake,'-Kjobs=16','build','+'+NEW_MODULE],timeout=1200)
    run('compile_block29_warning_as_error',[lake,'env','lean','-DwarningAsError=true',
        'KomorebiPhysics/Relativistic3DEdgeCompatibility.lean'])
    run('compile_block29_api',[lake,'env','lean','-DwarningAsError=true','CheckBlock29API.lean'])
    audit_text=run('audit_block29',[lake,'env','lean','AuditBlock29.lean'],timeout=600)
    observed=set()
    for m in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]',audit_text,re.S):
        observed.update(x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip())
    if not observed<=ALLOWED_AXIOMS: raise RuntimeError('unexpected axioms: '+repr(sorted(observed-ALLOWED_AXIOMS)))

    negatives=[]
    for p in sorted((ROOT/'negative_controls/block29').glob('*.lean')):
        text=run('negative_'+p.stem,[lake,'env','lean',p],expected_failure=True,
                 diagnostic='unsolved goals',timeout=300)
        diagnostics=[line for line in text.splitlines() if 'error:' in line or '⊢' in line]
        negatives.append({'file':str(p.relative_to(ROOT)),'diagnostic_excerpt':diagnostics[:4] or ['unsolved goals']})
    if len(negatives)!=3: raise RuntimeError(f'expected 3 negative controls, got {len(negatives)}')

    proof_inputs=[ROOT/(NEW_MODULE.replace('.','/')+'.lean'),ROOT/'KomorebiPhysics.lean',
        ROOT/'AuditBlock29.lean',ROOT/'CheckBlock29API.lean',ROOT/'declaration_inventory.json',
        ROOT/'reference/block28_declaration_inventory.json',ROOT/'reference/block28_production_report.json',
        ROOT/'verification/block29_inventory_summary.json',ROOT/'lakefile.toml',ROOT/'lean-toolchain',
        ROOT/'lake-manifest.json',Path(__file__),ROOT/'scripts/refresh_block29_inventory.py']
    proof_inputs+=sorted((ROOT/'negative_controls/block29').glob('*.lean'))
    source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in proof_inputs}
    finished=datetime.now(timezone.utc)
    parent_negative=parent_report['negative_controls']['cumulative_evidence_total']
    report={
      'schema':'komorebi.physics.block29.verification.v1','status':'PASS',
      'started_utc':started.isoformat(),'finished_utc':finished.isoformat(),
      'seconds':round((finished-started).total_seconds(),4),
      'release':'Komorebi Physics Lean v0.29.0 — Checked Block 29',
      'verification_mode':'modular cumulative verification',
      'claim_contract':{
        'proved':('For arbitrary fine U(1) links, two half-step Clifford transport exactly refines a '
          'coarse directional shift whenever the ordered two-half-edge product reconstructs the framed '
          'coarse link. The contracts are gauge invariant and compose through the full factorwise '
          'M-X-Y-Z-Y-X-M walk. Canonical exact refinement can preserve nontrivial coarse plaquette '
          'holonomy. For arbitrary one-axis half-link pairs, the adjacent-scale Hilbert defect is exactly '
          'the coarse reconstructed-link mismatch energy. A concrete flat connection with quarter-turn '
          'half-links has a nonzero refinement defect, formally refuting an unconditional curvature-only rule.'),
        'not_proved':('No theorem bounds an arbitrary full Clifford-walk defect solely by face plaquettes. '
          'No complete operator-norm bound for the five straight-edge mismatches, scale-decay law, '
          'summability theorem for the concrete walk, continuum Dirac limit, dynamical gauge equation, '
          'gravity, cosmology, or empirical claim is established.')},
      'trust_boundary':('All 65 Block 29 declarations and their complete import closure were kernel-checked '
        'against the pinned Lean/Mathlib cache. The 127 v0.28 modules are inherited only after byte-for-byte '
        'source comparison with the checked v0.28 report. Several attempted monolithic rebuilds of every '
        'unrelated parent module exceeded the outer execution window and are not counted as PASS. Lean and '
        'Mathlib were not rebuilt from compiler source.'),
      'lean_version':version,'mathlib_revision':mathlib,'checks':checks,
      'counts':{'active_modules':len(inv['modules']),'parent_modules':len(parent_inv['modules']),
        'new_modules':1,'total_theorems':inv_theorems,'audited_declarations':len(inv['declarations']),
        'new_theorems':sum(d['kind']=='theorem' for d in new),'new_audited_declarations':len(new),
        'new_by_kind':{k:sum(d['kind']==k for d in new) for k in sorted({d['kind'] for d in new})}},
      'source_precheck':{'status':'PASS','new_active_files_scanned':len(active),
        'prohibited_tokens_found':0,'cumulative_source_theorem_count':source_theorems},
      'axiom_audit':{'status':'PASS','allowed':sorted(ALLOWED_AXIOMS),'observed':sorted(observed),
        'declarations_checked':len(new)},
      'negative_controls':{'status':'PASS','new_passed':len(negatives),'new_total':len(negatives),
        'controls':negatives,'parent_inherited_evidence':parent_negative,
        'cumulative_evidence_total':parent_negative+len(negatives)},
      'parent_preservation':{'status':'PASS','modules_compared':len(parent_inv['modules']),
        'changed_modules':0,'reference_report_sha256':sha256(ROOT/'reference/block28_production_report.json'),
        'parent_cumulative_build_status':parent_report.get('status')},
      'excluded_attempts':[
        {'kind':'monolithic_cumulative_rebuild','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted; parent build inherited after source identity'},
        {'kind':'monolithic_cumulative_rebuild_retry','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted; parent build inherited after source identity'},
        {'kind':'missing_top_modules_bulk_build','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted'}],
      'source_sha256':source_hashes}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'PASS','report':str(out/'report.json'),'counts':report['counts'],
      'axioms':sorted(observed),'negative_controls':len(negatives),
      'parent_preservation':report['parent_preservation']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
