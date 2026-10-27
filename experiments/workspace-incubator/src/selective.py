"""Selective access to eight retained facts, with no assigned neural slots.

Executed development successor to Workspace Incubator v0.2. This is not the
original RRCT v0.62 primary and does not implement a vocabulary-linked J-lens.
"""
from __future__ import annotations
import argparse, dataclasses, hashlib, json, os, platform, random, sys, time
from pathlib import Path
from typing import Any
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

ROOT=Path(__file__).resolve().parents[1]

@dataclasses.dataclass(frozen=True)
class Config:
    objects:int=8
    width:int=64
    message:int=8
    embedding:int=12
    batch:int=128
    steps:int=5000
    lr:float=0.002
    event_exchanges:int=1
    cue_exchanges:int=2
    delay:int=2
    seed:int=290301
    arm:str='full_wire'
    curriculum:bool=True
    def __post_init__(self):
        if self.objects<4 or self.objects>16: raise ValueError('objects 4..16')
        if self.arm not in ('full_wire','full_private','split_wire'):raise ValueError('unknown arm')
        if min(self.width,self.message,self.embedding,self.batch,self.steps)<1:raise ValueError('positive sizes')
        if min(self.event_exchanges,self.cue_exchanges,self.delay)<0:raise ValueError('nonnegative steps')

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic_json(p:Path,obj:Any)->None:
    p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n');os.replace(tmp,p)

def transition(world,events):
    """Exact interpreter. Events [kind,destination,source,value,fresh,alias,owner].
    0=set, 1=flip, 2=copy, 3=swap. A supplied freshness flag licenses the update.
    Neural learners receive raw event symbols, never this state or transition.
    """
    out=world.clone();rows=torch.arange(len(world),device=world.device)
    k,d,s,v,f,_,_=events.T
    vd=world[rows,d];vs=world[rows,s]
    new=torch.where(k==0,v,torch.where(k==1,1-vd,vs))
    out[rows,d]=torch.where(f.bool(),new,vd)
    mask=(k==3)&f.bool()
    out[rows[mask],s[mask]]=vd[mask]
    return out

def selected(world,cue):return world.gather(1,cue)
def targets(world,cue,q,arg):
    a=selected(world,cue);pair=a[:,0]+2*a[:,1]
    # report pair, parity, XOR-transform pair by a late mask, verify proposed pair.
    y=torch.where(q==0,pair,torch.where(q==1,a[:,0]^a[:,1],pair^arg))
    return torch.where(q==3,(pair==arg).long(),y)

@dataclasses.dataclass
class Batch:
    events:torch.Tensor
    roles:torch.Tensor
    cues:torch.Tensor
    cue_aliases:torch.Tensor
    q:torch.Tensor
    arg:torch.Tensor
    world:torch.Tensor
    @property
    def size(self):return len(self.events)
    def slice(self,ix):return Batch(**{f.name:getattr(self,f.name)[ix] for f in dataclasses.fields(self)})
    def clone(self):return Batch(**{f.name:getattr(self,f.name).clone() for f in dataclasses.fields(self)})

def make_batch(c:Config,g:torch.Generator,n:int,extra:int=1,active_objects:int|None=None,stale:bool=True):
    objects=c.objects if active_objects is None else active_objects
    if objects<4 or objects>c.objects:raise ValueError('active_objects')
    order=torch.rand(n,objects,generator=g).argsort(1)
    values=torch.randint(2,(n,objects),generator=g)
    ev=torch.zeros(n,objects+extra,7,dtype=torch.long)
    ev[:,:objects,1]=order;ev[:,:objects,2]=order
    ev[:,:objects,3]=values.gather(1,order);ev[:,:objects,4]=1
    if extra:
        ev[:,objects:,0]=torch.randint(2,(n,extra),generator=g) # set or flip
        ev[:,objects:,1]=torch.randint(objects,(n,extra),generator=g)
        ev[:,objects:,2]=torch.randint(objects,(n,extra),generator=g)
        ev[:,objects:,3]=torch.randint(2,(n,extra),generator=g)
        ev[:,objects:,4]=(torch.rand(n,extra,generator=g)>.25).long() if stale else 1
    ev[:,:,5]=torch.randint(2,(n,objects+extra),generator=g)
    ev[:,:,6]=torch.randint(2,(n,objects+extra),generator=g)
    world=torch.zeros(n,c.objects,dtype=torch.long)
    for t in range(ev.shape[1]):world=transition(world,ev[:,t])
    # Two disjoint, ordered relevance pairs. No original observations are replayed.
    ranks=torch.rand(n,objects,generator=g).argsort(1)
    cues=ranks[:,:4].reshape(n,2,2)
    q=torch.randint(4,(n,2),generator=g);arg=torch.randint(4,(n,2),generator=g)
    for stage in (0,1):
        pair=selected(world,cues[:,stage]);pair=pair[:,0]+2*pair[:,1]
        same=torch.randint(2,(n,),generator=g).bool()
        proposal=torch.where(same,pair,(pair+torch.randint(1,4,(n,),generator=g))%4)
        arg[:,stage]=torch.where(q[:,stage]==3,proposal,arg[:,stage])
    return Batch(ev,torch.randint(4,(n,2),generator=g),cues,
                 torch.randint(2,(n,2),generator=g),q,arg,world)

