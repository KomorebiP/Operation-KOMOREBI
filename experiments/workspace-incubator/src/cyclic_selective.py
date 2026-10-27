"""Return-cue coherence repair, using the same neural architecture and parameters.
All changes are task-distribution and continuation-training changes. No protected
memory bank, latent target or designated workspace coordinates are introduced.
"""
from __future__ import annotations
import argparse,dataclasses,json,os,platform,sys,time
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import selective as base
import gated_selective as gated
from selective import sha,atomic_json,targets

@dataclasses.dataclass(frozen=True)
class Config(gated.Config):
    stages:int=3
    def __post_init__(self):
        super().__post_init__()
        if self.stages<2:raise ValueError('at least2 cue stages')

def make_batch(c,g,n,extra=2,stages=None,mode='mixed'):
    b=base.make_batch(c,g,n,extra);S=c.stages if stages is None else stages
    cues=torch.rand(n,S,c.objects,generator=g).argsort(-1)[:,:,:2]
    if mode=='mixed':
        repeat=torch.rand(n,generator=g)<.25
        cues[:,1]=torch.where(repeat[:,None],cues[:,0],cues[:,1])
        if S>=3:
            return_mask=torch.rand(n,generator=g)<.5
            cues[:,-1]=torch.where(return_mask[:,None],cues[:,0],cues[:,-1])
    elif mode=='cycle':
        cues[:,0]=b.cues[:,0];cues[:,1]=b.cues[:,1];cues[:,-1]=cues[:,0]
    elif mode=='repeat':
        cues[:]=cues[:,0,None]
    elif mode!='random':raise ValueError(mode)
    q=torch.randint(4,(n,S),generator=g);arg=torch.randint(4,(n,S),generator=g)
    for s in range(S):
        values=b.world.gather(1,cues[:,s]);pair=values[:,0]+2*values[:,1]
        same=torch.randint(2,(n,),generator=g).bool()
        proposal=torch.where(same,pair,(pair+torch.randint(1,4,(n,),generator=g))%4)
        arg[:,s]=torch.where(q[:,s]==3,proposal,arg[:,s])
    b.cues=cues;b.cue_aliases=torch.randint(2,(n,S),generator=g);b.q=q;b.arg=arg
    return b

class Dyad(gated.Dyad):
    def forward(self,b,mode='intact',delay=None):
        h=self.encode(b,mode);answers=[];private=[]
        for s in range(b.cues.shape[1]):
            h=self.cue(h,b.cues[:,s],b.cue_aliases[:,s],mode,delay)
            answers.append([a.read(h[i],b.q[:,s],b.arg[:,s]) for i,a in enumerate(self.agents)])
            private.append([a.private(h[i]) for i,a in enumerate(self.agents)])
        return answers,private

@torch.no_grad()
def evaluate(m,seed,n=2048,extra=2,stages=3,cue_mode='mixed',mode='intact',delay=2,save=None):
    g=torch.Generator().manual_seed(seed);tally=torch.zeros(stages,2,4,dtype=torch.long);counts=torch.zeros(stages,4,dtype=torch.long);priv=torch.zeros(stages,2,dtype=torch.long);arrays=[]
    for start in range(0,n,256):
        b=make_batch(m.c,g,min(n-start,256),extra,stages,cue_mode);ans,pr=m(b,mode,delay);pred=[];ys=[];ps=[]
        for s in range(stages):
            y=targets(b.world,b.cues[:,s],b.q[:,s],b.arg[:,s]);p=torch.stack([v.argmax(-1) for v in ans[s]]);pp=torch.stack([v.argmax(-1) for v in pr[s]])
            for q in range(4):
                mask=b.q[:,s]==q;counts[s,q]+=mask.sum();tally[s,:,q]+=(p[:,mask]==y[mask]).sum(1)
            priv[s]+=(pp==b.roles.T).sum(1);pred.append(p.T.numpy());ys.append(y.numpy());ps.append(pp.T.numpy())
        arrays.append({'pred':np.stack(pred,1),'target':np.stack(ys,1),'private_pred':np.stack(ps,1),'world':b.world.numpy(),'roles':b.roles.numpy(),'cues':b.cues.numpy(),'q':b.q.numpy(),'arg':b.arg.numpy(),'events':b.events.numpy()})
    rates=tally/counts[:,None,:].clamp_min(1)
    result={'n':n,'stages':stages,'cue_mode':cue_mode,'mode':mode,'delay':delay,'extra':extra,'accuracy':float(tally.sum()/(2*stages*n)),'min_cell':float(rates.min()),'per_stage_agent_query':rates.tolist(),'stage_accuracy':(tally.sum((1,2))/(2*n)).tolist(),'private_accuracy':(priv/n).tolist(),'counts':counts.tolist(),'seed':seed}
    if save:np.savez_compressed(save,**{k:np.concatenate([a[k] for a in arrays]) for k in arrays[0]})
    return result

