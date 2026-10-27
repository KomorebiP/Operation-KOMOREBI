from pathlib import Path
import json,hashlib,shutil,subprocess
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work12/Komorebi_LSM_Lean_0.12.0';old=b/'work11/Komorebi_LSM_Lean_0.10.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['README.md','LEAN_GUIDE.md','AUDIT.md','PROGRESS.md','PROGRESS.json','COVERAGE.md','COVERAGE.json','ROADMAP_1.0.md','ROADMAP_1.0.json','CONTINUE_HERE.md','RELEASE_COUNTS.json','SOURCE_LINEAGE.json','PUBLICATION_STATUS.md','scripts/check_metadata.py']:
 (r/'history'/('PREDECESSOR_0.11.0_'+n.replace('/','_'))).write_bytes((old/n).read_bytes())
z=b/'deliverables11/Komorebi_Large_Signal_Model_Lean_0.11.0.zip';shutil.copy2(z,r/'history'/z.name)
mods=['OneSidedSubspace','NoisySubspaceResidual','Block12Examples']
(r/'KomorebiLSM.lean').write_text((old/'KomorebiLSM.lean').read_text()+''.join('import KomorebiLSM.'+m+'\n' for m in mods))
s=(old/'scripts/verify.py').read_text().replace("'Block11Examples']","'Block11Examples',"+','.join(map(repr,mods))+']').replace("'release':'0.11.0'","'release':'0.12.0'")
(r/'scripts/verify.py').write_text(s)
(r/'negative_controls/ProjectionGapWithoutEqualRank.lean').write_text('''import KomorebiLSM.Block12Examples
example : ‖(⊥ : Submodule ℝ ℝ).starProjection-(⊤ : Submodule ℝ ℝ).starProjection‖ ≤ 0 := by
  rw [Komorebi.LSM.Block12Examples.unequal_rank_full_gap_one]
  norm_num
''')
subprocess.run(['python3','scripts/build_inventory.py','--write'],cwd=r,check=True)
d=json.loads((r/'DECLARATIONS.json').read_text());nt=sum(x['kind']=='theorem' for x in d);ne=sum(x['kind']=='theorem' and 'Examples' in x['module'] for x in d)
c=dict(release='0.12.0',proof_modules=85,named_declarations=len(d),named_theorems=nt,example_theorems=ne,supporting_theorems=nt-ne,new_theorems=nt-1028,new_example_theorems=ne-316,complete_propositions=38,partial_propositions=1,unformalized_propositions=48,negative_controls=77)
(r/'RELEASE_COUNTS.json').write_text(json.dumps(c,indent=2)+'\n')
cover=json.loads((old/'COVERAGE.json').read_text());cover['formalization_version']='0.12.0'
e=cover['entries'][31];e['scope']='Proved: for equal-dimensional finite-dimensional real inner-product subspaces, a one-sided residual bound δ<1 implies the full projection gap bound δ, a coordinate lower bound sqrt(1-δ²), injection and an inverse norm bound. True residual is bounded by observed tail plus noise. Given an actual right inverse on the true subspace with norm ≤1/s, an observed tail ≤ε and noise ≤ε<s/2 yield the conditional gap ≤2ε/s<1. NOT proved here: sorted singular-value perturbation/rank separation including maximal-rank convention; construction and tail characterization of the leading-r left singular subspace; derivation of the right inverse norm from σ_r(X); or the explicit orthonormal-basis matrix decoder and minimum-singular-value formula. P32 remains partial.'
e['lean_targets']=[dict(x,source_sha256=sha(r/x['file'])) for x in d if x['module'] in ['SubspaceCoordinates','OneSidedSubspace','NoisySubspaceResidual']]
(r/'COVERAGE.json').write_text(json.dumps(cover,indent=2)+'\n')
road=json.loads((old/'ROADMAP_1.0.json').read_text());road['release']='0.12.0';(r/'ROADMAP_1.0.json').write_text(json.dumps(road,indent=2)+'\n')
lin=json.loads((old/'SOURCE_LINEAGE.json').read_text());lin.update(formalization_version='0.12.0',predecessor_archive=dict(path='history/'+z.name,sha256=sha(z),bytes=z.stat().st_size),inherited_proof_files={str(p.relative_to(old)):sha(p) for p in (old/'KomorebiLSM').glob('*.lean')},inherited_control_files={str(p.relative_to(old)):sha(p) for p in (old/'negative_controls').glob('*.lean')})
lin['runtime_note']='Reused the pinned runtime restored during block11, without changes. Compiler and all nine dependency pins checked by verifier; see historical block11 recovery records.'
(r/'SOURCE_LINEAGE.json').write_text(json.dumps(lin,indent=2)+'\n')
s=(old/'scripts/check_metadata.py').read_text()
for a,v in {'1338':str(len(d)),'1028 named':f'{nt} named','==1028':f'=={nt}','316 in':f'{ne} in','==316':f'=={ne}',"'Block11Examples']":"'Block11Examples','Block12Examples']",'All 78 inherited':'All 82 inherited',"inherited_proof_files'])==78":"inherited_proof_files'])==82",'All 1304 inherited':'All 1338 inherited','len(previous)==1304':'len(previous)==1338','All 82 proof modules':'All 85 proof modules','len(set(root_modules))==82':'len(set(root_modules))==85','All 76 negative controls':'All 77 negative controls',"counts['negative_controls']==76":"counts['negative_controls']==77",'All 72 predecessor':'All 76 predecessor',"inherited_control_files'])==72":"inherited_control_files'])==76",'Four new proof files and four new negative controls':'Three new proof files and one new negative control',"inherited_proof_files'])==4":"inherited_proof_files'])==3", "counts['negative_controls']-72==4":"counts['negative_controls']-76==1","counts['named_theorems']-998":"counts['named_theorems']-1028"}.items():s=s.replace(a,v)
pos=s.index("    result={'kind'")
s=s[:pos]+'''    record('One-sided residual implies full gap without assuming that gap',
           all('Komorebi.LSM.OneSidedSubspace.'+n in by_name for n in
             ['reverse_coordinate_lower','reverse_residual','reverse_operator_bound','projection_gap']))
    record('Noisy residual transfer retains explicit spectral premises',
           all('Komorebi.LSM.OneSidedSubspace.'+n in by_name for n in
             ['true_residual','residual_on_range','noisy_projection_gap','two_epsilon_gap']) and
           'NOT proved here' in cover['entries'][31]['scope'])
'''+s[pos:]
(r/'scripts/check_metadata.py').write_text(s)
print(c)
