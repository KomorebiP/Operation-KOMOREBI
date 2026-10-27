#!/usr/bin/env python3
"""Exact rational example checks and vector figures for the visual guide.

All assertions use Fraction. Plotted exponentials and continuous curves use
floating point only to draw the stated analytic formulas, not to verify limits.
"""
from pathlib import Path
from fractions import Fraction as F
import json, math, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
VAL=ROOT/'validation'; VAL.mkdir(exist_ok=True)
C={'navy':'#183345','teal':'#168A89','gold':'#D89B35','red':'#BC5A56','gray':'#76848A','pale':'#EDF4F4'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':C['navy'],'text.color':C['navy'],'axes.titlesize':12,'pdf.fonttype':42,'svg.fonttype':'none'})
checks=[]
def check(test,label):
    if not test: raise AssertionError(label)
    checks.append(label)
def matrix(rows): return [[F(x) for x in r] for r in rows]
def eye(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def mul(a,b): return [[sum((a[i][k]*b[k][j] for k in range(len(b))),F(0)) for j in range(len(b[0]))] for i in range(len(a))]
def add(a,b): return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def sub(a,b): return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def tr(a): return list(map(list,zip(*a)))
def power(a,n):
    out=eye(len(a))
    for _ in range(n):out=mul(out,a)
    return out
def scale(c,a): return [[c*x for x in r] for r in a]
def sq(v):return sum((x*x for x in v),F(0))
def mv(a,v):return [sum((x*y for x,y in zip(r,v)),F(0)) for r in a]
def infnorm(a):return max((sum((abs(x) for x in r),F(0)) for r in a),default=F(0))

# Redundant coordinates, compatibility, and exact composition.
a=matrix([[1,0],[0,1],[1,1]]); s=matrix([[1,0,0],[0,1,0]])
E=mul(a,s); I=eye(3)
check(mul(s,a)==eye(2),'redundant reconstruction s a=I')
check(mul(E,E)==E,'redundant coordinate projector idempotent')
T=matrix([[1,2],[0,1]]); S=matrix([[0,1],[1,0]])
K=mul(mul(a,T),s)
check(mul(mul(s,K),a)==T,'decode encoded operator')
check(mul(mul(E,K),E)==K,'encoded operator compatibility')
check(mul(mul(a,mul(S,T)),s)==mul(mul(mul(a,S),s),K),'exact encoded composition')
check(mul(mul(E,I),E)==E and E!=I,'identity on all coordinates is incompatible')
check(mv(E,[F(1),F(1),F(0)])==[F(1),F(1),F(2)],'incompatible coordinate record repaired by E')

# Delayed return: visible y, hidden (z1,z2).
L=matrix([[0,1,0],[0,0,1],[1,0,0]]); cc=matrix([[1,0,0]]); rr=tr(cc)
A=mul(mul(cc,L),rr); Q=sub(eye(3),mul(rr,cc))
B=matrix([[1,0]]); G=matrix([[0],[1]]); D=matrix([[0,1],[0,0]])
check(A==[[F(0)]],'delayed direct visible generator zero')
check(mul(mul(B,D),G)==[[F(1)]],'delayed first nonzero hidden moment')
check(mul(B,G)==[[F(0)]],'delayed zeroth moment vanishes')
for n in range(9):
    en=mul(mul(cc,power(L,n)),rr)[0][0]
    check(en==F(n%3==0),f'delayed prepared power {n}')
for m in range(5):
    for n in range(5):
        lhs=sub(mul(mul(cc,power(L,m+n)),rr),mul(mul(mul(cc,power(L,m)),rr),mul(mul(cc,power(L,n)),rr)))
        rhs=mul(mul(mul(mul(cc,power(L,m)),Q),power(L,n)),rr)
        check(lhs==rhs,f'compression defect factorization m={m},n={n}')
for k in range(2,10):check(mul(mul(B,power(D,k)),G)==[[F(0)]],f'nilpotent memory moment {k}')
for n in range(9):
    # Apply exact hidden convolution to a concrete orbit with arbitrary z0.
    x0=[F(2),F(3),F(5)]; xn=mv(power(L,n),x0)
    z0=x0[1:]; zn=mv(power(D,n),z0)
    for j in range(n):
        yj=mv(power(L,j),x0)[0]
        term=mv(mul(power(D,n-1-j),G),[yj]);zn=[u+v for u,v in zip(zn,term)]
    check(zn==xn[1:],f'hidden elimination n={n}')

# Noncommuting behavioral model.
TA=matrix([[0,1,0],[0,0,0],[0,0,1]])
TB=matrix([[0,0,0],[1,0,0],[0,0,1]])
q=matrix([[1,0,0],[0,1,0]]); O=matrix([[1,0,0]]); V=matrix([[1,0]])
UA=matrix([[0,1],[0,0]]);UB=matrix([[0,0],[1,0]])
check(mul(TA,TB)!=mul(TB,TA),'behavioral operations noncommute')
check(mul(q,TA)==mul(UA,q),'behavioral A intertwines')
check(mul(q,TB)==mul(UB,q),'behavioral B intertwines')
check(mul(V,q)==O,'behavioral readout factors')
check([O[0],mul(O,TA)[0]]==q,'depth one observation generates q')
for depth in range(6):
    for bits in range(2**depth):
        tw=eye(3);uw=eye(2)
        for j in range(depth):
            t,u=(TA,UA) if bits>>j&1==0 else (TB,UB)
            tw=mul(t,tw);uw=mul(u,uw)
        check(mul(O,tw)==mul(mul(V,uw),q),f'behavioral exact word depth={depth},bits={bits}')

# Exact two-rate budgets, including equal and zero rates.
for aa,bb in [(F(1),F(4,5)),(F(11,10),F(1)),(F(0),F(0)),(F(1,2),F(1,2))]:
    for n in range(10):
        H=sum((aa**j*bb**(n-1-j) for j in range(n)),F(0))
        check((aa-bb)*H==aa**n-bb**n,f'two-rate identity {aa},{bb},n={n}')
        if aa==bb and n>0:check(H==n*aa**(n-1),f'equal-rate budget {aa},n={n}')

# Geometry, minimum norm, Gram coordinates, and regularization.
forward=matrix([[1,1],[0,0],[0,0]]);recover=matrix([[F(1,2),0,0],[F(1,2),0,0]])
v=[F(3),F(4),F(5)];p=mv(recover,v);r=mv(forward,p);ob=[F(0),F(4),F(0)];inc=[F(0),F(0),F(5)]
check(p==[F(3,2),F(3,2)],'minimum source explicit')
check(r==[F(3),F(0),F(0)],'minimum source image')
check(sq([x-y for x,y in zip(v,r)])==41,'global image error 41')
check(sq(ob)+sq(inc)==41,'obstruction inconsistency split 16+25')
check(mul(mul(forward,recover),forward)==forward,'first Penrose identity')
check(mul(mul(recover,forward),recover)==recover,'second Penrose identity')
check(tr(mul(forward,recover))==mul(forward,recover),'image projector symmetric')
check(tr(mul(recover,forward))==mul(recover,forward),'source projector symmetric')
for k in range(-6,7):
    g=[p[0]+k,p[1]-k]
    check(mv(forward,g)==r,f'least squares kernel family {k}')
    check(sq(g)==sq(p)+2*k*k,f'minimum norm Pythagoras {k}')
gram=matrix([[1,1],[1,5]]);h=[F(-2),F(2)]
check(sum((x*y for x,y in zip(h,mv(gram,h))),F(0))==16,'native Gram harmonic norm 16')
check(sq(h)==8,'same harmonic coefficients Euclidean square 8 is wrong metric')
check(F(2)**2==4,'quotient coordinate treated as unit gives mistaken square 4')
for lam in [F(1,16),F(1,4),F(1),F(4)]:
    xl=[F(3)/(2+lam)]*2
    N=add(mul(tr(forward),forward),scale(lam,eye(2)))
    check(mv(N,xl)==mv(tr(forward),v),f'Tikhonov normal equation lambda={lam}')
    fit=sq([x-y for x,y in zip(mv(forward,xl),v)])
    bias=F(3)**2*(lam/(2+lam))**2
    check(fit==41+bias,f'regularized data bias decomposition lambda={lam}')
check(F(42)+F(2)==44,'lambda one regularized objective 44')

# Discrepancy and genuinely inexact scalar certificate.
eta=F(1);tau=F(3);lam=F(1);x=F(201,100);exact=F(2);rho=F(1,50);kap=F(1,50);xi=F(1,100);omega=F(1,100);m=F(2)
res=(1+lam)*x-F(4);fit=abs(x-F(4))
check(res==rho,'inexact actual normal residual')
check(abs(x-exact)==F(1,100),'inexact actual source correction')
check(fit==F(199,100),'inexact actual fitting norm')
check(abs(m-fit)<=omega,'inexact measured enclosure')
check(rho*rho<=lam*lam*kap*kap,'inexact source residual budget')
check(rho*rho<=4*lam*xi*xi,'inexact image residual budget')
check(eta+omega+xi<=m<=tau*eta-omega-xi,'inexact protected band')
check(2*(omega+xi)<=(tau-1)*eta,'inexact nonempty margin')
for ll in [F(1,16),F(1,4),F(1),F(4),F(16)]:
    xx=F(4)/(1+ll);rrr=F(4)*ll/(1+ll)
    check(xx+rrr==4,f'scalar discrepancy parameter {ll}')

# Calibration and approximate factorization in entrywise induced infinity norm.
U=matrix([[1,1]]);R=matrix([[F(1,2)],[F(1,2)]])
check(mul(U,R)==eye(1),'redundant calibration exact reconstruction')
tt=matrix([[F(3,2)]])
check(mul(mul(tt,U),R)==tt,'calibration factors operator')
for rho0 in [F(0),F(1,4),F(1,2),F(3,4)]:
    Ur=scale(1-rho0,U)
    check(infnorm(sub(eye(1),mul(Ur,R)))==rho0,f'approximate frame defect {rho0}')
    check(infnorm(tt)<=infnorm(mul(tt,Ur))*infnorm(R)/(1-rho0),f'approximate frame conservative bound {rho0}')
partial=matrix([[1],[0]])
for ss in [F(1),F(10),F(100),F(1000)]:
    unseen=matrix([[0,ss]])
    check(mul(unseen,partial)==[[F(0)]],f'nonspanning exact fit {ss}')
    check(infnorm(unseen)==ss,f'nonspanning unseen norm {ss}')
# Generalized nonfeasibility controls only; universal claim belongs to Lean.
for ll in [F(1,k) for k in range(1,17)]:
    xzero=F(0);candidate=F(1,10)+F(1)*abs(xzero)
    check(F(1)>F(2)*candidate,f'zero model generalized rejection lambda={ll}')

def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',pad_inches=.10)
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight',pad_inches=.10)
    fig.savefig(FIG/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.10)
    plt.close(fig)
def canvas(w=8,h=3.0):
    fig,ax=plt.subplots(figsize=(w,h));ax.set_xlim(0,10);ax.set_ylim(0,4);ax.axis('off');return fig,ax
def box(ax,xy,w,h,title,body='',color='teal'):
    x,y=xy;ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.12,rounding_size=.08',facecolor=C['pale'],edgecolor=C[color],lw=1.4))
    ax.text(x+w/2,y+h*.72,title,ha='center',va='center',weight='bold',fontsize=12)
    if body:ax.text(x+w/2,y+h*.35,body,ha='center',va='center',fontsize=10,linespacing=1.35)
def arrow(ax,start,end,label=None):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,color=C['gray'],lw=1.5))
    if label:ax.text((start[0]+end[0])/2,(start[1]+end[1])/2+.17,label,ha='center',fontsize=10)

