"""Series-L/RC and series-C/RL sample separators. Author: Komorebi P.

Continuous physical scope is the written Stieltjes argument; this is its exact
finite stencil and sample-transfer arithmetic, not a topology enumeration.
"""
from fractions import Fraction as F
import json
from pure_type_margins import SAMPLES,P,Q,gamma


def target(s):
    return sum(F(a)*s**i for i,a in enumerate(P))/sum(F(a)*s**i for i,a in enumerate(Q))


def certificate():
    rows=[]
    for name,indices,weights,margin in (
        ('series-L-with-RC',(0,1,2),(F(1),F(-2),F(1)),F(1,2000)),
        ('series-C-with-RL',tuple(range(7)),tuple(s*w for s,w in zip(SAMPLES,(1,-6,15,-20,15,-6,1))),F(1,500000))):
        residual=sum(w*target(SAMPLES[j]) for j,w in zip(indices,weights))
        norm=sum(abs(w) for w in weights)
        assert residual<0 and 0<margin<=F(1,2) and 4*margin*norm<-residual
        assert all(-1<gamma(s)<0 for s in SAMPLES)
        # Each basis kernel 1/(s+t) has a nonnegative second/sixth difference.
        # Verify the exact rational identity by polynomial multiplication,
        # independently of evaluating finitely many t's.
        nodes=[SAMPLES[j] for j in indices]
        numerator=[F(0)]*len(nodes)
        for j,w in enumerate(weights):
            # For the capacitor class, the shape is applied to s*Z;
            # divide the recorded Z weights by s to obtain its stencil.
            w=w/(nodes[j] if name=='series-C-with-RL' else 1)
            poly=[F(1)]
            for k,s in enumerate(nodes):
                if j==k:continue
                out=[F(0)]*(len(poly)+1)
                for i,v in enumerate(poly):out[i]+=s*v;out[i+1]+=v
                poly=out
            for i,v in enumerate(poly):numerator[i]+=w*v
        assert numerator[0]>0 and not any(numerator[1:])
        rows.append({'class':name,'sample_indices':list(indices),'Z_weights':list(map(str,weights)),
          'target_residual':str(residual),'weight_l1_norm':str(norm),'reflection_margin':str(margin),
          'kernel_numerator':str(numerator[0]),'strict_transfer_slack':str(-residual-4*margin*norm)})
    return {'status':'PASS','certificates':rows,
      'scope':'An actual series branch or series one-port with no resistor bypass, followed by an arbitrary RC/RL one-port. Any positive opposite-kind series reactance is allowed; arbitrary resistor and same-kind storage counts. Positive-real Laplace samples only.',
      'coverage_accounting':'No additional entire complete-resistor-core skeleton is claimed: unrestricted resistor placements may bypass the series element.',
      'formal_scope':'Written Stieltjes and reflection-transfer proof plus exact rational stencil arithmetic; selected Lean count remains 41.'}


def verify(record):
    if record!=certificate():raise ValueError('Series separator binding differs')
    return {'status':'PASS','classes':2}


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(certificate(),indent=2))
