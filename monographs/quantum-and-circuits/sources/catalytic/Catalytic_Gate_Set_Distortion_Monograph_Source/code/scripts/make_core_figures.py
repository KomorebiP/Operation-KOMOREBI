from __future__ import annotations

import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

C = np.array([
    [1,0,0,0,0,0],
    [1,1,0,0,0,0],
    [0,0,1,0,0,0],
    [0,1,1,1,0,0],
    [1,1,1,0,1,0],
    [1,1,1,0,0,1],
], dtype=int)

# 1. Canonical target matrix.
fig, ax = plt.subplots(figsize=(4.5, 4.2))
ax.imshow(C, cmap='Greys', vmin=0, vmax=1)
ax.set_xticks(range(6), [rf'$e_{j}$' for j in range(6)])
ax.set_yticks(range(6), [rf'$R_{i}$' for i in range(6)])
ax.set_xlabel('input coordinate')
ax.set_ylabel('output row')
ax.set_title('Canonical six-row target $C$')
for i in range(6):
    for j in range(6):
        ax.text(j, i, str(C[i,j]), ha='center', va='center',
                color='white' if C[i,j] else 'black', fontsize=10)
ax.set_xticks(np.arange(-.5, 6, 1), minor=True)
ax.set_yticks(np.arange(-.5, 6, 1), minor=True)
ax.grid(which='minor', linewidth=0.7)
ax.tick_params(which='minor', bottom=False, left=False)
fig.tight_layout()
fig.savefig(OUT / 'canonical_matrix.pdf', bbox_inches='tight')
plt.close(fig)

# 2. Carrier-state timeline.
fig, ax = plt.subplots(figsize=(8.6, 3.15))
ax.set_xlim(-0.45, 6.45)
ax.set_ylim(-1.55, 1.45)
ax.axis('off')
xs = np.arange(7)
states = [
    r'$e_1$',
    r'$e_1+e_2$',
    r'$e_1+e_2$',
    r'$e_0+e_1+e_2$',
    r'$e_0+e_1+e_2$',
    r'$e_0+e_1+e_2$',
    r'$e_0+e_1$',
]
gates = [
    r'$R_1\leftarrow R_1+R_2$',
    r'$R_3\leftarrow R_3+R_1$',
    r'$R_1\leftarrow R_1+R_0$',
    r'$R_4\leftarrow R_4+R_1$',
    r'$R_5\leftarrow R_5+R_1$',
    r'$R_1\leftarrow R_1-R_2$',
]
for k in range(6):
    ax.annotate('', xy=(xs[k+1]-0.08, 0), xytext=(xs[k]+0.08, 0),
                arrowprops=dict(arrowstyle='->', linewidth=1.2))
    ax.text((xs[k]+xs[k+1])/2, -0.64, gates[k], ha='center', va='center', fontsize=8.5)
for x, label in zip(xs, states):
    ax.scatter([x], [0], s=75, facecolor='white', edgecolor='black', zorder=3)
    ax.text(x, 0.36, label, ha='center', va='bottom', fontsize=10)
for x, label in [(2, r'copy to $R_3$'), (4, r'copy to $R_4$'), (5, r'copy to $R_5$')]:
    ax.annotate('', xy=(x, -0.12), xytext=(x, -1.02), arrowprops=dict(arrowstyle='->', linewidth=0.9))
    ax.text(x, -1.18, label, ha='center', va='top', fontsize=8.5)
ax.text(-0.35, 1.20, 'workspace row $R_1$', ha='left', va='center', fontsize=10, fontweight='bold')
ax.text(6.35, 1.20, 'upper dependency removed', ha='right', va='center', fontsize=9)
fig.tight_layout()
fig.savefig(OUT / 'carrier_timeline.pdf', bbox_inches='tight')
plt.close(fig)

