#!/usr/bin/env python3
"""Record source preservation and all final statement and section anchors."""
from pathlib import Path
import hashlib,json,re,difflib
import fitz
R=Path(__file__).resolve().parent
sha=lambda t:hashlib.sha256(t.encode()).hexdigest()
source=(R/'source/proofread.tex').read_text(); earlier=(R/'source/strengthened.tex').read_text(); final=(R/'Paper_IV_Traditional_Final.tex').read_text(); aux=(R/'Paper_IV_Traditional_Final.aux').read_text()
physical_by_label={page.get_label():i+1 for i,page in enumerate(fitz.open(R/'Paper_IV_Traditional_Final.pdf'))}
labels={m[1]:{'number':m[2],'printed_page':m[3],'page':m[3],'physical_pdf_page':physical_by_label.get(m[3])} for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',aux) if not m[1].endswith('@cref')}
pattern=r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|standardfact)\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}'
environments=list(re.finditer(pattern,source))
records=[];cross={}; proofs=[]
for label in re.findall(r'\\label\{([^}]+)\}',source):
 assert label in labels,label
 env=next((m for m in environments if '\\label{'+label+'}' in m.group()),None)
 item=dict(labels[label],final_label=label,source_label=label,source='Selected September 5 proofread manuscript',kind=env[1] if env else ('section' if label.startswith('sec:') else 'locator'))
 if env:item['title_tex']=env[2]
 cross[label]=item
for i,m in enumerate(environments,1):
 label=re.search(r'\\label\{([^}]+)\}',m.group())[1]
 assert m.group() in final,('statement changed',label)
 records.append({'ordinal':i,'manuscript_record':cross[label]['number'],'kind':m[1],'title_tex':m[2],'label':label,'statement_sha256':sha(m.group()),'preservation':'byte-identical',**cross[label]})
for i,m in enumerate(re.finditer(r'\\begin\{proof\}[\s\S]*?\\end\{proof\}',source),1):
 label=re.findall(r'\\label\{([^}]+)\}',source[:m.start()])[-1]
 assert m.group() in final,('proof changed',label)
 proofs.append({'ordinal':i,'source_label':label,'source_sha256':sha(m.group()),'status':'byte-identical-in-final','final_anchor':cross[label]})
assert len(records)==95 and len(proofs)==68
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'source').rglob('*')) if p.is_file()}
manifest['references.bib']=hashlib.sha256((R/'references.bib').read_bytes()).hexdigest()
(R/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'canonical_label_to_final.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n')
(R/'manuscript_record_to_final.json').write_text(json.dumps({x['manuscript_record']:x for x in records},ensure_ascii=False,indent=2)+'\n')
report={'schema':'komorebi.paper_iv.proof_preservation.v1','selected_source_sha256':sha(source),'final_tex_sha256':sha(final),'numbered_records':len(records),'proof_environments':len(proofs),'byte_identical_statements':len(records),'byte_identical_proofs':len(proofs),'theorem_like_results':sum(x['kind'] in ['theorem','proposition','lemma','corollary'] for x in records),'imported_standard_facts':sum(x['kind']=='standardfact' for x in records),'fresh_lean_build':False,'proofs':proofs}
(R/'PROOF_PRESERVATION.json').write_text(json.dumps(report,indent=2)+'\n')
(R/'SOURCE_CROSSWALK.json').write_text(json.dumps({'schema':'komorebi.paper_iv.source_crosswalk.v1','source_sha256':sha(source),'final_tex_sha256':sha(final),'statements':records,'labels':cross},ensure_ascii=False,indent=2)+'\n')
# Earlier strengthened edition: distinguish renaming from the deliberate scope migration.
aliases={'cor:fundamental_matrix_group_law':'cor:companion_addition_inversion','def:congruential_power':'def:residue_section_power','sec:congruential':'sec:residue_section','thm:congruential_semigroup':'thm:residue_section_parameter_addition','thm:reciprocal_semigroup':'thm:reciprocal_parameter_addition'}
migrated={'sec:operator_substitution','sf:holomorphic_calculus','prop:operator_reciprocal'}
earlier_labels=re.findall(r'\\label\{([^}]+)\}',earlier)
reconciliation=[]
for label in earlier_labels:
 if label in cross:
  reconciliation.append({'earlier_label':label,'status':'retained-in-later-manuscript','final':cross[label]})
 elif label in aliases:
  reconciliation.append({'earlier_label':label,'status':'renamed-in-later-manuscript','final':cross[aliases[label]],'reason':'The later manuscript uses residue-section and parameter-addition terminology; the mathematical topic is retained.'})
 elif label in migrated:
  reconciliation.append({'earlier_label':label,'status':'deliberately-outside-later-paper-iv-scope','final':None,'reason':'The later manuscript assigns bounded-operator functional calculus, semigroup and resolvent theory to Paper VI. The removed standard fact and proposition/proof remain in the unchanged earlier strengthened source. No Paper VI file was altered.'})
 else:raise ValueError(label)
prior_env=list(re.finditer(pattern,earlier))
reconcile={'schema':'komorebi.paper_iv.edition_reconciliation.v1','earlier_source_sha256':sha(earlier),'selected_source_sha256':sha(source),'earlier_numbered_records':len(prior_env),'selected_numbered_records':len(records),'earlier_proof_environments':earlier.count('\\begin{proof}'),'selected_proof_environments':len(proofs),'shared_labels':sum(x['status']=='retained-in-later-manuscript' for x in reconciliation),'renamed_labels':aliases,'deliberately_migrated_labels':sorted(migrated),'final_selection_reason':'The later proofread manuscript retains and corrects the cyclic analytic development, carries the completed v1.0.0 formal contract, and deliberately moves its one general functional-calculus proposition to Paper VI scope. Appending the redundant stronger edition would reintroduce corrected errors and confuse formal scope.','authorization':'Root approved latest scoped manuscript with historical source retention and explicit migration record; no historical appendix.','labels':reconciliation}
(R/'EDITION_RECONCILIATION.json').write_text(json.dumps(reconcile,ensure_ascii=False,indent=2)+'\n')
(R/'SOURCE_REVISION_DIFF.patch').write_text(''.join(difflib.unified_diff(earlier.splitlines(True),source.splitlines(True),fromfile='earlier-strengthened.tex',tofile='selected-proofread.tex')))
print(json.dumps({'pdf_pages':len(fitz.open(R/'Paper_IV_Traditional_Final.pdf')),'records':len(records),'proofs':len(proofs),'all_preserved_byte_identical':True,'labels':len(cross),'earlier_label_migration_counts':{s:sum(x['status']==s for x in reconciliation) for s in sorted(set(x['status'] for x in reconciliation))},'final_source_sha256':sha(final)},indent=2))
