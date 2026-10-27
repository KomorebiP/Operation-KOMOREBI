"""Reproducible illustrations of exact Paper IV models. No theorem search."""
from pathlib import Path
from fractions import Fraction as Q
from math import factorial
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
    'axes.spines.top':False,'axes.spines.right':False,
    'axes.labelcolor':'#212B34','text.color':'#212B34',
    'pdf.fonttype':42,'savefig.facecolor':'white'})
COLORS = ['#245D60','#B77946','#576F9D','#94709C']
records = []

def save(fig,name,scope):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.16)
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight',pad_inches=.16,dpi=160)
    plt.close(fig)
    records.append({'figure':name,'scope':scope})

# The dots are exact residue labels, not sampled analytic coefficients.
fig,ax=plt.subplots(figsize=(7.1,2.7),layout='constrained')
for m in range(18):
    j=m%3
    ax.scatter(m,j,s=110,color=COLORS[j],zorder=3)
    ax.text(m,j+.24,str(m),ha='center',fontsize=9)
for j in range(3):ax.axhline(j,color='#DCE6E5',lw=1,zorder=0)
ax.set(ylim=(-.45,2.65),xlim=(-.6,17.6),yticks=[0,1,2],
    yticklabels=[r'$j=0$',r'$j=1$',r'$j=2$'],xlabel='Exponent m',
    title='The N = 3 root filter assigns each exponent to one lane')
ax.set_xticks([])
save(fig,'root_filter','Exact m mod 3 labels for m=0,...,17.')

J=np.zeros((4,4),dtype=int)
for j in range(3):J[j+1,j]=1
J[0,3]=-1
assert np.array_equal(np.linalg.matrix_power(J,4),-np.eye(4,dtype=int))
fig,(ax,bx)=plt.subplots(1,2,figsize=(7.1,3.1),layout='constrained',
    gridspec_kw={'width_ratios':[1.1,1]})
pos=np.array([[-1,1],[1,1],[1,-1],[-1,-1]])
for i,p in enumerate(pos):
    ax.scatter(*p,s=640,facecolor='#EEF3F2',edgecolor=COLORS[0],zorder=4)
    ax.text(*p,r'$e_%d$'%i,ha='center',va='center',zorder=5)
for j in range(4):
    a=pos[j];b=pos[(j+1)%4]
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,
        shrinkA=19,shrinkB=19,color=COLORS[0] if j<3 else COLORS[1],lw=1.7))
    c=(a+b)/2
    offset=np.array([0,.23]) if j==0 else np.array([.24,0]) if j==1 else np.array([0,-.26]) if j==2 else np.array([-.27,0])
    ax.text(*(c+offset),'−1' if j==3 else '+1',ha='center',va='center')
ax.set(xlim=(-1.65,1.65),ylim=(-1.65,1.65),aspect='equal',title='One sign around the cycle')
ax.axis('off')
bx.imshow(J,cmap='RdBu',vmin=-1,vmax=1)
for i in range(4):
    for j in range(4):bx.text(j,i,str(J[i,j]),ha='center',va='center',color='white' if J[i,j] else '#212B34')
bx.set(xticks=range(4),yticks=range(4),xlabel='Source column',ylabel='Target row',title=r'$J_4^4=-I$')
save(fig,'signed_cycle','Exact integer J4 matrix and action. J4^4=-I checked.')

def reciprocal(N,n):
    a=[Q((-1)**k,factorial(N*k)) for k in range(n+1)]
    b=[Q(1)]
    for j in range(1,n+1):b.append(-sum(a[k]*b[j-k] for k in range(1,j+1)))
    return [int(b[j]*factorial(N*j)) for j in range(n+1)]
coeff=reciprocal(2,4)
assert coeff==[1,1,5,61,1385]
fig,ax=plt.subplots(figsize=(7.1,2.55),layout='constrained')
ax.axis('off')
columns=['n = 0','n = 1','n = 2','n = 3','n = 4']
table=ax.table(cellText=[['1','1','5','61','1385'],
    ['1','1/2','5/24','61/720','1385/40320']],
    colLabels=columns,rowLabels=[r'$P_{2,n}(1)$',r'$[z^{2n}]\sec z$'],
    loc='center',cellLoc='center',colWidths=[.145]*5)
