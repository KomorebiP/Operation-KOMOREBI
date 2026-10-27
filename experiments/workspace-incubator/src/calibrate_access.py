"""Secondary outcome-informed known-stress native access calibration.
Original 1000-update comparison is unchanged. No joint/central decoder is used.
"""
from __future__ import annotations
import argparse,json,os,sys,time,dataclasses
from pathlib import Path
import torch
from torch import nn
import access_repair as ar
import evaluate_noninterference as ev
from selective import atomic_json,sha
from noninterference import tensor_digest
ROOT=Path(__file__).resolve().parents[1]

def stress_data(c,g,n):
    fam=ev.FAMILIES[int(torch.randint(6,(),generator=g))]
    x=float(torch.rand((),generator=g));L=12 if x<.2 else 24 if x<.4 else 48
    seed=int(torch.randint(2**30,(),generator=g));b,p,aliases,v,args=ev.bank(c,fam,L,seed,n)
    pairs=torch.rand(n,8,generator=g).argsort(-1).reshape(n,4,2);alias=torch.randint(2,(n,4),generator=g)
    repeats=torch.rand(n,4,generator=g)<.5;second=torch.where(repeats[:,:,None],pairs,pairs.roll(1,1));second_alias=torch.randint(2,(n,4),generator=g)
    q0=ar.query_bank(v,g);q1=ar.query_bank(b.world.gather(1,pairs.reshape(n,8)).reshape(-1,2),g);q2=ar.query_bank(b.world.gather(1,second.reshape(n,8)).reshape(-1,2),g)
    return b,p,aliases,pairs,alias,second,second_alias,(q0,q1,q2),{'family':fam,'length':L,'seed':seed}

def train(parent,out,seed,steps=1000,batch=96):
    if out.exists():raise FileExistsError(out)
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.manual_seed(seed)
    m=ar.load(parent);m.set_arm('access');old=tensor_digest(m.base.state_dict());g=torch.Generator().manual_seed(seed+1)
    opt=torch.optim.AdamW(m.access.parameters(),lr=.0003,weight_decay=1e-5)
    spec={'arm':'access','phase':'known_stress_calibration','seed':seed,'steps':steps,'batch':batch,'lr':.0003,'weight_decay':1e-5}
    source=ar.source_hashes();source['src/calibrate_access.py']=sha(Path(__file__));source['notes/STRESS_CALIBRATION_CONTRACT.md']=sha(ROOT/'notes/STRESS_CALIBRATION_CONTRACT.md')
    begin=time.monotonic();out.mkdir(parents=True);meter={}
    rec={'status':'RUNNING','specification':spec,'parent_sha256':sha(parent),'sources':source,'started_at':time.time(),'command':sys.argv,'initial_base_digest':old,'known_family_and_length_calibration':True}
    atomic_json(out/'run.json',rec)
    for step in range(steps):
        m.train();d=stress_data(m.c,g,batch);key=f"{d[-1]['family']}_{d[-1]['length']}";meter[key]=meter.get(key,0)+1
        vals=ar.losses(m,d);loss=vals[0]
        if not bool(torch.isfinite(loss)):raise FloatingPointError('nonfinite loss')
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(m.access.parameters(),1.);opt.step()
        if (step+1)%100==0 or step+1==steps:
            row={'step':step+1,'seed':seed,'losses':[float(x.detach()) for x in vals],'elapsed_seconds':time.monotonic()-begin}
            with (out/'training.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(row),flush=True)
            ar.save_checkpoint(out,{'version':'0.6','config':dataclasses.asdict(m.c),'specification':spec,'model':m.state_dict(),'optimizer':opt.state_dict(),'data_rng':g.get_state(),'torch_rng':torch.get_rng_state(),'step':step+1,'meter':meter,'sources':source,'parent_sha256':rec['parent_sha256']})
    rec.update(status='COMPLETED',elapsed_seconds=time.monotonic()-begin,finished_at=time.time(),checkpoint_sha256=sha(out/'checkpoint.pt'),base_exactly_unchanged=old==tensor_digest(m.base.state_dict()),parent_unchanged=sha(parent)==rec['parent_sha256'],sources_unchanged=all(sha(ROOT/p)==v for p,v in source.items()),meter=meter)
    atomic_json(out/'run.json',rec)
    if not all(rec[x] for x in ('base_exactly_unchanged','parent_unchanged','sources_unchanged')):raise RuntimeError('immutable input changed')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('parent',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--seed',required=True,type=int);p.add_argument('--steps',type=int,default=1000);a=p.parse_args();train(a.parent,a.out,a.seed,a.steps)
