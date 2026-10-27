#!/usr/bin/env python3
"""Exact finite H12 models and portable mathematical illustrations.

Integer/Fraction checks are exact. Decimal complex coordinates (80 working
digits) and binary64 plotting are numerical illustrations, never enclosures.
No elliptic-gamma or infinite canonical product is numerically evaluated.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal as D, localcontext
from dataclasses import dataclass
import argparse, hashlib, json, platform, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--record-output')
args=parser.parse_args()
NAVY,TEAL,GOLD,RED,GRAY='#17334d','#168b8d','#d99a2b','#b55752','#77828c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,
 'axes.labelcolor':NAVY,'text.color':NAVY,'axes.edgecolor':'#bac4cc',
 'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
 'grid.alpha':.18,'figure.facecolor':'white','savefig.facecolor':'white'})
files=[]
def save(fig,name):
    for ext in ('pdf','png'):
        path=OUT/f'{name}.{ext}'; temp=OUT/f'.{name}.tmp.{ext}'
        fig.savefig(temp,bbox_inches='tight',pad_inches=.18,dpi=200,
                    metadata={'Creator':'Komorebi H12 exact visual generator'} if ext=='pdf' else None)
        temp.replace(path)
        files.append({'path':str(path.relative_to(ROOT)),
                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)
def legend(fig,ax,ncol=2):
    h,l=ax.get_legend_handles_labels()
    fig.legend(h,l,loc='upper center',bbox_to_anchor=(.5,-.02),ncol=ncol,
               frameon=False,fontsize=11,columnspacing=1.6)
def note(fig,text):fig.suptitle(text,y=1.07,fontsize=11,color=NAVY)
def box(ax,xy,w,h,title,detail,color=TEAL):
    x,y=xy
    ax.add_patch(FancyBboxPatch(xy,w,h,boxstyle='round,pad=.04,rounding_size=.04',
                              fc='#f5f9fb',ec=color,lw=1.5))
    ax.text(x+w/2,y+h*.66,title,ha='center',va='center',weight='bold',fontsize=12)
    ax.text(x+w/2,y+h*.27,detail,ha='center',va='center',fontsize=10.5)
def arrow(ax,a,b,color=NAVY):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.7,'color':color})
def heat(ax,data,rows,cols,title):
    a=np.array([[float(x) for x in row] for row in data]);lim=max(1,np.max(abs(a)))
    ax.imshow(a,cmap='RdBu',vmin=-lim,vmax=lim,aspect='auto')
    for i,row in enumerate(data):
        for j,x in enumerate(row):ax.text(j,i,str(x),ha='center',va='center',fontsize=13,
                                          color='white' if abs(float(x))>.65*lim else NAVY)
    ax.set(xticks=range(len(cols)),xticklabels=cols,yticks=range(len(rows)),yticklabels=rows,title=title)
    ax.grid(False)

def H(n):return int(n>0)
def weight(c):return 4 if c%5==0 else -1
def pivot(b,c):return -((2*b-3*c)//7)
def order(a,b,c):
    j=pivot(b,c);return weight(c)*(H(j)-H(2*j-a)-H(a)+H(b))
def independent_order(a,b,c):
    found=[]
    for k in range(7):
        v=(Q(-2*b+3*c+k,7),Q(-7*a-4*b+6*c+2*k,7),Q(-5*b+4*c+20*k,7))
        if all(x.denominator==1 for x in v):found.append(tuple(int(x) for x in v))
    assert len(found)==1
    aa,bb,cc=found[0]
    return weight(cc)*(H(aa)-H(bb))-weight(c)*(H(a)-H(b))
def family(n):
    zeros={(-i,j,5*(n+k)) for i in range(1,n+1) for j in range(1,n+1) for k in range(1,n+1)}
    poles={(-i,j,5*(n+k)-r) for i in range(1,n+1) for j in range(1,n+1)
           for k in range(1,n+1) for r in range(1,5)}
    return zeros,poles

# An exact Q(beta) model with beta^3=7, used only for period identities.
def add(x,y):return tuple(a+b for a,b in zip(x,y))
def scale(a,x):return tuple(a*b for b in x)
def mul(x,y):
    c=[Q(0)]*5
    for i,a in enumerate(x):
        for j,b in enumerate(y):c[i+j]+=a*b
    for k in (4,3):c[k-3]+=7*c[k]
    return tuple(c[:3])
one=(Q(1),Q(0),Q(0)); beta_q=(Q(0),Q(1),Q(0))
tau_q=(Q(0),Q(2,15),Q(1,15));s_q=(Q(-2,15),Q(-1,15),Q(0))
delta_q=scale(Q(1,7),add(add(tau_q,scale(2,s_q)),scale(4,one)))
assert mul(beta_q,tau_q)==add(add(scale(2,tau_q),scale(4,s_q)),one)
assert mul(beta_q,s_q)==scale(-1,tau_q)
assert mul(beta_q,delta_q)==add(scale(-8,s_q),scale(-1,one))
N=np.array([[2,-1,0],[4,0,-15],[1,0,-2]],dtype=np.int64)
N5=np.array([[2,-1,0],[4,0,-3],[5,0,-2]],dtype=np.int64)
M=2*np.eye(3,dtype=np.int64)-N
assert np.array_equal(N@N@N,7*np.eye(3,dtype=np.int64))
assert np.array_equal(N5@N5@N5,7*np.eye(3,dtype=np.int64))
assert round(np.linalg.det(N))==7  # exact determinant also evaluated below
def det3(a):
    return int(a[0,0]*(a[1,1]*a[2,2]-a[1,2]*a[2,1])
               -a[0,1]*(a[1,0]*a[2,2]-a[1,2]*a[2,0])
               +a[0,2]*(a[1,0]*a[2,1]-a[1,1]*a[2,0]))
assert det3(N)==det3(N5)==7 and det3(M)==1

@dataclass(frozen=True)
class DC:
    re:D; im:D=D(0)
    def __add__(self,y):
        if not isinstance(y,DC):y=DC(D(y))
        return DC(self.re+y.re,self.im+y.im)
    __radd__=__add__
    def __neg__(self):return DC(-self.re,-self.im)
    def __sub__(self,y):return self+-y if isinstance(y,DC) else self+-D(y)
    def __mul__(self,y):
        if not isinstance(y,DC):y=DC(D(y))
        return DC(self.re*y.re-self.im*y.im,self.re*y.im+self.im*y.re)
    __rmul__=__mul__
    def __truediv__(self,y):
        if not isinstance(y,DC):y=DC(D(y))
        den=y.re*y.re+y.im*y.im
        return DC((self.re*y.re+self.im*y.im)/den,(self.im*y.re-self.re*y.im)/den)
    def point(self):return complex(float(self.re),float(self.im))
    def serial(self):return {'real':str(self.re),'imag':str(self.im)}
with localcontext() as ctx:
    ctx.prec=80
    r=D(2)
    for _ in range(200):
        rr=(2*r+D(7)/(r*r))/3
        if rr==r:break
        r=rr
    sqrt3=D(3).sqrt();omega=DC(-D(1)/2,sqrt3/2)
    beta=DC(-r/2,-r*sqrt3/2)
    tau=(beta*beta+2*beta)/15;t=-tau;s=-(beta+2)/15;delta=(tau+2*s+4)/7
    periods={k:v.serial() for k,v in [('beta',beta),('tau',tau),('t',t),('s',s),('delta',delta)]}
    embedding={}
    for n in (2,3):
        zz,pp=family(n)
        embedding[n]={label:[{'triple':list(v),'order':order(*v),
                              'coordinate':((v[0]*tau+v[1]*s+DC(D(v[2])/5))/beta).serial()}
                             for v in sorted(vals)] for label,vals in [('zeros',zz),('poles',pp)]}

checks={'period_identities_exact':True,'principal_matrices':{'M':M.tolist(),'N':N.tolist(),
 'N5':N5.tolist(),'det_N':det3(N),'det_N5':det3(N5),'N_cubed':(N@N@N).tolist(),
 'N5_cubed':(N5@N5@N5).tolist()},'fixed_periods_numerical':periods,
 'coordinate_arithmetic':'Python Decimal 80 working digits; not an interval enclosure'}
tested=0
for a in range(-6,7):
    for b in range(-6,7):
        for c in range(-6,7):
            assert order(a,b,c)==independent_order(a,b,c)
            assert order(a,b,c) in (-4,-1,0,1,4)
            tested+=1
checks['fraction_lift_comparison']={'box':[-6,6],'triples':tested,'all_seven_lifts':True}
table=[]
for n in range(1,17):
    zz,pp=family(n);assert len(zz)==n**3 and len(pp)==4*n**3 and not zz&pp
    assert all(order(*v)==4 for v in zz) and all(order(*v)==-1 for v in pp)
    assert all(-n<=a<0 and 0<b<=n and 0<c<=10*n for a,b,c in zz|pp)
    table.append({'n':n,'distinct_zeros':len(zz),'distinct_poles':len(pp),
                  'zero_multiplicity':4*len(zz),'pole_multiplicity':len(pp)})
checks['family_counts']=table;checks['plotted_embeddings']=embedding
lines=[[(k*x%3,k*y%3) for k in range(3)] for x,y in [(1,0),(0,1),(1,1),(1,2)]]
incidence={f'{x},{y}':sum((x,y) in line for line in lines) for x in range(3) for y in range(3)}
assert incidence['0,0']==4 and all(v==1 for k,v in incidence.items() if k!='0,0')
checks['four_norm_lines']={'lines':lines,'incidence':incidence}
checks['seven_action']={'multiplier':4,'modulus':7,'cycles':[[0],[1,4,2],[3,5,6]]}
jets=[[Q(0) if k<=g else -Q(1,k) for k in range(1,5)] for g in range(4)]
checks['canonical_local_log_coefficients']=[[str(x) for x in row] for row in jets]
reflection=[Q(0),Q(2),Q(0)];transition=[Q(0),Q(0),Q(6)]
cube=[3*Q(1,3)**k-1 for k in range(1,4)]
assert cube==[Q(0),Q(-2,3),Q(-8,9)]
checks['polynomial_reconstruction']={'reflection_z2':list(map(str,reflection)),
 'transition_second_derivative':list(map(str,transition)),'cube_exponents':list(map(str,cube))}
checks['negative_controls']={'unsmoothed_order_wrong':order(-1,1,11)!=4,
 'positive_pivot_without_positive_b_insufficient':order(-1,-1,10)==0,
 'genus_two_cubic_term_nonzero':jets[2][2]!=0,
 'wrong_cube_quadratic_coefficient_separates':cube[1]!=-Q(1,3)}
assert all(checks['negative_controls'].values())

fig,ax=plt.subplots(figsize=(9,3.5));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,4.1))
box(ax,(.2,2.3),2.5,1.3,'Analytic section','gamma → divisor → E₃',TEAL)
box(ax,(.2,.3),2.5,1.3,'Arithmetic unit','Gauss branch → norms',GOLD)
box(ax,(3.7,1.3),2.7,1.5,'Comparison data','modulus • phase • transport',NAVY)
box(ax,(7.45,1.3),2.2,1.5,'Exact equality','remaining comparison',RED)
arrow(ax,(2.8,2.8),(3.6,2.45));arrow(ax,(2.8,.95),(3.6,1.75))
arrow(ax,(6.5,2.05),(7.3,2.05),RED)
note(fig,'Two specified objects; their exact special-value identification remains open.')
save(fig,'00_map')

fig=plt.figure(figsize=(9.2,3.7),layout='constrained');grid=fig.add_gridspec(1,2,width_ratios=[1,1.1]);axs=[fig.add_subplot(grid[0,i]) for i in range(2)]
roots=[complex(float(r),0),beta.point().conjugate(),beta.point()]
axs[0].axhline(0,color=GRAY,lw=.8);axs[0].axvline(0,color=GRAY,lw=.8)
axs[0].scatter([z.real for z in roots],[z.imag for z in roots],s=90,color=GRAY)
axs[0].scatter([beta.point().real],[beta.point().imag],s=140,color=GOLD,label='chosen β')
axs[0].set(xlim=(-2.3,2.3),ylim=(-2.3,2.3),aspect='equal',xlabel='real part',ylabel='imaginary part',title='The three roots of β³ = 7')
handles=[]
for key,col,ls in [('t',TEAL,'-'),('s',GOLD,'-'),('tau',GRAY,'--'),('delta',NAVY,'-')]:
    z={'t':t,'s':s,'tau':tau,'delta':delta}[key].point()
    line,=axs[1].plot([0,z.real],[0,z.imag],color=col,ls=ls,lw=2.2,marker='o',label='δ' if key=='delta' else 'τ' if key=='tau' else key)
    handles.append(line)
axs[1].axhline(0,color=GRAY,lw=.8);axs[1].axvline(0,color=GRAY,lw=.8)
axs[1].set(aspect='equal',xlabel='real part',ylabel='imaginary part',title='Actual periods: τ = −t')
legend(fig,axs[1],4)
save(fig,'01_periods')

fig,ax=plt.subplots(figsize=(7.8,3.9));colors=[NAVY,TEAL,GOLD,RED]
for k,line in enumerate(lines):
    vals=np.array(line); ax.scatter(vals[:,0],vals[:,1],s=130,facecolors='none',edgecolors=colors[k],linewidths=1.7,label=str([(1,0),(0,1),(1,1),(1,2)][k]))
for x in range(3):
    for y in range(3):ax.text(x+.11,y+.07,f'({x},{y})',fontsize=11)
ax.scatter([0],[0],color=NAVY,s=30)
ax.set(xlim=(-.4,2.6),ylim=(-.35,2.4),aspect='equal',xticks=range(3),yticks=range(3),xlabel='first residue mod 3',ylabel='second residue mod 3')
note(fig,'Four order-three subgroups: the identity occurs four times, every other element once.')
legend(fig,ax,4);save(fig,'02_norm_lines')

fig,axs=plt.subplots(1,2,figsize=(9.2,3.6),layout='constrained')
angles=np.linspace(0,2*np.pi,500)
for ax in axs:
    ax.plot(np.cos(angles),np.sin(angles),color=GRAY,lw=1.5);ax.axhline(0,color=GRAY,lw=.7);ax.axvline(0,color=GRAY,lw=.7)
    ax.set(aspect='equal',xlim=(-1.35,1.35),ylim=(-1.3,1.3),xlabel='real part',ylabel='imaginary part')
axs[0].plot(np.cos(angles),np.sin(angles),color=TEAL,lw=3)
axs[0].set_title('Modulus alone permits a full circle')
for z,label,pos in [(1+0j,'1',(1.08,.07)),(complex(-.5,float(sqrt3)/2),'ω',(-.65,1.0)),(complex(-.5,-float(sqrt3)/2),'ω²',(-.72,-1.09))]:
    axs[1].scatter([z.real],[z.imag],s=90,color=GOLD);axs[1].text(*pos,label,fontsize=13)
axs[1].set_title('Cube equality would leave three factors')
note(fig,'Relative phase factors only; no plotted point is an evaluated gamma/arithmetic discrepancy.')
save(fig,'03_modulus_phase')

fig,axs=plt.subplots(1,3,figsize=(9.3,3.4),gridspec_kw={'width_ratios':[.7,1,1]})
for ax,cy,col in zip(axs,[[0],[1,4,2],[3,5,6]],[GRAY,TEAL,GOLD]):
    ax.axis('off');ax.set(xlim=(-1.4,1.4),ylim=(-1.4,1.4),aspect='equal')
    if len(cy)==1:ax.scatter([0],[0],s=700,facecolors='#f5f9fb',edgecolors=col);ax.text(0,0,'0',ha='center',va='center',fontsize=17)
    else:
        ps=[(np.cos(a),np.sin(a)) for a in [np.pi/2,np.pi/2+2*np.pi/3,np.pi/2+4*np.pi/3]]
        for i,(lab,pt) in enumerate(zip(cy,ps)):
            ax.scatter([pt[0]],[pt[1]],s=700,facecolors='#f5f9fb',edgecolors=col,zorder=3);ax.text(*pt,str(lab),ha='center',va='center',fontsize=16,zorder=4)
            nxt=ps[(i+1)%3];v=np.array(nxt)-np.array(pt);arrow(ax,np.array(pt)+.22*v,np.array(pt)+.77*v,col)
    ax.set_title('fixed point' if len(cy)==1 else 'three-cycle')
note(fig,'Exact label action ρ: k ↦ 4k mod 7. Diagram placement is schematic.')
save(fig,'04_seven_cover')

bs=np.arange(-8,9);cs=np.arange(-8,9);J=np.array([[pivot(b,c) for c in cs] for b in bs]);digits=7*J+2*bs[:,None]-3*cs[None,:]
assert np.all((digits>=0)&(digits<7))
fig=plt.figure(figsize=(9.2,3.8),layout='constrained');g=fig.add_gridspec(1,4,width_ratios=[1,.045,.2,1.3]);ax=fig.add_subplot(g[0,0]);ca=fig.add_subplot(g[0,1]);ax2=fig.add_subplot(g[0,3])
im=ax.imshow(J,origin='lower',extent=(-8.5,8.5,-8.5,8.5),cmap='RdBu',vmin=-6,vmax=6);fig.colorbar(im,cax=ca,label='ceiling pivot j')
ax.set(xlabel='integer c',ylabel='integer b',title='j = ceil((3c − 2b)/7)');ax.grid(False)
counts=np.bincount(digits.ravel(),minlength=7);ax2.bar(range(7),counts,color=TEAL);ax2.set(xlabel='unique residue digit k',ylabel='count in the declared finite box',xticks=range(7),title='Every digit stays in {0,…,6}')
checks['ceiling_plot']={'b':[-8,8],'c':[-8,8],'digit_counts':counts.tolist()}
save(fig,'05_ceiling')

fig,ax=plt.subplots(figsize=(8.8,3.3));cc=np.arange(-10,16);ww=np.array([weight(int(c)) for c in cc]);ax.bar(cc,ww,color=[GOLD if w==4 else TEAL for w in ww],width=.68)
ax.axhline(0,color=GRAY,lw=1);ax.set(xlabel='integer c',ylabel='smoothing weight w(c)',xticks=range(-10,16,5),yticks=[-1,0,4],ylim=(-1.6,4.8))
note(fig,'Weight 4 on multiples of five; weight −1 on the other four residues.')
save(fig,'06_smoothing')

fig=plt.figure(figsize=(9,4.8));ax=fig.add_subplot(111,projection='3d')
zz,pp=family(3)
for vals,col,marker,label in [(pp,TEAL,'x','108 pole points, order −1'),(zz,GOLD,'o','27 zero points, order 4')]:
    v=np.array(sorted(vals));ax.scatter(v[:,0],v[:,1],v[:,2],c=col,marker=marker,s=38 if marker=='o' else 23,alpha=.9,label=label)
ax.set(xlabel='integer a',ylabel='integer b',zlabel='integer c',xticks=[-3,-2,-1],yticks=[1,2,3],zticks=[16,20,25,30])
ax.view_init(elev=24,azim=-52);ax.set_box_aspect((1,1,1.6));ax.tick_params(labelsize=11)
note(fig,'Actual n = 3 subfamilies in a genuine three-coordinate chamber; no planar flattening.')
legend(fig,ax,2);save(fig,'07_chamber_3d')

fig,ax=plt.subplots(figsize=(8.5,4.0))
for label,col,marker in [('poles',TEAL,'x'),('zeros',GOLD,'o')]:
    recs=embedding[2][label];points=[complex(float(v['coordinate']['real']),float(v['coordinate']['imag'])) for v in recs]
    ax.scatter([z.real for z in points],[z.imag for z in points],s=60 if label=='zeros' else 40,c=col,marker=marker,label=f'{len(points)} '+label+(' (order 4)' if label=='zeros' else ' (order −1)'))
ax.set(aspect='equal',xlabel='Re λ',ylabel='Im λ');legend(fig,ax,2)
note(fig,'Finite actual n = 2 families. Decimal coordinates are rounded for plotting, not enclosed.')
save(fig,'08_complex_families')

fig,axs=plt.subplots(1,2,figsize=(9.2,3.5),layout='constrained');ns=np.arange(1,17)
axs[0].plot(ns,ns**3,'o-',color=GOLD,label='zero points: n³');axs[0].plot(ns,4*ns**3,'s-',color=TEAL,label='pole points: 4n³')
axs[0].set(xlabel='family parameter n',ylabel='distinct points',title='Different numbers of points')
axs[1].plot(ns,4*ns**3,'o-',color=NAVY,label='both multiplicity counts: 4n³');axs[1].set(xlabel='family parameter n',ylabel='total multiplicity',title='Equal positive and negative mass')
h0,l0=axs[0].get_legend_handles_labels();h1,l1=axs[1].get_legend_handles_labels();fig.legend(h0+h1,l0+l1,loc='upper center',bbox_to_anchor=(.5,-.02),ncol=3,frameon=False,fontsize=11)
save(fig,'09_family_counts')

fig,ax=plt.subplots(figsize=(8.8,3.6));x=np.geomspace(1,30,250);ax.loglog(x,x*x,color=TEAL,lw=2,label='normalized order-two profile r²');ax.loglog(x,x*x*x,color=GOLD,lw=2,label='normalized order-three profile r³')
ax.set(xlabel='illustrative scale r / r*',ylabel='illustrative normalized growth',xticks=[1,3,10,30]);note(fig,'Scaling profiles with constants set to one; not empirical divisor counts or theta samples.')
legend(fig,ax,2);save(fig,'10_growth_orders')

fig,axs=plt.subplots(1,2,figsize=(9.4,3.7),gridspec_kw={'width_ratios':[1.15,1],'wspace':.42})
heat(axs[0],jets,['E₀','E₁','E₂','E₃'],['w','w²','w³','w⁴'],'Exact coefficients of log E_g')
w=np.geomspace(.02,.7,220);L2=np.log1p(-w)+w+w*w/2;L3=L2+w**3/3;bound=w**4/(4*(1-w))
axs[1].loglog(w,abs(L3),color=TEAL,lw=2,label='|log E₃(w)| on real 0 < w < 1');axs[1].loglog(w,bound,'--',color=GOLD,label='analytic upper bound')
axs[1].set(xlabel='real w',ylabel='magnitude',title='The first remaining term has degree four')
legend(fig,axs[1],2);save(fig,'11_canonical_jets')

fig,axs=plt.subplots(1,2,figsize=(9.2,3.5),layout='constrained');T=np.geomspace(2,128,150)
axs[0].loglog(T,2/T,color=TEAL,lw=2);axs[0].set(xlabel='cutoff radius T',ylabel='illustrative log-tail bound',title='2A |z|⁴ / T with A = |z| = 1')
j=np.arange(1,11);axs[1].semilogy(j,np.ones(len(j)),color=RED,marker='s',label='genus 2: constant shell profile');axs[1].semilogy(j,2.**(-j),color=TEAL,marker='o',label='genus 3: summable shell profile')
axs[1].set(xlabel='dyadic shell index j',ylabel='illustrative upper profile',xticks=[1,3,5,7,9],title='Cubic counting × local remainder')
legend(fig,axs[1],2);note(fig,'Analytic scaling illustrations only; no numerical truncation of the infinite divisor product.')
save(fig,'12_tail_bound')

fig,ax=plt.subplots(figsize=(8.8,4));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,4.8))
box(ax,(.35,2.9),3.7,1.15,'Same full divisor','R / W_D = R₀ exp h',TEAL)
box(ax,(5.4,2.9),4.1,1.15,'Additional analytic identity','matching fourth log derivatives',GOLD)
box(ax,(2.8,.65),4.5,1.25,'Fourth derivative h⁽⁴⁾ = 0','h = α₁z + α₂z² + α₃z³',NAVY)
arrow(ax,(4.2,3.48),(5.23,3.48));arrow(ax,(7.3,2.76),(5.5,2.05))
note(fig,'Divisor matching alone leaves an arbitrary entire h. The fourth derivative is essential.')
save(fig,'13_ambiguity')

fig,ax=plt.subplots(figsize=(8.8,3.0));heat(ax,[[1,1,1],[-1,1,-1],[0,2,0]],['P(z)','P(−z)','sum'],['α₁z','α₂z²','α₃z³'],'Reflection cancels the odd polynomial terms')
save(fig,'14_reflection')

fig,ax=plt.subplots(figsize=(8.8,3.0));heat(ax,[[1,1,1],[0,2,3],[0,0,3],[0,0,6]],['constant term','coefficient of z','coefficient of z²','second derivative'],['α₁','α₂','α₃'],'Exact coefficients of P(z+1) − P(z)')
save(fig,'15_transition')

fig,axs=plt.subplots(1,2,figsize=(9.3,3.5),gridspec_kw={'width_ratios':[1.6,1],'wspace':.45})
heat(axs[0],[[Q(0),Q(-2,3),Q(-8,9)]],['3P(1/3) − P(1)'],['α₁','α₂','α₃'],'Exact conductor-three exponents')
axs[1].plot(np.cos(angles),np.sin(angles),color=GRAY,lw=1)
for z,lab in [(1+0j,'1'),(complex(-.5,float(sqrt3)/2),'ω'),(complex(-.5,-float(sqrt3)/2),'ω²')]:
    axs[1].scatter([z.real],[z.imag],s=100,color=GOLD);axs[1].text(z.real*.72,z.imag*.72,lab,ha='center',va='center',fontsize=13)
axs[1].set(aspect='equal',xlim=(-1.2,1.2),ylim=(-1.2,1.2),xticks=[],yticks=[],title='Relative lift factors cube to 1');axs[1].grid(False)
save(fig,'16_cube')

fig,ax=plt.subplots(figsize=(9,4));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,4.8))
box(ax,(.3,2.7),4.15,1.35,'Regularity on the complex plane','canonical meromorphic divisor cancellation',TEAL)
box(ax,(5.55,2.7),4.15,1.35,'Periodic relative multiplier','nonzero • based • principal norm',RED)
box(ax,(2.8,.35),4.4,1.3,'Arithmetic identification','U_Γ = U_alg remains open',RED)
ax.plot([4.6,5.35],[3.35,3.35],':',color=RED,lw=2);ax.text(5,3.85,'extra obligations',ha='center',fontsize=11,color=RED)
arrow(ax,(7.6,2.55),(6.4,1.85),RED)
note(fig,'Plane divisor repair does not establish periodic descent or the original scalar comparison.')
save(fig,'17_conjugation')

record={'status':'passed finite checks','scope':'Exact declared finite integer/Fraction identities and numerical coordinate illustrations. Source proofs, not finite tests, supply infinite claims. No arithmetic gamma equality or numerical infinite-product certificate.',
 'command':'python generate_figures.py','software':{'Python':sys.version.split()[0],'NumPy':np.__version__,'Matplotlib':matplotlib.__version__},
 'checks':checks,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'figure_files':files}
(ROOT/'finite_control.json').write_text(json.dumps(record,indent=2)+'\n')
if args.record_output:
    target=ROOT/args.record_output;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'figures':18,'exact_fraction_triples':tested,'family_n_range':[1,16],'coordinate_digits':80,'status':record['status']}))
