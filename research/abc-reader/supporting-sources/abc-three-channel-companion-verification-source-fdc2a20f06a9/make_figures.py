from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)

INK='#17202A'; MUTED='#5D6D7E'; BLUE='#2E86AB'; TEAL='#2A9D8F'; ORANGE='#F4A261'; RED='#E76F51'; PURPLE='#7D3C98'; GOLD='#C49A00'; PALE='#F7F7F3'


def save(fig,name):
    fig.savefig(FIG/f'{name}.pdf',bbox_inches='tight')
    fig.savefig(FIG/f'{name}.png',dpi=220,bbox_inches='tight')
    plt.close(fig)


def periodogram(a,b,c):
    s=np.array([a*c,b*c,-a*b],dtype=np.complex128)
    sh=np.array([sum(s[j]*np.exp(2j*np.pi*j*k/3) for j in range(3)) for k in range(3)])
    return s, np.abs(sh)**2

# 1. Exact flatness vs near miss.
a,b=3,125
c=a+b
s_exact,p_exact=periodogram(a,b,c)
s_miss,p_miss=periodogram(a,b,c+1)
fig,axes=plt.subplots(1,2,figsize=(10.8,4.4))
x=np.arange(3)
axes[0].bar(x,p_exact/p_exact.max(),color=[BLUE,TEAL,ORANGE],edgecolor='black')
axes[0].set_xticks(x,['$k=0$','$k=1$','$k=2$'])
axes[0].set_ylim(0,1.12); axes[0].set_ylabel('normalized periodogram')
axes[0].set_title(r'Exact relation: $3+125=128$')
axes[0].text(1,1.04,'perfectly flat',ha='center',weight='bold',color=TEAL)
axes[1].bar(x,p_miss/p_miss.max(),color=[BLUE,TEAL,ORANGE],edgecolor='black')
axes[1].set_xticks(x,['$k=0$','$k=1$','$k=2$'])
axes[1].set_ylim(0,1.12); axes[1].set_ylabel('normalized periodogram')
axes[1].set_title(r'Near miss: test $c=129$')
axes[1].text(1,1.04,'flatness is broken',ha='center',weight='bold',color=RED)
fig.suptitle('The additive equation is a three-frequency flatness condition',fontsize=16,weight='bold')
fig.tight_layout(rect=[0,0,1,.92]); save(fig,'01_periodogram_flatness')

# 2. Perfect reconstruction matrix.
A=a*a+a*b+b*b
C=np.array([[a*c,b*c,-a*b],[-a*b,a*c,b*c],[b*c,-a*b,a*c]],dtype=float)
U=C/A; G=U@U.T
fig,axes=plt.subplots(1,2,figsize=(10.5,4.5))
im0=axes[0].imshow(U,cmap='coolwarm',vmin=-1,vmax=1)
axes[0].set_title(r'analysis block $\mathcal{C}/A$')
axes[0].set_xticks(range(3),['channel 0','channel 1','channel 2'],rotation=25,ha='right')
axes[0].set_yticks(range(3),['phase 0','phase 1','phase 2'])
for i in range(3):
    for j in range(3): axes[0].text(j,i,f'{U[i,j]:.3f}',ha='center',va='center',fontsize=9)
im1=axes[1].imshow(G,cmap='viridis',vmin=0,vmax=1)
axes[1].set_title(r'Gram matrix $(\mathcal{C}/A)(\mathcal{C}/A)^T$')
axes[1].set_xticks(range(3));axes[1].set_yticks(range(3))
for i in range(3):
    for j in range(3): axes[1].text(j,i,f'{G[i,j]:.3f}',ha='center',va='center',color='white' if G[i,j]>.5 else 'black')
fig.colorbar(im0,ax=axes[0],fraction=.046,pad=.04);fig.colorbar(im1,ax=axes[1],fraction=.046,pad=.04)
fig.suptitle('The circulant block is an exact perfect-reconstruction operator',fontsize=16,weight='bold')
fig.tight_layout(rect=[0,0,1,.92]); save(fig,'02_perfect_reconstruction')

# 3. Eisenstein geometry.
fig,ax=plt.subplots(figsize=(7.2,6.4))
# triangular lattice
for m in range(-5,6):
    for n in range(-5,6):
        x=m+n/2; y=n*math.sqrt(3)/2
        ax.scatter(x,y,s=10,color='#BFC9CA',zorder=1)
