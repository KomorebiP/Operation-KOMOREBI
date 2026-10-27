#!/usr/bin/env python3
"""Exact ordinary-index evidence for the all-step theorem and actual row bridge."""
from fractions import Fraction as F
from math import comb,factorial
from pathlib import Path
import json,sys

def bernoulli(n):
    b=[F(1)]
    for m in range(1,n+1):b.append(-sum(comb(m+1,j)*b[j] for j in range(m))/(m+1))
    return b
def v2(x):
    x=F(x)
    if not x:return None
    a,b=abs(x.numerator),x.denominator
    return (a&-a).bit_length()-(b&-b).bit_length()
def determinant(a):
    a=[list(map(F,r)) for r in a];d=F(1)
    for j in range(len(a)):
        p=next((p for p in range(j,len(a)) if a[p][j]),None)
        if p is None:return F(0)
        if p!=j:a[j],a[p]=a[p],a[j];d=-d
        z=a[j][j];d*=z
        for p in range(j+1,len(a)):
            t=a[p][j]/z
            for k in range(j+1,len(a)):a[p][k]-=t*a[j][k]
    return d
def P(y,n):
    z=F(1)
    for j in range(n):z*=(y-j)*(2*y-2*j-1)
    return z
def A(y):return F(9**(y+1)-1,8*(y+1)*(2*y+1))
def A_mod(y,mod):
    den=8*(y+1)*(2*y+1);vd=v2(den)
    num=(pow(9,y+1,mod*(2**vd))-1)//(2**vd)
    return num*pow(den//(2**vd),-1,mod)%mod
def chart_coeffs(r,x,cutoff=160,mod=16):
    # D cancels exactly from Xi. The undepletion correction is1 mod16,
    # since epsilon has valuation2r-1 and every final coefficient is integral.
    assert 2*r-1>=4
    result=[A_mod(x,mod)];sv,pv=0,0;su,pu=1,1
    for q in range(1,cutoff+1):
        den=r+q;vd=v2(den);sv+=4-vd
        su=su*pow((2*r+2*q-3)*(den//(2**vd)),-1,mod)%mod
        fac=x-q+1;vf=v2(fac);pv+=vf
        pu=pu*(fac//(2**vf))*(2*x-2*q+1)%mod
        value_v=sv+pv
        assert value_v>=0
        if q>=2:assert value_v>=4
        result.append((2**value_v)*su*pu*A_mod(x-q,mod)%mod if value_v<4 else 0)
    return result
def main(out):
    B=bernoulli(118)
    D=lambda n: F(1) if not n else 2*(1-2**(2*n-1))*B[2*n]
    beta=lambda n: F(1) if not n else -F(4**n*(2*n-1),factorial(2*n))*B[2*n]
    gamma=lambda n:F(8**n)*beta(n)/D(n)
    vals=[];det_checks=0
    for m in range(1,7):
        baseline=2*m*(m-1)+4*sum(v2(factorial(k)) for k in range(m))
        step=[]
        for q in range(1,6):
            vv=[]
            for x in range(10):
                z=determinant([[D(x+(i+j)*q) for j in range(m)] for i in range(m)])
                expect=baseline+m*(m-1)*v2(q)
                assert v2(z)==expect
                vv.append(v2(z));det_checks+=1
            step.append({'q':q,'valuations_x_0_to_9':vv})
        vals.append({'matrix_order':m,'steps':step})
    E=[1]
    for n in range(1,15):E.append(-sum(comb(2*n,2*j)*E[j] for j in range(n)))
    row_checks=0;samples=[]
    for r in range(1,7):
        for y in range(9):
            s=r+y
            coeff=[gamma(r+q)*P(y,q)*A(y-q) for q in range(y+1)]
            row=sum(coeff[q]*D(r+q) for q in range(y+1))
            prefix=sum(8**n*beta(n)*P(s,n)*A(s-n) for n in range(r))
            original=F(E[s]-prefix,P(s,r))
            assert row==original
            assert coeff[-1]!=0
            row_checks+=1
            if r<=2 and y<=2:samples.append({'r':r,'y':y,'kernel_coefficients':[str(c) for c in coeff],'actual_pairing':str(row)})
    w=[F(40,3),F(64,7)]
    mean=w[0]*D(1)+w[1]*D(2)
    norm=w[0]**2*D(1)+2*w[0]*w[1]*D(2)+w[1]**2*D(3)
    hankel=D(1)*D(3)-D(2)**2
    schur=norm-mean**2/D(1)
    assert mean==F(-8,45) and hankel==F(48,175) and schur==F(-589824,8575)
    assert schur==w[1]**2*hankel/D(1)
    # Unit norm recurrence and occupied factorial lattice, independently checked.
    rho=lambda n:-F(n**4,4*n*n-1)
    lattice=[]
    for n in range(1,13):
        aa=rho(2*n)*rho(2*n-1);bb=rho(2*n)+rho(2*n+1)
        assert v2(aa/16)>=0 and v2((bb-1)/4)>=0
        hh=F(factorial(2*n)**4,4**(2*n)*factorial(n)**4)
        for j in range(1,2*n+1):hh/=4*j*j-1
        assert v2(hh)==0
        unit=hh.numerator*pow(hh.denominator,-1,16)%16
        assert unit==pow(5,n,16)
        lattice.append({'n':n,'norm_mod16':unit,'downward_K_in_f_valuation':v2(aa/16)})
    chart=[]
    for T in [0,1,22831001499602523078606181325]:
        r=(17659+2**18*T)*2**640-161
        for Z in [0,1,5]:
            x=10202+2**15*Z;coeff=chart_coeffs(r,x)
            assert coeff[:2]==[5,15] and all(c==0 for c in coeff[2:])
            u1=sum(coeff)%16;u9=sum(c*pow(9,q,16) for q,c in enumerate(coeff))%16
            assert (u1,u9)==(4,12)
            chart.append({'T':str(T),'Z':Z,'q0_mod16':coeff[0],'q1_mod16':coeff[1],
              'q2_to_q160_zero_mod16':True,'Xi_at_U1_mod16':u1,'Xi_at_U9_mod16':u9,'normalized_ratio_mod4':3})
    finite_bounds=[4*q+3-(321-2*q).bit_count()-q.bit_count() for q in range(2,161)]
    assert finite_bounds[:3]==[4,7,13] and min(finite_bounds)==4
    result={'status':'passed','determinant_checks':det_checks,'orders':[1,6],'x_range':[0,9],'q_range':[1,5],
      'determinant_valuations':vals,'actual_row_checks':row_checks,'row_cutoff_range':[1,6],'row_argument_range':[0,8],
      'row_samples':samples,'actual_linear_kernel_schur':{'mean':str(mean),'hankel_minor':str(hankel),'schur':str(schur)},
      'orthogonal_lattice_checks':lattice,
      'actual_chart_square_obstruction_checks':chart,'finite_gamma_bound_min_q2_to_q160':min(finite_bounds),
      'nonclaims':['Finite ordinary checks do not establish all dyadic x,q; the separate completed-lattice proof does.',
        'No actual stationary Euler nonvanishing theorem.','No undepleted q-step transfer threshold asserted.']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','determinants':det_checks,'actual_row_checks':row_checks,'lattice_checks':len(lattice)}))
if __name__=='__main__':main(sys.argv[1])
