#!/usr/bin/env python3
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json
import sys
from check_structure import bernoullis,eulers,skeleton,source

def power9(s):
    s=F(s)
    assert (2*s).denominator==1
    return F(-3)**int(2*s)

def A(s):
    s=F(s)
    assert s not in [F(-1),F(-1,2)]
    return (9*power9(s)-1)/(8*(s+1)*(2*s+1))

def main(out):
    b=bernoullis(64);e=eulers(32)
    beta=[F(1)]+[-F(4**n*(2*n-1),factorial(2*n))*b[2*n]
                 for n in range(1,33)]
    a=[F(1)]+[-beta[n]/(2*n-1) for n in range(1,33)]
    count_weighted=count_cutoff=count_shift=0
    for n in range(33):
        conv=sum(4**j*a[j]*a[n-j] for j in range(n+1))
        assert conv==beta[n]+(2 if n==1 else 0)
        count_weighted+=1
    for r in range(2,17):
        c={n:sum(4**j*a[j]*a[n-j]
                    for j in range(max(0,n-r+1),min(r-1,n)+1))
           for n in range(r,2*r-1)}
        assert c[r]==F(2*r+4**r,2*r-1)*beta[r]
        assert c[2*r-2]==4**(r-1)*a[r-1]**2
        for n in range(r,33):
            first=sum(a[i]*4**(n-i)*a[n-i] for i in range(r,n+1))
            second=sum(a[i]*4**(n-i)*a[n-i]
                       for i in range(min(r-1,n-r)+1))
            assert first+second+c.get(n,0)==beta[n]
            count_cutoff+=1
    def M(r,s):
        c=(3*power9(s)-1)/(2*(2*s+1))
        return c-sum(8**n*a[n]*skeleton(s,n)*A(s-n) for n in range(r))
    for n in range(2,25):
        for r in range(2,n+1):
            f=F(e[n])-sum(8**m*beta[m]*skeleton(n,m)*source(n-m)
                         for m in range(r))
            m=M(r,F(n));mh=M(r,F(2*n-1,2))
            uh=sum(8**j*a[j]*F(1,9**j)*skeleton(F(2*n-1,2),j-1)
                   for j in range(r,n+1))
            rhs=-(2*n*(m-mh)+m)+F(n*9**(n+1),3)*uh
            assert f==rhs
            count_shift+=1
    result={'status':'passed','base_checkpoint':'Euler-coupled-stationarity-20261005',
            'exact_arithmetic':'fractions.Fraction',
            'weighted_coefficients_n0_to32':count_weighted,
            'cutoff_identity_coefficients_r2_to16_n_to32':count_cutoff,
            'half_shift_pairs_2_le_r_le_N_le24':count_shift,
            'half_shift_branch':'9^(s-1/2)=−9^s/3',
            'nonclaims':['No critical-value nonvanishing theorem',
                         'No omission of the finite cross-boundary defect',
                         'The half-shift operator is not ordinary differentiation']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'WEIGHTED_TAIL_CHECKS.json')
