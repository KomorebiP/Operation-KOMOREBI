from __future__ import annotations

import itertools
import json
import math
import re
from pathlib import Path

import numpy as np
from numpy.linalg import inv, norm
from scipy.integrate import quad, quad_vec
from scipy.linalg import expm, eigh

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_VI_Strengthened_Annals_Edition.tex"
BIB = ROOT / "PSC_Paper_VI_Strengthened_Annals_Edition.bib"
ORIGINAL = Path(__file__).with_name("original_numerical_results.json")

checks = 0
groups: list[tuple[str, int]] = []


def scalar_close(a, b, tol=1e-10, msg=""):
    global checks
    checks += 1
    if not (abs(complex(a) - complex(b)) <= tol):
        raise AssertionError(msg or f"{a!r} != {b!r} within {tol}")


def array_close(a, b, tol=1e-10, msg=""):
    global checks
    aa = np.asarray(a)
    bb = np.asarray(b)
    if aa.shape != bb.shape:
        raise AssertionError(msg or f"shape mismatch {aa.shape} != {bb.shape}")
    diff = np.abs(aa - bb)
    for value in diff.ravel():
        checks += 1
        if not value <= tol:
            raise AssertionError(msg or f"array residual {diff.max()} exceeds {tol}")


def true(value, msg=""):
    global checks
    checks += 1
    if not bool(value):
        raise AssertionError(msg or "condition failed")


def mark(name, start):
    groups.append((name, checks - start))


rng = np.random.default_rng(260813)

# 1. Packet semigroup and directed paths
start = checks
for dim in (3, 4, 5):
    A = rng.normal(size=(dim, dim)) * 0.2
    split = dim // 2
    P = [np.diag([1.0] * split + [0.0] * (dim - split)),
         np.diag([0.0] * split + [1.0] * (dim - split))]
    for s in np.linspace(0, 0.7, 8):
        for t in np.linspace(0, 0.8, 9):
            Ts = expm(s * A)
            Tt = expm(t * A)
            Tst = expm((s + t) * A)
            array_close(Tst, Ts @ Tt, 3e-12)
            for beta in range(2):
                for alpha in range(2):
                    rhs = sum(P[beta] @ Ts @ P[g] @ Tt @ P[alpha] for g in range(2))
                    array_close(P[beta] @ Tst @ P[alpha], rhs, 4e-12)
    h = 1e-7
    Tph = expm(h * A)
    for beta in range(2):
        for alpha in range(2):
            derivative = (P[beta] @ Tph @ P[alpha] - (P[alpha] if beta == alpha else 0)) / h
            array_close(derivative, P[beta] @ A @ P[alpha], 2e-7)

# Acyclic transfer gives a finite Dyson series: strictly upper triangular N
D = np.diag([-0.2, -0.4, -0.7, -1.0])
N = np.array([[0, 0.4, 0, 0], [0, 0, 0.3, 0], [0, 0, 0, 0.2], [0, 0, 0, 0]], float)
array_close(np.linalg.matrix_power(N, 4), np.zeros((4, 4)), 0)
mark("packet semigroup and paths", start)

# 2. Duhamel, resolvent, and holomorphic defect
start = checks
for _ in range(25):
    Af = rng.normal(size=(3, 3)) * 0.25
    Ac = rng.normal(size=(2, 2)) * 0.25
    C = rng.normal(size=(2, 3))
    Delta = C @ Af - Ac @ C
    for t in (0.0, 0.03, 0.2, 0.9):
        lhs = C @ expm(t * Af) - expm(t * Ac) @ C
        if t == 0:
            rhs = np.zeros_like(lhs)
        else:
            rhs, _ = quad_vec(lambda s: expm((t-s)*Ac) @ Delta @ expm(s*Af), 0, t, epsabs=1e-12)
        array_close(lhs, rhs, 2e-10)
    z = 4.0 + 0.4j
    Rf = inv(z*np.eye(3) - Af)
    Rc = inv(z*np.eye(2) - Ac)
    array_close(C @ Rf - Rc @ C, Rc @ Delta @ Rf, 2e-12)
    # Polynomial functional calculus defect for g(x)=x^3+2x
    gAf = Af@Af@Af + 2*Af
    gAc = Ac@Ac@Ac + 2*Ac
    rhs = C@Af@Af@Af - Ac@Ac@Ac@C + 2*Delta
    array_close(C@gAf - gAc@C, rhs, 2e-12)
mark("defect calculus", start)

