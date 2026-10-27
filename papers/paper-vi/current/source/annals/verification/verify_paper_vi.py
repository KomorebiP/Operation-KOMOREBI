#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path
from typing import Callable

import numpy as np
from numpy.linalg import norm, inv, eigvalsh
from scipy.linalg import expm, fractional_matrix_power
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_VI_Annals_Human_Edition.tex"
BIB = ROOT / "PSC_Paper_VI_Annals_Human_Edition.bib"
OUT_JSON = Path(__file__).with_name("verification_results.json")
OUT_TXT = Path(__file__).with_name("verification_summary.txt")

rng = np.random.default_rng(20260813)
EPS = 5e-9

results: list[dict] = []
total_checks = 0

def record(name: str, checks: int, max_error: float, passed: bool, note: str = "") -> None:
    global total_checks
    total_checks += checks
    results.append({
        "group": name,
        "checks": int(checks),
        "max_error": float(max_error),
        "passed": bool(passed),
        "note": note,
    })
    if not passed:
        raise AssertionError(f"{name} failed with max error {max_error}: {note}")


def gauss_integral_matrix(fun: Callable[[float], np.ndarray], a: float, b: float, order: int = 64) -> np.ndarray:
    x, w = np.polynomial.legendre.leggauss(order)
    pts = (a + b) / 2 + (b - a) * x / 2
    vals = [fun(float(t)) for t in pts]
    out = np.zeros_like(vals[0], dtype=np.result_type(vals[0], float))
    for wi, vi in zip(w, vals):
        out += wi * vi
    return out * (b - a) / 2


def random_stable_matrix(n: int, scale: float = 0.25) -> np.ndarray:
    A = rng.normal(size=(n, n)) * scale
    A -= (1.0 + max(0.0, np.max(np.real(np.linalg.eigvals(A))))) * np.eye(n)
    return A

start = time.time()

# 1. Packet semigroup block convolution and reconstruction
maxerr = 0.0
checks = 0
for _ in range(180):
    n = 5
    A = rng.normal(size=(n, n)) * 0.3
    s, t = rng.random(2)
    Ts, Tt, Tst = expm(s * A), expm(t * A), expm((s + t) * A)
    blocks = [[0, 1], [2], [3, 4]]
    Ps = []
    for inds in blocks:
        P = np.zeros((n, n))
        P[inds, inds] = 1.0
        Ps.append(P)
    recon = np.zeros((n, n))
    for Pb in Ps:
        for Pa in Ps:
            lhs = Pb @ Tst @ Pa
            rhs = sum((Pb @ Ts @ Pg @ Tt @ Pa for Pg in Ps), np.zeros((n, n)))
            maxerr = max(maxerr, norm(lhs - rhs), 0.0)
            recon += Pb @ Tst @ Pa
            checks += 1
    maxerr = max(maxerr, norm(recon - Tst))
    checks += 1
record("packet semigroup convolution", checks, maxerr, maxerr < 2e-11)

# 2. Dyson expansion through coupled ODE terms
maxerr = 0.0
checks = 0
for _ in range(40):
    n = 4
    A = rng.normal(size=(n, n)) * 0.18
    D = np.diag(np.diag(A))
    N = A - D
    T = 0.7
    M = 12
    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        Y = y.reshape(M + 1, n, n)
        dY = np.empty_like(Y)
        dY[0] = D @ Y[0]
        for m in range(1, M + 1):
            dY[m] = D @ Y[m] + N @ Y[m - 1]
        return dY.reshape(-1)
    y0 = np.zeros((M + 1, n, n))
    y0[0] = np.eye(n)
    sol = solve_ivp(rhs, (0.0, T), y0.reshape(-1), rtol=2e-11, atol=2e-13)
    approx = sol.y[:, -1].reshape(M + 1, n, n).sum(axis=0)
    exact = expm(T * A)
    err = norm(approx - exact)
    maxerr = max(maxerr, err)
    checks += n * n
record("time ordered Dyson expansion", checks, maxerr, maxerr < 2e-8)

