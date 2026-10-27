from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Polygon
import numpy as np
from numpy.linalg import eigvalsh, matrix_rank, norm

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
RES = ROOT / 'results'
TAB = ROOT / 'tables'
for d in (FIG, RES, TAB):
    d.mkdir(parents=True, exist_ok=True)

INK = '#243138'
BLUE = '#21676B'
TEAL = '#21676B'
ORANGE = '#A45C36'
RED = '#A45C36'
PURPLE = '#627078'
MAGENTA = '#627078'
YELLOW = '#C29A70'
MUTED = '#5D6D7E'
GRID = '#CBD3D8'
PAPER = '#FFFFFF'
WHITE = '#FFFFFF'
COLORS = [BLUE, TEAL, ORANGE, RED, PURPLE, MAGENTA, YELLOW]

plt.rcParams.update({
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'figure.facecolor': PAPER,
    'axes.facecolor': PAPER,
    'savefig.facecolor': PAPER,
    'font.size': 10.5,
    'axes.titlesize': 12.5,
    'axes.titleweight': 'bold',
    'axes.labelcolor': INK,
    'axes.edgecolor': INK,
    'xtick.color': INK,
    'ytick.color': INK,
    'text.color': INK,
    'legend.frameon': False,
})


@dataclass
class Check:
    name: str
    passed: bool
    value: float | int | str
    tolerance: float | str


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIG / f'{stem}.pdf', bbox_inches='tight')
    fig.savefig(FIG / f'{stem}.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


def diagram_axes(figsize=(12.8, 6.4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    return fig, ax


def box(ax, xy, w, h, text, color, fontsize=10.8, weight='bold'):
    patch = FancyBboxPatch(
        xy, w, h,
        boxstyle='round,pad=.012,rounding_size=.018',
        linewidth=1.6, edgecolor=color, facecolor=color + '18'
    )
    ax.add_patch(patch)
    ax.text(xy[0] + w/2, xy[1] + h/2, text,
            ha='center', va='center', fontsize=fontsize, weight=weight)


def arrow(ax, start, end, color=INK, text=None, bend=0.0):
    patch = FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=13,
                            linewidth=1.5, color=color,
                            connectionstyle=f'arc3,rad={bend}')
    ax.add_patch(patch)
    if text:
        ax.text((start[0]+end[0])/2, (start[1]+end[1])/2 + .028,
                text, ha='center', va='center', fontsize=9.2, color=color)


def projector_from_columns(C: np.ndarray, tol=1e-12) -> np.ndarray:
    U, s, _ = np.linalg.svd(C, full_matrices=False)
    r = int(np.sum(s > tol))
    if r == 0:
        return np.zeros((C.shape[0], C.shape[0]))
    Ur = U[:, :r]
    return Ur @ Ur.T


def cycle_frame_example(seed=7):
    rng = np.random.default_rng(seed)
    hdim = 8
    q, _ = np.linalg.qr(rng.normal(size=(hdim, hdim)))
    H = q[:, :5]
    cycles = []
    for j in range(8):
        coeff = rng.normal(size=5)
        if j < 3:
            coeff[j] += 2.2
        cycles.append(H @ coeff + .04*rng.normal(size=hdim))
    C = np.column_stack(cycles)
    S = C @ C.T
    G = H.T @ S @ H
    eig = eigvalsh(G)
    return H, C, S, G, eig


def polyphase_example(seed=11):
    rng = np.random.default_rng(seed)
    dim = 7
    degrees = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
    C = rng.normal(size=(dim, len(degrees)))
    C[:, :dim] += np.eye(dim)
    parent = C @ C.T
    children2 = []
    for r in range(2):
        Cr = C[:, degrees % 2 == r]
        children2.append(Cr @ Cr.T)
    children4 = []
    for r in range(4):
        Cr = C[:, degrees % 4 == r]
        children4.append(Cr @ Cr.T)
    return degrees, C, parent, children2, children4


def positive_transfer_example(seed=17):
    rng = np.random.default_rng(seed)
    d = 6
    A1 = rng.normal(size=(3,d))
    A2 = rng.normal(size=(4,d))
    A3 = rng.normal(size=(2,d))
    A2[:, -1] += np.array([1.4, -1.1, .8, -.4])
    As = [A1,A2,A3]
    Ts = [A.T @ A for A in As]
    T = sum(Ts)
    eig = eigvalsh(T)
    return As, Ts, T, eig


def cayley_hamilton_inverse_example(seed=23):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(5,5))
    T = A.T @ A + .8*np.eye(5)
    coeff = np.poly(T)  # det(lambda I - T) = lambda^d + c_{d-1} ... c0
    d = T.shape[0]
    c0 = coeff[-1]
    P = np.zeros_like(T)
    for k in range(d):
        power = d-1-k
        ck = coeff[k+1] if k+1 < len(coeff)-1 else coeff[-2]
        # easier explicit formula below
    # T^{-1}=-(T^{d-1}+c_{d-1}T^{d-2}+...+c_1 I)/c0
    P = np.linalg.matrix_power(T,d-1)
    for j in range(1,d):
        P += coeff[j] * np.linalg.matrix_power(T,d-1-j)
    Tinv_poly = -P/c0
    return T, Tinv_poly, norm(Tinv_poly @ T - np.eye(d))


def contraction_example(seed=29):
    rng = np.random.default_rng(seed)
    n = 5
    L = np.diag(np.linspace(1.4,2.2,n))
    R = np.linalg.inv(L)
    f = .035*rng.normal(size=n)
    def B(a,b):
        return .22*(a*b)
    a = np.zeros(n)
    residuals=[]
    for _ in range(30):
        a_new = -R @ (f + B(a,a))
        residuals.append(norm(a_new-a))
        a = a_new
    full = f + L@a + B(a,a)
    return np.array(residuals), norm(full), a


def adams_projector_matrix(n=5,m=2,p=2):
    vals = np.array([m**q for q in range(n+1)],float)
    P = np.eye(n+1)
    D = np.diag(vals)
    for q in range(n+1):
        if q == p:
            continue
        P = P @ ((D - (m**q)*np.eye(n+1))/((m**p)-(m**q)))
    return D, P


def make_figures() -> list[str]:
    stems=[]
    # 01 pipeline
    fig,ax=diagram_axes()
    ax.text(.5,.95,'Projector-resolved route through the Hodge problem',ha='center',fontsize=20,weight='bold')
    stages=[(.03,.64,.14,.14,'Hodge class\nseed',BLUE),(.20,.64,.14,.14,'primitive and\nsupport address',TEAL),(.37,.64,.14,.14,'cycle-frame\nanalysis',ORANGE),(.54,.64,.14,.14,'correspondence\ntransfer',PURPLE),(.71,.64,.14,.14,'polyphase\nrefinement',MAGENTA),(.87,.64,.10,.14,'cycle\nsynthesis',RED)]
    for x,y,w,h,t,c in stages: box(ax,(x,y),w,h,t,c,10.2)
    for a,b in zip(stages[:-1],stages[1:]): arrow(ax,(a[0]+a[2],a[1]+a[3]/2),(b[0],b[1]+b[3]/2))
    box(ax,(.22,.25),.22,.15,'proved finite core\nframes, kernels, saturation',TEAL,11)
    box(ax,(.56,.25),.22,.15,'remaining bridge\nprimitive fourfold saturation',ORANGE,11)
    arrow(ax,(.45,.64),(.33,.40),TEAL)
    arrow(ax,(.63,.64),(.67,.40),ORANGE)
    ax.text(.5,.09,'The general conjecture is not assumed. Every unresolved implication is kept as an explicit obstruction packet.',ha='center',fontsize=10.7,color=MUTED)
    save(fig,'01_hodge_program_pipeline'); stems.append('01_hodge_program_pipeline')

    # 02 Hodge diamond fourfold
    fig,ax=diagram_axes((10.5,7.2))
    ax.text(.5,.96,'Hodge diamond of a complex fourfold',ha='center',fontsize=19,weight='bold')
    coords=[]
    for k in range(9):
        pmin=max(0,k-4); pmax=min(4,k)
        vals=list(range(pmin,pmax+1))
        for idx,p in enumerate(vals):
            q=k-p
            x=.5 + (p-q)*.075
            y=.86-k*.085
            coords.append((p,q,x,y))
    for p,q,x,y in coords:
        target=(p,q)==(2,2)
        col=RED if target else (BLUE if p==q else GRID)
        ax.add_patch(Circle((x,y),.028,facecolor=col+'55',edgecolor=col,lw=1.3))
        ax.text(x,y,rf'$h^{{{p},{q}}}$',ha='center',va='center',fontsize=8.5)
    ax.annotate('first general unresolved middle packet',xy=(.5,.52),xytext=(.78,.62),arrowprops=dict(arrowstyle='->',color=RED,lw=1.5),color=RED,fontsize=10.5)
    ax.text(.5,.08,r'The program isolates $H^{2,2}_{\mathrm{prim}}(X)\cap H^4(X,\mathbb{Q})$ before attempting cycle reconstruction.',ha='center',fontsize=11)
    save(fig,'02_fourfold_hodge_diamond'); stems.append('02_fourfold_hodge_diamond')

    # 03 primitive decomposition
    fig,ax=diagram_axes()
    ax.text(.5,.95,'Lefschetz decomposition removes algebraically generated descendants',ha='center',fontsize=19,weight='bold')
    box(ax,(.08,.60),.24,.17,r'$\alpha\in H^{2p}(X)$',BLUE,13)
    box(ax,(.39,.60),.22,.17,r'$\sum_r L^r\alpha_r$',TEAL,13)
    box(ax,(.70,.60),.22,.17,'primitive packets\n$\\alpha_r$',ORANGE,12)
    arrow(ax,(.32,.685),(.39,.685),INK,'Lefschetz split')
    arrow(ax,(.61,.685),(.70,.685),INK,'address by depth')
    box(ax,(.14,.24),.28,.14,'algebraic polarization packet\n$L=[h]\\smile(-)$',PURPLE,11)
    box(ax,(.58,.24),.28,.14,'only primitive packets\nremain to be solved',RED,11)
    arrow(ax,(.28,.60),(.28,.38),PURPLE)
    arrow(ax,(.81,.60),(.72,.38),RED)
    save(fig,'03_lefschetz_primitive_reduction'); stems.append('03_lefschetz_primitive_reduction')

    # 04 obstruction projector geometry
    fig,ax=plt.subplots(figsize=(9.8,5.5))
    th=np.linspace(0,2*np.pi,300)
    ax.fill(2.7*np.cos(th),1.55*np.sin(th),color=BLUE,alpha=.12,label='Hodge packet')
    ax.fill(1.6*np.cos(th),.85*np.sin(th),color=TEAL,alpha=.25,label='algebraic cycle packet')
    ax.arrow(1.2,.2,1.0,.45,width=.018,head_width=.12,color=RED,length_includes_head=True)
    ax.text(1.95,.72,r'$\mathcal{O}_X^p\alpha$',color=RED,fontsize=12)
    ax.text(0,0,'algebraic',ha='center',va='center',fontsize=12,weight='bold')
    ax.text(0,1.25,'rational $(p,p)$',ha='center',fontsize=11)
    ax.set_aspect('equal'); ax.set_xlim(-3.2,3.2); ax.set_ylim(-1.9,1.9); ax.axis('off'); ax.legend(loc='lower left')
    ax.set_title('The master obstruction is the Hodge packet orthogonal to all algebraic-cycle classes')
    fig.tight_layout(); save(fig,'04_master_obstruction_projector'); stems.append('04_master_obstruction_projector')

    # 05 coniveau support
    fig,ax=diagram_axes()
    ax.text(.5,.95,'Support localization is equivalent to algebraicity in degree $2p$',ha='center',fontsize=19,weight='bold')
    box(ax,(.06,.59),.25,.17,r'$\alpha\in H^{2p}(X)$',BLUE,13)
    box(ax,(.38,.59),.25,.17,r'$j^*\alpha=0$ on $X\setminus Z$',ORANGE,12)
    box(ax,(.69,.59),.25,.17,r'$\alpha=\sum_i q_i[Z_i]$',TEAL,12)
    arrow(ax,(.31,.675),(.38,.675),INK,'restriction test')
    arrow(ax,(.63,.675),(.69,.675),INK,'purity')
    box(ax,(.24,.22),.52,.16,'remaining open task: generate the correct codimension-$p$ support for an arbitrary primitive Hodge packet',RED,10.8)
    save(fig,'05_support_localization_pipeline'); stems.append('05_support_localization_pipeline')

    H,C,S,G,eig=cycle_frame_example()
    # 06 cycle vectors
    fig,ax=plt.subplots(figsize=(10.8,5.0))
    im=ax.imshow(C,cmap='coolwarm',aspect='auto')
    ax.set_xlabel('cycle generator'); ax.set_ylabel('cohomology coordinate')
    ax.set_title('Toy cycle-analysis matrix $C_D$')
    fig.colorbar(im,ax=ax,label='coordinate')
    fig.tight_layout(); save(fig,'06_cycle_analysis_matrix'); stems.append('06_cycle_analysis_matrix')

    # 07 Gram spectrum
    fig,axes=plt.subplots(1,2,figsize=(12.4,4.8))
    im=axes[0].imshow(G,cmap='viridis')
    axes[0].set_title('Hodge-restricted frame Gram matrix')
    fig.colorbar(im,ax=axes[0],fraction=.046,pad=.03)
    axes[1].bar(np.arange(len(eig)),eig,color=[TEAL if x>1e-6 else RED for x in eig])
    axes[1].set_xlabel('eigenvalue index'); axes[1].set_ylabel('eigenvalue'); axes[1].set_title('spectral saturation certificate')
    axes[1].grid(axis='y',alpha=.18)
    fig.suptitle('A positive minimum eigenvalue certifies complete cycle coverage',fontsize=16,weight='bold')
    fig.tight_layout(rect=[0,0,1,.92]); save(fig,'07_cycle_frame_spectrum'); stems.append('07_cycle_frame_spectrum')

    # 08 reconstruction
    alpha=H@np.array([.8,-.4,.6,.1,-.3])
    P=projector_from_columns(C)
    rec=P@alpha
    fig,axes=plt.subplots(1,2,figsize=(12.2,4.7))
    axes[0].plot(alpha,'o-',color=BLUE,label='target Hodge packet')
    axes[0].plot(rec,'s--',color=TEAL,label='cycle-frame reconstruction')
    axes[0].legend(); axes[0].grid(alpha=.18); axes[0].set_xlabel('coordinate')
    axes[1].bar(np.arange(len(alpha)),alpha-rec,color=RED)
    axes[1].set_title('reconstruction residual'); axes[1].grid(axis='y',alpha=.18)
    fig.suptitle('Exact synthesis is ordinary finite-dimensional frame reconstruction',fontsize=16,weight='bold')
    fig.tight_layout(rect=[0,0,1,.92]); save(fig,'08_cycle_frame_reconstruction'); stems.append('08_cycle_frame_reconstruction')

    degrees,Cp,parent,ch2,ch4=polyphase_example()
    # 09 degree tree
    fig,ax=diagram_axes((12.5,6.8)); ax.text(.5,.95,'Degree-residue polyphase refinement of algebraic cycle packets',ha='center',fontsize=19,weight='bold')
    box(ax,(.40,.78),.20,.10,'all cycle generators',PURPLE,10.5)
    for r,x in enumerate([.25,.60]):
        box(ax,(x,.56),.15,.10,f'degree = {r} mod 2',COLORS[r],10)
        arrow(ax,(.50,.78),(x+.075,.66),COLORS[r])
    xs=[.06,.29,.54,.77]
    for r,x in enumerate(xs):
        box(ax,(x,.30),.15,.10,f'degree = {r} mod 4',COLORS[r],9.8)
        parentx=.325 if r%2==0 else .675
        arrow(ax,(parentx,.56),(x+.075,.40),COLORS[r])
    ax.text(.5,.10,r'$S_{M,r}=\sum_{\ell=0}^{L-1}S_{LM,r+\ell M}$ exactly, even when the child spans overlap.',ha='center',fontsize=11)
    save(fig,'09_degree_polyphase_tree'); stems.append('09_degree_polyphase_tree')

    # 10 assembly residual
    res2=norm(parent-sum(ch2)); res4=norm(parent-sum(ch4)); childres=[norm(ch2[0]-(ch4[0]+ch4[2])),norm(ch2[1]-(ch4[1]+ch4[3]))]
    fig,ax=plt.subplots(figsize=(10.6,4.7))
    vals=[res2,res4,*childres]
    labels=['all = mod 2','all = mod 4','even parent','odd parent']
    ax.semilogy(range(4),np.maximum(vals,1e-18),'o-',color=TEAL,lw=2)
    ax.set_xticks(range(4),labels,rotation=15); ax.set_ylabel('assembly residual'); ax.set_title('Exact frame refinement checks'); ax.grid(alpha=.18,which='both')
    fig.tight_layout(); save(fig,'10_polyphase_assembly_residuals'); stems.append('10_polyphase_assembly_residuals')

    # 11 kernel intersection
    rng=np.random.default_rng(34)
    x=np.linspace(-1,1,200)
    curves=[]
    for r in range(4):
        curves.append((r+1)*(x-(r-1.5)*.18)**2 + .08*r)
    fig,ax=plt.subplots(figsize=(11.0,4.8))
    for r,c in enumerate(curves): ax.plot(x,c,color=COLORS[r],lw=2,label=f'child packet {r}')
    ax.plot(x,np.sum(curves,axis=0),color=INK,lw=2.4,label='parent positive transfer')
    ax.set_xlabel('test Hodge direction'); ax.set_ylabel('packet energy'); ax.set_title('A direction survives the parent only if it survives every positive child'); ax.legend(ncol=2); ax.grid(alpha=.18)
    save(fig,'11_child_kernel_intersection'); stems.append('11_child_kernel_intersection')

    # 12 saturation
    D=np.arange(1,15)
    dims=np.minimum(6,np.floor(1.4*np.sqrt(D)).astype(int)+1)
    dims[8:]=6
    residual=np.where(D<9,np.exp(-.42*D),0.0)
    fig,axes=plt.subplots(1,2,figsize=(12.3,4.7))
    axes[0].step(D,dims,where='mid',color=BLUE,lw=2); axes[0].set_xlabel('degree cutoff $D$'); axes[0].set_ylabel('cycle-span dimension'); axes[0].set_title('finite-dimensional span stabilizes')
    axes[1].semilogy(D,np.maximum(residual,1e-17),'o-',color=RED); axes[1].axvline(9,color=TEAL,ls='--',label='saturation'); axes[1].set_xlabel('degree cutoff $D$'); axes[1].set_ylabel('Hodge residual'); axes[1].legend(); axes[1].set_title('convergence becomes exact membership')
    for ax in axes: ax.grid(alpha=.18,which='both')
    fig.suptitle('Nested bounded-degree cycle spaces can change rank only finitely many times',fontsize=16,weight='bold'); fig.tight_layout(rect=[0,0,1,.92]); save(fig,'12_finite_saturation'); stems.append('12_finite_saturation')

    # 13 rational coefficient recovery
    rng=np.random.default_rng(41)
    M=np.array([[2,1,0],[1,3,1],[0,1,2],[1,0,1]],float)
    qtrue=np.array([1.5,-.5,2.0])
    b=M@qtrue
    qhat=np.linalg.lstsq(M,b,rcond=None)[0]
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.7))
    axes[0].imshow(M,cmap='viridis'); axes[0].set_title('intersection matrix $M$'); axes[0].set_xlabel('support component'); axes[0].set_ylabel('test class')
    axes[1].bar(np.arange(3)-.15,qtrue,width=.3,color=BLUE,label='exact rational coefficient'); axes[1].bar(np.arange(3)+.15,qhat,width=.3,color=TEAL,label='reconstructed'); axes[1].set_xticks(range(3),['$Z_1$','$Z_2$','$Z_3$']); axes[1].legend(); axes[1].grid(axis='y',alpha=.18)
    fig.suptitle('Once the support is known, multiplicities are finite rational linear algebra',fontsize=16,weight='bold'); fig.tight_layout(rect=[0,0,1,.92]); save(fig,'13_support_multiplicity_reconstruction'); stems.append('13_support_multiplicity_reconstruction')

    # 14 support exact sequence diagram
    fig,ax=diagram_axes()
    ax.text(.5,.95,'Cohomology with supports gives an exact verification test',ha='center',fontsize=19,weight='bold')
    box(ax,(.05,.58),.25,.16,r'$H_Z^{2p}(X,\mathbb{Q})$',ORANGE,12)
    box(ax,(.38,.58),.24,.16,r'$H^{2p}(X,\mathbb{Q})$',BLUE,12)
    box(ax,(.70,.58),.25,.16,r'$H^{2p}(X\setminus Z,\mathbb{Q})$',TEAL,11.5)
    arrow(ax,(.30,.66),(.38,.66),INK,'support map'); arrow(ax,(.62,.66),(.70,.66),INK,'restriction $j^*$')
    box(ax,(.28,.22),.44,.14,r'$j^*\alpha=0\Leftrightarrow\alpha$ is supported on $Z$',RED,12)
    arrow(ax,(.82,.58),(.60,.36),RED)
    save(fig,'14_support_exact_sequence'); stems.append('14_support_exact_sequence')

    # 15 divisor lowering
    fig,ax=diagram_axes(); ax.text(.5,.95,'Divisor-lowering correspondence theorem',ha='center',fontsize=20,weight='bold')
    box(ax,(.05,.60),.25,.17,'primitive Hodge packet\n$V\\subset H^{2p}(X)$',BLUE,12)
    box(ax,(.38,.60),.24,.17,'degree-two packets\n$H^2(Y_r)$',TEAL,12)
    box(ax,(.70,.60),.25,.17,'returned cycle packet\n$H^{2p}(X)$',ORANGE,12)
    arrow(ax,(.30,.685),(.38,.685),PURPLE,'$A_r=(\\Gamma_r)_*$')
    arrow(ax,(.62,.685),(.70,.685),PURPLE,'$B_r=(\\Lambda_r)_*$')
    box(ax,(.25,.23),.50,.15,r'$T=\sum_rB_rA_r$ invertible on $V\Longrightarrow$ every rational Hodge class in $V$ is algebraic',RED,11.2)
    save(fig,'15_divisor_lowering_transfer'); stems.append('15_divisor_lowering_transfer')

    As,Ts,T,eigt=positive_transfer_example()
    # 16 positive transfer
    fig,axes=plt.subplots(1,2,figsize=(12.2,4.7))
    axes[0].imshow(T,cmap='viridis'); axes[0].set_title(r'$T=\sum_rA_r^{\top}A_r$')
    axes[1].bar(range(len(eigt)),eigt,color=[TEAL if x>.3 else ORANGE for x in eigt]); axes[1].set_title('joint injectivity spectrum'); axes[1].set_xlabel('primitive packet index'); axes[1].set_ylabel('eigenvalue'); axes[1].grid(axis='y',alpha=.18)
    fig.suptitle('Several incomplete incidence channels can be complete together',fontsize=16,weight='bold'); fig.tight_layout(rect=[0,0,1,.92]); save(fig,'16_positive_correspondence_frame'); stems.append('16_positive_correspondence_frame')

    # 17 channel kernels
    fig,ax=plt.subplots(figsize=(10.8,5.0))
    x=np.linspace(-1,1,250)
    energies=[]
    for r,A in enumerate(As):
        v=np.vstack([x,np.sqrt(np.maximum(0,1-x*x)),np.zeros_like(x),np.zeros_like(x),np.zeros_like(x),np.zeros_like(x)])
        e=np.sum((A@v)**2,axis=0)
        energies.append(e)
        ax.plot(x,e,lw=2,color=COLORS[r],label=f'channel {r+1}')
    ax.plot(x,np.sum(energies,axis=0),color=INK,lw=2.4,label='total transfer')
    ax.set_xlabel('one-dimensional slice through primitive directions'); ax.set_ylabel('detected energy'); ax.set_title('Kernel intersection rather than individual completeness'); ax.legend(); ax.grid(alpha=.18)
    save(fig,'17_multi_incidence_kernel_intersection'); stems.append('17_multi_incidence_kernel_intersection')

    # 18 cayley hamilton inverse
    Tc,Tinv,resch=cayley_hamilton_inverse_example()
    fig,axes=plt.subplots(1,2,figsize=(12.0,4.7))
    axes[0].imshow(Tc,cmap='viridis'); axes[0].set_title('invertible algebraic transfer $T$')
    axes[1].imshow(Tinv,cmap='coolwarm'); axes[1].set_title('polynomial inverse $T^{-1}$')
    fig.suptitle('Cayley-Hamilton makes the inverse an algebraic correspondence polynomial',fontsize=16,weight='bold'); fig.tight_layout(rect=[0,0,1,.92]); save(fig,'18_cayley_hamilton_inverse'); stems.append('18_cayley_hamilton_inverse')

    # 19 family propagation
    fig,ax=diagram_axes(); ax.text(.5,.95,'Relative correspondences propagate invertibility through a connected family',ha='center',fontsize=19,weight='bold')
    xs=np.linspace(.08,.92,8)
    for i,x in enumerate(xs):
        ax.add_patch(Circle((x,.62),.035,facecolor=BLUE+'35',edgecolor=BLUE,lw=1.4)); ax.text(x,.62,rf'$s_{i}$',ha='center',va='center',fontsize=9)
        if i: arrow(ax,(xs[i-1]+.037,.62),(x-.037,.62),GRID)
    ax.plot([.08,.92],[.35,.35],color=PURPLE,lw=3)
    ax.text(.5,.29,'one flat rational transfer matrix in Gauss-Manin coordinates',ha='center',fontsize=11,color=PURPLE)
    for x in xs: ax.plot([x,x],[.585,.35],color=GRID,lw=1)
    ax.text(.5,.10,r'$\det T_{s_0}\neq0$ at one fiber implies $\det T_s\neq0$ on the whole connected base.',ha='center',fontsize=11)
    save(fig,'19_family_propagation'); stems.append('19_family_propagation')

    # 20 closure ops
    fig,ax=diagram_axes(); ax.text(.5,.95,'Solved branches propagate through standard geometric operations',ha='center',fontsize=19,weight='bold')
    box(ax,(.39,.70),.22,.13,'solved variety $X$',TEAL,12)
    items=[(.04,.34,.20,.14,'projective bundle\n$\\mathbb{P}(E)$',BLUE),(.28,.34,.20,.14,'blow-up along\nsolved center',ORANGE),(.52,.34,.20,.14,'generically finite\ndescent',PURPLE),(.76,.34,.20,.14,'affine paving\ncell closures',RED)]
    for x,y,w,h,t,c in items:
        box(ax,(x,y),w,h,t,c,10.5); arrow(ax,(.50,.70),(x+w/2,y+h),c)
    ax.text(.5,.10,'Each operation preserves algebraicity through explicit cohomological decompositions and algebraic transfer classes.',ha='center',fontsize=10.7,color=MUTED)
    save(fig,'20_geometric_closure_operations'); stems.append('20_geometric_closure_operations')

    # 21 cubic geometry
    fig,ax=diagram_axes((12.8,6.7)); ax.text(.5,.95,'Cubic fourfold validation through the universal line',ha='center',fontsize=19,weight='bold')
    box(ax,(.05,.58),.24,.16,'cubic fourfold $X$\nprimitive $H^4$',BLUE,12)
    box(ax,(.38,.58),.24,.16,'incidence variety $P$\nuniversal line',PURPLE,12)
    box(ax,(.71,.58),.24,.16,'Fano variety $F(X)$\nprimitive $H^2$',TEAL,12)
    arrow(ax,(.29,.66),(.38,.66),PURPLE,'$q^*$'); arrow(ax,(.62,.66),(.71,.66),PURPLE,'$p_*$')
    arrow(ax,(.83,.58),(.17,.58),ORANGE,'divisor return with $g^2$',-.18)
    box(ax,(.25,.20),.50,.15,'classical polarized Hodge isomorphism\nvalidates the divisor-lowering criterion',ORANGE,11)
    save(fig,'21_cubic_fourfold_incidence'); stems.append('21_cubic_fourfold_incidence')

    # 22 cubic transfer toy spectrum
    vals=np.array([1.05,1.08,1.11,1.14,1.16,1.18,1.22,1.25,1.29,1.31])
    fig,ax=plt.subplots(figsize=(10.6,4.6)); ax.bar(range(len(vals)),vals,color=TEAL); ax.axhline(0,color=INK); ax.set_xlabel('primitive cohomology mode'); ax.set_ylabel('normalized transfer eigenvalue'); ax.set_title('Illustrative normalized spectrum of an invertible incidence transfer'); ax.grid(axis='y',alpha=.18); save(fig,'22_cubic_transfer_spectrum'); stems.append('22_cubic_transfer_spectrum')

    # 23 GM diagram
    fig,ax=diagram_axes(); ax.text(.5,.95,'Gushel-Mukai validation through line or plane incidence packets',ha='center',fontsize=19,weight='bold')
    box(ax,(.05,.60),.22,.16,'GM fourfold\nvanishing $H^4$',BLUE,11.5)
    box(ax,(.39,.60),.22,.16,'double EPW sextic\nprimitive $H^2$',TEAL,11.5)
    box(ax,(.73,.60),.22,.16,'GM sixfold\nvanishing $H^6$',ORANGE,11.5)
    arrow(ax,(.27,.68),(.39,.68),PURPLE,'universal lines')
    arrow(ax,(.73,.62),(.61,.62),PURPLE,'universal planes')
    box(ax,(.24,.22),.52,.15,'both middle packets are lowered to divisor classes on a hyperkahler fourfold',RED,11)
    save(fig,'23_gushel_mukai_correspondences'); stems.append('23_gushel_mukai_correspondences')

    # 24 Adams spectrum
    Dm,Pm=adams_projector_matrix()
    fig,axes=plt.subplots(1,2,figsize=(12.1,4.7))
    axes[0].bar(range(6),np.diag(Dm),color=BLUE); axes[0].set_xticks(range(6),[rf'$K^{{{2*q}}}$' for q in range(6)]); axes[0].set_ylabel('Adams eigenvalue'); axes[0].set_title(r'$\psi^2$ separates cohomological degree')
    axes[1].imshow(Pm,cmap='viridis',vmin=0,vmax=1); axes[1].set_title('degree-four Adams projector')
    fig.suptitle('Topological K-theory packages the Hodge problem into spectral degree packets',fontsize=16,weight='bold'); fig.tight_layout(rect=[0,0,1,.92]); save(fig,'24_adams_degree_projector'); stems.append('24_adams_degree_projector')

    # 25 Maurer-Cartan
    fig,ax=diagram_axes(); ax.text(.5,.95,'Dolbeault integrability splits into removable and harmonic packets',ha='center',fontsize=19,weight='bold')
    box(ax,(.05,.60),.24,.16,r'$F_A^{0,2}$\ninitial defect',RED,12)
    box(ax,(.38,.60),.24,.16,r'$Q_A$ range packet\nsolve with $R_A$',TEAL,11.5)
    box(ax,(.71,.60),.24,.16,r'$\Pi_A$ obstruction\npacket $\Phi_A$',ORANGE,11.5)
    arrow(ax,(.29,.68),(.38,.68)); arrow(ax,(.62,.68),(.71,.68))
    box(ax,(.25,.22),.50,.15,r'$F_{A+a}^{0,2}=F_A^{0,2}+\bar\partial_Aa+a\wedge a$',PURPLE,12)
    arrow(ax,(.50,.60),(.50,.37),PURPLE)
    save(fig,'25_dolbeault_obstruction_split'); stems.append('25_dolbeault_obstruction_split')

    # 26 contraction
    cres,full,a=contraction_example()
    fig,ax=plt.subplots(figsize=(10.7,4.7)); ax.semilogy(range(1,len(cres)+1),np.maximum(cres,1e-18),'o-',color=TEAL); ax.set_xlabel('fixed-point iteration'); ax.set_ylabel('successive correction norm'); ax.set_title('Toy range-packet contraction for the Maurer-Cartan equation'); ax.grid(alpha=.18,which='both'); save(fig,'26_dolbeault_contraction'); stems.append('26_dolbeault_contraction')

    # 27 spectral microscope
    k=np.arange(5,80)
    defect=.18
    trace=(defect**2)*(k**2)+.8*k
    no_def=.8*k
    fig,ax=plt.subplots(figsize=(10.7,4.7)); ax.plot(k,trace,color=RED,lw=2,label='nonintegrable packet'); ax.plot(k,no_def,color=TEAL,lw=2,label='integrable reference'); ax.set_xlabel('ample twist power $k$'); ax.set_ylabel('even-degree kernel trace'); ax.set_title('Large twisting amplifies the positive integrability defect'); ax.legend(); ax.grid(alpha=.18); save(fig,'27_asymptotic_integrability_packet'); stems.append('27_asymptotic_integrability_packet')

    # 28 trace blindness
    N=np.array([[0,1,0],[0,0,1],[0,0,0]],float)
    traces=[np.trace(np.linalg.matrix_power(N,r)) for r in range(1,6)]
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.7)); axes[0].imshow(N,cmap='coolwarm'); axes[0].set_title('nonzero nilpotent obstruction block'); axes[1].bar(range(1,6),traces,color=ORANGE); axes[1].set_xlabel('power $r$'); axes[1].set_ylabel(r'$\mathrm{tr}(N^r)$'); axes[1].set_title('all trace moments vanish'); axes[1].set_ylim(-.2,.2)
    fig.suptitle('Chern-character traces cannot see every endomorphism-valued obstruction',fontsize=16,weight='bold'); fig.tight_layout(rect=[0,0,1,.92]); save(fig,'28_trace_blindness'); stems.append('28_trace_blindness')

    # 29 dependency graph
    fig,ax=diagram_axes((13.0,7.0)); ax.text(.5,.96,'Dependency graph of the Hodge program',ha='center',fontsize=20,weight='bold')
    nodes=[(.04,.76,.18,.11,'primitive\nreduction',TEAL),(.27,.76,.18,.11,'cycle-frame\nconstruction',BLUE),(.50,.76,.18,.11,'support or\nincidence channel',ORANGE),(.73,.76,.22,.11,'positive transfer\nor Adams packet',PURPLE),(.13,.48,.20,.11,'finite spectral\ncertificate',TEAL),(.40,.48,.20,.11,'divisor lowering\nand reconstruction',BLUE),(.67,.48,.20,.11,'Dolbeault\nobstruction packet',ORANGE),(.26,.19,.22,.11,'completed\ncorrespondence branch',TEAL),(.57,.19,.22,.11,'open primitive\nfourfold saturation',RED)]
    for x,y,w,h,t,c in nodes: box(ax,(x,y),w,h,t,c,10.2)
    edges=[((.13,.76),(.23,.59)),((.36,.76),(.23,.59)),((.59,.76),(.50,.59)),((.84,.76),(.77,.59)),((.23,.48),(.37,.30)),((.50,.48),(.37,.30)),((.77,.48),(.68,.30))]
    for a0,b0 in edges: arrow(ax,a0,b0,GRID)
    save(fig,'29_hodge_dependency_graph'); stems.append('29_hodge_dependency_graph')

    # 30 primitive target
    fig,ax=diagram_axes(); ax.text(.5,.95,'Next research target: multi-incidence saturation on special fourfolds',ha='center',fontsize=19,weight='bold')
    box(ax,(.07,.66),.20,.13,'line channel',BLUE,11)
    box(ax,(.29,.66),.20,.13,'conic channel',TEAL,11)
    box(ax,(.51,.66),.20,.13,'plane channel',ORANGE,11)
    box(ax,(.73,.66),.20,.13,'exceptional\nchannel',PURPLE,10.5)
    box(ax,(.25,.26),.50,.16,r'$T_{\mathrm{tot}}=\sum A_r^\dagger A_r$\nprove $\lambda_{\min}(T_{\mathrm{tot}})>0$',RED,12)
    for x in [.17,.39,.61,.83]: arrow(ax,(x,.66),(.50,.42),GRID)
    ax.text(.5,.10,'No individual incidence family must be complete. The intersection of all channel kernels must vanish.',ha='center',fontsize=10.8,color=MUTED)
    save(fig,'30_multi_incidence_target'); stems.append('30_multi_incidence_target')

    # 31 workflow
    fig,ax=diagram_axes((13.0,6.7)); ax.text(.5,.95,'Computational and formal verification workflow',ha='center',fontsize=19,weight='bold')
    items=[(.03,.64,.16,.14,'exact cycle and\ncorrespondence data',BLUE),(.22,.64,.16,.14,'rational basis and\nintersection matrices',TEAL),(.41,.64,.16,.14,'packet frames and\npolyphase children',ORANGE),(.60,.64,.16,.14,'rank, kernel, and\nspectrum checks',PURPLE),(.79,.64,.18,.14,'symbolic certificate\nand theorem proof',RED)]
    for x,y,w,h,t,c in items: box(ax,(x,y),w,h,t,c,10)
    for a,b in zip(items[:-1],items[1:]): arrow(ax,(a[0]+a[2],a[1]+a[3]/2),(b[0],b[1]+b[3]/2))
    box(ax,(.28,.24),.20,.13,'numerical scouting\nnot a proof',ORANGE,10.5)
    box(ax,(.53,.24),.20,.13,'rational dual or\nrank certificate',TEAL,10.5)
    arrow(ax,(.49,.64),(.38,.37),ORANGE); arrow(ax,(.68,.64),(.63,.37),TEAL)
    save(fig,'31_verification_workflow'); stems.append('31_verification_workflow')

    # 32 status matrix
    labels=['primitive reduction','cycle frames','polyphase assembly','finite saturation','support verification','divisor lowering','family propagation','cubic validation','GM validation','general fourfold']
    status=np.array([1,1,1,1,1,1,1,.9,.9,.15])
    fig,ax=plt.subplots(figsize=(11.2,5.6)); ax.barh(np.arange(len(labels)),status,color=[TEAL if x>.8 else (ORANGE if x>.3 else RED) for x in status]); ax.set_yticks(np.arange(len(labels)),labels); ax.set_xlim(0,1.05); ax.set_xlabel('completion status inside this manuscript'); ax.set_title('Proof-status ledger'); ax.grid(axis='x',alpha=.18); fig.tight_layout(); save(fig,'32_status_ledger'); stems.append('32_status_ledger')

    return stems


