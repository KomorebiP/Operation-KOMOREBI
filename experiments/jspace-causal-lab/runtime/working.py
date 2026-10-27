"""Native temporary computations over retained eight-fact memory.

Development successor to v0.3, not original RRCT v0.62 primary. The only new
neural mechanism is a generic operation-conditioned residual map. It has access
to every hidden coordinate, with no semantic axes or protected memory tensor.
"""
from __future__ import annotations
import argparse, dataclasses, json, os, platform, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import selective as base
import gated_selective as gated
import cyclic_selective as cyc
from selective import sha, atomic_json

@dataclasses.dataclass(frozen=True)
class Config(cyc.Config):
    work_exchanges:int=1
    work_width:int=128
    max_program:int=3
    def __post_init__(self):
        super().__post_init__()
        if self.work_exchanges<0 or self.work_width<1 or self.max_program<0:
            raise ValueError('invalid working configuration')

@dataclasses.dataclass
class Batch(base.Batch):
    programs:torch.Tensor
    op_aliases:torch.Tensor
    @property
    def size(self): return len(self.events)
    def clone(self):
        return Batch(**{f.name:getattr(self,f.name).clone() for f in dataclasses.fields(self)})
    def slice(self,ix):
        return Batch(**{f.name:getattr(self,f.name)[ix] for f in dataclasses.fields(self)})


def apply_ops(pair:torch.Tensor, programs:torch.Tensor)->torch.Tensor:
    """Evaluator only. -1 absent, 0 identity, 1 flip-left, 2 flip-right, 3 swap."""
    out=pair.clone()
    for t in range(programs.shape[1]):
        op=programs[:,t]
        left=out[:,0]; right=out[:,1]
        nl=torch.where(op==1,1-left,torch.where(op==3,right,left))
        nr=torch.where(op==2,1-right,torch.where(op==3,left,right))
        out=torch.stack([nl,nr],1)
    return out


def working_values(b:Batch,s:int)->torch.Tensor:
    return apply_ops(b.world.gather(1,b.cues[:,s]),b.programs[:,s])


def consume(pair,q,arg):
    value=pair[:,0]+2*pair[:,1]
    return torch.where(q==0,value,torch.where(q==1,pair[:,0]^pair[:,1],
           torch.where(q==2,value^arg,(value==arg).long())))


def make_queries(b:Batch,g:torch.Generator,balanced:bool=False)->None:
    n,S=b.cues.shape[:2]
    b.q=torch.randint(4,(n,S),generator=g)
    if balanced:
        for s in range(S): b.q[:,s]=(torch.arange(n)+s)%4
    b.arg=torch.zeros(n,S,dtype=torch.long)
    for s in range(S):
        v=working_values(b,s);v=v[:,0]+2*v[:,1]
        mask=torch.randint(4,(n,),generator=g)
        same=torch.randint(2,(n,),generator=g).bool()
        proposal=torch.where(same,v,(v+torch.randint(1,4,(n,),generator=g))%4)
        b.arg[:,s]=torch.where(b.q[:,s]==2,mask,torch.where(b.q[:,s]==3,proposal,0))


def make_batch(c,g,n,extra=2,max_program=None,stages=3,cue_mode='mixed',program_mode='random',balanced=False):
    # cyc generates queries as well, but all queries/arguments are discarded and
    # regenerated jointly AFTER the actual working semantics have been fixed.
    old=cyc.make_batch(c,g,n,extra,stages,cue_mode)
    L=c.max_program if max_program is None else max_program
    prog=torch.randint(4,(n,stages,L),generator=g)
    lens=torch.randint(L+1,(n,stages),generator=g)
    if L: prog=torch.where(torch.arange(L)[None,None,:]<lens[:,:,None],prog,-1)
    # The final request is always a pure factual reload, with no temporary ops.
    prog[:,-1,:]=-1
    if program_mode=='fixed':
        prog[:,:-1,:]=torch.randint(4,(n,stages-1,L),generator=g)
    elif program_mode=='identity': prog.fill_(-1)
    elif program_mode=='flip_twice':
        if L!=2:raise ValueError('flip_twice requires length2')
        prog[:,:-1,0]=1;prog[:,:-1,1]=1
    elif program_mode=='swap_twice':
        if L!=2:raise ValueError('swap_twice requires length2')
        prog[:,:-1,0]=3;prog[:,:-1,1]=3
    elif program_mode!='random':raise ValueError(program_mode)
    b=Batch(**{f.name:getattr(old,f.name) for f in dataclasses.fields(base.Batch)},
        programs=prog,op_aliases=torch.randint(2,(n,stages,L),generator=g))
    make_queries(b,g,balanced)
    return b

