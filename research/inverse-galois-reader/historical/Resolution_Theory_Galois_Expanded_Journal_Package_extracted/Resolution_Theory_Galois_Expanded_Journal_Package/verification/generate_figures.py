from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'font.size':9,'axes.titlesize':11})

def save(fig,name):
    fig.savefig(OUT/name,bbox_inches='tight')
    plt.close(fig)

def box(ax,x,y,w,h,text):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.025',fill=False,linewidth=1.1))
    ax.text(x,y,text,ha='center',va='center')

def arrow(ax,a,b,text=None,rad=0.0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=11,linewidth=1.0,connectionstyle=f'arc3,rad={rad}'))
    if text:
        ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.13,text,ha='center',va='center',fontsize=8)

# 1 architecture
fig,ax=plt.subplots(figsize=(9.7,3.2)); ax.axis('off')
labels=['resolved object','packet family','transfer corners','refinement','named residual']
xs=np.linspace(.9,8.8,len(labels))
for x,l in zip(xs,labels): box(ax,x,1.55,1.45,.68,l)
for a,b in zip(xs[:-1],xs[1:]): arrow(ax,(a+.75,1.55),(b-.75,1.55))
ax.text(4.85,2.72,'Resolution Theory keeps representation inside the mathematical object',ha='center',fontsize=12)
ax.set_xlim(0,9.7);ax.set_ylim(.5,2.95);save(fig,'01_architecture.pdf')

# 2 block reconstruction
fig,ax=plt.subplots(figsize=(8.2,4.2)); ax.axis('off')
for i,y in enumerate([3.1,2.2,1.3]):
    box(ax,1.2,y,1.5,.48,rf'$P_{i+1}H$')
for j,y in enumerate([3.1,2.2,1.3]):
    box(ax,7.0,y,1.5,.48,rf'$Q_{j+1}K$')
for i,ys in enumerate([3.1,2.2,1.3]):
    for j,yt in enumerate([3.1,2.2,1.3]):
        arrow(ax,(2.0,ys),(6.2,yt),rf'$Q_{j+1}TP_{i+1}$',rad=.03*(j-i))
ax.text(4.1,3.9,r'$T=\sum_{a,i}Q_aTP_i$',ha='center',fontsize=12)
ax.set_xlim(.2,8.0);ax.set_ylim(.75,4.05);save(fig,'02_block_reconstruction.pdf')

# 3 common refinement and atlas
fig,axes=plt.subplots(1,2,figsize=(9.4,3.8))
for ax,title in zip(axes,['commuting resolutions','noncommuting resolutions']):
    ax.axis('off'); ax.set_title(title)
# left grid
ax=axes[0]
for i,x in enumerate([1.0,2.0]):
    for j,y in enumerate([1.0,2.0]):
        ax.add_patch(Rectangle((x-.35,y-.35),.7,.7,fill=False))
        ax.text(x,y,rf'$P_{i+1}Q_{j+1}$',ha='center',va='center',fontsize=8)
ax.text(1.5,2.9,r'$[P_i,Q_a]=0$',ha='center')
ax.text(1.5,.25,'products form a common refinement',ha='center',fontsize=8)
ax.set_xlim(.3,2.7);ax.set_ylim(0,3.2)
# right atlas
ax=axes[1]
box(ax,.9,2.3,1.3,.5,r'$\{P_i\}$')
box(ax,2.9,2.3,1.3,.5,r'$\{Q_a\}$')
box(ax,1.9,.9,1.8,.55,r'mixed corners $Q_aTP_i$')
arrow(ax,(1.25,2.05),(1.65,1.2));arrow(ax,(2.55,2.05),(2.15,1.2))
ax.text(1.9,3.0,r'$[P_i,Q_a]\ne0$',ha='center')
ax.text(1.9,.25,'an atlas replaces a false global chart',ha='center',fontsize=8)
ax.set_xlim(.15,3.65);ax.set_ylim(0,3.25)
save(fig,'03_common_refinement_atlas.pdf')

