"""Exact, reproducible figures for the 1.8.0 visual edition.

All geometry is vector output. Data plots read the committed finite examples.
The cube is a genuine 3D view of eight F_2^3 states, not a continuous solution set.
Run from any directory: python scripts/design_figures.py
"""
from __future__ import annotations
import csv
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Polygon, PathPatch
from matplotlib.path import Path as MPath
from matplotlib import font_manager
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from proof_path_theory import load_proof_field, unique_and_dag_certificate, Representation, TaskRequirement, compression_report
OUT=ROOT/'docs'/'figures'; OUT.mkdir(parents=True,exist_ok=True)
PINE='#24564F'; INK='#1B3330'; MUTED='#637570'; GOLD='#A56A21'; RUST='#AB5842'; BLUE='#436483'
PALE='#EDF3F0'; CREAM='#F6F2E9'; LINE='#BCCAC4'; MIST='#DEE8E2'; WHITE='#FFFFFF'
plt.rcParams.update({'font.family':'Lato','font.size':10,'text.color':INK,
 'mathtext.fontset':'stix','axes.labelcolor':INK,'axes.edgecolor':LINE,
 'xtick.color':MUTED,'ytick.color':MUTED,'pdf.fonttype':42,'ps.fonttype':42,
 'figure.facecolor':'white','axes.facecolor':'white','axes.spines.top':False,
 'axes.spines.right':False,'savefig.dpi':200})
# Do not silently substitute another font and change the measured layout.
font_manager.findfont('Lato', fallback_to_default=False)
FIXED=datetime(2026,10,19,tzinfo=timezone.utc)
AUDIT={'edition':'1.8.0','figures':{},'checks':{}}

# x and y coordinates are inches, so layout dimensions and type sizes agree.
def canvas(h=3.8):
    f=plt.figure(figsize=(6.25,h))
    ax=f.add_axes([0,0,1,1]); ax.set(xlim=(0,6.25),ylim=(0,h));ax.axis('off')
    return f,ax

def txt(ax,x,y,s,size=10,ha='left',va='center',color=INK,weight='normal',**kw):
    return ax.text(x,y,s,fontsize=size,ha=ha,va=va,color=color,weight=weight,linespacing=1.35,**kw)

def rule(ax,x1,y1,x2,y2,color=LINE,lw=.8,ls='-',**kw):
    ax.plot([x1,x2],[y1,y2],color=color,lw=lw,ls=ls,**kw)

def arrow(ax,a,b,color=PINE,lw=1.35,ls='-',rad=0,style='-|>',z=1):
    p=FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=10,linewidth=lw,
                     color=color,linestyle=ls,connectionstyle=f'arc3,rad={rad}',zorder=z)
    ax.add_patch(p);return p

def node(ax,x,y,label,kind='core',r=.19,size=11):
    col={'core':PINE,'side':GOLD,'blocked':RUST,'open':BLUE,'neutral':MUTED}[kind]
    if kind in ['blocked','open']:
        p=Rectangle((x-r,y-r),2*r,2*r,fill=False,edgecolor=col,lw=1.2,linestyle='--' if kind=='open' else '-',zorder=3)
    else:p=Circle((x,y),r,facecolor=PINE if kind=='core' else WHITE,edgecolor=col,lw=1.25,zorder=3)
    ax.add_patch(p);txt(ax,x,y,label,size=size,ha='center',color=WHITE if kind=='core' else col,zorder=4)

def gate(ax,x,y,label='AND',color=PINE):
    ax.add_patch(Polygon([(x-.22,y),(x,y+.18),(x+.22,y),(x,y-.18)],facecolor=WHITE,edgecolor=color,lw=1.05,zorder=4))
    txt(ax,x,y,label,7.3,ha='center',color=color,zorder=5)

def band(ax,x,y,w,h,fc=PALE):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor='none',zorder=-1))

def note(ax,x,y,s,color=MUTED,size=9.2):return txt(ax,x,y,s,size,color=color)

def save(f,stem,meaning):
    f.canvas.draw()
    # Reject figure-level clipping of text. Text overlap is also inspected in rendered pages.
    bb=f.bbox
    out=[]
    for ax in f.axes:
        for t in ax.texts:
            if not t.get_visible() or not t.get_text():continue
            # 3D texts are projected by a separate renderer and checked on the final page.
            if hasattr(t,'get_position_3d'): continue
            box=t.get_window_extent(f.canvas.get_renderer())
            if box.x0 < bb.x0-1 or box.y0 < bb.y0-1 or box.x1 > bb.x1+1 or box.y1 > bb.y1+1:
                out.append(t.get_text())
    if out:raise RuntimeError(f'{stem}: text outside figure: {out}')
    f.savefig(OUT/(stem+'.pdf'),transparent=(stem=='cover_field'),metadata={'Title':meaning,'Author':'Komorebi P.','CreationDate':FIXED,'ModDate':FIXED})
    f.savefig(OUT/(stem+'.png'),dpi=200)
    AUDIT['figures'][stem]={'width_inches':round(f.get_figwidth(),3),'height_inches':round(f.get_figheight(),3),'meaning':meaning,'text_inside_canvas':True}
    plt.close(f)


