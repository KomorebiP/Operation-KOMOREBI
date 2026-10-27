#!/usr/bin/env python3
"""Regenerate the checkpoint-49 physics atlas. No empirical data or theorem checks.

Run from the release root: python tools/make_figures.py
Exact symbolic checks authenticate the coordinate matrices. Finite floating
checks authenticate selected plotted examples only. Mathematical claims are
supported by the source proofs, never by the figures or their residuals.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import platform
import time
import sys
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.special import zeta
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap

START = time.monotonic()
STAMP = dt.datetime.now(dt.timezone.utc).isoformat()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
TEAL = "#245D60"
INK = "#212B34"
MUTED = "#58646B"
PALE = "#EEF3F2"
GOLD = "#AD7842"
LILAC = "#7C738E"
LIGHT = "#C9D8D6"
COLORS = [TEAL, GOLD, LILAC, MUTED]
CMAP = LinearSegmentedColormap.from_list("komorebi", [GOLD, "#FAFBFA", TEAL])
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.labelsize": 11, "axes.titlesize": 12.5,
    "axes.titleweight": "medium", "axes.titlepad": 14,
    "axes.labelcolor": INK, "text.color": INK,
    "axes.edgecolor": "#ADBAB9", "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False,
    "legend.fontsize": 10, "lines.linewidth": 2.2,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "pdf.fonttype": 42,
    "ps.fonttype": 42, "mathtext.fontset": "dejavusans",
})
outputs = []
checks = []


def record(name, passed, detail):
    checks.append({"name": name, "passed": bool(passed), "detail": detail})
    if not passed:
        raise AssertionError(f"{name}: {detail}")


def save(fig, name):
    for ext in ("pdf", "png"):
        target = OUT / f"{name}.{ext}"
        fig.savefig(target, dpi=190, bbox_inches="tight", pad_inches=0.16)
        outputs.append({"path": str(target.relative_to(ROOT)),
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    plt.close(fig)


def grid(ax):
    ax.grid(True, color="#DDE5E3", linewidth=.65, alpha=.8)
    ax.set_axisbelow(True)


def box(ax, x, y, w, h, title, detail="", color=PALE, edge=TEAL,
        title_size=12, detail_size=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.012,rounding_size=0.015",
                 facecolor=color, edgecolor=edge, lw=1.2))
    if detail:
        ax.text(x+w/2, y+h*.66, title, ha="center", va="center",
                fontsize=title_size, color=INK)
        ax.text(x+w/2, y+h*.28, detail, ha="center", va="center",
                fontsize=detail_size, color=MUTED, linespacing=1.5)
    else:
        ax.text(x+w/2, y+h/2, title, ha="center", va="center",
                fontsize=title_size, color=INK)


def arrow(ax, start, end, dashed=False, color=MUTED):
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "->", "lw": 1.4,
                            "color": color, "linestyle": "--" if dashed else "-"})


# The matrices are the exact column-spinor convention in the traditional source.
I = sp.I
exact = [
    sp.Matrix([[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]),
    sp.Matrix([[0,0,0,-I],[0,0,I,0],[0,-I,0,0],[I,0,0,0]]),
    sp.Matrix([[0,0,1,0],[0,0,0,-1],[1,0,0,0],[0,-1,0,0]]),
    sp.diag(1,1,-1,-1),
]
eye = sp.eye(4)
record("exact Clifford relations", all(A.H == A and A*A == eye for A in exact)
       and all(exact[j]*exact[k]+exact[k]*exact[j] == sp.zeros(4)
               for j in range(4) for k in range(j+1,4)),
       "SymPy exact Gaussian-integer arithmetic; four 4x4 matrices, six distinct pairs.")
AX, AY, AZ, B = [np.array(A.tolist(), dtype=complex) for A in exact]


def hamiltonian(m, p):
    return m*B + p[0]*AX + p[1]*AY + p[2]*AZ


def propagator(m, p, t):
    H = hamiltonian(m, p)
    E = np.sqrt(m*m+np.dot(p,p))
    if E == 0:
        return np.eye(4, dtype=complex)
    return np.cos(E*t)*np.eye(4) - 1j*np.sin(E*t)/E*H


# 01: Schematic refinement. This is a toy projector tree, not a spatial box claim.
fig, ax = plt.subplots(figsize=(8.7, 5.2))
ax.set(xlim=(0,1), ylim=(0,1)); ax.axis("off")
box(ax, .30, .81, .40, .14, r"Identity $I$", r"all four coordinates")
box(ax, .10, .49, .31, .17, r"$P$", r"coordinates 0, 1")
box(ax, .59, .49, .31, .17, r"$Q=I-P$", r"coordinates 2, 3")
for x, name in [(.02,r"$P_0$"),(.27,r"$P_1$"),(.52,r"$Q_2$"),(.77,r"$Q_3$")]:
    box(ax, x, .13, .21, .16, name, "one coordinate", title_size=13)
arrow(ax,(.43,.80),(.26,.67)); arrow(ax,(.57,.80),(.74,.67))
for start,end in [((.20,.48),(.12,.30)),((.31,.48),(.38,.30)),
                  ((.69,.48),(.63,.30)),((.80,.48),(.87,.30))]:
    arrow(ax,start,end)
ax.text(.5,.025,r"Orthogonality: $PQ=0$     Completeness: $P+Q=I$",
        ha="center",fontsize=12)
save(fig,"01_refinement")

# 02: Genuine 3D slices of a normalized torus plane wave.
fig = plt.figure(figsize=(8.0,6.0))
ax = fig.add_subplot(111, projection="3d")
x = np.linspace(0,1,81); X,Y = np.meshgrid(x,x)
for zz in (0,.5,1):
    Z = np.full_like(X,zz)
    val = np.cos(2*np.pi*(X+Y+Z))
    ax.plot_surface(X,Y,Z,facecolors=CMAP((val+1)/2),rstride=1,cstride=1,
                    shade=False,alpha=.84,linewidth=0,antialiased=False)
ax.set(xlim=(0,1),ylim=(0,1),zlim=(0,1),xlabel=r"$x_1$",ylabel=r"$x_2$",zlabel=r"$x_3$")
ax.set_xticks([0,.5,1]); ax.set_yticks([.5,1]); ax.set_zticks([0,.5,1])
ax.set_box_aspect((1,1,1)); ax.view_init(elev=23,azim=-51)
ax.set_title(r"Real part of $e_{(1,1,1)}(x)$ on three coordinate slices",pad=18)
sm=plt.cm.ScalarMappable(cmap=CMAP,norm=plt.Normalize(-1,1))
fig.colorbar(sm,ax=ax,shrink=.62,pad=.09,label=r"$\cos[2\pi(x_1+x_2+x_3)]$",ticks=[-1,0,1])
save(fig,"02_torus_modes")

# 03: Real and imaginary parts, only two panels for all four matrices.
fig, axs = plt.subplots(2,1,figsize=(9,5.2),layout="constrained")
whole=np.concatenate([AX,AY,AZ,B],axis=1)
for ax,arr,title in zip(axs,[whole.real,whole.imag],["Real entries","Imaginary coefficients"]):
    ax.imshow(arr,cmap=CMAP,vmin=-1,vmax=1,aspect="equal")
    ax.set_title(title,loc="left",pad=12)
    ax.set_xticks([1.5,5.5,9.5,13.5],[r"$\alpha_x$",r"$\alpha_y$",r"$\alpha_z$",r"$\beta$"])
    ax.xaxis.tick_top(); ax.tick_params(axis="x",length=0,pad=7)
    ax.set_yticks(range(4),["0","1","2","3"]); ax.set_ylabel("row")
    for j in (3.5,7.5,11.5): ax.axvline(j,color="white",lw=4)
    for r in range(4):
        for c in range(16):
            if arr[r,c]: ax.text(c,r,f"{int(arr[r,c]):+d}",ha="center",va="center",color="white",fontsize=11)
    for spine in ax.spines.values(): spine.set_visible(False)
save(fig,"03_clifford")

# 04: Real momentum interpolation explicitly distinguished from torus modes.
h=1/12; m=1
k=np.linspace(-np.pi/h,np.pi/h,1201)
E=np.sqrt(m*m+k*k); Eh=np.sqrt(m*m+(np.sin(h*k)/h)**2)
fig,axs=plt.subplots(1,2,figsize=(9,4.5),layout="constrained")
axs[0].plot(k,E,color=TEAL,label="continuum"); axs[0].plot(k,-E,color=TEAL)
axs[0].plot(k,Eh,color=GOLD,ls="--",label="centered"); axs[0].plot(k,-Eh,color=GOLD,ls="--")
kn=2*np.pi*np.arange(-5,6); En=np.sqrt(1+(np.sin(h*kn)/h)**2)
axs[0].scatter(kn,En,s=19,color=GOLD,zorder=3,label="integer torus modes")
axs[0].scatter(kn,-En,s=19,color=GOLD,zorder=3)
axs[0].set(xlabel=r"real momentum $k$",ylabel="energy",title=r"Two signs of the shell, $m=1$")
axs[0].legend(loc="upper center",fontsize=9)
kl=np.linspace(0,2*np.pi,400)
axs[1].plot(kl,np.sqrt(1+kl*kl)-np.sqrt(1+(np.sin(h*kl)/h)**2),color=TEAL)
axs[1].scatter([2*np.pi],[np.sqrt(1+4*np.pi**2)-np.sqrt(37)],color=GOLD,s=40,zorder=4)
axs[1].set(xlabel=r"real momentum $k$",ylabel=r"$E(k)-E_h(k)$",title=r"Low momentum discrepancy, $h=1/12$")
axs[1].set_xticks([0,np.pi,2*np.pi],["0",r"$\pi$",r"$2\pi$"])
for ax in axs: grid(ax)
save(fig,"04_dispersion")

# 05: Fixed mode consistency; displayed bound is an analytic inequality.
fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
kl=np.linspace(-2*np.pi,2*np.pi,501)
axs[0].plot(kl,kl,color=TEAL,label=r"$k$")
axs[0].plot(kl,np.sin(h*kl)/h,color=GOLD,ls="--",label=r"$\sin(hk)/h$")
axs[0].set(xlabel=r"$k$",ylabel="kinetic momentum",title=r"Centered symbol at $h=1/12$")
axs[0].legend(); grid(axs[0])
hs=2.0**(-np.arange(2,12)); p=2*np.pi
err=np.abs(np.sin(hs*p)/hs-p); bound=hs**2*p**3/6
axs[1].loglog(hs,err,"o-",color=TEAL,label="axis mode error")
axs[1].loglog(hs,bound,"--",color=GOLD,label=r"$h^2(2\pi)^3/6$")
axs[1].set(xlabel=r"spacing $h$",ylabel="absolute error",title=r"Fixed $n=(1,0,0)$")
axs[1].legend(); grid(axs[1])
record("finite symbol bound",np.all(err <= bound*(1+1e-10)),
       {"h":hs.tolist(),"p":float(p),"max_error_over_bound":float(np.max(err/bound)),
        "convention":"The exact h=0 extension is p; all sampled h are nonzero."})
save(fig,"05_symbol_error")

# 06: Exact three-mode formula evaluated on a finite display grid.
modes=np.array([[0,0,0],[1,0,0],[1,1,1]],dtype=float)
amps=np.array([1/np.sqrt(2),.5,.5])
momenta=np.sin(h*2*np.pi*modes)/h
ts=np.linspace(0,1,401); xs=np.linspace(0,1,241,endpoint=False)
e0=np.array([1,0,0,0],complex)
states=np.array([[propagator(1,q,t)@e0 for q in momenta] for t in ts])
coeff=states*amps[None,:,None]
components=np.sum(abs(coeff)**2,axis=1)
phases=np.exp(2j*np.pi*modes[:,0,None]*xs[None,:])
field=np.einsum("tmc,mx->txc",coeff,phases)
density=np.sum(abs(field)**2,axis=2)
fig,axs=plt.subplots(1,2,figsize=(9,4.4),layout="constrained")
im=axs[0].pcolormesh(xs,ts,density,shading="auto",cmap="YlGnBu",rasterized=True)
axs[0].set(xlabel=r"$x_1$ at $x_2=x_3=0$",ylabel=r"time $t$",title="Local density moves")
fig.colorbar(im,ax=axs[0],pad=.03,shrink=.82,label=r"$\|f_h(t,x)\|^2$")
for j in [0,2,3]: axs[1].plot(ts,components[:,j],color=COLORS[j if j<3 else 1],label=f"component {j}")
axs[1].plot(ts,components.sum(axis=1),color=INK,ls="--",lw=1.8,label="total = 1")
axs[1].set(xlabel=r"time $t$",ylabel="integrated squared norm",ylim=(-.025,1.08),title="The total norm stays fixed")
axs[1].legend(loc="upper center",bbox_to_anchor=(.5,-.17),ncol=2); grid(axs[1])
norm_res=float(np.max(abs(components.sum(axis=1)-1)))
record("three-mode norm conservation on time grid",norm_res<5e-14,
       {"t_interval":[0,1],"time_samples":401,"spatial_slice_samples":241,
        "max_norm_residual":norm_res,"m":1,"h":"1/12","modes":modes.tolist(),
        "weights_squared":[.5,.25,.25],"pointwise_density_is_not_normalized":True})
expm_res=0.; unitary_res=0.
for mass in [0.,1.,-2.]:
    for q in [np.zeros(3),np.array([6.,0.,0.]),np.array([6.,6.,6.])]:
        for t in [0.,.137,.4,1.]:
            U=propagator(mass,q,t)
            expm_res=max(expm_res,float(np.max(abs(U-expm(-1j*t*hamiltonian(mass,q))))))
            unitary_res=max(unitary_res,float(np.max(abs(U.conj().T@U-np.eye(4)))))
record("closed propagator against independent matrix exponential",expm_res<1e-13 and unitary_res<1e-13,
       {"mass":[0,1,-2],"kinetic_vectors":[[0,0,0],[6,0,0],[6,6,6]],
        "times":[0,.137,.4,1],"max_expm_residual":expm_res,
        "max_unitarity_residual":unitary_res,"includes_zero_energy_branch":True})
save(fig,"06_packet_evolution")

# 07: Rigorous-form upper bounds for one explicitly chosen infinite sequence.
fig,axs=plt.subplots(1,2,figsize=(9,4.6),layout="constrained")
ns=np.arange(1,81); coef=ns.astype(float)**-2/np.sqrt(zeta(4,1))
axs[0].loglog(ns,coef**2,color=TEAL)
axs[0].axvline(16,color=GOLD,ls="--",label=r"cutoff $K=16$")
axs[0].fill_between(ns,coef**2,1e-10,where=ns>16,color=GOLD,alpha=.18)
axs[0].set(xlabel="positive axis mode n",ylabel=r"$|a_n|^2$",ylim=(1e-9,2),title="Choose a finite core first")
axs[0].legend(); grid(axs[0])
hh=np.logspace(-5,-1,260)
for K,c in zip([4,16,64],[TEAL,GOLD,LILAC]):
    nn=np.arange(1,K+1,dtype=float)
    aa=nn**-2/np.sqrt(zeta(4,1))
    C=np.sqrt(np.sum(aa**2*(2*np.pi*nn)**6))/6
    tail=2*np.sqrt(zeta(4,K+1)/zeta(4,1))
    normcore=np.sqrt(np.sum(aa**2))
    upper=np.minimum(2*normcore,C*hh**2)+tail
    axs[1].loglog(hh,upper,color=c,label=f"K = {K}")
    axs[1].axhline(tail,color=c,alpha=.28,lw=1)
axs[1].set(xlabel=r"spacing $h$",ylabel="upper bound at |t| ≤ 1",title="Then refine the spacing")
axs[1].legend(); grid(axs[1])
save(fig,"07_two_tail")

# 08: Exact p-series thresholds are explained in the text; these sums are finite.
fig,axs=plt.subplots(1,2,figsize=(9,4.5),layout="constrained")
nn=np.arange(1,4097,dtype=float)
for s,c in zip([.4,1.,1.5,2.],COLORS):
    a2=nn**(-2*s)
    for ax,w in zip(axs,[np.ones_like(nn),1+(2*np.pi*nn)**2]):
        ax.loglog(nn,np.cumsum(w*a2),color=c,label=f"s = {s:g}")
axs[0].set(title=r"Ordinary squared norm",xlabel="truncation N",ylabel=r"$\sum_{n=1}^N n^{-2s}$")
axs[1].set(title=r"First-order squared norm",xlabel="truncation N",ylabel=r"$\sum_{n=1}^N(1+4\pi^2n^2)n^{-2s}$")
for ax in axs: grid(ax); ax.legend(loc="upper left")
save(fig,"08_domain_thresholds")

# 09: Infinite tail formulas for normalized n^-2 positive-axis coefficients.
K=np.unique(np.geomspace(1,512,130).astype(int))
l2sq=zeta(4,K+1)/zeta(4,1)
graphsq=(2*zeta(4,K+1)+4*np.pi**2*zeta(2,K+1))/zeta(4,1)
fig,ax=plt.subplots(figsize=(8.3,4.8),layout="constrained")
ax.loglog(K,np.sqrt(l2sq),color=TEAL,label=r"field error $\|a-P_Ka\|$")
ax.loglog(K,np.sqrt(graphsq),color=GOLD,label=r"graph error $\|a-P_Ka\|_{H}$")
ax.loglog(K,.7*K.astype(float)**-1.5,color=TEAL,ls=":",alpha=.6,label=r"reference $K^{-3/2}$")
ax.loglog(K,7*K.astype(float)**-.5,color=GOLD,ls=":",alpha=.6,label=r"reference $K^{-1/2}$")
ax.set(xlabel="Fourier cutoff K",ylabel="tail norm",title=r"A domain vector converges in both coordinates of its graph")
ax.legend(loc="lower left"); grid(ax)
record("Hurwitz-zeta graph tails",np.all(np.diff(l2sq)<0) and np.all(np.diff(graphsq)<0),
       {"K_min":1,"K_max":512,"samples":len(K),"coefficient":"n^-2/sqrt(zeta(4)) on n=(n,0,0), n>=1",
        "mass":1,"graph_norm_convention":"sqrt(||a||²+||Ha||²)",
        "l2_tail_at_512":float(np.sqrt(l2sq[-1])),"graph_tail_at_512":float(np.sqrt(graphsq[-1])),
        "infinite_tails":"SciPy Hurwitz-zeta evaluations, not sums stopped at 512"})
save(fig,"09_graph_truncation")

# 10: The commutative square is the definition of the transported operator.
fig,ax=plt.subplots(figsize=(8.7,5.5)); ax.set(xlim=(0,1),ylim=(0,1)); ax.axis("off")
box(ax,.04,.67,.35,.20,r"Coefficient domain $D(H_m)$",r"weighted sequences",title_size=11.5)
box(ax,.61,.67,.35,.20,r"Physical domain $D(\mathsf{H}_m)$",r"torus spinor fields",title_size=11.5)
box(ax,.04,.14,.35,.20,r"$\ell^2(\mathbb{Z}^3;\mathbb{C}^4)$",r"coefficient Hilbert space",title_size=12)
box(ax,.61,.14,.35,.20,r"$L^2(\mathbb{T}^3;\mathbb{C}^4)$",r"physical Hilbert space",title_size=12)
arrow(ax,(.40,.77),(.60,.77)); arrow(ax,(.40,.24),(.60,.24))
ax.text(.50,.83,r"$\mathcal{F}^{-1}$",ha="center",fontsize=15)
ax.text(.50,.30,r"$\mathcal{F}^{-1}$",ha="center",fontsize=15)
arrow(ax,(.215,.66),(.215,.35)); arrow(ax,(.785,.66),(.785,.35))
ax.text(.235,.50,r"$H_m$",ha="left",fontsize=15)
ax.text(.805,.50,r"$\mathsf{H}_m$",ha="left",fontsize=15)
ax.text(.5,.51,r"$\mathsf{H}_m=\mathcal{F}^{-1}H_m\mathcal{F}$",ha="center",fontsize=13)
ax.text(.5,.035,r"The horizontal maps preserve inner products and norms.",ha="center",fontsize=11,color=MUTED)
save(fig,"10_fourier_transport")

# 11: The same domain, different graph norms. Normalized n^-2 gives kinetic norm²=60.
fig,axs=plt.subplots(1,2,figsize=(9,4.5),layout="constrained")
p=np.logspace(-2,3,450)
for mass,c in zip([0,1,3],[TEAL,GOLD,LILAC]):
    axs[0].semilogx(p,(1+mass**2+p**2)/(1+p**2),color=c,label=f"m = {mass}")
axs[0].set(xlabel=r"momentum magnitude $|p|$",ylabel="graph weight / first-order weight",title="Mass changes an equivalent norm")
axs[0].legend(); grid(axs[0])
mm=np.linspace(-4,4,401)
axs[1].plot(mm,61+mm**2,color=TEAL)
axs[1].axhline(61,color=GOLD,ls="--",label="massless graph norm²")
axs[1].set(xlabel=r"mass parameter $m$",ylabel=r"$\|a\|_{H_m}^2$",title=r"One fixed domain vector: $61+m^2$")
axs[1].legend(); grid(axs[1])
record("exact kinetic norm of normalized axis example",
       sp.simplify(4*sp.pi**2*sp.zeta(2)/sp.zeta(4)) == 60,
       "For a_n=n^-2/sqrt(zeta(4)), n>=1: ||a||²=1, momentum norm²=60, graph norm²=61+m².")
save(fig,"11_mass_domain")

# 12: A status diagram, not a forecast or a percentage-completion claim.
fig,ax=plt.subplots(figsize=(8.8,6.6)); ax.set(xlim=(0,1),ylim=(0,1)); ax.axis("off")
ax.text(.03,.97,"CHECKED THROUGH BLOCK 49",fontsize=11,color=TEAL,weight="bold")
box(ax,.06,.77,.88,.14,"44–45  ·  Finite packets", "Hilbert unitarity and compact-time convergence")
box(ax,.06,.56,.88,.14,"46–47  ·  Full Hilbert spaces", "Infinite coefficient fields and unitary torus transport")
box(ax,.06,.35,.88,.14,"48–49  ·  Unbounded Hamiltonian", "Self-adjointness, graph core and exact weighted domain")
arrow(ax,(.5,.765),(.5,.705),color=TEAL); arrow(ax,(.5,.555),(.5,.495),color=TEAL)
ax.plot([.03,.97],[.285,.285],ls="--",lw=1.1,color=GOLD)
ax.text(.03,.25,"NEXT MATHEMATICAL CONNECTIONS",fontsize=10.7,color=GOLD,weight="bold")
box(ax,.04,.055,.44,.13,"Evolution ↔ generator", "Full operator identification",color="#F7F1E9",edge=GOLD,title_size=11.5,detail_size=10)
box(ax,.52,.055,.44,.13,"Operator limits and coupling", "Resolvents, rates and backgrounds",color="#F7F1E9",edge=GOLD,title_size=11.5,detail_size=10)
save(fig,"12_frontier")

record("figure output inventory",len(outputs)==24,"12 PDF figures and 12 PNG previews generated.")
source_path=Path(__file__).resolve()
source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
manifest={
    "schema_version":1,"claim_id":"physics-monograph49-recomputed-illustrations",
    "repository":{"commit":"not applicable: standalone publication staging directory","dirty":True},
    "command":"python tools/make_figures.py",
    "environment":{"software":[f"Python {platform.python_version()}",f"NumPy {np.__version__}",
        f"SciPy {scipy.__version__}",f"SymPy {sp.__version__}",f"Matplotlib {matplotlib.__version__}"],
        "hardware":platform.machine()},
    "mathematics":{
        "assertion_tested":"The explicit plotted finite examples respect the supplied Clifford matrices, propagator formulas, symbol bound and stated tail formulas in the recorded ranges.",
        "coefficient_domain":"Exact Gaussian integers for Clifford checks; exact symbolic zeta identities; IEEE double/complex128 for plots and finite residuals.",
        "conventions":"Unit torus, normalized Haar measure, p(n)=2*pi*n, column spinors 0..3, alpha_y first row (0,0,0,-i), U=exp(-i*t*H); graph norm sqrt(||a||²+||Ha||²).",
        "inputs":[{"path":"tools/make_figures.py","sha256":source_hash}],
        "bounds":{"clifford_matrices":4,"clifford_pairs":6,"matrix_exponential_cases":36,
            "packet_time_samples":401,"packet_time_interval":[0,1],"packet_x1_slice_samples":241,
            "power_series_partial_sum_max":4096,"graph_cutoff_max":512,
            "finite_tail_bound_cutoffs":[4,16,64],"symbol_h_exponents":[2,11]},
        "non_claims":["These plots do not constitute Lean verification or new physical evidence.",
            "Finite partial sums do not prove infinite-series convergence.",
            "The symbolic threshold classification uses the p-series criterion explained in the atlas.",
            "No unrestricted quadratic L2 rate, sampled-grid model or spectral-exponential identification is claimed."]},
    "randomness":{"used":False,"generator":"none","seed":None},
    "run":{"started_at":STAMP,"runtime_seconds":time.monotonic()-START,"exit_status":0},
    "outputs":outputs,"checks":checks,
    "result":"Implementation and finite assertions verified in the recorded ranges, conditional on stated numerical tolerances for floating calculations.",
    "residual_risks":["Floating evaluations are not interval certified.",
        "Hurwitz-zeta evaluations rely on SciPy.","Figures illustrate selected examples rather than exhaust arbitrary fields."]}
(ROOT/"evidence"/"figure_checks.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"figures":12,"checks":len(checks),"all_passed":all(c["passed"] for c in checks),
                  "runtime_seconds":manifest["run"]["runtime_seconds"]},indent=2))
