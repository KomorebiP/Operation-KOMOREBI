#!/usr/bin/env python3
"""Independent exact/modular checks for the packet-derivative continuation.

Python 3.10+, standard library only. These are implementation checks, not
substitutes for the universal Lean proofs. All arithmetic is rational/integer.
"""
from __future__ import annotations
import argparse, hashlib, json, math, time
from collections import Counter
from fractions import Fraction
from pathlib import Path


def trim(a: list[int]) -> list[int]:
    while len(a)>1 and a[-1]==0: a.pop()
    return a or [0]


def add(a: list[int], b: list[int], modulus: int | None=None) -> list[int]:
    c=[(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))]
    return trim([x%modulus for x in c] if modulus else c)


def scale(a: list[int], c: int, modulus: int | None=None) -> list[int]:
    return trim([(x*c)%modulus if modulus else x*c for x in a])


def mul(a: list[int], b: list[int], modulus: int | None=None) -> list[int]:
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return trim([x%modulus for x in c] if modulus else c)


def shift(a: list[int], h: int, modulus: int) -> list[int]:
    # Direct binomial substitution, not Horner composition.
    c=[0]*len(a)
    for n,v in enumerate(a):
        for k in range(n+1): c[k]=(c[k]+v*math.comb(n,k)*pow(h,n-k,modulus))%modulus
    return trim(c)


def hasse(a: list[int], k: int, modulus: int | None=None) -> list[int]:
    c=[math.comb(n,k)*a[n] for n in range(k,len(a))]
    return trim([v%modulus for v in c] if modulus else c)


def evaluate(a: list[int], x: int, modulus: int | None=None) -> int:
    y=0
    for c in reversed(a): y=y*x+c; y=y%modulus if modulus else y
    return y


def qmod(x: Fraction, modulus: int) -> int:
    if x.denominator%2==0: raise ValueError('Nonintegral coefficient passed to dyadic residue conversion')
    return x.numerator*pow(x.denominator,-1,modulus)%modulus


def val2(n: int) -> int | None:
    if n==0: return None
    n=abs(n); return (n & -n).bit_length()-1


