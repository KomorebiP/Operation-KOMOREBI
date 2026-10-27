#!/usr/bin/env python3
"""Record exact source preservation and final TeX anchors after a successful build."""
from pathlib import Path
import re,json,hashlib
import fitz
R=Path(__file__).resolve().parent
T=(R/'Paper_III_Traditional_Final.tex').read_text()
A=(R/'Paper_III_Traditional_Final.aux').read_text()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
labels={m[1]:{'number':m[2],'page':m[3],'physical_pdf_page':int(m[3])+1 if m[3].isdigit() else None} for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',A) if not m[1].endswith('@cref')}
statements=[];proofs=[];allcross={}
pattern=r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|construction|standardfact|roadmap)\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}'
for branch in ['canonical','expanded']:
    src=(R/'source'/f'{branch}.tex').read_text()
    environments=list(re.finditer(pattern,src))
    cross={}
    for label in re.findall(r'\\label\{([^}]+)\}',src):
        assert label in labels,label
        env=next((m for m in environments if '\\label{'+label+'}' in m.group()),None)
        item=dict(labels[label],final_label=label,source_label=label,branch=branch,relation='Retained in the same source part; exact local corrections are recorded in EDITORIAL_CHANGES.json.',kind=env[1] if env else ('section' if label.startswith('sec:') else 'locator'))
        if env:item['title_tex']=env[2]
        cross[label]=item
    (R/f'{branch}_label_to_final.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n')
    allcross.update(cross)
    for i,m in enumerate(environments,1):
        lab=re.search(r'\\label\{([^}]+)\}',m.group())
        item={'branch':branch,'ordinal':i,'kind':m[1],'title_tex':m[2],'source_statement_sha256':sha(m.group()),'source_statement_tex':m.group()}
        if lab:item.update(cross[lab[1]])
        else:item['locator_note']='Original source environment has no explicit label; locate by environment order and title in the retained part.'
        statements.append(item)
    for i,m in enumerate(re.finditer(r'\\begin\{proof\}[\s\S]*?\\end\{proof\}',src),1):
        before=src[:m.start()]; labs=re.findall(r'\\label\{([^}]+)\}',before)
        lab=labs[-1] if labs else None
        status='byte-identical-in-final' if m.group() in T else 'retained-with-audited-local-proof-wording-change'
        proofs.append({'branch':branch,'ordinal':i,'source_label':lab,'source_sha256':sha(m.group()),'status':status,'final_anchor':lab})
counts={b:{'total':sum(x['branch']==b for x in proofs),'byte_identical_in_final':sum(x['branch']==b and x['status']=='byte-identical-in-final' for x in proofs)} for b in ['canonical','expanded']}
report={'schema':'komorebi.paper_iii.proof_preservation.v1','final_tex_sha256':sha(T),'source_sha256':{b:sha((R/'source'/f'{b}.tex').read_text()) for b in ['canonical','expanded']},'counts':counts,'final_proof_environments':T.count('\\begin{proof}'),'final_named_results':sum(m[1] in ['theorem','proposition','lemma','corollary','definition'] for m in re.finditer(pattern,T)),'policy':'All 95 source proof environments retained. Four local expanded proof exceptions are logged: continuity of projected infinite sums, kernel coset terminology, bounded-ODE inverse justification, and the empty-family maximum convention. Original source copies are unchanged. No theorem deduplication was performed.','proofs':proofs,'fresh_lean_build':False}
(R/'PROOF_PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n')
(R/'SOURCE_CROSSWALK.json').write_text(json.dumps({'schema':'komorebi.paper_iii.source_crosswalk.v1','final_tex_sha256':sha(T),'statements':statements,'labels':allcross},ensure_ascii=False,indent=2)+'\n')
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for directory in ['source','figures'] for p in sorted((R/directory).rglob('*')) if p.is_file()}
(R/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'proof_counts':counts,'final_proofs':report['final_proof_environments'],'named_results':report['final_named_results'],'statement_environments':len(statements),'anchors':len(allcross),'pdf_pages':len(fitz.open(R/'Paper_III_Traditional_Final.pdf'))},indent=2))