# 3. Generic one-catalyst motif.
fig, ax = plt.subplots(figsize=(7.4, 4.3))
ax.set_xlim(-3.8, 3.8)
ax.set_ylim(-2.25, 2.25)
ax.axis('off')
pos = {
    'p': (0, 0.55),
    'q': (0, -0.55),
    'x': (-2.7, 1.25),
    'u': (-2.7, -0.25),
    'y0': (2.7, 1.35),
    'y1': (2.7, 0.15),
    'y2': (2.7, -1.05),
}
for name, (x,y) in pos.items():
    ax.scatter([x],[y], s=550 if name in ('p','q') else 300, facecolor='white', edgecolor='black', zorder=4)
labels = {'p':r'$p$','q':r'$q$','x':r'$x$','u':r'$u$',
          'y0':r'$y_0$','y1':r'$y_1$','y2':r'$y_2$'}
for name,(x,y) in pos.items():
    ax.text(x,y,labels[name],ha='center',va='center',fontsize=10)

def arrow(a,b,text,rad=0.0,yoff=0.0,style='->'):
    xa,ya=pos[a]; xb,yb=pos[b]
    ax.annotate('',xy=(xb,yb),xytext=(xa,ya),
                arrowprops=dict(arrowstyle=style,connectionstyle=f'arc3,rad={rad}',linewidth=1.15))
    ax.text((xa+xb)/2,(ya+yb)/2+yoff,text,ha='center',va='center',fontsize=8.5,
            bbox=dict(facecolor='white',edgecolor='none',pad=0.8))

arrow('q','p','open / close',rad=0.22,style='<->')
arrow('u','q','cross')
arrow('x','p','phase')
arrow('p','y0','cross: before',rad=-0.05,yoff=0.16)
arrow('p','y1','cross: after',yoff=0.12)
arrow('p','y2','cross: after',rad=0.05,yoff=-0.10)
ax.text(0,1.92,'Minimal three-cross, one-phase catalytic motif',ha='center',va='center',fontsize=11,fontweight='bold')
ax.text(0,-1.90,r'$2$ catalyst rows $+$ $3$ cross consumers $+$ $1$ phase switch $=6$ roles',
        ha='center',va='center',fontsize=10)
fig.tight_layout()
fig.savefig(OUT / 'catalytic_motif.pdf', bbox_inches='tight')
plt.close(fig)

# 4. Pasch configuration.
lines = {
    'L1':(-2.5,-1.3357082778655922),
    'L2':(2.25,1.4783448989260966),
    'L3':(0.5,-1.9115490539262265),
    'L4':(-0.75,1.904300151473076),
}
pairs = {1:('L1','L2'),2:('L1','L3'),3:('L1','L4'),6:('L2','L3'),7:('L2','L4'),4:('L3','L4')}
def intersect(a,b):
    m1,b1=lines[a]; m2,b2=lines[b]
    x=(b2-b1)/(m1-m2)
    return x,m1*x+b1
pts={k:intersect(*v) for k,v in pairs.items()}
fig, ax = plt.subplots(figsize=(5.7,5.0))
ax.set_xlim(-3.45,3.45); ax.set_ylim(-3.35,3.75); ax.axis('off')
xx=np.linspace(-4,4,120)
styles=['-','--','-.',':']
for (m,b),style in zip(lines.values(),styles):
    ax.plot(xx,m*xx+b,linewidth=1.25,linestyle=style)
for k,(x,y) in pts.items():
    ax.scatter([x],[y],s=76,facecolor='white',edgecolor='black',zorder=3)
    ax.text(x+0.10,y+0.13,rf'${k}$',fontsize=10)
ax.set_title('The six carrier states form a Pasch configuration',pad=8)
ax.text(0,-3.17,r'four projective lines in $\mathrm{PG}(2,2)$; the seventh Fano point is absent',ha='center',fontsize=9)
fig.tight_layout()
fig.savefig(OUT / 'pasch_configuration.pdf', bbox_inches='tight')
plt.close(fig)

# 5. Exact distance census heat map.
pairs_counts={(0,0):1,(1,1):15,(2,2):125,(3,3):720,(4,4):2914,(5,5):7851,
              (6,6):12656,(7,6):20,(7,7):7926,(8,8):540}
M=np.full((9,9),np.nan)
for (low,amb),cnt in pairs_counts.items():
    M[low,amb]=math.log10(cnt+1)