# 4 linking algebra
fig,ax=plt.subplots(figsize=(8.7,4.2)); ax.axis('off')
box(ax,1.25,2.3,1.9,.65,'compatible corner maps')
box(ax,4.35,2.3,2.1,.65,'resolved linking algebra')
box(ax,7.55,2.3,1.9,.65,r'$B(K)$')
arrow(ax,(2.25,2.3),(3.25,2.3),'assemble')
arrow(ax,(5.45,2.3),(6.55,2.3),'unique * map')
ax.text(4.35,3.35,r'$p_yAp_x\longmapsto Q_yB(K)Q_x$',ha='center',fontsize=11)
ax.text(4.35,.8,'composition and adjoint are checked corner by corner',ha='center')
ax.set_xlim(.15,8.55);ax.set_ylim(.45,3.6);save(fig,'04_linking_universal_property.pdf')

# 5 refinement naturality diagram
fig,ax=plt.subplots(figsize=(8.0,4.6));ax.axis('off')
box(ax,1.5,3.1,1.7,.6,r'$e=\sum_\alpha e_\alpha$')
box(ax,6.5,3.1,1.7,.6,r'$\pi(e)=\sum_\alpha\pi(e_\alpha)$')
box(ax,1.5,1.1,1.7,.6,'abstract refinement')
box(ax,6.5,1.1,1.7,.6,'projector refinement')
arrow(ax,(2.4,3.1),(5.6,3.1),r'$\pi$')
arrow(ax,(2.4,1.1),(5.6,1.1),r'$\pi$')
arrow(ax,(1.5,2.78),(1.5,1.42),'refine')
arrow(ax,(6.5,2.78),(6.5,1.42),'refine')
ax.text(4,4.05,'representation and refinement commute',ha='center',fontsize=12)
ax.set_xlim(.45,7.55);ax.set_ylim(.55,4.25);save(fig,'05_refinement_naturality.pdf')

# 6 countable convergence
fig,ax=plt.subplots(figsize=(7.8,4.0))
n=np.arange(1,60)
strong=1/np.sqrt(n)
norm=np.ones_like(n,dtype=float)
ax.plot(n,strong,label=r'$\|(I-P_N)x\|$ for one vector')
ax.plot(n,norm,label=r'$\|I-P_N\|$')
ax.set_xlabel('number of retained packets')
ax.set_ylabel('defect')
ax.set_title('Countable resolution: strong convergence need not be norm convergence')
ax.legend(frameon=False)
save(fig,'06_strong_vs_norm.pdf')

# 7 unbounded completion
fig,ax=plt.subplots(figsize=(9.1,3.9));ax.axis('off')
box(ax,1.2,2.1,1.55,.65,'closed generator $D$')
box(ax,4.55,3.0,1.9,.62,r'resolvent $(D-i)^{-1}$')
box(ax,4.55,1.2,1.9,.62,r'bounded transform $F_D$')
box(ax,7.9,2.1,1.55,.65,'packet calculus')
arrow(ax,(2.0,2.35),(3.55,2.8),'bounded')
arrow(ax,(2.0,1.85),(3.55,1.4),'bounded')
arrow(ax,(5.55,2.8),(7.05,2.35))
arrow(ax,(5.55,1.4),(7.05,1.85))
ax.text(4.55,3.65,'unbounded structure enters through bounded surrogates and graph data',ha='center',fontsize=11)
ax.set_xlim(.15,8.85);ax.set_ylim(.55,3.85);save(fig,'07_unbounded_completion.pdf')

# 8 nonlinear hypergraph
fig,ax=plt.subplots(figsize=(8.7,4.1));ax.axis('off')
for i,x in enumerate([1.0,2.2,3.4]):
    ax.add_patch(Circle((x,2.7),.2,fill=False));ax.text(x,2.7,rf'$j_{i+1}$',ha='center',va='center')
