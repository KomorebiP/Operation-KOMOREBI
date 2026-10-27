from pathlib import Path
root=Path(__file__).resolve().parents[3];p=root/'release_work/runtime/release_audit/verify_release.py';s=p.read_text()
s=s.replace("'Replay uses Lean own kernel, not an independent verifier.'", "'Logical checks use Lean own kernel, not an independent verifier. Exact upstream theorem duplicates are checked under fresh audit names and counted separately from new-name replay.'")
start=s.index("        text=lean('replay_whole_closure'")
end=s.index("        for row in report['source_files']:",start)
s=s[:start]+'''        text=lean('replay_whole_closure',audit/'ReplayClosure.lean',pattern=r'REPLAY_CLOSURE_PASS MODULES '+str(len(mods))+r' CONSTANTS \\d+',extra={'KOMOREBI_REPLAY_MODULES':','.join(mods),'KOMOREBI_REPLAY_CORRUPT':'0','KOMOREBI_REPLAY_DUPLICATE_CORRUPT':'0'})
        replayed=[json.loads(x[len('REPLAY_CHECKED '):]) for x in text.splitlines() if x.startswith('REPLAY_CHECKED ')]
        rechecked=[json.loads(x[len('REPLAY_UPSTREAM_DUPLICATE_RECHECKED '):]) for x in text.splitlines() if x.startswith('REPLAY_UPSTREAM_DUPLICATE_RECHECKED ')]
        runtime=[json.loads(x[len('REPLAY_RUNTIME_ONLY '):]) for x in text.splitlines() if x.startswith('REPLAY_RUNTIME_ONLY ')]
        expected={x['name'] for x in owned if not x['runtime_only']};actual={x['name'] for x in replayed};duplicate_names={x['name'] for x in rechecked}
        assert len(actual)==len(replayed) and len(duplicate_names)==len(rechecked) and not actual & duplicate_names
        assert actual|duplicate_names==expected,{'missing':sorted(expected-(actual|duplicate_names)),'extra':sorted((actual|duplicate_names)-expected)}
        for row in rechecked:
            assert row['name']=='ContinuousLinearMap.codRestrict.congr_simp'
            assert row['upstream_owner']=='Mathlib.Analysis.LocallyConvex.HahnBanach'
            assert row['audit_name']==row['name']+'._paperIReplayBody'
            assert all(row[k] is True for k in ['same_name','same_type','same_level_params','same_all','same_value','fresh_kernel_body_check'])
        assert {x['name'] for x in runtime}=={x['name'] for x in owned if x['runtime_only']}
        assert 'REPLAY_UPSTREAM_ONLY_PASS' in text
        summary=re.search(r'REPLAY_CLOSURE_PASS MODULES (\\d+) CONSTANTS (\\d+) NEW_NAME_REPLAYS (\\d+) DUPLICATE_BODY_RECHECKS (\\d+)',text)
        assert summary and tuple(map(int,summary.groups()))==(len(mods),len(expected),len(replayed),len(rechecked))
        for name,items in [('replayed_constants',replayed),('upstream_duplicate_body_rechecks',rechecked),('runtime_only_constants',runtime)]:
            (out/(name+'.json')).write_text(json.dumps(items,indent=2)+'\\n')
        negative_count=11
        if rechecked:
            bad=lean('kernel_duplicate_body_corrupt_control',audit/'ReplayClosure.lean',reject=True,pattern=r'kernel.*type mismatch|declaration type mismatch|type mismatch',extra={'KOMOREBI_REPLAY_MODULES':','.join(mods),'KOMOREBI_REPLAY_CORRUPT':'0','KOMOREBI_REPLAY_DUPLICATE_CORRUPT':'1'})
            assert 'REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED' in bad and 'REPLAY_CLOSURE_PASS' not in bad
            assert 'REPLAY_UPSTREAM_DUPLICATE_RECHECKED' not in bad
            negative_count+=1
        report.update(replay_exact_name_match=True,replay_starting_environment_excludes_project_modules=True,logical_checked_count=len(expected),replay_logical_constant_count=len(replayed),upstream_duplicate_body_recheck_count=len(rechecked),upstream_duplicate_body_recheck_names=sorted(duplicate_names),upstream_duplicate_body_recheck_record='upstream_duplicate_body_rechecks.json',replay_runtime_only_count=len(runtime),replay_modules=mods,negative_controls=negative_count)
''' +s[end:]
(root/'release_work/runtime/overlap_review/verify_release_candidate.py').write_text(s)
