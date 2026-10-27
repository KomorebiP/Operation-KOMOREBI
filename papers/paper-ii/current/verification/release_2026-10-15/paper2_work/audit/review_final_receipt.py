from pathlib import Path
import collections,datetime,hashlib,json,re
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'paper2_work/final_audit_03';AUDIT=ROOT/'paper2_work/tools/final_audit';FORMAL=ROOT/'release_package/Komorebi_Paper_II_Release_2026-10-15/formal/current';REL=FORMAL.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
vp=RUN/'verification.json';mp=ROOT/'paper2_work/audit/final_correspondence.json';vb=vp.read_bytes();mb=mp.read_bytes();vs=hashlib.sha256(vb).hexdigest();ms=hashlib.sha256(mb).hexdigest()
assert vs=='4f7c6203b0a6c36693aaf0b0c32c826ff5eae08417645df040e45e5efdff9e10';assert ms=='c826d23bfe0b3c50ec6e498b035fa21b08df1f9a9b025e6f941c04d6a669c801'
mapap=ROOT/'paper2_work/audit/final_correspondence_mapA.json';assert sha(mapap)=='458f2b270297e648c42fb1b698aab029622cdbfa07bbfa7d80ce696d127517af';mapa=load(mapap)
v=json.loads(vb);m=json.loads(mb)
assert m['kernel_binding']==mapa['kernel_binding'] and m['semantic_acceptance_binding']==mapa['semantic_acceptance_binding']
assert len(m['records'])==len(mapa['records'])
for x,y in zip(m['records'],mapa['records']):
 assert x['record_id']==y['record_id'] and x['current_source']['statement_sha256']==y['current_source']['statement_sha256'] and x['current_source']['proof_sha256']==y['current_source']['proof_sha256'] and x['kernel_evidence']==y['kernel_evidence']
checks={c['label']:c for c in v['checks']}
assert v['status']=='PASS' and v['mode']=='fresh-complete-closure'
assert len(checks)==len(v['checks'])
for c in v['checks']:
 p=RUN/c['log'];assert sha(p)==c['log_sha256'],c['label'];assert c['passed'],c['label']
 assert (c['exit']==0 if c['expected']=='zero' else 0<c['exit']<124),c['label']
 if c['required_pattern']:assert re.search(c['required_pattern'],p.read_text(),re.I),c['label']
negative={c['label'] for c in v['checks'] if c['expected']=='nonzero'}
assert negative=={'guard_InjectedAxiom','guard_InjectedPlaceholder','guard_InjectedOpaque','guard_InjectedUnsafe','negative_false_equality','negative_placeholder','negative_missing_positive','kernel_corrupt_control','kernel_duplicate_body_corrupt_control'} and v['negative_controls']==9
for row in v['audit_inputs']:
 assert sha(AUDIT/row['path'])==row['sha256'],row['path'];assert sha(RUN/'execution_inputs/audit'/row['path'])==row['sha256'],row['path']
for name,digest in v['source_configuration'].items():assert sha(FORMAL/name)==digest and sha(RUN/'execution_inputs/source_configuration'/name)==digest
manifest=load(RUN/'execution_inputs/release_modules.json');assert sha(RUN/'execution_inputs/release_modules.json')==v['manifest_sha256']==m['kernel_binding']['frozen_manifest_sha256'];assert len(manifest)==62
src={r['module']:r for r in v['source_files']};assert len(src)==62==v['production_module_count']
for row in manifest:
 r=src[row['module']];assert all(r[k]==value for k,value in row.items());assert r['origin']=='fresh_compile'
 assert sha(FORMAL/r['source'])==r['source_sha256']==sha(RUN/'source_snapshots'/r['source'])
 assert sha(RUN/r['object'])==r['object_sha256']
 assert checks['compile_'+r['module'].replace('.','_')]['passed']
def rows(label,prefix):return [json.loads(x[len(prefix):]) for x in (RUN/checks[label]['log']).read_text().splitlines() if x.startswith(prefix)]
def same_inventory(actual,recorded):
 assert len(actual)==len(recorded);assert sorted(actual,key=lambda r:r['name'])==sorted(recorded,key=lambda r:r['name'])
 assert len({r['name'] for r in actual})==len(actual)
