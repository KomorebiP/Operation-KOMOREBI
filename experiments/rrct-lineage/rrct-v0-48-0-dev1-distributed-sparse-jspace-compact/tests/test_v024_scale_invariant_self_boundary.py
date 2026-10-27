import numpy as np
from rrct.scale_invariant_self_boundary_experiment import scale_invariant_window_statistics

def test_scale_invariant_stats_are_nearly_invariant_to_joint_residual_scaling():
    rng=np.random.default_rng(1);z=rng.normal(size=(8,2));r=.4*z+rng.normal(0,.03,size=(8,2))
    a=scale_invariant_window_statistics(z,r);b=scale_invariant_window_statistics(z,2*r)
    assert np.max(np.abs(a-b))<0.01

def test_scale_invariant_stats_distinguish_temporal_shuffle():
    rng=np.random.default_rng(2);z=rng.normal(size=(8,2));r=.35*z+rng.normal(0,.02,size=(8,2))
    a=scale_invariant_window_statistics(z,r);b=scale_invariant_window_statistics(np.roll(z,1,axis=0),r)
    assert a[1]>b[1]
