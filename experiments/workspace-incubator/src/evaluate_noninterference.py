"""Frozen behavioral and all-fact assays. No hidden-state projection edits.

Exact score definitions are intentionally separate from independent_score.py.
Raw histories and predictions are retained so every score can be recomputed.
"""
from __future__ import annotations
import argparse,dataclasses,json,time
from pathlib import Path
import numpy as np
import torch
import working as wk
from noninterference import neutralize
from selective import sha,atomic_json

LENGTHS=(3,6,12,24,48)
FAMILIES=('random_nonidentity','mirror_identity','identity_tokens','flip_involution','commuting_flips','swap_conjugation')
WORDS={'flip_involution':(1,1),'commuting_flips':(1,2,1,2),'swap_conjugation':(3,1,3,2)}

def actions(p):
    n,L=p.shape
    v=torch.tensor([[0,0],[1,0],[0,1],[1,1]]).repeat(n,1)
    ans=wk.apply_ops(v,p[:,None].expand(n,4,L).reshape(n*4,L)).reshape(n,4,2)
    return ans[:,:,0]+2*ans[:,:,1]

def programs(family,L,n,g):
    if L<0:raise ValueError('nonnegative length')
    if L==0:return torch.empty(n,0,dtype=torch.long)
    if family=='random_nonidentity':
        p=torch.randint(4,(n,L),generator=g)
        bad=(actions(p)==torch.arange(4)).all(1)
        while bool(bad.any()):
            p[bad]=torch.randint(4,(int(bad.sum()),L),generator=g)
            bad=(actions(p)==torch.arange(4)).all(1)
    elif family=='mirror_identity':
        p=torch.randint(4,(n,1,L),generator=g)
        p=neutralize(p,torch.ones(n,1,dtype=torch.bool))[:,0]
    elif family=='identity_tokens':p=torch.zeros(n,L,dtype=torch.long)
    elif family in WORDS:
        w=WORDS[family]
        if L<len(w):raise ValueError('no full neutral relation at this length')
        seq=list(w)*(L//len(w))+[0]*(L%len(w));p=torch.tensor(seq).expand(n,-1).clone()
    else:raise ValueError(family)
    return p

def bank(c,family,L,seed,n=512):
    # Context independent of program family and length, so all models receive
    # the same worlds/roles/cues. Separate generator controls program randomness.
    g=torch.Generator().manual_seed(seed)
    b=wk.make_batch(c,g,n,extra=2,max_program=0,stages=3,cue_mode='cycle',program_mode='identity')
    gi=torch.Generator().manual_seed(seed+1000+L)
    p=programs(family,L,n,gi);aliases=torch.randint(2,p.shape,generator=gi)
    if family!='random_nonidentity' and not torch.equal(actions(p),torch.arange(4).expand(n,-1)):
        raise AssertionError('not globally identity')
    v=wk.apply_ops(b.world.gather(1,b.cues[:,0]),p)
    args=torch.zeros(n,4,dtype=torch.long)
    args[:,2]=torch.randint(4,(n,),generator=g)
    z=v[:,0]+2*v[:,1];same=torch.randint(2,(n,),generator=g).bool()
    args[:,3]=torch.where(same,z,(z+torch.randint(1,4,(n,),generator=g))%4)
    return b,p,aliases,v,args


def native_run(m,h,p,aliases,mechanism):
    for t in range(p.shape[1]):
        if mechanism=='normal':h=m.operate(h,p[:,t],aliases[:,t])
        elif mechanism=='no_exchange':h=m.operate(h,p[:,t],aliases[:,t],exchange=False)
        elif mechanism=='zero_messages':h=m.operate(h,p[:,t],aliases[:,t],mode='cut')
        elif mechanism=='exchange_only':
            for _ in range(m.c.work_exchanges):h=m.exchange(h)
        else:raise ValueError(mechanism)
    return h


def metrics(data):
    pred=data['pred'];truth=data['target'];bits=data['memory_bits'];world=data['world'];role=data['roles']
    mem=(bits==world[:,None,:]);allmem=mem.all(-1);work=pred[:,0,:]==truth[:,0,None]
    pair=data['pair_reload']==data['pair_target'][:,None]
    return dict(working_accuracy=float((pred==truth[:,:,None]).mean()),exact_work=float(work.mean()),
        per_consumer=(pred==truth[:,:,None]).mean((0,2)).tolist(),per_agent_work=work.mean(0).tolist(),
        memory_all_eight=float(allmem.mean()),memory_bit_accuracy=float(mem.mean()),per_agent_memory=allmem.mean(0).tolist(),
        original_pair_recall=float(pair.mean()),private_accuracy=float((data['private_pred']==role).mean()),
        private_after_reload=float((data['memory_private']==role[:,None,:]).mean()),
        work_and_memory=float((work&allmem).mean()),work_correct_memory_wrong=float((work&~allmem).mean()),
        memory_correct_conditional_on_work=float((work&allmem).sum()/max(1,work.sum())))


@torch.no_grad()
def evaluate(m,family,L,seed,n=512,mechanism='normal'):
    if mechanism=='exchange_only' and family=='random_nonidentity':raise ValueError('different abstract target')
    b,p,aliases,v,args=bank(m.c,family,L,seed,n)
    h=m.cue(m.encode(b),b.cues[:,0],b.cue_aliases[:,0],delay=0)
    end=m.silent(native_run(m,h,p,aliases,mechanism))
    pred=[];y=[]
    for q in range(4):
        qs=torch.full((n,),q,dtype=torch.long)
        pred.append(torch.stack([a.read(end[i],qs,args[:,q]).argmax(-1) for i,a in enumerate(m.agents)],1))
        y.append(wk.consume(v,qs,args[:,q]))
    private=torch.stack([a.private(end[i]).argmax(-1) for i,a in enumerate(m.agents)],1)
    z=torch.zeros(n,dtype=torch.long);bits=[];mem_private=[]
    for pair in ((0,1),(2,3),(4,5),(6,7)):
        cue=torch.tensor(pair).expand(n,-1);r=m.cue(end,cue,z)
        rp=torch.stack([a.read(r[i],z,z).argmax(-1) for i,a in enumerate(m.agents)],1)
        bits.append(torch.stack([rp&1,(rp>>1)&1],-1))
        mem_private.append(torch.stack([a.private(r[i]).argmax(-1) for i,a in enumerate(m.agents)],1))
    orig=m.cue(end,b.cues[:,0],b.cue_aliases[:,0])
    pair_reload=torch.stack([a.read(orig[i],z,z).argmax(-1) for i,a in enumerate(m.agents)],1)
    pair=b.world.gather(1,b.cues[:,0]);pair_target=pair[:,0]+2*pair[:,1]
    data={k:v.numpy() for k,v in dict(pred=torch.stack(pred,1),target=torch.stack(y,1),memory_bits=torch.cat(bits,2),
        private_pred=private,memory_private=torch.stack(mem_private,1),pair_reload=pair_reload,pair_target=pair_target,
        world=b.world,roles=b.roles,events=b.events,cue=b.cues[:,0],cue_alias=b.cue_aliases[:,0],program=p,op_alias=aliases,arguments=args,
        final_native_state=torch.stack(end,1)).items()}
    return dict(family=family,length=L,seed=seed,n=n,mechanism=mechanism,extrapolation=L>12,metrics=metrics(data)),data


def run(checkpoint,out,seed=920501,n=512,mechanisms=True):
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    m=wk.load(checkpoint);started=time.time()
    plan=dict(checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),source_sha256=sha(Path(__file__)),seed=seed,n=n,started_at=started,
              families=FAMILIES,lengths=LENGTHS,mechanisms=mechanisms,status='STARTED')
    atomic_json(out/'plan.json',plan);result={}
    cond=[('identity_tokens',0,'normal')]
    for L in LENGTHS:
        for fam in FAMILIES:
            if fam in WORDS and L<len(WORDS[fam]):continue
            cond.append((fam,L,'normal'))
    if mechanisms:
        for fam in ['commuting_flips','identity_tokens']:
            for mode in ['no_exchange','zero_messages','exchange_only']:cond.append((fam,48,mode))
    for fam,L,mode in cond:
        name=f'{fam}_L{L}_{mode}'
        res,arrays=evaluate(m,fam,L,seed,n,mode)
        np.savez_compressed(out/(name+'.npz'),**arrays);result[name]=res
        print(json.dumps(dict(case=name,**res['metrics'])),flush=True)
    atomic_json(out/'result.json',result)
    plan.update(status='COMPLETED',finished_at=time.time(),elapsed_seconds=time.time()-started,checkpoint_unchanged=sha(checkpoint)==plan['checkpoint_sha256'],result_sha256=sha(out/'result.json'))
    atomic_json(out/'run.json',plan)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('checkpoint',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seed',type=int,default=920501);p.add_argument('--n',type=int,default=512);p.add_argument('--no-mechanisms',action='store_true')
    a=p.parse_args();run(a.checkpoint,a.out,a.seed,a.n,not a.no_mechanisms)
if __name__=='__main__':main()
