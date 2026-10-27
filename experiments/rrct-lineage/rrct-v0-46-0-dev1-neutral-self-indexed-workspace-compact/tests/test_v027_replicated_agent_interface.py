import numpy as np
from rrct.replicated_agent_interface_experiment import discover_replicated_agent_interface, _subspace_overlap


def _synthetic(seed=3):
    rng=np.random.default_rng(seed)
    qi,_=np.linalg.qr(rng.normal(size=(8,8)));qo,_=np.linalg.qr(rng.normal(size=(12,12)))
    ui=qi[:,:2];uo=qo[:,:2];ti=ui@ui.T;to=uo@uo.T
    y=rng.normal(size=(1600,12));z=rng.normal(size=(1600,8));effect=ui@np.asarray([[.42,.03],[-.02,.37]])@uo.T
    nxt=.65*y+z@effect+rng.normal(0,.07,size=(1600,12))
    return rng,y,z,nxt,ti,to


def test_replicated_discovery_recovers_both_hidden_subspaces():
    _,y,z,nxt,ti,to=_synthetic()
    found=discover_replicated_agent_interface(y,z,nxt,seed=9)
    assert found.rank==2
    assert found.replicated_mask[:2].all()
    assert not found.replicated_mask[2:].any()
    assert _subspace_overlap(found.internal_projector,ti)>.95
    assert _subspace_overlap(found.sensory_projector,to)>.95


def test_temporal_permutation_destroys_replicated_interface():
    _,y,z,nxt,ti,to=_synthetic(7)
    shuffled=discover_replicated_agent_interface(y,np.roll(z,1,axis=0),nxt,seed=13)
    assert _subspace_overlap(shuffled.internal_projector,ti)<.20
    assert _subspace_overlap(shuffled.sensory_projector,to)<.20
