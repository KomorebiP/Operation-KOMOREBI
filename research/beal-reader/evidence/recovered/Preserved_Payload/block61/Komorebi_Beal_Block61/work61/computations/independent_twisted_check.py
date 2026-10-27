#!/usr/bin/env python3
"""Independent chi^-1 certificate audit: cyclic group-ring norms, direct power symbols,
permuted residue primes, and determinant expansion. Does not import primary code."""
from __future__ import annotations
import argparse,json
from itertools import product,permutations
from pathlib import Path

S=(197,883,1373,1667);T=(29,71,491)
P={197:[1,-1,-1,-1,1,-1],883:[0,0,1,-2,1,2],1373:[0,2,-2,-1,-2,-2],
1667:[1,-2,1,2,1,2],29:[0,0,0,1,-1,-1],71:[0,1,-1,-1,1,-1],491:[0,1,-2,2,0,2]}

def check(ok,message):
    if not ok:raise AssertionError(message)

def canon(a):
    a=list(a)+[0]*(7-len(a));v=a[6];return [x-v for x in a]

def ringmul(a,b):
    c=[0]*7
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[(i+j)%7]+=x*y
    return canon(c)

def automorphism(a,k):
    c=[0]*7
    for j,x in enumerate(a):c[(j*k)%7]+=x
    return canon(c)

def peval(a,x,q):return sum(c*pow(x,j,q) for j,c in enumerate(a))%q

def determinant(a):
    n=len(a);out=0
    for perm in permutations(range(n)):
        t=(-1)**sum(perm[i]>perm[j] for i in range(n) for j in range(i+1,n))
        for i,j in enumerate(perm):t*=a[i][j]
        out+=t
    return out

