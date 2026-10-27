import numpy as np
from rrct.active_self_discovery_experiment import _active_probe, _design_uncertainty, _hidden_interface, _response


def test_active_probe_targets_largest_design_uncertainty():
    rng=np.random.default_rng(7)
    meta=[np.array([1.,0,0,0,0,0]) for _ in range(20)]
    z=_active_probe(meta,rng)
    assert abs(z[0]) < 1e-8
    assert np.isclose(np.linalg.norm(z),1.0)


def test_design_uncertainty_falls_with_balanced_probing():
    interface=_hidden_interface(3);rng=np.random.default_rng(9)
    z=[];c=[];y=[];n=[]
    vals=[]
    for i in range(180):
        probe=np.eye(6)[i%6]
        cc,yy,nn=_response(rng,probe,interface,.12)
        z.append(probe);c.append(cc);y.append(yy);n.append(nn)
        if i in (59,119,179): vals.append(_design_uncertainty(np.asarray(z),np.asarray(c),np.asarray(y),np.asarray(n)))
    assert vals[2] < vals[1] < vals[0]
