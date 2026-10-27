#!/usr/bin/env python3
from math import factorial
import json,time
from pathlib import Path
BASE=Path(__file__).resolve().parent

def v2(n):
    if n==0:return 10**9
    n=abs(int(n));return (n&-n).bit_length()-1

def s2(n):return int(n).bit_count()
def lam(r,q):return 3*q+s2(r+q)-s2(r)
def e(j,k):return 3*k+s2(j-1)-s2(j-k-1)
def A(j):return 3*j+1+s2(j-1)
def E(j):return min(e(j,k) for k in range(j))
def Lstar(j):return A(j)-E(j)
def d(j,i):return j-1-s2(i)-s2(j-1-i)

def C(k,s,q):
    return sum(((q-1-(s%(1<<a)))//(1<<a)+1) if q>(s%(1<<a)) else 0 for a in range(1,k+1))
def mcount(k,s,q):
    ss=s%(1<<k)
    return 0 if q<=ss else (q-1-ss)//(1<<k)+1

start=time.perf_counter(); checks=0
# Exact wall formulas.
for j in range(1,401):
    ls=Lstar(j)
    for L in range(max(ls+1,1),ls+5):
        r=(1<<L)-j
        mu=lam(r,j)
        assert mu==A(j)-L
        for k in range(j):
            assert lam(r,k)==e(j,k)
            assert lam(r,k)-mu==(L-ls)+(e(j,k)-E(j))
            checks+=3
        for h in range(0,25):
            q=j+h
            if h < (1<<L):
                assert lam(r,q)-mu==3*h+s2(h)
                checks+=1
# Derivative maximum.
for j in range(1,1001):
    ds=[d(j,i) for i in range(j)]
    assert max(ds)==(j-1-s2(j-1))
    checks+=1
# Address content identity by direct valuation-count combinatorics.
for k in range(1,8):
    for s in range(1<<k):
        for q in range(0,80):
            # min(k,v2(s-i)), with v2(0)=infinity
            direct=0
            count=0
            for i in range(q):
                z=s-i
                direct += k if z==0 else min(k,v2(z))
                if z%(1<<k)==0: count+=1
            assert direct==C(k,s,q)
            assert count==mcount(k,s,q)
            checks+=2
# j=3 staged thresholds.
j=3; ls=Lstar(j); assert ls==11
stage=[]
for delta in (1,2,3):
    L=ls+delta; r=(1<<L)-j
    # normalized direct address costs after one binary blowup
    mu=lam(r,j)
    row={'delta':delta,'L':L,'r':r,'branches':{}}
    B=max(0,(r.bit_count()-1)//3)
    for parity in (0,1):
        vals=[lam(r,q)-mu+C(1,parity,q) for q in range(B+1)]
        nu=min(vals); mins=[q for q,z in enumerate(vals) if z==nu]
        row['branches'][str(parity)]={'nu':nu,'minimizers':mins,'m':[mcount(1,parity,q) for q in mins]}
    stage.append(row)
assert stage[0]['branches']['0']['minimizers']==[0]
assert stage[0]['branches']['1']['minimizers']==[0,3]
assert stage[1]['branches']['0']['minimizers']==[0,3]
assert stage[1]['branches']['1']['minimizers']==[3]
assert stage[2]['branches']['0']['minimizers']==[3]
assert stage[2]['branches']['1']['minimizers']==[3]
res={'status':'PASS','checks':checks,'j3_stages':stage,'runtime_seconds':time.perf_counter()-start,
     'theorem_summary':{
       'normal_form':'G_{L,j}(x)=P_j(x)U_{L,j}(x-j)+2^delta V_{L,j}(x), delta=L-L_j',
       'root_threshold':'delta > 2*(v2(i!)+v2((j-1-i)!))',
       'all_roots_threshold':'delta > 2*v2((j-1)!)'}}
(BASE/'RESULTS_WALL_NORMAL_FORM.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
