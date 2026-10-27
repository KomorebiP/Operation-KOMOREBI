from pathlib import Path
from collections import Counter
import hashlib,json,shutil,zipfile,ast
r=Path('/workspace/scratch/196a43c5b4f3');p=r/'polynomial_counts'
s=r/'release_staging/PRSC_IX_Complete_Lift_Counts'
sha=lambda b:hashlib.sha256(b).hexdigest()
def copy(src,dst):
 assert src.is_file() and not src.is_symlink(),src
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for group in ('formalization','scripts','contracts','controls','audit'):
 for src in (p/group).iterdir():
  if src.is_file() and src.suffix in ('.lean','.py','.json','.md'):
   copy(src,s/'polynomial_counts'/group/src.name)
for n in ('inventory.json','POLYNOMIAL_LIFT_COUNTS.md','INDEPENDENT_PROOF_AUDIT.md','DEVELOPMENT.md'):
 copy(p/n,s/'polynomial_counts'/n)
for src in (p/'replay_01').iterdir():
 if src.is_file():copy(src,s/'polynomial_counts/verification'/src.name)
for group in ('linear','digits','residues','cokernel','counts','controls_dev'):
 for src in (p/group).rglob('*'):
  if any(x in ('build','__pycache__') for x in src.relative_to(p).parts) or not src.is_file() or src.is_symlink():continue
  if src.suffix in ('.lean','.md','.log','.json'):
   copy(src,s/'polynomial_counts/development'/src.relative_to(p))
copy(p/'assemble_release.py',s/'historical/counts_release_assembly/assemble_release.py')
report=json.loads((p/'replay_01/polynomial_counts_verification.json').read_text())
rec=json.loads((p/'audit/RECONCILIATION.json').read_text())
assert report['status']==rec['status']=='PASS'
assert rec['report_sha256']==sha((p/'replay_01/polynomial_counts_verification.json').read_bytes())
inv=json.loads((p/'inventory.json').read_text())
for e in inv['modules']+inv['contracts']+inv['negative_controls']:
 assert sha((s/'polynomial_counts'/e['source']).read_bytes())==e['sha256']
for e in report['runs']:
 assert sha((s/'polynomial_counts/verification'/e['log']).read_bytes())==e['log_sha256']
