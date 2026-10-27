#!/usr/bin/env python3
"""Regenerate the cumulative inventory and all-declaration axiom audit."""
from pathlib import Path
import json, re
from verify import strip_comments_and_strings
ROOT=Path(__file__).resolve().parents[1]
NEW_MODULES=['KomorebiPhysics.'+s for s in ['ResolventDomain','ResolventCommutator','ResolventBounds','ResolventParameters','DiagonalResolvents','NonreducingPacket','ResolventExamples']]
def main():
    inv=json.loads((ROOT/'verification/block13_documentation/declaration_inventory.json').read_text())
    for mod in NEW_MODULES:
        rel=mod.replace('.','/')+'.lean'; stack=[]
        for lineno,line in enumerate(strip_comments_and_strings((ROOT/rel).read_text()).splitlines(),1):
            ns=re.match(r'^namespace\s+(\S+)',line)
            end=re.match(r'^end\s+(\S+)',line)
            d=re.match(r'^(theorem|def|structure|abbrev)\s+([^\s({:]+)',line)
            if ns: stack.append(ns[1])
            elif end and stack and end[1]==stack[-1]: stack.pop()
            elif d: inv['declarations'].append(dict(name='.'.join(stack+[d[2]]),kind=d[1],module=mod,source_file=rel,line=lineno,origin='new_full_edition_block_14'))
        if stack: raise ValueError(stack)
        inv['modules'].append(mod)
    names=[d['name'] for d in inv['declarations']]
    if len(names)!=len(set(names)): raise ValueError('Duplicate names')
    (ROOT/'declaration_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    (ROOT/'Audit.lean').write_text('import KomorebiPhysics\n\n'+''.join('#print axioms '+n+'\n' for n in names))
    print(json.dumps({'modules':len(inv['modules']),'names':len(names),'theorems':sum(d['kind']=='theorem' for d in inv['declarations']),'new':{m:{k:sum(d['module']==m and d['kind']==k for d in inv['declarations']) for k in ['theorem','def','structure']} for m in NEW_MODULES}},indent=2))
if __name__=='__main__': main()