fig,ax=canvas(8,3.2)
box(ax,(.2,1.0),2.6,2.0,'Represent','Analysis / synthesis\nRealizable coordinates')
box(ax,(3.7,1.0),2.6,2.0,'Evolve','Transfer / memory\nFuture observations')
box(ax,(7.2,1.0),2.6,2.0,'Recover','Residual / conditioning\nCertified reconstruction')
arrow(ax,(2.95,2),(3.55,2));arrow(ax,(6.45,2),(7.05,2))
ax.text(5,.35,'Every stage retains its own assumptions and error budgets.',ha='center',fontsize=11)
save(fig,'reading_route')

fig=plt.figure(figsize=(7.5,4.1));ax=fig.add_subplot(111,projection='3d')
uu,vv=np.meshgrid(np.linspace(-1,2,7),np.linspace(-1,2,7))
ax.plot_surface(uu,vv,uu+vv,color=C['teal'],alpha=.25,edgecolor='none')
ax.scatter([1],[1],[0],s=50,color=C['red']);ax.scatter([1],[1],[2],s=50,color=C['navy'])
ax.plot([1,1],[1,1],[0,2],color=C['gold'],lw=2)
ax.text(1,1,-.4,'(1,1,0)',fontsize=10);ax.text(1.02,1.02,2.25,'E v = (1,1,2)',fontsize=10)
ax.set_xlabel('u',labelpad=6);ax.set_ylabel('v',labelpad=6);ax.set_zlabel('')
ax.text2D(.88,.50,'w',transform=ax.transAxes,fontsize=11,ha='left',va='center')
ax.set_title('Realizable records satisfy w = u + v',pad=12);ax.view_init(22,-58)
save(fig,'redundant_plane')