box(ax,4.55,2.7,1.2,.52,r'$D^3F$')
box(ax,7.2,2.7,1.25,.52,r'output $i$')
for x in [1.0,2.2,3.4]:arrow(ax,(x+.22,2.7),(3.92,2.7))
arrow(ax,(5.18,2.7),(6.55,2.7))
ax.text(4.2,3.65,'multilinear packet transfer is a typed hyperedge',ha='center',fontsize=11)
ax.text(4.2,1.25,r'$Q_iD^mF(P_{j_1}\cdot,\ldots,P_{j_m}\cdot)$',ha='center',fontsize=11)
ax.set_xlim(.35,8.0);ax.set_ylim(.75,3.85);save(fig,'08_nonlinear_hypergraph.pdf')

# 9 operad composition
fig,ax=plt.subplots(figsize=(8.4,4.5));ax.axis('off')
# tree
for x in [1.0,2.1,3.2,5.3,6.4]:
    ax.add_patch(Circle((x,.8),.16,fill=False))
box(ax,2.1,2.0,1.15,.48,r'$D^2F$')
box(ax,5.85,2.0,1.15,.48,r'$D^2F$')
box(ax,4.0,3.25,1.15,.48,r'$D^2G$')
for x in [1.0,2.1]:arrow(ax,(x,1.0),(1.8,1.76))
arrow(ax,(3.2,1.0),(2.4,1.76))
for x in [5.3,6.4]:arrow(ax,(x,1.0),(5.85,1.76))
arrow(ax,(2.68,2.2),(3.65,3.0));arrow(ax,(5.27,2.2),(4.35,3.0))
ax.text(4.0,4.05,'Faà di Bruno composition is rooted packet tree substitution',ha='center',fontsize=11)
ax.set_xlim(.35,7.1);ax.set_ylim(.45,4.25);save(fig,'09_operad_composition.pdf')

# 10 logic fibration
fig,ax=plt.subplots(figsize=(9.0,4.1));ax.axis('off')
box(ax,1.1,2.15,1.5,.6,'coarse resolution')
box(ax,4.4,3.0,1.7,.6,'Boolean predicates')
box(ax,4.4,1.3,1.7,.6,'error certificates')
box(ax,7.8,2.15,1.5,.6,'fine resolution')
arrow(ax,(1.88,2.35),(3.48,2.82),'pullback')
arrow(ax,(1.88,1.95),(3.48,1.48),'transport')
arrow(ax,(5.32,2.82),(7.02,2.35),'refine')
arrow(ax,(5.32,1.48),(7.02,1.95),'refine')
ax.text(4.45,3.75,'Resolution Logic keeps truth and quantitative evidence in parallel fibers',ha='center',fontsize=11)
ax.set_xlim(.2,8.7);ax.set_ylim(.65,3.95);save(fig,'10_resolution_logic.pdf')

# 11 realization atlas
fig,ax=plt.subplots(figsize=(9.8,5.2));ax.axis('off')
box(ax,4.9,4.1,2.35,.7,'abstract resolved system')
positions=[(.9,1.65,'Fourier\ncharacter chart'),(2.9,1.65,'wavelet and\npolyphase chart'),(4.9,1.65,'arithmetic\nresidue chart'),(6.9,1.65,'quantum\nprojector chart'),(8.9,1.65,'Galois fixed\nobject chart')]
for x,y,t in positions:
    box(ax,x,y,1.55,.72,t);arrow(ax,(4.9,3.72),(x,y+.4),rad=.07*(x-4.9)/4.0)
ax.text(4.9,.55,'every chart preserves packets, transfer corners, and declared refinement laws',ha='center')
ax.set_xlim(.05,9.75);ax.set_ylim(.3,4.55);save(fig,'11_realization_atlas.pdf')