def field_geometry(ax,base=0,labels=True,compact=False):
    # The actual example: A -> D, {A,D} -> L1, L1 -> L2 -> B,
    # D -> E -> C, and the uncertified candidate A -> F.
    y=base+1.7; xs=[.45,1.60,3.13,4.42,5.78]
    arrow(ax,(xs[0]+.2,y),(xs[1]-.2,y))
    arrow(ax,(xs[1]+.2,y),(2.38,y))
    arrow(ax,(2.82,y),(xs[2]-.2,y))
    # Conjunctive premise A enters a separate AND gate from above.
    rule(ax,xs[0],y+.2,xs[0],y+.72,color=PINE,lw=1.1)
    rule(ax,xs[0],y+.72,2.60,y+.72,color=PINE,lw=1.1)
    arrow(ax,(2.60,y+.72),(2.60,y+.19))
    gate(ax,2.60,y)
    for x1,x2 in [(xs[2],xs[3]),(xs[3],xs[4])]:arrow(ax,(x1+.20,y),(x2-.20,y))
    for x,l in zip(xs,['$A$','$D$','$L_1$','$L_2$','$B$']):node(ax,x,y,l)
    if labels:
        for x,l in zip(xs,['premise','definition','lemma','lemma','target']):txt(ax,x,y+.36 if l=='definition' else y-.36,l,9,ha='center',color=MUTED)
    # The lower branch is certified discovery material but not needed for B.
    ey=base+.52
    arrow(ax,(xs[1],y-.2),(xs[1],ey+.18),color=GOLD)
    node(ax,xs[1],ey,'$E$',kind='side')
    arrow(ax,(xs[1]+.2,ey),(3.13-.20,ey),color=GOLD)
    node(ax,3.13,ey,'$C$',kind='side')
    if labels:
        txt(ax,xs[1],ey-.35,'example',9,ha='center',color=MUTED)
        txt(ax,3.13,ey-.35,'boundary',9,ha='center',color=MUTED)
    # Failed route is an archive annotation, not a certified deduction.
    fy=base+3.13
    arrow(ax,(xs[0],y+.77),(xs[0],fy-.21),color=RUST,ls='--')
    node(ax,xs[0],fy,'$F$',kind='blocked')
    if labels:txt(ax, .88, fy, 'failed candidate; not a proof step',9.3,color=RUST)


def theory_map():
    f,ax=canvas(4.75)
    rows=[('01','FIELD','What can be derived?',r'Certified rules and an explicit record of failure.'),
          ('02','REALIZATION','Can local descriptions fit together?',r'Restrictions, whole supports, fibers and witnesses.'),
          ('03','MEMORY','What survives compression?',r'One decoder per task; retained and lost distinctions.'),
          ('04','INQUIRY','What changes during review?',r'Provenance, shared error, audit capacity and depth.'),
          ('05','EXECUTION','What can be checked independently?',r'Finite records, exact examples and scoped formal evidence.')]
    for i,(num,title,q,body) in enumerate(rows):
        y=4.25-.88*i
        txt(ax,.12,y,num,21,color=PINE,weight='bold')
        txt(ax,.82,y+.12,title,8.3,color=PINE,weight='bold')
        txt(ax,.82,y-.09,q,13,weight='bold')
        txt(ax,.82,y-.37,body,9.5,color=MUTED)
        if i<4:rule(ax,.82,y-.55,6.1,y-.55)
    save(f,'fig_00_theory_map','Five reading routes through the monograph')


def architecture():
    f,ax=canvas(3.7)
    txt(ax,.10,3.42,'ONE ARCHIVE, DIFFERENT QUESTIONS',8.8,color=PINE,weight='bold')
    # Three explicit projections, not an asserted universal hierarchy.
    band(ax,.12,2.47,6.0,.60,CREAM)
    txt(ax,.33,2.78,r'$\mathcal{P}=(V,\mathcal{J},A,T,\tau,\mathcal{E},\mathbf{v},\mathbf{c})$',16)
    txt(ax,5.85,2.78,'declared field',9,ha='right',color=MUTED)
    titles=['CERTIFICATE','LOCAL MODELS','TASK REPRESENTATION']
    questions=['Does the target follow?','Can the views agree?','What can be recovered?']
    formulas=[r'$A\vdash B$',r'$\Gamma(\mathcal{M}_F)$',r'$q=d_q\circ C$']
    bodies=['Certified nodes and rules.','Rules on complete supports.','One decoder across archives.']
    for i,(t,q,eq,b) in enumerate(zip(titles,questions,formulas,bodies)):
        x=.15+i*2.06
        arrow(ax,(3.12,2.44),(x+.92,1.99),color=LINE,lw=1)
        txt(ax,x,1.79,t,8.2,color=PINE,weight='bold')
        txt(ax,x,1.46,q,10.7,weight='bold')
        txt(ax,x+.87,1.01,eq,19,ha='center')
        txt(ax,x,.52,b,8.8,color=MUTED)
        if i<2:rule(ax,x+1.96,.4,x+1.96,1.8)
    note(ax,.15,.13,'These are different mathematical tasks, not interchangeable certificates.')
    save(f,'fig_01_architecture','The same proof field supports distinct verification, realization and recovery questions')


def and_core():
    field=load_proof_field(ROOT/'examples/and_dag.json'); c=unique_and_dag_certificate(field)
    assert c.node_ids==frozenset(['A','D','L1','L2','B'])
    AUDIT['checks']['and_dag_core']=sorted(c.node_ids)
    f,ax=canvas(4.65);field_geometry(ax,base=.90)
    band(ax,.08,.10,6.08,.65,PALE)
    txt(ax,.30,.45,r'$K=\{A,D,L_1,L_2,B\}$',14)
    txt(ax,5.97,.45,'5 nodes  /  4 certified rules',9.6,ha='right',color=PINE)
    save(f,'fig_02_and_dag_core','Exact least core of examples/and_dag.json; the AND premise is retained')


def alternative():
    f,ax=canvas(3.15)
    node(ax,.55,1.68,'$A$');node(ax,5.65,1.68,'$B$')
    for y,label,cost,col in [(2.45,r'$L_{\rm short}$','storage 1',PINE),(.88,r'$L_{\rm rich}$','storage 3',GOLD)]:
        arrow(ax,(.73,1.78 if y>1 else 1.58),(2.33,y),color=col)
        band(ax,2.35,y-.26,1.43,.52,PALE if col==PINE else CREAM)
        txt(ax,3.06,y,label,14,ha='center',color=col)
        arrow(ax,(3.80,y),(5.45,1.78 if y>1 else 1.58),color=col)
        txt(ax,3.06,y-.47,cost,9.6,ha='center',color=col)
    txt(ax,.36,.22,'Both routes certify B. The objective chooses what else is worth retaining.',9.9,color=MUTED)
    save(f,'fig_03_alternative_hypergraph','Two alternative certified routes with stored costs one and three')


