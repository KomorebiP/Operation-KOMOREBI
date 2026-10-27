"""Paired all-corpus check of a geometry-domain repair. Author: Komorebi P."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import engine
ROOT=Path(__file__).resolve().parent
_OLD=_NEW=None

def initialize():
    global _OLD,_NEW
    manifest=engine.read(ROOT/'repair_results/source_freeze.json');engine.verify(manifest)
    _OLD=engine.contract.load_entrants(ROOT/'entrants13',{'micro_schemas':manifest['original_sha256']})[0]
    _NEW=engine.contract.load_entrants(ROOT/'repair_entrants',{'micro_schemas_v2':manifest['repair_sha256']})[0]

def semantic(rows):
    return sorted(engine.contract.digest({k:v for k,v in r.items() if k not in ('entrant','candidate_hash')}) for r in rows)

def job(task):
    task=engine.sanitize(task)
    a,ar=engine.contract._compile_one(_OLD,task,engine.LIMITS)
    b,br=engine.contract._compile_one(_NEW,task,engine.LIMITS)
    preserved=semantic(a)==semantic(b) if ar['status']=='ok' else None
    return engine.seal({'task_semantic_hash':engine.contract.digest(task),'original_receipt':ar,'repair_receipt':br,
        'successful_original_candidates_preserved':preserved,'original_behavior_hashes':sorted(c['behavior_hash'] for c in a),
        'candidates':[engine.annotate(c,13) for c in b]})

def main():
    tasks=engine.read(ROOT/'data/challenges.json');initialize();records={}
    with ProcessPoolExecutor(max_workers=2,initializer=initialize) as pool:
        jobs={pool.submit(job,t):k for k,t in tasks.items()}
        for f in as_completed(jobs):
            records[jobs[f]]=f.result()
            if len(records)%100==0:print('paired tasks',len(records),flush=True)
    result=engine.seal({'schema':'komorebi.block17.geometry_repair_census.v1','author':'Komorebi P.',
        'source_freeze_hash':engine.read(ROOT/'repair_results/source_freeze.json')['content_hash'],
        'challenges_hash':engine.contract.digest({k:engine.sanitize(t) for k,t in tasks.items()}),'records':records,
        'original_errors':sum(r['original_receipt']['status']!='ok' for r in records.values()),
        'repair_errors':sum(r['repair_receipt']['status']!='ok' for r in records.values()),
        'preservation_failures':sum(r['successful_original_candidates_preserved'] is False for r in records.values()),
        'validation_passed':all(r['repair_receipt']['status']=='ok' and r['successful_original_candidates_preserved'] is not False for r in records.values()),
        'tasks_activated':sum(bool(r['candidates']) for r in records.values()),
        'new_activations_after_original_error':sum(bool(r['candidates']) and r['original_receipt']['status']!='ok' for r in records.values()),
        'label_access':'demonstrations_only'})
    engine.write(ROOT/'repair_results/census.json',result)
    print({k:v for k,v in result.items() if k!='records'},flush=True)
    if not result['validation_passed']:raise SystemExit(1)

if __name__=='__main__':main()