table.auto_set_font_size(False);table.set_fontsize(11);table.scale(1,2)
for (r,c),cell in table.get_celld().items():
    cell.set_edgecolor('#DCE6E5')
    if r==0:cell.set_facecolor('#EEF3F2')
ax.set_title('The factorial normalization carries the same coefficients in two forms',pad=15)
save(fig,'reciprocal_normalization','Exact Fraction inversion of cos z through z^8. P=(1,1,5,61,1385).')

fig,(ax,bx)=plt.subplots(1,2,figsize=(7.1,3.0),layout='constrained')
tau=np.sqrt(2)*np.pi*(np.arange(3)+.5)
for k in range(4):
    z=(1j**k)*tau
    ax.scatter(z.real,z.imag,s=55,color=COLORS[k])
ax.axhline(0,color='#BECAC9',lw=.7);ax.axvline(0,color='#BECAC9',lw=.7)
ax.set(xlabel=r'Re z',ylabel=r'Im z',aspect='equal',title=r'$D_4(z)=\cos(z/\sqrt{2})\cosh(z/\sqrt{2})$')
lam=tau**4
bx.scatter(lam,np.zeros(3),s=65,color=COLORS[0]);bx.axhline(0,color='#BECAC9',lw=.7)
for m,l in enumerate(lam):bx.annotate('m = '+str(m),(l,0),xytext=(0,15),textcoords='offset points',ha='center',fontsize=9)
bx.set(xscale='log',ylim=(-.4,.6),yticks=[],xlabel=r'Reduced zero $\lambda=\tau_m^4$ (log scale)',title='Four zeros become one orbit zero')
save(fig,'zero_orbits','Exact order-four zeros +/-tau_m and +/-i tau_m, m=0,1,2, rendered in floating coordinates. No claim about other N.')

fig,(ax,bx)=plt.subplots(1,2,figsize=(7.1,2.9),layout='constrained')
counts=np.arange(1,41);lam=(np.pi*(np.arange(40)+.5))**2
for m,b,target in [(1,ax,.5),(2,bx,1/6)]:
    sums=np.cumsum(lam**(-m))
    b.plot(counts,sums,color=COLORS[0],lw=2,label='Finite partial sum')
    b.axhline(target,color=COLORS[1],linestyle='--',lw=1.3,label='Exact infinite value')
    b.set(xlabel='Number of retained reduced zeros',ylabel=r'$\sum_{k<M}\lambda_k^{-%d}$'%m,
        title=r'$\sigma_%d=%s$'%(m,'1/2' if m==1 else '1/6'))
    b.legend(fontsize=8,loc='lower right')
save(fig,'zero_moments','First 40 order-two reduced zeros. Curves are finite numerical partial sums, dashed targets 1/2 and 1/6 follow from exact coefficients/product theorem.')

fig,ax=plt.subplots(figsize=(7.1,2.5),layout='constrained')
x=np.linspace(0,2,201)
ax.plot(x,x,color=COLORS[0],lw=2,label=r'$P_{2,1}(r)=r$')
ax.plot(x,x*(3*x+2),color=COLORS[1],lw=2,label=r'$P_{2,2}(r)=r(3r+2)$')
ax.scatter([1,1],[1,5],color=[COLORS[0],COLORS[1]],s=50,zorder=4)
ax.set(xlabel='Reciprocal order r',ylabel='Block coefficient',title='An exact parameter polynomial defines an entire family')
ax.legend(loc='upper left',fontsize=9)
save(fig,'parameter_polynomials','Exact N=2 coefficient polynomials evaluated on r in [0,2]. Formula identities, not fitted curves.')

(ROOT/'FIGURE_MODELS.json').write_text(json.dumps({'status':'PASS','figures':records,
    'new_theorems':0,'finite_examples_only':True,'generator':Path(__file__).name},indent=2)+'\n')
print('Generated',len(records),'figures')
