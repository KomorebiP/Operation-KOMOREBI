#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
DECL=re.compile(r"^\s*(?:@\[[^\n\]]+\]\s*)*(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)",re.MULTILINE)
def main():
 root=Path(__file__).resolve().parents[1]
 names=[]; records=[]
 for path in sorted((root/'lean'/'KomorebiPadic').glob('*.lean')):
  text=path.read_text(encoding='utf-8')
  for m in DECL.finditer(text):
   name=m.group(1); line=text.count('\n',0,m.start())+1
   names.append(name); records.append({'name':name,'file':str(path.relative_to(root)),'line':line})
 dup=sorted({n for n in names if names.count(n)>1})
 if dup: raise SystemExit(f'duplicate theorem names: {dup}')
 if len(names)!=165: raise SystemExit(f'expected 165 theorems, got {len(names)}')
 out=root/'verification'/'AxiomAuditBlock11.lean'
 lines=['import KomorebiPadic','','namespace KomorebiPadic','']+[f'#print axioms {n}' for n in names]+['','end KomorebiPadic','']
 out.write_text('\n'.join(lines),encoding='utf-8')
 (root/'results'/'theorem_names_block11.txt').write_text('\n'.join(names)+'\n',encoding='utf-8')
 (root/'results'/'theorem_locations_block11.json').write_text(json.dumps(records,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(f'theorems={len(names)}\nwrote={out}')
if __name__=='__main__': main()
