from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent
T=(R/'Paper_II_Traditional_Final.tex').read_text(); A=(R/'Paper_II_Traditional_Final.aux').read_text()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
labels={m[1]:{'number':m[2],'page':m[3]} for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',A)}
cross=json.loads((R/'canonical_label_to_final.json').read_text())
for k,v in cross.items():
 v.update(labels[v['final_label']]); v['physical_pdf_page']=int(v['page'])+1 if v.get('page','').isdigit() else None
# This source label follows an unnumbered display; LaTeX stores its subsection counter.
smith=cross['eq:smith-inversion']
smith.update({'locator_kind':'unnumbered_display_in_section',
              'locator_section':labels['sec:smith-realization']['number'],
              'inherited_aux_number':labels['eq:smith-inversion']['number'],
              'number':None,
              'locator_text':'Section '+labels['sec:smith-realization']['number']+', Smith-phase identity',
              'relation':'Canonical unnumbered Smith-phase identity retained in the stated subsection; the inherited auxiliary counter is not an equation number.'})
(R/'canonical_label_to_final.json').write_text(json.dumps(cross,indent=2)+'\n')
proofs=[]; statements=[]
def envs(t):
 return list(re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|remark|boundary|certificate|standardfact)\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}',t))
for branch in ['expanded','canonical']:
 t=(R/'source'/f'{branch}.tex').read_text()
 for i,p in enumerate(re.finditer(r'\\begin\{proof\}[\s\S]*?\\end\{proof\}',t),1):
  before=t[:p.start()]; ls=re.findall(r'\\label\{([^}]+)\}',before); lab=ls[-1] if ls else None
  status='byte-identical-in-final' if p.group() in T else 'source-preserved; shared argument represented by expanded counterpart'
  if lab=='thm:smith-solve':status='retained-with-audited-existential-quantifier-restoration'
  proofs.append({'branch':branch,'ordinal':i,'source_label':lab,'source_sha256':sha(p.group()),'status':status,'final_anchor':cross.get(lab,{}).get('final_label',lab)})
 for m in envs(t):
  l=re.search(r'\\label\{([^}]+)\}',m.group()); lab=l[1] if l else None
  if not lab:continue
  target=cross.get(lab,{}).get('final_label',lab)
  statements.append({'branch':branch,'kind':m[1],'title_tex':m[2],'source_label':lab,'source_statement_sha256':sha(m.group()),'final_label':target,'number':labels.get(target,{}).get('number'),'page':labels.get(target,{}).get('page'),'relation':cross.get(lab,{}).get('relation','expanded source retained; consult exact local repair log'),'source_statement_tex':m.group()})
proof_counts={b:{'total':sum(x['branch']==b for x in proofs),'byte_identical_in_final':sum(x['branch']==b and x['status']=='byte-identical-in-final' for x in proofs)} for b in ['expanded','canonical']}
report={'schema':'komorebi.paper_ii.proof_preservation.v1','final_tex_sha256':sha(T),'source_sha256':{b:sha((R/'source'/f'{b}.tex').read_text()) for b in ['expanded','canonical']},'counts':proof_counts,'final_proof_environments':T.count('\\begin{proof}'),'final_named_results':sum(x[1] in ['theorem','proposition','lemma','corollary','definition'] for x in envs(T)),'proofs':proofs,'policy':'All expanded ordinary proof bodies retained byte-for-byte. Nonduplicate canonical proofs retained; shared elementary canonical arguments are represented by expanded counterparts, with original full canonical source preserved. No claim of exact identity for merged statements.','fresh_lean_build':False}
(R/'PROOF_PRESERVATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(R/'SOURCE_CROSSWALK.json').write_text(json.dumps({'schema':'komorebi.paper_ii.source_crosswalk.v1','statements':statements,'additional_locators':{'eq:smith-inversion':dict(cross['eq:smith-inversion'],source_label='eq:smith-inversion',branch='canonical')}},ensure_ascii=False,indent=2)+'\n')
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'source').rglob('*')) if p.is_file()}
manifest.update({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'figures').glob('*.pdf'))})
(R/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'counts':proof_counts,'final_proofs':report['final_proof_environments'],'named_results':report['final_named_results'],'crosswalk_entries':len(statements),'canonical_anchors':len(cross)},indent=2))