fig,axs=plt.subplots(1,2,figsize=(8.2,3.3),gridspec_kw={'width_ratios':[1,1.1]})
ax=axs[0];ax.set_xlim(-1.5,1.5);ax.set_ylim(-1.5,1.5);ax.axis('off')
pts={'y':(-1,.0),'z2':(.8,-.9),'z1':(.8,.9)}
for label,(xx,yy) in pts.items():ax.scatter([xx],[yy],s=1100,color=C['pale'],edgecolor=C['teal']);ax.text(xx,yy,label,ha='center',va='center',fontsize=12)
for p0,p1 in [('y','z2'),('z2','z1'),('z1','y')]:
    a0=np.array(pts[p0]);a1=np.array(pts[p1]);vv0=(a1-a0)/np.linalg.norm(a1-a0);arrow(ax,a0+.28*vv0,a1-.28*vv0)
ax.set_title('One return takes three steps')
ns=np.arange(8);ee=np.array([int(n%3==0) for n in ns]);axs[1].stem(ns,ee,linefmt=C['teal'],markerfmt='o',basefmt=' ')
axs[1].plot(ns,[1]+[0]*7,'s--',color=C['gold'],label='Aⁿ')
axs[1].set(xlabel='Full depth n',ylabel='Prepared Eₙ',ylim=(-.12,1.25),xticks=ns);axs[1].legend(frameon=False);axs[1].set_title('Shallow agreement, delayed failure')
fig.tight_layout();save(fig,'delayed_return')

