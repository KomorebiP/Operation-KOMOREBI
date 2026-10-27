#!/usr/bin/env python3
"""Compare protected mathematical source against the corrected October5 edition.

This is byte-level preservation, token inventory and local link checking.
It does not audit the validity of the inherited mathematical proofs.
"""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
CHECKS=Path(__file__).resolve().parent
BASE=CHECKS/'reference/baseline_traditional_2026-10-05.tex'
CURRENT=ROOT/'editable/traditional/Paper_V_Traditional_Final.tex'
ENVIRONMENTS=['theorem','proposition','lemma','corollary','definition','example','construction','conjecture','remark','boundary','certificate','classical','standardfact']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(t,names):
    pat=r'\\begin\{(?P<env>'+ '|'.join(names)+r')\}.*?\\end\{(?P=env)\}'
    return [(m.group('env'),m.group(0)) for m in re.finditer(pat,t,re.S)]
def label(block):
    m=re.search(r'\\label\{([^}]+)\}',block)
    return m.group(1) if m else None
def expansion(p,seen=None):
    seen=set() if seen is None else seen
    p=p.resolve()
    if p in seen:return ''
    seen.add(p);text=p.read_text()
    def sub(m):
        q=p.parent/m.group(1)
        if not q.suffix:q=q.with_suffix('.tex')
        if not q.resolve().is_relative_to(ROOT.resolve()) or not q.is_file():return m.group(0)
        return expansion(q,seen)
    return re.sub(r'\\input\{([^}]+)\}',sub,text)
def groups(pat,t):
    out=[]
    for x in re.findall(pat,t,re.S):out.extend(y.strip() for y in x.split(',') if '#' not in y)
    return out
def maths(t):
    return {
        'inline_dollars':re.findall(r'(?<![\\$])\$(?!\$)(.*?)(?<!\\)\$(?!\$)',t,re.S),
        'inline_parentheses':re.findall(r'(?<!\\)\\\((.*?)(?<!\\)\\\)',t,re.S),
        'display_brackets':re.findall(r'(?<!\\)\\\[(.*?)(?<!\\)\\\]',t,re.S),
        'numbered_equation_environments':[x[1] for x in extract(t,['equation','equation\\*','align','align\\*','gather','gather\\*','multline','multline\\*'])]
    }

a=BASE.read_text();b=CURRENT.read_text();numbered_a=extract(a,ENVIRONMENTS);numbered_b=extract(b,ENVIRONMENTS)
proof_a=extract(a,['proof']);proof_b=extract(b,['proof'])
def diff(rows1,rows2):
    return [{'ordinal':i+1,'baseline_environment':rows1[i][0] if i<len(rows1) else None,
             'baseline_label':label(rows1[i][1]) if i<len(rows1) else None,
             'current_environment':rows2[i][0] if i<len(rows2) else None,
             'current_label':label(rows2[i][1]) if i<len(rows2) else None}
            for i in range(max(len(rows1),len(rows2))) if i>=len(rows1) or i>=len(rows2) or rows1[i]!=rows2[i]]
numbered_diff=diff(numbered_a,numbered_b);proof_diff=diff(proof_a,proof_b)
ma=maths(a);mb=maths(b);math_review={}
for kind,tokens in ma.items():
    missing=Counter(tokens)-Counter(mb[kind]);math_review[kind]={'baseline_tokens':len(tokens),'current_tokens':len(mb[kind]),'missing_baseline_token_occurrences':sum(missing.values()),'missing_examples':[{'token':s[:300],'multiplicity':n} for s,n in list(missing.items())[:12]]}
expanded=expansion(CURRENT);labels=groups(r'\\label\{([^}]+)\}',expanded);refs=groups(r'\\(?:eqref|(?:c|C)?ref)\{([^}]+)\}',expanded)
citations=set(groups(r'\\cite\w*\*?(?:\[[^\]]*\])?\{([^}]+)\}',expanded));old_cites=set(groups(r'\\cite\w*\*?(?:\[[^\]]*\])?\{([^}]+)\}',a))
bib=(CURRENT.parent/'references.bib').read_text();bib_keys=set(re.findall(r'@\w+\s*\{\s*([^,]+),',bib))
report={'schema':'komorebi.paper_v.monograph_preservation.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'baseline':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':sha(BASE)},'current':{'path':CURRENT.relative_to(ROOT).as_posix(),'sha256':sha(CURRENT)},
        'numbered_records':{'expected':119,'baseline':len(numbered_a),'current':len(numbered_b),'all_byte_identical':not numbered_diff,'differences':numbered_diff},
        'proof_bodies':{'expected':83,'baseline':len(proof_a),'current':len(proof_b),'all_byte_identical':not proof_diff,'differences':proof_diff},
        'canonical_formula_inventory':math_review,'references':{'duplicate_labels':[k for k,v in Counter(labels).items() if v>1],'unresolved_local_references':sorted(set(refs)-set(labels))},
        'citations':{'baseline_keys':sorted(old_cites),'current_keys':sorted(citations),'missing_baseline_keys':sorted(old_cites-citations),'unresolved_bib_keys':sorted(citations-bib_keys)},
        'non_claim':'Byte preservation and local syntax/link checks do not establish proof validity, external source authenticity or Lean acceptance.'}
passed=len(numbered_a)==len(numbered_b)==119 and len(proof_a)==len(proof_b)==83 and not numbered_diff and not proof_diff
passed &= all(x['missing_baseline_token_occurrences']==0 for x in math_review.values())
passed &= not report['references']['duplicate_labels'] and not report['references']['unresolved_local_references'] and not report['citations']['missing_baseline_keys'] and not report['citations']['unresolved_bib_keys']
report['status']='PASS' if passed else 'FAIL';(CHECKS/'PROOF_PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if passed else 1)
