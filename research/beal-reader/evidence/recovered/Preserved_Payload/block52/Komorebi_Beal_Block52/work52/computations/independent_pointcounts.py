#!/usr/bin/env python3
"""Independent, direct enumeration of all admissible pairs, with square tables.

No imports from finite_frobenius.py or predecessor code. Uses the largest
quadratic nonresidue, direct sextic powers rather than Horner/norm characters,
and Newton identities rather than the closed squared-Frobenius formula.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def need(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)

def trim(p: list[int]) -> list[int]:
    while len(p)>1 and p[-1]==0:
        p.pop()
    return p

def gcd_degree(p: list[int], r: list[int], q: int) -> int:
    p,r=trim(p[:]),trim(r[:])
    while r != [0]:
        rem=p[:]
        inv=pow(r[-1],-1,q)
        while len(rem)>=len(r) and rem!=[0]:
            shift=len(rem)-len(r); c=rem[-1]*inv % q
            for i,x in enumerate(r):
                rem[i+shift]=(rem[i+shift]-c*x)%q
            trim(rem)
        p,r=r,rem
    return len(p)-1

def tables(q: int):
    squares1={z*z%q for z in range(q)}
    d=next(z for z in range(q-1,1,-1) if z not in squares1)
    def mul(u,v):
        a,b=u; c,e=v
        return ((a*c+d*b*e)%q,(a*e+b*c)%q)
    roots2={}
    for x in range(q):
        for y in range(q):
            z=mul((x,y),(x,y))
            roots2[z]=roots2.get(z,0)+1
    need(len(roots2)==(q*q+1)//2 and roots2[(0,0)]==1,'Quadratic square table')
    need(sum(roots2.values())==q*q,'Square table multiplicities')
    rows2=[]
    for x in range(q):
        for y in range(q):
            x3=mul(mul((x,y),(x,y)),(x,y)); x6=mul(x3,x3)
            rows2.append((x,y,*x3,*x6))
    roots1={}
    for z in range(q):
        s=z*z%q; roots1[s]=roots1.get(s,0)+1
    rows1=[(x,pow(x,3,q),pow(x,6,q)) for x in range(q)]
    return d,roots1,rows1,roots2,rows2

def count_pair(A,B,q,tabs):
    _,roots1,rows1,roots2,rows2=tabs
    a,b,c=12*A%q,10*B%q,5*B*B%q
    n1=2+sum(roots1.get((x6+b*x3+a*x+c)%q,0) for x,x3,x6 in rows1)
    n2=2+sum(roots2.get(((u+b*r+a*x+c)%q,(v+b*s+a*y)%q),0)
             for x,y,r,s,u,v in rows2)
    t=q+1-n1
    z=t*t-(q*q+1-n2)
    need(z%2==0,'Newton integrality')
    return n1,n2,[q*q,-q*t,z//2,-t,1]

def squared_polynomial(P):
    # Newton sums of roots of a monic degree-four polynomial, to degree eight.
    cs=list(reversed(P)); sums=[4]
    for m in range(1,9):
        if m<=4:
            sm=-sum(cs[j]*sums[m-j] for j in range(1,m))-m*cs[m]
        else:
            sm=-sum(cs[j]*sums[m-j] for j in range(1,5))
        sums.append(sm)
    new=[1]
    for m in range(1,5):
        num=-sum(new[m-i]*sums[2*i] for i in range(1,m+1))
        need(num%m==0,'Squared-root Newton integrality')
        new.append(num//m)
    return list(reversed(new))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    reference=json.loads(args.reference.read_text())
    out=[]
    for record in reference['primes']:
        q=record['q']; tabs=tables(q)
        # This is direct enumeration, not orbit enumeration or reference keys.
        nonzero_sevenths={pow(z,7,q) for z in range(1,q)}
        admissible=[(a,b) for a in range(q) for b in range(q)
                    if (a**3+b**5)%q in nonzero_sevenths]
        expected={tuple(pair):r for r in record['rows'] for pair in r['admissible_pairs']}
        need(set(admissible)==set(expected),'Independent equation-pair coverage')
        matched=[]; polys={}; hist={}
        for a,b in admissible:
            poly=[5*b*b%q,12*a%q,0,10*b%q,0,0,1]
            derivative=[(i*poly[i])%q for i in range(1,7)]
            need(gcd_degree(poly,derivative,q)==0,'Unexpected singular eligible curve')
            n1,n2,P=count_pair(a,b,q,tabs)
            r=expected[a,b]
            need((n1,n2,P)==(r['N1'],r['N2'],r['Pq_ascending']),f'Point count mismatch {q,a,b}')
            # Independently evaluate the defining quadratic radicand of nu in K.
            sqrt5=[z for z in range(q) if z*z%q==5%q]
            if sqrt5:
                Q=q
                symbols=[]
                sq={z*z%q for z in range(q)}
                for z in sqrt5:
                    D=3*(5-z)*pow(2,-1,q)%q
                    symbols.append(1 if D in sq else -1)
                need(len(set(symbols))==1,'Split places give different nu')
                sign=symbols[0]
                Pbase=P
            else:
                Q=q*q
                # Norm(3(5-sqrt5)/2)=45, and quadratic character = norm character.
                sign=1 if pow(45,(q-1)//2,q)==1 else -1
                Pbase=squared_polynomial(P)
            twisted=[c*(sign if i%2 else 1) for i,c in enumerate(Pbase)]
            need(twisted==r['twisted_polynomial'],'Restriction/twist mismatch')
            order=sum(twisted); need(order>0,'Nonpositive group order')
            valuation=0; m=order
            while m%7==0:
                m//=7;valuation+=1
            need(order==r['jacobian_order'] and valuation==r['v7_order'],'Order mismatch')
            # Q=1 mod 7, so the *twisted* residual target is (T-1)^4.
            need(Q%7==1,'Unexpected norm congruence')
            ok=all((x-y)%7==0 for x,y in zip(twisted,[1,-4,6,-4,1]))
            need(ok==r['residual_match'],'Residual predicate mismatch')
            if ok: matched.append([a,b])
            hist[str(valuation)]=hist.get(str(valuation),0)+1
            polys[f'{a},{b}']={'N1':n1,'N2':n2,'Pq':P,'order':order}
        need(matched==record['residual_pairs'],'Residual locus mismatch')
        out.append({'q':q,'field_nonresidue':tabs[0],'direct_pairs':len(admissible),
                    'smoothness_gcd_checks':len(admissible),'valuation_histogram_pairs':hist,
                    'residual_pairs':matched,'direct_results':polys})
    result={'status':'PASS','method':'all admissible pairs; explicit quadratic-field square-root counts; independent Newton and twist calculations',
            'reference_sha256':hashlib.sha256(args.reference.read_bytes()).hexdigest(),
            'total_direct_pairs':sum(r['direct_pairs'] for r in out),'primes':out}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','independent_direct_pairs':result['total_direct_pairs']}))

if __name__=='__main__':
    main()
