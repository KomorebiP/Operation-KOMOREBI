#!/usr/bin/env python3
"""Verify Komorebi Physics v0.28.0 / checked Block 28.

The 126 v0.27 mathematical modules are inherited only after byte-for-byte
source comparison with the checked parent record. Block 28 is rebuilt and
all new declarations are axiom-audited against the pinned Lean/Mathlib cache.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KIT = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULE = 'KomorebiPhysics.Relativistic3DFullWalkRefinement'
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
    ap.add_argument('--out',type=Path,default=ROOT/'verification/block28_final')
    ap.add_argument('--timeout',type=int,default=1200)
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
        else: ok=(not timed_out and rc==0)
        rec={'label':label,'argv':[str(x) for x in argv],'returncode':rc,
             'timed_out':timed_out,'seconds':round(time.monotonic()-t0,4),
             'expected_failure':expected_failure,'diagnostic':diagnostic,
             'status':'PASS' if ok else 'FAIL','log':str(log.relative_to(ROOT)),
             'log_sha256':sha256(log)}
        checks.append(rec)
        if not ok: raise RuntimeError(f'{label} failed; see {log}')
        return text

    inv=json.loads((ROOT/'declaration_inventory.json').read_text())
    parent_inv=json.loads((ROOT/'reference/block27_declaration_inventory.json').read_text())
    parent_report=json.loads((ROOT/'reference/block27_production_report.json').read_text())
    if len(inv['modules'])!=127: raise RuntimeError(f"expected 127 modules, found {len(inv['modules'])}")
    if len(parent_inv['modules'])!=126: raise RuntimeError(f"expected 126 parent modules, found {len(parent_inv['modules'])}")
    names=[d['name'] for d in inv['declarations']]
    if len(names)!=len(set(names)): raise RuntimeError('duplicate declaration names')

    module_files=[ROOT/(m.replace('.','/')+'.lean') for m in inv['modules']]
    active=module_files+[ROOT/'KomorebiPhysics.lean',ROOT/'Audit.lean',ROOT/'AuditBlock28.lean']
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
    if len(new)!=82: raise RuntimeError(f'expected 82 Block 28 declarations, found {len(new)}')
    if sum(d['kind']=='theorem' for d in new)!=56: raise RuntimeError('expected 56 Block 28 theorems')
    audit_names=re.findall(r'^#print axioms (\S+)$',(ROOT/'AuditBlock28.lean').read_text(),re.M)
    if audit_names!=[d['name'] for d in new]: raise RuntimeError('AuditBlock28 mismatch')

    parent_errors=[]
    for mod in parent_inv['modules']:
        rel=mod.replace('.','/')+'.lean'; p=ROOT/rel
        expected=parent_report['source_sha256'].get(rel); got=sha256(p)
        if expected is None or got!=expected: parent_errors.append({'module':mod,'expected':expected,'got':got})
    if parent_errors: raise RuntimeError(f'v0.27 parent changed: {parent_errors[:5]}')

    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    mathlib=subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
    if EXPECTED_LEAN not in version: raise RuntimeError('Lean pin mismatch: '+version)
    if mathlib!=EXPECTED_MATHLIB: raise RuntimeError('Mathlib pin mismatch: '+mathlib)

    run('cumulative_build',[lake,'-Kjobs=16','build','MovingFrames','KomorebiPhysics'],timeout=1800)
    run('top_warning_as_error',[lake,'env','lean','-DwarningAsError=true','KomorebiPhysics.lean'])
    run('compile_block28_warning_as_error',[lake,'env','lean','-DwarningAsError=true',
        'KomorebiPhysics/Relativistic3DFullWalkRefinement.lean'])
    audit_text=run('audit_block28',[lake,'env','lean','AuditBlock28.lean'],timeout=600)
    observed=set()
    for m in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]',audit_text,re.S):
        observed.update(x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip())
    if not observed<=ALLOWED_AXIOMS: raise RuntimeError('unexpected axioms: '+repr(sorted(observed-ALLOWED_AXIOMS)))

    negatives=[]
    for p in sorted((ROOT/'negative_controls/block28').glob('*.lean')):
        text=run('negative_'+p.stem,[lake,'env','lean',p],expected_failure=True,
                 diagnostic='unsolved goals',timeout=300)
        diagnostics=[line for line in text.splitlines() if 'error:' in line or '⊢' in line]
        negatives.append({'file':str(p.relative_to(ROOT)),'diagnostic_excerpt':diagnostics[:3] or ['unsolved goals']})
    if len(negatives)!=3: raise RuntimeError(f'expected 3 negative controls, got {len(negatives)}')

    proof_inputs=module_files+[ROOT/'KomorebiPhysics.lean',ROOT/'Audit.lean',ROOT/'AuditBlock28.lean',
        ROOT/'declaration_inventory.json',ROOT/'reference/block27_declaration_inventory.json',
        ROOT/'reference/block27_production_report.json',ROOT/'verification/block28_inventory_summary.json',
        ROOT/'lakefile.toml',ROOT/'lean-toolchain',ROOT/'lake-manifest.json',Path(__file__),
        ROOT/'scripts/refresh_block28_inventory.py']
    proof_inputs+=sorted((ROOT/'negative_controls/block28').glob('*.lean'))
    source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in proof_inputs}
    finished=datetime.now(timezone.utc)
    report={
      'schema':'komorebi.physics.block28.verification.v1','status':'PASS',
      'started_utc':started.isoformat(),'finished_utc':finished.isoformat(),
      'seconds':round((finished-started).total_seconds(),4),
      'release':'Komorebi Physics Lean v0.28.0 — Checked Block 28',
      'claim_contract':{
        'proved':('A globally glued half-grid with canonical U(1) frame links gives exact two-half-step '
          'intertwining for all three Clifford directions and exact factorwise refinement of the full '
          'M-X-Y-Z-Y-X-M walk. The frame embedding is gauge covariant and Hilbert isometric with '
          'one-eighth cell measure. A continuous-linear telescoping theorem bounds any contractive '
          'seven-factor adjacent-scale defect by the sum of its five spatial local defects; cubical '
          'phase-path defects have exact norm |Omega-1|, yielding a concrete five-face curvature budget.'),
        'not_proved':('The concrete curvature budget is for phase-path swap operators and a conditional '
          'generic factor theorem. No theorem identifies arbitrary nonflat full Clifford-walk factor '
          'defects with those five face amplitudes. No scale decay, summability, continuum Dirac limit, '
          'dynamical gauge equation, gravity, or empirical claim is established.')},
      'trust_boundary':('All Block 28 declarations and the cumulative project were checked against the '
        'pinned Lean/Mathlib cache. The 126 v0.27 mathematical modules are inherited only after '
        'byte-for-byte source comparison with the checked parent report. Lean and Mathlib were not '
        'rebuilt from compiler source.'),
      'lean_version':version,'mathlib_revision':mathlib,'checks':checks,
      'counts':{'active_modules':len(inv['modules']),'parent_modules':len(parent_inv['modules']),
        'new_modules':1,'total_theorems':inv_theorems,'audited_declarations':len(inv['declarations']),
        'new_theorems':sum(d['kind']=='theorem' for d in new),'new_audited_declarations':len(new),
        'new_by_kind':{k:sum(d['kind']==k for d in new) for k in sorted({d['kind'] for d in new})}},
      'source_precheck':{'status':'PASS','active_files_scanned':len(active),
        'prohibited_tokens_found':0,'source_theorem_count':source_theorems},
      'axiom_audit':{'status':'PASS','allowed':sorted(ALLOWED_AXIOMS),'observed':sorted(observed),
        'declarations_checked':len(new)},
      'negative_controls':{'status':'PASS','new_passed':len(negatives),'new_total':len(negatives),
        'controls':negatives,'parent_inherited_evidence':parent_report['negative_controls']['cumulative_evidence_total'],
        'cumulative_evidence_total':parent_report['negative_controls']['cumulative_evidence_total']+len(negatives)},
      'parent_preservation':{'status':'PASS','modules_compared':len(parent_inv['modules']),
        'changed_modules':0,'reference_report_sha256':sha256(ROOT/'reference/block27_production_report.json')},
      'source_sha256':source_hashes}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'PASS','report':str(out/'report.json'),'counts':report['counts'],
      'axioms':sorted(observed),'negative_controls':len(negatives)},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
