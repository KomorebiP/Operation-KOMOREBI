from __future__ import annotations
import json, pathlib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.model_selection import LeaveOneGroupOut

BASE=pathlib.Path('/mnt/data/rrct_v054_scale_work')

def read_jsonl(path):
    return [json.loads(x) for x in open(path) if x.strip()]

# d2
rows=json.load(open(BASE/'screen_dim2_targeted.json'))
# d4
for p in [BASE/'d4_h8_low.jsonl',BASE/'d4_h8_high.jsonl',BASE/'d4_h16.jsonl',BASE/'d4_h32.jsonl',BASE/'d4_h64.jsonl']:
    rows += read_jsonl(p)
# d1 structural controls
rows_d1=read_jsonl(BASE/'d1_highscale.jsonl')

df=pd.DataFrame(rows)
df=df.drop_duplicates(['dim','hidden','steps','seed']).sort_values(['dim','hidden','steps','seed']).reset_index(drop=True)
df['log2_steps']=np.log2(df.steps)
df['log2_hidden']=np.log2(df.hidden)
df['log2_dim']=np.log2(df.dim)
df['hidden_sq']=df.log2_hidden**2
X=df[['log2_steps','log2_hidden','hidden_sq','log2_dim']].to_numpy()
y=df.screen_emergence.astype(int).to_numpy()
model=LogisticRegression(C=3.0,max_iter=10000).fit(X,y)
pred=model.predict_proba(X)[:,1]
logo=LeaveOneGroupOut();cv=np.zeros(len(df))
for train,test in logo.split(X,y,groups=df.seed):
    m=LogisticRegression(C=3.0,max_iter=10000).fit(X[train],y[train]);cv[test]=m.predict_proba(X[test])[:,1]
coef={'intercept':float(model.intercept_[0]),'log2_steps':float(model.coef_[0,0]),'log2_hidden':float(model.coef_[0,1]),'log2_hidden_squared':float(model.coef_[0,2]),'log2_dim':float(model.coef_[0,3])}

def threshold_steps(dim,hidden,p):
    logit=np.log(p/(1-p))
    h=np.log2(hidden);d=np.log2(dim)
    return float(2**((logit-coef['intercept']-coef['log2_hidden']*h-coef['log2_hidden_squared']*h*h-coef['log2_dim']*d)/coef['log2_steps']))

thresholds=[]
for dim in [2,4]:
    for hidden in [8,16,32,64]:
        thresholds.append({'dim':dim,'hidden':hidden,'steps_p50':threshold_steps(dim,hidden,.5),'steps_p90':threshold_steps(dim,hidden,.9)})

agg=df.groupby(['dim','hidden','steps']).agg(mean_accuracy=('accuracy','mean'),sd_accuracy=('accuracy','std'),emergence_rate=('screen_emergence','mean'),mean_cut=('cut_accuracy','mean')).reset_index()
result={
 'schema':'rrct.v054.workspace_emergence_scaling.analysis.v1',
 'development_trial_count':int(len(df)),
 'development_seed_count':int(df.seed.nunique()),
 'dims':[int(x) for x in sorted(df.dim.unique())],
 'hidden_widths':[int(x) for x in sorted(df.hidden.unique())],
 'step_values':[int(x) for x in sorted(df.steps.unique())],
 'emergence_definition':{'action_accuracy_min':.98,'cut_accuracy_max':.15,'full_probe_accuracy_min':.95,'full_patch_accuracy_min':.95},
 'formula': 'P(E=1)=sigmoid(b0+bS log2(steps)+bH log2(hidden)+bHH log2(hidden)^2+bD log2(dim))',
 'coefficients':coef,
 'in_sample':{'auc':float(roc_auc_score(y,pred)),'brier':float(brier_score_loss(y,pred)),'log_loss':float(log_loss(y,pred))},
 'leave_one_seed_out':{'auc':float(roc_auc_score(y,cv)),'brier':float(brier_score_loss(y,cv)),'log_loss':float(log_loss(y,cv))},
 'predicted_thresholds':thresholds,
 'one_dimensional_control':{
   'trial_count':len(rows_d1),
   'max_accuracy':float(max(r['accuracy'] for r in rows_d1)),
   'max_compute':int(max(r['compute'] for r in rows_d1)),
   'emergence_count':int(sum(r['screen_emergence'] for r in rows_d1)),
 },
 'aggregates':agg.to_dict('records'),
}
(BASE/'scaling_analysis.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
df.to_csv(BASE/'scaling_trials.csv',index=False)
agg.to_csv(BASE/'scaling_aggregates.csv',index=False)
print(json.dumps({k:result[k] for k in ['development_trial_count','coefficients','in_sample','leave_one_seed_out','predicted_thresholds','one_dimensional_control']},indent=2))
