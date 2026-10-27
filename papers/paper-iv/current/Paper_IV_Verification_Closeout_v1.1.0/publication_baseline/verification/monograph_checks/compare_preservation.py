#!/usr/bin/env python3
"""Read-only comparison of every numbered statement and proof environment.

Run from the release root. This verifies preservation, not theorem correctness.
"""
from pathlib import Path
import re,json,hashlib,difflib,datetime,collections
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'source/complete/original_snapshot/proofread_review/PRSC_IV_Review/paper/paper4.tex'
FINAL=ROOT/'editable/traditional/Paper_IV_Traditional_Final.tex'
OUT=ROOT/'verification/monograph_checks'
ENV=['theorem','proposition','lemma','corollary','definition','example','remark','standardfact']
SHA=lambda s:hashlib.sha256(s.encode()).hexdigest()
def extract(source,environments):
    p=r'\\begin\{('+ '|'.join(environments)+r')\}(.*?)\\end\{\1\}'
    return [{'type':m.group(1),'body':m.group(2),'raw':m.group(0),'label':(re.findall(r'\\label\{([^}]+)\}',m.group(2)) or [''])[0],'source_line':source[:m.start()].count('\n')+1} for m in re.finditer(p,source,re.S)]
# Include dollar, escaped-delimiter and amsmath environments. Matrices/cases
# inside display delimiters are part of their containing formula.
MATH=re.compile(r'(?<!\\)\$\$(?:.|\n)*?(?<!\\)\$\$|(?<!\\)\$(?:\\.|[^$])*(?<!\\)\$|\\\[(?:.|\n)*?\\\]|\\\((?:.|\n)*?\\\)|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|flalign\*?|alignat\*?)\}(?:.|\n)*?\\end\{\1\}')
def math_segments(s):return [m.group(0) for m in MATH.finditer(s)]
def normalized_prose(s):
    chunks=[];prev=0
    for m in MATH.finditer(s):
        chunks.append(re.sub(r'\s+',' ',s[prev:m.start()].replace(';',',').replace('---',' ').replace('--',' ').replace('-',' ')))
        chunks.append(m.group(0));prev=m.end()
    chunks.append(re.sub(r'\s+',' ',s[prev:].replace(';',',').replace('---',' ').replace('--',' ').replace('-',' ')))
    return ''.join(chunks).strip()
def compare(original,current,kind):
    a=extract(original,ENV if kind=='statements' else ['proof']);b=extract(current,ENV if kind=='statements' else ['proof'])
    records=[]
    for i,(x,y) in enumerate(zip(a,b),1):
        xm,ym=math_segments(x['body']),math_segments(y['body'])
        rec={'ordinal':i,'environment':x['type'],'label':x['label'],'baseline_line':x['source_line'],'final_line':y['source_line'],'same_type_and_label':x['type']==y['type'] and x['label']==y['label'],'byte_identical':x['raw']==y['raw'],'equal_after_explicit_prose_punctuation_and_whitespace_normalization':normalized_prose(x['raw'])==normalized_prose(y['raw']),'math_segments_byte_identical':xm==ym,'math_segment_count':len(xm),'baseline_sha256':SHA(x['raw']),'final_sha256':SHA(y['raw'])}
        if not rec['byte_identical']:
            rec['diff']=''.join(difflib.unified_diff(x['raw'].splitlines(True),y['raw'].splitlines(True),fromfile='baseline',tofile='monograph'))
        records.append(rec)
    return {'baseline_count':len(a),'final_count':len(b),'counts_by_environment':dict(collections.Counter(x['type'] for x in b)),'same_length':len(a)==len(b),'all_types_and_labels_preserved':len(a)==len(b) and all(x['same_type_and_label'] for x in records),'all_byte_identical':len(a)==len(b) and all(x['byte_identical'] for x in records),'all_equivalent_after_explicit_prose_normalization':len(a)==len(b) and all(x['equal_after_explicit_prose_punctuation_and_whitespace_normalization'] for x in records),'all_math_segments_byte_identical':len(a)==len(b) and all(x['math_segments_byte_identical'] for x in records),'records':records}
original=BASE.read_text();current=FINAL.read_text()
statements=compare(original,current,'statements');proofs=compare(original,current,'proofs')
labels=re.findall(r'\\label\{([^}]+)\}',current)
refs=[r.strip() for rs in re.findall(r'\\(?:eqref|ref|[cC]ref|autoref|pageref|nameref)\{([^}]+)\}',current) for r in rs.split(',')]
bib=(ROOT/'editable/traditional/references.bib').read_text()
keys=set(re.findall(r'@\w+\{([^,]+),',bib));cites={r.strip() for rs in re.findall(r'\\cite\w*(?:\[[^\]]*\])?\{([^}]+)\}',current) for r in rs.split(',')}
static={'labels':len(labels),'duplicate_labels':[k for k,v in collections.Counter(labels).items() if v>1],'unresolved_refs':sorted(set(refs)-set(labels)),'unresolved_citations':sorted(cites-keys),'citation_keys':len(cites)}
report={'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Source preservation and static cross-reference integrity. This does not verify the mathematical arguments or run Lean.','baseline':{'path':str(BASE.relative_to(ROOT)),'sha256':SHA(original)},'final':{'path':str(FINAL.relative_to(ROOT)),'sha256':SHA(current)},'statements':statements,'proofs':proofs,'static_integrity':static,'new_lean_verification':False}
report['status']='PASS' if statements['baseline_count']==statements['final_count']==95 and proofs['baseline_count']==proofs['final_count']==68 and statements['all_equivalent_after_explicit_prose_normalization'] and proofs['all_equivalent_after_explicit_prose_normalization'] and statements['all_math_segments_byte_identical'] and proofs['all_math_segments_byte_identical'] and not static['duplicate_labels'] and not static['unresolved_refs'] and not static['unresolved_citations'] else 'REVIEW_REQUIRED'
(OUT/'PRESERVATION_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
lines=[f"Paper IV preservation review: {report['status']}",f"Statements: {statements['final_count']}/{statements['baseline_count']}; all byte-identical: {statements['all_byte_identical']}; all math byte-identical: {statements['all_math_segments_byte_identical']}",f"Proofs: {proofs['final_count']}/{proofs['baseline_count']}; all byte-identical: {proofs['all_byte_identical']}; all math byte-identical: {proofs['all_math_segments_byte_identical']}",f"Duplicate labels: {static['duplicate_labels']}; unresolved references: {static['unresolved_refs']}; unresolved citations: {static['unresolved_citations']}","No fresh Lean execution. Preservation is distinct from theorem verification."]
(OUT/'PRESERVATION_REVIEW.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
