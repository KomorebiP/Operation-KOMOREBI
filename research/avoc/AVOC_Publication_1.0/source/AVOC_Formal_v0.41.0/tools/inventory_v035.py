#!/usr/bin/env python3
"""Inventory v0.35 staged affine-controller declarations."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OLD=json.loads((ROOT/'results/v0.34.0/declaration_inventory.json').read_text())
MODULES=['StagedAffineControl','StagedAffineOperational','StagedAffineExamples','StagedAffineCodec']
new=[]
for mod in MODULES:
    p=ROOT/'AVOC'/f'{mod}.lean';text=p.read_text();stack=[]
    pat=re.compile(r'^(namespace\s+(\S+)|end(?:\s+\S+)?|(?:@\[[^\]]+\]\s*)?(theorem|lemma)\s+([^\s(]+))',re.M)
    for m in pat.finditer(text):
        token=m.group(1)
        if token.startswith('namespace '):
            name=m.group(2);stack.append(name if not stack else stack[-1]+'.'+name)
        elif token.startswith('end'):
            if stack:stack.pop()
        else:
            kind,name=m.group(3),m.group(4);ns=stack[-1] if stack else ''
            new.append(dict(module=f'AVOC/{mod}.lean',line=text[:m.start()].count('\n')+1,
                kind=kind,name=name,qualified_name=f'{ns}.{name}' if ns else name))
entries=sorted(OLD+new,key=lambda x:(x['module'],x['line']))
assert len({x['qualified_name'] for x in entries})==len(entries)
rd=ROOT/'results/v0.35.0';rd.mkdir(parents=True,exist_ok=True)
(rd/'declaration_inventory.json').write_text(json.dumps(entries,indent=2)+'\n')
(rd/'new_declarations.json').write_text(json.dumps(new,indent=2)+'\n')
(ROOT/'AVOC/FullAudit.lean').write_text('import AVOC\n\n'+''.join('#print axioms '+x['qualified_name']+'\n' for x in entries))
lines=['# AVOC v0.35.0 — complete theorem index','',
       f'{len(OLD)} inherited + {len(new)} new = {len(entries)} named theorem/lemma declarations.',
       'Counts include helpers and examples, not independent discoveries.','']
last=None
for x in entries:
    if x['module']!=last:last=x['module'];lines+=['',f'## `{last}`','']
    lines.append(f"- `{x['qualified_name']}` — line {x['line']}")
(ROOT/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
files=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
actual=[]
for p in files: actual += re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',p.read_text(),re.M)
assert len(actual)==len(entries),(len(actual),len(entries))
summary=dict(inherited_theorems=len(OLD),new_theorems=len(new),total_theorems=len(entries),
    non_audit_modules=len(files),source_lines=sum(len(p.read_text().splitlines()) for p in files),new_modules=MODULES)
(rd/'source_counts.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
