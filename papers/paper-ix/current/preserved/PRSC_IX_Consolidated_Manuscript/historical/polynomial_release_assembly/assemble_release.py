from pathlib import Path
from collections import Counter
import hashlib,json,shutil,zipfile
r=Path('/workspace/scratch/196a43c5b4f3');p=r/'polynomial_lifting'
s=r/'release_staging/PRSC_IX_Complete_Polynomial_Lifting'
sha=lambda b:hashlib.sha256(b).hexdigest()
# Copy only source, review and log material, never compiled artifacts or symlinks.
def copy(src,dst):
 assert src.is_file() and not src.is_symlink(),src
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for group in ('formalization','scripts','contracts'):
 for src in (p/group).iterdir():
  if src.is_file() and src.suffix in ('.lean','.py'):
   copy(src,s/'polynomial_lifting'/group/src.name)
for src in (p/'controls').glob('*.lean'):copy(src,s/'polynomial_lifting/controls'/src.name)
for name in ('inventory.json','POLYNOMIAL_LIFTING.md','INDEPENDENT_PROOF_AUDIT.md'):
 copy(p/name,s/'polynomial_lifting'/name)
for src in (p/'replay_01').iterdir():
 if src.is_file():copy(src,s/'polynomial_lifting/verification'/src.name)
for group in ('taylor','obstruction','representative'):
 for src in (p/group).rglob('*'):
  if 'build' in src.parts or not src.is_file() or src.is_symlink():continue
  if src.suffix in ('.lean','.md','.log','.json'):
   copy(src,s/'polynomial_lifting/development'/src.relative_to(p))
for src in (p/'controls/development').iterdir():
 if src.is_file() and src.suffix in ('.log','.md'):
  copy(src,s/'polynomial_lifting/development/controls'/src.name)
# Retain archive assembly notes for reproducible provenance, separate from replay scripts.
for name in ('assemble_release.py','update_release_docs.py'):
 copy(p/name,s/'historical/polynomial_release_assembly'/name)
report=json.loads((p/'replay_01/polynomial_verification.json').read_text())
assert report['status']=='PASS'
inv=json.loads((p/'inventory.json').read_text())
for e in inv['modules']+inv['contracts']+inv['negative_controls']:
 assert sha((s/'polynomial_lifting'/e['source']).read_bytes())==e['sha256']
for entry in report['runs']:
 assert sha((s/'polynomial_lifting/verification'/entry['log']).read_bytes())==entry['log_sha256']
