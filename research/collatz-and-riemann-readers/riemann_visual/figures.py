#!/usr/bin/env python3
"""Deterministic figures and bounded controls for the Riemann visual guide.

No off-line zeta zeros are sampled. Chosen diagnostic models are labeled.
Exact arithmetic uses Fraction and integers. Plotting uses binary64.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
from datetime import datetime, timezone
from math import comb, factorial, gcd, log, pi, sqrt, exp
import hashlib
import json
import platform
import sys
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'figures'
OUT.mkdir(exist_ok=True)
INPUT=ROOT/'shared/figures/data.json'
START=datetime.now(timezone.utc).isoformat()
CLOCK=time.perf_counter()
TEAL='#147d92'; GOLD='#b18128'; RED='#b94b4b'; CHAR='#27323a'
GREEN='#40937e'; LIGHT='#ecf4f5'; GREY='#8a969b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,
    'axes.titlesize':15,'axes.labelsize':13,'xtick.labelsize':12,
    'ytick.labelsize':12,'legend.fontsize':12,'lines.linewidth':2.3,
    'axes.spines.top':False,'axes.spines.right':False,
    'axes.edgecolor':GREY,'text.color':CHAR,'axes.labelcolor':CHAR,
    'pdf.fonttype':42,'savefig.facecolor':'white'})
DATA={'convention':'Centered z=rho-1/2. Packet e^(tz²+uz). Gaussian g=(2πt)^(-1/4)e^(-(u-a)²/(4t)).',
      'figures':{},'checks':{},'software':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__}}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canvas(nrows=1,ncols=1,**kw):
    return plt.subplots(nrows,ncols,figsize=(10.1,6.55),layout='constrained',**kw)
def tidy(ax,xlabel=None,ylabel=None):
    ax.grid(True,alpha=.16)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
def save(fig,name,kind,inputs):
    fig.savefig(OUT/(name+'.pdf'),metadata={'Creator':'Komorebi P. Python figures','Title':name})
    fig.savefig(OUT/(name+'.png'),dpi=170)
    DATA['figures'][name]={'kind':kind,'inputs':inputs}
    plt.close(fig)
def diagram():
    fig,ax=canvas();ax.set_xlim(0,10);ax.set_ylim(0,6.3);ax.axis('off');return fig,ax
def box(ax,x,y,w,h,text,face=LIGHT,edge=TEAL,size=14):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08,rounding_size=0.08',
        facecolor=face,edgecolor=edge,linewidth=1.5))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,linespacing=1.5)
def arrow(ax,a,b,color=GREY):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=18,color=color,linewidth=1.6))
def banner(ax,text): ax.text(.5,.97,text,transform=ax.transAxes,ha='center',va='top',fontsize=13,color=RED)
def mu(n):
    result=1;p=2
    while p*p<=n:
        if n%p==0:
            n//=p;result=-result
            if n%p==0:return 0
        p+=1
    if n>1:result=-result
    return result
def divisors(q):return [b for b in range(1,q+1) if q%b==0]
def w(k,n):return F(1,n*n)*F(n*n-1,n*n)**k
def delta(q,k,m):return sum((mu(b)*w(k,b*m) for b in divisors(q)),F(0))
def fracstr(v):return str(v)
def bernoulli_even(j):
    # The Akiyama triangular recurrence gives exact rational B_(2j).
    a=[F(0)]*(2*j+1)
    for m in range(2*j+1):
        a[m]=F(1,m+1)
        for n in range(m,0,-1):a[n-1]=n*(a[n-1]-a[n])
    return a[0]

# 01 Centered geometry. All dots are a declared model.
fig,ax=canvas();ax.axvspan(-.5,.5,color=LIGHT)
for x,col,style in [(-.5,GREY,'--'),(.5,GREY,'--'),(0,TEAL,'-')]:ax.axvline(x,color=col,ls=style,lw=2)
ax.scatter([0,0,.22,-.22],[1.0,-1.0,2.2,-2.2],s=110,c=[TEAL,TEAL,RED,RED])
ax.text(.02,2.55,'critical line',color=TEAL,fontsize=14)
ax.text(.23,1.92,'model displacement',color=RED,fontsize=13)
ax.set(xlim=(-.68,.68),ylim=(-3,3),xlabel=r'Centered real part $\Re z=\Re\rho-1/2$',ylabel=r'Imaginary part $\Im z$')
banner(ax,'GEOMETRIC MODEL • dots are not sampled zeta zeros')
tidy(ax);save(fig,'01_centered','schematic geometry',{'strip':[-.5,.5],'points':[[0,1],[0,-1],[.22,2.2],[-.22,-2.2]]})

# 02 Audited cached xi input. No new zeta evaluation is claimed.
cached=json.loads(INPUT.read_text())['riemann']['xi']
y=np.array(cached['t_grid']);xi=np.array([float(v) for v in cached['normalized_values']])
fig,(ax1,ax2)=canvas(2,1,sharex=True)
ax1.plot(y,xi,color=TEAL);ax1.axhline(0,color=GREY,lw=1);tidy(ax1,ylabel=r'$\xi(1/2+iy)/\xi(1/2)$')
ax1.set_title('701 cached critical line samples')
ax2.plot(y,xi*np.exp(np.pi*y/4),color=GOLD);ax2.axhline(0,color=GREY,lw=1)
tidy(ax2,xlabel='Critical line height y',ylabel=r'Value multiplied by $e^{\pi y/4}$')
save(fig,'02_completion','cached numerical evaluation',{'source_sha256':sha(INPUT),'samples':len(y),'height_bounds':[0,35],'source_precision':cached['decimal_precision']})

# 03 Quartet geometry, no heat-phase formula.
fig,ax=canvas();a=.2;gamma=1.5
ax.axvline(0,color=TEAL,lw=2);ax.axhline(0,color=GREY,lw=1)
points=[(a,gamma),(-a,gamma),(a,-gamma),(-a,-gamma)]
labels=[r'$z=\delta+i\gamma$',r'$-\overline{z}=-\delta+i\gamma$',r'$\overline{z}=\delta-i\gamma$',r'$-z=-\delta-i\gamma$']
for (x,h),lab in zip(points,labels):
    ax.scatter(x,h,s=110,color=RED,zorder=4)
    ax.text(x+(.025 if x>0 else -.025),h+.16,lab,ha='left' if x>0 else 'right',fontsize=14)
for p,q in [(points[0],points[1]),(points[0],points[2]),(points[0],points[3])]:
    arrow(ax,p,q,TEAL)
ax.set(xlim=(-.6,.6),ylim=(-2.25,2.4),xlabel=r'$\Re z$',ylabel=r'$\Im z$');tidy(ax)
banner(ax,'HYPOTHETICAL QUARTET • selected δ = 0.2, γ = 1.5')
save(fig,'03_quartet','hypothetical geometry model',{'delta':a,'gamma':gamma,'points':points})

# 04 Exact damping function, independent of any sampled zeros.
h=np.linspace(0,20,501);fig,ax=canvas()
for t,col in zip([.01,.04,.1],[GOLD,TEAL,RED]):ax.semilogy(h,np.exp(-t*h*h),color=col,label=f't = {t:g}')
ax.set_ylim(1e-18,1.6);ax.legend(loc='lower left');tidy(ax,'Ordinate magnitude |γ|',r'Gaussian damping $e^{-t\gamma^2}$')
ax.set_title('Positive heat time suppresses the ordinate tail')
save(fig,'04_damping','exact function illustration in binary64',{'heat_times':[.01,.04,.1],'gamma_bounds':[0,20],'points':501})

# 05 Single-mode amplitude envelope, fixed heat factor omitted.
u=np.linspace(0,40,401);fig,ax=canvas()
for d,col in zip([0,.1,.2],[TEAL,GOLD,RED]):ax.semilogy(u,np.exp(d*u),color=col,label=f'δ = {d:g}')
ax.legend(loc='upper left');tidy(ax,'Translation u',r'Amplitude envelope $e^{\delta u}$')
ax.set_title('Hypothetical single modes • fixed heat multiplier omitted')
save(fig,'05_heat_growth','schematic chosen mode envelopes',{'deltas':[0,.1,.2],'u_bounds':[0,40],'fixed_heat_multiplier':'omitted, nonzero'})

# 06 Laplace domain and hypothetical pole geometry.
fig,ax=canvas();ax.axvspan(0,.8,color=LIGHT,label='holomorphic if packet is bounded')
ax.axvline(0,color=TEAL,lw=2);ax.axvline(.5,color=GOLD,ls='--',lw=2)
for p in points:ax.scatter(*p,color=RED,s=115,zorder=4)
ax.annotate('hypothetical pole\nnonzero residue',xy=(.2,1.5),xytext=(.38,.35),fontsize=14,
    arrowprops={'arrowstyle':'->','color':RED},color=RED)
ax.text(.52,-1.95,'initial equality\nRe w > 1/2',color=GOLD,fontsize=13)
ax.text(.04,-2,'extension from\nboundedness',color=TEAL,fontsize=13)
ax.set(xlim=(-.5,.8),ylim=(-2.2,2.2),xlabel=r'$\Re w$',ylabel=r'$\Im w$');tidy(ax)
ax.set_title('Pole positions are a model, not observed zeta data')
save(fig,'06_laplace','exact analytic domains with hypothetical poles',{'extension_domain':'Re(w)>0','initial_domain':'Re(w)>1/2','model_poles':points})

# 07 Model local energies and their logarithmic rates.
J=np.arange(1,81);fig,(ax1,ax2)=canvas(2,1,sharex=True)
for d,col in [(0,TEAL),(.1,RED)]:
    E=np.exp(2*d*J);ax1.semilogy(J,E,color=col,label=f'energy model, δ = {d:g}')
    ax2.plot(J,np.log1p(E)/J,color=col)
ax1.legend(loc='upper left');tidy(ax1,ylabel='Model energy E_J')
ax2.axhline(.2,color=RED,ls='--',lw=1);ax2.axhline(0,color=GREY,lw=1)
tidy(ax2,'Unit band index J',r'$\log(1+E_J)/J$');ax1.set_title('Chosen profiles • actual packet energies are not measured')
save(fig,'07_energy','schematic energy criterion illustration',{'J_bounds':[1,80],'model':'E_J=exp(2δJ)','deltas':[0,.1]})

# 08 Three channels and constants.
fig,ax=diagram()
box(ax,.25,4.35,9.4,1.35,r'$\Theta_t(u)$  =  pole channel  +  archimedean channel  −  prime channel',size=14)
box(ax,.25,1.8,2.75,1.8,'Pole channel\n'+r'$2e^{t/4}\cosh(u/2)$',face='#f5efe3',edge=GOLD,size=15)
box(ax,3.45,1.8,2.85,1.8,'Archimedean channel\n'+r'$(2\pi)^{-1}\int e^{-tv^2}$'+'\n'+r'$\cos(uv)\,\Psi_\infty(v)\,dv$',size=14)
box(ax,6.75,1.8,2.9,1.8,'Prime channel\n'+r'$\frac{1}{2\sqrt{\pi t}}\sum_{n\geq2}$'+'\n'+r'$\frac{\Lambda(n)}{\sqrt{n}}\,[G_++G_-]$',face='#f6eaea',edge=RED,size=14)
ax.text(5,.65,r'$G_\pm=e^{-(u\mp\log n)^2/(4t)}$',ha='center',fontsize=16)
for x in [1.6,4.85,8.2]:arrow(ax,(x,4.3),(x,3.7))
save(fig,'08_channels','exact formula diagram',{'signs':['+','+','-'],'prime_prefactor':'1/(2sqrt(pi*t))','arch_prefactor':'1/(2pi)'})

# 09 Annihilator action.
fig,ax=diagram();box(ax,3.35,4.4,3.3,1.1,r'$L=1/4-\partial_u^2$',size=21)
box(ax,.3,2.5,3.4,1.25,r'$e^{u/2}$  and  $e^{-u/2}$',face='#f5efe3',edge=GOLD,size=18)
box(ax,6.3,2.5,3.4,1.25,r'$e^{t z^2+uz}$',size=19)
arrow(ax,(4,4.3),(2,3.8));arrow(ax,(6,4.3),(8,3.8))
box(ax,.3,.45,3.4,1.25,'multiplier = 0\nexplicit poles removed',face='#f5efe3',edge=GOLD,size=16)
box(ax,6.3,.45,3.4,1.25,r'$1/4-z^2=\rho(1-\rho)$'+'\nnontrivial zeros retained',size=16)
arrow(ax,(2,2.4),(2,1.8));arrow(ax,(8,2.4),(8,1.8))
save(fig,'09_annihilator','exact operator diagram',{'annihilator':'1/4-d_u²','zero_multiplier':'rho(1-rho)','nonzero_for':'all nontrivial zeros'})

# 10 Gaussian functions and physical norm controls.
x=np.linspace(-12,12,16001);fig,ax=canvas();normerr=[]
for t,col in zip([.25,.5,1],[GOLD,TEAL,RED]):
    g=(2*np.pi*t)**(-.25)*np.exp(-x*x/(4*t));ax.plot(x,g,color=col,label=f't = {t:g}')
    normerr.append(abs(float(np.trapezoid(g*g,x))-1))
t=.5;a=1.25;g0=(2*np.pi*t)**(-.25)*np.exp(-x*x/(4*t));ga=(2*np.pi*t)**(-.25)*np.exp(-(x-a)**2/(4*t))
overlap=float(np.trapezoid(g0*ga,x));target=exp(-a*a/(8*t))
assert max(normerr)<1e-12 and abs(overlap-target)<1e-12
ax.set_xlim(-5,5);ax.legend();tidy(ax,'Physical translation u','Normalized Gaussian amplitude')
ax.set_title('Each Gaussian has squared integral one')
DATA['checks']['gaussian']={'x_bounds':[-12,12],'points':len(x),'heat_times':[.25,.5,1],'norm_errors':normerr,'overlap_shift':a,'overlap_numeric':overlap,'overlap_exact_formula':target,'error':abs(overlap-target)}
save(fig,'10_gaussian','normalized exact functions with numerical norm checks',DATA['checks']['gaussian'])

# 11 Hermite functions by a normalized stable recurrence.
def hermites(x,order):
    rows=[np.pi**(-.25)*np.exp(-x*x/2)]
    if order>0:rows.append(np.sqrt(2)*x*rows[0])
    for n in range(1,order):rows.append(np.sqrt(2/(n+1))*x*rows[n]-np.sqrt(n/(n+1))*rows[n-1])
    return rows
rows=hermites(x,4);gram=np.array([[np.trapezoid(a*b,x) for b in rows] for a in rows]);gramerr=float(np.max(abs(gram-np.eye(5))))
assert gramerr<1e-12
fig,ax=canvas()
for r,(v,col) in enumerate(zip(rows,[TEAL,GOLD,RED,GREEN,CHAR])):ax.plot(x,v,color=col,label=f'r = {r}')
ax.set_xlim(-4.5,4.5);ax.legend(ncols=3,loc='upper left');tidy(ax,'Standard coordinate x','Hermite mode amplitude')
ax.set_title('Five orthonormal modes at t = 1/2, c = 0')
DATA['checks']['hermite']={'orders':[0,1,2,3,4],'x_bounds':[-12,12],'points':len(x),'Gram_matrix':gram.tolist(),'max_Gram_error':gramerr}
save(fig,'11_hermite','exact basis evaluated numerically',DATA['checks']['hermite'])

# 12 Finite Poisson coefficients with independent recurrence control.
lam=6;r=np.arange(25);masses=np.array([exp(-lam)*lam**int(i)/factorial(int(i)) for i in r])
rec=[exp(-lam)]
for i in range(1,25):rec.append(rec[-1]*lam/i)
poissonerr=float(np.max(abs(masses-np.array(rec))));assert poissonerr<1e-15
fig,ax=canvas();ax.bar(r,masses,color=[TEAL if i<=10 else GOLD for i in r],width=.8)
ax.axvline(10.5,color=RED,ls='--');ax.text(11,.15,'discarded tail\nwhen R = 10',color=RED,fontsize=14)
tidy(ax,'Hermite index r',r'Squared coefficient $e^{-6}6^r/r!$');ax.set_title('Declared coherent state example λ = 6')
DATA['checks']['poisson']={'lambda':lam,'r_bounds':[0,24],'masses':masses.tolist(),'recurrence_error':poissonerr,'tail_after_10':float(1-sum(masses[:11])),'tail_after_24':float(1-sum(masses))}
save(fig,'12_poisson','exact coherent identity evaluated numerically',DATA['checks']['poisson'])

# 13 Rate function and aggregate coefficient cost.
q=np.linspace(1.001,6,501);rate=q*np.log(q)-q+1;fig,ax=canvas()
ax.plot(q,rate,color=TEAL,label=r'$I(q\mid1)=q\log q-q+1$');ax.axhline(1,color=RED,ls='--',label='aggregate condition I > 1')
v=4*log(4)-3;ax.scatter([4],[v],s=100,color=GOLD,zorder=4);ax.text(4.12,v,'q = 4\nI ≈ 2.545',fontsize=14,color=GOLD)
ax.legend(loc='upper left');tidy(ax,'Retained mode ratio q','Exponential rate I');ax.set_title('Parameter calculation with α = 1, q > α')
save(fig,'13_truncation','exact rate function illustration',{'alpha':1,'q_bounds':[1.001,6],'q_example':4,'I_example':v,'aggregate_condition':'I>1'})

# 14 Ground channel parameter diagram.
fig,ax=diagram();box(ax,.3,3.75,3.5,1.55,'Zero field\n'+r'$\widetilde{\Theta}_t(u)$',size=21)
box(ax,6.2,3.75,3.5,1.55,'Same zero field\n'+r'$\widetilde{\Theta}_{t+s}(c)$',size=21)
arrow(ax,(3.95,4.5),(6,4.5),TEAL)
ax.text(5,3.2,'Gaussian pairing',ha='center',fontsize=16,color=TEAL)
box(ax,.3,.8,9.4,1.65,r'$\int g_{s,c}(u)\,\widetilde{\Theta}_t(u)\,du=K_s\widetilde{\Theta}_{t+s}(c)$'+'\n'+r'$K_s=2\sqrt{\pi s}(2\pi s)^{-1/4}$',size=19)
ax.text(5,.15,'Heat time advances by s. Translation is evaluated at c.',ha='center',fontsize=14)
save(fig,'14_ground','exact parameter identity diagram',{'s':'positive','t':'positive','new_heat':'t+s','evaluation':'c','coefficient':'2sqrt(pi*s)(2pi*s)^(-1/4)'})

# 15 Classical finite coefficient formula. Decimal precision controls.
PITEXT='3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679'
def ck_values(precision):
    with localcontext() as ctx:
        ctx.prec=precision;p=Decimal(PITEXT);inverses=[]
        for n in range(1,14):
            B=abs(bernoulli_even(n));zet=(Decimal(B.numerator)/Decimal(B.denominator))*(2*p)**(2*n)/(2*Decimal(factorial(2*n)))
            inverses.append(1/zet)
        return [sum(((-1)**j*Decimal(comb(k,j))*inverses[j] for j in range(k+1)),Decimal(0)) for k in range(13)]
c80=ck_values(80);c60=ck_values(60);cerr=max(abs(a-b) for a,b in zip(c80,c60));assert cerr<Decimal('1e-50')
assert bernoulli_even(1)==F(1,6) and bernoulli_even(2)==F(-1,30) and bernoulli_even(3)==F(1,42)
assert abs(float(c80[0])-6/pi**2)<1e-15
fig,ax=canvas();ax.stem(np.arange(13),[float(v) for v in c80],linefmt=TEAL,markerfmt='o',basefmt=GREY)
ax.axhline(0,color=GREY,lw=1);tidy(ax,'Finite index K','Numerically evaluated c_K');ax.set_title('Thirteen finite coefficients • no asymptotic inference')
DATA['checks']['ck']={'K_bounds':[0,12],'formula':'sum_j (-1)^j binom(K,j)/zeta(2j+2)','pi_decimal':PITEXT,'decimal_precisions':[60,80],'max_precision_difference':str(cerr),'values':[str(v) for v in c80],'Bernoulli_benchmarks':['1/6','-1/30','1/42']}
save(fig,'15_ck','finite exact coefficient formula evaluated numerically',DATA['checks']['ck'])

# 16 Q6 geometric square and exact summand bars.
fig,(ax1,ax2)=canvas(1,2,gridspec_kw={'width_ratios':[1,1.2]});ax1.axis('off');ax1.set_xlim(-.4,1.4);ax1.set_ylim(-.4,1.45)
vertices={1:(0,0),2:(1,0),3:(0,1),6:(1,1)}
for p,q0 in [(1,2),(1,3),(2,6),(3,6)]:ax1.plot(*zip(vertices[p],vertices[q0]),color=GREY,lw=2)
for b,(a,h0) in vertices.items():
    ax1.scatter(a,h0,s=230,color=TEAL if mu(b)>0 else RED,zorder=3)
    ax1.text(a,h0+.15,('+' if mu(b)>0 else '−')+f' w({b}m)',ha='center',fontsize=14)
ax1.text(.5,-.27,'2 × 3 binary divisor square',ha='center',fontsize=13)
bs=divisors(6);vals=[mu(b)*w(1,b*5) for b in bs]
ax2.bar([str(b) for b in bs],[float(v) for v in vals],color=[TEAL if v>0 else RED for v in vals]);ax2.axhline(0,color=GREY,lw=1)
tidy(ax2,'Divisor b of Q = 6','Signed weight at K = 1, m = 5');ax2.set_title('Corner sum = 17/675')
assert sum(vals)==F(17,675)
save(fig,'16_cube6','exact divisor indexing and rational example',{'Q':6,'K':1,'m':5,'divisors':bs,'rational_summands':[str(v) for v in vals],'sum':'17/675'})

# 17 Q30 as two squares, third coordinate distinctly visible.
fig,ax=diagram();coord={1:(.7,1.2),2:(3.3,1.2),3:(.7,4.5),6:(3.3,4.5),5:(6.1,1.2),10:(8.7,1.2),15:(6.1,4.5),30:(8.7,4.5)}
for b in [1,2,3,6]:
    arrow(ax,(coord[b][0]+.25,coord[b][1]),(coord[5*b][0]-.25,coord[5*b][1]),'#cbd7db')
for block in [[1,2,3,6],[5,10,15,30]]:
    for i,j in [(0,1),(0,2),(1,3),(2,3)]:ax.plot(*zip(coord[block[i]],coord[block[j]]),color=GREY,lw=2)
for b,(a,h0) in coord.items():
    ax.scatter(a,h0,s=500,color=TEAL if mu(b)>0 else RED,zorder=3)
    ax.text(a,h0+.43,('+' if mu(b)>0 else '−')+f' w({b}m)',ha='center',fontsize=14)
ax.text(2,.3,'without prime 5',ha='center',fontsize=14);ax.text(7.4,.3,'with prime 5',ha='center',fontsize=14)
ax.text(5,6,'Q = 30: eight exact divisor corners',ha='center',fontsize=17)
assert delta(30,1,7)==F(6848,540225)
save(fig,'17_cube30','exact divisor cube indexing',{'Q':30,'divisors':divisors(30),'signs':[mu(b) for b in divisors(30)],'K1_m7':'6848/540225'})

# 18 Exact rational finite rough-base sums.
ms=[m for m in range(1,101) if gcd(m,6)==1];signed=[mu(m)*delta(6,1,m) for m in ms];absolute=[abs(v) for v in signed]
cs=[];ca=[];s=F(0);a0=F(0)
for v,av in zip(signed,absolute):s+=v;a0+=av;cs.append(float(s));ca.append(float(a0));assert abs(s)<=a0
fig,ax=canvas();ax.plot(ms,cs,color=TEAL,label='signed finite partial sum');ax.plot(ms,ca,color=RED,label='finite absolute mass')
ax.axhline(0,color=GREY,lw=1);ax.legend();tidy(ax,'Base cutoff B, m ≤ B, gcd(m,6) = 1','Finite total at K = 1');ax.set_title('Exact finite sums through 100 • neither is the full infinite sum')
DATA['checks']['finite_grouping']={'Q':6,'K':1,'base_bound':100,'bases':ms,'signed_terms':[str(v) for v in signed],'signed_total':str(s),'absolute_total':str(a0),'partial_triangle_checks':len(ms)}
save(fig,'18_signed','exact rational finite example',DATA['checks']['finite_grouping'])

# 19 Exact Möbius support table, including zero coefficients.
rows_support=[[m,mu(m),'zero support' if mu(m)==0 else 'squarefree'] for m in range(1,50) if gcd(m,6)==1]
fig,ax=canvas();ax.axis('off')
tab=ax.table(cellText=rows_support,colLabels=['rough base m','μ(m)','support'],loc='center',cellLoc='center',colWidths=[.24,.24,.4]);tab.auto_set_font_size(False);tab.set_fontsize(13);tab.scale(1,1.55)
for (r0,c),cell in tab.get_celld().items():
    cell.set_edgecolor('white')
    if r0==0:cell.set_facecolor(TEAL);cell.get_text().set_color('white')
    elif rows_support[r0-1][1]==0:cell.set_facecolor('#f4dddd')
    else:cell.set_facecolor('#ecf4f5' if r0%2 else '#f7f9fa')
assert mu(25)==mu(49)==0
save(fig,'19_support','exact finite integer enumeration',{'Q':6,'base_bounds':[1,49],'rows':rows_support})

# 20 Tail curves: numerical evaluation with exact Fraction benchmark controls.
M=30;K=900;mt=np.arange(90,361);kappa=6/pi**2-(pi**4/90)/9
fig,ax=canvas();curve_data={};exact_tail=0
for Q,col in [(6,TEAL),(30,GOLD)]:
    arr=np.array([sum(mu(b)/(b*b)*(1-1/((b*m)**2))**K for b in divisors(Q)) for m in mt]);curve_data[str(Q)]=arr.tolist()
    ax.plot(mt/M,arr,color=col,label=f'Q = {Q}')
    assert float(min(arr))>=kappa-1e-12
    for m in [90,120,180,360]:
        exact=float(delta(Q,K,m)*m*m)
        assert abs(exact-arr[m-90])<3e-12;exact_tail+=1
ax.axhline(kappa,color=RED,ls='--',label=f'κ₃ ≈ {kappa:.3f}');ax.legend();tidy(ax,'Tail position m / M',r'$m^2\Delta_Qw_{M^2}(m)$');ax.set_title('Finite tail checks with M = 30, R = 3')
DATA['checks']['positive_tail']={'M':M,'K':K,'R':3,'m_bounds':[90,360],'Q':[6,30],'kappa_numeric':kappa,'exact_fraction_controls':exact_tail,'values':curve_data}
save(fig,'20_positive_tail','proved inequality with bounded numerical controls',DATA['checks']['positive_tail'])

# 21 Explicit scale model, not actual counts.
MM=np.logspace(2,14,481);dd=np.floor(np.sqrt(np.log(MM)));main=MM/(dd+1);error=2**dd*np.sqrt(MM)
fig,ax=canvas();ax.loglog(MM,main,color=TEAL,label='main scale M / (d + 1)');ax.loglog(MM,error,color=RED,label='error scale 2ᵈ√M')
ax.legend();tidy(ax,'Scale M', 'Scale model, constants omitted');ax.set_title('Chosen d = floor(√log M) • not an exact base count')
save(fig,'21_count','schematic asymptotic scale model',{'M_bounds':[100,1e14],'d':'floor(sqrt(log(M)))','constants':'omitted','count_claim':'not an actual count'})

# 22 Barrier rate model explicitly schematic.
MM=np.logspace(1,8,401);fig,ax=canvas();ax.loglog(MM,MM**-1,color=RED,label='absolute route: M⁻¹ reference');ax.loglog(MM,MM**-1.45,color=TEAL,label='target example: M⁻³ᐟ²⁺⁰·⁰⁵')
ax.fill_between(MM,MM**-1.45,MM**-1,color=LIGHT,alpha=.9);ax.legend();tidy(ax,'Scale M','Rate model with constants omitted');ax.set_title('Schematic powers • no lower bound on signed |c| is asserted')
save(fig,'22_barrier','schematic rate comparison',{'exponents':[-1,-1.45],'epsilon_example':.05,'M_bounds':[10,1e8],'not_claimed':'measured actual majorant or signed coefficients'})

# 23 Dependency map preserves separate interfaces and exact/open markings.
fig,ax=diagram()
box(ax,3.75,4.9,2.5,.9,'RH',size=24)
box(ax,.2,2.9,4.0,1.2,'HEAT INTERFACE\nsubexponential local energy',size=16)
box(ax,5.8,2.9,4.0,1.2,'SEQUENCE INTERFACE\nsigned c_K bound',size=16)
arrow(ax,(4.3,5.0),(2.6,4.2),TEAL);arrow(ax,(5.7,5.0),(7.4,4.2),TEAL)
ax.text(2.7,4.65,'equivalent',ha='center',fontsize=12,color=TEAL);ax.text(7.4,4.65,'equivalent',ha='center',fontsize=12,color=TEAL)
box(ax,.2,.45,4,1.45,'Exact heat formula\nStable Hermite resolution\nEnergy estimate OPEN',size=15)
box(ax,5.8,.45,4,1.45,'Exact prime cubes\nAbsolute route too large\nSigned estimate OPEN',face='#f5efe3',edge=GOLD,size=15)
arrow(ax,(2.2,2.75),(2.2,2.0));arrow(ax,(7.8,2.75),(7.8,2.0))
save(fig,'23_dependencies','exact dependency and open-state diagram',{'equivalences':['RH iff heat energy subexponential','RH iff Baez Duarte bound'],'no_arrow':'no new direct Möbius to prime heat transfer','open':['full energy estimate','signed c_K estimate']})

# 24 Evidence matrix, no universal proof disguised as a check.
fig,ax=canvas();ax.axis('off')
table=[['Exact finite arithmetic','Divisors, μ support, rational cubes','Finite identities only'],['Numerical controls','Gaussian, Hermite, Poisson, c_K','Declared precision and range'],['Recovered numerical data','701 xi samples, height 0 to 35','No global zero claim'],['Chosen diagnostic models','Off line geometry, energy, rates','Illustrations only'],['Manuscript proofs','Heat criteria and corrected barrier','Hypotheses retained'],['Open arithmetic target','Signed rough base bound','Equivalent to RH']]
tab=ax.table(cellText=table,colLabels=['Evidence kind','What it supplies','Boundary'],loc='center',cellLoc='left',colWidths=[.27,.4,.33]);tab.auto_set_font_size(False);tab.set_fontsize(12);tab.scale(1,3.25)
for (r0,c),cell in tab.get_celld().items():
    cell.set_edgecolor('white')
    if r0==0:cell.set_facecolor(TEAL);cell.get_text().set_color('white')
    else:cell.set_facecolor('#ecf4f5' if r0%2 else '#f7f9fa')
save(fig,'24_checks','evidence boundary table',{'rows':table})

# Additional exact independent algebra checks for the two K1 cubes.
cube_checks=0
for Q,A,B in [(6,F(2,3),F(25,27)),(30,F(16,25),F(208,225))]:
    for m in range(1,101):assert delta(Q,1,m)==A/F(m*m)-B/F(m**4);cube_checks+=1
support_checks=0
for n in range(1,201):
    rhs=sum(mu(l) for l in range(1,int(sqrt(n))+1) if n%(l*l)==0)
    assert rhs==mu(n)**2;support_checks+=1
grouping_checks=0
for Q in [6,30]:
    for k in [1,2,3]:
        direct=sum((mu(n)*w(k,n) for n in range(1,201)),F(0))
        grouped=sum((mu(m)*sum((mu(b)*w(k,b*m) for b in divisors(Q) if b*m<=200),F(0)) for m in range(1,201) if gcd(m,Q)==1),F(0))
        assert direct==grouped;grouping_checks+=1
DATA['checks']['exact_algebra']={'K1_cube_identity_instances':cube_checks,'mu_square_support_instances':support_checks,'truncated_grouping_instances':grouping_checks,'grouping_Q':[6,30],'grouping_K':[1,2,3],'n_bound':200,'controls':'finite grouping truncates corners by b*m<=200; not by base cutoff alone'}
OUTDATA=HERE/'data.json';OUTDATA.write_text(json.dumps(DATA,indent=2)+'\n')
runtime=time.perf_counter()-CLOCK
report={'schema_version':1,'claim_id':'Riemann visual guide v1.1 finite figure controls','repository':{'commit':'unavailable: local manuscript workspace','dirty':True},'command':'python conjecture_set/riemann_visual/figures.py','environment':{'software':[{'name':k,'version':v} for k,v in DATA['software'].items()],'hardware':platform.platform()},'mathematics':{'assertion_tested':'Finite exact cube/support/grouping identities and numerical normalization controls for the guide; no RH-level asymptotic assertion is tested.','coefficient_domain':'Python integers and exact Fraction for arithmetic; Decimal 60/80 digits for finite c_K; binary64 plots and quadrature.','conventions':DATA['convention'],'inputs':[{'path':'shared/figures/data.json','sha256':sha(INPUT)},{'path':'riemann_visual/figures.py','sha256':sha(__file__)}],'bounds':{'xi_samples':701,'xi_height':[0,35],'c_K':[0,12],'exact_cube_m':[1,100],'support_n':[1,200],'grouped_n':[1,200],'tail_m':[90,360],'gaussian_grid_points':16001,'Hermite_orders':[0,4],'Poisson_modes':[0,24],'finite_base_cutoff':100},'non_claims':['No sampled off-line zeta zeros.','No bound on asymptotic signed Möbius cancellation.','No fresh Lean replay.','Plots of chosen models are not actual zero or arithmetic data.']},'randomness':{'used':False,'generator':'none','seed':None},'run':{'started_at':START,'runtime_seconds':runtime,'exit_status':0},'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [OUTDATA,*sorted(OUT.glob('*.pdf')),*sorted(OUT.glob('*.png'))]],'checks':[{'name':'exact algebra','result':DATA['checks']['exact_algebra']},{'name':'Gaussian norm and overlap','max_error':max(*normerr,abs(overlap-target))},{'name':'Hermite Gram','max_error':gramerr},{'name':'Poisson recurrence','max_error':poissonerr},{'name':'c_K precision','max_error':str(cerr)},{'name':'positive tail rational controls','instances':exact_tail}],'result':'Finite assertions passed in all declared ranges. Numerical checks passed at the stated tolerances.','residual_risks':['Cached xi data are reused; zeta was not evaluated afresh.','Binary64 plotting is not interval certification.','Finite c_K values cannot decide the asymptotic criterion.','Version 1 manifest records hashes but no machine-enforced resource caps.']}
(HERE/'COMPUTATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
(HERE/'requirements.txt').write_text(f'numpy=={np.__version__}\nmatplotlib=={matplotlib.__version__}\n')
print(json.dumps({'figures':len(DATA['figures']),'seconds':runtime,'exact_checks':DATA['checks']['exact_algebra'],'numerical_Gram_error':gramerr,'output':'conjecture_set/riemann_visual/data.json'},indent=2))
