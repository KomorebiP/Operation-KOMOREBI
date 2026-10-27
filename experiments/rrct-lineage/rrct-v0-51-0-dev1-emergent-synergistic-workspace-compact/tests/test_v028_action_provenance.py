import numpy as np
from rrct.action_provenance_experiment import discover_action_provenance, _subspace_recall, _subspace_precision


def _synthetic(seed=4):
    rng=np.random.default_rng(seed)
    qs,_=np.linalg.qr(rng.normal(size=(6,6))); qi,_=np.linalg.qr(rng.normal(size=(8,8))); qo,_=np.linalg.qr(rng.normal(size=(12,12)))
    s=qs[:,:2]; sc=qs[:,2:4]; ss=qs[:,4:6]; ui=qi[:,:2]; uc=qi[:,2:4]; vo=qo[:,:2]; vn=qo[:,2:4]
    a=s@np.diag([.7,.6])@ui.T + sc@np.diag([.9,.8])@uc.T
    b=s@np.diag([.5,.45])@vo.T + ss@np.diag([1.0,.9])@vn.T
    n=1800; z=rng.normal(size=(n,6)); y=rng.normal(size=(n,12))
    cmd=z@a+rng.normal(0,.06,size=(n,8)); nxt=.65*y+z@b+rng.normal(0,.06,size=(n,12))
    return rng,z,cmd,y,nxt,s@s.T,ui@ui.T,vo@vo.T


def test_action_provenance_is_intersection_not_single_path():
    _,z,cmd,y,nxt,ts,ti,to=_synthetic()
    found=discover_action_provenance(z,cmd,y,nxt,seed=19)
    assert found.rank==2
    assert found.command_path.rank==4
    assert found.sensory_path.rank==4
    assert _subspace_recall(found.source_projector,ts)>.98
    assert _subspace_precision(found.source_projector,ts)>.98
    assert _subspace_recall(found.internal_projector,ti)>.95
    assert _subspace_recall(found.sensory_projector,to)>.95
    assert _subspace_precision(found.command_path.projector,ts)<.60
    assert _subspace_precision(found.sensory_path.projector,ts)<.60


def test_temporal_shuffle_removes_action_provenance():
    rng,z,cmd,y,nxt,ts,_,_=_synthetic(8)
    found=discover_action_provenance(z[rng.permutation(len(z))],cmd,y,nxt,seed=31)
    assert found.rank==0
    assert _subspace_recall(found.source_projector,ts)<.10
