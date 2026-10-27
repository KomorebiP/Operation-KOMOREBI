"""Solution-open evaluation, kept outside the prediction import graph.
Author: Komorebi P.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import solver
import storage
from engine import read,write,seal,verify,contract

def score(submission,solutions):
    if set(submission)!=set(solutions):raise ValueError('task sets differ')
    first=whole=0;keys=[]
    for key,targets in sorted(solutions.items()):
        rows=submission[key]
        if len(rows)!=len(targets):raise ValueError('test arity differs')
        flags=[]
        for i,(r,y) in enumerate(zip(rows,targets)):
            if set(r)!={'attempt_1','attempt_2'}:raise ValueError('malformed attempts')
            for grid in r.values():contract.validate_grid(grid)
            first+=r['attempt_1']==y
            exact=y in (r['attempt_1'],r['attempt_2']);flags.append(exact)
            if exact:keys.append(f'{key}:{i}')
        whole+=all(flags)
    n=sum(map(len,solutions.values()))
    return {'pass1_exact_outputs':first,'pass2_exact_outputs':len(keys),'whole_tasks':whole,
            'total_outputs':n,'total_tasks':len(solutions),'pass1_fraction':first/n,
            'pass2_fraction':len(keys)/n,'whole_task_fraction':whole/len(solutions),'exact_keys':keys}

def comparison(before,after,solutions):
    a,b=score(before,solutions),score(after,solutions)
    x,y=set(a['exact_keys']),set(b['exact_keys'])
    wrong=[];changes=[]
    for k,targets in solutions.items():
        for i,t in enumerate(targets):
            if before[k][i]!=after[k][i]:
                changes.append(f'{k}:{i}')
                if f'{k}:{i}' not in y:wrong.append(f'{k}:{i}')
    return {'score':b,'gains':sorted(y-x),'losses':sorted(x-y),'changed_outputs':sorted(changes),
            'changed_wrong_outputs_including_losses':sorted(wrong)}

def evaluate(root):
    root=Path(root)
    freeze=read(root/'results/pre_score_prediction_freeze.json');verify(freeze)
    if freeze['prediction_hash']!=solver.prediction_hash():raise ValueError('prediction code changed after freeze')
    solutions=read(root/'evidence/solutions.json');g47=read(root/'evidence/g47.json')
    census=storage.read(root/'results/census.json');verify(census)
    frozen={n:read(root/f'results/{n}.json') for n in solver.POLICIES}
    for n,r in frozen.items():
        verify(r)
        if r['content_hash']!=freeze['predictions'][n] or r['census_hash']!=census['content_hash']:
            raise ValueError('prediction freeze mismatch')
    base=frozen['base']['submission'];reference=score(g47,solutions)
    report={'author':'Komorebi P.','primary_policy':solver.PRIMARY,
            'claim_boundary':'Unfiltered runtime predictions on exposed public training data; no unseen-set estimate.',
            'reference_g47':reference,'policies':{},'census_hash':census['content_hash'],
            'prediction_freeze_hash':freeze['content_hash']}
    oracle_keys=[];oracle_whole=0;candidates=Counter();errors=[];tiers=Counter()
    for k,r in census['records'].items():
        flags=[]
        for c in r['candidates']:
            candidates[c['entrant']]+=1
            tiers[c.get('execution_replay',{}).get('status',c.get('verification','unspecified'))]+=1
        for name,receipt in r['receipts'].items():
            if receipt['status']!='ok':errors.append({'task_id':k,'entrant':name,**receipt})
        for i,target in enumerate(solutions[k]):
            outputs=[c['test_outputs'][i] for c in r['candidates']]+list(base[k][i].values())
            exact=target in outputs;flags.append(exact)
            if exact:oracle_keys.append(f'{k}:{i}')
        oracle_whole+=all(flags)
    report['runtime']={'candidates':sum(candidates.values()),'candidates_by_source':dict(candidates),
        'tasks_with_candidates':sum(bool(r['candidates']) for r in census['records'].values()),
        'verification_tiers':dict(tiers),'error_receipts':errors,'error_count':len(errors)}
    report['candidate_plus_live_base_oracle_diagnostic']={'exact_outputs':len(oracle_keys),
        'whole_tasks_any_behavior_per_output':oracle_whole,'exact_keys':oracle_keys}
    for name,r in frozen.items():
        result=comparison(base,r['submission'],solutions)
        result['activated_tasks']=sum(d['activated'] for d in r['decisions'].values())
        active_outputs=exact_candidate_outputs=attempts=exact_attempts=false_tasks=0
        for key,d in r['decisions'].items():
            task_active=task_hit=False
            for i,sources in enumerate(d['selected_sources']):
                choices=[r['submission'][key][i][f'attempt_{j+1}'] for j,source in enumerate(sources)
                         if not source.startswith('live_base_')]
                if not choices:continue
                task_active=True;active_outputs+=1
                hits=sum(grid==solutions[key][i] for grid in choices)
                attempts+=len(choices);exact_attempts+=hits
                exact_candidate_outputs+=bool(hits);task_hit|=bool(hits)
            false_tasks+=task_active and not task_hit
        result['candidate_only_selection']={
            'activated_outputs':active_outputs,'selected_candidate_attempts':attempts,
            'exact_candidate_attempts':exact_attempts,
            'candidate_attempt_precision':exact_attempts/attempts if attempts else None,
            'outputs_with_correct_candidate':exact_candidate_outputs,
            'candidate_output_conditional_accuracy':exact_candidate_outputs/active_outputs if active_outputs else None,
            'false_activation_tasks_no_correct_candidate':false_tasks,
            'false_activation_fraction_of_activated_tasks':false_tasks/result['activated_tasks'] if result['activated_tasks'] else None}
        result['tied_top_tasks']=sum(d['tied_at_top'] for d in r['decisions'].values())
        result['typed_vetoes']=[{'task_id':k,**w} for k,d in r['decisions'].items() for w in d['repairs'] if w['status']=='veto']
        x=set(result['score']['exact_keys']);g=set(reference['exact_keys'])
        result['g47_missing_outputs']=sorted(g-x);result['gains_beyond_g47']=sorted(x-g)
        result['available_correct_outputs_not_selected']=sorted(set(oracle_keys)-x)
        result['live_base_attempt1_changes']=sum(base[k][i]['attempt_1']!=z['attempt_1'] for k,rows in r['submission'].items() for i,z in enumerate(rows))
        report['policies'][name]=result
    report['typed_repair_ablation']=comparison(frozen['recent_control']['submission'],frozen['typed_recent']['submission'],solutions)
    report['trace_support_ablation']=comparison(frozen['typed_recent']['submission'],frozen['typed_supported']['submission'],solutions)
    report['frontier_unchanged']={'sha256':contract.sha256_file(root/'evidence/g47.json'),
        'outputs':reference['pass2_exact_outputs'],'whole_tasks':reference['whole_tasks']}
    return seal(report)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=evaluate(a.root);write(a.output,r)
    for n,v in r['policies'].items():
        s=v['score'];print(n,s['pass1_exact_outputs'],s['pass2_exact_outputs'],s['whole_tasks'],'gain/loss',len(v['gains']),len(v['losses']))
