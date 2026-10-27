#!/usr/bin/env python3
"""Verify Komorebi Physics v0.26.0 / checked Block 26.

The 124 v0.25 mathematical modules are inherited only after byte-for-byte
source-hash comparison.  The new Block 26 module is rebuilt and audited against
the exact pinned Lean/Mathlib cache.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KIT = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULE = 'KomorebiPhysics.Relativistic3DGeometricEdgeRefinement'
EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
PROHIBITED = re.compile(
    r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b'
    r'|skipKernelTC|#eval|#run'
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', type=Path, default=DEFAULT_KIT)
    ap.add_argument('--out', type=Path, default=ROOT / 'verification/block26_final')
    ap.add_argument('--timeout', type=int, default=900)
    args = ap.parse_args()

    kit = args.kit.resolve()
    lake = kit / 'toolchain/bin/lake'
    lean = kit / 'toolchain/bin/lean'
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    checks: list[dict] = []

    def run(label: str, argv: list[str | Path], *, expected_failure: bool = False,
            diagnostic: str | None = None, timeout: int | None = None) -> str:
        t0 = time.monotonic()
        result = subprocess.run(
            [str(x) for x in argv], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=timeout or args.timeout,
        )
        text = result.stdout
        log = out / f'{label}.log'
        log.write_text(text)
        if expected_failure:
            ok = (
                result.returncode != 0
                and diagnostic is not None
                and diagnostic in text
                and 'unknown module prefix' not in text
                and 'object file' not in text
                and 'no such file or directory' not in text
            )
        else:
            ok = result.returncode == 0
        rec = {
            'label': label,
            'argv': [str(x) for x in argv],
            'returncode': result.returncode,
            'seconds': round(time.monotonic() - t0, 4),
            'expected_failure': expected_failure,
            'diagnostic': diagnostic,
            'status': 'PASS' if ok else 'FAIL',
            'log': str(log.relative_to(ROOT)),
            'log_sha256': sha256(log),
        }
        checks.append(rec)
        if not ok:
            raise RuntimeError(f'{label} failed its verification contract; see {log}')
        return text

    inventory = json.loads((ROOT / 'declaration_inventory.json').read_text())
    parent_inventory = json.loads((ROOT / 'reference/block25_declaration_inventory.json').read_text())
    parent_report = json.loads((ROOT / 'reference/block25_production_report.json').read_text())

    if len(inventory['modules']) != 125:
        raise RuntimeError(f"expected 125 modules, found {len(inventory['modules'])}")
    names = [d['name'] for d in inventory['declarations']]
    if len(names) != len(set(names)):
        raise RuntimeError('duplicate names in declaration inventory')

    # Source trust precheck.
    module_files = [ROOT / (m.replace('.', '/') + '.lean') for m in inventory['modules']]
    active_files = module_files + [ROOT / 'KomorebiPhysics.lean', ROOT / 'Audit.lean', ROOT / 'AuditBlock26.lean']
    prohibited_hits = []
    for path in active_files:
        if not path.is_file():
            raise FileNotFoundError(path)
        clean = strip_comments_and_strings(path.read_text())
        hit = PROHIBITED.search(clean)
        if hit:
            prohibited_hits.append({'file': str(path.relative_to(ROOT)), 'token': hit.group(0)})
    if prohibited_hits:
        raise RuntimeError('prohibited active tokens: ' + repr(prohibited_hits))

    theorem_count = sum(
        len(re.findall(r'\btheorem\s+', strip_comments_and_strings(path.read_text())))
        for path in module_files
    )
    inventory_theorems = sum(d['kind'] == 'theorem' for d in inventory['declarations'])
    if theorem_count != inventory_theorems:
        raise RuntimeError(f'theorem count mismatch: source={theorem_count}, inventory={inventory_theorems}')

    new_declarations = [d for d in inventory['declarations'] if d['module'] == NEW_MODULE]
    audit_names = re.findall(r'^#print axioms (\S+)$', (ROOT / 'AuditBlock26.lean').read_text(), re.M)
    if audit_names != [d['name'] for d in new_declarations]:
        raise RuntimeError('AuditBlock26.lean does not exactly match the new declaration inventory')

    # Byte identity against the checked v0.25 parent.
    parent_errors = []
    for mod in parent_inventory['modules']:
        rel = mod.replace('.', '/') + '.lean'
        got = sha256(ROOT / rel)
        expected = parent_report['source_sha256'][rel]
        if got != expected:
            parent_errors.append({'module': mod, 'expected': expected, 'got': got})
    if parent_errors:
        raise RuntimeError('v0.25 parent module changed: ' + repr(parent_errors[:5]))

    version = subprocess.check_output([str(lean), '--version'], text=True).strip()
    mathlib = subprocess.check_output(
        ['git', '-C', str(kit / 'workspace/.lake/packages/mathlib'), 'rev-parse', 'HEAD'],
        text=True,
    ).strip()
    if EXPECTED_LEAN not in version:
        raise RuntimeError('Lean pin mismatch: ' + version)
    if mathlib != EXPECTED_MATHLIB:
        raise RuntimeError('Mathlib pin mismatch: ' + mathlib)

    # Kernel/build gates.
    run('cumulative_build', [lake, '-q', 'build', 'KomorebiPhysics'], timeout=1200)
    run('top_warning_as_error', [lake, 'env', 'lean', '-DwarningAsError=true', 'KomorebiPhysics.lean'])
    run('compile_block26_warning_as_error', [
        lake, 'env', 'lean', '-DwarningAsError=true',
        'KomorebiPhysics/Relativistic3DGeometricEdgeRefinement.lean',
    ])
    audit_text = run('audit_block26', [lake, 'env', 'lean', 'AuditBlock26.lean'])

    observed: set[str] = set()
    for match in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]', audit_text, re.S):
        observed.update(
            item.strip() for item in match.group(1).replace('\n', ' ').split(',') if item.strip()
        )
    if not observed <= ALLOWED_AXIOMS:
        raise RuntimeError('unexpected axioms: ' + repr(sorted(observed - ALLOWED_AXIOMS)))

    negatives = []
    for path in sorted((ROOT / 'negative_controls/block26').glob('*.lean')):
        text = run(
            'negative_' + path.stem,
            [lake, 'env', 'lean', path],
            expected_failure=True,
            diagnostic='unsolved goals',
            timeout=300,
        )
        negatives.append({
            'file': str(path.relative_to(ROOT)),
            'diagnostic': next((line for line in text.splitlines() if 'error:' in line), 'unsolved goals'),
        })

    proof_inputs = list(module_files)
    proof_inputs += [
        ROOT / 'KomorebiPhysics.lean', ROOT / 'Audit.lean', ROOT / 'AuditBlock26.lean',
        ROOT / 'declaration_inventory.json', ROOT / 'reference/block25_declaration_inventory.json',
        ROOT / 'reference/block25_production_report.json',
        ROOT / 'verification/block25_parent_preservation.json',
        ROOT / 'verification/block26_inventory_summary.json',
        ROOT / 'lakefile.toml', ROOT / 'lean-toolchain', ROOT / 'lake-manifest.json',
        Path(__file__),
    ]
    proof_inputs += sorted((ROOT / 'negative_controls/block26').glob('*.lean'))
    source_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in proof_inputs}

    finished = datetime.now(timezone.utc)
    inherited_negatives = parent_report['negative_controls']['cumulative_evidence_total']
    report = {
        'schema': 'komorebi.physics.block26.verification.v1',
        'status': 'PASS',
        'started_utc': started.isoformat(),
        'finished_utc': finished.isoformat(),
        'seconds': round((finished - started).total_seconds(), 4),
        'release': 'Komorebi Physics Lean v0.26.0 — Checked Block 26',
        'trust_boundary': (
            'The new Block 26 proof terms were rebuilt against the pinned Lean/Mathlib cache. '
            'The compiler and imported dependency cache were not rebuilt from source. The 124 '
            'v0.25 mathematical modules are inherited through byte-for-byte source preservation '
            'and a passing cumulative import/build.'
        ),
        'lean_version': version,
        'mathlib_revision': mathlib,
        'checks': checks,
        'counts': {
            'active_modules': len(inventory['modules']),
            'parent_modules': len(parent_inventory['modules']),
            'new_modules': 1,
            'total_theorems': inventory_theorems,
            'audited_declarations': len(inventory['declarations']),
            'new_theorems': sum(d['kind'] == 'theorem' for d in new_declarations),
            'new_audited_declarations': len(new_declarations),
            'new_by_kind': {
                kind: sum(d['kind'] == kind for d in new_declarations)
                for kind in sorted({d['kind'] for d in new_declarations})
            },
        },
        'source_precheck': {
            'status': 'PASS',
            'active_files_scanned': len(active_files),
            'prohibited_tokens_found': 0,
            'source_theorem_count': theorem_count,
        },
        'axiom_audit': {
            'status': 'PASS',
            'new_declarations_checked': len(new_declarations),
            'allowed': sorted(ALLOWED_AXIOMS),
            'observed': sorted(observed),
        },
        'negative_controls': {
            'status': 'PASS',
            'new_passed': len(negatives),
            'new_total': len(negatives),
            'controls': negatives,
            'parent_inherited_evidence': inherited_negatives,
            'cumulative_evidence_total': inherited_negatives + len(negatives),
        },
        'parent_preservation': {
            'status': 'PASS',
            'modules_checked': len(parent_inventory['modules']),
            'modules_preserved': len(parent_inventory['modules']),
            'parent_source_archive_sha256': parent_report.get('source_archive_sha256')
                or parent_report.get('archive_sha256')
                or '43d8883d46d488843a1d35b80d7a5ce621f9934a84dcaf9ac5a2fdbbcf716d66',
        },
        'source_sha256': source_hashes,
    }
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'verification/block26_source_precheck.json').write_text(json.dumps(report['source_precheck'], indent=2) + '\n')
    (ROOT / 'verification/block26_negative_controls.json').write_text(json.dumps(report['negative_controls'], indent=2) + '\n')
    (ROOT / 'verification/block26_axiom_audit.json').write_text(json.dumps(report['axiom_audit'], indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'counts': report['counts'], 'seconds': report['seconds']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