def set_cover():
    M=np.array([[1,1,0,0],[0,1,1,0],[0,0,1,1],[1,0,0,1]])
    opts=[s for k in range(5) for s in itertools.combinations(range(4),k) if k and M[list(s)].sum(0).min()>0]
    assert min(map(len,opts))==2
    AUDIT['checks']['set_cover_minimum']=2
    f,ax=canvas(4.0)
    txt(ax,.22,3.66,'SELECT LEMMAS',8.5,color=PINE,weight='bold')
    txt(ax,2.52,3.66,'COVER OBLIGATIONS',8.5,color=PINE,weight='bold')
    for j in range(4):txt(ax,2.45+.63*j,3.25,f'$u_{j+1}$',12,ha='center')
    for i in range(4):
        y=2.74-.57*i;sel=i in[0,2]
        if sel:band(ax,.12,y-.24,4.72,.48,PALE)
        txt(ax,.30,y,f'$S_{i+1}$',13,color=PINE if sel else MUTED)
        txt(ax,.94,y,'retain' if sel else 'omit',9.5,color=PINE if sel else MUTED)
        for j in range(4):
            x=2.45+.63*j
            if M[i,j]:ax.add_patch(Circle((x,y),.09,facecolor=PINE if sel else WHITE,edgecolor=PINE if sel else LINE,lw=1.15))
            else:txt(ax,x,y,'·',13,ha='center',color=LINE)
    rule(ax,4.95,1,4.95,3.45)
    txt(ax,5.56,3.1,'ALL',9,ha='center',color=PINE,weight='bold')
    txt(ax,5.56,2.79,'four',12,ha='center')
    txt(ax,5.56,2.48,'obligations',9.5,ha='center')
    arrow(ax,(5.56,2.18),(5.56,1.72));gate(ax,5.56,1.55)
    arrow(ax,(5.56,1.35),(5.56,.97));node(ax,5.56,.76,'$T$')
    txt(ax,.24,.43,r'$S_1\cup S_3=\{u_1,u_2,u_3,u_4\}$',12)
    note(ax,.24,.12,'One optimum costs 2. No single lemma covers all four obligations.')
    save(f,'fig_04_certificate_complexity','Membership matrix for the exact Set Cover instance with one minimum highlighted')


def preorder():
    f,ax=canvas(3.65)
    positions=[(3.12,3.05,r'$(C_0,x,y)$'),(1.48,1.93,r'$(C_0,x)$'),(4.75,1.93,r'$(C_0,y)$'),(3.12,.76,r'$C_0$')]
    for x,y,label in positions:
        band(ax,x-.67,y-.23,1.34,.46,PALE if y>2.8 else CREAM if y>1 else PALE)
        txt(ax,x,y,label,16,ha='center')
    for a,b in [((2.8,2.78),(1.8,2.2)),((3.45,2.78),(4.4,2.2)),((1.81,1.64),(2.8,1.02)),((4.42,1.64),(3.45,1.02))]:arrow(ax,a,b,color=PINE)
    txt(ax,3.12,2.07,'incomparable',9.8,ha='center',color=GOLD)
    txt(ax,3.12,1.83,r'for $\{q_x,q_y\}$',9.5,ha='center',color=GOLD)
    txt(ax,.26,1.42,r'recovers $q_x$',9.4,color=MUTED)
    txt(ax,5.98,1.42,r'recovers $q_y$',9.4,color=MUTED,ha='right')
    note(ax,.18,.19,'Arrows discard information. The two middle schemes are incomparable for {qₓ, qᵧ}.',size=9.1)
    save(f,'fig_05_recoverability_preorder','Exact four-archive retention diamond, not a claimed hierarchy of all presentation formats')


def loss_vectors():
    field=load_proof_field(ROOT/'examples/and_dag.json');c=unique_and_dag_certificate(field)
    report=compression_report(field,Representation('certificate',c.node_ids,certificate=c))
    kept=report.retained_values.as_dict();lost=report.loss_values.as_dict()
    AUDIT['checks']['loss_vectors']={'retained':kept,'lost':lost}
    f,ax=canvas(3.9)
    txt(ax,.10,3.60,'VALUE COORDINATE',8.7,color=PINE,weight='bold')
    txt(ax,5.05,3.60,'RETAINED',8.0,color=PINE,ha='center',weight='bold')
    txt(ax,5.93,3.60,'LOST',8.0,color=GOLD,ha='center',weight='bold')
    for i,name in enumerate(kept):
        y=3.03-i*.55
        txt(ax,.12,y,name.capitalize(),10.2)
        r,l=kept[name],lost[name];scale=.28
        if r:band(ax,1.54,y-.13,r*scale,.26,PALE);rule(ax,1.54,y,1.54+r*scale,y,color=PINE,lw=7)
        if l:rule(ax,1.54+r*scale,y,1.54+(r+l)*scale,y,color=GOLD,lw=7)
        if r+l==0:txt(ax,1.54,y,'no declared value',9.0,color=MUTED)
        txt(ax,5.05,y,f'{r:g}',11,ha='center',color=PINE)
        txt(ax,5.93,y,f'{l:g}',11,ha='center',color=GOLD)
    note(ax,.12,.29,'Values are declared model inputs. Verification loss is zero; bridge loss is eight.',size=9.2)
    save(f,'fig_06_loss_vectors','Exact five-coordinate retained/lost values from the canonical AND-DAG')


def bridge_dominators():
    f,ax=canvas(3.6)
    pos={'A':(.45,1.68),'E':(1.83,2.64),'F':(1.83,.79),'C':(3.50,1.69),'TA':(5.76,2.53),'TB':(5.76,1.66),'TC':(5.76,.49)}
    # Routes E -> Future C bypass C. Labels preserve role as a bridge model.
    for s,t in [('A','E'),('A','F'),('E','C'),('F','C'),('C','TA'),('C','TB')]:
        a=np.array(pos[s]);b=np.array(pos[t]);u=(b-a)/np.linalg.norm(b-a)
        arrow(ax,a+.22*u,b-.22*u,color=GOLD if s=='F' else PINE)
    arrow(ax,(2.03,2.76),(5.58,.38),color=LINE,lw=1.1,rad=-.45)
    for k,(x,y) in pos.items():
        node(ax,x,y,{'TA':'A′','TB':'B′','TC':'C′'}.get(k,k),kind='side' if k in ['E','F'] else 'core',r=.20,size=10.5)
    txt(ax,.45,1.26,'archive',8.6,ha='center',color=MUTED)
    txt(ax,1.83,3.03,'example',8.6,ha='center',color=MUTED)
    txt(ax,1.83,.40,'failed route',8.6,ha='center',color=MUTED)
    txt(ax,3.50,1.19,'boundary theorem',9,ha='center',color=PINE)
    txt(ax,3.50,.88,'dominates A′ and B′',9,ha='center',color=PINE,weight='bold')
    note(ax,.16,.10,'Bridge arrows mean declared future reach, not certified logical implication.',size=9.1)
    save(f,'fig_07_bridge_dominators','Declared bridge graph with a bypass and a two-target dominator')


