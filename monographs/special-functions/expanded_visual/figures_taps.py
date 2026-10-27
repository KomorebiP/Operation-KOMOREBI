"""Exact tap, polyphase, reconstruction and streaming plates T01--T16.

Causal convention: x[n]=0 for n<0; OGFs use delay variables z (fine)
and u (coarse). All finite witnesses use Python integers/Fractions.
Frequency curves are explicitly bounded floating-point illustrations.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as Q
import hashlib, json, math, platform, time, os
from datetime import datetime, timezone
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from guide_style import COLORS, INK, MUTED, PALE, save_figure

ROOT = Path(__file__).resolve().parent
START = time.perf_counter()
STARTED_AT = datetime.now(timezone.utc).isoformat()
INPUT_PATHS = [Path(__file__), ROOT/'guide_style.py', ROOT/'chapters_taps.tex',
               ROOT/'source_context'/'PSC_V_convolution_extract.txt']
INPUT_HASHES = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in INPUT_PATHS}
plt.rcParams.update({'font.size':16,'axes.labelsize':15,'axes.titlesize':17,
    'xtick.labelsize':12,'ytick.labelsize':12,'legend.fontsize':13})
CHECKS = []

def check(name, condition, details):
    assert condition, name
    CHECKS.append({'name':name,'status':'PASS','details':details})

def fib(n):
    a,b=0,1;out=[]
    for _ in range(n):out.append(a);a,b=b,a+b
    return out

def conv(h,x,n=None):
    if n is None:n=len(h)+len(x)-1
    return [sum(h[k]*x[j-k] for k in range(len(h)) if 0<=j-k<len(x)) for j in range(n)]

def add(p,q):
    n=max(len(p),len(q));return [(p[i] if i<len(p) else 0)+(q[i] if i<len(q) else 0) for i in range(n)]

def trim(p):
    p=list(p)
    while len(p)>1 and p[-1]==0:p.pop()
    return p

def matmul(a,b):
    return [[trim(add(conv(a[i][0],b[0][j]),conv(a[i][1],b[1][j]))) for j in range(2)] for i in range(2)]

def route(h,M):
    # y[Mm+r] = sum_{s,k} h[Mk+r-s] x[M(m-k)+s].
    a=[]
    for r in range(M):
        row=[]
        for s in range(M):
            p=[0]*(1+(len(h)-1-r+s)//M)
            for k,hk in enumerate(h):
                if (k-r+s)%M==0:
                    q=(k-r+s)//M
                    assert q>=0
                    if q>=len(p):p.extend([0]*(q+1-len(p)))
                    p[q]+=hk
            row.append(trim(p or [0]))
        a.append(row)
    return a

def run_route(h,x,M,n):
    phases=[x[s::M] for s in range(M)]
    a=route(h,M)
    out=[]
    for j in range(n):
        m,r=divmod(j,M)
        out.append(sum(a[r][s][k]*phases[s][m-k] for s in range(M)
                       for k in range(len(a[r][s])) if 0<=m-k<len(phases[s])))
    return out

def poly_label(p):
    terms=[]
    for k,c in enumerate(p):
        if not c:continue
        sign='+' if c>0 else '-';v=abs(c)
        base='' if v==1 and k else str(v)
        base+=('u' if k==1 else ('u^{%d}'%k if k else ''))
        terms.append((sign,base))
    if not terms:return '0'
    return ''.join(('' if i==0 and s=='+' else s)+t for i,(s,t) in enumerate(terms))

def frame(title=None, size=(10,5.0)):
    f=plt.figure(figsize=size)
    if title:f.suptitle(title,fontsize=18,y=0.99)
    return f

def box(ax,xy,w,h,label,color=COLORS[0],fc=PALE,fontsize=17):
    x,y=xy
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.018,rounding_size=0.02',
                    linewidth=1.4,edgecolor=color,facecolor=fc))
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=fontsize,color=INK)

def arrow(ax,a,b,label='',color=COLORS[0],rad=0,textxy=None,fontsize=15):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'-|>','lw':2,'color':color,
                                         'connectionstyle':f'arc3,rad={rad}'})
    if label:
        p=textxy or ((a[0]+b[0])/2,(a[1]+b[1])/2+.05)
        ax.text(*p,label,color=color,ha='center',va='center',fontsize=fontsize,
                bbox={'facecolor':'white','edgecolor':'none','pad':1.5})

def blank(ax):
    # Include the rounded-box padding at both ends of each diagram.
    ax.set_xlim(-.025,1.025);ax.set_ylim(-.02,1.03);ax.axis('off')

def stems(ax,x,y,title,color=COLORS[0],annotate=False):
    ax.vlines(x,0,y,color=color,lw=2)
    ax.scatter(x,y,color=color,s=35,zorder=3)
    ax.axhline(0,color=MUTED,lw=.8)
    ax.set_title(title,pad=12)
    ax.set_xticks(x)
    ax.grid(axis='y')
    ax.margins(x=.055,y=.2)
    if annotate:
        lo=min(y);hi=max(y);d=max(hi-lo,1)*.045
        for xx,yy in zip(x,y):ax.text(xx,yy+d if yy>=0 else yy-d,str(yy),ha='center',
                    va='bottom' if yy>=0 else 'top',fontsize=12)

def save(f,tag):
    save_figure(f,f'T{tag:02d}_taps')

# T01: one impulse response, three delayed samples.
f=frame();a=f.add_subplot(121);stems(a,list(range(3)),[1,2,1],r'Finite taps $h[k]$',annotate=True)
a.set_xlabel('tap delay k');a.set_ylabel('weight');a.set_ylim(-.15,2.7)
b=f.add_subplot(122);blank(b)
for y,s,w in [(.76,r'$x[n]$',1),(.46,r'$x[n-1]$',2),(.16,r'$x[n-2]$',1)]:
    box(b,(.02,y),.27,.13,s);arrow(b,(.30,y+.065),(.75,.53),f'× {w}',textxy=(.47,y+.065))
box(b,(.75,.43),.21,.20,r'$y[n]$',color=COLORS[1]);b.text(.52,.93,'Add the three contributions',ha='center',fontsize=16)
f.tight_layout(w_pad=3);save(f,1)

# T02: integer convolution.
x=fib(12);h=[1,2,1];y=conv(h,x,12)
check('Fibonacci direct convolution first 12',y==[0,1,3,5,8,13,21,34,55,89,144,233],{'input':x,'taps':h,'output':y})
f=frame();axs=f.subplots(2,1)
stems(axs[0],list(range(12)),x,r'Input $F_n$: start with $0,1$',annotate=True)
stems(axs[1],list(range(12)),y,r'Output $F_n+2F_{n-1}+F_{n-2}$',COLORS[1],True)
axs[1].set_xlabel('fine index n');f.tight_layout(h_pad=1.0);save(f,2)

# T03: matrix as visible four channel operations.
P=route(h,2)
check('Two-phase matrix coefficients',P==[[[1,1],[0,2]],[[2],[1,1]]],{'matrix_coefficients':P,'row_order':['even','odd'],'column_order':['even','odd']})
f=frame();ax=f.add_subplot();blank(ax)
for yy,label in [(.67,r'$E(u)$'),(.25,r'$O(u)$')]:box(ax,(.01,yy),.19,.17,label)
for yy,label in [(.67,r'$Y_0(u)$'),(.25,r'$Y_1(u)$')]:box(ax,(.80,yy),.19,.17,label,COLORS[1])
arrow(ax,(.21,.755),(.79,.755),r'$1+u$',textxy=(.50,.82))
arrow(ax,(.21,.335),(.79,.335),r'$1+u$',textxy=(.50,.27))
arrow(ax,(.21,.70),(.79,.40),r'$2$',COLORS[2],textxy=(.38,.54))
arrow(ax,(.21,.40),(.79,.70),r'$2u$',COLORS[1],textxy=(.63,.54))
ax.text(.5,.98,'Same taps, separated by parity',ha='center',va='top',fontsize=18)
ax.text(.5,.08,r'$u$ delays by one pair of fine samples',ha='center',fontsize=16)
save(f,3)

# T04: per-tap wrap assignment, avoids ambiguous delay arrows.
f=frame();axs=f.subplots(1,2)
for ax,r,title in zip(axs,[0,1],[r'Even output $y[2m]$',r'Odd output $y[2m+1]$']):
    blank(ax);ax.set_title(title,pad=12)
    inputs=([r'$E_m$',r'$O_{m-1}$',r'$E_{m-1}$'] if r==0 else [r'$O_m$',r'$E_m$',r'$O_{m-1}$'])
    # Indexed input nodes already contain the coarse delay. Arrow labels
    # therefore show the original tap weights, without a second delay.
    terms=[r'$1$',r'$2$',r'$1$']
    for i,(inp,t) in enumerate(zip(inputs,terms)):
        yy=.72-i*.26;box(ax,(.02,yy),.32,.14,inp)
        arrow(ax,(.36,yy+.07),(.81,.48),t,textxy=(.56,yy+.07))
    box(ax,(.80,.38),.18,.20,r'$sum$',COLORS[1])
    ax.text(.5,.015,'Fine delay k = 0, 1, 2',ha='center',fontsize=15)
f.tight_layout(w_pad=2);save(f,4)

# T05: arbitrary M exact routing; four-phase worked matrix.
h4=[1,2,3,4,5];P4=route(h4,4)
check('Four-phase five-tap matrix',P4==[[[1,5],[0,4],[0,3],[0,2]],[[2],[1,5],[0,4],[0,3]],[[3],[2],[1,5],[0,4]],[[4],[3],[2],[1,5]]],{'taps':h4,'matrix_coefficients':P4})
f=frame();ax=f.add_subplot();blank(ax)
left=.20;bottom=.10;w=.18;hh=.17
for s in range(4):ax.text(left+(s+.5)*w,.90,rf'$X_{s}$',ha='center',fontsize=18)
for r in range(4):
    yy=bottom+(3-r)*hh
    ax.text(.13,yy+hh/2,rf'$Y_{r}$',ha='center',va='center',fontsize=18)
    for s in range(4):
        fc=PALE if s<=r else '#FAEFEA'
        box(ax,(left+s*w,yy),w-.012,hh-.009,'$'+poly_label(P4[r][s])+'$',
            color=COLORS[0] if s<=r else COLORS[1],fc=fc,fontsize=17)
ax.text(.55,.015,'Warm cells cross the block boundary: a factor u',ha='center',fontsize=15)
save(f,5)

# T06: composition agrees at coefficient and phase levels.
g=[1,-1];combined=conv(g,h);product=matmul(route(g,2),route(h,2));Pcombined=route(combined,2)
check('Tap composition exact convolution and matrix multiplication',combined==[1,1,-1,-1] and product==Pcombined,{'first_taps':h,'second_taps':g,'combined_taps':combined,'product_coefficients':product})
f=frame(size=(10,5.1));gs=f.add_gridspec(2,3,height_ratios=[1.2,.45])
for ax,vals,ttl,col in zip([f.add_subplot(gs[0,i]) for i in range(3)],[h,g,combined],['First taps h','Second taps g','Combined taps g ∗ h'],[COLORS[0],COLORS[1],COLORS[2]]):
    stems(ax,list(range(len(vals))),vals,ttl,col,True);ax.set_xlabel('delay k');ax.set_ylim(-1.6,2.8)
ax=f.add_subplot(gs[1,:]);blank(ax)
ax.text(.5,.65,r'$P_2(g)\cdot P_2(h)=P_2(g*h)$',ha='center',fontsize=24)
ax.text(.5,.18,'Composition is exact in either representation',ha='center',fontsize=16)
f.tight_layout(h_pad=1.4,w_pad=2);save(f,6)

# T07: finite differences and the causal boundary.
n=list(range(11));sq=[j*j for j in n];d=conv([1,-1],sq,11);dd=conv([1,-1],d,11)
check('Finite differences of squared integers',d==[0]+[2*j-1 for j in range(1,11)] and dd==[0,1]+[2]*9,{'input':sq,'first_difference':d,'second_difference':dd,'boundary':'negative input indices zero'})
f=frame();axs=f.subplots(1,2)
stems(axs[0],n,d,r'First difference of $n^2$',annotate=True)
stems(axs[1],n,dd,r'Second difference',COLORS[1],True)
for a in axs:a.set_xlabel('n')
axs[1].axvspan(-.2,1.3,color='#FAEFEA',zorder=0);axs[1].text(4.7,2.65,'Constant after the boundary',ha='center',fontsize=14)
axs[1].set_ylim(-.2,3.1);f.tight_layout(w_pad=2);save(f,7)

# T08: recurrence taps leave the initial impulse.
fx=fib(24);res=conv([1,-1,-1],fx,24)
check('Fibonacci annihilator including causal initial residual',res==[0,1]+[0]*22,{'taps':[1,-1,-1],'tested_indices':[0,23],'residual':res})
f=frame();axs=f.subplots(1,2,gridspec_kw={'width_ratios':[1,1.5]})
stems(axs[0],[0,1,2],[1,-1,-1],'Recurrence taps',annotate=True);axs[0].set_xlabel('tap delay')
stems(axs[1],list(range(12)),res[:12],r'Output: one initial impulse',COLORS[1],True)
axs[1].set_xlabel('n');axs[1].set_ylim(-.25,1.6)
f.tight_layout(w_pad=2);save(f,8)

# T09: phase recurrences share denominator but not numerator.
f48=fib(48);E=f48[0::2];O=f48[1::2];q=[1,-3,1]
er=conv(q,E,24);orr=conv(q,O,24)
check('Even and odd Fibonacci recurrence residuals',er==[0,1]+[0]*22 and orr==[1,-1]+[0]*22,{'denominator_taps':q,'tested_coarse_indices':[0,23],'even_residual':er,'odd_residual':orr})
f=frame();axs=f.subplots(1,2)
stems(axs[0],list(range(9)),er[:9],r'Even channel: $\delta_1$',annotate=True)
stems(axs[1],list(range(9)),orr[:9],r'Odd channel: $\delta_0-\delta_1$',COLORS[1],True)
for a in axs:a.set_ylim(-1.5,1.6);a.set_xlabel('coarse index m')
f.tight_layout(w_pad=2);save(f,9)

# T10: finite numerator taps, infinite response.
H=[1,3]
for i in range(2,24):H.append(3*H[-1]-H[-2])
Ee=conv([0,1],H,24);Oo=conv([1,-1],H,24)
check('Finite numerator taps acting on infinite reciprocal prefix',Ee==E and Oo==O and conv(q,H,24)==[1]+[0]*23,{'H_prefix':H[:10],'numerator_even':[0,1],'numerator_odd':[1,-1],'checked_terms':24})
f=frame();ax=f.add_subplot();blank(ax)
box(ax,(.05,.60),.90,.23,'H coefficients: 1, 3, 8, 21, 55, 144, …',fontsize=20)
ax.text(.5,.92,'The reciprocal continues indefinitely',ha='center',fontsize=18)
box(ax,(.07,.13),.35,.24,'Finite taps (0, 1)\nE = u H',color=COLORS[0],fontsize=19)
box(ax,(.58,.13),.35,.24,'Finite taps (1, −1)\nO = (1 − u) H',color=COLORS[1],fontsize=19)
arrow(ax,(.30,.58),(.245,.39));arrow(ax,(.70,.58),(.755,.39),color=COLORS[1])
save(f,10)

# T11: bounded numerical frequency response, exact endpoint/gain facts.
N=801;w=np.linspace(0,np.pi,N);Hw=sum(v*np.exp(-1j*k*w) for k,v in enumerate(h));mag=4*np.cos(w/2)**2
err=float(np.max(np.abs(np.abs(Hw)-mag)))
check('Frequency illustration compared with closed magnitude',err<5e-14,{'arithmetic':'NumPy float64 / complex128','grid_samples':N,'omega_interval':[0,math.pi],'maximum_absolute_error':err,'exact_DC_gain':sum(h),'exact_pi_zero':'1-2+1=0'})
f=frame();ax=f.add_subplot();ax.plot(w,np.abs(Hw),color=COLORS[0]);ax.scatter([0,np.pi],[4,0],color=COLORS[1],s=65,zorder=4)
ax.set_xticks([0,np.pi/2,np.pi],['0',r'$\pi/2$',r'$\pi$']);ax.set_ylim(-.18,4.8)
ax.set_xlabel(r'frequency $\omega$');ax.set_ylabel(r'$|H(e^{-i\omega})|$');ax.grid()
ax.annotate('DC gain = 1 + 2 + 1 = 4',xy=(0,4),xytext=(.43,4.4),fontsize=16,arrowprops={'arrowstyle':'->','color':COLORS[1]})
ax.annotate('Zero at π',xy=(np.pi,0),xytext=(2.23,1.1),fontsize=16,arrowprops={'arrowstyle':'->','color':COLORS[1]})
f.tight_layout();save(f,11)

# T12: linear phase only off zeros.
ww=np.linspace(-np.pi,np.pi,803)[1:-1];HH=sum(v*np.exp(-1j*k*ww) for k,v in enumerate(h))
demod=np.exp(1j*ww)*HH;phase_err=float(np.max(np.abs(np.angle(HH)+ww)));amp_err=float(np.max(np.abs(demod-(2+2*np.cos(ww)))))
check('Symmetric three-tap phase illustration off the zero',phase_err<1e-10 and amp_err<5e-14,{'omega_grid':'801 interior samples of 803 endpoints-inclusive samples on [-pi,pi]','endpoint_zeros_excluded':True,'maximum_phase_error':phase_err,'maximum_demodulated_amplitude_error':amp_err})
f=frame();axs=f.subplots(1,2)
axs[0].plot(ww,np.angle(HH));axs[0].plot([-np.pi,np.pi],[np.pi,-np.pi],ls='--',color=COLORS[1],lw=1.2)
axs[0].set_title(r'Phase $=-\omega$ away from zeros');axs[0].set_ylabel('radians')
axs[1].plot(ww,demod.real,color=COLORS[2]);axs[1].set_title(r'Remove the delay $e^{-i\omega}$');axs[1].set_ylabel('real amplitude')
for ax in axs:
    ax.set_xticks([-np.pi,0,np.pi],[r'$-\pi$','0',r'$\pi$']);ax.set_xlabel(r'$\omega$');ax.grid()
    ax.axvline(-np.pi,color=MUTED,ls=':',lw=1);ax.axvline(np.pi,color=MUTED,ls=':',lw=1)
axs[1].text(0,.4,'Endpoint zeros: phase undefined',ha='center',fontsize=13)
f.tight_layout(w_pad=2.0);save(f,12)

# T13: Haar exact algebra without inexact radicals in finite checks.
haar_pairs=[(a,b) for a in range(-5,6) for b in range(-5,6)]
check('Haar sum/difference exact perfect reconstruction',all((Q(a+b+a-b,2),Q(a+b-(a-b),2))==(a,b) for a,b in haar_pairs),{'arithmetic':'integers and fractions; common sqrt(2) factored symbolically','pairs_checked':len(haar_pairs),'pair_range':[-5,5],'normalized_matrix':'(1/sqrt(2))*[[1,1],[1,-1]]'})
f=frame();ax=f.add_subplot();blank(ax)
box(ax,(.01,.39),.18,.23,'Pair\n(3, 5)',fontsize=20)
box(ax,(.34,.60),.31,.19,r'$c=4\sqrt{2}$',fontsize=22)
box(ax,(.34,.21),.31,.19,r'$d=-\sqrt{2}$',COLORS[1],fontsize=22)
box(ax,(.81,.39),.18,.23,'Pair\n(3, 5)',COLORS[2],fontsize=20)
arrow(ax,(.20,.57),(.33,.69));arrow(ax,(.20,.43),(.33,.30),color=COLORS[1])
arrow(ax,(.66,.69),(.80,.57),color=COLORS[2]);arrow(ax,(.66,.30),(.80,.43),color=COLORS[2])
ax.text(.26,.88,'Analysis A',ha='center',fontsize=18);ax.text(.74,.88,r'Synthesis $A^{\mathsf{T}}$',ha='center',fontsize=18)
ax.text(.5,.04,r'$c=(3+5)/\sqrt{2},\quad d=(3-5)/\sqrt{2}$',ha='center',fontsize=21)
save(f,13)

# T14: exact lifting with finite signed causal filters.
def lifting(e,o,p,up):
    n=len(e);pe=conv(p,e,n);dd=[o[j]-pe[j] for j in range(n)]
    ud=conv(up,dd,n);ss=[e[j]+ud[j] for j in range(n)]
    eback=[ss[j]-ud[j] for j in range(n)];peback=conv(p,eback,n)
    oback=[dd[j]+peback[j] for j in range(n)]
    return ss,dd,eback,oback
p=[1,-1];up=[0,-1];e=[3,-1,4,0,2,-5,1,2];o=[1,2,-2,4,0,3,-1,5];ss,dd,ee,oo=lifting(e,o,p,up)
checks_lifting=0
for pp in ([1],[1,-1],[0,2,-3],[Q(1,2),Q(-2,3)]):
    for uu in ([0],[0,-1],[2,-1],[Q(-1,4),Q(2,5)]):
        _,_,er,orr=lifting(e,o,pp,uu);assert er==e and orr==o;checks_lifting+=1
check('Signed finite predict/update exact invertibility',ee==e and oo==o,{'arithmetic':'integers/Fractions','filter_pairs_checked':checks_lifting,'negative_coarse_indices':'zero','example_predict_taps':p,'example_update_taps':up,'input_even':e,'input_odd':o,'output_S':ss,'output_D':dd})
f=frame();ax=f.add_subplot();blank(ax)
for xy,wid,lab,col in [((.02,.62),.22,r'$(E,O)$',COLORS[0]),((.38,.62),.24,r'$(E,D)$',COLORS[1]),((.76,.62),.22,r'$(S,D)$',COLORS[2]),
                       ((.76,.15),.22,r'$(S,D)$',COLORS[2]),((.38,.15),.24,r'$(E,D)$',COLORS[1]),((.02,.15),.22,r'$(E,O)$',COLORS[0])]:
    box(ax,xy,wid,.17,lab,col,fontsize=22)
arrow(ax,(.25,.705),(.37,.705));arrow(ax,(.63,.705),(.75,.705),color=COLORS[2])
arrow(ax,(.75,.235),(.63,.235),color=COLORS[2]);arrow(ax,(.37,.235),(.25,.235))
ax.text(.32,.9,r'$D=O-PE$',ha='center',fontsize=19);ax.text(.70,.9,r'$S=E+UD$',ha='center',fontsize=19)
ax.text(.70,.045,r'$E=S-UD$',ha='center',fontsize=19);ax.text(.32,.045,r'$O=D+PE$',ha='center',fontsize=19)
ax.text(.5,.49,r'Example: $P=1-u,\quad U=-u$',ha='center',fontsize=19)
save(f,14)

# T15: rate 3/2, same summation represented three ways.
rx=[1,2,3,4];rh=[1,2,1];ups=[0]*((len(rx)-1)*3+1)
for j,v in enumerate(rx):ups[3*j]=v
filtered=conv(rh,ups);direct=filtered[::2]
rphase=[];table=[]
for m in range(len(direct)):
    r=(2*m)%3;ell=(2*m-r)//3;pr=rh[r::3]
    val=sum(pr[k]*rx[ell-k] for k in range(len(pr)) if 0<=ell-k<len(rx))
    rphase.append(val);table.append([m,r,ell,rh[r],val])
check('Rational resampling 3/2 exact routing',direct==rphase==[1,1,4,3,3,8],{'input':rx,'upsampled':ups,'taps':rh,'filtered':filtered,'downsampled':direct,'phase_order':[row[1] for row in table],'input_indices':[row[2] for row in table],'interpretation':'routing equality only; no anti-alias specification'})
f=frame(size=(10,5.1));axs=f.subplots(2,1,gridspec_kw={'height_ratios':[1.2,1.1]})
stems(axs[0],list(range(len(filtered))),filtered,'Fine-grid convolution; warm dots are kept',COLORS[0],True)
axs[0].scatter(list(range(0,len(filtered),2)),direct,color=COLORS[1],s=75,zorder=4);axs[0].set_xlabel('fine index n (keep n = 2m)')
axs[1].axis('off');cell=[[str(row[j]) for row in table] for j in range(5)]
tab=axs[1].table(cellText=cell,rowLabels=['output m','phase r','input ℓ','tap weight','output y[m]'],cellLoc='center',loc='center',colWidths=[.125]*6)
tab.auto_set_font_size(False);tab.set_fontsize(14);tab.scale(1,1.55)
for (i,j),c in tab.get_celld().items():
    c.set_edgecolor('#C9D5D7');c.set_facecolor(PALE if i==4 else 'white')
f.tight_layout(h_pad=1);save(f,15)

# T16: chunk streaming retains L-1 samples, and explicit tail flush.
def stream(h,x,sizes,flush=False):
    state=[0]*(len(h)-1);out=[];snap=[];offset=0
    for size in sizes:
        for value in x[offset:offset+size]:
            history=state+[value]
            out.append(sum(h[k]*history[-1-k] for k in range(len(h))))
            state=history[1:]
        offset+=size;snap.append(list(state))
    assert offset==len(x)
    if flush:
        for _ in range(len(h)-1):
            history=state+[0];out.append(sum(h[k]*history[-1-k] for k in range(len(h))));state=history[1:]
    return out,snap
cx=fib(12);streamout,snaps=stream(h,cx,[4,5,3],True)
assert streamout==conv(h,cx)
streamcases=0
for L in range(1,6):
    hh=[((3*k+L)%7)-3 for k in range(L)]
    xx=[((11*j+L)%19)-9 for j in range(41)]
    for sizes in ([41],[1]*41,[4,5,3,8,21],[17,13,11]):
        got,_=stream(hh,xx,sizes,True);assert got==conv(hh,xx);streamcases+=1
check('Exact chunk streaming and tail flush',streamout==conv(h,cx),{'filter_lengths_checked':[1,5],'input_length':41,'chunk_partitions_per_length':4,'cases_checked':streamcases,'example_chunks':[4,5,3],'example_state_snapshots_oldest_first':snaps,'example_output_full':streamout,'required_state':'L-1 input samples for this direct-form FIR implementation'})
f=frame(size=(10,5.1));axs=f.subplots(2,1,gridspec_kw={'height_ratios':[1.2,.65]})
stems(axs[0],list(range(len(streamout))),streamout,'Whole-record and chunked outputs coincide',annotate=True)
for p0 in [3.5,8.5,11.5]:axs[0].axvline(p0,color=COLORS[1],ls='--',lw=1.4)
axs[0].axvspan(11.5,13.6,color=PALE,zorder=0);axs[0].set_xlabel('fine sample index n')
blank(axs[1])
for i,(txt,state) in enumerate(zip(['After 4 samples','After 9 samples','After 12 samples'],snaps)):
    xp=.04+i*.33;box(axs[1],(xp,.20),.26,.50,f'{txt}\nstate {tuple(state)}',fontsize=16)
axs[1].text(.96,.92,'Then flush\ntwo zeros',ha='right',fontsize=14)
f.tight_layout(h_pad=1.3);save(f,16)

# Shared exact routing contract across several small moduli and signed filters.
routing_cases=0
for M in range(2,7):
    for L in range(1,10):
        hh=[((k*5+L)%11)-5 for k in range(L)]
        xx=[((j*7+M)%17)-8 for j in range(31)]
        yy=conv(hh,xx)
        assert run_route(hh,xx,M,len(yy))==yy
        routing_cases+=1
check('General causal FIR phase-routing formula bounded exact tests',True,{'arithmetic':'Python integers','moduli':[2,6],'tap_lengths':[1,9],'input_length':31,'cases_checked':routing_cases,'negative_index_convention':'zero','full_tail_checked':True})

figs=[]
for i in range(1,17):
    for ext in ['pdf','png']:
        path=ROOT/'figures'/f'T{i:02d}_taps.{ext}'
        figs.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
record={'schema_version':1,'status':'PASS','scope':'T01--T16 author exact finite checks and bounded numerical illustrations',
    'claim_id':'T01--T16 causal FIR routing, reconstruction, and stream implementation',
    'repository':{'commit':None,'dirty':True,'revision_note':'Unversioned artifact workspace; input file hashes recorded below.'},
    'scientific_contract':'Causal zero extension; fine OGF delay z, coarse OGF delay u. Exact algebra supports routing/reconstruction identities. Finite runs verify the shown implementation and examples, not universal recurrence assertions for unrelated sequences.',
    'command':'env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_taps.py',
    'software':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
    'arithmetic':{'finite_witnesses':'Python integers and fractions.Fraction','frequency_curves':'NumPy float64 / complex128'},
    'elapsed_seconds':time.perf_counter()-START,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'checks':CHECKS,'figure_count':16,'figures':figs,
    'nonclaims':['No ideal anti-aliasing performance is asserted for the chosen resampling taps.','No constant-coefficient finite annihilator is asserted for all OEIS sequences.','The reciprocal response H is infinite, although its denominator and numerator taps are finite.','No boundary-free recurrence is asserted at causal initial indices.']}
record['environment']={'software':[{'name':name,'version':version} for name,version in record['software'].items()],
    'hardware':platform.machine()+'; CPU-only Matplotlib; '+str(os.cpu_count())+' logical CPUs',
    'cooperative_thread_caps':{'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),
                             'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS')},
    'machine_enforced_limits':'No per-process memory/CPU cap; bounded loops and fixed figure sizes.'}
record['mathematics']={'assertion_tested':record['scientific_contract'],
    'coefficient_domain':'Python integers and Fraction for algebra; NumPy float64/complex128 for the frequency illustration only.',
    'conventions':'Version 1: n>=0, zero extension at negative indices; fine delay z, coarse delay u; matrix rows output phases, columns input phases; blockwise Haar pairing.',
    'inputs':['Fibonacci prefixes','Signed deterministic finite input vectors','Finite tap polynomials','801-point frequency grids'],
    'bounds':{'routing_moduli':[2,6],'routing_tap_lengths':[1,9],'routing_input_length':31,
              'routing_cases':45,'Haar_integer_pair_range':[-5,5],'Haar_pairs':121,
              'lifting_filter_pairs':16,'streaming_filter_lengths':[1,5],
              'streaming_cases':20,'frequency_samples':801},
    'non_claims':record['nonclaims']}
record['randomness']={'used':False,'generator':'not used','seed':None}
record['run']={'started_at':STARTED_AT,'runtime_seconds':record['elapsed_seconds'],'exit_status':0}
record['outputs']=[{'path':p['path'],'sha256':p['sha256']} for p in figs]
record['input_artifacts']=[]
for name,before in INPUT_HASHES.items():
    after=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    assert before==after, 'input changed during tap run: '+name
    record['input_artifacts'].append({'path':name,'sha256':before,'sha256_after':after})
record['result']='Implementation and finite assertions verified in the stated ranges; frequency illustrations agree with their closed formulas within the recorded numerical tolerance.'
record['residual_risks']=['Finite witnesses do not replace the elementary coefficient-index derivation or authenticated source theorem.',
    'Frequency error bounds are observed floating-point residuals on the plotted grids, not interval-certified estimates for every real frequency.',
    'Legacy schema version 1 has no machine-checkable resource-limit record; input hashes are supplied as an additional provenance field.']
(ROOT/'evidence').mkdir(exist_ok=True)
(ROOT/'evidence'/'tap_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':'PASS','plates':16,'checks':len(CHECKS),'routing_cases':routing_cases,'streaming_cases':streamcases,'frequency_magnitude_max_error':err}))
