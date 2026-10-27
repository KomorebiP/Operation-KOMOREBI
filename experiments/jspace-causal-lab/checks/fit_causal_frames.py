"""Prospective fixed calibration of a report-Jacobian candidate and controls.
Rank three is limited by four centered report rows, not an emergence result.
No scientific claim of natural support is made for projected replacements.
"""
from causal_support import *
import time,platform
start=time.time();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
rank=3;seed=927710;N=768
obj={'schema':'komorebi.causal-editor.frames.v1','rank':rank,'calibration_seed':seed,'contexts':N,
     'phase':'after cue, 0/3/6 native operations and two extra native operations; before silent delay and query',
     'method':'SVD of centered, averaged exact-report gradients through two frozen silent updates',
     'weights_sha256':hashlib.sha256((ROOT/'app/weights.bin').read_bytes()).hexdigest(),'lineages':{},
     'boundary':'Output-informed fixed candidate, not semantic discovery or a validated natural-space certificate.'}
def canonical(u):
    u=u.clone()
    for row in u:
        if row[row.abs().argmax()]<0:row.mul_(-1)
    return u
for lin in ['A','B']:
    m=load(lin);spec=fixture_bank(N,seed)
    with torch.no_grad():
        hs=source(m,spec)
        # Balanced legal alternatives over the same retained factual context.
        banks=[program(m,hs,p) for p in [[0,0],[1,0],[0,2],[1,2]]]
        native=[torch.stack([b[i] for b in banks],1) for i in range(2)]
        h=[x.reshape(-1,64).detach().requires_grad_(True) for x in native]
    delayed=m.base.silent(h)
    zero=torch.zeros(len(h[0]),dtype=torch.long)
    Js=[]
    for i,a in enumerate(m.base.agents):
        y=a.read(delayed[i],zero,zero)
        j=torch.stack([torch.autograd.grad(y[:,k].sum(),h[i],retain_graph=True)[0].mean(0) for k in range(4)])
        Js.append(j-j.mean(0))
    # Interaction-only covariance centers within a world/history over its four programs.
    x=[(v-v.mean(1,keepdim=True)).reshape(-1,64) for v in native]
    cu,cs,cv=torch.linalg.svd(x[0].T@x[1]/len(x[0]),full_matrices=False)
    frames={};data={}
    for i in range(2):
        _,sv,vh=torch.linalg.svd(Js[i].double(),full_matrices=False)
        U=canonical(vh[:rank].float());flat=native[i].reshape(-1,64)
        _,ps,pv=torch.linalg.svd((flat-flat.mean(0)).double(),full_matrices=False)
        g=torch.Generator().manual_seed(seed+99+i)
        ru,_=torch.linalg.qr(torch.randn(64,rank,generator=g))
        frames[i]={'J':U.tolist(),'PCA':canonical(pv[:rank].float()).tolist(),
          'interaction':canonical((cu[:,:rank].T if i==0 else cv[:rank]).float()).tolist(),
          'random':canonical(ru.T).tolist()}
        coords=flat@U.T
        data[i]={'means':coords.mean(0).tolist(),'scales':coords.std(0).tolist(),'singular_values':sv.tolist(),
                 'orthonormal_error':float((U@U.T-torch.eye(rank)).abs().max()),
                 'variance_fraction':float(coords.var(0).sum()/flat.var(0).sum())}
    obj['lineages'][lin]={'frames':[frames[0],frames[1]],'statistics':[data[0],data[1]],
                           'candidate_rank':rank}
    print(lin,'J fraction',*[round(data[i]['variance_fraction'],4) for i in range(2)],flush=True)
obj['runtime_seconds']=time.time()-start;obj['environment']={'torch':torch.__version__,'python':platform.python_version()}
(ROOT/'app/frames.json').write_text(json.dumps(obj,separators=(',',':'),allow_nan=False))
print('Saved frames before evaluation',hashlib.sha256((ROOT/'app/frames.json').read_bytes()).hexdigest(),flush=True)
