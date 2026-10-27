#!/usr/bin/env python3
"""Render 32 mathematical plates from exact model data. One axes per figure.

Vector PDF and SVG outputs are authoritative illustrations. PNG previews are
supplied for convenient reuse. No empirical observations are synthesized.
"""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
from itertools import product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from matplotlib import rcParams
from atlas_models import model_data,corner_criterion,quadratic,transvection

rcParams.update({'font.size':11,'axes.titlesize':12,'axes.labelsize':11,
                 'xtick.labelsize':10,'ytick.labelsize':10,'pdf.fonttype':42,
                 'svg.hashsalt':'P11-B05-atlas','savefig.dpi':150})
D=model_data()


def new(diagram=False):
    fig=plt.figure(figsize=(7.2,4.2))
    ax=fig.add_axes([.025,.10,.95,.82] if diagram else [.17,.22,.79,.61])
    if diagram:
        ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis('off')
    return fig,ax


def txt(ax,x,y,s,size=11,ha='center',va='center',**kw):
    return ax.text(x,y,s,fontsize=size,ha=ha,va=va,**kw)


def box(ax,x,y,w,h,s,size=11,ls='solid'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06,rounding_size=0.08',
                              fill=False,linewidth=1,linestyle=ls))
    return txt(ax,x+w/2,y+h/2,s,size)


