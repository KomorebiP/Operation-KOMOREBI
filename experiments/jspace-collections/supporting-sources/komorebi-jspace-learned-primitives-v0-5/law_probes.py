"""Test supplied algebraic-law templates against learned kernels. Komorebi P.

Passing finite probes is evidence, not a universal proof. These findings do not
authorize the executor to silently reorder operands or change old programs.
"""
import json
from pathlib import Path
import numpy as np
from run_experiment import make_catalog

def probe(catalog,seed=96417,count=512,tolerance=1e-6):
    rng=np.random.default_rng(seed);a,b,c=rng.uniform(-1,1,(3,count));zero=np.zeros(count);one=np.ones(count)
    records=[]
    for channel in catalog.accepted:
        f=lambda x,y:catalog.call(channel,x,y)
        ab=f(a,b)
        residuals={'symmetric':ab-f(b,a),'antisymmetric':ab+f(b,a),
                   'associative':f(f(a,b),c)-f(a,f(b,c)),
                   'zero_right_identity':f(a,zero)-a,'zero_left_identity':f(zero,a)-a,
                   'one_right_identity':f(a,one)-a,'one_left_identity':f(one,a)-a,
                   'zero_right_annihilator':f(a,zero),'zero_left_annihilator':f(zero,a)}
        errors={name:float(np.max(abs(value))) for name,value in residuals.items()}
        records.append({'channel':channel,'supported_templates':[name for name,error in errors.items() if error<=tolerance],
                        'max_probe_errors':errors,'probe_count':count,'input_domain':[-1,1],
                        'tolerance':tolerance,'status':'finite_empirical_evidence','kernel_identity':catalog.kernels.identity()})
    return records

if __name__=='__main__':
    root=Path(__file__).resolve().parent;results=[]
    for seed in range(3):results.append({'seed':seed,'laws':probe(make_catalog(root/'results',seed))})
    (root/'results/law_probes.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results[0],indent=2))
