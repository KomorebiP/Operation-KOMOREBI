import numpy as np
from rrct.contextual_self_access_experiment import _ComparisonReadout
from rrct.metacognitive_closure_experiment import MetacognitiveAccessReadout

def _fit_constant(target):
    m=MetacognitiveAccessReadout();x=np.zeros((4,29));x[:,0]=1;y=np.tile(np.asarray(target,float),(4,1));m.fit(x,y);return m

def test_comparison_readout_records_generic_and_returns_contextual():
    contextual=_fit_constant([0.8,0.2,0.1]);generic=_fit_constant([-0.6,0.7,0.3]);c=_ComparisonReadout(contextual,generic)
    out=c.predict(np.zeros(16),np.zeros(12))
    assert out[0] > 0.5
    assert len(c.generic_predictions)==1
    assert c.generic_predictions[0][0] < 0.0

def test_comparison_readout_is_noncausal_recorder():
    contextual=_fit_constant([0.2,0.2,0.1]);generic=_fit_constant([0.2,0.2,0.1]);c=_ComparisonReadout(contextual,generic)
    w=np.arange(16,dtype=float)/20;s=np.arange(12,dtype=float)/20
    a=c.predict(w,s);b=contextual.predict(w,s)
    assert np.allclose(a,b)
