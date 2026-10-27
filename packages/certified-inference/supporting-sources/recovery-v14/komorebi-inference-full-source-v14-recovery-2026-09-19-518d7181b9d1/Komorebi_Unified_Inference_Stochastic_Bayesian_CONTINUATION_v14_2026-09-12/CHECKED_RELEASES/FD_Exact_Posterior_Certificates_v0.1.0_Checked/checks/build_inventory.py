#!/usr/bin/env python3
"""Build declaration inventory and a full kernel axiom audit for the active source slice."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
NEW=['RationalMatrixCertificates','RationalPacketCertificates','RationalCertificateChecker','RationalCandidateAcceptance',
     'GramNoiseFloor','RationalModelSemantics','PosteriorEnclosureBounds','RationalPosteriorCertificate',
     'GeneratedExactScalar','GeneratedExactRotated']

def strip_comments(s):
    out=[];i=0;depth=0
    while i<len(s):
        if s.startswith('/-',i):depth+=1;i+=2;continue
        if depth and s.startswith('-/',i):depth-=1;i+=2;continue
        if depth:
            out.append('\n' if s[i]=='\n' else ' ');i+=1;continue
        if s.startswith('--',i):
            j=s.find('\n',i)
            if j<0:break
            out.append('\n');i=j+1;continue
        out.append(s[i]);i+=1
    return ''.join(out)

def main():
    inherited=json.loads((ROOT/'INHERITED_DECLARATIONS.json').read_text())
    result=[dict(x,previous_group=x.get('group'),group='inherited_v6') for x in inherited]
    for mod in NEW:
        stack=[]
        for ln,line in enumerate(strip_comments((ROOT/'Komorebi'/f'{mod}.lean').read_text()).splitlines(),1):
            line=line.strip()
            if line.startswith('namespace '):stack.append(line.split()[1]);continue
            if line.startswith('end '):
                if not stack or stack[-1]!=line.split()[1]:raise ValueError(f'Namespace mismatch: {mod} {line} {stack}')
                stack.pop();continue
            m=re.match(r'(?:@\[[^\]]+\]\s*)?(theorem|lemma)\s+([^\s(:]+)',line)
            if m:
                name='.'.join([*stack,m.group(2)])
                result.append(dict(name=name,module=mod,kind=m.group(1),line=ln,group='new'))
    if len({x['name'] for x in result})!=len(result):raise ValueError('Duplicate theorem name')
    (ROOT/'DECLARATIONS.json').write_text(json.dumps(result,indent=2)+'\n')
    base=list(json.loads((ROOT/'INHERITED_SOURCES.json').read_text()))
    order=base+NEW+['RationalPosteriorAxiomAudit']
    (ROOT/'MODULE_ORDER.json').write_text(json.dumps(order,indent=2)+'\n')
    text='\n'.join('import Komorebi.'+m for m in base+NEW)+'\n\n'
    text+='\n'.join('#print axioms '+x['name'] for x in result)+'\n'
    (ROOT/'Komorebi/RationalPosteriorAxiomAudit.lean').write_text(text)
    print(json.dumps(dict(modules=len(order),inherited=len(inherited),new=len(result)-len(inherited),total=len(result))))
if __name__=='__main__':main()
