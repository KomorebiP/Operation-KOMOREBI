from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

OUT = Path(__file__).resolve().parents[1] / 'figures'
OUT.mkdir(parents=True, exist_ok=True)


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT / name, format='pdf', bbox_inches='tight')
    plt.close()

# 1. Polyphase coordinates
n = np.arange(32)
x = 0.55*np.sin(0.34*n) + 0.28*np.cos(0.11*n) + 0.04*n/32
fig, axes = plt.subplots(5, 1, figsize=(7.2, 7.7), sharex=False)
axes[0].plot(n, x, marker='o', markersize=2.8)
axes[0].set_title('Signal and its four exact residue channels')
axes[0].set_ylabel('signal')
for r in range(4):
    q = np.arange(len(x[r::4]))
    axes[r+1].stem(q, x[r::4], basefmt=' ')
    axes[r+1].set_ylabel(f'phase {r}')
axes[-1].set_xlabel('coarse address')
save('01_polyphase_coordinates.pdf')

# 2. Transfer blocks
h = {0:1.0,1:2.0,2:3.0,3:4.0,4:5.0}
weights = np.zeros((4,4))
for k in range(4):
    for s in range(4):
        for m in range(-2,3):
            q = 4*m + k - s
            if q in h:
                weights[k,s] += abs(h[q])
fig, ax = plt.subplots(figsize=(5.6,4.7))
im = ax.imshow(weights)
for i in range(4):
    for j in range(4):
        ax.text(j,i,f'{weights[i,j]:.0f}',ha='center',va='center')
ax.set_xticks(range(4), [f'input {r}' for r in range(4)])
ax.set_yticks(range(4), [f'output {r}' for r in range(4)])
ax.set_title('Absolute tap weight in four phase transfer blocks')
fig.colorbar(im, ax=ax, label='absolute tap sum')
save('02_transfer_blocks.pdf')

# 3. Frame perturbation singular values
w = np.linspace(0,2*np.pi,500)
s1 = 1.0 + 0.18*np.cos(w)
s2 = 0.78 + 0.12*np.sin(2*w)
p1 = s1 + 0.08*np.sin(3*w)
p2 = s2 - 0.07*np.cos(2*w)
fig, ax = plt.subplots(figsize=(6.7,4.2))
ax.plot(w, s1, label='largest singular value')
ax.plot(w, s2, label='smallest singular value')
ax.plot(w, p1, linestyle=':', label='perturbed largest')
ax.plot(w, p2, linestyle=':', label='perturbed smallest')
ax.set_xlabel('frequency')
ax.set_ylabel('singular value')
ax.set_title('Frame stability is controlled pointwise in frequency')
ax.legend()
save('03_frame_stability.pdf')

# 4. Packet tree
fig, ax = plt.subplots(figsize=(7.0,4.8))
levels = {0:[0.5],1:[0.25,0.75],2:[0.125,0.375,0.625,0.875],3:[0.0625,0.1875,0.3125,0.4375,0.5625,0.6875,0.8125,0.9375]}
for lev,xs in levels.items():
    y=1-lev*0.29
    for x0 in xs:
        ax.scatter([x0],[y],s=40)
for lev in range(3):
    for i,x0 in enumerate(levels[lev]):
        y0=1-lev*0.29
        for child in (2*i,2*i+1):
            x1=levels[lev+1][child]; y1=1-(lev+1)*0.29
            ax.plot([x0,x1],[y0,y1],linewidth=0.9)
# Highlight an admissible pruning with rectangles around leaves at mixed depths
for x0,y0 in [(0.25,0.71),(0.625,0.42),(0.8125,0.13),(0.9375,0.13)]:
    ax.add_patch(Rectangle((x0-0.035,y0-0.035),0.07,0.07,fill=False,linewidth=1.5))
ax.text(0.5,1.07,'root')
ax.text(0.5,-0.03,'boxed nodes form one admissible pruned basis',ha='center')
ax.set_xlim(0,1); ax.set_ylim(-0.08,1.12); ax.axis('off')
ax.set_title('A complete packet tree and one admissible pruning')
save('04_packet_tree.pdf')

