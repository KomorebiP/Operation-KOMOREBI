"""Reproducible vector figures for Realization Boundaries.

Requires matplotlib. Uses its default colors and a consistent serif typeface.
Diagrams display proved relationships. The one data plot evaluates rad(m)
exactly on its stated finite domain.
"""
from __future__ import annotations
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from dense_lift_groups import prime, prime_divisors

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 11,
                     'mathtext.fontset': 'dejavuserif', 'pdf.fonttype': 42,
                     'svg.fonttype': 'none'})
index = []


def canvas(width: float = 7.0, height: float = 3.5):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.subplots_adjust(left=.035, right=.965, bottom=.065, top=.95)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, label, fontsize=12):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                              boxstyle='round,pad=0.05,rounding_size=0.06',
                              fill=False, linewidth=.9))
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize)


def arrow(ax, x1, y1, x2, y2, label=None, offset=.17):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops={'arrowstyle': '->', 'lw': .95})
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2+offset, label,
                ha='center', va='bottom', fontsize=9)


def save(fig, name, description):
    for suffix in ['pdf','svg','png']:
        fig.savefig(OUT/f'{name}.{suffix}', dpi=200, bbox_inches='tight', pad_inches=.1)
    plt.close(fig)
    index.append({'file':name+'.pdf','description':description,
                  'source':'src/make_figures.py','kind':'exact diagram or theorem-derived finite data'})


fig, ax=canvas(height=3.5)
xs=[.7,2.45,4.2]
for y in [3.55,1.35]:
    for i,x in enumerate(xs):
        box(ax,x,y,1.15,.65,rf'$A_{i+1}$')
    ax.text(5.7,y,r'$\cdots$',ha='center',va='center',fontsize=17)
for x1,x2 in zip(xs,xs[1:]):
    arrow(ax,x1+.58,3.55,x2-.58,3.55)
    arrow(ax,x2-.58,1.35,x1+.58,1.35)
arrow(ax,4.8,3.55,5.25,3.55)
arrow(ax,5.25,1.35,4.8,1.35)
box(ax,8.15,3.55,2.7,.95,r'$D=\bigoplus_p C_p$',13)
box(ax,8.15,1.35,2.7,.95,r'$P=\prod_p C_p$',13)
arrow(ax,6.1,3.55,6.72,3.55)
arrow(ax,6.72,1.35,6.1,1.35)
ax.text(.2,4.45,'Zero-extension maps',fontsize=10)
ax.text(.2,2.25,'Coordinate projections',fontsize=10)
ax.text(8.15,2.78,r'endomorphism-seed rank $\aleph_0$',ha='center',fontsize=9)
ax.text(8.15,.55,'topological rank 1',ha='center',fontsize=9)
save(fig,'01_two_limits','Direct and inverse systems of identical finite cyclic stages.')

fig, ax=plt.subplots(figsize=(7,3.1))
fig.subplots_adjust(left=.12,right=.98,top=.85,bottom=.24)
bits=[0,1,0,0,1,1,0,1]
selected=[]; omitted=[]
for n,a in enumerate(bits):
    ax.plot([n,n,float('nan'),n,n],[0,.60,float('nan'),.93,1],linestyle=':',linewidth=.6)
    for b,y in [(0,1),(1,0)]:
        (selected if b==a else omitted).append((n,y))
        ax.text(n,y-.2,str(prime(2*n+b)),ha='center',va='top',fontsize=10)
    ax.text(n,1.45,str(a),ha='center',fontsize=11)
ax.scatter([x for x,y in selected],[y for x,y in selected],s=74,marker='o')
ax.plot([x for x,y in omitted],[y for x,y in omitted],linestyle='None',marker='o',markersize=8,markerfacecolor='none')
ax.set_xlim(-.55,7.55);ax.set_ylim(-.5,1.65)
ax.set_xticks(range(8));ax.set_xticklabels([str(i) for i in range(8)])
ax.set_xlabel(r'pair index $n$',labelpad=8)
ax.set_yticks([0,1]);ax.set_yticklabels([r'$p_{2n+1}$',r'$p_{2n}$'])
for spine in ax.spines.values():spine.set_visible(False)
ax.tick_params(length=0,pad=9)
ax.text(-.8,1.45,r'$a_n$',ha='right',fontsize=11)
save(fig,'02_prime_pairs','Exact paired-prime selector example with filled selected coordinates.')

fig, ax=canvas(height=3.4)
box(ax,5,4.35,2.1,.65,r'$u_\varnothing=(1,0)$')
box(ax,2.4,2.65,3.55,.85,r'$m=2:\quad (u_\varnothing)_2=1$')
box(ax,7.6,2.65,3.55,.85,r'$m=3:\quad (u_\varnothing)_3=0$')
arrow(ax,4.25,4.0,2.8,3.12)
arrow(ax,5.75,4.0,7.2,3.12)
box(ax,2.4,.8,3.55,.95,'No root\ncertificate: the prime 2',11)
box(ax,7.6,.8,3.55,.95,r'$y=(1/3,0)$'+'\n'+r'$3y=u_\varnothing$',12)
arrow(ax,2.4,2.2,2.4,1.35)
arrow(ax,7.6,2.2,7.6,1.35)
save(fig,'03_root_certificates','A negative root certificate and an exact positive witness.')

