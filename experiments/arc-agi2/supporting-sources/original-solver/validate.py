"""Release checks and fresh-process replay. Author: Komorebi P."""
from __future__ import annotations
import argparse,ast,copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
import engine,solver
import storage

def validate(root):
    root=Path(root).resolve()
    engine.initialize()
    tests=unittest.defaultTestLoader.discover(str(root/'tests'))
    runner=unittest.TextTestRunner(verbosity=1).run(tests)
    if not runner.wasSuccessful():raise AssertionError('test failures')
    challenges=engine.read(root/'data/challenges.json');census=storage.read(root/'results/census.json')
    frozen=engine.read(root/f'results/{solver.PRIMARY}.json');engine.verify(frozen)
    seal=engine.read(root/'results/pre_score_source_freeze.json');engine.verify(seal)
    if seal['engine_hash']!=engine.code_hash() or seal['prediction_hash']!=solver.prediction_hash() or seal['bank_hash']!=engine.bank_hash():
        raise AssertionError('pre-score source mismatch')
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/'fresh.json'
        subprocess.run([sys.executable,str(root/'dispatch_cached.py'),'--challenges',str(root/'data/challenges.json'),
            '--census',str(root/'results/census.json'),'--policy',solver.PRIMARY,'--output',str(out)],check=True)
        if out.read_bytes()!=(root/f'results/{solver.PRIMARY}.json').read_bytes():raise AssertionError('fresh dispatch differed')
    renamed={};records={};mapping={}
    for i,(key,task) in enumerate(reversed(sorted(challenges.items()))):
        name=f'anonymous_{i:04d}';mapping[key]=name;renamed[name]=task;records[name]=census['records'][key]
    changed=copy.deepcopy(census);changed['records']=records;changed['challenges_hash']=engine.contract.digest(renamed);changed=engine.seal(changed)
    alternate=solver.dispatch(renamed,changed,solver.PRIMARY)
    if any(frozen['submission'][k]!=alternate['submission'][name] for k,name in mapping.items()):
        raise AssertionError('task IDs or corpus order affected dispatch')
    identifiers=set(challenges);hits=[]
    paths=list((root/'vendor').rglob('*.py'))+list((root/'entrants13').glob('*.py'))+list((root/'entrants').glob('*.py'))
    paths += [root/n for n in ('engine.py','legacy.py','action_adapter.py','solver.py','repairs.py','memo.py',
                              'run_scan.py','geometry_repair.py','repair_entrants/micro_schemas_v2.py',
                              'storage.py','dispatch_cached.py')]
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in identifiers:
                hits.append({'file':str(path.relative_to(root)),'line':node.lineno,'task_id':node.value})
    if hits:raise AssertionError('literal task ID in runtime code')
    evaluation=engine.read(root/'results/evaluation.json');engine.verify(evaluation)
    replay=engine.read(root/'results/compiler_replay_validation.json');engine.verify(replay)
    if replay['engine_hash']!=engine.code_hash() or replay['bank_hash']!=engine.bank_hash():
        raise AssertionError('sampled compiler replay source mismatch')
    sampled=engine.read(root/'results/live_replay_sample.json');engine.verify(sampled)
    spawn=engine.read(root/'results/spawn_validation.json');engine.verify(spawn)
    spawned=engine.read(root/'results/spawn_replay_sample.json');engine.verify(spawned)
    if spawn['engine_hash']!=engine.code_hash() or spawn['launcher_sha256']!=engine.contract.sha256_file(root/'run_scan.py'):
        raise AssertionError('fresh-worker launcher binding mismatch')
    prediction_freeze=engine.read(root/'results/pre_score_prediction_freeze.json');engine.verify(prediction_freeze)
    if prediction_freeze['worker_startup_validation_hash']!=spawn['content_hash']:
        raise AssertionError('worker startup receipt changed after prediction freeze')
    representation=engine.read(root/'results/census_storage.json');engine.verify(representation)
    if representation['content_hash']!=prediction_freeze['census_storage_receipt_hash'] or representation['census_content_hash']!=census['content_hash']:
        raise AssertionError('compressed census receipt changed after freeze')
    if representation['storage_helper_sha256']!=engine.contract.sha256_file(root/'storage.py') or representation['cached_dispatch_helper_sha256']!=engine.contract.sha256_file(root/'dispatch_cached.py'):
        raise AssertionError('compressed census helpers changed after freeze')
    if spawned!=sampled or not spawn['sample_records_exact']:
        raise AssertionError('fresh-worker startup changed sampled compiler results')
    for check in replay['checks']:
        key=check['task_id']
        if census['records'][key]!=sampled['records'][key] or census['records'][key]['content_hash']!=check['record_hash']:
            raise AssertionError('sampled live compiler record differed from final census')
    repair=engine.read(root/'repair_results/census.json');engine.verify(repair)
    repair_freeze=engine.read(root/'repair_results/source_freeze.json');engine.verify(repair_freeze)
    if not repair['validation_passed'] or repair['source_freeze_hash']!=repair_freeze['content_hash']:
        raise AssertionError('geometry repair did not pass paired validation')
    if repair_freeze['repair_sha256']!=engine.contract.sha256_file(root/'repair_entrants/micro_schemas_v2.py'):
        raise AssertionError('geometry repair source changed')
    if evaluation['frontier_unchanged']['sha256']!=engine.contract.sha256_file(root/'evidence/g47.json'):
        raise AssertionError('frontier changed')
    result=engine.seal({'schema':'komorebi.block17.validation.v1','author':'Komorebi P.',
        'unit_tests_run':runner.testsRun,'unit_tests_passed':runner.testsRun-len(runner.failures)-len(runner.errors),
        'source_authentication':True,'fresh_process_dispatch_byte_identical':True,
        'fresh_process_full_bank_compiler_samples':len(replay['checks']),
        'fresh_process_compiler_sample_records_match_final_census':True,
        'fresh_worker_startup_sample_census_identical':True,
        'fresh_worker_launcher_sha256':spawn['launcher_sha256'],
        'compressed_census_receipt_verified':True,
        'geometry_repair_original_errors':repair['original_errors'],'geometry_repair_errors':repair['repair_errors'],
        'geometry_repair_successful_candidate_preservation':repair['preservation_failures']==0,
        'task_id_and_corpus_order_invariance':True,'literal_task_id_runtime_hits':hits,
        'prediction_hash':solver.prediction_hash(),'bank_hash':engine.bank_hash(),'census_hash':census['content_hash'],
        'g47_sha256':evaluation['frontier_unchanged']['sha256'],
        'limit':'Fresh dispatch replay plus sampled compiler reruns; reused 48-source census was live-replayed in Block 16.'})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.root);engine.write(a.output,r);print(json.dumps(r,indent=2))