class Agent(gated.Agent):
    def __init__(self,c):
        super().__init__(c)
        self.work_embedding=nn.Embedding(8,2*c.embedding)
        self.work_state=nn.Linear(c.width,c.work_width)
        self.work_context=nn.Linear(2*c.embedding,c.work_width)
        self.work_out=nn.Linear(c.work_width,c.width)
        # Initial operation update is exactly identity; its representation learns.
        nn.init.zeros_(self.work_out.weight);nn.init.zeros_(self.work_out.bias)
    def work(self,h,op,alias):
        ctx=self.work_embedding(2*op.clamp_min(0)+alias)
        delta=self.work_out(torch.tanh(self.work_state(h))*torch.sigmoid(self.work_context(ctx)))
        return h+delta

class Dyad(gated.Dyad):
    def __init__(self,c):
        nn.Module.__init__(self);self.c=c;self.agents=nn.ModuleList([Agent(c),Agent(c)])
    def operate(self,h,op,alias,mode='intact',exchange=True):
        active=op>=0
        if not active.any():return h
        new=[a.work(h[i],op,alias) for i,a in enumerate(self.agents)]
        if exchange:
            for _ in range(self.c.work_exchanges):new=self.exchange(new,mode)
        return [torch.where(active[:,None],new[i],h[i]) for i in (0,1)]
    def program(self,h,programs,aliases,mode='intact'):
        for t in range(programs.shape[1]):h=self.operate(h,programs[:,t],aliases[:,t],mode)
        return h
    def silent(self,h,delay=None):
        for _ in range(self.c.delay if delay is None else delay):
            h=[a.observe(a.blank_input(len(h[i])),h[i]) for i,a in enumerate(self.agents)]
        return h
    def stage(self,h,cue,alias,programs,op_aliases,mode='intact',delay=None):
        h=self.cue(h,cue,alias,mode,delay=0)
        h=self.program(h,programs,op_aliases,mode)
        return self.silent(h,delay)
    def forward(self,b,mode='intact',delay=None,return_states=False):
        h=self.encode(b,mode);answers=[];private=[];states=[]
        for s in range(b.cues.shape[1]):
            h=self.stage(h,b.cues[:,s],b.cue_aliases[:,s],b.programs[:,s],b.op_aliases[:,s],mode,delay)
            answers.append([a.read(h[i],b.q[:,s],b.arg[:,s]) for i,a in enumerate(self.agents)])
            private.append([a.private(h[i]) for i,a in enumerate(self.agents)]);states.append(h)
        return (answers,private,states) if return_states else (answers,private)

