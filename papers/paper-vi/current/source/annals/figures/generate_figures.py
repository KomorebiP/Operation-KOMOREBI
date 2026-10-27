import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
from scipy.linalg import expm
from pathlib import Path

out = Path(__file__).resolve().parent

# 1. Packet semigroup block norms
A = np.array([[-0.8, 0.6, 0.0, 0.0], [0.2, -0.7, 0.4, 0.0], [0.0, 0.3, -0.9, 0.5], [0.0, 0.0, 0.2, -0.6]])
P = [np.diag([1,1,0,0]), np.diag([0,0,1,1])]
ts = np.linspace(0, 6, 160)
vals = {(b,a): [] for a in range(2) for b in range(2)}
for t in ts:
    T = expm(t*A)
    for b in range(2):
        for a in range(2):
            vals[(b,a)].append(np.linalg.norm(P[b] @ T @ P[a], 2))
plt.figure(figsize=(6.2, 3.8))
for key, y in vals.items():
    plt.plot(ts, y, label=f"block {key[1]+1} to {key[0]+1}")
plt.xlabel("time")
plt.ylabel("operator norm")
plt.legend(frameon=False, ncol=2)
plt.tight_layout()
plt.savefig(out / "packet_semigroup_blocks.pdf")
plt.close()

# 2. Refinement defect bound
Af = np.array([[-1.0,0.4,0.0],[0.2,-0.9,0.3],[0.0,0.1,-0.7]])
C = np.array([[1.0,0.0,0.0],[0.0,0.5,0.5]])
Ac_exact = np.array([[-1.0,0.2],[0.1,-0.65]])
# least squares coarse fit, then perturb to show nonzero defect
Ac = Ac_exact + np.array([[0.0,0.035],[-0.02,0.0]])
Delta = C@Af - Ac@C
err=[]; bd=[]
for t in ts:
    e=np.linalg.norm(C@expm(t*Af)-expm(t*Ac)@C,2)
    err.append(e)
    bd.append(t*np.exp(0.5*t)*np.linalg.norm(Delta,2))
plt.figure(figsize=(6.2,3.8))
plt.plot(ts,err,label="semigroup defect")
plt.plot(ts,bd,label="Duhamel bound")
plt.xlabel("time")
plt.ylabel("norm")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "refinement_defect.pdf")
plt.close()

# 3. Markov lumping
Q=np.array([[-0.8,0.2,0.0,0.0],[0.8,-0.7,0.3,0.0],[0.0,0.5,-0.6,0.2],[0.0,0.0,0.3,-0.2]])
# force column sums 0
for j in range(4): Q[j,j]=-np.sum(Q[:,j])+Q[j,j]
Cmark=np.array([[1,1,0,0],[0,0,1,1]],dtype=float)
# use least squares coarse generator
Qbar=Cmark@Q@Cmark.T@np.linalg.inv(Cmark@Cmark.T)
p0=np.array([1.0,0,0,0])
coarse=[]; direct=[]
for t in np.linspace(0,8,150):
    coarse.append(Cmark@expm(t*Q)@p0)
    direct.append(expm(t*Qbar)@(Cmark@p0))
coarse=np.array(coarse); direct=np.array(direct)
plt.figure(figsize=(6.2,3.8))
plt.plot(np.linspace(0,8,150),coarse[:,0],label="fine then coarse")
plt.plot(np.linspace(0,8,150),direct[:,0],label="coarse model")
plt.xlabel("time")
plt.ylabel("mass in first block")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "markov_lumping.pdf")
plt.close()

# 4. Martingale packet decomposition
x=np.arange(16)
f=np.array([0.2,0.5,0.1,0.8, 1.2,1.0,1.5,1.1, 0.4,0.2,0.7,0.5, 1.5,1.9,1.4,1.7])
def blockmean(v,b):
    return np.repeat([np.mean(v[i:i+b]) for i in range(0,len(v),b)],b)
P4=blockmean(f,4); P2=blockmean(f,2)
plt.figure(figsize=(6.2,3.8))
plt.step(x,f,where="mid",label="signal")
plt.step(x,P4,where="mid",label="coarse expectation")
plt.step(x,P2-P4,where="mid",label="martingale packet")
plt.xlabel("state")
plt.ylabel("value")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "martingale_packets.pdf")
plt.close()

# 5. Bayesian flow
g=np.array([-0.4,0.3,1.0])
p=np.array([0.45,0.35,0.20])
tb=np.linspace(0,8,180)
flow=np.array([np.exp(t*g)*p/np.sum(np.exp(t*g)*p) for t in tb])
plt.figure(figsize=(6.2,3.8))
for i in range(3): plt.plot(tb,flow[:,i],label=f"state {i+1}")
plt.xlabel("likelihood time")
plt.ylabel("posterior mass")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "bayesian_flow.pdf")
plt.close()

# 6. Sufficiency defect versus within block oscillation
osc=np.linspace(0,0.8,100)
p=np.array([0.2,0.3,0.25,0.25])
def update(L):
    q=L*p; return q/q.sum()
C2=np.array([[1,1,0,0],[0,0,1,1]],float)
defects=[]
for e in osc:
    L=np.array([1-e,1+e,2,2])
    fine=C2@update(L)
    coarse=np.array([1,2])*(C2@p); coarse=coarse/coarse.sum()
    defects.append(0.5*np.sum(np.abs(fine-coarse)))
