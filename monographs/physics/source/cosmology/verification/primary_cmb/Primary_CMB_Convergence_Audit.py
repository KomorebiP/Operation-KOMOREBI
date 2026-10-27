from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
worker=ROOT/'verification'/'Primary_CMB_Convergence_Worker.py'
cases=['base','quadrature','multipole','timestep']
records={case:json.loads((ROOT/'data'/f'primary_cmb_convergence_{case}.json').read_text()) for case in cases}

def discrepancy(name:str)->float:
    ref=records['base']; test=records[name]; values=[]
    for key in ['AT','AV','AE']:
        a=np.asarray(ref[key]); b=np.asarray(test[key]); scale=max(float(np.max(np.abs(a))),0.1)
        values.append(float(np.max(np.abs(a-b))/scale))
    return max(values)

quad=discrepancy('quadrature')
mult=discrepancy('multipole')
step=discrepancy('timestep')
checks=[
    {'id':'PCV01','statement':'momentum quadrature refinement is controlled','value':quad,'threshold':0.08,'status':'PASS' if quad<=0.08 else 'FAIL'},
    {'id':'PCV02','statement':'photon-neutrino-dark multipole refinement is controlled','value':mult,'threshold':0.12,'status':'PASS' if mult<=0.12 else 'FAIL'},
    {'id':'PCV03','statement':'time-step refinement is controlled','value':step,'threshold':0.05,'status':'PASS' if step<=0.05 else 'FAIL'},
    {'id':'PCV04','statement':'all accepted-state Einstein constraint residuals are below one percent','value':max(r['constraint_max'] for r in records.values()),'threshold':0.01,'status':'PASS' if max(r['constraint_max'] for r in records.values())<=0.01 else 'FAIL'},
]
convergence_df=pd.DataFrame(checks)
convergence_df.to_csv(ROOT/'data'/'primary_cmb_convergence_checks.csv',index=False)
main_df=pd.read_csv(ROOT/'data'/'primary_cmb_checks.csv')
pd.concat([main_df,convergence_df],ignore_index=True).to_csv(ROOT/'data'/'primary_cmb_all_checks.csv',index=False)
pd.DataFrame([
    {'control':'momentum quadrature','relative_discrepancy':quad},
    {'control':'multipole truncation','relative_discrepancy':mult},
    {'control':'time-step refinement','relative_discrepancy':step},
    {'control':'accepted-state Einstein constraint','relative_discrepancy':max(r['constraint_max'] for r in records.values())},
]).to_csv(ROOT/'data'/'primary_cmb_convergence_summary.csv',index=False)
summary={'quadrature_source_discrepancy':quad,'multipole_source_discrepancy':mult,'timestep_source_discrepancy':step,'pass_count':sum(c['status']=='PASS' for c in checks),'fail_count':sum(c['status']=='FAIL' for c in checks),'checks':checks}
(ROOT/'data'/'Primary_CMB_Convergence_Audit.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