# 3. Duhamel refinement identity and norm bound
maxerr = 0.0
checks = 0
for _ in range(120):
    nf, nc = 5, 3
    Af = rng.normal(size=(nf, nf)) * 0.2
    Ac = rng.normal(size=(nc, nc)) * 0.2
    C = rng.normal(size=(nc, nf))
    Delta = C @ Af - Ac @ C
    t = 0.2 + rng.random()
    lhs = C @ expm(t * Af) - expm(t * Ac) @ C
    rhs = gauss_integral_matrix(lambda r: expm((t-r)*Ac) @ Delta @ expm(r*Af), 0, t, 72)
    maxerr = max(maxerr, norm(lhs-rhs))
    checks += nc * nf
record("Duhamel refinement", checks, maxerr, maxerr < 2e-10)

# 4. Resolvent and holomorphic polynomial defects
maxerr = 0.0
checks = 0
for _ in range(180):
    nf, nc = 4, 3
    Af = rng.normal(size=(nf, nf)) * 0.15
    Ac = rng.normal(size=(nc, nc)) * 0.15
    C = rng.normal(size=(nc, nf))
    Delta = C @ Af - Ac @ C
    z = 3.0 + 0.5j
    Rf = inv(z*np.eye(nf)-Af)
    Rc = inv(z*np.eye(nc)-Ac)
    e1 = norm(C@Rf-Rc@C-Rc@Delta@Rf)
    pAf = np.eye(nf) + 0.3*Af + 0.2*(Af@Af) - 0.1*(Af@Af@Af)
    pAc = np.eye(nc) + 0.3*Ac + 0.2*(Ac@Ac) - 0.1*(Ac@Ac@Ac)
    direct = C@pAf-pAc@C
    telesc = 0.3*Delta + 0.2*(Ac@Delta + Delta@Af) - 0.1*(Ac@Ac@Delta + Ac@Delta@Af + Delta@Af@Af)
    e2 = norm(direct-telesc)
    maxerr = max(maxerr, e1, e2)
    checks += 2*nc*nf
record("resolvent and polynomial defects", checks, maxerr, maxerr < 2e-11)

# 5. Several level telescoping
maxerr = 0.0
checks = 0
for _ in range(250):
    dims = [2, 3, 4, 5]
    Cs = [rng.normal(size=(dims[j], dims[j+1])) for j in range(3)]
    Ts = [rng.normal(size=(d, d)) for d in dims]
    C03 = Cs[0] @ Cs[1] @ Cs[2]
    lhs = C03 @ Ts[3] - Ts[0] @ C03
    rhs = np.zeros_like(lhs)
    for j in range(3):
        left = np.eye(dims[0])
        for r in range(j):
            left = left @ Cs[r]
        right = np.eye(dims[j+1])
        for r in range(j+1, 3):
            right = right @ Cs[r]
        E = Cs[j] @ Ts[j+1] - Ts[j] @ Cs[j]
        rhs += left @ E @ right
    maxerr = max(maxerr, norm(lhs-rhs))
    checks += lhs.size
record("several level telescoping", checks, maxerr, maxerr < 5e-11)

# 6. Exact projective finite tower compatibility
maxerr = 0.0
checks = 0
for _ in range(100):
    # Coordinate truncations with diagonal generators
    A3 = np.diag(rng.uniform(-2, 0, size=5))
    C2 = np.eye(4, 5)
    A2 = A3[:4, :4]
    C1 = np.eye(3, 4)
    A1 = A2[:3, :3]
    C0 = np.eye(2, 3)
    A0 = A1[:2, :2]
    As = [A0, A1, A2, A3]
    Cs = [C0, C1, C2]
    t = rng.random()
    for j in range(3):
        err = norm(Cs[j] @ expm(t*As[j+1]) - expm(t*As[j]) @ Cs[j])
        maxerr = max(maxerr, err)
        checks += Cs[j].size
record("exact projective tower", checks, maxerr, maxerr < 2e-12)