def arrow(ax,a,b,label=None,offset=(0,.3),ls='solid'):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','linewidth':1.25,'linestyle':ls})
    if label:txt(ax,(a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,10)


def axes_clean(ax):
    ax.spines[['top','right']].set_visible(False)


def table_diagram(headers,rows,colwidths=None):
    fig,ax=new(True)
    tab=ax.table(cellText=rows,colLabels=headers,cellLoc='center',loc='center',colWidths=colwidths)
    tab.auto_set_font_size(False);tab.set_fontsize(11);tab.scale(1,2.2)
    return fig,ax


def V01():
    fig,ax=new(True)
    box(ax,.2,3.7,2.7,1.2,'Supplied source\n'+r'$\rho,\ d_\rho$')
    box(ax,3.7,3.7,2.6,1.2,'Actual arithmetic\nwitness '+r'$R(d_\rho,\pi)$')
    box(ax,7.1,3.7,2.6,1.2,'Characterization\n'+r'$\pi\simeq\mathrm{LLC}(\rho)$')
    arrow(ax,(2.95,4.3),(3.65,4.3));arrow(ax,(6.35,4.3),(7.05,4.3))
    box(ax,.3,.6,2.5,1.25,'H1–H4\nfinite supplied data')
    box(ax,3.75,.6,2.5,1.25,'Conjecture 66\nexistence open',ls='dashed')
    box(ax,7.1,.6,2.6,1.25,'H5 for this same '+r'$\pi$'+'\n+ characterization')
    for x in [1.55,5,8.4]:arrow(ax,(x,1.9),(x,3.6))
    return fig,ax


def V02():
    fig,ax=new(True)
    for x,label,member in [(2.5,'Realizes the packet',r'$\pi_1$'),(7.5,'Passes H5',r'$\pi_2$')]:
        ax.add_patch(Circle((x,3.2),1.45,fill=False,linewidth=1.3));txt(ax,x,3.2,member,22);txt(ax,x,5,label,12)
    txt(ax,5,.75,r'$\{\pi_1\}\cap\{\pi_2\}=\varnothing$',20)
    txt(ax,5,1.55,'Two separately successful candidates do not supply one witness.',11)
    return fig,ax


def V03():
    fig,ax=new(True)
    box(ax,.15,3.6,2.7,1.2,r'$H_3\times H_3$'+'\n'+r'$27\cdot27=729$')
    box(ax,3.65,3.6,2.7,1.2,'Quotient by\n'+r'$\{(z,z^{-1})\}$')
    box(ax,7.15,3.6,2.7,1.2,'Balanced product\n'+r'$729/3=243$')
    arrow(ax,(2.9,4.2),(3.6,4.2));arrow(ax,(6.4,4.2),(7.1,4.2))
    box(ax,1,1,3.1,1.2,'One shared center\nnot two unrelated centers')
    box(ax,5.6,1,3.5,1.2,'Heisenberg degree\n'+r'$3\cdot3=9$')
    txt(ax,5,.3,'Orthogonal factors commute; the actual extensions are inputs.',10)
    return fig,ax


def V04():
    fig,ax=new()
    for r in D['binder_roots']:
        n=r['level']
        for j,v in enumerate(r['roots']):
            ax.annotate(str(v),(n,j),xytext=(0,11),textcoords='offset points',ha='center',fontsize=11)
            if n>1:ax.annotate('',xy=(n-1,j),xytext=(n,j),arrowprops={'arrowstyle':'->'})
    for j in [0,1]:ax.scatter(range(1,6),[j]*5,s=65)
    ax.set_xticks(range(1,6),[r'$3^1$',r'$3^2$',r'$3^3$',r'$3^4$',r'$3^5$'])
    ax.set_yticks([0,1],['branch +1','branch −1']);ax.set_ylim(-.45,1.65);ax.set_xlim(.7,5.3)
    ax.set_xlabel('modulus (arrows are reduction maps)');axes_clean(ax)
    return fig,ax


def V05():
    fig,ax=new()
    triples=list(product([1,2],repeat=3));pq=list(product(range(3),repeat=2))
    yes=[];no=[]
    for i,t in enumerate(triples):
        for j,r in enumerate(pq):
            (yes if corner_criterion(t+r) else no).append((j,i))
    ax.scatter(*zip(*no),marker='x',s=50,label='excluded in this corner')
    ax.scatter(*zip(*yes),marker='o',s=75,label='admissible')
    ax.set_xticks(range(9),[f'{p},{q}' for p,q in pq]);ax.set_yticks(range(8),[','.join(map(str,t)) for t in triples]);ax.invert_yaxis()
    ax.set_xlabel('(p, q)');ax.set_ylabel('(u, v, w)');ax.legend(loc='upper center',bbox_to_anchor=(.5,1.2),ncol=2,fontsize=9)
    ax.set_xlim(-.5,8.5);ax.set_ylim(7.5,-.5);axes_clean(ax)
    return fig,ax


def V06():
    fig,ax=new(True)
    ys=[4.5,3,1.5];labels=['deep congruence units','whole compact\ncharacter','noncompact generator']
    lhs=[r'$\theta|_{U^m}$',r'$\theta|_{H^1}$',r'$\Lambda(\varpi)$']
    for y,l,s in zip(ys,labels,lhs):
        box(ax,.15,y-.4,3,.85,l);arrow(ax,(3.2,y),(4.2,y));box(ax,4.25,y-.4,2.25,.85,s,15)
    box(ax,7.4,2,2.3,2,'One full\ninducing\nrepresentation\n'+r'$\Lambda$')
    for y in ys:arrow(ax,(6.55,y),(7.35,3))
    txt(ax,5,.2,'A deep equality cannot fill in the two larger-domain certificates.',11)
    return fig,ax


def V07():
    fig,ax=new()
    yes=[];no=[]
    for t in D['trace_grid']['valuations']:
        for r in D['trace_grid']['depths']:(yes if t+r>=1 else no).append((r,t))
    ax.scatter(*zip(*yes),marker='o',s=110,label='all units invisible')
    ax.scatter(*zip(*no),marker='x',s=85,label='visible monomial exists')
    ax.set_xticks(range(1,7));ax.set_yticks(range(-4,3));ax.set_xlabel('unit depth r');ax.set_ylabel(r'$\tau = v_t(\mathrm{trace})$')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.23),ncol=2,fontsize=9)
    ax.set_xlim(.6,6.4);ax.set_ylim(-4.5,2.5);axes_clean(ax)
    return fig,ax


