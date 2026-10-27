from pathlib import Path
import json,hashlib,subprocess,zipfile
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work13/Komorebi_LSM_Lean_0.13.0';old=b/'work12/Komorebi_LSM_Lean_0.12.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['README.md','LEAN_GUIDE.md','AUDIT.md','PROGRESS.md','PROGRESS.json','COVERAGE.md','COVERAGE.json','ROADMAP_1.0.md','ROADMAP_1.0.json','CONTINUE_HERE.md','RELEASE_COUNTS.json','SOURCE_LINEAGE.json','PUBLICATION_STATUS.md','scripts/check_metadata.py']:
 (r/'history'/('PREDECESSOR_0.12.0_'+n.replace('/','_'))).write_bytes((old/n).read_bytes())
z=b/'deliverables12/Komorebi_Large_Signal_Model_Lean_0.12.0.zip';snap=r/'history/PREDECESSOR_0.12.0_Source_Snapshot.zip'
with zipfile.ZipFile(z) as src, zipfile.ZipFile(snap,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
 omitted=[]
 for item in src.infolist():
  if item.is_dir():continue
  if item.filename.endswith('.zip'):omitted.append(item.filename);continue
  name=item.filename
  if name=='Komorebi_LSM_Lean_0.12.0/MANIFEST.json':name='Komorebi_LSM_Lean_0.12.0/ORIGINAL_ARCHIVE_MANIFEST.json'
  dst.writestr(name,src.read(item.filename))
snapshot={'source_archive_name':z.name,'source_archive_sha256':sha(z),'snapshot':str(snap.relative_to(r)),'omitted_nested_archives':omitted,'note':'Complete predecessor proof/control/declaration evidence copied from the exact delivered ZIP; redundant nested ZIP payloads omitted. Original manifest renamed to avoid implying this snapshot has the original full inventory. Original delivered archive remains saved separately.'}
(r/'verification/PREDECESSOR_0.12.0_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2)+'\n')
mods=['SpectralLowerBound','SpectralPseudoinverse','SpectralSharpness','Block13Examples']
(r/'KomorebiLSM.lean').write_text((old/'KomorebiLSM.lean').read_text()+''.join('import KomorebiLSM.'+m+'\n' for m in mods))
s=(old/'scripts/verify.py').read_text().replace("'Block12Examples']","'Block12Examples',"+','.join(map(repr,mods))+']').replace("'release':'0.12.0'","'release':'0.13.0'")
(r/'scripts/verify.py').write_text(s)
(r/'negative_controls/SpectralInverseTooSmall.lean').write_text('''import KomorebiLSM.Block13Examples
example : ‖Komorebi.LSM.Identification.pinvL ((2:ℝ) • ContinuousLinearMap.id ℝ ℝ)‖ ≤ (1/4:ℝ) := by
  rw [Komorebi.LSM.Block13Examples.double_inverse_norm]
  norm_num
''')
(r/'negative_controls/ZeroRankPositiveSpectrum.lean').write_text('''import KomorebiLSM.Block13Examples
example : 0 < Komorebi.LSM.Spectral.leastPositive (0 : ℝ →ₗ[ℝ] ℝ) := by
  rw [Komorebi.LSM.Block13Examples.zero_has_no_positive_singular_value]
  norm_num
''')
subprocess.run(['python3','scripts/build_inventory.py','--write'],cwd=r,check=True)
d=json.loads((r/'DECLARATIONS.json').read_text());nt=sum(x['kind']=='theorem' for x in d);ne=sum(x['kind']=='theorem' and 'Examples' in x['module'] for x in d)
c=dict(release='0.13.0',proof_modules=89,named_declarations=len(d),named_theorems=nt,example_theorems=ne,supporting_theorems=nt-ne,new_theorems=nt-1043,new_example_theorems=ne-320,complete_propositions=38,partial_propositions=1,unformalized_propositions=48,negative_controls=79)
(r/'RELEASE_COUNTS.json').write_text(json.dumps(c,indent=2)+'\n')
cover=json.loads((old/'COVERAGE.json').read_text());cover['formalization_version']='0.13.0'
e=cover['entries'][31];e['scope']='Proved: actual sorted singular values give the lower norm bound on the orthogonal kernel complement. For positive rank r, the existing orthogonal pseudoinverse and its constructed restriction to the true range have exact norm 1/σ_r(X), with zero-based index r−1. A unit minimizing vector is constructed from the Gram eigenbasis. Together with block12, an estimated subspace of equal dimension whose observed tail is ≤ε gives the full gap ≤2ε/σ_r(X)<1 under actual noise ≤ε<σ_r(X)/2. The right inverse and its norm are derived, not supplied. Coordinate lower bounds, injection and inverse conditioning remain available from the proved gap. NOT proved here: singular-value perturbation/rank separation including maximal-rank convention; construction and residual characterization of the actual leading-r left singular subspace; or the explicit orthonormal-basis matrix decoder and minimum-singular-value formula. P32 remains partial.'
e['lean_targets']=[dict(x,source_sha256=sha(r/x['file'])) for x in d if x['module'] in ['SubspaceCoordinates','OneSidedSubspace','NoisySubspaceResidual','SpectralLowerBound','SpectralPseudoinverse','SpectralSharpness']]
(r/'COVERAGE.json').write_text(json.dumps(cover,indent=2)+'\n')
road=json.loads((old/'ROADMAP_1.0.json').read_text());road['release']='0.13.0';(r/'ROADMAP_1.0.json').write_text(json.dumps(road,indent=2)+'\n')
lin=json.loads((old/'SOURCE_LINEAGE.json').read_text());lin.update(formalization_version='0.13.0',predecessor_archive=dict(path=str(snap.relative_to(r)),sha256=sha(snap),bytes=snap.stat().st_size,kind='source_snapshot_without_nested_archives'),original_predecessor_archive=dict(name=z.name,sha256=sha(z),bytes=z.stat().st_size,library_file_id='libfile_e8dc9db362fc8191bd2c6d7d4e2c2623'),inherited_proof_files={str(p.relative_to(old)):sha(p) for p in (old/'KomorebiLSM').glob('*.lean')},inherited_control_files={str(p.relative_to(old)):sha(p) for p in (old/'negative_controls').glob('*.lean')})
(r/'SOURCE_LINEAGE.json').write_text(json.dumps(lin,indent=2)+'\n')
s=(old/'scripts/check_metadata.py').read_text()
repl={'1354 unique':f'{len(d)} unique',"counts['named_declarations'] == 1354":f"counts['named_declarations'] == {len(d)}",'1043 named':f'{nt} named','==1043':f'=={nt}','320 in':f'{ne} in','==320':f'=={ne}',"'Block12Examples']":"'Block12Examples','Block13Examples']",'All 82 inherited':'All 85 inherited',"inherited_proof_files'])==82":"inherited_proof_files'])==85",'All 1338 inherited':'All 1354 inherited','len(previous)==1338':'len(previous)==1354','All 85 proof modules':'All 89 proof modules','len(set(root_modules))==85':'len(set(root_modules))==89','All 77 negative controls':'All 79 negative controls',"counts['negative_controls']==77":"counts['negative_controls']==79",'All 76 predecessor':'All 77 predecessor',"inherited_control_files'])==76":"inherited_control_files'])==77",'Three new proof files and one new negative control':'Four new proof files and two new negative controls',"inherited_proof_files'])==3":"inherited_proof_files'])==4","counts['negative_controls']-76==1":"counts['negative_controls']-77==2","counts['named_theorems']-1028":"counts['named_theorems']-1043",'Preserved predecessor ZIP matches its hash':'Preserved predecessor source snapshot matches its hash'}
for a,v in repl.items():s=s.replace(a,v)
pos=s.index("    result={'kind'")
s=s[:pos]+'''    record('Actual spectral lower bound and exact pseudoinverse norm are linked',
           all('Komorebi.LSM.Spectral.'+n in by_name for n in
             ['rightBasis','image_norm_sq','tail_coordinate_zero','leastPositive',
              'lower_on_kernel_orthogonal','exists_unit_minimizer','pinv_operator_norm_eq',
              'rangeInverse_right','rangeInverse_norm_eq','gap_from_observed_tail']))
    record('P32 retains missing spectral-tail and basis obligations',
           cover['entries'][31]['status']=='partial' and
           'NOT proved here' in cover['entries'][31]['scope'] and
           'The right inverse and its norm are derived' in cover['entries'][31]['scope'])
'''+s[pos:]
(r/'scripts/check_metadata.py').write_text(s)
print(c)
