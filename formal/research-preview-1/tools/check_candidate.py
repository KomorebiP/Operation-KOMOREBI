#!/usr/bin/env python3
"""Read-only source/evidence consistency check. Does not execute Lean."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    padic = root / 'padic'
    sys.path.insert(0, str(padic / 'verification'))
    from evidence_parser import parse_declared, parse_environment, strip_comments
    errors: list[str] = []
    count = 0
    def check(ok: bool, message: str) -> None:
        nonlocal count
        count += 1
        if not ok:
            errors.append(message)
    ident = json.loads((padic / 'evidence/SOURCE_IDENTITY.json').read_text())
    for item in ident['files']:
        rel = Path(item['candidate_path'])
        check(not rel.is_absolute() and '..' not in rel.parts, f'Unsafe identity path: {rel}')
        path = root / rel
        check(path.is_file(), f'Missing: {rel}')
        if path.is_file():
            check(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], f'Changed: {rel}')
    modules = sorted((padic / 'lean').rglob('*.lean'))
    check(len(modules) == 92, 'Production-module count differs from the frozen baseline')
    theorem_count = 0
    for path in modules:
        code = strip_comments(path.read_text())
        theorem_count += len(re.findall(r'\btheorem\s+[A-Za-z_]', code))
        check(not re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b', code),
              f'Forbidden production construct: {path.name}')
        for module in re.findall(r'^import\s+(KomorebiPadic(?:\.[A-Za-z0-9_]+)*)', code, re.M):
            imp = padic / 'lean' / (module.replace('.', '/') + '.lean')
            check(imp.is_file(), f'Missing project import: {module}')
    inventory = json.loads((padic / 'verification/theorem_inventory.json').read_text())
    check(theorem_count == inventory['total'] == 1120, 'Declared theorem count differs')
    declared = parse_declared((padic / 'evidence/block34_declared_axioms.log').read_text())
    environment = parse_environment((padic / 'evidence/block34_environment_axioms.log').read_text())
    check(set(declared) == set(inventory['names']), 'Retained declared axiom coverage differs')
    allowed = {'propext', 'Quot.sound', 'Classical.choice'}
    for name in inventory['names']:
        check(name in environment, f'Retained environment misses {name}')
        if name in declared and name in environment:
            check(declared[name] == environment[name][1], f'Retained axiom routes disagree: {name}')
    for name, (_module, axioms) in environment.items():
        check(axioms <= allowed, f'Unexpected retained axiom set: {name}')
    for claim in json.loads((root / 'claims.json').read_text()):
        for anchor in claim['anchors']:
            lines = (root / anchor['file']).read_text().splitlines()
            check(anchor['declaration'] in lines[anchor['line'] - 1],
                  f'Claim anchor changed: {claim["id"]}:{anchor["declaration"]}')
    result = {'status': 'PASS' if not errors else 'FAIL', 'checks': count, 'errors': errors,
              'scope': 'Selected source identity, local imports, claim locators, retained axiom logs. NOT a new Lean run.',
              'production_modules': len(modules), 'declared_theorems': theorem_count,
              'retained_environment_theorem_constants': len(environment)}
    print(json.dumps(result, indent=2))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
