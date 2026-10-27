from __future__ import annotations
import json, math, pathlib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
ROOT=pathlib.Path(__file__).resolve().parents[1]
dev=pd.read_csv(ROOT/'development_results/scaling_trials.csv').rename(columns={'screen_emergence':'emergence'})
hold=pd.read_csv(ROOT/'holdout_results/HOLDOUT_POINTS.csv')
post=[]
for p in sorted((ROOT/'holdout_results/posthoc').glob('*.json')): post.append(json.loads(p.read_text()))
post=pd.DataFrame(post)
base=json.loads((ROOT/'development_results/scaling_analysis.json').read_text())
coef=base['coefficients']
def features(df):
 h=np.log2(df.hidden_width.to_numpy(float));return np.column_stack([np.log2(df.steps.to_numpy(float)),h,h*h,np.log2(df.bottleneck_dim.to_numpy(float))])
def predict(df,c=coef):
 X=features(df);b=np.array([c['log2_steps'],c['log2_hidden'],c['log2_hidden_squared'],c['log2_dim']]);z=c['intercept']+X@b;return 1/(1+np.exp(-z))
hold['predicted_probability']=predict(hold)
formula_hold=hold[hold.bottleneck_dim>=2].copy()
y=formula_hold.emergence.astype(int).to_numpy();p=formula_hold.predicted_probability.to_numpy()
validation={'schema':'rrct.v054.scaling_validation.v1','frozen_status':json.loads((ROOT/'holdout_results/HOLDOUT_ANALYSIS.json').read_text())['status'],'holdout_point_count':len(hold),'formula_domain_point_count':len(formula_hold),'formula_domain':'bottleneck_dim >= 2; d=1 is a structural out-of-domain control','original_formula_holdout':{'auc':float(roc_auc_score(y,p)),'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,p))},'configuration_calibration':[]}
for key,g in hold.groupby(['bottleneck_dim','hidden_width','steps']):
 validation['configuration_calibration'].append({'dim':int(key[0]),'hidden':int(key[1]),'steps':int(key[2]),'predicted_probability':float(g.predicted_probability.mean()),'observed_rate':float(g.emergence.mean()),'mean_action_accuracy':float(g.action_accuracy.mean()),'mean_probe_accuracy':float(g.probe_accuracy.mean()),'mean_patch_accuracy':float(g.patch_accuracy.mean())})
# Post-hoc combined descriptive fit; not a frozen test.
all_df=pd.concat([dev.rename(columns={'dim':'bottleneck_dim','hidden':'hidden_width'}),hold[hold.bottleneck_dim>=2],post],ignore_index=True,sort=False)
X=features(all_df);yy=all_df.emergence.astype(int).to_numpy();m=LogisticRegression(C=3.0,max_iter=10000).fit(X,yy)
cc={'intercept':float(m.intercept_[0]),'log2_steps':float(m.coef_[0,0]),'log2_hidden':float(m.coef_[0,1]),'log2_hidden_squared':float(m.coef_[0,2]),'log2_dim':float(m.coef_[0,3])}
def threshold(dim,hidden,prob):
 l=math.log(prob/(1-prob));h=math.log2(hidden);d=math.log2(dim);return 2**((l-cc['intercept']-cc['log2_hidden']*h-cc['log2_hidden_squared']*h*h-cc['log2_dim']*d)/cc['log2_steps'])
validation['posthoc_combined_formula']={
 'formula':'P(E=1)=sigmoid(b0+bS log2(steps)+bH log2(hidden)+bHH log2(hidden)^2+bD log2(dim))',
 'coefficients':cc,
 'thresholds':[
  {
   'dim':d,'hidden':h,
   'steps_p50_single_seed':threshold(d,h,.5),
   'steps_p90_single_seed':threshold(d,h,.9),
   'steps_p95_all_four_seeds':threshold(d,h,.95**.25),
  }
  for d,h in [(2,32),(4,16),(2,8),(4,8)]
 ],
 'cohort_reliability_identity':'If seed outcomes are conditionally independent with per-seed probability p, probability all n seeds emerge is p^n; target all-seed reliability q therefore uses p=q^(1/n).'
}
if len(post):
 validation['posthoc_d2_h32_s1200']={'n':len(post),'emergence_rate':float(post.emergence.mean()),'mean_action_accuracy':float(post.action_accuracy.mean()),'mean_probe_accuracy':float(post.probe_accuracy.mean()),'mean_patch_accuracy':float(post.patch_accuracy.mean()),'mean_cut_accuracy':float(post.cut_accuracy.mean())}
(ROOT/'holdout_results/SCALING_VALIDATION.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n')
hold.to_csv(ROOT/'holdout_results/HOLDOUT_POINTS_WITH_PREDICTIONS.csv',index=False)
print(json.dumps(validation,indent=2,sort_keys=True))