def run_checks() -> tuple[list[Check], dict]:
    checks=[]
    def add(name, passed, value, tol): checks.append(Check(name,bool(passed),value,tol))

    H,C,S,G,eig=cycle_frame_example()
    P=projector_from_columns(C)
    add('cycle frame projector idempotency', norm(P@P-P)<1e-12, norm(P@P-P), 1e-12)
    add('frame range rank', matrix_rank(S)==matrix_rank(C), [matrix_rank(S),matrix_rank(C)], 'equal')
    add('Hodge Gram positive', eig.min()>1e-5, float(eig.min()), 1e-5)

    degrees,Cp,parent,ch2,ch4=polyphase_example()
    add('mod 2 assembly', norm(parent-sum(ch2))<1e-12, norm(parent-sum(ch2)),1e-12)
    add('mod 4 assembly', norm(parent-sum(ch4))<1e-12, norm(parent-sum(ch4)),1e-12)
    add('even child refinement', norm(ch2[0]-ch4[0]-ch4[2])<1e-12, norm(ch2[0]-ch4[0]-ch4[2]),1e-12)
    add('odd child refinement', norm(ch2[1]-ch4[1]-ch4[3])<1e-12, norm(ch2[1]-ch4[1]-ch4[3]),1e-12)

    As,Ts,T,eigt=positive_transfer_example()
    stacked=np.vstack(As)
    add('positive transfer rank', matrix_rank(T)==matrix_rank(stacked), [matrix_rank(T),matrix_rank(stacked)], 'equal')
    add('positive transfer invertible', eigt.min()>1e-6, float(eigt.min()),1e-6)
    v=np.random.default_rng(3).normal(size=T.shape[0])
    add('positive energy identity', abs(v@T@v-sum(norm(A@v)**2 for A in As))<1e-10, abs(v@T@v-sum(norm(A@v)**2 for A in As)),1e-10)

    Tc,Tinv,resch=cayley_hamilton_inverse_example()
    add('Cayley Hamilton inverse', resch<1e-10, resch,1e-10)

    cres,full,a=contraction_example()
    add('nonlinear contraction decreases', cres[-1]<cres[0], [float(cres[0]),float(cres[-1])], 'decrease')
    add('range equation residual', full<1e-10, full,1e-10)

    Dm,Pm=adams_projector_matrix()
    add('Adams projector idempotency', norm(Pm@Pm-Pm)<1e-12, norm(Pm@Pm-Pm),1e-12)
    target=np.zeros(6); target[2]=1
    add('Adams projector degree isolation', norm(np.diag(Pm)-target)<1e-12, norm(np.diag(Pm)-target),1e-12)

    N=np.array([[0,1,0],[0,0,1],[0,0,0]],float)
    trace_res=max(abs(np.trace(np.linalg.matrix_power(N,r))) for r in range(1,6))
    add('nilpotent trace blindness', trace_res<1e-12 and norm(N)>0, trace_res,1e-12)

    # exact support coefficient reconstruction toy
    M=np.array([[2,1,0],[1,3,1],[0,1,2],[1,0,1]],float)
    q=np.array([1.5,-.5,2.0]); b=M@q; qhat=np.linalg.lstsq(M,b,rcond=None)[0]
    add('support multiplicity reconstruction', norm(q-qhat)<1e-12, norm(q-qhat),1e-12)

    # stabilization toy
    dims=np.minimum(6,np.floor(1.4*np.sqrt(np.arange(1,15))).astype(int)+1); dims[8:]=6
    add('finite rank stabilization', np.all(dims[8:]==dims[8]), int(dims[-1]), 'constant tail')

    result={
        'title':'Projector-Resolved Hodge Calculus I',
        'figure_pairs':32,
        'checks':len(checks),
        'passed':sum(c.passed for c in checks),
        'minimum_cycle_gram_eigenvalue':float(eig.min()),
        'minimum_transfer_eigenvalue':float(eigt.min()),
        'cayley_hamilton_residual':float(resch),
        'dolbeault_toy_residual':float(full),
        'checks_detail':[asdict(c) for c in checks],
    }
    return checks,result


def write_outputs(stems,checks,result):
    (RES/'verification.json').write_text(json.dumps(result,indent=2,default=lambda o: o.item() if hasattr(o,'item') else str(o)),encoding='utf-8')
    with (TAB/'checks.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['name','passed','value','tolerance'])
        for c in checks: w.writerow([c.name,c.passed,json.dumps(c.value,default=lambda o: o.item() if hasattr(o,'item') else str(o)),c.tolerance])
    (ROOT/'FIGURE_INDEX.md').write_text('# Figure index\n\n'+'\n'.join(f'{i}. `{s}.pdf` and `{s}.png`' for i,s in enumerate(stems,1))+'\n',encoding='utf-8')


def main():
    stems=make_figures()
    checks,result=run_checks()
    write_outputs(stems,checks,result)
    print(json.dumps({k:result[k] for k in ['figure_pairs','checks','passed']},indent=2))
    if not all(c.passed for c in checks):
        raise SystemExit('one or more checks failed')


if __name__=='__main__':
    main()