owned=load(RUN/'owned_declarations.json');same_inventory(rows('owned_audit','OWNED '),owned)
replayed=load(RUN/'replayed_constants.json');same_inventory(rows('replay_whole_closure','REPLAY_CHECKED '),replayed)
o={r['name']:r for r in owned};logical={n:r for n,r in o.items() if not r['runtime_only']};rp={r['name']:r for r in replayed}
assert len(o)==1952==v['owned_total'];assert len(logical)==1944==v['owned_logical_total']==v['logical_checked_count'];assert set(logical)==set(rp)
assert all(r['module']==rp[n]['module'] for n,r in logical.items());assert all(set(r['axioms'])<={'propext','Classical.choice','Quot.sound'} for r in owned)
helpers={n:r for n,r in o.items() if r['runtime_only']};assert len(helpers)==8==v['owned_runtime_only']
hr=load(AUDIT/'reviewed_runtime_helpers.json');assert hr['status']=='REVIEWED' and sha(AUDIT/'reviewed_runtime_helpers.json')==v['reviewed_runtime_helpers_sha256'];assert {r['name'] for r in hr['helpers']}==set(helpers)
helper_inv=load(RUN/'generated_runtime_helper_inventory.json');same_inventory(rows('helper_inventory','HELPER_REVIEW '),helper_inv)
assert 'HELPER_DEPENDENCY_SEPARATION_PASS OWNED 1952 HELPERS 8 REFERENCES 0' in (RUN/'helper_inventory.log').read_text()
for r in hr['helpers']:
 for k in ['module','type_expr','value_expr','level_params','axioms']:assert r[k]==helpers[r['name']][k]
 inv=next(x for x in helper_inv if x['name']==r['name']);assert all(r[k]==value for k,value in inv.items());assert not inv['unsafe'] and not inv['parent_partial'] and not inv['parent_unsafe']
 for key in ['type_expr','value_expr','parent_type_expr','parent_value_expr']:assert hashlib.sha256(r[key].encode()).hexdigest()==r[key+'_sha256']
runtime=rows('replay_whole_closure','REPLAY_RUNTIME_ONLY ');assert {r['name'] for r in runtime}==set(helpers) and len(runtime)==8 and all(r['partial'] and not r['unsafe'] for r in runtime)
dup=load(RUN/'upstream_duplicate_body_rechecks.json');same_inventory(rows('replay_whole_closure','REPLAY_UPSTREAM_DUPLICATE_RECHECKED '),dup);assert len(dup)==1
ud=dup[0];assert ud['name']=='Submodule.factor.eq_1' and ud['name'] not in o and ud['fresh_kernel_body_check'];assert ud['audit_name']=='Submodule.factor.eq_1._paperIIReplayBody' and ud['audit_name'] not in o
assert ud['serialized_in']=='KomorebiVerification.PaperII.ReleaseGluing' and ud['upstream_owner']=='Mathlib.RingTheory.AdicCompletion.Basic'
ur=load(AUDIT/'reviewed_upstream_duplicates.json');assert ur['status']=='REVIEWED' and sha(AUDIT/'reviewed_upstream_duplicates.json')==v['reviewed_upstream_duplicates_sha256'];assert len(ur['theorems'])==1
for k in ['name','serialized_in','upstream_owner','type_expr','value_expr','level_params','all']:assert ud[k]==ur['theorems'][0][k]
for k in ['type_expr','value_expr']:assert hashlib.sha256(ud[k].encode()).hexdigest()==ur['theorems'][0][k+'_sha256']
text=(RUN/'replay_whole_closure.log').read_text();assert re.search(r'REPLAY_CLOSURE_PASS MODULES 62 CONSTANTS 1944 NEW_NAME_REPLAYS 1944 DUPLICATE_BODY_RECHECKS 1',text);assert 'REPLAY_UPSTREAM_ONLY_PASS' in text
bad=(RUN/'kernel_duplicate_body_corrupt_control.log').read_text();assert 'REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED' in bad and 'type mismatch' in bad;assert 'REPLAY_UPSTREAM_DUPLICATE_RECHECKED' not in bad and 'REPLAY_CLOSURE_PASS' not in bad
kb=m['kernel_binding'];assert kb['verification_sha256']==vs and kb['owned_inventory_sha256']==sha(RUN/'owned_declarations.json') and kb['replay_inventory_sha256']==sha(RUN/'replayed_constants.json')
ap=Path(m['semantic_acceptance_binding']['path']);a=load(ap);assert sha(ap)==m['semantic_acceptance_binding']['sha256'];assert a['frozen_manifest_sha256']==v['manifest_sha256'];approved={r['record_id']:r for r in a['records']}
assert len(m['records'])==81 and sum(r['proof_level'] for r in m['records'])==53
names=set();statuses=collections.Counter()
for r in m['records']:
 ts=r['historical_targets_located_in_current_source']+[x for e in r['current_evidence'] for x in e['declarations']];rn=set()
 for t in ts:
  n=t['name'];rn.add(n);names.add(n);assert n in logical and n in rp and t['module']==logical[n]['module']==rp[n]['module'];assert t['source_sha256']==src[t['module']]['source_sha256']
 assert r['kernel_evidence']['mapped_names']==sorted(rn) and r['kernel_evidence']['receipt_sha256']==vs
 if r['proof_level']:
  ar=approved[r['record_id']];assert ar['statement_sha256']==r['current_source']['statement_sha256'] and ar['proof_sha256']==r['current_source']['proof_sha256'];assert ar['mapped_declaration_names']==sorted(rn)
  assert ar['semantic_status']==r['current_exact_semantic_acceptance'];statuses[r['status']]+=1
