#!/usr/bin/env python3
"""Structured rational Bernoulli approximants and exact arithmetic budgets.

No parameter digits are extended. Large-index tests use the proved finite
midpoint formula for depleted Bernoulli units, at the already fixed base r.
"""
from fractions import Fraction as F
from math import comb, factorial, gcd
from pathlib import Path
import json
import sys


def bernoullis(n):
    b=[F(1)]
    for m in range(1,n+1):b.append(-sum(F(comb(m+1,k))*b[k] for k in range(m))/(m+1))
    return b


def trim(p):
    while len(p)>1 and p[-1]==0:p.pop()
    return p


def add(p,q):
    return trim([(p[i] if i<len(p) else 0)+(q[i] if i<len(q) else 0)
                 for i in range(max(len(p),len(q)))])


def scale(p,c):return trim([c*x for x in p])


def mul(p,q):
    out=[0]*(len(p)+len(q)-1)
    for i,x in enumerate(p):
        for j,y in enumerate(q):out[i+j]+=x*y
    return trim(out)


def ev(p,x):
    out=0
    for y in reversed(p):out=out*x+y
    return out


def der(p):return [i*p[i] for i in range(1,len(p))] or [0]


def divide_series(a,d,n):
    out=[]
    for k in range(n+1):
        val=F(a[k] if k<len(a) else 0)
        val-=sum(F(d[j])*out[k-j] for j in range(1,min(k,len(d)-1)+1))
        out.append(val/d[0])
    return out


def fm(q,bits):
    q=F(q);assert q.denominator%2
    return q.numerator*pow(q.denominator,-1,1<<bits)%(1<<bits)


def v2(x,cap):
    x%=1<<cap
    return (x&-x).bit_length()-1 if x else cap


def binom_int(n,k):
    z=1
    for j in range(k):z=z*(n-j)//(j+1)
    return z


