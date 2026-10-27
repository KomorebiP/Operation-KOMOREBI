"""Phase-local native access repair; no central hidden-state decoder.

Each access module sees only its own hidden state, a normal relevance cue and
its partner's eight-dimensional messages. The base model is exactly frozen in
arm=access. This adds parameters and a supplied phase dispatch, not new memory.
"""
from __future__ import annotations
import argparse, copy, dataclasses, hashlib, json, os, platform, sys, time
from pathlib import Path
from typing import Any
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import working as wk
import evaluate_noninterference as ev
from selective import atomic_json, sha
from noninterference import tensor_digest
ROOT=Path(__file__).resolve().parents[1]

class AccessAgent(nn.Module):
    def __init__(self, a):
        super().__init__(); self.c=a.c
        # Only modules used by the cue phase are copied; answer heads stay original.
        for name in ('name','command','input','observe','emit','gate','receive',
                     'route_state','route_context','route_out'):
            setattr(self,name,copy.deepcopy(getattr(a,name)))
    def context(self,cue,alias):
        e=self.c.embedding
        x=torch.cat((self.command(8+alias), self.name(cue[:,0]),self.name(cue[:,1]),
                     torch.zeros(len(cue),e,device=cue.device)),dim=-1)
        return torch.tanh(self.input(x))
    def local(self,h,cue,alias):
        ctx=self.context(cue,alias)
        routed=h+self.route_out(torch.tanh(self.route_state(h))*torch.sigmoid(self.route_context(ctx))) if self.c.routing else h
        return self.observe(ctx,routed)
    def send(self,h):
        return torch.sigmoid(self.gate(h))*torch.tanh(self.emit(h))

class Repair(nn.Module):
    def __init__(self,base):
        super().__init__(); self.base=base; self.c=base.c
        self.access=nn.ModuleList([AccessAgent(a) for a in base.agents])
    def set_arm(self,arm:str):
        if arm not in ('access','joint'): raise ValueError(arm)
        for p in self.base.parameters(): p.requires_grad_(arm=='joint')
        for p in self.access.parameters(): p.requires_grad_(True)
        self.arm=arm
    def retrieve(self,h,cue,alias,mode='intact',delay=None):
        # No world, query, answer, or other agent's raw state enters either module.
        h=[a.local(h[i],cue,alias) for i,a in enumerate(self.access)]
        for _ in range(self.c.cue_exchanges):
            m=[a.send(h[i]) for i,a in enumerate(self.access)]
            if mode=='cut':m=[torch.zeros_like(x) for x in m]
            elif mode=='shuffle':m=[x.roll(1,0) for x in m]
            elif mode=='cut_AtoB':m=[torch.zeros_like(m[0]),m[1]]
            elif mode=='cut_BtoA':m=[m[0],torch.zeros_like(m[1])]
            elif mode not in ('intact','skip_exchange'):raise ValueError(mode)
            if mode!='skip_exchange':
                h=[a.receive(m[1-i],h[i]) for i,a in enumerate(self.access)]
        return self.base.silent(h,self.c.delay if delay is None else delay)
    def legacy_retrieve(self,h,cue,alias,mode='intact',delay=None):
        return self.base.cue(h,cue,alias,mode,delay)

FAMILIES=('random_nonidentity','mirror_identity','identity_tokens','flip_involution')
LENGTHS=(0,3,6,12,24)

def native_prefix(base,b,p,aliases):
    h=base.cue(base.encode(b),b.cues[:,0],b.cue_aliases[:,0],delay=0)
    return base.silent(base.program(h,p,aliases))

def query_bank(v,g):
    n=len(v);q=torch.randint(4,(n,),generator=g);z=v[:,0]+2*v[:,1]
    mask=torch.randint(4,(n,),generator=g);same=torch.randint(2,(n,),generator=g).bool()
    proposal=torch.where(same,z,(z+torch.randint(1,4,(n,),generator=g))%4)
    arg=torch.where(q==2,mask,torch.where(q==3,proposal,0))
    return q,arg,wk.consume(v,q,arg)

def train_data(c,g,n):
    family=FAMILIES[int(torch.randint(len(FAMILIES),(),generator=g))]
    L=LENGTHS[int(torch.randint(len(LENGTHS),(),generator=g))]
    seed=int(torch.randint(2**30,(),generator=g))
    b,p,aliases,v,args=ev.bank(c,family,L,seed,n)
    pairs=torch.rand(n,8,generator=g).argsort(-1).reshape(n,4,2)
    alias=torch.randint(2,(n,4),generator=g)
    repeats=torch.rand(n,4,generator=g)<.5
    second=torch.where(repeats[:,:,None],pairs,pairs.roll(1,1))
    second_alias=torch.randint(2,(n,4),generator=g)
    qwork=query_bank(v,g)
    q1=query_bank(b.world.gather(1,pairs.reshape(n,8)).reshape(-1,2),g)
    q2=query_bank(b.world.gather(1,second.reshape(n,8)).reshape(-1,2),g)
    return b,p,aliases,pairs,alias,second,second_alias,(qwork,q1,q2),{'family':family,'length':L,'seed':seed}

def read_loss(base,h,queries,roles):
    q,arg,y=queries
    return sum(F.cross_entropy(a.read(h[i],q,arg),y)+.2*F.cross_entropy(a.private(h[i]),roles[:,i])
               for i,a in enumerate(base.agents))/2

