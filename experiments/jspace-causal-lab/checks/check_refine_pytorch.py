"""Independent original PyTorch definitions versus new JS persistent paths.
Starting paired activation snapshots are supplied; all subsequent transitions,
patch arithmetic, logits and final native recall are recomputed in PyTorch.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import torch
from causal_support import load, program, patch, memory
ROOT=Path(__file__).resolve().parents[1]
torch.set_num_threads(1)
rows=json.loads((ROOT/'checks/refined_numeric_fixtures.json').read_text())
frames=json.loads((ROOT/'app/frames.json').read_text())
maxstate=maxlogit=0.;decisions=mismatches=0;mem_decisions=mem_mismatches=0;models={}
for p in rows:
 key=(p['lineage'],p['variant'])
 if key not in models:models[key]=load(*key)
 m=models[key];o=p['origin'];s=p['settings'];f=frames['lineages'][p['lineage']]
 base=[torch.tensor(h,dtype=torch.float32)[None,:] for h in o['baseline']]
 donor=[torch.tensor(h,dtype=torch.float32)[None,:] for h in o['donor']]
 k='J' if s['method'] in ['native','complement','none'] else s['method']
 mode={'native':'native','complement':'complement','none':'none'}.get(s['method'],'project')
 bases=[a[k] for a in f['frames']]
 edit=patch(base,donor,bases,s['strength'],s['offsets'],[a['scales'] for a in f['statistics']] if s['method']=='J' else None,s['agent'],mode)
 with torch.no_grad():
  states=[m.base.silent(program(m,h,s['suffix'])) for h in [base,edit]]
  for i,snap in enumerate(p['snapshots']):
   if i:
    a=p['actions'][i-1]
    if a['type']=='work':states=[m.base.silent(program(m,h,a['ops'])) for h in states]
    elif a['type']=='silent':states=[m.base.silent(h,a['count']) for h in states]
    else:
     cue=torch.tensor([a['cue']]);alias=torch.zeros(1,dtype=torch.long)
     fn=m.legacy_retrieve if p['variant']=='parent' else m.retrieve
     states=[fn(h,cue,alias,mode=a['mode']) for h in states]
   for b,h in enumerate(states):
    for agent in range(2):
     maxstate=max(maxstate,float(np.max(np.abs(h[agent][0].numpy()-np.array(snap['states'][b][agent])))))
     for q in range(4):
      z=torch.tensor([q]);arg=torch.tensor([3 if q==2 else 1 if q==3 else 0])
      logits=m.base.agents[agent].read(h[agent],z,arg)[0]
      ref=snap['outputs'][b][q][agent]
      maxlogit=max(maxlogit,float(np.max(np.abs(logits.numpy()-ref['logits']))))
      decisions+=1;mismatches+=int(logits.argmax().item()!=ref['prediction'])
      priv=m.base.agents[agent].private(h[agent])[0]
      decisions+=1;mismatches+=int(priv.argmax().item()!=ref['privatePrediction'])
  for b,h in enumerate(states):
   bits=memory(m,h,[{'world':p['world']}],p['variant'])[:,0,:].numpy()
   ref=np.array(p['finalMemory']['before' if b==0 else 'after']['bits'])
   mem_decisions+=bits.size;mem_mismatches+=int((bits!=ref).sum())
assert mismatches==0,(mismatches,decisions)
assert mem_mismatches==0,(mem_mismatches,mem_decisions)
assert maxstate<0.0003,maxstate
assert maxlogit<0.003,maxlogit
out={'status':'PASS','trajectories':len(rows),'snapshots':sum(len(p['snapshots']) for p in rows),
 'output_and_private_decisions':decisions,'decision_mismatches':mismatches,
 'final_memory_bit_decisions':mem_decisions,'memory_mismatches':mem_mismatches,
 'max_state_abs_error':maxstate,'max_logit_abs_error':maxlogit,
 'torch_version':torch.__version__,'fixture_sha256':hashlib.sha256((ROOT/'checks/refined_numeric_fixtures.json').read_bytes()).hexdigest(),
 'scope':'Original PyTorch transitions from supplied paired origins. Shared/private outputs count reused snapshots and contexts. Sampled numerical agreement, not universal or bitwise equivalence.'}
(ROOT/'checks/refined_numeric_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