def chart(h=3.5,bottom=.19,right=.92):
    f=plt.figure(figsize=(6.25,h));ax=f.add_axes([.11,bottom,right-.11,.91-bottom])
    ax.tick_params(labelsize=9,length=3);ax.grid(axis='y',color=LINE,alpha=.40,lw=.6)
    ax.set_axisbelow(True);return f,ax


def submodular():
    rows=list(csv.DictReader((ROOT/'data/retention_comparison.csv').open()))
    x=[int(r['budget']) for r in rows];g=[float(r['greedy_utility']) for r in rows];o=[float(r['exact_utility']) for r in rows]
    assert np.allclose(g,o)
    f,ax=chart(4.4);ax.plot(x,o,c=GOLD,lw=1.5,ls='--',marker='s',ms=7,mfc='white',label='Exact optimum')
    ax.plot(x,g,c=PINE,lw=1.4,marker='o',ms=3.5,label='Greedy selection')
    ax.set(xlabel='Retained items (cardinality budget)',ylabel='Weighted future reach',xticks=x)
    ax.legend(loc='lower right',frameon=False,fontsize=9)
    ax.text(.04,.95,'Same values on this instance.',transform=ax.transAxes,va='top',fontsize=10,color=PINE)
    ax.text(.04,.86,r'General guarantee: $1-1/e$, not equality.',transform=ax.transAxes,va='top',fontsize=9,color=MUTED)
    save(f,'fig_08_submodular_greedy','Exact and greedy values from the retained finite coverage instance')


def version():
    f,ax=canvas(2.85)
    pos={'A':(.43,2.09),'D':(.43,.75),'L1':(2.02,2.09),'L2':(3.72,2.09),'B':(5.49,2.09),'E':(2.02,.75),'C':(3.72,.75)}
    for s,t in [('A','L1'),('D','L1'),('L1','L2'),('L2','B'),('D','E'),('E','C')]:
        a=np.array(pos[s]);b=np.array(pos[t]);u=(b-a)/np.linalg.norm(b-a)
        arrow(ax,a+.21*u,b-.21*u,color=RUST if s in ['L1','L2'] else LINE)
    for k,(x,y) in pos.items():node(ax,x,y,{'L1':'$L_1$','L2':'$L_2$'}.get(k,k),kind='blocked' if k in ['L1','L2','B'] else 'neutral')
    txt(ax,2.02,2.55,'changed',9.3,ha='center',color=RUST,weight='bold')
    txt(ax,4.50,2.55,'recheck descendants',9.3,ha='center',color=RUST)
    txt(ax,3.70,.27,'Independent branch: not marked by this revision.',9.2,ha='center',color=MUTED)
    save(f,'fig_09_version_invalidation','Changed L1 and its exact syntactic descendant review set')


def effective():
    f,ax=chart(3.8,right=.83);n=np.arange(1,101)
    for rho,col,ls in [(0,PINE,'-'),(.05,BLUE,'--'),(.1,GOLD,'-.'),(.25,RUST,':')]:
        neff=n/(1+(n-1)*rho);ax.plot(n,neff,c=col,lw=1.65,ls=ls)
        ax.text(102,neff[-1],f'ρ = {rho:g}\n{neff[-1]:.2f}',fontsize=9,va='center',color=col)
    ax.set_yscale('log');ax.set(xlim=(1,101),ylim=(1,140),xlabel='Nominal reviewers',ylabel='Effective count (log scale)')
    ax.set_yticks([1,2,5,10,20,50,100]);ax.set_yticklabels(['1','2','5','10','20','50','100'])
    ax.text(.06,.93,r'$n_{\mathrm{eff}}=\dfrac{n}{1+(n-1)\rho}$',transform=ax.transAxes,va='top',fontsize=15)
    AUDIT['checks']['effective_count_n100_rho01']=100/10.9
    save(f,'fig_10_effective_reviewers','The equicorrelated-review count with explicit logarithmic scaling and endpoint values')


def queues():
    rows=list(csv.DictReader((ROOT/'data/audit_queue.csv').open()))
    f,ax=chart(3.6,right=.79);x=[int(r['step']) for r in rows]
    for key,label,col,ls in [('stable','4 arrivals',PINE,'-'),('critical','5 arrivals',GOLD,'--'),('unstable','6 arrivals',RUST,'-.')]:
        y=[float(r[key]) for r in rows];ax.plot(x,y,c=col,lw=1.8,ls=ls)
        ax.text(40,y[-1],label,fontsize=9.2,va='center',color=col)
    ax.set(xlabel='Audit cycle',ylabel='Unaudited backlog',xlim=(0,39),ylim=(-2,53))
    ax.text(.04,.93,'Capacity: 5 per cycle\nInitial backlog: 10',transform=ax.transAxes,va='top',fontsize=10)
    save(f,'fig_11_audit_queues','Three committed constant-rate audit trajectories')


def refinement():
    residuals=np.array([1,.55,.30,.18,.12,.09,.075]);costs=np.array([0,.25,.65,1.2,2.1,3.5,5.5])
    f,ax=chart(3.9);depths={}
    for name,rw,cw,col,ls in [('Certificate',1,.75,PINE,'-'),('Teaching',2.5,.35,GOLD,'--'),('Archive',5,.15,BLUE,'-.')]:
        vals=rw*residuals+cw*costs;i=int(vals.argmin());depths[name]=i
        ax.plot(range(7),vals,c=col,lw=1.6,ls=ls,marker='o',ms=3,label=f'{name}: depth {i}')
        ax.plot(i,vals[i],marker='s',ms=8,mfc='white',mec=col,mew=1.5)
    ax.set(xlabel='Expansion depth',ylabel='Declared weighted objective',xticks=range(7))
    ax.legend(frameon=False,fontsize=9,loc='upper center')
    AUDIT['checks']['optimal_depths']=depths
    save(f,'fig_12_refinement_goals','Objective values and exact minimizing depths for three declared tasks')


