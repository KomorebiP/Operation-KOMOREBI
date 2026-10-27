import numpy as np
from rrct.persistent_self_trace_experiment import V022_TRACE_DECAY

def test_trace_decay_is_bounded_and_persistent():
 x=np.array([1.,.4,0.,0.,.2]);y=x.copy()
 for _ in range(4):y*=V022_TRACE_DECAY
 assert np.linalg.norm(y)>0.5*np.linalg.norm(x)
 assert np.linalg.norm(y)<np.linalg.norm(x)
