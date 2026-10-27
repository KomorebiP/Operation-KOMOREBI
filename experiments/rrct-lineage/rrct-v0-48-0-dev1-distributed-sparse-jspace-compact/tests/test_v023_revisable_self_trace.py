import numpy as np
from rrct.revisable_self_trace_experiment import V023_TRACE_DECAY, V023_BLACKOUT_START, V023_BLACKOUT_END

def test_trace_decay_persists_but_is_not_infinite():
    x=np.array([1.,.4,0.,0.,.2]); y=x.copy()
    for _ in range(V023_BLACKOUT_END-V023_BLACKOUT_START): y*=V023_TRACE_DECAY
    assert np.linalg.norm(y)>0.5*np.linalg.norm(x)
    assert np.linalg.norm(y)<np.linalg.norm(x)

def test_blackout_has_positive_length():
    assert V023_BLACKOUT_END > V023_BLACKOUT_START
