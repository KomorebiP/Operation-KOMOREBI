from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon
from matplotlib.lines import Line2D

OUT=Path('/mnt/data/PSC_Paper_XII_Strengthened_Annals_Edition_Package/figures')
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams['pdf.fonttype']=42
plt.rcParams['ps.fonttype']=42
plt.rcParams['font.size']=10

def save(fig,name):
    fig.savefig(OUT/name,bbox_inches='tight')
    plt.close(fig)

def box(ax,xy,w,h,text,fc=None,fontsize=10,rounding=0.03,lw=1.1):
    p=FancyBboxPatch(xy,w,h,boxstyle=f'round,pad=0.02,rounding_size={rounding}',facecolor=fc,edgecolor='black',linewidth=lw)
    ax.add_patch(p)
    ax.text(xy[0]+w/2,xy[1]+h/2,text,ha='center',va='center',fontsize=fontsize)
    return p

def arrow(ax,a,b,style='-|>',lw=1.2,connectionstyle='arc3'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=12,linewidth=lw,connectionstyle=connectionstyle))

def base(figsize=(9,4.5)):
    fig,ax=plt.subplots(figsize=figsize)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    return fig,ax

# 01
fig,ax=base((11,4.6))
labels=['Residual occupancy','Local deformation','Patching support','Hecke occupancy','Realization']
xs=[.02,.22,.42,.62,.82]
for x,l in zip(xs,labels): box(ax,(x,.38),.16,.24,l,fontsize=10)
for i in range(4): arrow(ax,(xs[i]+.16,.5),(xs[i+1],.5))
ax.text(.5,.82,'Five logically separate gates',ha='center',fontsize=14)
ax.text(.5,.15,'No coordinate change supplies a missing residual root or a missing automorphic class',ha='center',fontsize=10)
save(fig,'01_global_gates.pdf')

# 02
fig,ax=base((9,5))
box(ax,(.08,.65),.3,.18,'Local deformation ring')
box(ax,(.62,.65),.3,.18,'Local condition quotient')
arrow(ax,(.38,.74),(.62,.74))
ax.text(.5,.78,'quotient map',ha='center',fontsize=9)
# components
ax.plot([.13,.22,.31],[.38,.25,.38],marker='o')
ax.plot([.13,.22,.31],[.38,.51,.38],marker='o')
ax.text(.22,.13,'Irreducible components need not be clopen',ha='center')
box(ax,(.62,.25),.3,.18,'Support locus of the chosen condition')
arrow(ax,(.38,.38),(.62,.34))
ax.text(.5,.92,'Local packets are usually quotient conditions, not central idempotents',ha='center',fontsize=13)
save(fig,'02_local_quotient_packets.pdf')

# 03
fig,ax=base((9,5))
box(ax,(.08,.37),.22,.22,'trace zero adjoint\nmodule')
box(ax,(.4,.62),.2,.18,'sign packet')
box(ax,(.4,.18),.2,.18,'standard packet')
arrow(ax,(.30,.49),(.40,.71)); arrow(ax,(.30,.47),(.40,.27))
box(ax,(.7,.62),.2,.18,'three cycle\nprojector')
box(ax,(.7,.18),.2,.18,'transposition\nprojector')
arrow(ax,(.60,.71),(.70,.71)); arrow(ax,(.60,.27),(.70,.27))
ax.text(.5,.92,'Finite adequacy certificate for the standard representation of S3 over F7',ha='center',fontsize=12)
save(fig,'03_adequacy_packets.pdf')

# 04
fig,ax=base((10,5))
levels=[('.12','O[Delta 1]'),('.32','O[Delta 2]'),('.52','O[Delta 3]'),('.72','O[[Zp^q]]')]
for x,l in levels: box(ax,(float(x),.55),.16,.18,l)
for i in range(3): arrow(ax,(float(levels[i+1][0]),.55),(float(levels[i][0])+.16,.55),style='-|>')
for x,_ in levels[:3]:
    box(ax,(float(x),.18),.16,.16,'coinvariants')
    arrow(ax,(float(x)+.08,.55),(float(x)+.08,.34))
ax.text(.5,.9,'Auxiliary group algebras and augmentation descent',ha='center',fontsize=13)
save(fig,'04_auxiliary_group_tower.pdf')

# 05
fig,ax=base((9,5))
box(ax,(.07,.58),.24,.2,'k[Delta]')
box(ax,(.39,.58),.24,.2,'truncated\npolynomial algebra')
arrow(ax,(.31,.68),(.39,.68))
box(ax,(.69,.58),.24,.2,'local augmentation\nring')
arrow(ax,(.63,.68),(.69,.68))
ax.text(.5,.42,'X_i = gamma_i minus 1',ha='center',fontsize=11)
ax.text(.5,.28,'X_i raised to the group order is zero',ha='center',fontsize=11)
ax.text(.5,.12,'The description works at odd primes and at the coefficient prime two',ha='center',fontsize=10)
save(fig,'05_augmentation_algebra.pdf')