class Agent(nn.Module):
    def __init__(self,c:Config):
        super().__init__();self.c=c;e=c.embedding
        self.name=nn.Embedding(c.objects,e)
        self.command=nn.Embedding(12,e) # 0..7 events, 8/9 cue, 10 blank, 11 unobserved
        self.value=nn.Embedding(4,e) # bit + 2*freshness
        self.input=nn.Linear(4*e,2*e)
        self.observe=nn.GRUCell(2*e,c.width)
        self.role=nn.Embedding(4,c.width)
        self.emit=nn.Linear(c.width,c.message);self.gate=nn.Linear(c.width,1)
        self.receive=nn.GRUCell(c.message,c.width)
        self.query=nn.Embedding(4,e);self.argument=nn.Embedding(4,e)
        self.answer=nn.Sequential(nn.Linear(c.width+2*e,128),nn.Tanh(),nn.Linear(128,4))
        self.private=nn.Linear(c.width,4)
        for cell in (self.observe,self.receive):
            with torch.no_grad():cell.bias_ih[c.width:2*c.width].fill_(1.)
    def event_input(self,event,seen):
        k,d,s,v,f,alias,_=event.T
        inp=torch.cat([self.command(2*k+alias),self.name(d),self.name(s),self.value(v+2*f)],-1)
        absent=torch.cat([self.command(torch.full_like(k,11)),torch.zeros(len(k),3*self.c.embedding)],-1)
        return torch.tanh(self.input(torch.where(seen[:,None],inp,absent)))
    def cue_input(self,cue,alias):
        zeros=torch.zeros(len(cue),self.c.embedding)
        return torch.tanh(self.input(torch.cat([self.command(8+alias),self.name(cue[:,0]),self.name(cue[:,1]),zeros],-1)))
    def blank_input(self,n):
        return torch.tanh(self.input(torch.cat([self.command(torch.full((n,),10,dtype=torch.long)),torch.zeros(n,3*self.c.embedding)],-1)))
    def send(self,h):return torch.sigmoid(self.gate(h))*torch.tanh(self.emit(h))
    def read(self,h,q,arg):return self.answer(torch.cat([h,self.query(q),self.argument(arg)],-1))

