#!/usr/bin/env python3
"""Build the versioned inventory from the unchanged prior index plus new modules."""
from pathlib import Path
import hashlib,json,re,zipfile
root=Path(__file__).resolve().parents[1]
old=json.loads((root/'results/v0.20.0/declaration_inventory.json').read_text())
modules=['AttemptAccounting','AttemptRecovery','AttemptCodec','AttemptExamples']
new=[]
for m in modules:
    p=root/'AVOC'/f'{m}.lean';text=p.read_text();ns=re.search(r'^namespace\s+(\S+)',text,re.M).group(1)
    for match in re.finditer(r'^(?:@\[[^\]]+\]\s*)?(theorem|lemma)\s+([\w.\u0370-\u03ff\u2080-\u209f\']+)',text,re.M):
        name=match.group(2);new.append(dict(module=f'AVOC/{m}.lean',line=text[:match.start()].count('\n')+1,kind=match.group(1),name=name,qualified_name=ns+'.'+name))
entries=sorted(old+new,key=lambda x:(x['module'],x['line']));assert len({x['qualified_name'] for x in entries})==len(entries)
rd=root/'results/v0.21.0';rd.mkdir(exist_ok=True,parents=True)
for name,obj in [('declaration_inventory',entries),('new_declarations',new)]:
    (rd/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
(root/'AVOC/FullAudit.lean').write_text('import AVOC\n\n'+''.join('#print axioms '+x['qualified_name']+'\n' for x in entries))
text=(root/'AVOC.lean').read_text()
for m in modules:
    if f'import AVOC.{m}\n' not in text:text+=f'import AVOC.{m}\n'
(root/'AVOC.lean').write_text(text)
lines=['# AVOC v0.21.0 — complete declaration index','',f'{len(entries)} theorem/lemma declarations: {len(old)} inherited plus {len(new)} new.','Counts include helper lemmas and concrete examples.','']
last=None
for x in entries:
    if x['module']!=last:last=x['module'];lines+=['',f'## `{last}`','']
    lines.append(f"- `{x['qualified_name']}` — line {x['line']}")
(root/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
files=[p for p in (root/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
oldcounts=json.loads((root/'results/v0.20.0/source_counts.json').read_text())
newdefs=sum(len(re.findall(r'^(?:noncomputable\s+)?(?:def|abbrev|structure|inductive)\s+', (root/'AVOC'/f'{m}.lean').read_text(),re.M)) for m in modules)
summary=dict(inherited_theorems=len(old),new_theorems=len(new),total_theorems=len(entries),non_audit_modules=len(files),source_lines=sum(len(p.read_text().splitlines()) for p in files),inherited_definitions=oldcounts['definition_like_count'],new_definitions=newdefs,definition_like_count=oldcounts['definition_like_count']+newdefs)
(rd/'source_counts.json').write_text(json.dumps(summary,indent=2)+'\n')
print(summary)