fig,ax=canvas(8,2.8)
for idx,(title,body,col) in enumerate([('M₀ = 0','No immediate return','teal'),('M₁ = I','One hidden transition','gold'),('First discrepancy','E₃ − A³ = I','red')]):
    box(ax,(.2+3.45*idx,1.0),2.6,2.1,title,body,col)
arrow(ax,(2.97,2.05),(3.52,2.05));arrow(ax,(6.42,2.05),(6.97,2.05))
ax.text(5,.35,'Moment k is first visible at full depth k + 2.',ha='center')
save(fig,'moment_delay')

fig,ax=canvas(8,3.2)
box(ax,(.25,1.1),2.35,2.0,'Observe now','O(x,y,h) = x')
box(ax,(3.85,1.1),2.35,2.0,'Observe after A','O T_A(x,y,h) = y')
box(ax,(7.45,1.1),2.25,2.0,'Retain','q(x,y,h) = (x,y)')
arrow(ax,(2.77,2.0),(3.67,2.0));arrow(ax,(6.37,2.0),(7.27,2.0))
ax.text(5,.38,'h stays invisible under every word in A and B.',ha='center')
save(fig,'behavioral_model')

fig,ax=plt.subplots(figsize=(7.8,3.5));nn=np.arange(31)
ax.plot(nn,1-.8**nn,'o-',markersize=3,color=C['teal'],label='T = 1, U = 4/5: 1 − (4/5)ⁿ')
ax.plot(nn,1.1**nn-1,'o-',markersize=3,color=C['red'],label='T = 11/10, U = 1: (11/10)ⁿ − 1')
ax.set(xlabel='Depth n',ylabel='Exact scalar defect',ylim=(0,18));ax.legend(frameon=False,loc='upper left');ax.grid(alpha=.15);fig.tight_layout();save(fig,'discrete_stability')