class Dyad(nn.Module):
    def __init__(self,c):super().__init__();self.c=c;self.agents=nn.ModuleList([Agent(c),Agent(c)])
    def initial(self,b):return [torch.tanh(a.role(b.roles[:,i])) for i,a in enumerate(self.agents)]
    def exchange(self,h,mode='intact',messages=None):
        m=[a.send(h[i]) for i,a in enumerate(self.agents)] if messages is None else messages
        if self.c.arm=='full_private' or mode=='cut':m=[torch.zeros_like(x) for x in m]
        elif mode=='shuffle':m=[x.roll(1,0) for x in m]
        elif mode=='cut_AtoB':m=[torch.zeros_like(m[0]),m[1]]
        elif mode=='cut_BtoA':m=[m[0],torch.zeros_like(m[1])]
        return [a.receive(m[1-i],h[i]) for i,a in enumerate(self.agents)]
    def event(self,h,event,mode='intact',exchange=True):
        h=[a.observe(a.event_input(event,torch.ones(len(event),dtype=torch.bool) if self.c.arm.startswith('full') else event[:,6]==i),h[i]) for i,a in enumerate(self.agents)]
        if exchange:
            for _ in range(self.c.event_exchanges):h=self.exchange(h,mode)
        return h
    def encode(self,b,mode='intact'):
        h=self.initial(b)
        for t in range(b.events.shape[1]):h=self.event(h,b.events[:,t],mode)
        return h
    def cue(self,h,cue,alias,mode='intact',delay=None,trace=False):
        h=[a.observe(a.cue_input(cue,alias),h[i]) for i,a in enumerate(self.agents)]
        history=[h]
        for _ in range(self.c.cue_exchanges):h=self.exchange(h,mode);history.append(h)
        for _ in range(self.c.delay if delay is None else delay):
            h=[a.observe(a.blank_input(len(cue)),h[i]) for i,a in enumerate(self.agents)];history.append(h)
        return (h,history) if trace else h
    def forward(self,b,mode='intact',delay=None):
        h=self.encode(b,mode);answers=[];private=[]
        for stage in (0,1):
            h=self.cue(h,b.cues[:,stage],b.cue_aliases[:,stage],mode,delay)
            answers.append([a.read(h[i],b.q[:,stage],b.arg[:,stage]) for i,a in enumerate(self.agents)])
            private.append([a.private(h[i]) for i,a in enumerate(self.agents)])
        return answers,private

@torch.no_grad()
def evaluate(m,seed,n=1024,extra=2,mode='intact',delay=None,active_objects=None,save=None):
    g=torch.Generator().manual_seed(seed);rows=[];tally=torch.zeros(2,2,4,dtype=torch.long);counts=torch.zeros(2,4,dtype=torch.long);priv=torch.zeros(2,2,dtype=torch.long)
    for start in range(0,n,256):
        b=make_batch(m.c,g,min(n-start,256),extra,active_objects)
        ans,p=m(b,mode,delay);pred=[];ys=[];pp=[]
        for s in (0,1):
            y=targets(b.world,b.cues[:,s],b.q[:,s],b.arg[:,s]);ps=torch.stack([x.argmax(-1) for x in ans[s]])
            pr=torch.stack([x.argmax(-1) for x in p[s]])
            pred.append(ps.T.numpy());ys.append(y.numpy());pp.append(pr.T.numpy())
            for q in range(4):
                mask=b.q[:,s]==q;counts[s,q]+=mask.sum();tally[s,:,q]+=(ps[:,mask]==y[mask]).sum(1)
            priv[s]+=(pr==b.roles.T).sum(1)
        rows.append(dict(pred=np.stack(pred,1),target=np.stack(ys,1),private_pred=np.stack(pp,1),roles=b.roles.numpy(),world=b.world.numpy(),cues=b.cues.numpy(),q=b.q.numpy(),arg=b.arg.numpy(),events=b.events.numpy()))
    rates=tally/counts[:,None,:].clamp_min(1)
    result=dict(n=n,seed=seed,extra=extra,mode=mode,delay=m.c.delay if delay is None else delay,
      accuracy=float(tally.sum()/(4*n)),per_stage_agent_query=rates.tolist(),stage_accuracy=(tally.sum((1,2))/(2*n)).tolist(),
      min_cell=float(rates.min()),private_accuracy=(priv/n).tolist(),counts=counts.tolist())
    if save:
        np.savez_compressed(save,**{k:np.concatenate([r[k] for r in rows]) for k in rows[0]})
    return result