counts=Counter(d['kind'] for m in inv['modules'] if m['module'].startswith('Polynomial') for d in m['declarations'])
audit={
 'release':s.name,'author':'Komorebi P.','date':'2026-09-08','status':'PASS',
 'new_claims':['Actual multivariable integral Taylor divisibility','Finite fixed-presentation one-step polynomial obstruction for all q>0,L>=1','Independence under changing integer representatives of the same lower residue','Finite shared-correction criterion for actual paired polynomial lifts'],
 'new_scope':{'polynomials':'Arbitrary finite lists in Z[X_1,...,X_d], including zero variables/equations','modulus':'Every positive natural q, including composite q and q=1','depth':'L>=1','jacobian':'Actual evaluated formal partial derivatives','obstruction':'(Z/qZ)^e / im(reduction composed with DF(x))','shared_quotient':'Z^d / (ker J_x + ker K_x)'},
 'new_block':{'modules':5,'explicit_declarations':sum(counts.values()),'declarations':dict(counts)},
 'fresh_polynomial_gate':{k:report[k] for k in ['module_count','statement_contracts','negative_controls','explicit_declaration_audits','declarations','seconds','warnings_as_errors','fresh_project_compilation','mathlib_rebuilt','allowed_axioms']},
 'gate_count':len(report['runs']),
 'report':'polynomial_lifting/verification/polynomial_verification.json',
 'report_sha256':sha((p/'replay_01/polynomial_verification.json').read_bytes()),
 'independent_audit':'polynomial_lifting/INDEPENDENT_PROOF_AUDIT.md',
 'independent_audit_sha256':sha((p/'INDEPENDENT_PROOF_AUDIT.md').read_bytes()),
 'runtime':report['runtime'],
 'preserved_prior_results':['Full stated Nishibuchi Conjecture3.9','Step amplification and uncapped N=4 all-row bounds','Optimal classical N=2 dyadic edge tower','Exact N=4 displacements and all packet periods','Unique continuous dyadic isometric bijections with exact original coefficient images','Finite affine obstruction and common-quotient universal property with affine pair lifts'],
 'prior_blocks_rerun_this_block':False,
 'historical_metadata_correction':{'file':'historical/isometry_release_root/RELEASE_AUDIT.json','field':'combined_continuation statement_contracts/negative_controls','historical_values':[1,13],'correct_values':[3,11],'source':'strengthening/verification/continuation_verification.json actual gate entries','total_gates_unchanged':38},
 'remaining':['Finite-field correction-digit torsor and exact rank counts in Lean','Specified tower transition maps and infinite lifting hypotheses','Unrestricted native13.2/13.3 definitions, presentation invariance and descent','Exact higher differences, other least periods, general Mahler-kernel and arbitrary-row tail valuations'],
 'not_claimed':['Presentation-independent canonical native obstruction theory','Automatic infinite lifts','Automatic shared lifts from individual lifts alone','External novelty or priority','A rewritten unified current manuscript'],
 'checklist':'REMAINING_CHECKLIST.md','archive_scope':'All known local Paper IX work covered by prior-state inventory plus newly verified polynomial block; recovered partial manuscripts remain partial; portable runtime and build caches excluded'
}
(s/'RELEASE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
# Independent source and manuscript coverage: include hashes inside preserved baseline too.
files=[x for x in s.rglob('*') if x.is_file()]
assert all(not x.is_symlink() for x in s.rglob('*'))
covered={sha(x.read_bytes()) for x in files}
base=s/'baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip'
with zipfile.ZipFile(base) as z:
 baseline_rows=[{'path':i.filename,'bytes':i.file_size,'sha256':sha(z.read(i))} for i in z.infolist() if not i.is_dir()]
covered.update(x['sha256'] for x in baseline_rows)
prior=[]
for archive in sorted((r/'output').glob('*.zip')):
 if archive.name==s.name+'.zip':continue
 with zipfile.ZipFile(archive) as z:
  rows=[i for i in z.infolist() if not i.is_dir()]
  missing=[i.filename for i in rows if sha(z.read(i)) not in covered]
  assert not missing,(archive,missing)
 prior.append({'archive':archive.name,'archive_sha256':sha(archive.read_bytes()),'files':len(rows),'all_uncompressed_file_hashes_covered':True})
assert len(prior)==7
completeness={'status':'PASS','scope':'Known local Paper IX files plus new polynomial block; not a census of remote files',
 'prior_archives':prior,'missing_prior_file_hashes':0,'restored_prior_files':38,
 'baseline_zip_sha256':sha(base.read_bytes()),'baseline_entry_inventory':baseline_rows,
 'manuscript_files_exposed':25,
 'excluded':['Separate portable Lean runtime','Reproducible compiled outputs and caches','Unrelated raw search results','Full third-party Nishibuchi paper (version/URL/hash record retained)','Duplicate cumulative ZIP containers'],
 'limitations':['Two older edge manuscripts available only as partial source windows','Annals TeX is a reconstructed textual copy','Historical main manuscript is not revised to include every continuation']}
(s/'PACKAGE_COMPLETENESS.json').write_text(json.dumps(completeness,indent=2)+'\n')
# Distributed file hashes, excluding only this self-referential manifest.
rows=[]
for x in sorted(s.rglob('*')):
 assert not x.is_symlink(),x
 if not x.is_file() or x==s/'MANIFEST.json':continue
 assert not any(part in ('build','__pycache__') for part in x.relative_to(s).parts),x
 assert not any(x.name.endswith(ext) for ext in ('.olean','.olean.server','.olean.private','.ir','.ir.sig','.pyc')),x
 rows.append({'path':str(x.relative_to(s)),'bytes':x.stat().st_size,'sha256':sha(x.read_bytes())})
(s/'MANIFEST.json').write_text(json.dumps({'release':s.name,'algorithm':'SHA-256','manifest_excludes_itself':True,'file_count_excluding_manifest':len(rows),'files':rows},indent=2)+'\n')
out=r/'output'/(s.name+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for x in sorted(s.rglob('*')):
  if x.is_file():z.write(x,str(Path(s.name)/x.relative_to(s)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.infolist())==len(rows)+1
 for row in rows:
  b=z.read(str(Path(s.name)/row['path']))
  assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
result={'status':'PASS','archive':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'files':len(rows)+1,'prior_archives_covered':len(prior),'zip_crc':'PASS','all_entry_hashes':'PASS'}
(r/'polynomial_lifting/ARCHIVE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
