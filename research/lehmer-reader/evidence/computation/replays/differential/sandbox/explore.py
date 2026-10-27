from math import comb,isqrt
from collections import Counter
import time, json
from pathlib import Path

def tau_triangular(N):
    # F(q)=A(q)^8, A=sum (-1)^m(2m+1) q^(m(m+1)/2).
    # n F_n = sum_{T_m<=n,m>=1} a_m(9T_m-n)F_(n-T_m).
    ts=[]; m=1
    while m*(m+1)//2<N:
        ts.append((m*(m+1)//2,(-1 if m%2 else 1)*(2*m+1)));m+=1
    F=[0]*N;F[0]=1
    for n in range(1,N):
        s=0
        for t,a in ts:
            if t>n:break
            s+=a*(9*t-n)*F[n-t]
        F[n],rem=divmod(s,n)
        assert rem==0,(n,rem)
    return [0]+F

def sigma_primes(N):
    s=[0]*(N+1)
    for d in range(1,N+1):
        for n in range(d,N+1,d):s[n]+=d
    sieve=bytearray(b'\x01')*(N+1);sieve[:2]=b'\x00\x00'
    for p in range(2,isqrt(N)+1):
        if sieve[p]: sieve[p*p:N+1:p]=b'\x00'*((N-p*p)//p+1)
    return s,[p for p in range(2,N+1) if sieve[p]]

def val(a,p):
    if a==0:return None
    v=0
    while a%p==0:v+=1;a//=p
    return v

def product_tau(N):
    a=[0]*N;a[0]=1
    for k in range(1,N):
        b=a.copy()
        for j in range(1,min(24,(N-1)//k)+1):
            c=(-1)**j*comb(24,j)
            for i in range(j*k,N): b[i]+=c*a[i-j*k]
        a=b
    return [0]+a

if __name__=='__main__':
    t=time.perf_counter();N=20000
    tau=tau_triangular(N);sig,primes=sigma_primes(N)
    assert tau[:129]==product_tau(128)
    assert tau[1:8]==[1,-24,252,-1472,4830,-6048,-16744]
    records=[];nchecks=0
    for p in primes:
        S=[0]*5
        for k in range(1,p):
            a=sig[k]*sig[p-k]; power=1
            for j in range(5): S[j]+=power*a;power*=k
        # exact identities
        assert 12*S[0]==(p-1)*(p+1)*(5*p-6)
        assert 2*S[1]==p*S[0]
        assert 24*S[2]==p*p*(p-1)*(p+1)*(3*p-4)
        assert 24*S[3]==p**3*(p-1)*(p+1)*(2*p-3)
        C=p**4*(p+1)*(50*p*p-134*p+85)
        assert tau[p]==C-840*S[4]
        niebur=p**4*(p+1)-24*(35*S[4]-52*p*S[3]+18*p*p*S[2])
        assert tau[p]==niebur
        assert tau[p]**2<=4*p**11
        nchecks+=1
        if p>7:
            assert (S[4]%p**4==0)==(tau[p]%p**4==0)
        if val(tau[p],p) or p in [11,13,17,19,479,719,839,8191,16381]:
            records.append({'p':p,'tau':tau[p],'S4':S[4],'vp_tau':val(tau[p],p),'vp_S4':val(S[4],p),'S4_mod_p':S[4]%p,'S4_over_p_mod_p':(S[4]//p)%p if S[4]%p==0 else None})
    out={'N':N,'prime_count':len(primes),'identity_checks':nchecks,'selected':records,'runtime':time.perf_counter()-t}
    print(json.dumps(out,indent=2))
    open(Path(__file__).resolve().parent/'results_initial.json','w').write(json.dumps(out,indent=2)+'\n')
