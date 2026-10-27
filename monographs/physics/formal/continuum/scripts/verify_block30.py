#!/usr/bin/env python3
"""Verify Komorebi Physics v0.30.0 / checked Block 30.

The 128 v0.29 mathematical modules are inherited only after byte-for-byte
source comparison with the frozen Block 29 ledger.  The full cumulative target
is then built with one Lake worker and warnings treated as errors.  Block 30 is
directly compiled, API-checked, declaration-audited, and tested against three
negative controls.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time, os
from datetime import datetime, timezone
from pathlib import Path
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KIT = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULE = 'KomorebiPhysics.Relativistic3DCombinedDefect'
EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
PROHIBITED = re.compile(
    r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b'
    r'|skipKernelTC|#eval|#run'
)
NEG_DIAGNOSTICS = {
    'FalseQuarterPairDefectOperatorZero': 'unsolved goals',
    'FalseNonflatCurvatureBudgetZero': 'unsolved goals',
    'FalseConstantTwoBudgetSummable': 'error:',
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', type=Path, default=DEFAULT_KIT)
    ap.add_argument('--out', type=Path, default=ROOT/'verification/block30_final')
    ap.add_argument('--timeout', type=int, default=1800)
    args = ap.parse_args()
    kit = args.kit.resolve()
    lake = kit/'toolchain/bin/lake'
    lean = kit/'toolchain/bin/lean'
    if not lake.is_file() or not lean.is_file():
        raise FileNotFoundError(f'pinned kit incomplete: {kit}')
    out = args.out if args.out.is_absolute() else ROOT/args.out
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    checks = []
    env = os.environ.copy()
    env['PATH'] = str(kit/'toolchain/bin') + os.pathsep + env.get('PATH','')
    env.pop('LEAN_PATH', None); env.pop('LEAN_SRC_PATH', None); env.pop('LEAN_SYSROOT', None)

    def run(label, argv, *, expected_failure=False, diagnostic=None, timeout=None):
        t0 = time.monotonic()
        try:
            r = subprocess.run([str(x) for x in argv], cwd=ROOT, env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                timeout=timeout or args.timeout)
            text = r.stdout; rc = r.returncode; timed_out = False
        except subprocess.TimeoutExpired as exc:
            text = (exc.stdout or '') + (exc.stderr or '')
            if isinstance(text, bytes): text = text.decode(errors='replace')
            rc = None; timed_out = True
        log = out/f'{label}.log'; log.write_text(text, encoding='utf-8')
        if expected_failure:
            ok = (not timed_out and rc not in (0, None) and diagnostic in text
                and 'unknown module prefix' not in text
                and 'object file' not in text
                and 'no such file or directory' not in text.lower())
        else:
            ok = (not timed_out and rc == 0)
        rec = {'label': label, 'argv': [str(x) for x in argv], 'returncode': rc,
            'timed_out': timed_out, 'seconds': round(time.monotonic()-t0, 4),
            'expected_failure': expected_failure, 'diagnostic': diagnostic,
            'status': 'PASS' if ok else 'FAIL', 'log': str(log.relative_to(ROOT)),
            'log_sha256': sha256(log)}
        checks.append(rec)
        if not ok:
            raise RuntimeError(f'{label} failed; see {log}')
        return text

    inv = json.loads((ROOT/'declaration_inventory.json').read_text())
    parent_inv = json.loads((ROOT/'reference/block29_declaration_inventory.json').read_text())
    parent_report = json.loads((ROOT/'reference/block29_production_report.json').read_text())
    parent_hashes = json.loads((ROOT/'reference/block29_source_hashes.json').read_text())
    if parent_report.get('status') != 'PASS':
        raise RuntimeError('parent v0.29 report is not PASS')
    if len(inv['modules']) != 129:
        raise RuntimeError(f"expected 129 modules, found {len(inv['modules'])}")
    if len(parent_inv['modules']) != 128:
        raise RuntimeError(f"expected 128 parent modules, found {len(parent_inv['modules'])}")
    if parent_hashes.get('count') != 128:
        raise RuntimeError('parent hash ledger count mismatch')
    if NEW_MODULE not in inv['modules'] or NEW_MODULE in parent_inv['modules']:
        raise RuntimeError('new module membership mismatch')
    names = [d['name'] for d in inv['declarations']]
    if len(names) != len(set(names)):
        raise RuntimeError('duplicate declaration names')

    module_files = [ROOT/(m.replace('.','/')+'.lean') for m in inv['modules']]
    active = [ROOT/(NEW_MODULE.replace('.','/')+'.lean'), ROOT/'KomorebiPhysics.lean',
        ROOT/'AuditBlock30.lean', ROOT/'CheckBlock30API.lean']
    hits = []
    for p in active:
        if not p.is_file(): raise FileNotFoundError(p)
        m = PROHIBITED.search(strip_comments_and_strings(p.read_text()))
        if m: hits.append({'file': str(p.relative_to(ROOT)), 'token': m.group(0)})
    if hits: raise RuntimeError(f'prohibited active tokens: {hits[:10]}')

    source_theorems = sum(len(re.findall(r'\btheorem\s+',
        strip_comments_and_strings(p.read_text()))) for p in module_files)
    inv_theorems = sum(d['kind']=='theorem' for d in inv['declarations'])
    if source_theorems != inv_theorems:
        raise RuntimeError(f'theorem count mismatch {source_theorems}!={inv_theorems}')
    new = [d for d in inv['declarations'] if d['module']==NEW_MODULE]
    if len(new) != 68:
        raise RuntimeError(f'expected 68 Block 30 declarations, found {len(new)}')
    if sum(d['kind']=='theorem' for d in new) != 44:
        raise RuntimeError('expected 44 Block 30 theorems')
    audit_names = re.findall(r'^#print axioms (\S+)$',
        (ROOT/'AuditBlock30.lean').read_text(), re.M)
    if audit_names != [d['name'] for d in new]:
        raise RuntimeError('AuditBlock30 mismatch')
    if 'public import '+NEW_MODULE not in (ROOT/'KomorebiPhysics.lean').read_text():
        raise RuntimeError('top-level import missing')
    if 'version = "0.30.0"' not in (ROOT/'lakefile.toml').read_text():
        raise RuntimeError('lakefile version mismatch')

    parent_errors = []
    for rel, expected in parent_hashes['sha256'].items():
        p = ROOT/rel
        got = sha256(p) if p.is_file() else None
        if got != expected:
            parent_errors.append({'file': rel, 'expected': expected, 'got': got})
    if parent_errors:
        raise RuntimeError(f'v0.29 parent changed: {parent_errors[:5]}')

    version = subprocess.check_output([str(lean),'--version'], env=env, text=True).strip()
    mathlib = subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),
        'rev-parse','HEAD'], text=True).strip()
    if EXPECTED_LEAN not in version: raise RuntimeError('Lean pin mismatch: '+version)
    if mathlib != EXPECTED_MATHLIB: raise RuntimeError('Mathlib pin mismatch: '+mathlib)

    # Import the completed one-worker warnings-as-errors gate.  It is not rerun
    # here because replaying the cumulative build can exceed an outer tool window.
    cum_receipt_path = ROOT/'verification/block30_cumulative_one_worker/receipt.json'
    cum_log_path = ROOT/'verification/block30_cumulative_one_worker/build.log'
    cum = json.loads(cum_receipt_path.read_text())
    cum_text = cum_log_path.read_text()
    if (cum.get('status') != 'PASS' or cum.get('returncode') != 0 or
        cum.get('command') != ['lake','-Kjobs=1','--wfail','build'] or
        cum.get('log_sha256') != sha256(cum_log_path) or
        cum.get('terminal_line') not in cum_text):
        raise RuntimeError('cumulative one-worker receipt is invalid')
    imported_log = out/'cumulative_one_worker_warnings_as_errors.log'
    imported_log.write_text(cum_text)
    checks.append({'label':'cumulative_one_worker_warnings_as_errors',
        'argv':cum['command'],'returncode':0,'timed_out':False,
        'seconds':cum['seconds'],'expected_failure':False,'diagnostic':None,
        'status':'PASS','log':str(imported_log.relative_to(ROOT)),
        'log_sha256':sha256(imported_log),'imported_receipt':str(cum_receipt_path.relative_to(ROOT))})
    run('build_block30_import_closure',
        [lake,'-Kjobs=16','--wfail','build','+'+NEW_MODULE], timeout=1200)
    run('compile_block30_warning_as_error',
        [lake,'env','lean','-DwarningAsError=true',
         'KomorebiPhysics/Relativistic3DCombinedDefect.lean'])
    run('compile_block30_api',
        [lake,'env','lean','-DwarningAsError=true','CheckBlock30API.lean'])
    audit_text = run('audit_block30', [lake,'env','lean','AuditBlock30.lean'], timeout=900)
    observed = set()
    for m in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]', audit_text, re.S):
        observed.update(x.strip() for x in m.group(1).replace('\n',' ').split(',') if x.strip())
    if not observed <= ALLOWED_AXIOMS:
        raise RuntimeError('unexpected axioms: '+repr(sorted(observed-ALLOWED_AXIOMS)))

    negatives=[]
    for p in sorted((ROOT/'negative_controls/block30').glob('*.lean')):
        diag=NEG_DIAGNOSTICS[p.stem]
        text=run('negative_'+p.stem,[lake,'env','lean','-DwarningAsError=true',p],
            expected_failure=True,diagnostic=diag,timeout=300)
        excerpts=[line for line in text.splitlines() if 'error:' in line or '⊢' in line]
        negatives.append({'file':str(p.relative_to(ROOT)),
            'diagnostic_excerpt':excerpts[:5] or [diag]})
    if len(negatives)!=3:
        raise RuntimeError(f'expected 3 negative controls, got {len(negatives)}')

    proof_inputs=[ROOT/(NEW_MODULE.replace('.','/')+'.lean'),ROOT/'KomorebiPhysics.lean',
        ROOT/'AuditBlock30.lean',ROOT/'CheckBlock30API.lean',ROOT/'declaration_inventory.json',
        ROOT/'reference/block29_declaration_inventory.json',
        ROOT/'reference/block29_production_report.json',ROOT/'reference/block29_source_hashes.json',
        ROOT/'verification/block30_inventory_summary.json',ROOT/'lakefile.toml',ROOT/'lean-toolchain',
        ROOT/'lake-manifest.json',Path(__file__),ROOT/'scripts/refresh_block30_inventory.py',
        ROOT/'verification/block30_cumulative_one_worker/receipt.json',
        ROOT/'verification/block30_cumulative_one_worker/build.log']
    proof_inputs += sorted((ROOT/'negative_controls/block30').glob('*.lean'))
    source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in proof_inputs}
    finished=datetime.now(timezone.utc)
    parent_negative=parent_report['negative_controls']['cumulative_evidence_total']
    report={
      'schema':'komorebi.physics.block30.verification.v1','status':'PASS',
      'started_utc':started.isoformat(),'finished_utc':finished.isoformat(),
      'seconds':round((finished-started).total_seconds(),4),
      'release':'Komorebi Physics Lean v0.30.0 — Checked Block 30',
      'verification_mode':'cumulative one-worker build plus fresh Block 30 audit',
      'claim_contract':{
        'proved':('Finite-lattice Clifford shifts, phase-frame embeddings, and arbitrary half-link '
          'defects are packaged as continuous linear operators.  The full factorwise seven-factor '
          'straight-refinement defect is bounded by the sum of five actual spatial operator defects. '
          'Exact ordered edge reconstruction annihilates that defect independently of plaquette '
          'curvature.  A separate cubical gluing stage is controlled by a five-face curvature budget, '
          'and the composed two-stage defect is bounded by the sum of the edge and curvature budgets. '
          'Separate summability of the two scale-dependent budgets yields a single global limit and '
          'an explicit tail estimate.'),
        'not_proved':('No scalar sup-norm estimate reducing each straight operator defect to '
          'max |E_i-1| is established.  No mesh-scale decay law or concrete summability of the physical '
          'Clifford walk is proved.  No continuum Dirac convergence, dynamical gauge field equation, '
          'gravity, cosmology, or empirical claim is established.')},
      'trust_boundary':('All 68 Block 30 declarations were kernel-checked against the pinned '
        'Lean/Mathlib cache. The cumulative active project passed a one-worker warnings-as-errors build. '
        'The 128 v0.29 modules are inherited only after byte-for-byte source comparison with the frozen '
        'Block 29 ledger. Lean and Mathlib were not rebuilt from compiler source.'),
      'lean_version':version,'mathlib_revision':mathlib,'checks':checks,
      'counts':{'active_modules':len(inv['modules']),'parent_modules':len(parent_inv['modules']),
        'new_modules':1,'total_theorems':inv_theorems,'audited_declarations':len(inv['declarations']),
        'new_theorems':sum(d['kind']=='theorem' for d in new),
        'new_audited_declarations':len(new),
        'new_by_kind':{k:sum(d['kind']==k for d in new) for k in sorted({d['kind'] for d in new})}},
      'source_precheck':{'status':'PASS','new_active_files_scanned':len(active),
        'prohibited_tokens_found':0,'cumulative_source_theorem_count':source_theorems},
      'axiom_audit':{'status':'PASS','allowed':sorted(ALLOWED_AXIOMS),
        'observed':sorted(observed),'declarations_checked':len(new)},
      'negative_controls':{'status':'PASS','new_passed':len(negatives),'new_total':len(negatives),
        'controls':negatives,'parent_inherited_evidence':parent_negative,
        'cumulative_evidence_total':parent_negative+len(negatives)},
      'parent_preservation':{'status':'PASS','modules_compared':parent_hashes['count'],
        'changed_modules':0,'ledger_sha256':sha256(ROOT/'reference/block29_source_hashes.json'),
        'reference_report_sha256':sha256(ROOT/'reference/block29_production_report.json'),
        'parent_cumulative_build_status':parent_report.get('status')},
      'excluded_attempts':[
        {'kind':'portable_runtime_initial_extraction','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted; extraction later completed and runtime pin was verified'},
        {'kind':'cold_parent_one_worker_build','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted; Block 29 import closure later completed successfully'},
        {'kind':'cold_parent_one_worker_build_retry','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted'},
        {'kind':'initial_v030_one_worker_build','status':'INCONCLUSIVE_TIMEOUT',
         'claim_effect':'not counted; final one-worker gate supersedes it'}],
      'source_sha256':source_hashes}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'PASS','report':str(out/'report.json'),
      'counts':report['counts'],'axioms':sorted(observed),
      'negative_controls':len(negatives),'parent_preservation':report['parent_preservation']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
