"""Computed geometry and exact inverse plates for SF-DISCOVERY-110."""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from coupled_lab import coupled_odd_derivatives
from coupled_inverse import recover_rational_scales
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures_v11';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':14,
                    'axes.labelsize':12,'xtick.labelsize':10,'ytick.labelsize':10,
                    'axes.spines.top':False,'axes.spines.right':False,
                    'pdf.fonttype':42,'savefig.facecolor':'white'})
GREEN='#256b59';RED='#b14b37';BLUE='#386e99';GRAY='#53645e'
record={'checkpoint':'SF-DISCOVERY-110','figures':[]}
def save(fig,name,data):
    files=[]
    for extension in ['pdf','png']:
        path=OUT/(name+'.'+extension)
        fig.savefig(path,dpi=180,bbox_inches='tight',pad_inches=.15)
        files.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    record['figures'].append({'name':name,'files':files,**data})
    plt.close(fig)

def reduction_geometry():
    q=np.linspace(.045,.955,250);b=np.linspace(.045,.955,250)
    X,Y=np.meshgrid(q,b);a,r=.6,.4
    value=(X*X-Y*Y)*(X*Y-a*r)
    fig,ax=plt.subplots(figsize=(8.0,5.25),layout='constrained')
    color=ax.pcolormesh(X,Y,value,shading='auto',cmap='BrBG',norm=TwoSlopeNorm(vmin=-.20,vcenter=0,vmax=.20))
    ax.plot(q,q,color=GREEN,lw=2.8,label=r'$q=b$')
    good=q>=a*r/.955
    ax.plot(q[good],a*r/q[good],color=RED,lw=2.8,label=r'$qb=ar=6/25$')
    ax.scatter([.2],[.7],s=150,marker='*',c=BLUE,edgecolor='white',linewidth=.8,zorder=5)
    ax.annotate('Worked order-one pair',(.2,.7),xytext=(.08,.87),fontsize=11,
                arrowprops={'arrowstyle':'-','color':BLUE},color=BLUE)
    ax.set(xlim=(.045,.955),ylim=(.045,.955),xlabel='Self scale q',ylabel='Self scale b',
           title='Exactly two surfaces give component rescaling')
    ax.legend(loc='lower right',framealpha=.96)
    bar=fig.colorbar(color,ax=ax,pad=.025)
    bar.set_label(r'Signed factor $(q^2-b^2)(qb-ar)$')
    save(fig,'coupled_07_reduction_geometry',{'fixed_scales':{'a':'3/5','r':'2/5'},
         'exact_zero_sets':['q=b','qb=ar'],'colors':'Floating evaluation of an exactly factored polynomial; values outside color limits saturate.'})

def inverse_plate():
    scales=(F(1,5),F(2,5),F(3,5),F(7,10))
    U,V=coupled_odd_derivatives(*scales,last=3)
    jet=[U[1]/6,V[1]/6,U[2]/120,V[2]/120,U[3]/5040,V[3]/5040]
    recovered=recover_rational_scales(*jet)
    u1,v1,u2,v2,u3,v3=jet;p,k=3*u1,3*v1
    x=scales[0]**2;x2=k*p/x
    u3_alt=p*(x2*x2*u2+p*p*u1*v1+(p*p/x2)**2*v2)/7
    fig,axes=plt.subplots(1,3,figsize=(10.7,4.7),layout='constrained',gridspec_kw={'width_ratios':[1.05,1.1,1]})
    ax=axes[0];ax.axis('off');ax.set_title('1  Read the local coefficients',loc='left',pad=18)
    lines=[('Cubic terms',r'$p=3u_1=2/25$',r'$k=3v_1=21/50$'),
           ('Fifth-degree terms',r'$q^2\in\{1/25,\;21/25\}$',r'Both q candidates are admissible')]
    for y,(title,l1,l2) in zip([.78,.36],lines):
        ax.text(.02,y,title,color=GREEN,fontweight='bold',transform=ax.transAxes,fontsize=12)
        ax.text(.02,y-.12,l1,transform=ax.transAxes,fontsize=13)
        ax.text(.02,y-.24,l2,transform=ax.transAxes,fontsize=10.5)
    ax=axes[1]
    ax.bar([0,1],[float(u3),float(u3_alt)],color=[GREEN,RED],width=.6)
    ax.axhline(float(u3),color=BLUE,lw=1.7,ls='--',label='Observed coefficient')
    ax.set_xticks([0,1],[r'$q^2=1/25$',r'$q^2=21/25$'])
    ax.set_title('2  The seventh term selects',loc='left',pad=18)
    ax.set_ylabel(r'Predicted coefficient of $z^7$ in U')
    ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    ax.legend(fontsize=9,loc='upper left')
    ax=axes[2]
    ax.barh(range(4),[float(x) for x in recovered],color=GREEN,height=.58)
    ax.set_yticks(range(4),['q','r','a','b']);ax.invert_yaxis();ax.set_xlim(0,.94)
    for n,value in enumerate(recovered):
        ax.text(float(value)+.035,n,str(value),va='center',fontsize=12)
    ax.set_title('3  Recover all four scales',loc='left',pad=18)
    ax.set_xlabel('Recovered parameter');ax.grid(axis='x',alpha=.15)
    save(fig,'coupled_08_inverse',{'parameters':list(map(str,scales)),
          'ordinary_taylor_jet':list(map(str,jet)), 'q_squared_candidates':[str(x),str(x2)],
          'predicted_u3':[str(u3),str(u3_alt)],'recovered':list(map(str,recovered)),
          'arithmetic':'All data exact rational; only graphical positions are rounded.'})

if __name__=='__main__':
    reduction_geometry();inverse_plate()
    record['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT/'evidence/v11/structure_figures.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'figures':len(record['figures'])}))
