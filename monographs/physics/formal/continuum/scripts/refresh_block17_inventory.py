#!/usr/bin/env python3
"""Regenerate Block 17 cumulative declaration inventory and axiom audit."""
from pathlib import Path
import json, re
from verify import strip_comments_and_strings
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reference/block16_declaration_inventory.json'
NEW_MODULES=['KomorebiPhysics.'+s for s in [
    'RelativisticPauli', 'InvolutionExponential', 'DiracWalk1D',
    'Dispersion1D', 'Relativistic1DExamples']]
DECL_RE=re.compile(r'^(?:@\[[^\]]+\]\s*)?(theorem|def|structure|abbrev)\s+([^\s({:]+)')

def main():
    inv=json.loads(BASE.read_text())
    for mod in NEW_MODULES:
        rel=mod.replace('.','/')+'.lean'
        stack=[]
        text=strip_comments_and_strings((ROOT/rel).read_text())
        for lineno,line in enumerate(text.splitlines(),1):
            ns=re.match(r'^namespace\s+(\S+)',line)
            end=re.match(r'^end\s+(\S+)',line)
            d=DECL_RE.match(line)
            if ns:
                stack.append(ns[1])
            elif end and stack and end[1]==stack[-1]:
                stack.pop()
            elif d:
                inv['declarations'].append(dict(
                    name='.'.join(stack+[d[2]]), kind=d[1], module=mod,
                    source_file=rel, line=lineno, origin='new_full_edition_block_17'))
        if stack:
            raise ValueError(f'unclosed namespaces in {rel}: {stack}')
        inv['modules'].append(mod)
    names=[d['name'] for d in inv['declarations']]
    if len(names)!=len(set(names)):
        dup=sorted({n for n in names if names.count(n)>1})
        raise ValueError('Duplicate declaration names: '+str(dup[:20]))
    (ROOT/'declaration_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
    (ROOT/'Audit.lean').write_text('import KomorebiPhysics\n\n'+''.join('#print axioms '+n+'\n' for n in names))
    result={
        'modules':len(inv['modules']),
        'names':len(names),
        'theorems':sum(d['kind']=='theorem' for d in inv['declarations']),
        'new':{m:{k:sum(d['module']==m and d['kind']==k for d in inv['declarations'])
                  for k in ['theorem','def','structure','abbrev']} for m in NEW_MODULES}
    }
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
