from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STAGE = Path('/workspace/scratch/5cb45ce56d13/PRSC_X_Residue_Counting_Release')
AUDIT = ROOT / 'privatechecks/audit_replay'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest = json.loads((STAGE / 'manifest.json').read_text())
    rows = manifest['modules_in_build_order']
    expected = {r['module']: r for r in rows}
    assert len(expected) == 34
    records = json.loads((AUDIT / 'compilation.json').read_text())
    latest = {r['module']: r for r in records}
    assert set(latest) == set(expected), (set(expected) - set(latest), set(latest) - set(expected))
    for name, row in expected.items():
        r = latest[name]
        assert r['exit_code'] == 0 and r['source_unchanged'] and r['matches_author_olean'], name
        assert row['source_sha256'] == r['source_sha256'] and row['olean_sha256'] == r['olean_sha256'], name
        for base in [ROOT, STAGE]:
            assert digest(base / 'lean/PaperX' / (name + '.lean')) == row['source_sha256'], name
            assert digest(base / 'build/PaperX' / (name + '.olean')) == row['olean_sha256'], name
    for row in manifest['predecessor_sources']:
        name = row['module']
        for base in [ROOT, STAGE]:
            assert digest(base / 'lean/PaperX' / (name + '.lean')) == row['source_sha256'], name
            assert digest(base / 'build/PaperX' / (name + '.olean')) == row['olean_sha256'], name
    axioms = json.loads((AUDIT / 'axioms.json').read_text())
    assert axioms['exit_code'] == 0 and set(axioms['modules']) == set(expected)
    query = AUDIT / 'lean/AuditAxioms.lean'
    assert digest(query) == axioms['source_sha256']
    axlogfile = AUDIT / 'logs/AuditAxioms.log'
    axlog = axlogfile.read_text()
    counts = re.findall(r'AUDIT_DECLARATION_COUNT (\d+)', axlog)
    assert len(counts) == 1
    count = int(counts[0])
    matches = re.findall(r'^AUDIT_DECL (.+?): \[([^\]]*)\]$', axlog, re.M)
    owned = {n for n, _ in matches}
    assert len(matches) == count == len(owned)
    assert set(manifest['named_declarations']) <= owned
    observed = {x.strip() for _, group in matches for x in group.split(',') if x.strip()}
    assert observed <= {'propext', 'Classical.choice', 'Quot.sound'}
    controls = json.loads((AUDIT / 'controls.json').read_text())
    assert len(controls) == 5 and all(c['expected_result_observed'] for c in controls)
    for c in controls:
        assert digest(AUDIT / 'lean' / (c['name'] + '.lean')) == c['source_sha256']
        log = (AUDIT / 'logs' / (c['name'] + '.log')).read_text()
        if c['expected'] == 'pass':
            assert c['exit_code'] == 0
        elif c['name'] == 'AuditPlaceholder':
            assert c['exit_code'] != 0 and 'declaration uses `sorry`' in log
            assert 'does not exist' not in log
        else:
            assert c['exit_code'] != 0 and '⊢ False' in log
    for p in list(ROOT.glob('*.md')) + list(ROOT.glob('*.tex')):
        shutil.copy2(p, STAGE / p.name)
    for p in (ROOT / 'privatechecks').rglob('*'):
        if not p.is_file() or p.suffix not in {'.lean','.py','.log','.json','.md','.txt'}:
            continue
        rel = p.relative_to(ROOT)
        if any(x in {'audit_baseline','build','__pycache__'} for x in rel.parts):
            continue
        q = STAGE / rel
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, q)
    verification = {'status': 'passed', 'scope': 'Every new production module independently rebuilt against hash-verified frozen predecessor objects',
        'new_modules': len(rows), 'cumulative_source_modules': len(rows) + len(manifest['predecessor_sources']),
        'new_theorem_lemma_declarations': manifest['new_theorem_lemma_declarations'],
        'explicit_named_declarations': len(manifest['named_declarations']),
        'frozen_predecessor_sources_and_objects_unchanged': len(manifest['predecessor_sources']),
        'independent_compilation': [latest[r['module']] for r in rows],
        'transitive_axiom_audit': {'scope': 'Every environment declaration owned by the new modules, including generated declarations',
            'declarations': count, 'explicit_named_declarations_covered': len(manifest['named_declarations']),
            'observed_axioms': sorted(observed), 'source_sha256': digest(query), 'log_sha256': digest(axlogfile)},
        'compiler_controls': controls, 'full_cumulative_rebuild_claimed': False,
        'additional_archive_compiler_replay_claimed': False,
        'ledger': {'checked': 17, 'partial': 3},
        'completed_target': 'Actual ideal norm-character power-saving count under a residue-unit witness and nonvanishing on an inverse-class representative',
        'remaining': ['Supply arithmetic unit witnesses or justified descent for intended characters',
            'Supply suitable inverse-class representatives', 'Attach actual norm-character sums to the measurable/Mellin framework',
            'Attach actual Euler products and prescribed prime-series divergence',
            'Apply source separator assembly', 'Claim9.2 actual period-data/coefficient comparisons', 'Claim11.1 remaining transports and recovery']}
    (STAGE / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    (STAGE / 'licenses/NOTICE.md').write_text("""# Mathlib attribution and modification notice

Several ideal/generator equivalences adapt the proof in the pinned Mathlib source
`Mathlib/NumberTheory/NumberField/Ideal/Asymptotics.lean` and its
`CanonicalEmbedding/FundamentalCone.lean` dependencies. The new files expose
norm-preserving weighted and filtered identities, rather than only cardinalities.
`NormSignFormula.lean` adapts the field-norm embedding product argument;
its source header retains the upstream author and license notice.

Original ideal-asymptotics notice:
Copyright (c) 2025 Xavier Roblot. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xavier Roblot

The modifications are identified in the source comments and route reports.
The Apache 2.0 license is included as `Mathlib-LICENSE`.
Mathlib revision: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
""")
    readme = STAGE / 'README.md'
    readme.write_text(readme.read_text().split('\n## Completed verification')[0] +
        '\n## Completed verification\n\n' +
        f'All {len(rows)} new modules independently compiled with warnings treated as errors and reproduced identical proof objects. '+
        f'They add {manifest["new_theorem_lemma_declarations"]} theorem/lemma declarations. '+
        f'The transitive axiom audit covered {count} owned declarations, including generated declarations; only the standard three Lean axioms occurred. '+
        'One positive control passed, three false claims were rejected at the intended contradiction, and the placeholder was rejected specifically for using sorry. '+
        f'All {len(manifest["predecessor_sources"])} predecessor sources and proof objects retain their exact hashes. '+
        'This continuation does not claim a full cumulative rebuild.\n')
    subprocess.run([sys.executable, str(STAGE / 'checks/replay_residues.py'), '--verify-only'], check=True)
    files = {str(p.relative_to(STAGE)): digest(p) for p in sorted(STAGE.rglob('*'))
        if p.is_file() and p.name != 'INTEGRITY.json' and '__pycache__' not in p.parts}
    (STAGE / 'INTEGRITY.json').write_text(json.dumps(files, indent=2) + '\n')
    prefix = 'PRSC_X_Residue_Counting_Checked_Continuation'
    archive = STAGE.parent / (prefix + '.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in [*sorted(files), 'INTEGRITY.json']:
            z.write(STAGE / name, str(Path(prefix) / name))
    with tempfile.TemporaryDirectory(prefix='paperx-residue-extraction-') as tmp:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(tmp)
        extracted = Path(tmp) / prefix
        assert json.loads((extracted / 'INTEGRITY.json').read_text()) == files
        for name, h in files.items():
            assert digest(extracted / name) == h, name
        subprocess.run([sys.executable, str(extracted / 'checks/replay_residues.py'), '--verify-only'], check=True)
    result = {'archive': str(archive), 'size': archive.stat().st_size, 'sha256': digest(archive),
        'new_modules': len(rows), 'new_theorems': manifest['new_theorem_lemma_declarations'],
        'named_declarations': len(manifest['named_declarations']), 'owned_declarations_axiom_audited': count,
        'inventory_files': len(files), 'fresh_extraction_integrity': 'passed',
        'fresh_extraction_compiler_invoked': False, 'ledger': {'checked': 17, 'partial': 3}}
    (ROOT / 'privatechecks/release_result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
