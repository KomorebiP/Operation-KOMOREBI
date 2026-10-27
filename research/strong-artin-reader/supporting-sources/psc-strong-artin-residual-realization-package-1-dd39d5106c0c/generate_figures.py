from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

OUT=Path(__file__).resolve().parent/'figures'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'serif','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})

def save(fig,name):
    fig.savefig(OUT/name,bbox_inches='tight'); plt.close(fig)

def box(ax,x,y,w,h,text):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.02',fill=False,linewidth=1.1))
    ax.text(x,y,text,ha='center',va='center')

def arrow(ax,a,b,label=None):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=11,linewidth=1.0))
    if label:
        ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,label,ha='center',va='center',fontsize=8)

# 1 architecture
fig,ax=plt.subplots(figsize=(9,3.4)); ax.axis('off')
xs=[.8,2.7,4.6,6.5,8.4]
labels=['Artin parameter','cyclic restriction','automorphic base change','descent fibre','attachment']
for x,l in zip(xs,labels): box(ax,x,1.8,1.35,.68,l)
for a,b,t in zip(xs[:-1],xs[1:],['restrict','known sector','descend','align']): arrow(ax,(a+.7,1.8),(b-.7,1.8),t)
ax.text(4.6,2.85,'Strong Artin reduced to cyclic attachment',ha='center',fontsize=12)
ax.text(4.6,.55,'The first three arrows are available in the solvable induction program. The last arrow is the remaining gate.',ha='center',fontsize=8.5)
ax.set_xlim(0,9.2); ax.set_ylim(.2,3.2); save(fig,'01_artin_architecture.pdf')

# 2 two torsors
fig,ax=plt.subplots(figsize=(8.6,4)); ax.axis('off')
p=5
for row,y,title in [(0,2.8,'Galois extension torsor'),(1,1.2,'automorphic descent torsor')]:
    for j in range(p):
        x=1.2+j*1.45
        ax.add_patch(Circle((x,y),.20,fill=False)); ax.text(x,y,str(j),ha='center',va='center')
        if j<p-1: arrow(ax,(x+.24,y),(x+1.20,y))
    ax.text(.05,y,title,ha='left',va='center',fontsize=10)
ax.text(4.1,3.65,'Both fibres are torsors under the same quotient character group',ha='center',fontsize=11)
for j in range(p):
    x=1.2+j*1.45
    ax.plot([x,x],[2.56,1.44],linestyle=':',linewidth=.8)
ax.text(7.8,2.0,'attachment =\ncorrect offset',ha='center')
ax.set_xlim(0,8.6); ax.set_ylim(.5,3.9); save(fig,'02_cyclic_torsors.pdf')

# 3 coefficient rotation
fig,ax=plt.subplots(figsize=(7.2,4.1))
p=5
angles=np.arange(p)*2*np.pi/p
for k in [1,2,5]:
    vals=np.exp(1j*k*angles)
    ax.scatter(vals.real,vals.imag,label=f'degree {k}')
ax.axhline(0,linewidth=.7); ax.axvline(0,linewidth=.7)
ax.set_aspect('equal'); ax.legend(frameon=False); ax.set_title('Scalar twist rotates the degree k Hecke coefficient by $\\zeta^k$')
save(fig,'03_coefficient_rotations.pdf')

# 4 extension spectrum polynomials
fig,ax=plt.subplots(figsize=(8,4))
labels=['stable type A','stable type B','orbit type C']
for i,l in enumerate(labels):
    y=3-i
    ax.text(.2,y,l,ha='left',va='center')
    if i<2:
        mult=[1,0,2,0,1] if i==0 else [0,1,1,0,0]
        ax.bar(np.arange(5)+1.8,np.array(mult)*.28,bottom=y-.15,width=.55)
    else:
        ax.plot([1.8,6.2],[y,y],linewidth=2); ax.text(4,y+.2,'induced block: no extension label',ha='center')
ax.set_xlim(0,7); ax.set_ylim(.4,3.6); ax.set_xticks(np.arange(5)+1.8,[r'$0$',r'$1$',r'$2$',r'$3$',r'$4$']); ax.set_yticks([])
ax.set_title('Local extension spectra over a cyclic quotient'); save(fig,'04_extension_spectra.pdf')