fig, ax=plt.subplots(figsize=(5.5,4.9))
im=ax.imshow(M,origin='lower',cmap='Greys',vmin=0,vmax=math.log10(12657))
ax.set_xticks(range(9)); ax.set_yticks(range(9))
ax.set_xlabel(r'ambient distance $\ell_*$')
ax.set_ylabel(r'restricted distance $\ell_\downarrow$')
ax.set_title(r'Exact census in $U_6(\mathbf{F}_2)$')
for (low,amb),cnt in pairs_counts.items():
    ax.text(amb,low,f'{cnt:,}',ha='center',va='center',fontsize=8,
            color='white' if math.log10(cnt+1)>2.5 else 'black')
ax.set_xticks(np.arange(-.5,9,1),minor=True); ax.set_yticks(np.arange(-.5,9,1),minor=True)
ax.grid(which='minor',linewidth=0.55)
ax.tick_params(which='minor',bottom=False,left=False)
fig.colorbar(im,ax=ax,label=r'$\log_{10}(1+\mathrm{count})$',fraction=0.046,pad=0.04)
fig.tight_layout()
fig.savefig(OUT / 'distance_census.pdf', bbox_inches='tight')
plt.close(fig)

# 6. Green coefficients.
low=np.array([0,0,0,0,0,0,0,543,25080,510703,10824940])
amb=np.array([0,0,0,0,0,0,2,776,39454])
fig, ax=plt.subplots(figsize=(6.8,4.0))
kl=np.arange(len(low)); ka=np.arange(len(amb)); pl=low>0; pa=amb>0
ax.plot(kl[pl],low[pl],marker='o',linestyle='-',label=r'restricted $S_\downarrow$')
ax.plot(ka[pa],amb[pa],marker='s',linestyle='--',label=r'ambient $S_*$')
ax.set_yscale('log')
ax.set_xticks(range(0,11))
ax.set_xlabel('word length $k$')
ax.set_ylabel(r'number of words ending at $C$')
ax.set_title('Endpoint Green coefficients and first arrival')
ax.axvline(6,linewidth=0.8,linestyle=':')
ax.axvline(7,linewidth=0.8,linestyle=':')
ax.text(6.05,2.5,'ambient first arrival',rotation=90,va='bottom',fontsize=8.5)
ax.text(7.05,2.5,'restricted first arrival',rotation=90,va='bottom',fontsize=8.5)
ax.legend(frameon=False)
ax.grid(axis='y',which='both',linewidth=0.4,alpha=0.5)
fig.tight_layout()
fig.savefig(OUT / 'green_coefficients.pdf', bbox_inches='tight')
plt.close(fig)

# 7. Motif count.
fig, ax=plt.subplots(figsize=(5.7,3.6))
splits=['$(1,3)$','$(2,2)$','$(3,1)$']; vals=[6,8,6]
bars=ax.bar(splits,vals,edgecolor='black',facecolor='0.8')
for b,v in zip(bars,vals):
    ax.text(b.get_x()+b.get_width()/2,v+0.15,str(v),ha='center',va='bottom')
ax.set_ylim(0,9.5)
ax.set_xlabel('auxiliary rows left/right of the catalyst pair')
ax.set_ylabel('minimal defective targets')
ax.set_title('Analytic count of the 20 minimal motifs')
ax.grid(axis='y',linewidth=0.4,alpha=0.5)
fig.tight_layout()
fig.savefig(OUT / 'motif_count.pdf', bbox_inches='tight')
plt.close(fig)

# 8. Defect amplification by direct sum.
ks=np.arange(1,9)
fig, ax=plt.subplots(figsize=(5.8,3.7))
ax.plot(6*ks,7*ks,marker='o',label=r'restricted $=7k$')
ax.plot(6*ks,6*ks,marker='s',linestyle='--',label=r'ambient upper bound $=6k$')
ax.fill_between(6*ks,6*ks,7*ks,alpha=0.16)
ax.set_xlabel('dimension $n=6k$')
ax.set_ylabel('gate count')
ax.set_title('Direct-sum amplification of the catalytic defect')
ax.legend(frameon=False)
ax.grid(linewidth=0.4,alpha=0.5)
fig.tight_layout()
fig.savefig(OUT / 'direct_sum_amplification.pdf', bbox_inches='tight')
plt.close(fig)

