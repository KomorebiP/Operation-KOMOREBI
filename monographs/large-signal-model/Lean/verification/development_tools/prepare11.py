from pathlib import Path
import json,hashlib,shutil,subprocess,zipfile
base=Path('/workspace/scratch/2e8d212e9ca7');r=base/'work11/Komorebi_LSM_Lean_0.10.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
oldzip=base/'recovery11/Komorebi_Large_Signal_Model_Lean_0.10.0.zip'
with zipfile.ZipFile(oldzip) as z:
 prefix='Komorebi_LSM_Lean_0.10.0/'
 old={n[len(prefix):]:z.read(n) for n in z.namelist() if n.startswith(prefix) and not n.endswith('/')}
for n in ['README.md','LEAN_GUIDE.md','AUDIT.md','PROGRESS.md','PROGRESS.json','COVERAGE.md','COVERAGE.json','ROADMAP_1.0.md','ROADMAP_1.0.json','CONTINUE_HERE.md','RELEASE_COUNTS.json','SOURCE_LINEAGE.json','PUBLICATION_STATUS.md','scripts/check_metadata.py']:
 (r/'history'/('PREDECESSOR_0.10.0_'+n.replace('/','_'))).write_bytes(old[n])
shutil.copy2(oldzip,r/'history'/oldzip.name)
mods=['CoreStability','FilteringStability','SubspaceCoordinates','Block11Examples']
(r/'KomorebiLSM.lean').write_text(old['KomorebiLSM.lean'].decode()+''.join('import KomorebiLSM.'+m+'\n' for m in mods))
s=old['scripts/verify.py'].decode().replace("'Block10Examples']","'Block10Examples',"+','.join(map(repr,mods))+']').replace("'release':'0.10.0'","'release':'0.11.0'")
(r/'scripts/verify.py').write_text(s)
controls={
 'WeakFilteringMargin': 'example : (0:ℝ) < (ContinuousLinearMap.id ℝ ℝ) 0 := by norm_num\n',
 'NegativeFittedMass': 'example : (0:ℝ) < (ContinuousLinearMap.id ℝ ℝ) (-1) := by norm_num\n',
 'PosteriorAbsoluteLipschitz': '''example :
    ‖Filtering.normalize (ContinuousLinearMap.fst ℝ ℝ ℝ) ((1/4:ℝ),1/4) -
      Filtering.normalize (ContinuousLinearMap.fst ℝ ℝ ℝ) ((1/4:ℝ),0)‖ ≤ (1/4:ℝ) := by
  norm_num [Filtering.normalize, Prod.norm_def]
''',
 'WeakSubspaceGap': 'example : (0:ℝ) < Real.sqrt (1-(1:ℝ)^2) := by norm_num\n'}
for n,s in controls.items():(r/'negative_controls'/f'{n}.lean').write_text('import KomorebiLSM.Block11Examples\nopen Komorebi.LSM\n'+s)
subprocess.run(['python3','scripts/build_inventory.py','--write'],cwd=r,check=True)
d=json.loads((r/'DECLARATIONS.json').read_text());nt=sum(x['kind']=='theorem' for x in d);ne=sum(x['kind']=='theorem' and 'Examples' in x['module'] for x in d)
c={'release':'0.11.0','proof_modules':82,'named_declarations':len(d),'named_theorems':nt,'example_theorems':ne,'supporting_theorems':nt-ne,'new_theorems':nt-998,'new_example_theorems':ne-308,'complete_propositions':38,'partial_propositions':1,'unformalized_propositions':48,'negative_controls':76}
(r/'RELEASE_COUNTS.json').write_text(json.dumps(c,indent=2)+'\n')
cover=json.loads(old['COVERAGE.json']);oldcomplete=cover['complete'];cover.update(formalization_version='0.11.0',complete=sorted(oldcomplete+[33,34]),partial=[32],not_formalized_count=48)
scopes={
32:('partial','SubspaceCoordinates','Proved: given an actual orthogonal projection gap δ<1, the coordinate projection has lower norm bound sqrt(1-δ²), is injective, and for equal-dimensional subspaces has a constructed continuous linear inverse bounded by 1/sqrt(1-δ²). The gap is an explicit hypothesis, not a conclusion from noisy data. NOT proved here: sorted-singular-value perturbation/rank separation, the leading-r singular-subspace residual, the equal-rank projection norm identity, substitution δ=2ε/s, or the explicit orthonormal-basis matrix decoder formula. P32 is not complete.'),
33:('complete','CoreStability','Finite-dimensional real inner-product square core. The least singular value uses the inherited variational rowGain definition (infimum of adjoint norm ratios; inherited unit-sphere equivalence), consistently with P16. The constructed pseudoinverse is shown to be a two-sided inverse under the strict input error gap. Both exact error identities, the true-operator error bound, fitted-operator bound, and checked fitted-gap denominator bound are proved. Exact arithmetic and fixed core only; no data-dependent coverage or floating-point solve guarantee.'),
34:('complete','FilteringStability','Arbitrary real normed state space and continuous mass functional. Prediction error is derived from actual operators and states. True branch has positive mass, true state and posterior obey the supplied radius, and the strict dual-norm error budget guarantees positive fitted mass. Exact normalized residual identity and both denominator bounds are proved. Actual true and fitted recurrences yield the product-sum bound and a uniform contraction estimate. Checked realized fitted denominators do not certify all branches or probability-valid fitted states.')}
for k,(status,mod,scope) in scopes.items():
 e=cover['entries'][k-1];e.update(status=status,scope=scope,lean_targets=[dict(x,source_sha256=sha(r/x['file'])) for x in d if x['module']==mod])