# 5 global intersection
fig,ax=plt.subplots(figsize=(8,3.7)); ax.axis('off')
sets=[{0,1,2},{1,2,3},{1,4},{1,2}]
for i,S in enumerate(sets):
    y=3.0-i*.65
    ax.text(.4,y,f'place {i+1}',ha='left')
    for j in range(5):
        x=2+j*.9
        circ=Circle((x,y),.13,fill=(j in S),alpha=.35 if j in S else 1)
        ax.add_patch(circ); ax.text(x,y,str(j),ha='center',va='center',fontsize=8)
ax.text(6.8,1.95,'global index\nexists iff\nintersection nonempty',ha='center')
ax.set_xlim(0,7.8); ax.set_ylim(.5,3.5); save(fig,'05_global_alignment.pdf')

# 6 finite satake roots
fig,ax=plt.subplots(figsize=(6.2,6.2));
M=7; p=3
for order,radius,marker in [(M,1.0,'o'),(p*M,1.25,'x')]:
    ang=np.arange(order)*2*np.pi/order
    ax.scatter(radius*np.cos(ang),radius*np.sin(ang),marker=marker,label=f'$\\mu_{{{order}}}$')
ax.set_aspect('equal'); ax.axhline(0,linewidth=.6); ax.axvline(0,linewidth=.6); ax.legend(frameon=False)
ax.set_title('Finite base change forces descended Satake roots into a finite cyclotomic set')
save(fig,'06_finite_satake.pdf')

# 7 Kim-Yamauchi funnel
fig,ax=plt.subplots(figsize=(8.5,4)); ax.axis('off')
items=[('finite base change',1.0,3.0),('finite Satake roots',3.0,3.0),('integral Hecke data',5.0,3.0),('finite Hecke field',7.0,3.0),('Artin realization\ncriterion',4.0,1.2)]
for text,x,y in items: box(ax,x,y,1.5,.65,text)
for a,b in [((1.75,3),(2.25,3)),((3.75,3),(4.25,3)),((5.75,3),(6.25,3)),((5.0,2.65),(4.25,1.55)),((7.0,2.65),(4.65,1.55))]: arrow(ax,a,b)
ax.text(1.7,1.2,'remaining inputs:\nmod l realization\nGalois conjugacy\nexterior functoriality',ha='center',va='center')
ax.set_xlim(.1,7.9); ax.set_ylim(.5,3.7); save(fig,'07_finite_satake_funnel.pdf')

# 8 positive cone
fig,ax=plt.subplots(figsize=(7.2,5.0))
ax.arrow(0,0,5,0,head_width=.08,length_includes_head=True); ax.arrow(0,0,0,4,head_width=.08,length_includes_head=True)
for a,b in [(1,0),(0,1),(2,1),(1,2),(3,2)]: ax.scatter(a,b)
ax.fill([0,5,5],[0,0,4],alpha=.08)
ax.scatter(2.5,1.5,marker='*',s=140); ax.text(2.65,1.55,r'$m\chi$',fontsize=11)
ax.text(3.2,.45,'positive cone generated by\nknown entire packets',ha='center')
ax.set_xlim(-.2,5.4); ax.set_ylim(-.2,4.4); ax.set_xticks([]); ax.set_yticks([]); ax.set_title('Positive cone certificate for Artin holomorphy')
save(fig,'08_positive_cone.pdf')

# 9 clifford recursion
fig,ax=plt.subplots(figsize=(9,3.3)); ax.axis('off')
word=list('IEEIE')
for i,w in enumerate(word):
    x=.9+i*1.55
    box(ax,x,1.7,.85,.65,w)
    if i<len(word)-1: arrow(ax,(x+.45,1.7),(x+1.1,1.7))
    ax.text(x,.85,'induction' if w=='I' else 'attachment',ha='center',fontsize=8)
ax.text(4.0,2.7,'Clifford recursion: only E steps require new Strong Artin input',ha='center',fontsize=11)
ax.set_xlim(.2,8.3); ax.set_ylim(.4,3.0); save(fig,'09_clifford_recursion.pdf')

