#!/usr/bin/env python3
"""Regenerate Block 21 cumulative declaration inventory and axiom audit."""
from pathlib import Path
import json, re
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'reference/block20_declaration_inventory.json'
NEW_MODULES = ['KomorebiPhysics.' + s for s in [
    'Relativistic3DShellAsymptotics',
    'Relativistic3DContinuumLimit',
    'Relativistic3DGroupVelocity',
    'Relativistic3DAnisotropy',
    'Relativistic3DContinuumExamples',
]]
DECL_RE = re.compile(r'^(?:@\[[^\]]+\]\s*)?(theorem|def|structure|abbrev)\s+([^\s({:]+)')


def main() -> None:
    inv = json.loads(BASE.read_text())
    for mod in NEW_MODULES:
        rel = mod.replace('.', '/') + '.lean'
        stack: list[str] = []
        text = strip_comments_and_strings((ROOT / rel).read_text())
        for lineno, line in enumerate(text.splitlines(), 1):
            ns = re.match(r'^namespace\s+(\S+)', line)
            end = re.match(r'^end\s+(\S+)', line)
            decl = DECL_RE.match(line)
            if ns:
                stack.append(ns[1])
            elif end and stack and end[1] == stack[-1]:
                stack.pop()
            elif decl:
                inv['declarations'].append({
                    'name': '.'.join(stack + [decl[2]]),
                    'kind': decl[1],
                    'module': mod,
                    'source_file': rel,
                    'line': lineno,
                    'origin': 'new_full_edition_block_21',
                })
        if stack:
            raise ValueError(f'unclosed namespaces in {rel}: {stack}')
        inv['modules'].append(mod)

    names = [d['name'] for d in inv['declarations']]
    if len(names) != len(set(names)):
        seen: set[str] = set(); dup: list[str] = []
        for name in names:
            if name in seen and name not in dup: dup.append(name)
            seen.add(name)
        raise ValueError('Duplicate declaration names: ' + str(sorted(dup)[:20]))

    (ROOT / 'declaration_inventory.json').write_text(json.dumps(inv, indent=2) + '\n')
    (ROOT / 'Audit.lean').write_text(
        'import KomorebiPhysics\n\n' + ''.join('#print axioms ' + n + '\n' for n in names)
    )
    result = {
        'modules': len(inv['modules']),
        'names': len(names),
        'theorems': sum(d['kind'] == 'theorem' for d in inv['declarations']),
        'new': {
            mod: {
                kind: sum(d['module'] == mod and d['kind'] == kind for d in inv['declarations'])
                for kind in ['theorem', 'def', 'structure', 'abbrev']
            }
            for mod in NEW_MODULES
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
