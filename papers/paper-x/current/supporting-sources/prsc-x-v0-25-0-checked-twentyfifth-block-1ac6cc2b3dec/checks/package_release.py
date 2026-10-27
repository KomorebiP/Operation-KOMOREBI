"""Package the audited cumulative release; no network operations."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
PREFIX='PRSC_X_v0.25.0_Checked_TwentyFifth_Block'
PROOF_AUDIT='CLAIM91_PROOF_AUDIT.md'
PROOF_AUDIT_SOURCES='CLAIM91_PROOF_AUDIT_SOURCES.json'
BASELINE_VERIFICATION='predecessor_evidence/block24/verification.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def selected():
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(ROOT)
  if any(part in {'build_clean','probes','__pycache__','replay_build'} for part in rel.parts):continue
  if p.suffix=='.pyc':continue
  yield p

def archive(path):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in selected():z.write(p,PREFIX+'/'+p.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(path) as z:
  bad=z.testzip();assert bad is None,bad
 print(str(path),path.stat().st_size,flush=True)

def main():
 mode=sys.argv[1];output=Path(sys.argv[2]).resolve()
 v=json.loads((ROOT/'verification.json').read_text());assert v['status']=='passed' and v['module_count']==len(list((ROOT/'lean/PaperX').glob('*.lean')))
 prov=json.loads((ROOT/'provenance.json').read_text());new=set(prov['new_modules'])
 assert prov['release']==v['release']==PREFIX
 assert v['scope']==prov['theorem_scope'] and v['arithmetic_status']==prov['arithmetic_status']
 assert sha(ROOT/'references'/prov['baseline_archive']['filename'])==prov['baseline_archive']['sha256']
 assert v['module_count']==prov['predecessor_source_count']+len(new)
 reviewed=json.loads((ROOT/PROOF_AUDIT_SOURCES).read_text())
 assert {Path(entry['path']).stem for entry in reviewed['new_production_sources'] if entry.get('role','primary')=='primary'}==new
 for entry in reviewed['new_production_sources']:
  assert sha(ROOT/entry['path'])==entry['sha256']
 for section in ['internal_dependency_source_closure','reviewed_predecessor_definition_sources','evidence']:
  for entry in reviewed[section]:assert sha(ROOT/entry['path'])==entry['sha256']
 assert any(entry['path']==PROOF_AUDIT for entry in reviewed['evidence'])
 # Block 22 exact arithmetic evidence is retained as a predecessor regression.
 # Proof assembly in Block 25 does not claim a new bounded computation.
 for directory in ['local_quadratic_run','local_quadratic_review']:
  manifest=json.loads((ROOT/'checks'/directory/'manifest.json').read_text())
  assert manifest['run']['status']=='completed' and manifest['run']['exit_status']==0
  for entry in manifest['input_artifacts']:
   assert sha(ROOT/entry['path'])==entry['sha256']==entry['sha256_after']
  for entry in manifest['outputs']:assert sha(ROOT/entry['path'])==entry['sha256']
  assert (ROOT/'exact_local_quadratic.json').read_bytes()==(ROOT/'checks'/directory/'results.json').read_bytes()
 assert (ROOT/'EXACT_LOCAL_QUADRATIC_REVIEW.md').is_file()
 for filename in ['proofreading_structure.json','proofreading_patch.json']:
  proofread=json.loads((ROOT/filename).read_text())
  assert proofread['passed'] and sha(ROOT/proofread['source'])==proofread['source_sha256']
  if 'patch' in proofread:assert sha(ROOT/proofread['patch'])==proofread['patch_sha256']
 assert (ROOT/'PROOFREADING.md').is_file()
 for m in v['modules']:
  assert sha(ROOT/'lean/PaperX'/f"{m['module']}.lean")==m['source_sha256']
  assert sha(ROOT/'build_clean/PaperX'/f"{m['module']}.olean")==m['olean_sha256']
 old=json.loads((ROOT/BASELINE_VERIFICATION).read_text());assert old['status']=='passed'
 expected={m['module']:m for m in old['modules']}
 assert len(expected)==prov['predecessor_source_count']
 assert {m['module'] for m in v['modules'] if m['module'] not in new}==set(expected)
 assert all(m['source_sha256']==expected[m['module']]['source_sha256'] and m['olean_sha256']==expected[m['module']]['olean_sha256'] for m in v['modules'] if m['module'] not in new)
 if mode=='payload':
  if (ROOT/'build').exists():shutil.rmtree(ROOT/'build')
  shutil.copytree(ROOT/'build_clean',ROOT/'build')
  prov['predecessor_oleans_identical_after_fresh_build']=True
  prov['independently_reviewed_final_sources']=sorted(Path(e['path']).stem for e in reviewed['new_production_sources'] if e.get('review_mode')=='independent_exact_source')
  prov['final_source_review_mode']='Independent review of all eight exact final production sources and their source-claim scope.'
  prov['new_public_theorem_declarations']=v['new_theorem_declarations']
  (ROOT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
 elif mode=='final':
  replay=json.loads((ROOT/'archive_replay.json').read_text());assert replay['status']=='passed'
  assert {r['module'] for r in replay['runs']}==new
  hashes={m['module']:m for m in v['modules']}
  assert all(r['source_sha256']==hashes[r['module']]['source_sha256'] and r['olean_sha256']==hashes[r['module']]['olean_sha256'] for r in replay['runs'])
  assert replay['predecessor_objects_verified']==prov['predecessor_source_count']
  regression=replay['predecessor_regression']
  assert regression['status']=='passed' and regression['originating_block']==22
  assert regression['script_sha256']==sha(ROOT/'checks/exact_local_quadratic.py')
  assert regression['result_sha256']==sha(ROOT/'exact_local_quadratic.json')
  audit={'release':PREFIX,'status':'passed','scope':prov['theorem_scope'],'scope_boundary':'General Claim 9.1 remains partial: cofinite Frobenius coverage is proved for the fixed cyclotomic Galois group, while the general absolute-Galois case is still an input.','module_count':v['module_count'],'new_modules':sorted(new),'new_public_theorem_declarations':v['new_theorem_declarations'],'audited_public_declarations':v['audited_declarations'],'axioms':v['axioms'],'positive_controls':v['positive_controls'],'rejected_controls':v['rejected_controls'],'predecessor_sources_and_oleans_identical':True,'baseline_verification':BASELINE_VERIFICATION,'proof_audit':PROOF_AUDIT,'proof_review_mode':prov.get('final_source_review_mode'),'archive_replay':'archive_replay.json','predecessor_regression':{'originating_block':22,'independent_exact_review':'EXACT_LOCAL_QUADRATIC_REVIEW.md','script':'checks/exact_local_quadratic.py','script_sha256':regression['script_sha256'],'results':'exact_local_quadratic.json','result_sha256':regression['result_sha256'],'fresh_archive_replay':'passed'},'new_bounded_math_computation_claimed':False,'arithmetic_status':prov['arithmetic_status'],'status_counting_basis':prov['status_counting_basis'],'prior_arithmetic_application_target_resolved':prov['prior_arithmetic_application_target_resolved'],'arithmetic_promotions':prov.get('arithmetic_promotions',[]),'manuscript':'Amended LaTeX and patch; structural proofreading performed; no new PDF typeset.'}
  (ROOT/'PRSC_X_TwentyFifth_Block_Release_Audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 else:raise ValueError(mode)
 (ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in selected() if p.name!='SHA256SUMS'))
 archive(output)
 if mode=='final':
  with zipfile.ZipFile(output) as z:
   for m in v['modules']:
    assert hashlib.sha256(z.read(PREFIX+'/lean/PaperX/'+m['module']+'.lean')).hexdigest()==m['source_sha256']
    assert hashlib.sha256(z.read(PREFIX+'/build/PaperX/'+m['module']+'.olean')).hexdigest()==m['olean_sha256']
  print(json.dumps({'final_archive_sha256':sha(output),'all_delivered_sources_and_objects_match_replayed_payload':True}),flush=True)
if __name__=='__main__':main()
