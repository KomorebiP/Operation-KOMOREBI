from pathlib import Path
from collections import Counter
import hashlib,json,shutil,zipfile,ast
r=Path('/workspace/scratch/196a43c5b4f3');p=r/'polynomial_towers'
s=r/'release_staging/PRSC_IX_Complete_Padic_Towers'
sha=lambda b:hashlib.sha256(b).hexdigest()
def copy(src,dst):
 assert src.is_file() and not src.is_symlink(),src
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for group in ('formalization','scripts','contracts','controls','audit'):
 for src in (p/group).iterdir():
  if src.is_file() and src.suffix in ('.lean','.py','.json','.md'):
   copy(src,s/'polynomial_towers'/group/src.name)
for n in ('inventory.json','PADIC_TOWERS.md','INDEPENDENT_PROOF_AUDIT.md','DEVELOPMENT.md'):
 copy(p/n,s/'polynomial_towers'/n)
for src in (p/'replay_01').iterdir():
 if src.is_file():copy(src,s/'polynomial_towers/verification'/src.name)
copy(p/'replay_01_console.log',s/'polynomial_towers/verification/replay_console.log')
for group in ('step','tower','limit','padic','controls_dev'):
 for src in (p/group).rglob('*'):
  if any(x in ('build','__pycache__') for x in src.relative_to(p).parts) or not src.is_file() or src.is_symlink():continue
  if src.suffix in ('.lean','.md','.log','.json'):
   copy(src,s/'polynomial_towers/development'/src.relative_to(p))
copy(p/'assemble_release.py',s/'historical/tower_release_assembly/assemble_release.py')
report=json.loads((p/'replay_01/polynomial_towers_verification.json').read_text())
rec=json.loads((p/'audit/reconciliation.json').read_text())
assert report['status']==rec['status']=='PASS'
assert rec['report_sha256']==sha((p/'replay_01/polynomial_towers_verification.json').read_bytes())
inv=json.loads((p/'inventory.json').read_text())
for e in inv['modules']+inv['contracts']+inv['negative_controls']:
 assert sha((s/'polynomial_towers'/e['source']).read_bytes())==e['sha256']
for e in report['runs']:
 assert sha((s/'polynomial_towers/verification'/e['log']).read_bytes())==e['log_sha256']