def train(parent:Path,out:Path,seed=290601,steps=3000):
    if out.exists():raise FileExistsError(out)
    torch.set_num_threads(1);torch.manual_seed(seed);torch.use_deterministic_algorithms(True)
    prior=torch.load(parent,weights_only=False)
    c=Config(**dict(prior['config'],steps=steps,seed=seed,lr=.001,curriculum=False,stages=3))
    m=Dyad(c);m.load_state_dict(prior['model']);opt=torch.optim.AdamW(m.parameters(),lr=c.lr,weight_decay=1e-5)
    opt.load_state_dict(prior['optimizer'])
    for group in opt.param_groups:group['lr']=c.lr
    g=torch.Generator().manual_seed(seed+1);out.mkdir(parents=True)
    manifest={'status':'STARTED','claim_eligible':False,'config':dataclasses.asdict(c),'source_sha256':sha(Path(__file__)),'gated_source_sha256':sha(Path(gated.__file__)),'base_source_sha256':sha(Path(base.__file__)),'parent_sha256':sha(parent),'parent_path':str(parent),'parent_steps':prior['step'],'additional_steps':steps,'parameters':sum(p.numel() for p in m.parameters()),'command':sys.argv,'started_unix':time.time(),'environment':{'python':sys.version,'torch':torch.__version__,'numpy':np.__version__,'platform':platform.platform(),'threads':1,'cuda':False},'change':'terminal task distribution now includes overlapping, repeated and return cues, no neural architecture change'}
    atomic_json(out/'run.json',manifest)
    # Evaluate the unmodified parent under the new distribution before any training.
    initial={k:evaluate(m,seed+21000,n=1024,stages=S,cue_mode=mode) for k,S,mode in [('ordinary',3,'mixed'),('cycle',3,'cycle'),('repeat',2,'repeat')]}
    atomic_json(out/'parent_new_task.json',initial);begin=time.monotonic()
    for step in range(steps):
        extra=int(torch.randint(3,(),generator=g));b=make_batch(c,g,c.batch,extra);m.train();ans,pr=m(b)
        loss=sum(F.cross_entropy(ans[s][i],targets(b.world,b.cues[:,s],b.q[:,s],b.arg[:,s]))+.2*F.cross_entropy(pr[s][i],b.roles[:,i]) for s in range(3) for i in (0,1))/6
        if not torch.isfinite(loss):raise FloatingPointError('nonfinite loss')
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step()
        if (step+1)%250==0 or step+1==steps:
            m.eval();v=evaluate(m,seed+10000,n=512);row={'step':step+1,'loss':float(loss.detach()),'validation':v,'elapsed':time.monotonic()-begin}
            with (out/'training.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps({'seed':seed,'step':step+1,'loss':row['loss'],'accuracy':v['accuracy'],'min_cell':v['min_cell'],'elapsed':row['elapsed']}),flush=True)
            ck={'config':dataclasses.asdict(c),'model':m.state_dict(),'optimizer':opt.state_dict(),'data_rng':g.get_state(),'torch_rng':torch.get_rng_state(),'step':step+1,'source_sha256':manifest['source_sha256']};tmp=out/'checkpoint.tmp';torch.save(ck,tmp);os.replace(tmp,out/'checkpoint.pt')
    m.eval();results={}
    cases=[('ordinary',3,'mixed','intact',2,2),('cycle3',3,'cycle','intact',2,2),('repeat2',2,'repeat','intact',2,2),('random5',5,'random','intact',2,2),('cycle8',8,'cycle','intact',2,2),('delay6',3,'mixed','intact',6,2),('longer',3,'mixed','intact',2,5),('cut',3,'mixed','cut',2,2),('shuffle',3,'mixed','shuffle',2,2)]
    for name,S,cm,mode,delay,extra in cases:results[name]=evaluate(m,seed+21000,n=2048,stages=S,cue_mode=cm,mode=mode,delay=delay,extra=extra,save=out/(name+'.npz'))
    atomic_json(out/'behavior.json',results);manifest.update(status='COMPLETED',finished_unix=time.time(),checkpoint_sha256=sha(out/'checkpoint.pt'),source_unchanged=sha(Path(__file__))==manifest['source_sha256'],parent_unchanged=sha(parent)==manifest['parent_sha256']);atomic_json(out/'run.json',manifest)

def main():
    p=argparse.ArgumentParser();p.add_argument('parent',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=290601);p.add_argument('--steps',type=int,default=3000);a=p.parse_args();train(a.parent,a.out,a.seed,a.steps)
if __name__=='__main__':main()