def losses(m,data):
    b,p,aliases,pairs,alias,second,second_alias,queries,meta=data
    # Evaluation of the prefix is identical in both arms; gradients differ.
    h=native_prefix(m.base,b,p,aliases)
    work=read_loss(m.base,h,queries[0],b.roles)
    expanded=[x[:,None,:].expand(-1,4,-1).reshape(-1,m.c.width) for x in h]
    roles=b.roles[:,None,:].expand(-1,4,-1).reshape(-1,2)
    r=m.retrieve(expanded,pairs.reshape(-1,2),alias.flatten())
    first=read_loss(m.base,r,queries[1],roles)
    r=m.retrieve(r,second.reshape(-1,2),second_alias.flatten())
    secondloss=read_loss(m.base,r,queries[2],roles)
    return work+(first+secondloss)/2,work,first,secondloss

def source_hashes():
    names=('access_repair.py','working.py','selective.py','gated_selective.py','cyclic_selective.py','noninterference.py','evaluate_noninterference.py')
    return {f'src/{name}':sha(ROOT/'src'/name) for name in names}

def save_checkpoint(out,obj):
    # Stable internal archive filename makes independent same-environment replay comparable.
    tmp=out/'checkpoint.tmp';torch.save(obj,tmp);os.replace(tmp,out/'checkpoint.pt')

def train(parent:Path,out:Path,arm:str,seed:int,steps=1000,batch=96,lr=.0003,stop=None,resume=False):
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    base=wk.load(parent);m=Repair(base);m.set_arm(arm)
    g=torch.Generator().manual_seed(seed+1)
    opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=lr,weight_decay=1e-5)
    spec={'arm':arm,'seed':seed,'steps':steps,'batch':batch,'lr':lr,'weight_decay':1e-5}
    sources=source_hashes();parent_hash=sha(parent);start=0;meter={}
    initial_base=tensor_digest(m.base.state_dict())
    if resume:
        ck=torch.load(out/'checkpoint.pt',weights_only=False)
        if ck['specification']!=spec or ck['sources']!=sources or ck['parent_sha256']!=parent_hash:raise ValueError('resume source/config/input mismatch')
        m.load_state_dict(ck['model']);opt.load_state_dict(ck['optimizer']);g.set_state(ck['data_rng']);torch.set_rng_state(ck['torch_rng']);start=ck['step'];meter=ck['meter']
    else:
        if out.exists():raise FileExistsError(out)
        out.mkdir(parents=True)
    record={'status':'RUNNING','parent_sha256':parent_hash,'parent_name':parent.name,'specification':spec,
            'config':dataclasses.asdict(m.c),'sources':sources,'initial_base_tensor_digest':initial_base,
            'total_parameters':sum(p.numel() for p in m.parameters()),'trainable_parameters':sum(p.numel() for p in m.parameters() if p.requires_grad),
            'original_parameters':sum(p.numel() for p in m.base.parameters()),'copied_parameters':sum(p.numel() for p in m.access.parameters()),
            'command':sys.argv,'started_at':time.time(),'environment':{'python':sys.version,'torch':torch.__version__,'numpy':np.__version__,'threads':1},
            'claim_eligible_primary':False}
    atomic_json(out/'run.json',record);begin=time.monotonic();end=steps if stop is None else min(stop,steps)
    for step in range(start,end):
        m.train();data=train_data(m.c,g,batch)
        key=f"{data[-1]['family']}_{data[-1]['length']}";meter[key]=meter.get(key,0)+1
        vals=losses(m,data);loss=vals[0]
        if not bool(torch.isfinite(loss)):raise FloatingPointError('nonfinite loss')
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_([p for p in m.parameters() if p.requires_grad],1.);opt.step()
        if (step+1)%100==0 or step+1==end:
            row={'step':step+1,'arm':arm,'seed':seed,'losses':[float(v.detach()) for v in vals], 'elapsed_seconds':time.monotonic()-begin}
            with (out/'training.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(row),flush=True)
            save_checkpoint(out,{'version':'0.6','config':dataclasses.asdict(m.c),'specification':spec,'model':m.state_dict(),'optimizer':opt.state_dict(),
                                 'data_rng':g.get_state(),'torch_rng':torch.get_rng_state(),'step':step+1,'meter':meter,
                                 'sources':sources,'parent_sha256':parent_hash})
    digest=tensor_digest(m.base.state_dict())
    record.update(status='COMPLETED' if end==steps else 'PAUSED',last_step=end,elapsed_seconds=time.monotonic()-begin,
                  final_base_tensor_digest=digest,base_exactly_unchanged=digest==initial_base,
                  sources_unchanged=sources==source_hashes(),parent_unchanged=sha(parent)==parent_hash,
                  checkpoint_sha256=sha(out/'checkpoint.pt'),finished_at=time.time(),meter=meter)
    atomic_json(out/'run.json',record)
    if not record['sources_unchanged'] or not record['parent_unchanged']:raise RuntimeError('input drift')
    if arm=='access' and not record['base_exactly_unchanged']:raise RuntimeError('frozen base changed')
    return m

def load(path):
    ck=torch.load(path,weights_only=False)
    if ck.get('version')=='0.6':
        base=wk.Dyad(wk.Config(**ck['config']));m=Repair(base);m.load_state_dict(ck['model']);m.set_arm(ck['specification']['arm'])
    else:
        m=Repair(wk.load(path));m.set_arm('access')
    m.eval();return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('parent',type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--arm',choices=('access','joint'),required=True);p.add_argument('--seed',required=True,type=int)
    p.add_argument('--steps',default=1000,type=int);p.add_argument('--batch',default=96,type=int);p.add_argument('--lr',default=.0003,type=float)
    p.add_argument('--stop',type=int);p.add_argument('--resume',action='store_true');a=p.parse_args()
    train(a.parent,a.out,a.arm,a.seed,a.steps,a.batch,a.lr,a.stop,a.resume)
if __name__=='__main__':main()
