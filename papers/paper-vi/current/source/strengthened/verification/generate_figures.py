from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# 1. Packet block transfer norms
A = np.array([
    [-0.8, 0.35, 0.0, 0.0],
    [0.15, -0.6, 0.25, 0.0],
    [0.0, 0.2, -0.5, 0.3],
    [0.0, 0.0, 0.1, -0.4],
])
P = [np.diag([1,1,0,0]), np.diag([0,0,1,1])]
for t in [0.0, 0.8, 2.0]:
    T = expm(t*A)
    B = np.array([[np.linalg.norm(P[b]@T@P[a],2) for a in range(2)] for b in range(2)])
    fig, ax = plt.subplots(figsize=(4.8,4.0))
    edges=np.arange(3)
    im=ax.pcolormesh(edges,edges,B,shading="flat")
    for i in range(2):
        for j in range(2):
            ax.text(j+0.5,i+0.5,f"{B[i,j]:.3f}",ha="center",va="center")
    ax.set_xticks([0.5,1.5], labels=["input 1","input 2"])
    ax.set_yticks([0.5,1.5], labels=["output 1","output 2"])
    ax.set_xlim(0,2)
    ax.set_ylim(2,0)
    ax.set_title(f"Packet block norms at t = {t:g}")
    fig.tight_layout()
    fig.savefig(OUT/f"packet_blocks_t{str(t).replace('.','_')}.pdf")
    plt.close(fig)

# 2. Duhamel defect and linear bound
Af=np.array([[-1.0,0.4],[0.0,-0.3]])
C=np.array([[1.0,0.7]])
Ac=np.array([[-0.55]])
Delta=C@Af-Ac@C
ts=np.linspace(0,5,240)
defects=[]
bounds=[]
for t in ts:
    d=C@expm(t*Af)-expm(t*Ac)@C
    defects.append(np.linalg.norm(d,2))
    # direct Duhamel bound using exact scalar growth estimates from norms
    bounds.append(t*np.linalg.norm(Delta,2)*np.exp(t*max(np.linalg.norm(Af,2),np.linalg.norm(Ac,2))))
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.plot(ts,defects,label="semigroup defect")
ax.plot(ts,bounds,label="Duhamel bound")
ax.set_xlabel("time")
ax.set_ylabel("operator norm")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"duhamel_defect.pdf")
plt.close(fig)

# 3. Exact and perturbed Markov lumping
K=np.array([
 [0.55,0.25,0.10,0.10],
 [0.25,0.55,0.10,0.10],
 [0.10,0.10,0.60,0.20],
 [0.10,0.10,0.20,0.60],
])
Cpart=np.array([[1,1,0,0],[0,0,1,1]],dtype=float)
Kbar=np.array([[0.8,0.2],[0.2,0.8]])
p=np.array([0.7,0.1,0.1,0.1])
Kp=K.copy()
Kp[:,1]+=np.array([0.01,-0.01,-0.01,0.01])
steps=np.arange(0,26)
exact=[]; coarse=[]; pert=[]
for n in steps:
    exact.append((Cpart@np.linalg.matrix_power(K,n)@p)[0])
    coarse.append((np.linalg.matrix_power(Kbar,n)@Cpart@p)[0])
    pert.append((Cpart@np.linalg.matrix_power(Kp,n)@p)[0])
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.plot(steps,exact,label="fine then coarse")
ax.plot(steps,coarse,label="coarse model")
ax.plot(steps,pert,label="perturbed fine model")
ax.set_xlabel("step")
ax.set_ylabel("mass in coarse packet 1")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"markov_lumping.pdf")
plt.close(fig)

# 4. Martingale packet energies on a finite probability space
pi=np.array([0.08,0.12,0.18,0.22,0.16,0.24])
f=np.array([-1.2,-0.3,0.4,1.5,0.8,-0.6])
parts=[[[0,1,2,3,4,5]],[[0,1,2],[3,4,5]],[[0,1],[2],[3,4],[5]],[[0],[1],[2],[3],[4],[5]]]
def Pmat(part):
    P=np.zeros((6,6))
    for B in part:
        w=pi[B]/pi[B].sum()
        for i in B:
            P[i,B]=w
    return P
Ps=[Pmat(x) for x in parts]
Ds=[Ps[0]]+[Ps[i]-Ps[i-1] for i in range(1,len(Ps))]
energies=[np.sum(pi*(D@f)**2) for D in Ds]
fig,ax=plt.subplots(figsize=(6.0,3.8))
ax.bar(np.arange(len(energies)),energies)
ax.set_xticks(np.arange(len(energies)),labels=["mean","level 1","level 2","level 3"])
ax.set_ylabel("weighted energy")
fig.tight_layout()
fig.savefig(OUT/"martingale_packet_energy.pdf")
plt.close(fig)

# 5. Bayesian block sufficiency and within block change
p=np.array([0.22,0.18,0.15,0.10,0.20,0.15])
lam=np.array([1.0,1.0,1.0,0.35,1.1,1.8])
post=lam*p/(lam@p)
idx=np.arange(len(p))
fig,ax=plt.subplots(figsize=(6.4,4.0))
w=0.38
ax.bar(idx-w/2,p,w,label="prior")
ax.bar(idx+w/2,post,w,label="posterior")
ax.axvline(2.5,linewidth=1)
ax.set_xticks(idx)
ax.set_xlabel("fine state")
ax.set_ylabel("probability")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"bayesian_packets.pdf")
plt.close(fig)

