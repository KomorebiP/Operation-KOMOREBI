#!/usr/bin/env python3
"""Exact conservation of all nine retrieved modular mathematical parts.

This comparator checks source identity and the displayed-body inventory. It is
not a new proof-validity audit and does not assert compiler or continuum closure.
"""
from pathlib import Path
import collections,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent.parent
BEFORE=ROOT/'provenance/current_retrieved_baseline/traditional/parts'
AFTER=ROOT/'editable/traditional/parts'
KINDS=('theorem','proposition','lemma','corollary','definition','example','remark','boundary','certificate','conjecture','standardfact','classical','construction','statement')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def collect(s,kinds):
    return [(m.group(1),m.group(2)) for m in re.finditer(r'\\begin\{('+'|'.join(kinds)+r')\}(.*?)\\end\{\1\}',s,re.S)]
def mathspans(s):
    # Logical mathematical spans are also preserved because the entire part is
    # byte-identical. This inventory makes the supplemented displays explicit.
    return re.findall(r'\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)|\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}',s,re.S)
def main():
    failures=[];rows=[];counts=collections.Counter();proofs=0;spans=0
    filenames=sorted(p.name for p in BEFORE.glob('*.tex'))
    if len(filenames)!=9:failures.append({'problem':'Expected nine retrieved baseline mathematical parts','count':len(filenames)})
    if filenames!=sorted(p.name for p in AFTER.glob('*.tex')):failures.append({'problem':'Part inventory changed'})
    wrapper=(ROOT/'editable/traditional/Paper_VII_Traditional_Final.tex').read_text()
    actual=re.findall(r'\\input\{parts/([^}]+)\}',wrapper)
    if actual!=filenames:failures.append({'problem':'Source part input order changed','actual':actual,'expected':filenames})
    for name in filenames:
        b=BEFORE/name;a=AFTER/name
        if not a.is_file():failures.append({'part':name,'problem':'Part missing'});continue
        old=b.read_text();new=a.read_text();record=collect(old,KINDS);current=collect(new,KINDS);pf=collect(old,('proof',));cp=collect(new,('proof',));ms=mathspans(old);cms=mathspans(new)
        if b.read_bytes()!=a.read_bytes():failures.append({'part':name,'problem':'Complete source part differs'})
        if record!=current:failures.append({'part':name,'problem':'Protected statement body differs'})
        if pf!=cp:failures.append({'part':name,'problem':'Protected proof body differs'})
        if ms!=cms:failures.append({'part':name,'problem':'Logical math span differs'})
        counts.update(k for k,v in record);proofs+=len(pf);spans+=len(ms)
        rows.append({'baseline_path':str(b.relative_to(ROOT)),'current_path':str(a.relative_to(ROOT)),'baseline_sha256':sha(b),'current_sha256':sha(a),'byte_identical':b.read_bytes()==a.read_bytes(),'protected_environments':len(record),'numbered_records':sum(k!='statement' for k,v in record),'unnumbered_statements':sum(k=='statement' for k,v in record),'proof_bodies':len(pf),'logical_math_spans':len(ms)})
    protected=sum(counts.values());numbered=protected-counts['statement'];theorems=sum(counts[k] for k in ['theorem','proposition','lemma','corollary'])
    if (protected,numbered,counts['statement'],theorems,proofs)!=(147,142,5,96,107):failures.append({'problem':'Retrieved inventory differs from contract','actual':[protected,numbered,counts['statement'],theorems,proofs]})
    report={'schema':'komorebi.paper_vii.exact_monograph_preservation.v1','status':'FAIL' if failures else 'PASS','scope':'Complete byte identity of nine current retrieved mathematical parts, including all supplemented displays, and exact ordered statement/proof bodies. No new proof-validity audit.','baseline_parts':rows,'current_wrapper_path':'editable/traditional/Paper_VII_Traditional_Final.tex','current_wrapper_sha256':sha(ROOT/'editable/traditional/Paper_VII_Traditional_Final.tex'),'protected_environments':protected,'numbered_records':numbered,'unnumbered_statements':counts['statement'],'theorem_like_records':theorems,'proof_bodies':proofs,'record_kinds':dict(counts),'logical_math_spans':spans,'byte_identical_parts':sum(x['byte_identical'] for x in rows),'failures':failures}
    (ROOT/'verification/MONOGRAPH_PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='baseline_parts'},indent=2));return bool(failures)
if __name__=='__main__':sys.exit(main())