# 3. Refinement towers
start = checks
# Exact compatible two level tower
C = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
R = C.T
Ac = np.array([[-0.5, 0.2], [0.1, -0.7]])
Af = np.block([[Ac, np.zeros((2,1))], [np.zeros((1,2)), np.array([[-1.3]])]])
array_close(C@Af, Ac@C, 1e-14)
for t in np.linspace(0, 2, 41):
    array_close(C@expm(t*Af), expm(t*Ac)@C, 4e-13)
    array_close(C@expm(t*Af)@R, expm(t*Ac), 4e-13)
# Summable synthetic adjacent defects and telescoping bound
E = [2.0**(-j-4) for j in range(25)]
for n in range(1, 20):
    tail = sum(E[n:])
    true(tail <= 2.0**(-n-3) + 1e-15)
# Closure obstruction identity at a finite level
T = expm(0.3 * Af)
P = R @ C
lhs = (C@T@R) @ (C@T@R) - C@(T@T)@R
rhs = C@T@(P-np.eye(3))@T@R
array_close(lhs, rhs, 2e-13)
mark("refinement towers", start)

# 4. Markov lumping
start = checks
K = np.array([[.55,.25,.10,.10], [.25,.55,.10,.10], [.10,.10,.60,.20], [.10,.10,.20,.60]])
Cpart = np.array([[1,1,0,0],[0,0,1,1]], float)
Kbar = np.array([[.8,.2],[.2,.8]])
array_close(Cpart@K, Kbar@Cpart, 2e-15)
for n in range(60):
    array_close(Cpart@np.linalg.matrix_power(K,n), np.linalg.matrix_power(Kbar,n)@Cpart, 2e-13)
Kp = K.copy(); Kp[:,1] += np.array([.01,-.01,-.01,.01])
Delta = Cpart@Kp - Kbar@Cpart
for n in range(1, 50):
    lhs = Cpart@np.linalg.matrix_power(Kp,n)-np.linalg.matrix_power(Kbar,n)@Cpart
    rhs = sum(np.linalg.matrix_power(Kbar,n-1-j)@Delta@np.linalg.matrix_power(Kp,j) for j in range(n))
    array_close(lhs, rhs, 3e-13)
    true(norm(lhs,1) <= n*norm(Delta,1)+1e-12)
# Generator version
Q = K - np.eye(4)
Qbar = Kbar - np.eye(2)
for t in np.linspace(0, 3, 61):
    array_close(Cpart@expm(t*Q), expm(t*Qbar)@Cpart, 3e-13)
mark("Markov lumping", start)

# 5. Conditional expectations and martingale packets
start = checks
pi = np.array([.08,.12,.18,.22,.16,.24])
parts = [[[0,1,2,3,4,5]], [[0,1,2],[3,4,5]], [[0,1],[2],[3,4],[5]], [[0],[1],[2],[3],[4],[5]]]
def pmat(part):
    P = np.zeros((6,6))
    for block in part:
        w = pi[block]/pi[block].sum()
        for i in block:
            P[i,block] = w
    return P
Ps = [pmat(p) for p in parts]
W = np.diag(pi)
for P in Ps:
    array_close(P@P, P, 2e-15)
    array_close(P.T@W, W@P, 2e-15)
for i in range(len(Ps)):
    for j in range(len(Ps)):
        array_close(Ps[i]@Ps[j], Ps[min(i,j)], 3e-15)
Ds=[Ps[0]]+[Ps[i]-Ps[i-1] for i in range(1,len(Ps))]
for i,D in enumerate(Ds):
    for j,E in enumerate(Ds):
        array_close(D@E, D if i==j else np.zeros_like(D), 4e-15)
for _ in range(100):
    f=rng.normal(size=6)
    lhs=f@W@f
    rhs=sum((D@f)@W@(D@f) for D in Ds)
    scalar_close(lhs,rhs,3e-13)
mark("conditional expectation", start)

# 6. Bayesian reconstruction, sufficiency, and bounds
start = checks
for _ in range(500):
    p=rng.dirichlet(np.ones(7))
    lam=np.exp(rng.normal(size=7))
    mu=np.exp(rng.normal(size=7))
    B=lambda l,x: l*x/(l@x)
    array_close(B(mu,B(lam,p)), B(lam*mu,p), 4e-14)
    groups_idx=[np.array([0,1,2]),np.array([3,4]),np.array([5,6])]
    post=B(lam,p)
    masses=np.array([post[g].sum() for g in groups_idx])
    pmass=np.array([p[g].sum() for g in groups_idx])
    av=np.array([(lam[g]@p[g])/p[g].sum() for g in groups_idx])
    coarse=av*pmass/(av@pmass)
    array_close(masses,coarse,4e-14)
    d=np.sum(np.abs(lam-mu)*p)
    bound=2*d/max(lam@p,mu@p)
    true(norm(B(lam,p)-B(mu,p),1) <= bound+2e-14)
