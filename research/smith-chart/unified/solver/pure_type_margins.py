"""Exact linear shape witnesses for the recorded Hughes target. Author: Komorebi P.

These usable margins cover all RC networks and all RL networks, separately.
They do NOT exclude mixed RLC networks at the four-reactive budget.
"""
from fractions import Fraction as F
import json

P=(4,3,6)
Q=(9,2,6)
SAMPLES=tuple(map(F,('1/2','3/4','1','5/4','3/2','7/4','2')))


def gamma(s):
    p=sum(F(a)*s**i for i,a in enumerate(P))
    q=sum(F(a)*s**i for i,a in enumerate(Q))
    return (p-q)/(p+q)


def certificate():
    values=[gamma(s) for s in SAMPLES]
    weights=(1,-4,6,-4,1)
    residual=sum(F(w)*g for w,g in zip(weights,values))
    rl=residual/sum(abs(w) for w in weights)
    rc=(values[-1]-values[0])/2
    assert rl==F(401,5286560) and rc==F(264,2627)
    assert rl>0 and rc>0
    return {'status':'PASS','target':{'P':list(P),'Q':list(Q)},
        'positive_real_samples':list(map(str,SAMPLES)),
        'RC':{'shape':'gamma is nonincreasing','sample_indices':[0,6],'margin':str(rc)},
        'RL':{'shape':'fourth divided difference of gamma is nonpositive',
            'sample_indices':list(range(5)),'weights':list(weights),
            'target_shape_residual':str(residual),'weight_l1_norm':16,'margin':str(rl)},
        'formal_scope':'Lean checks the sample-error implication given the shape inequality; the network shape theorem remains an explicitly verified classical/written dependency',
        'non_claims':['Not the best margins','Not an exclusion of mixed RLC networks','Not a new all-topology four-reactive refutation']}


if __name__=='__main__':print(json.dumps(certificate(),indent=2))