def V08():
    fig,ax=new()
    ax.plot([1,2],[24,4],'o-',label='odd: p = 3, rank 9')
    ax.plot([1,2,3],[60,18,3],'s--',label='dyadic: rank 8')
    for xs,vs,offset in [([1,2],[24,4],(8,8)),([1,2,3],[60,18,3],(7,7))]:
        for x,v in zip(xs,vs):ax.annotate(str(v),(x,v),xytext=offset,textcoords='offset points')
    ax.set_xticks([1,2,3]);ax.set_xlabel('defining-sequence position');ax.set_ylabel('positive defining level');ax.set_ylim(0,69);ax.set_xlim(.85,3.35)
    ax.legend(loc='upper right');axes_clean(ax);return fig,ax


def V09():
    fig,ax=new();rows=D['capacities'];ds=[r['d'] for r in rows]
    ax.plot(ds,[r['source'] for r in rows],'o-',label='source: 2d')
    ax.plot(ds,[r['host'] for r in rows],'s--',label='original host: '+r'$2^d-2$')
    for r in rows:ax.annotate(str(r['host']),(r['d'],r['host']),xytext=(6,4),textcoords='offset points')
    ax.set_xticks(ds,[f"{r['d']}\nrank {r['rank']}" for r in rows]);ax.set_xlabel('packet count d and arithmetic rank');ax.set_ylabel('binary quotient dimension')
    ax.set_xlim(.8,5.35);ax.set_ylim(-1.2,33);ax.legend(loc='upper left');axes_clean(ax);return fig,ax


def V10():
    fig,ax=new(True)
    box(ax,.2,3.75,2.4,1.1,r'$H=C_2$'+'\ncharacter degree 1')
    box(ax,3.75,3.75,2.5,1.1,r'$M=C_6$'+'\ninduced degree 3')
    box(ax,7.4,3.75,2.4,1.1,r'$G=C_{12}$'+'\ninduced degree 6')
    arrow(ax,(2.65,4.3),(3.7,4.3),'index 3',offset=(0,.55));arrow(ax,(6.3,4.3),(7.35,4.3),'index 2',offset=(0,.55))
    for j in range(3):
        for i in range(2):
            x=1.8+j*2.5+i*.72;box(ax,x,1.2,.55,.6,str(i+2*j),12)
    txt(ax,5,.5,'Six cosets, whether induced directly or in two stages.',11)
    return fig,ax


def V11():
    fig,ax=new();names=['rho','End rho','Ad rho'];y=list(range(3))
    for key,off,label,mark in [('swan',-.22,'Swan','o'),('ordinary',0,'ordinary Artin','s'),('psi1_exponent',.22,'psi1 exponent','^')]:
        xs=[D['conductors'][n][key] for n in names]
        ax.scatter(xs,[i+off for i in y],marker=mark,s=60,label=label)
        for i,x in enumerate(xs):ax.annotate(str(x),(x,i+off),xytext=(5,0),textcoords='offset points',va='center',fontsize=9)
    ax.set_yticks(y,[r'$\rho$',r'$\mathrm{End}\,\rho$',r'$\mathrm{Ad}\,\rho$']);ax.set_xlim(0,260);ax.set_ylim(2.65,-.65)
    ax.set_xlabel('specified invariant or normalized exponent');ax.legend(loc='upper center',bbox_to_anchor=(.5,1.2),ncol=3,fontsize=9);axes_clean(ax)
    return fig,ax


def V12():
    fig,ax=new()
    for e,r,marker in [(1,8/3,'x'),(3,8,'o'),(9,24,'o')]:
        ax.annotate(f"e = {e}, r = {'8/3' if e==1 else int(r)}",(e,r),xytext=(10,8),textcoords='offset points')
    ax.scatter([1],[8/3],marker='x',s=90);ax.scatter([3,9],[8,24],marker='o',s=90)
    ax.set_xticks([1,3,9]);ax.set_xlabel('principal period e (must divide 9)');ax.set_ylabel('required leading level r = 24e/9')
    ax.set_xlim(.3,11.5);ax.set_ylim(0,29);axes_clean(ax);return fig,ax


