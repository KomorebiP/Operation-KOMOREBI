#!/usr/bin/env python3
"""Exact cyclotomic identities supporting, but not proving, the AI occurrence claim.
Domain Q[x]/(Phi_9(1+x)); local valuation v_L(3)=6, v_L(x)=1.
No p-adic approximation, sampled fields, representation library, or floating arithmetic.
"""
from fractions import Fraction as Q
import json

N=6
f=[3,9,18,21,15,6,1]
def elt(a): return tuple(Q(v) for v in a)+tuple(Q(0) for _ in range(N-len(a)))
zero=elt([]); one=elt([1]); x=elt([0,1])
def add(a,b): return tuple(u+v for u,v in zip(a,b))
def neg(a): return tuple(-v for v in a)
def sub(a,b): return add(a,neg(b))
def scale(a,c): return tuple(v*c for v in a)
def mul(a,b):
    c=[Q(0)]*(2*N-1)
    for i in range(N):
        for j in range(N): c[i+j]+=a[i]*b[j]
    for i in range(2*N-2,N-1,-1):
        t=c[i]
        for j in range(N): c[i-N+j]-=t*f[j]
    return tuple(c[:N])
def power(a,n):
    if n<0: return power(inv(a),-n)
    y=one
    while n:
        if n&1: y=mul(y,a)
        a=mul(a,a); n//=2
    return y
def inv(a):
    cols=[mul(a,power(x,j)) for j in range(N)]
    m=[[cols[j][i] for j in range(N)]+[one[i]] for i in range(N)]
    for i in range(N):
        k=next(k for k in range(i,N) if m[k][i])
        m[i],m[k]=m[k],m[i]
        t=m[i][i]; m[i]=[v/t for v in m[i]]
        for k in range(N):
            if k!=i:
                t=m[k][i]; m[k]=[v-t*w for v,w in zip(m[k],m[i])]
    return tuple(m[i][-1] for i in range(N))
def eval_at(a,y):
    z=zero
    for c in reversed(a): z=add(mul(z,y),scale(one,c))
    return z
def trace(a): return sum(mul(a,power(x,j))[j] for j in range(N))
def v3(q):
    q=Q(q)
    if not q:return None
    n,d=q.numerator,q.denominator; a=0
    while n%3==0: n//=3; a+=1
    while d%3==0: d//=3; a-=1
    return a
def valuation(a):
    return min(6*v3(c)+i for i,c in enumerate(a) if c)
def encode(a):return [str(v) for v in a]
def fractional_part_3(q):
    q=Q(q)
    d=q.denominator
    if d==1:return Q(0)
    k=0
    while d%3==0:d//=3;k+=1
    den=3**k
    residue=(q.numerator*pow(d,-1,den))%den
    return Q(residue,den)

zeta=add(one,x)
sigma_x=sub(power(zeta,4),one)
sigma=lambda a:eval_at(a,sigma_x)
zeta3=power(zeta,3)
piF=sub(zeta3,one)
beta=power(x,-10)
delta=sub(sigma(beta),beta)
checks={
 'zeta9_order': power(zeta,9)==one and power(zeta,3)!=one,
 'eisenstein_relative_polynomial': sub(add(add(power(x,3),scale(power(x,2),3)),scale(x,3)),piF)==zero,
 'sigma_order3': sigma(sigma(sigma(x)))==x and sigma(x)!=x,
 'sigma_fixes_F': sigma(piF)==piF,
 'beta_inverse_identity': mul(beta,power(x,10))==one,
 'trace_scalar': trace(one)==6,
 'trace_invariance': trace(beta)==trace(sigma(beta)),
 'different_relative_exponent6': valuation(scale(power(zeta,2),3))==6,
 'piF_valuation3': valuation(piF)==3,
 'relative_sigma_displacement': valuation(sub(mul(sigma_x,inv(x)),one))==2,
 'beta_val_minus10': valuation(beta)==-10,
 'conjugate_delta_val_minus8': valuation(delta)==-8,
 'chi_conductor7_witness': fractional_part_3(trace(mul(beta,power(x,6)))/3)!=0,
 'chi_conductor7_vanishing': fractional_part_3(trace(mul(beta,power(x,7)))/3)==0,
 'ratio_conductor5_witness': fractional_part_3(trace(mul(delta,power(x,4)))/3)!=0,
 'ratio_conductor5_vanishing': fractional_part_3(trace(mul(delta,power(x,5)))/3)==0,
}
result={
 'coefficient_domain':'Q[x]/(Phi_9(1+x)) using fractions.Fraction',
 'defining_polynomial_low_to_high':f,
 'valuations':{'v_L(3)':6,'v_L(pi_F)':valuation(piF),'v_L(sigma(pi_L)/pi_L-1)':2,'v_L(beta)':valuation(beta),'v_L(sigma(beta)-beta)':valuation(delta)},
 'beta_coefficients':encode(beta),
 'sigma_beta_minus_beta_coefficients':encode(delta),
 'additive_character_convention':'psi_Q3 standard, kernel Z3; psi_F(t)=psi_Q3(Tr_F/Q3(t)/3); psi_L=psi_F o Tr_L/F',
 'character_witnesses':{
   'chi(exp(pi_L^6)) exponent mod1':str(fractional_part_3(trace(mul(beta,power(x,6)))/3)),
   'ratio(exp(pi_L^4)) exponent mod1':str(fractional_part_3(trace(mul(delta,power(x,4)))/3)),
 },
 'checks':checks,
 'all_checks_pass':all(checks.values()),
 'non_claims':['No calculation of automorphic-induction matrix coefficients or H1 multiplicity.','No Lean proof.','No proof of Claim16.2 or original H5.','Conductor identities use the ordinary local-field reduction stated in ARITHMETIC113.md.']
}
print(json.dumps(result,indent=2))
assert all(checks.values())