fig,axs=plt.subplots(1,2,figsize=(8.2,3.3));ttime=np.linspace(0,8,250)
axs[0].plot(ttime,np.exp(.3*ttime)-1,color=C['red'],lw=2,label='e^(0.3t) − 1');axs[0].plot(ttime,.3*ttime,'--',color=C['gray'],label='0.3t')
axs[1].plot(ttime,1-np.exp(-ttime),color=C['teal'],lw=2,label='1 − e^(−t)');axs[1].axhline(1,color=C['gray'],ls='--',lw=1)
for ax in axs:ax.set(xlabel='Time t ≥ 0',ylabel='Scalar evolution defect');ax.legend(frameon=False);ax.grid(alpha=.15)
axs[0].set_title('Small defect with growth');axs[1].set_title('Decay supplies uniform control');fig.tight_layout();save(fig,'continuous_stability')

fig=plt.figure(figsize=(7.6,4.1));ax=fig.add_subplot(111,projection='3d')
ax.quiver(0,0,0,3,0,0,color=C['teal'],linewidth=2,arrow_length_ratio=.12)
ax.quiver(3,0,0,0,4,0,color=C['gold'],linewidth=2,arrow_length_ratio=.12)
ax.quiver(3,4,0,0,0,5,color=C['red'],linewidth=2,arrow_length_ratio=.12)
ax.quiver(0,0,0,3,4,5,color=C['navy'],linewidth=1.4,arrow_length_ratio=.08)
ax.text(1.0,-.6,0,'r = (3,0,0)',fontsize=10);ax.text(3.2,1.2,.2,'o = (0,4,0)',fontsize=10);ax.text(1.35,3.25,3.25,'i = (0,0,5)',fontsize=10,color=C['red'],bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})
ax.text(3.15,4.1,5.15,'v = (3,4,5)',fontsize=10)
ax.set(xlim=(0,5),ylim=(-1,5),zlim=(0,6),xlabel='Realizable',ylabel='Obstruction',zlabel='')
ax.text2D(.89,.50,'Inconsistency',transform=ax.transAxes,fontsize=10,ha='left',va='center',rotation=90)
ax.view_init(22,-58);save(fig,'global_geometry')

fig,ax=plt.subplots(figsize=(7.6,3.1));labels=['R₀ = span(e₁)','R₁ = span(e₁,e₂)'];ys=np.arange(2)
ax.barh(ys,[16,0],color=C['gold'],label='Obstruction energy');ax.barh(ys,[25,25],left=[16,0],color=C['red'],label='Inconsistency energy')
ax.text(8,0,'16',ha='center',va='center',color='white',weight='bold');ax.text(28.5,0,'25',ha='center',va='center',color='white',weight='bold');ax.text(12.5,1,'25',ha='center',va='center',color='white',weight='bold')
ax.set(yticks=ys,yticklabels=labels,xlabel='Squared distance to the realized space',xlim=(0,44));ax.invert_yaxis();ax.legend(loc='lower right',frameon=False);fig.tight_layout();save(fig,'refinement_energy')

