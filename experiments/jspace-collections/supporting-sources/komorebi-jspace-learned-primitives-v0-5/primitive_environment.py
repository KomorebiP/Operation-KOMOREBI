"""External observation source, never imported by the primitive executor.

Author: Komorebi P. Operation channels are supplied. Their formulas and names
are available to the environment/scorer, not to the neural learner.
"""
import numpy as np

CHANNELS=['channel_17','channel_42','channel_91','channel_63']

def outcomes(xy):
    x,y=np.asarray(xy).T
    return np.stack([x-y,x*y,x+y,np.maximum(x,y)],axis=0)

def dataset(seed,count=2048,bound=2.):
    rng=np.random.default_rng(seed);xy=rng.uniform(-bound,bound,(count,2))
    return xy,outcomes(xy)

def primitive_cases(seed=93011,count=1024):
    rng=np.random.default_rng(seed)
    return {'in_range':rng.uniform(-2,2,(count,2)),
            'larger_inputs':rng.uniform(-6,6,(count,2)),
            'unequal_magnitudes':np.column_stack([rng.uniform(-6,6,count),rng.uniform(-.1,.1,count)])}

def higher_targets(xy):
    x,z=np.asarray(xy).T
    return np.stack([x**3,x*x*z,x*z*z,z**3,x**4,x**3*z,x*x*z*z,x*z**3,z**4])

def higher_names():return ['x^3','x^2 z','x z^2','z^3','x^4','x^3 z','x^2 z^2','x z^3','z^4']

def world_values(base,higher,amplitude,xy):
    x,z=np.asarray(xy).T;a=np.asarray(base)
    return a[0]+a[1]*x+a[2]*z+a[3]*x*z+a[4]*x*x+a[5]*z*z+amplitude*higher_targets(xy)[higher]