# 10 rank-prime sieve
fig,ax=plt.subplots(figsize=(7.5,4.2))
ns=np.arange(2,19)
vals=[]
for n in ns:
    primes=[]
    x=n; q=2
    while q*q<=x:
        if x%q==0:
            primes.append(q)
            while x%q==0:x//=q
        q+=1
    if x>1:primes.append(x)
    vals.append(len(primes))
ax.bar(ns,vals); ax.set_xlabel('rank n'); ax.set_ylabel('number of prime divisors'); ax.set_title('Only quotient primes dividing the rank evade determinant selection')
save(fig,'10_rank_prime_sieve.pdf')

# 11 route comparison
fig,ax=plt.subplots(figsize=(9,4.2)); ax.axis('off')
box(ax,1.0,2.1,1.5,.7,'Strong Artin target')
box(ax,3.5,3.1,1.7,.7,'cyclic attachment\nspectra')
box(ax,6.7,3.1,1.8,.7,'finite Satake\nrealization')
box(ax,3.5,1.1,1.7,.7,'positive cone\nholomorphy')
box(ax,6.7,1.1,1.8,.7,'Artin L function\nholomorphy')
arrow(ax,(1.78,2.35),(2.62,2.85)); arrow(ax,(4.38,3.1),(5.78,3.1)); arrow(ax,(1.78,1.85),(2.62,1.35)); arrow(ax,(4.38,1.1),(5.78,1.1))
ax.text(5.1,2.05,'automorphy route',ha='center'); ax.text(5.1,.35,'analytic route',ha='center')
ax.set_xlim(.1,8.0); ax.set_ylim(.15,3.7); save(fig,'11_two_artin_routes.pdf')

print('generated',len(list(OUT.glob('*.pdf'))),'figures')

# 12 finite alphabet and separating prime
fig,ax=plt.subplots(figsize=(8.4,4.2)); ax.axis('off')
polys=['$P_1$','$P_2$','$P_3$','$Q_1$','$Q_2$']
xs=np.linspace(1.0,7.2,len(polys))
for x,l in zip(xs,polys):
    box(ax,x,3.0,.9,.58,l)
box(ax,4.1,1.65,2.0,.72,'reduction mod $\\lambda$')
for x in xs: arrow(ax,(x,2.68),(4.1,2.03))
for i,x in enumerate(xs):
    ax.add_patch(Circle((x,.65),.18,fill=False)); ax.text(x,.65,str(i+1),ha='center',va='center')
    arrow(ax,(4.1,1.27),(x,.86))
ax.text(4.1,3.82,'A separating prime preserves every distinction in the finite polynomial alphabet',ha='center',fontsize=11)
ax.set_xlim(.2,8.0); ax.set_ylim(.2,4.0); save(fig,'12_separating_alphabet.pdf')

# 13 one prime residual funnel
fig,ax=plt.subplots(figsize=(9.2,4.0)); ax.axis('off')
items=[('finite Satake\nalphabet',1.0,2.9),('good residual\nrealization',3.1,2.9),('restriction to\n$G_E$',5.2,2.9),('extension torsor\nindex $j_\\lambda$',7.3,2.9),('exact unramified\nattachment',4.2,1.0)]
for txt,x,y in items: box(ax,x,y,1.55,.68,txt)
for a,b in [((1.8,2.9),(2.3,2.9)),((3.9,2.9),(4.4,2.9)),((6.0,2.9),(6.5,2.9)),((7.3,2.52),(4.8,1.35)),((1.0,2.52),(3.6,1.35))]: arrow(ax,a,b)
ax.text(4.2,.28,'Injectivity of reduction lifts one residual congruence back to characteristic zero.',ha='center',fontsize=8.5)
ax.set_xlim(.1,8.4); ax.set_ylim(.1,3.65); save(fig,'13_one_prime_funnel.pdf')

