"""Native retrieval and downstream-reuse evaluations for the phase-local repair.

No candidate projection or supervised full-state probe is used here. All writes
are the network's usual cue/message/operation updates. Raw inputs and all outputs
are retained for independent integer scoring.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
import torch
import access_repair as ar
import evaluate_noninterference as ev
import working as wk
from selective import atomic_json,sha

LENGTHS=(0,3,6,12,24,48,96)
FAMILIES=ev.FAMILIES

@torch.no_grad()
def recall(m,end,pairs,aliases,mode='intact',depth=1,legacy=False):
    n=len(end[0]);C=pairs.shape[1]
    h=[x[:,None,:].expand(-1,C,-1).reshape(-1,m.c.width) for x in end]
    cue=pairs.reshape(-1,2);alias=aliases.reshape(-1)
    for _ in range(depth):
        h=m.legacy_retrieve(h,cue,alias,mode) if legacy else m.retrieve(h,cue,alias,mode)
    z=torch.zeros(n*C,dtype=torch.long)
    values=torch.stack([a.read(h[i],z,z).argmax(-1) for i,a in enumerate(m.base.agents)],1).reshape(n,C,2)
    priv=torch.stack([a.private(h[i]).argmax(-1) for i,a in enumerate(m.base.agents)],1).reshape(n,C,2)
    return values,priv,h

@torch.no_grad()
def evaluate(m,family,L,seed,n=512,mode='intact',depth=1,legacy=False):
    b,p,aliases,v,args=ev.bank(m.c,family,L,seed,n)
    end=ar.native_prefix(m.base,b,p,aliases)
    predictions=[];truth=[]
    for q in range(4):
        qs=torch.full((n,),q,dtype=torch.long)
        predictions.append(torch.stack([a.read(end[i],qs,args[:,q]).argmax(-1) for i,a in enumerate(m.base.agents)],1))
        truth.append(wk.consume(v,qs,args[:,q]))
    private=torch.stack([a.private(end[i]).argmax(-1) for i,a in enumerate(m.base.agents)],1)
    # Independent branches cover every retained fact; no hidden truth given to agents.
    g=torch.Generator().manual_seed(seed+551)
    pairs=torch.rand(n,8,generator=g).argsort(1).reshape(n,4,2)
    pair_alias=torch.randint(2,(n,4),generator=g)
    vals,mp,_=recall(m,end,pairs,pair_alias,mode,depth,legacy)
    # Scatter into fixed object index order for independent all-world scoring.
    bits=torch.stack([vals&1,(vals>>1)&1],-1).permute(0,2,1,3).reshape(n,2,8)
    ordered=torch.empty_like(bits)
    ordered.scatter_(2,pairs.reshape(n,1,8).expand(-1,2,-1),bits)
    # Generalization: route a factual pair then use the unchanged native operators.
    original=b.cues[:,0];alias=b.cue_aliases[:,0]
    r=(m.legacy_retrieve if legacy else m.retrieve)(end,original,alias,mode,delay=0)
    suffix=torch.randint(4,(n,3),generator=g);suffix_alias=torch.randint(2,(n,3),generator=g)
    reused=m.base.silent(m.base.program(r,suffix,suffix_alias))
    wanted=wk.apply_ops(b.world.gather(1,original),suffix)
    rpred=[];ry=[];reuse_args=args.clone()
    vv=wanted[:,0]+2*wanted[:,1]
    same=torch.randint(2,(n,),generator=g).bool()
    reuse_args[:,3]=torch.where(same,vv,(vv+torch.randint(1,4,(n,),generator=g))%4)
    for q in range(4):
        qs=torch.full((n,),q,dtype=torch.long)
        rpred.append(torch.stack([a.read(reused[i],qs,reuse_args[:,q]).argmax(-1) for i,a in enumerate(m.base.agents)],1))
        ry.append(wk.consume(wanted,qs,reuse_args[:,q]))
    reuse_private=torch.stack([a.private(reused[i]).argmax(-1) for i,a in enumerate(m.base.agents)],1)
    # Check whether post-retrieval native work damaged the memory used by later cues.
    rr,rrpriv,_=recall(m,reused,pairs,pair_alias,mode,1,legacy)
    rbits=torch.stack([rr&1,(rr>>1)&1],-1).permute(0,2,1,3).reshape(n,2,8)
    rordered=torch.empty_like(rbits);rordered.scatter_(2,pairs.reshape(n,1,8).expand(-1,2,-1),rbits)
    data={k:x.numpy() for k,x in dict(events=b.events,world=b.world,roles=b.roles,cue=original,cue_alias=alias,program=p,op_alias=aliases,arguments=args,
         pred=torch.stack(predictions,1),target=torch.stack(truth,1),private_pred=private,pairs=pairs,pair_aliases=pair_alias,
         recalled_pair=vals,memory_bits=ordered,memory_private=mp,suffix=suffix,suffix_alias=suffix_alias,reuse_arguments=reuse_args,
         reuse_pred=torch.stack(rpred,1),reuse_target=torch.stack(ry,1),reuse_private=reuse_private,
         reuse_memory_bits=rordered,reuse_memory_private=rrpriv).items()}
    result={'family':family,'length':L,'seed':seed,'n':n,'access_mode':mode,'depth':depth,'legacy_retrieval':legacy,
            'untrained_length':L>24,'named_generator_excluded_from_training':family in ('commuting_flips','swap_conjugation'), 'metrics':metrics(data)}
    return result,data

def metrics(d):
    work=d['pred']==d['target'][:,:,None];mem=d['memory_bits']==d['world'][:,None,:]
    reuse=d['reuse_pred']==d['reuse_target'][:,:,None];rm=d['reuse_memory_bits']==d['world'][:,None,:]
    return {'exact_work':float(work[:,0].mean()),'per_consumer':work.mean((0,2)).tolist(),
            'memory_all_eight':float(mem.all(-1).mean()),'memory_bit_accuracy':float(mem.mean()),'per_agent_memory':mem.all(-1).mean(0).tolist(),
            'private_work':float((d['private_pred']==d['roles']).mean()),
            'private_recalled':float((d['memory_private']==d['roles'][:,None,:]).mean()),
            'reuse_exact':float(reuse[:,0].mean()),'reuse_per_consumer':reuse.mean((0,2)).tolist(),
            'private_reuse':float((d['reuse_private']==d['roles']).mean()),
            'reuse_memory_all_eight':float(rm.all(-1).mean()),'reuse_memory_bit_accuracy':float(rm.mean())}

def run(checkpoint,out,seed=930601,n=512,full=True):
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    m=ar.load(checkpoint);started=time.time();inp=sha(checkpoint);source=sha(Path(__file__))
    specs=[('identity_tokens',0,'intact',1,False)]
    for L in LENGTHS[1:]:
        for fam in FAMILIES:
            if fam in ev.WORDS and L<len(ev.WORDS[fam]):continue
            specs.append((fam,L,'intact',1,False))
    if full:
        for fam,L in [('identity_tokens',0),('swap_conjugation',48)]:
            for mode in ('cut','shuffle','cut_AtoB','cut_BtoA','skip_exchange'):
                specs.append((fam,L,mode,1,False))
            for depth in (2,4,8):specs.append((fam,L,'intact',depth,False))
        # Same base state but old retrieval path, isolates copied path's contribution.
        specs.append(('swap_conjugation',48,'intact',1,True))
    plan={'checkpoint':str(checkpoint),'checkpoint_sha256':inp,'source_sha256':source,'seed':seed,'n':n,'specs':specs,'started_at':started}
    atomic_json(out/'plan.json',plan);results={}
    for fam,L,mode,depth,legacy in specs:
        name=f'{fam}_L{L}_{mode}_d{depth}'+('_legacy' if legacy else '')
        result,raw=evaluate(m,fam,L,seed,n,mode,depth,legacy)
        np.savez_compressed(out/(name+'.npz'),**raw);results[name]=result
        print(json.dumps({'case':name,**result['metrics']}),flush=True)
    atomic_json(out/'result.json',results)
    plan.update(status='COMPLETED',finished_at=time.time(),elapsed_seconds=time.time()-started,result_sha256=sha(out/'result.json'),
                inputs_unchanged=inp==sha(checkpoint) and source==sha(Path(__file__)))
    atomic_json(out/'run.json',plan)
    if not plan['inputs_unchanged']:raise RuntimeError('inputs changed')
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('checkpoint',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--seed',type=int,default=930601);p.add_argument('--n',type=int,default=512);p.add_argument('--main-only',action='store_true');a=p.parse_args()
    run(a.checkpoint,a.out,a.seed,a.n,not a.main_only)