# 06
fig,ax=base((10,5.5))
box(ax,(.08,.66),.26,.18,'patched ring R infinity')
box(ax,(.66,.66),.26,.18,'patched module M infinity')
arrow(ax,(.34,.75),(.66,.75))
ax.text(.5,.80,'full support',ha='center')
box(ax,(.08,.22),.26,.18,'finite ring R')
box(ax,(.66,.22),.26,.18,'finite module M')
arrow(ax,(.34,.31),(.66,.31))
arrow(ax,(.21,.66),(.21,.40)); arrow(ax,(.79,.66),(.79,.40))
ax.text(.5,.48,'augmentation quotient',ha='center',fontsize=10)
ax.text(.5,.08,'Full support descends by localization and Nakayama',ha='center',fontsize=12)
save(fig,'06_patching_support_descent.pdf')

# 07
fig,ax=base((9,5))
box(ax,(.05,.58),.28,.20,'R = S[[x]] divided by\nx(x minus t)')
box(ax,(.38,.58),.22,.20,'M = R divided by x')
box(ax,(.67,.58),.26,.20,'M is free over S')
arrow(ax,(.33,.68),(.38,.68)); arrow(ax,(.60,.68),(.67,.68))
# components
ax.plot([.2,.36],[.28,.12],linewidth=2)
ax.plot([.2,.36],[.28,.44],linewidth=2)
ax.scatter([.2],[.28])
ax.text(.27,.08,'two components',ha='center')
ax.plot([.65,.84],[.28,.28],linewidth=4)
ax.text(.745,.15,'support of M',ha='center')
ax.text(.5,.92,'Freeness over the auxiliary algebra does not imply full deformation support',ha='center',fontsize=12)
save(fig,'07_freeness_counterexample.pdf')

# 08
fig,ax=base((10,5))
box(ax,(.08,.56),.25,.20,'deformation ring R')
box(ax,(.67,.56),.25,.20,'Hecke algebra T')
arrow(ax,(.33,.66),(.67,.66))
ax.text(.5,.72,'ring isomorphism',ha='center')
box(ax,(.08,.20),.25,.18,'support in Spec R')
box(ax,(.67,.20),.25,.18,'support in Spec T')
arrow(ax,(.33,.29),(.67,.29))
arrow(ax,(.205,.56),(.205,.38)); arrow(ax,(.795,.56),(.795,.38))
ax.text(.5,.08,'Fitting ideals, fibers, and occupied points are transported exactly',ha='center',fontsize=11)
save(fig,'08_rt_support_transport.pdf')

# 09
fig,ax=base((10,5))
box(ax,(.05,.60),.24,.18,'finite Hecke algebra')
centers=[.46,.68,.88]
for i,x in enumerate(centers,1):
    box(ax,(x-.08,.57),.16,.20,f'local factor {i}')
    arrow(ax,(.29,.69),(x-.08,.67))
ax.text(.5,.90,'Artin decomposition into canonical generalized Hecke packets',ha='center',fontsize=13)
for x in centers:
    ax.add_patch(Circle((x,.25),.08,fill=False,linewidth=1.5))
    arrow(ax,(x,.57),(x,.33))
ax.text(.5,.08,'No semisimplicity assumption is needed for the algebra decomposition',ha='center',fontsize=10)
save(fig,'09_hecke_artin_packets.pdf')

# 10
fig,ax=base((9,5))
# Jordan blocks
for j,x in enumerate([.15,.45,.75]):
    ax.add_patch(Polygon([[x,.25],[x+.16,.25],[x+.16,.75],[x,.75]],closed=True,fill=False,linewidth=1.4))
    ax.text(x+.08,.80,f'eigenvalue a{j+1}',ha='center')
    for k in range(3):
        ax.plot([x+.02,x+.14],[.36+.13*k,.36+.13*k],linewidth=1)
ax.text(.5,.93,'Simultaneous generalized eigenspaces retain nilpotent Hecke data',ha='center',fontsize=12)
ax.text(.5,.10,'The central Artin idempotent selects a whole primary packet',ha='center')
save(fig,'10_generalized_eigenspaces.pdf')

# 11
fig,ax=base((9,5))
widths=[.82,.66,.50,.36,.24,.24]
ys=[.78,.65,.52,.39,.26,.13]
for i,(w,y) in enumerate(zip(widths,ys),1):
    ax.add_patch(FancyBboxPatch(((1-w)/2,y),w,.08,boxstyle='round,pad=.01',fill=False,linewidth=1.2))
    ax.text(.5,y+.04,f'finite packet {i}',ha='center',va='center',fontsize=9)
ax.text(.5,.93,'Nested occupied packets in one finite carrier stabilize',ha='center',fontsize=13)
save(fig,'11_finite_occupancy_staircase.pdf')

# 12
fig,ax=base((10,5))
for level,y in enumerate([.78,.58,.38,.18],1):
    xs=[.18,.42,.66,.84][:max(1,5-level)]
    for x in xs: ax.add_patch(Circle((x,y),.035,fill=False,linewidth=1.2))
    ax.text(.05,y,f'level {level}',va='center')
