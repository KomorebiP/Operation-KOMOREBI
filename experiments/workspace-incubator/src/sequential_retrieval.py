"""Exploratory sequential recall: unlike branch probes, no state reset per cue."""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import torch
import access_repair as ar
import evaluate_noninterference as ev
from selective import atomic_json,sha
ROOT=Path(__file__).resolve().parents[1]
@torch.no_grad()
def assay(m,fam,L,seed,n=1024):
    b,p,alias,v,args=ev.bank(m.c,fam,L,seed,n);h=ar.native_prefix(m.base,b,p,alias)
    g=torch.Generator().manual_seed(seed+213)
    order=torch.rand(n,8,generator=g).argsort(-1).reshape(n,4,2)
    aliases=torch.randint(2,(n,8),generator=g);z=torch.zeros(n,dtype=torch.long)
    preds=[];targets=[];private=[]
    for t in range(8):
        cue=order[:,t%4];h=m.retrieve(h,cue,aliases[:,t]);value=b.world.gather(1,cue);y=value[:,0]+2*value[:,1]
        preds.append(torch.stack([a.read(h[i],z,z).argmax(-1) for i,a in enumerate(m.base.agents)],1))
        targets.append(y);private.append(torch.stack([a.private(h[i]).argmax(-1) for i,a in enumerate(m.base.agents)],1))
    pp=torch.stack(preds,1).numpy();yy=torch.stack(targets,1).numpy();pr=torch.stack(private,1).numpy();correct=pp==yy[:,:,None]
    res={'stage_accuracy':correct.mean((0,2)).tolist(),'first_pass_all_eight':float(correct[:,:4].all(1).mean()),'second_pass_all_eight':float(correct[:,4:].all(1).mean()),
         'stage_private':(pr==b.roles.numpy()[:,None,:]).mean((0,2)).tolist(),'n':n,'length':L,'family':fam,'state_reset_between_cues':False}
    raw={'pred':pp,'target':yy,'private_pred':pr,'world':b.world.numpy(),'roles':b.roles.numpy(),'pairs':order.numpy(),'aliases':aliases.numpy(),
         'events':b.events.numpy(),'program':p.numpy(),'op_alias':alias.numpy(),'initial_cue':b.cues[:,0].numpy()}
    return res,raw

def run():
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);out=ROOT/'runs/sequential'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);results={};started=time.time()
    for lin in 'AB':
        for arm in ('parent','access','joint','calibrated'):
            path=ROOT/(f'inputs/v05_{lin}_random.pt' if arm=='parent' else f'runs/{lin}_{arm}/checkpoint.pt');m=ar.load(path);results[f'{lin}_{arm}']={}
            for fam,L in [('identity_tokens',0),('random_nonidentity',48),('swap_conjugation',48)]:
                key=f'{fam}_L{L}';r,a=assay(m,fam,L,970601);np.savez_compressed(out/f'{lin}_{arm}__{key}.npz',**a);results[f'{lin}_{arm}'][key]=r
    atomic_json(out/'result.json',results);atomic_json(out/'run.json',{'status':'COMPLETED','started_at':started,'elapsed_seconds':time.time()-started,'source_sha256':sha(Path(__file__)),
                     'interpretation':'outcome-informed sequential stress diagnostic after main and calibration outcomes','n':1024,'seed':970601,'no_new_training':True})
    print(json.dumps(results,indent=2))
if __name__=='__main__':run()