# 12 boundary map
fig,ax=plt.subplots(figsize=(9.7,4.8));ax.axis('off')
proved=[('finite corners',.9,3.35),('universal C*\nrepresentation',2.8,3.35),('countable and\nunbounded',4.9,3.35),('nonlinear jets',6.95,3.35),('Galois and\nramification',8.75,3.35)]
for t,x,y in proved: box(ax,x,y,1.45,.62,t)
for (_,a,_),(_,b,_) in zip(proved[:-1],proved[1:]):arrow(ax,(a+.74,3.35),(b-.74,3.35))
box(ax,1.7,1.25,1.8,.62,'monoidal fiber functor')
box(ax,3.75,1.25,1.8,.62,'measurable descent')
box(ax,5.8,1.25,1.8,.62,'modular wild theory')
box(ax,7.85,1.25,1.8,.62,'global inverse and logic')
ax.text(4.85,4.25,'proved core and exact remaining frontier',ha='center',fontsize=12)
ax.text(4.85,.4,'open problems remain separate existence, descent, and stability theorems',ha='center')
ax.set_xlim(.05,9.55);ax.set_ylim(.15,4.5);save(fig,'12_boundary_map.pdf')

# 13 compression projection
fig,ax=plt.subplots(figsize=(7.9,4.1));ax.axis('off')
box(ax,1.4,2.2,1.8,.62,'full transfer $T$')
box(ax,4.0,3.0,1.8,.62,'retained blocks')
box(ax,4.0,1.4,1.8,.62,'named residual')
box(ax,6.8,2.2,1.6,.62,'reconstruction')
arrow(ax,(2.35,2.45),(3.05,2.82),'project')
arrow(ax,(2.35,1.95),(3.05,1.58),'subtract')
arrow(ax,(4.95,2.85),(6.0,2.4))
arrow(ax,(4.95,1.55),(6.0,2.0))
ax.text(4.0,3.75,'compression is safe only when the complement remains explicit',ha='center',fontsize=11)
ax.set_xlim(.3,7.7);ax.set_ylim(.55,3.95);save(fig,'13_compression_residual.pdf')

print('generated',len(list(OUT.glob('*.pdf'))),'figures')

# 14 resolution metric and motion
fig,ax=plt.subplots(figsize=(8.2,4.2))
t=np.linspace(0,1,200)
theta=0.9*np.sin(np.pi*t/2)
d=np.sqrt(2)*np.abs(np.sin(theta/2))
ax.plot(t,d,label='chordal projector distance')
ax.set_xlabel('path parameter')
ax.set_ylabel('distance from the initial packet')
ax.set_title('Geometry of a moving rank one packet')
ax.legend(frameon=False)
save(fig,'14_resolution_metric.pdf')

# 15 block stability
fig,ax=plt.subplots(figsize=(8.4,4.1))
eps=np.linspace(0,0.5,100)
ax.plot(eps,2*eps,label='proved block field envelope')
ax.plot(eps,eps,label='ideal linear response')
ax.set_xlabel('combined source and target resolution displacement')
ax.set_ylabel('relative block field defect')
ax.set_title('Lipschitz stability of mixed transfer blocks')
ax.legend(frameon=False)
save(fig,'15_block_stability.pdf')

# 16 Kato transport
fig,ax=plt.subplots(figsize=(9.0,4.0));ax.axis('off')
box(ax,1.2,2.1,1.7,.62,r'$P_i(0)$')
box(ax,4.5,3.0,2.0,.62,r'$U(t)$')
box(ax,7.8,2.1,1.7,.62,r'$P_i(t)$')
box(ax,4.5,1.05,2.3,.62,r'$K(t)=\sum_i\dot P_iP_i$')
arrow(ax,(2.1,2.25),(3.45,2.82),'transport')
arrow(ax,(5.55,2.82),(6.9,2.25),'conjugate')
arrow(ax,(4.5,1.38),(4.5,2.65),'generate')
ax.text(4.5,3.65,'Covariant transport separates physical evolution from chart motion',ha='center',fontsize=11)
ax.set_xlim(.2,8.8);ax.set_ylim(.45,3.85);save(fig,'16_kato_transport.pdf')