# stable path
pts=[(.42,.78),(.42,.58),(.42,.38),(.42,.18)]
for a,b in zip(pts[:-1],pts[1:]): arrow(ax,a,b)
ax.text(.67,.08,'stable core gives one coherent branch',ha='center')
ax.text(.5,.93,'Mittag Leffler occupancy across changing carriers',ha='center',fontsize=13)
save(fig,'12_stable_core_inverse_limit.pdf')

# 13
fig,ax=base((9,5))
for m,y in enumerate([.78,.62,.46,.30,.14],1):
    ax.plot([.12+.08*m,.90],[y,y],linewidth=4)
    ax.text(.08,y,f'P{m}',va='center')
ax.text(.5,.92,'Every finite tail is nonzero',ha='center',fontsize=12)
ax.text(.5,.05,'The total intersection is zero',ha='center',fontsize=12)
save(fig,'13_tail_escape.pdf')

# 14
fig,ax=base((11,5))
box(ax,(.03,.60),.20,.18,'algebraic\nFrobenius spine')
for i,x in enumerate([.35,.57,.79],1):
    box(ax,(x,.60),.16,.18,f'coefficient\nplace {i}')
    arrow(ax,(.23,.69),(x,.69))
    for y in [.38,.20]:
        ax.add_patch(Circle((x+.08,y),.03,fill=False))
    arrow(ax,(x+.08,.57),(x+.08,.41)); arrow(ax,(x+.08,.35),(x+.08,.23))
ax.text(.5,.92,'One spine and several companion forests',ha='center',fontsize=13)
ax.text(.5,.08,'A missing residual companion is a horizontal obstruction',ha='center',fontsize=10)
save(fig,'14_companion_spine.pdf')

# 15
fig,ax=base((10,5))
box(ax,(.08,.60),.26,.18,'rational sign\nprojectors')
box(ax,(.66,.60),.26,.18,'integral augmentation\ncoordinates')
arrow(ax,(.34,.69),(.66,.69))
ax.text(.5,.75,'replace division by two',ha='center')
box(ax,(.08,.20),.26,.18,'merged residual\npackets')
box(ax,(.66,.20),.26,.18,'weighted local\nconditions')
arrow(ax,(.34,.29),(.66,.29))
ax.text(.5,.92,'What survives at the coefficient prime two',ha='center',fontsize=13)
ax.text(.5,.08,'Augmentation survives. Adequacy and local geometry remain separate hypotheses.',ha='center',fontsize=10)
save(fig,'15_coefficient_two_boundary.pdf')

# 16
fig,ax=base((10,5))
box(ax,(.06,.58),.22,.18,'point x in Spec R')
box(ax,(.39,.58),.22,.18,'nonzero fiber M at x')
box(ax,(.72,.58),.22,.18,'Hecke eigensystem')
arrow(ax,(.28,.67),(.39,.67)); arrow(ax,(.61,.67),(.72,.67))
box(ax,(.39,.20),.22,.18,'attached Galois\nrepresentation')
arrow(ax,(.83,.58),(.61,.38)); arrow(ax,(.17,.58),(.39,.38))
ax.text(.5,.92,'Pointwise automorphy from support',ha='center',fontsize=13)
ax.text(.5,.08,'Local global compatibility and classicality complete the last step',ha='center',fontsize=10)
save(fig,'16_pointwise_automorphy.pdf')

# 17
fig,ax=base((11,5.5))
labels=[('Companion\ncompletion',.03,.62),('Patching\nsupport',.23,.62),('Hecke\noccupancy',.43,.62),('Classical\nrealization',.63,.62),('Compatible\npropagation',.83,.62)]
for text,x,y in labels: box(ax,(x,y),.14,.18,text,fontsize=9)
for i in range(4): arrow(ax,(labels[i][1]+.14,.71),(labels[i+1][1],.71))
box(ax,(.35,.22),.30,.20,'conditional automorphic\ncompletion')
for text,x,y in labels: arrow(ax,(x+.07,y),(.5,.42),connectionstyle='arc3,rad=0.05')
ax.text(.5,.94,'Final theorem architecture',ha='center',fontsize=14)
save(fig,'17_final_completion.pdf')

# 18
fig,ax=base((10,5.5))
proved=['support descent','Artin Hecke packets','pointwise fiber criterion','finite carrier compactness']
openq=['companion existence','full patching support in every class','classicality in every carrier','unrestricted reciprocity']
for i,t in enumerate(proved): box(ax,(.05,.72-.17*i),.38,.11,t,fontsize=9)
for i,t in enumerate(openq): box(ax,(.57,.72-.17*i),.38,.11,t,fontsize=9)
ax.text(.24,.91,'proved under stated hypotheses',ha='center',fontsize=12)
ax.text(.76,.91,'not proved',ha='center',fontsize=12)
ax.plot([.5,.5],[.08,.88],linewidth=1)
save(fig,'18_claim_boundary.pdf')

print(f'generated {len(list(OUT.glob("*.pdf")))} figures')
