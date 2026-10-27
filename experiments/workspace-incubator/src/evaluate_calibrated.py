"""Same native assay with correct metadata for the outcome-informed length48 arm."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
import torch
import access_repair as ar
import evaluate_access as ea
import evaluate_noninterference as ev
from selective import atomic_json,sha

def run(path,out,seed=930601,n=512):
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    m=ar.load(path);initial=sha(path);started=time.time()
    specs=[('identity_tokens',0,'intact',1,False)]
    for L in ea.LENGTHS[1:]:
        for fam in ea.FAMILIES:
            if fam in ev.WORDS and L<len(ev.WORDS[fam]):continue
            specs.append((fam,L,'intact',1,False))
    for fam,L in [('identity_tokens',0),('swap_conjugation',48)]:
        for mode in ('cut','shuffle','cut_AtoB','cut_BtoA','skip_exchange'):specs.append((fam,L,mode,1,False))
        for depth in (2,4,8):specs.append((fam,L,'intact',depth,False))
    specs.append(('swap_conjugation',48,'intact',1,True))
    plan={'checkpoint_sha256':initial,'source_hashes':{Path(ea.__file__).name:sha(Path(ea.__file__)),Path(__file__).name:sha(Path(__file__))},
          'seed':seed,'n':n,'training_maximum_length':48,'all_six_generators_exposed_in_secondary_training':True,'known_stress_calibration_not_unseen_family_confirmation':True,'specs':specs,'started_at':started}
    atomic_json(out/'plan.json',plan);res={}
    for fam,L,mode,depth,legacy in specs:
        name=f'{fam}_L{L}_{mode}_d{depth}'+('_legacy' if legacy else '')
        r,d=ea.evaluate(m,fam,L,seed,n,mode,depth,legacy)
        r['untrained_length']=L>48;r['named_generator_excluded_from_training']=False;r['stage']='known_stress_calibrated'
        np.savez_compressed(out/(name+'.npz'),**d);res[name]=r
        print(json.dumps({'case':name,**r['metrics']}),flush=True)
    atomic_json(out/'result.json',res)
    plan.update(status='COMPLETED',elapsed_seconds=time.time()-started,checkpoint_unchanged=initial==sha(path),result_sha256=sha(out/'result.json'))
    atomic_json(out/'run.json',plan)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('checkpoint',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--seed',type=int,default=930601);p.add_argument('--n',type=int,default=512);a=p.parse_args();run(a.checkpoint,a.out,a.seed,a.n)
