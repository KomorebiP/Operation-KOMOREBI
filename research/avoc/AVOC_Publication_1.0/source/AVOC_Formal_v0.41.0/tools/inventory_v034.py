#!/usr/bin/env python3
"""Inventory v0.34 proof-derived terminal-operation bridge declarations."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OLD=json.loads((ROOT/'results/v0.33.0/declaration_inventory.json').read_text())
MODULES=['AffineTerminal','MultiLevelOperational','AffineTerminalCodec','CertifiedOperationalCatalogue','OperationalExamples']
new=[]
for mod in MODULES:
    p=ROOT/'AVOC'/f'{mod}.lean';text=p.read_text()
    # Follow namespace changes in source order; all declarations in these modules use one effective namespace at a time.
    namespace=''
    events=[]
    for m in re.finditer(r'^(namespace\s+(\S+)|end(?:\s+\S+)?|(?:@\[[^\]]+\]\s*)?(theorem|lemma)\s+([^\s(]+))',text,re.M):
        events.append(m)
    stack=[]
    for m in events:
        token=m.group(1)
        if token.startswith('namespace '):
            name=m.group(2);stack.append(name if not stack else stack[-1]+'.'+name)
        elif token.startswith('end'):
            if stack:stack.pop()
        else:
            kind=m.group(3);name=m.group(4);ns=stack[-1] if stack else ''
            new.append(dict(module=f'AVOC/{mod}.lean',line=text[:m.start()].count('\n')+1,
                kind=kind,name=name,qualified_name=f'{ns}.{name}' if ns else name))
entries=sorted(OLD+new,key=lambda x:(x['module'],x['line']))
assert len({x['qualified_name'] for x in entries})==len(entries), 'duplicate declaration names'
rd=ROOT/'results/v0.34.0';rd.mkdir(parents=True,exist_ok=True)
for name,data in [('declaration_inventory',entries),('new_declarations',new)]:
    (rd/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
# Keep imports current.
f=ROOT/'AVOC.lean';s=f.read_text()
for mod in MODULES:
    if f'import AVOC.{mod}\n' not in s:s+=f'import AVOC.{mod}\n'
f.write_text(s)
(ROOT/'AVOC/FullAudit.lean').write_text('import AVOC\n\n'+''.join('#print axioms '+x['qualified_name']+'\n' for x in entries))
lines=['# AVOC v0.34.0 — declaration inventory','',
       f'{len(OLD)} inherited + {len(new)} new = {len(entries)} named theorem/lemma declarations.',
       'Counts include helpers and examples, not independent discoveries.','']
last=None
for x in entries:
    if x['module']!=last:last=x['module'];lines+=['',f'## `{last}`','']
    lines.append(f"- `{x['qualified_name']}` — line {x['line']}")
(ROOT/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
files=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
actual=[]
for p in files:
    actual.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',p.read_text(),re.M))
assert len(actual)==len(entries),(len(actual),len(entries))
summary=dict(inherited_theorems=len(OLD),new_theorems=len(new),total_theorems=len(entries),
    non_audit_modules=len(files),source_lines=sum(len(p.read_text().splitlines()) for p in files),new_modules=MODULES)
(rd/'source_counts.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