# 6. Bayesian flow
p0=np.array([0.25,0.35,0.25,0.15])
g=np.array([-0.6,0.1,0.8,1.2])
ts=np.linspace(0,8,240)
traj=np.array([np.exp(t*g)*p0/np.sum(np.exp(t*g)*p0) for t in ts])
fig,ax=plt.subplots(figsize=(6.3,4.0))
for i in range(4): ax.plot(ts,traj[:,i],label=f"state {i+1}")
ax.set_xlabel("time")
ax.set_ylabel("posterior mass")
ax.legend(ncol=2)
fig.tight_layout()
fig.savefig(OUT/"bayesian_flow.pdf")
plt.close(fig)

# 7. Fractional multipliers
lamgrid=np.linspace(0,16,300)
fig,ax=plt.subplots(figsize=(6.3,4.0))
for alpha in [0.25,0.5,0.75,1.0]:
    ax.plot(lamgrid,np.exp(-np.power(lamgrid,alpha)),label=fr"$\alpha={alpha:g}$")
ax.set_xlabel("spectral value")
ax.set_ylabel("multiplier at t = 1")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"fractional_multipliers.pdf")
plt.close(fig)

# 8. Green kernel and discrete nodal values
x=np.linspace(0,1,300)
y=0.37
G=np.minimum(x,y)-x*y
n=16; h=1/(n+1); xi=np.arange(1,n+1)*h
L=(2*np.eye(n)-np.eye(n,k=1)-np.eye(n,k=-1))/h**2
j=int(round(y/h))-1; j=max(0,min(n-1,j)); yj=xi[j]
Gj=np.minimum(x,yj)-x*yj
col=np.linalg.inv(L)[:,j]/h
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.plot(x,Gj,label="continuum section")
ax.scatter(xi,col,label="scaled discrete inverse")
ax.set_xlabel("x")
ax.set_ylabel("Green value")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"green_kernel.pdf")
plt.close(fig)

# 9. Memory kernel and spectral truncation
mu=np.array([-0.25,-0.8,-2.2,-5.0])
weights=np.array([0.50,-0.30,0.16,0.08])
ts=np.linspace(0,16,400)
full=sum(w*np.exp(m*ts) for w,m in zip(weights,mu))
trunc=sum(w*np.exp(m*ts) for w,m in zip(weights[:2],mu[:2]))
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.plot(ts,full,label="full kernel")
ax.plot(ts,trunc,label="two mode approximation")
ax.plot(ts,np.abs(full-trunc),label="absolute error")
ax.set_xlabel("time")
ax.set_ylabel("kernel value")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"memory_compression.pdf")
plt.close(fig)

# 10. Survival and cause specific densities
A=np.array([[-0.45,0.12,0.00],[0.25,-0.50,0.18],[0.00,0.20,-0.42]])
p0=np.array([1.0,0.0,0.0])
a=-np.ones(3)@A
# split exit rates into two causes
cause1=np.array([0.12,0.08,0.12])
cause2=a-cause1
ts=np.linspace(0,18,300)
S=[]; f1=[]; f2=[]
for t in ts:
    pt=expm(t*A)@p0
    S.append(pt.sum())
    f1.append(cause1@pt)
    f2.append(cause2@pt)
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.plot(ts,S,label="survival")
ax.plot(ts,f1,label="cause 1 density")
ax.plot(ts,f2,label="cause 2 density")
ax.set_xlabel("time")
ax.set_ylabel("value")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"survival_causes.pdf")
plt.close(fig)

print(f"generated {len(list(OUT.glob('*.pdf')))} vector figures")

# 11. Hermite packet multipliers
n=np.arange(0,18)
fig,ax=plt.subplots(figsize=(6.3,4.0))
for alpha in [0.5,1.0,1.5]:
    ax.plot(n,np.exp(-np.power(n,alpha)),marker='o',label=fr"$\alpha={alpha:g}$")
ax.set_xlabel("Hermite packet index")
ax.set_ylabel("multiplier at t = 1")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"ou_hermite.pdf")
plt.close(fig)

# 12. Bayesian information chain rule
p=np.array([0.18,0.12,0.20,0.16,0.14,0.20])
lam=np.array([0.6,1.5,0.9,1.8,0.5,1.2])
q=lam*p/(lam@p)
blocks=[np.array([0,1]),np.array([2,3,4]),np.array([5])]
pm=np.array([p[b].sum() for b in blocks])
qm=np.array([q[b].sum() for b in blocks])
coarse=float(np.sum(qm*np.log(qm/pm)))
local=[]
for b,ma,na in zip(blocks,pm,qm):
    pa=p[b]/ma
    qa=q[b]/na
    local.append(float(na*np.sum(qa*np.log(qa/pa))))
vals=[coarse]+local
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.bar(np.arange(len(vals)),vals)
ax.set_xticks(np.arange(len(vals)),labels=["coarse","packet 1","packet 2","packet 3"])
ax.set_ylabel("relative information contribution")
fig.tight_layout()
fig.savefig(OUT/"bayesian_information_split.pdf")
plt.close(fig)

# 13. Jordan memory versus diagonal memory
jts=np.linspace(0,8,300)
plain=np.exp(-jts)
jordan=np.exp(-jts)*(1+jts)
fig,ax=plt.subplots(figsize=(6.3,4.0))
ax.plot(jts,plain,label="simple exponential mode")
ax.plot(jts,jordan,label="Jordan mode")
ax.set_xlabel("time")
ax.set_ylabel("memory amplitude")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"jordan_memory.pdf")
plt.close(fig)

print(f"generated {len(list(OUT.glob('*.pdf')))} vector figures after strengthening")