def workflow():
    f,ax=canvas(5.0)
    rows=[('01','A declared record','Nodes, rules, evidence and scoped certification flags.', 'examples/*.json'),
          ('02','Validation and closure','Check identifiers and compute declared derivability.', 'model.py  /  io.py'),
          ('03','Certificate and task reports','Extract a core; audit retained information and costs.', 'certificate.py  /  compression.py'),
          ('04','Independent checks','Check concrete equations, witnesses and formal scope.', 'tests/  /  formal/'),
          ('05','Inspectable publication','Publish the text, data, source and verification record.', 'docs/  /  data/  /  evidence/')]
    for i,(n,t,d,src) in enumerate(rows):
        y=4.52-.94*i
        txt(ax,.12,y,n,17,color=PINE,weight='bold');txt(ax,.78,y+.09,t,12,weight='bold')
        txt(ax,.78,y-.18,d,9.3,color=MUTED);txt(ax,.78,y-.43,src,8.6,color=PINE)
        if i<4:rule(ax,.31,y-.29,.31,y-.67,color=LINE);arrow(ax,(.31,y-.67),(.31,y-.76),color=PINE,lw=1)
    save(f,'fig_13_repository_workflow','Inspect the actual record, software, checks and publication layers')


def ambient():
    f,ax=canvas(4.3)
    # A finite declared field. Successful route and blocked attempt retained independently.
    band(ax,.09,2.12,6.07,.91,PALE)
    node(ax,.55,2.55,'$A$');node(ax,2.46,2.55,'$L$');node(ax,5.51,2.55,'$B$')
    arrow(ax,(.76,2.55),(2.25,2.55));arrow(ax,(2.67,2.55),(5.30,2.55))
    txt(ax,1.5,2.86,'certified',8.5,ha='center',color=PINE);txt(ax,4.0,2.86,'certified',8.5,ha='center',color=PINE)
    node(ax,2.46,1.05,'$R$',kind='blocked');arrow(ax,(.62,2.33),(2.27,1.2),color=RUST,ls='--')
    rule(ax,2.70,1.05,3.84,1.05,color=RUST,ls='--',lw=1.2)
    rule(ax,3.9,.90,3.9,1.20,color=RUST,lw=2)
    txt(ax,4.17,1.19,'scoped refutation',10,color=RUST,weight='bold')
    txt(ax,4.17,.91,'of this attempted step',9.2,color=MUTED)
    node(ax,2.46,3.77,'$U$',kind='open');arrow(ax,(.63,2.80),(2.25,3.70),color=BLUE,ls='--')
    txt(ax,2.93,3.77,'open obligation',10,color=BLUE)
    txt(ax,2.46,.63,'failed route',9,ha='center',color=RUST)
    txt(ax,.16,.20,r'A blocked route does not refute the certified route $A\to L\to B$.',10.4,color=PINE)
    save(f,'fig_14_ambient_field','Certified, unresolved and locally refuted routes have distinct logical roles')


def gluing():
    f,ax=canvas(4.4)
    txt(ax,.14,4.10,r'Certified rule: $\{a,b\}\longrightarrow c$',15,weight='bold')
    # Large patch windows. Values explicitly include false overlap.
    for x,title,items in [(.18,r'$U_0=\{a,c\}$',[('a',1),('c',0)]),(3.54,r'$U_1=\{b,c\}$',[('b',1),('c',0)])]:
        band(ax,x,2.08,2.50,1.43,CREAM);txt(ax,x+.16,3.24,title,13)
        for j,(key,val) in enumerate(items):
            xx=x+.52+j*1.19
            node(ax,xx,2.64,key,kind='core' if val else 'neutral')
            txt(ax,xx,2.26,f'{val}',11,ha='center',color=PINE if val else MUTED)
    rule(ax,2.82,2.65,3.37,2.65,color=LINE,lw=1)
    txt(ax,3.12,2.98,r'$c=0$',10,ha='center');txt(ax,3.12,2.40,'agree',8.7,ha='center',color=MUTED)
    arrow(ax,(1.43,2.00),(2.55,1.43),color=RUST);arrow(ax,(4.79,2.00),(3.71,1.43),color=RUST)
    band(ax,1.47,.91,3.36,.56,PALE)
    txt(ax,3.15,1.19,r'$(a,b,c)=(1,1,0)$',18,ha='center',color=RUST)
    txt(ax,3.15,.61,r'$a\wedge b=1$ but $c=0$',12,ha='center',color=RUST)
    note(ax,.14,.15,'Neither patch contains {a,b,c}. Matching and pairwise coverage miss the whole rule.',size=9.1)
    AUDIT['checks']['whole_support_counterexample']={'local_values':[[1,0],[1,0]],'matches':True,'global_rule_satisfied':False}
    save(f,'fig_15_whole_support','Worked pairwise-cover counterexample to whole-support gluing')


def restriction():
    f,ax=canvas(4.25)
    txt(ax,.12,3.98,r'One rule: $\{a,b\}\to c$; no admissible leaves ($L=\varnothing$).',11,color=MUTED)
    band(ax,1.40,2.82,3.46,.92,PALE)
    txt(ax,3.13,3.40,r'$\mathcal{M}_F(V):\;7\;\mathrm{models}$',18,ha='center')
    txt(ax,3.13,3.01,r'all binary triples except $(1,1,0)$',10.3,ha='center',color=MUTED)
    # For the display use projections onto ac, bc and c.
    for x,lbl in [(1.06,r'$\mathcal{M}_F(\{a,c\})$'),(5.10,r'$\mathcal{M}_F(\{b,c\})$')]:
        txt(ax,x,1.69,lbl,14,ha='center')
        txt(ax,x,1.34,'4 local models',9.6,ha='center',color=MUTED)
    arrow(ax,(2.15,2.83),(1.12,2.03));arrow(ax,(4.12,2.83),(5.02,2.03))
    # Restrictions are shown in the caption, avoiding labels on arrow shafts.
    
    txt(ax,3.13,.48,r'$\mathcal{M}_F(\{c\})$: 2 values',13,ha='center')
    arrow(ax,(1.43,1.13),(2.62,.65));arrow(ax,(4.77,1.13),(3.65,.65))
    note(ax,.17,.12,'Restriction commutes. Agreement below does not supply a missing global model.',size=9.1)
    triples=list(itertools.product([0,1],repeat=3));models=[t for t in triples if not(t[0] and t[1]) or t[2]]
    assert len(models)==7
    AUDIT['checks']['rule_model_count']=7
    save(f,'fig_16_restriction_bridge','Explicit local rule model diagram and its restriction maps')