# 9. Connected snapshot family.
fig, ax = plt.subplots(figsize=(8.2, 4.8))
ax.set_xlim(-4.5, 4.8)
ax.set_ylim(-2.8, 2.8)
ax.axis('off')
# Carrier rows.
ax.scatter([0, 0], [0.65, -0.65], s=[620, 620], facecolor='white', edgecolor='black', zorder=4)
ax.text(0, 0.65, r'$p$', ha='center', va='center', fontsize=11, zorder=6)
ax.text(0, -0.65, r'$q$', ha='center', va='center', fontsize=11, zorder=6)
ax.annotate('', xy=(0, 0.38), xytext=(0, -0.38),
            arrowprops=dict(arrowstyle='<->', connectionstyle='arc3,rad=0.25', linewidth=1.25))
ax.text(0.5, 0, 'open / close', ha='left', va='center', fontsize=9)
# Update rows.
xpos = [-3.8, -3.0, -2.2, -1.4]
for i, (x, y) in enumerate(zip(xpos, [1.75, 0.95, 0.15, -0.65]), start=1):
    ax.scatter([x], [y], s=250, facecolor='white', edgecolor='black', zorder=4)
    ax.text(x, y, rf'$x_{i}$', ha='center', va='center', fontsize=9.5, zorder=6)
    ax.annotate('', xy=(-0.28, 0.65), xytext=(x + 0.18, y),
                arrowprops=dict(arrowstyle='->', linewidth=1.0))
# Snapshot outputs.
youts = [2.05, 1.2, 0.35, -0.5, -1.35, -2.2]
for j, y in enumerate(youts):
    ax.scatter([3.7], [y], s=250, facecolor='white', edgecolor='black', zorder=4)
    ax.text(3.7, y, rf'$t_{j}$', ha='center', va='center', fontsize=9.5, zorder=6)
    ax.annotate('', xy=(3.45, y), xytext=(0.28, 0.65),
                arrowprops=dict(arrowstyle='->', linewidth=0.95,
                                connectionstyle=f'arc3,rad={0.09*(j-2.5)}'))
ax.text(-2.75, 2.48, r'$u$ lower updates of the carrier', ha='center', va='center', fontsize=10, fontweight='bold')
ax.text(3.0, 2.48, r'$v$ exported prefix snapshots', ha='center', va='center', fontsize=10, fontweight='bold')
ax.text(0, -2.58,
        r'ambient cost $u+v+2$; exact lower cost $u+2v$; certified defect $v-2$',
        ha='center', va='center', fontsize=10)
ax.set_title('Connected higher-dimensional snapshot family', pad=8)
fig.tight_layout()
fig.savefig(OUT / 'snapshot_family.pdf', bbox_inches='tight')
plt.close(fig)

# 10. Higher-dimensional connected cases.
ns = np.arange(6, 32)
restricted = np.zeros_like(ns, dtype=float)
ambient = np.zeros_like(ns, dtype=float)
restricted[0], ambient[0] = 7, 6
for idx, n in enumerate(ns[1:], start=1):
    v = (n - 1) // 2
    u = n - v - 2
    restricted[idx] = u + 2 * v
    ambient[idx] = n
fig, ax = plt.subplots(figsize=(6.6, 4.1))
ax.plot(ns, restricted, marker='o', markersize=3.5, label=r'exact restricted length')
ax.plot(ns, ambient, marker='s', markersize=3.2, linestyle='--', label=r'ambient construction')
ax.fill_between(ns, ambient, restricted, alpha=0.15)
ax.set_xlabel('dimension $n$')
ax.set_ylabel('gate count')
ax.set_title(r'Connected defects in every dimension $n\geq 6$')
ax.legend(frameon=False)
ax.grid(linewidth=0.4, alpha=0.5)
fig.tight_layout()
fig.savefig(OUT / 'connected_higher_cases.pdf', bbox_inches='tight')
plt.close(fig)