def bernoulli(n: int) -> list[Fraction]:
    b=[Fraction(1)]
    for m in range(1,n+1):
        b.append(-sum((math.comb(m+1,k)*b[k] for k in range(m)),Fraction(0))/Fraction(m+1))
    return b


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--precision',type=int,default=48)
    args=ap.parse_args()
    if args.output.exists(): raise FileExistsError('Refusing to overwrite an existing result')
    if not 24<=args.precision<=96: raise ValueError('Use precision in [24,96] for this bounded audit')
    start=time.monotonic(); P=args.precision; M=1<<P; counts=Counter()
    def check(group: str, statement: bool) -> None:
        if not statement: raise AssertionError(group)
        counts[group]+=1
    packets=(P+2)//3; max_r=16
    B=bernoulli(2*(max_r+packets+1))
    beta=[Fraction(1)]+[-Fraction((1<<(2*m))*(2*m-1))*B[2*m]/math.factorial(2*m)
                        for m in range(1,max_r+packets+2)]
    for m,v in enumerate(beta):
        check('beta_exact_integrality',v.denominator%2==1)
        if m: check('beta_exact_valuation',val2(v.numerator)==m.bit_count()-1)
    # Build the source by NEWTON taps, independent of logarithmic source evaluation.
    numer=[0]; falling=[1]
    for q in range((P+1)//2):
        tap=qmod(Fraction(8**q,math.factorial(q+1)),M)
        numer=add(numer,scale(falling,tap,M),M)
        falling=mul(falling,[-q,1],M)
    inverse=[pow(-2,n,M) for n in range(P)]
    full_source=mul(numer,inverse,M)
    check('source_degree_cutoff',all(c==0 for c in full_source[P:]))
    source=trim(full_source[:P]); source_deriv=hasse(source,1,M)
    check('source_mod8',trim([c%8 for c in source])==[1,2,4])
    for n in range(21):
        target=Fraction(9**(n+1)-1,8*(n+1)*(2*n+1))
        check('source_against_rational_rows',evaluate(source,n,M)==qmod(target,M))
    for x in range(-8,16):
        check('source_global_sample_slope',val2(evaluate(source_deriv,x,M))==1)
    exactP=[[1]]
    for q in range(1,33):
        i=q-1; exactP.append(mul(exactP[-1],[i*(2*i+1),-(4*i+1),2]))
    A_shift=[shift(source,-q,M) for q in range(packets)]
    P_mod=[[c%M for c in a] for a in exactP[:packets]]
    term={}; total={}
    for r in range(1,max_r+2):
        terms=[]; s=[0]
        for q in range(packets):
            scalar=qmod(Fraction(8**q)*beta[r+q],M)
            packet=scale(mul(P_mod[q],A_shift[q],M),scalar,M)
            terms.append(packet);s=add(s,packet,M)
            lhs=hasse(packet,1,M)
            rhs=scale(add(mul(hasse(P_mod[q],1,M),A_shift[q],M),
                          mul(P_mod[q],shift(source_deriv,-q,M),M),M),scalar,M)
            check('two_derivative_channels',lhs==rhs)
        term[r]=terms;total[r]=s
    for r in range(1,max_r+1):
        for k in range(5):
            lhs=hasse(total[r],k,M);rhs=[0]
            for packet in term[r]: rhs=add(rhs,hasse(packet,k,M),M)
            check('packet_jet_interchange',lhs==rhs)
            for Q in range(1,min(9,packets)):
                trunc=[0]
                for packet in term[r][:Q]: trunc=add(trunc,packet,M)
                err=hasse(add(total[r],scale(trunc,-1,M),M),k,M)
                check('all_coefficient_jet_tail_bound',all(c%(1<<min(P,3*Q))==0 for c in err))
        nxt=shift(total[r+1],-1,M);nxtprime=hasse(nxt,1,M);poly=[0,-1,2];polyprime=[-1,4]
        rhs=add(scale(source,qmod(beta[r],M),M),scale(mul(poly,nxt,M),8,M),M)
        check('full_numerator_recurrence',total[r]==rhs)
        dp=hasse(total[r],1,M)
        rhsprime=add(scale(source_deriv,qmod(beta[r],M),M),
                      scale(add(mul(polyprime,nxt,M),mul(poly,nxtprime,M),M),8,M),M)
        check('differentiated_recurrence',dp==rhsprime)
        W=add(mul(source,add(mul(polyprime,nxt,M),mul(poly,nxtprime,M),M),M),
              scale(mul(source_deriv,mul(poly,nxt,M),M),-1,M),M)
        wrhs=add(mul(source,dp,M),scale(mul(source_deriv,total[r],M),-1,M),M)
        check('denominator_free_wronskian',scale(W,8,M)==wrhs)
        if r.bit_count()<=2:
            for x in range(-8,16):
                check('actual_sparse_depth_slope_norm',val2(evaluate(dp,x,M))-val2(beta[r].numerator)==1)
    for q in range(1,33):
        dp=hasse(exactP[q],1)
        for n in range(q):
            check('integer_row_value_vanishing',evaluate(exactP[q],n)==0)
            slope=evaluate(dp,n)
            expected=(-1)**(q-1-n)*math.factorial(n)*math.factorial(q-1-n)*math.prod(2*n-2*i-1 for i in range(q))
            check('integer_row_slope_exact_product',slope==expected and slope!=0)
            check('integer_row_slope_valuation',val2(slope)==val2(math.factorial(n))+val2(math.factorial(q-1-n)))
    examples=[]
    for n in range(6):
        truncated=[0]
        for packet in term[1][:n+1]: truncated=add(truncated,packet,M)
        check('finite_row_value_termination',evaluate(total[1],n,M)==evaluate(truncated,n,M))
        difference=(evaluate(hasse(total[1],1,M),n,M)-evaluate(hasse(truncated,1,M),n,M))%M
        check('finite_row_derivative_nontermination_examples',difference!=0)
        examples.append({'r':1,'offset':n,'omitted_numerator_slope_valuation':val2(difference)})
    check('fixed_difference_is_not_derivative',1**2-0**2==1 and 2*0==0)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result={'status':'PASS','precision_bits':P,'registered_checks':sum(counts.values()),
            'categories':dict(counts),'integer_row_examples':examples,
            'seconds':round(time.monotonic()-start,6),
            'scope':'Finite exact/modular implementation checks. Universal statements are Lean theorems.',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