def binary_cube():
    f=plt.figure(figsize=(6.25,4.4));ax=f.add_axes([.01,.10,.98,.86],projection='3d')
    pts=list(itertools.product([0,1],repeat=3));sol=[p for p in pts if sum(p)%2==0 and p[0]==0]
    assert sol==[(0,0,0),(0,1,1)]
    # cube edges are coordinate flips, not F2 solution lines.
    for a,b in itertools.combinations(pts,2):
        if sum(x!=y for x,y in zip(a,b))==1:ax.plot(*zip(a,b),color=LINE,lw=.8,alpha=.85)
    for p in pts:
        good=p in sol;par=sum(p)%2==0
        ax.scatter(*p,s=120 if good else 42,marker='o' if good else 's' if par else 'x',
                   color=PINE if good else GOLD if par else '#A8B8B0',depthshade=False)
        # All vertex labels small but native; offset away from coordinate origin.
        dx,dy,dz=(.03,.03,.055)
        ax.text(p[0]+dx,p[1]+dy,p[2]+dz,''.join(map(str,p)),fontsize=10,color=PINE if good else MUTED)
    ax.set(xlim=(-.20,1.26),ylim=(-.20,1.26),zlim=(-.15,1.3))
    ax.text(.52,-.17,-.12,'a',fontsize=15,color=PINE)
    ax.text(-.17,.52,-.12,'b',fontsize=15,color=PINE)
    ax.text(-.12,-.12,.55,'c',fontsize=15,color=PINE)
    ax.set_proj_type('ortho');ax.set_box_aspect((1,1,1),zoom=1.40);ax.view_init(elev=23,azim=-56);ax.set_axis_off()
    f.text(.04,.94,r'$(a,b,c)\in\mathbb{F}_2^3,\quad a+b+c=0,\quad a=0$',fontsize=17,color=INK)
    f.text(.05,.06,'8 states',fontsize=11,color=MUTED)
    f.text(.28,.06,'4 satisfy parity',fontsize=11,color=GOLD)
    f.text(.61,.06,'2 preserve a = 0',fontsize=11,color=PINE,weight='bold')
    AUDIT['checks']['binary_cube']={'ambient_count':8,'parity_count':4,'protected_count':2,'solutions':sol}
    save(f,'fig_17_binary_cube','Eight binary vertices with four parity states and two protected realizations')


def queries():
    f,ax=canvas(4.35)
    band(ax,.12,3.49,6.0,.56,PALE);txt(ax,3.12,3.77,r'$\mathcal{A}=\{000,011\},\quad H=\langle011\rangle$',17,ha='center')
    rows=[('Read a','0','0','0 bits','2 remain'),('Read b','0','1','1 bit','1 remains'),('Read (b,b)','(0,0)','(1,1)','1 bit','1 remains')]
    xs=[.25,2.43,3.45,4.72,5.92]
    for x,s in zip(xs,['OBSERVATION','000','011','GAIN','FIBER']):txt(ax,x,3.02,s,8.6,ha='left' if x==.25 else 'center',color=PINE,weight='bold')
    for i,row in enumerate(rows):
        y=2.51-.74*i
        rule(ax,.15,y-.35,6.1,y-.35)
        for j,(x,s) in enumerate(zip(xs,row)):
            txt(ax,x,y,s,10.0 if j>2 else 11,ha='left' if j==0 else 'center',color=PINE if j==3 else INK)
    txt(ax,.22,.42,r'$\mathrm{gain}=\operatorname{rank}(Q|_H)$, not the number of output coordinates.',12)
    note(ax,.22,.10,'Bits refer to the uniform distribution on the two compatible realizations.',size=9.1)
    AUDIT['checks']['observation_gains']=[0,1,1]
    save(f,'fig_18_observation_partitions','Three observations of the same binary fiber, including a redundant two-row output')


def obstruction():
    f,ax=canvas(4.1)
    rows=[('compatibility',r'$a+b=0$'),('protected',r'$a=0$'),('protected',r'$b=1$')]
    for i,(tag,eq) in enumerate(rows):
        y=3.56-.63*i
        txt(ax,.22,y,tag,9.3,color=MUTED)
        txt(ax,2.05,y,eq,19)
        txt(ax,5.45,y,'× 1',12,color=RUST)
    rule(ax,.18,1.95,6.08,1.95,color=RUST,lw=1.25)
    txt(ax,.22,1.64,'Add all three equations in F₂.',11)
    txt(ax,4.86,1.56,r'$0=1$',28,color=RUST,ha='center')
    band(ax,.16,.45,5.91,.75,CREAM)
    txt(ax,.37,.97,r'$\ell=(1,1,1)$',16,color=RUST)
    txt(ax,3.24,.97,r'$\ell M=0,\qquad\ell b=1$',16,color=RUST)
    note(ax,.37,.63,'The third coordinate is free, but no value can repair this contradiction.',size=9.0)
    note(ax,.22,.15,'This is an impossibility certificate for the prescribed binary problem, not a timeout.',size=9.1)
    M=np.array([[1,1,0],[1,0,0],[0,1,0]]);b=np.array([0,0,1]);ell=np.ones(3,dtype=int)
    assert ((ell@M)%2==0).all() and (ell@b)%2==1
    AUDIT['checks']['obstruction_witness']={'ell':[1,1,1],'ellM':[0,0,0],'ellb':1}
    save(f,'fig_19_obstruction_witness','An explicit F2 row witness for the incompatible protected example')


def collision():
    f,ax=canvas(4.35)
    for y,bit in [(3.55,0),(1.02,1)]:
        band(ax,.12,y-.43,2.17,.84,CREAM)
        txt(ax,.30,y+.15,rf'$\mathcal{{P}}_{bit}=(C_0,{bit})$',19)
        txt(ax,.32,y-.23,'same proof; different side record',8.3,color=MUTED)
    band(ax,3.19,1.9,1.18,.80,PALE);txt(ax,3.78,2.30,r'$C_0$',25,ha='center')
    arrow(ax,(2.32,3.40),(3.30,2.66));arrow(ax,(2.32,1.18),(3.30,1.93))
    txt(ax,2.79,3.32,r'$C$',13,color=PINE);txt(ax,2.80,1.15,r'$C$',13,color=PINE)
    arrow(ax,(4.42,2.3),(5.26,2.3),color=RUST)
    txt(ax,5.53,2.60,r'$d_q$',17,ha='center',color=RUST)
    txt(ax,5.53,2.05,'0 or 1?',12,ha='center',color=RUST)
    txt(ax,.27,.43,r'$q(\mathcal{P}_0)=0\ne1=q(\mathcal{P}_1)$',16)
    note(ax,.27,.13,'The decoder sees the same input. It cannot recover both different answers.',size=9.2)
    save(f,'fig_20_compression_collision','Two archives collapse to one certificate and make a side-record task undecodable')


