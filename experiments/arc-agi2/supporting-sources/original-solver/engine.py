"""Task-blind compiler integration. Author: Komorebi P."""
from __future__ import annotations
import argparse, copy, json, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import contract
import legacy
from memo import feature_cache

ROOT = Path(__file__).resolve().parent
LIMITS = dict(contract.DEFAULT_LIMITS)
FEATURE_LIMITS = {**LIMITS, 'max_depth': 2, 'beam_width': 32, 'max_programs': 32}
_ENTRANTS13 = _ENTRANTS_NEW = None

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    contract.write_json(path, value)

def seal(value):
    body = copy.deepcopy(value)
    body.pop('content_hash', None)
    body['content_hash'] = contract.digest(body)
    return body

def verify(value):
    if value.get('content_hash') != contract.digest({k:v for k,v in value.items() if k != 'content_hash'}):
        raise ValueError('content hash mismatch')

def sanitize(task):
    if any('output' in x for x in task.get('test', [])):
        raise ValueError('attached test output rejected')
    return contract.sanitize_task(task)

def code_hash():
    return contract.digest({n:contract.sha256_file(ROOT/n) for n in ('engine.py','legacy.py','action_adapter.py','contract.py','memo.py')})

def bank_hash():
    return contract.digest({n:read(ROOT/n) for n in ('vendor_manifest.json','bank13.json','bank14_15.json')})

def initialize():
    global _ENTRANTS13
    legacy.verify_sources()
    _ENTRANTS13 = contract.load_entrants(ROOT/'entrants13', read(ROOT/'bank13.json'))
    registry = read(ROOT/'bank14_15.json')
    for n, item in registry.items():
        if contract.sha256_file(ROOT/'entrants'/f'{n}.py') != item['sha256']:
            raise ValueError(f'new bank source mismatch: {n}')

def initialize_new():
    global _ENTRANTS_NEW
    if str(ROOT/'entrants') not in sys.path:
        sys.path.insert(0,str(ROOT/'entrants'))
    _ENTRANTS_NEW = contract.load_entrants(ROOT/'entrants', {n:r['sha256'] for n,r in read(ROOT/'bank14_15.json').items()})

def annotate(candidate, block):
    value = copy.deepcopy(candidate)
    value['origin_candidate_hash'] = value.pop('candidate_hash')
    value['source_block'] = block
    value['candidate_hash'] = contract.digest(value)
    return value

def compile_record(task, include_new=False):
    if _ENTRANTS13 is None:
        initialize()
    task = sanitize(task)
    rows, base, receipts = legacy.compile_old(task)
    for entrant in _ENTRANTS13:
        if entrant.name == 'feature_induction':
            with feature_cache(entrant.module):
                candidates, receipt = contract._compile_one(entrant, task, FEATURE_LIMITS)
            receipt['search_limits'] = {k:FEATURE_LIMITS[k] for k in ('max_depth','beam_width','max_programs')}
        else:
            candidates, receipt = contract._compile_one(entrant, task, LIMITS)
        rows.extend(annotate(c,13) for c in candidates)
        receipts[entrant.name] = receipt
    if include_new:
        if _ENTRANTS_NEW is None:
            initialize_new()
        blocks = read(ROOT/'bank14_15.json')
        for entrant in _ENTRANTS_NEW:
            candidates, receipt = contract._compile_one(entrant, task, LIMITS)
            rows.extend(annotate(c,blocks[entrant.name]['source_block']) for c in candidates)
            receipts[entrant.name] = receipt
    rows.sort(key=lambda c:c['candidate_hash'])
    return seal({'task_semantic_hash':contract.digest(task),'candidates':rows,'base':base,'receipts':receipts})

