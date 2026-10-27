from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
STAGE = Path('/workspace/scratch/5cb45ce56d13/PRSC_X_Residue_Counting_Release')
KIT = Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    baseline = json.loads((ROOT / 'evidence/frozen_sources.json').read_text())
    baseline_names = {r['module'] for r in baseline}
    assert len(baseline_names) == len(baseline) == 221
    sources = {p.stem: p for p in (ROOT / 'lean/PaperX').glob('*.lean')}
    new = set(sources) - baseline_names
    assert len(new) == 34
    deps = {n: set(re.findall(r'^import PaperX\.(\w+)', p.read_text(), re.M)) for n, p in sources.items()}
    for row in baseline:
        name = row['module']
        assert digest(sources[name]) == row['source_sha256'], name
        assert digest(ROOT / 'build/PaperX' / (name + '.olean')) == row['olean_sha256'], name
    done = set(baseline_names)
    order = []
    while new - done:
        ready = sorted(n for n in new - done if deps[n] <= done)
        assert ready, 'cyclic or missing imports'
        order.extend(ready)
        done.update(ready)
    rows, names = [], []
    for name in order:
        text = sources[name].read_text()
        namespaces = re.findall(r'^namespace (\S+)', text, re.M)
        assert len(namespaces) == 1
        declarations = re.findall(r'^(?:(?:private|protected|noncomputable)\s+)*(theorem|lemma|def|abbrev|structure|instance)\s+([^\s(:{]+)', text, re.M)
        assert not re.search(r'^private\s+(theorem|lemma|def)', text, re.M)
        named = [namespaces[0] + '.' + n for _, n in declarations]
        names.extend(named)
        rows.append({'module': name, 'source_sha256': digest(sources[name]),
            'olean_sha256': digest(ROOT / 'build/PaperX' / (name + '.olean')),
            'PaperX_dependencies': sorted(deps[name]),
            'theorem_lemma_declarations': sum(k in ('theorem','lemma') for k, _ in declarations),
            'named_declarations': named})
    assert len(names) == len(set(names))
    manifest = {'release': 'PRSC_X_Residue_Counting_Checked_Continuation',
        'lean_version': '4.34.0-rc2', 'lean_executable_sha256': digest(KIT / 'toolchain/bin/lean'),
        'mathlib_revision': 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
        'base_archive': {'filename': 'PRSC_X_Quantitative_Counting_Checked_Continuation.zip',
            'sha256': '1f0091e84f7ac1311824413a30324f71ea0403d1b0d4785f6afd0914c9c9d2c2'},
        'predecessor_sources': baseline, 'modules_in_build_order': rows,
        'new_theorem_lemma_declarations': sum(r['theorem_lemma_declarations'] for r in rows),
        'named_declarations': names,
        'replay_scope': 'Rebuild new modules from source against hash-verified frozen predecessor proof objects; no new author proof objects imported'}
    for folder in ['lean/PaperX','build/PaperX','checks','evidence/baseline','licenses']:
        (STAGE / folder).mkdir(parents=True, exist_ok=True)
    for name, src in sources.items():
        shutil.copy2(src, STAGE / 'lean/PaperX' / src.name)
        shutil.copy2(ROOT / 'build/PaperX' / (name + '.olean'), STAGE / 'build/PaperX' / (name + '.olean'))
    for f in ['lean_env.py','replay_residues.py','compile_wave.py']:
        shutil.copy2(ROOT / 'checks' / f, STAGE / 'checks' / f)
    (STAGE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (STAGE / 'checks/NamedAxioms.lean').write_text(''.join('import PaperX.' + r['module'] + '\n' for r in rows)
        + '\n' + ''.join('#print axioms ' + n + '\n' for n in names))
    shutil.copytree(ROOT / 'evidence', STAGE / 'evidence', dirs_exist_ok=True)
    historical = Path('/root/.codex/tmp/paperx_block27/source/Projector_Resolved_Seed_Calculus_X_Block27_Amended.tex')
    shutil.copy2(historical, STAGE / 'evidence/baseline' / historical.name)
    shutil.copy2(KIT / 'workspace/.lake/packages/mathlib/LICENSE', STAGE / 'licenses/Mathlib-LICENSE')
    for p in list(ROOT.glob('*.md')) + list(ROOT.glob('*.tex')):
        shutil.copy2(p, STAGE / p.name)
    print(json.dumps({'stage': str(STAGE), 'new_modules': len(new), 'cumulative_modules': len(sources),
        'theorems': manifest['new_theorem_lemma_declarations'], 'named_declarations': len(names)}, indent=2))

if __name__ == '__main__':
    main()