# use a scaled example z=a+b*zeta, a=3,b=5 to fit
ag,bg=3,5
zx=ag+bg/2; zy=bg*math.sqrt(3)/2
ax.arrow(0,0,zx,zy,width=.025,head_width=.22,length_includes_head=True,color=BLUE,zorder=4)
ax.arrow(0,0,zx,-zy,width=.018,head_width=.18,length_includes_head=True,color=ORANGE,zorder=4)
rad=math.sqrt(ag*ag+ag*bg+bg*bg)
theta=np.linspace(0,2*np.pi,500)
ax.plot(rad*np.cos(theta),rad*np.sin(theta),'--',color=MUTED,lw=1.4,label=r'$|z|^2=A$')
ax.text(zx+.18,zy+.18,r'$z=a+b\zeta$',fontsize=13,color=BLUE)
ax.text(zx+.18,-zy-.35,r'$\bar z$',fontsize=13,color=ORANGE)
ax.text(.1,.15,'0',fontsize=11)
ax.set_aspect('equal');ax.set_xlim(-6.3,7);ax.set_ylim(-6.1,6.1);ax.axis('off')
ax.set_title('The nonconstant DFT channels are Eisenstein conjugates',fontsize=16,weight='bold')
ax.legend(loc='lower left',frameon=False)
save(fig,'03_eisenstein_geometry')

# 4. Harmonic flow diagram.
fig,ax=plt.subplots(figsize=(11,6.0));ax.axis('off')
boxes=[
(.10,.55,'$z=a+b\\zeta$\nEisenstein phase',BLUE),
(.34,.76,'$z^2,\\ \\bar z^2$\nnonconstant DFT modes',TEAL),
(.34,.31,'$2z^3=L+3\\sqrt{-3}\\,abc$\nthird harmonic',ORANGE),
(.62,.55,'$A=a^2+ab+b^2$\n$L=(a-b)(a+2b)(2a+b)$',PURPLE),
(.88,.55,'$c_4=16A$\n$c_6=32L$\n$\\Delta=16a^2b^2c^2$',RED),
]
for x,y,text,col in boxes:
    ax.text(x,y,text,ha='center',va='center',fontsize=11.5,bbox=dict(boxstyle='round,pad=.52',facecolor=col+'20',edgecolor=col,lw=1.8),zorder=3)
def arrow(i,j,label='',dx=0,dy=0):
    x1,y1,_,_=boxes[i];x2,y2,_,_=boxes[j]
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',lw=1.8,color=MUTED,shrinkA=42,shrinkB=42),zorder=1)
    if label: ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha='center',fontsize=9,color=MUTED,bbox=dict(facecolor='white',edgecolor='none',pad=.8),zorder=4)
arrow(0,1,'square',-.01,.035);arrow(0,2,'cube',-.01,-.04);arrow(1,3,'norm',0,.045);arrow(2,3,'real and imaginary parts',0,-.045);arrow(3,4,'Frey invariants',0,.045)
ax.set_xlim(0,1);ax.set_ylim(0,1)
ax.set_title('The Frey invariants appear as harmonics of one phase packet',fontsize=16,weight='bold',pad=20)
save(fig,'04_harmonic_to_frey')

# 5. Isogeny fiber diagram.
fig,ax=plt.subplots(figsize=(11,6.2));ax.axis('off')
points=[(.13,.74,'$P_{bc}$\n$(4bc,\\ 4bc(a+2b))$',BLUE),(.13,.45,'$-P_{ab}$',TEAL),(.13,.18,'$-P_{ac}$',ORANGE),(.56,.46,'$\\phi$\nquotient by $\\langle T\\rangle$',PURPLE),(.87,.46,'$(4A,-4L)$\nFrey invariant point',RED)]
for x,y,text,col in points:
    ax.text(x,y,text,ha='center',va='center',fontsize=11.8,bbox=dict(boxstyle='round,pad=.52',facecolor=col+'20',edgecolor=col,lw=1.8),zorder=3)
# torsion orbit arrows on left
ax.annotate('',xy=(.13,.50),xytext=(.13,.68),arrowprops=dict(arrowstyle='->',lw=1.6,color=MUTED,shrinkA=25,shrinkB=25));ax.text(.18,.59,'+$T$',color=MUTED,fontsize=11)
ax.annotate('',xy=(.13,.23),xytext=(.13,.39),arrowprops=dict(arrowstyle='->',lw=1.6,color=MUTED,shrinkA=22,shrinkB=22));ax.text(.18,.31,'+$T$',color=MUTED,fontsize=11)
ax.annotate('',xy=(.17,.69),xytext=(.17,.22),arrowprops=dict(arrowstyle='->',lw=1.2,color=MUTED,connectionstyle='arc3,rad=-.52',shrinkA=20,shrinkB=20));ax.text(.29,.46,'+$T$',color=MUTED,fontsize=11)
for yy in [.74,.45,.18]:
    ax.annotate('',xy=(.49,.46),xytext=(.23,yy),arrowprops=dict(arrowstyle='->',lw=1.5,color=MUTED,shrinkA=25,shrinkB=28),zorder=1)
