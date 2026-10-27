#!/usr/bin/env python3
"""Exact 3-dimensional LLL plus declared bounded projective reconstruction."""
from fractions import Fraction as F
from pathlib import Path
from itertools import product
from math import gcd
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'stationary_separation/ordinary/certified_run/results.json'


def dot(a,b): return sum(x*y for x,y in zip(a,b))

def gram(basis):
    orth=[]; mu=[[F(0) for _ in basis] for _ in basis]; norms=[]
    for i,v in enumerate(basis):
        w=list(map(F,v))
        for j,o in enumerate(orth):
            mu[i][j]=F(dot(v,o),norms[j])
            w=[x-mu[i][j]*y for x,y in zip(w,o)]
        orth.append(w);norms.append(dot(w,w))
    return mu,norms

def determinant(b):
    a,c,d=b
    return a[0]*(c[1]*d[2]-c[2]*d[1])-a[1]*(c[0]*d[2]-c[2]*d[0])+a[2]*(c[0]*d[1]-c[1]*d[0])

def dual_height_lower_bound(basis):
    # For v=B^T z, z=(B^T)^(-1)v; rows of the inverse are cofactors(B)/det(B).
    cofactors=[]
    for i in range(3):
        row=[]
        for j in range(3):
            other_i=[k for k in range(3) if k!=i]
            other_j=[k for k in range(3) if k!=j]
            minor=(basis[other_i[0]][other_j[0]]*basis[other_i[1]][other_j[1]]-
                   basis[other_i[0]][other_j[1]]*basis[other_i[1]][other_j[0]])
            row.append((-1)**(i+j)*minor)
        cofactors.append(row)
    det=determinant(basis)
    # Independently verify cofactors(B) B^T = det(B) I.
    for i in range(3):
        for j in range(3):
            assert dot(cofactors[i],basis[j])==(det if i==j else 0)
    maximum=max(sum(map(abs,row)) for row in cofactors)
    lower=(abs(det)+maximum-1)//maximum
    return lower, {'absolute_determinant':str(abs(det)),
                   'maximum_dual_cofactor_row_sum':str(maximum),
                   'nonzero_vector_height_lower_bound':str(lower)}

def nearest(t): return (t.numerator*2+t.denominator)//(2*t.denominator)

def lll(basis):
    basis=[v[:] for v in basis]
    initial=abs(determinant(basis));k=1;steps=0
    while k<len(basis):
        for j in range(k-1,-1,-1):
            mu,norm=gram(basis)
            q=nearest(mu[k][j])
            if q: basis[k]=[a-q*b for a,b in zip(basis[k],basis[j])]
        mu,norm=gram(basis)
        if norm[k] >= (F(3,4)-mu[k][k-1]**2)*norm[k-1]: k+=1
        else:
            basis[k],basis[k-1]=basis[k-1],basis[k]
            k=max(k-1,1)
        steps+=1
        assert steps<10000
    mu,norm=gram(basis)
    assert abs(determinant(basis))==initial
    assert all(abs(mu[i][j])<=F(1,2) for i in range(3) for j in range(i))
    assert all(norm[i]>=(F(3,4)-mu[i][i-1]**2)*norm[i-1] for i in [1,2])
    return basis,steps

def valuation(n):
    if not n:return None
    return (abs(n)&-abs(n)).bit_length()-1

def summarize(v,p):
    A,B,C=v;d=B*B-A*C;H=max(map(abs,v));M=1<<p
    dg=gcd(abs(d),A*A);num=d//dg;den=A*A//dg
    return {'A':str(A),'B':str(B),'C':str(C),'height':str(H),'height_bits':H.bit_length(),
            'discriminant_over_4':str(d),'discriminant_bits':abs(d).bit_length(),
            'discriminant_valuation':valuation(d),
            'reduced_discriminant_numerator':str(num),
            'reduced_discriminant_denominator':str(den),
            'reduced_numerator_bits':abs(num).bit_length(),
            'strict_reduced_numerator_test':0<abs(num)<M,
            'zero_discriminant':d==0,'strict_discriminant_height_test':0<abs(d)<M,
            'strict_coefficient_height_test':d!=0 and 2*H*H<M}

