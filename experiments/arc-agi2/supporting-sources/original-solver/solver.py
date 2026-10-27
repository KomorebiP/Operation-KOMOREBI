"""Deterministic, label-free dispatch across the inherited banks.
Author: Komorebi P.
"""
from __future__ import annotations
import argparse, copy, re
from collections import defaultdict
from pathlib import Path
import engine
from engine import ROOT, read, write, seal, verify, sanitize, contract
from repairs import inspect_repair

POLICIES=('base','recent_control','typed_recent','typed_joint','typed_agreement','typed_supported')
PRIMARY='typed_recent'

def prediction_hash():
    return contract.digest({'engine':engine.code_hash(),**{n:contract.sha256_file(ROOT/n) for n in ('solver.py','repairs.py')}})

def lineage(name):
    return re.sub(r'_v[0-9]+$','',name)

def version(name):
    m=re.search(r'_v([0-9]+)$',name)
    return int(m[1]) if m else 1

def priority(candidate):
    if candidate['entrant']=='core_search':
        return 0  # This is the same core already executed by the live base.
    return min(14,candidate['source_block'])

def rank_record(record,policy):
    if policy not in POLICIES:raise ValueError('unknown policy')
    verify(record)
    versions={}
    for c in record['candidates']:
        n=lineage(c['entrant']);versions[n]=max(versions.get(n,0),version(c['entrant']))
    groups=defaultdict(list);repairs=[];superseded=[]
    for c in record['candidates']:
        if version(c['entrant'])!=versions[lineage(c['entrant'])]:
            superseded.append(c['candidate_hash']);continue
        repair=inspect_repair(c) if policy.startswith('typed_') else {'status':'not_requested'}
        if repair['status']!='out_of_scope':
            repairs.append({'candidate_hash':c['candidate_hash'],**repair})
        if repair['status']=='veto':continue
        if policy=='typed_supported' and c['entrant']=='feature_induction':
            unseen=c.get('evidence',{}).get('unseen_test_keys')
            if not isinstance(unseen,int) or unseen!=0:
                repairs.append({'candidate_hash':c['candidate_hash'],'status':'abstained_unknown',
                    'reason':'unsupported_test_feature_keys','unseen_test_keys':unseen,
                    'program_hash':contract.digest(c['program']),
                    'claim':'lack of trace support, not proof that this prediction is false'})
                continue
        if c['entrant']=='core_search' and policy!='typed_joint':continue
        groups[c['behavior_hash']].append(c)
    behaviors=[]
    for h,rows in groups.items():
        top=max(priority(c) for c in rows)
        elite=[c for c in rows if priority(c)==top]
        source_votes=len({lineage(c['entrant']) for c in rows})
        elite_votes=len({lineage(c['entrant']) for c in elite})
        complexity=min(c['complexity'] for c in elite)
        rank=(source_votes,top,-complexity) if policy=='typed_agreement' else (top,elite_votes,-complexity,source_votes)
        behaviors.append({'behavior_hash':h,'test_outputs':rows[0]['test_outputs'],'rank':list(rank),
                          'sources':sorted({c['entrant'] for c in rows}),
                          'candidate_hashes':sorted(c['candidate_hash'] for c in rows)})
    behaviors.sort(key=lambda b:(tuple(-x for x in b['rank']),b['behavior_hash']))
    return {'behaviors':behaviors,'repairs':repairs,'superseded':sorted(superseded),
            'tied_at_top':len(behaviors)>1 and behaviors[0]['rank']==behaviors[1]['rank'],
            'unknown_mass':'uncalibrated'}

def dispatch(challenges,census,policy):
    verify(census)
    clean={k:sanitize(t) for k,t in challenges.items()}
    if census['bank_hash']!=engine.bank_hash() or census['code_hash']!=engine.code_hash():
        raise ValueError('source binding mismatch')
    if census['challenges_hash']!=contract.digest(clean) or set(census['records'])!=set(clean):
        raise ValueError('challenge binding mismatch')
    if census['scope']!='all_banks':raise ValueError('incomplete bank scope')
    submission={};decisions={}
    for key,task in sorted(clean.items()):
        record=census['records'][key]
        if record['task_semantic_hash']!=contract.digest(task):raise ValueError('record task mismatch')
        d=rank_record(record,policy);result=[];selected=[]
        for i,base in enumerate(record['base']):
            if policy=='base':
                row=copy.deepcopy(base);sources=['live_base_1','live_base_2']
            elif policy=='typed_joint':
                options=[(b['test_outputs'][i],b['behavior_hash']) for b in d['behaviors']]
                options.extend((base[f'attempt_{j}'],f'live_base_{j}') for j in (1,2))
                distinct=[]
                for grid,source in options:
                    if all(grid!=a for a,_ in distinct):distinct.append((grid,source))
                    if len(distinct)==2:break
                if len(distinct)==1:distinct.append(distinct[0])
                row={f'attempt_{j+1}':x[0] for j,x in enumerate(distinct)}
                sources=[x[1] for x in distinct]
            else:
                row=copy.deepcopy(base);sources=['live_base_1','live_base_2']
                # A repeat of Attempt 1 consumes no extra guess; use the first distinct behavior.
                for b in d['behaviors']:
                    grid=b['test_outputs'][i]
                    if grid!=row['attempt_1']:
                        row['attempt_2']=grid;sources[1]=b['behavior_hash'];break
            result.append(row);selected.append(sources)
        d['selected_sources']=selected
        d['activated']=any(any(not s.startswith('live_base_') for s in ss) for ss in selected)
        decisions[key]=d;submission[key]=result
    return seal({'schema':'komorebi.block17.autonomous_dispatch.v1','author':'Komorebi P.',
                 'policy':policy,'primary_policy':PRIMARY,'prediction_hash':prediction_hash(),
                 'bank_hash':engine.bank_hash(),'census_hash':census['content_hash'],
                 'champion_fallback':False,'label_access':'demonstrations_only',
                 'decisions':decisions,'submission':submission})

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--challenges',required=True,type=Path);p.add_argument('--census',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path);p.add_argument('--policy',choices=POLICIES,default=PRIMARY)
    a=p.parse_args();write(a.output,dispatch(read(a.challenges),read(a.census),a.policy))
