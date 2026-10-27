#!/usr/bin/env python3
"""Independent exact ABC controls. All classifications use integers.

The quality column is a float for display only. This finite census cannot
establish the quantified abc conjecture.
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

def factor(n: int) -> dict[int, int]:
    out: dict[int, int] = {}
    d = 2
    while d*d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0)+1
            n //= d
        d = 3 if d == 2 else d+2
    if n > 1: out[n] = out.get(n, 0)+1
    return out

def radical(n: int) -> int:
    return math.prod(factor(n))

def row(a: int, b: int, c: int) -> dict[str, object]:
    assert a+b == c and math.gcd(a,b) == 1
    R = radical(a)*radical(b)*radical(c)
    Q = a*b*c//R
    assert Q*R == a*b*c
    return {'a':a,'b':b,'c':c,'rad_a':radical(a),'rad_b':radical(b),
            'rad_c':radical(c),'R':R,'Q':Q,'c_over_R_numerator':c,
            'c_over_R_denominator':R,'quality_display_only':math.log(c)/math.log(R),
            'factor_a':factor(a),'factor_b':factor(b),'factor_c':factor(c)}

started=time.monotonic()
N=10000
rad=[1]*(N+1)
phi=list(range(N+1))
for p in range(2,N+1):
    if rad[p] == 1:
        for k in range(p,N+1,p):
            rad[k] *= p
            phi[k] -= phi[k]//p
count=0
high=[]
integer_hist={}
for c in range(2,N+1):
    for a in range(1,c//2+1):
        if math.gcd(a,c) != 1: continue
        b=c-a; count+=1
        R=rad[a]*rad[b]*rad[c]
        if c > R:
            high.append({'a':a,'b':b,'c':c,'R':R,'quality_display_only':math.log(c)/math.log(R)})
        bucket=(c//500, R.bit_length())
        integer_hist[bucket]=integer_hist.get(bucket,0)+1
independent_count=1+sum(phi[3:])//2
assert count == independent_count
assert count == 1+sum(x//2 for x in phi[3:])
with (OUT/'abc_census_high_quality.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=['a','b','c','R','quality_display_only'])
    writer.writeheader();writer.writerows(high)
with (OUT/'abc_census_integer_histogram.csv').open('w',newline='') as stream:
    writer=csv.writer(stream);writer.writerow(['c_bin_width_500','R_bit_length','count'])
    writer.writerows([*key,value] for key,value in sorted(integer_hist.items()))
examples=[row(1,8,9),row(3,125,128),row(1,4374,4375),row(2,109*3**10,23**5),row(2,3**10,3**10+2)]
assert examples[3]['R'] == 15042
assert 2+3**10 != 23**5
family=[row(1,2**k,2**k+1)|{'k':k} for k in range(1,21)]
modular=[]
for precision in (8,16,32,64):
    modulus=2**precision
    # For k > 2N, k-v2(k) >= N. Thus the omitted tail is 0 modulo 2^N.
    K=2*precision
    raw=0;depleted=0
    for k in range(1,K+1):
        v=(k & -k).bit_length()-1
        odd=k//2**v
        term=pow(2,k-v,modulus)*pow(odd,-1,modulus)
        raw=(raw+term)%modulus
        if k%2: depleted=(depleted+term)%modulus
    assert raw == 0
    assert depleted % 2 == 0 and depleted % 4 == 2
    modular.append({'precision':precision,'K':K,'raw_residue':raw,
                    'depleted_residue':depleted,'depleted_valuation':1})
report={'status':'PASS','census':{'c_max':N,'a_le_b':True,'primitive_triples':count,
    'totient_control_count':independent_count,'high_quality_c_greater_R':len(high),
    'highest_quality_display_only':max(high,key=lambda z:z['quality_display_only']),
    'exact_classification':'c > R over integers, equivalent to quality > 1'},
    'examples':examples,'endpoint_family':family,'small_prime_rank_one_control':modular,
    'arithmetic':'Standard-library exact integers. Logs and elapsed time are display diagnostics only.',
    'non_claims':['Finite census cannot prove abc','Zero residues at finite precision alone are not an analytic proof of Li_1(2)=0','No product formula supplied'],
    'elapsed_seconds_diagnostic_only':round(time.monotonic()-started,3)}
(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','census':report['census'],'examples':examples,'seconds':report['elapsed_seconds_diagnostic_only']},indent=2))