assert len(names)==348==kb['mapped_declaration_count'];assert {x['name'] for x in kb['mapped_declarations']}==names
assert statuses=={'kernel_checked_semantically_accepted_scope':51,'kernel_checked_partial_scope_open_bridge':2}
assert {r['record_id'] for r in m['records'] if r.get('status')=='kernel_checked_partial_scope_open_bridge'}=={'thm:holomorphic_defect','cor:exact_compatibility'}
# Re-extract current environments independently; accepted map B must bind full chapters.
ENV=re.compile(r'\\begin\{(definition|theorem|remark|corollary|proposition|example|standardfact|certificate)\}(?:\[[^\]]*\])?.*?\\end\{\1\}',re.S);PR=re.compile(r'\\begin\{proof\}(?:\[[^\]]*\])?.*?\\end\{proof\}',re.S)
chapter_drift=[]
for file,oldsha in m['current_chapter_sha256'].items():
 current=REL/file
 if sha(current)!=oldsha:chapter_drift.append(file)
 text=current.read_text();current_statements=[hashlib.sha256(x.group().encode()).hexdigest() for x in ENV.finditer(text)];mapped=[r['current_source']['statement_sha256'] for r in m['records'] if r['current_source']['file']==file];assert current_statements==mapped,file
 current_proofs=[hashlib.sha256(x.group().encode()).hexdigest() for x in PR.finditer(text)];mapped_proofs=[r['sha256'] for r in m['explicit_proof_bodies'] if r['file']==file];assert current_proofs==mapped_proofs,file
assert not chapter_drift,chapter_drift
assert vp.read_bytes()==vb and mp.read_bytes()==mb
report={'schema':'paper-ii-independent-final-receipt-review/1','status':'PASS','reviewer':'paper2_runtime','review_kind':'Read-only artifact consistency validation independent of receipt summary fields; reviewer authored audit infrastructure, so this is not a separate kernel implementation or independent source-author audit.','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipt':{'path':str(vp.relative_to(ROOT)),'sha256':vs},'accepted_map_B':{'path':str(mp.relative_to(ROOT)),'sha256':ms},'archived_map_A':{'path':str(mapap.relative_to(ROOT)),'sha256':sha(mapap)},'map_transition':'Map A to B preserves exact statement/proof hashes, mapped endpoints, semantic approval and kernel bindings.','counts':{'fresh_modules':62,'owned':1952,'owned_logical_replayed':1944,'reviewed_runtime_helpers':8,'exact_upstream_duplicate_fresh_body_checks':1,'negative_controls':9,'mapped_owned_replayed_declarations':348,'manuscript_records':81,'complete_proof_scopes':51,'partial_analytic_scopes':2},'checks':{'all_receipt_log_hashes':True,'all_execution_audit_input_snapshot_hashes':True,'source_configuration_and_frozen_manifest':True,'all_current_source_snapshot_and_object_hashes':True,'owned_and_replay_inventories_equal_authenticated_logs':True,'owned_logical_name_sets_exactly_equal_1944':True,'standard_axioms_only':True,'eight_exact_runtime_helper_and_parent_expressions':True,'zero_logical_references_to_runtime_helpers':True,'one_exact_upstream_type_body_owner_identity':True,'fresh_duplicate_kernel_body_check_and_invalid_body_rejection':True,'all348mapped_names_owner_source_and_replay_binding':True,'root_semantic_statement_proof_endpoint_identity':True,'all81current_raw_statement_and50proof_hashes_match_mapB':True,'all_current_chapter_hashes_match_mapB':True,'map_A_to_B_preserves_exact_mathematical_bindings':True},'current_chapter_files_changed_since_map_B':chapter_drift,'publication_followup':'Map B binds the current full chapter hashes after narrative/layout synchronization; any later change requires another exact hash refresh.','limits':['Pinned Lean kernel and upstream cache remain trusted.','General canonical rectifiable HFC and its exact-compatibility scope remain partial.','This review does not promote a claim that the whole manuscript is formalized.'],'validator':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(__file__)}}
out=ROOT/'paper2_work/audit/final_receipt_independent_review.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'review':str(out.relative_to(ROOT)),'sha256':sha(out),'status':'PASS','logs_checked':len(v['checks']),'audit_inputs_checked':len(v['audit_inputs']),'chapter_narrative_drift':chapter_drift},indent=2))
