#!/usr/bin/env python3
"""Fresh source inventory including explicit private theorem declarations."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.39.0'; RD.mkdir(parents=True,exist_ok=True)
entries=[]
rx=re.compile(r'^(?:@\[[^\]]+\]\s*)?(?:(namespace)\s+(\S+)|(section)(?:\s+(\S+))?|(end)(?:\s+(\S+))?|(?:(private)\s+)?(theorem|lemma)\s+([^\s(:]+))',re.M)
for p in sorted((ROOT/'AVOC').glob('*.lean')):
    if p.name in {'Audit.lean','FullAudit.lean'}:continue
    s=p.read_text(); stack=[]; ns=''
    for m in rx.finditer(s):
        if m.group(1):
            stack.append(ns); ns=ns+'.'+m.group(2) if ns else m.group(2)
        elif m.group(3):stack.append(ns)
        elif m.group(5):
            if stack:ns=stack.pop()
        else:
            name=ns+'.'+m.group(9) if ns else m.group(9)
            if m.group(7):name=f'_private.AVOC.{p.stem}.0.'+name
            entries.append(dict(module=str(p.relative_to(ROOT)),line=s[:m.start()].count('\n')+1,
              kind=m.group(8),name=m.group(9),qualified_name=name,private=bool(m.group(7))))
assert len(entries)==len({r['qualified_name'] for r in entries})
old=json.loads((ROOT/'results/v0.38.0/declaration_inventory.json').read_text())
oldnames={r['qualified_name'] for r in old};names={r['qualified_name'] for r in entries}
assert not oldnames-names, sorted(oldnames-names)
new=[r for r in entries if r['qualified_name'] not in oldnames]
(RD/'declaration_inventory.json').write_text(json.dumps(entries,indent=2)+'\n')
(RD/'new_inventory_entries.json').write_text(json.dumps(new,indent=2)+'\n')
audit_text='import AVOC\n\n'+''.join('#print axioms '+r['qualified_name']+'\n' for r in entries if not r['private'])
private_names=[r['qualified_name'] for r in entries if r['private']]
audit_text+='\nopen Lean Elab Command\nrun_cmd do\n  let env ← getEnv\n  let names : List String := '+json.dumps(private_names)+'\n  let mut found := 0\n  for (name, _) in env.constants.toList do\n    if names.contains name.toString then\n      found := found + 1\n      let axioms ← collectAxioms name\n      logInfo m!"\'{name.toString}\' depends on axioms: {axioms.qsort Name.lt |>.map MessageData.ofConstName |>.toList}"\n  unless found = '+str(len(private_names))+' do throwError "private declaration inventory mismatch"\n'
(ROOT/'AVOC/FullAudit.lean').write_text(audit_text)
lines=['# AVOC v0.39.0 theorem index','',f'{len(entries)} named theorem/lemma declarations, including explicit private helpers.',
       'These are source declarations, not a count of independent mathematical discoveries.','']
last=None
for r in entries:
    if r['module']!=last:last=r['module'];lines+=['',f'## {last}','']
    lines.append(f"- `{r['qualified_name']}` (source line {r['line']})")
(ROOT/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
summary=dict(total_named_theorems=len(entries),old_reported_inventory=len(old),
  newly_reported_private_helpers=sum(r['private'] for r in new),
  new_theorems=sum(not r['private'] for r in new),
  non_audit_modules=len(list((ROOT/'AVOC').glob('*.lean')))-2)
(RD/'source_counts.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