def V13():
    fig,ax=new();xs=[0,1,2];ys=[1,8,72]
    bars=ax.bar(xs,ys,width=.55)
    ax.bar_label(bars,labels=['1 trivial','8','72'],padding=4)
    ax.set_xticks(xs,['0 (trivial)','1','2']);ax.set_xlabel('break after the recorded splitting extension');ax.set_ylabel('character multiplicity in End rho');ax.set_ylim(0,86)
    ax.text(.03,.87,r'$8\cdot1+72\cdot2=152$',transform=ax.transAxes,fontsize=16);axes_clean(ax);return fig,ax


def V14():
    fig,ax=new()
    ax.axhline(232,linestyle='--',linewidth=1,label='retained source: 232')
    ax.plot([4,10],[232,244],'o',markersize=10)
    ax.annotate('necessary pass\nnot identification',(4,232),xytext=(-12,-36),textcoords='offset points',ha='center',fontsize=10)
    ax.annotate('excluded by this invariant',(10,244),xytext=(0,13),textcoords='offset points',ha='center',fontsize=10)
    ax.set_xticks([4,10]);ax.set_xlim(1,13);ax.set_ylim(222,253);ax.set_xlabel('critical level c, conditional on the actual-order certificate');ax.set_ylabel('ordinary self-pair conductor');ax.legend(loc='upper left',fontsize=10);axes_clean(ax);return fig,ax


def V15():
    fig,ax=new(True)
    for y,name,vals,d in [(4.5,'Full profile',[240,36,3],6),(2.5,'Skipped profile',[240,39],4)]:
        txt(ax,.15,y+.65,name,12,ha='left');x=.15
        for k,val in enumerate(vals):
            w=8.4*val/279
            ax.add_patch(Rectangle((x,y-.2),w,.6,fill=False,hatch=['','///','xxx'][k]))
            if val>10:txt(ax,x+w/2,y+.1,str(val),11)
            else:txt(ax,9.0,y+.12,'3',11);arrow(ax,(8.9,y+.12),(x+w/2,y+.12))
            x+=w
        txt(ax,9.1,y-.6,'D = '+str(d),12)
    txt(ax,4.5,.9,r'$240+36+3=240+39=279$',18)
    txt(ax,4.5,.25,r'$2\cdot133+6=2\cdot134+4=272$',14)
    return fig,ax


def V16():
    fig,ax=new(True)
    for start,m,title in [(0,4,'rank 9 / fibre order 4'),(5.5,3,'rank 3 / fibre order 3')]:
        txt(ax,start+2.05,5.7,title,12)
        for x in range(m):
            y=4.65-x*.9
            txt(ax,start+.45,y,str(x),12);txt(ax,start+3.6,y,str(x),12)
            end=4.65-((9 if m==4 else 3)*x%m)*.9
            arrow(ax,(start+.7,y),(start+3.3,end))
        txt(ax,start+2.05,.55,'bijective' if m==4 else 'all map to zero',12)
    return fig,ax


def V17():
    fig,ax=new(True)
    box(ax,.3,3.7,2.8,1.2,r'$|A|=8$'+'\nradical order 2')
    box(ax,3.7,3.7,2.65,1.2,r'$|A/R|=4$'+'\nquotient by radical')
    box(ax,7,3.7,2.65,1.2,r'$\dim M=2$'+'\nnot '+r'$\sqrt{8}$')
    arrow(ax,(3.15,4.3),(3.65,4.3));arrow(ax,(6.4,4.3),(6.95,4.3))
    box(ax,.7,1.1,8.6,1.2,r'$S_3\downarrow C_3:\quad 2=(\mathrm{orbit}\ 2)(\mathrm{multiplicity}\ 1)(\mathrm{degree}\ 1)$',13)
    txt(ax,5,.35,'A second copy of one noncommuting Weyl plane is not an independent factor.',10)
    return fig,ax


