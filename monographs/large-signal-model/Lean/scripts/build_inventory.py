#!/usr/bin/env python3
"""Inspect explicitly named declarations in this project's fixed source style.

This is a source-index utility, not a Lean parser or a mathematical verifier.
Compiler-generated constructors, recursors and instance machinery are outside
its counts; module kernel replay checks the actual generated environment.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
DECL=re.compile(r'^[ \t]*(?:@\[[^\]\n]*\][ \t]*)*(?:noncomputable[ \t]+)?(theorem|def|structure|abbrev|inductive|instance)[ \t]+(\w+(?:\.\w+)*)')

def scan_file(path: Path) -> list[dict]:
    stack=[]
    records=[]
    for n,line in enumerate(path.read_text().splitlines(),1):
        st=line.strip()
        if st.startswith('namespace '):stack.append(('namespace',st.split()[1]))
        elif st=='noncomputable section':stack.append(('section',''))
        elif st=='section' or st.startswith('section '):stack.append(('section',st[7:].strip()))
        elif st=='end' or st.startswith('end '):
            if not stack:raise ValueError(f'unbalanced scope: {path}:{n}')
            kind,name=stack.pop()
            if st!='end' and st[4:].strip()!=name:
                raise ValueError(f'mismatched scope: {path}:{n}')
        match=DECL.match(line)
        if match:
            kind,name=match.groups()
            name='.'.join([s for k,s in stack if k=='namespace']+[name])
            records.append({'name':name,'kind':kind,'file':str(path.relative_to(ROOT)),
                            'line':n,'module':path.stem})
    if stack:raise ValueError(f'unclosed scope: {path}')
    return records

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true',help='rewrite inventory and axiom command file')
    args=ap.parse_args()
    imports=re.findall(r'^import KomorebiLSM\.(\w+)$',(ROOT/'KomorebiLSM.lean').read_text(),re.M)
    records=[]
    for m in imports:records+=scan_file(ROOT/'KomorebiLSM'/f'{m}.lean')
    if len({d['name'] for d in records})!=len(records):raise ValueError('duplicate explicit name')
    if args.write:
        (ROOT/'DECLARATIONS.json').write_text(json.dumps(records,indent=2)+'\n')
        (ROOT/'AxiomAudit.lean').write_text('import KomorebiLSM\n\n'+''.join('#print axioms '+d['name']+'\n' for d in records))
    elif records!=json.loads((ROOT/'DECLARATIONS.json').read_text()):
        raise ValueError('source declaration inventory differs')
    print(f'PASS: {len(records)} explicitly named source declarations.')
if __name__=='__main__':main()