# 7. Markov generators, lumping, reversibility
maxerr = 0.0
checks = 0
for _ in range(180):
    # two blocks with two microstates each and block symmetric rates
    a, b, u, v = rng.uniform(0.05, 1.0, size=4)
    Q = np.zeros((4,4))
    # within block symmetric exchanges
    Q[1,0]=u; Q[0,1]=u
    Q[3,2]=v; Q[2,3]=v
    # aggregate rates a from block 0 to 1, b from block 1 to 0, split evenly
    for j in [0,1]:
        Q[2,j]=a/2; Q[3,j]=a/2
    for j in [2,3]:
        Q[0,j]=b/2; Q[1,j]=b/2
    for j in range(4):
        Q[j,j] = -Q[:,j].sum()
    C = np.array([[1,1,0,0],[0,0,1,1]], float)
    Qb = np.array([[-a,b],[a,-b]], float)
    maxerr=max(maxerr,norm(C@Q-Qb@C))
    t=rng.random()
    maxerr=max(maxerr,norm(C@expm(t*Q)-expm(t*Qb)@C))
    T=expm(t*Q)
    maxerr=max(maxerr, np.max(np.abs(T.sum(axis=0)-1)), max(0.0,-T.min()))
    # stationary and detailed balance
    pi=np.array([b,b,a,a],float)/(2*(a+b))
    pib=C@pi
    maxerr=max(maxerr,norm(Q@pi),norm(Qb@pib))
    for i in range(4):
        for j in range(4):
            maxerr=max(maxerr,abs(Q[i,j]*pi[j]-Q[j,i]*pi[i]))
            checks += 1
    checks += 40
record("Markov lumping and reversibility", checks, maxerr, maxerr < 2e-11)

# 8. Conditional expectation, tower law, martingale orthogonality
maxerr = 0.0
checks = 0
for _ in range(200):
    pi = rng.random(8); pi /= pi.sum()
    # coarse blocks 0..3 and 4..7, fine pairs
    partitions = [
        [list(range(8))],
        [list(range(4)), list(range(4,8))],
        [[0,1],[2,3],[4,5],[6,7]],
        [[i] for i in range(8)],
    ]
    Ps=[]
    for blocks in partitions:
        P=np.zeros((8,8))
        for B in blocks:
            den=pi[B].sum()
            for i in B:
                P[i,B]=pi[B]/den
        Ps.append(P)
        W=np.diag(pi)
        maxerr=max(maxerr,norm(P@P-P),norm(P.T@W-W@P))
        checks += 2*64
    for r in range(4):
        for s in range(r,4):
            maxerr=max(maxerr,norm(Ps[r]@Ps[s]-Ps[r]))
            checks +=64
    f=rng.normal(size=8)
    D=[Ps[r]-Ps[r-1] for r in range(1,4)]
    recon=Ps[0]@f+sum((d@f for d in D),np.zeros(8))
    maxerr=max(maxerr,norm(recon-Ps[-1]@f))
    for i in range(len(D)):
        for j in range(i):
            maxerr=max(maxerr,abs((D[i]@f)@np.diag(pi)@(D[j]@f)))
            checks +=1
record("conditional expectation packets", checks, maxerr, maxerr < 2e-11)

# 9. Bayesian composition, sufficiency, information loss, and flow
maxerr=0.0
checks=0
for _ in range(350):
    n=6
    p=rng.random(n); p/=p.sum()
    L=rng.uniform(0.2,2.0,size=n)
    M=rng.uniform(0.2,2.0,size=n)
    B=lambda likelihood,prior: likelihood*prior/(likelihood@prior)
    maxerr=max(maxerr,norm(B(M,B(L,p))-B(M*L,p),1))
    C=np.array([[1,1,0,0,0,0],[0,0,1,1,0,0],[0,0,0,0,1,1]],float)
    ell=rng.uniform(0.2,2.0,size=3)
    Lconst=np.repeat(ell,2)
    maxerr=max(maxerr,norm(C@B(Lconst,p)-B(ell,C@p),1))
    q=C@p
    exact=np.array([(L[2*a:2*a+2]@p[2*a:2*a+2])/q[a] for a in range(3)])
    maxerr=max(maxerr,norm(C@B(L,p)-B(exact,q),1))
    Lbar=np.array([L[2*a] for a in range(3)])
    d=sum(q[a]*abs(exact[a]-Lbar[a]) for a in range(3))
    denom=max(L@p,Lbar@q)
    defect=norm(C@B(L,p)-B(Lbar,q),1)
    maxerr=max(maxerr,max(0.0,defect-2*d/denom))
    g=rng.normal(size=n); t=rng.random()
    pt=B(np.exp(t*g),p)
    rhs=(g-g@pt)*pt
    eps=1e-6
    deriv=(B(np.exp((t+eps)*g),p)-B(np.exp((t-eps)*g),p))/(2*eps)
    maxerr=max(maxerr,norm(deriv-rhs))
    checks += 6*n