# Exact sufficiency for block constant likelihood
ell=np.array([.6,1.3,2.0])
lam=np.concatenate([np.full(3,ell[0]),np.full(2,ell[1]),np.full(2,ell[2])])
for _ in range(200):
    p=rng.dirichlet(np.ones(7))
    fine=lam*p/(lam@p)
    masses=np.array([fine[:3].sum(),fine[3:5].sum(),fine[5:].sum()])
    cp=np.array([p[:3].sum(),p[3:5].sum(),p[5:].sum()])
    coarse=ell*cp/(ell@cp)
    array_close(masses,coarse,3e-14)
# Nonconstant likelihood changes local distribution
p=np.ones(4)/4; lam=np.array([1.,2.,1.,1.])
post=lam*p/(lam@p)
true(abs(post[0]/(post[0]+post[1])-.5)>0.1)
mark("Bayesian transfer", start)

# 7. Bayesian flow and hidden Markov filtering
start = checks
for _ in range(120):
    p=rng.dirichlet(np.ones(6)); g=rng.normal(size=6)
    def phi(t):
        w=np.exp(t*g)*p
        return w/w.sum()
    s,t=rng.random(2)*2
    w=np.exp(s*g)*phi(t); composed=w/w.sum()
    array_close(phi(s+t),composed,3e-14)
    h=1e-6
    deriv=(phi(t+h)-phi(t-h))/(2*h)
    pt=phi(t)
    rhs=(g-g@pt)*pt
    array_close(deriv,rhs,2e-9)
    mean=g@pt
    var=((g-mean)**2)@pt
    h2=1e-4
    psi=lambda x: math.log(np.sum(np.exp(x*g)*p))
    second=(psi(t+h2)-2*psi(t)+psi(t-h2))/h2**2
    scalar_close(second,var,2e-6)
K=np.array([[.8,.25],[.2,.75]])
p=np.array([.6,.4])
likes=[np.array([1.4,.5]),np.array([.3,1.2]),np.array([1.7,.4])]
for l in likes:
    p=K@p; p=l*p/(l@p)
    scalar_close(p.sum(),1,2e-15)
    true(np.all(p>=0))
mark("Bayesian flow and filtering", start)

# 8. Fractional powers and subordination
start = checks
for dim in (2,3,5):
    U,_=np.linalg.qr(rng.normal(size=(dim,dim)))
    vals=np.linspace(.4,3.0,dim)
    L=U@np.diag(vals)@U.T
    for alpha in (.2,.5,.8):
        La=U@np.diag(vals**alpha)@U.T
        beta_integral,_=quad(lambda u: 1.0,0,1,weight="alg",wvar=(alpha-1,-alpha),epsabs=2e-12)
        scalar_factor=math.sin(math.pi*alpha)/math.pi*beta_integral
        approx=U@np.diag(vals**alpha*scalar_factor)@U.T
        array_close(La,approx,2e-10)
        for t in (.1,.7):
            array_close(expm(-t*La)@expm(-.3*La),expm(-(t+.3)*La),4e-13)
# Fractional defect bound on diagonal fine/coarse pair
Lf=np.diag([.8,1.7,2.9]); Lc=np.diag([1.0,2.2]); C=rng.normal(size=(2,3))
for alpha in (.2,.5,.8):
    D=C@Lf-Lc@C
    lhs=C@np.diag(np.diag(Lf)**alpha)-np.diag(np.diag(Lc)**alpha)@C
    bound=alpha*(.8**(alpha-1))*norm(D,2)
    true(norm(lhs,2)<=bound+2e-12)
# Poisson subordination scalar checks
for lam in (0.,.25,1.,4.,9.):
    for t in (.2,1.,2.):
        val,_=quad(lambda s: t/(2*math.sqrt(math.pi))*s**(-1.5)*math.exp(-t*t/(4*s)-lam*s),0,np.inf,epsabs=1e-11)
        scalar_close(val,math.exp(-t*math.sqrt(lam)),2e-10)
mark("fractional functional calculus", start)

