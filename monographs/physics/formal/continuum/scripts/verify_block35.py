#!/usr/bin/env python3
"""Cumulative verification for Komorebi Physics v0.35.0 / Block 35.

The 133 checked v0.34 mathematical modules are inherited only after
byte-for-byte source comparison with the frozen Block 34 ledger and validation
of the frozen Block 34 PASS report.  Block 35 and its complete import closure
are rebuilt, warning-checked, API-checked, declaration-audited, and tested
against three mathematical negative controls.

The verifier performs a terminal cumulative top-level build in addition to the
focused Block 35 import-closure, API, axiom, and negative-control gates. Parent
source preservation remains checked independently against the frozen v0.34
ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KIT = Path('/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2')
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEW_MODULE = 'KomorebiPhysics.Relativistic3DL2CellReconstruction'
EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
EXPECTED_MODULES = 134
EXPECTED_PARENT_MODULES = 133
EXPECTED_NEW_DECLARATIONS = 28
EXPECTED_NEW_THEOREMS = 20
PROHIBITED = re.compile(
    r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b'
    r'|skipKernelTC|#eval|#run'
)
NEG_DIAGNOSTICS = {
    'FalseAveragingNotLeftInverse': 'error:',
    'FalseResidualInnerOne': 'error:',
    'FalseProjectionNormAboveOne': 'error:',
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--kit', type=Path, default=DEFAULT_KIT)
    parser.add_argument('--out', type=Path, default=ROOT / 'verification/block35_final')
    parser.add_argument('--timeout', type=int, default=1800)
    args = parser.parse_args()

    kit = args.kit.resolve()
    lake = kit / 'toolchain/bin/lake'
    lean = kit / 'toolchain/bin/lean'
    if not lake.is_file() or not lean.is_file():
        raise FileNotFoundError(f'pinned Lean kit incomplete: {kit}')

    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    checks: list[dict] = []
    env = os.environ.copy()
    env['PATH'] = str(kit / 'toolchain/bin') + os.pathsep + env.get('PATH', '')
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT'):
        env.pop(key, None)

    def run(
        label: str,
        argv: list[object],
        *,
        expected_failure: bool = False,
        diagnostic: str | None = None,
        timeout: int | None = None,
        run_env: dict[str, str] | None = None,
    ) -> str:
        print(f'VERIFIER_START {label}', flush=True)
        t0 = time.monotonic()
        log = out / f'{label}.log'
        timed_out = False
        rc: int | None = None
        with log.open('w', encoding='utf-8') as handle:
            try:
                proc = subprocess.run(
                    [str(x) for x in argv],
                    cwd=ROOT,
                    env=run_env or env,
                    text=True,
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                    timeout=timeout or args.timeout,
                )
                rc = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                handle.write('\nVERIFIER_TIMEOUT\n')
        text = log.read_text(encoding='utf-8', errors='replace')
        if expected_failure:
            lower = text.lower()
            ok = (
                not timed_out
                and rc not in (0, None)
                and diagnostic is not None
                and diagnostic in text
                and 'unknown module prefix' not in lower
                and 'object file' not in lower
                and 'no such file or directory' not in lower
            )
        else:
            ok = not timed_out and rc == 0
        record = {
            'label': label,
            'argv': [str(x) for x in argv],
            'returncode': rc,
            'timed_out': timed_out,
            'seconds': round(time.monotonic() - t0, 4),
            'expected_failure': expected_failure,
            'diagnostic': diagnostic,
            'status': 'PASS' if ok else 'FAIL',
            'log': str(log.relative_to(ROOT)),
            'log_sha256': sha256(log),
        }
        checks.append(record)
        print(f'VERIFIER_END {label} {record["status"]} {record["seconds"]}s', flush=True)
        if not ok:
            raise RuntimeError(f'{label} failed; see {log}')
        return text

    inventory_path = ROOT / 'declaration_inventory.json'
    parent_inventory_path = ROOT / 'reference/block34_declaration_inventory.json'
    parent_report_path = ROOT / 'reference/block34_production_report.json'
    parent_hashes_path = ROOT / 'reference/block34_source_hashes.json'
    inventory = json.loads(inventory_path.read_text())
    parent_inventory = json.loads(parent_inventory_path.read_text())
    parent_report = json.loads(parent_report_path.read_text())
    parent_hashes = json.loads(parent_hashes_path.read_text())

    if parent_report.get('status') != 'PASS':
        raise RuntimeError('frozen v0.34 parent report is not PASS')
    if len(inventory['modules']) != EXPECTED_MODULES:
        raise RuntimeError(
            f"expected {EXPECTED_MODULES} modules, found {len(inventory['modules'])}"
        )
    if len(parent_inventory['modules']) != EXPECTED_PARENT_MODULES:
        raise RuntimeError(
            f"expected {EXPECTED_PARENT_MODULES} parent modules, "
            f"found {len(parent_inventory['modules'])}"
        )
    if parent_hashes.get('count') != EXPECTED_PARENT_MODULES:
        raise RuntimeError('parent source-hash ledger count mismatch')
    if NEW_MODULE not in inventory['modules'] or NEW_MODULE in parent_inventory['modules']:
        raise RuntimeError('new-module membership mismatch')

    declaration_names = [d['name'] for d in inventory['declarations']]
    if len(declaration_names) != len(set(declaration_names)):
        raise RuntimeError('duplicate declaration names in inventory')

    module_files = [ROOT / (m.replace('.', '/') + '.lean') for m in inventory['modules']]
    active_files = [
        ROOT / (NEW_MODULE.replace('.', '/') + '.lean'),
        ROOT / 'KomorebiPhysics.lean',
        ROOT / 'AuditBlock35.lean',
        ROOT / 'CheckBlock35API.lean',
    ]
    prohibited_hits = []
    for path in active_files:
        if not path.is_file():
            raise FileNotFoundError(path)
        match = PROHIBITED.search(strip_comments_and_strings(path.read_text()))
        if match:
            prohibited_hits.append(
                {'file': str(path.relative_to(ROOT)), 'token': match.group(0)}
            )
    if prohibited_hits:
        raise RuntimeError(f'prohibited active tokens: {prohibited_hits[:10]}')

    source_theorems = sum(
        len(re.findall(r'\btheorem\s+', strip_comments_and_strings(path.read_text())))
        for path in module_files
    )
    inventory_theorems = sum(
        declaration['kind'] == 'theorem' for declaration in inventory['declarations']
    )
    if source_theorems != inventory_theorems:
        raise RuntimeError(
            f'theorem count mismatch: source {source_theorems}, inventory {inventory_theorems}'
        )

    new_declarations = [
        declaration
        for declaration in inventory['declarations']
        if declaration['module'] == NEW_MODULE
    ]
    new_theorems = sum(d['kind'] == 'theorem' for d in new_declarations)
    if len(new_declarations) != EXPECTED_NEW_DECLARATIONS:
        raise RuntimeError(
            f'expected {EXPECTED_NEW_DECLARATIONS} Block 35 declarations, '
            f'found {len(new_declarations)}'
        )
    if new_theorems != EXPECTED_NEW_THEOREMS:
        raise RuntimeError(
            f'expected {EXPECTED_NEW_THEOREMS} Block 35 theorems, found {new_theorems}'
        )

    audit_path = ROOT / 'AuditBlock35.lean'
    audit_names = re.findall(r'^#print axioms (\S+)$', audit_path.read_text(), re.M)
    if audit_names != [d['name'] for d in new_declarations]:
        raise RuntimeError('AuditBlock35 declaration order/content mismatch')
    if f'public import {NEW_MODULE}' not in (ROOT / 'KomorebiPhysics.lean').read_text():
        raise RuntimeError('top-level Block 35 import missing')
    if 'version = "0.35.0"' not in (ROOT / 'lakefile.toml').read_text():
        raise RuntimeError('lakefile version mismatch')

    parent_errors = []
    for relative, expected_hash in parent_hashes['sha256'].items():
        path = ROOT / relative
        got_hash = sha256(path) if path.is_file() else None
        if got_hash != expected_hash:
            parent_errors.append(
                {'file': relative, 'expected': expected_hash, 'got': got_hash}
            )
    if parent_errors:
        raise RuntimeError(f'v0.34 parent source changed: {parent_errors[:5]}')

    lean_version = subprocess.check_output(
        [str(lean), '--version'], env=env, text=True
    ).strip()
    mathlib_revision = subprocess.check_output(
        ['git', '-C', str(kit / 'workspace/.lake/packages/mathlib'), 'rev-parse', 'HEAD'],
        text=True,
    ).strip()
    if EXPECTED_LEAN not in lean_version:
        raise RuntimeError(f'Lean pin mismatch: {lean_version}')
    if mathlib_revision != EXPECTED_MATHLIB:
        raise RuntimeError(f'Mathlib pin mismatch: {mathlib_revision}')

    project_lean_path = subprocess.check_output(
        [str(lake), 'env', 'printenv', 'LEAN_PATH'],
        cwd=ROOT,
        env=env,
        text=True,
    ).strip()
    lean_env = env.copy()
    lean_env['LEAN_PATH'] = project_lean_path

    run(
        'build_block35_import_closure',
        [lake, '-Kjobs=16', '--wfail', 'build', NEW_MODULE],
        timeout=1500,
    )
    run(
        'build_full_cumulative_project',
        [lake, '-Kjobs=16', '--wfail', 'build', 'KomorebiPhysics'],
        timeout=1800,
    )
    run(
        'compile_block35_warning_as_error',
        [lean, '-DwarningAsError=true',
            'KomorebiPhysics/Relativistic3DL2CellReconstruction.lean'],
        timeout=900,
        run_env=lean_env,
    )
    run(
        'compile_block35_api',
        [lean, '-DwarningAsError=true', 'CheckBlock35API.lean'],
        timeout=900,
        run_env=lean_env,
    )
    audit_text = run(
        'audit_block35',
        [lean, 'AuditBlock35.lean'],
        timeout=900,
        run_env=lean_env,
    )
    observed_axioms: set[str] = set()
    for match in re.finditer(r'depends on axioms:\s*\[([^\]]*)\]', audit_text, re.S):
        observed_axioms.update(
            item.strip()
            for item in match.group(1).replace('\n', ' ').split(',')
            if item.strip()
        )
    if not observed_axioms <= ALLOWED_AXIOMS:
        raise RuntimeError(
            f'unexpected axioms: {sorted(observed_axioms - ALLOWED_AXIOMS)}'
        )

    negative_records = []
    negative_dir = ROOT / 'negative_controls/block35'
    for path in sorted(negative_dir.glob('*.lean')):
        diagnostic = NEG_DIAGNOSTICS[path.stem]
        text = run(
            'negative_' + path.stem,
            [lean, '-DwarningAsError=true', path],
            expected_failure=True,
            diagnostic=diagnostic,
            timeout=300,
            run_env=lean_env,
        )
        excerpts = [
            line
            for line in text.splitlines()
            if 'error:' in line or '⊢' in line or 'Tactic' in line
        ]
        negative_records.append(
            {
                'file': str(path.relative_to(ROOT)),
                'diagnostic_excerpt': excerpts[:8] or [diagnostic],
            }
        )
    if len(negative_records) != 3:
        raise RuntimeError(
            f'expected 3 Block 35 negative controls, found {len(negative_records)}'
        )

    proof_inputs = [
        ROOT / (NEW_MODULE.replace('.', '/') + '.lean'),
        ROOT / 'KomorebiPhysics.lean',
        ROOT / 'AuditBlock35.lean',
        ROOT / 'CheckBlock35API.lean',
        inventory_path,
        parent_inventory_path,
        parent_report_path,
        parent_hashes_path,
        ROOT / 'verification/block35_inventory_summary.json',
        ROOT / 'lakefile.toml',
        ROOT / 'lean-toolchain',
        ROOT / 'lake-manifest.json',
        Path(__file__),
        ROOT / 'scripts/refresh_block35_inventory.py',
    ]
    proof_inputs += sorted(negative_dir.glob('*.lean'))
    source_hashes = {
        str(path.relative_to(ROOT)): sha256(path) for path in proof_inputs
    }

    finished = datetime.now(timezone.utc)
    parent_negative_total = parent_report['negative_controls'][
        'cumulative_evidence_total'
    ]
    report = {
        'schema': 'komorebi.physics.block35.verification.v1',
        'status': 'PASS',
        'started_utc': started.isoformat(),
        'finished_utc': finished.isoformat(),
        'seconds': round((finished - started).total_seconds(), 4),
        'release': 'Komorebi Physics Lean v0.35.0 — Checked Block 35',
        'verification_mode': (
            'full cumulative top-level build plus frozen checked v0.34 parent, '
            'byte-identical parent sources, and focused Block 35 audit'
        ),
        'claim_contract': {
            'proved': (
                'For any finite family of pairwise-disjoint measurable unit-volume cells '
                'covering a measure space, cell-normalized amplitudes admit an exact linear '
                'isometry into genuine L2 by finite step interpolation.  Its Hilbert adjoint '
                'is proved coordinatewise to be the Bochner integral over each cell.  The '
                'reconstruction-average composite is an idempotent self-adjoint orthogonal '
                'projection, is contractive, satisfies an exact Pythagorean decomposition, '
                'and minimizes L2 error over the finite step subspace.  For a sequence of '
                'such finite cell systems, convergence of any step approximants implies '
                'convergence of the corresponding orthogonal projections.'
            ),
            'not_proved': (
                'The block uses unit-volume cells and does not yet construct a specific '
                'three-dimensional dyadic cubical partition, prove density of the union of '
                'those dyadic step subspaces, or identify the finite Clifford lattice states '
                'with one named continuum L2(R^3,C^4) hierarchy.  It does not prove generator '
                'consistency or convergence of discrete propagators to the continuum Dirac '
                'evolution.  Gauge dynamics, emergent geometry, gravity, cosmology, and '
                'empirical predictions remain outside this theorem.'
            ),
        },
        'trust_boundary': (
            'All 28 Block 35 declarations were kernel-checked against the pinned Lean/Mathlib '
            'cache, and the complete Block 35 import closure was rebuilt.  The 133 v0.34 '
            'mathematical modules are inherited only after byte-for-byte source comparison '
            'with the frozen Block 34 ledger and validation of its PASS report.  Lean and '
            'Mathlib were not rebuilt from compiler source.'
        ),
        'lean_version': lean_version,
        'mathlib_revision': mathlib_revision,
        'checks': checks,
        'counts': {
            'active_modules': len(inventory['modules']),
            'parent_modules': len(parent_inventory['modules']),
            'new_modules': 1,
            'total_theorems': inventory_theorems,
            'audited_declarations': len(inventory['declarations']),
            'new_theorems': new_theorems,
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
            'cumulative_source_theorem_count': source_theorems,
        },
        'axiom_audit': {
            'status': 'PASS',
            'allowed': sorted(ALLOWED_AXIOMS),
            'observed': sorted(observed_axioms),
            'declarations_checked': len(new_declarations),
        },
        'negative_controls': {
            'status': 'PASS',
            'new_passed': len(negative_records),
            'new_total': len(negative_records),
            'controls': negative_records,
            'parent_inherited_evidence': parent_negative_total,
            'cumulative_evidence_total': parent_negative_total + len(negative_records),
        },
        'parent_preservation': {
            'status': 'PASS',
            'modules_compared': parent_hashes['count'],
            'changed_modules': 0,
            'ledger_sha256': sha256(parent_hashes_path),
            'reference_report_sha256': sha256(parent_report_path),
            'parent_report_status': parent_report.get('status'),
            'parent_verification_mode': parent_report.get('verification_mode'),
        },
        'excluded_attempts': [
            {
                'kind': 'initial_parent_import_closure_build',
                'status': 'INCONCLUSIVE_TIMEOUT_AFTER_2745_OF_2748_JOBS',
                'claim_effect': (
                    'not counted; the first parent-target build exceeded the outer window. '
                    'The preserved cache was resumed and the remaining three jobs completed '
                    'with a terminal successful build receipt.'
                ),
            },
            {
                'kind': 'unit_interval_example_elaboration',
                'status': 'DEFERRED_SCOPE',
                'claim_effect': (
                    'not counted; an optional concrete unit-interval witness increased '
                    'elaboration cost and was removed.  The checked theorem remains fully '
                    'quantified over measure spaces satisfying the explicit partition contract.'
                ),
            },
            {
                'kind': 'general_nonunit_cell_normalization',
                'status': 'NOT_ATTEMPTED_IN_FINAL_SCOPE',
                'claim_effect': (
                    'not claimed; Block 35 uses unit-volume cell normalization.  General '
                    'cell-volume weights and a concrete dyadic cubical family remain explicit '
                    'next-block obligations.'
                ),
            },
        ],
        'source_sha256': source_hashes,
    }
    report_path = out / 'report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(
        json.dumps(
            {
                'status': 'PASS',
                'report': str(report_path),
                'counts': report['counts'],
                'axioms': sorted(observed_axioms),
                'negative_controls': len(negative_records),
                'parent_preservation': report['parent_preservation'],
            },
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
