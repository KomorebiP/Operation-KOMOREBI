"""Supplied synthetic environment. Author: Komorebi P.

The editor receives output profiles, not coefficient labels. The environment
still defines the polynomial family and the three kinds of query.
"""
import numpy as np
from workspace import features, coefficients, truth

POINTS = np.array([(x,z) for x in [-2.,-1.,0.,1.,2.] for z in [-2.,-1.,0.,1.,2.]])
ANCHORS = np.array([12,17,7,13,11,18])

def panel(points=POINTS):
    p=features(points);origin=features(np.array([0.,0.]))
    return np.stack([p,p-origin,p+origin])

def calibration_profiles(seed=50101,count=256,cubic=False,shuffle=False,points=POINTS):
    rng=np.random.default_rng(seed)
    c=coefficients(rng,count)
    values=10*truth(c[:,None,:],points)
    if cubic:
        values+=rng.integers(-2,3,(count,1))*points[None,:,0]**3
    origin=c[:,0,None]
    profiles=np.stack([values,values-origin,values+origin],axis=1)
    if shuffle:
        # Preserve each reader's marginal examples, destroy their correspondence.
        profiles[:,1]=profiles[rng.permutation(count),1]
        profiles[:,2]=profiles[rng.permutation(count),2]
    return profiles.reshape(count,-1)

def observer(model,descriptors=None):
    desc=panel() if descriptors is None else np.asarray(descriptors,float)
    def observe(states):
        states=np.atleast_2d(states)
        repeated=np.broadcast_to(desc,(len(states),)+desc.shape)
        return (10*model.predict(states,repeated)).reshape(len(states),-1)
    return observe
