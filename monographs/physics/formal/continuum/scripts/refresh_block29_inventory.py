#!/usr/bin/env python3
"""Append the checked Block 29 module to the v0.28 declaration inventory."""
from pathlib import Path
import json, re
from verify import strip_comments_and_strings

ROOT = Path(__file__).resolve().parents[1]
MOD = 'KomorebiPhysics.Relativistic3DEdgeCompatibility'
ORIGIN = 'block29_edge_compatibility_curvature_separation'
DECL_RE = re.compile(r'^(?:@\[[^\]]+\]\s*)?(theorem|def|structure|abbrev)\s+([^\s({:]+)')

def scan_module(mod: str):
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
            if end.group(1) and stack and end.group(1)==stack[-1]:
                stack.pop()
        elif decl:
            rows.append({'name':'.'.join(stack+[decl.group(2)]),'kind':decl.group(1),
                         'module':mod,'source_file':rel,'line':lineno,'origin':ORIGIN})
    if stack:
        raise ValueError(f'unclosed named namespaces in {rel}: {stack}')
    return rows

def main():
    inv=json.loads((ROOT/'declaration_inventory.json').read_text())
    if MOD in inv['modules']:
        inv['declarations']=[d for d in inv['declarations'] if d['module']!=MOD]
    else:
        inv['modules'].append(MOD)
    rows=scan_module(MOD)
    inv['declarations'].extend(rows)
    names=[d['name'] for d in inv['declarations']]
    if len(names)!=len(set(names)):
        from collections import Counter
        dup=[n for n,c in Counter(names).items() if c>1]
        raise ValueError(f'duplicate declarations: {dup[:20]}')
    (ROOT/'declaration_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    (ROOT/'Audit.lean').write_text('import KomorebiPhysics\n\n'+''.join(f'#print axioms {n}\n' for n in names))
    (ROOT/'AuditBlock29.lean').write_text('import KomorebiPhysics.Relativistic3DEdgeCompatibility\n\n'+
        ''.join(f'#print axioms {d["name"]}\n' for d in rows))
    summary={'modules':len(inv['modules']),'declarations':len(inv['declarations']),
             'theorems':sum(d['kind']=='theorem' for d in inv['declarations']),
             'block29_declarations':len(rows),
             'block29_theorems':sum(d['kind']=='theorem' for d in rows),
             'by_kind':{k:sum(d['kind']==k for d in rows) for k in ['theorem','def','structure','abbrev']}}
    out=ROOT/'verification/block29_inventory_summary.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
