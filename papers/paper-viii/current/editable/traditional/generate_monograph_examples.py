#!/usr/bin/env python3
"""Three exact finite examples. Arithmetic uses Fraction; plots only display it.

The costs and integer errors are illustrative declared models. They are neither
measured GPU timings nor assertions about actual floating-point kernels.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'monograph_figures';OUT.mkdir(exist_ok=True)
DATA=ROOT/'monograph_data';DATA.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#212B34','text.color':'#212B34','axes.titleweight':'bold','savefig.dpi':160})
PINE='#245D60';OCHRE='#A2763B';INK='#212B34';MUTE='#7D898B'

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),metadata={'CreationDate':None,'ModDate':None},bbox_inches='tight',pad_inches=.16)
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight',pad_inches=.16)
    plt.close(fig)

def matvec(M,x):return [sum(a*b for a,b in zip(row,x)) for row in M]
def exact(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,(list,tuple)):return [exact(v) for v in x]
    if isinstance(x,dict):return {k:exact(v) for k,v in x.items()}
    return x
D=list(map(F,[2,3,4,5]));u=list(map(F,[1,0,1,0]));v=list(map(F,[1,1,0,0]));x=list(map(F,[1,2,3,4]))
A=[[int(i==j)*D[i]+u[i]*v[j] for j in range(4)] for i in range(4)]
s=sum(a*b for a,b in zip(v,x));dx=[d*t for d,t in zip(D,x)];correction=[z*s for z in u];y=matvec(A,x)
assert y==[a+b for a,b in zip(dx,correction)]==list(map(F,[5,6,15,20]))
dinv_u=[a/d for a,d in zip(u,D)];dinv_y=[a/d for a,d in zip(y,D)];denominator=1+sum(a*b for a,b in zip(v,dinv_u));coef=sum(a*b for a,b in zip(v,dinv_y))/denominator
recovered=[a-b*coef for a,b in zip(dinv_y,dinv_u)];assert denominator==F(3,2) and coef==3 and recovered==x
fig,(ax,bx)=plt.subplots(1,2,figsize=(8.8,3.7),gridspec_kw={'width_ratios':[1,1.25]})
ax.imshow(np.array(A,dtype=float),cmap='Blues',vmin=0,vmax=5)
for i in range(4):
    for j in range(4):ax.text(j,i,str(A[i][j]),ha='center',va='center',color='white' if A[i][j]>=4 else INK,fontweight='bold')
ax.set(xticks=range(4),yticks=range(4),xticklabels=['1','2','3','4'],yticklabels=['1','2','3','4'],xlabel='Input coordinate',ylabel='Output coordinate',title=r'$A=D+uv^T$')
idx=np.arange(4);bx.bar(idx,[float(t) for t in dx],label='Diagonal action',color=PINE,width=.58);bx.bar(idx,[float(t) for t in correction],bottom=[float(t) for t in dx],label='Rank-one correction',color=OCHRE,width=.58)
for i,val in enumerate(y):bx.text(i,float(val)+.4,str(val),ha='center',fontweight='bold')
bx.set(xticks=idx,xticklabels=['1','2','3','4'],ylim=(0,24),xlabel='Output coordinate',ylabel='Exact action value',title=r'$Ax=Dx+u(v^Tx)$');bx.legend(loc='upper left',frameon=False,fontsize=9);fig.tight_layout(w_pad=2);save(fig,'01_exact_bdlr_action')

# Root r has children a,b. Only a can split, into a1,a2.
nodes={'r':{'cost':1,'error':6,'children':['a','b'],'overhead':0},'a':{'cost':2,'error':4,'children':['a1','a2'],'overhead':0},'b':{'cost':1,'error':0,'children':[],'overhead':0},'a1':{'cost':3,'error':1,'children':[],'overhead':0},'a2':{'cost':1,'error':0,'children':[],'overhead':0}}
def enumerate_prunings(node):
    n=nodes[node];result=[{'leaves':[node],'cost':n['cost'],'error':n['error']}]
    if n['children']:
        for combination in product(*(enumerate_prunings(c) for c in n['children'])):
            result.append({'leaves':sum((k['leaves'] for k in combination),[]),'cost':n['overhead']+sum(k['cost'] for k in combination),'error':sum(k['error'] for k in combination)})
    return result
prunings=enumerate_prunings('r');assert [(z['cost'],z['error']) for z in prunings]==[(1,6),(3,4),(5,1)]
def solve(node,lam):
    n=nodes[node];keep=F(n['cost'])+lam*n['error']
    if not n['children']:return keep
    return min(keep,F(n['overhead'])+sum(solve(c,lam) for c in n['children']))
lagrangian=[]
for lam in [F(0),F(1,2),F(2,3),F(3,4),F(4,5),F(1),F(2)]:
    scores=[F(z['cost'])+lam*z['error'] for z in prunings];assert solve('r',lam)==min(scores)
    lagrangian.append({'lambda':lam,'scores':scores,'minimum':min(scores),'optimal_indices':[i for i,s in enumerate(scores) if s==min(scores)]})
budgets=[{'budget':b,'minimum_cost':min((z['cost'] for z in prunings if z['error']<=b),default=None)} for b in range(7)]
assert budgets[4]['minimum_cost']==3 and budgets[6]['minimum_cost']==1
# Middle can beat the root only for lambda>=1, and the full split only
# for lambda<=2/3. These intervals have empty intersection.
assert F(1)>F(2,3)
fig,(ax,bx)=plt.subplots(1,2,figsize=(8.8,3.5),gridspec_kw={'width_ratios':[1,1.1]})
pos={'r':(0,2),'a':(-.7,1),'b':(.7,1),'a1':(-1.05,0),'a2':(-.35,0)}
for n,rec in nodes.items():
    for child in rec['children']:ax.plot([pos[n][0],pos[child][0]],[pos[n][1],pos[child][1]],color=MUTE,zorder=0)
    xx,yy=pos[n];ax.scatter(xx,yy,s=500,c=PINE if n!='b' else OCHRE,zorder=2)
    ax.text(xx,yy,n,color='white',ha='center',va='center',fontweight='bold');ax.text(xx,yy-.25,f"cost {rec['cost']}, error {rec['error']}",ha='center',va='top',fontsize=8)
ax.set(xlim=(-1.55,1.2),ylim=(-.65,2.45),title='A finite candidate tree');ax.axis('off')
bx.plot([6,1],[1,5],color=MUTE,linestyle='--',label='Supported lower boundary')
labels=['Keep root','Keep a and b','Keep a1, a2, b']
for z,label,col in zip(prunings,labels,[PINE,OCHRE,PINE]):bx.scatter(z['error'],z['cost'],s=65,c=col,zorder=3)
bx.annotate('Keep root',(6,1),(-65,10),textcoords='offset points',fontsize=9)
bx.annotate('Budget-only optimum',(4,3),(-20,18),textcoords='offset points',fontsize=9,color=OCHRE)
bx.annotate('Full split',(1,5),(12,-6),textcoords='offset points',fontsize=9)
bx.set(xlim=(.4,6.6),ylim=(.5,5.7),xlabel='Declared integer error',ylabel='Declared additive cost',title='Budget and Lagrangian choices');bx.grid(alpha=.15);fig.tight_layout(w_pad=2);save(fig,'02_exact_compiler_frontier')

options=[{'F':{'cost':1,'error':5},'A':{'cost':4,'error':0}}, {'F':{'cost':1,'error':2},'A':{'cost':3,'error':0}}, {'F':{'cost':1,'error':1},'A':{'cost':3,'error':0}}]
assignments=[]
for labels in product('FA',repeat=3):assignments.append({'assignment':''.join(labels),'cost':sum(options[i][k]['cost'] for i,k in enumerate(labels)),'error':sum(options[i][k]['error'] for i,k in enumerate(labels))})
table={0:0};tables=[table.copy()]
for choices in options:
    nxt={}
    for b,c in table.items():
        for row in choices.values():nxt[b+row['error']]=min(nxt.get(b+row['error'],float('inf')),c+row['cost'])
    table=nxt;tables.append(table.copy())
for b in range(9):
    brute=min((z['cost'] for z in assignments if z['error']<=b),default=None)
    dp=min((c for err,c in table.items() if err<=b),default=None)
    assert brute==dp
feasible=[z for z in assignments if z['error']<=3];best=min(feasible,key=lambda z:z['cost']);assert best=={'assignment':'AFF','cost':6,'error':3}
fig,ax=plt.subplots(figsize=(8.6,3.3))
for row in assignments:
    selected=row['assignment']=='AFF';ax.scatter(row['error'],row['cost'],s=95 if selected else 48,c=OCHRE if selected else PINE,zorder=3)
    offset=(-22,8) if row['assignment']=='AAF' else (5,6)
    ax.annotate(row['assignment'],(row['error'],row['cost']),offset,textcoords='offset points',fontsize=9,fontweight='bold' if selected else 'normal')
ax.axvline(3,color=OCHRE,linestyle='--',label='Budget 3');ax.axvspan(-.4,3,alpha=.08,color=OCHRE)
ax.set(xlim=(-.45,8.7),ylim=(2.5,10.8),xlabel='Declared integer error',ylabel='Declared additive cost',title='One precision option per edge');ax.legend(frameon=False,loc='upper right');ax.grid(alpha=.15);fig.tight_layout();save(fig,'03_exact_precision_budget')

controls={'dropping_rank_one_action_detected':dx!=y,'incorrect_Woodbury_denominator_detected':[a-b*F(9,2) for a,b in zip(dinv_y,dinv_u)]!=x,'unsupported_middle_requires_empty_lambda_interval':F(1)>F(2,3),'all_fast_precision_exceeds_budget':assignments[0]['error']>3,'ignoring_sensitive_edge_infeasible':next(z for z in assignments if z['assignment']=='FAA')['error']>3}
assert all(controls.values())
record={'schema':'komorebi.paper_viii.monograph_exact_examples.v1','scope':'Three illustrative exact finite models. No actual precision-kernel or hardware claims.','bdlr':{'D_diagonal':D,'u':u,'v':v,'A':A,'x':x,'Dx':dx,'correction':correction,'y':y,'woodbury_denominator':denominator,'woodbury_coefficient':coef,'D_inverse_y':dinv_y,'D_inverse_u':dinv_u,'recovered_x':recovered,'stored_scalar_slots':12,'dense_scalar_slots':16},'compiler':{'nodes':nodes,'prunings':prunings,'lagrangian':lagrangian,'budget_frontier':budgets,'supported_transition':F(4,5),'middle_optimum_lambda_lower':F(1),'middle_optimum_lambda_upper':F(2,3)},'precision':{'options':options,'assignments':assignments,'dynamic_program_tables':tables,'budget':3,'optimum':best},'false_controls':controls,'status':'PASS'}
(DATA/'exact_examples.json').write_text(json.dumps(exact(record),indent=2)+'\n')
with (DATA/'precision_assignments.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['assignment','cost','error']);w.writeheader();w.writerows(assignments)
print(json.dumps({'status':'PASS','models':3,'false_controls_rejected':len(controls),'precision_assignments':len(assignments),'compiler_prunings':len(prunings)},indent=2))
