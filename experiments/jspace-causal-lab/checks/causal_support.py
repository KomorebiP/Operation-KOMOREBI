"""Load the unchanged browser weights into the original PyTorch definitions.
No training, target-conditioned answer replacement or joint hidden-state reader.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib, json, sys
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import working as wk
import access_repair as ar

def load(lineage='A',variant='calibrated'):
    meta=json.loads((ROOT/'app/weights.json').read_text())
    raw=(ROOT/'app/weights.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=meta['weights_sha256']:
        raise ValueError('weights hash mismatch')
    def tensors(prefix):
        return {k[len(prefix):]:torch.from_numpy(np.frombuffer(raw,dtype='<f4',count=t['length'],offset=t['offset']).copy().reshape(t['shape']))
                for k,t in meta['tensors'].items() if k.startswith(prefix)}
    base=wk.Dyad(wk.Config(**meta['lineages'][lineage]['config']))
    base.load_state_dict(tensors(lineage+'.parent.'))
    m=ar.Repair(base)
    if variant!='parent':m.access.load_state_dict(tensors(lineage+'.'+variant+'.access.'))
    for p in m.parameters():p.requires_grad_(False)
    m.eval();return m

def fixture_bank(n,seed):
    rng=np.random.default_rng(seed)
    specs=[]
    for i in range(n):
        world=rng.integers(0,2,8).tolist(); order=rng.permutation(8)
        specs.append(dict(world=world,events=[[0,int(j),int(j),world[j],1,int(rng.integers(2)),int(rng.integers(2))] for j in order],
           roles=rng.integers(0,4,2).tolist(),cue=rng.choice(8,2,replace=False).tolist(),alias=int(rng.integers(2)),
           ops=rng.integers(0,4,[0,3,6][i%3]).tolist(),opAliases=rng.integers(0,2,[0,3,6][i%3]).tolist()))
    return specs

def source(m,specs):
    n=len(specs);length=max([len(s['ops']) for s in specs],default=0)
    ops=torch.full((n,length),-1,dtype=torch.long);aliases=torch.zeros_like(ops)
    for i,s in enumerate(specs):
        ops[i,:len(s['ops'])]=torch.tensor(s['ops'],dtype=torch.long)
        aliases[i,:len(s['opAliases'])]=torch.tensor(s['opAliases'],dtype=torch.long)
    b=SimpleNamespace(events=torch.tensor([s['events'] for s in specs]),roles=torch.tensor([s['roles'] for s in specs]))
    cue=torch.tensor([s['cue'] for s in specs]);alias=torch.tensor([s['alias'] for s in specs])
    with torch.no_grad():h=m.base.program(m.base.cue(m.base.encode(b),cue,alias,delay=0),ops,aliases)
    return h

def program(m,h,ops):
    n=len(h[0]);p=torch.as_tensor(ops,dtype=torch.long)
    if p.ndim==1:p=p[None,:].repeat(n,1)
    return m.base.program(h,p,torch.zeros_like(p))

def pair_value(s):
    w=[s['world'][i] for i in s['cue']]
    for op in s['ops']:
        if op==1:w[0]^=1
        elif op==2:w[1]^=1
        elif op==3:w=w[::-1]
    return w[0]+2*w[1]

def read(m,h):
    n=len(h[0]);zero=torch.zeros(n,dtype=torch.long)
    # [agent, query, case, class]. q2 mask3, q3 proposal1 are fixed, answer-independent.
    return torch.stack([torch.stack([a.read(h[i],zero+q,zero+(3 if q==2 else 1 if q==3 else 0)) for q in range(4)]) for i,a in enumerate(m.base.agents)])

def patch(h,donor,bases,strength=1.,offsets=(0.,0.,0.),scales=None,agent='both',mode='project'):
    result=[]
    for i in range(2):
        if agent!='both' and str(i)!=agent:result.append(h[i].clone());continue
        u=torch.as_tensor(bases[i],dtype=h[i].dtype)
        diff=donor[i]-h[i];p=(diff@u.T)@u
        delta=diff if mode=='native' else diff-p if mode=='complement' else p
        if mode=='none':delta=torch.zeros_like(diff)
        out=h[i]+float(strength)*delta
        if scales is not None and mode=='project':
            out=out+(torch.as_tensor(offsets,dtype=out.dtype)*torch.as_tensor(scales[i],dtype=out.dtype))@u
        result.append(out)
    return result

def memory(m,h,specs,variant):
    n=len(h[0]);pred=[]
    for j in range(4):
        cue=torch.tensor([[2*j,2*j+1]]*n);alias=torch.zeros(n,dtype=torch.long)
        r=(m.legacy_retrieve if variant=='parent' else m.retrieve)([x.clone() for x in h],cue,alias)
        val=torch.stack([a.read(r[i],alias,alias).argmax(-1) for i,a in enumerate(m.base.agents)])
        pred.append(torch.stack([val%2,val//2],-1))
    return torch.cat(pred,-1)