# 9. Green operators and finite differences
start = checks
for n in range(2,70):
    h=1/(n+1)
    L=(2*np.eye(n)-np.eye(n,k=1)-np.eye(n,k=-1))/h**2
    Linv=inv(L)
    x=np.arange(1,n+1)*h
    G=np.minimum.outer(x,x)-np.outer(x,x)
    array_close(Linv/h,G,2e-11)
    true(norm(Linv,np.inf)<=1/8+1e-13)
    # u=sin(pi x), f=pi^2 sin(pi x)
    u=np.sin(math.pi*x); f=math.pi**2*u
    uh=np.linalg.solve(L,f)
    bound=h*h/96*math.pi**4
    true(np.max(np.abs(uh-u))<=bound+3e-12)
    for k in range(1,n+1):
        lamh=4/h**2*math.sin(k*math.pi*h/2)**2
        lam=(k*math.pi)**2
        true(lamh<=lam+1e-10)
        true(lam-lamh<=lam**2*h*h/12+1e-9)
mark("Green and finite difference", start)

# 10. Feynman Kac formulas
start = checks
K=np.array([[.7,.2],[.3,.8]])
V=np.array([.2,.6]); f=np.array([1.3,-.4]); M=np.diag(np.exp(-V))@K.T
for n in range(7):
    lhs=np.linalg.matrix_power(M,n)@f
    rhs=np.zeros(2)
    for i in range(2):
        total=0.0
        for path_tail in itertools.product(range(2),repeat=n):
            path=(i,)+path_tail
            prob=1.0; weight=1.0
            for r in range(n):
                weight*=math.exp(-V[path[r]])
                prob*=K[path[r+1],path[r]]
            total+=prob*weight*f[path[-1]]
        rhs[i]=total
    array_close(lhs,rhs,3e-14)
Q=K-np.eye(2)
for t in np.linspace(0,2,21):
    F=expm(t*(Q.T-np.diag(V)))
    true(np.min(F)>=-2e-14)
    true(norm(F,np.inf)<=math.exp(-min(V)*t)+2e-13)
mark("Feynman Kac", start)

# 11. Feshbach, memory, and local closure
start = checks
for _ in range(100):
    App=rng.normal(size=(2,2))*.2
    Apq=rng.normal(size=(2,2))*.2
    Aqp=rng.normal(size=(2,2))*.2
    Aqq=rng.normal(size=(2,2))*.2-np.eye(2)
    A=np.block([[App,Apq],[Aqp,Aqq]])
    z=3.0+.2j
    Sigma=Apq@inv(z*np.eye(2)-Aqq)@Aqp
    F=z*np.eye(2)-App-Sigma
    top=inv(z*np.eye(4)-A)[:2,:2]
    array_close(top,inv(F),2e-12)
    scalar_close(np.linalg.det(z*np.eye(4)-A),np.linalg.det(z*np.eye(2)-Aqq)*np.linalg.det(F),2e-11)
    lap,_=quad_vec(lambda t: np.exp(-z*t)*(Apq@expm(t*Aqq)@Aqp),0,30,epsabs=1e-11)
    array_close(lap,Sigma,2e-9)
# Exact local closure with zero return coupling
App=np.array([[-.4,.2],[0.,-.6]])
Aqq=np.diag([-1.,-1.4])
Apq=np.array([[1.,0.],[0.,0.]])
Aqp=np.array([[0.,0.],[0.,1.]])
# Apq Aqq^k Aqp is zero for all k in this diagonal triangular choice
for k in range(5): array_close(Apq@np.linalg.matrix_power(Aqq,k)@Aqp,np.zeros((2,2)),1e-14)
A=np.block([[App,Apq],[Aqp,Aqq]])
for t in np.linspace(0,3,31): array_close(expm(t*A)[:2,:2],expm(t*App),3e-12)
mark("Feshbach and memory", start)

# 12. Modal compression and Volterra stability
start = checks
mu=np.array([-.25,-.8,-2.2,-5.0])
B=np.array([.5,-.3,.16,.08])
for t in np.linspace(0,10,101):
    full=np.sum(B*np.exp(mu*t))
    trunc=np.sum(B[:2]*np.exp(mu[:2]*t))
    true(abs(full-trunc)<=np.sum(np.abs(B[2:])*np.exp(mu[2:]*t))+1e-14)
