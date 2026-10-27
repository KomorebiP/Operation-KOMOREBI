from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon

OUT = Path('/mnt/data/PSC_Paper_XI_Strengthened_Annals_Edition_Work/figures')
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.size'] = 9
plt.rcParams['axes.unicode_minus'] = False


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches='tight', format='pdf')
    plt.close(fig)


def box(ax, xy, w, h, text, fontsize=8):
    p = FancyBboxPatch(xy, w, h, boxstyle='round,pad=0.02', linewidth=1, fill=False)
    ax.add_patch(p)
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha='center', va='center', fontsize=fontsize)
    return p


def arrow(ax, a, b, style='-|>', lw=1):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=10, linewidth=lw))

# 1 architecture
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis('off')
labels = [
    ('Weil Deligne\nblocks', .3, 2.6), ('Tame Frobenius\npackets', 2.3, 2.6),
    ('Wild Heisenberg\nenvelopes', 4.3, 2.6), ('Type side\npackets', 6.3, 2.6),
    ('Local factors and\nreconstruction', 8.3, 2.6)
]
for t,x,y in labels: box(ax,(x,y),1.45,.72,t)
for x in [1.75,3.75,5.75,7.75]: arrow(ax,(x,2.96),(x+.5,2.96))
box(ax,(3.4,.75),3.2,.8,'Restricted bridge proved under a declared\nequivariant symplectic identification',8)
arrow(ax,(5.05,1.55),(5.05,2.58))
ax.text(5,.25,'The full choice free wild bridge and the complete pair factor comparison remain open.',ha='center',fontsize=8)
save(fig,'01_architecture.pdf')

# 2 WD chain
fig, ax = plt.subplots(figsize=(8,2.8)); ax.axis('off'); ax.set_xlim(0,9); ax.set_ylim(0,3)
n=6
for j in range(n):
    box(ax,(.5+1.35*j,1.15),.9,.55,rf'$\tau|\cdot|^{{{j}}}$',9)
    if j<n-1: arrow(ax,(1.4+1.35*j,1.43),(1.82+1.35*j,1.43))
ax.text(4.45,2.25,r'$N$ is the one step transfer and $N^m=0$',ha='center')
ax.text(4.45,.55,r'$\operatorname{Sp}_m(\tau)$ is reconstructed from one atom and a finite nilpotent chain',ha='center')
save(fig,'02_weil_deligne_chain.pdf')

# 3 tame orbit
fig, ax = plt.subplots(figsize=(6,5)); ax.axis('off'); ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.4,1.4)
n=7
pts=[]
for j in range(n):
    th=2*np.pi*j/n; pts.append((math.cos(th),math.sin(th)))
for j,(x,y) in enumerate(pts):
    ax.add_patch(Circle((x,y),.13,fill=False)); ax.text(x,y,rf'$\chi^{{q^{j}}}$',ha='center',va='center',fontsize=8)
    x2,y2=pts[(j+1)%n]; arrow(ax,(.86*x+.14*x2,.86*y+.14*y2),(.2*x+.8*x2,.2*y+.8*y2))
ax.text(0,0,r'Frobenius',ha='center',va='center')
ax.text(0,-1.3,'One transitive orbit gives one tame irreducible atom.',ha='center')
save(fig,'03_tame_frobenius_orbit.pdf')

