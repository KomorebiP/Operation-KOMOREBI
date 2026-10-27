#!/usr/bin/env python3
"""Exact finite corroboration; this does not replace the Lean universal proofs."""
from __future__ import annotations
from pathlib import Path
from itertools import product
from math import gcd
import hashlib,json,platform,time

MOD=4
ONE=(1,0,0,1)
ZERO=(0,0,0,0)
def add(a,b): return tuple((x+y)%MOD for x,y in zip(a,b))
def neg(a): return tuple((-x)%MOD for x in a)
def sub(a,b): return add(a,neg(b))
def mul(a,b):
    return ((a[0]*b[0]+a[1]*b[2])%MOD,(a[0]*b[1]+a[1]*b[3])%MOD,
            (a[2]*b[0]+a[3]*b[2])%MOD,(a[2]*b[1]+a[3]*b[3])%MOD)
def inverse(a):
    d=(a[0]*a[3]-a[1]*a[2])%MOD
    if gcd(d,MOD)!=1: raise ValueError('matrix is not invertible')
    t=pow(d,-1,MOD)
    return tuple((t*x)%MOD for x in (a[3],-a[1],-a[2],a[0]))
def run():
    started=time.monotonic()
    matrices=list(product(range(MOD),repeat=4))
    units=[a for a in matrices if gcd(a[0]*a[3]-a[1]*a[2],MOD)==1]
    kernel=list(product((0,2),repeat=4))
    assert len(matrices)==256 and len(units)==96 and len(kernel)==16
    assert all(mul(x,y)==ZERO for x in kernel for y in kernel)
    cases=0
    for F in units:
        inv=inverse(F)
        fp=[ONE];ip=[ONE]
        for _ in range(4):fp.append(mul(fp[-1],F));ip.append(mul(ip[-1],inv))
        for x in kernel:
            norm=ZERO
            perturbed=ONE
            for d in range(5):
                if d:
                    j=d-1
                    norm=add(norm,mul(mul(fp[j],x),ip[j]))
                    perturbed=mul(perturbed,mul(add(ONE,x),F))
                assert perturbed==mul(add(ONE,norm),fp[d])
                for z in kernel:
                    left=mul(mul(add(ONE,z),perturbed),sub(ONE,z))
                    adj=mul(mul(fp[d],z),ip[d])
                    right=mul(add(ONE,sub(add(norm,z),adj)),fp[d])
                    assert left==right,(F,x,z,d,left,right)
                    cases+=1
    assert cases==96*16*5*16
    upper=[a for a in range(27) if a%9==4]
    cubes=[pow(a,3,27) for a in upper]
    assert upper==[4,13,22] and cubes==[10,10,10]
    assert pow(4,9,27)==1 and pow(4,3,27)!=1
    scalar_kernel=[0,9,18]
    # Scalar conjugation is trivial. N_3 = 3 on this square-zero kernel.
    norm3=[(3*x)%27 for x in scalar_kernel]
    mismatch=((1-pow(4,3,27))*pow(pow(4,3,27),-1,27))%27
    assert norm3==[0,0,0] and mismatch==18
    return {
      'status':'PASS','arithmetic':'exact modular integers, no floating point',
      'matrix_population':{'ambient_matrices':256,'invertible_matrices':96,
          'kernel_matrices':16,'degrees':[0,1,2,3,4],
          'conjugated_power_cases':cases,'excluded':'noninvertible matrices only'},
      'scalar_control':{'coefficient_map':'Z/27 -> Z/9','residual_generator':4,
          'all_generator_lifts':upper,'cubes':cubes,'lifted_order':9,
          'kernel':scalar_kernel,'norm3_values':norm3,
          'prescribed_degree3_value':1,'mismatch':mismatch},
      'nonclaims':['finite test is not the universal theorem',
          'no arithmetic Galois-group construction or Strong Artin conclusion'],
      'python':platform.python_version(),'seconds':time.monotonic()-started,
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
if __name__=='__main__':
    result=run()
    path=Path(__file__).with_name('EXACT_CHECKS.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
