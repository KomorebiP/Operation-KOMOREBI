#!/usr/bin/env python3
"""Regenerate cumulative declaration inventory and audits for Blocks 23–25."""
from pathlib import Path
import json, re
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'reference/block22_declaration_inventory.json'
NEW = [
    ('KomorebiPhysics.Relativistic3DCliffordTransportU1', 'block23_u1_repair'),
    ('KomorebiPhysics.LocalDiscreteGlobalContinuum', 'block24_refinement_bridge'),
    ('KomorebiPhysics.Relativistic3DCliffordHilbertRefinement', 'block25_hilbert_refinement'),
]
DECL_RE = re.compile(r'^(?:@\[[^\]]+\]\s*)?(theorem|def|structure|abbrev)\s+([^\s({:]+)')

def scan_module(mod: str, origin: str):
    rel = mod.replace('.', '/') + '.lean'
    text = strip_comments_and_strings((ROOT / rel).read_text())
    stack=[]; rows=[]
    for lineno,line in enumerate(text.splitlines(),1):
        line=line.strip()
        ns=re.match(r'^namespace\s+(\S+)',line)
        end=re.match(r'^end(?:\s+(\S+))?$',line)
        decl=DECL_RE.match(line)
        if ns:
            stack.append(ns.group(1))
        elif end:
            # Bare `end` closes sections as well; only pop when a named namespace matches.
            if end.group(1) and stack and end.group(1)==stack[-1]:
                stack.pop()
        elif decl:
            rows.append({
                'name': '.'.join(stack+[decl.group(2)]),
                'kind': decl.group(1), 'module': mod, 'source_file': rel,
                'line': lineno, 'origin': origin,
            })
    if stack:
        raise ValueError(f'unclosed named namespaces in {rel}: {stack}')
    return rows

def main():
    inv=json.loads(BASE.read_text())
    new_rows=[]
    for mod,origin in NEW:
        rows=scan_module(mod,origin)
        inv['modules'].append(mod)
        inv['declarations'].extend(rows)
        new_rows.extend(rows)
    names=[d['name'] for d in inv['declarations']]
    if len(names)!=len(set(names)):
        from collections import Counter
        dup=[n for n,c in Counter(names).items() if c>1]
        raise ValueError(f'duplicate declarations: {dup[:20]}')
    (ROOT/'declaration_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    (ROOT/'Audit.lean').write_text('import KomorebiPhysics\n\n'+''.join(f'#print axioms {n}\n' for n in names))
    (ROOT/'AuditBlock25.lean').write_text(
        'import KomorebiPhysics\n\n'+''.join(f'#print axioms {d["name"]}\n' for d in new_rows))
    summary={
        'modules':len(inv['modules']), 'declarations':len(inv['declarations']),
        'theorems':sum(d['kind']=='theorem' for d in inv['declarations']),
        'new_declarations':len(new_rows),
        'new_theorems':sum(d['kind']=='theorem' for d in new_rows),
        'by_module':{
            mod:{k:sum(d['module']==mod and d['kind']==k for d in new_rows)
                 for k in ['theorem','def','structure','abbrev']}
            for mod,_ in NEW
        },
    }
    (ROOT/'verification/block25_inventory_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
