import numpy as np
from rrct.discovered_agent_interface_experiment import discover_agent_interface, _subspace_overlap


def test_joint_discovery_recovers_both_hidden_rank_two_subspaces():
    rng=np.random.default_rng(3)
    qi,_=np.linalg.qr(rng.normal(size=(8,8))); qo,_=np.linalg.qr(rng.normal(size=(12,12)))
    ui=qi[:,:2]; uo=qo[:,:2]
    ti=ui@ui.T; to=uo@uo.T
    y=rng.normal(size=(1200,12)); z=rng.normal(size=(1200,8))
    effect=ui@np.asarray([[.42,.03],[-.02,.37]])@uo.T
    nxt=.65*y+z@effect+rng.normal(0,.07,size=(1200,12))
    found=discover_agent_interface(y,z,nxt,seed=9)
    assert found.rank==2
    assert _subspace_overlap(found.internal_projector,ti)>.95
    assert _subspace_overlap(found.sensory_projector,to)>.95


def test_temporal_permutation_destroys_joint_interface():
    rng=np.random.default_rng(7)
    qi,_=np.linalg.qr(rng.normal(size=(8,8))); qo,_=np.linalg.qr(rng.normal(size=(12,12)))
    ui=qi[:,:2]; uo=qo[:,:2]; ti=ui@ui.T;to=uo@uo.T
    y=rng.normal(size=(1200,12));z=rng.normal(size=(1200,8));effect=.4*ui@uo.T
    nxt=.6*y+z@effect+rng.normal(0,.07,size=(1200,12))
    shuffled=discover_agent_interface(y,np.roll(z,1,axis=0),nxt,seed=13)
    assert _subspace_overlap(shuffled.internal_projector,ti)<.20
    assert _subspace_overlap(shuffled.sensory_projector,to)<.20
