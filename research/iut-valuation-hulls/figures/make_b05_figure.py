"""Reproducible mathematics plot (no generative image methods)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

out=Path(__file__).parent
fig,axes=plt.subplots(1,2,figsize=(11.8,4.0), layout='constrained')
ax=axes[0]
ax.set_xlim(-0.1,4.3)
ax.set_ylim(0,8)
ax.set_xticks([0.7,2,3.5],['Unit orbit','Integral closure','Pilot-adjoined ideal'])
ax.tick_params(axis='x', labelrotation=12)
ax.set_yticks(np.arange(0,8))
ax.set_ylabel('Normalized valuation depth')
ax.axhline(4, lw=1.4, ls=':', color='0.3')
ax.axhline(1, lw=1.4, ls='--', color='0.5')
ax.scatter([0.7],[4], s=90, zorder=10, label='Initial theta depth = 4')
ax.plot([2,2],[4,7.5],lw=4,solid_capstyle='round',label='Integral multiples: depth ≥ 4')
ax.plot([3.5,3.5],[1,7.5],lw=4,solid_capstyle='round',label='Pilot-adjoined: depth ≥ 1')
ax.scatter([3.5],[1],s=100,zorder=10)
ax.annotate('Pilot depth = 1\n(outside original closure)',xy=(2.08,1),xytext=(0.2,1.75),fontsize=9,arrowprops={'arrowstyle':'->','lw':.9})
ax.set_title('What each closure can reach')
ax.grid(axis='y',alpha=.16)
ax.spines[['top','right']].set_visible(False)

ax=axes[1]
m=np.arange(0,16)
ax.plot(m,11*m,marker='o',markevery=[0,3,6,9,12,15],lw=2.5,label='Total cost $E(m)=11m$')
ax.plot(m,np.zeros_like(m),ls=':',lw=1.6,label='Zero-cost baseline')
ax.set(xlabel='Pilot valuation depth $m$',ylabel='Enlargement exponent $E$',title='Weights $s=(1,4,9)$; 3 summands')
ax.grid(alpha=.2)
ax.legend(loc='upper left',fontsize=9,frameon=False)
ax.text(0.04,.75,'For $m=3$, total cost $=33$\nNormalized per summand $=11$',
        transform=ax.transAxes,fontsize=10,va='top')
ax.spines[['top','right']].set_visible(False)
fig.suptitle('IUT-inspired local valuation-hull model  |  Komorebi B05',fontsize=13,weight='semibold')
fig.savefig(out/'valuation_hull_gap.svg',bbox_inches='tight')
fig.savefig(out/'valuation_hull_gap.png',dpi=180,bbox_inches='tight')
plt.close(fig)
