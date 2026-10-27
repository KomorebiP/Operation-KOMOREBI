import json,hashlib,csv,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'checkpoint_v0.3.0' if (ROOT/'checkpoint_v0.3.0').exists() else ROOT.parent/'Paper_III_Continuation_v0.3.0'
OUT=Path(__file__).resolve().parents[1]/'metadata'
OUT.mkdir(parents=True,exist_ok=True)
cross=json.loads((BASE/'baseline/editable/traditional/SOURCE_CROSSWALK.json').read_text())
sec16=json.loads((BASE/'coverage/SECTION16_CORRESPONDENCE.json').read_text())
sec17=json.loads((BASE/'coverage/SECTION17_CORRESPONDENCE_v0.3.0.json').read_text())
sec16map={x['manuscript_label']:x for x in sec16['rows'] if x.get('manuscript_label')}
sec17map={x['label']:x for x in sec17['rows']}
result_kinds={'theorem','lemma','proposition','corollary','standardfact'}
rows=[]
for record in cross['statements']:
 label=record.get('source_label')
 env=record.get('source_statement_tex','')
 digest=hashlib.sha256(env.encode()).hexdigest()
 assert digest==record['source_statement_sha256']
 num=record.get('number')
 if not num or '.' not in str(num):section=None
 else:
  try:section=int(str(num).split('.')[0])
  except ValueError:section=None
 typ=record['kind'];branch=record['branch']
 if branch=='canonical':
  classification='FINITE_FORMAL_CONTRACT_HISTORICAL' if typ in result_kinds else 'CANONICAL_SOURCE_PRESERVED'
  provenance='baseline finite contract, 41 map rows; exact row pairing not newly kernel-replayed'
 elif label in sec16map:
  classification='ACCEPTED_SECTION16_RECORDED' if typ in result_kinds else 'SECTION16_DEFINITION_RECORDED'
  provenance='coverage/SECTION16_CORRESPONDENCE.json with source-exact accepted declaration names and types'
 elif label in sec17map:
  classification='ORDINARY_SECTION17_SUPPLEMENT_NOT_LEAN' if typ in result_kinds else 'SECTION17_DEFINITION_DRAFT_NOT_LEAN'
  provenance='new Section 17 proof supplement plus two uncompiled Lean candidates'
 elif typ=='standardfact':
  classification='EXTERNAL_STANDARD_FACT_NOT_NEW_LEAN_PROOF'
  provenance='expanded monograph classical input; no accepted Paper III formal map'
 elif typ in result_kinds:
  classification='EXPANDED_PROSE_PROOF_ONLY_NO_ACCEPTED_LEAN_MAP'
  provenance='expanded monograph ordinary mathematical argument; no current exact Lean target accepted'
 else:
  classification='EXPANDED_DEFINITION_EXAMPLE_OR_SCOPE'
  provenance='expanded monograph source; not an independently checked Lean theorem'
 targets=[]
 if label in sec16map:
  targets=[x['name'] for x in sec16map[label].get('targets',[]) if 'name' in x]
 row={'branch':branch,'source_ordinal':record['ordinal'],'kind':typ,'number':num,'title':record.get('title') or record.get('title_tex'),
 'label':label,'physical_pdf_page':record.get('physical_pdf_page'), 'source_statement_sha256':digest,
 'evidence_class':classification,'evidence_detail':provenance,'accepted_lean_targets':targets,
 'new_lean_kernel_replay_this_closeout':False,'source_branch_file':'baseline/editable/traditional/source/'+('canonical.tex' if branch=='canonical' else 'expanded.tex')}
 if label in sec17map:
  row['section17_original_status']=sec17map[label]['status']
  row['section17_2026_10_20_ordinary_proof']='release/docs/Paper_III_Section17_Analytic_Closeout.pdf'
 rows.append(row)
assert len(rows)==167
counts=collections.Counter(x['evidence_class'] for x in rows)
kindcounts=collections.Counter(x['kind'] for x in rows)
assert sum(x['kind'] in result_kinds for x in rows)==100
assert sum(x['kind']=='standardfact' for x in rows)==2
assert sum(x['branch']=='canonical' for x in rows)==66
assert sum(x['branch']=='expanded' for x in rows)==101
out={'schema':'komorebi.paper_iii.manuscript_statement_register/1','selected_manuscript_sha256':hashlib.sha256((BASE/'baseline/publication/pdfs/Paper_III_Traditional_Final.pdf').read_bytes()).hexdigest(),
 'total_environments':len(rows),'prooflike_statements_including_external_standard_facts':100,
 'non_standard_result_environments':98,'external_standard_fact_environments':2,'histogram':dict(counts),
 'kinds':dict(kindcounts),'status':'SOURCE_IDENTITY_VERIFIED__SEMANTIC_LEAN_SCOPE_NONUNIFORM','rows':rows,
 'do_not_claim':'A 100-item source census does not certify the October 16 report of 2,693 kernel-replayed declarations. Such a replay was not available for this release.'}
(OUT/'MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
with (OUT/'MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.csv').open('w',newline='') as f:
 fields=['branch','source_ordinal','kind','number','title','label','physical_pdf_page','source_statement_sha256','evidence_class','evidence_detail','accepted_lean_targets','new_lean_kernel_replay_this_closeout','source_branch_file'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rows:
  r2={k:r.get(k,'') for k in fields};r2['accepted_lean_targets']=';'.join(r2['accepted_lean_targets']);w.writerow(r2)
print(json.dumps({'counts':counts,'kinds':kindcounts,'total':len(rows)},indent=2))
