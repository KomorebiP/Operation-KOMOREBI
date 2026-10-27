import numpy as np
from rrct.self_calibrating_access_experiment import _ownership
class C:
 def predict_probability(self,x): return 0.8

def test_ownership_requires_full_private_probe_window():
 assert np.isnan(_ownership(C(),[np.zeros(2)]*7,[np.zeros(2)]*7))

def test_ownership_uses_full_window_when_available():
 assert np.isclose(_ownership(C(),[np.zeros(2)]*8,[np.zeros(2)]*8),0.8)
