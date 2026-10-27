import sys
from pathlib import Path
import pytest
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import access_repair as ar
import working as wk
from noninterference import tensor_digest

torch.set_num_threads(1)
@pytest.fixture
def model():
    return ar.load(ROOT/'inputs'/'v05_A_random.pt')

def data(m,seed=42,n=16):
    return ar.train_data(m.c,torch.Generator().manual_seed(seed),n)

@pytest.mark.parametrize('mode',['intact','cut','shuffle','cut_AtoB','cut_BtoA','skip_exchange'])
def test_copy_initial_equivalence(model,mode):
    d=data(model);b=d[0];h=ar.native_prefix(model.base,b,d[1],d[2])
    if mode=='skip_exchange':
        a=model.retrieve(h,b.cues[:,1],b.cue_aliases[:,1],mode)
        assert all(torch.isfinite(x).all() for x in a);return
    a=model.retrieve(h,b.cues[:,1],b.cue_aliases[:,1],mode)
    z=model.base.cue(h,b.cues[:,1],b.cue_aliases[:,1],mode)
    assert all(torch.equal(x,y) for x,y in zip(a,z))

def test_training_freezes_every_base_tensor(model):
    d=data(model);old={k:v.clone() for k,v in model.base.state_dict().items()}
    opt=torch.optim.AdamW(model.access.parameters(),lr=.001)
    loss=ar.losses(model,d)[0];loss.backward();opt.step()
    assert all(torch.equal(v,model.base.state_dict()[k]) for k,v in old.items())
    assert all(p.grad is None for p in model.base.parameters())
    assert any(p.grad is not None and p.grad.abs().sum()>0 for p in model.access.parameters())

def test_joint_receives_work_gradients(model):
    model.set_arm('joint');ar.losses(model,data(model))[0].backward()
    assert model.base.agents[0].work_out.weight.grad.abs().sum()>0
    assert model.access[1].receive.weight_ih.grad.abs().sum()>0

def test_no_weight_sharing(model):
    assert not any(a.data_ptr()==b.data_ptr() for a in model.access[0].parameters() for b in model.access[1].parameters())
    assert not any(a.data_ptr()==b.data_ptr() for a in model.access.parameters() for b in model.base.parameters())

def test_query_arguments_no_answer_leakage(model):
    for seed in range(12):
        d=data(model,seed,n=16)
        for q,arg,y in d[-2]:
            assert torch.equal(arg[(q==0)|(q==1)],torch.zeros_like(arg[(q==0)|(q==1)]))
        b=d[0];h1=ar.native_prefix(model.base,b,d[1],d[2]);b.q.zero_();b.arg.fill_(3)
        h2=ar.native_prefix(model.base,b,d[1],d[2]);assert all(torch.equal(a,b) for a,b in zip(h1,h2))

@pytest.mark.parametrize('seed',range(4))
def test_all_facts_and_targets(model,seed):
    d=data(model,seed);b,p,alias,c1,a1,c2,a2,qs,_=d
    assert torch.equal(c1.reshape(-1,8).sort(1).values,torch.arange(8).expand(b.size,-1))
    for j,cues in enumerate((c1,c2),1):
        q,arg,y=qs[j];v=b.world.gather(1,cues.reshape(b.size,8)).reshape(-1,2)
        for i in range(len(v)):
            x=int(v[i,0])+2*int(v[i,1]);typ=int(q[i]);a=int(arg[i])
            expected=[x,int(v[i,0])^int(v[i,1]),x^a,int(x==a)][typ]
            assert int(y[i])==expected

def test_matching_rng_and_data(model):
    a=torch.Generator().manual_seed(876);b=torch.Generator().manual_seed(876)
    for _ in range(8):
        x=ar.train_data(model.c,a,16);y=ar.train_data(model.c,b,16)
        assert x[-1]==y[-1]
        for name in ('events','world','roles','cues'):assert torch.equal(getattr(x[0],name),getattr(y[0],name))
    assert torch.equal(a.get_state(),b.get_state())

def test_bad_modes(model):
    b=data(model)[0];h=model.base.encode(b)
    with pytest.raises(ValueError):model.retrieve(h,b.cues[:,0],b.cue_aliases[:,0],'invalid')
    with pytest.raises(ValueError):model.set_arm('unknown')
