#!/usr/bin/env python3
"""Exact tests of an ABC research checkpoint. Not a proof of global abc.
Uses integer modular arithmetic for p-adic divisibility; float logs only for visualization.
"""
from __future__ import annotations
import json, math
from pathlib import Path


def primes_to(n):
    b=bytearray(b'\1')*(n+1);b[:2]=b'\0\0'
    for i in range(2, math.isqrt(n)+1):
        if b[i]:
            b[i*i:n+1:i]=b'\0'*((n-i*i)//i+1)
    return [j for j,k in enumerate(b) if k]

def factor(n):
    out=[]; j=2
    while j*j<=n:
        if n%j==0:
            out.append(j)
            while n%j==0:n//=j
        j+=1 if j==2 else 2
    if n>1:out.append(n)
    return out

def order(q,p):
    d=p-1
    for r in factor(d):
        while d%r==0 and pow(q,d//r,p)==1:d//=r
    assert pow(q,d,p)==1
    return d

def soluble_root(q,h,p,d):
    if pow((-pow(h,-1,p))%p,d,p)!=1:
        return None
    # Direct proof certificate (one residue class modulo the order)
    for t in range(d):
        if (1+h*pow(q,t,p))%p==0:return t
    raise AssertionError('No root in generated subgroup')

def root_lift(q,h,p,d,f0,e):
    # Generic prime has s_p=1; Hensel derivative of q^d is nonzero mod p.
    res=f0
    old_period=d
    for k in range(2,e+1):
        m=p**k
        candidates=[res+j*old_period for j in range(p) if (1+h*pow(q,res+j*old_period,m))%m==0]
        assert len(candidates)==1,(q,h,p,e,k,len(candidates))
        res=candidates[0]
        old_period*=p
    return res,old_period

def count_congruence(F,r,period):
    r%=period
    if r==0:return F//period
    return max(0,1+(F-r)//period)

def count_window(q,h,F,Y,X):
    total=0.0; event_count=0; main=0.0; boundary=0.0
    rows=[]
    for p in primes_to(math.isqrt(X)):
        if p<=max(Y,2) or h*q%p==0:continue
        d=order(q,p)
        if pow(q,d,p*p)==1:continue  # exceptional, excluded
        f0=soluble_root(q,h,p,d)
        if f0 is None:continue
        m=p*p;e=2
        while m<=X:
            r,per=root_lift(q,h,p,d,f0,e)
            count=count_congruence(F,r,per)
            v=math.log(p)*count
            total+=v
            event_count+=count
            main+=math.log(p)/(d*p**(e-1))
            boundary+=math.log(p)
            rows.append({'p':p,'e':e,'period':per,'root_mod_period':r,'count':count})
            m*=p;e+=1
    # Independent brute-force check using modular arithmetic for small F and X.
    direct=0.0;events=0
    for row in rows:
        p,e=row['p'],row['e']
        mod=p**e
        cnt=sum((1+h*pow(q,f,mod))%mod==0 for f in range(1,F+1))
        assert cnt==row['count'],(row,cnt)
        direct+=cnt*math.log(p)
        events+=cnt
    assert abs(total-direct)<1e-7
    assert total/F<=main+boundary/F+1e-9
    return {'F':F,'Y':Y,'X':X,'total_weighted':total,
      'mean_weighted':total/F,'events':event_count,'prime_power_rows':len(rows),
      'main_exact_density':main,'finite_boundary_over_F':boundary/F,
      'check':'all exact residue counts match brute force'}

def test_gcd(q,h,max_f):
    from math import gcd
    ns=[0]+[1+h*q**f for f in range(1,max_f+1)]
    tested=0; max_gcd=0
    for f in range(1,max_f):
        for g in range(f+1,max_f+1):
            v=gcd(ns[f],ns[g]);w=gcd(ns[f],q**(g-f)-1)
            assert v==w,(f,g,v,w)
            max_gcd=max(max_gcd,v);tested+=1
    return {'pairs':tested,'max_gcd':max_gcd}

def test_fixed_support(S=(2,3),P=(5,7,11,17),max_power=25):
    rows=[]
    mx={str(p):{'e':0,'u':0,'v':0} for p in P}
    for u in range(max_power+1):
        for v in range(max_power+1):
            if u==0 and v==0:continue
            c=S[0]**u+S[1]**v
            for p in P:
                k=0
                while (c%(p**(k+1)))==0:k+=1
                if k>mx[str(p)]['e']:
                    mx[str(p)]={'e':k,'u':u,'v':v}
            if (u,v) in {(5,2),(7,3),(3,1),(10,15),(20,18)}:
                rows.append({'u':u,'v':v,'c':str(c),'valuation_at_P':{str(p):next((k-1 for k in range(1,40) if c%p**k!=0),39) for p in P}})
    return {'checked_pairs':(max_power+1)**2-1,'largest_valuations_at_P':mx,'examples':rows}

def main():
    # Finite partial tails: not a proof of the infinite upper bound.
    tail_summaries={}
    for q in (2,3):
        vals=[]
        for p in primes_to(100000):
            if p==2 or q%p==0:continue
            d=order(q,p)
            vals.append((p,math.log(p)/(d*(p-1))))
        tail_summaries[str(q)]=[]
        for Y in (100,1000,10000):
            s=sum(v for p,v in vals if p>Y)
            tail_summaries[str(q)].append({'Y':Y,'partial_tail_up_to_100000':s,'sqrt_Y_times_partial_tail':Y**.5*s})
    win=[count_window(3,2,1500,3,50000),count_window(3,2,4000,10,250000),count_window(3,2,10000,30,1000000)]
    out={'weighted_order_partial_tails':tail_summaries,'moving_prime_power_windows':win,
       'gcd_collision_tests':test_gcd(3,2,70),
       'signed_input_fixed_support_examples':test_fixed_support(),
       'status':'Finite exact computations only. Global results proved in the note; Yu used as external theorem.'}
    target=Path(__file__).with_name('results.json')
    target.write_text(json.dumps(out,indent=2)+'\n')
    print('PASS all checks')
    print('moving:',[(x['F'],x['events'],round(x['mean_weighted'],6),x['prime_power_rows']) for x in win])
    print('collisions:',out['gcd_collision_tests'])
    print('tails q=3:',tail_summaries['3'])
if __name__=='__main__':main()
