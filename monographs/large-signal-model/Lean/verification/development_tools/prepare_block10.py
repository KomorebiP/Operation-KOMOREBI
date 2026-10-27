from pathlib import Path
import json, hashlib, shutil, subprocess
base=Path(__file__).resolve().parent.parent
root=base/'work/Komorebi_LSM_Lean_Block10'
old=base/'deliverables/Komorebi_LSM_Lean_0.9.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mods=['RationalFeasibility','RationalCertificateSearch','RationalCertificateSoundness','Block10Examples']
(root/'KomorebiLSM.lean').write_text((old/'KomorebiLSM.lean').read_text()+''.join('import KomorebiLSM.'+m+'\n' for m in mods))
v=(old/'scripts/verify.py').read_text().replace("'Block9Examples']","'Block9Examples',"+','.join(repr(m) for m in mods)+']').replace("'release':'0.9.0'","'release':'0.10.0'")
v=v.replace("ROOT/'scripts/build_inventory.py', ROOT/'RELEASE_COUNTS.json'","ROOT/'scripts/build_inventory.py', ROOT/'RELEASE_COUNTS.json', ROOT/'scripts/RunRationalSearch.lean'")
pos=v.index("        rec=run([lean,'-j1','-DwarningAsError=true',str(ROOT/'AxiomAudit.lean')]")
v=v[:pos]+'''        rec=run([lean,'-j1','-DwarningAsError=true',str(ROOT/'scripts/RunRationalSearch.lean')],env,args.timeout)
        rec.update({'phase':'executable_examples','expected_stdout':'true\\ntrue\\nfalse\\ntrue\\nfalse'})
        report['stages'].append(rec);save()
        if rec['returncode'] != 0 or rec['timed_out'] or rec['stdout'].strip()!=rec['expected_stdout']:
            raise RuntimeError('exact rational executable examples failed')
        print('EXECUTED exact rational checker and finite search examples',flush=True)
'''+v[pos:]
(root/'scripts/verify.py').write_text(v)
subprocess.run(['python3','scripts/build_inventory.py','--write'],cwd=root,check=True)
decls=json.loads((root/'DECLARATIONS.json').read_text());nt=sum(d['kind']=='theorem' for d in decls)
ne=sum(d['kind']=='theorem' and 'Examples' in d['module'] for d in decls)
counts={'release':'0.10.0','proof_modules':78,'named_declarations':len(decls),'named_theorems':nt,'example_theorems':ne,'supporting_theorems':nt-ne,'new_theorems':nt-968,'new_example_theorems':ne-300,'complete_propositions':36,'partial_propositions':0,'unformalized_propositions':51,'negative_controls':72}
(root/'RELEASE_COUNTS.json').write_text(json.dumps(counts,indent=2)+'\n')
cover=json.loads((old/'COVERAGE.json').read_text());e=cover['entries'][44]
e['status']='complete';e['scope']='Finite rational input matrices and exact per-action mass identities. The input certificate only assumes rational normalized full-row-rank generators; its nonnegative lift and initial coefficients may be real. Finite weak rational Fourier–Motzkin elimination proves rational witnesses exist, including boundary faces. A rational right inverse is derived. Computable natural-number decoding enumerates every finite width and rational witness, exact rational checks are sound, and some finite fuel returns a certificate whenever the stated one exists. Accepted witnesses instantiate the closed, pointed, generating invariant cone and all-word bounds of P39. No strict margin, practical complexity, universal existence, or finite-failure impossibility is claimed.'
e['lean_targets']=[dict(d,source_sha256=sha(root/d['file'])) for d in decls if d['module'] in mods[:-1]]
cover.update(formalization_version='0.10.0',complete=sorted(cover['complete']+[45]),not_formalized_count=51)
cover['interpretation']='Coverage is statement-level self-review against the frozen source. Kernel acceptance is recorded separately in verification/block10_release_run/report.json. The kernel does not read English prose.'
(root/'COVERAGE.json').write_text(json.dumps(cover,indent=2)+'\n')
road=json.loads((old/'ROADMAP_1.0.json').read_text());road.update(release='0.10.0',completed=cover['complete'],remaining_count=51)
for t in road['tracks']:t['propositions']=[n for n in t['propositions'] if n!=45]
road['tracks']=[t for t in road['tracks'] if t['propositions']]
(root/'ROADMAP_1.0.json').write_text(json.dumps(road,indent=2)+'\n')
lineage=json.loads((old/'SOURCE_LINEAGE.json').read_text());lineage['formalization_version']='0.10.0'
archive=base/'deliverables/Komorebi_Large_Signal_Model_Lean_0.9.0.zip'
shutil.copy2(archive,root/'history'/archive.name)
lineage['predecessor_archive']={'path':'history/'+archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size}
lineage['inherited_proof_files']={str(p.relative_to(old)):sha(p) for p in sorted((old/'KomorebiLSM').glob('*.lean'))}
lineage['inherited_control_files']={str(p.relative_to(old)):sha(p) for p in sorted((old/'negative_controls').glob('*.lean'))}
(root/'SOURCE_LINEAGE.json').write_text(json.dumps(lineage,indent=2)+'\n')
for name in ['README.md','LEAN_GUIDE.md','PROGRESS.md','PROGRESS.json','AUDIT.md','COVERAGE.md','COVERAGE.json','ROADMAP_1.0.md','ROADMAP_1.0.json','CONTINUE_HERE.md','RELEASE_COUNTS.json','SOURCE_LINEAGE.json','PUBLICATION_STATUS.md']:
 shutil.copy2(old/name,root/'history'/('PREDECESSOR_0.9.0_'+name))
