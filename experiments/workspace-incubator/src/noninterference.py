"""Matched native-memory noninterference continuation, adaptive development v0.5.

No model architecture changes. The two arms differ only in working programs:
independent random words versus 50% inverse-palindrome words. Both train the
same late consumers, private recall, and four independent all-fact reloads.
The latter are terminal readouts, not targets on hidden coordinates.
"""
from __future__ import annotations
import argparse, dataclasses, hashlib, json, os, platform, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import working as wk
from selective import atomic_json, sha

ROOT=Path(__file__).resolve().parents[1]


def neutralize(programs:torch.Tensor, mask:torch.Tensor)->torch.Tensor:
    """Every opcode is an involution. First half followed by its reverse is identity.
    Neutralization preserves program length, including an identity center if odd.
    All entries must be actual operations, rather than padding (-1).
    """
    if programs.ndim!=3 or mask.shape!=programs.shape[:2]:
        raise ValueError('expected (batch,stages,length) and (batch,stages)')
    if bool(((programs<0)|(programs>3)).any()):raise ValueError('native opcodes 0..3 required')
    L=programs.shape[-1]; k=L//2
    first=programs[...,:k]
    center=torch.zeros_like(programs[...,k:k+1]) if L%2 else programs[...,0:0]
    word=torch.cat((first,center,first.flip(-1)),-1)
    return torch.where(mask[...,None],word,programs)


def schedule(step:int)->tuple[int,...]:
    if step<200:return (2,4,6)
    return (2,4,6,8,12)


def train_batch(c,g,step:int,arm:str,n:int):
    if arm not in ('random','neutral'):raise ValueError(arm)
    ls=schedule(step);L=ls[int(torch.randint(len(ls),(),generator=g))]
    extra=int(torch.randint(3,(),generator=g))
    b=wk.make_batch(c,g,n,extra=extra,max_program=L,stages=3,cue_mode='mixed',program_mode='fixed')
    # Draw all random choices in both arms before transforming any program.
    mask=torch.rand(n,2,generator=g)<.5
    if arm=='neutral':b.programs[:,:2]=neutralize(b.programs[:,:2],mask)
    # Replace previous query arguments jointly with targets, avoiding stale proposal leakage.
    wk.make_queries(b,g)
    pairs=torch.rand(n,8,generator=g).argsort(-1).reshape(n,4,2)
    aliases=torch.randint(2,(n,4),generator=g)
    return b,pairs,aliases,dict(length=L,neutral_mask=int(mask.sum()) if arm=='neutral' else 0)


def loss_for(m,b,pairs,aliases):
    ans,priv,states=m(b,return_states=True)
    task=sum(F.cross_entropy(ans[s][i],wk.consume(wk.working_values(b,s),b.q[:,s],b.arg[:,s]))
             +.2*F.cross_entropy(priv[s][i],b.roles[:,i]) for s in range(3) for i in (0,1))/6
    # Four branches each begin at the same post-program state. They do not overwrite
    # each other. This tests all eight facts, beyond the originally active pair.
    z=torch.zeros(b.size,dtype=torch.long);mem=0.
    for j in range(4):
        h=m.cue(states[1],pairs[:,j],aliases[:,j])
        p=b.world.gather(1,pairs[:,j]);y=p[:,0]+2*p[:,1]
        for i,a in enumerate(m.agents):
            mem=mem+F.cross_entropy(a.read(h[i],z,z),y)+.2*F.cross_entropy(a.private(h[i]),b.roles[:,i])
    mem=mem/8
    return task+.5*mem,task,mem


def source_hashes():
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src').glob('*.py'))
            if p.name in ('noninterference.py','working.py','selective.py','gated_selective.py','cyclic_selective.py')}


