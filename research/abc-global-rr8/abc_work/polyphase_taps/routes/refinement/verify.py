#!/usr/bin/env python3
"""Exact bounded checks for genuine nested phases and exponent blocking.

Run: python3 verify.py
Grid: coprime 1<=B<A<=8, n=1,...,12, every positive divisor M of n.
Nested phases: listed (A,B,p), radices2,3,5, depths0,...,3, t=0,...,24.
"""
from pathlib import Path
from math import gcd,lcm,prod
import hashlib,json,platform,time


def factor(n):
    out={}
    d=2
    while d*d<=n:
        while n%d==0:
            out[d]=out.get(d,0)+1
            n//=d
        d+=1 if d==2 else 2
    if n>1:
        out[n]=out.get(n,0)+1
    return out


def val(x,p):
    e=0
    while x%p==0:
        e+=1
        x//=p
    return e


def phi(n):
    ans=n
    for p in factor(n):
        ans=ans//p*(p-1)
    return ans


def order(A,B,p):
    d=p-1
    for ell in factor(d):
        while d%ell==0 and pow(A,d//ell,p)==pow(B,d//ell,p):
            d//=ell
    return d


def cyclotomic_values(A,B,limit):
    out={}
    for d in range(1,limit+1):
        prior=prod(out[k] for k in range(1,d) if d%k==0)
        value=A**d-B**d
        assert value%prior==0
        out[d]=value//prior
    return out


def data(A,B,n,fs=None):
    c=A**n+B**n
    fs=factor(c) if fs is None else fs
    values=cyclotomic_values(A,B,2*n)
    E=set()
    W=G=1
    contacts={}
    for p,e in fs.items():
        if p==2:
            continue
        d=order(A,B,p)
        birth=val(values[d],p)
        assert e==birth+val(n,p)
        W*=p**(birth-1)
        G*=p**val(n,p)
        contacts[p]=(d,birth)
        if birth>=2:
            E.add(d)
    B2=2**max(fs.get(2,0)-1,0)
    U=c//prod(fs)
    assert U==B2*W*G
    return {'values':values,'E':E,'W':W,'G':G,'B2':B2,'U':U,'contacts':contacts,'degree':sum(phi(d) for d in E)}


def main():
    start=time.monotonic()
    script=Path(__file__)
    before=hashlib.sha256(script.read_bytes()).hexdigest()
    grid=blocks=components=compressions=0
    newly_exceptional=0
    examples=[]
    for A in range(2,9):
        for B in range(1,A):
            if gcd(A,B)!=1:
                continue
            for n in range(1,13):
                grid+=1
                fs=factor(A**n+B**n)
                old=data(A,B,n,fs)
                for M in range(1,n+1):
                    if n%M:
                        continue
                    blocks+=1
                    t=n//M
                    new=data(A**M,B**M,t,fs)
                    image={d//gcd(d,M) for d in old['E']}
                    assert image<=new['E']
                    H=1
                    for p,(d,s) in old['contacts'].items():
                        dr,sr=new['contacts'][p]
                        assert dr==d//gcd(d,M) and sr==s+val(M,p)
                        H*=p**val(M,p)
                        if s==1 and sr>=2:
                            newly_exceptional+=1
                    assert M%H==0
                    assert new['W']==old['W']*H and old['G']==new['G']*H
                    assert new['B2']==old['B2']
                    assert old['degree']<=M*sum(phi(r) for r in image)<=M*new['degree']
                    old_product=prod(old['values'][d] for d in old['E'])
                    new_product=prod(new['values'][r] for r in image)
                    assert new_product%old_product==0
                    allowed_old=[d for d in range(1,2*n+1) if 2*n%d==0 and n%d!=0]
                    allowed_new=[r for r in range(1,2*t+1) if 2*t%r==0 and t%r!=0]
                    for r in allowed_new:
                        fiber=[d for d in allowed_old if d//gcd(d,M)==r]
                        assert new['values'][r]==prod(old['values'][d] for d in fiber)
                        assert M*phi(r)==sum(phi(d) for d in fiber)
                        components+=1
                    if (A,B,n,M) in [(2,1,3,3),(7,1,2,2)]:
                        examples.append({'A':A,'B':B,'n':n,'M':M,'old_W':old['W'],'new_W':new['W'],'old_G':old['G'],'new_G':new['G'],'old_degree':old['degree'],'new_degree':new['degree']})
                twopart=2**val(n,2)
                m=lcm(twopart,*(d//2 for d in old['E']))
                compressed=data(A,B,m)
                assert n%m==0 and (n//m)%2==1
                assert old['W']==compressed['W'] and old['B2']==compressed['B2']
                assert old['U']%compressed['U']==0
                assert n%(old['U']//compressed['U'])==0
                assert old['degree']<=m
                compressions+=1
    phase_assertions=child_counts=0
    local_records=[]
    for A,B,p in [(7,1,5),(3,1,7),(8,1,3),(2,1,1093)]:
        d=order(A,B,p)
        s=val(A**d-B**d,p)
        floors=[]
        for t in range(p):
            n=d*t+d//2
            expected=s+val(2*t+1,p)
            assert (pow(A,n,p**expected)+pow(B,n,p**expected))%(p**expected)==0
            assert (pow(A,n,p**(expected+1))+pow(B,n,p**(expected+1)))%(p**(expected+1))!=0
            floors.append(expected)
        assert floors.count(s)==p-1 and floors.count(s+1)==1
        for N in (2,3,5):
            for r in range(4):
                M=N**r
                for k in range(1,s+3):
                    L=d*p**max(0,k-s)
                    g=gcd(M,L)
                    gn=gcd(M*N,L)
                    for j in range(M):
                        compatible=(L//2-j)%g==0
                        actual_children=sum((L//2-j-M*a)%gn==0 for a in range(N))
                        assert actual_children==(N*g//gn if compatible else 0)
                        child_counts+=1
                        period=L//g
                        residue=0 if period==1 else ((L//2-j)//g*pow(M//g,-1,period))%period
                        for t in range(25):
                            n=M*t+j
                            if n==0:
                                continue
                            actual=(pow(A,n,p**k)+pow(B,n,p**k))%(p**k)==0
                            predicted=compatible and t%period==residue
                            assert actual==predicted
                            phase_assertions+=1
        local_records.append({'A':A,'B':B,'p':p,'order':d,'birth':s,'p_children_at_birth':p-1,'p_children_one_layer_deeper':1})
    after=hashlib.sha256(script.read_bytes()).hexdigest()
    assert before==after
    result={'status':'completed','outcome':'exact finite phase/refinement/blocking assertions verified',
        'assertion_tested':'nested residue contact, compatible-child count, persistent birth floor, blocked order/depth, W/G transport, exact cyclotomic fibers, normalized degree, compression',
        'grid_cases':grid,'all_divisor_blockings':blocks,'cyclotomic_component_checks':components,'compression_checks':compressions,
        'newly_exceptional_contacts_after_blocking':newly_exceptional,'nested_phase_contact_assertions':phase_assertions,'compatible_child_count_assertions':child_counts,
        'local_birth_floor_cases':local_records,'blocking_controls':examples,
        'domain':{'grid':'coprime 1<=B<A<=8, 1<=n<=12, every M|n','nested':'listed bases/primes; N=2,3,5; r=0,...,3; every phase j; t=0,...,24; 1<=k<=birth+2; n=0 excluded','coverage':'exhaustive on these stated grids, not all exponent values'},
        'script_sha256_before':before,'script_sha256_after':after,'software':{'python':platform.python_version(),'platform':platform.platform()},'runtime_seconds':time.monotonic()-start,
        'non_claims':['not ABC','not a new high-order birth-height estimate','not Lean compiled']}
    Path('verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
