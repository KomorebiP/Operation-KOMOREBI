#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,difflib
import fitz
R=Path(__file__).resolve().parent
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
final=(R/'Paper_VI_Traditional_Final.tex').read_text();aux=(R/'Paper_VI_Traditional_Final.aux').read_text();doc=fitz.open(R/'Paper_VI_Traditional_Final.pdf')
edits=json.loads((R/'EDITORIAL_CHANGES.json').read_text());anchors=edits['invisible_locator_labels']
labels={m[1]:dict(number=m[2],printed_page=m[3],page=m[3],physical_pdf_page=int(m[3])+1 if m[3].isdigit() else None,final_label=m[1]) for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',aux) if not m[1].endswith('@cref')}
record_pattern=r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|standardfact|classical|conjecture|certificate|construction)\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}'
pfpat=r'\\begin\{proof\}[\s\S]*?\\end\{proof\}'
# All labels are genuine final-PDF locators; aliases identify original records.
rows=[];proofs=[]
for m in re.finditer(record_pattern,final):
 all_labs=re.findall(r'\\label\{([^}]+)\}',m.group());label=all_labs[0];prefix=label.split(':')[0];part={'core':'I','extended':'II','earlier':'III','migration':'III'}[prefix]
 title=m[2];loc=labels[label]
 item=dict(part=part,source_branch=prefix,kind=m[1],title_tex=title,label=label,all_labels=all_labs,**loc,formal_scope='released-core-result' if prefix=='core' and m[1] in ['theorem','proposition','lemma','corollary'] else 'outside-33-result-contract',final_record_sha256=sha(m.group()))
 rows.append(item)
for i,m in enumerate(re.finditer(pfpat,final),1):
 before=[x for x in re.finditer(record_pattern,final[:m.start()])];rec=before[-1];lab=re.findall(r'\\label\{([^}]+)\}',rec.group())[0]
 proofs.append(dict(ordinal=i,label=lab,final_proof_sha256=sha(m.group()),**labels[lab]))
for x in rows:
 for lab in x['all_labels']:labels[lab].update({k:v for k,v in x.items() if k not in ['label','all_labels','final_label']})
for a in anchors:
 labels[a['label']].update(a)
 if a['type']=='section':labels['section:'+labels[a['label']]['number']]=dict(labels[a['label']],alias_of=a['label'])
# Compare whole branches, allowing only declared edits and locator transformations.
clean=final
for a in anchors:clean=clean.replace('\\label{'+a['label']+'}','')
clean=re.sub(r'(\\(?:label|ref|pageref|eqref|cref|Cref))\{([^}]+)\}',lambda m:m[1]+'{'+','.join(re.sub(r'^(core|extended|earlier|migration):','',x) for x in m[2].split(','))+'}',clean)
branches=[];preserved=[]
for prefix,rawname,corrname in [('core','formal_core.tex','core_corrected.tex'),('extended','strengthened.tex','extension_corrected.tex')]:
 raw=(R/'source'/rawname).read_text();corr=(R/corrname).read_text()
 a=list(re.finditer(record_pattern,raw));b=list(re.finditer(record_pattern,corr));ap=list(re.finditer(pfpat,raw));bp=list(re.finditer(pfpat,corr))
 assert len(a)==len(b);assert len(ap)==len(bp)
 for i,(x,y) in enumerate(zip(a,b),1):assert y.group() in clean,(prefix,'missing record',i)
 for i,(x,y) in enumerate(zip(ap,bp),1):
  assert y.group() in clean,(prefix,'missing proof',i)
  preserved.append(dict(branch=prefix,ordinal=i,source_sha256=sha(x.group()),corrected_sha256=sha(y.group()),status='byte-identical' if x.group()==y.group() else 'documented-audit-repair'))
 branches.append(dict(branch=prefix,records=len(a),proof_environments=len(ap),raw_sha256=sha(raw),corrected_sha256=sha(corr),unchanged_records=sum(x.group()==y.group() for x,y in zip(a,b)),unchanged_proofs=sum(x.group()==y.group() for x,y in zip(ap,bp))))
 (R/(prefix+'_changes.patch')).write_text(''.join(difflib.unified_diff(raw.splitlines(True),corr.splitlines(True),fromfile='source/'+rawname,tofile=corrname)))
# Check selected earlier records one-for-one after the explicit cross-reference redirects.
old=(R/'source/earlier_annals.tex').read_text();corr=(R/'earlier_corrected.tex').read_text();dest=json.loads((R/'EARLIER_RESULT_DESTINATIONS.json').read_text())
selected=edits['selected_earlier_labels'];earlierproofs=0
for label in selected:
 source=next(m for m in re.finditer(record_pattern,old) if '\\label{'+label+'}' in m.group());corrected=next(m for m in re.finditer(record_pattern,corr) if '\\label{'+label+'}' in m.group())
 def redirect(t):
  return re.sub(r'(\\(?:ref|pageref|eqref|cref|Cref))\{([^}]+)\}',lambda m:m[1]+'{'+','.join(x if x in selected else re.sub(r'^(core|extended):','',dest[x]['final_label']) for x in m[2].split(','))+'}',t)
 assert redirect(corrected.group()) in clean,('earlier record',label)
 if source[1] in ['theorem','proposition','lemma','corollary']:
  def nextpf(s,m):return re.search(pfpat,s[m.end():]).group()
  a=nextpf(old,source);b=nextpf(corr,corrected);assert redirect(b) in clean,('earlier proof',label);earlierproofs+=1
  preserved.append(dict(branch='earlier',source_label=label,source_sha256=sha(a),corrected_sha256=sha(b),status='byte-identical-before-reference-remapping' if a==b else 'documented-audit-repair-and-reference-remapping'))
branches.append(dict(branch='earlier',records=len(selected),proof_environments=earlierproofs,selected_only=True))
assert earlierproofs==24
assert len(proofs)==140,len(proofs)
assert sum(x['source_branch']=='core' and x['kind'] in ['theorem','proposition','lemma','corollary'] for x in rows)==33
assert sum(x['source_branch']=='extended' and x['kind'] in ['theorem','proposition','lemma','corollary'] for x in rows)==84
# Attach final locations to the 63-result semantic coverage map.
for k,v in dest.items():v.update({k2:v2 for k2,v2 in labels[v['final_label']].items() if k2 in ['number','printed_page','physical_pdf_page']})
reconciliation=dict(schema='komorebi.paper_vi.edition_reconciliation.v1',edition_date='2026-10-05',parts=branches,earlier_annals_result_count=63,earlier_results_retained=24,earlier_results_mapped_elsewhere=39,earlier_results=dest,migration={x:labels['migration:'+x] for x in ['sec:operator_substitution','sf:holomorphic_calculus','prop:operator_reciprocal']},scope='Semantic mappings identify result scope, not identical prose or extra Lean certification.')
for name,value in [('canonical_label_to_final.json',labels),('manuscript_record_to_final.json',{x['number']:x for x in rows}),('SOURCE_CROSSWALK.json',dict(statements=rows,labels=labels)),('EDITION_RECONCILIATION.json',reconciliation),('PROOF_PRESERVATION.json',dict(pdf_pages=len(doc),statement_records=len(rows),proof_environments=len(proofs),core_complete=True,strengthened_complete=True,earlier_selected_records_complete=True,branches=branches,preserved_proofs=preserved,final_proofs=proofs,final_tex_sha256=sha(final)) )]:
 (R/name).write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps(dict(pdf_pages=len(doc),statement_records=len(rows),proof_environments=len(proofs),branches=branches),indent=2))
