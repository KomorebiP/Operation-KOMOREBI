#!/usr/bin/env python3
"""Run: python3 abc_work/polyphase_taps/routes/multichannel/verify.py"""
import hashlib
import itertools
import json
import platform
import time
from fractions import Fraction
from pathlib import Path

OUT=Path(__file__).resolve().parent
ABC=OUT.parents[2]
BASE=ABC/'roots_unity/LATEST.md'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def v(x,p):
    if x==0:
        return float('inf')
    x=Fraction(x)
    def vi(n):
        n=abs(n)
        e=0
        while n%p==0:
            n//=p
            e+=1
        return e
    return vi(x.numerator)-vi(x.denominator)

def content(x,p):
    return min(v(a,p) for a in x)

def mv(M,x):
    return [sum(a*b for a,b in zip(row,x)) for row in M]

def det(M):
    return M[0][0]*M[1][1]-M[0][1]*M[1][0]

def inverse(M):
    D=det(M)
    return [[Fraction(M[1][1],D),Fraction(-M[0][1],D)],
            [Fraction(-M[1][0],D),Fraction(M[0][0],D)]]

def main():
    started=time.monotonic()
    before=sha(BASE)
    p,n=17,8
    root=3
    examples=[]
    exhaustive_count=0
    for e in range(1,9):
        modulus=p**e
        assert (root**n+1)%modulus==0
        digit=(-(root**n+1)//modulus*pow(n*pow(root,n-1,p),-1,p))%p
        k=2 if digit==1 else 1
        A=root+k*modulus
        X=A**n
        c=X+1
        assert v(c,p)==e
        x=[X,1]
        banks={
            'expose':[[1,1],[0,1]],
            'hide':[[1,0],[-1,1]],
            'Haar':[[1,1],[1,-1]],
            'determinant_contact':[[1,X],[-1,1]],
            'adaptive_normalization':[[Fraction(1,modulus),Fraction(1,modulus)],[0,1]],
        }
        expose=mv(banks['expose'],x)
        hide=mv(banks['hide'],x)
        haar=mv(banks['Haar'],x)
        concentrated=mv(banks['determinant_contact'],[1,1])
        normalized=mv(banks['adaptive_normalization'],x)
        assert [v(z,p) for z in expose]==[e,0]
        assert [v(z,p) for z in hide]==[0,0]
        assert 2*hide[0]+hide[1]==c
        assert [v(z,p) for z in haar]==[e,0]
        assert concentrated==[c,0]
        assert content(concentrated,p)==e
        assert v(det(banks['determinant_contact']),p)==e
        assert [v(z,p) for z in normalized]==[0,0]
        assert p**e*normalized[0]==c
        assert v(det(banks['adaptive_normalization']),p)==-e
        synthesis=inverse(banks['adaptive_normalization'])
        assert synthesis==[[modulus,-1],[0,1]]
        assert max(abs(a) for row in synthesis for a in row)>=modulus
        for name,M in banks.items():
            source=[1,1] if name=='determinant_contact' else x
            assert mv(inverse(M),mv(M,source))==source
        # Exhaustive finite check of the integral determinant/content lemma.
        for entries in itertools.product(range(-3,4),repeat=4):
            M=[list(entries[:2]),list(entries[2:])]
            D=det(M)
            if D==0:
                continue
            for source in [x,[p**e,1],[p,p**e]]:
                nu=content(source,p)
                ny=content(mv(M,source),p)
                assert nu<=ny<=nu+v(D,p)
                exhaustive_count+=1
        # A rational real-energy-preserving bank has explicit denominator cost.
        rotation=[[Fraction(3,5),Fraction(4,5)],[-Fraction(4,5),Fraction(3,5)]]
        assert inverse(rotation)==[[Fraction(3,5),-Fraction(4,5)],[Fraction(4,5),Fraction(3,5)]]
        for source in [[1,1],[5,1],[5**e,5]]:
            nu=content(source,5)
            ny=content(mv(rotation,source),5)
            assert nu-1<=ny<=nu+1
        examples.append({'p':p,'n':n,'e':e,'A':A,'c_bits':c.bit_length(),
                         'input_depths':[0,0],'exposed_depths':[e,0],
                         'hidden_depths':[0,0],'determinant_depth':e,
                         'normalization_denominator':modulus,
                         'synthesis_max_coefficient':modulus})
        root+=digit*modulus
    after=sha(BASE)
    assert before==after
    result={'status':'completed','assertion_tested':'Exact analysis/synthesis and determinant-content bounds on eight primitive deep contacts, plus all nonsingular 2x2 integral matrices with coefficients -3 through 3 on the three specified vectors at each depth.',
            'nonclaims':['No ABC proof','No full factorization of outputs','No impossibility theorem for adaptive taps','No Lean compilation'],
            'command':'python3 abc_work/polyphase_taps/routes/multichannel/verify.py',
            'python':platform.python_version(),'elapsed_seconds':time.monotonic()-started,
            'input_sha256_before':before,'input_sha256_after':after,
            'code_sha256':sha(Path(__file__)),
            'matrix_vector_checks':exhaustive_count,'examples':examples}
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(examples),'contacts;',exhaustive_count,'matrix-vector content checks')

if __name__=='__main__':
    main()