def main(out):
    data=json.loads(INPUT.read_text());rows=[]
    for row in data['actual_controls']:
        p=row['precision'];M=1<<p;a=int(row['a']);beta=int(row['twice_b'])//2
        basis,steps=lll([[1,beta,a],[0,1<<(p-1),0],[0,0,M]])
        lower,dual=dual_height_lower_bound(basis)
        found=set()
        for coeff in product(range(-8,9),repeat=3):
            v=[sum(coeff[i]*basis[i][j] for i in range(3)) for j in range(3)]
            A,B,C=v
            if A%2==0:continue
            common=gcd(gcd(abs(A),abs(B)),abs(C));assert common%2==1
            v=[x//common for x in v]
            if v[0]<0:v=[-x for x in v]
            A,B,C=v
            assert A%2==1 and gcd(gcd(A,abs(B)),abs(C))==1
            assert (2*B-A*int(row['twice_b']))%M==0 and (C-A*a)%M==0
            d=B*B-A*C
            assert (d-A*A*int(row['discriminant_over_4']))%M==0
            found.add(tuple(v))
        def ht(v):return max(map(abs,v))
        nonzero=[v for v in found if v[1]*v[1]-v[0]*v[2]]
        zero=[v for v in found if not v[1]*v[1]-v[0]*v[2]]
        assert nonzero
        shortest=min(found,key=lambda v:(ht(v),v))
        shortest_nz=min(nonzero,key=lambda v:(ht(v),v))
        best_delta=min(nonzero,key=lambda v:(abs(v[1]*v[1]-v[0]*v[2]),ht(v),v))
        def reduced_numerator(v):
            d=v[1]*v[1]-v[0]*v[2]
            return abs(d)//gcd(abs(d),v[0]*v[0])
        best_reduced=min(nonzero,key=lambda v:(reduced_numerator(v),ht(v),v))
        # Any strict discriminator must recover the inherited actual valuation.
        for v in nonzero:
            d=v[1]*v[1]-v[0]*v[2]
            if reduced_numerator(v)<M:
                assert valuation(d)==row['actual_phi_valuation_capped_at_precision']<p
        rows.append({'T':row['T'],'precision':p,'basis':basis,'lll_steps':steps,
                     'distinct_primitive_odd_denominator_models':len(found),
                     'dual_certificate':dual,
                     'strict_coefficient_height_globally_impossible':2*lower*lower>=M,
                     'shortest_model':summarize(shortest,p),
                     'shortest_nonzero_discriminant_model':summarize(shortest_nz,p),
                     'smallest_nonzero_discriminant_model':summarize(best_delta,p),
                     'smallest_reduced_discriminant_numerator_model':summarize(best_reduced,p),
                     'strict_reduced_numerator_models':sum(reduced_numerator(v)<M for v in nonzero),
                     'square_model_count':len(zero),
                     'smallest_square_model':summarize(min(zero,key=lambda v:(ht(v),v)),p) if zero else None,
                     'strict_discriminant_models':sum(0<abs(v[1]*v[1]-v[0]*v[2])<M for v in nonzero),
                     'strict_coefficient_models':sum(2*ht(v)**2<M for v in nonzero)})
    result={'status':'passed','input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            'basis_convention':'Coordinates(A,B,C) give AZ^2+2BZ+C; lattice determinant2^(2P-1)',
            'enumeration':'Every integer combination of the exact LLL basis with each coefficient in[-8,8], retaining oddA and dividing the odd common gcd',
            'actual_controls':rows,
            'nonclaims':['Enumeration is not a proof of global shortest height or impossibility',
                         'No new T digits or new candidates',
                         'No projective scaling invariant forces a uniform height exponent below1/2']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{'T':r['T'],'P':r['precision'],
                      'shortest_height_bits':r['shortest_model']['height_bits'],
                      'dual_height_lower_bound':r['dual_certificate']['nonzero_vector_height_lower_bound'],
                      'strict_coefficient_height_globally_impossible':r['strict_coefficient_height_globally_impossible'],
                      'shortest_discriminant_bits':r['shortest_model']['discriminant_bits'],
                      'shortest_is_square':r['shortest_model']['zero_discriminant'],
                      'minimum_discriminant_bits':r['smallest_nonzero_discriminant_model']['discriminant_bits'],
                      'strict_discriminant_models':r['strict_discriminant_models'],
                      'minimum_reduced_numerator_bits':r['smallest_reduced_discriminant_numerator_model']['reduced_numerator_bits'],
                      'strict_reduced_numerator_models':r['strict_reduced_numerator_models'],
                      'strict_coefficient_models':r['strict_coefficient_models'],
                      'square_models':r['square_model_count']} for r in rows],indent=2))

if __name__=='__main__':main(sys.argv[1])