def bias_floor():
    f,ax=chart(4.55,right=.83);ax.set_position([.11,.16,.72,.62]);n=np.arange(1,501)
    models=[('Independent',0,0,PINE,'-'),('Common offset',.3,0,GOLD,'--'),('Offset + dependence',.3,.1,RUST,'-.')]
    for title,b,rho,col,ls in models:
        mse=b*b+rho+(1-rho)/n;ax.plot(n,mse,c=col,lw=1.7,ls=ls)
    ax.set(xlim=(1,500),ylim=(.001,1.3),xlabel='Number of reviewers',ylabel='Mean squared error (log scale)')
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xticks([1,10,100,500]);ax.set_xticklabels(['1','10','100','500'])
    for y,l,col in [(.002,'0.002\nindependent',PINE),(.092,'0.092\noffset',GOLD),(.1918,'0.192\nboth',RUST)]:
        ax.text(525,y,l,color=col,fontsize=9,va='center')
    ax.axhline(.09,c=GOLD,lw=.6,ls=':');ax.axhline(.19,c=RUST,lw=.6,ls=':')
    f.text(.12,.93,r'$\mathrm{MSE}=b^2+\rho+(1-\rho)/n$',fontsize=16,color=INK)
    f.text(.12,.855,'Declared model: σ² = 1, b = 0.3 when present, ρ = 0.1 when present.',fontsize=9.6,color=MUTED)
    AUDIT['checks']['mse_n500']=[.002,.092,.1918]
    save(f,'fig_21_review_error_floor','Three explicit MSE curves distinguish individual noise, common offset and shared dependence')


def cover():
    f,ax=canvas(3.6)
    field_geometry(ax,base=.04,labels=False)
    # A mathematical motif using the exact AND-DAG geometry; no stock illustration.
    save(f,'cover_field','Cover motif: certified core and side records of the actual AND-DAG example')


def semantic_cover():
    from proof_path_theory import (ProofField, ProofFieldViews, ClaimNode, NodeKind,
        Justification, analyze_semantic_cover, verify_semantic_cover)
    field=ProofField([ClaimNode(v,v,NodeKind.CLAIM) for v in 'abc'],
        [Justification('r0',('a',),'b','declared'),
         Justification('r1',('b',),'c','declared'),
         Justification('r2',('a',),'c','declared')],premises=(),targets=('c',))
    view=ProofFieldViews(field);patches=[{'a','b'},{'b','c'}]
    certificate=analyze_semantic_cover(view,patches)
    assert certificate.sufficient and verify_semantic_cover(view,patches,certificate)
    assert not view.covers_supports(patches)
    assert certificate.entailments[-1].witness.rule_ids==('r0','r1')
    AUDIT['checks']['semantic_cover']={'whole_support':False,'semantic':True,
        'missing_rule':'r2','derivation':['r0','r1']}
    f,ax=canvas(4.0)
    txt(ax,.15,3.72,'VISIBLE CONSTRAINTS',8.8,color=PINE,weight='bold')
    txt(ax,.18,3.30,r'$U_0=\{a,b\}$',13,color=PINE)
    txt(ax,4.33,3.30,r'$U_1=\{b,c\}$',13,color=BLUE)
    band(ax,.18,2.22,3.12,.74,PALE)
    band(ax,3.0,2.22,3.04,.74,CREAM)
    for x,label in[(.65,'$a$'),(3.12,'$b$'),(5.57,'$c$')]:node(ax,x,2.60,label)
    arrow(ax,(.87,2.60),(2.90,2.60));arrow(ax,(3.35,2.60),(5.35,2.60))
    txt(ax,1.84,2.94,r'$r_0$',10,ha='center',color=PINE)
    txt(ax,4.33,2.94,r'$r_1$',10,ha='center',color=PINE)
    rule(ax,.65,2.38,.65,1.42,color=GOLD,ls='--')
    arrow(ax,(.65,1.42),(5.57,1.42),color=GOLD,ls='--')
    rule(ax,5.57,1.42,5.57,2.38,color=GOLD,ls='--')
    txt(ax,3.10,1.79,r'$r_2:a\to c$',13,ha='center',color=GOLD)
    txt(ax,3.12,1.12,'Its support is missing. Its implication is already enforced.',9.6,ha='center',color=MUTED)
    txt(ax,.22,.62,r'$\mathrm{cl}_{F_{\mathcal{U}}}(\{a\})=\{a,b,c\}$',16)
    note(ax,.22,.20,'Every original rule is checked, not just one target or one local assignment.',size=9.2)
    save(f,'fig_22_semantic_cover','A hidden redundant implication is entailed by visible rules; exact semantic-cover certificate')