# 17 commutant gap
fig,ax=plt.subplots(figsize=(8.0,4.2))
leak=np.logspace(-6,-1,100)
for gamma,marker in [(0.2,'o'),(1.0,'s'),(5.0,'^')]:
    dist=np.sqrt(leak/gamma)
    ax.loglog(leak,dist,marker=marker,markevery=20,label=rf'$\gamma={gamma}$')
ax.set_xlabel('commutator leakage energy')
ax.set_ylabel('distance to the exact commutant')
ax.set_title('The commutant gap converts leakage into geometric stability')
ax.legend(frameon=False)
save(fig,'17_commutant_gap.pdf')

# 18 weighted inverse paths
fig,ax=plt.subplots(figsize=(9.3,4.4));ax.axis('off')
for i,x in enumerate([.8,2.2,3.6,5.0,6.4,7.8]):
    ax.add_patch(Circle((x,1.2),.18,fill=False));ax.text(x,1.2,str(i),ha='center',va='center',fontsize=8)
for i in range(5):
    arrow(ax,(.98+1.4*i,1.2),(2.02+1.4*i,1.2))
arrow(ax,(.98,1.35),(4.82,2.55),'long packet path',rad=-.18)
arrow(ax,(2.38,1.35),(7.62,2.75),'another path',rad=-.15)
box(ax,4.3,3.25,2.5,.62,r'$T^{-1}=\sum_{n\geq 0}(-D^{-1}R)^nD^{-1}$')
ax.text(4.3,.45,'inverse blocks are sums over weighted packet paths',ha='center')
ax.set_xlim(.2,8.6);ax.set_ylim(.2,3.65);save(fig,'18_weighted_inverse_paths.pdf')

# 19 strict and Karoubi completion
fig,ax=plt.subplots(figsize=(9.0,4.2));ax.axis('off')
box(ax,1.2,2.4,1.8,.62,'finite object windows')
box(ax,4.4,3.05,2.0,.62,'strict multiplier limit')
box(ax,4.4,1.55,2.0,.62,'packet idempotents')
box(ax,7.7,2.4,1.8,.62,'Karoubi packet objects')
arrow(ax,(2.15,2.55),(3.35,2.92),'strict')
arrow(ax,(2.15,2.25),(3.35,1.68),'split')
arrow(ax,(5.45,2.92),(6.75,2.55))
arrow(ax,(5.45,1.68),(6.75,2.25))
ax.text(4.45,3.78,'Countable completion separates norm, strict, strong, and object level closure',ha='center',fontsize=11)
ax.set_xlim(.2,8.7);ax.set_ylim(.55,4.0);save(fig,'19_strict_karoubi.pdf')

# 20 nonlinear dynamics and stochastic correction
fig,ax=plt.subplots(figsize=(9.2,4.4));ax.axis('off')
box(ax,1.1,2.4,1.65,.62,'linear semigroup')
box(ax,3.6,3.1,1.8,.62,'nonlinear packet vertex')
box(ax,3.6,1.55,1.8,.62,'Ito quadratic vertex')
box(ax,6.3,2.4,1.8,.62,'Duhamel tree')
box(ax,8.3,2.4,1.25,.62,'flow')
arrow(ax,(1.95,2.55),(2.68,2.98))
arrow(ax,(1.95,2.25),(2.68,1.68))
arrow(ax,(4.55,3.0),(5.35,2.55))
arrow(ax,(4.55,1.65),(5.35,2.25))
arrow(ax,(7.25,2.4),(7.65,2.4))
ax.text(4.6,3.85,'Resolved dynamics uses linear edges, nonlinear hyperedges, and stochastic contractions',ha='center',fontsize=11)
ax.set_xlim(.2,8.95);ax.set_ylim(.55,4.05);save(fig,'20_dynamics_stochastic.pdf')