@torch.no_grad()
def evaluate(m,seed,n=2048,extra=2,max_program=3,stages=3,cue_mode='mixed',program_mode='random',mode='intact',delay=2,save=None):
    g=torch.Generator().manual_seed(seed);parts=[]
    tally=torch.zeros(stages,2,4,dtype=torch.long);counts=torch.zeros(stages,4,dtype=torch.long);pc=torch.zeros(stages,2,dtype=torch.long)
    for start in range(0,n,256):
        b=make_batch(m.c,g,min(256,n-start),extra,max_program,stages,cue_mode,program_mode,True)
        ans,pr=m(b,mode,delay);pred=[];truth=[];pp=[];vals=[]
        for s in range(stages):
            v=working_values(b,s);y=consume(v,b.q[:,s],b.arg[:,s]);p=torch.stack([x.argmax(-1) for x in ans[s]],1);r=torch.stack([x.argmax(-1) for x in pr[s]],1)
            for q in range(4):
                mask=b.q[:,s]==q;counts[s,q]+=mask.sum();tally[s,:,q]+=(p[mask]==y[mask,None]).sum(0)
            pc[s]+=(r==b.roles).sum(0);pred.append(p.numpy());truth.append(y.numpy());pp.append(r.numpy());vals.append(v.numpy())
        if save:
            parts.append(dict(pred=np.stack(pred,1),target=np.stack(truth,1),private_pred=np.stack(pp,1),working=np.stack(vals,1),
                **{f.name:getattr(b,f.name).numpy() for f in dataclasses.fields(Batch)}))
    rates=tally/counts[:,None,:].clamp_min(1)
    result=dict(seed=seed,n=n,stages=stages,max_program=max_program,program_mode=program_mode,cue_mode=cue_mode,extra=extra,mode=mode,delay=delay,
        accuracy=float(tally.sum()/(2*n*stages)),min_cell=float(rates.min()),per_stage_agent_query=rates.tolist(),
        stage_accuracy=(tally.sum((1,2))/(2*n)).tolist(),private_accuracy=(pc/n).tolist(),counts=counts.tolist())
    if save:np.savez_compressed(save,**{k:np.concatenate([p[k] for p in parts]) for k in parts[0]})
    return result

def source_hashes():
    return {p.name:sha(p) for p in [Path(__file__),Path(base.__file__),Path(gated.__file__),Path(cyc.__file__)]}

def load(path):
    ck=torch.load(path,weights_only=False);m=Dyad(Config(**ck['config']));m.load_state_dict(ck['model']);m.eval();return m

def final_banks(m,seed,out,n=2048):
    specs=[('ordinary',3,'mixed','random',3,'intact',2),('cycle3',3,'cycle','random',3,'intact',2),
        ('repeat3',3,'repeat','random',3,'intact',2),('program6',6,'cycle','fixed',3,'intact',2),
        ('program12',12,'cycle','fixed',3,'intact',2),('cycle8',3,'cycle','random',8,'intact',2),
        ('delay6',3,'cycle','random',3,'intact',6),('no_work',0,'cycle','identity',3,'intact',2),
        ('flip_twice',2,'cycle','flip_twice',3,'intact',2),('swap_twice',2,'cycle','swap_twice',3,'intact',2),
        ('cut',3,'cycle','random',3,'cut',2),('cut_AtoB',3,'cycle','random',3,'cut_AtoB',2),('cut_BtoA',3,'cycle','random',3,'cut_BtoA',2)]
    results={}
    for name,L,cm,pm,S,mode,delay in specs:
        results[name]=evaluate(m,seed,n=n,max_program=L,cue_mode=cm,program_mode=pm,stages=S,mode=mode,delay=delay,save=out/(name+'.npz'))
    atomic_json(out/'behavior.json',results)
    return results

