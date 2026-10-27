#!/usr/bin/env python3
"""Bind a technical release to its tested source, wheel, proofs, and monograph.

A passing gate is not a signature, independent proof checker, or legal opinion.
The current candidate explicitly has no selected public licenses. Its technical
readiness and publication status are reported separately.
"""
from __future__ import annotations
import argparse
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import sys
import zipfile
sys.dont_write_bytecode = True
from check_manifest import check as check_manifest
from verify_lineage import safe_file, sha, verify_lineage

ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def json_file(root: Path, name: str) -> dict:
    data = json.loads(safe_file(root, name).read_text(encoding='utf-8'))
    require(type(data) is dict, 'Expected an object: ' + name)
    return data

def check_bindings(root: Path, mapping: dict, label: str) -> int:
    require(type(mapping) is dict and bool(mapping), 'Empty ' + label + ' source binding')
    for path, expected in mapping.items():
        require(sha(safe_file(root, path)) == expected, 'Stale ' + label + ' evidence: ' + path)
    return len(mapping)

def wheel_check(root: Path) -> dict:
    version = safe_file(root, 'VERSION').read_text(encoding='utf-8').strip()
    wheels = list((root / 'dist').glob('*.whl'))
    require(len(wheels) == 1, 'Expected exactly one current wheel')
    wheel = wheels[0]
    require(not wheel.is_symlink(), 'Wheel must not be a symlink')
    names = ['repair_certificates.py', 'rational_menu.py', 'branch_menu.py']
    names += sorted(p.relative_to(root / 'python').as_posix()
                    for p in (root / 'python/komorebi_repair').glob('*.py'))
    with zipfile.ZipFile(wheel) as z:
        entries = z.namelist()
        require(len(set(entries)) == len(entries), 'Duplicate wheel member')
        require(z.testzip() is None, 'Wheel CRC failed')
        metadata = [n for n in entries if n.endswith('.dist-info/METADATA')]
        require(len(metadata) == 1, 'Missing or duplicate wheel metadata')
        msg = BytesParser().parsebytes(z.read(metadata[0]))
        require(msg['Name'] == 'komorebi-constructive-repair', 'Wrong wheel project')
        require(msg['Version'] == version, 'Stale wheel version')
        require(sorted(n for n in entries if n.endswith('.py')) == sorted(names),
                'Wheel runtime-source inventory differs')
        for name in names:
            require(z.read(name) == safe_file(root, 'python/' + name).read_bytes(),
                    'Wheel/source mismatch: ' + name)
    return {'files': len(names), 'version': version, 'sha256': sha(wheel), 'wheel': wheel.name}

def proof_check(root: Path) -> dict:
    v = json_file(root, 'evidence/verification/current/verification.json')
    require(v['status'] == 'PASS', 'Formal verification did not pass')
    checks = v['checks']
    require(type(checks) is dict and bool(checks) and
            all(type(c) is dict and c.get('pass') is True for c in checks.values()),
            'A formal check is absent, malformed, or failed')
    mods = json.loads(safe_file(root, 'evidence/modules.json').read_text(encoding='utf-8'))
    require(len(mods) == 51 and len(set(mods)) == 51, 'Wrong frozen module inventory')
    registry = json_file(root, 'docs/theorem_registry.json')['theorems']
    names = {r['name'] for r in registry}
    require(len(names) == len(registry) == 526, 'Wrong frozen declaration registry')
    require(v['proof_modules'] == len(mods) and v['theorem_declarations'] == len(registry),
            'Formal count/registry mismatch')
    ax = v['axioms']
    require(set(ax) == names, 'Incomplete axiom inventory')
    require(all(type(a) is list and not (set(a) - ALLOWED_AXIOMS) for a in ax.values()),
            'Disallowed theorem axiom')
    mapping = v['source_sha256']
    required = {'lean/KomorebiRepair/' + m.replace('.', '/') + '.lean' for m in mods}
    require(required <= set(mapping), 'Proof source is missing from verification binding')
    count = check_bindings(root, mapping, 'formal')
    labels = [c['label'] for c in v['commands']]
    require(len(labels) == len(set(labels)), 'Duplicate verification command label')
    require(all('compile_KomorebiRepair_' + m.replace('.', '_') in labels and
                'replay_' + m.replace('.', '_') in labels for m in mods),
            'Missing compilation or replay command')
    return {'modules': len(mods), 'declarations': len(names), 'bound_files': count,
            'checks': len(checks), 'commands': len(labels)}

def acceptance_check(root: Path, wheel_hash: str) -> dict:
    a = json_file(root, 'evidence/rc3/acceptance_run/acceptance.json')
    require(a['status'] == 'PASS', 'Release acceptance did not pass')
    require(bool(a['checks']) and all(c.get('pass') is True for c in a['checks'].values()),
            'Release acceptance contains a failed check')
    count = check_bindings(root, a['source_sha256'], 'acceptance')
    required = {'python/' + p.relative_to(root / 'python').as_posix()
                for p in (root / 'python').rglob('*.py')}
    required |= {p.relative_to(root).as_posix() for d in ('scripts', 'tests')
                 for p in (root / d).glob('*.py')}
    required |= {'VERSION', 'pyproject.toml', 'README.md'}
    require(required <= set(a['source_sha256']), 'Incomplete runtime/verification-source binding')
    require(a['wheel_sha256'] == wheel_hash, 'Acceptance used a different wheel')
    return {'source_files': count, 'checks': len(a['checks'])}

def monograph_check(root: Path) -> dict:
    b = json_file(root, 'monograph/build_receipt.json')
    require(b['status'] == 'PASS', 'Monograph build did not pass')
    require(all(b.get(k) is True for k in ('references_resolved', 'no_overfull_boxes', 'no_missing_characters')),
            'Monograph diagnostic check failed')
    require(sha(safe_file(root, 'monograph/Constructive_Repair.tex')) == b['source_sha256'],
            'LaTeX source changed since compilation')
    require(sha(safe_file(root, 'monograph/Constructive_Repair.pdf')) == b['pdf_sha256'],
            'PDF changed since compilation')
    return {'pages': b['pages'], 'pdf_sha256': b['pdf_sha256']}

def check(root: Path) -> dict:
    root = root.resolve()
    integrity = check_manifest(root, strict=True)
    lineage = verify_lineage(root)
    wheel = wheel_check(root)
    proofs = proof_check(root)
    acceptance = acceptance_check(root, wheel['sha256'])
    monograph = monograph_check(root)
    decision = json_file(root, 'PUBLICATION_DECISION.json')
    # A new author license selection requires a new scoped publication review.
    require(decision == {'public_code_license': None, 'public_document_license': None,
                         'publication_authorized': False}, 'Publication decision changed; review required')
    return {'technical_status': 'PASS', 'publication_status': 'AWAITING_AUTHOR_LICENSE_SELECTION',
            'integrity': integrity, 'lineage': lineage, 'wheel': wheel, 'proofs': proofs,
            'acceptance': acceptance, 'monograph': monograph,
            'scope': 'Source/receipt consistency and release acceptance. Not authentication, an independent proof checker, or legal approval.'}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    a = ap.parse_args()
    try:
        result = check(a.root)
    except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({'technical_status': 'FAIL', 'publication_status': 'NOT_READY', 'error': str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
