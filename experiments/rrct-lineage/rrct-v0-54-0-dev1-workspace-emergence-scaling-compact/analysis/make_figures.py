from __future__ import annotations
import json, pathlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
dev=pd.read_csv(ROOT/'development_results/scaling_trials.csv')
hold=pd.read_csv(ROOT/'holdout_results/HOLDOUT_POINTS_WITH_PREDICTIONS.csv')
post=pd.DataFrame([json.loads(p.read_text()) for p in sorted((ROOT/'holdout_results/posthoc').glob('*.json'))])

def development_curve(dim:int,path:str):
 d=dev[dev.dim==dim]
 agg=d.groupby(['hidden','steps']).screen_emergence.mean().reset_index()
 fig,ax=plt.subplots(figsize=(10.5,6.8))
 for h,g in agg.groupby('hidden'):
  g=g.sort_values('steps');ax.plot(g.steps,g.screen_emergence,marker='o',label=f'width {int(h)}')
 ax.set_xscale('log',base=2);ax.set_ylim(-.04,1.04);ax.set_xlabel('Terminal-training updates (log2 scale)');ax.set_ylabel('Fraction of seeds meeting screen emergence');ax.set_title(f'Development emergence curves: bottleneck dimension {dim}',fontsize=15,pad=14);ax.grid(alpha=.22);ax.legend()
 fig.savefig(FIG/path,dpi=220,bbox_inches='tight');plt.close(fig)

development_curve(2,'01_development_emergence_dim2.png')
development_curve(4,'02_development_emergence_dim4.png')

# Holdout transition + posthoc.
fig,ax=plt.subplots(figsize=(10.5,6.8))
for dim,h,label in [(2,32,'d=2, width=32'),(4,16,'d=4, width=16')]:
 g=hold[(hold.bottleneck_dim==dim)&(hold.hidden_width==h)].groupby('steps').emergence.mean().reset_index()
 if dim==2 and len(post):
  g=pd.concat([g,pd.DataFrame({'steps':[1200],'emergence':[post.emergence.mean()]})],ignore_index=True).sort_values('steps')
 ax.plot(g.steps,g.emergence,marker='o',linewidth=2,label=label)
ax.set_xscale('log',base=2);ax.set_ylim(-.04,1.04);ax.set_xlabel('Training updates');ax.set_ylabel('Full causal-emergence rate across four fresh seeds');ax.set_title('Fresh-seed phase transition and post-hoc completion point',fontsize=15,pad=14);ax.grid(alpha=.22);ax.legend()
ax.annotate('Frozen d=2 endpoint\nonly 3/4 at 800',xy=(800,.75),xytext=(520,.42),arrowprops={'arrowstyle':'->'},fontsize=10)
ax.annotate('Post-hoc: 4/4 at 1200',xy=(1200,1.0),xytext=(1450,.78),arrowprops={'arrowstyle':'->'},fontsize=10)
fig.savefig(FIG/'03_holdout_phase_transition.png',dpi=220,bbox_inches='tight');plt.close(fig)

# Predicted vs observed calibration (formula domain only).
groups=[]
for (d,h,s),g in hold[hold.bottleneck_dim>=2].groupby(['bottleneck_dim','hidden_width','steps']):
 groups.append({'label':f'd{int(d)}/h{int(h)}/s{int(s)}','predicted':g.predicted_probability.mean(),'observed':g.emergence.mean()})
g=pd.DataFrame(groups)
fig,ax=plt.subplots(figsize=(8.5,8.0));ax.scatter(g.predicted,g.observed,s=100)
for _,r in g.iterrows():ax.annotate(r.label,(r.predicted,r.observed),xytext=(5,5),textcoords='offset points',fontsize=9)
ax.plot([0,1],[0,1],linewidth=1.5,label='perfect calibration');ax.set_xlim(-.03,1.03);ax.set_ylim(-.03,1.03);ax.set_xlabel('Development-fit predicted emergence probability');ax.set_ylabel('Observed fresh-seed emergence rate');ax.set_title('The formula orders the frontier but overstates reliability',fontsize=15,pad=14);ax.grid(alpha=.22);ax.legend()
fig.savefig(FIG/'04_formula_calibration.png',dpi=220,bbox_inches='tight');plt.close(fig)

# Full causal metrics across key configurations.
key_order=[(1,64,2400),(2,32,200),(2,32,400),(2,32,800),(2,32,1200),(4,16,200),(4,16,400),(4,16,800)]
rows=[]
for d,h,s in key_order:
 if s==1200:
  g=post
 else:g=hold[(hold.bottleneck_dim==d)&(hold.hidden_width==h)&(hold.steps==s)]
 rows.append({'label':f'd{d}\nh{h}\ns{s}','action':g.action_accuracy.mean(),'probe':g.probe_accuracy.mean(),'patch':g.patch_accuracy.mean()})
r=pd.DataFrame(rows);x=np.arange(len(r));w=.25
fig,ax=plt.subplots(figsize=(13,7));ax.bar(x-w,r.action,w,label='Task');ax.bar(x,r.probe,w,label='Latent probe');ax.bar(x+w,r.patch,w,label='Causal transplant');ax.set_ylim(0,1.12);ax.set_xticks(x);ax.set_xticklabels(r.label);ax.set_ylabel('Mean strict accuracy');ax.set_title('Full causal verification across capacity and training scale',fontsize=15,pad=14);ax.grid(axis='y',alpha=.22);ax.legend()
fig.savefig(FIG/'05_full_causal_metrics.png',dpi=220,bbox_inches='tight');plt.close(fig)
print('\n'.join(str(p) for p in sorted(FIG.glob('*.png'))))
