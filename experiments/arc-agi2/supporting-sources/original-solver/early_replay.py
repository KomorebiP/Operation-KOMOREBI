"""Fresh full-bank replay from a saved, unscored checkpoint.
Author: Komorebi P.
"""
import json,zipfile,subprocess,sys,tempfile
from pathlib import Path
import engine
ROOT=Path(__file__).resolve().parent

def main():
    checkpoint=ROOT.parent/'Komorebi_PR_LASM_Block17_Work_Checkpoint.zip'
    state=engine.read(ROOT.parent/'Komorebi_PR_LASM_Block17_Checkpoint_State.json')
    if engine.contract.sha256_file(checkpoint)!=state['sha256']:raise ValueError('checkpoint file changed')
    tasks=engine.read(ROOT/'data/challenges.json');ids={engine.contract.digest(engine.sanitize(t)):k for k,t in tasks.items()}
    old={}
    with zipfile.ZipFile(checkpoint) as z:
        for name in z.namelist():
            if not name.startswith('block17/results/final_legacy_census.tasks/') or not name.endswith('.json'):continue
            item=json.loads(z.read(name));engine.verify(item);r=item['record'];engine.verify(r)
            old[ids[r['task_semantic_hash']]]=r
    prior=engine.read(ROOT/'evidence/block16_census.json');engine.verify(prior)
    registry=engine.read(ROOT/'bank14_15.json')
    selected=[]
    predicates=[lambda k:any(c['source_block']<=12 for c in old[k]['candidates']),
                lambda k:any(c['entrant']=='feature_induction' for c in old[k]['candidates']),
                lambda k:bool(prior['records'][k]['candidates'])]
    def size(k):return sum(len(x['input'])*len(x['input'][0]) for split in ('train','test') for x in tasks[k][split])
    for test in predicates:selected.append(min((k for k in old if k not in selected and test(k)),key=lambda k:(size(k),k)))
    sample={k:tasks[k] for k in selected};engine.write(ROOT/'results/replay_challenges.json',sample)
    subprocess.run([sys.executable,str(ROOT/'engine.py'),'scan','--challenges',str(ROOT/'results/replay_challenges.json'),
       '--include-new','--workers','3','--output',str(ROOT/'results/live_replay_sample.json')],check=True)
    fresh=engine.read(ROOT/'results/live_replay_sample.json');engine.verify(fresh)
    checks=[]
    for k in selected:
        a,b=old[k],prior['records'][k]
        rows=a['candidates']+[engine.annotate(c,registry[c['entrant']]['source_block']) for c in b['candidates']]
        expected=engine.seal({'task_semantic_hash':a['task_semantic_hash'],'base':a['base'],
                             'candidates':sorted(rows,key=lambda c:c['candidate_hash']),'receipts':{**a['receipts'],**b['receipts']}})
        if fresh['records'][k]!=expected:raise AssertionError(f'full-bank fresh record differed: {k}')
        checks.append({'task_id':k,'record_hash':expected['content_hash'],'candidates':len(rows),
                       'compiler_interfaces':len(expected['receipts']),'all_sources_live':True,'byte_content_equal':True})
    engine.write(ROOT/'results/compiler_replay_validation.json',engine.seal({'author':'Komorebi P.',
        'selection_rule':'smallest total input-cell count, then lexical ID, for native/feature/modern activations in saved unscored checkpoint',
        'checkpoint_sha256':state['sha256'],'engine_hash':engine.code_hash(),'bank_hash':engine.bank_hash(),'checks':checks,
        'scope':'Three fresh-process full-bank samples; not a second complete corpus scan.'}))
    print(checks,flush=True)

if __name__=='__main__':main()
