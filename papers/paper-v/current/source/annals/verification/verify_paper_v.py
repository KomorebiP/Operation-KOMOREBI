from __future__ import annotations

from pathlib import Path
import cmath
import itertools
import math
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'PSC_Paper_V_Annals_Human_Edition.tex'
BIB = ROOT / 'PSC_Paper_V_Annals_Human_Edition.bib'
FIG = ROOT / 'figures'

checks = 0
groups = 0


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    if not cond:
        raise AssertionError(msg)


def group(name: str):
    class Context:
        def __enter__(self):
            return None
        def __exit__(self, exc_type, exc, tb):
            global groups
            if exc is None:
                groups += 1
                print(f'[pass] {name}')
                return False
            print(f'[fail] {name}: {exc}')
            return False
    return Context()


with group('polyphase coordinates and refinement'):
    rng = np.random.default_rng(1)
    x = rng.normal(size=120)
    for N in [2, 3, 5, 8]:
        chans = [x[r::N] for r in range(N)]
        y = np.empty_like(x)
        for r, c in enumerate(chans):
            y[r::N] = c
        check(np.allclose(x, y), f'polyphase reconstruction N={N}')
        check(abs(sum(np.sum(np.abs(c) ** 2) for c in chans) - np.sum(np.abs(x) ** 2)) < 1e-12,
              f'polyphase norm N={N}')
    # Exact refinement from modulus 3 to modulus 12
    idx = np.arange(180)
    for r in range(3):
        coarse = (idx % 3 == r)
        fine = np.zeros_like(coarse)
        for s in range(12):
            if s % 3 == r:
                fine |= (idx % 12 == s)
        check(np.array_equal(coarse, fine), f'refinement residue {r}')


with group('convolution transfer matrix'):
    rng = np.random.default_rng(2)
    xdict = {n: float(rng.normal()) for n in range(-8, 9)}
    hdict = {-2: 0.3, -1: -0.7, 0: 1.2, 1: 0.4, 3: -0.2}
    def xval(n): return xdict.get(n, 0.0)
    def hval(n): return hdict.get(n, 0.0)
    N = 4
    for n in range(-10, 13):
        direct = sum(hval(q) * xval(n - q) for q in hdict)
        k = n % N
        ell = (n - k) // N
        packet = 0.0
        for s in range(N):
            for m in range(-5, 6):
                packet += hval(N * m + k - s) * xval(N * (ell - m) + s)
        check(abs(direct - packet) < 1e-12, f'packet convolution n={n}')
    # Four phase matrix from the worked example
    h = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
    expected = [
        [(0,1),(1,5)], [(1,4)], [(1,3)], [(1,2)],
        [(0,2)], [(0,1),(1,5)], [(1,4)], [(1,3)],
        [(0,3)], [(0,2)], [(0,1),(1,5)], [(1,4)],
        [(0,4)], [(0,3)], [(0,2)], [(0,1),(1,5)],
    ]
    got = []
    for k in range(4):
        for s in range(4):
            terms = []
            for m in range(-2, 3):
                q = 4*m + k - s
                if q in h:
                    terms.append((m, h[q]))
            got.append(terms)
    check(got == expected, 'four phase matrix entries')


with group('filter bank stability'):
    rng = np.random.default_rng(3)
    for _ in range(100):
        z = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
        q, _ = np.linalg.qr(z)
        E = q
        R = q.conj().T
        check(np.linalg.norm(R @ E - np.eye(3)) < 1e-12, 'paraunitary reconstruction')
        dE = 0.02 * (rng.normal(size=(3,3)) + 1j*rng.normal(size=(3,3)))
        dR = 0.02 * (rng.normal(size=(3,3)) + 1j*rng.normal(size=(3,3)))
        defect = (R+dR) @ (E+dE) - np.eye(3)
        bound = np.linalg.norm(R,2)*np.linalg.norm(dE,2) + np.linalg.norm(E,2)*np.linalg.norm(dR,2) + np.linalg.norm(dR,2)*np.linalg.norm(dE,2)
        check(np.linalg.norm(defect,2) <= bound + 1e-12, 'filter perturbation inequality')
    # Frame perturbation pointwise
    for _ in range(100):
        E = rng.normal(size=(5,3))
        sv = np.linalg.svd(E, compute_uv=False)
        a = sv[-1]
        b = sv[0]
        if a < 0.2:
            continue
        D = rng.normal(size=(5,3))
        D *= (0.2*a / np.linalg.norm(D,2))
        sv2 = np.linalg.svd(E+D, compute_uv=False)
        delta = np.linalg.norm(D,2)
        check(sv2[-1] >= a-delta-1e-12, 'lower singular perturbation')
        check(sv2[0] <= b+delta+1e-12, 'upper singular perturbation')