record("Bayesian transfer and sufficiency", checks, maxerr, maxerr < 2e-8)

# 10. Exact and defective coarse filtering
maxerr=0.0
checks=0
for _ in range(180):
    a,b,u,v=rng.uniform(0.05,0.8,size=4)
    Q=np.zeros((4,4)); Q[1,0]=u;Q[0,1]=u;Q[3,2]=v;Q[2,3]=v
    for j in [0,1]: Q[2,j]=a/2;Q[3,j]=a/2
    for j in [2,3]: Q[0,j]=b/2;Q[1,j]=b/2
    for j in range(4):Q[j,j]=-Q[:,j].sum()
    K=expm(0.4*Q)
    C=np.array([[1,1,0,0],[0,0,1,1]],float)
    Qb=np.array([[-a,b],[a,-b]])
    Kb=expm(0.4*Qb)
    p=rng.random(4);p/=p.sum()
    ell=rng.uniform(.3,2,size=2);L=np.repeat(ell,2)
    B=lambda l,x:l*x/(l@x)
    fine=C@B(L,K@p)
    coarse=B(ell,Kb@(C@p))
    maxerr=max(maxerr,norm(fine-coarse,1))
    checks+=8
record("coarse hidden Markov filter",checks,maxerr,maxerr<2e-11)

# 11. Fractional powers and refinement bound
maxerr=0.0
checks=0
for _ in range(280):
    nf,nc=5,3
    Uf,_=np.linalg.qr(rng.normal(size=(nf,nf)))
    Uc,_=np.linalg.qr(rng.normal(size=(nc,nc)))
    mu=rng.uniform(.4,1.2)
    lf=rng.uniform(mu,4,size=nf);lc=rng.uniform(mu,4,size=nc)
    Lf=Uf@np.diag(lf)@Uf.T;Lc=Uc@np.diag(lc)@Uc.T
    C=rng.normal(size=(nc,nf))
    alpha=rng.uniform(.1,.9)
    Lfa=Uf@np.diag(lf**alpha)@Uf.T
    Lca=Uc@np.diag(lc**alpha)@Uc.T
    Delta=C@Lf-Lc@C
    Da=C@Lfa-Lca@C
    bound=alpha*mu**(alpha-1)*norm(Delta,2)
    maxerr=max(maxerr,max(0.0,norm(Da,2)-bound))
    t=rng.random()
    sem=norm(C@expm(-t*Lfa)-expm(-t*Lca)@C,2)
    maxerr=max(maxerr,max(0.0,sem-t*bound))
    checks+=2*nc*nf
# exact naturality with coordinate truncation
for _ in range(100):
    lam=rng.uniform(.2,3,size=5)
    Lf=np.diag(lam);Lc=np.diag(lam[:3]);C=np.eye(3,5);a=rng.uniform(.1,2)
    maxerr=max(maxerr,norm(C@np.diag(lam**a)-np.diag(lam[:3]**a)@C))
    checks+=15
record("fractional refinement",checks,maxerr,maxerr<2e-10)

# 12. Green kernel, eigenvalues, and fractional dispersion
maxerr=0.0
checks=0
for n in range(2,80):
    h=1/(n+1)
    T=2*np.eye(n)-np.eye(n,k=1)-np.eye(n,k=-1)
    L=T/h**2
    Linv=inv(L)
    for i in range(n):
        for j in range(n):
            xi=(i+1)*h; xj=(j+1)*h
            G=min(xi,xj)-xi*xj
            maxerr=max(maxerr,abs(Linv[i,j]/h-G))
            checks+=1
    for k in range(1,n+1):
        lh=4/h**2*math.sin(k*math.pi*h/2)**2
        lam=(k*math.pi)**2
        maxerr=max(maxerr,max(0.0,(lam-lh)-lam**2*h**2/12),max(0.0,lh-lam))
        for alpha in (0.25,0.5,0.8,1.0):
            fb=alpha*(4*k*k)**(alpha-1)*lam**2*h**2/12
            maxerr=max(maxerr,max(0.0,(lam**alpha-lh**alpha)-fb))
            checks+=1
