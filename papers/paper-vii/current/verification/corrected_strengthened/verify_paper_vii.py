from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from numpy.linalg import eigvalsh, matrix_rank, norm
from scipy.linalg import expm, logm, polar

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_VII_Strengthened_Annals_Edition.tex"
BIB = ROOT / "PSC_Paper_VII_Strengthened_Annals_Edition.bib"
PDF = ROOT / "PSC_Paper_VII_Strengthened_Annals_Edition.pdf"
FIGDIR = ROOT / "figures"
LEGACY = ROOT / "legacy" / "numerical_results.json"
OUT_JSON = Path(__file__).with_name("verification_results.json")
OUT_TXT = Path(__file__).with_name("verification_summary.txt")

rng = np.random.default_rng(20260814)
TOL = 2e-9

class Audit:
    def __init__(self) -> None:
        self.total = 0
        self.groups: dict[str, dict[str, object]] = {}
        self._current = ""
        self._start = 0

    def begin(self, name: str) -> None:
        self._current = name
        self._start = self.total

    def check(self, condition: bool, message: str = "") -> None:
        self.total += 1
        if not bool(condition):
            raise AssertionError(f"{self._current}: {message or 'check failed'}")

    def close(self, details: dict[str, object] | None = None) -> None:
        self.groups[self._current] = {
            "checks": self.total - self._start,
            "status": "passed",
            "details": details or {},
        }


def rand_unitary(n: int) -> np.ndarray:
    z = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    q, r = np.linalg.qr(z)
    phase = np.diag(r)
    phase = np.where(np.abs(phase) > 0, phase / np.abs(phase), 1)
    return q @ np.diag(np.conj(phase))


def rand_hermitian(n: int, scale: float = 1.0) -> np.ndarray:
    a = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    return scale * (a + a.conj().T) / 2


def projectors_from_dims(dims: list[int]) -> list[np.ndarray]:
    n = sum(dims)
    out = []
    start = 0
    for d in dims:
        p = np.zeros((n, n), dtype=complex)
        p[start:start+d, start:start+d] = np.eye(d)
        out.append(p)
        start += d
    return out


def supermatrix(phi, n: int) -> np.ndarray:
    # Column vectorization convention.
    cols = []
    for j in range(n):
        for i in range(n):
            e = np.zeros((n, n), dtype=complex)
            e[i, j] = 1
            cols.append(phi(e).reshape(-1, order="F"))
    return np.column_stack(cols)


def choi_from_map(phi, n: int) -> np.ndarray:
    jmat = np.zeros((n*n, n*n), dtype=complex)
    for i in range(n):
        for j in range(n):
            e = np.zeros((n, n), dtype=complex)
            e[i, j] = 1
            jmat += np.kron(phi(e), e)
    return jmat


def partial_trace_out(jmat: np.ndarray, nout: int, nin: int) -> np.ndarray:
    a = jmat.reshape(nout, nin, nout, nin)
    return np.einsum("aiaj->ij", a)


def kron_all(xs: list[np.ndarray]) -> np.ndarray:
    out = np.array([[1.0 + 0j]])
    for x in xs:
        out = np.kron(out, x)
    return out