fig,ax=plt.subplots(figsize=(6.8,3.7));xx=np.linspace(-.5,3.5,150)
ax.plot(xx,3-xx,color=C['gold'],lw=2,label='All best sources: g₁ + g₂ = 3')
ax.plot(xx,xx,'--',color=C['teal'],label='Identifiable direction: g₁ = g₂')
ax.plot([0,1.5],[0,1.5],color=C['navy'],lw=2)
ax.scatter([1.5,3],[1.5,0],s=60,c=[C['teal'],C['red']]);ax.annotate('Minimum norm (3/2,3/2)',(1.5,1.5),xytext=(1.9,2.8),fontsize=10,arrowprops={'arrowstyle':'->','color':C['gray']})
ax.annotate('Same image (3,0)',(3,0),xytext=(1.4,-.6),fontsize=10,arrowprops={'arrowstyle':'->','color':C['gray']})
ax.set(xlabel='g₁',ylabel='g₂',xlim=(-.5,3.7),ylim=(-.9,3.5),aspect='equal');ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,1.23),fontsize=9);ax.grid(alpha=.15);fig.tight_layout();save(fig,'minimum_source')

fig,ax=plt.subplots(figsize=(7.4,2.9));ax.barh([1,0],[16,4],color=[C['teal'],C['red']]);ax.text(8,1,'16',ha='center',va='center',color='white',weight='bold');ax.text(2,0,'4',ha='center',va='center',color='white',weight='bold')
ax.set(yticks=[1,0],yticklabels=['Native Gram metric','Treat quotient coordinate as unit'],xlabel='Squared obstruction norm',xlim=(0,18));fig.tight_layout();save(fig,'gram_metric')

fig,axs=plt.subplots(1,2,figsize=(8.1,3.2));ll=np.logspace(-3,2,220);source=3/(2+ll)
axs[0].semilogx(ll,source,color=C['teal'],lw=2);axs[0].axhline(1.5,color=C['gray'],ls='--',lw=1,label='Unregularized 3/2');axs[0].set(xlabel='λ > 0',ylabel='Each source coordinate');axs[0].legend(frameon=False,fontsize=9)
axs[1].semilogx(ll,9*(ll/(2+ll))**2,color=C['gold'],lw=2);axs[1].set(xlabel='λ > 0',ylabel='Extra image-bias energy');axs[1].axvline(1,color=C['gray'],ls=':',lw=1)
for ax in axs:ax.grid(alpha=.15)
fig.tight_layout();save(fig,'regularization_bias')

fig,ax=plt.subplots(figsize=(7.5,3.5));ll=np.logspace(-6,1,250)
for n,col in zip([1,2,8,32],[C['teal'],C['gold'],C['red'],C['navy']]):
    ss=1/n;ax.semilogx(ll,ll/(ss*ss+ll),label=f'Fixed mode, singular value 1/{n}',color=col,lw=2)
ax.set(xlabel='λ > 0',ylabel='Source-filter error',ylim=(-.03,1.05));ax.legend(frameon=False,fontsize=9,loc='upper left');ax.grid(alpha=.15);fig.tight_layout();save(fig,'strong_uniform_modes')

fig,ax=plt.subplots(figsize=(7.5,3.5));ll=np.logspace(-2,2,250);residual=4*ll/(1+ll)
ax.axhspan(1,3,color=C['teal'],alpha=.14,label='Accepted discrepancy band [1,3]')
ax.semilogx(ll,residual,color=C['navy'],lw=2);ax.scatter([1],[2],color=C['gold'],s=60,zorder=5);ax.annotate('λ = 1, source = 2, residual = 2',(1,2),xytext=(1.8,.5),fontsize=10,arrowprops={'arrowstyle':'->','color':C['gray']})
ax.axhline(4,color=C['gray'],ls='--',lw=1);ax.text(.014,4.12,'Upper limit ‖v‖ = 4',fontsize=10)
ax.set(xlabel='Positive parameter λ',ylabel='Fitting residual r(λ)',ylim=(0,4.5));ax.legend(frameon=False,fontsize=9,loc='upper center',bbox_to_anchor=(.5,1.18));ax.grid(alpha=.15);fig.tight_layout();save(fig,'discrepancy_curve')