new={'PolynomialSurjectiveStep','PolynomialIntegerTower','PadicTowerLimit','PolynomialSmoothCounts','PolynomialPadicLift','PolynomialTowerControls'}
counts=Counter(d['kind'] for m in inv['modules'] if m['module'] in new for d in m['declarations'])
audit={
 'release':s.name,'author':'Komorebi P.','date':'2026-09-08','status':'PASS',
 'new_claims':['Surjective initial actual reduced Jacobian produces an infinite compatible integer polynomial tower','Reduced Jacobian is exactly constant along the tower','Compatible integer tower converges in the actual p-adic integers and retains every prescribed precision','Original polynomial evaluation is exactly zero at the constructed limit','Every selected smooth tower stage has exactly p^(d-e) next-level residue lifts and a one-element obstruction group'],
 'scope':{'polynomials':'Arbitrary finite lists F in Z[X_1,...,X_d]^e, zero dimensions allowed','integer_tower_base':'q>0, including composites and q=1','polynomial_start':'L>=1 and F(x)=0 modulo q^L','jacobian':'One initial surjectivity hypothesis on the actual map DF(x) modulo q','padic_root':'Prime p; a in Z_p^d, F(a)=0, a=x modulo p^L','tower':'z0=x, roots modulo p^(L+n), adjacent compatibility modulo p^(L+n), z_n tends to a','error':'a-z_n divisible by p^(L+n); not exact valuation equality','branching':'p^(d-e) distinct next-level residue lifts at each selected stage; no multi-level count asserted','uniqueness':'Only the limit of a fixed compatible sequence is asserted unique'},
 'new_modules':{'count':len(new),'explicit_declarations':sum(counts.values()),'declarations':dict(counts),'note':'Includes support lemmas and boundary controls, not independent discoveries.'},
 'fresh_gate':{k:report[k] for k in ['module_count','statement_contracts','negative_controls','explicit_declaration_audits','declarations','seconds','warnings_as_errors','fresh_project_compilation','mathlib_rebuilt','allowed_axioms']},
 'gate_count':len(report['runs']),'report':'polynomial_towers/verification/polynomial_towers_verification.json',
 'report_sha256':sha((p/'replay_01/polynomial_towers_verification.json').read_bytes()),
 'independent_audit':'polynomial_towers/INDEPENDENT_PROOF_AUDIT.md','independent_audit_sha256':sha((p/'INDEPENDENT_PROOF_AUDIT.md').read_bytes()),
 'independent_reconciliation':rec,'runtime':report['runtime'],'prior_blocks_rerun_this_block':False,
 'preserved_results':'Full stated Nishibuchi conjecture, sharp towers, exact dyadic periods and isometries, affine/shared and fixed-presentation polynomial obstruction/torsor/count results preserved with previous evidence.',
 'controls':['X^2-5 has lower roots mod2 and mod4 but none mod8 or through every level','Surjective rectangular projection has distinct dyadic roots in one lower residue','Nonsingular X-2 cannot retain an unjustified extra binary digit'],
 'remaining':['Formal uniqueness in the square nonsingular case','Rectangular local parametrization and general singular tower criteria','Unrestricted native13.2/13.3 objects, presentation invariance and descent','Exact higher differences, other least periods, general Mahler-kernel and arbitrary-row tail valuations'],
 'not_claimed':['Automatic infinite lifting from one successful singular step','Uniqueness among all polynomial roots with a merely surjective rectangular Jacobian','Joint lifting from separately surjective blocks without combined compatibility','Presentation-independent native canonical obstructions','A rewritten unified manuscript or external novelty'],
 'checklist':'REMAINING_CHECKLIST.md','archive_scope':'Known local Paper IX work and all previous cumulative archives by file hash, plus the newly checked tower/root block'
}
(s/'RELEASE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
readme=s/'README.md';t=readme.read_text();needle='## Verification and reproduction\n\n'
para=f"The fresh replay passed **{len(report['runs'])} gates in {report['seconds']} seconds**: 14 modules, three contract files containing five expanded contract declarations, three rejected invalid proofs and **{report['explicit_declaration_audits']} explicit declaration audits**. Six new modules contribute {sum(counts.values())} declarations (31 theorems and four definitions); the other audited declarations belong to preserved dependencies and contracts.\n\n"
if para not in t:t=t.replace(needle,needle+para)
readme.write_text(t)
for f in [s/'replay_paper9_towers.py',*(s/'polynomial_towers/scripts').glob('*.py')]:ast.parse(f.read_text())
for f in (s/'README.md',s/'REMAINING_CHECKLIST.md',s/'polynomial_towers/PADIC_TOWERS.md'):
 t=f.read_text();assert t.count('\\[')==t.count('\\]') and t.count('\\(')==t.count('\\)'),f
 assert '\x08' not in t and '\x0c' not in t,f
proofread={'mode':'self-review','scope':['README.md','REMAINING_CHECKLIST.md changed entries','polynomial_towers/PADIC_TOWERS.md'],
 'routine_edits':'Status, evidence paths and fresh gate totals synchronized; mathematical delimiters reviewed.',
 'mathematical_token_corrections':'None after drafting; new theorem statements independently audited.',
 'unresolved_issues':[],'validation':'Python replay syntax and mathematical delimiters PASS; exact Lean contracts and independent source review PASS.',
 'limits':'Historical manuscripts were preserved, not rewritten during this block.'}
(s/'polynomial_towers/PROOFREAD_REVIEW.json').write_text(json.dumps(proofread,indent=2)+'\n')
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
assert len(archives)==9,len(archives)
completeness={'status':'PASS','scope':'Known local Paper IX collection plus new tower/root block; not a census of remote files','prior_archives':archives,
 'missing_prior_file_hashes':0,'baseline_zip_sha256':sha(base.read_bytes()),'baseline_entry_inventory':baseline,
 'new_source_inventory':'polynomial_towers/inventory.json','new_fresh_gate':'polynomial_towers/verification/polynomial_towers_verification.json','manuscript_files_exposed':25,
 'excluded':['Separate portable Lean runtime','Compiled outputs and caches','Unrelated raw search results','Full third-party Nishibuchi paper; URL/version/hash record retained','Duplicate cumulative ZIP containers'],
 'limitations':['Two older edge manuscripts recovered only as partial source windows','Annals TeX reconstructed text copy','Historical main manuscript not revised to absorb every continuation']}
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
