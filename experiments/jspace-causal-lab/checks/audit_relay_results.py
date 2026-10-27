"""Independent scalar output/target/aggregate audit; does not call JS scoring."""
from pathlib import Path
import json,gzip,hashlib,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'checks/relay'
raw=json.loads(gzip.decompress((OUT/'raw.json.gz').read_bytes()));result=json.loads((OUT/'assay.json').read_text())
def op(v,k):
    x,y=v%2,v//2
    if k==1:x=1-x
    if k==2:y=1-y
    if k==3:x,y=y,x
    return x+2*y
def targets(v,factual):return [v,(v%2)^(v//2),v^3,int(v==factual)]
def near(a,b):return abs(a-b)<1e-10
counts={'consumer_decisions':0,'private_decisions':0,'factual_bit_decisions':0,'packet_scalars':0}
cells={}
for t in raw:
    s=t['spec'];world=[0]*8
    for e in s['events']:
        assert e[0]==0 and e[4]==1;world[e[1]]=e[3]
    assert world==t['world']==s['world']
    f=world[s['cue'][0]]+2*world[s['cue'][1]]
    for k in s['ops']:f=op(f,k)
    assert f==t['initial']['factualValue'];d=f^(1+(t['caseIndex']%3));assert d==t['initial']['targetValue']
    w=t['plan']['writer'];a=1-w;ix=0;events=0
    for r in t['records']:
        if r['phase']=='local':k=t['plan']['ops'][ix];ix+=1;f=op(f,k);d=op(d,k)
        if r['phase']=='receive':events+=1;assert r['packet']['intervened']==(events==1)
        assert r['references']=={'factual':targets(f,f),'donor':targets(d,f)}
        for b in range(5):
            for q in range(4):
                pred=r['outputs'][b][q][a];assert pred['prediction']==max(range(4),key=lambda z:pred['logits'][z])
                for agent in range(2):
                    p=r['outputs'][b][q][agent];assert p['prediction']==max(range(4),key=lambda z:p['logits'][z]);counts['consumer_decisions']+=1
                    if q==0:assert p['privatePrediction']==max(range(4),key=lambda z:p['privateLogits'][z]);counts['private_decisions']+=1
            assert r['receiverDonor'][b]==(r['outputs'][b][0][a]['prediction']==d)
            assert r['writerDonor'][b]==(r['outputs'][b][0][w]['prediction']==d)
            logits=r['outputs'][b][0][a]['logits'];ex=[math.exp(v-max(logits)) for v in logits];assert near(r['targetProbability'][b],ex[d]/sum(ex))
        competence=r['outputs'][0][0][a]['prediction']==f and r['outputs'][4][0][a]['prediction']==d
        assert r['referenceError']==(not competence);assert r['eligible']==(competence and f!=d)
        if r['packet']:
            p=r['packet'];counts['packet_scalars']+=8*7
            if p['intervened']:
                assert p['sent'][2]==p['original'];assert p['sent'][3]==p['edited']
                # Same recipient's all output scores must be bit-identical at this cut.
                for q in range(4):assert r['outputs'][2][q][a]==r['outputs'][0][q][a];assert r['outputs'][3][q][a]==r['outputs'][1][q][a]
    for mem in t['finalMemory']:
        for a in range(2):assert mem['correct'][a]==sum(x==y for x,y in zip(mem['bits'][a],world));counts['factual_bit_decisions']+=8
    key=(t['model']['lineage'],w,t['settings']['method']);cells.setdefault(key,[]).append(t)
for c in result['cells']:
    records=cells[c['lineage'],c['writer'],c['method']];assert len(records)==c['histories']
    for label,idx in [('first',0),('last',-1)]:
        rr=[next(r for r in t['records'] if r['phase']=='receive') if idx==0 else [r for r in t['records'] if r['phase']=='receive'][-1] for t in records]
        for field in ['recipientDonor','writerDonor']:
            src='receiverDonor' if field=='recipientDonor' else field
            assert c[label][field]==[sum(r[src][b] for r in rr) for b in range(5)]
        assert c[label]['eligible']==sum(r['eligible'] for r in rr)
        assert c[label]['referenceErrors']==sum(r['referenceError'] for r in rr)
        assert c[label]['eligibleTransfer']==sum(r['eligible'] and r['receiverDonor'][1] for r in rr)
    for b in range(5):
        assert c['memory']['allFacts'][b]==[sum(t['finalMemory'][b]['correct'][a]==8 for t in records) for a in range(2)]
        assert c['memory']['private'][b]==[sum(t['records'][-1]['outputs'][b][0][a]['privatePrediction']==t['roles'][a] for t in records) for a in range(2)]
for p,h in result['execution']['input_hashes_after'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
out={'status':'PASS','traces':len(raw),'records':sum(len(t['records']) for t in raw),'aggregate_cells':len(result['cells']),'rechecked_entries':counts,'input_hashes_unchanged':True,'limits':'Histories reused across methods, directions, branches, lineages and checkpoints.'}
(OUT/'independent_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