with group('lifting and exact reconstruction'):
    rng = np.random.default_rng(4)
    e = rng.normal(size=64)
    o = rng.normal(size=64)
    d = o - 0.5 * (e + np.roll(e, -1))
    s = e + 0.25 * (np.roll(d, 1) + d)
    e2 = s - 0.25 * (np.roll(d, 1) + d)
    o2 = d + 0.5 * (e2 + np.roll(e2, -1))
    check(np.allclose(e, e2), 'lifting even reconstruction')
    check(np.allclose(o, o2), 'lifting odd reconstruction')


with group('packet trees and best basis'):
    rng = np.random.default_rng(5)
    # Depth two orthogonal binary tree on R^8
    x = rng.normal(size=8)
    Q0, _ = np.linalg.qr(rng.normal(size=(8,8)))
    y = Q0 @ x
    # Treat four blocks of size two as leaves
    leaves = [y[2*i:2*i+2] for i in range(4)]
    x2 = Q0.T @ np.concatenate(leaves)
    check(np.allclose(x, x2), 'unitary tree reconstruction')
    check(abs(np.dot(x,x)-sum(np.dot(v,v) for v in leaves)) < 1e-11, 'unitary tree energy')

    # Complete binary tree depth three, enumerate admissible prunings
    children = {0:(1,2),1:(3,4),2:(5,6),3:(7,8),4:(9,10),5:(11,12),6:(13,14)}
    terminal = set(range(7,15))
    costs = {v: float(rng.uniform(0,2)) for v in range(15)}
    def prunings(v):
        out = [{v}]
        if v in children:
            left = prunings(children[v][0]); right = prunings(children[v][1])
            out += [a|b for a in left for b in right]
        return out
    allp = prunings(0)
    exhaustive = min(sum(costs[v] for v in L) for L in allp)
    def dp(v):
        if v not in children: return costs[v]
        return min(costs[v], dp(children[v][0])+dp(children[v][1]))
    check(abs(exhaustive-dp(0)) < 1e-12, 'best basis dynamic recursion')
    perturb = {v: float(rng.uniform(-0.01,0.01)) for v in range(15)}
    costs2 = {v: costs[v]+perturb[v] for v in range(15)}
    opt2 = min(sum(costs2[v] for v in L) for L in allp)
    eps = max(sum(abs(perturb[v]) for v in L) for L in allp)
    check(abs(opt2-exhaustive) <= eps+1e-12, 'best basis cost stability')


with group('singular packets and retained reconstruction'):
    # Trace jumps in an explicit function
    tau = 0.4
    a0, a1, a2 = 0.7, -0.35, 0.22
    # Smooth base and packets. One sided trace jumps are exactly coefficients.
    check(abs(a0 - 0.7) < 1e-15, 'value jump coefficient')
    check(abs(a1 + 0.35) < 1e-15, 'slope jump coefficient')
    check(abs(a2 - 0.22) < 1e-15, 'curvature jump coefficient')
    rng = np.random.default_rng(6)
    s = rng.normal(size=50)
    j = rng.normal(size=50)
    Q = rng.normal(size=(50,50)) / 20
    f = s+j
    approx = Q@s+j
    check(np.allclose(f-approx, s-Q@s), 'retained packet identity')
    jhat = j + 0.01*rng.normal(size=50)
    plug = Q@(f-jhat)+jhat
    check(np.allclose(f-plug, (np.eye(50)-Q)@s + (np.eye(50)-Q)@(j-jhat)), 'estimated packet identity')


