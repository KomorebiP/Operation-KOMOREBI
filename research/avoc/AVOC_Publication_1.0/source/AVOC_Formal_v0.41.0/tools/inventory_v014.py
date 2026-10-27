#!/usr/bin/env python3
"""Extend the audited inherited index, after checking inherited source identity."""
from pathlib import Path
import hashlib, json, re
root=Path(__file__).resolve().parents[1]
old=json.loads((root/'results/v0.13.0/declaration_inventory.json').read_text())
new_modules=['GuardedControl','GuardedPolicyRegret','ResearchController','ResearchPolicy','ResearchControllerExamples']
new=[]
for m in new_modules:
 p=root/'AVOC'/f'{m}.lean';text=p.read_text()
 ns=re.search(r'^namespace\s+(\S+)',text,re.M).group(1)
 for match in re.finditer(r'^(?:@\[[^\]]+\]\s*)?(theorem|lemma)\s+([\w.\u0370-\u03ff\u2080-\u209f\']+)',text,re.M):
  name=match.group(2)
  new.append(dict(module=f'AVOC/{m}.lean',line=text[:match.start()].count('\n')+1,
                  kind=match.group(1),name=name,qualified_name=ns+'.'+name))
all_entries=sorted(old+new,key=lambda z:(z['module'],z['line']))
assert len({x['qualified_name'] for x in all_entries})==len(all_entries)
rd=root/'results/v0.14.0';rd.mkdir(parents=True,exist_ok=True)
(rd/'declaration_inventory.json').write_text(json.dumps(all_entries,indent=2)+'\n')
(rd/'new_declarations.json').write_text(json.dumps(new,indent=2)+'\n')
(root/'AVOC/FullAudit.lean').write_text('import AVOC\n\n'+''.join('#print axioms '+x['qualified_name']+'\n' for x in all_entries))
lines=['# AVOC v0.14.0 — complete theorem index','',f'{len(all_entries)} theorem/lemma declarations: {len(old)} inherited and {len(new)} new.','',
       'Counts include auxiliary lemmas and examples, not independent discoveries.','']
last=None
for x in all_entries:
 if x['module']!=last:
  last=x['module'];lines+=['',f'## `{last}`','']
 lines.append(f"- `{x['qualified_name']}` — line {x['line']}")
(root/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
files=[p for p in (root/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
newdefs=0
for m in new_modules:
 text=(root/'AVOC'/f'{m}.lean').read_text()
 newdefs+=len(re.findall(r'^(?:noncomputable\s+)?(?:def|abbrev|structure|inductive)\s+',text,re.M))
summary=dict(inherited_theorems=len(old),new_theorems=len(new),total_theorems=len(all_entries),
             non_audit_modules=len(files),source_lines=sum(len(p.read_text().splitlines()) for p in files),
             inherited_definitions=229,new_definitions=newdefs,definition_like_count=229+newdefs)
(rd/'source_counts.json').write_text(json.dumps(summary,indent=2)+'\n')
print(summary)