def train(c,out:Path,resume:bool=False,stop:int|None=None):
    torch.set_num_threads(1);torch.manual_seed(c.seed);np.random.seed(c.seed);random.seed(c.seed);torch.use_deterministic_algorithms(True)
    src=sha(Path(__file__));m=Dyad(c);opt=torch.optim.AdamW(m.parameters(),lr=c.lr,weight_decay=1e-5)
    gen=torch.Generator().manual_seed(c.seed+1);out.mkdir(parents=True,exist_ok=True);ck=out/'checkpoint.pt';first=0
    if ck.exists():
        if not resume:raise FileExistsError(ck)
        state=torch.load(ck,weights_only=False)
        if state['source_sha256']!=src or state['config']!=dataclasses.asdict(c):raise ValueError('config/source changed')
        m.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);gen.set_state(state['data_rng']);torch.set_rng_state(state['torch_rng']);first=state['step']
    else:
        atomic_json(out/'run.json',dict(status='STARTED',claim_eligible=False,config=dataclasses.asdict(c),source_sha256=src,
          command=sys.argv,parameters=sum(p.numel() for p in m.parameters()),started_unix=time.time(),
          environment=dict(python=sys.version,torch=torch.__version__,numpy=np.__version__,platform=platform.platform(),threads=1,cuda=torch.cuda.is_available())))
    begin=time.monotonic()
    for step in range(first,min(c.steps,stop or c.steps)):
        if c.curriculum:
            active=4 if step<600 else (6 if step<1200 else c.objects)
            extra=0 if step<1000 else int(torch.randint(3,(),generator=gen))
        else:active=c.objects;extra=int(torch.randint(3,(),generator=gen))
        b=make_batch(c,gen,c.batch,extra,active);m.train();ans,pr=m(b)
        loss=sum(F.cross_entropy(ans[s][i],targets(b.world,b.cues[:,s],b.q[:,s],b.arg[:,s]))+.2*F.cross_entropy(pr[s][i],b.roles[:,i]) for s in (0,1) for i in (0,1))/4
        if not torch.isfinite(loss):raise FloatingPointError('nonfinite loss')
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step()
        if (step+1)%250==0 or step+1==min(c.steps,stop or c.steps):
            m.eval();val=evaluate(m,c.seed+10000,n=512,extra=min(extra,2),active_objects=active)
            row=dict(step=step+1,loss=float(loss.detach()),active_objects=active,extra=extra,validation=val,elapsed_invocation=time.monotonic()-begin)
            with (out/'training.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(dict(seed=c.seed,arm=c.arm,step=step+1,loss=row['loss'],accuracy=val['accuracy'],min_cell=val['min_cell'],active=active,elapsed=row['elapsed_invocation'])),flush=True)
            state=dict(config=dataclasses.asdict(c),model=m.state_dict(),optimizer=opt.state_dict(),data_rng=gen.get_state(),torch_rng=torch.get_rng_state(),step=step+1,source_sha256=src)
            tmp=out/'checkpoint.tmp';torch.save(state,tmp);os.replace(tmp,ck)
            if step+1 in (1000,2500,c.steps):torch.save(state,out/f'checkpoint_{step+1}.pt')
    if (stop or c.steps)>=c.steps:
        m.eval();result={}
        for name,extra,mode,delay in [('ordinary',2,'intact',2),('no_extra',0,'intact',2),('longer',5,'intact',2),('delay6',2,'intact',6),('cut',2,'cut',2),('shuffle',2,'shuffle',2),('cut_AtoB',2,'cut_AtoB',2),('cut_BtoA',2,'cut_BtoA',2)]:
            result[name]=evaluate(m,c.seed+20000,n=2048,extra=extra,mode=mode,delay=delay,save=out/(name+'.npz'))
        atomic_json(out/'behavior.json',result)
        record=json.loads((out/'run.json').read_text());record.update(status='COMPLETED',final_step=c.steps,source_unchanged=sha(Path(__file__))==src,checkpoint_sha256=sha(ck),behavior_sha256=sha(out/'behavior.json'),finished_unix=time.time());atomic_json(out/'run.json',record)
    return m

def load(path):
    ck=torch.load(path,weights_only=False);m=Dyad(Config(**ck['config']));m.load_state_dict(ck['model']);m.eval();return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seed',type=int,default=290301);p.add_argument('--arm',choices=['full_wire','full_private','split_wire'],default='full_wire');p.add_argument('--steps',type=int,default=5000);p.add_argument('--width',type=int,default=64);p.add_argument('--batch',type=int,default=128);p.add_argument('--stop',type=int);p.add_argument('--resume',action='store_true');p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();train(Config(seed=a.seed,arm=a.arm,steps=a.steps,width=a.width,batch=a.batch),a.out,a.resume,a.stop)
if __name__=='__main__':main()
