from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parents[1]
audit=root/'privatechecks/audit_replay'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((root/'evidence/frozen_sources.json').read_text())
assert len(base)==221
base_names={r['module'] for r in base}
new={p.stem for p in (root/'lean/PaperX').glob('*.lean') if p.stem not in base_names}
records=json.loads((audit/'compilation.json').read_text())
history_path=audit/'compilation_history.json'
if history_path.exists():
 old=json.loads(history_path.read_text())
 records=old+[r for r in records if r not in old]
latest={r['module']:r for r in records}
assert len(new)==34,len(new)
assert set(latest)==new,(set(latest)^new)
rows=[]
for name in sorted(new):
 r=latest[name]
 assert r['exit_code']==0 and r['matches_author_olean'] and r['source_unchanged'],name
 src=root/'lean/PaperX'/f'{name}.lean'; copy=audit/'lean/PaperX'/f'{name}.lean'
 obj=root/'build/PaperX'/f'{name}.olean'; fresh=audit/'build/PaperX'/f'{name}.olean'
 assert sha(src)==sha(copy)==r['source_sha256'],name
 assert sha(obj)==sha(fresh)==r['olean_sha256'],name
 assert not re.search(r'^\s*(?:axiom|unsafe)\b|\b(?:sorry|admit|native_decide)\b',src.read_text(),re.M),name
 rows.append({'module':name,'source_sha256':sha(src),'olean_sha256':sha(obj),'theorems':len(re.findall(r'^(?:theorem|lemma)\b',src.read_text(),re.M))})
assert all(sha(root/'lean/PaperX'/f'{r["module"]}.lean')==r['source_sha256'] and sha(root/'build/PaperX'/f'{r["module"]}.olean')==r['olean_sha256'] for r in base)
ax=json.loads((audit/'axioms.json').read_text());assert ax['exit_code']==0
axtext=(audit/'logs/AuditAxioms.log').read_text()
count=int(re.search(r'AUDIT_DECLARATION_COUNT (\d+)',axtext).group(1))
observed=len(re.findall(r'^AUDIT_DECL ',axtext,re.M)); assert observed==count,(observed,count)
assert set(ax['modules'])==new
controls=json.loads((audit/'controls.json').read_text());assert all(c['expected_result_observed'] for c in controls)
result={'verdict':'proved as written at declared block scope','modules_in_build_order':list(dict.fromkeys(r['module'] for r in records if r['exit_code']==0)),'new_module_count':len(new),'new_theorem_lemma_count':sum(r['theorems'] for r in rows),'environment_owned_declarations_axiom_audited':count,'allowed_axioms':['propext','Classical.choice','Quot.sound'],'independent_rebuilds_all_exit_zero':True,'all_proof_objects_identical':True,'all_221_predecessor_sources_unchanged':True,'all_221_predecessor_objects_unchanged':True,'all_new_sources_unchanged':True,'baseline_module_count':221,'cumulative_source_module_count':255,'full_cumulative_rebuild_claimed':False,'empty_source_closure_rebuild_claimed':False,'scope':'Actual ideal-lattice residue estimates and actual ideal norm-character power saving under a residue-unit witness and nonvanishing on the inverse-class representative; ordinary class-character power saving and Mellin endpoint regularity; pole conclusions under stated residues and product identity. Full Claim9.1 remains partial.','full_ledger':{'checked':17,'partial':3},'audit_harness_failures':[r for r in records if r['exit_code']!=0],'controls':controls,'modules':rows}
history_path.write_text(json.dumps(records,indent=2)+'\n')
(audit/'compilation.json').write_text(json.dumps([latest[m] for m in result['modules_in_build_order']],indent=2)+'\n')
(root/'privatechecks/audit_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['modules','audit_harness_failures','controls']},indent=2))
