from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[3];work=root/'release_work/runtime/overlap_review';formal=root/'release_package/Komorebi_Paper_I_Release_2026-10-15/formal';audit=root/'release_work/runtime/release_audit'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=json.loads((work/'candidate_checks.json').read_text());assert len(checks)==2 and all(x['passed'] for x in checks)
shutil.copy2(work/'ReplayClosureCandidate.lean',audit/'ReplayClosure.lean');shutil.copy2(work/'verify_release_candidate.py',audit/'verify_release.py')
evidence=audit/'upstream_duplicate_review';evidence.mkdir(exist_ok=True)
for name in ['InspectOverlaps.lean','overlap_diagnostic.json','candidate_checks.json','candidate_positive.log','candidate_corrupt_duplicate.log']:
 shutil.copy2(work/name,evidence/name)
receipt={'status':'REVIEWED','name':'ContinuousLinearMap.codRestrict.congr_simp','upstream_owner':'Mathlib.Analysis.LocallyConvex.HahnBanach','production_owners':[{'module':name,'source':str(Path(*name.split('.')).with_suffix('.lean')),'sha256':sha(formal/'current'/Path(*name.split('.')).with_suffix('.lean'))} for name in ['KomorebiVerification.TopologicalCompletion','PaperIRelease.GeneralNormedPackets']],'identity_fields':['name','type','levelParams','all','value'],'singleton_mutual_block':True,'self_reference':False,'strategy':'Submit exact type and proof body to public Kernel.Environment.addDeclCore under fresh audit-only theorem name; record this separately from official new-name replay. Original upstream constant remains present; no environment deletion or private reconstruction.','audit_name':'ContinuousLinearMap.codRestrict.congr_simp._paperIReplayBody','negative_control':'Change only audit theorem proof body to Nat literal 0 after exact identity gate; require kernel type mismatch and absent success markers.','candidate_source_sha256':sha(audit/'ReplayClosure.lean'),'reviewed_evidence':[{'path':str(p.relative_to(audit)),'sha256':sha(p)} for p in sorted(evidence.iterdir())]}
(audit/'reviewed_upstream_duplicate.json').write_text(json.dumps(receipt,indent=2)+'\n')
for p in audit.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:
  dst=formal/'scripts/release_audit'/p.relative_to(audit);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
print(json.dumps({'ReplayClosure.lean':sha(audit/'ReplayClosure.lean'),'verify_release.py':sha(audit/'verify_release.py'),'reviewed_upstream_duplicate.json':sha(audit/'reviewed_upstream_duplicate.json')},indent=2))
