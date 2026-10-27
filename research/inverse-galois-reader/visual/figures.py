#!/usr/bin/env python3
"""Reproducible vector figures for the inverse Galois reader edition.

All algebraic arrays use exact rational arithmetic. Root coordinates in figure
06 are approximate visual positions only. Diagrams are models of the stated
maps and never stand in for existence proofs. Run --only NAME to rebuild a plate.
"""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import argparse
import hashlib
import json
import math
import platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.colors import LinearSegmentedColormap

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
OUT = BASE / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
INK, TEAL, COPPER, GRAY, SOFT = '#243138', '#21676B', '#A45C36', '#627078', '#E9F0EF'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 16,
    'mathtext.fontset': 'dejavusans', 'axes.edgecolor': GRAY,
    'axes.labelcolor': INK, 'text.color': INK, 'xtick.color': GRAY,
    'ytick.color': GRAY, 'pdf.fonttype': 42, 'ps.fonttype': 42,
    'savefig.facecolor': 'white', 'figure.facecolor': 'white'})
FACTS = {}

def canvas(title, tag='MODEL / exact map labels'):
    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    fig.subplots_adjust(left=.025, right=.975, bottom=.025, top=.955)
    ax.set(xlim=(0, 10), ylim=(0, 6))
    ax.axis('off')
    ax.text(.15, 5.74, title, ha='left', va='top', fontsize=20, weight='bold')
    ax.text(.15, 5.28, tag, ha='left', va='top', fontsize=12.5, color=GRAY)
    return fig, ax

def box(ax, x, y, w, h, label, color=SOFT, fontsize=16, edge=TEAL):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04,rounding_size=.09',
                          linewidth=1.3, edgecolor=edge, facecolor=color)
    ax.add_patch(patch)
    t = ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=fontsize,
                linespacing=1.3)
    # Measure actual rendered text, shrink only if needed. No label may spill.
    ax.figure.canvas.draw()
    max_w = ax.transData.transform((x+w-.10,y))[0]-ax.transData.transform((x+.10,y))[0]
    max_h = ax.transData.transform((x,y+h-.10))[1]-ax.transData.transform((x,y+.10))[1]
    for _ in range(10):
        bb=t.get_window_extent(ax.figure.canvas.get_renderer())
        ratio=min(max_w/max(bb.width,1),max_h/max(bb.height,1))
        if ratio>=1: break
        t.set_fontsize(t.get_fontsize()*min(.97,ratio*.98))
        ax.figure.canvas.draw()
    if t.get_fontsize()<11.5:
        raise ValueError(f'Box label is too small: {label!r}, {t.get_fontsize():.1f}')
    return patch

def arrow(ax, start, end, label=None, color=TEAL, dashed=False, rad=0, label_xy=None):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=17,
        linewidth=1.6, color=color, linestyle='--' if dashed else '-',
        connectionstyle=f'arc3,rad={rad}', shrinkA=4, shrinkB=4))
    if label:
        x,y=label_xy or ((start[0]+end[0])/2,(start[1]+end[1])/2+.16)
        ax.text(x,y,label,ha='center',va='center',fontsize=14,color=color,
                bbox={'facecolor':'white','edgecolor':'none','pad':2})

def note(ax, text, y=.30, color=GRAY, fontsize=14):
    ax.text(5,y,text,ha='center',va='center',fontsize=fontsize,color=color,linespacing=1.35)

def save(fig, name, scope, facts):
    fig.savefig(OUT/f'{name}.pdf', metadata={'CreationDate':None,'ModDate':None,
                   'Title':name,'Author':'Komorebi P.'})
    fig.savefig(OUT/f'{name}.png', dpi=170)
    plt.close(fig)
    FACTS[name]={'scope':scope,'facts':facts}

def mul(a,b): return tuple(a[b[i]] for i in range(len(a)))
S3=[(0,1,2),(1,0,2),(0,2,1),(2,1,0),(1,2,0),(2,0,1)]
LABELS=['e','(12)','(23)','(13)','(123)','(132)']
def avg(G,H):
    mat=[[Fraction(0) for _ in G] for _ in G]
    for j,g in enumerate(G):
        for h in H: mat[G.index(mul(h,g))][j]+=Fraction(1,len(H))
    return mat
