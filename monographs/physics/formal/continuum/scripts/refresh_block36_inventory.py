#!/usr/bin/env python3
"""Rebuild the v0.36 declaration inventory from the frozen v0.35 inventory."""
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify import strip_comments_and_strings
MOD='KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction'
REL=Path(MOD.replace('.','/')+'.lean')
ORIGIN='block36_weighted_octree_L2_density'
PAT=re.compile(r'^(?:@\[[^\]]+\]\s*)?(?:noncomputable\s+)?(theorem|def|structure|abbrev)\s+([^\s({:]+)')
def scan():
 text=strip_comments_and_strings((ROOT/REL).read_text()); stack=[]; rows=[]
 for lineno,line in enumerate(text.splitlines(),1):
  s=line.strip(); ns=re.match(r'^namespace\s+(\S+)',s); end=re.match(r'^end(?:\s+(\S+))?$',s); decl=PAT.match(s)
  if ns: stack.append(ns.group(1))
  elif end:
   if end.group(1) and stack and end.group(1)==stack[-1]: stack.pop()
  elif decl: rows.append({'name':'.'.join(stack+[decl.group(2)]),'kind':decl.group(1),'module':MOD,'source_file':str(REL),'line':lineno,'origin':ORIGIN})
 if stack: raise ValueError(stack)
 return rows
inv=json.loads((ROOT/'reference/block35_declaration_inventory.json').read_text()); rows=scan(); inv['modules'].append(MOD); inv['declarations'].extend(rows)
(ROOT/'declaration_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
(ROOT/'AuditBlock36.lean').write_text('import '+MOD+'\n\n'+''.join(f'#print axioms {d["name"]}\n' for d in rows))
(ROOT/'CheckBlock36API.lean').write_text('import '+MOD+'\n\n'+''.join(f'#check {d["name"]}\n' for d in rows))
summary={'modules':len(inv['modules']),'declarations':len(inv['declarations']),'theorems':sum(d['kind']=='theorem' for d in inv['declarations']),'block36_declarations':len(rows),'block36_theorems':sum(d['kind']=='theorem' for d in rows),'by_kind':{k:sum(d['kind']==k for d in rows) for k in ['theorem','def','structure','abbrev']}}
(ROOT/'verification/block36_inventory_summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
