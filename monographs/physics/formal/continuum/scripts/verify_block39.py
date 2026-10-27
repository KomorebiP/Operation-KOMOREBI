#!/usr/bin/env python3
"""Verify Block 39 against the frozen checked v0.38 predecessor."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
OUT = ROOT / 'verification' / 'block39' / 'production'
OUT.mkdir(parents=True, exist_ok=True)

CHECKS = [
    ('module_build', ['lake','-d',str(ROOT),'build','KomorebiPhysics.Relativistic3DEuclideanDyadicProjection'], False),
    ('source_warning_as_error', ['lake','-d',str(ROOT),'env','lean','-DwarningAsError=true',str(ROOT/'KomorebiPhysics/Relativistic3DEuclideanDyadicProjection.lean')], False),
    ('top_build', ['lake','-d',str(ROOT),'build','KomorebiPhysics'], False),
    ('api', ['lake','-d',str(ROOT),'env','lean','-DwarningAsError=true',str(ROOT/'verification/block39/CheckBlock39API.lean')], False),
    ('axioms', ['lake','-d',str(ROOT),'env','lean',str(ROOT/'verification/block39/AuditBlock39.lean')], False),
    ('negative_adjoint_zero', ['lake','-d',str(ROOT),'env','lean',str(ROOT/'negative_controls/block39/FalseAdjointAnnihilatesPullback.lean')], True),
    ('negative_projection_zero_norm', ['lake','-d',str(ROOT),'env','lean',str(ROOT/'negative_controls/block39/FalseProjectionExpandsZero.lean')], True),
    ('negative_strong_limit_zero', ['lake','-d',str(ROOT),'env','lean',str(ROOT/'negative_controls/block39/FalseStrongLimitZero.lean')], True),
]
FORBIDDEN = {
    'sorry': re.compile(r'(?m)^\s*sorry\b|\bsorryAx\b'),
    'admit': re.compile(r'(?m)^\s*admit\b'),
    'custom_axiom': re.compile(r'(?m)^\s*axiom\b'),
    'native_decide': re.compile(r'\bnative_decide\b'),
    'unsafe': re.compile(r'(?m)^\s*unsafe\b'),
}
ALLOWED_AXIOMS = {'propext','Classical.choice','Quot.sound'}

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def run(label, args, expected_failure):
    log=OUT/f'{label}.log'
    argv=['bash',str(RUNTIME/'run.sh'),args[0],*args[1:]]
    t=time.time()
    proc=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_bytes(proc.stdout)
    passed=(proc.returncode!=0) if expected_failure else (proc.returncode==0)
    return {
      'label':label,'argv':argv,'returncode':proc.returncode,
      'expected_failure':expected_failure,'passed':passed,
      'elapsed_seconds':round(time.time()-t,6),
      'log':str(log.relative_to(ROOT)),'log_sha256':sha(log),
    }

def parse_axioms(text: str):
    found=set()
    # Lean prints either `[propext, Classical.choice, Quot.sound]` or `[]`.
    for body in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', text):
        for item in body.split(','):
            item=item.strip()
            if item: found.add(item)
    return sorted(found)

def main() -> int:
    records=[]; ok=True
    for label,args,expected in CHECKS:
        rec=run(label,args,expected); records.append(rec)
        print(f"{label}: {'PASS' if rec['passed'] else 'FAIL'} (rc={rec['returncode']})",flush=True)
        ok &= rec['passed']
        if not rec['passed']:
            break
    source=ROOT/'KomorebiPhysics/Relativistic3DEuclideanDyadicProjection.lean'
    text=source.read_text()
    hits={name:len(list(pat.finditer(text))) for name,pat in FORBIDDEN.items()}
    trust_pass=all(v==0 for v in hits.values()); ok &= trust_pass
    parent=json.loads((ROOT/'verification/block39/parent_preservation.json').read_text())
    parent_pass=bool(parent.get('all_identical')); ok &= parent_pass
    axiom_log=OUT/'axioms.log'
    found=parse_axioms(axiom_log.read_text(errors='replace')) if axiom_log.exists() else []
    axiom_pass=set(found)<=ALLOWED_AXIOMS
    ok &= axiom_pass
    inv=json.loads((ROOT/'verification/block39/inventory_summary.json').read_text())
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [
      source, ROOT/'KomorebiPhysics.lean', ROOT/'lakefile.toml',
      ROOT/'verification/block39/CheckBlock39API.lean',
      ROOT/'verification/block39/AuditBlock39.lean',
      ROOT/'negative_controls/block39/FalseAdjointAnnihilatesPullback.lean',
      ROOT/'negative_controls/block39/FalseProjectionExpandsZero.lean',
      ROOT/'negative_controls/block39/FalseStrongLimitZero.lean',
      ROOT/'declaration_inventory.json', ROOT/'verification/block39/parent_preservation.json',
    ]}
    report={
      'schema':'komorebi.physics.block39.production-verification.v1',
      'release':'Komorebi Physics Lean v0.39.0 — Checked Block 39',
      'status':'PASS' if ok else 'FAIL',
      'verification_mode':'modular cumulative verification against frozen checked v0.38 parent',
      'runtime':{'lean':'4.34.0-rc2','mathlib_rev':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'},
      'checks':records,
      'source_trust_scan':{'passed':trust_pass,'hits':hits},
      'axiom_audit':{'passed':axiom_pass,'observed':found,'allowed':sorted(ALLOWED_AXIOMS)},
      'parent_preservation':{'passed':parent_pass,'parent_module_count':parent.get('parent_module_count')},
      'counts':inv,
      'source_sha256':source_hashes,
    }
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/block39/Production_Verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if ok else 1

if __name__=='__main__': sys.exit(main())
