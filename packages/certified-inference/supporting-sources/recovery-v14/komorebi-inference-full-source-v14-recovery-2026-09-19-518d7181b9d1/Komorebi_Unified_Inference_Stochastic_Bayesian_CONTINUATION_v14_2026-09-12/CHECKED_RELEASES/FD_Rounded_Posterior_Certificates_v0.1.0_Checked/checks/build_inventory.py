#!/usr/bin/env python3
"""Generate a dependency-ordered source inventory and complete declaration audit."""
from pathlib import Path
import re,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
OLD=Path(sys.argv[1]) if len(sys.argv)>1 else None
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mods={p.stem:p for p in (ROOT/'Komorebi').glob('*.lean') if p.stem!='RoundedAxiomAudit'}
order=[];visiting=set()
def visit(n):
    if n in order:return
    if n in visiting:raise RuntimeError('Import cycle '+n)
    visiting.add(n)
    for dep in re.findall(r'^import Komorebi\.(\w+)',mods[n].read_text(),re.M):
        if dep not in mods:raise RuntimeError('Missing dependency '+dep)
        visit(dep)
    visiting.remove(n);order.append(n)
for n in sorted(mods):visit(n)
if OLD is not None:
    olddecls=json.loads((OLD/'DECLARATIONS.json').read_text())
    oldnames={p.stem for p in (OLD/'Komorebi').glob('*.lean')}
    retained={n:{'sha256':sha(mods[n]),'previous_sha256':sha(OLD/'Komorebi'/f'{n}.lean')} for n in order if n in oldnames}
else:
    olddecls=json.loads((ROOT/'INHERITED_DECLARATIONS.json').read_text())
    previous=json.loads((ROOT/'INHERITED_SOURCES.json').read_text())
    retained={n:{'sha256':sha(mods[n]),'previous_sha256':h['previous_sha256']} for n,h in previous.items()}
assert all(r['sha256']==r['previous_sha256'] for r in retained.values())
decls=[{**d,'group':'inherited_v8'} for d in olddecls if d['module'] in retained]
for n in order:
    if n in retained:continue
    txt=mods[n].read_text();namespace=re.search(r'^namespace (\S+)',txt,re.M).group(1)
    for match in re.finditer(r'(?m)^(?:@\[[^\n]+\]\s*)?(?:protected\s+)?(theorem|lemma)\s+(\w+)',txt):
        # New modules have one namespace, with anonymous sections only.
        decls.append({'name':namespace+'.'+match.group(2),'module':n,'kind':match.group(1),
                      'line':txt[:match.start()].count('\n')+1,'group':'new'})
assert len({d['name'] for d in decls})==len(decls)
# Validate syntactic declaration counts against every source, including retained modules.
for n in order:
    count=len(re.findall(r'(?m)^(?:@\[[^\n]+\]\s*)?(?:protected\s+)?(?:theorem|lemma)\s+\w+',mods[n].read_text()))
    actual=sum(d['module']==n for d in decls)
    assert count==actual,(n,count,actual)
(ROOT/'DECLARATIONS.json').write_text(json.dumps(decls,indent=2)+'\n')
(ROOT/'INHERITED_SOURCES.json').write_text(json.dumps(retained,indent=2)+'\n')
(ROOT/'MODULE_ORDER.json').write_text(json.dumps(order+['RoundedAxiomAudit'],indent=2)+'\n')
lines=['import Komorebi.'+n for n in order]+['']+['#print axioms '+d['name'] for d in decls]
(ROOT/'Komorebi/RoundedAxiomAudit.lean').write_text('\n'.join(lines)+'\n')
print('active modules',len(order)+1,'inherited',len(retained),'declarations',len(decls),'new',sum(d['group']=='new' for d in decls))
