"""New-history confirmation after all neural weights were frozen.
Length48 generators were seen during secondary calibration; not an OOD claim.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import torch
import access_repair as ar
import evaluate_access as ea
from selective import atomic_json,sha
ROOT=Path(__file__).resolve().parents[1]
def run():
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    out=ROOT/'runs'/'confirmation'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);seed=960601;n=1024
    paths={f'{lin}_{arm}':ROOT/(f'inputs/v05_{lin}_random.pt' if arm=='parent' else f'runs/{lin}_{arm}/checkpoint.pt') for lin in 'AB' for arm in ('parent','access','joint','calibrated')}
    specs=[('identity_tokens',0),('random_nonidentity',48),('swap_conjugation',48),('swap_conjugation',96)]
    plan={'seed':seed,'n':n,'specs':specs,'checkpoint_hashes':{k:sha(p) for k,p in paths.items()},'source_sha256':sha(Path(__file__)),
          'stage':'new-history secondary confirmation, not unseen-generator calibration result','started_at':time.time()}
    atomic_json(out/'plan.json',plan);results={}
    for name,path in paths.items():
        m=ar.load(path);results[name]={}
        for fam,L in specs:
            key=f'{fam}_L{L}';r,a=ea.evaluate(m,fam,L,seed,n)
            r['stage']='frozen_new_history_confirmation';r['untrained_length']=L>(48 if name.endswith('calibrated') else 24 if not name.endswith('parent') else 12)
            r['named_generator_excluded_from_training']=fam in ('commuting_flips','swap_conjugation') and not name.endswith('calibrated')
            np.savez_compressed(out/f'{name}__{key}.npz',**a);results[name][key]=r
            print(json.dumps({'model':name,'case':key,**r['metrics']}),flush=True)
    atomic_json(out/'result.json',results)
    plan.update(status='COMPLETED',finished_at=time.time(),inputs_unchanged=all(sha(paths[k])==v for k,v in plan['checkpoint_hashes'].items()))
    atomic_json(out/'run.json',plan)
if __name__=='__main__':run()