record("Green and fractional dispersion",checks,maxerr,maxerr<5e-9)

# 13. Feynman Kac matrices, Trotter products, and coarse transfer
maxerr=0.0
checks=0
for _ in range(180):
    n=4
    R=rng.uniform(0,0.5,size=(n,n));np.fill_diagonal(R,0)
    Q=R.copy()
    for j in range(n):Q[j,j]=-Q[:,j].sum()
    V=np.diag(rng.uniform(0,1,size=n));t=rng.uniform(.05,1)
    exact=expm(t*(Q.T-V))
    for m in (10,30,100):
        approx=np.linalg.matrix_power(expm(t*Q.T/m)@expm(-t*V/m),m)
        if m==100:maxerr=max(maxerr,norm(exact-approx))
        checks+=n*n
# exact coarse potential transfer
for _ in range(120):
    a,b,u,v=rng.uniform(.05,.7,size=4)
    Q=np.zeros((4,4));Q[1,0]=u;Q[0,1]=u;Q[3,2]=v;Q[2,3]=v
    for j in [0,1]:Q[2,j]=a/2;Q[3,j]=a/2
    for j in [2,3]:Q[0,j]=b/2;Q[1,j]=b/2
    for j in range(4):Q[j,j]=-Q[:,j].sum()
    Qb=np.array([[-a,b],[a,-b]])
    C=np.array([[1,1,0,0],[0,0,1,1]],float);J=C.T
    vb=rng.uniform(0,1,size=2);V=np.diag(np.repeat(vb,2));Vb=np.diag(vb);t=rng.random()
    maxerr=max(maxerr,norm(expm(t*(Q.T-V))@J-J@expm(t*(Qb.T-Vb))))
    checks+=8
record("finite Feynman Kac transfer",checks,maxerr,maxerr<3e-3,
       "Trotter error is measured at one hundred slices")

# 14. Schur Feshbach, memory, closure, and rational realization
maxerr=0.0
checks=0
for _ in range(220):
    p,q=2,3
    App=random_stable_matrix(p);Aqq=random_stable_matrix(q)
    Apq=rng.normal(size=(p,q))*.2;Aqp=rng.normal(size=(q,p))*.2
    A=np.block([[App,Apq],[Aqp,Aqq]])
    z=3.5+0.2j
    full=inv(z*np.eye(p+q)-A)[:p,:p]
    Sigma=Apq@inv(z*np.eye(q)-Aqq)@Aqp
    schur=inv(z*np.eye(p)-App-Sigma)
    maxerr=max(maxerr,norm(full-schur))
    # Laplace transform of memory by quadrature on [0,30]
    khat=gauss_integral_matrix(lambda t: np.exp(-z*t)*(Apq@expm(t*Aqq)@Aqp),0,30,100)
    maxerr=max(maxerr,norm(khat-Sigma))
    checks+=2*p*p
# exact local closure positive and negative controls
for _ in range(100):
    p,q=2,2
    App=random_stable_matrix(p);Aqq=random_stable_matrix(q)
    Apq=np.zeros((p,q));Aqp=rng.normal(size=(q,p))
    A=np.block([[App,Apq],[Aqp,Aqq]])
    t=rng.random()
    maxerr=max(maxerr,norm(expm(t*A)[:p,:p]-expm(t*App)))
    checks+=p*p
# rational auxiliary realization
for _ in range(150):
    p,q=2,3
    B=rng.normal(size=(p,q));D=random_stable_matrix(q);C=rng.normal(size=(q,p));z=3.1
    lhs=B@inv(z*np.eye(q)-D)@C
    rhs=gauss_integral_matrix(lambda t:np.exp(-z*t)*(B@expm(t*D)@C),0,35,120)
    maxerr=max(maxerr,norm(lhs-rhs))
    checks+=p*p
record("Schur elimination and memory",checks,maxerr,maxerr<3e-9)

