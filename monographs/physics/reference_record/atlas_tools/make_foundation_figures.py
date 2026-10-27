#!/usr/bin/env python3
"""Reproduce twelve foundations plates and their bounded computation record.

Run from the edition root: python tools/make_foundation_figures.py
Exact symbolic assertions check the displayed finite algebra. Floating checks
validate explicit examples, not universal theorems or Lean compilation.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import platform
import time
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.special import zeta
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

START = time.monotonic()
STAMP = dt.datetime.now(dt.timezone.utc).isoformat()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source" / "foundation_figures"
OUT.mkdir(parents=True, exist_ok=True)
(ROOT / "evidence" / "foundations").mkdir(parents=True, exist_ok=True)
TEAL, GOLD, LILAC = "#245D60", "#AD7842", "#7C738E"
INK, MUTED, PALE = "#212B34", "#58646B", "#EEF3F2"
CMAP = LinearSegmentedColormap.from_list("foundation", [GOLD, "#FAFBFA", TEAL])
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11,
    "axes.labelsize":11,"axes.titlesize":12.5,"axes.titlepad":13,
    "axes.labelcolor":INK,"text.color":INK,"axes.edgecolor":"#ADBAB9",
    "xtick.color":MUTED,"ytick.color":MUTED,"axes.spines.top":False,
    "axes.spines.right":False,"legend.frameon":False,"legend.fontsize":10,
    "lines.linewidth":2.2,"figure.facecolor":"white","axes.facecolor":"white",
    "savefig.facecolor":"white","pdf.fonttype":42,"ps.fonttype":42,
    "mathtext.fontset":"dejavusans"})
checks, outputs = [], []

def record(name, passed, detail):
    checks.append({"name":name,"passed":bool(passed),"detail":detail})
    if not passed:
        raise AssertionError(f"{name}: {detail}")

def save(fig, name):
    for ext in ("pdf", "png"):
        path = OUT / f"{name}.{ext}"
        metadata = {"Creator":"Komorebi foundations figure generator"}
        if ext == "pdf":
            metadata.update({"CreationDate":None,"ModDate":None})
        fig.savefig(path, dpi=190, bbox_inches="tight", pad_inches=.15,
                    metadata=metadata)
        outputs.append({"path":str(path.relative_to(ROOT)),
                        "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)

def grid(ax):
    ax.grid(True,color="#DDE5E3",linewidth=.65,alpha=.8)
    ax.set_axisbelow(True)

def matrix(ax, values, title, labels=None, vmax=None, fmt="g"):
    values=np.asarray(values,dtype=float)
    v=float(np.max(np.abs(values))) if vmax is None else vmax
    ax.imshow(values,cmap=CMAP,vmin=-v,vmax=v,interpolation="nearest")
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            value=values[row,col]
            text=labels[row][col] if labels is not None else format(value,fmt)
            ax.text(col,row,text,ha="center",va="center",fontsize=13,
                    color="white" if abs(value)>.64*v else INK)
    ax.set_xticks(range(values.shape[1]),range(1,values.shape[1]+1))
    ax.set_yticks(range(values.shape[0]),range(1,values.shape[0]+1))
    ax.set_title(title)
    for spine in ax.spines.values(): spine.set_visible(False)

# 01. Orthogonal coordinates retain the complex state, not only populations.
v=sp.Matrix([1,sp.I,2,-sp.I])/sp.sqrt(7)
P=sp.diag(1,1,0,0); Q=sp.eye(4)-P
record("exact packet reconstruction and norm separation",
       P*P==P and Q*Q==Q and P*Q==sp.zeros(4) and P*v+Q*v==v
       and sp.simplify((v.H*v)[0])==1
       and sp.simplify((v.H*P*v)[0])==sp.Rational(2,7),
       "C^4, psi=(1,i,2,-i)/sqrt(7), P=diag(1,1,0,0), Q=I-P.")
vn=np.array(v,dtype=complex).ravel()
fig,axs=plt.subplots(1,2,figsize=(9,4.25),layout="constrained")
x=np.arange(1,5)
axs[0].bar(x-.16,vn.real,.31,color=TEAL,label="real part")
axs[0].bar(x+.16,vn.imag,.31,color=GOLD,label="imaginary part")
axs[0].axvline(2.5,color=MUTED,ls="--",lw=1)
axs[0].axhline(0,color=MUTED,lw=.8)
axs[0].set(xticks=x,xlabel="coordinate",ylabel="complex amplitude components",
           title="The two packets retain every coordinate",ylim=(-.53,.92))
axs[0].text(1.5,.82,"packet A",ha="center",color=TEAL)
axs[0].text(3.5,.82,"packet B",ha="center",color=TEAL)
axs[0].legend(loc="lower left")
axs[1].bar([0,1],[2/7,5/7],color=[TEAL,GOLD],width=.6)
axs[1].set(xticks=[0,1],xticklabels=["A: coordinates 1, 2","B: coordinates 3, 4"],
           ylim=(0,1),ylabel="squared packet norm",title="Orthogonality makes the weights add")
for j,text in enumerate(["2/7","5/7"]): axs[1].text(j,[2/7,5/7][j]+.035,text,ha="center",fontsize=13)
axs[1].axhline(1,color=LILAC,ls=":",label="total = 1");axs[1].legend(loc="upper left")
grid(axs[1]);save(fig,"01_packets")

# 02. The coarse block norms are descriptive magnitudes, not probabilities.
H=sp.Matrix([[0,1,0,2],[1,0,-1,0],[0,-1,0,1],[2,0,1,0]])
corners=[R*H*S for R in (P,Q) for S in (P,Q)]
record("exact operator corner reconstruction",sum(corners,sp.zeros(4))==H,
       "Four corners of the displayed 4x4 integer Hermitian matrix; exact SymPy arithmetic.")
fig,axs=plt.subplots(1,2,figsize=(8.9,4.25),layout="constrained")
matrix(axs[0],H,"One operator, four coarse corners")
axs[0].axhline(1.5,color=INK,lw=2);axs[0].axvline(1.5,color=INK,lw=2)
axs[0].set(xlabel="input coordinate",ylabel="output coordinate")
strength=np.array([[sum(abs(H[i,j])**2 for i in rows for j in cols)
                    for cols in ([0,1],[2,3])] for rows in ([0,1],[2,3])],float)
matrix(axs[1],strength,"Squared Frobenius norms of the corners",vmax=5)
axs[1].set(xticks=[0,1],xticklabels=["A","B"],yticks=[0,1],yticklabels=["A","B"],
           xlabel="input packet",ylabel="output packet")
save(fig,"02_corners")

# 03. Exact two-level coherent exchange, independently checked by expm.
t=np.linspace(0,2*np.pi,601)
sx=np.array([[0,1],[1,0]],complex)
state=np.column_stack([np.cos(t),-1j*np.sin(t)])
curr=2*np.imag(np.conj(state[:,1])*state[:,0])
sample=np.linspace(0,2*np.pi,25)
expm_error=max(np.linalg.norm(expm(-1j*s*sx)@np.array([1,0])-np.array([np.cos(s),-1j*np.sin(s)])) for s in sample)
balance_error=float(np.max(np.abs(curr-np.sin(2*t))))
record("coherent current orientation and independent evolution",expm_error<2e-14 and balance_error<2e-14,
       {"g":1,"time_interval":[0,float(2*np.pi)],"plot_samples":601,
        "matrix_exponential_samples":25,"expm_max_error":float(expm_error),
        "current_max_error":balance_error,"tolerance":2e-14})
fig,axs=plt.subplots(2,1,figsize=(8.8,5.2),sharex=True,layout="constrained")
axs[0].plot(t,np.cos(t)**2,color=TEAL,label=r"$p_1=\cos^2t$")
axs[0].plot(t,np.sin(t)**2,color=GOLD,label=r"$p_2=\sin^2t$")
axs[0].set(ylabel="population",ylim=(-.06,1.4),title="Coherent exchange reverses direction");axs[0].legend(ncol=2,loc="upper right")
axs[1].plot(t,curr,color=TEAL,label=r"$J_{2\leftarrow1}=\dot p_2$")
axs[1].plot(t,-curr,color=GOLD,ls="--",label=r"$J_{1\leftarrow2}=\dot p_1$")
axs[1].axhline(0,color=MUTED,lw=.8);axs[1].set(xlabel="time t  (g = 1)",ylabel="signed current",ylim=(-1.2,1.55))
axs[1].legend(ncol=2,loc="upper right")
for ax in axs:grid(ax)
save(fig,"03_coherent_current")

# 04. Antisymmetric abstract current example and exact coarse aggregation.
J=sp.Matrix([[0,-3,0,sp.Rational(1,2)],[3,0,-2,0],[0,2,0,-1],[-sp.Rational(1,2),0,1,0]])
R=sp.Matrix([[1,1,0,0],[0,0,1,1]])
K=sp.Matrix([[0,-1,1,0],[1,0,-1,0],[-1,1,0,0],[0,0,0,0]])
record("exact coarse balance and invisible cycle",
       J+J.T==sp.zeros(4) and R*J*sp.ones(4,1)==R*J*R.T*sp.ones(2,1)
       and K+K.T==sp.zeros(4) and K*sp.ones(4,1)==sp.zeros(4,1),
       {"fine_current_matrix":str(J),"fine_divergence":str(J*sp.ones(4,1)),
        "coarse_current":str(R*J*R.T),"cycle_matrix":str(K),
        "scope":"Abstract instantaneous current arrays; no Hamiltonian realization inferred."})
fig,axs=plt.subplots(1,2,figsize=(9,4.6),layout="constrained")
pos={1:(.25,.75),2:(.25,.25),3:(.75,.25),4:(.75,.75)}
ax=axs[0];ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
ax.add_patch(Rectangle((.09,.10),.32,.79,facecolor=PALE,edgecolor=TEAL,lw=1))
ax.add_patch(Rectangle((.59,.10),.32,.79,facecolor="#F8F0E6",edgecolor=GOLD,lw=1))
ax.text(.25,.96,"A = {1, 2}",ha="center",color=TEAL);ax.text(.75,.96,"B = {3, 4}",ha="center",color=GOLD)
for node,(xx,yy) in pos.items():
    ax.add_patch(Circle((xx,yy),.06,facecolor="white",edgecolor=INK,lw=1.1))
    ax.text(xx,yy,str(node),ha="center",va="center",fontsize=12)
for source,target,label,lpos in [(1,2,"3",(.16,.50)),(2,3,"2",(.50,.29)),(3,4,"1",(.84,.50)),(4,1,"1/2",(.50,.79))]:
    s=np.array(pos[source]);e=np.array(pos[target]);d=(e-s)/np.linalg.norm(e-s)
    ax.annotate("",xy=e-.07*d,xytext=s+.07*d,arrowprops={"arrowstyle":"->","lw":1.8,"color":INK})
    ax.text(*lpos,label,ha="center",va="center",fontsize=12)
ax.set_title("Fine currents include internal exchange")
ax=axs[1];ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
for xx,label,col in [(.22,"A",TEAL),(.78,"B",GOLD)]:
    ax.add_patch(Circle((xx,.55),.14,facecolor=PALE,edgecolor=col,lw=1.6))
    ax.text(xx,.55,label,ha="center",va="center",fontsize=19,color=col)
ax.annotate("",xy=(.62,.55),xytext=(.38,.55),arrowprops={"arrowstyle":"->","lw":2,"color":INK})
ax.text(.50,.66,"3/2",ha="center",fontsize=14)
ax.text(.22,.28,r"$\dot p_A=-3/2$",ha="center",fontsize=13)
ax.text(.78,.28,r"$\dot p_B=+3/2$",ha="center",fontsize=13)
ax.text(.5,.11,"Only net boundary transfer remains.",ha="center",color=MUTED)
ax.set_title("Coarse balance cancels internal currents")
save(fig,"04_coarse_balance")

# 05. Stationary physical vector, rotating coordinate atlas.
theta=sp.symbols("theta",real=True)
U=sp.Matrix([[sp.cos(theta),-sp.sin(theta)],[sp.sin(theta),sp.cos(theta)]])
Gamma=sp.simplify(U.T*U.diff(theta));phi=U.T*sp.Matrix([1,0])
record("exact moving-frame connection",
       sp.simplify(phi.diff(theta)+Gamma*phi)==sp.zeros(2,1)
       and sp.simplify(Gamma+Gamma.T)==sp.zeros(2),
       "theta=t, laboratory A=0, Gamma=U^T U'=[[0,-1],[1,0]], phi'= -Gamma phi.")
fig,axs=plt.subplots(1,2,figsize=(9,4.3),layout="constrained")
ax=axs[0];ax.set_aspect("equal");ang=.65
ax.arrow(0,0,.96,0,width=.008,head_width=.06,color=INK,length_includes_head=True)
ax.text(.65,-.14,r"fixed $\psi=e_1$",color=INK)
for xx,yy,label,col in [(np.cos(ang),np.sin(ang),r"$u_1(t)$",TEAL),(-np.sin(ang),np.cos(ang),r"$u_2(t)$",GOLD)]:
    ax.arrow(0,0,xx,yy,width=.007,head_width=.06,color=col,length_includes_head=True)
    ax.text(xx*1.12,yy*1.12,label,ha="center",color=col)
arc=np.linspace(0,ang,50);ax.plot(.35*np.cos(arc),.35*np.sin(arc),color=MUTED,lw=1.2)
ax.text(.40,.14,r"$t$",color=MUTED)
ax.set(xlim=(-.9,1.15),ylim=(-.23,1.16),title="The frame moves while the state stays fixed");ax.axis("off")
tt=np.linspace(0,np.pi,401)
axs[1].plot(tt,np.cos(tt)**2,color=TEAL,label=r"$p_1(t)=\cos^2t$")
axs[1].plot(tt,np.sin(tt)**2,color=GOLD,label=r"$p_2(t)=\sin^2t$")
axs[1].set(xlabel="frame angle t",ylabel="moving-atlas population",ylim=(-.04,1.4),title="The connection accounts for the change")
axs[1].legend(loc="upper center");grid(axs[1]);save(fig,"05_moving_frame")

# 06. Same diagonal populations need not determine a Hamiltonian current.
rho_plus=sp.Matrix([[1,sp.I],[-sp.I,1]])/2
rho_minus=rho_plus.conjugate();Xs=sp.Matrix([[0,1],[1,0]])
dp=[(-sp.I*(Xs*rho-rho*Xs))[1,1] for rho in (rho_plus,rho_minus)]
record("exact coherence-dependent current",dp==[1,-1] and rho_plus.det()==0 and rho_minus.det()==0,
       "rho+ from (1,-i)/sqrt2 and rho- from (1,i)/sqrt2; both p=(1/2,1/2), but p2'=+1,-1 for H=sigma_x.")
# Symmetric jump operators sqrt(k)|1><2| and sqrt(k)|2><1|.
a,b=sp.symbols("a b",real=True);rhod=sp.diag(a,b)
L12=sp.Matrix([[0,1],[0,0]]);L21=L12.T
diss=sum((L*rhod*L.H-(L.H*L*rhod+rhod*L.H*L)/2 for L in (L12,L21)),sp.zeros(2))
record("exact symmetric Lindblad population reduction",diss==sp.diag(b-a,a-b),
       "k=1, diagonal rho, two rank-one jump operators; the dissipative derivative is diag(p2-p1,p1-p2).")
fig,axs=plt.subplots(1,2,figsize=(9,4.3),layout="constrained")
tt=np.linspace(0,5,501)
axs[0].plot(tt,np.cos(tt)**2,color=TEAL,label="Hamiltonian: coherent exchange")
axs[0].plot(tt,.5+.5*np.exp(-2*tt),color=GOLD,label="symmetric jumps: rate k = 1")
axs[0].axhline(.5,color=MUTED,lw=.8,ls=":")
axs[0].set(xlabel="time",ylabel=r"$p_1(t)$",ylim=(-.04,1.4),title="Two different evolution laws")
axs[0].legend(loc="upper right",fontsize=8.7);grid(axs[0])
axs[1].bar([0,1,2],[1,-1,0],color=[TEAL,GOLD,LILAC],width=.6)
axs[1].axhline(0,color=MUTED,lw=.8)
axs[1].set(xticks=[0,1,2],xticklabels=[r"$\rho_+$",r"$\rho_-$","classical"],
           ylim=(-1.25,1.3),ylabel=r"initial derivative $\dot p_2$",title="All three have p₁ = p₂ = 1/2")
axs[1].text(.5,.06,"opposite coherences",transform=axs[1].transAxes,ha="center",color=MUTED,fontsize=10)
save(fig,"06_density_and_jumps")

# 07. Joint populations differ while both subsystem marginals agree.
bell=sp.Matrix([1,0,0,1])/sp.sqrt(2)
rhob=bell*bell.H
joint=np.array([[.5,0],[0,.5]]);independent=np.full((2,2),.25)
rhoA=sp.Matrix(2,2,lambda i,j:sum(rhob[2*i+k,2*j+k] for k in range(2)))
record("exact Bell marginal and finite tensor population",rhoA==sp.eye(2)/2
       and np.array_equal(joint.sum(axis=0),independent.sum(axis=0))
       and np.array_equal(joint.sum(axis=1),independent.sum(axis=1)),
       "Basis |00>,|01>,|10>,|11>; Bell pure state versus maximally mixed product I4/4 have equal computational-basis marginals and different joint populations.")
fig,axs=plt.subplots(1,2,figsize=(8.6,4.2),layout="constrained")
for ax,arr,title in zip(axs,[joint,independent],[r"Bell state $(|00\rangle+|11\rangle)/\sqrt{2}$",r"Product mixed state $(I_2/2)\otimes(I_2/2)$"]):
    matrix(ax,arr,title,vmax=.5,fmt=".2f")
    ax.set(xticks=[0,1],xticklabels=["B = 0","B = 1"],yticks=[0,1],yticklabels=["A = 0","A = 1"],
           xlabel="column sums: 1/2, 1/2",ylabel="row sums: 1/2, 1/2")
save(fig,"07_tensor_marginals")

# 08. Positive effects with a completely explicit four-dimensional dilation.
Fp=sp.diag(sp.Rational(4,5),sp.Rational(1,5));Fm=sp.eye(2)-Fp
Vp=sp.diag(2/sp.sqrt(5),1/sp.sqrt(5));Vm=sp.diag(1/sp.sqrt(5),2/sp.sqrt(5))
V=Vp.col_join(Vm);Pi=sp.diag(1,1,0,0)
record("exact positive-effect dilation",V.H*V==sp.eye(2) and V.H*Pi*V==Fp
       and Fp*Fp!=Fp and Fp*Fm!=sp.zeros(2),
       "F+=diag(4/5,1/5), F-=I-F+; V=(sqrt(F+),sqrt(F-))^T; Pi+ selects first two of four output coordinates.")
fig,axs=plt.subplots(1,2,figsize=(9,4.3),layout="constrained")
tt=np.linspace(0,np.pi,401)
axs[0].plot(tt,.8*np.cos(tt)**2+.2*np.sin(tt)**2,color=TEAL,label=r"$p_+=\langle\psi,F_+\psi\rangle$")
axs[0].plot(tt,.64*np.cos(tt)**2+.04*np.sin(tt)**2,color=GOLD,ls="--",label=r"$\|F_+\psi\|^2$")
axs[0].set(xlabel=r"state angle $\theta$",ylabel="weight",ylim=(0,1),title="An effect is not a projector")
axs[0].legend(loc="upper center");grid(axs[0])
matrix(axs[1],np.array(V,float),"An isometry into four channel coordinates",vmax=1,
       labels=[[r"$2/\sqrt{5}$","0"],["0",r"$1/\sqrt{5}$"],[r"$1/\sqrt{5}$","0"],["0",r"$2/\sqrt{5}$"]])
axs[1].axhline(1.5,color=INK,lw=2)
axs[1].set(xlabel="input coordinate",ylabel="channel output coordinate")
save(fig,"08_positive_effects")

# 09. Same cutoff, different topology. Infinite tails use Hurwitz zeta.
N=np.unique(np.logspace(0,3,120).astype(int))
fixed=np.sqrt(zeta(2,N+1)/zeta(2));resolvent=1/np.sqrt((N+1)**2+1)
record("cutoff curves and tail benchmark",np.all(np.diff(fixed)<0)
       and abs(fixed[0]**2-(1-1/zeta(2)))<2e-15,
       {"diagonal_spectrum":"lambda_n=n, n>=1","state":"a_n=n^-1/sqrt(zeta(2))",
        "cutoffs_min_max":[1,1000],"cutoff_count":len(N),"fixed_error_N1000":float(fixed[-1]),
        "tail_evaluation":"SciPy Hurwitz zeta, not a finite sum masquerading as an infinite tail",
        "operator_norm_value_1":"Analytic all-N argument in atlas, not numerically inferred."})
fig,ax=plt.subplots(figsize=(8.8,4.5),layout="constrained")
ax.loglog(N,np.ones(len(N)),color=INK,label=r"unitary error in operator norm: exactly 1")
ax.loglog(N,fixed,color=TEAL,label=r"unitary error on one fixed state $a_n\propto n^{-1}$")
ax.loglog(N,resolvent,color=GOLD,label=r"resolvent error in operator norm")
ax.set(xlabel="cutoff N",ylabel="error norm",title="Strong convergence and norm convergence ask different questions",ylim=(5e-4,3.5))
ax.legend(loc="lower left");grid(ax);save(fig,"09_cutoff_topology")

# 10. Nested state, form, and operator domains for lambda_n=n.
exponents=[.4,.75,1.25,1.75];indices=np.arange(1,4097,dtype=float)
sampleN=np.unique(np.logspace(0,np.log10(4096),100).astype(int))
fig,axs=plt.subplots(1,3,figsize=(10.1,4.35),layout="constrained")
for weight,ax,title in zip([0,1,2],axs,["State norm squared","Form energy","Operator image norm squared"]):
    for s,col in zip(exponents,[MUTED,GOLD,LILAC,TEAL]):
        partial=np.cumsum(indices**(weight-2*s))
        ax.loglog(sampleN,partial[sampleN-1],color=col,label=f"s = {s:g}")
    ax.set(xlabel="partial-sum bound N",title=title);grid(ax)
axs[0].set_ylabel("partial sum");axs[0].legend(loc="upper left",fontsize=9)
record("power-law partial-sum implementation",all(np.all(np.diff(np.cumsum(indices**(q-2*s)))>0) for q in [0,1,2] for s in exponents),
       {"s_values":exponents,"weights":[0,1,2],"partial_sum_max":4096,
        "classification":"State s>1/2; form s>1; operator s>3/2, proved by the p-series criterion in the atlas, not by bounded sums."})
save(fig,"10_weighted_domains")

# 11. Graph tails of one domain vector. Orthogonal coordinate error vs image.
N=np.unique(np.logspace(0,3,120).astype(int))
e0=np.sqrt(zeta(4,N+1)/zeta(4));eH=np.sqrt(zeta(2,N+1)/zeta(4));eg=np.sqrt(e0**2+eH**2)
record("graph tail identity and monotonicity",np.all(np.diff(eg)<0)
       and np.max(np.abs(eg**2-e0**2-eH**2))<2e-15,
       {"state":"a_n=n^-2/sqrt(zeta(4))","lambda_n":"n, n>=1",
        "cutoff_min_max":[1,1000],"l2_tail_N1000":float(e0[-1]),
        "graph_tail_N1000":float(eg[-1]),"tolerance":2e-15})
fig,ax=plt.subplots(figsize=(8.8,4.5),layout="constrained")
ax.loglog(N,e0,color=TEAL,label=r"state error $\|a-P_Na\|$")
ax.loglog(N,eH,color=LILAC,ls="--",label=r"image error $\|H(a-P_Na)\|$")
ax.loglog(N,eg,color=GOLD,label=r"graph error $\|a-P_Na\|_H$")
ax.set(xlabel="cutoff N",ylabel="tail norm",title="Applying an unbounded operator makes the tail more expensive")
ax.legend(loc="lower left");grid(ax);save(fig,"11_graph_tails")

# 12. The finite pointwise obstruction and a nonzero exact matrix derivation.
D=sp.Matrix([[-1,1],[1,-1]]);e=sp.Matrix([1,0]);point_res=D*e-2*sp.diag(*e)*(D*e)
X=sp.diag(1,0);Kmat=Xs;delta=lambda B:sp.I*(Kmat*B-B*Kmat)
basis=[sp.Matrix(2,2,lambda a,b:1 if (a,b)==(i,j) else 0) for i in range(2) for j in range(2)]
record("matrix derivation exact algebra and failed pointwise difference",
       point_res==sp.Matrix([1,1]) and delta(X)!=sp.zeros(2)
       and all(delta(A*B)==delta(A)*B+A*delta(B) for A in basis for B in basis)
       and all(sp.trace(delta(A)*B)==-sp.trace(A*delta(B)) for A in basis for B in basis),
       {"pointwise_difference_matrix":str(D),"idempotent":"e1=(1,0)",
        "Leibniz_failure_on_e1_squared":str(point_res),"matrix_generator":"sigma_x",
        "matrix_basis_pairs":16,"arithmetic":"exact Gaussian integers",
        "scope":"Finite basis checks reproduce the worked 2x2 algebra; general proof is the commutator expansion."})
fig,axs=plt.subplots(1,2,figsize=(9,4.3),layout="constrained")
x=np.array([0,1]);axs[0].bar(x-.17,[-1,1],.33,color=TEAL,label=r"$D(e_1^2)$")
axs[0].bar(x+.17,[-2,0],.33,color=GOLD,label=r"$2e_1D(e_1)$")
axs[0].axhline(0,color=MUTED,lw=.8);axs[0].set(xticks=[0,1],xticklabels=["coordinate 1","coordinate 2"],
       ylim=(-2.3,1.8),ylabel="coordinate value",title="Pointwise finite differences fail Leibniz")
axs[0].legend(loc="upper right")
matrix(axs[1],np.array(delta(X)/sp.I,float),r"$\delta_BX=i[B,X]$: imaginary coefficients",vmax=1)
axs[1].set(xlabel="input coordinate",ylabel="output coordinate")
save(fig,"12_matrix_derivations")

record("complete plate inventory",len(outputs)==24,"Twelve PDF plates and twelve PNG previews; deterministic inputs and no random sampling.")
path=Path(__file__).resolve()
manifest={"schema_version":1,"claim_id":"physics-foundations-atlas-finite-examples-v0.2.0",
    "repository":{"commit":"not applicable: standalone publication staging directory","dirty":True},
    "command":"python tools/make_foundation_figures.py",
    "environment":{"software":[f"Python {platform.python_version()}",f"NumPy {np.__version__}",
        f"SciPy {scipy.__version__}",f"SymPy {sp.__version__}",f"Matplotlib {matplotlib.__version__}"],
        "hardware":platform.machine()},
    "mathematics":{"assertion_tested":"The twelve plotted examples satisfy the exact finite identities and floating consistency checks stated in this manifest.",
        "coefficient_domain":"Exact rationals and Gaussian rational matrices in SymPy; IEEE double and complex128 for sampled evolution and curves.",
        "conventions":"Inner product conjugate-linear in first entry; column states; J_target<-source; A=-iH; hbar=1; diagonal model lambda_n=n for n>=1; graph norm sqrt(||a||²+||Ha||²).",
        "inputs":[{"path":"tools/make_foundation_figures.py","sha256":hashlib.sha256(path.read_bytes()).hexdigest()}],
        "bounds":{"finite_state_dimensions":[2,4],"matrix_exponential_samples":25,
            "coherent_plot_samples":601,"coherent_interval":[0,float(2*np.pi)],
            "maximum_partial_sum":4096,"maximum_tail_cutoff":1000,
            "matrix_basis_pairs":16,"power_exponents":exponents},
        "non_claims":["No Lean source is compiled by this figure generator.",
            "Finite samples and partial sums do not prove all-time evolution or infinite-series convergence.",
            "The all-N cutoff norm and domain thresholds are justified by the analytic arguments in the atlas.",
            "The four-node current array is an abstract balance example, not an asserted physical Hamiltonian realization.",
            "No new empirical physics, general convergence rate, or universal classification follows from these plots."]},
    "randomness":{"used":False,"generator":"none","seed":None},
    "run":{"started_at":STAMP,"runtime_seconds":time.monotonic()-START,"exit_status":0},
    "outputs":outputs,"checks":checks,
    "result":"Implementation and finite assertions verified in the recorded ranges, conditional on the stated numerical tolerances for floating calculations.",
    "residual_risks":["Floating calculations are not interval certified.",
        "Infinite tail evaluations rely on SciPy Hurwitz zeta.",
        "Exact symbolic checks rely on SymPy and do not constitute proof-assistant validation."]}
(ROOT/"evidence"/"foundations"/"figure_checks.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"figures":12,"checks":len(checks),"all_passed":all(c["passed"] for c in checks),"runtime_seconds":manifest["run"]["runtime_seconds"]},indent=2))