def V18():
    fig,ax=new(True)
    xs=[1.65,5,8.35]
    for x,a,phase,word in zip(xs,[0,1,2],[r'$\zeta_3$',r'$1$',r'$\zeta_3^2$'],['excluded','scalar test passes','excluded']):
        box(ax,x-1.35,3.2,2.7,1.8,r'$\nu^{'+str(a)+'}$'+'\nremaining scalar\n'+phase,14)
        txt(ax,x,2.6,word,11)
    box(ax,2.6,.35,4.8,1.05,r'$\operatorname{Hom}(\theta^{\prime},\pi_F^0)\ne0$'+'\nstill requires a proof',12,ls='dashed')
    arrow(ax,(5,2.2),(5,1.45),ls='dashed')
    return fig,ax


def V19():
    fig,ax=new(True)
    box(ax,.4,3.2,3.65,1.7,'Abstract action on '+r'$\mathbf{F}_3^2$'+'\n'+r'$A(x,y)=(-y,x)$'+'\norder 4, symplectic',13)
    box(ax,5.8,3.2,3.8,1.7,'Homomorphism '+r'$C_4\to C_{3^r}$'+'\n'+r'$4x=0\ (\mathrm{mod}\ 3^r)$'+'\nonly x = 0',13)
    arrow(ax,(4.15,4.05),(5.7,4.05),'not automatic',offset=(0,.9),ls='dashed')
    txt(ax,5,1.5,'A nontrivial finite action may fail in a specified native normalizer.',12)
    txt(ax,5,.65,'This excludes that action mechanism, not every allowed arithmetic host.',11)
    return fig,ax


def V20():
    fig,ax=table_diagram(['finite subgroup','q(e)','q(f)','q(e+f)','order 2','order 4'],
                [['D8',0,0,1,5,2],['Q8',1,1,1,1,6]],[.23,.13,.13,.17,.17,.17])
    txt(ax,5,5.65,r'$[X,Z]=[iX,iZ]=-I$',17)
    txt(ax,5,.3,'Same scalar pushout, different marked finite subgroups.',12)
    return fig,ax


def V21():
    fig,ax=new();matrix=D['section_cocycle_difference']
    for v,w in product(range(4),repeat=2):
        ax.text(w+.18,v,str(matrix[v][w]),va='center',fontsize=11)
    for value,marker in [(0,'o'),(1,'x')]:
        pts=[(w,v) for v,w in product(range(4),repeat=2) if matrix[v][w]==value]
        ax.scatter(*zip(*pts),marker=marker,s=140)
    ax.set_xticks(range(4),['0','e','f','e+f']);ax.set_yticks(range(4),['0','e','f','e+f']);ax.set_xlabel('w');ax.set_ylabel('v');ax.set_xlim(-.5,3.6);ax.set_ylim(3.5,-.5)
    ax.set_title('Change only the chosen section value at e+f');axes_clean(ax);return fig,ax


def V22():
    fig,ax=new(True)
    box(ax,.25,3.4,4.1,1.9,'Transported marking\nsource subgroup is input\nhost image chosen through F',12)
    box(ax,5.65,3.4,4.1,1.9,'Fixed native marking\nboth subgroups are inputs\nF must preserve both',12)
    box(ax,.25,.75,4.1,1.45,'Scalar-pushout attachment\nwith capacity and recovery inputs',11)
    box(ax,5.65,.75,4.1,1.45,'Additional native square test\ncan obstruct equal capacity',11)
    arrow(ax,(2.3,3.3),(2.3,2.3));arrow(ax,(7.7,3.3),(7.7,2.3))
    return fig,ax