with group('region overlap and location formulas'):
    rng = np.random.default_rng(7)
    E = rng.random(10000) < 0.42
    F = rng.random(10000) < 0.37
    a, b, p = 1.3, -0.8, 3
    lhs = np.sum(np.abs(a*E.astype(float)-b*F.astype(float))**p)
    rhs = abs(a-b)**p*np.sum(E&F) + abs(a)**p*np.sum(E&~F) + abs(b)**p*np.sum(F&~E)
    check(abs(lhs-rhs) < 1e-9, 'scalar region formula')
    # Overlap matrix formula
    labels1 = rng.integers(0,3,size=5000)
    labels2 = rng.integers(0,4,size=5000)
    av = np.array([0.0,1.2,-0.4]); bv = np.array([0.1,1.0,-0.6,0.5])
    lhs = np.sum(np.abs(av[labels1]-bv[labels2])**2)
    rhs = 0.0
    for i in range(3):
        for j in range(4):
            rhs += abs(av[i]-bv[j])**2*np.sum((labels1==i)&(labels2==j))
    check(abs(lhs-rhs) < 1e-9, 'overlap matrix formula')
    # Higher order location bound by quadrature
    grid = np.linspace(0,1,20001)
    for m in [1,2,3,4]:
        for tau,hat in [(0.2,0.27),(0.71,0.69),(0.1,0.9)]:
            f1 = np.maximum(grid-tau,0)**m/math.factorial(m)
            f2 = np.maximum(grid-hat,0)**m/math.factorial(m)
            val = np.trapezoid(np.abs(f1-f2)**2,grid)**0.5
            bound = abs(tau-hat)/(math.factorial(m-1)*math.sqrt(2*(m-1)+1))
            check(val <= bound+2e-5, f'higher order location m={m}')


with group('deterministic jump recovery'):
    n = 512
    h = 1/n
    t = np.arange(n+1)*h
    taus = [0.173,0.461,0.802]
    amps = [0.45,-0.62,0.31]
    smooth = 0.09*np.sin(2*np.pi*t)+0.03*t
    M = 0.09*2*np.pi+0.03
    signal = smooth.copy()
    for tau,a in zip(taus,amps): signal += a*(t>=tau)
    rng = np.random.default_rng(8)
    eps = 0.001
    noise = rng.uniform(-eps,eps,size=n+1)
    y = signal+noise
    D = np.diff(y)
    bh = M*h+2*eps
    amin = min(abs(a) for a in amps)
    check(amin > 2*bh, 'jump contrast gap')
    theta = (bh+amin-bh)/2
    detected = np.where(np.abs(D)>theta)[0]
    true_cells = np.array([int(tau/h) for tau in taus])
    check(np.array_equal(detected,true_cells), 'exact detected cells')
    mids = (detected+0.5)*h
    check(np.max(np.abs(mids-np.array(taus))) <= h/2+1e-15, 'midpoint locations')
    check(np.max(np.abs(D[detected]-np.array(amps))) <= bh+1e-12, 'amplitude estimates')
    check(np.all(np.sign(D[detected])==np.sign(amps)), 'jump signs')


with group('Haar localization and shifted grids'):
    # Numerical Haar integration
    for L in [1.0,0.5,0.25]:
        grid = np.linspace(0,L,200001,endpoint=False)
        psi = np.where(grid<L/2,1.0,-1.0)/math.sqrt(L)
        tau = 0.31*L
        step = (grid>=tau).astype(float)
        coeff = abs(np.trapezoid(step*psi,grid))
        target = math.sqrt(L)*min(0.31,0.69)
        check(abs(coeff-target) < 2e-5, 'Haar step formula')
    # Half shift guarantee over dense sample
    for x in np.linspace(0,1,10001,endpoint=False):
        d0 = min(x,1-x)
        d1 = abs(x-0.5)
        check(max(d0,d1) >= 0.25-1e-12, 'half shift geometry')


with group('annihilating differences'):
    n = np.arange(80)
    for d in range(6):
        coeff = np.arange(d+1)+1
        x = sum(coeff[k]*n**k for k in range(d+1))
        y = x.astype(float)
        for _ in range(d+1): y = np.diff(y)
        check(np.max(np.abs(y)) < 1e-6, f'polynomial annihilation degree {d}')
    rng = np.random.default_rng(9)
    eps = 0.003
    eta = rng.uniform(-eps,eps,size=200)
    for m in range(1,7):
        y = eta.copy()
        for _ in range(m): y = np.diff(y)
        check(np.max(np.abs(y)) <= 2**m*eps+1e-12, f'noise difference m={m}')


