#!/usr/bin/env python3
"""Regenerate Block 09 declaration records, preserving the Block 08 inventory."""
from pathlib import Path
import json
import re
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
NEW_MODULES = ['KomorebiPhysics.GraphDomain', 'KomorebiPhysics.CountableAtlas', 'KomorebiPhysics.CountableContinuity', 'KomorebiPhysics.DiagonalDomain', 'KomorebiPhysics.SpectralGraph', 'KomorebiPhysics.UnboundedExamples', 'KomorebiPhysics.DomainExamples']

def main() -> None:
    inventory = json.loads((ROOT / 'verification/block08_documentation/declaration_inventory.json').read_text())
    for module in NEW_MODULES:
        rel = module.replace('.', '/') + '.lean'
        source = strip_comments_and_strings((ROOT / rel).read_text())
        namespaces: list[str] = []
        for line_number, line in enumerate(source.splitlines(), 1):
            ns = re.match(r'^namespace\s+(\S+)', line)
            end = re.match(r'^end\s+(\S+)', line)
            declaration = re.match(r'^(theorem|def|structure)\s+([^\s({:]+)', line)
            if ns:
                namespaces.append(ns.group(1))
            elif end and namespaces and end.group(1) == namespaces[-1]:
                namespaces.pop()
            elif declaration:
                kind, name = declaration.groups()
                inventory['declarations'].append({
                    'name': '.'.join(namespaces + [name]), 'kind': kind,
                    'module': module, 'source_file': rel, 'line': line_number,
                    'origin': 'new_full_edition_block_09',
                })
        if namespaces:
            raise ValueError(f'Unclosed namespace(s) in {rel}: {namespaces}')
        inventory['modules'].append(module)
    names = [d['name'] for d in inventory['declarations']]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate declaration names')
    (ROOT / 'declaration_inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    (ROOT / 'Audit.lean').write_text('import KomorebiPhysics\n\n' + ''.join(f'#print axioms {name}\n' for name in names))
    print(json.dumps({'modules': len(inventory['modules']), 'audited_declarations': len(names),
        'total_theorems': sum(d['kind']=='theorem' for d in inventory['declarations']),
        'block09_theorems': sum(d['kind']=='theorem' and d['origin']=='new_full_edition_block_09' for d in inventory['declarations'])}, indent=2))

if __name__ == '__main__':
    main()
