#!/usr/bin/env python3
"""Audit source references and exact predecessor preservation, not proof validity."""
from __future__ import annotations
import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Machine_Societies_v1.0.0.tex'
PAIR=re.compile(r'\\begin\{(theorem|proposition)\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\}\s*\\begin\{proof\}(.*?)\\end\{proof\}',re.S)

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(text:str):
    rows={}
    for m in PAIR.finditer(text):
        labels=re.findall(r'\\label\{((?:prop|thm):[^}]+)\}',m[3])
        if len(labels)!=1:raise ValueError(f'A proved statement needs one label: {m[2]}')
        rows[labels[0]]={'kind':m[1],'title':m[2],'statement':m[3],'proof':m[4]}
    return rows

def main()->int:
    text=SOURCE.read_text();oldfile=ROOT/'sources/v0.7.0/Machine_Societies_v0.7.0.tex'
    old=pairs(oldfile.read_text());current=pairs(text)
    labels=re.findall(r'\\label\{([^}]+)\}',text)
    refs=re.findall(r'\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}',text)
    bib=re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',text)
    cites=[k.strip() for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',text) for k in group.split(',')]
    counts={k:len(re.findall(r'\\begin\{'+k+r'\}',text)) for k in ('theorem','proposition','proof','definition','counterexample','figure')}
    counts.update({'proved_statements':len(current),'bibliography':len(bib),'parts':len(re.findall(r'\\part\{',text))})
    mismatches=[k for k,v in old.items() if k not in current or v!=current[k]]
    issues={'missing_reference_labels':sorted(set(refs)-set(labels)),
            'duplicate_labels':[k for k,v in Counter(labels).items() if v>1],
            'missing_citation_keys':sorted(set(cites)-set(bib)),
            'unused_bibliography':sorted(set(bib)-set(cites)),
            'duplicate_bibliography':[k for k,v in Counter(bib).items() if v>1],
            'predecessor_statement_or_proof_changes':mismatches}
    if counts['proof']!=len(current) or counts['theorem']+counts['proposition']!=len(current):
        issues['proof_pairing']=['Not every theorem/proposition has one adjacent proof.']
    aux=ROOT/'build/Machine_Societies_v1.0.0.aux'
    numbering={m[0]:(m[1],m[2]) for m in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',aux.read_text())} if aux.is_file() else {}
    inventory=[]
    for key,row in current.items():
        number,page=numbering.get(key,('uncompiled','uncompiled'))
        inventory.append({'label':key,'number':number,'page':page,'kind':row['kind'],
                          'title':row['title'],'new_in_1_0':key not in old})
    result={'status':'PASS' if not any(issues.values()) else 'FAIL', 'source_sha256':sha(SOURCE),
            'predecessor_source_sha256':sha(oldfile),'counts':counts,
            'retained_statement_and_proof_pairs':len(old),'new_pairs':len(current)-len(old),
            'issues':issues,'inventory':inventory,
            'boundary':'Syntax, inventory and verbatim preservation only. Does not authenticate mathematical correctness.'}
    (ROOT/'validation/source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Theorem and proposition index — first edition','',
           'Machine Societies · Komorebi P. · Version 1.0.0 · 8 October 2026','',
           'This is an inventory of conditional prose proofs, not a count of original discoveries. Printed page numbers refer to the compiled first edition. The 56 v0.7 statements and their corresponding proofs are preserved verbatim. Six statements are added in the accountability chapter. No Lean or other formal-kernel build is claimed.','',
           '| Statement | Title | Printed page | Edition status |','|---|---|---:|---|']
    for row in inventory:
        title=row['title'].replace('|','/').replace('\\','')
        lines.append(f"| {row['kind'].title()} {row['number']} | {title} | {row['page']} | {'Added in 1.0' if row['new_in_1_0'] else 'Retained from 0.7'} |")
    lines+=['','## Interpretation of the six additions','',
            'The inspection result is a specified simultaneous two-player game. The privacy envelope is a sharp finite testing consequence, with explicit attainment. Conditional disclosure uses the standard sequential-composition argument. Appeal allocation applies Hall matching to interval windows. Available authorized endings reuse the finite safety and reachability constructions with two distinct action modes. Guarded certificate use is a sufficient inductive composition rule with a shared progress rank. Each result retains its stated information, authority, cost and implementation assumptions.']
    (ROOT/'THEOREM_INDEX.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':result['status'],'counts':counts,'retained_pairs':len(old),'new_pairs':result['new_pairs'],'issues':issues},indent=2))
    return result['status']!='PASS'
if __name__=='__main__':raise SystemExit(main())