fig, ax=canvas(height=3.3)
box(ax,1.4,3.2,2.2,1.0,'Selector\n'+r'$A$',12)
box(ax,5,3.2,2.8,1.0,'Normal-form copy\n'+r'$\mathbb{Q}\times D$',12)
box(ax,8.6,3.2,2.1,1.0,'Marked copy\n'+r'$(H,h)$',12)
arrow(ax,2.55,3.2,3.55,3.2,'finite cocycle',.6)
arrow(ax,6.45,3.2,7.48,3.2,'same type',.6)
arrow(ax,8.6,2.65,8.6,1.4)
arrow(ax,8.6,1.4,1.4,1.4)
arrow(ax,1.4,1.4,1.4,2.65)
ax.text(5,1.7,'Two complementary root searches recover every bit',ha='center',fontsize=10)
ax.text(5,.55,'Unmarked copies: a fixed element and finite exception data are needed.',ha='center',fontsize=9)
save(fig,'04_degree_equivalence','Construction and marked decoding, with the unmarked qualification.')

fig, ax=canvas(height=3.6)
labels=[r'$G_\varnothing$',r'$G_{\mathbb{N}}$',r'$G_K$',r'$G_A$']
xs=[1.15,3.7,6.3,8.85]
for x,label in zip(xs,labels):
    box(ax,x,4,2.05,.78,label,15)
    arrow(ax,x,3.55,5+(x-5)*.12,1.65)
box(ax,5,1.12,4.1,1.0,r'$P=\prod_p C_p$',17)
ax.text(5,.15,'The same unmarked finite quotients and transition maps',ha='center',fontsize=10)
ax.text(5,4.85,'Different original dense realizations',ha='center',fontsize=11)
save(fig,'05_shared_completion','Distinct dense source groups with one common profinite completion.')

fig, ax=canvas(height=3.9)
ax.text(3,4.8,'Even block: defeat an output',ha='center',fontsize=10)
ax.text(7.45,4.8,'Odd block: preserve a free bit',ha='center',fontsize=10)
for j,y in enumerate([3.95,2.85,1.75,.65]):
    ax.text(.05,y,rf'$j={j}$',ha='left',va='center',fontsize=11)
    box(ax,3,y,3.65,.75,rf'$1-B_{j}(2\langle {j},k\rangle)$',12)
    box(ax,7.45,y,3.65,.75,rf'$C({j}),\ C({j}),\ C({j}),\ldots$',12)
save(fig,'06_repeated_diagonal','Infinite repeated disagreements and repeated free bits in the escape construction.')

fig, ax=plt.subplots(figsize=(7,3.1))
xs=list(range(1,31))
ys=[]
for n in xs:
    r=1
    for p in prime_divisors(n):r*=p
    ys.append(r)
ax.bar(xs,ys,width=.7)
ax.set_xlabel(r'multiplier $m$')
ax.set_ylabel(r'$|G_A/mG_A|=\operatorname{rad}(m)$')
ax.set_xticks([1,5,10,15,20,25,30])
ax.set_yticks([0,5,10,15,20,25,30])
ax.set_xlim(.25,30.75)
ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
fig.tight_layout()
save(fig,'07_squarefree_quotients','The exact radical function for multipliers one through thirty.')

fig, ax=canvas(height=4.7)
positions={
 'ambient':(2.1,4.4),'pure':(7.4,4.4),
 'normal':(2.1,3.0),'root':(7.4,3.0),
 'class':(2.1,1.6),'quot':(7.4,1.6),
 'degree':(1.5,.2),'grammar':(4.95,.2),'obs':(8.5,.2)}
labels={'ambient':'Ambient quotient','pure':'Pure preimages','normal':'Normal forms / cocycle',
 'root':'Root criterion','class':'Tail signature / classification','quot':'All finite quotients',
 'degree':'Exact oracle cost','grammar':'Grammar escape','obs':'No decoder'}
for key,(x,y) in positions.items():
    w=3.3 if key in ['ambient','pure','normal','root','class','quot'] else 2.75
    box(ax,x,y,w,.63,labels[key],9.6)
for a,b in [('ambient','pure'),('ambient','normal'),('pure','root'),('normal','root'),('root','quot'),('root','class'),('class','degree'),('class','grammar'),('quot','obs'),('class','obs')]:
    x1,y1=positions[a];x2,y2=positions[b]
    if y1==y2:
        sign=1 if x2>x1 else -1
        arrow(ax,x1+sign*1.7,y1,x2-sign*1.7,y2)
    else:
        arrow(ax,x1,y1-.34,x2,y2+.34)
ax.set_ylim(-.35,5)
save(fig,'08_proof_dependencies','The main dependency structure of the printed proofs.')

(OUT/'figure_index.json').write_text(json.dumps(index,indent=2)+'\n')
print(f'Created {len(index)} figures in PDF, SVG, and PNG formats.')
