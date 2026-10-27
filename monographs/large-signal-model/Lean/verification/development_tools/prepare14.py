from pathlib import Path
import json,hashlib,subprocess,zipfile
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work14/Komorebi_LSM_Lean_0.14.0';old=b/'work13/Komorebi_LSM_Lean_0.13.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['README.md','LEAN_GUIDE.md','AUDIT.md','PROGRESS.md','PROGRESS.json','COVERAGE.md','COVERAGE.json','ROADMAP_1.0.md','ROADMAP_1.0.json','CONTINUE_HERE.md','RELEASE_COUNTS.json','SOURCE_LINEAGE.json','PUBLICATION_STATUS.md','scripts/check_metadata.py']:
 (r/'history'/('PREDECESSOR_0.13.0_'+n.replace('/','_'))).write_bytes((old/n).read_bytes())
z=b/'deliverables13/Komorebi_Large_Signal_Model_Lean_0.13.0.zip';snap=r/'history/PREDECESSOR_0.13.0_Source_Snapshot.zip'
assert sha(z)=='7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5'
with zipfile.ZipFile(z) as src, zipfile.ZipFile(snap,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
 omitted=[]
 for item in src.infolist():
  if item.is_dir():continue
  if item.filename.endswith('.zip'):omitted.append(item.filename);continue
  name=item.filename
  if name=='Komorebi_LSM_Lean_0.13.0/MANIFEST.json':name='Komorebi_LSM_Lean_0.13.0/ORIGINAL_ARCHIVE_MANIFEST.json'
  dst.writestr(name,src.read(item.filename))
snapshot={'source_archive_name':z.name,'source_archive_sha256':sha(z),'snapshot':str(snap.relative_to(r)),'omitted_nested_archives':omitted,'note':'Complete predecessor proof/control/declaration evidence from the exact delivered ZIP; redundant nested ZIP payloads omitted. Original manifest renamed. Original delivered archive is separately saved.'}
(r/'verification/PREDECESSOR_0.13.0_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2)+'\n')
mods=['SpectralSubspaces','SpectralTail','SingularPerturbation','LeftSingularModes','NoisySpectralSubspace','BasisCoordinates','BasisDecoder','DecoderMatrixFormula','FiniteTableP32','Block14Examples']
(r/'KomorebiLSM.lean').write_text((old/'KomorebiLSM.lean').read_text()+''.join('import KomorebiLSM.'+m+'\n' for m in mods))
s=(old/'scripts/verify.py').read_text().replace("'Block13Examples']","'Block13Examples',"+','.join(map(repr,mods))+']').replace("'release':'0.13.0'","'release':'0.14.0'")
(r/'scripts/verify.py').write_text(s)
(r/'negative_controls/SpectralTailTooSmall.lean').write_text('''import KomorebiLSM.Block14Examples
example : ‖(Komorebi.LSM.Spectral.leadingLeft
    (((2:ℝ) • ContinuousLinearMap.id ℝ ℝ).toLinearMap) 0 (by simp))ᗮ.starProjection.comp
    ((2:ℝ) • ContinuousLinearMap.id ℝ ℝ)‖ ≤ 1 := by
  rw [Komorebi.LSM.Block14Examples.discard_all_scalar_modes]
  norm_num
''')
(r/'negative_controls/SpectralPerturbationTooSmall.lean').write_text('''import KomorebiLSM.Block14Examples
example : |((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)).singularValues 0 -
    (0 : ℝ →ₗ[ℝ] ℝ).singularValues 0| ≤ 1 := by
  rw [Komorebi.LSM.Block14Examples.double_first_singular]
  norm_num
''')
subprocess.run(['python3','scripts/build_inventory.py','--write'],cwd=r,check=True)
d=json.loads((r/'DECLARATIONS.json').read_text());nt=sum(x['kind']=='theorem' for x in d);ne=sum(x['kind']=='theorem' and 'Examples' in x['module'] for x in d)
c=dict(release='0.14.0',proof_modules=99,named_declarations=len(d),named_theorems=nt,example_theorems=ne,supporting_theorems=nt-ne,new_theorems=nt-1063,new_example_theorems=ne-324,complete_propositions=39,partial_propositions=0,unformalized_propositions=48,negative_controls=81)
(r/'RELEASE_COUNTS.json').write_text(json.dumps(c,indent=2)+'\n')
cover=json.loads((old/'COVERAGE.json').read_text());cover.update(formalization_version='0.14.0',complete=sorted(cover['complete']+[32]),partial=[],interpretation='Statement-level self-review; Lean kernel checks the formal statements, not their English correspondence. P32 is complete in its stated finite-table scope. See the current source and exact-archive verification.')
e=cover['entries'][31];e['status']='complete';e['scope']='Full finite-table P32 for real finite-dimensional inner-product maps, hence rectangular real matrices with their Euclidean norms. Actual sorted, zero-padded singular values satisfy the all-index operator perturbation bound. The leading-r left subspace is constructed as images of ordered right Gram modes and proved to be the span of orthonormal left Gram modes; its dimension and exact residual norm are derived. Positive true rank and noise ≤ε<σ_r(X)/2 imply rank separation and projection gap ≤2ε/σ_r(X)<1 without supplied inverse, tail or projection-gap premises. For arbitrary orthonormal bases of the true and learned ranges, the actual cross-matrix minimum singular value is ≥sqrt(1−(2ε/σ_r(X))²), estimated coordinates are injective, and the explicit ordinary matrix inverse decoder U(UhatᵀU)⁻¹ has both inverse laws and the stated norm bound. The maximum possible rank convention is proved using zero padding. This does not certify that a finite table captures the full process.'
e['lean_targets']=[dict(x,source_sha256=sha(r/x['file'])) for x in d if x['module'] in ['SubspaceCoordinates','OneSidedSubspace','NoisySubspaceResidual','SpectralLowerBound','SpectralPseudoinverse','SpectralSharpness']+mods[:-1]]
(r/'COVERAGE.json').write_text(json.dumps(cover,indent=2)+'\n')
road=json.loads((old/'ROADMAP_1.0.json').read_text());road.update(release='0.14.0',completed=cover['complete'],partial=[],remaining_count=48)
road['tracks']=[dict(t,propositions=[n for n in t['propositions'] if n!=32]) for t in road['tracks'] if any(n!=32 for n in t['propositions'])]
(r/'ROADMAP_1.0.json').write_text(json.dumps(road,indent=2)+'\n')
lin=json.loads((old/'SOURCE_LINEAGE.json').read_text());lin.update(formalization_version='0.14.0',predecessor_archive=dict(path=str(snap.relative_to(r)),sha256=sha(snap),bytes=snap.stat().st_size,kind='source_snapshot_without_nested_archives'),original_predecessor_archive=dict(name=z.name,sha256=sha(z),bytes=z.stat().st_size,library_file_id='libfile_729eaed94db48191b7d4bdbc4ae19fea'),inherited_proof_files={str(p.relative_to(old)):sha(p) for p in (old/'KomorebiLSM').glob('*.lean')},inherited_control_files={str(p.relative_to(old)):sha(p) for p in (old/'negative_controls').glob('*.lean')})
(r/'SOURCE_LINEAGE.json').write_text(json.dumps(lin,indent=2)+'\n')
s=(old/'scripts/check_metadata.py').read_text()
repl={'1378 unique':f'{len(d)} unique',"counts['named_declarations'] == 1378":f"counts['named_declarations'] == {len(d)}",'1063 named':f'{nt} named','==1063':f'=={nt}','324 in':f'{ne} in','==324':f'=={ne}',"'Block13Examples']":"'Block13Examples','Block14Examples']",'All 85 inherited':'All 89 inherited',"inherited_proof_files'])==85":"inherited_proof_files'])==89",'All 1354 inherited':'All 1378 inherited','len(previous)==1354':'len(previous)==1378','All 89 proof modules':'All 99 proof modules','len(set(root_modules))==89':'len(set(root_modules))==99','All 79 negative controls':'All 81 negative controls',"counts['negative_controls']==79":"counts['negative_controls']==81",'All 77 predecessor':'All 79 predecessor',"inherited_control_files'])==77":"inherited_control_files'])==79",'Four new proof files':'Ten new proof files',"inherited_proof_files'])==4":"inherited_proof_files'])==10","counts['negative_controls']-77==2":"counts['negative_controls']-79==2","counts['named_theorems']-1043":"counts['named_theorems']-1063",'Coverage is 38 complete, one partial':'Coverage is 39 complete, zero partial','30, 33, 34':'30, 32, 33, 34',"if x['status']=='partial']==[32]":"if x['status']=='partial']==[]"}
for a,v in repl.items():s=s.replace(a,v)
s=s.replace('len(remaining)==len(set(remaining))==49','len(remaining)==len(set(remaining))==48')
s=s.replace("record('P32 remains partial and does not assume a data-derived gap as proved',\n           cover['entries'][31]['status']=='partial' and 'NOT proved here' in cover['entries'][31]['scope'])", "record('P32 is complete with its finite-table scope retained',\n           cover['entries'][31]['status']=='complete' and 'does not certify' in cover['entries'][31]['scope'])")
s=s.replace("'Noisy residual transfer retains explicit spectral premises'","'Earlier residual transfer and constructed spectral endpoint coexist'")
s=s.replace("and\n           'NOT proved here' in cover['entries'][31]['scope']", "and\n           'Komorebi.LSM.Spectral.finite_table_stability' in by_name")
a=s.index("    record('P32 retains missing spectral-tail and basis obligations'");zpos=s.index("    result={'kind'",a)
s=s[:a]+'''    record('P32 derives actual spectral tails and basis decoder',
           cover['entries'][31]['status']=='complete' and
           all('Komorebi.LSM.'+n in by_name for n in
             ['Spectral.leadingLeft_tail_norm','Spectral.singularValue_abs_sub_le',
              'Spectral.leadingLeft_eq_span_leftModes','Spectral.singularValue_zero_at_max_rank',
              'BasisCoordinates.cross_min_singular','BasisCoordinates.decoder_matrix_formula',
              'BasisCoordinates.decoder_coordinates','BasisCoordinates.coordinates_decoder',
              'BasisCoordinates.decoder_norm_bound','FiniteTableP32.coordinates_and_decoder']))
'''+s[zpos:]
(r/'scripts/check_metadata.py').write_text(s)
print(json.dumps(c,indent=2))