# 14 quotient prime congruence
fig,ax=plt.subplots(figsize=(9.0,4.0)); ax.axis('off')
box(ax,1.2,2.8,1.6,.68,'descent polynomial\n$P_v$')
box(ax,4.0,2.8,1.6,.68,'base change\n$P_v^{[p]}$')
box(ax,6.8,2.8,1.6,.68,'Artin restriction\n$Q_v^{[p]}$')
arrow(ax,(2.02,2.8),(3.18,2.8),'$p$th power')
arrow(ax,(4.82,2.8),(5.98,2.8),'equality')
box(ax,4.0,1.05,2.4,.72,'mod $\\lambda_p$: Frobenius is injective')
arrow(ax,(4.0,2.42),(4.0,1.43))
box(ax,7.25,1.05,1.8,.72,'$\\overline{P}_v=\\overline{Q}_v$')
arrow(ax,(5.22,1.05),(6.34,1.05))
ax.text(4.35,3.65,'The quotient prime supplies residual automorphy before any lifting theorem',ha='center',fontsize=11)
ax.set_xlim(.2,8.4); ax.set_ylim(.4,3.85); save(fig,'14_quotient_prime_congruence.pdf')

# 15 l adic rigidity
fig,ax=plt.subplots(figsize=(8.3,4.2)); ax.axis('off')
box(ax,1.15,2.8,1.6,.72,'Frobenius roots\nin $\\mu_N$')
box(ax,3.55,2.8,1.65,.72,'all image elements\nsatisfy $g^N=1$')
box(ax,5.95,2.8,1.6,.72,'zero Lie algebra\nof closure')
box(ax,5.95,1.15,1.6,.72,'finite image')
arrow(ax,(1.98,2.8),(2.7,2.8),'Chebotarev')
arrow(ax,(4.4,2.8),(5.12,2.8),'differentiate')
arrow(ax,(5.95,2.42),(5.95,1.53))
ax.text(3.9,.55,'Cyclotomic Frobenius spectra cannot support positive dimensional l adic monodromy.',ha='center',fontsize=8.5)
ax.set_xlim(.2,7.3); ax.set_ylim(.3,3.65); save(fig,'15_ladic_rigidity.pdf')

# 16 realization gates
fig,ax=plt.subplots(figsize=(9.2,4.2)); ax.axis('off')
box(ax,1.0,2.8,1.55,.68,'finite Satake\ndescent')
for txt,x in [('separating residual\nprime',3.1),('one l adic\nrealization',5.2),('quotient prime\nlifting',7.3)]:
    box(ax,x,2.8,1.55,.68,txt); arrow(ax,(1.8,2.8),(x-.8,2.8))
box(ax,4.3,1.0,2.1,.72,'finite image Artin attachment')
for x in [3.1,5.2,7.3]: arrow(ax,(x,2.42),(4.3,1.38))
ax.text(4.3,.25,'Any one gate closes one invariant Clifford step.',ha='center',fontsize=9)
ax.set_xlim(.1,8.3); ax.set_ylim(.1,3.7); save(fig,'16_realization_gates.pdf')

# 17 strengthened recursion
fig,ax=plt.subplots(figsize=(9.4,4.1)); ax.axis('off')
word=list('IEEIEE')
for i,w in enumerate(word):
    x=.75+i*1.38
    box(ax,x,2.7,.72,.62,w)
    if i<len(word)-1: arrow(ax,(x+.38,2.7),(x+1.0,2.7))
    if w=='E':
        ax.text(x,1.9,'R  L  Q',ha='center',fontsize=8)
        ax.text(x,1.55,'one gate',ha='center',fontsize=7)
    else:
        ax.text(x,1.72,'induction',ha='center',fontsize=7)
ax.text(4.2,3.55,'Solvable Strong Artin closes when every E step has one realization gate',ha='center',fontsize=11)
ax.text(4.2,.65,'R = separating residual   L = l adic realization   Q = quotient prime lift',ha='center',fontsize=8.5)
ax.set_xlim(.15,8.5); ax.set_ylim(.35,3.8); save(fig,'17_strengthened_recursion.pdf')

print('generated',len(list(OUT.glob('*.pdf'))),'figures')

