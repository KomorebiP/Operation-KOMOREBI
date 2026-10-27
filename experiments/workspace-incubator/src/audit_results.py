"""Independent integer interpretation, score recomputation and replay audit.
No imports from the neural task/evaluation implementation are used for targets.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def world_from_events(events):
    n=events.shape[0];w=np.zeros((n,8),dtype=np.int64)
    for t in range(events.shape[1]):
        for i in range(n):
            k,d,s,v,f,alias,owner=map(int,events[i,t])
            if not f:continue
            if k==0:w[i,d]=v
            elif k==1:w[i,d]^=1
            elif k==2:w[i,d]=w[i,s]
            elif k==3:w[i,d],w[i,s]=w[i,s],w[i,d]
            else:raise AssertionError('bad event')
    return w

def interpret(pair,ops):
    v=pair.copy()
    for t in range(ops.shape[1]):
        op=ops[:,t]
        v[op==1,0]^=1;v[op==2,1]^=1
        ix=np.flatnonzero(op==3);v[ix]=v[ix,::-1]
        assert np.isin(op,[0,1,2,3]).all()
    return v

def answers(v,args):
    z=v[:,0]+2*v[:,1]
    return np.stack((z,v[:,0]^v[:,1],z^args[:,2],(z==args[:,3]).astype(np.int64)),1)

def close(a,b):
    if isinstance(a,list):return np.allclose(a,b,rtol=0,atol=1e-12)
    return abs(a-b)<1e-12

def audit_bank(p,result):
    with np.load(p,allow_pickle=False) as z:d={k:z[k] for k in z.files}
    w=world_from_events(d['events']);assert np.array_equal(w,d['world'])
    selected=w[np.arange(len(w))[:,None],d['cue']]
    v=interpret(selected,d['program']);target=answers(v,d['arguments'])
    assert np.array_equal(target,d['target'])
    rt=answers(interpret(selected,d['suffix']),d['reuse_arguments']);assert np.array_equal(rt,d['reuse_target'])
    assert np.all(d['arguments'][:,:2]==0) and np.all(d['reuse_arguments'][:,:2]==0)
    n=len(w)
    for i in range(n):
        assert sorted(d['pairs'][i].flatten().tolist())==list(range(8))
        for j in range(4):
            for a in range(2):
                code=int(d['recalled_pair'][i,j,a]);u,vv=d['pairs'][i,j]
                assert d['memory_bits'][i,a,u]==code%2 and d['memory_bits'][i,a,vv]==code//2
    mem=d['memory_bits']==w[:,None,:];rmem=d['reuse_memory_bits']==w[:,None,:]
    work=d['pred']==target[:,:,None];reuse=d['reuse_pred']==rt[:,:,None]
    m={'exact_work':float(work[:,0].mean()),'per_consumer':work.mean((0,2)).tolist(),'memory_all_eight':float(mem.all(-1).mean()),
       'memory_bit_accuracy':float(mem.mean()),'per_agent_memory':mem.all(-1).mean(0).tolist(),
       'private_work':float((d['private_pred']==d['roles']).mean()),'private_recalled':float((d['memory_private']==d['roles'][:,None,:]).mean()),
       'reuse_exact':float(reuse[:,0].mean()),'reuse_per_consumer':reuse.mean((0,2)).tolist(),
       'private_reuse':float((d['reuse_private']==d['roles']).mean()),'reuse_memory_all_eight':float(rmem.all(-1).mean()),'reuse_memory_bit_accuracy':float(rmem.mean())}
    assert set(m)==set(result['metrics'])
    for k in m:
        if not close(m[k],result['metrics'][k]):raise AssertionError((str(p),k,m[k],result['metrics'][k]))
    return sum(d[k].size for k in ('pred','memory_bits','private_pred','memory_private','reuse_pred','reuse_memory_bits','reuse_private'))

def recursive_equal(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(recursive_equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(recursive_equal(x,y) for x,y in zip(a,b))
    return a==b

def run():
    torch.set_num_threads(1);banks=0;entries=0;by_model={}
    for directory in sorted((ROOT/'runs').glob('eval_*')):
        if not directory.is_dir() or directory.name.endswith('_replay'):continue
        results=json.loads((directory/'result.json').read_text());count=0
        for name,res in results.items():count+=audit_bank(directory/(name+'.npz'),res);banks+=1
        entries+=count;by_model[directory.name]={'banks':len(results),'recorded_output_entries':count}
    original=torch.load(ROOT/'runs/A_access/checkpoint.pt',weights_only=False)
    replay=torch.load(ROOT/'runs/A_access_replay/checkpoint.pt',weights_only=False)
    ck_equal=recursive_equal(original,replay);assert ck_equal
    byte_equal=sha(ROOT/'runs/A_access/checkpoint.pt')==sha(ROOT/'runs/A_access_replay/checkpoint.pt');assert byte_equal
    folder_a=ROOT/'runs/eval_A_access';folder_b=ROOT/'runs/eval_A_access_replay'
    j_equal=json.loads((folder_a/'result.json').read_text())==json.loads((folder_b/'result.json').read_text());assert j_equal
    nreplay=0
    for p in folder_a.glob('*.npz'):
        assert sha(p)==sha(folder_b/p.name);nreplay+=1
    # Frozen prefix predictions must match originals on every main native bank.
    frozen_check={}
    for lin in 'AB':
        parent=torch.load(ROOT/f'inputs/v05_{lin}_random.pt',weights_only=False)
        count=0
        for arm in ('access','calibrated'):
            ck=torch.load(ROOT/f'runs/{lin}_{arm}/checkpoint.pt',weights_only=False)
            assert all(torch.equal(v,ck['model']['base.'+k]) for k,v in parent['model'].items())
            for p in (ROOT/f'runs/eval_{lin}_parent').glob('*.npz'):
                with np.load(p) as a,np.load(ROOT/f'runs/eval_{lin}_{arm}'/p.name) as b:
                    for key in ('events','program','op_alias','cue','cue_alias','pred','target','private_pred'):
                        assert np.array_equal(a[key],b[key]);count+=1
        frozen_check[lin]=count
    rec={'status':'PASS','independent_interpreter':'scalar event updates and separate NumPy bit-program interpreter','banks':banks,
         'recorded_output_entries_rechecked':entries,'case_reuse_warning':'Entries include reused histories, multiple agents, branches and conditions, not independent experiments.',
         'by_model':by_model,'full_checkpoint_fields_replay_equal':ck_equal,'checkpoint_bytes_replay_equal':byte_equal,
         'saved_model_tensors':len(original['model']),'optimizer_and_rng_replay_equal':True,'evaluation_result_replay_equal':j_equal,'byte_exact_evaluation_banks':nreplay,
         'frozen_prefix_array_checks':frozen_check}
    (ROOT/'checks/independent_audit.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
if __name__=='__main__':run()
