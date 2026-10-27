#!/usr/bin/env python3
"""Generate a declaration inventory and live #print axioms audit from source."""
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[1]
MODULES = ['Foundations','LinearAccess','OptimalRepair','Dimension','Predictive','Haar']
PREFIXES = {'Foundations':'KomorebiInformation', 'LinearAccess':'KomorebiInformation.Linear',
            'OptimalRepair':'KomorebiInformation.Linear','Dimension':'KomorebiInformation.Linear',
            'Predictive':'KomorebiInformation.Predictive','Haar':'KomorebiInformation.Haar'}
def prepare() -> list[dict]:
    inventory = []
    imports = [f'public import KomorebiInformation.{m}' for m in MODULES]
    (ROOT/'lean/KomorebiInformation.lean').write_text('module\n'+'\n'.join(imports)+'\n')
    lines = ['module','public import KomorebiInformation','public section','']
    for module in MODULES:
        path = ROOT/'lean/KomorebiInformation'/f'{module}.lean'
        text = path.read_text()
        for match in re.finditer(r'^theorem\s+(\w+)', text, re.M):
            name = f'{PREFIXES[module]}.{match[1]}'
            entry = {'name':name,'module':module,'file':str(path.relative_to(ROOT)),
                     'line':text.count('\n',0,match.start())+1}
            inventory.append(entry)
            lines.extend([f'#check {name}', f'#print axioms {name}', ''])
    (ROOT/'lean/Audit.lean').write_text('\n'.join(lines))
    (ROOT/'DECLARATIONS.json').write_text(json.dumps(inventory,indent=2)+'\n')
    return inventory
if __name__ == '__main__':
    print(f'Prepared audit for {len(prepare())} theorem declarations.')