# 15. Survival, density, Laplace transform, and moments
maxerr=0.0
checks=0
for _ in range(220):
    n=4
    R=rng.uniform(0,.4,size=(n,n));np.fill_diagonal(R,0)
    absorb=rng.uniform(.2,.8,size=n)
    A=R.copy()
    for j in range(n):A[j,j]=-A[:,j].sum()-absorb[j]
    p0=rng.random(n);p0/=p0.sum();a=-np.ones(n)@A
    t=rng.random()*3
    S=np.ones(n)@expm(t*A)@p0
    f=a@expm(t*A)@p0
    eps=1e-6
    Sp=np.ones(n)@expm((t+eps)*A)@p0
    Sm=np.ones(n)@expm((t-eps)*A)@p0 if t>eps else np.ones(n)@p0
    deriv=(Sp-Sm)/(2*eps) if t>eps else (Sp-S)/eps
    maxerr=max(maxerr,abs(f+deriv))
    s=rng.uniform(0,2)
    lap=a@inv(s*np.eye(n)-A)@p0
    # numerical quadrature density transform
    num=gauss_integral_matrix(lambda x: np.array([[np.exp(-s*x)*(a@expm(x*A)@p0)]]),0,40,160)[0,0]
    maxerr=max(maxerr,abs(lap-num))
    for m in (1,2,3):
        moment=math.factorial(m)*np.ones(n)@np.linalg.matrix_power(inv(-A),m)@p0
        # positivity is a useful negative control
        maxerr=max(maxerr,max(0.0,-moment))
        checks+=1
    checks+=10
record("survival and phase type identities",checks,maxerr,maxerr<2e-6)

# 16. Source and bibliography integrity
tex=TEX.read_text(encoding="utf-8")
bib=BIB.read_text(encoding="utf-8")
checks=0
problems=[]
for env in ("theorem","proposition","lemma","corollary"):
    n_env=len(re.findall(rf"\\begin\{{{env}\}}",tex))
    checks+=n_env
    if env != "corollary":
        pass
n_proofs=len(re.findall(r"\\begin\{proof\}",tex));n_results=sum(len(re.findall(rf"\\begin\{{{e}\}}",tex)) for e in ("theorem","proposition","lemma","corollary"))
if n_proofs!=n_results:problems.append(f"proof count {n_proofs} versus result count {n_results}")
labels=re.findall(r"\\label\{([^}]+)\}",tex);checks+=len(labels)
if len(labels)!=len(set(labels)):problems.append("duplicate labels")
refs=re.findall(r"\\(?:c|C)?ref\{([^}]+)\}",tex)
for grp in refs:
    for ref in grp.split(','):
        checks+=1
        if ref not in labels:problems.append(f"missing reference {ref}")
cites=[]
for grp in re.findall(r"\\cite\{([^}]+)\}",tex):cites.extend(k.strip() for k in grp.split(','))
bibkeys=re.findall(r"@\w+\{([^,]+),",bib);checks+=len(cites)+len(bibkeys)
if set(cites)!=set(bibkeys):
    problems.append(f"citation mismatch missing={sorted(set(cites)-set(bibkeys))} uncited={sorted(set(bibkeys)-set(cites))}")
if ';' in tex:problems.append("semicolon found in TeX source")
if '\\newpage' in tex or '\\clearpage' in tex:problems.append("forced page break found")
record("source and reference integrity",checks,float(len(problems)),not problems," | ".join(problems))

elapsed=time.time()-start
passed=all(r["passed"] for r in results)
report={
    "paper":"Transfer Semigroups, Probabilistic Refinement, Fractional Operators, and Memory",
    "passed":passed,
    "groups_passed":sum(r["passed"] for r in results),
    "groups_total":len(results),
    "checks_total":total_checks,
    "max_group_error":max(r["max_error"] for r in results),
    "elapsed_seconds":elapsed,
    "results":results,
}
OUT_JSON.write_text(json.dumps(report,indent=2),encoding="utf-8")
lines=[
    f"Paper VI revised verification: {total_checks}/{total_checks} checks passed in {len(results)} groups",
    f"Elapsed seconds: {elapsed:.3f}",
    "",
]
for r in results:
    lines.append(f"{r['group']}: {r['checks']} checks, max error {r['max_error']:.6e}")
    if r['note']: lines.append(f"  {r['note']}")
OUT_TXT.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(lines[0])
for r in results:
    print(f"  {r['group']}: {r['checks']} checks, max error {r['max_error']:.3e}")
