#!/usr/bin/env python3
"""Inventory all active theorem/lemma declarations and generate a complete axiom audit.

Inherited qualified names are taken from preserved inventories and checked
against immutable source hashes. New nested namespaces and anonymous/named
sections are tracked explicitly. Declaration counts must match in every file.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT='RoundoffSolverAxiomAudit'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def without_comments(s:str)->str:
    # Retain newlines for source positions, including nested Lean block comments.
    out=[];i=0;depth=0;string=False
    while i<len(s):
        if depth:
            if s[i:i+2]=='/-':depth+=1;out.extend('  ');i+=2
            elif s[i:i+2]=='-/':depth-=1;out.extend('  ');i+=2
            else:out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif string:
            out.append(s[i])
            if s[i]=='\\' and i+1<len(s):out.append(s[i+1]);i+=2;continue
            if s[i]=='"':string=False
            i+=1
        elif s[i:i+2]=='/-':depth=1;out.extend('  ');i+=2
        elif s[i:i+2]=='--':
            j=s.find('\n',i)
            if j<0:j=len(s)
            out.extend(' '*(j-i));i=j
        else:
            if s[i]=='"':string=True
            out.append(s[i]);i+=1
    if depth:raise RuntimeError('Unclosed block comment.')
    return ''.join(out)

def parse_new(module:str,path:Path)->list[dict]:
    txt=without_comments(path.read_text());stack=[];ns='';found=[]
    for line_no,line in enumerate(txt.splitlines(),1):
        if match:=re.match(r'^namespace\s+(\S+)\s*$',line):
            stack.append(('namespace',ns));ns=ns+'.'+match[1] if ns else match[1]
        elif re.match(r'^(?:noncomputable\s+)?section(?:\s+\S+)?\s*$',line):
            stack.append(('section',ns))
        elif re.match(r'^end(?:\s+\S+)?\s*$',line):
            if not stack:raise RuntimeError(f'{module}:{line_no}: unmatched end')
            _,ns=stack.pop()
        if match:=re.match(r'^(?:@\[[^\n]+\]\s*)?(?:protected\s+)?(theorem|lemma)\s+([^\s(:{]+)',line):
            if not ns:raise RuntimeError('Declaration outside a tracked namespace.')
            found.append(dict(name=ns+'.'+match[2],module=module,kind=match[1],line=line_no,group='new'))
    if any(kind=='namespace' for kind,_ in stack):raise RuntimeError(f'{module}: unclosed namespace')
    # Lean permits a top-level section (including noncomputable section) to end at EOF.
    return found

def main()->None:
    mods={p.stem:p for p in (ROOT/'Komorebi').glob('*.lean') if p.stem!=AUDIT}
    inherited=json.loads((ROOT/'INHERITED_SOURCES.json').read_text())
    old={}
    directory=ROOT.parent/'inherited'
    inventories=([folder/'DECLARATIONS.json' for folder in directory.iterdir()]
                 if directory.is_dir() else [ROOT/'INHERITED_DECLARATIONS.json'])
    for inventory in inventories:
        for d in json.loads(inventory.read_text()):
            if d['module'] not in inherited:continue
            key=d['name'];value={**d,'group':'inherited','previous_group':d.get('previous_group',d.get('group'))}
            if key in old:
                assert old[key]['module']==value['module'] and old[key]['kind']==value['kind']
            else:old[key]=value
    decls=list(old.values())
    for n,p in mods.items():
        if n in inherited:
            assert sha(p)==inherited[n]['sha256'],f'Changed inherited source {n}'
        else:decls.extend(parse_new(n,p))
    assert len({d['name'] for d in decls})==len(decls),'Duplicate declarations.'
    for n,p in mods.items():
        count=len(re.findall(r'(?m)^(?:@\[[^\n]+\]\s*)?(?:protected\s+)?(?:theorem|lemma)\s+[^\s(:{]+',without_comments(p.read_text())))
        assert count==sum(d['module']==n for d in decls),(n,count)
    order=[];visiting=set()
    def visit(n:str)->None:
        if n in order:return
        if n in visiting:raise RuntimeError('Import cycle '+n)
        visiting.add(n)
        for d in re.findall(r'^import Komorebi\.(\w+)',mods[n].read_text(),re.M):
            if d not in mods:raise RuntimeError('Missing dependency '+d)
            visit(d)
        visiting.remove(n);order.append(n)
    for n in sorted(mods):visit(n)
    decls.sort(key=lambda d:(order.index(d['module']),d['line']))
    (ROOT/'DECLARATIONS.json').write_text(json.dumps(decls,indent=2)+'\n')
    (ROOT/'INHERITED_DECLARATIONS.json').write_text(json.dumps([d for d in decls if d['group']=='inherited'],indent=2)+'\n')
    (ROOT/'MODULE_ORDER.json').write_text(json.dumps(order+[AUDIT],indent=2)+'\n')
    src='\n'.join(['import Komorebi.'+n for n in order]+['']+
                  ['#print axioms '+d['name'] for d in decls])+'\n'
    (ROOT/'Komorebi'/f'{AUDIT}.lean').write_text(src)
    print(json.dumps(dict(modules=len(order)+1,inherited_modules=len(inherited),
        declarations=len(decls),new=sum(d['group']=='new' for d in decls)),indent=2))

if __name__=='__main__':main()
