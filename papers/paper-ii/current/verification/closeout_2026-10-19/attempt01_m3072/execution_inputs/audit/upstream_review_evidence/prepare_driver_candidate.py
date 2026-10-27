from pathlib import Path
import difflib
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent;current=root/'paper2_work/tools/final_audit/verify_release.py';s=current.read_text()
s=s.replace('    reviewed_helpers=[]\n','    reviewed_helpers=[]\n    reviewed_duplicates=[]\n')
needle="            report['reviewed_runtime_helpers_sha256']=sha(audit/'reviewed_runtime_helpers.json')\n"
addition="""            duplicate_review=json.loads((audit/'reviewed_upstream_duplicates.json').read_text())
            if duplicate_review['status']!='REVIEWED':raise ValueError('Upstream duplicate requires independent root review')
            reviewed_duplicates=duplicate_review['theorems']
            if len(reviewed_duplicates)!=1 or reviewed_duplicates[0]['name']!='Submodule.factor.eq_1':
                raise ValueError('Unexpected upstream duplicate review set')
            for row in duplicate_review['source_files']:
                base=root if row['origin']=='project' else kit/'workspace/.lake/packages/mathlib'
                if sha(base/row['path'])!=row['sha256']:raise ValueError('Upstream duplicate review source changed')
            for row in duplicate_review['runtime_cache_files']:
                if sha(kit/row['path'])!=row['sha256']:raise ValueError('Reviewed upstream compiled cache changed')
            for row in duplicate_review['evidence']:
                if sha(audit/row['path'])!=row['sha256']:raise ValueError('Upstream duplicate review evidence changed')
            report['reviewed_upstream_duplicates_sha256']=sha(audit/'reviewed_upstream_duplicates.json')
"""
assert needle in s;s=s.replace(needle,needle+addition)
s=s.replace("extra={'KOMOREBI_REPLAY_MODULES':','.join(modules),'KOMOREBI_REPLAY_CORRUPT':'0'})","extra={'KOMOREBI_REPLAY_MODULES':','.join(modules),'KOMOREBI_REPLAY_CORRUPT':'0','KOMOREBI_REPLAY_DUPLICATE_CORRUPT':'0'})")
needle="            replayed=[json.loads(line[len('REPLAY_CHECKED '):]) for line in text.splitlines() if line.startswith('REPLAY_CHECKED ')]\n"
addition="""            duplicates=[json.loads(line[len('REPLAY_UPSTREAM_DUPLICATE_RECHECKED '):]) for line in text.splitlines() if line.startswith('REPLAY_UPSTREAM_DUPLICATE_RECHECKED ')]
            if len(duplicates)!=len(reviewed_duplicates) or {r['name'] for r in duplicates}!={r['name'] for r in reviewed_duplicates}:
                raise ValueError('Rechecked upstream duplicate set differs from review')
            owned_names={r['name'] for r in owned}
            for expected in reviewed_duplicates:
                actual=next(r for r in duplicates if r['name']==expected['name'])
                if actual['name'] in owned_names:raise ValueError('Cannot classify source-owned declaration as upstream duplicate')
                for key in ['name','serialized_in','upstream_owner','type_expr','value_expr','level_params','all']:
                    if actual[key]!=expected[key]:raise ValueError('Reviewed upstream duplicate identity changed: '+key)
                if not actual['fresh_kernel_body_check']:raise ValueError('Upstream duplicate lacks independent kernel body check')
            (out/'upstream_duplicate_body_rechecks.json').write_text(json.dumps(duplicates,indent=2)+'\\n')
            corrupt_duplicate=lean('kernel_duplicate_body_corrupt_control',audit/'ReplayClosure.lean',reject=True,
                pattern=r'kernel.*type mismatch|declaration type mismatch|type mismatch',
                extra={'KOMOREBI_REPLAY_MODULES':','.join(modules),'KOMOREBI_REPLAY_CORRUPT':'0','KOMOREBI_REPLAY_DUPLICATE_CORRUPT':'1'})
            if 'REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED' not in corrupt_duplicate or 'REPLAY_UPSTREAM_DUPLICATE_RECHECKED' in corrupt_duplicate or 'REPLAY_CLOSURE_PASS' in corrupt_duplicate:
                raise ValueError('Corrupted upstream duplicate did not reach fresh kernel body rejection')
            report['negative_controls']=9
            report['upstream_duplicate_body_recheck_count']=len(duplicates)
            report['upstream_duplicate_body_recheck_names']=[r['name'] for r in duplicates]
            report['upstream_duplicate_body_recheck_record']='upstream_duplicate_body_rechecks.json'
"""
assert needle in s;s=s.replace(needle,addition+needle)
(out/'verify_release_candidate.py').write_text(s)
(out/'verify_release.diff').write_text(''.join(difflib.unified_diff(current.read_text().splitlines(True),s.splitlines(True),fromfile='current/verify_release.py',tofile='proposed/verify_release.py')))
