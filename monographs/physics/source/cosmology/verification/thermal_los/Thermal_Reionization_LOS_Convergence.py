from __future__ import annotations
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
sys.path.insert(0,str(Path(__file__).resolve().parent))
import Thermal_Reionization_LOS_Verification as M

hist=M.ThermalHistory(); src=pd.read_csv(DATA/'primary_cmb_sources.csv')
ells=np.array([2,5,10,20,50,100,200,262,500,582,894,1000,1500,2000,2500])
runs={}
for name,nk in [('coarse',2200),('main',3000),('fine',4500)]:
    df,ctrl,info,_=M.project_spectra(hist,src,kpoints=nk,selected_only=ells)
    df.to_csv(DATA/f'convergence_{name}_spectra.csv',index=False)
    runs[name]=df

base=runs['main']; fine=runs['fine']
rows=[]
for i,ell in enumerate(ells):
    b=base.iloc[i]; f=fine.iloc[i]
    rB=b.C_TE/np.sqrt(max(b.C_TT*b.C_EE,1e-300)); rF=f.C_TE/np.sqrt(max(f.C_TT*f.C_EE,1e-300))
    rows.append({'ell':ell,'TT_relative':abs(b.C_TT-f.C_TT)/max(abs(f.C_TT),1e-30),'EE_relative':abs(b.C_EE-f.C_EE)/max(abs(f.C_EE),1e-30),'TE_correlation_absolute':abs(rB-rF)})
out=pd.DataFrame(rows); out.to_csv(DATA/'thermal_reionization_los_convergence.csv',index=False)
metrics={'TT_max_relative':float(out.TT_relative.max()),'EE_max_relative':float(out.EE_relative.max()),'TE_correlation_max_absolute':float(out.TE_correlation_absolute.max()),'TT_acoustic_max_relative':float(out.loc[out.ell>=200,'TT_relative'].max()),'EE_acoustic_max_relative':float(out.loc[out.ell>=200,'EE_relative'].max())}
checks=[
 {'id':'TRLC01','statement':'selected TT projection converges under k-grid refinement','value':metrics['TT_max_relative'],'threshold':0.06,'status':'PASS' if metrics['TT_max_relative']<=0.06 else 'FAIL'},
 {'id':'TRLC02','statement':'selected EE projection converges under k-grid refinement','value':metrics['EE_max_relative'],'threshold':0.06,'status':'PASS' if metrics['EE_max_relative']<=0.06 else 'FAIL'},
 {'id':'TRLC03','statement':'TE correlation converges under k-grid refinement','value':metrics['TE_correlation_max_absolute'],'threshold':0.06,'status':'PASS' if metrics['TE_correlation_max_absolute']<=0.06 else 'FAIL'},
 {'id':'TRLC04','statement':'acoustic TT projection converges under k-grid refinement','value':metrics['TT_acoustic_max_relative'],'threshold':0.05,'status':'PASS' if metrics['TT_acoustic_max_relative']<=0.05 else 'FAIL'},
]
pd.DataFrame(checks).to_csv(DATA/'thermal_reionization_los_convergence_checks.csv',index=False)
res={**metrics,'pass_count':sum(x['status']=='PASS' for x in checks),'fail_count':sum(x['status']=='FAIL' for x in checks),'checks':checks}
(DATA/'Thermal_Reionization_LOS_Convergence.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