# 11. Recursive zeta-shaped lift.
fig, ax = plt.subplots(figsize=(8.0, 4.3))
ax.set_xlim(-0.4, 10.4)
ax.set_ylim(-0.5, 4.5)
ax.axis('off')
levels = [0, 1, 2]
xs = [0.8, 4.0, 7.8]
sizes = [1.15, 1.75, 2.5]
for level, x, size in zip(levels, xs, sizes):
    y = 1.05
    if level == 0:
        rect = mpl.patches.Rectangle((x, y), size, size, fill=False, linewidth=1.3)
        ax.add_patch(rect)
        ax.text(x + size/2, y + size/2, r'$A$', ha='center', va='center', fontsize=13)
    else:
        half = size/2
        for row in range(2):
            for col in range(2):
                rect = mpl.patches.Rectangle((x + col*half, y + (1-row)*half), half, half,
                                             fill=False, linewidth=1.15)
                ax.add_patch(rect)
        ax.text(x + half/2, y + 3*half/2, rf'$\mathcal{{Z}}^{{{level-1}}}(A)$' if level>1 else r'$A$', ha='center', va='center', fontsize=10)
        ax.text(x + 3*half/2, y + 3*half/2, r'$0$', ha='center', va='center', fontsize=11)
        ax.text(x + half/2, y + half/2, rf'$\mathcal{{Z}}^{{{level-1}}}(A)$' if level>1 else r'$A$', ha='center', va='center', fontsize=10)
        ax.text(x + 3*half/2, y + half/2, rf'$\mathcal{{Z}}^{{{level-1}}}(A)$' if level>1 else r'$A$', ha='center', va='center', fontsize=10)
    ax.text(x + size/2, 0.48, rf'level ${level}$', ha='center', va='center', fontsize=9.5)
for x0, x1 in [(2.1, 3.65), (5.85, 7.4)]:
    ax.annotate('', xy=(x1, 2.1), xytext=(x0, 2.1), arrowprops=dict(arrowstyle='->', linewidth=1.2))
ax.text(5.0, 4.08, r'Recursive lift $\mathcal{Z}(A)$ with block pattern $A,0;A,A$', ha='center', va='center', fontsize=13)
ax.text(5.0, -0.05,
        r'$\Delta(\mathcal{Z}^r(A))\geq 2^r\Delta(A)$; exact lower recurrence $a_{r+1}=2a_r+m2^r$',
        ha='center', va='center', fontsize=9.5)
fig.tight_layout()
fig.savefig(OUT / 'recursive_zeta_lift.pdf', bbox_inches='tight')
plt.close(fig)

# 12. Tensor amplification from the 21-dimensional seed.
rs = np.arange(1, 6)
N = 21 ** rs
low = rs * (21 ** (rs - 1)) * 29
amb = rs * N
gap = low - amb
fig, ax = plt.subplots(figsize=(6.7, 4.2))
ax.plot(N, low, marker='o', label=r'exact restricted length')
ax.plot(N, amb, marker='s', linestyle='--', label=r'ambient construction')
ax.plot(N, gap, marker='^', linestyle=':', label=r'certified defect')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(r'dimension $N=21^r$')
ax.set_ylabel('gate count')
ax.set_title(r'Tensor amplification: $\Theta(N\log N)$ defect')
ax.legend(frameon=False)
ax.grid(which='both', linewidth=0.4, alpha=0.5)
fig.tight_layout()
fig.savefig(OUT / 'tensor_amplification.pdf', bbox_inches='tight')
plt.close(fig)