def train(parent,out,seed=310401,steps=3000,arm=None,resume=False,stop=None,batch=128):
    torch.set_num_threads(1);torch.manual_seed(seed);torch.use_deterministic_algorithms(True)
    ck0=torch.load(parent,weights_only=False)
    d=dict(ck0['config']);d.update(seed=seed,steps=steps,lr=.001,stages=3,curriculum=False,batch=batch)
    if arm:d['arm']=arm
    c=Config(**d);m=Dyad(c)
    missing,unexpected=m.load_state_dict(ck0['model'],strict=False)
    if unexpected or any('.work_' not in x for x in missing):raise ValueError((missing,unexpected))
    opt=torch.optim.AdamW(m.parameters(),lr=c.lr,weight_decay=1e-5);g=torch.Generator().manual_seed(seed+1)
    first=0;sources=source_hashes();begin=time.monotonic()
    if out.exists():
        if not resume:raise FileExistsError(out)
        run=json.loads((out/'run.json').read_text());ck=torch.load(out/'checkpoint.pt',weights_only=False)
        if run['sources']!=sources or ck['config']!=dataclasses.asdict(c):raise ValueError('changed source/config')
        m.load_state_dict(ck['model']);opt.load_state_dict(ck['optimizer']);g.set_state(ck['data_rng']);torch.set_rng_state(ck['torch_rng']);first=ck['step']
    else:
        out.mkdir(parents=True)
        run=dict(status='STARTED',claim_eligible=False,design='native working operations, no latent targets',config=dataclasses.asdict(c),
          parameters=sum(x.numel() for x in m.parameters()),parent_sha256=sha(parent),parent_path=str(parent),parent_step=ck0['step'],
          sources=sources,optimizer='AdamW restarted for all parameters; no freeze',command=sys.argv,started_unix=time.time(),
          seeds=dict(training=seed+1,development=seed+10000,behavior=seed+20000),
          environment=dict(python=sys.version,torch=torch.__version__,numpy=np.__version__,platform=platform.platform(),threads=1,cuda=False))
        atomic_json(out/'run.json',run)
        m.eval();atomic_json(out/'initial.json',{k:evaluate(m,seed+10000,n=512,max_program=L) for k,L in [('no_work',0),('working3',3)]})
    end=min(steps,stop or steps)
    for step in range(first,end):
        L=1 if step<500 else (2 if step<1000 else c.max_program)
        b=make_batch(c,g,c.batch,extra=int(torch.randint(3,(),generator=g)),max_program=L)
        m.train();ans,pr=m(b)
        loss=sum(F.cross_entropy(ans[s][i],consume(working_values(b,s),b.q[:,s],b.arg[:,s]))+.2*F.cross_entropy(pr[s][i],b.roles[:,i]) for s in range(3) for i in (0,1))/6
        if not torch.isfinite(loss):raise FloatingPointError('loss')
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step()
        if (step+1)%250==0 or step+1==end:
            m.eval();val=evaluate(m,seed+10000,n=512,max_program=3)
            row=dict(step=step+1,loss=float(loss.detach()),max_training_program=L,validation=val,elapsed_invocation=time.monotonic()-begin)
            with (out/'training.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps({k:row[k] for k in ['step','loss','max_training_program','elapsed_invocation']}|dict(seed=seed,accuracy=val['accuracy'],stage=val['stage_accuracy'])),flush=True)
            state=dict(config=dataclasses.asdict(c),model=m.state_dict(),optimizer=opt.state_dict(),data_rng=g.get_state(),torch_rng=torch.get_rng_state(),step=step+1,source_hashes=sources)
            tmp=out/'checkpoint.tmp';torch.save(state,tmp);os.replace(tmp,out/'checkpoint.pt')
    if end==steps:
        m.eval();res=final_banks(m,seed+20000,out)
        run.update(status='COMPLETED',finished_unix=time.time(),final_step=steps,sources_unchanged=source_hashes()==sources,parent_unchanged=sha(parent)==run['parent_sha256'],checkpoint_sha256=sha(out/'checkpoint.pt'),behavior_sha256=sha(out/'behavior.json'))
        atomic_json(out/'run.json',run)
    else:
        run.update(status='PAUSED_AT_REQUESTED_BOUND',last_step=end);atomic_json(out/'run.json',run)
    return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('parent',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=310401);p.add_argument('--steps',type=int,default=3000);p.add_argument('--batch',type=int,default=128);p.add_argument('--stop',type=int);p.add_argument('--resume',action='store_true');p.add_argument('--arm',choices=['full_wire','full_private']);a=p.parse_args();train(a.parent,a.out,a.seed,a.steps,a.arm,a.resume,a.stop,a.batch)
if __name__=='__main__':main()