# 4 regular orbit counts
fig, ax = plt.subplots(figsize=(7,3.7))
ns=np.arange(1,9)
for q in [2,3,5]:
    vals=[]
    for n in ns:
        total=0
        for d in range(1,n+1):
            if n%d==0:
                # mobius small
                x=d; mu=1; p=2
                yy=x
                prime=2
                mu=1
                f=2
                z=yy
                pp=2
                square=False
                count=0
                r=z
                a=2
                while a*a<=r:
                    if r%a==0:
                        e=0
                        while r%a==0: r//=a; e+=1
                        if e>1: square=True
                        count+=1
                    a+=1
                if r>1: count+=1
                if square: m=0
                else: m=(-1)**count
                total += m*(q**(n//d)-1)
        vals.append(total/n)
    ax.plot(ns,vals,marker='o',label=rf'$q={q}$')
ax.set_yscale('log'); ax.set_xlabel(r'orbit length $n$'); ax.set_ylabel('regular Frobenius orbits')
ax.legend(frameon=False); ax.grid(True,linewidth=.3)
save(fig,'04_regular_orbit_counts.pdf')

# 5 finite cuspidal projector
fig, ax = plt.subplots(figsize=(8,3.2)); ax.axis('off'); ax.set_xlim(0,9); ax.set_ylim(0,3.4)
box(ax,(.4,1.3),1.5,.7,'regular torus\ncharacter')
box(ax,(3,1.3),1.7,.7,'cuspidal\nrepresentation')
box(ax,(5.8,1.3),1.7,.7,'primitive central\nidempotent')
box(ax,(7.85,1.3),.8,.7,'block')
for a,b in [((1.9,1.65),(3,1.65)),((4.7,1.65),(5.8,1.65)),((7.5,1.65),(7.85,1.65))]: arrow(ax,a,b)
ax.text(4.5,.55,'Parabolic unipotent averages vanish on the cuspidal block.',ha='center')
save(fig,'05_cuspidal_projector.pdf')

# 6 gcd lcm tensor
fig, ax = plt.subplots(figsize=(7.5,4.2)); ax.set_xlim(0,12); ax.set_ylim(0,8); ax.set_aspect('equal'); ax.axis('off')
n,m=4,6
g=math.gcd(n,m); L=math.lcm(n,m)
for i in range(n):
    for j in range(m):
        ax.add_patch(plt.Rectangle((j,i),1,1,fill=False,linewidth=.5))
        ax.text(j+.5,i+.5,str((j-i)%g),ha='center',va='center',fontsize=7)
ax.text(3,5.1,rf'$n={n}$ and $m={m}$',ha='center')
ax.text(3,-.7,rf'${g}$ interaction packets, each of length ${L}$',ha='center')
box(ax,(7.3,3.1),3.8,1.1,r'$\gcd(n,m)$ orbit classes'+'\n'+r'$\operatorname{lcm}(n,m)$ steps per class',9)
arrow(ax,(6.2,2.2),(7.3,3.55))
save(fig,'06_gcd_lcm_refinement.pdf')

# 7 gauss phases
fig, ax = plt.subplots(figsize=(5,5)); ax.set_aspect('equal')
theta=np.linspace(0,2*np.pi,400); ax.plot(np.cos(theta),np.sin(theta),linewidth=.7)
angles=[0,np.pi/4,np.pi/2,3*np.pi/4,np.pi,5*np.pi/4,3*np.pi/2,7*np.pi/4]
for k,a in enumerate(angles):
    ax.plot([0,np.cos(a)],[0,np.sin(a)],linewidth=.8)
    ax.text(1.12*np.cos(a),1.12*np.sin(a),rf'$\zeta_8^{k}$',ha='center',va='center',fontsize=8)
ax.set_xlim(-1.35,1.35); ax.set_ylim(-1.35,1.35); ax.axis('off')
ax.text(0,-1.28,'Normalized finite Gauss sums contribute unit phases.',ha='center')
save(fig,'07_gauss_phase_circle.pdf')

# 8 Heisenberg geometry
fig, ax = plt.subplots(figsize=(8,4)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,5)
box(ax,(.4,2.0),1.8,.8,r'$V=X\oplus X^*$'+'\nfinite symplectic space')
box(ax,(3.1,2.0),1.8,.8,r'$H(V)=V\times Z$'+'\nHeisenberg group')
box(ax,(5.8,2.0),1.8,.8,'Schrodinger\nrepresentation')
box(ax,(8.1,2.0),1.4,.8,r'$\dim=p^r$')
for a,b in [((2.2,2.4),(3.1,2.4)),((4.9,2.4),(5.8,2.4)),((7.6,2.4),(8.1,2.4))]: arrow(ax,a,b)
box(ax,(3.2,.45),4.0,.72,'maximal isotropic averaging selects one primitive line',8)
arrow(ax,(5.2,1.17),(6.3,1.98))
save(fig,'08_heisenberg_geometry.pdf')

# 9 commutator envelope
fig, ax = plt.subplots(figsize=(8,4.5)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,5)
box(ax,(.45,3),2.1,.7,'projective intertwiners\n$T_aT_b=c(a,b)T_{a+b}$')
box(ax,(3.35,3),2.1,.7,'commutator form\n$b(a,b)=c(a,b)c(b,a)^{-1}$')
box(ax,(6.25,3),1.5,.7,r'radical'+'\n'+r'$\operatorname{rad}b$')
box(ax,(8.35,3),1.25,.7,'symplectic\nquotient')
for a,b in [((2.55,3.35),(3.35,3.35)),((5.45,3.35),(6.25,3.35)),((7.75,3.35),(8.35,3.35))]: arrow(ax,a,b)
box(ax,(3.1,1.0),3.8,.9,r'nondegenerate case: $\mathrm{C}^c[A]\cong M_{\sqrt{|A|}}(\mathrm{C})$',8)
arrow(ax,(8.95,2.98),(6.9,1.9))
save(fig,'09_commutator_envelope.pdf')

# 10 one break envelope
fig, ax = plt.subplots(figsize=(9,4)); ax.axis('off'); ax.set_xlim(0,11); ax.set_ylim(0,4.5)
box(ax,(.3,2.4),1.7,.75,'normal wild\nsubgroup $N$')
box(ax,(2.6,2.4),1.7,.75,r'stable constituent'+'\n'+r'$\rho$')
box(ax,(4.9,2.4),1.7,.75,r'multiplicity space'+'\n'+r'$M_\rho$')
box(ax,(7.2,2.4),1.7,.75,'projective quotient\naction')
box(ax,(9.45,2.4),1.25,.75,'symplectic\nenvelope')
for a,b in [((2,2.78),(2.6,2.78)),((4.3,2.78),(4.9,2.78)),((6.6,2.78),(7.2,2.78)),((8.9,2.78),(9.45,2.78))]: arrow(ax,a,b)
ax.text(5.5,.9,'The construction is intrinsic for the declared one break Clifford datum, up to equivariant isometry.',ha='center',fontsize=8)
save(fig,'10_one_break_envelope.pdf')

# 11 restricted bridge
fig, ax = plt.subplots(figsize=(8.5,4.5)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,5)
box(ax,(.6,3.2),3,.75,'Galois side symplectic envelope')
box(ax,(6.4,3.2),3,.75,'type side quotient $J^1/H^1$')
arrow(ax,(3.6,3.58),(6.4,3.58)); ax.text(5,3.92,'equivariant symplectic isometry',ha='center',fontsize=8)
box(ax,(.6,1.2),3,.75,'Heisenberg representation')
box(ax,(6.4,1.2),3,.75,'Heisenberg representation')
arrow(ax,(2.1,3.18),(2.1,1.97)); arrow(ax,(7.9,3.18),(7.9,1.97))
arrow(ax,(3.6,1.58),(6.4,1.58)); ax.text(5,1.92,'Stone von Neumann intertwiner',ha='center',fontsize=8)
ax.text(5,.45,'A residual scalar discrepancy is removed by matching one cyclic stabilizer generator phase.',ha='center',fontsize=8)
save(fig,'11_restricted_bridge.pdf')

# 12 odd phase blocks
fig, ax = plt.subplots(figsize=(8,4)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,5)
for i,t in enumerate(['hyperbolic block','anisotropic block','fixed part']): box(ax,(.6+3.1*i,3),2.2,.7,t)
box(ax,(3.05,1.15),3.9,.85,r'$\gamma(g,V)=\prod_j\gamma(g_j,V_j)$'+'\nunder orthogonal direct sums',9)
for i in range(3): arrow(ax,(1.7+3.1*i,2.98),(4.2+0.3*i,2.0))
ax.text(5,.45,r'In odd characteristic the normalized finite Weil phase is controlled blockwise.',ha='center')
save(fig,'12_odd_phase_blocks.pdf')

# 13 dyadic Arf
fig, ax = plt.subplots(figsize=(8,4.3)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,5)
box(ax,(.5,3.1),2.2,.8,r'symplectic form'+'\n'+r'$b$ over $\mathrm{F}_2$')
box(ax,(3.5,3.1),2.2,.8,'quadratic refinement\n$q(x+y)-q(x)-q(y)=b(x,y)$')
box(ax,(6.5,3.1),1.4,.8,'Arf\ninvariant')
box(ax,(8.45,3.1),1.1,.8,'Gauss\nsign')
for a,b in [((2.7,3.5),(3.5,3.5)),((5.7,3.5),(6.5,3.5)),((7.9,3.5),(8.45,3.5))]: arrow(ax,a,b)
ax.text(5,1.35,r'$\sum_x(-1)^{q(x)}=(-1)^{\operatorname{Arf}(q)}2^r$',ha='center',fontsize=11)
ax.text(5,.55,'The alternating form alone does not determine the dyadic phase.',ha='center')
save(fig,'13_dyadic_quadratic_refinement.pdf')

# 14 holonomy graph
fig, ax = plt.subplots(figsize=(7,5)); ax.axis('off'); ax.set_xlim(-1.4,1.4); ax.set_ylim(-1.25,1.45)
pts=[(-.9,.7),(0,1.15),(.9,.7),(.85,-.35),(0,-.9),(-.85,-.35)]
edges=[(0,1),(1,2),(2,3),(3,4),(4,5),(5,0),(0,3),(1,4)]
for u,v in edges:
    arrow(ax,pts[u],pts[v],style='-|>',lw=.8)
for i,p in enumerate(pts):
    ax.add_patch(Circle(p,.11,fill=False)); ax.text(p[0],p[1],str(i),ha='center',va='center')
ax.text(0,-1.17,'Tree edges fix gauges. Fundamental cycle holonomies contain the remaining obstruction.',ha='center',fontsize=8)
save(fig,'14_matrix_holonomy.pdf')

# 15 breakwise decomposition
fig, ax = plt.subplots(figsize=(8.5,4.2)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,4.5)
for i,r in enumerate([1,2,3]): box(ax,(.5+3*i,3),2.2,.7,rf'break $r_{r}$ packet')
box(ax,(3.1,1.1),3.8,.9,r'$V=V_{r_1}\perp V_{r_2}\perp V_{r_3}$'+'\n'+r'$\omega_V\cong\omega_{r_1}\otimes\omega_{r_2}\otimes\omega_{r_3}$',9)
for i in range(3): arrow(ax,(1.6+3*i,2.98),(4.1+0.4*i,2.0))
save(fig,'15_breakwise_decomposition.pdf')

# 16 boundary ladder
fig, ax = plt.subplots(figsize=(8,5)); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,7)
steps=[
'finite tame packets', 'intrinsic one break envelope', 'equivariant type side bridge',
'canonical phase comparison', 'all break assembly', 'pair local factor comparison',
'independent atomic correspondence'
]
for i,t in enumerate(steps):
    y=6.3-.85*i
    box(ax,(2.6,y),4.8,.55,t,8)
    if i<len(steps)-1: arrow(ax,(5,y),(5,y-.28))
ax.text(1.15,5.65,'proved',rotation=90,ha='center',va='center')
ax.text(1.15,2.45,'open beyond\nrestricted cases',rotation=90,ha='center',va='center',fontsize=8)
ax.plot([1.8,1.8],[4.1,6.8],linewidth=1); ax.plot([1.8,1.8],[.8,4.0],linewidth=1,linestyle=':')
save(fig,'16_boundary_ladder.pdf')

print(f'generated {len(list(OUT.glob("*.pdf")))} vector figures')
