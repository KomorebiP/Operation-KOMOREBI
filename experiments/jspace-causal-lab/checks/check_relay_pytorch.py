"""Independent execution with original PyTorch models, not the JS neural engine."""
from pathlib import Path
import json,sys
import numpy as np
import torch
from causal_support import load,source,program,patch,memory,pair_value
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'checks/relay'
torch.set_num_threads(1)
frames=json.loads((ROOT/'app/frames.json').read_text())
references=json.loads((OUT/'reference.json').read_text())
maxerr={'origin':0.,'state':0.,'logit':0.,'packet':0.};count={'consumer':0,'private':0,'factual_bits':0};mismatches={k:0 for k in count}
def close(k,t,a,tol=5e-5):
    x=t.detach().cpu().numpy() if isinstance(t,torch.Tensor) else np.asarray(t)
    y=np.asarray(a);assert x.shape==y.shape,(k,x.shape,y.shape)
    err=float(np.max(np.abs(x-y))) if x.size else 0.
    maxerr[k]=max(maxerr[k],err)
    assert err<tol,(k,err)
def truth(v,op):
    x,y=v&1,(v>>1)&1
    if op==1:x^=1
    elif op==2:y^=1
    elif op==3:x,y=y,x
    return x+2*y
with torch.no_grad():
 for rec in references:
    l=rec['model']['lineage'];m=load(l,rec['model']['variant']);spec=rec['spec'];n=1;z=torch.zeros(n,dtype=torch.long)
    s=source(m,[spec]);fv=pair_value(spec);tv=rec['initial']['targetValue'];assert fv==rec['initial']['factualValue']
    base=program(m,s,[0,0]);mask=fv^tv;ops=[1,1] if mask==0 else [1 if mask&1 else 0,2 if mask&2 else 0];donor=program(m,s,ops)
    for a in range(2):
        close('origin',base[a][0],rec['initial']['baseline'][a]);close('origin',donor[a][0],rec['initial']['donor'][a])
    st=rec['settings'];mode='native' if st['method']=='native' else 'complement' if st['method']=='complement' else 'project'
    key='J' if st['method'] in ['native','complement','none'] else st['method']
    u=[v[key] for v in frames['lineages'][l]['frames']];ed=patch(base,donor,u,st['strength'],agent=str(rec['plan']['writer']),mode=mode)
    hs=[[x.clone() for x in b] for b in [base,ed,ed,base,donor]]
    w=rec['plan']['writer'];event=0;oi=0
    for row in rec['records']:
        if row['phase']=='local':
            op=rec['plan']['ops'][oi];oi+=1
            hs=[[a.work(h[i],z+op,z) for i,a in enumerate(m.base.agents)] for h in hs]
            fv=truth(fv,op);tv=truth(tv,op)
        elif row['phase']=='receive':
            messages=[[a.send(h[i]) for i,a in enumerate(m.base.agents)] for h in hs]
            close('packet',messages[0][w][0],row['packet']['original']);close('packet',messages[1][w][0],row['packet']['edited'])
            if event==0:messages[2][w]=messages[0][w].clone();messages[3][w]=messages[1][w].clone()
            for b in range(5):close('packet',messages[b][w][0],row['packet']['sent'][b])
            hs=[m.base.exchange(h,messages=messages[b]) for b,h in enumerate(hs)];event+=1
        for b,h in enumerate(hs):
            for a in range(2):close('state',h[a][0],row['states'][b][a])
            rd=m.base.silent([v.clone() for v in h])
            for q,arg in enumerate([0,0,3,fv]):
                for a,net in enumerate(m.base.agents):
                    logits=net.read(rd[a],z+q,z+arg)[0];expected=row['outputs'][b][q][a]
                    close('logit',logits,expected['logits']);count['consumer']+=1;mismatches['consumer']+=int(logits.argmax()!=expected['prediction'])
                    if q==0:
                        pp=net.private(rd[a])[0];close('logit',pp,expected['privateLogits']);count['private']+=1;mismatches['private']+=int(pp.argmax()!=expected['privatePrediction'])
    for b,h in enumerate(hs):
        bits=memory(m,m.base.silent(h),[spec],rec['model']['variant']).numpy()[:,0,:];got=np.array(rec['finalMemory'][b]['bits']);count['factual_bits']+=bits.size;mismatches['factual_bits']+=int(np.sum(bits!=got))
assert not any(mismatches.values()),mismatches
result={'status':'PASS','trajectories':len(references),'input_histories':len({json.dumps(r['spec'],sort_keys=True) for r in references}),
 'checkpoints':sum(len(r['records']) for r in references),'decisions':count,'decision_mismatches':mismatches,'maximum_absolute_errors':maxerr,
 'torch':torch.__version__,'scope':'Sampled agreement with unchanged original PyTorch definitions, not universal or bitwise equivalence.'}
(OUT/'pytorch_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
