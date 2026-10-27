"""Freeze all policy outputs, then open the independent evaluator.
Author: Komorebi P.
"""
from pathlib import Path
import engine,solver,evaluate
import geometry_repair
import storage

def main():
    root=Path(__file__).resolve().parent
    source=engine.read(root/'results/pre_score_source_freeze.json');engine.verify(source)
    assert source['engine_hash']==engine.code_hash() and source['prediction_hash']==solver.prediction_hash()
    startup=engine.read(root/'results/spawn_validation.json');engine.verify(startup)
    assert startup['engine_hash']==engine.code_hash()
    assert startup['launcher_sha256']==engine.contract.sha256_file(root/'run_scan.py')
    tasks=engine.read(root/'data/challenges.json')
    old=storage.read(root/'results/legacy_census.json');prior=engine.read(root/'evidence/block16_census.json')
    cache_binding=engine.read(root/'results/prior_cache_binding.json');engine.verify(cache_binding)
    assert prior['content_hash']==cache_binding['census_content_hash']
    assert engine.contract.sha256_file(root/'evidence/block16_census.json')==cache_binding['census_file_sha256']
    census=engine.merge(tasks,old,prior)
    del old,prior
    representation=storage.write_gzip(root/'results/census.json.gz',census)
    representation.update({'author':'Komorebi P.','census_content_hash':census['content_hash'],
        'storage_helper_sha256':engine.contract.sha256_file(root/'storage.py'),
        'cached_dispatch_helper_sha256':engine.contract.sha256_file(root/'dispatch_cached.py')})
    representation=engine.seal(representation)
    engine.write(root/'results/census_storage.json',representation)
    print('Combined census stored losslessly.',flush=True)
    predictions={}
    for name in solver.POLICIES:
        r=solver.dispatch(tasks,census,name)
        engine.write(root/f'results/{name}.json',r);predictions[name]=r['content_hash']
        print('frozen',name,r['content_hash'],flush=True)
    engine.write(root/'results/pre_score_prediction_freeze.json',engine.seal({'author':'Komorebi P.',
        'prediction_hash':solver.prediction_hash(),'source_freeze_hash':source['content_hash'],
        'prior_cache_binding_hash':cache_binding['content_hash'],
        'worker_startup_validation_hash':startup['content_hash'],'worker_launcher_sha256':startup['launcher_sha256'],
        'census_storage_receipt_hash':representation['content_hash'],
        'census_hash':census['content_hash'],'predictions':predictions,'labels_opened_in_this_run':False}))
    geometry_repair.freeze_predictions(tasks,census,engine.read(root/f'results/{solver.PRIMARY}.json'))
    geometry_repair.freeze_predictions(tasks,census,engine.read(root/'results/typed_supported.json'),'supported_')
    del census,r
    report=evaluate.evaluate(root);engine.write(root/'results/evaluation.json',report)
    for name,r in report['policies'].items():
        s=r['score'];print(name,s['pass1_exact_outputs'],s['pass2_exact_outputs'],s['whole_tasks'],
                          'gain/loss',len(r['gains']),len(r['losses']),flush=True)
    repaired=geometry_repair.score_frozen()
    print('geometry_repair',repaired['score']['pass2_exact_outputs'],repaired['score']['whole_tasks'],
          'gain/loss',len(repaired['gains']),len(repaired['losses']),flush=True)
    repaired_supported=geometry_repair.score_frozen('supported_')
    print('geometry_repair_supported',repaired_supported['score']['pass2_exact_outputs'],repaired_supported['score']['whole_tasks'],
          'gain/loss',len(repaired_supported['gains']),len(repaired_supported['losses']),flush=True)

if __name__=='__main__':main()