def symbol_log(x,q,g=2):
    check(x%q!=0,'Nonunit passed to symbol')
    root=pow(g,(q-1)//7,q);check(root!=1 and pow(root,7,q)==1,'Bad symbol basis')
    table={pow(root,j,q):j for j in range(7)}
    return table[pow(x,(q-1)//7,q)]

def extmul(a,b,q):return ((a[0]*b[0]+5*a[1]*b[1])%q,(a[0]*b[1]+a[1]*b[0])%q)

def extpow(a,n,q):
    b=(1,0)
    for bit in bin(n)[2:]:
        b=extmul(b,b,q)
        if bit=='1':b=extmul(b,a,q)
    return b

def extlog(a,q):
    e=(q*q-1)//7;basis=extpow((2,0),e,q)
    tab={extpow(basis,j,q):j for j in range(7)}
    return tab[extpow(a,e,q)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primary',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    raw=json.loads(args.primary.read_text());norms={};roots={}
    for q,co in P.items():
        # Deliberately use theta=zeta^-1 throughout.
        inv=automorphism(canon(co),6)
        val=[1,0,0,0,0,0,0]
        for a in range(1,7):val=ringmul(val,automorphism(inv,a))
        check(val==[q,0,0,0,0,0,0],f'Norm-product failed at {q}')
        check(raw['prime_generators'][str(q)]=={'coefficients':co,'norm':q},'Primary norm or polynomial differs')
        norms[str(q)]=val
        if q in S:
            rr=[a for a in range(2,q) if pow(a,7,q)==1 and peval(inv,a,q)==0]
            check(len(rr)==1,'Nonunique theta residue');roots[q]=rr[0]
            check(roots[q]*raw['support_fields'][str(q)]['zeta_residue']%q==1,'Wrong inverse-basis prime')
    # Solve the equivariance equations, rather than insert six ordinary-character weights.
    weights={1:1}
    for a in range(1,7):weights[pow(a,-1,7)]=pow(a,-1,7)
    transports=0
    for q in S:
        for a in range(1,7):
            for b in range(1,7):
                target=next(c for c in range(1,7) if pow(pow(roots[q],c,q),a,q)==pow(roots[q],b,q))
                check(weights[target]==pow(a,-1,7)*weights[b]%7,'chi^-1 covariance failed');transports+=1
    # Ordinary constant weights demonstrably violate the required nontrivial eigenspace.
    check(any(1!=pow(a,-1,7) for a in range(1,7)),'Ordinary-weight negative control broken')
    rows=[];symbols=0
    for ell in T:
        inv=automorphism(canon(P[ell]),6);row=[]
        for q in S:
            vals=[peval(inv,pow(roots[q],b,q),q) for b in range(1,7)]
            logs=[symbol_log(x,q) for x in vals];symbols+=6
            check(raw['residue_evaluations'][str(ell)][str(q)]=={'values':vals,'logs_mod7':logs},'Changed residue data')
            # Compute with inverse primitive generator, then return to the canonical g=2 coordinate.
            other=[symbol_log(x,q,pow(2,-1,q)) for x in vals]
            check(all((a+b)%7==0 for a,b in zip(logs,other)),'Primitive-generator normalization failed')
            row.append(-sum(weights[b]*logs[b-1] for b in range(1,7))%7)
        rows.append(row)
    check(rows==raw['matrix'],'Primary Frobenius matrix differs')
    minors=[determinant([[r[j] for j in range(4) if j!=k] for r in rows]) for k in range(4)]
    check(minors==raw['signed_column_deletion_minors'] and minors[-1]%7==1,'Minor mismatch')
    kernel=[]
    for v in product(range(7),repeat=4):
        if all(sum(x*y for x,y in zip(row,v))%7==0 for row in rows):kernel.append(list(v))
    check(kernel==raw['F7_kernel'] and len(kernel)==7,'Kernel enumeration differs')
    natural=[]
    for q in S:
        half=pow(2,-1,q);phi=(half,half)
        check(extpow(phi,q+1,q)==(q-1,0),'Inert phi norm is not -1')
        natural.append([extlog(phi,q),extlog((3,0),q),extlog((0,1),q)])
    check(natural==raw['natural_kummer_rows'],'Natural Kummer rows differ')
    check(determinant([[natural[0][1],natural[0][2]],[natural[3][1],natural[3][2]]])%7==6,
          'Compatible-coefficient contradiction failed')
    # Recover the full F49 kernel with Cramer coefficients for the three pivot variables.
    pivot=[[r[j] for j in range(3)] for r in rows];den=determinant(pivot)%7
    coeff=[]
    for c in range(3):
        replace=[list(r) for r in pivot]
        for i in range(3):replace[i][c]=-rows[i][3]
        coeff.append(determinant(replace)*pow(den,-1,7)%7)
    extkernel=[[(c*a%7,c*b%7) for c in coeff]+[(a,b)] for a,b in product(range(7),repeat=2)]
    nonzero=[v for v in extkernel if any(x!=(0,0) for x in v)]
    check(len(nonzero)==48,'Wrong extension kernel size')
    total=0;surv=0
    for u in product(range(7),repeat=2):
        for r in product(range(7),repeat=2):
            if r==(0,0):continue
            z=[((aa*u[0]+bb*r[0]+cc)%7==0 and (aa*u[1]+bb*r[1])%7==0) for aa,bb,cc in natural]
            for v in nonzero:
                total+=1;surv+=int(all(vv==(0,0) or zz for vv,zz in zip(v,z)))
    check(total==112896 and surv==0,'A compatible pair remains')
    check(raw['common_coefficient_test']=={'normalized_F49_directions':2352,'nonzero_F49_ray_vectors':48,
        'joint_pairs':112896,'surviving_pairs':0},'Primary count claims changed')
    splitfields=0
    for q in T:
        ws=[w for w in range(q) if w*w%q==5]
        rr=sorted((1+w)*pow(2,-1,q)%q for w in ws)
        values=[pow(r,(q-1)//7,q) for r in rr]
        check(raw['bad_prime_phi_tests'][str(q)]=={'roots':rr,'seventh_symbols':values},'Bad-prime phi data changed')
        check(len(rr)==2 and all(x!=1 for x in values),'No local period obstruction');splitfields+=2
    out={'schema':'beal.block61.independent.v1','status':'PASS_INDEPENDENT_FINITE_CHECK',
         'norm_products':norms,'matrix':rows,'minor_values':minors,'F7_kernel':kernel,
         'natural_kummer_rows':natural,'counts':{'prime_generator_norms':7,'direct_ray_symbols':symbols,
         'Delta_transport':transports,'natural_extension_field_symbols':12,'split_phi_tests':splitfields,
         'F7_vectors_enumerated':2401,'nonzero_F49_vectors':48,'joint_coefficient_pairs':total},
         'imports_primary_arithmetic':False,'independent_review':False,
         'surviving_joint_pairs':surv}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print(out['counts'])
if __name__=='__main__':main()
