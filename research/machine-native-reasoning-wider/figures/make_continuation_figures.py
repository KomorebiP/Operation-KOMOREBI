#!/usr/bin/env python3
"""Reproducible analytical figures; no model activations or empirical claims.

Coordinates depict the exact declared examples. Every boxed label is checked
against its allocated rectangle after rendering, before assets are written.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
HERE=Path(__file__).resolve().parent
CHECKS=[]

def box(ax,x,y,w,h,text,size=11):
    patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.015',fill=False,linewidth=1.2)
    ax.add_patch(patch)
    label=ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size)
    ax.figure._fit_records=getattr(ax.figure,'_fit_records',[])+[(ax,(x,y,w,h),label)]

def save(fig,name):
    fig.canvas.draw();renderer=fig.canvas.get_renderer();local=[]
    for ax,(x,y,w,h),t in getattr(fig,'_fit_records',[]):
        p0=ax.transData.transform((x,y));p1=ax.transData.transform((x+w,y+h))
        b=t.get_window_extent(renderer)
        fits=b.x0>=p0[0]+2 and b.x1<=p1[0]-2 and b.y0>=p0[1]+2 and b.y1<=p1[1]-2
        local.append({'text':t.get_text(),'fits_with_two_pixel_margin':bool(fits)})
        if not fits:raise ValueError(f'Text does not fit {name}: {t.get_text()!r}')
    CHECKS.append({'figure':name,'boxed_text_checks':local,'status':'PASS'})
    fig.savefig(HERE/(name+'.pdf'),bbox_inches='tight',pad_inches=.12,
                metadata={'Title':name.replace('_',' '),'Creator':'Matplotlib; exact finite example','CreationDate':None})
    fig.savefig(HERE/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)

def support():
    fig,ax=plt.subplots(figsize=(7.0,3.4));ax.set(xlim=(0,10),ylim=(0,4));ax.axis('off')
    box(ax,.2,1.30,2.15,1.25,'State $s$\nSafe\nNot ended',11)
    box(ax,7.3,2.45,2.25,.85,'Goal $g$\nSafe ending',11)
    box(ax,7.3,.35,2.25,.85,'State $b$\nUnsafe',11)
    ax.annotate('',xy=(7.25,2.85),xytext=(2.4,2.05),arrowprops={'arrowstyle':'->','lw':1.5})
    ax.annotate('',xy=(7.25,.8),xytext=(2.4,1.75),arrowprops={'arrowstyle':'->','lw':1.5,'linestyle':'--'})
    ax.text(4.65,2.72,r'$1-\epsilon$',ha='center',fontsize=13)
    ax.text(4.65,.78,r'$\epsilon>0$',ha='center',fontsize=13)
    ax.text(5,3.7,r'Nominal row: $s\to g$ with probability 1',ha='center',fontsize=12)
    ax.text(5,-.05,r'Row distance: $d_{\mathrm{TV}}=\epsilon$'+'\n'+r'Sure ending fails for every $\epsilon>0$',ha='center',fontsize=11)
    save(fig,'support_margin')

def migration():
    fig,ax=plt.subplots(figsize=(7.0,3.4));ax.set(xlim=(0,10),ylim=(0,4));ax.axis('off')
    entries=[(.2,'Display $y$',2,0),(3.65,'Display + target',4,1),(7.1,'All three bits',8,2)]
    for x,title,states,bits in entries:
        box(ax,x,1.0,2.65,1.65,f'{title}\n{states} records\n{bits} extra '+('bit' if bits==1 else 'bits'),10.5)
    ax.annotate('',xy=(3.55,1.85),xytext=(2.95,1.85),arrowprops={'arrowstyle':'->','lw':1.4})
    ax.annotate('',xy=(7.0,1.85),xytext=(6.4,1.85),arrowprops={'arrowstyle':'->','lw':1.4})
    ax.text(3.22,2.98,'Add calibration $s$',ha='center',fontsize=10.5)
    ax.text(6.7,2.98,'Also observe $n$',ha='center',fontsize=10.5)
    ax.text(5,3.7,'A new task changes the required distinctions',ha='center',fontsize=12)
    ax.text(5,.35,'Eight source histories $(b,s,n)$; display $y=b\\oplus s$.\nExtra bits are measured relative to the original display record.',ha='center',fontsize=10.5)
    save(fig,'migration_fibres')

def closure():
    fig,ax=plt.subplots(figsize=(7.0,3.6));ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off')
    for x,t in [(1.2,'0\nSeed'),(3.6,'1\nDerived'),(6.0,'2\nDerived'),(8.4,'3\nNot derived')]:
        box(ax,x-.83,3.65,1.66,.95,t,10)
    for x1,x2 in [(2.1,2.7),(4.5,5.1)]:
        ax.annotate('',xy=(x2,4.12),xytext=(x1,4.12),arrowprops={'arrowstyle':'->','lw':1.4})
    xs=[1.7,4.6,6.55,8.55]
    headers=['Reported set','Replay\nvalid','All rules\nsatisfied','Exact\nclosure']
    for x,cell in zip(xs,headers):ax.text(x,2.94,cell,ha='center',va='center',fontsize=10.5,fontweight='bold')
    ax.plot([.4,9.6],[2.49,2.49],linewidth=1)
    rows=[('{0, 1}','Yes','No','No'),('{0, 1, 2, 3}','No','Yes','No'),('{0, 1, 2}','Yes','Yes','Yes')]
    for r,row in enumerate(rows):
        for x,cell in zip(xs,row):ax.text(x,2.12-r*.60,cell,ha='center',va='center',fontsize=10.5)
    ax.text(5,.12,'Replay excludes unsupported additions.\nSaturation excludes missing consequences.',ha='center',fontsize=10.5)
    save(fig,'closure_contract')

if __name__=='__main__':
    support();migration();closure()
    (HERE/'CONTINUATION_FIGURE_DATA.json').write_text(json.dumps({
        'support_margin':{'states':['s','g','b'],'safe':['s','g'],'goal':['g'],'perturbed_end_row':{'g':'1-epsilon','b':'epsilon'},'assumption':'0 < epsilon < 1'},
        'migration_fibres':{'source_histories':8,'attained_records':[2,4,8],'supplementary_bits':[0,1,2]},
        'closure_contract':{'nodes':4,'seeds':[0],'rules':[[[0],1],[[1],2]],'least_closure':[0,1,2]},
        'layout_checks':CHECKS
    },indent=2)+'\n')
