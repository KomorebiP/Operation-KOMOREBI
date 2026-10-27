from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent.parent;S=ROOT/'source_v_viii';B=S/'book_edit_baseline';O=ROOT/'editorial/book_revision'
active=json.loads((O/'v_viii_active_sources.json').read_text());changed=[]
for key,paths in active.items():
 if key.endswith('lean_guide'):continue
 roman=key.split('_')[0]
 for path in paths:
  p=Path(path)
  if 'graphics' in path:continue
  old=p.read_text();lines=old.splitlines(keepends=True);new=[]
  for l in lines:
   if l.startswith('\\vpage{'):
    l=l.replace('Mathematical text, Part ',f'Chapter {roman}, Part ').replace('Mathematical text: ',f'Chapter {roman}: ')
    l=l.replace('compare Mathematical text, Part I,',f'compare Chapter {roman}, Part I,')
    l=l.replace('{What the final visual edition verifies}', '{How to read the evidence}')
    l=l.replace('{EVIDENCE MAP / INHERITED RECORDS AND FRESH EXAMPLES}', '{EVIDENCE MAP / FORMAL RECORDS AND FINITE EXAMPLES}')
    l=l.replace('{The final package retains original sources, new checks, build logs, and the traditional volume.}',f'{{Chapter {roman} formal companion: source, execution, and example records.}}')
   new.append(l)
  out=''.join(new)
  if out!=old:
   b=B/p.relative_to(S)
   if not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
   p.write_text(out);changed.append(str(p.relative_to(ROOT)))
(O/'v_viii_qualified_locator_journal.json').write_text(json.dumps(changed,indent=2));print(len(changed),'files with qualified source locators')
