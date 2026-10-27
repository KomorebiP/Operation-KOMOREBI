from pathlib import Path
r=Path('/mnt/data/Komorebi_Paper_I_Completion_Block06_v0.6.0_2026-10-11')
s=(r/'predecessor/scripts/verify_block05.py').read_text()
s=s.replace('Block 05','Block 06').replace('Block05','Block06').replace('block05','block06').replace('BLOCK05','BLOCK06').replace('0.5.0','0.6.0')
s=s.replace('Four new production modules','Five new production modules').replace('All 37 production','All 42 production').replace("33 source/object pairs",'37 source/object pairs').replace('The 33 predecessor','The 37 predecessor')
s=s.replace("newmods=['PaperICompletion5.LinearPrimaryEigenspace','PaperICompletion5.GeometricSeedFormula','PaperICompletion5.CyclicGeometricCriterion','PaperICompletion5']", "newmods=['PaperICompletion6.ScalarExtension','PaperICompletion6.PrimaryCyclicCriterion','PaperICompletion6.OneInvariantFactor','PaperICompletion6.SixWayCyclicCriterion','PaperICompletion6']")
a=s.index("        for s in oldtop['stages']:")
b=s.index("        report['runtime_files_authenticated']",a)
s=s[:a]+'''        accepted=oldtop['accepted_run']
        assert sha(pred/accepted['path'])==accepted['sha256']
        report['predecessor_verification_sha256']=sha(pred/'VERIFICATION.json')
        source_rows=[]
        stage=(pred/accepted['path']).parent
        b=json.loads((pred/accepted['path']).read_text());assert b['status']=='PASS'
        for row in b['source_files']:
            source=pred/row['source'];oldobj=stage/row['object']
            assert sha(source)==row['source_sha256'] and sha(oldobj)==row['object_sha256']
            source_policy(source)
            rel=Path(*row['module'].split('.'));target=(inherited/rel).with_suffix('.olean')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(oldobj,target)
            snap=(out/'source_snapshots'/rel).with_suffix('.lean');snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
            source_rows.append({'module':row['module'],'source':str(source.relative_to(root)),
                'source_sha256':sha(source),'source_lines':len(source.read_text().splitlines()),
                'object':str(target.relative_to(out)),'object_sha256':sha(target),'origin':'authenticated_predecessor'})
        assert len(source_rows)==37 and len({row['module'] for row in source_rows})==37
        report['source_files']=source_rows;report['predecessor_module_pairs_authenticated']=37;save()
        bindings=list(pred.rglob('runtime_bindings.json'));assert len(bindings)==1
        binding=json.loads(bindings[0].read_text())
        for row in binding['files']:assert sha(kit/row['path'])==row['sha256'],row['path']
''' +s[b:]
a=s.index("        previous=set(re.findall")
b=s.index("        names=sorted",a)
s=s[:a]+'''        previous=set(re.findall(r"^#check\\s+([\\w.']+)",
            (pred/'evidence/final_audit/DeclarationTypes.lean').read_text(),re.M))
        assert len(previous)==oldtop['resolved_public_or_coverage_names']
'''+s[b:]
s=s.replace("'import PaperICompletion5\\n'", "'import PaperICompletion6\\n'")
a=s.index('        # New mathematical boundary consumers')
b=s.index("        bnames=",a)
s=s[:a]+'''        # Only authenticated prior boundary objects are imported by the fresh consumer.
        old_manifest={x['path']:x for x in json.loads((pred/'MANIFEST_SHA256.json').read_text())['files']}
        report['inherited_boundary_objects']=[]
        for name in ['PrimaryBoundaryConsumers','IntrinsicBoundaryConsumers','GeometricBoundaryConsumers']:
            source=pred/'evidence/final_audit/test_objects'/(name+'.olean')
            rel=str(source.relative_to(pred));assert sha(source)==old_manifest[rel]['sha256']
            shutil.copy2(source,tobj/(name+'.olean'))
            report['inherited_boundary_objects'].append({'module':name,'sha256':sha(source)})
        tenv={'LEAN_PATH':os.pathsep.join([str(tobj),env['LEAN_PATH']])}
        test=root/'tests/ScalarExtensionBoundaryConsumers.lean'
        lean('scalar_extension_boundary_consumers',test,target=tobj/'ScalarExtensionBoundaryConsumers.olean',cwd=root/'tests',extra=tenv)
'''+s[b:]
s=s.replace('PaperIBlock05Tests.', 'PaperIBlock06Tests.') # original was already replaced Block05 =>Block06 earlier
s=s.replace('PaperIBlock06Tests.', 'PaperIBlock06Tests.')
s=s.replace("bp.write_text('import GeometricBoundaryConsumers\\n'", "bp.write_text('import ScalarExtensionBoundaryConsumers\\n'")
s=s.replace("report['boundary_object_sha256']=sha(tobj/'GeometricBoundaryConsumers.olean')", "report['boundary_object_sha256']=sha(tobj/'ScalarExtensionBoundaryConsumers.olean')")
a=s.index("        negatives=[")
b=s.index("        for name,pattern in negatives:",a)
s=s[:a]+'''        negatives=[('FalseEquality','unsolved goals|type mismatch|Tactic.*rfl.*failed'),
            ('Placeholder','declaration uses.*sorry'),('MissingAlgClosed','failed to synthesize'),
            ('MissingNonzero','failed to synthesize'),('WrongCompanionSign','type mismatch'),
            ('RepeatedChainAsCyclic','type mismatch'),('MissingFiniteDimensional','failed to synthesize')]
'''+s[b:]
s=s.replace('not only the four freshly compiled additions','not only the five freshly compiled additions')
s=s.replace("lean('replay_geometric_boundaries',root/'tests/ReplayExact.lean',pattern='REPLAY_EXACT_PASS GeometricBoundaryConsumers',extra={**tenv,'KOMOREBI_REPLAY_MODULE':'GeometricBoundaryConsumers'})", "lean('replay_scalar_extension_boundaries',root/'tests/ReplayExact.lean',pattern='REPLAY_EXACT_PASS ScalarExtensionBoundaryConsumers',extra={**tenv,'KOMOREBI_REPLAY_MODULE':'ScalarExtensionBoundaryConsumers'})")
(r/'scripts/verify_block06.py').write_text(s)
s=(r/'predecessor/scripts/run_block05.sh').read_text().replace('block05','block06')
(r/'scripts/run_block06.sh').write_text(s)
# Fixtures intentionally invalid; never part of production source closure.
neg={
'FalseEquality': 'import PaperICompletion6\nexample : (0 : ℕ) = 1 := by rfl\n',
'Placeholder':'import PaperICompletion6\nexample : True := by sorry\n',
'MissingAlgClosed':'''import ScalarExtensionBoundaryConsumers
open Komorebi.PaperICompletion6.ScalarExtension
example := hasCyclicVector_iff_extended_spectral_multiplicities_one ℚ PaperIBlock04Tests.squaredOperator
''',
'MissingNonzero':'''import PaperICompletion6
open Komorebi.PaperICompletion6.SixWayCyclicCriterion
example := cyclic_six_way_algebraicClosure (0 : Module.End ℚ (Fin 0 → ℚ))
''',
'WrongCompanionSign':'''import ScalarExtensionBoundaryConsumers
open PaperIBlock03Tests PaperIBlock06Tests
open Komorebi.PaperICompletion6.OneInvariantFactor
example : companionMatrix quadratic ⟨0, by rw [quadratic_degree]; decide⟩
    ⟨1, by rw [quadratic_degree]; decide⟩ = (1 : ℚ) :=
  quadratic_companion_entries.2.2.1
''',
'RepeatedChainAsCyclic':'''import ScalarExtensionBoundaryConsumers
open Komorebi.SingleOperatorGraph
example : HasCyclicVector (PaperIBlock05Tests.repeatedJordanOperator.baseChange (AlgebraicClosure ℂ)) :=
  PaperIBlock06Tests.squared_extended_cyclic
''',
'MissingFiniteDimensional':'''import PaperICompletion6
open Komorebi.PaperICompletion6.ScalarExtension
example (T : Module.End ℚ (ℕ → ℚ)) := minpoly_baseChange (AlgebraicClosure ℚ) T
'''
}
for name,body in neg.items():(r/'tests/negative'/(name+'.lean')).write_text(body)
