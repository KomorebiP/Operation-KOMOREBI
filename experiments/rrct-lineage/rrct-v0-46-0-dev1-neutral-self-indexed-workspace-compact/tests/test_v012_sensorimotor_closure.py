import numpy as np

from rrct.sensorimotor_closure_experiment import SensorimotorRidgeModel, _derange_actions


def _rows():
    rows=[]
    for i in range(8):
        o=np.zeros(12);o[0]=i/10;o[11]=1
        a=np.asarray([(-1)**i*0.2,0.1*i/8])
        n=o.copy();n[0]+=0.3*a[0];n[1]+=0.3*a[1]
        rows.append((o,a,n))
    return rows


def test_action_conditioned_model_uses_action_channel():
    m=SensorimotorRidgeModel(action_conditioned=True);m.fit(_rows())
    obs=_rows()[0][0]
    left=m.predict(obs,np.asarray([0.8,0.0]));right=m.predict(obs,np.asarray([-0.8,0.0]))
    assert not np.allclose(left,right)


def test_no_action_model_is_action_invariant():
    m=SensorimotorRidgeModel(action_conditioned=False);m.fit(_rows())
    obs=_rows()[0][0]
    left=m.predict(obs,np.asarray([0.8,0.0]));right=m.predict(obs,np.asarray([-0.8,0.0]))
    assert np.allclose(left,right)


def test_deranged_actions_have_no_fixed_assignments():
    rows=_rows(); shuffled=_derange_actions(rows,91)
    original=[tuple(v[1]) for v in rows]; changed=[tuple(v[1]) for v in shuffled]
    assert all(a!=b for a,b in zip(original,changed))
    assert sorted(original)==sorted(changed)


def test_sensorimotor_predictions_are_finite_and_bounded():
    m=SensorimotorRidgeModel(action_conditioned=True);m.fit(_rows())
    out=m.predict(np.zeros(12),np.asarray([1.0,-1.0]))
    assert out.shape==(12,)
    assert np.all(np.isfinite(out))
    assert np.all(np.abs(out[:6])<=1.0)
    assert 0.0<=out[6]<=1.0
