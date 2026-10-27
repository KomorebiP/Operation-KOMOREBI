#!/usr/bin/env python3
"""Check the source inventory and references. This does not verify mathematical proofs."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='Machine_Understanding_v1.0.0'

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'build'/'source_audit.json')
    args=p.parse_args()
    raw=(ROOT/(BASE+'.tex')).read_text()
    # Ignore comments while retaining escaped percent signs.
    text=re.sub(r'(?<!\\)%[^\n]*','',raw)
    labels=re.findall(r'\\label\{([^}]+)\}',text)
    refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text)
    keys=re.findall(r'\\bibitem\{([^}]+)\}',text)
    cites=[k.strip() for group in re.findall(r'\\cite\{([^}]+)\}',text) for k in group.split(',')]
    errors=[]
    for label,count in Counter(labels).items():
        if count!=1:errors.append('Duplicate label: '+label)
    for key,count in Counter(keys).items():
        if count!=1:errors.append('Duplicate bibliography key: '+key)
    errors.extend('Missing reference: '+x for x in sorted(set(refs)-set(labels)))
    errors.extend('Missing bibliography key: '+x for x in sorted(set(cites)-set(keys)))
    errors.extend('Unused bibliography key: '+x for x in sorted(set(keys)-set(cites)))
    statements=re.findall(r'\\begin\{(theorem|proposition)\}\[([^]]+)\]\\label\{([^}]+)\}(.*?)\\end\{\1\}',text,re.S)
    ordered=list(re.finditer(r'\\begin\{(theorem|proposition)\}',text))
    pairs=[]
    for i,m in enumerate(ordered):
        piece=text[m.start():ordered[i+1].start() if i+1<len(ordered) else len(text)]
        proofs=re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}',piece,re.S)
        if len(proofs)!=1:errors.append(f'Statement {i+1} is not followed by exactly one proof.')
        else:pairs.append(hashlib.sha256(proofs[0].encode()).hexdigest())
    inventory={k:len(re.findall(r'\\begin\{'+k+r'\}',text)) for k in ['theorem','proposition','definition','counterexample','proof','figure']}
    expected={'theorem':10,'proposition':10,'definition':3,'counterexample':12,'proof':20,'figure':8}
    if inventory!=expected:errors.append('Inventory differs from declared first edition.')
    declared=json.loads((ROOT/'CLAIMS.json').read_text())['claims']
    if {s[2] for s in statements}!={s['id'] for s in declared}:errors.append('Claim ledger does not match formal statement labels.')
    figures=re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',text)
    for figure in figures:
        if not (ROOT/figure).is_file():errors.append('Missing figure: '+figure)
    result={'status':'passed' if not errors else 'failed','source_sha256':hashlib.sha256(raw.encode()).hexdigest(),
            'inventory':inventory,'bibliography_entries':len(keys),'label_count':len(labels),'reference_count':len(refs),
            'proof_hashes_in_statement_order':pairs,'errors':errors,
            'scope':'Syntactic source, proof-pairing and file-presence audit; not proof-kernel verification.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','inventory','bibliography_entries','errors')},indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