def protected_closure():
    from proof_path_theory import (ProofField, ProofFieldViews, ClaimNode, NodeKind,
        Justification, solve_extension, verify_extension_result)
    view=ProofFieldViews(ProofField([ClaimNode(v,v,NodeKind.CLAIM) for v in 'abc'],
        [Justification('r0',('a','b'),'c','declared')],premises=(),targets=('c',)))
    good=solve_extension(view,positive=('a',),negative=('c',))
    bad=solve_extension(view,positive=('a','b'),negative=('c',))
    assert good.feasible and good.closure==frozenset('a') and not bad.feasible
    assert bad.obstruction.target=='c' and bad.obstruction.rule_ids==('r0',)
    assert verify_extension_result(view,positive=('a','b'),negative=('c',),result=bad)
    AUDIT['checks']['protected_rule_closure']={'feasible_closure':['a'],
        'forbidden_closure':['a','b','c'],'witness':['r0']}
    f,ax=canvas(4.2)
    txt(ax,.16,3.95,r'One field: $\{a,b\}\to c$, no admitted leaves.',12,weight='bold')
    band(ax,.12,2.18,6.0,1.3,PALE)
    txt(ax,.32,3.18,'FEASIBLE',8.7,color=PINE,weight='bold')
    txt(ax,.32,2.83,r'$S=\{a\},\quad N=\{c\}$',13)
    txt(ax,3.25,3.14,r'$\mathrm{cl}_F(S)=\{a\}$',14,color=PINE)
    txt(ax,3.25,2.64,'No forbidden node is derived.',10,color=MUTED)
    band(ax,.12,.55,6.0,1.32,CREAM)
    txt(ax,.32,1.58,'OBSTRUCTED',8.7,color=RUST,weight='bold')
    txt(ax,.32,1.23,r'$S=\{a,b\},\quad N=\{c\}$',13)
    txt(ax,3.25,1.56,r'$\mathrm{cl}_F(S)=\{a,b,c\}$',14,color=RUST)
    txt(ax,3.25,1.04,r'$r_0:\{a,b\}\Rightarrow c\in N$',12,color=RUST)
    note(ax,.22,.19,'The negative witness is a scoped derivation of c, not a failed search.',size=9.5)
    save(f,'fig_23_protected_closure','One conjunction rule with a least feasible model and a derivation of a forbidden node')

def trace_contract():
    from proof_path_theory.trace_codec import (IndexedProblem,IndexedRule,IndexedCertificate,
        IndexedWitness,check_indexed_certificate,replay_indexed)
    from dataclasses import replace
    p=IndexedProblem(4,(0,),(IndexedRule((0,),1),IndexedRule((1,),2)),(),(3,))
    c=IndexedCertificate(True,(0,1,2),(0,1))
    assert check_indexed_certificate(p,c)
    assert replay_indexed(p,(0,),strict=True)==(1,0)
    assert not check_indexed_certificate(p,replace(c,closure=(0,1),trace=(0,)))
    assert not check_indexed_certificate(p,replace(c,closure=(0,1,2,3),trace=()))
    blocked=replace(p,negative=(2,))
    witness=IndexedWitness(2,(0,1))
    assert check_indexed_certificate(blocked,replace(c,feasible=False,obstruction=witness))
    assert not check_indexed_certificate(blocked,c)
    AUDIT['checks']['trace_contract']={'node_count':4,'leaves':[0],'rules':[[[0],1],[[1],2]],
        'closure':[0,1,2],'strict_trace':[0,1],'partial_rejected':True,
        'closed_superset_rejected':True,'positive_forbidden':[3],
        'negative_forbidden':[2],'negative_witness':[2,[0,1]]}
    f,ax=canvas(4.65)
    txt(ax,.16,4.43,'ONE FIXED RULE FIELD',8.7,color=PINE,weight='bold')
    for x,label,kind in [(.58,'0','core'),(2.25,'1','core'),(3.91,'2','core'),(5.70,'3','side')]:
        node(ax,x,3.99,label,kind=kind)
    arrow(ax,(.80,3.99),(2.03,3.99));arrow(ax,(2.47,3.99),(3.69,3.99))
    txt(ax,1.4,4.25,r'$r_0$',10,ha='center',color=PINE)
    txt(ax,3.08,4.25,r'$r_1$',10,ha='center',color=PINE)
    txt(ax,5.70,3.62,'unsupported',9,ha='center',color=GOLD)
    band(ax,.12,2.55,6.0,.86,PALE)
    txt(ax,.30,3.17,'REPLAY',8.6,color=PINE,weight='bold')
    txt(ax,.30,2.83,r'$K\subseteq\mathrm{cl}_F(S)$',14)
    txt(ax,3.23,3.17,'FINAL MODEL TEST',8.6,color=PINE,weight='bold')
    txt(ax,3.23,2.83,r'$\mathrm{cl}_F(S)\subseteq K$',14)
    rule(ax,3.01,2.68,3.01,3.26,color=LINE)
    txt(ax,3.12,2.22,r'$[0,1]\quad\Longrightarrow\quad K=\{0,1,2\}$',17,ha='center',color=PINE)
    rule(ax,.14,1.96,6.1,1.96)
    txt(ax,.28,1.68,'VALID STEPS, INCOMPLETE SET',8.3,color=RUST,weight='bold')
    txt(ax,.28,1.39,r'$[0],\quad K=\{0,1\}$',12)
    note(ax,.28,1.09,'Rule r₁ is still enabled.',color=RUST,size=9.5)
    txt(ax,3.22,1.68,'CLOSED SET, NO DERIVATION',8.3,color=RUST,weight='bold')
    txt(ax,3.22,1.39,r'$[],\quad K=\{0,1,2,3\}$',12)
    note(ax,3.22,1.09,'No trace can derive node 3.',color=RUST,size=9.5)
    rule(ax,.14,.83,6.1,.83)
    txt(ax,.28,.54,r'$N=\{3\}$',12,color=PINE)
    txt(ax,1.39,.54,'feasible',10,color=PINE)
    txt(ax,3.22,.54,r'$N=\{2\}$',12,color=RUST)
    txt(ax,4.33,.54,'witness: (2, [0, 1])',10,color=RUST)
    note(ax,.28,.18,'The request is fixed separately. Rejected evidence is not an obstruction.',size=9.4)
    save(f,'fig_24_trace_contract','Replay plus saturation proves the least closure; forbidden-set changes alter feasibility')


def main():
    for fn in [theory_map,architecture,and_core,alternative,set_cover,preorder,loss_vectors,
               bridge_dominators,submodular,version,effective,queues,refinement,workflow,
               ambient,gluing,restriction,binary_cube,queries,obstruction,collision,bias_floor,semantic_cover,protected_closure,trace_contract,cover]:
        fn()
    (ROOT/'data/visual_contracts_1.8.0.json').write_text(json.dumps(AUDIT,indent=2)+'\n')
    (ROOT/'data/results.json').write_text(json.dumps({'publication_edition':'1.8.0','technical_version':'1.6.0','figures':25,'cover_motifs':1,'visual_contracts':'visual_contracts_1.8.0.json'},indent=2)+'\n')
    print(f'Generated {len(AUDIT["figures"])-1} figures and one exact cover motif.')

if __name__=='__main__':main()