prior={'AffineObstructionCore','PolynomialTaylor','PolynomialObstruction'}
counts=Counter(d['kind'] for m in inv['modules'] if m['module'] not in prior for d in m['declarations'])
audit={
 'release':s.name,'author':'Komorebi P.','date':'2026-09-08','status':'PASS',
 'new_claims':['Finite correction-digit fiber carries an explicit kernel AddTorsor structure when nonempty','Correction digits bijectively parametrize actual next-level residue classes','Actual polynomial lift count is zero if obstructed, p^(d-rank A) otherwise','Original obstruction group has cardinality p^(e-rank A)','Class-preserving equivalence between original integer-domain and finite-ring Jacobian cokernels'],
 'new_scope':{'polynomials':'Arbitrary finite lists in Z[X_1,...,X_d], including zero dimensions','torsor_modulus':'q>0; polynomial bridge L>=1','residue_parametrization':'q>0,L>=0','count_modulus':'prime p, polynomial depth L>=1','rank':'Dimension over ZMod p of the range of the actual evaluated formal Jacobian','counted_objects':'Distinct actual polynomial solution classes modulo p^(L+1) above the prescribed x modulo p^L','residual':'F(x)/p^L modulo p, derived from the actual lower polynomial congruences'},
 'new_modules':{'count':6,'explicit_declarations':sum(counts.values()),'declarations':dict(counts),'note':'Includes generic support and positive control theorems; these are not independent discoveries.'},
 'fresh_gate':{k:report[k] for k in ['module_count','statement_contracts','negative_controls','explicit_declaration_audits','declarations','seconds','warnings_as_errors','fresh_project_compilation','mathlib_rebuilt','allowed_axioms']},
 'gate_count':len(report['runs']),
 'report':'polynomial_counts/verification/polynomial_counts_verification.json',
 'report_sha256':sha((p/'replay_01/polynomial_counts_verification.json').read_bytes()),
 'independent_audit':'polynomial_counts/INDEPENDENT_PROOF_AUDIT.md',
 'independent_audit_sha256':sha((p/'INDEPENDENT_PROOF_AUDIT.md').read_bytes()),
 'independent_reconciliation':rec,'runtime':report['runtime'],
 'prior_blocks_rerun_this_block':False,
 'prior_results':'Full stated Nishibuchi conjecture, sharp towers, exact dyadic periods and isometries, affine/shared and fixed-presentation polynomial obstruction results preserved with their previous evidence.',
 'controls':{'linear_equation':'one actual lift','zero_equation':'q actual lifts','singular_square':'two actual lifts modulo4 above0mod2','square_minus_two':'zero actual lifts modulo4 above0mod2','lower_residue_restriction':'zero polynomial has4 unrestricted rootsmod4, only2 above0mod2'},
 'remaining':['Lifting through all levels and a compatible p-adic limit under a surjective reduced Jacobian','Unrestricted native13.2/13.3 definitions, presentation invariance and descent','Exact higher differences, other least periods, general Mahler-kernel and arbitrary-row tail valuations'],
 'not_claimed':['Automatic infinite lifting from a single successful step','Rank-nullity cardinality formulas over composite moduli','Canonical presentation-independent native obstructions','Counts of integer representatives','A rewritten unified manuscript or external novelty'],
 'checklist':'REMAINING_CHECKLIST.md','archive_scope':'Known local Paper IX work and all previous cumulative archives by file hash, plus the newly checked counts block'
}
(s/'RELEASE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
# Add observed evidence to the current introduction.
readme=s/'README.md';t=readme.read_text()
needle='## Verification and reproduction\n\n'
para=f"The fresh replay passed **{len(report['runs'])} gates in {report['seconds']} seconds**: nine modules, three contract modules containing six expanded contract declarations, three rejected invalid proofs and **{report['explicit_declaration_audits']} explicit declaration audits**. Six new modules contribute {sum(counts.values())} declarations; the rest are three preserved dependencies and statement contracts.\n\n"
if para not in t:t=t.replace(needle,needle+para)
readme.write_text(t)
# Proportionate publication/source review; no unnecessary recompilation.
for f in [s/'replay_paper9_counts.py',*(s/'polynomial_counts/scripts').glob('*.py')]:ast.parse(f.read_text())
for f in (s/'README.md',s/'REMAINING_CHECKLIST.md',s/'polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md'):
 t=f.read_text();assert t.count('\\[')==t.count('\\]') and t.count('\\(')==t.count('\\)'),f
 assert '\x08' not in t and '\x0c' not in t,f
proofread={'mode':'self-review','scope':['README.md','REMAINING_CHECKLIST.md changed entries','polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md'],
 'routine_edits':'Current status, evidence paths and verification totals synchronized; mathematical delimiters checked.',
 'mathematical_token_corrections':'None required after drafting. New theorem statements were independently audited.',
 'unresolved_issues':[],'validation':'Python replay syntax/paths and mathematical delimiters PASS; independent mathematical review and exact Lean contracts PASS.',
 'limits':'Historical manuscripts were preserved, not proofread or rewritten during this block.'}
(s/'polynomial_counts/PROOFREAD_REVIEW.json').write_text(json.dumps(proofread,indent=2)+'\n')
# Verify every previous ZIP's uncompressed file contents are preserved.
files=[x for x in s.rglob('*') if x.is_file()]
assert all(not x.is_symlink() for x in s.rglob('*'))
covered={sha(x.read_bytes()) for x in files}
base=s/'baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip'
with zipfile.ZipFile(base) as z:
 baseline=[{'path':i.filename,'bytes':i.file_size,'sha256':sha(z.read(i))} for i in z.infolist() if not i.is_dir()]
covered.update(x['sha256'] for x in baseline)
archives=[]
for archive in sorted((r/'output').glob('*.zip')):
 if archive.name==s.name+'.zip':continue
 with zipfile.ZipFile(archive) as z:
  rows=[i for i in z.infolist() if not i.is_dir()]
  missing=[i.filename for i in rows if sha(z.read(i)) not in covered]
  assert not missing,(archive,missing)
 archives.append({'archive':archive.name,'archive_sha256':sha(archive.read_bytes()),'files':len(rows),'all_uncompressed_file_hashes_covered':True})
assert len(archives)==8,len(archives)
completeness={'status':'PASS','scope':'Known local Paper IX work plus new count block; not a census of remote files',
 'prior_archives':archives,'missing_prior_file_hashes':0,'baseline_zip_sha256':sha(base.read_bytes()),'baseline_entry_inventory':baseline,
 'new_source_inventory':'polynomial_counts/inventory.json','new_fresh_gate':'polynomial_counts/verification/polynomial_counts_verification.json','manuscript_files_exposed':25,
 'excluded':['Separate portable Lean runtime','Compiled outputs and caches','Unrelated raw search results','Full third-party Nishibuchi paper; URL/version/hash record retained','Duplicate cumulative ZIP containers'],
 'limitations':['Two older edge manuscripts recovered only as partial source windows','Annals TeX is a reconstructed text copy','Historical main manuscript not revised to absorb every continuation']}
(s/'PACKAGE_COMPLETENESS.json').write_text(json.dumps(completeness,indent=2)+'\n')
rows=[]
for f in sorted(s.rglob('*')):
 assert not f.is_symlink(),f
 if not f.is_file() or f==s/'MANIFEST.json':continue
 assert not any(x in ('build','__pycache__') for x in f.relative_to(s).parts),f
 assert not any(f.name.endswith(x) for x in ('.olean','.olean.server','.olean.private','.ir','.ir.sig','.pyc')),f
 rows.append({'path':str(f.relative_to(s)),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())})
(s/'MANIFEST.json').write_text(json.dumps({'release':s.name,'algorithm':'SHA-256','manifest_excludes_itself':True,'file_count_excluding_manifest':len(rows),'files':rows},indent=2)+'\n')
out=r/'output'/(s.name+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(s.rglob('*')):
  if f.is_file():z.write(f,str(Path(s.name)/f.relative_to(s)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.infolist())==len(rows)+1
 for row in rows:
  b=z.read(str(Path(s.name)/row['path']))
  assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
result={'status':'PASS','archive':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'files':len(rows)+1,'prior_archives_covered':len(archives),'zip_crc':'PASS','all_entry_hashes':'PASS'}
(p/'ARCHIVE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