ax.annotate('',xy=(.80,.46),xytext=(.63,.46),arrowprops=dict(arrowstyle='->',lw=1.8,color=MUTED,shrinkA=28,shrinkB=32),zorder=1)
ax.text(.13,.05,'three points in one rational 3-torsion orbit',ha='center',fontsize=10.5,color=MUTED)
ax.set_xlim(0,1);ax.set_ylim(0,1)
ax.set_title('The nonlinear analysis map is the standard rational 3-isogeny',fontsize=16,weight='bold',pad=20)
save(fig,'05_isogeny_fiber')

# 6. Support atlases for record triple.
ar,br=2,3**10*109;cr=ar+br
Ar=ar*ar+ar*br+br*br;Lr=(ar-br)*(ar+2*br)*(2*ar+br)
fac0=sp.factorint(ar*br*cr);facA=sp.factorint(Ar);facL=sp.factorint(abs(Lr)//2)
fig,ax=plt.subplots(figsize=(11,5.6));ax.axis('off')
sets=[(.18,.54,'original atlas',fac0,BLUE),(.50,.54,'Eisenstein norm atlas',facA,TEAL),(.82,.54,'cubic harmonic atlas',facL,ORANGE)]
for x,y,title,fac,col in sets:
    ax.add_patch(plt.Circle((x,y),.16,facecolor=col+'18',edgecolor=col,lw=2))
    ax.text(x,y+.12,title,ha='center',fontsize=11,weight='bold',color=col)
    lines=[]
    for p,e in fac.items(): lines.append(f'{p}' + (f'^{e}' if e>1 else ''))
    text='\n'.join(lines[:7])
    if len(lines)>7:text+='\n...'
    ax.text(x,y-.01,text,ha='center',va='center',fontsize=10)
ax.text(.34,.25,r'$\gcd(A,abc)=1$',ha='center',fontsize=12,weight='bold')
ax.text(.66,.25,r'$\gcd(A,L)=1$ for this example',ha='center',fontsize=12,weight='bold')
ax.text(.50,.09,'Only the forced dyadic factor is shared between the original and harmonic atlases.',ha='center',fontsize=10.5,color=MUTED)
ax.set_title('The record triple in three nearly disjoint prime atlases',fontsize=16,weight='bold',pad=20)
save(fig,'06_support_atlases')

# 7. Claim-status architecture.
fig,ax=plt.subplots(figsize=(11,6));ax.axis('off')
cols=[(.17,'Source-supported principles',BLUE,[
'discrete CDF recovery','spectral filtering','periodogram = |DFT|²','analytic compound recursion']),
(.50,'Proved and checked here',TEAL,[
'flat three-mode periodogram','perfect-reconstruction block','Smith form (1,A,A²)','Eisenstein factorization','Frey 3-isogeny identities']),
(.83,'Still proposed or open',RED,[
'canonical transformed transfer','double-atlas expansion','uniform occupancy bound','any proof of abc'])]
for x,title,col,items in cols:
    ax.text(x,.85,title,ha='center',fontsize=13,weight='bold',color=col)
    for j,item in enumerate(items):
        y=.69-j*.14
        ax.text(x,y,item,ha='center',va='center',fontsize=10.5,bbox=dict(boxstyle='round,pad=.42',facecolor=col+'18',edgecolor=col,lw=1.4))
ax.annotate('',xy=(.39,.48),xytext=(.28,.48),arrowprops=dict(arrowstyle='->',lw=2,color=MUTED))
ax.annotate('',xy=(.72,.48),xytext=(.61,.48),arrowprops=dict(arrowstyle='->',lw=2,color=MUTED))
ax.text(.50,.06,'The companion keeps these three levels separate throughout.',ha='center',fontsize=11,color=MUTED)
ax.set_title('Claim boundary used in the verification',fontsize=16,weight='bold',pad=20)
save(fig,'07_claim_status')

# 8. Worked-example scale plot.
df=pd.read_csv(ROOT/'tables'/'worked_examples.csv')
fig,ax=plt.subplots(figsize=(9.6,4.8))
x=np.arange(len(df)); labels=[f"{int(a)}+{int(b)}" for a,b in zip(df.a,df.b)]
ax.bar(x,np.log10(df.A),color=[BLUE,TEAL,ORANGE,PURPLE,RED,GOLD],edgecolor='black')
ax.set_xticks(x,labels,rotation=35,ha='right');ax.set_ylabel(r'$\log_{10}A$')
ax.set_title('The middle Smith scale across the worked examples')
ax.grid(axis='y',alpha=.18);fig.tight_layout();save(fig,'08_worked_smith_scales')

print(json.dumps({'figure_pairs':8,'record_A':Ar,'record_L_factors':{str(k):v for k,v in facL.items()}},indent=2))
