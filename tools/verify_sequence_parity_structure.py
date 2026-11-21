"""Finite boundary, parity, normalization and stationary-symbol checks."""
import argparse,json,time
from fractions import Fraction as F
from math import comb
from pathlib import Path
import sequence_parity_hankel as p
from sequence_differential_hankel import structured_differential_hankel
from test_sequence_differential_hankel import direct_hankel


def prefixes(a,c,odd,parity,last):
    aa,cc,M=p.base.parameters(a,c);L=2*M;U=2*M-int(odd);K=4*M+1
    initial=tuple(range(L));v={initial:F(1)};values=[F(1)]
    def entry(i,j):
        return p.base.band_entry(2*i+(0 if odd else parity),2*j+(1 if odd else parity),aa,cc) if j>=0 else F(0)
    tail=[entry(K,K-L+k) for k in range(L+U+1)]
    for row in (K+1,K+3):assert tail==[entry(row,row-L+k) for k in range(L+U+1)]
    for i in range(last):
        diagonal=tail if i>=K else [entry(i,i-L+k) for k in range(L+U+1)]
        out={}
        for state,value in v.items():
            occupied=set(state)
            for k in range(L+U+1):
                if k in occupied or (0 not in occupied and k!=0):continue
                target=tuple(j-1 for j in sorted(occupied|{k}) if j)
                sign=(-1)**sum(j>k for j in occupied)
                out[target]=out.get(target,F(0))+sign*diagonal[k]*value
        v={key:value for key,value in out.items() if value}
        assert len(v)<=comb(L+U,L)
        values.append(v.get(initial,F(0)))
    return values,comb(L+U,L),K


def exact_div(a,b):
    a=list(a);q=[F(0)]*max(1,len(a)-len(b)+1)
    while len(a)>=len(b):
        shift=len(a)-len(b);v=F(a[-1],b[-1]);q[shift]+=v
        for j,x in enumerate(b):a[shift+j]-=v*x
        while a and not a[-1]:a.pop()
    assert not any(a)
    return q


parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
args=parser.parse_args();started=time.perf_counter();cases=[];comparisons=direct=0
for a,c in [([1,1,1],[1]),([0,1],[1]),([1,1],[1,0,1]),([1,1,1,1],[1]),([1,1],[0,1]),([1],[0,0,0,1])]:
    odd=not any(c[::2]);M=len(a)+len(c)-2;last=4*M+3
    if odd:
        block,states,K=prefixes(a,c,True,0,last)
        values=[F(1)]+[F(0) if n%2 else (-1)**(n//2)*block[n//2]**2/4 for n in range(1,2*last+1)]
    else:
        even,states,K=prefixes(a,c,False,0,last);other,_,_=prefixes(a,c,False,1,last)
        values=[F(1)]+[even[(n+1)//2]*other[n//2]/4 for n in range(1,2*last+1)]
    schur=structured_differential_hankel(a,c,len(values)-1);assert values==schur;comparisons+=len(values)
    for n in range(13):assert values[n]==direct_hankel(a,c,n);direct+=1
    cases.append({'weights':a,'operator':c,'M':M,'odd':odd,'states_per_block':states,'stationary_start':K,'checked_original_sizes':[0,len(values)-1]})

# Exact linear-coefficient stationary symbol factorization for all quadratics.
# tau(2n)=2a at n=0, otherwise 2(b-c)|n|+2c|n|^3.
cores=[];stencil=[(-1)**j*comb(4,j) for j in range(5)]
for parameter in range(3):
    a,b,c=[int(j==parameter) for j in range(3)]
    def tau(n):return 2*a if not n else 2*(b-c)*abs(n)+2*c*abs(n)**3
    numerator=[sum(stencil[i]*stencil[j]*tau(d-i+j) for i in range(5) for j in range(5)) for d in range(-4,5)]
    cores.append(list(map(str,exact_div(numerator,[1,-4,6,-4,1]))))
result={'outcome':'Parity, boundary, stationary and symbol identities checked in the stated cases',
    'cases':cases,'independent_schur_values':comparisons,'direct_determinants':direct,
    'stationary_symbol_identity':'z^4 T(z)=(1-z)^4*(a core_a(z)+b core_b(z)+c core_c(z))',
    'cores_ascending':cores,'elapsed_seconds':time.perf_counter()-started,
    'scope':'General parity reduction is proved separately; finite checks reach M3 even and odd operators.'}
Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))
