#!/usr/bin/env python3
"""Cumulative verification for Komorebi Physics v0.34.0 / Block 34.

The 132 checked v0.33 mathematical modules are inherited only after
byte-for-byte source comparison with the frozen Block 33 ledger and validation
of the frozen Block 33 PASS report.  Block 34 and its complete import closure
are rebuilt, warning-checked, API-checked, declaration-audited, and tested
against three mathematical negative controls.

A terminal monolithic rebuild of every unrelated parent module is not required
by this verifier.  Prior receipts remain frozen parent evidence, while all new
proof-bearing code and its complete dependency closure are rebuilt here.
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
NEW_MODULE = 'KomorebiPhysics.Relativistic3DRegularConnection'
EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
EXPECTED_MODULES = 133
EXPECTED_PARENT_MODULES = 132
EXPECTED_NEW_DECLARATIONS = 92
EXPECTED_NEW_THEOREMS = 58
PROHIBITED = re.compile(
    r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b'
    r'|skipKernelTC|#eval|#run'
)
NEG_DIAGNOSTICS = {
    'FalseSinusoidalCurvatureConstant': 'error:',
    'FalseRegularDyadicHalfRate': 'error:',
    'FalseZeroSinusoidalEnvelope': 'error:',
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
    parser.add_argument('--out', type=Path, default=ROOT / 'verification/block34_final')
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
        try:
            proc = subprocess.run(
                [str(x) for x in argv],
                cwd=ROOT,
                env=run_env or env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout or args.timeout,
            )
            text = proc.stdout
            rc: int | None = proc.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            text = (exc.stdout or '') + (exc.stderr or '')
            if isinstance(text, bytes):
                text = text.decode(errors='replace')
            rc = None
            timed_out = True

        log = out / f'{label}.log'
        log.write_text(text, encoding='utf-8')
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
    parent_inventory_path = ROOT / 'reference/block33_declaration_inventory.json'
    parent_report_path = ROOT / 'reference/block33_production_report.json'
    parent_hashes_path = ROOT / 'reference/block33_source_hashes.json'
    inventory = json.loads(inventory_path.read_text())
    parent_inventory = json.loads(parent_inventory_path.read_text())
    parent_report = json.loads(parent_report_path.read_text())
    parent_hashes = json.loads(parent_hashes_path.read_text())

    if parent_report.get('status') != 'PASS':
        raise RuntimeError('frozen v0.33 parent report is not PASS')
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
        ROOT / 'AuditBlock34.lean',
        ROOT / 'CheckBlock34API.lean',
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
            f'expected {EXPECTED_NEW_DECLARATIONS} Block 34 declarations, '
            f'found {len(new_declarations)}'
        )
    if new_theorems != EXPECTED_NEW_THEOREMS:
        raise RuntimeError(
            f'expected {EXPECTED_NEW_THEOREMS} Block 34 theorems, found {new_theorems}'
        )

    audit_path = ROOT / 'AuditBlock34.lean'
    audit_names = re.findall(r'^#print axioms (\S+)$', audit_path.read_text(), re.M)
    if audit_names != [d['name'] for d in new_declarations]:
        raise RuntimeError('AuditBlock34 declaration order/content mismatch')
    if f'public import {NEW_MODULE}' not in (ROOT / 'KomorebiPhysics.lean').read_text():
        raise RuntimeError('top-level Block 34 import missing')
    if 'version = "0.34.0"' not in (ROOT / 'lakefile.toml').read_text():
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
        raise RuntimeError(f'v0.33 parent source changed: {parent_errors[:5]}')

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
        'build_block34_import_closure',
        [lake, '-Kjobs=16', '--wfail', 'build', NEW_MODULE],
        timeout=1500,
    )
    run(
        'compile_block34_warning_as_error',
        [lean, '-DwarningAsError=true',
            'KomorebiPhysics/Relativistic3DRegularConnection.lean'],
        timeout=900,
        run_env=lean_env,
    )
    run(
        'compile_block34_api',
        [lean, '-DwarningAsError=true', 'CheckBlock34API.lean'],
        timeout=900,
        run_env=lean_env,
    )
    audit_text = run(
        'audit_block34',
        [lean, 'AuditBlock34.lean'],
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
    negative_dir = ROOT / 'negative_controls/block34'
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
            f'expected 3 Block 34 negative controls, found {len(negative_records)}'
        )

    proof_inputs = [
        ROOT / (NEW_MODULE.replace('.', '/') + '.lean'),
        ROOT / 'KomorebiPhysics.lean',
        ROOT / 'AuditBlock34.lean',
        ROOT / 'CheckBlock34API.lean',
        inventory_path,
        parent_inventory_path,
        parent_report_path,
        parent_hashes_path,
        ROOT / 'verification/block34_inventory_summary.json',
        ROOT / 'lakefile.toml',
        ROOT / 'lean-toolchain',
        ROOT / 'lake-manifest.json',
        Path(__file__),
        ROOT / 'scripts/refresh_block34_inventory.py',
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
        'schema': 'komorebi.physics.block34.verification.v1',
        'status': 'PASS',
        'started_utc': started.isoformat(),
        'finished_utc': finished.isoformat(),
        'seconds': round((finished - started).total_seconds(), 4),
        'release': 'Komorebi Physics Lean v0.34.0 — Checked Block 34',
        'verification_mode': (
            'modular cumulative verification: frozen checked v0.33 parent, '
            'byte-identical parent sources, and fresh Block 34 import-closure audit'
        ),
        'claim_contract': {
            'proved': (
                'For a coordinate-regular spatially varying abelian connection, exact '
                'coordinate-edge interval integrals generate U(1) links whose ordered '
                'half-edge products equal the full edge exactly.  Uniform bounds on the '
                'six cross-coordinate derivatives imply quadratic bounds for the three '
                'plaquette phases and therefore for the five-face cubical gluing budget. '
                'The actual connection-generated finite-site link triples have zero '
                'straight-edge budget, while the complete finite-Hilbert edge-plus-gluing '
                'defect is bounded by h^2 times an explicit derivative envelope.  On a '
                'dyadic mesh these operator defects decay with ratio 1/4, are summable, '
                'and instantiate the checked global-limit theorem.  A non-affine witness '
                'A_y(x)=sin(x), with varying curvature F_xy(x)=cos(x), is included.'
            ),
            'not_proved': (
                'The theorem assumes explicit one-dimensional differentiability and '
                'global bounds for the six cross-coordinate derivatives.  It gives a '
                'sufficient derivative-sum plaquette bound, not an exact general Stokes '
                'flux formula or a sharp bound solely by the curl.  It does not construct '
                'reconstruction into L2(R^3,C^4), identify the limit with the continuum '
                'Dirac propagator, or provide dynamical Maxwell/Yang-Mills equations.  No '
                'emergent geometry, gravity, cosmology, or empirical prediction is established.'
            ),
        },
        'trust_boundary': (
            'All 92 Block 34 declarations were kernel-checked against the pinned Lean/Mathlib '
            'cache, and the complete Block 34 import closure was rebuilt.  The 132 v0.33 '
            'mathematical modules are inherited only after byte-for-byte source comparison '
            'with the frozen Block 33 ledger and validation of its PASS report.  Lean and '
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
                'kind': 'initial_parent_cache_build',
                'status': 'INCONCLUSIVE_TIMEOUT',
                'claim_effect': (
                    'not counted; the first parent-target build reached its final jobs but '
                    'exceeded the outer command window.  A resumed import-closure build passed.'
                ),
            },
            {
                'kind': 'first_production_verifier_wrapper',
                'status': 'INCONCLUSIVE_OUTER_TIMEOUT_AFTER_BUILD_PASS',
                'claim_effect': (
                    'not counted as a complete verification run; its forced import-closure '
                    'build passed 2748 jobs, but the outer wrapper expired before the axiom '
                    'and negative-control gates.  Those gates were rerun in the final verifier.'
                ),
            },
            {
                'kind': 'full_v034_cumulative_build_attempts',
                'status': 'INCONCLUSIVE_TIMEOUT',
                'claim_effect': (
                    'not counted; three monolithic cumulative attempts rebuilt most parent '
                    'targets but did not emit terminal success receipts.  Parent proof evidence '
                    'is inherited only through the frozen PASS report and byte-identical source ledger.'
                ),
            },
            {
                'kind': 'sinusoidal_witness_elaboration_repairs',
                'status': 'IMPLEMENTATION_FAILURE_REPAIRED',
                'claim_effect': (
                    'not counted; constant-line continuity, a z-direction derivative, and the '
                    'qualified Real.abs_cos_le_one theorem were repaired before successful compilation.'
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
