#!/usr/bin/env python3
"""Apply only the individually reviewed XI plan. XII is owned by another agent."""
from pathlib import Path
from collections import Counter
import hashlib,json,shutil

ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT=ROOT/'editorial/rhythm_review'
plan=json.loads((OUT/'xi_xii_plan.json').read_text())
scope=json.loads((OUT/'xi_xii_scope.json').read_text())
baseline={x['file']:x['sha256'] for x in scope if '/XI/' in x['file']}
assert all('/XI/' in e['file'] and '/XII/' not in e['file'] for e in plan)
backups=OUT/'xi_xii_before'
texts={};journal=[];files=[]
for name in dict.fromkeys(e['file'] for e in plan):
    path=ROOT/name;before=path.read_text();after=before
    assert hashlib.sha256(before.encode()).hexdigest()==baseline[name],name
    target=backups/name
    assert not target.exists(),str(target)
    for e in [e for e in plan if e['file']==name]:
        count=e.get('occurrences',1)
        assert after.count(e['old'])==count,(name,e['old'],after.count(e['old']),count)
        positions=[];start=0
        for _ in range(count):
            pos=before.index(e['old'],start);positions.append(before[:pos].count('\n')+1);start=pos+len(e['old'])
        after=after.replace(e['old'],e['new'],count)
        journal.append(e|{'before_lines':positions,'occurrences':count})
    texts[name]=(before,after)
for name,(before,after) in texts.items():
    path=ROOT/name;target=backups/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target);path.write_text(after)
    files.append({'file':name,'backup':str(target.relative_to(ROOT)),
                  'before_sha256':hashlib.sha256(before.encode()).hexdigest(),
                  'after_sha256':hashlib.sha256(after.encode()).hexdigest(),
                  'journal_entries':sum(e['file']==name for e in journal),
                  'semicolons_before':before.count(';'),'semicolons_after':after.count(';')})
(OUT/'xi_xii_journal.json').write_text(json.dumps(journal,indent=2,ensure_ascii=False)+'\n')
(OUT/'xi_xii_files.json').write_text(json.dumps(files,indent=2)+'\n')
print(json.dumps({'scope':'XI ONLY','files':len(files),'journal_entries':len(journal),
                  'actual_replacements':sum(e['occurrences'] for e in journal),
                  'categories':dict(Counter(e['category'] for e in journal)),
                  'semicolons_removed':sum(e['semicolons_before']-e['semicolons_after'] for e in files)},indent=2))
