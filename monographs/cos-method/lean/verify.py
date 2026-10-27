#!/usr/bin/env python3
"""Build and audit the scoped companion with an installed pinned Lean toolchain."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'verification'
OUT.mkdir(exist_ok=True)


def checked(command, log_name, expected=0):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (OUT / log_name).write_text(result.stdout + result.stderr)
    if result.returncode != expected:
        raise RuntimeError(f'{command!r} returned {result.returncode}; expected {expected}; see verification/{log_name}')
    return {'command': command, 'exit_code': result.returncode, 'log': 'verification/' + log_name}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    checks.append(checked(['lake', 'build'], 'lean_build.log'))
    for module, stem in [('KomorebiQCOS/FiniteGram.lean', 'finite_gram'), ('KomorebiQCOS/Certificates.lean', 'certificates'), ('KomorebiQCOS.lean', 'root')]:
        check = checked(['lake', 'env', 'lean', module], stem + '_fresh_source.log')
        (OUT / (stem + '_fresh_source.exitcode')).write_text(str(check['exit_code']) + '\n')
        checks.append(check)
    checks.append(checked(['lake', 'env', 'lean', 'AxiomAudit.lean'], 'axiom_audit.log'))
    checks.append(checked(['lake', 'env', 'lean', 'verification/controls/PositiveControl.lean'], 'positive_control.log'))
    checks.append(checked(['lake', 'env', 'lean', 'verification/controls/FalseArithmetic.lean'], 'false_arithmetic_control.log', expected=1))
    checks.append(checked(['lake', 'env', 'lean', 'verification/controls/MissingBudget.lean'], 'missing_budget_control.log', expected=1))
    version = checked(['lake', 'env', 'lean', '--version'], 'lean_version.log')
    checks.append(version)
    version_text = (OUT / 'lean_version.log').read_text().strip()
    expected_commit = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
    if '4.34.0-rc2' not in version_text or expected_commit not in version_text:
        raise RuntimeError('Compiler version does not match lean-toolchain and expected official commit')
    manifest = json.loads((ROOT / 'lake-manifest.json').read_text())
    mathlib = next(p for p in manifest['packages'] if p['name'] == 'mathlib')
    expected_mathlib = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
    if mathlib['type'] != 'git' or mathlib['rev'] != expected_mathlib:
        raise RuntimeError('Mathlib manifest is not the expected portable pinned git revision')
    source_files = [ROOT / 'KomorebiQCOS.lean', *sorted((ROOT / 'KomorebiQCOS').glob('*.lean')), ROOT / 'AxiomAudit.lean']
    mathematical_sources = list((ROOT / 'KomorebiQCOS').glob('*.lean'))
    for path in source_files:
        if re.search(r'\b(?:sorry|admit|sorryAx)\b|(?m:^\s*axiom\s)', path.read_text()):
            raise RuntimeError(f'Admission or custom-axiom token in {path.relative_to(ROOT)}')
    axioms_text = (OUT / 'axiom_audit.log').read_text()
    dependencies = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", axioms_text)
    axiom_rows = [{'declaration': name, 'axioms': [s.strip() for s in ax.split(',') if s.strip()]} for name, ax in dependencies]
    expected_names = {d['name'] for d in json.loads((ROOT / 'Declaration_Inventory.json').read_text())['declarations']}
    if {r['declaration'] for r in axiom_rows} != expected_names:
        raise RuntimeError('Axiom audit declarations do not match exact project inventory')
    axiom_union = sorted({a for row in axiom_rows for a in row['axioms']})
    if set(axiom_union) - {'propext', 'Classical.choice', 'Quot.sound'}:
        raise RuntimeError(f'Unexpected axiom dependency: {axiom_union}')
    theorem_count = sum(len(re.findall(r'(?m)^(?:@\[simp\] )?theorem\b', f.read_text())) for f in mathematical_sources)
    def_count = sum(len(re.findall(r'(?m)^def\b', f.read_text())) for f in mathematical_sources)
    if theorem_count != 26 or def_count != 8:
        raise RuntimeError('Source declaration count changed; update inventory and guide deliberately')
    report = {
        'status': 'PASS',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': '26 exact finite-real algebra and arithmetic enclosure/error-budget theorems; 8 definitions; not an end-to-end engine or numerical certificate',
        'compiler': version_text,
        'mathlib_revision': expected_mathlib,
        'project_theorem_count': theorem_count,
        'project_definition_count': def_count,
        'audited_declaration_count': len(axiom_rows),
        'axiom_union': axiom_union,
        'sorryAx': False,
        'custom_axiom_declarations': False,
        'positive_control': 'accepted; no axioms',
        'negative_controls': ['false arithmetic rejected', 'missing error-budget acceptance premise rejected'],
        'checks': checks,
        'source_sha256': {str(f.relative_to(ROOT)): digest(f) for f in source_files},
        'evidence_sha256': {c['log']: digest(ROOT / c['log']) for c in checks},
        'axiom_dependencies': axiom_rows,
        'reproducibility_note': 'Compiler and mathlib cache excluded from publication ZIP. The producing environment used a narrow executable-self-location adapter; the official compiler and shared proof-kernel library match their archive members.'
    }
    (OUT / 'BUILD_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'project_theorem_count', 'project_definition_count', 'audited_declaration_count', 'axiom_union', 'sorryAx']}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('verification failed:', exc, file=sys.stderr)
        sys.exit(1)