# 21 countable logic
fig,ax=plt.subplots(figsize=(8.8,4.2));ax.axis('off')
box(ax,1.2,2.2,1.65,.62,'countable fine atoms')
box(ax,4.35,3.0,2.0,.62,r'$\exists=\sup$ over fibers')
box(ax,4.35,1.45,2.0,.62,r'$\forall=\inf$ over fibers')
box(ax,7.6,2.2,1.65,.62,'coarse certificates')
arrow(ax,(2.05,2.45),(3.3,2.88))
arrow(ax,(2.05,1.95),(3.3,1.58))
arrow(ax,(5.4,2.88),(6.75,2.45))
arrow(ax,(5.4,1.58),(6.75,1.95))
ax.text(4.4,3.7,'Countable atomic Resolution Logic is a complete indexed lattice semantics',ha='center',fontsize=11)
ax.set_xlim(.2,8.6);ax.set_ylim(.55,3.9);save(fig,'21_countable_logic.pdf')

# 22 arithmetic sieve and Gauss bridge
fig,ax=plt.subplots(figsize=(9.4,4.2));ax.axis('off')
box(ax,1.1,2.25,1.7,.62,r'parent packet $a\;\mathrm{mod}\;q$')
box(ax,3.55,3.0,1.8,.62,'forbidden child')
box(ax,3.55,1.45,1.8,.62,'survivor residual')
box(ax,6.3,2.25,1.9,.62,'additive child modes')
box(ax,8.45,2.25,1.35,.62,'Dirichlet band')
arrow(ax,(1.98,2.45),(2.62,2.85),'refine')
arrow(ax,(1.98,2.05),(2.62,1.6),'refine')
arrow(ax,(4.5,1.58),(5.3,2.05),'DFT')
arrow(ax,(7.28,2.25),(7.75,2.25),'Gauss')
ax.text(4.7,3.75,'Arithmetic realization: sieve geometry and character energy are changes of resolution',ha='center',fontsize=11)
ax.set_xlim(.15,9.15);ax.set_ylim(.55,3.95);save(fig,'22_prime_packet_gauss.pdf')

print('generated after expansion',len(list(OUT.glob('*.pdf'))),'figures')

# 23 finite Galois dictionary
fig,ax=plt.subplots(figsize=(9.4,4.2));ax.axis('off')
box(ax,1.1,2.35,1.55,.62,r'subgroup $H\leq G$')
box(ax,3.45,3.05,1.8,.62,r'average $P_H$')
box(ax,3.45,1.55,1.8,.62,r'fixed field $L^H$')
box(ax,6.2,2.35,2.0,.66,r'fixed packet $\operatorname{ran}P_H$')
box(ax,8.35,2.35,1.45,.62,'resolution order')
arrow(ax,(1.9,2.55),(2.5,2.9),'average')
arrow(ax,(1.9,2.15),(2.5,1.7),'fix')
arrow(ax,(4.4,3.0),(5.15,2.55),'range')
arrow(ax,(4.4,1.6),(5.15,2.15),'realize')
arrow(ax,(7.23,2.35),(7.58,2.35),'reverse')
ax.text(4.7,3.82,'Finite Galois theory as a projector resolution',ha='center',fontsize=12)
ax.text(4.7,.65,r'$H\leq J\Longrightarrow P_J\leq P_H$ and $L^J\subseteq L^H$',ha='center')
ax.set_xlim(.15,9.1);ax.set_ylim(.4,4.0);save(fig,'23_galois_resolution_dictionary.pdf')

# 24 normality and quotient
fig,ax=plt.subplots(figsize=(9.2,4.0));ax.axis('off')
box(ax,1.15,2.2,1.65,.62,r'$H\triangleleft G$')
box(ax,3.55,3.0,1.8,.62,r'$e_H\in Z(C[G])$')
box(ax,3.55,1.45,1.8,.62,r'$[P_H,U_g]=0$')
box(ax,6.25,2.2,1.85,.68,r'$V^H$ is $G$ invariant')
box(ax,8.25,2.2,1.35,.62,r'$G/H$ action')
arrow(ax,(2.0,2.45),(2.62,2.88))
arrow(ax,(2.0,1.95),(2.62,1.57))
arrow(ax,(4.5,2.88),(5.28,2.45))
arrow(ax,(4.5,1.57),(5.28,1.95))
arrow(ax,(7.2,2.2),(7.55,2.2),'compress')
ax.text(4.6,3.72,'Normality is central compatibility of the fixed resolution',ha='center',fontsize=11)
ax.set_xlim(.15,8.95);ax.set_ylim(.55,3.9);save(fig,'24_normality_quotient.pdf')