# 13. Regular matroid M(K4) underlying the six carrier states.
fig, ax = plt.subplots(figsize=(6.4, 5.2))
ax.set_xlim(-2.3, 2.3)
ax.set_ylim(-2.15, 2.25)
ax.axis('off')
pos4 = {
    1: (0.0, 1.65),
    2: (-1.65, 0.25),
    3: (1.65, 0.25),
    4: (0.0, -1.55),
}
edge_labels = {
    (1, 2): r'$p\;(12)$',
    (1, 3): r'$x\;(13)$',
    (2, 3): r'$x+p\;(23)$',
    (1, 4): r'$p+q\;(14)$',
    (2, 4): r'$q\;(24)$',
    (3, 4): r'$x+p+q\;(34)$',
}
label_offsets = {
    (1, 2): (-0.18, 0.13),
    (1, 3): (0.18, 0.13),
    (2, 3): (0.0, 0.16),
    (1, 4): (0.22, 0.0),
    (2, 4): (-0.18, -0.02),
    (3, 4): (0.22, -0.02),
}
for (a, b), label in edge_labels.items():
    xa, ya = pos4[a]
    xb, yb = pos4[b]
    ax.plot([xa, xb], [ya, yb], linewidth=1.25)
    dx, dy = label_offsets[(a, b)]
    ax.text((xa + xb) / 2 + dx, (ya + yb) / 2 + dy, label,
            ha='center', va='center', fontsize=9,
            bbox=dict(facecolor='white', edgecolor='none', pad=0.8))
for vtx, (xv, yv) in pos4.items():
    ax.scatter([xv], [yv], s=360, facecolor='white', edgecolor='black', zorder=4)
    ax.text(xv, yv, rf'${vtx}$', ha='center', va='center', fontsize=10.5, zorder=5)
ax.text(0, 2.05, r'The carrier dependence matroid is $M(K_4)$',
        ha='center', va='center', fontsize=11, fontweight='bold')
ax.text(0, -1.98,
        r'four triangular cycles $\longleftrightarrow$ four three-element dependencies',
        ha='center', va='center', fontsize=9.5)
fig.tight_layout()
fig.savefig(OUT / 'regular_matroid_k4.pdf', bbox_inches='tight')
plt.close(fig)

# 14. Fixed upper-gate penalties versus growing dimension.
ns = np.arange(7, 42)
v = np.floor((ns - 1) / 2)
fig, ax = plt.subplots(figsize=(6.6, 4.1))
ax.plot(ns, v - 2, linestyle='-', marker='o', markersize=3.3,
        label=r'two-gate budget / $\lambda=1$')
ax.plot(ns, v - 6, linestyle='--', marker='s', markersize=3.0,
        label=r'weighted lower bound, $\lambda=3$')
ax.plot(ns, v - 10, linestyle='-.', marker='^', markersize=3.0,
        label=r'weighted lower bound, $\lambda=5$')
ax.axhline(0, linewidth=0.8, linestyle=':')
ax.set_xlabel('dimension $n$')
ax.set_ylabel('certified restricted-minus-weighted advantage')
ax.set_title('Every fixed upper-gate penalty is eventually amortized')
ax.legend(frameon=False)
ax.grid(linewidth=0.4, alpha=0.5)
fig.tight_layout()
fig.savefig(OUT / 'weighted_catalysis.pdf', bbox_inches='tight')
plt.close(fig)

# 15. Microscopic rank-one, bandwidth-one escape.
fig, ax = plt.subplots(figsize=(7.8, 4.3))
ax.set_xlim(-0.4, 10.4)
ax.set_ylim(-0.4, 5.0)
ax.axis('off')

# Three schematic matrix states.
origins = [(0.4, 1.0), (4.0, 1.0), (7.6, 1.0)]
titles = ['lower start', 'catalytic interval', 'lower finish']
for idx, ((ox, oy), title) in enumerate(zip(origins, titles)):
    ngrid = 5
    cell = 0.5
    for i in range(ngrid):
        for j in range(ngrid):
            x = ox + j * cell
            y = oy + (ngrid - 1 - i) * cell
            fill = '0.88' if j <= i else 'white'
            rect = mpl.patches.Rectangle((x, y), cell, cell, facecolor=fill,
                                         edgecolor='0.55', linewidth=0.55)
            ax.add_patch(rect)
    # diagonal
    for i in range(ngrid):
        x = ox + i * cell + cell / 2
        y = oy + (ngrid - 1 - i) * cell + cell / 2
        ax.text(x, y, '1', ha='center', va='center', fontsize=7.5)
    if idx == 1:
        # adjacent strict upper entry p,q
        i, j = 2, 3
        x = ox + j * cell
        y = oy + (ngrid - 1 - i) * cell
        rect = mpl.patches.Rectangle((x, y), cell, cell, facecolor='0.35',
                                     edgecolor='black', linewidth=1.0)
        ax.add_patch(rect)
        ax.text(x + cell / 2, y + cell / 2, r'$*$', color='white',
                ha='center', va='center', fontsize=10)
        ax.annotate('only upper entry', xy=(x + cell / 2, y + cell / 2),
                    xytext=(ox + 1.25, 4.25), ha='center', fontsize=8.5,
                    arrowprops=dict(arrowstyle='->', linewidth=0.9))
    ax.text(ox + 1.25, 0.55, title, ha='center', va='center', fontsize=9.5,
            fontweight='bold')