# 18 finite trace injection
fig,ax=plt.subplots(figsize=(9.1,4.2)); ax.axis('off')
box(ax,1.0,2.85,1.55,.72,'finite residual\nimage $\\Gamma$')
box(ax,3.45,2.85,1.85,.72,'trace coordinates\ntrace of g times basis')
box(ax,6.15,2.85,1.75,.72,'alphabet cube\nT to the d')
arrow(ax,(1.8,2.85),(2.5,2.85),'nondegenerate\npairing')
arrow(ax,(4.4,2.85),(5.25,2.85),'injective')
box(ax,3.6,1.15,2.35,.72,'$|\\Gamma|\\leq t^d\\leq t^{n^2}$')
arrow(ax,(3.45,2.47),(3.6,1.53))
ax.text(3.75,.38,'A finite trace alphabet gives a uniform group order bound in residual characteristic greater than the rank.',ha='center',fontsize=8.5)
ax.set_xlim(.15,7.25); ax.set_ylim(.15,3.75); save(fig,'18_trace_alphabet_bound.pdf')

# 19 large residual lift
fig,ax=plt.subplots(figsize=(9.4,4.3)); ax.axis('off')
items=[('finite Hecke\npolynomial alphabet',.95,3.0),('one large residual\nGalois realization',3.15,3.0),('bounded image and\ncross characteristic',5.35,3.0),('ordinary finite\nrepresentation',7.55,3.0),('exact Artin\npolynomials',4.3,1.05)]
for txt,x,y in items: box(ax,x,y,1.68,.7,txt)
for a,b,label in [((1.8,3.0),(2.3,3.0),'trace bound'),((4.0,3.0),(4.5,3.0),'$\\ell>|\\Gamma|$'),((6.2,3.0),(6.7,3.0),'Brauer lift')]: arrow(ax,a,b,label)
arrow(ax,(7.55,2.62),(5.05,1.38),'finite cyclotomic\nalphabet')
arrow(ax,(.95,2.62),(3.55,1.38),'separating prime')
ax.text(4.3,.28,'One sufficiently large residual realization already produces a characteristic zero Artin representation.',ha='center',fontsize=8.7)
ax.set_xlim(.05,8.5); ax.set_ylim(.1,3.8); save(fig,'19_large_residual_realization.pdf')

# 20 no-go filters
fig,ax=plt.subplots(figsize=(9.1,4.2)); ax.axis('off')
box(ax,.95,2.85,1.55,.7,'order $p$\ncyclic offset')
box(ax,3.15,3.05,1.75,.66,'algebraic determinant\ncharacters')
box(ax,3.15,1.85,1.75,.66,'highly ramified\nepsilon twists')
box(ax,6.35,2.45,2.0,.85,'both are blind when\n$p\\mid n$')
arrow(ax,(1.75,2.85),(2.25,3.05))
arrow(ax,(1.75,2.65),(2.25,1.95))
arrow(ax,(4.05,3.05),(5.3,2.6))
arrow(ax,(4.05,1.85),(5.3,2.3))
ax.text(4.25,.65,'The missing label must be detected by bounded depth noncentral data or by global realization.',ha='center',fontsize=9)
ax.set_xlim(.1,7.6); ax.set_ylim(.3,3.7); save(fig,'20_no_go_filters.pdf')

# 21 finite trace l adic rigidity
fig,ax=plt.subplots(figsize=(9.0,4.2)); ax.axis('off')
box(ax,.95,2.85,1.55,.7,'finite Frobenius\ntrace alphabet')
box(ax,3.2,2.85,1.75,.7,'trace finite on\nalgebraic monodromy')
box(ax,5.6,2.85,1.75,.7,'identity component\nhas trace $n$')
box(ax,5.6,1.15,1.75,.7,'connected part\nacts trivially')
box(ax,2.8,1.15,1.65,.7,'finite image')
arrow(ax,(1.75,2.85),(2.3,2.85),'Chebotarev')
arrow(ax,(4.1,2.85),(4.7,2.85),'Zariski')
arrow(ax,(5.6,2.47),(5.6,1.53),'torus weights')
arrow(ax,(4.7,1.15),(3.65,1.15))
ax.text(4.15,.35,'Any semisimple l adic realization of a finite Satake system is automatically Artin.',ha='center',fontsize=8.8)
ax.set_xlim(.1,7.1); ax.set_ylim(.15,3.7); save(fig,'21_finite_trace_ladic.pdf')

print('generated final',len(list(OUT.glob('*.pdf'))),'figures')