cover['interpretation']='Statement-level self-review; kernel checks formal statements, not the English correspondence. P32 explicitly remains partial. See the current source and external archive verification.'
(r/'COVERAGE.json').write_text(json.dumps(cover,indent=2)+'\n')
road=json.loads(old['ROADMAP_1.0.json']);road.update(release='0.11.0',completed=cover['complete'],remaining_count=49,partial=[32])
for t in road['tracks']:t['propositions']=[n for n in t['propositions'] if n not in [33,34]]
(r/'ROADMAP_1.0.json').write_text(json.dumps(road,indent=2)+'\n')
lin=json.loads(old['SOURCE_LINEAGE.json']);lin.update(formalization_version='0.11.0',predecessor_archive={'path':'history/'+oldzip.name,'sha256':sha(oldzip),'bytes':oldzip.stat().st_size},inherited_proof_files={n:hashlib.sha256(v).hexdigest() for n,v in old.items() if n.startswith('KomorebiLSM/') and n.endswith('.lean')},inherited_control_files={n:hashlib.sha256(v).hexdigest() for n,v in old.items() if n.startswith('negative_controls/') and n.endswith('.lean')})
lin['runtime_note']='Restored pinned archive from all seven saved parts; combined SHA-256 matched. Full extraction exhausted disk. Retried without native/editor artifacts, then restored required .olean.server files after import diagnostics. Compiler and all nine dependency pins are checked by the verifier. No proof-check bypass or library source edits.'
(r/'SOURCE_LINEAGE.json').write_text(json.dumps(lin,indent=2)+'\n')
s=old['scripts/check_metadata.py'].decode()
repl={
 '1304 unique named declarations':f'{len(d)} unique named declarations',"counts['named_declarations'] == 1304":f"counts['named_declarations'] == {len(d)}",
 '998 named theorems, 308 in example modules':f'{nt} named theorems, {ne} in example modules',"counts['named_theorems']==998":f"counts['named_theorems']=={nt}","counts['example_theorems']==308":f"counts['example_theorems']=={ne}","'Block10Examples']":"'Block10Examples','Block11Examples']",
 'Coverage is 36 complete, no partial, 51 unformalized':'Coverage is 38 complete, one partial, 48 unformalized','=='+repr(oldcomplete):'=='+repr(cover['complete']),"x['status']=='partial']==[]":"x['status']=='partial']==[32]","x['status']=='not_formalized' for x in cover['entries'])==51":"x['status']=='not_formalized' for x in cover['entries'])==48",
 'All 74 inherited proof files':'All 78 inherited proof files',"len(lineage['inherited_proof_files'])==74":"len(lineage['inherited_proof_files'])==78",'All 1256 inherited declaration records':'All 1304 inherited declaration records','len(previous)==1256':'len(previous)==1304',
 'All 78 proof modules':'All 82 proof modules','len(set(root_modules))==78':'len(set(root_modules))==82','All 72 negative controls':'All 76 negative controls',"counts['negative_controls']==72":"counts['negative_controls']==76","counts['negative_controls']-68==4":"counts['negative_controls']-72==4","counts['named_theorems']-968":"counts['named_theorems']-998",
 'len(remaining)==len(set(remaining))==51':'len(remaining)==len(set(remaining))==49','All 68 predecessor rejection-control sources':'All 72 predecessor rejection-control sources',"len(lineage['inherited_control_files'])==68":"len(lineage['inherited_control_files'])==72"}
for a,b in repl.items():s=s.replace(a,b)
pos=s.index("    result={'kind'")
s=s[:pos]+'''    record('P32 remains partial and does not assume a data-derived gap as proved',
           cover['entries'][31]['status']=='partial' and 'NOT proved here' in cover['entries'][31]['scope'])
    record('P33 includes both identities and all three denominator bounds',
           all('Komorebi.LSM.Identification.'+n in by_name for n in ['core_inverse_laws','core_error_identity','core_error_bound','core_fitted_residual','core_fitted_identity','core_fitted_bound','core_checked_fitted_bound']))
    record('P34 includes exact normalization, path recurrence and uniform contraction',
           all('Komorebi.LSM.Filtering.'+n in by_name for n in ['prediction_error','fitted_mass_positive','normalized_residual','normalized_error_checked','normalized_error_margin','filtering_step','filtering_path','filtering_uniform']))
    record('Subspace coordinate inverse is constructed under the explicit gap',
           all('Komorebi.LSM.SubspaceCoordinates.'+n in by_name for n in ['coordinate_lower','coordinate_injective','coordinateEquiv','coordinate_inverse_bound']))
'''+s[pos:]
(r/'scripts/check_metadata.py').write_text(s)
(r/'lakefile.toml').write_text(old['lakefile.toml'].decode().replace('0.10.0','0.11.0'))
print(json.dumps(c,indent=2))
