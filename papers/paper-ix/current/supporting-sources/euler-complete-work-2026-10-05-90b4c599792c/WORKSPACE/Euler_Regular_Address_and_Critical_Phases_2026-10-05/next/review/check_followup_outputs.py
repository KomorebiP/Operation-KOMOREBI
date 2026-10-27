#!/usr/bin/env python3
"""Independent finite review of the terminal-129 followup coefficient record."""
from pathlib import Path
import json
import sys
from fractions import Fraction
from math import prod, factorial
from check_stored_outputs import affine, cover, ev, reduction

ROOT=Path(__file__).resolve().parents[2]


def check_prefix17():
    data=json.loads((ROOT/'next/irregular_address/PREFIX17_CERTIFICATE.json').read_text())
    B=[Fraction(1),Fraction(-1,2),Fraction(1,6),0,Fraction(-1,30),0,Fraction(1,42)]
    def mod(x):
        x=Fraction(x)
        assert x.denominator%2
        return x.numerator*pow(x.denominator,-1,64)%64
    residues=[]
    for n in (-34,-32,-30):
        residues.append(mod(sum((Fraction(prod(n-i for i in range(h)),factorial(h))*(1<<h)*B[h] for h in range(7)),Fraction())))
    assert residues==data['bernoulli_residues']==[13,1,21]
    scalars=[]
    for q in range(3):
        coeff=Fraction(1<<5*q)*Fraction(-35+2*q,-35)*Fraction(residues[q],residues[0])/prod(-34+h for h in range(1,2*q+1))
        scalars.append(mod(coeff))
    assert scalars==data['prefix_coefficients_q0_q1_q2']==[1,55,16]
    def mul(a,b):
        p=[0]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b):p[i+j]=(p[i+j]+x*y)%64
        return p
    # log(9)/8 = 1 - 4 + 64/3 - 128 modulo64 = 61.
    ell8=mod(Fraction(1)-4+Fraction(64,3)-128)
    assert ell8==61
    # Only h=0,1,2 in the integral source expansion can contribute mod64.
    numerator=[0]*3
    for h in range(3):
        coefficient=mod(Fraction((1<<3*h)*ell8**(h+1),factorial(h+1)))
        power=[1]
        for _ in range(h):power=mul(power,[1,1])
        for i,v in enumerate(power):numerator[i]=(numerator[i]+coefficient*v)%64
    source=mul(numerator,[pow(-2,h,64) for h in range(6)])
    assert all(x==0 for x in source[6:])
    source=source[:6]
    assert source==data['source_coefficients_mod64']
    p=[1];prefix=[0]*12
    for q in range(3):
        if q:
            i=q-1;p=mul(mul(p,[-i,1]),[-2*i-1,2])
        term=mul(p,affine(source,-q,0,6))
        for i,v in enumerate(term):prefix[i]=(prefix[i]+scalars[q]*v)%64
    while len(prefix)>1 and not prefix[-1]:prefix.pop()
    assert prefix==data['prefix_coefficients_mod64']==[1,13,40,8,48,32]
    assert [x for x in range(64) if ev(prefix,x,64)==0]==[43]
    assert ev(prefix,11,64)==32
    return {'prefix_modulus':64,'source_coefficients':source,'prefix_coefficients':prefix,
            'root_mod64':43,'valuation_sigma_minus_11':5}


def run():
    data=json.loads((ROOT/'next/terminal129/phase_129.json').read_text())
    A,C,W=data['A'],data['C'],data['W']
    for p,q in ((data['low'],A),(data['high'],C)):
        shifted=affine(p,104,7,224)
        assert all(x%(1<<130)==0 for x in shifted)
        expected=[x>>130 for x in shifted]
        def trim(p):
            p=list(p)
            while len(p)>1 and not p[-1]:p.pop()
            return p
        assert trim(expected)==trim(q)
    m=1<<94
    wc=[0]*max(1,len(A)+len(C)-2)
    for i,a in enumerate(A):
        for j,c in enumerate(C):
            if i+j:wc[i+j-1]=(wc[i+j-1]+(j-i)*a*c)%m
    assert trim(wc)==W
    cover(data['atlas']);candidates=[]
    for leaf in data['atlas']:
        content=leaf.get('value',leaf.get('content'))
        assert reduction(W,leaf['s'],leaf['k'],content)==leaf['reduction']
        if leaf['kind']=='constant':
            assert leaf['reduction']==[1]
            continue
        assert (leaf['s'],leaf['k'],content) in ((2,3,6),(6,3,6))
        f=[x>>6 for x in affine(W,leaf['s'],3,94)]
        z=0
        for k in range(88):
            modulus=1<<(k+1)
            options=[x for x in (z,z+(1<<k)) if ev(f,x,modulus)==0]
            assert len(options)==1
            z=options[0]
        y=leaf['s']+8*z
        assert y==leaf['root_mod'] and leaf['root_bits']==91
        assert affine(A,leaf['s'],3,2)==[2]
        assert affine(C,leaf['s'],3,2)==[2]
        modulus=1<<91
        a=ev(A,y,modulus)//2;c=ev(C,y,modulus)//2
        B=(-c*pow(a,-1,modulus//2))%(modulus//2)
        assert B>(1<<89)
        candidates.append({'B':B,'B_bits':90,'Y':y,'Y_bits':91})
    assert len(candidates)==2
    assert [(x['B'],x['Y']) for x in candidates]==[(x['B'],x['Y']) for x in data['candidates']]
    tables=[]
    for j,L0 in ((129,392),(161,487)):
        costs=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        theta=3*j+1+(j-1).bit_count()
        assert min(costs)==theta-L0
        assert [q for q,c in enumerate(costs) if c==min(costs)]==[1]
        tables.append({'terminal':j,'boundary_L':L0,'lower_min':min(costs),'boundary_last_minimizer':j})
    return {'status':'PASS','scope':'Independent review of stored coefficient records; no original Euler coefficient reconstruction.',
            'terminal129_local_content':130,'W_bits':94,'W_leaves':4,
            'critical_Y_bits':91,'nonunit_ratio_loss':1,'parameter_B_bits':90,
            'candidates':candidates,'boundary_carry_tables':tables,
            'irregular_prefix17':check_prefix17()}


if __name__=='__main__':
    result=run()
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('FOLLOWUP_OUTPUT_CHECKS.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
