"""Apply the separately frozen geometry repair only after its ancestor fails.
Author: Komorebi P.
"""
from pathlib import Path
import copy
import engine,solver,evaluate
import storage
ROOT=Path(__file__).resolve().parent

def predict(tasks,census,parent,repair):
    for x in (census,parent,repair):engine.verify(x)
    if not repair['validation_passed']:raise ValueError('repair validation failed')
    if parent['policy'] not in ('typed_recent','typed_supported'):raise ValueError('unsupported repair parent policy')
    freeze=engine.read(ROOT/'repair_results/source_freeze.json');engine.verify(freeze)
    if repair['source_freeze_hash']!=freeze['content_hash']:raise ValueError('repair source binding mismatch')
    if engine.contract.sha256_file(ROOT/'repair_entrants/micro_schemas_v2.py')!=freeze['repair_sha256']:
        raise ValueError('repair source changed')
    if repair['challenges_hash']!=census['challenges_hash']:raise ValueError('repair challenge binding mismatch')
    result=copy.deepcopy(parent);applied=[]
    for key,r in sorted(repair['records'].items()):
        engine.verify(r)
        old=census['records'][key]
        if r['task_semantic_hash']!=old['task_semantic_hash']:raise ValueError('repair task binding mismatch')
        if r['original_receipt']!=old['receipts']['micro_schemas']:raise ValueError('paired reference receipt mismatch')
        if r['original_receipt']['status']=='ok' or not r['candidates']:continue
        if not r['original_receipt'].get('error','').startswith('IndexError:'):
            raise ValueError('unclassified ancestor failure')
        augmented=engine.seal({**old,'candidates':sorted(old['candidates']+r['candidates'],key=lambda c:c['candidate_hash']),
                             'receipts':{**old['receipts'],'micro_schemas_v2':r['repair_receipt']}})
        mini=engine.seal({'scope':'all_banks','records':{key:augmented},
             'challenges_hash':engine.contract.digest({key:engine.sanitize(tasks[key])}),
             'code_hash':engine.code_hash(),'bank_hash':engine.bank_hash()})
        one=solver.dispatch({key:tasks[key]},mini,parent['policy'])
        result['decisions'][key]=one['decisions'][key];result['submission'][key]=one['submission'][key]
        applied.append(key)
    result.update({'schema':'komorebi.block17.geometry_repair_dispatch.v1','variant':'geometry_domain_repair',
        'parent_dispatch_hash':parent['content_hash'],'repair_census_hash':repair['content_hash'],
        'repair_source_freeze_hash':freeze['content_hash'],'repair_driver_hash':engine.contract.sha256_file(Path(__file__)),
        'repair_applied_tasks':applied,'routing':'repair only after the ancestor reports IndexError; no label-conditioned activation'})
    return engine.seal(result)

def freeze_predictions(tasks,census,parent,prefix=''):
    repair=engine.read(ROOT/'repair_results/census.json')
    result=predict(tasks,census,parent,repair)
    engine.write(ROOT/f'repair_results/{prefix}dispatch.json',result)
    engine.write(ROOT/f'repair_results/{prefix}prediction_freeze.json',engine.seal({'author':'Komorebi P.',
        'prediction_hash':result['content_hash'],'parent_dispatch_hash':parent['content_hash'],
        'repair_census_hash':repair['content_hash'],'driver_hash':result['repair_driver_hash'],
        'label_access_before_freeze':'demonstrations_only'}))
    return result

def score_frozen(prefix=''):
    frozen=engine.read(ROOT/f'repair_results/{prefix}dispatch.json');binding=engine.read(ROOT/f'repair_results/{prefix}prediction_freeze.json')
    engine.verify(frozen);engine.verify(binding)
    if engine.contract.sha256_file(Path(__file__))!=binding['driver_hash']:raise ValueError('repair driver changed after freeze')
    if frozen['content_hash']!=binding['prediction_hash']:raise ValueError('repair prediction freeze mismatch')
    parent=engine.read(ROOT/f"results/{frozen['policy']}.json")
    if parent['content_hash']!=binding['parent_dispatch_hash']:raise ValueError('repair parent mismatch')
    solutions=engine.read(ROOT/'evidence/solutions.json');g47=engine.read(ROOT/'evidence/g47.json')
    result=evaluate.comparison(parent['submission'],frozen['submission'],solutions)
    g=set(evaluate.score(g47,solutions)['exact_keys']);p=set(result['score']['exact_keys'])
    result.update({'author':'Komorebi P.','variant':'geometry_domain_repair','frozen_prediction_hash':frozen['content_hash'],
                   'repair_applied_tasks':frozen['repair_applied_tasks'],'g47_missing_outputs':sorted(g-p),
                   'gains_beyond_g47':sorted(p-g),'claim_boundary':'Unfiltered training comparison; no exact-only promotion.'})
    result=engine.seal(result);engine.write(ROOT/f'repair_results/{prefix}evaluation.json',result);return result

if __name__=='__main__':
    tasks=engine.read(ROOT/'data/challenges.json');census=storage.read(ROOT/'results/census.json')
    parent=engine.read(ROOT/f'results/{solver.PRIMARY}.json')
    freeze_predictions(tasks,census,parent);r=score_frozen();print(r['score']['pass2_exact_outputs'],len(r['gains']),len(r['losses']))
