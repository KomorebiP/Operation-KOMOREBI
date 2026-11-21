"""Complete degree-25 polynomial certificate for every quadratic weight."""
import argparse,json,time
from fractions import Fraction as F
from functools import lru_cache
from math import comb
from pathlib import Path
import sequence_parity_hankel as p



@lru_cache(None)
def fixed_band(i,j,weights):
    return sum(F((-1)**(s+t)*comb(4,s)*comb(4,t))*p.base.chebyshev_jet_gram_entry(i-2*s,j-2*t,weights,(F(1),))
               for s in range(5) if 2*s<=i for t in range(5) if 2*t<=j)

@lru_cache(None)
def fixed_tail(d,weights):
    a,b,c=weights
    def tau(n):
        n=abs(n)
        return 2*a if not n else (F(0) if n%2 else (b-c)*n+c*F(n**3,4))
    return sum(F((-1)**(s+t)*comb(4,s)*comb(4,t))*tau(d-2*s+2*t)
               for s in range(5) for t in range(5))


def multiply(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out


def quartic(a,b,c):
    return [16*a**4,-32*a**3+32*a*a*b-96*a*a*c,
            24*a*a-32*a*b-96*a*c+16*b*b,-8*a+8*b-24*c,F(1)]


def check(a,b,c):
    g=quartic(F(a),F(b),F(c));q=multiply(multiply(g,g),multiply(g,g))
    weights=[a,b,c];operator=[1];w=4;K=9;initial=tuple(range(w));vectors=0;early=0
    tail=tuple(fixed_tail(2*(w-k),tuple(map(F,weights))) for k in range(2*w+1))
    for parity in (0,1):
        v={initial:F(1)};residual={};values=[F(1)]
        for i in range(K+16):
            diagonal=tail if i>=K else [
                fixed_band(2*i+parity,2*(i-w+k)+parity,tuple(map(F,weights)))
                if i-w+k>=0 else F(0) for k in range(2*w+1)]
            v=p.base._step(v,w,diagonal);values.append(v.get(initial,F(0)))
            n=i+1
            if K<=n<=K+16:p.base._add_scaled(residual,v,q[n-K])
        assert not residual,(a,b,c,parity,'full state');vectors+=1
        for n in range(1,K):
            assert not sum(q[j]*values[n+j] for j in range(17)),(a,b,c,parity,n)
            early+=1
    return vectors,early


parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
args=parser.parse_args();started=time.perf_counter();vectors=early=points=0
for b in range(26):
    for a in range(26-b):
        v,e=check(a,b,1);vectors+=v;early+=e;points+=1
    print(json.dumps({'b':b,'points':points,'elapsed':time.perf_counter()-started}),flush=True)
# Off-grid checks are regression evidence, separate from the complete grid.
extra=[(-2,3,1),(0,0,1),(1,2,1),(1,1,0),(0,0,0),(F(1,2),F(-2,3),F(3,5))]
for a,b,c in extra:
    # With c=0 use a fixed M=2 model, not the actual-degree helper.
    assert check(a,b,c)==(2,16)
result={'outcome':'Complete degree-25 vector-polynomial certificate verified',
    'conventions':'P(m)=a+b*m+c*m*(m-1); identity operator; fixed M=2, width4, stationary row9 for both parity blocks',
    'homogeneous_full_state_residual_degree':25,'interpolation_grid':'c=1, a>=0,b>=0,a+b<=25',
    'complete_parameter_points':points,'full_70_state_vector_identities':vectors,
    'early_scalar_identities':early,'early_indices':[1,8],
    'off_grid_cases':[[str(x) for x in row] for row in extra],
    'quartic_descending':['1','-8a+8b-24c','24a^2-32ab-96ac+16b^2','-32a^3+32a^2b-96a^2c','16a^4'],
    'block_annihilator':'g(S)^4 from n>=1',
    'scope':'Uniform characteristic-zero conclusion requires the written homogeneity and triangular interpolation proof; no all-parameter minimality claim.',
    'elapsed_seconds':time.perf_counter()-started}
Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))