# 5. Best basis recursion
leaves=np.arange(8)
raw=np.array([0.82,0.22,0.31,0.76,0.18,0.25,0.62,0.70])
selected=np.array([0.31,0.31,0.31,0.31,0.18,0.25,0.62,0.70])
fig,ax=plt.subplots(figsize=(6.8,4.0))
ax.plot(leaves,raw,marker='o',label='finest leaf costs')
ax.plot(leaves,selected,marker='s',label='cost after optimal pruning')
ax.set_xlabel('terminal packet address')
ax.set_ylabel('additive cost')
ax.set_title('Dynamic recursion compares retaining and splitting')
ax.legend()
save('05_best_basis.pdf')

# 6. Higher order singular packets
z=np.linspace(0,1,800)
tau=0.43
phi0=(z>=tau).astype(float)
phi1=np.maximum(z-tau,0)
phi2=0.5*np.maximum(z-tau,0)**2
fig,ax=plt.subplots(figsize=(6.8,4.1))
ax.plot(z,phi0,label='value jump packet')
ax.plot(z,phi1,label='slope jump packet')
ax.plot(z,phi2,label='curvature jump packet')
ax.axvline(tau,linestyle=':')
ax.set_xlabel('position')
ax.set_ylabel('packet value')
ax.set_title('Truncated power packets encode derivative jumps')
ax.legend()
save('06_higher_order_packets.pdf')

# 7. Known packet reconstruction
z=np.linspace(0,1,1024,endpoint=False)
s=0.24*np.sin(2*np.pi*z)+0.12*np.cos(6*np.pi*z)
j=0.75*(z>=0.36)-0.48*(z>=0.72)
f=s+j
# low Fourier approximation only to smooth part
K=8
coef=np.fft.fft(s)
mask=np.zeros_like(coef,dtype=bool); mask[:K+1]=True; mask[-K:]=True
qs=np.fft.ifft(coef*mask).real
qf=np.fft.ifft(np.fft.fft(f)*mask).real
fig,axes=plt.subplots(2,1,figsize=(7.2,6.0),sharex=True)
axes[0].plot(z,f,label='original')
axes[0].plot(z,qf,label='global Fourier approximation')
axes[0].plot(z,qs+j,label='retained packet approximation')
axes[0].legend(); axes[0].set_ylabel('signal')
axes[1].plot(z,np.abs(f-qf),label='global error')
axes[1].plot(z,np.abs(f-(qs+j)),label='retained packet error')
axes[1].legend(); axes[1].set_ylabel('absolute error'); axes[1].set_xlabel('position')
axes[0].set_title('The jump packet is retained while only the smooth part is approximated')
save('07_known_packet_reconstruction.pdf')

# 8. Overlap matrix
M=np.array([[0.46,0.02,0.00],[0.03,0.24,0.02],[0.00,0.03,0.20]])
fig,ax=plt.subplots(figsize=(5.5,4.6))
im=ax.imshow(M)
for i in range(3):
    for j in range(3): ax.text(j,i,f'{M[i,j]:.2f}',ha='center',va='center')
ax.set_xticks(range(3),['estimated 0','estimated 1','estimated 2'])
ax.set_yticks(range(3),['true 0','true 1','true 2'])
ax.set_title('Region overlap matrix')
fig.colorbar(im,ax=ax,label='measure')
save('08_overlap_matrix.pdf')

# 9. Jump detection
n=256; hstep=1/n; t=np.arange(n+1)*hstep
s=0.12*np.sin(2*np.pi*t)+0.04*t
j=0.72*(t>=0.31)-0.46*(t>=0.67)
f=s+j
rng=np.random.default_rng(10)
noise=0.006*rng.standard_normal(n+1)
y=f+noise
D=np.diff(y)
fig,axes=plt.subplots(2,1,figsize=(7.3,5.9),sharex=False)
axes[0].plot(t,y,label='observed samples')
axes[0].plot(t,f,label='underlying signal')
axes[0].legend(); axes[0].set_ylabel('value')
axes[1].stem(np.arange(n),np.abs(D),basefmt=' ')
axes[1].axhline(0.12,linestyle=':',label='threshold')
axes[1].legend(); axes[1].set_xlabel('grid cell'); axes[1].set_ylabel('contrast magnitude')
axes[0].set_title('Separated jumps create isolated contrast cells')
save('09_jump_detection.pdf')

# 10. Haar scale separation
jvals=np.arange(2,11)
L=2.0**(-jvals)
smooth=0.25*L**1.5
jump=0.22*L**0.5
fig,ax=plt.subplots(figsize=(6.4,4.2))
ax.loglog(L,smooth,marker='o',label='smooth coefficient bound')
ax.loglog(L,jump,marker='s',label='separated jump coefficient')
ax.set_xlabel('support length')
ax.set_ylabel('coefficient magnitude')
ax.set_title('Smooth and jump coefficients have different scale laws')
ax.legend()
save('10_haar_scale_separation.pdf')