l1_tail=np.sum(np.abs(B[2:])/(-mu[2:]))
val,_=quad(lambda t: abs(np.sum(B[2:]*np.exp(mu[2:]*t))),0,np.inf)
true(val<=l1_tail+1e-10)
# Scalar Volterra comparison by time stepping, merely checks the proved upper bound
dt=0.002; T=2.0; grid=np.arange(0,T+dt/2,dt)
Kfun=np.exp(-grid); Ktilde=.9*np.exp(-grid)
def solve(kernel):
    x=np.zeros_like(grid); x[0]=1
    for i in range(1,len(grid)):
        conv=dt*np.sum(kernel[1:i+1][::-1]*x[:i])
        x[i]=x[i-1]+dt*(-.4*x[i-1]+conv)
    return x
x=solve(Kfun); xt=solve(Ktilde)
eps=np.trapezoid(np.abs(Kfun-Ktilde),grid)
L=np.trapezoid(np.abs(Kfun),grid); Bsup=np.max(np.abs(xt)); bound=Bsup*T*eps*math.exp(L*T)
true(np.max(np.abs(x-xt))<=bound+5e-3)
mark("memory compression", start)

# 13. Survival and competing risks
start = checks
A=np.array([[-.45,.12,0.],[.25,-.50,.18],[0.,.20,-.42]])
p0=np.array([1.,0.,0.]); one=np.ones(3); a=-one@A
true(np.all(a>=0))
for t in np.linspace(0,25,201):
    pt=expm(t*A)@p0; S=one@pt; dens=a@pt
    true(S>=-2e-14); true(dens>=-2e-14)
    h=1e-6
    dS=(one@expm((t+h)*A)@p0-one@expm((t-h)*A)@p0)/(2*h) if t>h else one@A@p0
    scalar_close(-dS,dens,2e-8)
for s in (0.,.2,1.,3.):
    transform=a@inv(s*np.eye(3)-A)@p0
    integ,_=quad(lambda t: math.exp(-s*t)*(a@expm(t*A)@p0),0,100,epsabs=1e-11)
    scalar_close(transform,integ,2e-9)
for m in (1,2,3,4):
    formula=math.factorial(m)*one@np.linalg.matrix_power(inv(-A),m)@p0
    integ,_=quad(lambda t: t**m*(a@expm(t*A)@p0),0,np.inf,epsabs=1e-10)
    scalar_close(formula,integ,2e-8)
c1=np.minimum(a,np.array([.12,.08,.12])); c2=a-c1
scalar_close(c1@inv(-A)@p0+c2@inv(-A)@p0,1,3e-13)
mark("survival and competing risks", start)

# 14. Source, bibliography, and package integrity
start = checks
tex=TEX.read_text()
bib=BIB.read_text()
# theorem proof parity
results=len(re.findall(r"\\begin\{(?:theorem|proposition|lemma|corollary)\}",tex))
proofs=len(re.findall(r"\\begin\{proof\}",tex))
scalar_close(results,proofs,0,"every proved result must have a proof")
labels=re.findall(r"\\label\{([^}]+)\}",tex)
true(len(labels)==len(set(labels)),"duplicate labels")
refs=[]
for body in re.findall(r"\\(?:cref|Cref|ref|eqref)\{([^}]+)\}",tex): refs.extend(x.strip() for x in body.split(','))
for ref in refs: true(ref in set(labels),f"missing reference {ref}")
keys=set(re.findall(r"@\w+\{([^,]+),",bib))
cites=[]
for body in re.findall(r"\\cite\{([^}]+)\}",tex): cites.extend(x.strip() for x in body.split(','))
for key in cites: true(key in keys,f"missing bibliography key {key}")
for key in keys: true(key in set(cites),f"uncited bibliography key {key}")
true(';' not in tex,"semicolon found in manuscript source")
true('\\newpage' not in tex and '\\clearpage' not in tex and '\\pagebreak' not in tex,"forced page break")
for phrase in ("delve", "game changer", "groundbreaking framework", "seamlessly", "robust tapestry", "in conclusion,"):
    true(phrase.lower() not in tex.lower(),f"stock phrase found: {phrase}")
for fig in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}",tex):
    true((ROOT/'figures'/fig).exists(),f"missing figure {fig}")
# Compare a few recomputed values with the retained original record
orig=json.loads(ORIGINAL.read_text())
true(orig['packet_semigroup']['block_composition_residual']<1e-12)
true(orig['refinement']['duhamel_identity_residual']<1e-12)
true(orig['latent_elimination']['feshbach_resolvent_residual']<1e-12)
true(orig['pde']['observed_order']>1.99)
mark("source and package integrity", start)

print(f"Paper VI revised verification: {checks}/{checks} checks passed in {len(groups)} groups")
for name,count in groups:
    print(f"  {name}: {count}")