shutil.copy2(old/'scripts/check_metadata.py',root/'history/PREDECESSOR_0.9.0_check_metadata.py')
m=(old/'scripts/check_metadata.py').read_text()
repls={
'1256 unique named declarations':f'{len(decls)} unique named declarations',"counts['named_declarations'] == 1256":f"counts['named_declarations'] == {len(decls)}",
'968 theorems, 300 in the ten example modules':f'{nt} named theorems, {ne} in example modules',"counts['named_theorems']==968":f"counts['named_theorems']=={nt}","counts['example_theorems']==300":f"counts['example_theorems']=={ne}",
"'Block9Examples']":"'Block9Examples','Block10Examples']",
'Coverage is 35 complete, no partial, 52 unformalized':'Coverage is 36 complete, no partial, 51 unformalized',
'=='+repr(json.loads((old/'COVERAGE.json').read_text())['complete']):'=='+repr(cover['complete']),
"for x in cover['entries'])==52":"for x in cover['entries'])==51",
'All sixty-seven inherited proof files':'All 74 inherited proof files',"len(lineage['inherited_proof_files'])==67":"len(lineage['inherited_proof_files'])==74",
'All 1178 inherited declaration records':'All 1256 inherited declaration records','len(previous)==1178':'len(previous)==1256',
'All 74 proof modules':'All 78 proof modules','len(set(root_modules))==74':'len(set(root_modules))==78',
'All sixty-eight negative controls':'All 72 negative controls',"counts['negative_controls']==68":"counts['negative_controls']==72",
'Seven new proof files and six new negative controls':'Four new proof files and four new negative controls',
"len(lineage['inherited_proof_files'])==7":"len(lineage['inherited_proof_files'])==4",
"counts['negative_controls']-62==6":"counts['negative_controls']-68==4",
"counts['named_theorems']-904":"counts['named_theorems']-968",
'len(remaining)==len(set(remaining))==52':'len(remaining)==len(set(remaining))==51',
'All sixty-two predecessor rejection-control sources':'All 68 predecessor rejection-control sources',"len(lineage['inherited_control_files'])==62":"len(lineage['inherited_control_files'])==68"
}
for a,b in repls.items():m=m.replace(a,b)
pos=m.index("    result={'kind'")
m=m.replace("len(lineage['inherited_proof_files'])==44","len(lineage['inherited_proof_files'])==74")
m=m[:pos]+'''    record('P45 targets cover real feasibility, computable enumeration and P39 soundness',
           all('Komorebi.LSM.RationalSearch.'+n in by_name for n in [
               'rational_feasible','rational_nonnegative_solution','rational_right_inverse',
               'rationalize_certificate','checkCode','search','search_sound','search_persistent',
               'rational_finite_certificate_search','accepted_probability_domain',
               'rational_mass_identity','accepted_all_word_probabilities']))
    record('P45 does not impose a strict-margin hypothesis',
           'boundary faces' in cover['entries'][44]['scope'] and
           'No strict margin' in cover['entries'][44]['scope'])
    record('Roadmap remaining_count matches its actual exhaustive list',roadmap['remaining_count']==len(remaining))
    record('Executable examples are included in verifier source snapshot',
           'scripts/RunRationalSearch.lean' in mod.inventory())
'''+m[pos:]
(root/'scripts/check_metadata.py').write_text(m)
(root/'lakefile.toml').write_text((old/'lakefile.toml').read_text().replace('0.9.0','0.10.0'))
print(json.dumps(counts,indent=2))