# 25 Fourier Galois chart
fig,ax=plt.subplots(figsize=(9.4,4.2));ax.axis('off')
box(ax,1.2,2.25,1.8,.66,'normal basis\ngroup packets')
box(ax,4.0,2.25,1.75,.66,'finite Fourier\ntransform')
box(ax,6.75,2.95,1.8,.62,r'character packets $e_\chi$')
box(ax,6.75,1.5,1.8,.62,r'fixed projector $P_H$')
box(ax,8.75,2.25,1.0,.62,r'$H^\perp$')
arrow(ax,(2.15,2.25),(3.08,2.25),'change chart')
arrow(ax,(4.92,2.45),(5.82,2.82))
arrow(ax,(4.92,2.05),(5.82,1.63))
arrow(ax,(7.7,1.68),(8.2,2.05),'index')
ax.text(4.7,3.72,'Galois resolvents are Fourier packet coordinates',ha='center',fontsize=11)
ax.text(4.7,.62,r'$P_H=\sum_{\chi\in H^\perp}e_\chi$',ha='center',fontsize=11)
ax.set_xlim(.15,9.25);ax.set_ylim(.4,3.95);save(fig,'25_fourier_galois_chart.pdf')

# 26 Galois closure atlas
fig,ax=plt.subplots(figsize=(9.4,4.5));ax.axis('off')
center=(4.7,2.35)
box(ax,*center,1.7,.62,r'$M=L^H$')
angles=np.linspace(0,2*np.pi,6,endpoint=False)
for j,ang in enumerate(angles):
    x=4.7+3.0*np.cos(ang);y=2.35+1.45*np.sin(ang)
    box(ax,x,y,1.35,.48,rf'$L^{{g_{j+1}Hg_{j+1}^{{-1}}}}$')
    arrow(ax,(4.7+.9*np.cos(ang),2.35+.32*np.sin(ang)),(x-.72*np.cos(ang),y-.25*np.sin(ang)))
box(ax,2.1,.45,2.45,.5,r'$L^{\operatorname{Core}_G(H)}$: compositum')
box(ax,7.3,.45,2.55,.5,r'$L^{\operatorname{Ncl}_G(H)}$: intersection')
ax.text(4.7,4.15,'A nonnormal field is an atlas of conjugate projector charts',ha='center',fontsize=11)
ax.set_xlim(.1,9.3);ax.set_ylim(.1,4.35);save(fig,'26_galois_closure_atlas.pdf')

# 27 ramification resolution
fig,ax=plt.subplots(figsize=(9.4,4.3));ax.axis('off')
xs=np.linspace(.9,8.5,6)
labels=[r'$G_0=I$',r'$G_1$',r'$G_2$',r'$G_3$',r'$G_4$',r'$1$']
for x,l in zip(xs,labels):box(ax,x,2.75,1.0,.5,l)
for a,b in zip(xs[:-1],xs[1:]):arrow(ax,(a+.52,2.75),(b-.52,2.75),'shrink')
for j,x in enumerate(xs):
    box(ax,x,1.25,1.0,.5,rf'$P_{j}$')
    arrow(ax,(x,2.48),(x,1.52),'fix')
for a,b in zip(xs[:-1],xs[1:]):arrow(ax,(a+.52,1.25),(b-.52,1.25),'refine')
ax.text(4.7,3.75,'Ramification groups produce a nested projector filtration',ha='center',fontsize=11)
ax.text(4.7,.42,r'$D_i=P_{i+1}-P_i$ are orthogonal details and the conductor weights unresolved ranks',ha='center')
ax.set_xlim(.2,9.2);ax.set_ylim(.15,3.95);save(fig,'27_ramification_resolution.pdf')

