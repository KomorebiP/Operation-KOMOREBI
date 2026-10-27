#!/usr/bin/env python3
"""Scientific figures for Catalan Series 08.

Exact rational decisions live in the computation evidence. Decimal coordinates
are display aids. Schematic figures are explicitly labelled as such.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import argparse
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'visual/figures'
OUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only', nargs='+', help='Regenerate only these figure stems, while checking the complete provenance inventory.')
SELECTED = set(parser.parse_args().only or [])
spec = importlib.util.spec_from_file_location('packet', ROOT / 'computations/catalan_packet_audit.py')
packet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packet)
DATA = json.loads((ROOT / 'evidence/computation/independent_final/diagnostic_data.json').read_text())
RUN = json.loads((ROOT / 'evidence/computation/historical_default/results.json').read_text())
mp.mp.dps = 120
G = mp.catalan
INK, TEAL, COPPER, SOFT, GRAY = '#243138', '#21676B', '#A45C36', '#E9F0EF', '#627078'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 12,
    'axes.labelsize': 13, 'axes.titlesize': 16, 'axes.titleweight': 'bold',
    'text.color': INK, 'axes.labelcolor': INK, 'axes.edgecolor': GRAY,
    'xtick.color': INK, 'ytick.color': INK,
    'axes.spines.top': False, 'axes.spines.right': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
})
PROVENANCE = []

def finish(fig, name, provenance, title=None):
    if SELECTED and name not in SELECTED:
        plt.close(fig)
        if not (OUT / f'{name}.pdf').is_file() or not (OUT / f'{name}.png').is_file():
            raise FileNotFoundError(f'Unselected figure is missing: {name}')
        PROVENANCE.append({'figure': f'{name}.pdf', 'provenance': provenance})
        return
    if title:
        fig.suptitle(title, x=.07, y=.98, ha='left', fontsize=17, color=INK, weight='bold')
    fig.savefig(OUT / f'{name}.pdf', bbox_inches='tight', pad_inches=.15,
                metadata={'Creator': 'Operation Komorebi scientific figure script', 'CreationDate': None})
    fig.savefig(OUT / f'{name}.png', dpi=180, bbox_inches='tight', pad_inches=.15)
    plt.close(fig)
    PROVENANCE.append({'figure': f'{name}.pdf', 'provenance': provenance})

def canvas():
    fig, ax = plt.subplots(figsize=(9.2, 6.1))
    ax.set(xlim=(0, 10), ylim=(0, 7))
    ax.axis('off')
    return fig, ax

def box(ax, x, y, w, h, text, color=SOFT, fs=15):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.12,rounding_size=.12',
                              facecolor=color,edgecolor='none'))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,linespacing=1.45)

def arrow(ax, a, b, color=TEAL):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=16,lw=1.7,color=color))

def floatq(q):
    q = Fraction(q)
    return float(mp.mpf(q.numerator) / q.denominator)

def logq(q):
    q = Fraction(q)
    return float(mp.log10(abs(mp.mpf(q.numerator) / q.denominator)))

# 01. Constant identity and numeric location.
fig, ax = plt.subplots(figsize=(9.2, 6.1))
ax.set(xlim=(0,1.05),ylim=(0,1)); ax.axis('off')
ax.hlines(.33,0,1,color=GRAY,lw=1.5)
for x in [0,.5,1]:
    ax.vlines(x,.30,.36,color=GRAY); ax.text(x,.25,str(x),ha='center')
ax.plot(float(G),.33,'o',color=TEAL,markersize=14)
ax.text(.07,.82,r'$G=\beta(2)=\sum_{k=0}^{\infty}\frac{(-1)^k}{(2k+1)^2}$',fontsize=25)
ax.text(float(G),.45,'G ≈ 0.915965594177219',ha='right',fontsize=17,color=TEAL)
ax.text(.07,.64,'A defined real number. This edition does not resolve its rationality.',fontsize=15)
finish(fig,'01_constant','Defining convergent series. Numeric marker uses mpmath at 120 digits as display only.')

# 02. Exact finite alternating partial sums.
N=14; sums=[]; s=Fraction(0)
for k in range(N):
    s += Fraction((-1)**k,(2*k+1)**2); sums.append(s)
fig, ax = plt.subplots(figsize=(9.2,6.1))
x=np.arange(1,N+1)
ax.plot(x,[float(v) for v in sums],color=GRAY,lw=1.2)
ax.scatter(x,[float(v) for v in sums],c=[TEAL if k%2 else COPPER for k in range(N)],s=55,zorder=4)
ax.axhline(float(G),color=TEAL,lw=1.3,linestyle='--',label='G (decimal display)')
ax.set(xlabel='N terms',ylabel=r'$s_N$',ylim=(.88,1.015),xticks=[1,2,4,6,8,10,12,14])
ax.text(5.5,.987,r'$s_{2r}<G<s_{2r+1}$',fontsize=19)
ax.text(5.5,.970,r'$|G-s_N|\leq (2N+1)^{-2}$',fontsize=18)
ax.grid(axis='y',alpha=.17); ax.legend(loc='lower right',frameon=False)
finish(fig,'02_alternating_series','Exact Fraction partial sums N=1..14. Alternating-series theorem supplies the displayed bound.')

# 03. Single integral, display clipped away from endpoint logarithmic singularity.
fig, ax = plt.subplots(figsize=(9.2,6.1))
x=np.linspace(.0007,1,1100); y=-np.log(x)/(1+x*x)
ax.plot(x,y,color=TEAL,lw=2.2); ax.fill_between(x,0,y,color=SOFT)
ax.set(xlabel='x',ylabel=r'$-\log x\,/\,(1+x^2)$',xlim=(0,1),ylim=(0,5.5))
ax.text(.32,3.8,r'$G=\int_0^1\frac{-\log x}{1+x^2}\,dx$',fontsize=24)
ax.text(.32,3.0,'Finite improper integral\nLogarithmic endpoint singularity',fontsize=15,linespacing=1.5)
ax.grid(alpha=.15)
finish(fig,'03_log_integral','Integral obtained by geometric expansion and integration of x^(2k)(-log x). Plot is a floating display, not quadrature evidence.')

# 04. Double integral exact representation, display contour.
fig, ax = plt.subplots(figsize=(9.2,6.1))
x=np.linspace(0,1,160); xx,yy=np.meshgrid(x,x); zz=1/(1+xx*xx*yy*yy)
im=ax.contourf(xx,yy,zz,levels=np.linspace(.5,1,16),cmap='BuGn')
fig.colorbar(im,ax=ax,label=r'$1/(1+x^2y^2)$')
ax.set(xlabel='x',ylabel='y',aspect='equal'); ax.set_title(r'$G=\int_0^1\!\int_0^1\frac{dx\,dy}{1+x^2y^2}$',pad=12)
finish(fig,'04_double_integral','Exact geometric-series representation on the unit square. Contour grid is numeric display only.')

# 05. Neighbouring beta values: no implication across parity.
fig,ax=canvas()
box(ax,.4,3.9,2.6,1.5,r'$\beta(1)=\pi/4$'+'\nKnown evaluation',fs=17)
box(ax,3.65,2.2,2.7,1.65,r'$\beta(2)=G$'+'\nNo proof\nestablished here',color='#D7E9E6',fs=18)
box(ax,7,3.9,2.6,1.5,r'$\beta(3)=\pi^3/32$'+'\nKnown evaluation',fs=17)
ax.text(5,6.3,r'$\beta(s)=\sum_{k\geq0}(-1)^k(2k+1)^{-s}$',ha='center',fontsize=22)
ax.text(5,.8,'Exact identities at neighbouring arguments do not decide β(2).',ha='center',fontsize=14)
finish(fig,'05_beta_family','Definitions and elementary beta(1), beta(3) identities. Diagram shows no claimed implication.')

# 06. Rationality creates a nonzero integer lattice gap.
fig,ax=plt.subplots(figsize=(9.2,6.1));ax.set(xlim=(-2.3,2.3),ylim=(-.6,2.7)); ax.axis('off')
ax.hlines(.6,-2.1,2.1,color=GRAY,lw=1.5)
for k in [-2,-1,0,1,2]:
    ax.plot(k,.6,'o',color=TEAL,ms=10);ax.text(k,.28,str(k),ha='center',fontsize=15)
ax.axvspan(-1,1,ymin=.14,ymax=.38,color=SOFT)
ax.text(0,2.2,r'$G=a/b\quad\Longrightarrow\quad b(AG-B)=aA-bB\in\mathbb{Z}$',ha='center',fontsize=19)
ax.text(0,1.45,r'$0<|AG-B|<1/b$'+'\nwould place a nonzero integer in this gap',ha='center',fontsize=18)
finish(fig,'06_rationality_lattice','Exact elementary rationality contradiction for integer A,B and fixed hypothetical denominator b.')

# 07. Error versus exact denominator of partial sums.
fig,axs=plt.subplots(1,2,figsize=(9.2,6.1)); s=Fraction(0); dens=[]; errors=[]
for k in range(60):
    s += Fraction((-1)**k,(2*k+1)**2); dens.append(s.denominator);errors.append(1/(2*(k+1)+1)**2)
n=np.arange(1,61)
axs[0].plot(n,[math.log10(d) for d in dens],color=COPPER,lw=2); axs[0].set(xlabel='N terms',ylabel=r'$\log_{10} D_N$',title='Reduced denominator')
axs[1].plot(n,np.log10(errors),color=TEAL,lw=2);axs[1].set(xlabel='N terms',ylabel='log₁₀ alternating error bound',title='Slow guaranteed decay')
for ax in axs:ax.grid(alpha=.15)
fig.tight_layout(w_pad=2)
finish(fig,'07_series_denominators','Exact Fraction reduced denominators N<=60. Error curve is the alternating-series bound; no irrationality conclusion is drawn.')

# 08. Rational approximation becomes a linear form after denominator clearing.
fig,ax=canvas()
box(ax,.6,4.3,3.7,1.25,r'$s_N=P_N/D_N$'+'\nReduced rational approximant')
box(ax,5.7,4.3,3.7,1.25,r'$G-s_N$'+'\nReal approximation error')
box(ax,2.25,1.65,5.5,1.5,r'$D_N G-P_N=D_N(G-s_N)$'+'\nThe denominator multiplies the error',color='#D7E9E6',fs=19)
arrow(ax,(2.5,4.1),(4,3.3));arrow(ax,(7.5,4.1),(6,3.3))
ax.text(5,.45,'An error tending to zero is only the beginning.',ha='center',fontsize=15)
finish(fig,'08_error_clearing','Exact denominator-clearing identity. Diagram is explanatory, not a computation.')

# 09. Recurrence structure.
fig,ax=canvas()
box(ax,.35,3,2.4,1.25,r'$x_{n-1}$'+'\nPrevious value',fs=17)
box(ax,3.8,4.65,2.4,1.25,r'$x_n$'+'\nCurrent value',fs=17)
box(ax,7.15,3,2.4,1.25,r'$x_{n+1}$'+'\nNext value',color='#D7E9E6',fs=17)
arrow(ax,(2.9,3.7),(7,3.7));arrow(ax,(6.3,5.1),(7.8,4.4))
ax.text(4.85,3.9,r'$C_n/A_n$',fontsize=17,ha='center');ax.text(7.25,5.5,r'$Q_n/A_n$',fontsize=17,ha='center')
ax.text(5,1.6,r'$A_nx_{n+1}=Q_nx_n+C_nx_{n-1}$',fontsize=25,ha='center')
ax.text(5,.65,'Both u and v obey the same recurrence, from distinct initial data.',ha='center',fontsize=14)
finish(fig,'09_recurrence_structure','Historical exact Zudilin recurrence in computations/catalan_packet_audit.py. A_n,C_n,Q_n are defined in guide prose.')

# 10. Initial exact values.
u,v=packet.zudilin_sequences(60)
fig,ax=canvas();ax.text(.4,6.2,'Two rational sequences',fontsize=22,weight='bold')
rows=[[str(n),str(u[n]),str(v[n]),str(v[n]/u[n])] for n in range(4)]
table=ax.table(cellText=rows,colLabels=['n','uₙ','vₙ','vₙ/uₙ'],loc='center',cellLoc='center',colWidths=[.09,.25,.31,.34]);table.auto_set_font_size(False);table.set_fontsize(15);table.scale(1,3)
for (r,c),cell in table.get_celld().items():
    cell.set_edgecolor('white');cell.set_facecolor(TEAL if r==0 else SOFT if r%2 else 'white')
    if r==0:cell.set_text_props(color='white',weight='bold')
ax.text(5,.45,'Values shown are exact fractions from integer and rational arithmetic.',ha='center',fontsize=14)
finish(fig,'10_initial_sequences','Exact Fraction recurrence evaluation, n=0..3.')

# 11. Observed growth and characteristic roots, display only.
fig,ax=plt.subplots(figsize=(9.2,6.1)); ns=np.arange(1,61)
ax.plot(ns,[logq(u[n])/n for n in ns],color=TEAL,lw=2,label=r'$\log_{10}(u_n)/n$')
lam=(11+5*math.sqrt(5))/2
ax.axhline(math.log10(lam),color=COPPER,ls='--',label=r'$\log_{10}((11+5\sqrt{5})/2)$')
ax.set(xlabel='n',ylabel='growth rate display',ylim=(0,1.2));ax.grid(alpha=.15);ax.legend(frameon=False,loc='lower right')
ax.text(12,.45,r'$A_n\sim320n^6,\quad Q_n\sim3520n^6,\quad C_n\sim320n^6$',fontsize=16)
ax.text(12,.31,r'$\lambda^2-11\lambda-1=0$',fontsize=20)
finish(fig,'11_recurrence_growth','Exact u_n for n<=60 converted to numeric logs. Polynomial leading coefficients and characteristic equation are algebraic facts; curve alone proves no asymptotic theorem.')

# 12. Certified approximant errors; tiny interval uncertainty invisible at scale.
fig,ax=plt.subplots(figsize=(9.2,6.1)); rows=DATA['approximants']
ns=[r['n'] for r in rows]; ys=[r['display_log10_abs_error_lower'] for r in rows]
ax.plot(ns,ys,color=TEAL,lw=2);ax.scatter(ns,ys,c=[TEAL if r['error_sign']>0 else COPPER for r in rows],s=65,zorder=4)
ax.set(xlabel='n',ylabel=r'$\log_{10}|G-v_n/u_n|$',xticks=ns);ax.grid(alpha=.15)
ax.text(.06,.12,'Teal: G exceeds the approximant\nCopper: G is below the approximant',transform=ax.transAxes,fontsize=13)
finish(fig,'12_approximant_error','Certified rational G enclosure and exact recurrence fractions in independent_final/diagnostic_data.json, n=0,1,2,5,10,20,40. Logs are rounded display aids.')

# 13. Determinant nonvanishing and sign.
fig,axs=plt.subplots(1,2,figsize=(9.2,6.1));ns=np.arange(0,41)
w=[u[n+1]*v[n]-u[n]*v[n+1] for n in ns]
axs[0].stem(ns[:13],[1 if x>0 else -1 for x in w[:13]],linefmt=TEAL,markerfmt='o',basefmt=GRAY);axs[0].set(xlabel='n',ylabel='sign of Wₙ',yticks=[-1,1],title='Alternating determinant')
axs[1].plot(ns,[logq(x) for x in w],color=COPPER,lw=2);axs[1].set(xlabel='n',ylabel=r'$\log_{10}|W_n|$',title='Nonzero at every index')
for ax in axs:ax.grid(alpha=.15)
fig.tight_layout(w_pad=2)
finish(fig,'13_wronskian','Exact determinant formula verified through n<=200 in historical rerun and proved algebraically in monograph. Display n<=40.')

# 14. Wronskian derivation chain (compact relation).
fig,ax=canvas()
ax.text(5,6.2,r'$W_n=u_{n+1}v_n-u_nv_{n+1}$',ha='center',fontsize=23)
box(ax,.6,3.8,4,1.35,'Insert the shared recurrence\nThe Qₙ terms cancel',fs=14.5)
box(ax,5.4,3.8,4,1.35,r'$W_n=-(C_n/A_n)W_{n-1}$',fs=19)
arrow(ax,(4.75,4.45),(5.25,4.45))
box(ax,1.25,1,7.5,1.7,r'$W_n=\frac{(-1)^{n+1}p(n+1)}{2(2n+1)^2(2n+2)^2}$'+'\nwith '+r'$p(t)=20t^2-8t+1$',color='#D7E9E6',fs=20)
arrow(ax,(7.3,3.6),(6.3,2.9))
finish(fig,'14_wronskian_identity','Exact algebra: recurrence cancellation, telescoping coefficient ratio, W0=-13/8. No limiting input.')

# 15. Finite scaled coefficients.
ts=packet.t_sequence(8)
fig,ax=canvas();ax.text(5,6.1,r'$T_n=16^n u_n$',ha='center',fontsize=27)
rows=[[str(n),str(ts[n])] for n in range(6)]
table=ax.table(cellText=rows,colLabels=['n','Tₙ'],loc='center',cellLoc='center',colWidths=[.12,.72]);table.auto_set_font_size(False);table.set_fontsize(16);table.scale(1,2.3)
for (r,c),cell in table.get_celld().items():
    cell.set_edgecolor('white');cell.set_facecolor(TEAL if r==0 else SOFT if r%2 else 'white')
    if r==0:cell.set_text_props(color='white')
ax.text(5,.2,'Exact integer divisions were checked through T₁₀₀₀₀ in the default scan.',ha='center',fontsize=13)
finish(fig,'15_scaled_coefficients','Exact initial scaled coefficients. Historical_default scan needs T_n through n=10000 and checks every recurrence division.')

# 16. Pascal dependency.
fig,ax=canvas()
box(ax,.75,4.2,3.35,1.15,r'$S_{n,m}$',fs=25);box(ax,5.8,4.2,3.35,1.15,r'$S_{n+1,m}$',fs=25)
box(ax,3.35,1.9,3.35,1.15,r'$S_{n,m+1}$',color='#D7E9E6',fs=25)
arrow(ax,(2.45,4),(4.35,3.25));arrow(ax,(7.45,4),(5.7,3.25))
ax.text(5,6.4,r'$S_{n,m}=\sum_{i=0}^m\binom{m}{i} T_{n+i}$',ha='center',fontsize=24)
ax.text(5,.5,r'$S_{n,m+1}=S_{n,m}+S_{n+1,m}$',ha='center',fontsize=23)
finish(fig,'16_pascal_transform','Exact Pascal identity by binomial coefficient addition. Computational recurrence uses this identity modulo a power of 2.')

# 17. A concrete small binomial packet.
fig,ax=plt.subplots(figsize=(9.2,6.1));m=4;n=1
weights=[math.comb(m,i) for i in range(m+1)];terms=[weights[i]*ts[n+i] for i in range(m+1)]
ax.bar(range(5),[math.log10(t) for t in terms],color=[TEAL,COPPER,TEAL,COPPER,TEAL],width=.65)
ax.set(xlabel='i in the packet',ylabel=r'$\log_{10}(\binom{4}{i} T_{1+i})$',xticks=range(5));ax.grid(axis='y',alpha=.15)
for i,wgt in enumerate(weights):ax.text(i,math.log10(terms[i])+.18,f'weight {wgt}',ha='center',fontsize=12)
ax.text(.03,.95,r'$S_{1,4}=T_1+4T_2+6T_3+4T_4+T_5$',transform=ax.transAxes,fontsize=19,va='top')
finish(fig,'17_binomial_packet','Exact n=1,m=4 binomial packet terms, displayed on a logarithmic axis.')

# 18. Modular exactness logic.
fig,ax=canvas()
box(ax,.45,4.55,4.15,1.3,r'$r=S\operatorname{mod}\,2^K\ne0$'+'\nFinite residue is nonzero',color='#D7E9E6',fs=18)
box(ax,5.4,4.55,4.15,1.3,r'$r=S\operatorname{mod}\,2^K=0$'+'\nResidue loses the valuation',fs=18)
box(ax,.45,1.85,4.15,1.3,r'$v_2(S)=v_2(r)<K$'+'\nExact valuation',color='#D7E9E6',fs=18)
box(ax,5.4,1.85,4.15,1.3,r'$v_2(S)\geq K$'+'\nOnly a lower bound',fs=18)
arrow(ax,(2.5,4.3),(2.5,3.35));arrow(ax,(7.5,4.3),(7.5,3.35))
ax.text(5,.45,'Default run: K = 128. No zero residues. Maximum valuation = 31.',ha='center',fontsize=15)
finish(fig,'18_modular_exactness','Elementary residue valuation fact. Default run data: K128, unresolved residues0, max31.')

# 19. Bounded heatmap.
grid=np.full((100,401),np.nan)
for row in DATA['binomial_v2_grid']:grid[row['n']-1,:len(row['v2'])]=row['v2']
fig,ax=plt.subplots(figsize=(9.2,6.1)); cmap=plt.get_cmap('viridis').copy();cmap.set_bad('white')
im=ax.imshow(grid,origin='lower',aspect='auto',extent=(-.5,400.5,.5,100.5),interpolation='nearest',cmap=cmap,vmin=2,vmax=20)
fig.colorbar(im,ax=ax,label=r'$v_2(S_{n,m})$',ticks=[2,6,10,14,18,20])
ax.plot([0,400],[0,100],color=COPPER,lw=1.4);ax.set(xlabel='m',ylabel='n',title='20,300 exact direct-sum valuations')
ax.text(250,30,'Outside the\ntested triangle',ha='center',fontsize=14,color=GRAY)
finish(fig,'19_v2_heatmap','Independent exact direct-sum grid 1<=n<=100,0<=m<=4n. All displayed valuation cells are exact.')

# 20. Prefix maxima bounded domain.
fig,ax=plt.subplots(figsize=(9.2,6.1));rows=DATA['binomial_v2_prefix_maxima']
ax.step([r['n_max'] for r in rows],[r['maximum_v2'] for r in rows],where='post',color=TEAL,lw=2)
ax.set(xlabel='N in 1 ≤ n ≤ N, 0 ≤ m ≤ 4n',ylabel='largest exact valuation in this triangle',ylim=(0,23),xlim=(1,100));ax.grid(alpha=.15)
ax.text(6,3,'Small independent domain: N ≤ 100\nLarger default domain: N = 2000 gives maximum 31',fontsize=14)
finish(fig,'20_prefix_maxima','Independent exact prefix maxima n<=100. Large-domain summary from fresh historical-default rerun, n<=2000.')

# 21. Full scan boundary and true evidence scope.
fig,ax=plt.subplots(figsize=(9.2,6.1));ax.fill([0,2000,2000],[0,0,8000],color=SOFT)
ax.plot([0,2000],[0,8000],color=TEAL,lw=2);ax.scatter([1466],[2113],color=COPPER,s=100,zorder=3)
ax.annotate('First maximum 31\n(n,m) = (1466,2113)',(1466,2113),xytext=(350,4400),arrowprops={'arrowstyle':'->','color':COPPER},fontsize=14)
ax.set(xlabel='n',ylabel='m',xlim=(0,2300),ylim=(0,9200));ax.text(1300,7800,r'$m\leq4n$',fontsize=20,color=TEAL)
ax.text(250,650,'8,006,000 finite pairs',fontsize=17,color=TEAL)
finish(fig,'21_scan_domain','Exact default domain 1<=n<=2000,0<=m<=4n. Pair count 2N^2+3N=8006000. First maximum follows default scan order.')

# 22. Exact LCM cost.
fig,ax=plt.subplots(figsize=(9.2,6.1)); vals=[]; ell=1
for k in range(1,301):ell=math.lcm(ell,k);vals.append(math.log(ell))
ax.step(range(1,301),vals,where='post',color=COPPER,lw=2,label=r'$\log\,\operatorname{lcm}(1,\ldots,t)$')
ax.plot([1,300],[1,300],color=TEAL,ls='--',label='reference line t')
ax.set(xlabel='t',ylabel='natural logarithm',title='The denominator has an exponential cost');ax.grid(alpha=.15);ax.legend(frameon=False)
finish(fig,'22_lcm_growth','Exact integer lcm values t<=300 converted to display logarithms. Reference line t is a visual comparator, not a finite-data proof of the PNT asymptotic.')

# 23. Historical cleared content rates.
fig,ax=plt.subplots(figsize=(9.2,6.1));rows=DATA['cleared_gcd_decomposition'];ks=[r['n']+r['m'] for r in rows]
ax.plot(ks,[r['display_log_gcd_over_n_plus_m'] for r in rows],color=COPPER,marker='o',lw=2)
for r in rows:ax.annotate(f"({r['n']},{r['m']})",(r['n']+r['m'],r['display_log_gcd_over_n_plus_m']),xytext=(3,9),textcoords='offset points',fontsize=11)
ax.set(xlabel='n + m',ylabel=r'$\log d_{n,m}/(n+m)$',ylim=(0,.225),title='Five finite common-divisor measurements');ax.grid(alpha=.15)
ax.text(.05,.08,'No asymptotic lower bound follows from five points.',transform=ax.transAxes,fontsize=14)
finish(fig,'23_gcd_rate','Five exact cleared common divisors, fresh diagnostic decomposition. Natural log ratios are rounded display aids.')

# 24. Redundant scaling decomposition.
fig,axs=plt.subplots(1,2,figsize=(9.2,6.1),gridspec_kw={'width_ratios':[1.1,1]});rows=DATA['cleared_gcd_decomposition'];ks=[r['n'] for r in rows]
rlogs=[math.log2(int(r['redundant_scale_Q_over_D'])) for r in rows];glogs=[math.log2(int(r['minimal_pair_gcd'])) for r in rows]
axs[0].bar(np.arange(5),rlogs,color=SOFT,edgecolor=TEAL,label='redundant scale Q/D');axs[0].bar(np.arange(5),glogs,bottom=rlogs,color=COPPER,label='minimal pair gcd')
axs[0].set(xticks=range(5),xticklabels=ks,xlabel='n (five historical pairs)',ylabel='log₂ cleared gcd');axs[0].legend(frameon=False,fontsize=10);axs[0].grid(axis='y',alpha=.15)
axs[1].axis('off');axs[1].text(.05,.84,r'$d_{\rm cleared}=R\,g$',fontsize=23)
axs[1].text(.05,.67,r'$R=Q/D$',fontsize=21)
axs[1].text(.05,.48,'Minimal pair gcds\n8, 4, 8, 64, 8',fontsize=17,linespacing=1.6)
axs[1].text(.05,.18,'The chosen clearing scale\naccounts for most of the\nreported common divisor.',fontsize=13,linespacing=1.5)
fig.tight_layout(w_pad=2)
finish(fig,'24_gcd_decomposition','Exact identity d_cleared=(Q/D)*g_minimal from the five diagnostic pairs. Log2 decomposition is display only.')

# 25. Generic threshold plane, explicitly schematic numeric delta.
fig,ax=plt.subplots(figsize=(9.2,6.1));xs=np.linspace(0,5,250);delta=1.5;boundary=xs-delta
ax.fill_between(xs,np.maximum(boundary,0),5,color=SOFT);ax.plot(xs,boundary,color=COPPER,lw=2)
ax.set(xlim=(0,5),ylim=(0,5),xlabel='clearing rate c',ylabel='content recovery rate h',title='Schematic rate comparison: fixed δ = 1.5')
ax.text(.6,3.6,'δ + h > c\nNormalized error decays',fontsize=19,color=TEAL)
ax.text(3.2,.55,'δ + h < c\nThis rate estimate fails',fontsize=15,color=COPPER)
ax.text(2.35,1.23,'δ + h = c',rotation=39,fontsize=13,color=COPPER);ax.grid(alpha=.15)
finish(fig,'25_threshold_plane','Generic schematic: raw error exp(-delta*n+o(n)), clearance exp(c*n+o(n)), content exp(h*n+o(n)). Numeric delta1.5 is illustrative and not a Catalan theorem.')

# 26. Countermodels for extrapolation.
fig,ax=plt.subplots(figsize=(9.2,6.1));xs=np.arange(1,101);base=np.log1p(xs)/xs
up=base.copy();down=base.copy();up[49:]=base[49]+.008*(xs[49:]-50);down[49:]=base[49]*np.exp(-.05*(xs[49:]-50))
ax.plot(xs,up,color=TEAL,lw=2,label='positive eventual rate');ax.plot(xs,down,color=COPPER,lw=2,label='zero eventual rate')
ax.axvspan(1,50,color=SOFT,alpha=.5);ax.axvline(50,color=GRAY,ls='--');ax.set(xlabel='index',ylabel='schematic normalized log rate',title='Same finite observations, different tails')
ax.text(5,.59,'Shared prefix\nthrough index 50',fontsize=14);ax.legend(frameon=False,loc='upper right');ax.grid(alpha=.15)
finish(fig,'26_finite_countermodels','Synthetic illustrative sequences sharing their first50 values. These curves are not Catalan coefficients or fitted predictions.')

# 27. Sign diagnostic shows need for genuine nonvanishing.
signs=np.full((20,81),np.nan)
for r in DATA['raw_filter_grid']:signs[r['n']-1,r['m']]=r['certified_sign']
fig,ax=plt.subplots(figsize=(9.2,6.1));cmap=ListedColormap([COPPER,TEAL]);cmap.set_bad('white')
im=ax.imshow(signs,origin='lower',aspect='auto',extent=(-.5,80.5,.5,20.5),interpolation='nearest',cmap=cmap,vmin=-1,vmax=1)
cb=fig.colorbar(im,ax=ax,ticks=[-1,1]);cb.ax.set_yticklabels(['negative','positive'])
ax.set(xlabel='m',ylabel='n',title='Certified raw-filter signs in 860 finite pairs')
ax.plot([0,80],[0,20],color=GRAY,lw=1);ax.text(50,4,'Untested\nregion',color=GRAY,ha='center',fontsize=14)
finish(fig,'27_filter_signs','Exact rational enclosure certifies signed F=8(-1)^n sum binom(m,i)16^(n+i)(u_(n+i)G-v_(n+i)) signs on1<=n<=20,0<=m<=4n. Under corrected source normalization F=16^n Jtilde. No arbitrary odd-m sign rule is inferred.')

# 28. Conditional route, three genuine obligations.
fig,ax=canvas()
box(ax,.3,4.2,2.85,1.55,'Integer coefficients\nAₙ, Bₙ ∈ ℤ',fs=17)
box(ax,3.55,4.2,2.85,1.55,'Nonzero form\n0 < |AₙG − Bₙ|',fs=17)
box(ax,6.8,4.2,2.85,1.55,'Vanishing size\n|AₙG − Bₙ| → 0',fs=17)
box(ax,2.5,1.15,5,1.5,'Together these imply\nG is irrational',color='#D7E9E6',fs=23)
for x in [1.7,5,8.2]:arrow(ax,(x,4),(5,2.85))
ax.text(5,.15,'Finite checks help audit the construction. They do not supply the third condition.',ha='center',fontsize=13)
finish(fig,'28_conditional_route','Exact elementary irrationality criterion with all three hypotheses explicit. Diagram states a conditional theorem, not its application to Catalan.')

# 29. Evidence boundaries.
fig,ax=canvas()
box(ax,.4,4.05,4.2,1.7,'Exact identities\nSeries, recurrence and\nWronskian algebra',color='#D7E9E6',fs=18)
box(ax,5.4,4.05,4.2,1.7,'Finite evidence\n8,006,000 valuations\nand five gcd pairs',fs=18)
box(ax,.4,1,4.2,1.7,'External inputs\nVersioned sources and\ncorrected normalization',fs=16)
box(ax,5.4,1,4.2,1.7,'Unresolved step\nUniform error control\nwith nonvanishing',color='#F1E5DB',fs=17)
finish(fig,'29_evidence_boundaries','Project claim classification. Historical finite data are fresh reruns, external sources require the literature ledger, and no irrationality proof is established here.')

# 30. Corrected integral filter and its exact parity argument.
phi=(1+math.sqrt(5))/2
psi_max=phi**-5
fig,axs=plt.subplots(1,2,figsize=(9.2,6.1))
xs=np.linspace(0,psi_max,500)
for ax,power,title in zip(axs,[1,2],['Odd degree\nThe factor changes sign','Even degree\nThe factor is nonnegative']):
    ys=(1-16*xs)**power
    ax.plot(xs,ys,color=COPPER if power==1 else TEAL,lw=2.2)
    ax.axhline(0,color=GRAY,lw=1)
    ax.axvline(1/16,color=GRAY,ls='--',lw=1)
    ax.set(xlabel=r'$\psi$',ylabel=rf'$(1-16\psi)^{{{power}}}$',xlim=(0,psi_max),xticks=[0,1/16,psi_max],xticklabels=['0','1/16','φ⁻⁵'],title=title)
    ax.grid(alpha=.15)
axs[0].fill_between(xs,0,1-16*xs,where=xs>=1/16,color='#F1E5DB')
axs[1].fill_between(xs,0,(1-16*xs)**2,color=SOFT)
fig.suptitle(r'$\widetilde J_{n,m}=\int_{[0,1]^2}\psi^n(1-16\psi)^m\,d\mu$',fontsize=23,y=1.01)
fig.tight_layout(w_pad=2.5)
finish(fig,'30_integral_filter','LC03/LC06 corrected integral identity: dmu=dxdy/[sqrt(x(1-y))*(1-xy)], J0=8G, psi_max=phi^-5>1/16. Numeric plotted coordinates illustrate the exact parity sign argument, with no quadrature claim.')

# 31. Versioned source envelope and the arithmetic cost of historical clearing.
alphas=np.linspace(0,5,700)
first=np.array([1/(16*(1+a))*(a/(1+a))**a if a else 1/16 for a in alphas])
second=psi_max*(16*psi_max-1)**alphas
envelope=np.maximum(first,second)
R=16*phi**5
eta=(math.log(R)+alphas*np.log1p(R)-math.log(16)-np.log(envelope))/(4*(1+alphas)+math.log(R)+alphas*np.log1p(R))
kappa=4*(1+alphas)+math.log(16)+np.log(envelope)
fig,axs=plt.subplots(1,2,figsize=(9.2,6.1))
axs[0].plot(alphas,first,color=TEAL,lw=2,label=r'$[16(1+\alpha)]^{-1}(\alpha/(1+\alpha))^\alpha$')
axs[0].plot(alphas,second,color=COPPER,lw=2,label=r'$\phi^{-5}(16\phi^{-5}-1)^\alpha$')
axs[0].set(xlabel=r'$\alpha=m/n$',ylabel=r'$M(\alpha)$ envelope branches',yscale='log',title='Upper bound on the integral rate')
axs[0].legend(frameon=False,fontsize=11,loc='upper right')
axs[1].plot(alphas,eta,color=TEAL,lw=2)
axs[1].axhline(1,color=GRAY,ls='--',lw=1)
axs[1].set(xlabel=r'$\alpha=m/n$',ylabel='guaranteed denominator exponent',ylim=(0,1.05),title='Below the threshold 1')
axs[1].annotate('Source maximum ≈ 0.62335',(3.31765,.62335),xytext=(.15,.79),arrowprops={'arrowstyle':'->','color':TEAL},fontsize=12)
for ax in axs: ax.grid(alpha=.15)
fig.tight_layout(w_pad=2.7)
finish(fig,'31_source_rate','LC07 Eskandari 2609.26354v1: M(alpha)=max{[16(1+alpha)]^-1*(alpha/(1+alpha))^alpha,phi^-5*(16phi^-5-1)^alpha}. Exponent formula from LC07. Numeric curves alpha in [0,5] are display evaluations of source-dependent asymptotic bounds, not finite arithmetic evidence or new proofs; actual integral decay is not asserted equal to M.')

for entry in PROVENANCE:
    entry['sha256'] = hashlib.sha256((OUT / entry['figure']).read_bytes()).hexdigest()
    entry['png_sha256'] = hashlib.sha256((OUT / entry['figure'].replace('.pdf','.png')).read_bytes()).hexdigest()
(ROOT / 'visual/figure_provenance.json').write_text(json.dumps({
    'project':'Catalan Series 08',
    'rules':'Exact integer/rational decisions are separated from numeric coordinates and schematic models.',
    'input_diagnostic_sha256':hashlib.sha256((ROOT / 'evidence/computation/independent_final/diagnostic_data.json').read_bytes()).hexdigest(),
    'input_default_result_sha256':hashlib.sha256((ROOT / 'evidence/computation/historical_default/results.json').read_bytes()).hexdigest(),
    'input_source_contracts_sha256':hashlib.sha256((ROOT / 'literature/source_contracts.md').read_bytes()).hexdigest(),
    'figure_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'figures':PROVENANCE,
},indent=2)+'\n')
print(f'Recorded {len(PROVENANCE)} scientific figures; regenerated {len(SELECTED) if SELECTED else len(PROVENANCE)}.')
