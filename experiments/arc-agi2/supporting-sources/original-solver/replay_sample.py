"""Fresh-process full-bank replay of a deterministic structural sample.
Author: Komorebi P.
"""
import argparse,subprocess,sys,tempfile
from pathlib import Path
import engine

def replay(root,output):
    root=Path(root);tasks=engine.read(root/'data/challenges.json');census=engine.read(root/'results/census.json')
    # Selection uses candidate provenance and input order, never evaluation labels.
    selected=[]
    predicates=[lambda r: any(c['source_block']<=12 for c in r['candidates']),
                lambda r:any(c['entrant']=='feature_induction' for c in r['candidates']),
                lambda r:any(c['source_block']>=14 for c in r['candidates'])]
    for predicate in predicates:
        k=next(k for k in sorted(tasks) if k not in selected and predicate(census['records'][k]))
        selected.append(k)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d);engine.write(p/'challenges.json',{k:tasks[k] for k in selected})
        subprocess.run([sys.executable,str(root/'engine.py'),'scan','--challenges',str(p/'challenges.json'),
                        '--include-new','--workers','3','--output',str(p/'census.json')],check=True)
        fresh=engine.read(p/'census.json');engine.verify(fresh)
    checks=[]
    for k in selected:
        original=census['records'][k];new=fresh['records'][k]
        if original!=new:raise AssertionError(f'full replay record mismatch: {k}')
        checks.append({'task_id':k,'record_hash':new['content_hash'],'candidate_count':len(new['candidates']),
                       'all_banks_live_rerun':True,'byte_content_equal':True})
    result=engine.seal({'author':'Komorebi P.','sample_rule':'first distinct tasks with native, feature and modern candidates',
        'checks':checks,'all_compiler_interfaces_per_task':len(next(iter(census['records'].values()))['receipts']),
        'code_hash':engine.code_hash(),'bank_hash':engine.bank_hash()})
    engine.write(output,result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(replay(a.root,a.output))
