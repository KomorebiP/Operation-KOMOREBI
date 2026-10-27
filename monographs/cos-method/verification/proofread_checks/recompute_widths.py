"""Re-evaluate archived exact inputs and plot widths before float conversion."""
from pathlib import Path
from dataclasses import asdict
import json,sys
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'engine'))
from interval_kcos import interval_positive_logsf,even_df_scaled_chi_square_logsf_interval
from directed_accuracy import directed_relative_accuracy,interval_endpoint_strings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
source=json.loads((Path(__file__).with_name('fixed_resolution_controls.json')).read_text())
rows=[]
for row in source:
    p=row['inputs']
    r=interval_positive_logsf(p['q_decimal'],['0.02']*80,theta_decimal=p['theta_decimal'],upper_decimal=p['upper_decimal'],eta_decimal=p['eta_decimal'],K=int(p['K']),interval_dps=int(p['interval_dps']))
    a=directed_relative_accuracy(r.log10_interval,'1e-8',dps=150)
    e=even_df_scaled_chi_square_logsf_interval(p['q_decimal'],coefficient_decimal='0.02',df=80,interval_dps=140)
    lo,hi=map(Decimal,interval_endpoint_strings(r.log10_interval));elo,ehi=map(Decimal,interval_endpoint_strings(e['log10_interval']))
    assert lo<=elo<=ehi<=hi
    assert r.log10_interval==row['result']['log10_interval'], 'diagnostic change altered authoritative enclosure'
    rows.append(dict(target_log10_p=row['target_log10_p'],inputs=p,result=asdict(r),directed_width_upper=a.width_upper,directed_ratio_upper=a.ratio_upper,independent_control=e,control_fully_contained=True,enclosure_unchanged=True))
Path(__file__).with_name('corrected_fixed_resolution_controls.json').write_text(json.dumps(rows,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(8.2,4.1),layout='constrained')
x=[-int(r['target_log10_p']) for r in rows]; y=[float(r['directed_width_upper']) for r in rows]
ax.loglog(x,y,marker='o',lw=1.6,ms=6)
ax.set_xticks(x,labels=['100','1000','5000']);ax.minorticks_off()
ax.set_xlabel(r'Tail depth, $-\log_{10}p$ (target)',fontsize=11)
ax.set_ylabel(r'Width of the $\log_{10}p$ interval (decades)',fontsize=11)
ax.set_title('Directed enclosure width at fixed numerical resolution',fontsize=12,pad=14)
ax.grid(True,alpha=.2)
for a,b in zip(x,y):ax.annotate(f'{b:.3e}',(a,b),xytext=(0,12),textcoords='offset points',ha='center',fontsize=10)
ax.set_ylim(min(y)*.6,max(y)*2.5)
fig.savefig(ROOT/'book/figures_final/figure_24_interval_deep_tail_width.png',dpi=220)
plt.close(fig)
print([(r['target_log10_p'],float(r['directed_width_upper']),float(r['directed_ratio_upper'])) for r in rows])
