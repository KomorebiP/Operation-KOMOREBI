from __future__ import annotations
import json,pathlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch,FancyBboxPatch
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]; FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True); x=json.loads((ROOT/'results/ANALYSIS.json').read_text()); edge=x['cost_edge']
# architecture
fig,ax=plt.subplots(figsize=(15,9)); ax.set_xlim(0,15);ax.set_ylim(0,10);ax.axis('off');ax.set_title('RRCT v0.56: Cost-Regularized Workspace Formation',fontsize=18,pad=18)
def box(x0,y,w,h,text,lw=1.7):
 p=FancyBboxPatch((x0,y),w,h,boxstyle='round,pad=0.04,rounding_size=0.08',fill=False,linewidth=lw);ax.add_patch(p);ax.text(x0+w/2,y+h/2,text,ha='center',va='center',fontsize=10)
def arrow(a,b,c,d): ax.add_patch(FancyArrowPatch((a,b),(c,d),arrowstyle='-|>',mutation_scale=14,linewidth=1.4))
box(5,8.3,5,1.05,'ANONYMOUS TASK-DEMAND CUE\nNoisy projection of public dependency structure',2)
box(5.25,6.6,4.5,1,'LEARNED FORMATION ROUTER\nCounterfactual terminal loss + active cost',2)
labels=['No workspace\nC=0','Flat workspace\nC=1','Pair 01|23\nC=2.5','Pair 02|13\nC=2.5','Pair 03|12\nC=2.5','Overlap/full\nC=4']
xs=[.4,2.8,5.2,7.6,10,12.4]
for xx,ll in zip(xs,labels): box(xx,4.1,2 if xx<12 else 2.2,1.2,ll)
box(4.6,1.8,5.8,1.15,'SELECTED ACTIVE GRAPH\nControls terminal action; closes or switches next episode',2)
box(4.9,.25,5.2,.85,'TERMINAL TASK RESULT\nNo oracle route index supplied')
arrow(7.5,8.3,7.5,7.6)
for xx in [1.4,3.8,6.2,8.6,11,13.5]: arrow(7.5,6.6,xx,5.3);arrow(xx,4.1,7.5,2.95)
arrow(7.5,1.8,7.5,1.1);ax.text(.5,9.55,r'$J_r=L_r+\lambda C_r$',fontsize=12)
ax.text(.5,.05,'The route library is supplied. What is learned is whether to form a workspace, which coalition graph to activate, and how much depth to purchase.',fontsize=9.5)
fig.savefig(FIG/'01_architecture.png',dpi=220,bbox_inches='tight');plt.close(fig)
# edge
lam=np.array([r['lambda_cost'] for r in edge]); task=np.array([r['mean_task_accuracy'] for r in edge]); route=np.array([r['mean_route_accuracy'] for r in edge]); cost=np.array([r['mean_cost'] for r in edge]); oracle=np.array([r['mean_oracle_cost'] for r in edge])
fig,ax=plt.subplots(figsize=(12.5,7.5));ax.plot(lam,task,marker='o',label='Terminal task accuracy');ax.plot(lam,route,marker='s',label='Minimal-route accuracy');ax.axvspan(*x['goldilocks_cost_band'],alpha=.12,label='Observed optimal band');ax.axvline(x['break_even_lambda']['overlap'],linestyle='--');ax.axvline(np.mean([x['break_even_lambda'][k] for k in ('pair_01_23','pair_02_13','pair_03_12')]),linestyle=':');ax.set(xlabel=r'Workspace price $\lambda$',ylabel='Accuracy',ylim=(0,1.08),title='Formation-Cost Goldilocks Edge');ax.grid(alpha=.2);ax.legend(loc='lower left');fig.savefig(FIG/'02_cost_edge.png',dpi=220,bbox_inches='tight');plt.close(fig)
# costs
fig,ax=plt.subplots(figsize=(11.5,7));ax.plot(lam,cost,marker='o',label='Selected active cost');ax.plot(lam,oracle,linestyle='--',label='Minimal sufficient cost');ax.set(xlabel=r'Workspace price $\lambda$',ylabel='Mean active route cost',title='Underpricing Overbuilds; Overpricing Underbuilds');ax.grid(alpha=.2);ax.legend();fig.savefig(FIG/'03_active_cost.png',dpi=220,bbox_inches='tight');plt.close(fig)
# diagonal route selection
selected=[0.0,.12,.24,.40]; diag=np.array([[next(r for r in edge if r['lambda_cost']==v)['route_by_task'][i][i] for v in selected] for i in range(6)])
fig,ax=plt.subplots(figsize=(10.5,7));im=ax.imshow(diag,aspect='auto',vmin=0,vmax=1);ax.set_yticks(range(6),x['task_names']);ax.set_xticks(range(4),[f'λ={v:.2f}' for v in selected]);ax.set_title('Probability of Selecting the Minimal Sufficient Route');
for i in range(6):
 for j in range(4): ax.text(j,i,f'{diag[i,j]:.2f}',ha='center',va='center',fontsize=9)
fig.colorbar(im,ax=ax,label='Selection probability');fig.savefig(FIG/'04_route_selection.png',dpi=220,bbox_inches='tight');plt.close(fig)