# 28 profinite resolution
fig,ax=plt.subplots(figsize=(9.4,4.1));ax.axis('off')
xs=[1.0,2.8,4.6,6.4]
for j,x in enumerate(xs):
    box(ax,x,2.75,1.35,.52,rf'$G/H_{j+1}$')
for a,b in zip(xs[:-1],xs[1:]):arrow(ax,(a+.7,2.75),(b-.7,2.75),'quotient')
for j,x in enumerate(xs):
    box(ax,x,1.25,1.35,.52,rf'$P_{{H_{j+1}}}$')
    arrow(ax,(x,2.48),(x,1.52),'average')
for a,b in zip(xs[:-1],xs[1:]):arrow(ax,(a+.7,1.25),(b-.7,1.25),'strong refine')
box(ax,8.55,2.0,1.1,.65,r'$G$')
arrow(ax,(7.1,2.75),(8.0,2.25),'limit')
arrow(ax,(7.1,1.25),(8.0,1.75),'$P_{H_n}\to I$')
ax.text(4.7,3.72,'Profinite symmetry is reconstructed from finite quotient resolutions',ha='center',fontsize=11)
ax.set_xlim(.15,9.25);ax.set_ylim(.45,3.95);save(fig,'28_profinite_resolution.pdf')

# 29 Hilbert 90 and Brauer obstruction
fig,ax=plt.subplots(figsize=(9.2,4.3));ax.axis('off')
box(ax,1.2,2.75,1.9,.62,'linear semilinear\ncocycle')
box(ax,4.55,2.75,2.0,.62,'Hilbert 90')
box(ax,7.9,2.75,1.9,.62,'global vector\npacket')
arrow(ax,(2.2,2.75),(3.5,2.75),'trivialize')
arrow(ax,(5.6,2.75),(6.9,2.75),'descend')
box(ax,1.2,1.1,1.9,.62,'projective\ncocycle')
box(ax,4.55,1.1,2.0,.62,r'$\delta(\alpha)\in Br(L/K)$')
box(ax,7.9,1.1,1.9,.62,'central simple\nalgebra packet')
arrow(ax,(2.2,1.1),(3.5,1.1),'obstruction')
arrow(ax,(5.6,1.1),(6.9,1.1),'nonzero class')
ax.text(4.55,3.75,'Linear atlases descend. Projective atlases can retain a Brauer obstruction.',ha='center',fontsize=11)
ax.set_xlim(.15,8.95);ax.set_ylim(.45,3.95);save(fig,'29_hilbert90_brauer.pdf')

# 30 Tannakian boundary
fig,ax=plt.subplots(figsize=(9.4,4.2));ax.axis('off')
box(ax,1.15,2.25,1.9,.68,'resolved monoidal\ncategory')
box(ax,4.15,3.0,2.0,.62,'ordinary corner\nrepresentation')
box(ax,4.15,1.5,2.0,.62,'faithful exact\ntensor fiber functor')
box(ax,7.35,3.0,1.9,.62,'concrete packets\nand transfers')
box(ax,7.35,1.5,1.9,.62,r'$Aut^{\otimes}(\omega)$')
arrow(ax,(2.15,2.5),(3.1,2.9))
arrow(ax,(2.15,2.0),(3.1,1.6))
arrow(ax,(5.2,3.0),(6.35,3.0))
arrow(ax,(5.2,1.5),(6.35,1.5),'reconstruct')
ax.text(4.7,3.78,'The monoidal fiber functor is the Galois reconstruction boundary',ha='center',fontsize=11)
ax.set_xlim(.15,8.55);ax.set_ylim(.5,3.95);save(fig,'30_tannakian_boundary.pdf')

print('generated with Galois expansion',len(list(OUT.glob('*.pdf'))),'figures')
