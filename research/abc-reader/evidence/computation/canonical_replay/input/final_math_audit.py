from __future__ import annotations
import itertools, math, json, random
from pathlib import Path
from fractions import Fraction
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ

ROOT=Path(__file__).resolve().parent


def factors(n:int):
    return {int(p):int(e) for p,e in sp.factorint(n).items()}

def rad(n:int):
    r=1
    for p in factors(n): r*=p
    return r

def snf_diag(A:sp.Matrix):
    D=smith_normal_form(A,domain=ZZ)
    return tuple(abs(int(D[i,i])) for i in range(min(D.rows,D.cols)) if D[i,i]!=0)

def phase_matrix(a:int,b:int):
    c=a+b
    cols=[]
    for p in factors(a): cols.append((a//p,-a*b//p))
    for p in factors(b): cols.append((b//p,a*b//p))
    for p in factors(c): cols.append((-c//p,0))
    if not cols: return sp.zeros(2,0)
    return sp.Matrix(2,len(cols),lambda i,j:cols[j][i])

def polyphase_matrix(e:int,N:int):
    counts=[sum(1 for k in range(e) if k%N==r) for r in range(N)]
    return sp.Matrix(N,N,lambda r,s:counts[(r-s)%N])

def wronskian_test(a,b,x):
    c=a+b
    ps=[]; lam=[]
    for n,sgn in [(a,1),(b,1),(c,-1)]:
        for p,e in factors(n).items():
            ps.append((n,p,e,sgn))
            lam.append(sgn*n*e//p)
    assert sum(l*v for l,v in zip(lam,x))==0
    def dx(n):
        return sum(n*e*x[i]//p for i,(nn,p,e,sgn) in enumerate(ps) if nn==n)
    W=a*dx(b)-b*dx(a)
    return W

results={}
# 1. Smith invariants of the exponent-free phase matrix on all nondegenerate triples c<=1000.
count=0
for c in range(3,1001):
    for a in range(1,c//2+1):
        b=c-a
        if math.gcd(a,b)!=1 or (a,b)==(1,1): continue
        A=phase_matrix(a,b)
        entries=[abs(int(v)) for v in A if v]
        d1=math.gcd(*entries)
        minors=[]
        for i in range(A.cols):
            for j in range(i+1,A.cols):
                det=abs(int(A[0,i]*A[1,j]-A[0,j]*A[1,i]))
                if det:minors.append(det)
        d12=math.gcd(*minors)
        diag=(d1,d12//d1)
        Q=a*b*c//rad(a*b*c)
        if diag!=(1,Q):
            raise AssertionError(('phase_snf',a,b,c,diag,Q,A))
        count+=1
results['phase_snf_triples']=count

# 2. Polyphase SNF over a broad grid.
count=0
for N in range(2,13):
    for e in range(1,31):
        if math.gcd(e,N)!=1: continue
        diag=snf_diag(polyphase_matrix(e,N))
        expected=(1,)*(N-1)+(e,)
        if diag!=expected:
            raise AssertionError(('polyphase',e,N,diag,expected))
        count+=1
results['polyphase_snf_cases']=count

# 3. Wronskian divisibility for random exact additive packets by constructing null vectors.
rng=random.Random(20260731)
count=0
for _ in range(2500):
    c=rng.randint(3,10000)
    a=rng.randint(1,c-1); b=c-a
    g=math.gcd(a,b); a//=g; b//=g; c=a+b
    # prime-coordinate additive row
    lam=[]
    for n,sgn in [(a,1),(b,1),(c,-1)]:
        for p,e in factors(n).items(): lam.append(sgn*n*e//p)
    if len(lam)<2: continue
    i,j=rng.sample(range(len(lam)),2)
    gg=math.gcd(abs(lam[i]),abs(lam[j]))
    x=[0]*len(lam);x[i]=lam[j]//gg;x[j]=-lam[i]//gg
    W=wronskian_test(a,b,x)
    Q=a*b*c//rad(a*b*c)
    if W%Q: raise AssertionError(('wronskian',a,b,c,W,Q))
    count+=1
results['wronskian_divisibility_packets']=count

# 4. Divisor packet identity n=prod B_d^phi(d).
count=0
for n in list(range(1,5000))+[2**80*3**25*5**7, 24833+5020969537415167]:
    f=factors(n)
    maxe=max(f.values(),default=0)
    out=1
    for d in range(1,maxe+1):
        B=1
        for p,e in f.items():
            if e%d==0:B*=p
        out*=B**int(sp.totient(d))
    if out!=n: raise AssertionError(('divisor_packet',n,out))
    count+=1
results['divisor_packet_cases']=count

# 5. Kummer kernel identity via direct valuation-vector order, small cases.
count=0
for c in range(2,1000):
    f=factors(c); M=c//rad(c)
    if M==1: continue
    es=list(f.values())
    g=math.gcd(M,*es)
    order=M//g
    # verify exact order in (Z/M)^r
    if not all((order*e)%M==0 for e in es): raise AssertionError
    for k in range(1,order):
        if all((k*e)%M==0 for e in es): raise AssertionError(('kummer',c,M,g,order,k))
    count+=1
results['kummer_kernel_cases']=count

# 6. Atkin-Lehner Walsh identities on diagonal involution model.
count=0
for r in range(1,8):
    signs=list(itertools.product((-1,1),repeat=r)); n=2**r
    Ws=[]
    for j in range(r): Ws.append(sp.diag(*[s[j] for s in signs]))
    I=sp.eye(n); packets=[]
    for eps in signs:
        A=sp.eye(n)
        for e,W in zip(eps,Ws): A*=I+e*W
        if A*A != 2**r*A: raise AssertionError
        packets.append(A)
    if sum(packets,sp.zeros(n)) != 2**r*I: raise AssertionError
    for i in range(len(packets)):
        for j in range(i):
            if packets[i]*packets[j]!=sp.zeros(n):raise AssertionError
    count+=len(packets)
results['walsh_packets']=count

# 7. Worked theta exact brute force for 3+125=128.
lam=[1,75,-448]
best=None; vecs=[]
for x0 in range(-8,9):
 for x1 in range(-8,9):
  for x2 in range(-8,9):
   if x0==x1==x2==0 or x0+75*x1-448*x2:continue
   W=3*(125*3*x1//5)-125*(3*x0//3) # d(b)=75*x1, d(a)=x0
   # correct W = 3*75*x1 -125*x0
   W=225*x1-125*x0
   if W==0:continue
   h=max(abs(x0),abs(x1),abs(x2))
   if best is None or h<best:best=h;vecs=[(x0,x1,x2,W)]
   elif h==best:vecs.append((x0,x1,x2,W))
if best!=6 or (-2,6,1,1600) not in vecs:
    raise AssertionError(('theta_worked',best,vecs[:20]))
results['worked_theta_height']=best

(ROOT/'final_math_audit_results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
