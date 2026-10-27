from __future__ import annotations

from fractions import Fraction
from math import comb, factorial, pi
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

matplotlib.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.unicode_minus': True,
})


def save(fig, name: str) -> None:
    fig.savefig(OUT / name, bbox_inches='tight', pad_inches=0.04)
    plt.close(fig)


def box(ax, xy, text, width=1.65, height=.52):
    x, y = xy
    p = FancyBboxPatch((x-width/2, y-height/2), width, height,
                       boxstyle='round,pad=0.03,rounding_size=0.04',
                       linewidth=0.9, facecolor='white', edgecolor='black')
    ax.add_patch(p)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.5)


def arrow(ax, a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=10,
                                 linewidth=0.9, color='black'))

# 1. Architecture
fig, ax = plt.subplots(figsize=(8.2, 2.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 2.3); ax.axis('off')
xs = [0.8, 2.45, 4.1, 5.75, 7.4, 9.05]
labels = ['coefficient\nseed', 'residue or\nunit address', 'triangular\ncoordinates', 'valuation and\ndifferences', 'local lift or\nrecurrence', 'exact\nreconstruction']
for x, label in zip(xs, labels): box(ax, (x, 1.15), label, 1.42, .72)
for a, b in zip(xs[:-1], xs[1:]): arrow(ax, (a+.72,1.15),(b-.72,1.15))
save(fig, '01_arithmetic_architecture.pdf')

# helpers

def reduced_inverse(m: int, p: int, nmax: int):
    e=[1]
    for n in range(1,nmax+1):
        total=sum((comb(m*n,m*q)%p)*e[q] for q in range(n))%p
        e.append((-total)%p)
    return e

# 2. Hurwitz subgroup orbits
fig, ax = plt.subplots(figsize=(6.5, 3.0))
ax.set_aspect('equal'); ax.axis('off')
p=13; m=3
angles=np.linspace(0,2*pi,p,endpoint=False)
pts=np.c_[np.cos(angles),np.sin(angles)]
H={1,3,9}
for u,(x,y) in enumerate(pts):
    ax.scatter([x],[y],s=45,facecolors='white',edgecolors='black',zorder=3)
    ax.text(1.12*x,1.12*y,str(u),ha='center',va='center',fontsize=8)
for u in H:
    ax.scatter([pts[u,0]],[pts[u,1]],s=90,facecolors='0.75',edgecolors='black',zorder=2)
ax.text(0,-1.45,'The subgroup average in the additive group algebra',ha='center',fontsize=9)
ax.set_xlim(-1.55,1.55);ax.set_ylim(-1.55,1.35)
save(fig,'02_hurwitz_subgroup_average.pdf')

# 3. Standard window heatmap
pairs=[(5,1),(5,2),(7,1),(7,2),(7,3),(13,2),(13,3),(13,4),(13,6)]
rows=[]; labels=[]
for p,m in pairs:
    e=reduced_inverse(m,p,36)
    rows.append(e[1:31])
    labels.append(f'p={p}, m={m}, h={(p-1)//m}')
arr=np.array(rows,float)
fig, ax=plt.subplots(figsize=(8.2,3.6))
im=ax.pcolormesh(np.arange(arr.shape[1]+1)-.5,np.arange(arr.shape[0]+1)-.5,arr,shading='flat',cmap='Greys',rasterized=False)
ax.set_ylim(arr.shape[0]-.5,-.5)
ax.set_yticks(range(len(labels)),labels)
ax.set_xticks([0,4,9,14,19,24,29],[1,5,10,15,20,25,30])
ax.set_xlabel('compressed row n')
ax.set_title('Reduced standard window inverses in finite fields')
save(fig,'03_standard_window_periods.pdf')

# 4. Congruential matrix mod p
p=7;m=2;j=3;nmax=14
mat=np.zeros((nmax+1,nmax+1))
for n in range(nmax+1):
    for q in range(n+1):
        mat[n,q]=comb(m*p*n+j,m*p*q)%p
fig,ax=plt.subplots(figsize=(5.3,4.5))
im=ax.pcolormesh(np.arange(mat.shape[1]+1)-.5,np.arange(mat.shape[0]+1)-.5,mat,shading='flat',cmap='Greys',rasterized=False)
ax.set_ylim(mat.shape[0]-.5,-.5)
ax.set_xlabel('column q');ax.set_ylabel('row n')
ax.set_title('A standard window matrix modulo 7')
save(fig,'04_standard_window_matrix.pdf')

# Euler and zigzag helpers

def bernoulli_numbers(n):
    A=[Fraction(0) for _ in range(n+1)]; B=[]
    for m in range(n+1):
        A[m]=Fraction(1,m+1)
        for r in range(m,0,-1): A[r-1]=r*(A[r-1]-A[r])
        B.append(A[0])
    return B
B=bernoulli_numbers(100)

def euler_numbers(nmax):
    E=[0]*(nmax+1);E[0]=1
    for n in range(1,nmax+1):
        E[n]=-sum(comb(n,k)*E[k] for k in range(n) if (n-k)%2==0)
    return E
E=euler_numbers(80)

def zigzag_numbers(nmax):
    Z=[0]*(nmax+1);Z[0]=1
    for n in range(nmax):
        v=sum(comb(n,k)*Z[k]*Z[n-k] for k in range(n+1))
        if n==0:v+=1
        Z[n+1]=v//2
    return Z
Z=zigzag_numbers(80)

def vp_int(x,p):
    if x==0:return 99
    x=abs(x);v=0
    while x%p==0:v+=1;x//=p
    return v

def vp_frac(x,p):return vp_int(x.numerator,p)-vp_int(x.denominator,p)

# 5. odd transform weights
p=5;nmax=20
W=np.full((nmax//2+1,nmax//2+1),np.nan)
for ni,n in enumerate(range(0,nmax+1,2)):
    for m0 in range(n//2+1):
        W[ni,m0]=2*m0
fig,ax=plt.subplots(figsize=(5.6,4.3))
masked=np.ma.masked_invalid(W)
im=ax.pcolormesh(np.arange(W.shape[1]+1)-.5,np.arange(W.shape[0]+1)-.5,masked,shading='flat',cmap='Greys',rasterized=False)
ax.set_xlabel('transfer depth m');ax.set_ylabel('even row n divided by 2')
ax.set_title('Visible odd prime weight 2m')
save(fig,'05_odd_coordinate_weights.pdf')

# 6. odd tail valuations
q=5;n=24
S=[sum((-1)**a*(2*a+1)**k for a in range(q)) for k in range(n+1)]
actual=[];bound=[]
for M in range(n//2):
    trunc=sum((-1)**r*Z[2*r+1]*comb(n,2*r)*q**(2*r)*S[n-2*r] for r in range(M+1))
    actual.append(vp_int(E[n]-trunc,5));bound.append(2*M+2)
fig,ax=plt.subplots(figsize=(6.2,3.4))
ax.plot(range(len(actual)),actual,'o-',label='actual valuation')
ax.plot(range(len(bound)),bound,'s--',label='uniform bound')
ax.set_xlabel('retained depth M');ax.set_ylabel('5 adic valuation')
ax.legend(frameon=False);ax.grid(alpha=.2)
save(fig,'06_odd_tail_valuations.pdf')

# 7. beta valuations
ms=np.arange(1,33)
vals=np.array([bin(int(m)).count('1')-1 for m in ms])
fig,ax=plt.subplots(figsize=(7.0,3.2))
ax.stem(ms,vals,basefmt=' ')
ax.set_xlabel('m');ax.set_ylabel('valuation of beta m')
ax.set_title('Exact dyadic inverse coefficient valuations')
ax.grid(axis='y',alpha=.2)
save(fig,'07_beta_valuations.pdf')

# 8. dyadic row weights
n=28
ms2=np.arange(1,n//2+1)
termw=[]
for r in ms2:
    falling=factorial(n)//factorial(n-2*r)
    termw.append(2*r + (bin(int(r)).count('1')-1) + vp_int(falling,2))
fig,ax=plt.subplots(figsize=(6.6,3.3))
ax.plot(ms2,termw,'o-',label='row dependent weight')
ax.plot(ms2,2*ms2,'s--',label='uniform visible weight')
ax.set_xlabel('transfer depth m');ax.set_ylabel('2 adic lower bound')
ax.legend(frameon=False);ax.grid(alpha=.2)
save(fig,'08_dyadic_row_weights.pdf')

# 9. unit coordinate split diagram
fig,ax=plt.subplots(figsize=(8.2,3.0));ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,3)
box(ax,(1.25,2.2),'odd prime unit',2.0,.58);box(ax,(4.0,2.2),'torsion root',1.7,.58);box(ax,(6.4,2.2),'principal unit',1.8,.58)
arrow(ax,(2.25,2.2),(3.15,2.2));arrow(ax,(4.85,2.2),(5.5,2.2))
box(ax,(1.25,.8),'dyadic unit',2.0,.58);box(ax,(4.0,.8),'sign packet',1.7,.58);box(ax,(6.4,.8),'unit in 1 plus 4Z2',2.4,.58)
arrow(ax,(2.25,.8),(3.15,.8));arrow(ax,(4.85,.8),(5.15,.8))
ax.text(8.7,2.2,'step p minus 1',ha='center',va='center');ax.text(8.7,.8,'parity then step 2',ha='center',va='center')
save(fig,'09_unit_coordinate_split.pdf')

# 10. Mahler triangular matrix
N=14
M=np.zeros((N+1,N+1))
for n in range(N+1):
    for r in range(n+1): M[n,r]=comb(n,r)
fig,ax=plt.subplots(figsize=(5.3,4.2))
L=np.log10(M+1)
im=ax.pcolormesh(np.arange(L.shape[1]+1)-.5,np.arange(L.shape[0]+1)-.5,L,shading='flat',cmap='Greys',rasterized=False)
ax.set_xlabel('Mahler order r');ax.set_ylabel('sample n')
ax.set_title('Newton and Mahler reconstruction matrix')
save(fig,'10_mahler_coordinates.pdf')

# 11. Amice valuation profile of log(1+T)
K=30
fig,ax=plt.subplots(figsize=(6.8,3.4))
for p0 in [2,3,5]:
    vals=[-vp_int(k,p0) for k in range(1,K+1)]
    ax.plot(range(1,K+1),vals,'o-',markersize=3,label=f'p={p0}')
ax.set_xlabel('coefficient index');ax.set_ylabel('valuation of 1 divided by k')
ax.legend(frameon=False);ax.grid(alpha=.2)
save(fig,'11_amice_valuation_profiles.pdf')

# 12. lift obstruction diagram
fig,ax=plt.subplots(figsize=(8.0,2.8));ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,2.8)
box(ax,(1.2,1.4),'solution mod p power L',2.1,.68)
box(ax,(4.0,1.4),'scaled residual mod p',2.1,.68)
box(ax,(6.8,1.4),'Jacobian cokernel class',2.2,.68)
box(ax,(9.0,1.4),'lift or obstruction',1.7,.68)
arrow(ax,(2.3,1.4),(2.9,1.4));arrow(ax,(5.1,1.4),(5.65,1.4));arrow(ax,(7.95,1.4),(8.15,1.4))
save(fig,'12_lift_obstruction.pdf')

# 13. Fibonacci packets
F=[0,1]
for _ in range(2,34):F.append(F[-1]+F[-2])
fig,ax=plt.subplots(figsize=(6.8,3.5))
for j in range(3):
    vals=[F[3*k+j] for k in range(9)]
    ax.plot(range(9),vals,'o-',label=f'residue {j}')
ax.set_yscale('log');ax.set_xlabel('packet step');ax.set_ylabel('Fibonacci value')
ax.legend(frameon=False);ax.grid(alpha=.2)
save(fig,'13_recurrence_packets.pdf')

# 14. eigenvalue power map
fig,ax=plt.subplots(figsize=(5.0,4.0));ax.set_aspect('equal')
ths=np.array([.2,1.1,2.3,3.8,5.2]);rad=np.array([.75,.88,.66,.82,.72])
z=rad*np.exp(1j*ths);Npow=3;zn=z**Npow
ax.scatter(z.real,z.imag,s=55,facecolors='white',edgecolors='black',label='original roots')
ax.scatter(zn.real,zn.imag,s=55,marker='s',facecolors='0.7',edgecolors='black',label='jump roots')
for a,b in zip(z,zn):ax.plot([a.real,b.real],[a.imag,b.imag],linewidth=.7,color='0.5')
ax.axhline(0,color='0.7',linewidth=.6);ax.axvline(0,color='0.7',linewidth=.6)
ax.legend(frameon=False,loc='upper right');ax.set_xlabel('real part');ax.set_ylabel('imaginary part')
save(fig,'14_recurrence_root_power.pdf')

# 15. CRT packet grid
fig,ax=plt.subplots(figsize=(6.5,4.0))
a=3;M0=5;N0=2**a*M0
arr=np.full((2**a,M0),-1)
for r in range(N0):arr[r%(2**a),r%M0]=r
im=ax.pcolormesh(np.arange(arr.shape[1]+1)-.5,np.arange(arr.shape[0]+1)-.5,arr,shading='flat',cmap='Greys',rasterized=False)
ax.set_ylim(arr.shape[0]-.5,-.5)
for i in range(2**a):
    for j in range(M0):ax.text(j,i,str(int(arr[i,j])),ha='center',va='center',fontsize=7)
ax.set_xlabel('residue modulo 5');ax.set_ylabel('residue modulo 8')
ax.set_title('CRT addresses for residues modulo 40')
save(fig,'15_crt_packets.pdf')

# 16. theorem boundary
fig,ax=plt.subplots(figsize=(8.2,2.8));ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,2.8)
box(ax,(1.2,1.4),'proved identities',1.8,.65)
box(ax,(3.6,1.4),'uniform congruence\nand period theorems',2.3,.65)
box(ax,(6.3,1.4),'finite verification',1.9,.65)
box(ax,(8.8,1.4),'open valuation\nand global gluing',2.0,.65)
arrow(ax,(2.1,1.4),(2.4,1.4));arrow(ax,(4.75,1.4),(5.35,1.4));arrow(ax,(7.25,1.4),(7.8,1.4))
save(fig,'16_claim_boundary.pdf')

print(f'generated {len(list(OUT.glob("*.pdf")))} vector figures')
