#!/usr/bin/env python3
"""Index the explicit declarations in this project and regenerate #print axioms requests.
Supports the namespace/section style used here; not a general Lean parser.
"""
from pathlib import Path
import re, json
root=Path(__file__).resolve().parents[1]
# Index explicit named declarations, with their namespace and source line.
entries=[]
for p in sorted((root/'KomorebiSpace').glob('*.lean')):
 s=p.read_text()
 # Preserve line numbering while stripping nested block comments.
 out=[]; depth=0; i=0
 while i<len(s):
  if s[i:i+2]=='/-':depth+=1;out.extend('  ');i+=2
  elif depth and s[i:i+2]=='-/':depth-=1;out.extend('  ');i+=2
  elif depth:out.append('\n' if s[i]=='\n' else ' ');i+=1
  else:out.append(s[i]);i+=1
 stack=[]
 for num,line in enumerate(''.join(out).splitlines(),1):
  line=line.split('--',1)[0].strip()
  m=re.match(r'namespace\s+(\S+)',line)
  if m:stack.append(('namespace',m.group(1)));continue
  m=re.match(r'(?:noncomputable\s+)?section(?:\s+(\S+))?$',line)
  if m:stack.append(('section',m.group(1)));continue
  m=re.match(r'end(?:\s+(\S+))?$',line)
  if m:
   if not stack:raise RuntimeError((p,num,'extra end'))
   kind,name=stack.pop()
   if m.group(1) and name!=m.group(1):raise RuntimeError((p,num,'scope',stack,name,m.group(1)))
   continue
  m=re.search(r'\b(theorem|def|abbrev|structure)\s+([^\s({:]+)',line)
  if m:
   full='.'.join([n for k,n in stack if k=='namespace']+[m.group(2)])
   entries.append({'name':full,'kind':m.group(1),'file':str(p.relative_to(root)),'line':num})
 if stack:raise RuntimeError((p,stack))
(root/'audit/declaration_index.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False)+'\n')
thms=[e for e in entries if e['kind']=='theorem']
text='import KomorebiSpace\n\nset_option autoImplicit false\n\n'+''.join('#print axioms '+e['name']+'\n' for e in thms)
(root/'checks/AxiomAudit.lean').write_text(text)
print('explicit declarations',len(entries),'theorems',len(thms))
print('\n'.join(e['name'] for e in thms))