def V23():
    fig,ax=new(True);ax.set_xlim(-1,19);ax.set_ylim(-1.5,10)
    for value,marker in [(0,'o'),(1,'x')]:
        pts=[(start+(v%8),7-v//8) for start,name in [(0,'plus'),(10,'minus')]
             for v,q in enumerate(D['gauss6'][name]['values']) if q==value]
        ax.scatter(*zip(*pts),marker=marker,s=40,label='q = '+str(value))
    for start,name,label in [(0,'plus','Arf 0: 36 zeros'),(10,'minus','Arf 1: 28 zeros')]:
        txt(ax,start+3.5,9,label,12)
        txt(ax,start+3.5,-.8,'G(q) = '+str(D['gauss6'][name]['gauss']),12)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.05),ncol=2,fontsize=9)
    return fig,ax


def V24():
    fig,ax=new(True)
    rows=[]
    for HD in [4,6,8]:
        for ha in [0,1]:rows.append([str(HD),str(ha)]+['yes' if HD>6 or HD==6 and ha==sa else 'no' for sa in [0,1]])
    tab=ax.table(cellText=rows,colLabels=['host dim','host Arf','source Arf 0','source Arf 1'],cellLoc='center',loc='center',colWidths=[.21,.21,.29,.29]);tab.auto_set_font_size(False);tab.set_fontsize(11);tab.scale(1,1.9)
    txt(ax,5,6,'Source dimension is 6; the embedding may be freely chosen.',11)
    return fig,ax


def V25():
    fig,ax=new(True);ys=[4.95,3.75,2.55,1.35];labels=['0','e','f','e+f'];images=[0,1,3,2]
    for i,y in enumerate(ys):
        txt(ax,1,y,labels[i]+'\nq = '+str(quadratic(i,1)),11)
        txt(ax,8.75,y,labels[i]+'\nq0 = '+str(quadratic(i,1,2)),11)
        arrow(ax,(2,y),(7.7,ys[images[i]]))
    txt(ax,5,5.85,r'$T_e(x,y)=(x+y,y)$',16)
    txt(ax,5,.2,'0 and e stay fixed; f and e+f are exchanged.',11)
    return fig,ax


def V26():
    rows=[]
    for d in D['defect_gate']:
        rows.append([['0','e','f','e+f'][d['a']],d['q_a'],d['mismatches'], 'works' if d['q_a']==0 else 'fails'])
    fig,ax=table_diagram(['defect a','q(a)','mismatched vectors','T_a correction'],rows,[.22,.17,.31,.30])
    txt(ax,5,5.65,r'$q_0=q+B(a,-)$',16);txt(ax,5,.4,'When q(a) = 1, Arf changes and the obstruction is genuine.',11)
    return fig,ax


def V27():
    lab=['0','e','f','e+f'];data=D['odd_action'];rows=[]
    for g in range(3):rows.append([['1','g','g²'][g],lab[data['deltas'][g]],lab[data['g_u'][g]],lab[data['corrected'][g]]])
    fig,ax=table_diagram(['group element','delta_g','g u','u + delta_g + g u'],rows,[.24,.2,.2,.36])
    txt(ax,5,5.7,r'$u=\sum_h\delta_h=e$',16);txt(ax,5,.35,r'$g(x,y)=(y,x+y)$'+'   on '+r'$\mathbf{F}_2^2$',13)
    return fig,ax


def V28():
    fig,ax=table_diagram(['candidate u','u + s u','remaining delta_s'],[[x,'0','e'] for x in ['0','e','f','e+f']],[.34,.33,.33])
    txt(ax,5,5.65,'C2 acts trivially; the cocycle has delta_s = e.',12)
    txt(ax,5,.35,'Every permitted coboundary is zero. None removes this cocycle.',11)
    return fig,ax


