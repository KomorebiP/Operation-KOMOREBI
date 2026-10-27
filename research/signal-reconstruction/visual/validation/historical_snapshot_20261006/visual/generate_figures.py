#!/usr/bin/env python3
"""Exact finite controls and original vector figures for the signal companion.

Fraction and Gaussian-rational assertions are finite implementation evidence.
Floating plots evaluate stated formulas and illustrate conditioning; they are
not universal proofs, interval arithmetic, or certified root approximations.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse, json, hashlib, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)
C = dict(navy='#183345', teal='#168A89', gold='#D89B35', red='#BC5A56', gray='#76848A', pale='#EDF4F4')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':C['navy'],'text.color':C['navy'],'axes.titlesize':12,'pdf.fonttype':42,'svg.fonttype':'none'})
checks = []
def check(test, label):
    if not test: raise AssertionError(label)
    checks.append(label)
def eye(n): return [[F(i == j) for j in range(n)] for i in range(n)]
def matmul(a,b): return [[sum((a[i][k]*b[k][j] for k in range(len(b))),F(0)) for j in range(len(b[0]))] for i in range(len(a))]
def mv(a,v): return [sum((x*y for x,y in zip(row,v)),F(0)) for row in a]
def transpose(a): return [list(v) for v in zip(*a)]
def add(a,b): return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def scale(c,a): return [[c*x for x in row] for row in a]
def rank(a):
    a=[list(row) for row in a]; r=0
    for j in range(len(a[0])):
        piv=next((i for i in range(r,len(a)) if a[i][j]),None)
        if piv is None: continue
        a[r],a[piv]=a[piv],a[r]; v=a[r][j]; a[r]=[x/v for x in a[r]]
        for i in range(len(a)):
            if i != r:
                v=a[i][j]; a[i]=[x-v*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r
def g(z): return (F(z[0]),F(z[1]))
def ga(z,w): return (z[0]+w[0],z[1]+w[1])
def gm(z,w): return (z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0])
def gc(z): return (z[0],-z[1])
def gp(z,n):
    if n<0: return gp(gc(z),-n)
    out=(F(1),F(0))
    for _ in range(n): out=gm(out,z)
    return out
def gs(c,z): return (F(c)*z[0],F(c)*z[1])
def total(zs):
    out=(F(0),F(0))
    for z in zs:out=ga(out,z)
    return out
def numeric(z):return complex(float(z[0]),float(z[1]))

# Exact packet selectors and transfer reconstruction in Q^8.
x=list(map(F,[2,-1,3,0,1,4,-2,5])); I=eye(8)
Ps=[[[F(i==j and i%4==r) for j in range(8)] for i in range(8)] for r in range(4)]
summed=[[sum(P[i][j] for P in Ps) for j in range(8)] for i in range(8)]
check(summed==I,'order-four packet completeness')
for a in range(4):
    for b in range(4):check(matmul(Ps[a],Ps[b])==(Ps[a] if a==b else scale(0,I)),f'packet annihilation {a},{b}')
U=[[F(i==(j+1)%8) for j in range(8)] for i in range(8)]
T=add(add(scale(2,I),scale(-1,U)),scale(3,matmul(U,U)))
check(mv(T,x)==list(map(F,[-7,11,13,-6,11,7,-5,24])),'master transfer output')
blocks=[matmul(matmul(Pb,T),Pa) for Pb in Ps for Pa in Ps]
check([[sum(B[i][j] for B in blocks) for j in range(8)] for i in range(8)]==T,'all transfer blocks reconstruct T')
for n in range(8):check(x[n]==[x[r::4] for r in range(4)][n%4][n//4],f'polyphase interleaving address {n}')
for r in range(2):
    parent=[[F(i==j and i%2==r) for j in range(8)] for i in range(8)]
    check(add(Ps[r],Ps[r+2])==parent,f'parity refinement {r}')

# Exact residualized finite rays: constant background, cyclic masks.
M=8; P=[[F(1,M) for j in range(M)] for i in range(M)]
R=add(eye(M),scale(-1,P))
q=[F(i<3) for i in range(M)]; y=[F(2)+F(5,4)*v for v in q]
rq=mv(R,q); ry=mv(R,y)
dot=lambda a,b:sum((x*y for x,y in zip(a,b)),F(0))
A=dot(rq,ry)/dot(rq,rq)
check(A==F(5,4),'residualized profiled amplitude exact')
check([u-A*v for u,v in zip(ry,rq)]==[F(0)]*M,'true finite ray zero residual')
check(mv(P,[a-A*b for a,b in zip(y,q)])==[F(2)]*M,'finite background recovered')
check(dot(rq,rq)==F(15,8),'true residualized mask norm squared')
qcomp=[1-v for v in q]
check(mv(R,qcomp)==[-v for v in rq],'complement lies on opposite ray')
check(dot(mv(R,qcomp),ry)/dot(rq,rq)==-F(5,4),'complement rejected by positive-amplitude convention')
qwrong=[F(1<=i<4) for i in range(M)]
wrong=mv(R,qwrong); Aw=dot(wrong,ry)/dot(wrong,wrong)
wrongdist=dot([u-Aw*v for u,v in zip(ry,wrong)],[u-Aw*v for u,v in zip(ry,wrong)])
check(wrongdist==F(55,24),'wrong-ray objective differs from true')
check(sum(abs(a-b) for a,b in zip(q,qwrong))==2,'shifted masks symmetric difference cardinality')

# Gaussian-rational moments, exact recurrence and offset phase relation.
zs=[g((1,0)),g((0,1)),g((-1,0)),g((0,-1))]; amps=list(map(F,[1,2,-1,-2]))
moment=lambda n:total(gs(a,gp(z,n)) for a,z in zip(amps,zs))
check(sum(amps)==0,'four-jump periodic compatibility')
for n in range(32):
    check(moment(n+4)==moment(n),f'four-root annihilator recurrence n={n}')
    direct=complex(sum(float(a)*numeric(z)**n for a,z in zip(amps,zs)))
    check(direct==numeric(moment(n)),f'orthogonal direct Gaussian moment n={n}')
N=3; q0=2
for l,(a,z) in enumerate(zip(amps,zs)):
    b0=gs(a,gp(z,q0*N)); u=gp(z,N)
    for r in range(5):
        b=gs(a,gp(z,q0*N+r))
        check(b==gm(b0,gp(z,r)),f'offset coefficient l={l},r={r}')
        for k in range(6):check(gs(a,gp(z,(q0+k)*N+r))==gm(b,gp(u,k)),f'polyphase moment component l={l},r={r},q={k}')
    S=total(gm(gc(gm(b0,gp(z,r))),gm(b0,gp(z,r+1))) for r in range(4))
    check(S==gs(4*(b0[0]**2+b0[1]**2),z),f'offset cross-product phase l={l}')
check(len({gp(z,N) for z in zs})==4,'N=3 has no aliases among Gaussian nodes')
check(len({gp(z,4) for z in zs})==1,'N=4 collision negative control')

# Two opposite jumps: a completely hand-checkable Prony example.
m=[F(2 if n%2 else 0) for n in range(1,7)]
H=[[m[i+j] for j in range(2)] for i in range(2)]
check(H==[[F(2),F(0)],[F(0),F(2)]],'two-jump Hankel is twice identity')
check(rank(H)==2,'two-jump exact order rank')
for i in range(4):check(-m[i]+m[i+2]==0,f'annihilator z^2-1 index {i}')
check(rank([[m[i+j] for j in range(3)] for i in range(3)])==2,'larger exact Hankel rank stays two')

# Exact corrected mean-zero L1 formulas, with an independent partition integral.
def saw(t,tau,T): return F(1,2)-((t-tau)%T)/T
for T0 in [F(1),F(2),F(4)]:
    for k in range(1,9):
        d=T0*F(k,20)
        breaks=[F(0),d,T0]
        integ=sum((b-a)*abs(saw((a+b)/2,F(0),T0)-saw((a+b)/2,d,T0)) for a,b in zip(breaks,breaks[1:]))
        check(integ==2*d*(1-d/T0),f'sawtooth translated L1 T={T0},d={d}')
        check(integ<=2*d,f'factor-two location allowance T={T0},d={d}')
        check(integ>d,f'factor-one location bound rejected T={T0},d={d}')
    integ=(T0/2)*F(1,4)+(T0/2)*F(1,4)
    check(integ==T0/4,f'mean-zero sawtooth amplitude L1 T={T0}')

# Exact finite image dictionary with constant background and disjoint atoms.
W=5; pixels=W*W
supports=[{0,1,5,6},{3,4,8,9},{16,17,21,22}]
Ds=[[F(i in S) for S in supports] for i in range(pixels)]
RD=[[v-sum(Ds[k][j] for k in range(pixels))/pixels for j,v in enumerate(row)] for row in Ds]
check(rank(RD)==3,'finite image residual dictionary injective')
alpha=[F(1),F(3,4),F(-1,2)]; img=[F(2)+v for v in mv(Ds,alpha)]
res=[v-sum(img)/pixels for v in img]
check(mv(RD,alpha)==res,'finite image background elimination')
gram=matmul(transpose(RD),RD)
check(rank(gram)==3,'finite image coefficient Gram nonsingular')

def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',pad_inches=.12)
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight',pad_inches=.12)
    fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)
def draw_box(ax,x,y,w,h,title,body):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.10',facecolor=C['pale'],edgecolor=C['teal'],lw=1.2))
    ax.text(x+w/2,y+h*.73,title,ha='center',va='center',weight='bold',fontsize=11)
    ax.text(x+w/2,y+h*.32,body,ha='center',va='center',fontsize=10)
def unitcircle(ax):
    th=np.linspace(0,2*np.pi,400);ax.plot(np.cos(th),np.sin(th),color=C['gray'],lw=1)
    ax.axhline(0,color=C['gray'],lw=.5);ax.axvline(0,color=C['gray'],lw=.5)
    ax.set_aspect('equal');ax.set_xlim(-1.3,1.3);ax.set_ylim(-1.3,1.3);ax.set_xlabel('Real part');ax.set_ylabel('Imaginary part')
def smooth(t):return .25+.4*np.cos(2*t)-np.sin(3*t)/3+.2*np.cos(5*t)
def edge(t):
    wrapped=(t+np.pi)%(2*np.pi)-np.pi
    return ((wrapped>=-np.pi/3)&(wrapped<np.pi/3)).astype(float)
def edge_partial(t,n):
    k=np.arange(1,n+1);return 1/3+2/np.pi*np.sum(np.sin(k*np.pi/3)[:,None]/k[:,None]*np.cos(k[:,None]*t[None,:]),axis=0)

# 01: exact finite packet refinement.
fig,axs=plt.subplots(2,1,figsize=(8.3,4.6),sharex=True)
for r in range(4):
    inds=np.arange(r,8,4);axs[0].stem(inds,np.array(x,dtype=float)[inds],linefmt='-',markerfmt='o',basefmt=' ')
    for n in inds:axs[0].text(n,float(x[n])+.25,f'r={r}',ha='center',fontsize=9)
axs[0].set_ylabel('Signal value');axs[0].set_title('Every sample retains one residue address')
for r in range(4):
    axs[1].scatter(np.arange(r,8,4),[r]*2,s=65,label=f'Packet r={r}')
axs[1].set_yticks(range(4));axs[1].set_ylabel('Residue modulo 4');axs[1].set_xlabel('Original sample index n');axs[1].set_xticks(range(8));fig.tight_layout();save(fig,'01_packet_refinement')

# 02: transfer structure is atlas dependent.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.9))
tn=np.array(T,dtype=float);perm=[0,4,1,5,2,6,3,7]
for ax,a,title in zip(axs,[tn,tn[np.ix_(perm,perm)]],['Original addresses','Order-four packet addresses']):
    im=ax.imshow(a,cmap='RdBu_r',vmin=-3,vmax=3);ax.set_title(title);ax.set_xlabel('Input coordinate');ax.set_ylabel('Output coordinate');ax.set_xticks(range(8));ax.set_yticks(range(8))
for j in [1.5,3.5,5.5]:axs[1].axhline(j,color=C['navy'],lw=1.4);axs[1].axvline(j,color=C['navy'],lw=1.4)
fig.colorbar(im,ax=axs.ravel().tolist(),shrink=.8,label='Transfer coefficient');save(fig,'02_transfer_blocks')

# 03: annihilation by frequency masks.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.8))
angles=np.linspace(0,2*np.pi,721)
for ax,ns in zip(axs,[[6,10],[6,11]]):
    val=np.sqrt(sum(np.abs(np.exp(1j*n*angles)-1)**2 for n in ns));ax.plot(angles/np.pi,val,color=C['teal'])
    ax.set_title(f'Frequency set {ns}; gcd = {math.gcd(*ns)}');ax.set_xlabel('Phase difference / pi');ax.set_ylabel('Combined measurement difference');ax.set_xticks([0,1,2]);ax.set_ylim(-.05,3)
fig.tight_layout();save(fig,'03_alias_gcd')

# 04: a known smooth/edge decomposition.
t=np.linspace(-np.pi,np.pi,1600)
fig,axs=plt.subplots(3,1,figsize=(8.3,5.5),sharex=True)
for ax,a,title,col in zip(axs,[smooth(t),edge(t),smooth(t)+edge(t)],['Smooth packet s','Native interval packet j','Observed signal f = s + j'],['teal','gold','navy']):
    ax.plot(t/np.pi,a,color=C[col]);ax.set_ylabel('Amplitude');ax.set_title(title,loc='left')
axs[-1].set_xlabel('Position / pi');fig.tight_layout();save(fig,'04_signal_packets')

# 05: residue structure of the exact Fourier tail.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.6))
ns=np.arange(1,49);coeff=np.sin(ns*np.pi/3)/(np.pi*ns)
axs[0].stem(ns,coeff,linefmt='-',markerfmt='o',basefmt=' ');axs[0].set_xlabel('Fourier index n');axs[0].set_ylabel('Edge coefficient');axs[0].set_title('1/n decay with exact phase zeros')
axs[1].scatter(ns,np.pi*ns*coeff,c=ns%6,cmap='viridis',s=28);axs[1].set_xlabel('Fourier index n');axs[1].set_ylabel('pi n times coefficient');axs[1].set_title('Six residue classes carry the phase');fig.tight_layout();save(fig,'05_fourier_tail')

# 06: Gibbs has shrinking width and persistent normalized height.
tt=np.linspace(np.pi/3-.5,np.pi/3+.5,1400)
fig,axs=plt.subplots(1,2,figsize=(8.3,3.8))
axs[0].plot(tt-np.pi/3,edge(tt),color=C['navy'],lw=2,label='Native edge')
for n,col in zip([8,32,128],['red','gold','teal']):axs[0].plot(tt-np.pi/3,edge_partial(tt,n),color=C[col],label=rf'$S_{{{n}}}j$')
axs[0].set_xlabel('Distance from right edge');axs[0].set_ylabel('Edge amplitude');axs[0].legend(fontsize=9);axs[0].set_title('The oscillatory layer contracts')
scaled=np.linspace(-7,7,1000)
for n,col in zip([32,128,512],['red','gold','teal']):axs[1].plot(scaled,edge_partial(np.pi/3-scaled/(n+.5),n),color=C[col],label=f'N={n}')
axs[1].axhline(1,color=C['gray'],lw=.8);axs[1].axhline(0,color=C['gray'],lw=.8);axs[1].set_xlabel('Scaled inward distance z');axs[1].set_ylabel('Edge amplitude');axs[1].set_title('The first overshoot persists');axs[1].legend(fontsize=9);fig.tight_layout();save(fig,'06_gibbs_geometry')

# 07: known-edge coefficient estimation.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.5))
ks=np.arange(7,32,2);mk=(-1.)**ks*np.sin(np.pi*ks/2)/(np.pi*ks)
noise=.003*np.sin(ks); measured=1.25*mk+noise
axs[0].scatter(mk,measured,color=C['teal']); xx=np.linspace(mk.min(),mk.max(),100);axs[0].plot(xx,1.25*xx,color=C['navy'],label='True amplitude 5/4');axs[0].set_xlabel('Known mask coefficient');axs[0].set_ylabel('Measured coefficient');axs[0].legend(fontsize=9)
den=np.sqrt(np.cumsum(mk**2));axs[1].plot(np.arange(1,len(ks)+1),1/den,color=C['red']);axs[1].set_xlabel('Out-of-band coefficients used');axs[1].set_ylabel('Coefficient error amplification');axs[1].set_title('The mask coefficient norm controls fit');fig.tight_layout();save(fig,'07_known_edge_fit')

# 08: positive residualized rays and an exact wrong candidate.
fig,ax=plt.subplots(figsize=(7.5,3.8))
ax.axhline(0,color=C['gray'],lw=.6);ax.axvline(0,color=C['gray'],lw=.6)
for ang,col,name in [(0,'teal','True positive ray'),(.78,'gold','Wrong positive ray'),(np.pi,'red','Complement ray')]:
    ax.plot([0,3*np.cos(ang)],[0,3*np.sin(ang)],color=C[col],lw=2,label=name)
ax.scatter([2.2],[0],s=70,color=C['navy']);ax.text(2.2,-.25,'Residualized data',ha='center');ax.set_aspect('equal');ax.set_xlim(-3.3,3.3);ax.set_ylim(-.7,2.7);ax.set_xlabel('Illustrative residual coordinate 1');ax.set_ylabel('Illustrative residual coordinate 2');ax.legend(loc='upper left',fontsize=9);save(fig,'08_dictionary_rays')

# 09: restricted singular-value allowance.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.5))
eps=np.linspace(0,.1,100)
for gam,col in [(1,'teal'),(.2,'gold'),(.05,'red')]:axs[0].plot(eps,2*eps/gam,color=C[col],label=f'gamma = {gam}')
axs[0].set_xlabel('Residual noise allowance epsilon');axs[0].set_ylabel('Coefficient error bound');axs[0].legend(fontsize=9);axs[0].set_title('2 epsilon / gamma on sparse secants')
aa=np.linspace(.01,np.pi/2,100);axs[1].plot(aa,np.sin(aa),color=C['teal']);axs[1].set_xlabel('Angle between candidate rays');axs[1].set_ylabel('Normalized distance to wrong ray');axs[1].set_title('A finite margin can disappear');fig.tight_layout();save(fig,'09_dictionary_conditioning')

# 10: differentiated moments turn jumps into exponential atoms.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.5))
ns=np.arange(16);ms=np.array([numeric(moment(int(n))) for n in ns]);axs[0].stem(ns,ms.real,linefmt='-',markerfmt='o',basefmt=' ',label='Real');axs[0].plot(ns,ms.imag,'s-',color=C['gold'],label='Imaginary');axs[0].set_xlabel('Moment index n');axs[0].set_ylabel('Differentiated moment');axs[0].legend(fontsize=9);axs[0].set_title('Four exact Gaussian nodes')
unitcircle(axs[1]);axs[1].scatter([numeric(z).real for z in zs],[numeric(z).imag for z in zs],c=[C['teal'],C['gold'],C['red'],C['navy']],s=65)
for z,a in zip(zs,amps):axs[1].text(numeric(z).real*1.13,numeric(z).imag*1.13,str(a),ha='center',va='center')
axs[1].set_title('Node labels show jump amplitudes');fig.tight_layout();save(fig,'10_derivative_moments')

# 11: exact Prony display.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.6))
hh=np.array(H,dtype=float);axs[0].imshow(hh,cmap='Blues',vmin=0,vmax=2)
for i in range(2):
    for j in range(2):axs[0].text(j,i,str(int(hh[i,j])),ha='center',va='center',fontsize=26,color='white' if hh[i,j] else C['navy'])
axs[0].set_xticks([0,1]);axs[0].set_yticks([0,1]);axs[0].set_title('H_2 from moments 2, 0, 2');axs[0].set_xlabel('Column index');axs[0].set_ylabel('Row index')
unitcircle(axs[1]);axs[1].scatter([-1,1],[0,0],s=75,color=C['teal']);axs[1].text(0,.35,'Q(z) = z^2 - 1',ha='center',fontsize=14);axs[1].text(-1,-.25,'tau = pi',ha='center');axs[1].text(1,-.25,'tau = 0',ha='center');fig.tight_layout();save(fig,'11_prony_example')

# 12: exact and perturbed Hankel singular-value gap.
hn=np.array([[numeric(moment(i+j+1)) for j in range(6)] for i in range(6)])
en=.03*np.fromfunction(lambda i,j:np.cos(i+j+1),(6,6))
sv0=np.linalg.svd(hn,compute_uv=False);sv=np.linalg.svd(hn+en,compute_uv=False);enorm=np.linalg.norm(en,2)
fig,ax=plt.subplots(figsize=(7.8,3.7));ax.semilogy(np.arange(1,7),np.maximum(sv0,1e-16),'o-',color=C['teal'],label='Exact H_0');ax.semilogy(np.arange(1,7),np.maximum(sv,1e-16),'s-',color=C['gold'],label='Perturbed H');ax.axhline(enorm,color=C['red'],ls='--',label='Actual spectral norm of E');ax.axvline(4.5,color=C['gray'],ls=':');ax.set_xlabel('Singular-value index');ax.set_ylabel('Singular value (floating evaluation)');ax.set_xticks(range(1,7));ax.legend(fontsize=9);save(fig,'12_hankel_gap')

# 13: collision geometry.
ds=np.geomspace(1e-4,1,100);sig=[];momnorm=[]
for d in ds:
    vv=np.exp(-1j*np.outer(np.arange(12),[0,d]));sig.append(np.linalg.svd(vv,compute_uv=False)[-1]);momnorm.append(np.linalg.norm(1-np.exp(-1j*np.arange(1,13)*d)))
fig,axs=plt.subplots(1,2,figsize=(8.3,3.6));axs[0].loglog(ds,sig,color=C['teal']);axs[0].set_xlabel('Jump separation delta');axs[0].set_ylabel('Smallest Vandermonde singular value');axs[0].set_title('Inversion loses conditioning')
axs[1].loglog(ds,momnorm,color=C['red']);axs[1].set_xlabel('Jump separation delta');axs[1].set_ylabel('Norm of moments 1 - exp(-i n delta)');axs[1].set_title('Fixed measurements collapse');fig.tight_layout();save(fig,'13_collision_boundary')

# 14: finite polyphase sample budget.
base=[(2+q)*3 for q in range(9)];adj=[(2+q)*3+1 for q in range(4)]
fig,ax=plt.subplots(figsize=(8.3,3.3));ax.scatter(base,[0]*len(base),color=C['teal'],s=60,label='Base: 2 L_max + 1');ax.scatter(adj,[1]*len(adj),color=C['gold'],s=60,label='Adjacent: L_max')
for n in base:ax.text(n,-.20,str(n),ha='center',fontsize=9)
for n in adj:ax.text(n,1.18,str(n),ha='center',fontsize=9)
ax.set_ylim(-.6,1.6);ax.set_yticks([0,1],['Offset r=0','Offset r=1']);ax.set_xlabel('Positive Fourier index n');ax.set_title('L_max = 4, N = 3, q_0 = 2: thirteen innovation samples');ax.legend(fontsize=9,loc='center right');save(fig,'14_polyphase_budget')

# 15: genuine 3D phase relation.
fig=plt.figure(figsize=(7.8,4.7));ax=fig.add_subplot(111,projection='3d')
rr=np.linspace(0,5,400);theta=3*np.pi/4;ax.plot(np.cos(theta*rr),np.sin(theta*rr),rr,color=C['teal'],lw=2)
r0=np.arange(6);ax.scatter(np.cos(theta*r0),np.sin(theta*r0),r0,color=C['navy'],s=40)
for r in r0:ax.text(np.cos(theta*r),np.sin(theta*r),r+.12,str(r),fontsize=9)
ax.set_xlabel(r'$\mathrm{Re}(b_r/b_0)$',labelpad=7);ax.set_ylabel(r'$\mathrm{Im}(b_r/b_0)$',labelpad=7);ax.set_zlabel('');ax.text2D(.80,.58,'Offset r',transform=ax.transAxes,fontsize=10,rotation=90,ha='center',va='center')
ax.set_title('Offset coefficients retain the missing phase',pad=13);ax.view_init(22,-53);save(fig,'15_offset_helix')

# 16: branch choice geometry.
fig,axs=plt.subplots(1,2,figsize=(8.3,4.0));Nroot=5;theta=4*np.pi/5;z=np.exp(1j*theta);roots=np.exp(2j*np.pi*np.arange(Nroot)/Nroot);tilde=np.exp(1j*(theta+.08))
for ax in axs:unitcircle(ax);ax.scatter(roots.real,roots.imag,color=C['gold'],s=55)
axs[0].scatter([1],[0],color=C['red'],s=100,marker='x',label='Principal root');axs[0].scatter([z.real],[z.imag],color=C['navy'],s=95,marker='*',label='True phase');axs[0].set_title('u = z^5 = 1 leaves five candidates');axs[0].legend(loc='lower left',fontsize=9)
axs[1].scatter([tilde.real],[tilde.imag],color=C['teal'],s=65,label='Offset phase estimate');axs[1].plot([tilde.real,z.real],[tilde.imag,z.imag],color=C['teal'],lw=2);axs[1].set_title('The offset phase selects the branch');axs[1].legend(loc='lower left',fontsize=9);fig.tight_layout();save(fig,'16_branch_margin')

# 17: root gain on the correct associated branch.
eta=np.linspace(0,1.95,200);fig,axs=plt.subplots(1,2,figsize=(8.3,3.6))
for nr,col in zip([2,5,10],['red','gold','teal']):axs[0].plot(eta,2*np.sin(np.arcsin(eta/2)/nr),color=C[col],label=f'N={nr}')
axs[0].set_xlabel('Normalized alias-node chord error eta');axs[0].set_ylabel('Associated root chord error');axs[0].legend(fontsize=9);axs[0].set_title('Printed root gain formula')
nr=np.arange(2,31);axs[1].plot(nr,np.sin(np.pi/nr),color=C['red']);axs[1].set_xlabel('Decimation N');axs[1].set_ylabel('Available branch margin sin(pi/N)');axs[1].set_title('Greater gain also narrows the margin');fig.tight_layout();save(fig,'17_root_gain')

# 18: corrected mean-zero edge location error.
tt=np.linspace(0,1,1200,endpoint=False);d=.12;j0=(tt<.5).astype(float)-.5;jd=((tt>=d)&(tt<.5)).astype(float)-(.5-d)
fig,axs=plt.subplots(1,2,figsize=(8.3,3.7));axs[0].step(tt,j0,where='post',color=C['navy'],label='Edges at 0 and 1/2');axs[0].step(tt,jd,where='post',color=C['gold'],label='First edge moved by d');axs[0].fill_between(tt,j0,jd,color=C['red'],alpha=.18,step='post');axs[0].set_xlabel('Position on period T=1');axs[0].set_ylabel('Mean-zero edge amplitude');axs[0].legend(fontsize=8.5)
dd=np.linspace(0,.5,200);axs[1].plot(dd,2*dd*(1-dd),color=C['teal'],label='Exact L1 = 2 d (1-d)');axs[1].plot(dd,dd,color=C['red'],ls='--',label='False coefficient-one bound');axs[1].plot(dd,2*dd,color=C['gray'],ls=':',label='Valid factor-two bound');axs[1].set_xlabel('Shortest location displacement d');axs[1].set_ylabel('L1 edge error');axs[1].legend(fontsize=8.5);fig.tight_layout();save(fig,'18_corrected_l1')

# 19: the final reconstruction uses different packet operators.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.8));n=24
for ax,window in zip(axs,[(-np.pi,np.pi),(np.pi/3-.3,np.pi/3+.3)]):
    xx=np.linspace(*window,1500);truth=smooth(xx)+edge(xx);raw=smooth(xx)+edge_partial(xx,n)
    ax.plot(xx/np.pi,raw,color=C['red'],label='Raw S_24 f');ax.plot(xx/np.pi,truth,color=C['teal'],lw=1.5,label='Native edge + smooth packet');ax.set_xlabel('Position / pi');ax.set_ylabel('Signal amplitude')
axs[0].set_title('Complete signal');axs[1].set_title('Right boundary detail');axs[0].legend(fontsize=9);fig.tight_layout();save(fig,'19_resolved_synthesis')

# 20: exact finite dictionary image and model mismatch.
ww=40; yy,xx=np.mgrid[:ww,:ww];atoms=[((xx>=4)&(xx<15)&(yy>=5)&(yy<18)).astype(float),((xx>=24)&(xx<34)&(yy>=7)&(yy<25)).astype(float),((xx>=8)&(xx<21)&(yy>=27)&(yy<35)).astype(float)]
truth=.35+atoms[0]+.75*atoms[1]-.5*atoms[2]
fig,axs=plt.subplots(1,3,figsize=(8.8,3.4));axs[0].imshow(truth,cmap='viridis',vmin=-.2,vmax=1.4);axs[0].set_title('Declared finite image');axs[1].imshow(sum(a*at for a,at in zip([1,.75,-.5],atoms)),cmap='viridis',vmin=-.2,vmax=1.4);axs[1].set_title('Native geometric packet')
angle=np.arctan2(yy-20,xx-20);rad=np.hypot(xx-20,yy-20);star=(rad<11+5*np.cos(7*angle)).astype(float);D=np.column_stack([at.ravel()-at.mean() for at in atoms]);rv=star.ravel()-star.mean();ahat=np.linalg.lstsq(D,rv,rcond=None)[0];fit=star.mean()+sum(a*at-a*at.mean() for a,at in zip(ahat,atoms));mismatch=star-fit
axs[2].imshow(mismatch,cmap='RdBu_r',vmin=-1,vmax=1);axs[2].set_title('Star: out-of-dictionary residual')
for ax in axs:ax.set_xticks([]);ax.set_yticks([])
fig.tight_layout();save(fig,'20_finite_image_dictionary')

# 21: the validation residual is a consistency test, not a truth oracle.
fig,axs=plt.subplots(1,2,figsize=(8.3,3.7));rr=np.arange(6);z=np.exp(1j*.7);coeff=z**rr;pert=coeff+.10*np.cos(1.4*rr);fitphase=np.sum(np.conj(pert[:-1])*pert[1:]);fitphase/=abs(fitphase);v=np.abs(pert[1:]-fitphase*pert[:-1])
axs[0].plot(rr,coeff.real,'o-',color=C['teal'],label='Exact Re b_r');axs[0].plot(rr,pert.real,'s--',color=C['red'],label='Perturbed Re b_r');axs[0].set_xlabel('Offset r');axs[0].set_ylabel('Coefficient real part');axs[0].legend(fontsize=9)
axs[1].bar(rr[:-1],v,color=C['gold']);axs[1].set_xlabel('Adjacent offset pair r, r+1');axs[1].set_ylabel('Absolute phase recurrence residual');axs[1].set_title('A local model check on fitted coefficients');fig.tight_layout();save(fig,'21_offset_validation')

parser=argparse.ArgumentParser();parser.add_argument('--result',required=True);args=parser.parse_args()
result=Path(args.result);result.parent.mkdir(parents=True,exist_ok=True)
figure_hashes={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FIG.glob('*')) if p.suffix in ['.pdf','.svg','.png']}
record={'status':'PASS','exact_assertions':len(checks),'assertion_labels':checks,'coefficient_domain':'Fraction rationals and Gaussian-rational pairs','figure_count':len(list(FIG.glob('*.pdf'))),'figure_hashes':figure_hashes,'exact_examples':{'packet_dimension':8,'packet_order':4,'finite_ray_samples':8,'Gaussian_nodes':4,'Gaussian_moment_indices':[0,35],'polyphase_decimation':3,'offset_indices':[0,4],'polyphase_q_indices':[0,5],'periods_for_L1':['1','2','4'],'displacements_per_period':8,'image_pixels':25,'image_dictionary_atoms':3},'floating_diagnostics':{'Hankel_dimension':6,'Hankel_perturbation_spectral_norm':float(enorm),'Hankel_singular_values_exact_model':sv0.tolist(),'Hankel_singular_values_perturbed':sv.tolist(),'collision_separations':[1e-4,1.0],'collision_samples':100,'Vandermonde_rows':12},'non_claims':['Finite assertions do not prove the universal theorems.','Floating diagnostics are not certified interval computations.','Plotting point samples do not verify a continuous L1 integral.','No Python code is formally verified or extracted from Lean.','No fresh Lean run is claimed.']}
result.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'exact_assertions':len(checks),'figures':record['figure_count'],'status':'PASS'}))
