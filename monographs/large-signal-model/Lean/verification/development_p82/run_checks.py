#!/usr/bin/env python3
"""Fresh source/dependency-bound P82 checks after sourcing env_v019.sh."""
from pathlib import Path
import subprocess, json, hashlib, os, importlib.util, datetime, re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT.parents[1]
OUT = Path(__file__).resolve().parent
LEAN = str(BASE / 'runtime/gated-bin/lean')
freeze = json.loads((OUT / 'SOURCE_FREEZE.json').read_text())
records = json.loads((OUT / 'DECLARATIONS.json').read_text())
spec = importlib.util.spec_from_file_location('verifier', ROOT / 'scripts/verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
stages = []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dependency_closure(mods):
    seen = set()
    def visit(mod):
        if mod in seen:
            return
        seen.add(mod)
        source = ROOT / 'KomorebiLSM' / f'{mod}.lean'
        for dep in re.findall(r'^import KomorebiLSM\.(\w+)$', source.read_text(), re.M):
            visit(dep)
    for mod in mods:
        visit(mod)
    return {mod: sha(ROOT / 'KomorebiLSM' / f'{mod}.lean') for mod in sorted(seen)}

dependencies = dependency_closure(freeze)
(OUT / 'DEPENDENCY_SNAPSHOT.json').write_text(json.dumps(dependencies, indent=2) + '\n')
report = {'status': 'RUNNING', 'sources': freeze, 'stages': stages}

def save():
    (OUT / 'AUTHOR_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')

def run(stage, name, args, env=None, negative=False):
    cmd = [LEAN, '-j1', '-DwarningAsError=true'] + list(map(str, args))
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    text = proc.stdout + proc.stderr
    log = OUT / f'{name}_{stage}.log'
    log.write_text(text)
    accepted = (proc.returncode == 1 and '⊢ False' in text and text.count('error:') == 1) if negative else proc.returncode == 0
    row = {'stage': stage, 'name': name, 'command': cmd, 'returncode': proc.returncode,
           'log': str(log.relative_to(ROOT)), 'log_sha256': sha(log), 'accepted': accepted}
    stages.append(row)
    (OUT / 'EXECUTION_STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
    save()
    print(json.dumps(row), flush=True)
    assert accepted, text
    return text

save()
try:
    for mod, pin in freeze.items():
        source = ROOT / 'KomorebiLSM' / f'{mod}.lean'
        assert sha(source) == pin['source_sha256']
        assert not verifier.PROHIBITED.search(source.read_text())
        run('compile', mod, ['-o', ROOT / '.build/lib/lean/KomorebiLSM' / f'{mod}.olean', source])
    text = run('axiom_audit', 'all_named', [OUT / 'AxiomAudit.lean'])
    axioms = verifier.parse_axioms(text, {d['name'] for d in records})
    assert len(axioms) == 95
    text = run('signatures', 'public', [OUT / 'SignatureAudit.lean'])
    assert 'StandardBorelSpace' not in text and 'condExpKernel' not in text
    for mod in freeze:
        env = os.environ.copy()
        env['KOMOREBI_REPLAY_MODULE'] = 'KomorebiLSM.' + mod
        text = run('kernel_replay', mod, [ROOT / 'scripts/ReplayModule.lean'], env)
        assert 'KERNEL_REPLAY_PASS KomorebiLSM.' + mod in text
    controls = []
    for name in ['ObservableMomentMissingPosterior', 'ObservableMomentSingularBasis', 'ObservableMomentOmitInverseNorm']:
        source = ROOT / 'negative_controls' / f'{name}.lean'
        before = sha(source)
        run('negative_control', name, [source], negative=True)
        assert before == sha(source)
        controls.append({'source': str(source.relative_to(ROOT)), 'sha256': before})
    assert dependencies == dependency_closure(freeze)
    report.update(status='ALL_AUTHOR_CHECKS_PASS', declarations=len(records),
                  theorems=sum(d['kind'] == 'theorem' for d in records),
                  axioms_allowed_only=True, axioms=axioms, controls=controls,
                  dependency_snapshot='DEPENDENCY_SNAPSHOT.json',
                  dependency_snapshot_sha256=sha(OUT / 'DEPENDENCY_SNAPSHOT.json'),
                  dependency_sources_unchanged=True,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('P82_ALL_AUTHOR_CHECKS_PASS', flush=True)
except Exception as exc:
    report.update(status='FAILED', failure=repr(exc))
    save()
    raise
