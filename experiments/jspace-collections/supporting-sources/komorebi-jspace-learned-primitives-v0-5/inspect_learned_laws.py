"""Read-only audit of the square network's learned coefficients. Komorebi P.

Decoded coefficients are never used to train or execute the kernels. No
rounding, snapping, or replacement with a named arithmetic instruction occurs.
"""
import json
from pathlib import Path
import numpy as np
from primitive_model import Kernels

def coefficients(model,i):
    if model.activation!='square':raise ValueError('Only square units have this exact polynomial expansion.')
    w=model.p['W'][i];b=model.p['b'][i];v=model.p['v'][i]
    q=np.einsum('j,ij,kj->ik',v,w,w)
    linear=4*w@(v*b)+2*model.p['skip'][i]
    constant=4*np.sum(v*b*b)+4*model.p['c'][i]
    return np.array([constant,linear[0],linear[1],2*q[0,1],q[0,0],q[1,1]])

def main():
    root=Path(__file__).resolve().parent;rows=[]
    # Scoring identities only. The learner and executor do not receive these.
    expected=[np.array([0,1,-1,0,0,0]),np.array([0,0,0,1,0,0]),np.array([0,1,1,0,0,0])]
    for seed in range(3):
        for name in ['trained_square','random_readout_square','untrained_square','shuffled_square']:
            m=Kernels.load(root/f'results/models/{name}_{seed}.npz')
            for i,target in enumerate(expected):
                c=coefficients(m,i);error=abs(c-target)
                rows.append({'seed':seed,'model':name,'channel':m.channels[i],
                             'basis':['1','a','b','a*b','a^2','b^2'],'decoded_coefficients':c.tolist(),
                             'max_coefficient_error':float(error.max()),
                             'coefficient_error_envelope_on_bound6':float(error@np.array([1,6,6,36,36,36])),
                             'scope':'Real polynomial expansion evaluated numerically; floating-point evaluation error not certified.'})
    (root/'results/learned_law_audit.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps([r for r in rows if r['seed']==0 and r['model']=='trained_square'],indent=2))

if __name__=='__main__':main()