# 11. Shifted grid geometry
fig,ax=plt.subplots(figsize=(7.0,3.4))
L=1.0; tau=1.08
for k in range(4):
    ax.plot([k,k],[0.65,1.0],linewidth=1.0)
    ax.plot([k+0.5,k+0.5],[0.0,0.35],linewidth=1.0)
ax.plot([0,4],[0.82,0.82],linewidth=0.8)
ax.plot([0,4],[0.18,0.18],linewidth=0.8)
ax.scatter([tau],[0.82],s=55,label='jump in original grid')
ax.scatter([tau],[0.18],s=55,label='same jump in shifted grid')
ax.annotate('distance at least one quarter cell\nin one of the two grids',xy=(tau,0.18),xytext=(1.55,0.42),arrowprops={'arrowstyle':'->'})
ax.set_xlim(0,4); ax.set_ylim(-0.05,1.08); ax.set_yticks([0.18,0.82],['half shifted grid','original grid']); ax.set_xticks(range(5))
ax.set_title('Two interlaced grids remove dyadic boundary alignment')
ax.legend(loc='upper right')
save('11_shifted_grids.pdf')

# 12. Gibbs comparison
z=np.linspace(-1,1,1600,endpoint=False)
f=np.where(np.abs(z)<0.38,1.0,0.0)+0.16*np.cos(2*np.pi*z)
# Smooth component cosine retained with exact rectangular packet
j=np.where(np.abs(z)<0.38,1.0,0.0)
s=0.16*np.cos(2*np.pi*z)
K=20
coef=np.fft.fft(f); mask=np.zeros_like(coef,dtype=bool); mask[:K+1]=True; mask[-K:]=True
global_approx=np.fft.ifft(coef*mask).real
coef_s=np.fft.fft(s); smooth_approx=np.fft.ifft(coef_s*mask).real
fig,ax=plt.subplots(figsize=(7.1,4.4))
ax.plot(z,f,label='target')
ax.plot(z,global_approx,label='global Fourier partial sum')
ax.plot(z,smooth_approx+j,label='exact packet plus smooth partial sum')
ax.set_xlabel('position'); ax.set_ylabel('value'); ax.set_title('Packet separation changes the approximation problem')
ax.legend()
save('12_gibbs_comparison.pdf')

# 13. Sparse comparison
budgets=np.array([16,32,64,128,256])
haar=np.array([1.7999e-1,3.8414e-2,1.6267e-2,1.7387e-3,1.5870e-4])
fourier=np.array([6.6522e-2,4.9153e-2,3.8056e-2,2.5631e-2,1.7424e-2])
fig,ax=plt.subplots(figsize=(6.4,4.2))
ax.loglog(budgets,haar,marker='o',label='fixed Haar packet basis')
ax.loglog(budgets,fourier,marker='s',label='Fourier coefficients')
ax.set_xlabel('retained coefficients'); ax.set_ylabel('root mean square error')
ax.set_title('One finite sparse approximation comparison')
ax.legend()
save('13_sparse_comparison.pdf')

# 14. Smith coordinates
th=np.linspace(0,2*np.pi,600)
fig,ax=plt.subplots(figsize=(5.6,5.6))
ax.plot(np.cos(th),np.sin(th))
for rho in (0.25,0.5,0.75): ax.plot(rho*np.cos(th),rho*np.sin(th),linewidth=0.8)
for ang in np.linspace(0,2*np.pi,12,endpoint=False): ax.plot([0,math.cos(ang)],[0,math.sin(ang)],linewidth=0.6)
pts=np.exp(1j*np.linspace(0,2*np.pi,8,endpoint=False))*0.68
ax.scatter(pts.real,pts.imag,s=30)
ax.set_aspect('equal'); ax.set_xlim(-1.08,1.08); ax.set_ylim(-1.08,1.08)
ax.set_xlabel('real reflection coordinate'); ax.set_ylabel('imaginary reflection coordinate')
ax.set_title('Cyclic phase action in Cayley coordinates')
save('14_smith_coordinates.pdf')

print(f'generated {len(list(OUT.glob("*.pdf")))} vector figures')