def V29():
    fig,ax=new()
    m=D['projective_phase']['cocycle_exponents']
    for g,h in product(range(3),repeat=2):
        ax.annotate(str(m[g][h]),(h,g),xytext=(12,0),textcoords='offset points',va='center')
    for value,marker in [(0,'o'),(3,'s')]:
        pts=[(h,g) for g,h in product(range(3),repeat=2) if m[g][h]==value]
        ax.scatter(*zip(*pts),marker=marker,s=190)
    ax.set_xticks(range(3));ax.set_yticks(range(3));ax.set_xlim(-.5,2.6);ax.set_ylim(2.5,-.5);ax.set_xlabel('h');ax.set_ylabel('g');ax.set_title('Scalar cocycle exponents modulo 9');axes_clean(ax);return fig,ax


def V30():
    fig,ax=new(True)
    for i in range(6):box(ax,.35+1.6*i,4.1,1.35,1.1,'lift '+str(i+1)+'\n'+r'$q_i=?$',12)
    box(ax,.35,1.25,2.7,1.4,'Same candidate\nrepresented center\ncommutator data',11)
    box(ax,3.65,1.25,2.7,1.4,'All prescribed\nsection products\n—not only six squares',11)
    box(ax,6.95,1.25,2.7,1.4,'Honest phases\nand allowed\ntransport maps',11)
    for x in [1.7,5,8.3]:arrow(ax,(x,4.0),(x,2.75))
    txt(ax,5,.45,'The six question marks are deliberate: no native bit is fabricated.',11)
    return fig,ax


def V31():
    fig,ax=new(True)
    box(ax,.25,3.5,3.7,1.5,'Admissible monomial tower\nfull inducing character\nclassical induction + descent',11)
    box(ax,6,3.5,3.75,1.5,'Direct arithmetic recursion\nparameter + full type\nstated refinement inputs',11)
    box(ax,.25,.8,3.7,1.2,'Source-defined candidate\n'+r'$\pi_{\mathrm{AI}}$',13)
    box(ax,6,.8,3.75,1.2,'Type-defined candidate\n'+r'$\pi_{\mathrm{type}}$',13)
    arrow(ax,(2.1,3.4),(2.1,2.1));arrow(ax,(7.85,3.4),(7.85,2.1));arrow(ax,(4.05,1.4),(5.9,1.4),'identification\nnot supplied',offset=(0,.85),ls='dashed')
    return fig,ax


def V32():
    rows=[['restricted constructions','written arguments retained'],['finite corrections','proved conditionally; exact models'],['general realization','OPEN'],['same-candidate H5','OPEN'],['corrected-character occurrence','OPEN'],['fixed native marking','OPEN when independently required']]
    fig,ax=table_diagram(['reusable result or endpoint','current boundary'],rows,[.45,.55])
    txt(ax,5,6,'One proof ledger, not a percentage of a conjecture.',12)
    return fig,ax


FUNCTIONS=[globals()['V'+str(i).zfill(2)] for i in range(1,33)]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    records=[]
    for i,fn in enumerate(FUNCTIONS,1):
        fig,ax=fn();stem=f'V{i:02d}'
        # Deterministic metadata, including for each embedded vector figure.
        fig.savefig(a.output/(stem+'.pdf'),metadata={'CreationDate':None,'ModDate':None,'Creator':'Paper XI exact atlas renderer'})
        fig.savefig(a.output/(stem+'.svg'),metadata={'Date':None,'Creator':'Paper XI exact atlas renderer'})
        fig.savefig(a.output/(stem+'.png'),dpi=150)
        # Each mathematical plate uses exactly one axes (no subplot compression).
        records.append({'plate':stem,'axes':len(fig.axes),'outputs':{ext:hashlib.sha256((a.output/(stem+'.'+ext)).read_bytes()).hexdigest() for ext in ['pdf','svg','png']}})
        plt.close(fig)
    (a.output/'ATLAS_MODEL_DATA.json').write_text(json.dumps(D,indent=2,sort_keys=True)+'\n')
    (a.output/'FIGURE_MANIFEST.json').write_text(json.dumps({'figures':records,'count':len(records),'matplotlib_version':matplotlib.__version__},indent=2)+'\n')
    print(f'Rendered {len(records)} single-axes figures to {a.output}')
if __name__=='__main__':main()