def mm(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
EH=avg(S3,S3[:2]); EK=avg(S3,[S3[0],S3[2]])

def validate_exact_input():
    data_path=PROJECT/'computations/exact_examples.json'
    if not data_path.exists():
        raise FileNotFoundError('Verified exact_examples.json is required before figure generation')
    data=json.loads(data_path.read_text())['S3_regular_representation']
    source_basis=[tuple(p) for p in data['basis_permutations_zero_based']]
    order=[source_basis.index(p) for p in S3]
    for label,ours in [('H12_average',EH),('H23_average',EK)]:
        converted=[[Fraction(data[label][i][j]) for j in order] for i in order]
        if converted!=ours:
            raise AssertionError(f'Independent exact matrix disagrees with verified data: {label}')
    product1,product2=mm(EH,EK),mm(EK,EH)
    comm=[[product1[i][j]-product2[i][j] for j in range(6)] for i in range(6)]
    converted=[[Fraction(data['commutator'][i][j]) for j in order] for i in order]
    if comm!=converted: raise AssertionError('Exact commutator disagrees with verified data')
    if [comm[i][0] for i in range(6)] != [Fraction(0),Fraction(0),Fraction(0),Fraction(0),Fraction(1,4),Fraction(-1,4)]:
        raise AssertionError('Displayed commutator column has wrong sign or convention')

def f01():
    fig,ax=canvas('The realization question', 'OPEN / a quantifier over every finite group')
    box(ax,.6,3.35,3.25,1.1,'A finite group\n'+r'$G$')
    box(ax,6.1,3.35,3.25,1.1,r'$L/\mathbb{Q}$'+'\nfinite Galois')
    arrow(ax,(3.9,3.9),(6,3.9),'find',dashed=True)
    ax.text(5,2.70,r'$\mathrm{Gal}(L/\mathbb{Q})\cong G$',ha='center',fontsize=25,color=TEAL)
    box(ax,.6,1.10,2.6,.85,r'$C_2$'+'\n'+r'$\mathbb{Q}(\sqrt{2})$',fontsize=15)
    box(ax,3.70,1.10,2.6,.85,r'$C_3$'+'\n'+r'$x^3+x^2-2x-1$',fontsize=15)
    box(ax,6.80,1.10,2.6,.85,r'$S_3$'+'\n'+r'$x^3-2$',fontsize=15)
    note(ax,'Examples witness particular groups. They do not settle the universal question.')
    save(fig,'01_goal','open conjecture, classical examples',{'global_claim':'unresolved over Q'})

def f02():
    fig,ax=canvas('Subgroups and intermediate fields','SOURCE / finite Galois correspondence')
    fields=[r'$L$',r'$L^H$',r'$K$']; groups=[r'$\{1\}$',r'$H$',r'$G$']
    for i,(f,g) in enumerate(zip(fields,groups)):
        y=4.1-i*1.3
        box(ax,1.0,y,2.45,.72,f,fontsize=22)
        box(ax,6.55,y,2.45,.72,g,fontsize=22)
        arrow(ax,(3.6,y+.36),(6.4,y+.36),'fixed field / stabilizer')
    # vertical inclusions run in opposite directions
    arrow(ax,(2.2,3.65),(2.2,3.9),r'$\subseteq$',label_xy=(1.60,3.77))
    arrow(ax,(2.2,2.35),(2.2,2.6),r'$\subseteq$',label_xy=(1.60,2.47))
    arrow(ax,(7.8,3.9),(7.8,3.65),r'$\subseteq$',label_xy=(8.35,3.77))
    arrow(ax,(7.8,2.6),(7.8,2.35),r'$\subseteq$',label_xy=(8.35,2.47))
    note(ax,r'$[L:L^H]=|H|$',y=.72,fontsize=20,color=TEAL)
    note(ax,r'$[L^H:K]=[G:H]$',y=.27,fontsize=20,color=TEAL)
    save(fig,'02_field_group','source theorem displayed schematically',{'hypothesis':'L/K finite Galois','degree_formulas':['[L:L^H]=|H|','[L^H:K]=[G:H]']})

def f03():
    fig,ax=canvas('A complete quadratic realization','WRITTEN PROOF / Eisenstein at 2 and two conjugates')
    box(ax,.65,3.50,3.20,1.05,r'$f(x)=x^2-2$'+'\n'+r'$\Delta=8$',fontsize=21)
    box(ax,6.15,3.50,3.20,1.05,r'$L=\mathbb{Q}(\sqrt{2})$'+'\n'+r'$[L:\mathbb{Q}]=2$',fontsize=21)
    arrow(ax,(4,4),(6,4),'splitting field')
    for x,label in [(2.25,r'$\sqrt{2}$'),(7.75,r'$-\sqrt{2}$')]:
        ax.add_patch(Circle((x,2.15),.62,facecolor=SOFT,edgecolor=TEAL,lw=1.4))
        ax.text(x,2.15,label,fontsize=25,ha='center',va='center')
    arrow(ax,(3,2.35),(7,2.35),r'$\sigma$',rad=-.20,label_xy=(5,2.95))
    arrow(ax,(7,1.95),(3,1.95),r'$\sigma$',rad=-.20,label_xy=(5,1.40))
    note(ax,r'$\sigma^2=1,\qquad \mathrm{Gal}(L/\mathbb{Q})=\{1,\sigma\}\cong C_2$',fontsize=20,color=TEAL)
    save(fig,'03_quadratic','exact worked construction',{'polynomial':'x^2-2','discriminant':8,'group':'C2'})

def f04():
    fig,ax=canvas('Two independent sign changes','WRITTEN PROOF / the biquadratic field')
    xs=[1.25,3.85]; ys=[2.15,4.25]
    labs=[r'$(+,+)$',r'$(-,+)$',r'$(+,-)$',r'$(-,-)$']
    pts=[(xs[0],ys[1]),(xs[1],ys[1]),(xs[0],ys[0]),(xs[1],ys[0])]
    for p,lab in zip(pts,labs):
        ax.add_patch(Circle(p,.46,facecolor=SOFT,edgecolor=TEAL,lw=1.3));ax.text(*p,lab,ha='center',va='center',fontsize=17)
    for a,b in [(0,1),(2,3)]: arrow(ax,(pts[a][0]+.52,pts[a][1]),(pts[b][0]-.52,pts[b][1]),r'$\sqrt{2}\mapsto-\sqrt{2}$',label_xy=((xs[0]+xs[1])/2,pts[a][1]+.58))
    for a,b in [(0,2),(1,3)]: arrow(ax,(pts[a][0],pts[a][1]-.52),(pts[b][0],pts[b][1]+.52),rad=0)
    ax.text(2.55,.95,r'$\sqrt{3}\mapsto-\sqrt{3}$',ha='center',fontsize=17,color=TEAL)
    box(ax,5.25,3.9,4.0,.85,r'$L=\mathbb{Q}(\sqrt{2},\sqrt{3})$',fontsize=19)
    ax.text(7.25,3.25,r'$\mathrm{Gal}(L/\mathbb{Q})\cong C_2\times C_2$',ha='center',fontsize=19)
    for i,s in enumerate([r'$\mathbb{Q}(\sqrt{2})$',r'$\mathbb{Q}(\sqrt{3})$',r'$\mathbb{Q}(\sqrt{6})$']):
        box(ax,5.85,2.4-i*.65,2.85,.50,s,fontsize=16)
    note(ax,'The three order-two subgroups give exactly three quadratic intermediate fields.')
    save(fig,'04_biquadratic','exact worked construction',{'field':'Q(sqrt2,sqrt3)','degree':4,'quadratic_fields':['sqrt2','sqrt3','sqrt6']})

def f05():
    fig,ax=canvas('A cubic whose three roots form one cycle','WRITTEN PROOF / an irreducible cubic with square discriminant')
    pts=[(2,3.65),(8,3.65),(5,1.65)]
    labs=[r'$\alpha$',r'$\alpha^2-2$',r'$1-\alpha-\alpha^2$']
    for p,lab in zip(pts,labs): box(ax,p[0]-1.35,p[1]-.4,2.7,.8,lab,fontsize=23)
    arrow(ax,(3.5,3.65),(6.5,3.65),r'$\sigma$')
    arrow(ax,(7.7,3.1),(6.0,2.15),r'$\sigma$',label_xy=(7.05,2.35))
    arrow(ax,(4.0,2.15),(2.3,3.1),r'$\sigma$',label_xy=(2.95,2.35))
    ax.text(5,4.65,r'$f(x)=x^3+x^2-2x-1,\qquad\Delta=49$',ha='center',fontsize=22,color=TEAL)
    note(ax,r'$\sigma^3=1,\qquad L=\mathbb{Q}(\alpha),\qquad\mathrm{Gal}(L/\mathbb{Q})\cong C_3$',y=.55,fontsize=19,color=TEAL)
    save(fig,'05_cyclic_cubic','exact algebraic root expressions',{'polynomial':'x^3+x^2-2x-1','discriminant':49,'root_cycle':['alpha','alpha^2-2','1-alpha-alpha^2']})

def f06():
    fig,ax=canvas('The splitting field needs the nonreal roots too','COMPUTATION / approximate positions, exact algebraic labels')
    r=2**(1/3); pts=[(r*math.cos(2*math.pi*k/3),r*math.sin(2*math.pi*k/3)) for k in range(3)]
    # Position plot in a square coordinate region on the left.
    ax.plot([.75,4.9],[2.65,2.65],color=GRAY,lw=.8)
    ax.plot([2.6,2.6],[.75,4.6],color=GRAY,lw=.8)
    for (x,y),lab in zip(pts,[r'$\sqrt[3]{2}$',r'$\zeta_3\sqrt[3]{2}$',r'$\zeta_3^2\sqrt[3]{2}$']):
        px,py=2.6+x*1.28,2.65+y*1.28
        ax.plot(px,py,'o',ms=10,color=TEAL)
        ax.text(px+.10,py+.22,lab,fontsize=18,ha='left')
    ax.text(4.7,2.40,'Re',fontsize=13,color=GRAY);ax.text(2.72,4.55,'Im',fontsize=13,color=GRAY)
    box(ax,5.45,3.8,4.1,.90,r'$L=\mathbb{Q}(\sqrt[3]{2},\zeta_3)$',fontsize=19)
    box(ax,5.45,2.55,4.1,.85,r'$[L:\mathbb{Q}]=6$',fontsize=23)
    ax.text(7.5,1.85,r'$\Delta(x^3-2)=-108$',ha='center',fontsize=20)
    ax.text(7.5,1.05,r'$\mathrm{Gal}(L/\mathbb{Q})\cong S_3$',ha='center',fontsize=21,color=TEAL)
    note(ax,'The root plot illustrates the field. Irreducibility and discriminant certify the group.',fontsize=13.5)
    save(fig,'06_s3_roots','numerical positions only, exact polynomial/discriminant/group proof separate',{'polynomial':'x^3-2','discriminant':-108,'group':'S3','coordinates':'binary64 approximation; not group evidence'})

def f07():
    fig,ax=canvas('Finite factors reveal permutations','SOURCE + EXACT COMPUTATION / unramified primes for x⁴ − x − 1')
    box(ax,.55,3.7,4.1,1.0,'Modulo 2\n'+r'$x^4+x+1$'+'  irreducible',fontsize=18)
    box(ax,5.35,3.7,4.1,1.0,'Modulo 7\n'+r'$(x-3)(x^3+3x^2+2x-2)$',fontsize=16)
    arrow(ax,(2.6,3.6),(2.6,2.9)); arrow(ax,(7.4,3.6),(7.4,2.9))
    box(ax,.75,2.0,3.7,.85,'Cycle type 4\na four-cycle',fontsize=20)
    box(ax,5.55,2.0,3.7,.85,'Cycle type 3 + 1\na three-cycle',fontsize=20)
    arrow(ax,(4.55,2.4),(4.9,1.40),rad=.1)
    arrow(ax,(5.45,2.4),(5.1,1.40),rad=-.1)
    ax.text(5,.90,r'$\mathrm{Gal}(f/\mathbb{Q})=S_4$',ha='center',fontsize=25,color=TEAL)
    note(ax,r'$\Delta=-283$'+'; both primes are unramified. Finite factorization is not a universal realization.',y=.25,fontsize=13.5)
    save(fig,'07_factor_cycle','exact factors plus source Frobenius cycle theorem',{'polynomial':'x^4-x-1','discriminant':-283,'mod2':'x^4+x+1 irreducible','mod7':'(x-3)(x^3+3x^2+2x-2)','group':'S4'})

def f08():
    fig,ax=canvas('Every group can act on independent variables','WRITTEN PROOF / faithful permutation action')
    pairs=[('e','(12)'),('(23)','(123)'),('(13)','(132)')]
    for i,(a,b) in enumerate(pairs):
        y=4.15-i*1.1
        box(ax,1.25,y,2.35,.7,r'$x_{'+a+r'}$',fontsize=22)
        box(ax,6.4,y,2.35,.7,r'$x_{'+b+r'}$',fontsize=22)
        ax.add_patch(FancyArrowPatch((3.75,y+.35),(6.25,y+.35),arrowstyle='<->',mutation_scale=17,linewidth=1.6,color=TEAL))
        ax.text(5,y+.68,r'$(12)$',ha='center',fontsize=14,color=TEAL)
    note(ax,r'$h\cdot x_g=x_{hg},\qquad F=\mathbb{Q}(x_g:g\in G)$',y=.6,fontsize=21,color=TEAL)
    save(fig,'08_generic_variables','exact S3 left permutation action as generic construction illustration',{'action':'h.x_g=x_hg','S3_transposition_pairs':pairs})

def f09():
    fig,ax=canvas('The invariant field is the base produced by the action','SOURCE / Artin fixed-field theorem')
    box(ax,1.0,3.9,8.0,.85,r'$F=\mathbb{Q}(x_g:g\in G)$',fontsize=24)
    arrow(ax,(5,3.75),(5,3.05),'fixed field')
    box(ax,1.0,2.1,8.0,.85,r'$K=F^G,\qquad\mathrm{Gal}(F/K)\cong G$',fontsize=24)
    box(ax,1.0,.8,3.45,.8,'Correct realization\nover the invariant base',fontsize=16)
    box(ax,5.55,.8,3.45,.8,'The base is not yet\n'+r'$\mathbb{Q}$',fontsize=16,edge=COPPER)
    note(ax,r'$\mathrm{trdeg}_{\mathbb{Q}}K=|G|$'+'  because F/K is finite.',y=.2,fontsize=14)
    save(fig,'09_invariant_base','source theorem with arithmetic boundary',{'F':'Q(x_g:g in G)','K':'F^G','Gal(F/K)':'G','trdeg_K': '|G|','does_not_prove':'G over Q'})

def f10():
    fig,ax=canvas('Changing the base is the missing arithmetic step','OPEN / rationality is one sufficient route, not a necessary condition')
    box(ax,.50,3.65,3.1,.9,r'$F/F^G$'+'\nknown G-extension',fontsize=19)
    box(ax,6.4,3.65,3.1,.9,r'$L/\mathbb{Q}$'+'\nwanted number field',fontsize=19,edge=COPPER)
    arrow(ax,(3.8,4.1),(6.2,4.1),'descent / specialization',dashed=True,color=COPPER)
    box(ax,1.05,1.7,3.65,1.05,'A rational invariant base\ncan support specialization',fontsize=17)
    box(ax,5.30,1.7,3.65,1.05,'A regular realization\nover '+r'$\mathbb{Q}(t)$'+' also suffices',fontsize=17)
    note(ax,'Failure of one rationality route does not refute inverse Galois.',y=.55,fontsize=18,color=TEAL)
    save(fig,'10_base_descent','boundary and sufficient routes, not equivalences',{'Noether_rationality':'sufficient route, not necessary','regular_Qt':'sufficient via Hilbert'})

def f11():
    fig,ax=canvas('An average turns orbits into invariant coordinates','WRITTEN PROOF / left regular action on Q[S₃]')
    pairs=[(0,1),(2,4),(3,5)]
    for i,(a,b) in enumerate(pairs):
        y=4.2-i*1.2
        box(ax,.6,y,3.25,.73,r'$\delta_{'+LABELS[a]+r'},\ \delta_{'+LABELS[b]+r'}$',fontsize=20)
        arrow(ax,(4,y+.36),(5.6,y+.36),r'$E_H$')
        box(ax,5.7,y,3.7,.73,r'$\frac{\delta_{'+LABELS[a]+r'}+\delta_{'+LABELS[b]+r'}}{2}$',fontsize=22)
    note(ax,r'$H=\langle(12)\rangle,\quad E_H^2=E_H,\quad\mathrm{rank}(E_H)=6/2=3$',y=.6,fontsize=20,color=TEAL)
    save(fig,'11_subgroup_projector','exact left H-orbits and average',{'orbits':[[LABELS[j] for j in p] for p in pairs],'rank':3,'idempotent':True})

def matrix_panel(fig,ax,data,x,y,w,h,title,vmin=0,vmax=.5,cmap=None):
    # Native vector patches maintain exact values and sharp edges.
    n=len(data); cellw=w/n; cellh=h/n
    cmap=cmap or LinearSegmentedColormap.from_list('teal',['#ffffff',TEAL])
    for i in range(n):
        for j in range(n):
            v=float(data[i][j]); rgba=cmap((v-vmin)/(vmax-vmin))
            ax.add_patch(Rectangle((x+j*cellw,y+(n-i-1)*cellh),cellw,cellh,
                 facecolor=rgba,edgecolor='#D5DFDD',lw=.65))
            label='' if v==0 else (r'$\frac{1}{2}$' if v==.5 else str(data[i][j]))
            if label: ax.text(x+(j+.5)*cellw,y+(n-i-.5)*cellh,label,ha='center',va='center',fontsize=15,color='white' if v>.25 else INK)
    ax.text(x+w/2,y+h+.25,title,fontsize=21,ha='center',color=TEAL)
    for j,l in enumerate(LABELS): ax.text(x+(j+.5)*cellw,y-.17,l,ha='center',va='top',fontsize=13,rotation=45)
    for i,l in enumerate(LABELS): ax.text(x-.13,y+(n-i-.5)*cellh,l,ha='right',va='center',fontsize=13)

def f12():
    fig,ax=canvas('Two exact projector matrices','EXACT COMPUTATION / rational entries in the stated S₃ basis')
    matrix_panel(fig,ax,EH,.6,1.80,3.8,2.8,r'$E_{\langle(12)\rangle}$')
    matrix_panel(fig,ax,EK,5.7,1.80,3.8,2.8,r'$E_{\langle(23)\rangle}$')
    ax.text(5,.82,r'$(E_HE_K-E_KE_H)\delta_e=\frac{\delta_{(123)}-\delta_{(132)}}{4}$',ha='center',fontsize=21,color=COPPER)
    note(ax,'Nonzero commutator. Both matrices are still self-adjoint idempotents.',y=.25,fontsize=14)
    save(fig,'12_s3_matrix','exact finite rational matrices, written proof independent',{'basis':LABELS,'EH':[[str(v) for v in row] for row in EH],'EK':[[str(v) for v in row] for row in EK],'commutator_delta_e':'(delta_(123)-delta_(132))/4'})

def f13():
    fig,ax=canvas('Faithful group actions may lose group-algebra information','WRITTEN PROOF + EXACT EXAMPLE / standard representation of S₄')
    box(ax,.60,3.75,8.80,.95,r'$V=\{z\in\mathbb{Q}^4:z_1+z_2+z_3+z_4=0\}$',fontsize=21)
    box(ax,.60,2.05,4.10,1.0,r'$H=\langle(1234)\rangle$'+'\n'+r'$E_H|_V=0$',fontsize=21)
    box(ax,5.30,2.05,4.10,1.0,r'$K=\langle(12)\rangle$'+'\n'+r'$E_HE_K=E_KE_H=0$',fontsize=21)
    ax.text(5,1.28,r'$H\not\triangleleft S_4\qquad HK\ne KH$',ha='center',fontsize=25,color=COPPER)
    note(ax,'The action on V is faithful. The induced group-algebra action is not.',y=.48,fontsize=17)
    save(fig,'13_commutation','exact representation counterexample to an overstrong implication',{'representation':'standard faithful S4 on sum-zero Q^4','H':'<1234>','K':'<12>','EH':0,'HK_equals_KH':False,'not_IGP_counterexample':True})

def f14():
    fig,ax=canvas('The subgroup lattice also counts invariant dimensions','WRITTEN PROOF / Q[S₃] with the left regular action')
    nodes=[(5,4.45,r'$S_3$'+'\nrank 1'),(1.3,2.8,r'$\langle(12)\rangle$'+'\nrank 3'),(3.75,2.8,r'$\langle(23)\rangle$'+'\nrank 3'),(6.25,2.8,r'$\langle(13)\rangle$'+'\nrank 3'),(8.7,2.8,r'$A_3$'+'\nrank 2'),(5,1.15,r'$\{1\}$'+'\nrank 6')]
    for x,y,l in nodes: box(ax,x-1.0,y-.40,2.0,.80,l,fontsize=16)
    for i in range(1,5):
        x,y,_=nodes[i];ax.plot([5,x],[4.0,3.25],color=GRAY,lw=1.1);ax.plot([x,5],[2.35,1.6],color=GRAY,lw=1.1)
    note(ax,r'$\dim \mathbb{Q}[S_3]^H=[S_3:H]$'+'  for every subgroup H.',y=.26,fontsize=17,color=TEAL)
    save(fig,'14_coset_lattice','exact full S3 subgroup lattice and regular invariant dimensions',{'ranks':{'S3':1,'three C2':3,'A3':2,'identity':6},'lattice':'subgroup inclusion upward'})

def f15():
    fig,ax=canvas('A projector, a trace and a norm have distinct jobs','WRITTEN PROOF / quadratic conjugation')
    box(ax,.70,3.65,3.55,.9,r'$\alpha=a+b\sqrt{2}$',fontsize=23)
    box(ax,5.75,3.65,3.55,.9,r'$\sigma(\alpha)=a-b\sqrt{2}$',fontsize=23)
    arrow(ax,(4.45,4.1),(5.55,4.1),r'$\sigma$')
    for y,label in [(2.6,r'$E_{C_2}(\alpha)=\frac{\alpha+\sigma(\alpha)}{2}=a$'),(1.6,r'$\mathrm{Tr}_{L/\mathbb{Q}}(\alpha)=2a$'),(.60,r'$N_{L/\mathbb{Q}}(\alpha)=a^2-2b^2$')]:
        box(ax,1.1,y,7.8,.7,label,fontsize=22)
    save(fig,'15_trace_norm','exact identities, trace linear and norm multiplicative',{'average':'a','trace':'2a','norm':'a^2-2b^2','a_b_domain':'Q'})

def f16():
    fig,ax=canvas('A regular family can specialize to a number field','SOURCE / Hilbert irreducibility with the regularity hypothesis')
    box(ax,.60,3.65,4.05,1.05,r'$F/\mathbb{Q}(t)$'+'\nfinite Galois, group G',fontsize=21)
    box(ax,5.35,3.65,4.05,1.05,r'$F\cap\overline{\mathbb{Q}}=\mathbb{Q}$'+'\nregularity',fontsize=21)
    arrow(ax,(2.6,3.5),(5,2.2),'good rational parameter',label_xy=(3.0,2.60))
    arrow(ax,(7.4,3.5),(5,2.2),rad=-.12)
    box(ax,2.25,.85,5.5,1.2,r'$L/\mathbb{Q}\ \mathrm{finite\ Galois}$'+'\n'+r'$\mathrm{Gal}(L/\mathbb{Q})\cong G$',fontsize=23)
    note(ax,'The implication needs a regular family as input. Constructing it for every G remains open.',y=.27,fontsize=13.5)
    save(fig,'16_regular_specialization','external sufficient implication with hypotheses',{'input':'finite regular G-Galois extension of Q(t)','output':'G over Q by Hilbert irreducibility','universal_input':'not constructed'})

def f17():
    fig,ax=canvas('A specialization may change the group','EXACT TOY / x³ − t is not a regular splitting-field family over Q')
    for x,t,poly,group in [(.55,'0',r'$x^3$', 'multiple roots'),(3.7,'1',r'$(x-1)(x^2+x+1)$',r'$C_2$'),(6.85,'2',r'$x^3-2$',r'$S_3$')]:
        box(ax,x,3.65,2.6,.78,r'$t='+t+r'$',fontsize=23)
        box(ax,x,2.25,2.6,.98,poly+'\n'+group,fontsize=17)
        arrow(ax,(x+1.3,3.5),(x+1.3,3.33))
    box(ax,1.1,.75,7.8,.92,r'$\zeta_3\in F\cap\overline{\mathbb{Q}}$'+'\nnontrivial constants obstruct regularity',fontsize=21,edge=COPPER)
    note(ax,'Group changes in this toy do not supply the regular input in the previous figure.',y=.20,fontsize=14)
    save(fig,'17_parameter_bad','finite specialization examples and correct constant-field obstruction',{'family':'x^3-t','t0':'multiple roots','t1':'C2','t2':'S3','generic':'S3, nonregular because zeta3 constant'})

def f18():
    fig,ax=canvas('An embedding problem asks for a compatible lift','MODEL / the domain and surjectivity requirements matter')
    box(ax,.9,3.8,2.6,.80,r'$\Pi$',fontsize=27)
    box(ax,6.5,3.8,2.6,.80,r'$E$',fontsize=27)
    box(ax,6.5,1.7,2.6,.80,r'$G$',fontsize=27)
    arrow(ax,(3.7,4.2),(6.3,4.2),r'$\beta$',dashed=True)
    arrow(ax,(7.8,3.6),(7.8,2.7),r'$\pi$',label_xy=(8.25,3.15))
    arrow(ax,(3.3,3.6),(6.25,2.35),r'$\alpha$',label_xy=(4.3,2.55))
    ax.text(2.5,1.9,r'$\pi\beta=\alpha$',fontsize=23,ha='center',color=TEAL)
    note(ax,'Weak solution: a continuous lift. Proper solution: the lift is surjective.',y=.80,fontsize=17)
    note(ax,'Finite toy: Π=C₂, E=C₄, G=C₂, α=id has no lift through parity.',y=.25,fontsize=14,color=COPPER)
    save(fig,'18_embedding_problem','abstract embedding diagram and finite toy, not absolute Galois counterexample',{'equation':'pi beta=alpha','weak':'continuous homomorphism lift','proper':'surjective lift','finite_no_lift':'C2 identity through C4 parity'})

def f19():
    fig,ax=canvas('A split weak lift can miss half the target','EXACT FINITE TOY / E=C₂×C₂, Π=G=C₂')
    pts={(0,0):(3.4,3.7),(0,1):(6.6,3.7),(1,0):(3.4,1.7),(1,1):(6.6,1.7)}
    for p,xy in pts.items():
        face=SOFT if p[0]==0 else '#F8EDE6';edge=TEAL if p[0]==0 else COPPER
        ax.add_patch(Circle(xy,.55,facecolor=face,edgecolor=edge,lw=2))
        ax.text(*xy,f'({p[0]},{p[1]})',ha='center',va='center',fontsize=22)
    ax.plot([3.95,6.05],[3.7,3.7],color=TEAL,lw=3)
    ax.plot([3.95,6.05],[1.7,1.7],color=GRAY,lw=1)
    ax.text(5,4.55,r'$\beta(g)=(0,g)$',ha='center',fontsize=23,color=TEAL)
    ax.text(1.45,3.7,'image\nof β',ha='center',va='center',fontsize=17,color=TEAL)
    ax.text(8.55,1.7,'outside\nthe image',ha='center',va='center',fontsize=17,color=COPPER)
    note(ax,r'$|\mathrm{im}\,\beta|=2<|E|=4$',y=.70,fontsize=23,color=COPPER)
    note(ax,'This domain cannot surject onto E. The toy is not an absolute Galois impossibility.',y=.18,fontsize=13.5)
    save(fig,'19_weak_proper','finite weak nonproper solution, not arithmetic obstruction',{'Pi':'C2','E':'C2xC2','G':'C2','beta':'g->(0,g)','image_order':2,'E_order':4})

def f20():
    fig,ax=canvas('Separate the operator theorem from field realization','BOUNDARY / a correct reduction still needs its missing witness')
    rows=[('Group and representation','Actions, subgroups, averages','written proofs',TEAL),('Exact finite models','Matrices and compatibility','bounded computations',TEAL),('Arithmetic realization','A field over the chosen base','new witness needed',COPPER)]
    for i,(a,b,c,color) in enumerate(rows):
        y=3.8-i*1.15
        box(ax,.6,y,3.0,.85,a,fontsize=16,edge=color)
        box(ax,3.9,y,3.6,.85,b,fontsize=16,edge=color)
        ax.text(9.0,y+.42,c,ha='center',va='center',fontsize=14,color=color)
    note(ax,'An operator identity is not itself a polynomial, a splitting field, or a proper arithmetic lift.',y=.55,fontsize=15)
    save(fig,'20_boundary','claim classification diagram',{'proved':'operator and finite group statements','open':'universal arithmetic realization'})

def f21():
    fig,ax=canvas('Read each result at its actual scope','STATUS / the guide does not claim a universal realization theorem')
    rows=[('Classical explicit fields','C₂, C₂×C₂, C₃, S₃, S₄','closed examples',TEAL),('Generic invariant base','Every finite G over Fᴳ','source theorem',TEAL),('Projector calculus','Regular and quotient actions','proved / exact',TEAL),('Regular realization for every G','Over Q(t)','open',COPPER),('Inverse Galois over Q','Every finite G','open',COPPER),('Lean certification of this set','No compiled certificate supplied','not claimed',GRAY)]
    for i,(a,b,c,color) in enumerate(rows):
        y=4.50-i*.65
        ax.add_patch(Rectangle((.55,y-.19),8.95,.52,facecolor=SOFT if i<3 else '#FAF6F1',edgecolor='none'))
        ax.text(.73,y+.07,a,fontsize=14.5,ha='left',va='center')
        ax.text(5.40,y+.07,b,fontsize=14.0,ha='center',va='center')
        ax.text(9.22,y+.07,c,fontsize=14.0,ha='right',va='center',color=color)
    note(ax,'Sources, written derivations and finite checks play different evidential roles.',y=.35,fontsize=15)
    save(fig,'21_status_map','calibrated result scope',{'general_IGP':'open','regular_IGP':'open','Lean':'not certified'})

def f22():
    fig,ax=canvas('What supports the conclusions','DEPENDENCY / models illustrate; proofs and hypotheses carry the claim')
    box(ax,.45,3.6,2.8,1.1,'Written algebra\nidentity and proof',fontsize=18)
    box(ax,3.6,3.6,2.8,1.1,'Primary sources\nexact hypotheses',fontsize=18)
    box(ax,6.75,3.6,2.8,1.1,'Finite computation\nexact tested cases',fontsize=18)
    box(ax,1.0,1.35,3.5,1.0,'Validated statements\nwith stated scope',fontsize=19)
    box(ax,5.5,1.35,3.5,1.0,'Unresolved implication\nuniform field existence',fontsize=19,edge=COPPER)
    arrow(ax,(1.85,3.45),(2.75,2.55))
    arrow(ax,(5,3.45),(3.5,2.55))
    arrow(ax,(8.15,3.45),(4.4,2.55),'corroboration only',dashed=True,label_xy=(6.7,2.8))
    note(ax,'No arrow in this diagram supplies a realization for an arbitrary finite group.',y=.55,fontsize=15,color=COPPER)
    save(fig,'22_dependency','evidence dependency and open boundary',{'computation':'bounded support only','open_gap':'uniform arithmetic existence'})

FUNCTIONS=[f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22]
NAMES=['01_goal','02_field_group','03_quadratic','04_biquadratic','05_cyclic_cubic','06_s3_roots','07_factor_cycle','08_generic_variables','09_invariant_base','10_base_descent','11_subgroup_projector','12_s3_matrix','13_commutation','14_coset_lattice','15_trace_norm','16_regular_specialization','17_parameter_bad','18_embedding_problem','19_weak_proper','20_boundary','21_status_map','22_dependency']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='+',choices=NAMES)
    args=parser.parse_args(); old={}
    validate_exact_input()
    provenance=BASE/'figure_provenance.json'
    if provenance.exists(): old=json.loads(provenance.read_text()).get('figures',{})
    for name,fn in zip(NAMES,FUNCTIONS):
        if not args.only or name in args.only: fn()
    source_inputs={}
    for relative in ['computations/exact_examples.json','literature/source_contracts.md']:
        p=PROJECT/relative
        if p.exists(): source_inputs[relative]={'sha256':sha(p),'bytes':p.stat().st_size}
    for name in NAMES:
        if name in FACTS:
            old[name]={**FACTS[name],'assets':{ext:{'path':f'visual/figures/{name}.{ext}','sha256':sha(OUT/f'{name}.{ext}'),'bytes':(OUT/f'{name}.{ext}').stat().st_size} for ext in ['pdf','png']}}
    provenance.write_text(json.dumps({'edition':'1.0','series':'09','author':'Komorebi P.',
        'generator':{'path':'visual/figures.py','sha256':sha(Path(__file__))},
        'environment':{'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__},
        'scope':'Exact formulas and finite arrays; figure06 positions approximate only. Models do not prove field existence.',
        'source_inputs':source_inputs,'figures':old},indent=2,ensure_ascii=False)+'\n')
    print(f'Generated {len(FACTS)} figures; provenance contains {len(old)} plates.')
if __name__=='__main__': main()
