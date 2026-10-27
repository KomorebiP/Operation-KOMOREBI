#!/usr/bin/env python3
"""Validate and enumerate every statement/proof from both complete source branches."""
from pathlib import Path
import re,json,hashlib,difflib
import fitz
R=Path(__file__).resolve().parent
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
final=(R/'Paper_V_Traditional_Final.tex').read_text();aux=(R/'Paper_V_Traditional_Final.aux').read_text();d=fitz.open(R/'Paper_V_Traditional_Final.pdf')
changes=json.loads((R/'EDITORIAL_CHANGES.json').read_text());added=changes['invisible_locator_labels'];clean=final
for a in added:clean=clean.replace('\\label{'+a['label']+'}','')
# Canonical records lie in the final Arabic page-label region. Exclude the unnumbered cover's implicit label1.
regions=d.get_page_labels()
main_start=max(x['startpage'] for x in regions if x.get('style')=='D' and x.get('firstpagenum')==1)
page_labels={}
for i,page in enumerate(d,1):
 if i-1>=main_start:page_labels.setdefault(page.get_label(),[]).append(i)
labels={m[1]:{'number':m[2],'printed_page':m[3],'page':int(m[3]) if m[3].isdigit() else m[3],'physical_pdf_page':page_labels[m[3]][0] if len(page_labels.get(m[3],[]))==1 else None} for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',aux) if not m[1].endswith('@cref')}
pat=r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|standardfact|classical|conjecture|certificate)\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}'
pfpat=r'\\begin\{proof\}[\s\S]*?\\end\{proof\}'
rows=[];proofs=[];cross={};branches=[]
for part,key,rawfile,corrfile in [('I','core','formal_core.tex','core_corrected.tex'),('II','extension','annals_extension.tex','extension_corrected.tex')]:
 raw=(R/'source'/rawfile).read_text();corr=(R/corrfile).read_text()
 rawrecs=list(re.finditer(pat,raw));corrrecs=list(re.finditer(pat,corr));rawpfs=list(re.finditer(pfpat,raw));corrpfs=list(re.finditer(pfpat,corr));assert len(rawrecs)==len(corrrecs);assert len(rawpfs)==len(corrpfs)
 for i,(a,b) in enumerate(zip(rawrecs,corrrecs),1):
  assert b.group() in clean,(part,i,'statement absent')
  labs=re.findall(r'\\label\{([^}]+)\}',a.group());label=labs[0] if labs else f'{key}:record:{i:02}'
  loc=labels[label]
  item=dict(part=part,source_branch=key,ordinal=i,kind=a[1],title_tex=a[2],label=label,source_label=labs[0] if labs else None,original_number=loc['number'][1:] if part=='II' else loc['number'],manuscript_record=loc['number'],**loc,source_sha256=sha(a.group()),corrected_sha256=sha(b.group()),preservation='byte-identical' if a.group()==b.group() else 'documented-audit-repair',formal_scope='released-core-result' if part=='I' and a[1] in ['theorem','proposition','lemma','corollary'] else 'outside-20-result-Lean-contract')
  rows.append(item);cross[label]=dict(item,final_label=label)
 for i,(a,b) in enumerate(zip(rawpfs,corrpfs),1):
  assert b.group() in clean,(part,i,'proof absent')
  before=[(j,r) for j,r in enumerate(corrrecs,1) if r.end()<b.start()];j,r=before[-1]
  rec=next(x for x in rows if x['part']==part and x['ordinal']==j)
  proofs.append(dict(part=part,ordinal=i,label=rec['label'],number=rec['number'],source_sha256=sha(a.group()),corrected_sha256=sha(b.group()),preservation='byte-identical' if a.group()==b.group() else 'documented-audit-repair',page=rec['page'],physical_pdf_page=rec['physical_pdf_page']))
 for label in re.findall(r'\\label\{([^}]+)\}',raw):
  assert label in labels,label
  if label not in cross:cross[label]=dict(part=part,source_branch=key,source_label=label,final_label=label,**labels[label],kind='locator')
 branches.append(dict(part=part,raw_source_sha256=sha(raw),corrected_source_sha256=sha(corr),records=len(rawrecs),proofs=len(rawpfs),unchanged_records=sum(x['part']==part and x['preservation']=='byte-identical' for x in rows),unchanged_proofs=sum(x['part']==part and x['preservation']=='byte-identical' for x in proofs)))
 (R/f'{key}_changes.patch').write_text(''.join(difflib.unified_diff(raw.splitlines(True),corr.splitlines(True),fromfile='source/'+rawfile,tofile=corrfile)))
for a in added:
 if a['label'] not in cross:cross[a['label']]=dict(a,**labels[a['label']],final_label=a['label'])
# Human-readable section aliases support visual guide navigation.
for a in added:
 if a['type']=='section':
  loc=cross[a['label']]
  cross[f"section:{loc['number']}"]=dict(loc,alias_of=a['label'])
assert len(rows)==119 and len(proofs)==83
assert sum(x['part']=='I' and x['kind'] in ['theorem','proposition','lemma','corollary'] for x in rows)==20
assert sum(x['part']=='II' and x['kind'] in ['theorem','proposition','lemma','corollary'] for x in rows)==63
for name,value in [('canonical_label_to_final.json',cross),('manuscript_record_to_final.json',{r['manuscript_record']:r for r in rows}),('SOURCE_CROSSWALK.json',dict(statements=rows,labels=cross)),('PROOF_PRESERVATION.json',dict(schema='komorebi.paper_v.proof_preservation.v1',final_tex_sha256=sha(final),pdf_pages=len(d),branches=branches,statement_records=119,proof_environments=83,complete_preservation=True,proofs=proofs))]:
 (R/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'pdf_pages':len(d),'branches':branches,'labels_and_aliases':len(cross)},indent=2))