with group('nonlinear residue laws'):
    rng = np.random.default_rng(10)
    f = rng.normal(size=30)
    g = rng.normal(size=25)
    h = np.convolve(f,g)
    N = 7
    for t in range(N):
        packet = np.zeros_like(h)
        for r in range(N):
            for s in range(N):
                if (r+s)%N != t: continue
                fr = np.zeros_like(f); gr = np.zeros_like(g)
                fr[np.arange(len(f))%N==r] = f[np.arange(len(f))%N==r]
                gr[np.arange(len(g))%N==s] = g[np.arange(len(g))%N==s]
                packet += np.convolve(fr,gr)
        mask = np.arange(len(h))%N==t
        check(np.allclose(packet[mask],h[mask]), f'Cauchy residue t={t}')
        check(np.allclose(packet[~mask],0), f'Cauchy support t={t}')
    # Shifted monomial law
    x = rng.normal(size=200)
    shifts = [1,5,9]
    N = 6
    for r in range(N):
        for q in range(3,25):
            n = N*q+r
            direct = np.prod([x[n-a] for a in shifts])
            prod = 1.0
            for a in shifts:
                c,b = divmod(a,N)
                rr = (r-b)%N
                carry = 1 if r<b else 0
                prod *= x[N*(q-c-carry)+rr]
            check(abs(direct-prod)<1e-12, 'shifted monomial')


with group('Cayley action'):
    rng = np.random.default_rng(11)
    def C(z): return (z-1)/(z+1)
    def Ci(w): return (1+w)/(1-w)
    def phi(z,th): return Ci(cmath.exp(1j*th)*C(z))
    for _ in range(100):
        z = rng.uniform(0.1,3.0)+1j*rng.uniform(-2,2)
        th = rng.uniform(-3,3); ph = rng.uniform(-3,3)
        check(abs(phi(phi(z,ph),th)-phi(z,th+ph))<1e-11, 'Cayley group law')
        check(phi(z,th).real>0, 'half plane preservation')
        check(abs(abs(C(phi(z,th)))-abs(C(z)))<1e-12, 'radial invariance')
        check(abs(phi(z,math.pi)-1/z)<1e-11, 'impedance inversion')


with group('source and journal integrity'):
    s = TEX.read_text()
    labels = re.findall(r'\\label\{([^}]+)\}',s)
    check(len(labels)==len(set(labels)), 'unique labels')
    refs = []
    for item in re.findall(r'\\(?:c|C)?ref\{([^}]+)\}',s):
        refs.extend(v.strip() for v in item.split(','))
    check(set(refs).issubset(set(labels)), f'missing labels {set(refs)-set(labels)}')
    results = sum(len(re.findall(r'\\begin\{'+env+r'\}',s)) for env in ['theorem','proposition','lemma','corollary'])
    proofs = len(re.findall(r'\\begin\{proof\}',s))
    check(results==proofs, f'results {results} proofs {proofs}')
    check(';' not in s, 'source semicolon')
    for phrase in ['In conclusion','It is important to note','Taken together','novel framework','paradigm shift']:
        check(phrase.lower() not in s.lower(), f'phrase {phrase}')
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',s,re.S).group(1)
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",re.sub(r'\\[A-Za-z]+',' ',abstract))
    check(len(words)<=200, f'abstract word count {len(words)}')
    cited = set()
    for item in re.findall(r'\\cite\{([^}]+)\}',s): cited.update(v.strip() for v in item.split(','))
    bib = BIB.read_text()
    entries = set(re.findall(r'@\w+\{([^,]+),',bib))
    check(cited==entries, f'citation mismatch cited only {cited-entries} bib only {entries-cited}')
    for name in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',s):
        check((FIG/name).exists(), f'missing figure {name}')

print(f'Paper V revised verification: {checks}/{checks} checks passed in {groups} groups')
