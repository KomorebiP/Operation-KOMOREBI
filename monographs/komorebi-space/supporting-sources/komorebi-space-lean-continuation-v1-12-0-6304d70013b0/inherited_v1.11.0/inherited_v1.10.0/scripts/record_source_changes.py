#!/usr/bin/env python3
"""Record exact source changes against the accepted v1.9.0 monograph."""
from pathlib import Path
import hashlib, json, difflib

root = Path(__file__).resolve().parents[1]
old_candidates = [root.parent/'monograph_v1.9.0/source',
                  root.parent/'history/v1.9.0/source', root/'history/v1.9.0/source']
old = next((p for p in old_candidates if p.is_dir()), None)
if old is None:
    raise SystemExit('Missing v1.9.0 source predecessor: restore monograph_v1.9.0/source or history/v1.9.0/source before comparing.')
new = root/'source'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p.relative_to(old)):sha(p) for p in sorted(old.rglob('*')) if p.is_file()}
after = {str(p.relative_to(new)):sha(p) for p in sorted(new.rglob('*')) if p.is_file()}
changes = []
diff = []
for n in sorted(before.keys() | after.keys()):
    if before.get(n) == after.get(n): continue
    changes.append({'path':n,'parent_sha256':before.get(n),'new_sha256':after.get(n)})
    if n.endswith(('.tex','.sty')):
        a=(old/n).read_text().splitlines(keepends=True) if n in before else []
        b=(new/n).read_text().splitlines(keepends=True) if n in after else []
        diff.extend(difflib.unified_diff(a,b,fromfile='v1.9.0/'+n,tofile='v1.10.0/'+n))
(root/'audit/SOURCE_CHANGES.json').write_text(json.dumps({'parent_version':'1.9.0','version':'1.10.0','changed':changes,'unchanged_count':sum(before.get(n)==h for n,h in after.items()),'source_sha256':after},indent=2)+'\n')
(root/'audit/MANUSCRIPT_CHANGES.diff').write_text(''.join(diff))
print(json.dumps({'changed_files':[c['path'] for c in changes],'unchanged_files':sum(before.get(n)==h for n,h in after.items())}))
