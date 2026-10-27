#!/usr/bin/env python3
"""Exact narrow controls for weighted/Riccati kernel tail identities."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import argparse, json, time, platform

def v2(q):
    def vi(n):return (abs(n)&-abs(n)).bit_length()-1
    return vi(q.numerator)-vi(q.denominator)

def run():
    start=time.monotonic(); N=32
    # Independent construction: f(t) is reciprocal of sinh(sqrt(t))^2/t.
    d=[Q(2**(2*n+1),factorial(2*n+2)) for n in range(N+1)]
    beta=[Q(1)]
    for n in range(1,N+1):beta.append(-sum((d[i]*beta[n-i] for i in range(1,n+1)),Q(0)))
    aa=[b/Q(1-2*n) for n,b in enumerate(beta)]
    counts={'unweighted_kernel':0,'weighted_kernel':0,'weighted_tail':0,'riccati_tail':0,'nonunit_cancellation':0}
    for n in range(2,N+1):
        s=sum((beta[i]*beta[n-i]/Q((2*i-1)*(2*n-2*i-1)) for i in range(1,n)),Q(0))
        w=sum((4**i*beta[i]*beta[n-i]/Q((2*i-1)*(2*n-2*i-1)) for i in range(1,n)),Q(0))
        assert s==Q(2*n+1,2*n-1)*beta[n]
        assert w==Q(2*n+4**n,2*n-1)*beta[n]
        counts['unweighted_kernel']+=1;counts['weighted_kernel']+=1
    assert all(v2(beta[n])==n.bit_count()-1 for n in range(1,N+1))
    for r in range(2,13):
        for q in range(17):
            C=sum((4**(r+q-i)*aa[i]*aa[r+q-i] for i in range(q+1,r)),Q(0)) if q<=r-2 else Q(0)
            F=-sum((aa[i]*aa[r+q-i] for i in range(q+1,r)),Q(0)) if q<=r-2 else Q(0)
            rhs=sum((aa[r+i]*4**(q-i)*aa[q-i] for i in range(q+1)),Q(0))
            rhs+=4**r*sum((aa[i]*4**(q-i)*aa[r+q-i] for i in range(min(q,r-1)+1)),Q(0))+C
            assert rhs==beta[r+q];counts['weighted_tail']+=1
            rhs=(1-2*r)*aa[r+q]-2*sum((aa[i]*aa[r+q-i] for i in range(min(q,r-1)+1)),Q(0))+F
            if q>=r:rhs-=sum((aa[r+i]*aa[r+q-r-i] for i in range(q-r+1)),Q(0))
            assert rhs==2*q*aa[r+q];counts['riccati_tail']+=1
            if q==0:
                assert C==Q(2*r+4**r,2*r-1)*beta[r]
                assert 4**r*aa[r]+Q(4**r,2*r-1)*beta[r]==0
                counts['nonunit_cancellation']+=1
    r=2
    missing_cross=(1+4**r)*aa[r]
    assert missing_cross!=beta[r]
    image=8*aa[1]
    assert image==Q(8,3)
    return {'status':'passed','runtime_seconds':time.monotonic()-start,'python':platform.python_version(),
            'coefficient_domain':'Exact fractions over Q','kernel_coefficient_range':[0,N],
            'tail_r_range':[2,12],'tail_q_range':[0,16],'counts':counts,
            'negative_control_without_cross_boundary':{'r':2,'true_beta':'1/15','incorrect_without_C':str(missing_cross)},
            'zero_descent_counterexample':{'input':'(x-1)^2','input_value_at1':0,'input_derivative_at1':0,'T_g_value_at1':str(image)},
            'nonclaims':['No actual Euler nonintersection','No additional parameter precision','No Lean compilation']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    r=run();Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