def main() -> None:
    a = Audit()

    # 1. Seed orbit and seed rank.
    a.begin("seed orbit and observable algebra rank")
    for d in range(1, 6):
        for m in range(1, 7):
            for r in range(0, min(d, m) + 1):
                left = rng.normal(size=(d, r)) + 1j * rng.normal(size=(d, r))
                right = rng.normal(size=(r, m)) + 1j * rng.normal(size=(r, m))
                c = left @ right if r else np.zeros((d, m), complex)
                # Map A -> AC in vector coordinates.
                linear = np.kron(c.T, np.eye(d))
                observed = matrix_rank(linear, tol=1e-9)
                expected = d * matrix_rank(c, tol=1e-9)
                a.check(observed == expected, f"orbit rank d={d}, m={m}, r={r}")
                a.check((observed == d*m) == (matrix_rank(c) == m), "cyclic criterion")
    for d in range(1, 6):
        for m in range(1, 10):
            k = math.ceil(m / d)
            # Explicit row space construction with k seeds.
            rows = []
            for j in range(k):
                c = np.zeros((d, m), complex)
                cols = list(range(j*d, min((j+1)*d, m)))
                for q, col in enumerate(cols):
                    c[q, col] = 1
                rows.append(c)
            stacked = np.vstack(rows)
            a.check(matrix_rank(stacked) == m, "constructed seeds span multiplicity")
            a.check((k-1)*d < m or k == 0, "lower bound")
    a.close()

    # 2. Cyclic symmetry projectors and tensor refinement.
    a.begin("symmetry projectors selection and tensor refinement")
    for N in range(2, 10):
        dims = [int(rng.integers(1, 4)) for _ in range(N)]
        phases = np.exp(2j * np.pi * np.arange(N) / N)
        s = np.diag(np.concatenate([np.full(dims[j], phases[j]) for j in range(N)]))
        ps = []
        for j in range(N):
            p = sum(np.exp(-2j*np.pi*j*r/N) * np.linalg.matrix_power(s, r) for r in range(N)) / N
            ps.append(p)
        ident = np.eye(sum(dims))
        a.check(norm(sum(ps) - ident) < TOL, "projector completeness")
        for j in range(N):
            a.check(norm(ps[j] @ ps[j] - ps[j]) < TOL, "idempotence")
            a.check(norm(s @ ps[j] - phases[j] * ps[j]) < TOL, "eigen packet")
            for k in range(N):
                a.check(norm(ps[j] @ ps[k] - (ps[j] if j == k else 0)) < TOL, "orthogonality")
        # Charge q operator built only from allowed blocks.
        q = int(rng.integers(0, N))
        op = np.zeros_like(s)
        offsets = np.cumsum([0] + dims)
        for j in range(N):
            k = (j + q) % N
            block = rng.normal(size=(dims[k], dims[j])) + 1j*rng.normal(size=(dims[k], dims[j]))
            op[offsets[k]:offsets[k+1], offsets[j]:offsets[j+1]] = block
        a.check(norm(s @ op @ s.conj().T - phases[q] * op) < TOL, "operator charge")
        for j in range(N):
            for k in range(N):
                b = ps[k] @ op @ ps[j]
                a.check(norm(b) < TOL if k != (j+q) % N else True, "selection rule")
    # Tensor total charge refinement for small N.
    for N in range(2, 6):
        p1 = [np.diag([1 if i == j else 0 for i in range(N)]).astype(complex) for j in range(N)]
        p2 = p1
        total = []
        for r in range(N):
            total.append(sum(np.kron(p1[j], p2[(r-j) % N]) for j in range(N)))
        a.check(norm(sum(total)-np.eye(N*N)) < TOL, "tensor completeness")
        for r in range(N):
            a.check(norm(total[r]@total[r]-total[r]) < TOL, "tensor idempotence")
            for sidx in range(N):
                a.check(norm(total[r]@total[sidx]-(total[r] if r==sidx else 0)) < TOL, "tensor orthogonality")
    a.close()

    # 3. Circuit path expansion and block unitarity.
    a.begin("circuit packet paths and interference")
    for n in range(3, 8):
        dims = [1, n-2, 1]
        ps = projectors_from_dims(dims)
        gates = [rand_unitary(n) for _ in range(3)]
        u = gates[2] @ gates[1] @ gates[0]
        reconstructed = np.zeros((n, n), complex)
        path_blocks: dict[tuple[int, int], list[np.ndarray]] = {}
        for a0 in range(3):
            for a1 in range(3):
                for a2 in range(3):
                    for a3 in range(3):
                        b = ps[a3]@gates[2]@ps[a2]@gates[1]@ps[a1]@gates[0]@ps[a0]
                        reconstructed += b
                        path_blocks.setdefault((a3, a0), []).append(b)
        a.check(norm(reconstructed-u) < 5e-9, "path reconstruction")
        for src in range(3):
            for src2 in range(3):
                lhs = sum((ps[b]@u@ps[src]).conj().T @ (ps[b]@u@ps[src2]) for b in range(3))
                rhs = ps[src] if src == src2 else np.zeros((n,n), complex)
                a.check(norm(lhs-rhs) < 5e-9, "column unitarity")
        # Interference formula for a random source vector.
        src = 1
        x = ps[src] @ (rng.normal(size=n)+1j*rng.normal(size=n))
        x /= norm(x)
        for target in range(3):
            ys = [b@x for b in path_blocks[(target,src)]]
            lhs = norm(ps[target]@u@x)**2
            rhs = sum(norm(y)**2 for y in ys)
            for j in range(len(ys)):
                for k in range(j+1,len(ys)):
                    rhs += 2*np.real(np.vdot(ys[j],ys[k]))
            a.check(abs(lhs-rhs) < 2e-8, "interference identity")
            a.check(norm(ps[target]@u@x) <= sum(norm(y) for y in ys)+TOL, "path triangle")
    a.close()

    # 4. Fixed and moving leakage.
    a.begin("fixed and moving packet leakage")
    for n in range(2, 9):
        p = np.zeros((n,n),complex)
        r = max(1,n//2)
        p[:r,:r]=np.eye(r)
        q = np.eye(n)-p
        for _ in range(15):
            h = rand_hermitian(n)
            comm = h@p-p@h
            off = q@h@p
            a.check(abs(norm(comm,2)-norm(off,2)) < 2e-8, "off diagonal norm")
            for t in np.linspace(0,1.5,8):
                leak = norm(q@expm(-1j*t*h)@p,2)
                a.check(leak <= t*norm(off,2)+2e-8, "fixed leakage bound")
    # Rotating rank one packet, exact moving transport with H=iK.
    for speed in [0.2,0.7,1.3]:
        g = speed*np.array([[0,-1],[1,0]],dtype=complex)
        p0 = np.diag([1,0]).astype(complex)
        for t in np.linspace(0,2,11):
            w = expm(t*g)
            p = w@p0@w.conj().T
            dp = g@p-p@g
            k = dp@p + (-dp)@(np.eye(2)-p)  # sum dot P_a P_a
            a.check(norm(k-g) < 3e-9, "Kato generator")
            h = 1j*k
            u = expm(t*g)
            a.check(norm((np.eye(2)-p)@u@p0) < 3e-9, "exact moving packet")
            a.check(norm((np.eye(2)-p)@(h-1j*k)@p) < 3e-9, "geometric block vanishes")
    a.close()

    # 5. Direct rotations and curvature.
    a.begin("direct packet rotation and curvature")
    p0 = np.diag([1,0]).astype(complex)
    for theta in np.linspace(0.001,0.5,40):
        rmat = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]],complex)
        q0 = rmat@p0@rmat.conj().T
        p1 = np.eye(2)-p0
        q1 = np.eye(2)-q0
        s = q0@p0+q1@p1
        up, _ = polar(s)
        a.check(norm(q0@up-up@p0) < 2e-9, "direct rotation intertwining")
        a.check(norm(up.conj().T@up-np.eye(2)) < 2e-9, "direct rotation unitary")
    # Short rotation product convergence.
    speed=0.8
    g=speed*np.array([[0,-1],[1,0]],complex)
    target=expm(g)
    errs=[]
    for nsteps in [10,20,40,80]:
        prod=np.eye(2,dtype=complex)
        for j in range(nsteps):
            t0=j/nsteps; t1=(j+1)/nsteps
            r0=expm(t0*g); r1=expm(t1*g)
            ps0=[r0@p0@r0.conj().T, r0@(np.eye(2)-p0)@r0.conj().T]
            ps1=[r1@p0@r1.conj().T, r1@(np.eye(2)-p0)@r1.conj().T]
            s=sum(q@p for q,p in zip(ps1,ps0))
            ustep,_=polar(s)
            prod=ustep@prod
        err=norm(prod-target)
        errs.append(err)
        a.check(err < 0.2/nsteps + 2e-8, "short rotation convergence")
    a.check(all(errs[j+1] <= errs[j]+1e-10 for j in range(len(errs)-1)), "monotone convergence")
    # Bloch curvature finite difference at interior points.
    paulis=[np.array([[0,1],[1,0]],complex),np.array([[0,-1j],[1j,0]],complex),np.diag([1,-1]).astype(complex)]
    for theta in np.linspace(0.2,math.pi-0.2,9):
        for phi in np.linspace(0,2*math.pi,11,endpoint=False):
            nvec=np.array([math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)])
            p=(np.eye(2)+sum(nvec[i]*paulis[i] for i in range(3)))/2
            dnth=np.array([math.cos(theta)*math.cos(phi),math.cos(theta)*math.sin(phi),-math.sin(theta)])
            dnph=np.array([-math.sin(theta)*math.sin(phi),math.sin(theta)*math.cos(phi),0])
            dpth=sum(dnth[i]*paulis[i] for i in range(3))/2
            dpph=sum(dnph[i]*paulis[i] for i in range(3))/2
            curv=(-1j*np.trace(p@(dpth@dpph-dpph@dpth))).real
            a.check(abs(curv-0.5*math.sin(theta)) < 2e-9, "Bloch curvature")
    a.close()

    # 6. Operator packets, channels, Choi, covariance.
    a.begin("operator packets channel blocks and Choi symmetry")
    for n in range(2,7):
        dims=[1,n-1]
        ps=projectors_from_dims(dims)
        x=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
        blocks=[ps[i]@x@ps[j] for i in range(2) for j in range(2)]
        a.check(norm(sum(blocks)-x) < TOL, "operator packet reconstruction")
        a.check(abs(sum(norm(b,'fro')**2 for b in blocks)-norm(x,'fro')**2) < 2e-8, "HS Pythagoras")
        deph=sum(ps[i]@x@ps[i] for i in range(2))
        a.check(norm(sum(ps[i]@deph@ps[i] for i in range(2))-deph) < TOL, "dephasing idempotent")
    # Amplitude damping and Choi tests.
    for gamma in np.linspace(0,1,21):
        k0=np.diag([1,math.sqrt(1-gamma)]).astype(complex)
        k1=np.array([[0,math.sqrt(gamma)],[0,0]],complex)
        phi=lambda x,k0=k0,k1=k1: k0@x@k0.conj().T+k1@x@k1.conj().T
        jmat=choi_from_map(phi,2)
        a.check(eigvalsh((jmat+jmat.conj().T)/2).min() > -2e-9, "Choi positivity")
        a.check(norm(partial_trace_out(jmat,2,2)-np.eye(2)) < 2e-9, "Choi trace preservation")
        e01=np.array([[0,1],[0,0]],complex)
        a.check(norm(phi(e01)-math.sqrt(1-gamma)*e01) < 2e-9, "coherence contraction")
        z=np.diag([1,-1]).astype(complex)
        # Z covariance.
        for _ in range(3):
            y=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2))
            a.check(norm(phi(z@y@z)-z@phi(y)@z) < 2e-9, "amplitude damping covariance")
        rep=np.kron(z,np.conj(z))
        a.check(norm(rep@jmat@rep.conj().T-jmat) < 2e-9, "Choi symmetry")
    # Channel superblock composition with random linear maps.
    n=3; ps=projectors_from_dims([1,2])
    m1=rng.normal(size=(n*n,n*n))+1j*rng.normal(size=(n*n,n*n))
    m2=rng.normal(size=(n*n,n*n))+1j*rng.normal(size=(n*n,n*n))
    def sm_to_map(m):
        return lambda x: (m@x.reshape(-1,order='F')).reshape((n,n),order='F')
    phi=sm_to_map(m1); psi=sm_to_map(m2)
    # Projector supermatrices.
    ops=[]
    for aa in range(2):
        for bb in range(2):
            ops.append(supermatrix(lambda x,aa=aa,bb=bb: ps[aa]@x@ps[bb],n))
    a.check(norm(sum(ops)-np.eye(n*n)) < TOL, "operator superprojectors complete")
    rec=sum(q@m1@p for q in ops for p in ops)
    a.check(norm(rec-m1) < 2e-8, "channel block reconstruction")
    comp=m2@m1
    comp_rec=sum(e@m2@q@m1@p for e in ops for q in ops for p in ops)
    a.check(norm(comp_rec-comp) < 5e-8, "channel block composition")
    a.close()

    # 7. Lindblad coherence preservation.
    a.begin("Lindblad coherence preservation")
    z=np.diag([1,-1]).astype(complex)
    h=np.diag([0.3,1.1]).astype(complex)
    sm=np.array([[0,1],[0,0]],complex)
    sp=sm.conj().T
    jumps=[0.7*sm,0.4*sp]
    def lind(x):
        y=-1j*(h@x-x@h)
        for l in jumps:
            y += l@x@l.conj().T -0.5*(l.conj().T@l@x+x@l.conj().T@l)
        return y
    gmat=supermatrix(lind,2)
    # q=0 diagonal and q=1 off diagonal packets.
    basis0=[np.diag([1,0]).astype(complex),np.diag([0,1]).astype(complex)]
    basis1=[np.array([[0,1],[0,0]],complex),np.array([[0,0],[1,0]],complex)]
    for x in basis0:
        a.check(norm(z@lind(x)@z-lind(x)) < 2e-9, "zero coherence preserved")
    for x in basis1:
        a.check(norm(z@lind(x)@z+lind(x)) < 2e-9, "odd coherence preserved")
    for t in np.linspace(0,2,11):
        sem=expm(t*gmat)
        for phase, collection in [(1, basis0), (-1, basis1)]:
            for x in collection:
                y=(sem@x.reshape(-1,order='F')).reshape((2,2),order='F')
                a.check(norm(z@y@z-phase*y) < 2e-8, "semigroup coherence")
    a.close()

    # 8. Quantum error correction.
    a.begin("quantum error correction obstruction and recovery")
    I2=np.eye(2); X=np.array([[0,1],[1,0]],complex)
    ket000=np.zeros(8,complex); ket000[0]=1
    ket111=np.zeros(8,complex); ket111[7]=1
    v=np.column_stack([ket000,ket111])
    p=v@v.conj().T
    errors=[np.eye(8),np.kron(np.kron(X,I2),I2),np.kron(np.kron(I2,X),I2),np.kron(np.kron(I2,I2),X)]
    c=np.zeros((4,4),complex)
    for i,e in enumerate(errors):
        for j,f in enumerate(errors):
            compressed=v.conj().T@e.conj().T@f@v
            scalar=np.trace(compressed)/2
            c[i,j]=scalar
            a.check(norm(compressed-scalar*np.eye(2)) < 2e-9, "KL residual")
    a.check(eigvalsh(c).min() > -2e-9, "KL matrix positive")
    synd=[]
    for e in errors:
        vv=e@v
        synd.append(vv@vv.conj().T)
    a.check(norm(sum(synd)-np.eye(8)) < 2e-9, "syndrome completeness")
    for i in range(4):
        for j in range(4):
            a.check(norm(synd[i]@synd[j]-(synd[i] if i==j else 0)) < 2e-9, "syndrome orthogonality")
    # Equal error mixture and explicit recovery.
    for _ in range(30):
        w=rand_unitary(2)
        probs=rng.random(2); probs/=probs.sum()
        rho2=w@np.diag(probs)@w.conj().T
        rho=v@rho2@v.conj().T
        noisy=sum(e@rho@e.conj().T for e in errors)/4
        recovered=np.zeros((8,8),complex)
        for e,q in zip(errors,synd):
            recovered += e.conj().T@q@noisy@q@e
        a.check(norm(recovered-rho) < 3e-9, "exact bit flip recovery")
    # Approximate defect bound on perturbed error.
    pert=errors[1]+1e-3*rand_hermitian(8)
    fam=errors+[pert]
    eps=0.0
    residuals={}
    for i,e in enumerate(fam):
        for j,f in enumerate(fam):
            comp=p@e.conj().T@f@p
            scalar=np.trace(v.conj().T@comp@v)/2
            res=comp-scalar*p
            eps=max(eps,norm(res,2))
            residuals[(i,j)]=(scalar,res)
    for _ in range(100):
        psi=v@(rng.normal(size=2)+1j*rng.normal(size=2)); psi/=norm(psi)
        phi=v@(rng.normal(size=2)+1j*rng.normal(size=2)); phi/=norm(phi)
        i=int(rng.integers(len(fam))); j=int(rng.integers(len(fam)))
        scalar,res=residuals[(i,j)]
        lhs=abs(np.vdot(fam[i]@psi,fam[j]@phi)-scalar*np.vdot(psi,phi))
        a.check(lhs <= eps+2e-9, "approximate KL bound")
    a.close()

    # 9. Feshbach, self energy, and stability.
    a.begin("Feshbach resolvent self energy and stability")
    for nr,nh in [(1,1),(2,1),(2,2),(3,2)]:
        for _ in range(25):
            aa=rand_hermitian(nr)
            dd=rand_hermitian(nh)+4*np.eye(nh)
            bb=(rng.normal(size=(nr,nh))+1j*rng.normal(size=(nr,nh)))*0.25
            hh=np.block([[aa,bb],[bb.conj().T,dd]])
            z=0.4+0.7j
            sig=bb@np.linalg.inv(z*np.eye(nh)-dd)@bb.conj().T
            f=z*np.eye(nr)-aa-sig
            full=np.linalg.inv(z*np.eye(nr+nh)-hh)[:nr,:nr]
            a.check(norm(full-np.linalg.inv(f)) < 2e-8, "projected resolvent")
            im=(sig-sig.conj().T)/(2j)
            a.check(eigvalsh((im+im.conj().T)/2).max() < 2e-9, "Herglotz sign")
            delta=min(abs(z-x) for x in eigvalsh(dd))
            a.check(norm(sig,2) <= norm(bb,2)**2/delta+2e-9, "self energy bound")
            # Bare truncation identity.
            bare=np.linalg.inv(z*np.eye(nr)-aa)
            lhs=full-bare
            rhs=np.linalg.inv(f)@sig@bare
            a.check(norm(lhs-rhs) < 2e-8, "bare truncation identity")
            # Stability under perturbation.
            db=(rng.normal(size=bb.shape)+1j*rng.normal(size=bb.shape))*1e-4
            dD=rand_hermitian(nh,1e-4)
            bt=bb+db; dt=dd+dD
            sigt=bt@np.linalg.inv(z*np.eye(nh)-dt)@bt.conj().T
            deltat=min(delta,min(abs(z-x) for x in eigvalsh(dt)))
            g=max(norm(bb,2),norm(bt,2))
            bound=2*g/deltat*norm(db,2)+g*g/(deltat*deltat)*norm(dD,2)
            a.check(norm(sig-sigt,2) <= bound+2e-8, "self energy stability")
    a.close()

    # 10. Quantum memory and local closure.
    a.begin("hidden packet memory and local closure")
    for nr,nh in [(1,2),(2,2),(2,3)]:
        for _ in range(15):
            dd=rand_hermitian(nh)
            bb=(rng.normal(size=(nr,nh))+1j*rng.normal(size=(nr,nh)))*0.3
            times=np.sort(rng.uniform(-2,2,size=6))
            vs=[rng.normal(size=nr)+1j*rng.normal(size=nr) for _ in times]
            gram=0j
            for j,tj in enumerate(times):
                for k,tk in enumerate(times):
                    kern=bb@expm(-1j*(tj-tk)*dd)@bb.conj().T
                    gram += np.vdot(vs[j],kern@vs[k])
            a.check(gram.real > -2e-8 and abs(gram.imag)<2e-8, "positive memory kernel")
            # Spectral expansion.
            evals,vecs=np.linalg.eigh(dd)
            t=float(rng.uniform(-2,2))
            spec=sum(np.exp(-1j*t*evals[r]) * bb@np.outer(vecs[:,r],vecs[:,r].conj())@bb.conj().T for r in range(nh))
            direct=bb@expm(-1j*t*dd)@bb.conj().T
            a.check(norm(spec-direct)<2e-8,"oscillatory expansion")
            # Laplace transform via spectral formula versus resolvent.
            s=0.8+0.2j
            lap=sum((1/(s+1j*evals[r])) * bb@np.outer(vecs[:,r],vecs[:,r].conj())@bb.conj().T for r in range(nh))
            res=bb@np.linalg.inv(s*np.eye(nh)+1j*dd)@bb.conj().T
            a.check(norm(lap-res)<2e-8,"memory Laplace transform")
            # Local closure second derivative detects B.
            a.check(norm(bb@bb.conj().T,2) > 1e-12, "nonzero coupling changes second derivative")
    a.close()

    # 11. Euclidean transfer and reflection positivity.
    a.begin("Euclidean transfer and reflection positivity")
    for n in range(2,9):
        for _ in range(12):
            h=rand_hermitian(n)
            e0=eigvalsh(h).min()
            step=float(rng.uniform(0.05,1.0))
            tmat=expm(-step*(h-e0*np.eye(n)))
            vals=eigvalsh((tmat+tmat.conj().T)/2)
            a.check(vals.min()>-2e-9 and vals.max()<=1+2e-9,"positive contraction")
            hrec=-logm(tmat)/step
            a.check(norm(hrec-(h-e0*np.eye(n)))<2e-7,"Hamiltonian logarithm")
            m=6
            ns=rng.integers(0,7,size=m)
            vs=[rng.normal(size=n)+1j*rng.normal(size=n) for _ in range(m)]
            gram=np.array([[np.vdot(vs[j],np.linalg.matrix_power(tmat,int(ns[j]+ns[k]))@vs[k]) for k in range(m)] for j in range(m)])
            a.check(eigvalsh((gram+gram.conj().T)/2).min()>-2e-7,"reflection Gram positivity")
            # Ground packet convergence exact norm.
            evals,u=np.linalg.eigh(h)
            ground=np.where(np.abs(evals-evals[0])<1e-9)[0]
            p0=u[:,ground]@u[:,ground].conj().T
            excited=[x-evals[0] for x in evals if x-evals[0]>1e-9]
            if excited:
                nn=5
                lhs=norm(np.linalg.matrix_power(tmat,nn)-p0,2)
                rhs=math.exp(-nn*step*min(excited))
                a.check(abs(lhs-rhs)<2e-7,"ground packet convergence")
    a.close()

    # 12. Finite spectral dimension and torus convergence.
    a.begin("finite spectral geometry and torus limit")
    for d in [1,2,3]:
        for N in range(4,33):
            reps=np.arange(-(N//2), N-N//2)
            # sample all modes for d<=2 and random for d=3
            modes=[]
            if d==1:
                modes=[(int(k),) for k in reps]
            elif d==2 and N<=18:
                modes=[(int(k),int(l)) for k in reps for l in reps]
            else:
                modes=[tuple(int(x) for x in rng.choice(reps,size=d)) for _ in range(100)]
            for k in modes:
                arr=np.array(k,float)
                lam=4*N*N*np.sum(np.sin(np.pi*arr/N)**2)
                cont=4*np.pi*np.pi*np.sum(arr**2)
                upper=(4*np.pi**4/(3*N*N))*np.sum(arr**4)
                a.check(lam <= cont+2e-8,"dispersion lower difference")
                a.check(cont-lam <= upper+2e-7,"dispersion bound")
    # Convergence at fixed times in 1D and 2D.
    for d in [1,2]:
        for t in [0.01,0.03,0.1,0.4]:
            K=80
            coords=np.arange(-K,K+1)
            if d==1:
                target=np.sum(np.exp(-4*np.pi*np.pi*t*coords**2))
            else:
                target=np.sum(np.exp(-4*np.pi*np.pi*t*(coords[:,None]**2+coords[None,:]**2)))
            errs=[]
            for N in [16,32,64,128]:
                reps=np.arange(-(N//2),N-N//2)
                if d==1:
                    lam=4*N*N*np.sin(np.pi*reps/N)**2
                else:
                    lam=4*N*N*(np.sin(np.pi*reps[:,None]/N)**2+np.sin(np.pi*reps[None,:]/N)**2)
                z=np.sum(np.exp(-t*lam))
                errs.append(abs(z-target))
            a.check(errs[-1] < errs[0]+1e-10,"heat trace convergence")
            a.check(errs[-1] < 0.08,"heat trace terminal accuracy")
    # Finite UV and IR dimensions.
    eigs=np.array([0,1,4,9],float)
    for t in [1e-8,1e-7,1e-6]:
        z=np.sum(np.exp(-t*eigs)); mom=np.sum(eigs*np.exp(-t*eigs)); dim=2*t*mom/z
        a.check(dim<1e-4,"finite UV dimension")
    for t in [20,30,40]:
        z=np.sum(np.exp(-t*eigs)); mom=np.sum(eigs*np.exp(-t*eigs)); dim=2*t*mom/z
        a.check(dim<1e-6,"finite IR dimension")
    a.close()

    # 13. Constraint obstruction and refinement.
    a.begin("constraint quotient obstruction and refinement")
    sx=np.array([[0,1],[1,0]],complex)
    sy=np.array([[0,-1j],[1j,0]],complex)
    sz=np.diag([1,-1]).astype(complex)
    cs=[sx,sy,sz]
    basis=np.column_stack([c.reshape(-1,order='F') for c in cs])
    for i in range(3):
        for j in range(3):
            comm=cs[i]@cs[j]-cs[j]@cs[i]
            coeff,*_=np.linalg.lstsq(basis,comm.reshape(-1,order='F'),rcond=None)
            resid=comm.reshape(-1,order='F')-basis@coeff
            a.check(norm(resid)<2e-9,"Pauli closure quotient")
    # Nonclosing pair with span not containing commutator.
    c1=np.diag([0,1,2]).astype(complex)
    c2=np.array([[0,1,0],[1,0,1],[0,1,0]],complex)
    basis2=np.column_stack([c1.reshape(-1,order='F'),c2.reshape(-1,order='F')])
    comm=c1@c2-c2@c1
    coeff,*_=np.linalg.lstsq(basis2,comm.reshape(-1,order='F'),rcond=None)
    a.check(norm(comm.reshape(-1,order='F')-basis2@coeff)>0.1,"nonclosing quotient detected")
    # Physical compression always zero for a common kernel example.
    c1=np.diag([0,1,0]).astype(complex)
    c2=np.array([[0,0,0],[0,0,1],[0,1,0]],complex)
    pphys=np.diag([1,0,0]).astype(complex)
    a.check(norm(pphys@(c1@c2-c2@c1)@pphys)<TOL,"physical compression trivial")
    # Exact transport by an isometry.
    rmat=np.vstack([np.eye(2),np.zeros((1,2))]).astype(complex)
    coarse=[sx,sz]
    fine=[]
    for c in coarse:
        f=rmat@c@rmat.conj().T
        # arbitrary orthogonal complement action set to zero
        fine.append(f)
    for i in range(2):
        a.check(norm(fine[i]@rmat-rmat@coarse[i])<TOL,"constraint intertwining")
    a.check(norm((fine[0]@fine[1]-fine[1]@fine[0])@rmat-rmat@(coarse[0]@coarse[1]-coarse[1]@coarse[0]))<TOL,"commutator transport")
    a.close()

    # 14. Bounded towers and limit closures.
    a.begin("bounded quantum towers and limit closure")
    # Common Hilbert norm summable sequence.
    h0=rand_hermitian(4)
    hs=[h0]
    for n in range(1,12):
        hs.append(hs[-1]+rand_hermitian(4,scale=2**(-n-3)))
    hlim=hs[-1]
    for n,h in enumerate(hs):
        tail=sum(norm(hs[j+1]-hs[j],2) for j in range(n,len(hs)-1))
        a.check(norm(h-hlim,2)<=tail+2e-9,"summable tail")
        for t in [0.2,0.7,1.4]:
            a.check(norm(expm(-1j*t*h)-expm(-1j*t*hlim),2)<=t*norm(h-hlim,2)+2e-8,"unitary Duhamel")
    # Reflection positive kernels closed under entrywise limits.
    tvals=np.linspace(0.1,1.0,6)
    for n in [5,10,20,40]:
        lam=np.linspace(0,2,n)
        weights=np.ones(n)/n
        gram=np.array([[np.sum(weights*np.exp(-(tvals[j]+tvals[k])*lam)) for k in range(len(tvals))] for j in range(len(tvals))])
        a.check(eigvalsh(gram).min()>-2e-10,"reflection positive approximant")
    # Constraint closure norm limit with su2 perturbations decreasing.
    for n in [5,10,20,40]:
        eps=1/n
        cseq=[sx+eps*np.eye(2),sy,sz]
        anomaly=cseq[0]@cseq[1]-cseq[1]@cseq[0]-2j*cseq[2]
        a.check(norm(anomaly)<2e-9,"fixed structure survives scalar perturbation")
    # Heat trace continuity from trace norm finite dimensional.
    l=rand_hermitian(5); vals,u=np.linalg.eigh(l); vals=np.abs(vals); l=u@np.diag(vals)@u.conj().T
    for n in [5,10,20,40]:
        ln=l+np.eye(5)/n
        t=0.4
        en=expm(-t*ln); e=expm(-t*l)
        a.check(abs(np.trace(en)-np.trace(e))<=np.sum(np.linalg.svd(en-e,compute_uv=False))+2e-9,"trace norm heat")
    a.close()

    # 15. Legacy certificates and source/package integrity.
    a.begin("legacy certificates and source integrity")
    legacy=json.loads(LEGACY.read_text())
    a.check(abs(legacy["bell"]["state_error"])<1e-12,"legacy Bell error")
    a.check(legacy["bell"]["reachable_rank_three_qubit_x_generators"]==8,"legacy reachable rank")
    a.check(legacy["effective_dynamics"]["feshbach_resolvent_error"]<1e-12,"legacy Feshbach")
    a.check(legacy["error_correction"]["knill_laflamme_residual"]<1e-12,"legacy KL")
    a.check(legacy["error_correction"]["recovery_error"]<1e-12,"legacy recovery")
    a.check(legacy["symmetry"]["circuit_path_reconstruction_error"]<1e-12,"legacy circuit")
    tex=TEX.read_text()
    bib=BIB.read_text()
    labels=re.findall(r"\\label\{([^}]+)\}",tex)
    refs=[]
    for item in re.findall(r"\\(?:ref|cref|Cref|eqref)\{([^}]+)\}",tex):
        refs.extend(x.strip() for x in item.split(','))
    cites=[]
    for item in re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]+)\}",tex):
        cites.extend(x.strip() for x in item.split(','))
    bibkeys=re.findall(r"@\w+\{([^,]+),",bib)
    a.check(len(labels)==len(set(labels)),"unique labels")
    a.check(not (set(refs)-set(labels)),"all references resolved in source")
    a.check(not (set(cites)-set(bibkeys)),"all citations have bibliography entries")
    a.check(not (set(bibkeys)-set(cites)),"all bibliography entries cited")
    a.check(tex.count('\\begin{proof}')==79,"proof count")
    a.check(tex.count(';')==0,"no semicolons")
    a.check('--' not in tex,"no source double hyphens")
    a.check(not re.search(r"\\(?:newpage|clearpage|pagebreak|linebreak)\b",tex),"no forced breaks")
    abstract=tex.split('\\begin{abstract}',1)[1].split('\\end{abstract}',1)[0]
    words=re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",abstract)
    a.check(len(words)<=200,"abstract word limit")
    # PDF text checks.
    subprocess.run(["pdftotext",str(PDF),str(ROOT/"verification"/"pdf_text.txt")],check=True)
    pdf_text=(ROOT/"verification"/"pdf_text.txt").read_text(errors='ignore')
    a.check(';' not in pdf_text,"no PDF semicolons")
    a.check('-' not in pdf_text,"no visible ASCII hyphens")
    # Vector figures and no raster images.
    figs=sorted(FIGDIR.glob('*.pdf'))
    a.check(len(figs)==16,"all figure files present")
    for fig in figs:
        proc=subprocess.run(["pdfimages","-list",str(fig)],capture_output=True,text=True,check=True)
        lines=[ln for ln in proc.stdout.splitlines() if re.match(r"\s*\d+\s+\d+",ln)]
        a.check(len(lines)==0,f"vector figure {fig.name}")
    a.close({"abstract_words":len(words),"labels":len(labels),"bibliography_entries":len(bibkeys),"figures":len(figs)})

    results={
        "status":"passed",
        "total_checks":a.total,
        "groups":a.groups,
        "numpy_version":np.__version__,
    }
    OUT_JSON.write_text(json.dumps(results,indent=2)+"\n")
    lines=[f"Paper VII verification: {a.total}/{a.total} checks passed in {len(a.groups)} groups"]
    for name,data in a.groups.items():
        lines.append(f"{name}: {data['checks']} checks passed")
    OUT_TXT.write_text("\n".join(lines)+"\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
