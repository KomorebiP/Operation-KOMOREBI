from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
import csv, json, random
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]; RESULTS=ROOT/'results'; TABLES=ROOT/'tables'
RESULTS.mkdir(exist_ok=True); TABLES.mkdir(exist_ok=True)
@dataclass
class Ledger:
    checks:int=0; failures:int=0
    def check(self, cond:bool, label:str):
        self.checks+=1
        if not cond:
            self.failures+=1; raise AssertionError(label)
L=Ledger()
def vp_fraction(q:Fraction,p:int)->int:
    if q==0:return 10**9
    num,den=abs(q.numerator),q.denominator; v=0
    while num%p==0:num//=p;v+=1
    while den%p==0:den//=p;v-=1
    return v
def fibonacci(n):
    a,b=0,1
    for _ in range(n):a,b=b,a+b
    return a
def lucas(n):
    a,b=2,1
    for _ in range(n):a,b=b,a+b
    return a
def bell_numbers(nmax):
    b=[1]
    for n in range(nmax):b.append(sum(comb(n,k)*b[k] for k in range(n+1)))
    return b
def catalan(n):return comb(2*n,n)//(n+1)
def motzkin_numbers(nmax):
    if nmax==0:return [1]
    m=[1,1]
    for n in range(2,nmax+1):m.append(((2*n+1)*m[n-1]+(3*n-3)*m[n-2])//(n+2))
    return m
def partition_numbers(nmax):
    sigma=[0]*(nmax+1)
    for d in range(1,nmax+1):
        for k in range(d,nmax+1,d):sigma[k]+=d
    p=[0]*(nmax+1);p[0]=1
    for n in range(1,nmax+1):p[n]=sum(sigma[k]*p[n-k] for k in range(1,n+1))//n
    return p
def apery_numbers(nmax):
    a=[1]
    if nmax==0:return a
    a.append(5)
    for n in range(1,nmax):a.append(((34*n**3+51*n**2+27*n+5)*a[n]-n**3*a[n-1])//(n+1)**3)
    return a
def euler_even(max_even):
    e={0:1}
    for n in range(2,max_even+1,2):e[n]=-sum(comb(n,k)*e[k] for k in range(0,n,2))
    return e
def zigzag_odd(max_odd):
    x=sp.symbols('x'); ser=sp.series(sp.tan(x),x,0,max_odd+2).removeO().expand(); out={}
    for n in range(1,max_odd+1,2):out[n]=int(ser.coeff(x,n)*factorial(n))
    return out
def S(n,p):return sum((-1)**a*(2*a+1)**n for a in range(p))
def odd_prime_reconstruction(n,p,z):
    return sum((-1)**m*z[2*m+1]*comb(n,2*m)*p**(2*m)*S(n-2*m,p) for m in range(n//2+1))
def beta_coefficients(mmax):
    z=sp.symbols('z'); ser=sp.series(z**2/sp.sinh(z)**2,z,0,2*mmax+2).removeO().expand(); out=[]
    for m in range(mmax+1):
        q=sp.Rational(ser.coeff(z,2*m));out.append(Fraction(int(q.p),int(q.q)))
    return out
def R_even(n):return Fraction(3**(n+2)-1,4*(n+1)*(n+2))
def falling(n,k):return factorial(n)//factorial(n-k)
def dyadic_reconstruction(n,beta):
    return sum(beta[m]*2**(2*m)*falling(n,2*m)*R_even(n-2*m) for m in range(n//2+1))
def thue_morse(n):return n.bit_count()&1
def binomial_transform(a):return [sum(comb(n,k)*a[k] for k in range(n+1)) for n in range(len(a))]
def inverse_binomial_transform(b):return [sum((-1)**(n-k)*comb(n,k)*b[k] for k in range(n+1)) for n in range(len(b))]


def divisors(n):
    return [d for d in range(1,n+1) if n%d==0]
def standard_window_inverse(p,m,nmax):
    e=[0]*(nmax+1);e[0]=1
    for n in range(1,nmax+1):
        e[n]=(-sum(comb(m*n,m*q)*e[q] for q in range(n)))%p
    return e
def theta_polyphase(M,s,r,k):
    return sum((-1)**(k-j)*comb(k,j)*comb(M*j+s,r) for j in range(k+1))
def matrix2_mul(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def matrix2_pow(A,n):
    R=[[1,0],[0,1]]
    while n:
        if n&1:R=matrix2_mul(R,A)
        A=matrix2_mul(A,A);n//=2
    return R
def delta_step(values,n,H,r):
    return sum((-1)**(r-k)*comb(r,k)*values(n+k*H) for k in range(r+1))
def truncated_partition_coeffs(nmax,cutoff):
    coeff=[0]*(nmax+1);coeff[0]=1
    for m in range(1,cutoff+1):
        nxt=[0]*(nmax+1)
        for n,c in enumerate(coeff):
            if c:
                for r in range((nmax-n)//m+1):nxt[n+r*m]+=c
        coeff=nxt
    return coeff

def hankel_rank(values, size=7):
    r=min(size,(len(values)+1)//2)
    return int(sp.Matrix([[values[i+j] for j in range(r)] for i in range(r)]).rank())
def torsion_pair_rank(N,j):
    if N%2:return 2
    return 1 if j%2==0 else 0
def jordan_pair_rank(N,j):
    if N%2:return 4
    return 2 if j%2==0 else 1
def cubic_selector_rank(N,j):
    if N%3:return 3
    return 1 if j%3==0 else 0
def mixed_torsion_value(n):
    cubic_phase=2 if n%3==0 else -1
    return 2**n+(-2)**n+3**n*cubic_phase
def mixed_torsion_rank(N,j):
    r=N%6
    if r in (1,5):return 4
    if r==3:return 3
    if r in (2,4):return 3 if j%2==0 else 2
    return 2 if j%2==0 else 1

def main():
    rng=random.Random(20260812)
    for N in range(2,10):
        for _ in range(12):
            a=[rng.randint(-20,20) for _ in range(40)]
            packets=[[x if n%N==j else 0 for n,x in enumerate(a)] for j in range(N)]
            L.check([sum(p[n] for p in packets) for n in range(len(a))]==a,f'packet reconstruction N={N}')
            b=[rng.randint(-10,10) for _ in range(40)]
            prod=[sum(a[k]*b[n-k] for k in range(n+1)) for n in range(40)]
            for j in range(N):
                rhs=[0]*40
                for r in range(N):
                    s=(j-r)%N; ar=[a[n] if n%N==r else 0 for n in range(40)]; bs=[b[n] if n%N==s else 0 for n in range(40)]
                    conv=[sum(ar[k]*bs[n-k] for k in range(n+1)) for n in range(40)]
                    rhs=[x+y for x,y in zip(rhs,conv)]
                L.check([prod[n] if n%N==j else 0 for n in range(40)]==rhs,f'packet product N={N},j={j}')
    for M,N in [(3,4),(5,8),(7,9),(8,9)]:
        if sp.gcd(M,N)!=1:continue
        for r in range(M*N):
            for n in range(3*M*N):L.check(int(n%(M*N)==r)==int(n%M==r%M and n%N==r%N),f'CRT {M},{N},{r},{n}')
    for N in range(1,10):
        LN=lucas(N)
        for j in range(N):
            u=[fibonacci(N*m+j) for m in range(14)]
            for m in range(12):L.check(u[m+2]==LN*u[m+1]-((-1)**N)*u[m],f'Fib jump {N},{j},{m}')

    # Spectral torsion--Fourier transfer: exact packet Hankel ranks.
    for N in range(1,19):
        for j in range(0,12):
            seq=[2**(N*m+j)+(-2)**(N*m+j) for m in range(16)]
            L.check(hankel_rank(seq)==torsion_pair_rank(N,j),f'torsion pair rank {N},{j}')
            seq=[(N*m+j)*2**(N*m+j)+(N*m+j+1)*(-2)**(N*m+j) for m in range(16)]
            L.check(hankel_rank(seq)==jordan_pair_rank(N,j),f'Jordan torsion rank {N},{j}')
            seq=[3 if (N*m+j)%3==0 else 0 for m in range(16)]
            L.check(hankel_rank(seq)==cubic_selector_rank(N,j),f'cubic selector rank {N},{j}')
            seq=[mixed_torsion_value(N*m+j) for m in range(16)]
            L.check(hankel_rank(seq)==mixed_torsion_rank(N,j),f'mixed torsion rank {N},{j}')
    # Exact double periodicity and the finite 6 x 6 signature.
    for N in range(1,31):
        for j in range(18):
            L.check(mixed_torsion_rank(N+6,j)==mixed_torsion_rank(N,j),f'N periodicity {N},{j}')
            L.check(mixed_torsion_rank(N,j+6)==mixed_torsion_rank(N,j),f'j periodicity {N},{j}')
    expected_signature=[
        [2,1,2,1,2,1],
        [4,4,4,4,4,4],
        [3,2,3,2,3,2],
        [3,3,3,3,3,3],
        [3,2,3,2,3,2],
        [4,4,4,4,4,4],
    ]
    for r in range(6):
        N=6 if r==0 else r
        for j in range(6):L.check(mixed_torsion_rank(N,j)==expected_signature[r][j],f'torsion signature {r},{j}')
    # Rank-count quasipolynomial: each full address period contributes a fixed count.
    for N in range(1,61):
        q,s=divmod(N,6)
        row=expected_signature[N%6]
        for rank_value in range(1,5):
            actual=sum(mixed_torsion_rank(N,j)==rank_value for j in range(N))
            predicted=q*sum(x==rank_value for x in row)+sum(row[j]==rank_value for j in range(s))
            L.check(actual==predicted,f'rank count quasi {N},{rank_value}')
    # Fourier analysis/synthesis for the order-two Jordan example.
    x=sp.symbols('x')
    p_plus=x; p_minus=x+1
    R0=sp.expand(p_plus+p_minus); R1=sp.expand(p_plus-p_minus)
    L.check(sp.expand((R0+R1)/2-p_plus)==0,'Fourier recover plus')
    L.check(sp.expand((R0-R1)/2-p_minus)==0,'Fourier recover minus')

    bell=bell_numbers(18); L.check(bell[:10]==[1,1,2,5,15,52,203,877,4140,21147],'Bell initial')
    for n in range(16):L.check(bell[n+1]==sum(comb(n,k)*bell[k] for k in range(n+1)),f'Bell {n}')
    cat=[catalan(n) for n in range(20)]
    for n in range(1,18):L.check(cat[n]==sum(cat[k]*cat[n-1-k] for k in range(n)),f'Catalan {n}')
    mot=motzkin_numbers(20);L.check(mot[:11]==[1,1,2,4,9,21,51,127,323,835,2188],'Motzkin')
    part=partition_numbers(50);L.check(part[:16]==[1,1,2,3,5,7,11,15,22,30,42,56,77,101,135,176],'partition')
    for cutoff in range(1,25):
        trunc=truncated_partition_coeffs(24,cutoff)
        for n in range(cutoff+1):L.check(trunc[n]==part[n],f'part stab {cutoff},{n}')
    ap=apery_numbers(14);L.check(ap[:8]==[1,5,73,1445,33001,819005,21460825,584307365],'Apery')
    for n in range(1,12):L.check((n+1)**3*ap[n+1]==(34*n**3+51*n**2+27*n+5)*ap[n]-n**3*ap[n-1],f'Apery rec {n}')
    for _ in range(100):
        a=[rng.randint(-100,100) for _ in range(18)];L.check(inverse_binomial_transform(binomial_transform(a))==a,'binomial inverse')
    for n in range(4096):
        digit_rec=0;m=n
        while m:digit_rec^=(m&1);m>>=1
        L.check(thue_morse(n)==digit_rec,f'TM {n}');L.check(thue_morse(2*n)==thue_morse(n),f'TM even {n}');L.check(thue_morse(2*n+1)==1-thue_morse(n),f'TM odd {n}')
    e=euler_even(24);z=zigzag_odd(25)
    for p in [3,5,7,11]:
        for n in range(0,25,2):
            L.check(odd_prime_reconstruction(n,p,z)==e[n],f'odd Euler {p},{n}')
            for M in range(n//2+1):
                trunc=sum((-1)**m*z[2*m+1]*comb(n,2*m)*p**(2*m)*S(n-2*m,p) for m in range(min(M,n//2)+1));err=e[n]-trunc
                L.check(err==0 if M>=n//2 else err%(p**(2*M+2))==0,f'odd tail {p},{n},{M}')
    beta=beta_coefficients(12)
    for b in beta:L.check(vp_fraction(b,2)>=0,f'beta {b}')
    for m0 in range(1,len(beta)):
        L.check(vp_fraction(beta[m0],2)==m0.bit_count()-1,f'exact beta valuation {m0}')
    for n0 in range(0,81,2):
        L.check(vp_fraction(R_even(n0),2)==0,f'dyadic source unit {n0}')
    for n in range(0,25,2):
        L.check(dyadic_reconstruction(n,beta)==e[n],f'dyadic {n}')
        for M in range(n//2+1):
            trunc=sum(beta[m]*2**(2*m)*falling(n,2*m)*R_even(n-2*m) for m in range(min(M,n//2)+1));err=Fraction(e[n])-trunc
            L.check(err==0 if M>=n//2 else vp_fraction(err,2)>=2*M+2,f'dyadic tail {n},{M}')
    # Standard-window finite-field Fourier transfer and exact inverse period.
    for p0 in [3,5,7,11,13,17,19,23]:
        for m0 in divisors(p0-1):
            h=(p0-1)//m0
            inv=standard_window_inverse(p0,m0,5*h+4)
            for n0 in range(1,len(inv)-h):
                L.check(inv[n0+h]==inv[n0],f'standard window period {p0},{m0},{n0}')
            for n0 in range(0,min(3*h+3,len(inv))):
                lhs=sum(comb(m0*n0,m0*q)*inv[q] for q in range(n0+1))%p0
                L.check(lhs==(1 if n0==0 else 0),f'standard window inverse {p0},{m0},{n0}')

    # Carmichael--Mahler scalar and matrix transfer.
    for p0 in [3,5,7,11]:
        H=p0-1
        for u in range(1,p0*3):
            if u%p0==0:continue
            q=pow(u,H)-1
            for j in range(0,min(H,5)):
                for x0 in range(0,9):
                    rhs=sum((q**r)*comb(x0,r) for r in range(x0+1))*pow(u,j)
                    L.check(rhs==pow(u,H*x0+j),f'scalar Mahler {p0},{u},{j},{x0}')
                    for r in range(0,5):
                        L.check(vp_fraction(Fraction(pow(u,j)*pow(q,r)),p0)>=r,f'scalar Mahler weight {p0},{u},{j},{r}')
    C=[[1,1],[1,0]]
    C12=matrix2_pow(C,12)
    L.check(C12==[[233,144],[144,89]],'Fibonacci C12')
    for a0 in range(0,5):
        H=12*(2**a0)
        CH=matrix2_pow(C,H)
        for i in range(2):
            for j in range(2):
                target=1 if i==j else 0
                L.check((CH[i][j]-target)%(2**(a0+3))==0,f'matrix precision amplification {a0},{i},{j}')
        for n0 in range(0,20):
            for r in range(0,5):
                diff=delta_step(fibonacci,n0,H,r)
                L.check(diff%(2**((a0+3)*r))==0,f'Fibonacci refined Mahler {a0},{n0},{r}')

    # Exact polyphase and affine Mahler transfer.
    for M0 in range(1,7):
        for s0 in range(M0):
            for q0 in range(0,8):
                for r0 in range(0,18):
                    rhs=sum(theta_polyphase(M0,s0,r0,k)*comb(q0,k) for k in range(r0+1))
                    L.check(rhs==comb(M0*q0+s0,r0),f'polyphase binomial {M0},{s0},{q0},{r0}')
    for M0 in range(1,5):
        for N0 in range(1,5):
            for s0 in range(M0):
                for t0 in range(N0):
                    for r0 in range(0,14):
                        for ell in range(0,6):
                            lhs=sum(theta_polyphase(M0,s0,r0,k)*theta_polyphase(N0,t0,k,ell) for k in range(r0+1))
                            rhs=theta_polyphase(M0*N0,M0*t0+s0,r0,ell)
                            L.check(lhs==rhs,f'polyphase composition {M0},{N0},{s0},{t0},{r0},{ell}')
    for p0 in [2,3,5,7]:
        for a0 in [1,2]:
            M0=p0**a0
            for s0 in range(min(M0,8)):
                for k in range(0,5):
                    for r0 in range(0,M0*k+s0+1):
                        u=r0-M0*k
                        rhs=comb(s0,u) if 0<=u<=s0 else 0
                        L.check((theta_polyphase(M0,s0,r0,k)-rhs)%p0==0,f'Frobenius polyphase {p0},{a0},{s0},{k},{r0}')
    for p0 in [2,3,5]:
        for M0 in [2,3,4,5]:
            for s0 in range(M0):
                for k in range(0,8):
                    coeff=[(p0**r)*(1+r%5) for r in range(M0*k+s0+1)]
                    d=sum(coeff[r]*theta_polyphase(M0,s0,r,k) for r in range(k,M0*k+s0+1))
                    L.check(vp_fraction(Fraction(d),p0)>=k,f'polyphase valuation preservation {p0},{M0},{s0},{k}')

    m=5
    for c in [-7,-1,1,5,23]:
        for n in range(m+1):L.check(c*comb(n,m+1)==0,f'prefix {c},{n}')
        L.check(c*comb(m+1,m+1)==c,f'prefix divergence {c}')
    summary={'status':'PASS' if L.failures==0 else 'FAIL','checks':L.checks,'failures':L.failures,'families':['packet algebra','CRT refinement','Fibonacci/Lucas jumps','spectral torsion packet ranks','exact torsion signatures and periodicity','Fourier mode reconstruction','Bell','Catalan','Motzkin','partitions','Apery','binomial/Riordan','Thue-Morse','odd-prime Euler coordinates','sharp weighted dyadic Euler coordinates','finite-field standard-window periods','Carmichael-Mahler packet transfer','polyphase Mahler kernels and composition','prime-power Frobenius sparsity','polyphase valuation preservation','finite-prefix non-identifiability'],'sample_values':{'Bell_0_10':bell[:11],'Catalan_0_10':cat[:11],'Motzkin_0_10':mot[:11],'Partition_0_15':part[:16],'Apery_0_7':ap[:8],'Euler_even_0_20':[e[n] for n in range(0,21,2)]}}
    (RESULTS/'verification_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    with (TABLES/'verification_ledger.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['metric','value']);w.writerow(['status',summary['status']]);w.writerow(['checks',summary['checks']]);w.writerow(['failures',summary['failures']]);w.writerow(['families',len(summary['families'])])
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
