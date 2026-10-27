"""Recompute challenge origins, native trajectories, projected writes, outputs and recall.
Uses original retained PyTorch model definitions, not the JS implementation.
"""
from pathlib import Path
import json, hashlib
import numpy as np
import torch
from causal_support import load, source, program, patch, memory
ROOT=Path(__file__).resolve().parents[1]
torch.set_num_threads(1)
rows=json.loads((ROOT/'checks/robustness/numeric_fixtures.json').read_text())
frames=json.loads((ROOT/'app/frames.json').read_text())
counts=dict(trajectories=len(rows),snapshots=0,output_decisions=0,private_decisions=0,memory_bit_decisions=0,decision_mismatches=0,memory_mismatches=0)
errors=dict(origin=0.0,state=0.0,logit=0.0)
models={}
for p in rows:
 key=p['lineage'],p['variant'];m=models.setdefault(key,load(*key)) if key not in models else models[key]
 o=p['initial'];s=p['settings'];f=frames['lineages'][p['lineage']]
 with torch.no_grad():
  src=source(m,[p['spec']]);b=program(m,src,[0,0]);mask=o['factualValue']^o['targetValue'];donor_ops=[1,1] if mask==0 else [1 if mask&1 else 0,2 if mask&2 else 0];donor=program(m,src,donor_ops)
  for expected,actual in [(o['baseline'],b),(o['donor'],donor)]:
   errors['origin']=max(errors['origin'],max(float(np.max(np.abs(np.array(expected[a])-actual[a][0].numpy()))) for a in range(2)))
  # Supplied snapshots isolate all subsequent numerical errors from the origin port.
  b=[torch.tensor(h,dtype=torch.float32)[None,:] for h in o['baseline']];donor=[torch.tensor(h,dtype=torch.float32)[None,:] for h in o['donor']]
  k='J' if s['method'] in ['none','complement','native'] else s['method'];mode={'none':'none','complement':'complement','native':'native'}.get(s['method'],'project')
  edit=patch(b,donor,[a[k] for a in f['frames']],s['strength'],s['offsets'],[a['scales'] for a in f['statistics']] if s['method']=='J' else None,s['agent'],mode)
  states=[program(m,h,s['suffix']) for h in [b,edit,donor]];at=0;reloaded=0;closed=False
  order=p['cue']+[i for i in range(8) if i not in p['cue']]
  for rec in p['records']:
   while at<rec['work']:
    states=[program(m,h,[p['plan']['ops'][at]]) for h in states];at+=1
   if rec['phase']=='reload':
    if not closed:states=[m.base.silent(h) for h in states];closed=True
    while reloaded<rec['reloads']:
     c=order[(reloaded%4)*2:(reloaded%4)*2+2];fn=m.legacy_retrieve if p['variant']=='parent' else m.retrieve
     states=[fn(h,torch.tensor([c]),torch.zeros(1,dtype=torch.long),mode=p['plan']['mode']) for h in states];reloaded+=1
    current=states
   else:current=[m.base.silent(h) for h in states]
   counts['snapshots']+=1
   for branch,h in enumerate(current):
    for a in range(2):
     errors['state']=max(errors['state'],float(np.max(np.abs(h[a][0].numpy()-np.array(rec['states'][branch][a])))))
     for q,arg in enumerate(rec['queryArgs']):
      z=m.base.agents[a].read(h[a],torch.tensor([q]),torch.tensor([arg]))[0];rr=rec['outputs'][branch][q][a]
      errors['logit']=max(errors['logit'],float(np.max(np.abs(z.numpy()-np.array(rr['logits'])))))
      counts['output_decisions']+=1;counts['decision_mismatches']+=int(z.argmax().item()!=rr['prediction'])
     z=m.base.agents[a].private(h[a])[0];counts['private_decisions']+=1;counts['decision_mismatches']+=int(z.argmax().item()!=rec['outputs'][branch][0][a]['privatePrediction'])
    bits=memory(m,h,[{'world':p['world']}],p['variant'])[:,0,:].numpy()
    counts['memory_bit_decisions']+=bits.size;counts['memory_mismatches']+=int((bits!=np.array(rec['memory'][branch]['bits'])).sum())
assert counts['decision_mismatches']==0,counts
assert counts['memory_mismatches']==0,counts
assert errors['origin']<0.0003 and errors['state']<0.0003 and errors['logit']<0.003,errors
out={'status':'PASS',**counts,'maximum_absolute_errors':errors,'torch':torch.__version__,'source':'Unchanged original PyTorch runtime and source-generated origins','scope':'Sampled numerical agreement, not bitwise or universal equivalence.'}
(ROOT/'checks/robustness/pytorch_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