fig,ax=plt.subplots(figsize=(8,2.9));ax.set_ylim(-.3,2.9);ax.set_xlim(.7,3.3)
ax.plot([1,3],[2.1,2.1],lw=10,color=C['pale'],solid_capstyle='butt');ax.plot([1.02,2.98],[1.25,1.25],lw=10,color=C['teal'],alpha=.7,solid_capstyle='butt')
ax.scatter([1.99,2],[.35,.35],color=[C['red'],C['gold']],s=70)
ax.annotate('Actual fit = 1.99',(1.99,.35),xytext=(1.5,-.18),ha='right',fontsize=10,arrowprops={'arrowstyle':'->','color':C['gray']})
ax.annotate('Measured m = 2',(2,.35),xytext=(2.5,-.18),ha='left',fontsize=10,arrowprops={'arrowstyle':'->','color':C['gray']})
ax.text(2,2.5,'Exact companion band: [1,3]',ha='center');ax.text(2,1.62,'Protected measured band: [1.02,2.98]',ha='center')
ax.set_yticks([]);ax.set_xlabel('Fitting norm');ax.spines[['left','top','right']].set_visible(False);fig.tight_layout();save(fig,'protected_band')

fig,ax=canvas(8,3.2)
box(ax,(.2,1.1),2.55,2.0,'Data allowance','η ≥ ‖A p − v‖')
box(ax,(3.73,1.1),2.55,2.0,'Operator\nallowance','δ ≥ ‖C − A‖')
box(ax,(7.2,1.1),2.6,2.0,'Candidate\nallowance','η + δ ‖x‖')
arrow(ax,(2.93,2),(3.55,2));arrow(ax,(6.45,2),(7.02,2))
ax.text(5,.35,'Acceptance uses the allowance. Truth of η and δ requires separate evidence.',ha='center',fontsize=10)
save(fig,'uncertainty_allowance')

fig,axs=plt.subplots(1,2,figsize=(8.2,3.3));ax=axs[0]
ax.axhline(0,color=C['teal'],lw=3);ax.arrow(0,0,0,2.0,width=.025,head_width=.15,color=C['red'],length_includes_head=True)
ax.text(.12,1.4,'Untested direction\nCₛ(x,y) = s y',fontsize=10);ax.text(.1,-.65,'Calibration U(t) = (t,0)',fontsize=10)
ax.set(xlim=(-1,1.9),ylim=(-1,2.5),xlabel='x',ylabel='y');ax.set_title('Partial calibration misses y');ax.spines[['top','right']].set_visible(False)
ax=axs[1];rho0=np.linspace(0,.9,220);ax.plot(rho0,1/(1-rho0),color=C['gold'],lw=2)
ax.set(xlabel='Reconstruction defect ρ < 1',ylabel='Amplification 1/(1−ρ)',ylim=(0,11));ax.set_title('Approximate frames amplify error');ax.grid(alpha=.15)
fig.tight_layout();save(fig,'calibration_boundary')

fig,ax=canvas(8,3.4)
box(ax,(.3,1.5),2.5,1.7,'Calibration','Truth allowance η_cal\nMeasured model fit')
box(ax,(3.75,1.5),2.5,1.7,'Whole operator','δ_gen = (η_cal + fit)\n× ‖R‖')
box(ax,(7.2,1.5),2.5,1.7,'Recovery','Accepted candidate\nExplicit feasibility')
arrow(ax,(2.97,2.35),(3.57,2.35));arrow(ax,(6.42,2.35),(7.02,2.35))
ax.text(5,.75,'Strong consistency: valid allowances vanish, fixed identifiable true source.',ha='center',fontsize=10)
ax.text(5,.27,'Individual noisy-sample derivation and stable task-only recovery remain open.',ha='center',fontsize=10,color=C['red'])
save(fig,'calibration_recovery')

files=sorted(FIG.glob('*.pdf'))
report={'status':'PASS','arithmetic':'fractions.Fraction; no floating point assertions','assertions':len(checks),'claims_scope':'Displayed finite worked examples only; no universal theorem or limit proved by these checks.','figure_count':len(files),'floating_illustrations':['continuous_stability','regularization_bias','strong_uniform_modes','discrepancy_curve','calibration_boundary'],'assertion_labels':checks,'figure_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(VAL/'visual_example_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','assertions','figure_count','arithmetic']}))