def main(output):
    maximum=24
    B=bernoullis(80)
    a=[F(1)]+[F(4**m,factorial(2*m))*B[2*m] for m in range(1,41)]
    A=[[1],[3,1]];D=[[1],[3]]
    for n in range(2,maximum+1):
        A.append(add(scale(A[-1],2*n+1),[0]+A[-2]))
        D.append(add(scale(D[-1],2*n+1),[0]+D[-2]))
    heights=[];coefficient_checks=0
    for n in range(1,maximum+1):
        determinant=add(mul(A[n],D[n-1]),scale(mul(A[n-1],D[n]),-1))
        assert determinant==[0]*n+[(-1)**(n-1)]
        series=divide_series(A[n],D[n],n+1)
        for k in range(n+1):assert series[k]==a[k];coefficient_checks+=1
        odd_product=1
        for j in range(1,n+1):odd_product*=2*j+1
        expected=F((-1)**n,odd_product**2*(2*n+3))
        assert a[n+1]-series[n+1]==expected
        assert expected.numerator%2 and expected.denominator%2
        for exponent in (1,2):
            w=1<<(2*exponent)
            numerator,denominator=ev(A[n],w),ev(D[n],w)
            assert numerator>denominator>=odd_product and gcd(numerator,denominator)==1
            error_bits=2*exponent*(n+1);bits=error_bits+8;modulus=1<<bits
            count=(bits+2*exponent-1)//(2*exponent)+1
            true_g=sum(fm(a[k],bits)*pow(w,k,modulus) for k in range(count+1))%modulus
            true_f=sum(fm((1-2*k)*a[k],bits)*pow(w,k,modulus)
                       for k in range(count+1))%modulus
            model_g=F(numerator,denominator)
            model_f=model_g-2*w*F(ev(der(A[n]),w)*denominator-
                                      numerator*ev(der(D[n]),w),denominator**2)
            assert v2(true_g-fm(model_g,bits),bits)==error_bits
            assert v2(true_f-fm(model_f,bits),bits)==error_bits
            height=max(abs(model_f.numerator),model_f.denominator)
            if exponent==1 and n>=3:assert numerator>1<<error_bits
            heights.append({'N':n,'z_power_of_two':exponent,'exact_error_bits':error_bits,
                'g_height':str(numerator),'g_height_bit_length':numerator.bit_length(),
                'g_height_exceeds_precision':numerator>1<<error_bits,
                'f_height_bit_length':height.bit_length()})
    # Shifted actual-unit model, at the existing base index and its low residue.
    bits=32;modulus=1<<bits
    def depleted(m):
        return fm(sum(F(2**j)*B[j]*binom_int(2*m,j) for j in range(bits+2)),bits)
    def first_four(r):
        units=[depleted(r+q) for q in range(4)]
        c=[16]
        for q in range(1,4):
            factor=F(16*4**q)
            for j in range(1,2*q+1):factor/=2*r+j
            c.append(fm(factor,bits)*units[q]*pow(units[0],-1,modulus)%modulus)
        c0,c1,c2,c3=c
        det=(c1*c1-c0*c2)%modulus
        assert det%2
        q1=(c0*c3-c1*c2)*pow(det,-1,modulus)%modulus
        q2=(c2*c2-c1*c3)*pow(det,-1,modulus)%modulus
        assert [v2(x,bits) for x in c]==[4,0,1,1]
        assert v2(q1,bits)==v2(q2,bits)==1
        assert (c2+q1*c1+q2*c0)%modulus==0
        assert (c3+q1*c2+q2*c1)%modulus==0
        return units,c,q1,q2
    base_r=(17659<<640)-161
    low=first_four(-161);actual=first_four(base_r)
    assert low==actual
    units,c,q1,q2=actual
    assert [x%2048 for x in c]==[16,1,1386,1190]
    assert [q1%32,q2%32]==[22,30]
    # The recurrence bound is checked through q=63; its uniform proof is in the note.
    series=c[:2]
    for q in range(2,64):
        series.append((-q1*series[-1]-q2*series[-2])%modulus)
        assert v2(series[q],bits)>=min(q//2,bits)
    def source(n):
        denominator=8*(n+1)*(2*n+1)
        dval=v2(denominator,128)
        numerator=(pow(9,n+1,1<<(bits+dval))-1)%(1<<(bits+dval))
        assert numerator%(1<<dval)==0
        return (numerator>>dval)*pow(denominator>>dval,-1,modulus)%modulus
    def packet(x,q):
        product=1
        for j in range(q):product*= (x-j)*(2*x-2*j-1)
        return product*source(x-q)%modulus
    terms=[]
    for q in range(4):
        odd=(2*base_r+2*q-1)*pow(2*base_r-1,-1,modulus)%modulus
        terms.append(pow(8,q,modulus)*c[q]*odd*packet(10202,q)%modulus)
    assert [t%2048 for t in terms]==[592,688,1792,0]
    assert v2(terms[3],bits)==14
    assert sum(terms)%2048==1024
    # Exact Kummer valuation for the nonconvergent rank-one packets.
    divergence=[]
    for k in range(15,25):
        q=1<<k;m=22566
        binomial_val=q.bit_count()+(m-1).bit_count()-(q+m-1).bit_count()
        pval=q-q.bit_count()+binomial_val
        termval=-24+3*q-4*q+pval
        assert binomial_val==0 and termval==-25
        divergence.append({'k':k,'binomial_valuation':binomial_val,'K_packet_valuation':termval})
    out={'status':'passed','arithmetic':'exact Python integers and fractions.Fraction',
        'continued_fraction_N_range':[1,maximum],
        'matched_coefficient_checks':coefficient_checks,
        'exact_error_and_height_records':heights,
        'shifted_unit_precision':bits,
        'depleted_units_mod32':[x%32 for x in units],
        'scaled_shifted_moments_mod2048':[x%2048 for x in c],
        'rank_two_denominator_mod32':[q1%32,q2%32],
        'rank_two_deep_packet_terms_mod2048':[t%2048 for t in terms],
        'rank_two_M_value_valuation':10,'rank_two_K_value_valuation':-18,
        'rank_one_divergence_controls':divergence,
        'base_r_bit_length':base_r.bit_length(),
        'nonclaims':['No actual critical nonvanishing theorem.',
            'No multiplier digit extension.',
            'No assertion that source transformation preserves rationality.',
            'No higher-order shifted Hankel nonsingularity or denominator budget.']}
    Path(output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in
        ('exact_error_and_height_records','rank_one_divergence_controls')},indent=2))


if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'PADE_CHECKS.json')