# arrows between states
for x0, x1 in [(2.95, 3.85), (6.55, 7.45)]:
    ax.annotate('', xy=(x1, 2.25), xytext=(x0, 2.25),
                arrowprops=dict(arrowstyle='->', linewidth=1.2))
ax.text(3.4, 2.58, 'open', ha='center', fontsize=8.5)
ax.text(7.0, 2.58, 'close', ha='center', fontsize=8.5)
ax.text(5.25, 0.16,
        r'throughout the interval: $\operatorname{rank}(X^+)=1$ and $b^+(X)=1$',
        ha='center', va='center', fontsize=10)
ax.set_title('Microscopic flag escape with macroscopic reuse', pad=6)
fig.tight_layout()
fig.savefig(OUT / 'microscopic_escape.pdf', bbox_inches='tight')
plt.close(fig)

# 16. Algebraic defect strata.
fig, ax = plt.subplots(figsize=(7.4, 4.9))
ax.set_xlim(-0.4, 10.4)
ax.set_ylim(-0.3, 6.6)
ax.axis('off')

outer = mpl.patches.FancyBboxPatch((0.3, 0.35), 9.7, 5.65,
                                   boxstyle='round,pad=0.18,rounding_size=0.18',
                                   facecolor='0.96', edgecolor='black', linewidth=1.2)
ax.add_patch(outer)
ax.text(0.65, 5.62, r'$U_n$  (dimension $N=\binom{n}{2}$)', fontsize=11,
        fontweight='bold', ha='left')

ell1 = mpl.patches.Ellipse((5.2, 3.05), 7.5, 4.15,
                           facecolor='0.86', edgecolor='0.3', linewidth=1.0)
ell2 = mpl.patches.Ellipse((5.2, 3.05), 5.35, 2.82,
                           facecolor='0.72', edgecolor='0.25', linewidth=1.0)
ell3 = mpl.patches.Ellipse((5.2, 3.05), 2.45, 1.18,
                           facecolor='0.48', edgecolor='black', linewidth=1.0)
for patch in (ell1, ell2, ell3):
    ax.add_patch(patch)
ax.text(5.2, 4.72, r'$\overline{\mathcal{R}^*_{n,\leq N-1}}$',
        ha='center', fontsize=10)
ax.text(5.2, 3.88, r'$\overline{\mathcal{R}^*_{n,\leq N-d}}$',
        ha='center', fontsize=10)
ax.text(5.2, 3.05, r'$\overline{\mathcal{D}_{n,\geq d}}$',
        ha='center', va='center', fontsize=10, color='white', fontweight='bold')
ax.annotate(r'$\operatorname{codim}\geq d$', xy=(6.35, 3.05), xytext=(8.65, 2.0),
            ha='center', fontsize=10,
            arrowprops=dict(arrowstyle='->', linewidth=1.0))
ax.text(5.2, 0.75,
        'generic targets lie outside every ambient locus of length below $N$',
        ha='center', fontsize=9.5)
ax.set_title('Algebraic rarity of catalytic defect', pad=7)
fig.tight_layout()
fig.savefig(OUT / 'defect_strata.pdf', bbox_inches='tight')
plt.close(fig)

print(f'Wrote {len(list(OUT.glob("*.pdf")))} figures to {OUT}')