plt.figure(figsize=(6.2,3.8))
plt.plot(osc,defects)
plt.xlabel("within block likelihood oscillation")
plt.ylabel("coarse posterior defect")
plt.tight_layout()
plt.savefig(out / "bayesian_sufficiency.pdf")
plt.close()

# 7. Fractional damping
lam=np.linspace(0,30,300)
plt.figure(figsize=(6.2,3.8))
for alpha in [0.35,0.6,1.0]:
    plt.plot(lam,np.exp(-0.8*np.power(lam,alpha)),label=rf"alpha {alpha}")
plt.xlabel("spectral value")
plt.ylabel("damping factor")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "fractional_damping.pdf")
plt.close()

# 8. Green kernel section
x=np.linspace(0,1,300); y0=0.38
G=np.minimum(x,y0)-x*y0
plt.figure(figsize=(6.2,3.8))
plt.plot(x,G,label="continuum kernel")
for n in [8,20]:
    h=1/(n+1); xi=np.arange(1,n+1)*h
    L=(2*np.eye(n)-np.eye(n,k=1)-np.eye(n,k=-1))/h**2
    j=np.argmin(np.abs(xi-y0))
    col=np.linalg.inv(L)[:,j]/h
    plt.plot(xi,col,"o",ms=3,label=f"grid {n}")
plt.xlabel("position")
plt.ylabel("Green value")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "green_kernel.pdf")
plt.close()

# 9. Feynman Kac
K=np.array([[0.7,0.2,0.1],[0.2,0.6,0.2],[0.1,0.2,0.7]])
V=np.array([0.0,0.35,0.9]); f=np.array([1.0,0.5,0.1])
M=np.diag(np.exp(-V))@K.T
vals=[]
u=f.copy()
for n in range(13):
    vals.append(u.copy()); u=M@u
vals=np.array(vals)
plt.figure(figsize=(6.2,3.8))
for i in range(3): plt.plot(range(13),vals[:,i],marker="o",ms=3,label=f"initial state {i+1}")
plt.xlabel("steps")
plt.ylabel("weighted terminal value")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "feynman_kac.pdf")
plt.close()

# 10. Memory kernel and approximation
D=np.array([[-0.45,0.25],[-0.15,-1.15]])
B=np.array([[0.8,-0.3]])
Cc=np.array([[0.6],[0.5]])
tm=np.linspace(0,12,240)
k=np.array([(B@expm(t*D)@Cc)[0,0] for t in tm])
approx=0.33*np.exp(-0.37*tm)+0.12*np.exp(-1.28*tm)
plt.figure(figsize=(6.2,3.8))
plt.plot(tm,k,label="exact memory")
plt.plot(tm,approx,label="two mode approximation")
plt.xlabel("time")
plt.ylabel("kernel")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "memory_kernel.pdf")
plt.close()

# 11. Survival and hazard
A=np.array([[-0.65,0.18,0.0],[0.4,-0.55,0.15],[0.0,0.25,-0.35]])
# ensure nonpositive column sums
for j in range(3):
    off=np.sum(A[:,j])-A[j,j]
    A[j,j]=-(off+np.array([0.15,0.12,0.20])[j])
p0=np.array([1.0,0,0])
tv=np.linspace(0,18,250)
S=[]; hz=[]
a=-np.ones(3)@A
for t in tv:
    pt=expm(t*A)@p0
    s=pt.sum(); S.append(s); hz.append((a@pt)/s)
plt.figure(figsize=(6.2,3.8))
plt.plot(tv,S,label="survival")
plt.plot(tv,hz,label="hazard")
plt.xlabel("time")
plt.ylabel("value")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(out / "survival_hazard.pdf")
plt.close()

# 12. Projective tower diagram
plt.figure(figsize=(7.0,3.2))
ax=plt.gca(); ax.axis("off")
ys=[0.8,0.53,0.26]; xs=[0.15,0.5,0.85]
for row,y in enumerate(ys):
    for col,xv in enumerate(xs):
        ax.text(xv,y,rf"$X_{{{col}}}$" if row==1 else (rf"$T_{{{col}}}(t)X_{{{col}}}$" if row==0 else rf"$A_{{{col}}}X_{{{col}}}$"),ha="center",va="center",bbox=dict(boxstyle="round",fc="white"))
for row,y in enumerate(ys):
    for col in range(2):
        ax.annotate("",xy=(xs[col],y),xytext=(xs[col+1],y),arrowprops=dict(arrowstyle="->"))
for col,xv in enumerate(xs):
    ax.annotate("",xy=(xv,ys[0]-0.06),xytext=(xv,ys[1]+0.06),arrowprops=dict(arrowstyle="->"))
    ax.annotate("",xy=(xv,ys[1]-0.06),xytext=(xv,ys[2]+0.06),arrowprops=dict(arrowstyle="->"))
ax.text(0.5,0.05,"coarsening horizontally and evolution vertically",ha="center")
plt.tight_layout()
plt.savefig(out / "projective_tower.pdf")
plt.close()

print("generated", len(list(out.glob('*.pdf'))), "vector figures")