def scan(challenges, output, workers=8, include_new=False):
    clean = {k:sanitize(t) for k,t in challenges.items()}
    initialize()
    run_hash = contract.digest({'code':code_hash(),'bank':bank_hash(),'challenges':clean,'include_new':include_new,'limits':LIMITS})
    checkpoint = Path(output).with_suffix('.tasks')
    checkpoint.mkdir(parents=True,exist_ok=True)
    records, todo = {},{}
    for key, task in sorted(clean.items()):
        path = checkpoint/(contract.digest(key)+'.json')
        if path.exists():
            item = read(path); verify(item)
            if item['run_hash'] != run_hash:
                raise ValueError('stale checkpoint')
            verify(item['record']); records[key]=item['record']
        else:
            todo[key]=task
    with ProcessPoolExecutor(max_workers=workers,initializer=initialize) as pool:
        jobs = {pool.submit(compile_record,t,include_new):k for k,t in todo.items()}
        for job in as_completed(jobs):
            key=jobs[job]; records[key]=job.result()
            write(checkpoint/(contract.digest(key)+'.json'),seal({'run_hash':run_hash,'record':records[key]}))
            if len(records)%25 == 0:
                print(json.dumps({'completed':len(records),'candidate_tasks':sum(bool(r['candidates']) for r in records.values()),'error_receipts':sum(x['status']!='ok' for r in records.values() for x in r['receipts'].values())}),flush=True)
    result=seal({'schema':'komorebi.block17.live_census.v1','author':'Komorebi P.','run_hash':run_hash,
                 'code_hash':code_hash(),'bank_hash':bank_hash(),'challenges_hash':contract.digest(clean),
                 'scope':'all_banks' if include_new else 'core_blocks2_13','limits':LIMITS,'records':records,
                 'label_access':'demonstrations_only','champion_fallback':False})
    write(output,result)
    return result

def merge(challenges, old, prior):
    """Reuse an authenticated compiler census; never used as a task-ID lookup."""
    verify(old); verify(prior)
    clean={k:sanitize(t) for k,t in challenges.items()}
    expected=contract.digest(clean)
    if old['challenges_hash']!=expected or prior['challenges_hash']!=expected:
        raise ValueError('census challenge binding mismatch')
    if old['bank_hash']!=bank_hash() or old['code_hash']!=code_hash():
        raise ValueError('old bank/code binding mismatch')
    registry=read(ROOT/'bank14_15.json')
    if prior['bank_hash'] != contract.digest(registry):
        raise ValueError('cached new bank binding mismatch')
    if old['scope']!='core_blocks2_13' or set(old['records'])!=set(clean) or set(prior['records'])!=set(clean):
        raise ValueError('census scope mismatch')
    initialize()
    records={}
    for key,task in sorted(clean.items()):
        a,b=old['records'][key],prior['records'][key]
        verify(a);verify(b)
        if a['task_semantic_hash']!=contract.digest(task) or b['task_semantic_hash']!=contract.digest(task):
            raise ValueError('record input binding mismatch')
        rows=a['candidates']+[annotate(c,registry[c['entrant']]['source_block']) for c in b['candidates']]
        records[key]=seal({'task_semantic_hash':contract.digest(task),'base':a['base'],
            'candidates':sorted(rows,key=lambda c:c['candidate_hash']),'receipts':{**a['receipts'],**b['receipts']}})
    return seal({'schema':'komorebi.block17.combined_census.v1','author':'Komorebi P.','code_hash':code_hash(),
        'bank_hash':bank_hash(),'challenges_hash':expected,'scope':'all_banks','limits':LIMITS,'records':records,
        'label_access':'demonstrations_only','champion_fallback':False,
        'old_census_hash':old['content_hash'],'reused_block16_census_hash':prior['content_hash']})

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['scan','merge'])
    p.add_argument('--challenges',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=8)
    p.add_argument('--include-new',action='store_true')
    p.add_argument('--old',type=Path);p.add_argument('--prior',type=Path)
    a=p.parse_args()
    if a.command=='scan': scan(read(a.challenges),a.output,a.workers,a.include_new)
    else:write(a.output,merge(read(a.challenges),read(a.old),read(a.prior)))
