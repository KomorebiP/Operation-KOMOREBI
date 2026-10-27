"""Supervised engineered positive control, NOT a learned native access repair.

Factor a joint eight-output linear diagnostic into local partial sums and a
single simultaneous exchange of eight bounded real values per direction.
No central access to the other agent's raw state is used by a receiver.
The nonlinear scalar codec is supplied. It is not the native neural sender.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import torch
import access_repair as ar
import evaluate_noninterference as ev
from selective import sha,atomic_json
ROOT=Path(__file__).resolve().parents[1]

def code(s):return s/(1+np.abs(s))
def decode(m):
    if np.any(np.abs(m)>=1):raise FloatingPointError('bounded codec saturated')
    return m/(1-np.abs(m))

def sender(local,W,bias):return code(local@W+bias/2)
def receiver(local,W,bias,partner_message):return local@W+bias/2+decode(partner_message)

@torch.no_grad()
def capture(base,family,L,seed,n):
    b,p,a,v,args=ev.bank(base.c,family,L,seed,n)
    h=ar.native_prefix(base,b,p,a)
    return torch.cat(h,1).numpy().astype(np.float64),b.world.numpy()

def fit(x,y):
    mean=x.mean(0);scale=x.std(0);scale[scale<1e-6]=1.
    z=np.column_stack(((x-mean)/scale,np.ones(len(x))))
    penalty=np.eye(z.shape[1])*1e-3;penalty[-1,-1]=0
    beta=np.linalg.solve(z.T@z+penalty,z.T@(2*y-1))
    W=beta[:-1]/scale[:,None];bias=beta[-1]-mean@W
    return W,bias

def score(logits,truth):
    bits=(logits>0).astype(np.int64)
    return {'all_eight':float((bits==truth).all(1).mean()),'bit_accuracy':float((bits==truth).mean())}

def run():
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    out=ROOT/'runs'/'distributed_control'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);results={};started=time.time()
    for lin in 'AB':
        path=ROOT/'inputs'/f'v05_{lin}_random.pt';m=ar.load(path)
        xs=[];ys=[]
        # One fixed reader trained on a declared mixture, not separately per test.
        train_specs=[('identity_tokens',0),('random_nonidentity',12),('mirror_identity',24),('identity_tokens',48),
                     ('flip_involution',48),('commuting_flips',48),('swap_conjugation',48),('random_nonidentity',48)]
        for j,(fam,L) in enumerate(train_specs):
            x,y=capture(m.base,fam,L,950610+j,512);xs.append(x);ys.append(y)
        x=np.concatenate(xs);y=np.concatenate(ys);W,b=fit(x,y)
        gen=np.random.default_rng(950691);Wnull,bnull=fit(x,y[gen.permutation(len(y))])
        saved={'train_x':x,'train_y':y,'W':W,'bias':b,'W_shuffled':Wnull,'bias_shuffled':bnull};res={}
        tests=[('identity_tokens',0)]+[(fam,L) for L in (48,96) for fam in ev.FAMILIES]
        for j,(fam,L) in enumerate(tests):
            xx,yy=capture(m.base,fam,L,950701,512);s=xx@W+b
            a=xx[:,:64];bb=xx[:,64:];ma=sender(a,W[:64],b);mb=sender(bb,W[64:],b)
            ra=receiver(a,W[:64],b,mb);rb=receiver(bb,W[64:],b,ma)
            err=max(float(abs(ra-s).max()),float(abs(rb-s).max()))
            agreement=bool(np.array_equal(ra>0,s>0) and np.array_equal(rb>0,s>0))
            # These channel cuts are a compiled-control diagnostic, not a GRU intervention.
            cut=receiver(a,W[:64],b,np.zeros_like(mb));shuf=receiver(a,W[:64],b,mb[np.roll(np.arange(len(mb)),1)])
            null=xx@Wnull+bnull
            name=f'{fam}_L{L}';res[name]={'central':score(s,yy),'distributed_A':score(ra,yy),'distributed_B':score(rb,yy),
                     'local_A_only':score(cut,yy),'wrong_partner':score(shuf,yy),'shuffled_labels':score(null,yy),
                     'maximum_logit_error':err,'exact_prediction_agreement':agreement,'maximum_message_abs':float(max(abs(ma).max(),abs(mb).max()))}
            saved[name+'_x']=xx;saved[name+'_y']=yy;saved[name+'_central']=s;saved[name+'_A']=ra;saved[name+'_B']=rb;saved[name+'_message_A']=ma;saved[name+'_message_B']=mb
            if not agreement or err>1e-9:raise AssertionError('distributed factorization failed')
        np.savez_compressed(out/f'{lin}.npz',**saved);results[lin]=res
    atomic_json(out/'result.json',results)
    atomic_json(out/'run.json',{'status':'COMPLETED','started_at':started,'seconds':time.time()-started,'source_sha256':sha(Path(__file__)),'one_reader_per_lineage':True,'train_cases_per_lineage':4096,'test_cases_per_condition':512,
                              'role':'supervised engineered positive control, NOT native neural access', 'result_sha256':sha(out/'result.json')})
    print(json.dumps(results,indent=2))
if __name__=='__main__':run()