def tensor_digest(state):
    h=hashlib.sha256()
    for k,v in sorted(state.items()):h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def train(parent:Path,out:Path,arm:str,seed:int,steps:int=1500,batch:int=96,lr:float=.0003,stop:int|None=None,resume:bool=False):
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    prior=torch.load(parent,weights_only=False)
    conf=dict(prior['config']);conf.update(seed=seed,steps=steps,batch=batch,lr=lr,max_program=12)
    c=wk.Config(**conf);m=wk.Dyad(c);m.load_state_dict(prior['model'])
    opt=torch.optim.AdamW(m.parameters(),lr=lr,weight_decay=1e-5)
    g=torch.Generator().manual_seed(seed+1);first=0;frozen=source_hashes()
    specification=dict(arm=arm,seed=seed,steps=steps,batch=batch,lr=lr,memory_loss_weight=.5)
    if out.exists():
        if not resume:raise FileExistsError(out)
        rec=json.loads((out/'run.json').read_text());ck=torch.load(out/'checkpoint.pt',weights_only=False)
        if rec['sources']!=frozen or rec['specification']!=specification or rec['parent_sha256']!=sha(parent):
            raise ValueError('source/config/parent changed on resume')
        m.load_state_dict(ck['model']);opt.load_state_dict(ck['optimizer']);g.set_state(ck['data_rng']);torch.set_rng_state(ck['torch_rng']);first=ck['step']
    else:
        out.mkdir(parents=True)
        rec=dict(status='STARTED',specification=specification,config=conf,sources=frozen,
            parent_sha256=sha(parent),parent_name=parent.name,parent_step=prior['step'],
            parameters=sum(p.numel() for p in m.parameters()),started_at=time.time(),command=sys.argv,
            regime='paired adaptive development, not preregistered primary',
            optimizer='AdamW restart, all weights trainable',data_seed=seed+1,
            environment=dict(python=sys.version,torch=torch.__version__,numpy=np.__version__,platform=platform.platform(),threads=1))
        atomic_json(out/'run.json',rec)
    start=time.monotonic();end=min(steps,stop if stop is not None else steps)
    meter={};op_counts=torch.zeros(4,dtype=torch.long)
    for step in range(first,end):
        b,pairs,aliases,meta=train_batch(c,g,step,arm,batch)
        meter[str(meta['length'])]=meter.get(str(meta['length']),0)+1
        op_counts+=torch.bincount(b.programs[:,:2].flatten(),minlength=4)
        m.train();loss,task,mem=loss_for(m,b,pairs,aliases)
        if not bool(torch.isfinite(loss)):raise FloatingPointError('nonfinite loss')
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step()
        if (step+1)%100==0 or step+1==end:
            row=dict(step=step+1,arm=arm,seed=seed,loss=float(loss.detach()),task_loss=float(task.detach()),memory_loss=float(mem.detach()),elapsed=time.monotonic()-start,length_counts=meter,op_counts=op_counts.tolist())
            with (out/'training.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(row),flush=True)
            checkpoint=dict(config=conf,specification=specification,model=m.state_dict(),optimizer=opt.state_dict(),data_rng=g.get_state(),torch_rng=torch.get_rng_state(),step=step+1,source_hashes=frozen)
            tmp=out/'checkpoint.tmp';torch.save(checkpoint,tmp);os.replace(tmp,out/'checkpoint.pt')
    rec.update(status='COMPLETED' if end==steps else 'PAUSED',last_step=end,finished_at=time.time(),invocation_seconds=time.monotonic()-start,
               parent_unchanged=rec['parent_sha256']==sha(parent),sources_unchanged=frozen==source_hashes(),checkpoint_sha256=sha(out/'checkpoint.pt'),model_tensor_sha256=tensor_digest(m.state_dict()))
    atomic_json(out/'run.json',rec)
    if not rec['parent_unchanged'] or not rec['sources_unchanged']:raise RuntimeError('inputs changed')
    return m


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('parent',type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--arm',choices=['random','neutral'],required=True);p.add_argument('--seed',type=int,required=True)
    p.add_argument('--steps',type=int,default=1500);p.add_argument('--batch',type=int,default=96);p.add_argument('--lr',type=float,default=.0003)
    p.add_argument('--stop',type=int);p.add_argument('--resume',action='store_true');a=p.parse_args()
    train(a.parent,a.out,a.arm,a.seed,a.steps,a.batch,a.lr,a.stop,a.resume)
if __name__=='__main__':main()
