#!/usr/bin/env python3
"""Postflight source/statement/owned-kernel binding; never changes formal source or audit driver."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
REL=ROOT/'release_package/Komorebi_Paper_II_Release_2026-10-15'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def targets(r):
 return r['historical_targets_located_in_current_source']+[x for e in r['current_evidence'] for x in e['declarations']]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--working',type=Path,default=ROOT/'paper2_work/audit/current_correspondence.json')
 p.add_argument('--semantic-acceptance',type=Path,default=ROOT/'paper2_work/audit/current_semantic_acceptance.json')
 p.add_argument('--verification',type=Path,required=True)
 p.add_argument('--output',type=Path,default=ROOT/'paper2_work/audit/final_correspondence.json')
 args=p.parse_args();working=args.working.resolve();approval=args.semantic_acceptance.resolve();vp=args.verification.resolve();out=args.output.resolve()
 if out==working:raise ValueError('Keep working and final correspondence files separate')
 d=read(working);accept=read(approval);v=read(vp);audit=vp.parent
 if d['status']!='WORKING_NOT_RELEASE_ACCEPTED':raise ValueError('Expected raw refreshed working map')
 if v.get('status')!='PASS' or v.get('mode')!='fresh-complete-closure':raise ValueError('Final fresh whole-source PASS receipt required')
 if v.get('negative_controls')!=9 or not v.get('replay_exact_name_match') or not v.get('replay_starting_environment_excludes_project_modules'):raise ValueError('Required kernel closure/control gates absent')
 if v.get('upstream_duplicate_body_recheck_count')!=1 or v.get('upstream_duplicate_body_recheck_names')!=['Submodule.factor.eq_1']:raise ValueError('Reviewed upstream duplicate body check absent')
 if v['manifest_sha256']!=accept['frozen_manifest_sha256'] or v['manifest_sha256']!=d['frozen_formal_binding']['manifest_sha256']:raise ValueError('Frozen formal identity differs from accepted map')
 frozen=audit/'execution_inputs/release_modules.json'
 if sha(frozen)!=v['manifest_sha256']:raise ValueError('Recorded frozen manifest drift')
 by_source={r['module']:r for r in v['source_files']}
 if len(by_source)!=v['production_module_count'] or len(by_source)!=len(read(frozen)):raise ValueError('Incomplete fresh source inventory')
 for r in v['source_files']:
  if sha(REL/'formal/current'/r['source'])!=r['source_sha256']:raise ValueError('Production source changed: '+r['module'])
  if sha(audit/'source_snapshots'/r['source'])!=r['source_sha256']:raise ValueError('Source snapshot changed: '+r['module'])
  if r.get('origin')!='fresh_compile':raise ValueError('Non-fresh source provenance')
 checks={c['label']:c for c in v['checks']}
 if any(not c['passed'] for c in v['checks']):raise ValueError('Failed audit check in PASS receipt')
 def rows_from_log(label,prefix,path):
  c=checks[label];log=audit/c['log']
  if sha(log)!=c['log_sha256']:raise ValueError('Audit log drift: '+label)
  rows=[json.loads(line[len(prefix):]) for line in log.read_text().splitlines() if line.startswith(prefix)]
  material=read(path)
  if sorted(rows,key=lambda r:r['name'])!=sorted(material,key=lambda r:r['name']):raise ValueError('Inventory differs from authenticated log: '+label)
  if len({r['name'] for r in material})!=len(material):raise ValueError('Duplicate inventory name')
  return {r['name']:r for r in material}
 owned_path=audit/'owned_declarations.json';replayed_path=audit/'replayed_constants.json'
 owned=rows_from_log('owned_audit','OWNED ',owned_path)
 replayed=rows_from_log('replay_whole_closure','REPLAY_CHECKED ',replayed_path)
 logical={n:r for n,r in owned.items() if not r['runtime_only']}
 if set(logical)!=set(replayed) or len(owned)!=v['owned_total'] or len(logical)!=v['logical_checked_count']:raise ValueError('Whole logical inventory/replay mismatch')
 allowed={'propext','Classical.choice','Quot.sound'}
 if any(not set(r['axioms'])<=allowed for r in owned.values()):raise ValueError('Nonstandard axiom in owned inventory')
 for name,row in logical.items():
  if row['module']!=replayed[name]['module']:raise ValueError('Owner/replay module mismatch: '+name)
 for file,digest in d['current_chapter_sha256'].items():
  if sha(REL/file)!=digest:raise ValueError('Manuscript changed: refresh working map before acceptance')
 for row in accept['review_inputs'].values():
  if sha(ROOT/row['path'])!=row['sha256']:raise ValueError('Root semantic review changed: '+row['path'])
 if sha(ROOT/accept['weighted_review']['path'])!=accept['weighted_review']['sha256']:raise ValueError('Weighted semantic review changed')
 accepted={r['record_id']:r for r in accept['records']}
 if len(accepted)!=53:raise ValueError('Semantic approval denominator mismatch')
 resolved={};complete=partial=0;result=copy.deepcopy(d)
 for r in result['records']:
  names=set()
  for target in targets(r):
   name=target['name'];names.add(name)
   if name not in logical or name not in replayed:raise ValueError('Mapped name absent from owned logical replay: '+name)
   own=logical[name]
   if own['module']!=target['module']:raise ValueError('Mapped name owner differs: '+name)
   if by_source[own['module']]['source_sha256']!=target['source_sha256']:raise ValueError('Mapped name source hash differs: '+name)
   resolved[name]={'name':name,'module':own['module'],'kind':own['kind'],'source_sha256':target['source_sha256'],'axioms':own['axioms'],'owned_logical':True,'kernel_replayed':True}
  r['kernel_evidence']={'status':'PASS' if names else 'NO_MAPPED_ENDPOINTS_FOR_SUPPORTING_RECORD','mapped_names':sorted(names),'receipt_sha256':sha(vp)}
  if not r['proof_level']:continue
  a=accepted[r['record_id']]
  if a['statement_sha256']!=r['current_source']['statement_sha256'] or a['proof_sha256']!=r['current_source']['proof_sha256']:raise ValueError('Exact statement/proof differs from root semantic approval: '+r['record_id'])
  if a['mapped_declaration_names']!=sorted(names):raise ValueError('Mapped endpoints differ from root approval: '+r['record_id'])
  r['current_exact_semantic_acceptance']=a['semantic_status']
  r['aggregate_replay']='PASS'
  if a['semantic_status']=='ACCEPTED_COMPLETE_SCOPE':
   complete+=1;r['status']='kernel_checked_semantically_accepted_scope'
  elif a['semantic_status']=='ACKNOWLEDGED_PARTIAL_SCOPE':
   partial+=1;r['status']='kernel_checked_partial_scope_open_bridge'
  else:raise ValueError('Unknown semantic status')
 if (complete,partial)!=(51,2):raise ValueError('Unexpected final scope counts')
 result.update(status='FINAL_SCOPED_CORRESPONDENCE_WITH_TWO_ANALYTIC_GAPS',accepted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),final_proof_counts={'kernel_checked_semantically_accepted_scope':complete,'kernel_checked_partial_scope_open_bridge':partial})
 result['scope']='All81 manuscript records retained; of53 proof-level records,51 exact current statement scopes have accepted semantic correspondence to owned kernel-replayed constructions.2 general analytic scopes remain explicitly partial. This does not claim full Lean formalization of the entire manuscript.'
 result['release_gates']={'exact_source_aggregate_compile':'PASS','owned_kernel_type_body_replay':'PASS','standard_axiom_and_runtime_helper_closure':'PASS','current_manuscript_semantic_acceptance':'51_COMPLETE_SCOPES_ACCEPTED; 2_ANALYTIC_SCOPES_PARTIAL'}
 result['kernel_binding']={'verification':str(vp),'verification_sha256':sha(vp),'owned_inventory':str(owned_path),'owned_inventory_sha256':sha(owned_path),'replay_inventory':str(replayed_path),'replay_inventory_sha256':sha(replayed_path),'frozen_manifest_sha256':v['manifest_sha256'],'production_module_count':v['production_module_count'],'owned_total':v['owned_total'],'logical_checked_count':v['logical_checked_count'],'mapped_declaration_count':len(resolved),'mapped_declarations':[resolved[n] for n in sorted(resolved)],'all_mapped_names_are_local_owned_logical_and_replayed':True,'upstream_only_citations_exempted':[]}
 result['semantic_acceptance_binding']={'path':str(approval),'sha256':sha(approval),'complete_scopes':complete,'partial_scopes':partial}
 result['postflight']={'script':str(Path(__file__).resolve()),'script_sha256':sha(__file__),'working_map':str(working),'working_map_sha256':sha(working)}
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':'SCOPED_CORRESPONDENCE_ACCEPTED','output':str(out),'sha256':sha(out),'complete_scopes':complete,'partial_scopes':partial,'mapped_owned_and_replayed_names':len(resolved),'modules':v['production_module_count']},indent=2))
if __name__=='__main__':main()
