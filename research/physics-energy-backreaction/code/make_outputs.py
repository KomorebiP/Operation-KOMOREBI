from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'results/final'; F=ROOT/'figures'; F.mkdir(exist_ok=True)
r=json.loads((D/'dynamics.json').read_text());p=json.loads((D/'parameters.json').read_text())
for name,rows in [('parameter_family',p['parameter_family']),('radiative_diagnostics',p['radiative_table'])]:
 with (D/(name+'.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
flat=[]
for row in r:
 z={**row['config'],**{k:v for k,v in row.items() if k not in ('config','interpretation')}};flat.append(z)
with (D/'dynamics.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)

def save(fig,name):
 fig.tight_layout()
 fig.savefig(F/(name+'.pdf'),bbox_inches='tight')
 fig.savefig(F/(name+'.png'),dpi=180,bbox_inches='tight')
 plt.close(fig)

a=np.load(D/'run_00.npz')
fig,ax=plt.subplots(figsize=(7.1,3.7))
ax.plot(a['t'],a['kinetic'],label='Background kinetic energy')
ax.plot(a['t'],a['modes'],label='Instantaneous mode energy')
ax.plot(a['t'],a['kinetic']+a['modes'],'--',label='Total')
ax.set(xlabel=r'Dimensionless time $A(t-t_i)$',ylabel='Energy / initial reservoir',ylim=(-.025,1.18))
ax.legend(frameon=False,fontsize=9,loc='lower left');ax.grid(alpha=.2)
save(fig,'conserved_energy')
fig,ax=plt.subplots(figsize=(7.1,3.7))
for idx,label in [(0,'Full reaction force'),(14,'Reaction force omitted'),(15,'Coherence force omitted')]:
 a=np.load(D/f'run_{idx:02d}.npz');ax.plot(a['t'],a['kinetic']+a['modes'],label=label)
ax.set(xlabel=r'Dimensionless time $A(t-t_i)$',ylabel='Total energy / initial reservoir')
ax.legend(frameon=False,fontsize=9,loc='upper left');ax.grid(alpha=.2)
save(fig,'negative_controls')
fig,ax=plt.subplots(figsize=(7.1,3.7))
ids=[1,2,0,3,4];dep=[r[i]['config']['depth'] for i in ids]
ax.plot(dep,[r[i]['maximum_mode_energy_fraction'] for i in ids],'o-',label='Maximum instantaneous mode-energy fraction')
ax.plot(dep,[x['production_fraction'] for x in p['radiative_table'] if 14<=x['depth']<=18],'s--',label='Fraction of Gaussian production retained')
ax.set(xlabel='Maximum tower depth',ylabel='Fraction',ylim=(0,1.08),xticks=dep)
ax.legend(frameon=False,fontsize=9,loc='lower right');ax.grid(alpha=.2)
save(fig,'depth_sensitivity')
fig,ax=plt.subplots(figsize=(7.1,3.7))
rad=[x for x in p['radiative_table'] if x['depth']>=13]
ax.semilogy([x['depth'] for x in rad],[x['curvature_power_counting_proxy'] for x in rad],'o-')
ax.set(xlabel='Maximum tower depth',ylabel=r'Curvature power-counting proxy $\mathcal{N}_H$',xticks=[x['depth'] for x in rad])
ax.grid(alpha=.2)
save(fig,'radiative_proxy')
# Machine-readable values used by the document. Python formatting retains source precision in JSON.
nom=r[0]
checks=json.loads((D/'verification.json').read_text())['gates']
tex=[f'\\newcommand{{\\NomEnergyError}}{{{nom["energy_residual"]:.3g}}}',
     f'\\newcommand{{\\NomInvariantError}}{{{nom["invariant_residual"]:.3g}}}']
(ROOT/'generated_values.tex').write_text('\n'.join(tex)+'\n')
print(json.dumps({'runs':len(r),'passed':sum(g['pass_'] for g in checks),'failed':sum(not g['pass_'] for g in checks),'nominal':nom},indent=2))
