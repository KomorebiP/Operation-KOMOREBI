import numpy as np
from rrct.discovered_self_boundary_experiment import discover_self_boundary, _subspace_overlap

def test_discovery_recovers_hidden_mixed_subspace_without_rank_label():
    rng=np.random.default_rng(3);q,_=np.linalg.qr(rng.normal(size=(12,12)));truth=q[:,:2]@q[:,:2].T
    y=rng.normal(size=(500,12));z=rng.normal(size=(500,2));effect=np.asarray([[.4,0.],[0.,-.35]])@q[:,:2].T
    nxt=.65*y+z@effect+rng.normal(0,.08,size=(500,12))
    found=discover_self_boundary(y,z,nxt,seed=9)
    assert found.rank==2
    assert _subspace_overlap(found.projector,truth)>.9

def test_temporal_permutation_does_not_recover_same_boundary():
    rng=np.random.default_rng(7);q,_=np.linalg.qr(rng.normal(size=(12,12)));truth=q[:,:2]@q[:,:2].T
    y=rng.normal(size=(500,12));z=rng.normal(size=(500,2));effect=.4*np.eye(2)@q[:,:2].T
    nxt=.6*y+z@effect+rng.normal(0,.08,size=(500,12))
    shuffled=discover_self_boundary(y,np.roll(z,1,axis=0),nxt,seed=13)
    assert _subspace_overlap(shuffled.projector,truth)<.2
