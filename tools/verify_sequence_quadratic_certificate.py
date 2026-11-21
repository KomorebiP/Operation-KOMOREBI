"""Separate standard-library audit of the saved quadratic certificate.

Uses a 256-coordinate ordinary tensor, instead of the discovery code's
136-coordinate symmetric tensor. Initial block values use monomial matrices.
"""
import argparse,json,time
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import sequence_parity_hankel as p
from test_sequence_differential_hankel import direct_hankel


def trim(a):
    a=list(a)
    while len(a)>1 and not a[-1]:a.pop()
    return a


def times(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return trim(out)


def power(a,n):
    out=[1]
    for _ in range(n):out=times(out,a)
    return out


def exact_int(value):
    value=F(value)
    assert value.denominator==1
    return value.numerator


def tensor_step(v,q):
    d=len(q)-1
    first=[v[i+1][:] for i in range(d-1)]+[
        [-sum(q[a]*v[a][j] for a in range(d)) for j in range(d)]]
    return [row[1:]+[-sum(q[b]*row[b] for b in range(d))] for row in first]


def tensor_residual(v,q,R):
    d=len(q)-1;result=[[0]*d for _ in range(d)]
    for coefficient in R:
        for i in range(d):
            for j in range(d):result[i][j]+=coefficient*v[i][j]
        v=tensor_step(v,q)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();started=time.perf_counter()
    data=json.loads(Path(args.input).read_text());a,c=data['weights'],data['operator']
    assert a==[1,1,1] and c==[1]
    certificates=data['block_certificates']
    for parity,certificate in enumerate(certificates):
        assert certificate['parity']==parity and p.verify(a,c,certificate)
        for field,value in [('states',69),('start',8),('order',15),('coefficients',[0])]:
            forged={**certificate,field:value};assert not p.verify(a,c,forged)
        forged={**certificate,'coefficients':list(certificate['coefficients'])}
        forged['coefficients'][0]+=1;assert not p.verify(a,c,forged)
    q=list(map(exact_int,certificates[0]['coefficients']))
    assert q==list(map(exact_int,certificates[1]['coefficients']))
    K=certificates[0]['start'];d=len(q)-1
    blocks=[[exact_int(p.direct_block(a,c,parity,n)) for n in range(K+d+1)] for parity in (0,1)]
    R=list(map(exact_int,data['product_annihilator']))
    tensor_counts=[]
    for shift in (0,1):
        X=blocks[0][K+shift:K+d+shift];Y=blocks[1][K:K+d]
        v=[[x*y for y in Y] for x in X]
        assert not any(value for row in tensor_residual(v,q,R) for value in row)
        corrupt=R[:];corrupt[0]+=1
        assert any(value for row in tensor_residual(v,q,corrupt) for value in row)
        tensor_counts.append(d*d)
    denominator=[0]*(2*len(R)-1)
    for i,value in enumerate(reversed(R)):denominator[2*i]=value
    assert denominator[0]==1
    last=2*K+len(denominator)-2
    for parity in (0,1):
        while len(blocks[parity])<=(last+1)//2:
            n=len(blocks[parity])-d
            blocks[parity].append(-sum(q[j]*blocks[parity][n+j] for j in range(d)))
    W=[1]+[blocks[0][(n+1)//2]*blocks[1][n//2]//4 for n in range(1,last+1)]
    assert all(blocks[0][(n+1)//2]*blocks[1][n//2]%4==0 for n in range(1,last+1))
    full_num=trim([sum(denominator[j]*W[n-j] for j in range(min(n,len(denominator)-1)+1)) for n in range(len(W))])
    N=list(map(exact_int,data['reduced_numerator']));D=list(map(exact_int,data['reduced_denominator']))
    assert times(N,denominator)==times(full_num,D)
    factored_base=times(times([1,-2],[1,-24,-88,-96,16]),[1,-4,56,-16,16])
    assert power(factored_base,7)==D
    assert len(N)==len(D)==64
    field=data['modular_coprimality'];prime=field['prime']
    assert prime==1000003 and all(prime%k for k in range(2,isqrt(prime)+1))
    assert N[-1]%prime and D[-1]%prime
    identity=times(field['u'],N);other=times(field['v'],D)
    identity += [0]*max(0,len(other)-len(identity))
    for i,value in enumerate(other):identity[i]+=value
    assert trim([value%prime for value in identity])==[1]
    for n in range(21):assert W[n]==direct_hankel(a,c,n)
    result={'outcome':'Separate exact tensor, OGF, normalization and minimality audit passed',
        'review_provenance':'self-review, not independent review','full_tensor_coordinates':tensor_counts,
        'malformed_or_corrupted_block_certificates_rejected':10,'corrupted_tensor_relations_rejected':2,
        'direct_monomial_block_determinants':2*(K+d+1),'direct_original_determinants':21,
        'rational_function_cross_multiplication':True,'denominator_factorization_reconstructed':True,
        'modular_bezout_identity_verified':True,'minimal_eventual_order':63,'recurrence_start':1,
        'elapsed_seconds':time.perf_counter()-started}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))


if __name__=='__main__':main()
